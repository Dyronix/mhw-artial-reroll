from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from data.models import AppState, RollResult, TrackedWeapon


class ImportStrategy(Enum):
    ADD = "add"
    MERGE = "merge"
    REPLACE = "replace"
    CANCEL = "cancel"


@dataclass(frozen=True)
class MergePreview:
    existing: TrackedWeapon | None
    conflicts: list[int]


def find_matching_weapon(state: AppState, weapon_type: str, attribute: str) -> TrackedWeapon | None:
    return next(
        (
            weapon
            for weapon in state.tracked_weapons
            if weapon.weapon_type == weapon_type and weapon.attribute == attribute
        ),
        None,
    )


def preview_merge(existing: TrackedWeapon, incoming: TrackedWeapon) -> MergePreview:
    conflicts = []
    for index, incoming_roll in enumerate(incoming.rolls):
        if index >= len(existing.rolls):
            continue
        existing_roll = existing.rolls[index]
        if _is_non_empty(existing_roll) and _is_non_empty(incoming_roll) and existing_roll != incoming_roll:
            conflicts.append(index)
    return MergePreview(existing=existing, conflicts=conflicts)


def import_prerecorded_weapon(
    state: AppState,
    incoming: TrackedWeapon,
    strategy: ImportStrategy,
    overwrite_conflicts: bool = False,
) -> TrackedWeapon | None:
    if strategy == ImportStrategy.CANCEL:
        return None

    existing = find_matching_weapon(state, incoming.weapon_type, incoming.attribute)
    if existing is None or strategy == ImportStrategy.ADD:
        state.tracked_weapons.append(incoming)
        return incoming

    if strategy == ImportStrategy.REPLACE:
        existing.rolls = incoming.rolls
        return existing

    if strategy == ImportStrategy.MERGE:
        _merge_rolls(existing, incoming, overwrite_conflicts=overwrite_conflicts)
        return existing

    return None


def _merge_rolls(
    existing: TrackedWeapon,
    incoming: TrackedWeapon,
    overwrite_conflicts: bool,
) -> None:
    for index, incoming_roll in enumerate(incoming.rolls):
        if index >= len(existing.rolls):
            existing.rolls.append(incoming_roll)
            continue

        existing_roll = existing.rolls[index]
        if not _is_non_empty(existing_roll):
            existing.rolls[index] = incoming_roll
            continue

        if overwrite_conflicts and _is_non_empty(incoming_roll):
            existing.rolls[index] = incoming_roll


def _is_non_empty(roll: RollResult) -> bool:
    return roll.set_bonus_skill != "0" or roll.group_skill != "0" or roll.highlighted
