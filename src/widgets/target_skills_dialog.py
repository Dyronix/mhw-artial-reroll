from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import (
    QComboBox,
    QCompleter,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from data.models import AppConfig, TrackedWeapon
from services.skill_display import skill_completion_options


class SkillSearchLineEdit(QLineEdit):
    def __init__(self, skills: list[str], parent=None) -> None:
        super().__init__(parent)
        completer = QCompleter(skills, self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        self.setCompleter(completer)
        self.textEdited.connect(self.show_filtered_completions)

    def show_all_completions(self) -> None:
        completer = self.completer()
        if completer is None:
            return
        completer.setCompletionPrefix("")
        completer.complete()

    def show_filtered_completions(self) -> None:
        completer = self.completer()
        if completer is None:
            return
        completer.setCompletionPrefix(self.text().strip())
        if completer.completionCount() > 0:
            completer.complete()

    def focusInEvent(self, event) -> None:
        super().focusInEvent(event)
        self.show_all_completions()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        super().mousePressEvent(event)
        self.show_all_completions()


class TargetSkillList(QWidget):
    UNKNOWN_STYLE = "QLineEdit { border: 1px solid #ffb86c; }"

    def __init__(
        self,
        title: str,
        skills: list[str],
        alias_to_display: dict[str, str],
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.alias_to_display = alias_to_display
        self.normalized_aliases = {
            alias.casefold(): display for alias, display in alias_to_display.items()
        }

        label = QLabel(title)
        label.setProperty("role", "section")

        self.input = SkillSearchLineEdit(skills)
        self.input.setPlaceholderText("Add target skill")
        completer = self.input.completer()
        completer.activated[str].connect(self._apply_completion)
        self.input.textChanged.connect(self._update_input_validity)
        self.input.returnPressed.connect(self.add_current_text)

        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add_current_text)
        self.add_button.setEnabled(False)
        self.remove_button = QPushButton("Remove")
        self.remove_button.clicked.connect(self.remove_selected)

        input_row = QHBoxLayout()
        input_row.setSpacing(8)
        input_row.addWidget(self.input, 1)
        input_row.addWidget(self.add_button)
        input_row.addWidget(self.remove_button)

        self.list = QListWidget()
        self.list.setMinimumHeight(112)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(label)
        layout.addLayout(input_row)
        layout.addWidget(self.list)

    def set_values(self, values: list[str]) -> None:
        self.list.clear()
        for value in values:
            self._add_value(value)

    def values(self) -> list[str]:
        return [self.list.item(index).text() for index in range(self.list.count())]

    def add_current_text(self) -> None:
        text = self.input.text().strip()
        value = self._display_for_text(text)
        if value is None:
            self._update_input_validity()
            return
        self._add_value(value)
        self.input.clear()

    def remove_selected(self) -> None:
        for item in self.list.selectedItems():
            row = self.list.row(item)
            self.list.takeItem(row)

    def _apply_completion(self, text: str) -> None:
        self.input.setText(self._display_for_text(text) or text)

    def _display_for_text(self, text: str) -> str | None:
        stripped = text.strip()
        if not stripped:
            return ""
        return self.normalized_aliases.get(stripped.casefold())

    def _add_value(self, value: str) -> None:
        if not value:
            return
        existing = {item.casefold() for item in self.values()}
        if value.casefold() not in existing:
            self.list.addItem(value)

    def _update_input_validity(self) -> None:
        text = self.input.text().strip()
        if text and self._display_for_text(text) is None:
            self.input.setStyleSheet(self.UNKNOWN_STYLE)
            self.input.setToolTip("Unknown skill")
            self.add_button.setEnabled(False)
        else:
            self.input.setStyleSheet("")
            self.input.setToolTip("")
            self.add_button.setEnabled(bool(text))


class TargetSkillsDialog(QDialog):
    def __init__(
        self,
        weapon: TrackedWeapon,
        config: AppConfig,
        parent=None,
        skill_display_mode: str = "source",
    ) -> None:
        super().__init__(parent)
        self.weapon = weapon
        self.setWindowTitle(f"Target Skills - {weapon.display_name}")
        self.resize(640, 460)

        set_skills, set_aliases = skill_completion_options(
            config.set_bonus_skills,
            skill_display_mode,
        )
        group_skills, group_aliases = skill_completion_options(
            config.group_skills,
            skill_display_mode,
        )

        self.mode = QComboBox()
        self.mode.addItem("Any target skill", "any")
        self.mode.addItem("Both skill types when set", "all")
        mode_index = self.mode.findData(weapon.target_match_mode)
        self.mode.setCurrentIndex(max(0, mode_index))

        self.set_targets = TargetSkillList("Set Bonus Targets", set_skills, set_aliases)
        self.group_targets = TargetSkillList("Group Skill Targets", group_skills, group_aliases)
        self.set_targets.set_values(weapon.target_set_bonus_skills)
        self.group_targets.set_values(weapon.target_group_skills)

        mode_row = QHBoxLayout()
        mode_row.setSpacing(8)
        mode_row.addWidget(QLabel("Match"))
        mode_row.addWidget(self.mode)
        mode_row.addStretch(1)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.addLayout(mode_row)
        layout.addWidget(self.set_targets)
        layout.addWidget(self.group_targets)
        layout.addWidget(buttons)

    def accept(self) -> None:
        self.weapon.target_set_bonus_skills = self.set_targets.values()
        self.weapon.target_group_skills = self.group_targets.values()
        self.weapon.target_match_mode = str(self.mode.currentData() or "any")
        super().accept()
