from __future__ import annotations

from data.models import AppConfig, RollResult, Skill, TrackedWeapon
from services.skill_display import SKILL_DISPLAY_MODES, skill_display_value


def roll_matches_targets(
    roll: RollResult | None,
    weapon: TrackedWeapon,
    config: AppConfig,
) -> bool:
    if roll is None:
        return False

    set_targets = _target_keys(weapon.target_set_bonus_skills, config.set_bonus_skills)
    group_targets = _target_keys(weapon.target_group_skills, config.group_skills)
    if not set_targets and not group_targets:
        return False

    matches: list[bool] = []
    if set_targets:
        matches.append(_skill_key(roll.set_bonus_skill, config.set_bonus_skills) in set_targets)
    if group_targets:
        matches.append(_skill_key(roll.group_skill, config.group_skills) in group_targets)

    if weapon.target_match_mode == "all":
        return bool(matches) and all(matches)
    return any(matches)


def target_summary(weapon: TrackedWeapon, limit: int = 4) -> str:
    targets = weapon.target_set_bonus_skills + weapon.target_group_skills
    if not targets:
        return "Targets: none"
    visible = targets[:limit]
    extra = len(targets) - len(visible)
    suffix = f" +{extra} more" if extra else ""
    mode = "both types" if weapon.target_match_mode == "all" else "any"
    return f"Targets ({mode}): {', '.join(visible)}{suffix}"


def _target_keys(values: list[str], skills: list[Skill]) -> set[str]:
    return {_skill_key(value, skills) for value in values if value and value != "0"}


def _skill_key(value: str, skills: list[Skill]) -> str:
    text = value.strip()
    if not text or text == "0":
        return ""
    return _alias_keys(skills).get(text.casefold(), text.casefold())


def _alias_keys(skills: list[Skill]) -> dict[str, str]:
    keys: dict[str, str] = {}
    for skill in skills:
        canonical = skill.name.strip().casefold() or skill.source.strip().casefold()
        if not canonical:
            continue
        aliases = {skill.name.strip(), skill.source.strip()}
        for mode in SKILL_DISPLAY_MODES:
            aliases.add(skill_display_value(skill, mode).strip())
        for alias in aliases:
            if alias:
                keys[alias.casefold()] = canonical
    return keys
