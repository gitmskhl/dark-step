import pygame
from typing import Any

from scripts.hitbox_config import delete_entry, get_profile_path, load_profile, save_entry

# =========================
# Configuration
# =========================
SPRITESHEET_PATH = "images/idle.png"
FRAME_COUNT = 10
ANIMATION_FPS = 7
SCALE = 4.0
COLORKEY = None  # Example: (0, 0, 0)
PROFILE_NAME = "player"
TARGET_STATE = "idle"  # Example: idle, walk
TARGET_DIRECTION = "LEFT"  # RIGHT or LEFT
DEFAULT_DIRECTION = "RIGHT"  # Source spritesheet direction

# If True, use FRAME_WIDTH/FRAME_HEIGHT and ROW_INDEX for slicing.
# If False, the script slices one row into FRAME_COUNT equal parts.
USE_MANUAL_FRAME_SIZE = False
FRAME_WIDTH = 32
FRAME_HEIGHT = 32
ROW_INDEX = 0

WINDOW_PADDING = 120
WINDOW_BACKGROUND = (24, 24, 28)
RECT_COLOR = (255, 90, 90)
RECT_FILL_COLOR = (255, 90, 90, 45)
TEXT_COLOR = (235, 235, 235)
HELP_COLOR = (160, 160, 160)
RESIZE_BORDER_PX = 8
HANDLE_SIZE = 6


def load_frames(animation: dict[str, Any]) -> list[pygame.Surface]:
    path = str(animation["spritesheet_path"])
    frame_count = int(animation["frame_count"])
    scale = float(animation["scale"])
    colorkey = animation.get("colorkey")
    use_manual_frame_size = bool(animation.get("use_manual_frame_size", False))
    frame_width = int(animation.get("frame_width", FRAME_WIDTH))
    frame_height = int(animation.get("frame_height", FRAME_HEIGHT))
    row_index = int(animation.get("row_index", ROW_INDEX))

    spritesheet = pygame.image.load(path)
    sheet_w, sheet_h = spritesheet.get_size()

    if use_manual_frame_size:
        if frame_width <= 0 or frame_height <= 0:
            raise ValueError("FRAME_WIDTH and FRAME_HEIGHT must be > 0")
        if frame_count <= 0:
            raise ValueError("FRAME_COUNT must be > 0")

        y = row_index * frame_height
        if y + frame_height > sheet_h:
            raise ValueError("ROW_INDEX points outside the spritesheet")

        max_cols = sheet_w // frame_width
        if frame_count > max_cols:
            raise ValueError(
                f"FRAME_COUNT={frame_count} is larger than available columns={max_cols}"
            )

        frame_rects = [
            pygame.Rect(i * frame_width, y, frame_width, frame_height)
            for i in range(frame_count)
        ]
    else:
        if frame_count <= 0:
            raise ValueError("FRAME_COUNT must be > 0")
        if sheet_w % frame_count != 0:
            raise ValueError(
                f"Spritesheet width {sheet_w} is not divisible by FRAME_COUNT={frame_count}"
            )

        frame_w = sheet_w // frame_count
        frame_h = sheet_h
        frame_rects = [
            pygame.Rect(i * frame_w, 0, frame_w, frame_h)
            for i in range(frame_count)
        ]

    frames: list[pygame.Surface] = []
    for rect in frame_rects:
        frame = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        frame.blit(spritesheet, (0, 0), rect)
        if colorkey is not None:
            frame.set_colorkey(colorkey)

        if scale != 1.0:
            scaled_w = int(frame.get_width() * scale)
            scaled_h = int(frame.get_height() * scale)
            frame = pygame.transform.scale(frame, (scaled_w, scaled_h))

        frames.append(frame)

    return frames


def clamp_point_to_rect(point: tuple[int, int], rect: pygame.Rect) -> tuple[int, int]:
    x = max(rect.left, min(point[0], rect.right - 1))
    y = max(rect.top, min(point[1], rect.bottom - 1))
    return x, y


