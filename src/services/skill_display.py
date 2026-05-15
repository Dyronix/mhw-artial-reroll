from __future__ import annotations

from data.models import Skill


SKILL_DISPLAY_MODES = {
    "source": "Source",
    "name": "Skill Name",
    "source_and_name": "Source (Skill Name)",
}


def skill_display_value(skill: Skill, mode: str) -> str:
    source = skill.source.strip()
    name = skill.name.strip()
    if mode == "name":
        return name
    if mode == "source_and_name" and source and source != name:
        return f"{source} ({name})"
    return source or name


def skill_completion_options(skills: list[Skill], mode: str) -> tuple[list[str], dict[str, str]]:
    values: list[str] = []
    alias_to_display: dict[str, str] = {}
    seen: set[str] = set()
    for skill in skills:
        source = skill.source.strip()
        name = skill.name.strip()
        display = skill_display_value(skill, mode)
        if display and display not in seen:
            values.append(display)
            seen.add(display)

        # Keep exact typed aliases normalizable without showing them in the popup.
        for alias in (display, name, source):
            if alias:
                alias_to_display[alias] = display
    return values, alias_to_display
