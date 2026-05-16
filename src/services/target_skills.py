from __future__ import annotations

from data.models import AppConfig, RollResult, Skill, TargetRule, TrackedWeapon
from services.skill_display import SKILL_DISPLAY_MODES, skill_display_value


def roll_matches_targets(
    roll: RollResult | None,
    weapon: TrackedWeapon,
    config: AppConfig,
) -> bool:
    if roll is None:
        return False

    rules = _target_rules(weapon, config)
    if not rules:
        return False

    set_key = _skill_key(roll.set_bonus_skill, config.set_bonus_skills)
    group_key = _skill_key(roll.group_skill, config.group_skills)
    return any(_rule_matches(rule, set_key, group_key) for rule in rules)


def target_summary(weapon: TrackedWeapon, limit: int = 4) -> str:
    targets = weapon.target_rules
    if not targets:
        return "Targets: none"
    visible = targets[:limit]
    extra = len(targets) - len(visible)
    suffix = f" +{extra} more" if extra else ""
    names = ", ".join(_rule_summary(rule) for rule in visible)
    return f"Targets: {names}{suffix}"


def _target_rules(
    weapon: TrackedWeapon,
    config: AppConfig,
) -> list[tuple[str, str]]:
    if weapon.target_rules:
        rules: list[tuple[str, str]] = []
        seen: set[tuple[str, str]] = set()
        for rule in weapon.target_rules:
            normalized = _normalized_rule(rule, config)
            if normalized is None or normalized in seen:
                continue
            rules.append(normalized)
            seen.add(normalized)
        return rules
    return []


def _append_normalized_rule(
    rules: list[tuple[str, str]],
    seen: set[tuple[str, str]],
    rule: TargetRule,
    config: AppConfig,
) -> None:
    normalized = _normalized_rule(rule, config)
    if normalized is None or normalized in seen:
        return
    rules.append(normalized)
    seen.add(normalized)


def _rule_matches(rule: tuple[str, str], set_key: str, group_key: str) -> bool:
    rule_set_key, rule_group_key = rule
    needs_set = bool(rule_set_key)
    needs_group = bool(rule_group_key)
    if needs_set and rule_set_key != set_key:
        return False
    if needs_group and rule_group_key != group_key:
        return False
    return needs_set or needs_group


def _rule_summary(rule: TargetRule) -> str:
    if rule.set_bonus_skill != "0" and rule.group_skill != "0":
        return f"{rule.set_bonus_skill} + {rule.group_skill}"
    if rule.set_bonus_skill != "0":
        return rule.set_bonus_skill
    return rule.group_skill


def _normalized_rule(
    rule: TargetRule,
    config: AppConfig,
) -> tuple[str, str] | None:
    set_key = _skill_key(rule.set_bonus_skill, config.set_bonus_skills)
    group_key = _skill_key(rule.group_skill, config.group_skills)
    if not set_key and not group_key:
        return None
    return (set_key, group_key)


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
