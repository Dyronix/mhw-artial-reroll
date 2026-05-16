from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QLabel, QScrollArea, QVBoxLayout, QWidget

from data.models import AppConfig, AppState, weapon_display_name
from widgets.weapon_row import WeaponRow


class Dashboard(QFrame):
    edit_requested = Signal(str)
    rename_requested = Signal(str, str)
    targets_requested = Signal(str)
    clear_requested = Signal(str)
    delete_requested = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.rows_container = QWidget()
        self.rows_layout = QVBoxLayout(self.rows_container)
        self.rows_layout.setContentsMargins(0, 0, 0, 0)
        self.rows_layout.setSpacing(12)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.rows_container)

        title = QLabel("Weapon Roll Dashboard")
        title.setProperty("role", "section")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 16)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addWidget(scroll, 1)

        self.setProperty("frameRole", "card")

    def set_state(self, state: AppState, config: AppConfig) -> None:
        while self.rows_layout.count():
            item = self.rows_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not state.tracked_weapons:
            empty = QLabel("No weapons tracked yet")
            empty.setProperty("role", "muted")
            empty.setAlignment(Qt.AlignCenter)
            self.rows_layout.addWidget(empty, 1)
        else:
            for weapon in state.tracked_weapons:
                row = WeaponRow(weapon, config, weapon_display_name(state, weapon))
                row.edit_requested.connect(self.edit_requested.emit)
                row.rename_requested.connect(self.rename_requested.emit)
                row.targets_requested.connect(self.targets_requested.emit)
                row.clear_requested.connect(self.clear_requested.emit)
                row.delete_requested.connect(self.delete_requested.emit)
                self.rows_layout.addWidget(row)
            self.rows_layout.addStretch(1)
