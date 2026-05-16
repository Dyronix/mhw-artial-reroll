from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class WeaponType:
    name: str
    description: str = ""


@dataclass(frozen=True)
class Element:
    name: str


@dataclass(frozen=True)
class Ailment:
    name: str


@dataclass(frozen=True)
class Skill:
    name: str
    description: str = ""
    source: str = ""


@dataclass
class RollResult:
    set_bonus_skill: str = "0"
    group_skill: str = "0"
    highlighted: bool = False

    def useful(self) -> bool:
        return self.set_bonus_skill != "0" or self.group_skill != "0"


@dataclass
class TargetRule:
    set_bonus_skill: str = "0"
    group_skill: str = "0"


@dataclass
class TrackedWeapon:
    weapon_type: str
    attribute: str
    current_index: int = 0
    rolls: list[RollResult] = field(default_factory=list)
    target_rules: list[TargetRule] = field(default_factory=list)
    id: str = field(default_factory=lambda: uuid4().hex)

    @property
    def display_name(self) -> str:
        return f"{self.weapon_type} / {self.attribute}"


@dataclass
class RollHistoryWeapon:
    weapon_id: str
    weapon_type: str
    attribute: str
    roll_index: int
    roll: RollResult = field(default_factory=RollResult)


@dataclass
class RollHistoryEntry:
    sequence: int
    action: str
    weapons: list[RollHistoryWeapon] = field(default_factory=list)


@dataclass
class AppState:
    tracked_weapons: list[TrackedWeapon] = field(default_factory=list)
    skill_display_mode: str = "source"
    roll_history: list[RollHistoryEntry] = field(default_factory=list)
    next_history_sequence: int = 1


@dataclass(frozen=True)
class AppConfig:
    weapon_types: list[WeaponType]
    elements: list[Element]
    ailments: list[Ailment]
    group_skills: list[Skill]
    set_bonus_skills: list[Skill]
    skill_encyclopedia: list[Skill] = field(default_factory=list)

    @property
    def attributes(self) -> list[str]:
        return [item.name for item in self.elements] + [item.name for item in self.ailments]


def roll_from_dict(data: dict[str, Any]) -> RollResult:
    return RollResult(
        set_bonus_skill=_clean_skill(data.get("set_bonus_skill", "0")),
        group_skill=_clean_skill(data.get("group_skill", "0")),
        highlighted=bool(data.get("highlighted", False)),
    )


def weapon_from_dict(data: dict[str, Any]) -> TrackedWeapon:
    rolls = [roll_from_dict(item) for item in data.get("rolls", []) if isinstance(item, dict)]
    return TrackedWeapon(
        id=str(data.get("id") or uuid4().hex),
        weapon_type=str(data.get("weapon_type", "")),
        attribute=str(data.get("attribute", "")),
        current_index=max(0, int(data.get("current_index", 0) or 0)),
        rolls=rolls,
        target_rules=_clean_target_rule_list(data.get("target_rules", [])),
    )


def history_weapon_from_dict(data: dict[str, Any]) -> RollHistoryWeapon:
    roll_data = data.get("roll", {})
    return RollHistoryWeapon(
        weapon_id=str(data.get("weapon_id", "")),
        weapon_type=str(data.get("weapon_type", "")),
        attribute=str(data.get("attribute", "")),
        roll_index=max(0, int(data.get("roll_index", 0) or 0)),
        roll=roll_from_dict(roll_data if isinstance(roll_data, dict) else {}),
    )


def history_entry_from_dict(data: dict[str, Any]) -> RollHistoryEntry:
    weapons = [
        history_weapon_from_dict(item)
        for item in data.get("weapons", [])
        if isinstance(item, dict)
    ]
    return RollHistoryEntry(
        sequence=max(0, int(data.get("sequence", 0) or 0)),
        action=str(data.get("action", "")),
        weapons=weapons,
    )


def state_from_dict(data: dict[str, Any]) -> AppState:
    weapons = [
        weapon_from_dict(item)
        for item in data.get("tracked_weapons", [])
        if isinstance(item, dict)
    ]
    roll_history = [
        history_entry_from_dict(item)
        for item in data.get("roll_history", [])
        if isinstance(item, dict)
    ]
    return AppState(
        tracked_weapons=weapons,
        skill_display_mode=str(data.get("skill_display_mode") or "source"),
        roll_history=roll_history[-10:],
        next_history_sequence=max(1, int(data.get("next_history_sequence", 1) or 1)),
    )


def state_to_dict(state: AppState) -> dict[str, Any]:
    return asdict(state)


def _clean_skill(value: Any) -> str:
    text = str(value or "").strip()
    return text if text else "0"


def _clean_target_rule_list(value: Any) -> list[TargetRule]:
    if not isinstance(value, list):
        return []
    rules: list[TargetRule] = []
    seen: set[tuple[str, str]] = set()
    for item in value:
        if not isinstance(item, dict):
            continue
        set_bonus_skill = _clean_skill(item.get("set_bonus_skill"))
        group_skill = _clean_skill(item.get("group_skill"))
        if set_bonus_skill == "0" and group_skill == "0":
            continue
        key = (set_bonus_skill.casefold(), group_skill.casefold())
        if key in seen:
            continue
        rules.append(TargetRule(set_bonus_skill, group_skill))
        seen.add(key)
    return rules
