import json
from pathlib import Path
from typing import Any

HITBOX_CONFIG_DIR = Path("hitbox_configs")
HITBOX_CONFIG_SUFFIX = ".hitbox.json"


def get_profile_path(profile_name: str) -> Path:
    return HITBOX_CONFIG_DIR / f"{profile_name}{HITBOX_CONFIG_SUFFIX}"


def ensure_config_dir() -> None:
    HITBOX_CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_profile(profile_name: str) -> dict[str, Any] | None:
    path = get_profile_path(profile_name)
    if not path.exists():
        return None

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_entry(
    profile_name: str,
    state: str,
    direction: str,
    size_x: float,
    size_y: float,
    offset_x: float,
    offset_y: float,
    animation: dict[str, Any] | None = None,
) -> Path:
    ensure_config_dir()
    path = get_profile_path(profile_name)

    data = load_profile(profile_name) or {"profile": profile_name, "offsets": {}}
    offsets = data.setdefault("offsets", {})
    state_entry = offsets.setdefault(state, {})
    state_entry[direction] = {
        "size_x": float(size_x),
        "size_y": float(size_y),
        "offset_x": float(offset_x),
        "offset_y": float(offset_y),
    }

    if animation is not None:
        animations = data.setdefault("animations", {})
        animation_key = f"{state}:{direction}"
        animation_entry = dict(animation)
        animation_entry["state"] = state
        animation_entry["target_direction"] = direction
        animations[animation_key] = animation_entry

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=True, indent=2)

    return path


def delete_entry(profile_name: str, state: str, direction: str) -> bool:
    path = get_profile_path(profile_name)
    data = load_profile(profile_name)
    if not isinstance(data, dict):
        return False

    changed = False

    offsets = data.get("offsets")
    if isinstance(offsets, dict):
        state_entry = offsets.get(state)
        if isinstance(state_entry, dict) and direction in state_entry:
            del state_entry[direction]
            changed = True
            if not state_entry:
                offsets.pop(state, None)

    animations = data.get("animations")
    if isinstance(animations, dict):
        animation_key = f"{state}:{direction}"
        if animation_key in animations:
            del animations[animation_key]
            changed = True
        # Backward compatibility with old format where key was only state.
        if state in animations:
            del animations[state]
            changed = True

    if changed:
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=True, indent=2)

    return changed
