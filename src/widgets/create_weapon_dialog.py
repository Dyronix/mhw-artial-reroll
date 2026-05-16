from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
)

from data.models import AppConfig
from services.skill_display import skill_completion_options
from widgets.skill_entry_line_edit import SkillEntryLineEdit


class CreateWeaponDialog(QDialog):
    def __init__(
        self,
        config: AppConfig,
        parent=None,
        manual_mode: bool = False,
        skill_display_mode: str = "source",
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Add Prerecorded Weapon" if manual_mode else "Create New Weapon")

        self.weapon_type = QComboBox()
        self.weapon_type.addItems([item.name for item in config.weapon_types])

        self.attribute = QComboBox()
        self.attribute.addItems(config.attributes)
        self.nickname = QLineEdit()
        self.nickname.setPlaceholderText("Optional row name")
        set_skills, set_aliases = skill_completion_options(config.set_bonus_skills, skill_display_mode)
        group_skills, group_aliases = skill_completion_options(
            config.group_skills,
            skill_display_mode,
        )
        self.current_set_bonus = SkillEntryLineEdit(set_skills, set_aliases)
        self.current_set_bonus.setPlaceholderText("Optional")
        self.current_group_skill = SkillEntryLineEdit(group_skills, group_aliases)
        self.current_group_skill.setPlaceholderText("Optional")

        form = QFormLayout()
        form.addRow("Weapon Type", self.weapon_type)
        form.addRow("Attribute", self.attribute)
        form.addRow("Name", self.nickname)
        form.addRow("Weapon Set Bonus", self.current_set_bonus)
        form.addRow("Weapon Group Skill", self.current_group_skill)

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

    def selected_nickname(self) -> str:
        return self.nickname.text().strip()

    def selected_current_skills(self) -> tuple[str, str]:
        return (
            self.current_set_bonus.resolved_text() or "0",
            self.current_group_skill.resolved_text() or "0",
        )

    def accept(self) -> None:
        unresolved = []
        if self.current_set_bonus.has_unresolved_skill():
            unresolved.append("Weapon Set Bonus")
        if self.current_group_skill.has_unresolved_skill():
            unresolved.append("Weapon Group Skill")
        if unresolved:
            QMessageBox.warning(
                self,
                "Unresolved Skills",
                ", ".join(unresolved) + " must be a known skill or left blank.",
            )
            return
        super().accept()
