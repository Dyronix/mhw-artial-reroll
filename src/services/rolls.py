from __future__ import annotations

from data.models import AppState, RollResult, TrackedWeapon
from services.roll_history import record_roll_history


def advance_all(state: AppState, action: str = "Advanced all rolls") -> None:
    record_roll_history(state, action)
    for weapon in state.tracked_weapons:
        weapon.current_index += 1


def reverse_all(state: AppState) -> bool:
    if not state.roll_history:
        return False

    entry = state.roll_history[-1]
    current_ids = {weapon.id for weapon in state.tracked_weapons}
    snapshot_ids = {weapon.weapon_id for weapon in entry.weapons}
    if current_ids != snapshot_ids:
        return False

    weapons_by_id = {weapon.id: weapon for weapon in state.tracked_weapons}
    for snapshot in entry.weapons:
        weapon = weapons_by_id.get(snapshot.weapon_id)
        if weapon is None:
            return False
        weapon.current_index = max(0, snapshot.roll_index)
        weapon.current_set_bonus_skill = snapshot.roll.set_bonus_skill
        weapon.current_group_skill = snapshot.roll.group_skill

    state.roll_history.pop()
    state.next_history_sequence = max(1, entry.sequence)
    return True


def accept_next_roll_for_weapon(
    state: AppState,
    weapon: TrackedWeapon,
    action: str = "Accepted next roll",
) -> bool:
    roll = next_roll(weapon)
    if roll is None:
        return False
    weapon.current_set_bonus_skill = roll.set_bonus_skill
    weapon.current_group_skill = roll.group_skill
    advance_all(state, action=action)
    return True


def add_weapon_after_craft(
    state: AppState,
    weapon_type: str,
    attribute: str,
    nickname: str = "",
) -> TrackedWeapon:
    advance_all(state, action="Created weapon")
    weapon = TrackedWeapon(weapon_type=weapon_type, attribute=attribute, nickname=nickname)
    state.tracked_weapons.append(weapon)
    return weapon


def current_roll(weapon: TrackedWeapon) -> RollResult | None:
    if weapon.current_index < len(weapon.rolls):
        return weapon.rolls[weapon.current_index]
    return None


def next_roll(weapon: TrackedWeapon) -> RollResult | None:
    next_index = weapon.current_index + 1
    if next_index < len(weapon.rolls):
        return weapon.rolls[next_index]
    return None


def set_rolls(weapon: TrackedWeapon, rolls: list[RollResult]) -> None:
    weapon.rolls = rolls
    if weapon.current_index < 0:
        weapon.current_index = 0
    weapon.current_index = _aligned_current_index(weapon)


def _aligned_current_index(weapon: TrackedWeapon) -> int:
    if not weapon.rolls:
        return 0

    current_roll = RollResult(
        set_bonus_skill=weapon.current_set_bonus_skill,
        group_skill=weapon.current_group_skill,
    )
    for index, roll in enumerate(weapon.rolls):
        if (
            roll.set_bonus_skill == current_roll.set_bonus_skill
            and roll.group_skill == current_roll.group_skill
        ):
            return index

    return 0


def set_current_roll(weapon: TrackedWeapon, roll: RollResult) -> None:
    while len(weapon.rolls) <= weapon.current_index:
        weapon.rolls.append(RollResult())
    weapon.rolls[weapon.current_index] = roll