def make_rect_from_points(a: tuple[int, int], b: tuple[int, int]) -> pygame.Rect:
    left = min(a[0], b[0])
    top = min(a[1], b[1])
    right = max(a[0], b[0])
    bottom = max(a[1], b[1])
    return pygame.Rect(left, top, max(1, right - left + 1), max(1, bottom - top + 1))


def to_image_space(screen_rect: pygame.Rect, image_rect: pygame.Rect) -> pygame.Rect:
    return pygame.Rect(
        screen_rect.x - image_rect.x,
        screen_rect.y - image_rect.y,
        screen_rect.w,
        screen_rect.h,
    )


def detect_resize_edges(point: tuple[int, int], rect: pygame.Rect) -> set[str]:
    if not rect.collidepoint(point):
        return set()

    edges: set[str] = set()
    x, y = point
    if abs(x - rect.left) <= RESIZE_BORDER_PX:
        edges.add("left")
    if abs(x - (rect.right - 1)) <= RESIZE_BORDER_PX:
        edges.add("right")
    if abs(y - rect.top) <= RESIZE_BORDER_PX:
        edges.add("top")
    if abs(y - (rect.bottom - 1)) <= RESIZE_BORDER_PX:
        edges.add("bottom")
    return edges


def clamp_rect_to_image(rect: pygame.Rect, image_rect: pygame.Rect) -> pygame.Rect:
    x = max(image_rect.left, min(rect.x, image_rect.right - rect.w))
    y = max(image_rect.top, min(rect.y, image_rect.bottom - rect.h))
    w = max(1, min(rect.w, image_rect.w))
    h = max(1, min(rect.h, image_rect.h))
    x = min(x, image_rect.right - w)
    y = min(y, image_rect.bottom - h)
    return pygame.Rect(x, y, w, h)


def draw_resize_handles(screen: pygame.Surface, rect: pygame.Rect) -> None:
    handles = [
        (rect.left, rect.top),
        (rect.right - 1, rect.top),
        (rect.left, rect.bottom - 1),
        (rect.right - 1, rect.bottom - 1),
    ]
    for hx, hy in handles:
        handle_rect = pygame.Rect(
            hx - HANDLE_SIZE // 2,
            hy - HANDLE_SIZE // 2,
            HANDLE_SIZE,
            HANDLE_SIZE,
        )
        pygame.draw.rect(screen, RECT_COLOR, handle_rect)


def cursor_for_edges(edges: set[str]) -> int:
    if ("left" in edges and "top" in edges) or ("right" in edges and "bottom" in edges):
        return pygame.SYSTEM_CURSOR_SIZENWSE
    if ("right" in edges and "top" in edges) or ("left" in edges and "bottom" in edges):
        return pygame.SYSTEM_CURSOR_SIZENESW
    if "left" in edges or "right" in edges:
        return pygame.SYSTEM_CURSOR_SIZEWE
    if "top" in edges or "bottom" in edges:
        return pygame.SYSTEM_CURSOR_SIZENS
    return pygame.SYSTEM_CURSOR_ARROW


def resolve_cursor(
    interaction_mode: str | None,
    selected_rect_screen: pygame.Rect | None,
    image_rect: pygame.Rect,
    resize_edges: set[str],
) -> int:
    if interaction_mode == "resize":
        return cursor_for_edges(resize_edges)
    if interaction_mode == "move":
        return pygame.SYSTEM_CURSOR_SIZEALL
    if interaction_mode == "create":
        return pygame.SYSTEM_CURSOR_CROSSHAIR

    mouse_pos = pygame.mouse.get_pos()
    if not image_rect.collidepoint(mouse_pos):
        return pygame.SYSTEM_CURSOR_ARROW

    if selected_rect_screen is None:
        return pygame.SYSTEM_CURSOR_CROSSHAIR

    edges = detect_resize_edges(mouse_pos, selected_rect_screen)
    if edges:
        return cursor_for_edges(edges)
    if selected_rect_screen.collidepoint(mouse_pos):
        return pygame.SYSTEM_CURSOR_SIZEALL
    return pygame.SYSTEM_CURSOR_CROSSHAIR


