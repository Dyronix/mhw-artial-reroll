from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from data.models import AppState, RollResult, weapon_display_name
from services.rolls import current_roll, next_roll
from widgets.weapon_icon_utils import load_attribute_icon, load_weapon_icon, skill_summary_html


class CurrentRollsPanel(QFrame):
    accept_next_requested = Signal(str)

    def __init__(self, advance_button: QPushButton | None = None, parent=None) -> None:
        super().__init__(parent)
        self.setProperty("frameRole", "card")
        self.rows_container = QWidget()
        self.rows_container.setProperty("frameRole", "inset")
        self.content = QVBoxLayout(self.rows_container)
        self.content.setContentsMargins(12, 12, 12, 12)
        self.content.setSpacing(8)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidget(self.rows_container)

        self.advance_button = advance_button or QPushButton("Advance All Rolls")

        title = QLabel("Current Active Rolls")
        title.setProperty("role", "section")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 16)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addWidget(scroll, 1)
        layout.addWidget(self.advance_button, 0, Qt.AlignBottom)

    def set_state(self, state: AppState) -> None:
        while self.content.count():
            item = self.content.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not state.tracked_weapons:
            empty = QLabel("No tracked weapons")
            empty.setProperty("role", "muted")
            empty.setAlignment(Qt.AlignCenter)
            self.content.addWidget(empty)
            return

        for weapon in state.tracked_weapons:
            frame = _CurrentRollCard(weapon.id)
            frame.setToolTip(
                f"Accept the next recorded skills for {weapon_display_name(state, weapon)} and advance its roll."
            )
            frame.clicked.connect(self.accept_next_requested.emit)
            grid = QGridLayout(frame)
            grid.setContentsMargins(0, 6, 0, 6)
            grid.setHorizontalSpacing(12)
            grid.setVerticalSpacing(6)
            header = QWidget()
            header_layout = QHBoxLayout(header)
            header_layout.setContentsMargins(0, 0, 0, 0)
            header_layout.setSpacing(8)
            weapon_icon = QLabel()
            weapon_icon.setFixedSize(22, 22)
            attribute_icon = QLabel()
            attribute_icon.setFixedSize(22, 22)
            _set_icon_label(weapon_icon, load_weapon_icon(weapon.weapon_type, size=22))
            _set_icon_label(attribute_icon, load_attribute_icon(weapon.attribute, size=22))
            name = QLabel(weapon_display_name(state, weapon))
            name.setStyleSheet("background: transparent; font-weight: 700;")
            header_layout.addWidget(weapon_icon)
            header_layout.addWidget(attribute_icon)
            header_layout.addWidget(name, 1)
            grid.addWidget(header, 0, 0, 1, 2)
            grid.addWidget(QLabel(f"Current #{weapon.current_index + 1}"), 1, 0)
            grid.addWidget(QLabel(_roll_summary(current_roll(weapon))), 1, 1)
            grid.addWidget(QLabel(f"Next #{weapon.current_index + 2}"), 2, 0)
            grid.addWidget(QLabel(_roll_summary(next_roll(weapon))), 2, 1)
            hint = QLabel("Click card to accept next skills and advance")
            hint.setProperty("role", "muted")
            grid.addWidget(hint, 3, 0, 1, 2)
            grid.setColumnStretch(1, 1)
            self.content.addWidget(frame)


def _roll_summary(roll: RollResult | None) -> str:
    if roll is None:
        return "Not entered"
    return skill_summary_html(
        set_bonus_skill=roll.set_bonus_skill,
        group_skill=roll.group_skill,
        empty_text="0",
        highlighted=roll.highlighted,
    )


def _set_icon_label(label: QLabel, pixmap: QPixmap | None) -> None:
    if pixmap is None:
        label.clear()
        return
    label.setPixmap(pixmap)


class _CurrentRollCard(QFrame):
    clicked = Signal(str)

    def __init__(self, weapon_id: str, parent=None) -> None:
        super().__init__(parent)
        self.weapon_id = weapon_id
        self.setProperty("frameRole", "currentRollItem")
        self.setCursor(Qt.PointingHandCursor)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.LeftButton and self.rect().contains(event.position().toPoint()):
            self.clicked.emit(self.weapon_id)
        super().mouseReleaseEvent(event)
