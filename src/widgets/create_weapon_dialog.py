from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QVBoxLayout,
)

from data.models import AppConfig


class CreateWeaponDialog(QDialog):
    def __init__(self, config: AppConfig, parent=None, manual_mode: bool = False) -> None:
        super().__init__(parent)
        self.setWindowTitle("Add Prerecorded Weapon" if manual_mode else "Create New Weapon")

        self.weapon_type = QComboBox()
        self.weapon_type.addItems([item.name for item in config.weapon_types])

        self.attribute = QComboBox()
        self.attribute.addItems(config.attributes)

        form = QFormLayout()
        form.addRow("Weapon Type", self.weapon_type)
        form.addRow("Attribute", self.attribute)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        if manual_mode:
            description = QLabel(
                "Manual development-mode additions do not advance global roll state."
            )
            description.setProperty("role", "muted")
            description.setWordWrap(True)
            layout.addWidget(description)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def selected_weapon_type(self) -> str:
        return self.weapon_type.currentText()

    def selected_attribute(self) -> str:
        return self.attribute.currentText()