def apply_cursor(cursor_kind: int, current_cursor: int) -> int:
    if cursor_kind == current_cursor:
        return current_cursor

    try:
        pygame.mouse.set_cursor(pygame.cursors.Cursor(cursor_kind))
        return cursor_kind
    except pygame.error:
        return current_cursor


def default_animation_config() -> dict[str, Any]:
    return {
        "spritesheet_path": SPRITESHEET_PATH,
        "frame_count": FRAME_COUNT,
        "animation_fps": ANIMATION_FPS,
        "scale": SCALE,
        "colorkey": COLORKEY,
        "target_direction": TARGET_DIRECTION,
        "default_direction": DEFAULT_DIRECTION,
        "use_manual_frame_size": USE_MANUAL_FRAME_SIZE,
        "frame_width": FRAME_WIDTH,
        "frame_height": FRAME_HEIGHT,
        "row_index": ROW_INDEX,
    }


def normalize_animation_config(raw: dict[str, Any] | None) -> dict[str, Any]:
    config = default_animation_config()
    if isinstance(raw, dict):
        config.update(raw)
    return config


def get_saved_animations(profile_name: str) -> dict[str, dict[str, Any]]:
    data = load_profile(profile_name)
    if not isinstance(data, dict):
        return {}
    animations = data.get("animations")
    if not isinstance(animations, dict):
        return {}

    result: dict[str, dict[str, Any]] = {}
    for animation_key, cfg in animations.items():
        if isinstance(animation_key, str) and isinstance(cfg, dict):
            normalized_cfg = dict(cfg)
            if "state" not in normalized_cfg:
                normalized_cfg["state"] = animation_key
            result[animation_key] = normalized_cfg
    return result


def load_saved_selection(
    profile_name: str,
    state: str,
    direction: str,
    image_rect: pygame.Rect,
    frame_w: int,
    frame_h: int,
) -> pygame.Rect | None:
    data = load_profile(profile_name)
    if not isinstance(data, dict):
        return None

    offsets = data.get("offsets")
    if not isinstance(offsets, dict):
        return None

    state_entry = offsets.get(state)
    if not isinstance(state_entry, dict):
        return None

    direction_entry = state_entry.get(direction)
    if not isinstance(direction_entry, dict):
        return None

    required_keys = ("offset_x", "offset_y", "size_x", "size_y")
    if any(key not in direction_entry for key in required_keys):
        return None

    try:
        offset_x_ratio = float(direction_entry["offset_x"])
        offset_y_ratio = float(direction_entry["offset_y"])
        size_x_ratio = float(direction_entry["size_x"])
        size_y_ratio = float(direction_entry["size_y"])
    except (TypeError, ValueError):
        return None

    x = int(round(offset_x_ratio * frame_w))
    y = int(round(offset_y_ratio * frame_h))
    w = int(round(size_x_ratio * frame_w))
    h = int(round(size_y_ratio * frame_h))

    x = max(0, min(x, frame_w - 1))
    y = max(0, min(y, frame_h - 1))
    w = max(1, min(w, frame_w - x))
    h = max(1, min(h, frame_h - y))

    return pygame.Rect(image_rect.x + x, image_rect.y + y, w, h)


