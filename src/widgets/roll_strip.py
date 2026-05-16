from __future__ import annotations

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget

from app.theme import DRACULA
from data.models import AppConfig, TrackedWeapon
from services.target_skills import roll_matches_targets


class RollStrip(QScrollArea):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.container = QWidget()
        self.layout = QHBoxLayout(self.container)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(6)
        self.setWidget(self.container)
        self.setMinimumHeight(92)
        self.current_card: QFrame | None = None

    def set_weapon(self, weapon: TrackedWeapon, config: AppConfig) -> None:
        self.current_card = None
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not weapon.rolls and weapon.current_index == 0:
            label = QLabel("No rolls entered")
            label.setProperty("role", "muted")
            self.layout.addWidget(label)
            self.layout.addStretch(1)
            return

        start_index = max(0, weapon.current_index - 10)
        end_index = max(len(weapon.rolls), weapon.current_index + 1)

        for index in range(start_index, end_index):
            roll = weapon.rolls[index] if index < len(weapon.rolls) else None
            card = QFrame()
            card.setFixedSize(132, 70)
            card.setFrameShape(QFrame.NoFrame)
            background, border, text_color = _roll_colors(
                is_current=index == weapon.current_index,
                is_history=index < weapon.current_index,
                is_highlighted=bool(roll and roll.highlighted),
                is_target=roll_matches_targets(roll, weapon, config),
                is_useful=bool(roll and roll.useful()),
            )
            card.setStyleSheet(
                "QFrame {"
                f"background: {background};"
                f"border: 1px solid {border};"
                "border-radius: 6px;"
                "}"
            )
            layout = QVBoxLayout(card)
            layout.setContentsMargins(8, 6, 8, 6)
            layout.setSpacing(2)
            text = QLabel(
                _roll_title(
                    index,
                    highlighted=bool(roll and roll.highlighted),
                    is_current=index == weapon.current_index,
                    is_history=index < weapon.current_index,
                )
            )
            text.setAlignment(Qt.AlignCenter)
            text.setStyleSheet(f"background: transparent; color: {text_color}; font-weight: 700;")
            details = QLabel(_roll_details(roll))
            details.setAlignment(Qt.AlignCenter)
            details.setWordWrap(True)
            details.setStyleSheet(f"background: transparent; color: {text_color}; font-size: 11px;")
            layout.addWidget(text)
            layout.addWidget(details)
            self.layout.addWidget(card)
            if index == weapon.current_index:
                self.current_card = card
        self.layout.addStretch(1)
        QTimer.singleShot(0, self.focus_current_roll)

    def focus_current_roll(self) -> None:
        if self.current_card is not None:
            self.ensureWidgetVisible(self.current_card, xmargin=260, ymargin=0)


def _roll_title(index: int, highlighted: bool, is_current: bool, is_history: bool) -> str:
    if is_current:
        marker = "Current"
    elif highlighted:
        marker = "Highlight"
    elif is_history:
        marker = "Past"
    else:
        marker = "Roll"
    return f"{marker} #{index + 1}"


def _roll_details(roll) -> str:
    if roll is None or not roll.useful():
        return "Unknown"
    parts = []
    if roll.set_bonus_skill != "0":
        parts.append("Set")
    if roll.group_skill != "0":
        parts.append("Group")
    return " + ".join(parts)


def _roll_colors(
    is_current: bool,
    is_history: bool,
    is_highlighted: bool,
    is_target: bool,
    is_useful: bool,
) -> tuple[str, str, str]:
    if is_current and is_highlighted:
        return DRACULA["selection"], DRACULA["green"], DRACULA["green"]
    if is_current and is_target:
        return DRACULA["selection"], DRACULA["pink"], DRACULA["foreground"]
    if is_current:
        return DRACULA["selection"], DRACULA["cyan"], DRACULA["foreground"]
    if is_highlighted:
        return "#24382f", DRACULA["green"], DRACULA["green"]
    if is_target and is_history:
        return "#332734", "#c96aa0", DRACULA["muted"]
    if is_target:
        return "#3a2838", DRACULA["pink"], DRACULA["foreground"]
    if is_history and is_useful:
        return "#242b33", "#5f9ead", DRACULA["muted"]
    if is_useful:
        return "#24313a", DRACULA["cyan"], DRACULA["foreground"]
    if is_history:
        return "#242631", DRACULA["selection"], DRACULA["muted"]
    return "#21222c", DRACULA["panel_alt"], DRACULA["muted"]
