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
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from data.models import AppConfig, TargetRule, TrackedWeapon
from services.skill_display import skill_completion_options


class SkillSearchLineEdit(QLineEdit):
    def __init__(self, skills: list[str], parent=None) -> None:
        super().__init__(parent)
        self.completer_widget = QCompleter(skills, self)
        self.completer_widget.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer_widget.setFilterMode(Qt.MatchContains)
        self.setCompleter(self.completer_widget)
        self.textEdited.connect(self.show_filtered_completions)

    def set_skills(self, skills: list[str]) -> None:
        self.completer_widget.model().setStringList(skills)

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


class TargetRuleWizardDialog(QDialog):
    UNKNOWN_STYLE = "QLineEdit { border: 1px solid #ffb86c; }"

    def __init__(
        self,
        set_skills: list[str],
        set_aliases: dict[str, str],
        group_skills: list[str],
        group_aliases: dict[str, str],
        parent=None,
        initial_rule: TargetRule | None = None,
    ) -> None:
        super().__init__(parent)
        self._set_skills = set_skills
        self._set_aliases = set_aliases
        self._group_skills = group_skills
        self._group_aliases = group_aliases
        self.target_rule: TargetRule | None = None

        self.setWindowTitle("Add Target Skill" if initial_rule is None else "Edit Target Skill")
        self.resize(760, 280)

        self.description = QLabel()
        self.description.setProperty("role", "muted")
        self.description.setWordWrap(True)

        self.pages = QStackedWidget()
        self.pages.addWidget(self._build_primary_page())
        self.pages.addWidget(self._build_paired_page())

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self._go_back)
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self._advance)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        button_row = QHBoxLayout()
        button_row.setSpacing(8)
        button_row.addStretch(1)
        button_row.addWidget(self.back_button)
        button_row.addWidget(self.next_button)
        button_row.addWidget(cancel_button)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.addWidget(self.description)
        layout.addWidget(self.pages)
        layout.addLayout(button_row)

        self._apply_initial_rule(initial_rule)
        self._update_primary_skill_options()
        self._refresh_page_state()

    def _build_primary_page(self) -> QWidget:
        page = QWidget()

        self.primary_type = QComboBox()
        self.primary_type.addItem("Set Bonus Skill", "set")
        self.primary_type.addItem("Group Skill", "group")
        self.primary_type.currentIndexChanged.connect(self._update_primary_skill_options)

        self.primary_skill = SkillSearchLineEdit([])
        self.primary_skill.setPlaceholderText("Choose the first target skill")
        self.primary_skill.textChanged.connect(self._refresh_page_state)

        self.match_mode = QComboBox()
        self.match_mode.addItem("Match by itself", "single")
        self.match_mode.addItem("Match with another skill", "paired")
        self.match_mode.currentIndexChanged.connect(self._refresh_page_state)

        type_row = QHBoxLayout()
        type_row.setSpacing(8)
        type_row.addWidget(QLabel("Skill type"))
        type_row.addWidget(self.primary_type, 1)

        skill_row = QHBoxLayout()
        skill_row.setSpacing(8)
        skill_row.addWidget(QLabel("Skill"))
        skill_row.addWidget(self.primary_skill, 1)

        mode_row = QHBoxLayout()
        mode_row.setSpacing(8)
        mode_row.addWidget(QLabel("Target rule"))
        mode_row.addWidget(self.match_mode, 1)

        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addWidget(QLabel("Step 1"))
        layout.addLayout(type_row)
        layout.addLayout(skill_row)
        layout.addLayout(mode_row)
        layout.addStretch(1)
        return page

    def _build_paired_page(self) -> QWidget:
        page = QWidget()

        self.secondary_label = QLabel()
        self.secondary_label.setProperty("role", "section")

        self.secondary_skill = SkillSearchLineEdit([])
        self.secondary_skill.setPlaceholderText("Choose the paired target skill")
        self.secondary_skill.textChanged.connect(self._refresh_page_state)

        row = QHBoxLayout()
        row.setSpacing(8)
        row.addWidget(QLabel("Paired skill"))
        row.addWidget(self.secondary_skill, 1)

        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addWidget(QLabel("Step 2"))
        layout.addWidget(self.secondary_label)
        layout.addLayout(row)
        layout.addStretch(1)
        return page

    def _apply_initial_rule(self, rule: TargetRule | None) -> None:
        if rule is None:
            return
        if rule.set_bonus_skill != "0":
            self.primary_type.setCurrentIndex(self.primary_type.findData("set"))
            self.primary_skill.setText(rule.set_bonus_skill)
            if rule.group_skill != "0":
                self.match_mode.setCurrentIndex(self.match_mode.findData("paired"))
                self.secondary_skill.setText(rule.group_skill)
            return
        self.primary_type.setCurrentIndex(self.primary_type.findData("group"))
        self.primary_skill.setText(rule.group_skill)
        self.match_mode.setCurrentIndex(self.match_mode.findData("single"))

    def _update_primary_skill_options(self) -> None:
        skills, placeholder = self._current_skill_options()
        self.primary_skill.set_skills(skills)
        self.primary_skill.setPlaceholderText(placeholder)
        self._refresh_page_state()

    def _advance(self) -> None:
        if self.pages.currentIndex() == 0:
            primary_skill = self._current_primary_skill()
            if primary_skill is None:
                self._refresh_page_state()
                return
            if str(self.match_mode.currentData() or "single") == "single":
                if str(self.primary_type.currentData() or "set") == "set":
                    self.target_rule = TargetRule(set_bonus_skill=primary_skill)
                else:
                    self.target_rule = TargetRule(group_skill=primary_skill)
                self.accept()
                return
            self.pages.setCurrentIndex(1)
            self._refresh_page_state()
            return

        secondary_skill = self._current_secondary_skill()
        primary_skill = self._current_primary_skill()
        if primary_skill is None or secondary_skill is None:
            self._refresh_page_state()
            return
        if str(self.primary_type.currentData() or "set") == "set":
            self.target_rule = TargetRule(primary_skill, secondary_skill)
        else:
            self.target_rule = TargetRule(secondary_skill, primary_skill)
        self.accept()

    def _go_back(self) -> None:
        if self.pages.currentIndex() == 1:
            self.pages.setCurrentIndex(0)
            self._refresh_page_state()

    def _refresh_page_state(self) -> None:
        is_paired = str(self.match_mode.currentData() or "single") == "paired"
        primary_skill = self._current_primary_skill()

        if self.pages.currentIndex() == 0:
            self.description.setText(
                "Pick the first target skill and decide whether it should match on its own or "
                "only as part of a set + group pairing."
            )
            self.back_button.setEnabled(False)
            self.next_button.setText("Next" if is_paired else "Save")
            self.next_button.setEnabled(primary_skill is not None)
        else:
            other_label = "Group Skill" if str(self.primary_type.currentData() or "set") == "set" else "Set Bonus Skill"
            self.description.setText(
                "Finish the paired target by choosing the required skill from the other skill type."
            )
            self.secondary_label.setText(f"Pair with {other_label}")
            self.secondary_skill.set_skills(
                self._group_skills if other_label == "Group Skill" else self._set_skills
            )
            self.secondary_skill.setPlaceholderText(
                f"Choose the paired {other_label.lower()}"
            )
            self.back_button.setEnabled(True)
            self.next_button.setText("Save")
            self.next_button.setEnabled(secondary_skill_is_valid := (self._current_secondary_skill() is not None))
            if not secondary_skill_is_valid:
                self._update_line_validity(
                    self.secondary_skill,
                    self._current_secondary_skill(),
                )

        self._update_line_validity(self.primary_skill, primary_skill)
        if self.pages.currentIndex() == 1:
            self._update_line_validity(self.secondary_skill, self._current_secondary_skill())

    def _current_skill_options(self) -> tuple[list[str], str]:
        if str(self.primary_type.currentData() or "set") == "set":
            return self._set_skills, "Choose a Set Bonus target skill"
        return self._group_skills, "Choose a Group Skill target skill"

    def _current_alias_map(self) -> dict[str, str]:
        if str(self.primary_type.currentData() or "set") == "set":
            return self._normalized_aliases(self._set_aliases)
        return self._normalized_aliases(self._group_aliases)

    def _current_primary_skill(self) -> str | None:
        return self._resolve_skill(self.primary_skill.text(), self._current_alias_map())

    def _current_secondary_skill(self) -> str | None:
        if str(self.primary_type.currentData() or "set") == "set":
            aliases = self._normalized_aliases(self._group_aliases)
        else:
            aliases = self._normalized_aliases(self._set_aliases)
        return self._resolve_skill(self.secondary_skill.text(), aliases)

    def _resolve_skill(self, text: str, aliases: dict[str, str]) -> str | None:
        stripped = text.strip()
        if not stripped:
            return None
        return aliases.get(stripped.casefold())

    def _update_line_validity(self, line_edit: QLineEdit, value: str | None) -> None:
        if line_edit.text().strip() and value is None:
            line_edit.setStyleSheet(self.UNKNOWN_STYLE)
            line_edit.setToolTip("Unknown skill")
            return
        line_edit.setStyleSheet("")
        line_edit.setToolTip("")

    def _normalized_aliases(self, aliases: dict[str, str]) -> dict[str, str]:
        return {alias.casefold(): display for alias, display in aliases.items()}


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
        self.resize(920, 560)

        self.set_skills, self.set_aliases = skill_completion_options(
            config.set_bonus_skills,
            skill_display_mode,
        )
        self.group_skills, self.group_aliases = skill_completion_options(
            config.group_skills,
            skill_display_mode,
        )
        self.rules = list(weapon.target_rules)

        description = QLabel(
            "Each saved target is one matching rule. A rule can be a single Set Bonus skill, "
            "a single Group Skill, or a required Set Bonus + Group Skill pair."
        )
        description.setProperty("role", "muted")
        description.setWordWrap(True)

        self.list = QListWidget()
        self.list.setMinimumHeight(280)
        self.list.itemSelectionChanged.connect(self._sync_actions)
        self.list.itemDoubleClicked.connect(lambda _: self.edit_selected_rule())

        self.add_button = QPushButton("Add Rule")
        self.add_button.clicked.connect(self.add_rule)
        self.edit_button = QPushButton("Edit Rule")
        self.edit_button.clicked.connect(self.edit_selected_rule)
        self.remove_button = QPushButton("Remove Rule")
        self.remove_button.clicked.connect(self.remove_selected_rule)

        action_row = QHBoxLayout()
        action_row.setSpacing(8)
        action_row.addWidget(self.add_button)
        action_row.addWidget(self.edit_button)
        action_row.addWidget(self.remove_button)
        action_row.addStretch(1)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.addWidget(description)
        layout.addWidget(self.list)
        layout.addLayout(action_row)
        layout.addWidget(buttons)

        self._reload_rules()

    def add_rule(self) -> None:
        dialog = TargetRuleWizardDialog(
            self.set_skills,
            self.set_aliases,
            self.group_skills,
            self.group_aliases,
            self,
        )
        if dialog.exec() != QDialog.Accepted or dialog.target_rule is None:
            return
        if self._has_duplicate(dialog.target_rule):
            QMessageBox.warning(self, "Duplicate Rule", "That target rule already exists.")
            return
        self.rules.append(dialog.target_rule)
        self._reload_rules(selected_rule=dialog.target_rule)

    def edit_selected_rule(self) -> None:
        current_row = self.list.currentRow()
        if current_row < 0 or current_row >= len(self.rules):
            return
        original_rule = self.rules[current_row]
        dialog = TargetRuleWizardDialog(
            self.set_skills,
            self.set_aliases,
            self.group_skills,
            self.group_aliases,
            self,
            initial_rule=original_rule,
        )
        if dialog.exec() != QDialog.Accepted or dialog.target_rule is None:
            return
        if self._has_duplicate(dialog.target_rule, skip_index=current_row):
            QMessageBox.warning(self, "Duplicate Rule", "That target rule already exists.")
            return
        self.rules[current_row] = dialog.target_rule
        self._reload_rules(selected_rule=dialog.target_rule)

    def remove_selected_rule(self) -> None:
        current_row = self.list.currentRow()
        if current_row < 0 or current_row >= len(self.rules):
            return
        del self.rules[current_row]
        self._reload_rules(selected_row=min(current_row, len(self.rules) - 1))

    def _reload_rules(
        self,
        selected_rule: TargetRule | None = None,
        selected_row: int = -1,
    ) -> None:
        self.list.clear()
        for rule in self.rules:
            item = QListWidgetItem(_rule_label(rule))
            item.setData(Qt.UserRole, rule)
            self.list.addItem(item)
        if selected_rule is not None:
            for index, rule in enumerate(self.rules):
                if _rule_key(rule) == _rule_key(selected_rule):
                    self.list.setCurrentRow(index)
                    break
        elif selected_row >= 0:
            self.list.setCurrentRow(selected_row)
        self._sync_actions()

    def _sync_actions(self) -> None:
        has_selection = self.list.currentRow() >= 0
        self.edit_button.setEnabled(has_selection)
        self.remove_button.setEnabled(has_selection)

    def _has_duplicate(self, rule: TargetRule, skip_index: int = -1) -> bool:
        key = _rule_key(rule)
        for index, existing in enumerate(self.rules):
            if index == skip_index:
                continue
            if _rule_key(existing) == key:
                return True
        return False

    def accept(self) -> None:
        self.weapon.target_rules = list(self.rules)
        super().accept()


def _rule_label(rule: TargetRule) -> str:
    if rule.set_bonus_skill != "0" and rule.group_skill != "0":
        return f"Set Bonus: {rule.set_bonus_skill}  +  Group Skill: {rule.group_skill}"
    if rule.set_bonus_skill != "0":
        return f"Set Bonus: {rule.set_bonus_skill}"
    return f"Group Skill: {rule.group_skill}"


def _rule_key(rule: TargetRule) -> tuple[str, str]:
    return (rule.set_bonus_skill.casefold(), rule.group_skill.casefold())
