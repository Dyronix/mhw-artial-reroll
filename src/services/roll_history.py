from __future__ import annotations

from data.models import AppState, RollHistoryEntry, RollHistoryWeapon, RollResult, TrackedWeapon


HISTORY_LIMIT = 10


def record_roll_history(state: AppState, action: str) -> None:
    if not state.tracked_weapons:
        return

    entry = RollHistoryEntry(
        sequence=state.next_history_sequence,
        action=action,
        weapons=[_history_weapon(weapon) for weapon in state.tracked_weapons],
    )
    state.next_history_sequence += 1
    state.roll_history.append(entry)
    state.roll_history = state.roll_history[-HISTORY_LIMIT:]


def _history_weapon(weapon: TrackedWeapon) -> RollHistoryWeapon:
    if weapon.current_index < len(weapon.rolls):
        roll = weapon.rolls[weapon.current_index]
        snapshot = RollResult(
            set_bonus_skill=roll.set_bonus_skill,
            group_skill=roll.group_skill,
            highlighted=roll.highlighted,
        )
    else:
        snapshot = RollResult()

    return RollHistoryWeapon(
        weapon_id=weapon.id,
        weapon_type=weapon.weapon_type,
        attribute=weapon.attribute,
        roll_index=weapon.current_index,
        roll=snapshot,
    )
