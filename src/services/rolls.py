from __future__ import annotations

from data.models import AppState, RollResult, TrackedWeapon
from services.roll_history import record_roll_history


def advance_all(state: AppState, action: str = "Advanced all rolls") -> None:
    record_roll_history(state, action)
    for weapon in state.tracked_weapons:
        weapon.current_index += 1


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
