from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from data.models import Ailment, AppConfig, Element, Skill, WeaponType


def load_app_config(config_dir: Path) -> AppConfig:
    return AppConfig(
        weapon_types=[
            WeaponType(**item) for item in _read_list(config_dir / "weapon_types.json")
        ],
        elements=[Element(**item) for item in _read_list(config_dir / "elements.json")],
        ailments=[Ailment(**item) for item in _read_list(config_dir / "ailments.json")],
        group_skills=[Skill(**item) for item in _read_list(config_dir / "group_skills.json")],
        set_bonus_skills=[
            Skill(**item) for item in _read_list(config_dir / "set_bonus_skills.json")
        ],
        skill_encyclopedia=[
            Skill(**item) for item in _read_list(config_dir / "skill_encyclopedia.json")
        ],
    )


def _read_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError(f"Config file must contain a JSON list: {path}")
    return [item for item in data if isinstance(item, dict)]
