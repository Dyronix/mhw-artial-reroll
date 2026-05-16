from __future__ import annotations

from PySide6.QtCore import QSize, Signal
from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QToolButton, QVBoxLayout

from app.font_awesome import font_awesome_icon
from data.models import AppConfig, TrackedWeapon
from services.target_skills import target_summary
from widgets.roll_strip import RollStrip


class WeaponRow(QFrame):
    edit_requested = Signal(str)
    targets_requested = Signal(str)
    clear_requested = Signal(str)
    delete_requested = Signal(str)

    def __init__(self, weapon: TrackedWeapon, config: AppConfig, parent=None) -> None:
        super().__init__(parent)
        self.weapon = weapon
        self.config = config
        self.setProperty("frameRole", "card")

        self.title = QLabel(weapon.display_name)
        self.title.setProperty("role", "section")
        self.index_label = QLabel()
        self.index_label.setProperty("role", "muted")
        self.targets_label = QLabel()
        self.targets_label.setProperty("role", "muted")
        self.strip = RollStrip()

        edit_button = _icon_button("edit_rolls", "Edit rolls")
        edit_button.clicked.connect(lambda: self.edit_requested.emit(self.weapon.id))
        targets_button = _icon_button("targets", "Target skills")
        targets_button.clicked.connect(lambda: self.targets_requested.emit(self.weapon.id))
        clear_button = _icon_button("clear_rolls", "Clear rolls")
        clear_button.clicked.connect(lambda: self.clear_requested.emit(self.weapon.id))
        delete_button = _icon_button("delete_weapon", "Delete weapon")
        delete_button.clicked.connect(lambda: self.delete_requested.emit(self.weapon.id))

        actions = QHBoxLayout()
        actions.setSpacing(8)
        actions.addWidget(edit_button)
        actions.addWidget(targets_button)
        actions.addWidget(clear_button)
        actions.addWidget(delete_button)

        top = QGridLayout()
        top.addWidget(self.title, 0, 0)
        top.addWidget(self.index_label, 1, 0)
        top.addWidget(self.targets_label, 2, 0)
        top.addLayout(actions, 0, 1, 3, 1)
        top.setColumnStretch(0, 1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 14)
        layout.setSpacing(10)
        layout.addLayout(top)
        layout.addWidget(self.strip)
        self.refresh()

    def refresh(self) -> None:
        self.title.setText(self.weapon.display_name)
        self.index_label.setText(f"Current roll index: {self.weapon.current_index + 1}")
        self.targets_label.setText(target_summary(self.weapon))
        self.strip.set_weapon(self.weapon, self.config)


def _icon_button(icon_name: str, label: str) -> QToolButton:
    button = QToolButton()
    button.setProperty("buttonRole", "iconAction")
    button.setIcon(font_awesome_icon(icon_name))
    button.setIconSize(QSize(16, 16))
    button.setFixedSize(36, 34)
    button.setToolTip(label)
    button.setAccessibleName(label)
    return button