def draw_text_block(screen: pygame.Surface, lines: list[str]) -> None:
    font = pygame.font.SysFont("consolas", 18)
    x, y = 16, 12
    for line in lines:
        color = HELP_COLOR if line.startswith("[") else TEXT_COLOR
        surface = font.render(line, True, color)
        screen.blit(surface, (x, y))
        y += surface.get_height() + 4


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Hitbox Offset Maker")

    def activate_animation(state: str, raw_animation: dict[str, Any]) -> tuple[
        str,
        dict[str, Any],
        list[pygame.Surface],
        list[pygame.Surface],
        int,
        int,
        str,
        str,
        bool,
        float,
    ]:
        animation = normalize_animation_config(raw_animation)
        animation["target_direction"] = str(animation.get("target_direction", TARGET_DIRECTION)).upper()
        animation["default_direction"] = str(animation.get("default_direction", DEFAULT_DIRECTION)).upper()

        if animation["target_direction"] not in ("LEFT", "RIGHT"):
            raise ValueError("target_direction must be LEFT or RIGHT")
        if animation["default_direction"] not in ("LEFT", "RIGHT"):
            raise ValueError("default_direction must be LEFT or RIGHT")

        loaded_frames = load_frames(animation)
        if not loaded_frames:
            raise RuntimeError("No frames were loaded")

        local_should_flip = animation["target_direction"] != animation["default_direction"]
        local_display_frames = [
            pygame.transform.flip(frame, True, False) for frame in loaded_frames
        ] if local_should_flip else loaded_frames

        local_frame_w, local_frame_h = loaded_frames[0].get_size()
        local_frame_duration_ms = 1000 / max(1, int(animation.get("animation_fps", ANIMATION_FPS)))

        return (
            state,
            animation,
            loaded_frames,
            local_display_frames,
            local_frame_w,
            local_frame_h,
            animation["target_direction"],
            animation["default_direction"],
            local_should_flip,
            local_frame_duration_ms,
        )

    current_state = TARGET_STATE
    saved_animations = get_saved_animations(PROFILE_NAME)
    (
        current_state,
        current_animation,
        frames,
        display_frames,
        frame_w,
        frame_h,
        target_dir,
        default_dir,
        should_flip,
        frame_duration_ms,
    ) = activate_animation(current_state, {})

    screen_w = max(500, frame_w + WINDOW_PADDING * 2)
    screen_h = max(380, frame_h + WINDOW_PADDING * 2)
    screen = pygame.display.set_mode((screen_w, screen_h))
    clock = pygame.time.Clock()

    frame_index = 0
    frame_elapsed_ms = 0.0

    initial_frame = display_frames[frame_index]
    initial_image_rect = initial_frame.get_rect(center=(screen_w // 2, screen_h // 2))

    dragging = False
    drag_start: tuple[int, int] | None = None
    drag_current: tuple[int, int] | None = None
    interaction_mode: str | None = None  # create, move, resize
    move_offset: tuple[int, int] | None = None
    resize_edges: set[str] = set()
    resize_start_rect: pygame.Rect | None = None
    selected_rect_screen: pygame.Rect | None = load_saved_selection(
        PROFILE_NAME,
        current_state,
        target_dir,
        initial_image_rect,
        frame_w,
        frame_h,
    )
    status_message = ""
    status_until_ms = 0
    current_cursor = pygame.SYSTEM_CURSOR_ARROW
    show_extra_info = True

    running = True
    while running:
        # Resize window if another saved animation has larger frame size.
        needed_w = max(500, frame_w + WINDOW_PADDING * 2)
        needed_h = max(380, frame_h + WINDOW_PADDING * 2)
        if needed_w != screen_w or needed_h != screen_h:
            screen_w, screen_h = needed_w, needed_h
            screen = pygame.display.set_mode((screen_w, screen_h))

        dt = clock.tick(120)
        frame_elapsed_ms += dt
        while frame_elapsed_ms >= frame_duration_ms:
            frame_elapsed_ms -= frame_duration_ms
            frame_index = (frame_index + 1) % len(frames)

        current_frame = display_frames[frame_index]
        image_rect = current_frame.get_rect(center=(screen_w // 2, screen_h // 2))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_c:
                    selected_rect_screen = None
                elif event.key == pygame.K_i:
                    show_extra_info = not show_extra_info
                    status_message = "extra info shown" if show_extra_info else "extra info hidden"
                    status_until_ms = pygame.time.get_ticks() + 1800
                elif event.key == pygame.K_DELETE:
                    deleted = delete_entry(PROFILE_NAME, current_state, target_dir)
                    if deleted:
                        selected_rect_screen = None
                        saved_animations = get_saved_animations(PROFILE_NAME)
                        status_message = f"deleted saved data for {current_state}/{target_dir}"
                    else:
                        status_message = f"nothing to delete for {current_state}/{target_dir}"
                    status_until_ms = pygame.time.get_ticks() + 2200
                elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    saved_animations = get_saved_animations(PROFILE_NAME)
                    animation_keys = list(saved_animations.keys())
                    if not animation_keys:
                        status_message = "no saved animations in profile yet"
                        status_until_ms = pygame.time.get_ticks() + 2200
                    else:
                        current_animation_key = f"{current_state}:{target_dir}"
                        if current_animation_key not in animation_keys:
                            next_index = 0
                        else:
                            delta = 1 if event.key == pygame.K_RIGHT else -1
                            next_index = (animation_keys.index(current_animation_key) + delta) % len(animation_keys)

                        next_key = animation_keys[next_index]
                        next_animation = saved_animations[next_key]
                        next_state = str(next_animation.get("state", TARGET_STATE))
                        (
                            current_state,
                            current_animation,
                            frames,
                            display_frames,
                            frame_w,
                            frame_h,
                            target_dir,
                            default_dir,
                            should_flip,
                            frame_duration_ms,
                        ) = activate_animation(next_state, next_animation)

                        frame_index = 0
                        frame_elapsed_ms = 0.0
                        next_image_rect = display_frames[0].get_rect(center=(screen_w // 2, screen_h // 2))
                        selected_rect_screen = load_saved_selection(
                            PROFILE_NAME,
                            current_state,
                            target_dir,
                            next_image_rect,
                            frame_w,
                            frame_h,
                        )
                        status_message = f"animation switched: {next_key}"
                        status_until_ms = pygame.time.get_ticks() + 2200
                elif event.key == pygame.K_s:
                    active_rect_screen = selected_rect_screen
                    if active_rect_screen is not None:
                        rect_img = to_image_space(active_rect_screen, image_rect)
                        width_ratio = rect_img.w / frame_w
                        height_ratio = rect_img.h / frame_h
                        offset_x_ratio = rect_img.x / frame_w
                        offset_y_ratio = rect_img.y / frame_h
                        path = save_entry(
                            PROFILE_NAME,
                            current_state,
                            target_dir,
                            width_ratio,
                            height_ratio,
                            offset_x_ratio,
                            offset_y_ratio,
                            animation=current_animation,
                        )
                        status_message = f"saved: {current_state}/{target_dir} (+animation) -> {path}"
                    else:
                        status_message = "nothing to save: select a rectangle first"
                    status_until_ms = pygame.time.get_ticks() + 2200
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if image_rect.collidepoint(event.pos):
                    point = clamp_point_to_rect(event.pos, image_rect)
                    if selected_rect_screen is not None:
                        edges = detect_resize_edges(point, selected_rect_screen)
                        if edges:
                            interaction_mode = "resize"
                            resize_edges = edges
                            resize_start_rect = selected_rect_screen.copy()
                            dragging = True
                        elif selected_rect_screen.collidepoint(point):
                            interaction_mode = "move"
                            move_offset = (point[0] - selected_rect_screen.x, point[1] - selected_rect_screen.y)
                            dragging = True
                        else:
                            interaction_mode = "create"
                            drag_start = point
                            drag_current = point
                            dragging = True
                    else:
                        interaction_mode = "create"
                        drag_start = point
                        drag_current = point
                        dragging = True
            elif event.type == pygame.MOUSEMOTION and dragging:
                point = clamp_point_to_rect(event.pos, image_rect)
                if interaction_mode == "create" and drag_start is not None:
                    drag_current = point
                elif interaction_mode == "move" and selected_rect_screen is not None and move_offset is not None:
                    new_x = point[0] - move_offset[0]
                    new_y = point[1] - move_offset[1]
                    selected_rect_screen = clamp_rect_to_image(
                        pygame.Rect(new_x, new_y, selected_rect_screen.w, selected_rect_screen.h),
                        image_rect,
                    )
                elif interaction_mode == "resize" and selected_rect_screen is not None and resize_start_rect is not None:
                    left = resize_start_rect.left
                    top = resize_start_rect.top
                    right = resize_start_rect.right
                    bottom = resize_start_rect.bottom

                    if "left" in resize_edges:
                        left = point[0]
                    if "right" in resize_edges:
                        right = point[0] + 1
                    if "top" in resize_edges:
                        top = point[1]
                    if "bottom" in resize_edges:
                        bottom = point[1] + 1

                    left = max(image_rect.left, min(left, image_rect.right - 1))
                    top = max(image_rect.top, min(top, image_rect.bottom - 1))
                    right = max(image_rect.left + 1, min(right, image_rect.right))
                    bottom = max(image_rect.top + 1, min(bottom, image_rect.bottom))

                    if right <= left:
                        right = left + 1
                    if bottom <= top:
                        bottom = top + 1

                    selected_rect_screen = pygame.Rect(left, top, right - left, bottom - top)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and dragging:
                dragging = False
                if interaction_mode == "create" and drag_start is not None and drag_current is not None:
                    selected_rect_screen = make_rect_from_points(drag_start, drag_current)
                if selected_rect_screen is not None:
                    selected_rect_screen = clamp_rect_to_image(selected_rect_screen, image_rect)
                drag_start = None
                drag_current = None
                interaction_mode = None
                move_offset = None
                resize_edges = set()
                resize_start_rect = None

        cursor_kind = resolve_cursor(interaction_mode, selected_rect_screen, image_rect, resize_edges)
        current_cursor = apply_cursor(cursor_kind, current_cursor)

        screen.fill(WINDOW_BACKGROUND)
        screen.blit(current_frame, image_rect)

        preview_rect: pygame.Rect | None = None
        if dragging and drag_start is not None and drag_current is not None:
            preview_rect = make_rect_from_points(drag_start, drag_current)

        active_rect_screen = preview_rect if preview_rect is not None else selected_rect_screen

        if active_rect_screen is not None:
            fill = pygame.Surface((active_rect_screen.w, active_rect_screen.h), pygame.SRCALPHA)
            fill.fill(RECT_FILL_COLOR)
            screen.blit(fill, active_rect_screen.topleft)
            pygame.draw.rect(screen, RECT_COLOR, active_rect_screen, 2)
            draw_resize_handles(screen, active_rect_screen)

        lines: list[str] = []
        if show_extra_info:
            lines.extend(
                [
                    "[LMB] drag empty area: create | drag inside: move | drag edge/corner: resize",
                    "[S] save, [Delete] remove saved, [LEFT/RIGHT] animations, [I] toggle info, [C] clear, [ESC] quit",
                    f"spritesheet: {current_animation['spritesheet_path']}",
                    f"profile: {PROFILE_NAME} ({get_profile_path(PROFILE_NAME)})",
                    f"target: state={current_state}, direction={target_dir}",
                    f"default_direction={default_dir}, flipped_view={should_flip}",
                    f"fps={int(current_animation['animation_fps'])}, scale={float(current_animation['scale'])}",
                    f"frame: {frame_index + 1}/{len(frames)} | frame_size: {frame_w}x{frame_h}",
                ]
            )

        if active_rect_screen is not None:
            rect_img = to_image_space(active_rect_screen, image_rect)
            width_ratio = rect_img.w / frame_w
            height_ratio = rect_img.h / frame_h
            offset_x_ratio = rect_img.x / frame_w
            offset_y_ratio = rect_img.y / frame_h
            if show_extra_info:
                lines.extend(
                    [
                        "",
                        "Selected rect (pixels in current frame):",
                        f"x={rect_img.x}, y={rect_img.y}, w={rect_img.w}, h={rect_img.h}",
                        "Selected rect (fractions of frame):",
                    ]
                )
            lines.extend(
                [
                    f"size_x = {width_ratio:.4f}, size_y = {height_ratio:.4f}",
                    f"offset_x = {offset_x_ratio:.4f}, offset_y = {offset_y_ratio:.4f}",
                ]
            )
        else:
            if show_extra_info:
                lines.extend(["", "Selected rect (fractions of frame):"])
            lines.extend(["size_x = -, size_y = -", "offset_x = -, offset_y = -"])

        if status_message and pygame.time.get_ticks() <= status_until_ms:
            lines.extend(["", status_message])

        draw_text_block(screen, lines)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
