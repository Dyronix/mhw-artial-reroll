from __future__ import annotations

from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout

from data.models import AppState, RollResult
from services.rolls import current_roll, next_roll


class CurrentRollsPanel(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setProperty("frameRole", "card")
        self.content = QVBoxLayout()
        self.content.setSpacing(8)

        title = QLabel("Current Active Rolls")
        title.setProperty("role", "section")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 16)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addLayout(self.content)
        layout.addStretch(1)

    def set_state(self, state: AppState) -> None:
        while self.content.count():
            item = self.content.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not state.tracked_weapons:
            empty = QLabel("No tracked weapons")
            empty.setProperty("role", "muted")
            self.content.addWidget(empty)
            return

        for weapon in state.tracked_weapons:
            frame = QFrame()
            frame.setStyleSheet("QFrame { background: transparent; }")
            grid = QGridLayout(frame)
            grid.setContentsMargins(0, 6, 0, 6)
            grid.setHorizontalSpacing(12)
            grid.setVerticalSpacing(4)
            name = QLabel(weapon.display_name)
            name.setStyleSheet("background: transparent; font-weight: 700;")
            grid.addWidget(name, 0, 0, 1, 2)
            grid.addWidget(QLabel(f"Current #{weapon.current_index + 1}"), 1, 0)
            grid.addWidget(QLabel(_roll_summary(current_roll(weapon))), 1, 1)
            grid.addWidget(QLabel(f"Next #{weapon.current_index + 2}"), 2, 0)
            grid.addWidget(QLabel(_roll_summary(next_roll(weapon))), 2, 1)
            grid.setColumnStretch(1, 1)
            self.content.addWidget(frame)


def _roll_summary(roll: RollResult | None) -> str:
    if roll is None:
        return "Not entered"
    parts = []
    if roll.set_bonus_skill != "0":
        parts.append(f"Set: {roll.set_bonus_skill}")
    if roll.group_skill != "0":
        parts.append(f"Group: {roll.group_skill}")
    if not parts:
        return "0"
    suffix = " [highlight]" if roll.highlighted else ""
    return " | ".join(parts) + suffix
