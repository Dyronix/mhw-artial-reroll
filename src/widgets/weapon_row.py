from __future__ import annotations

from PySide6.QtCore import QSize, Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from app.font_awesome import font_awesome_icon
from data.models import AppConfig, TrackedWeapon
from services.skill_display import skill_completion_options
from services.target_skills import target_summary
from widgets.roll_strip import RollStrip
from widgets.skill_entry_line_edit import SkillEntryLineEdit


class WeaponRow(QFrame):
    edit_requested = Signal(str)
    accept_next_requested = Signal(str)
    rename_requested = Signal(str, str)
    current_skills_changed = Signal(str, str, str)
    targets_requested = Signal(str)
    delete_requested = Signal(str)

    def __init__(
        self,
        weapon: TrackedWeapon,
        config: AppConfig,
        title: str,
        skill_display_mode: str,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.weapon = weapon
        self.config = config
        self.title_text = title
        self.skill_display_mode = skill_display_mode
        self._rename_in_progress = False
        self._skills_edit_in_progress = False
        self.setProperty("frameRole", "card")

        self.title = QLabel(title)
        self.title.setProperty("role", "section")
        self.title.setCursor(Qt.IBeamCursor)
        self.title.mouseDoubleClickEvent = self._start_rename
        self.title.setToolTip("Double-click to rename this weapon row")
        self.title_editor = QLineEdit()
        self.title_editor.setVisible(False)
        self.title_editor.returnPressed.connect(self._commit_rename)
        self.title_editor.editingFinished.connect(self._finish_rename)
        self.index_label = QLabel()
        self.index_label.setProperty("role", "muted")
        self.current_skills_label = QLabel()
        self.current_skills_label.setProperty("role", "muted")
        self.current_skills_label.setCursor(Qt.IBeamCursor)
        self.current_skills_label.mouseDoubleClickEvent = self._start_skill_edit
        self.current_skills_label.setToolTip("Double-click to edit weapon skills")
        set_skills, set_aliases = skill_completion_options(
            self.config.set_bonus_skills,
            self.skill_display_mode,
        )
        group_skills, group_aliases = skill_completion_options(
            self.config.group_skills,
            self.skill_display_mode,
        )
        self.set_skill_editor = SkillEntryLineEdit(set_skills, set_aliases)
        self.set_skill_editor.setPlaceholderText("Set bonus")
        self.group_skill_editor = SkillEntryLineEdit(group_skills, group_aliases)
        self.group_skill_editor.setPlaceholderText("Group skill")
        self.set_skill_editor.returnPressed.connect(self._commit_skill_edit)
        self.group_skill_editor.returnPressed.connect(self._commit_skill_edit)
        self.set_skill_editor.editingFinished.connect(self._finish_skill_edit)
        self.group_skill_editor.editingFinished.connect(self._finish_skill_edit)
        self.skill_editor = QWidget()
        skill_editor_layout = QHBoxLayout(self.skill_editor)
        skill_editor_layout.setContentsMargins(0, 0, 0, 0)
        skill_editor_layout.setSpacing(8)
        skill_editor_layout.addWidget(self.set_skill_editor, 1)
        skill_editor_layout.addWidget(self.group_skill_editor, 1)
        self.skill_editor.setVisible(False)
        self.targets_label = QLabel()
        self.targets_label.setProperty("role", "muted")
        self.strip = RollStrip()

        edit_button = _icon_button("edit_rolls", "Edit rolls")
        edit_button.clicked.connect(lambda: self.edit_requested.emit(self.weapon.id))
        accept_next_button = _icon_button("accept_next_roll", "Accept next skills and advance all")
        accept_next_button.clicked.connect(lambda: self.accept_next_requested.emit(self.weapon.id))
        targets_button = _icon_button("targets", "Target skills")
        targets_button.clicked.connect(lambda: self.targets_requested.emit(self.weapon.id))
        delete_button = _icon_button("delete_weapon", "Delete weapon")
        delete_button.clicked.connect(lambda: self.delete_requested.emit(self.weapon.id))

        actions = QHBoxLayout()
        actions.setSpacing(8)
        actions.addWidget(edit_button)
        actions.addWidget(accept_next_button)
        actions.addWidget(targets_button)
        actions.addWidget(delete_button)

        top = QGridLayout()
        top.addWidget(self.title, 0, 0)
        top.addWidget(self.title_editor, 0, 0)
        top.addWidget(self.index_label, 1, 0)
        top.addWidget(self.current_skills_label, 2, 0)
        top.addWidget(self.skill_editor, 2, 0)
        top.addWidget(self.targets_label, 3, 0)
        top.addLayout(actions, 0, 1, 4, 1)
        top.setColumnStretch(0, 1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 14)
        layout.setSpacing(10)
        layout.addLayout(top)
        layout.addWidget(self.strip)
        self.refresh()

    def refresh(self) -> None:
        self.title.setText(self.title_text)
        self.index_label.setText(f"Current roll index: {self.weapon.current_index + 1}")
        self.current_skills_label.setText(_current_skills_summary(self.weapon))
        self.targets_label.setText(target_summary(self.weapon))
        self.strip.set_weapon(self.weapon, self.config)

    def _start_rename(self, event) -> None:
        del event
        self._rename_in_progress = True
        self.title_editor.setText(self.weapon.nickname.strip())
        self.title.setVisible(False)
        self.title_editor.setVisible(True)
        self.title_editor.setFocus()
        self.title_editor.selectAll()

    def _commit_rename(self) -> None:
        if not self._rename_in_progress:
            return
        self._rename_in_progress = False
        self.rename_requested.emit(self.weapon.id, self.title_editor.text().strip())
        self.title_editor.setVisible(False)
        self.title.setVisible(True)

    def _finish_rename(self) -> None:
        if self.title_editor.isVisible() and self._rename_in_progress:
            self._rename_in_progress = False
            self.rename_requested.emit(self.weapon.id, self.title_editor.text().strip())
            self.title_editor.setVisible(False)
            self.title.setVisible(True)

    def _start_skill_edit(self, event) -> None:
        del event
        self._skills_edit_in_progress = True
        self.set_skill_editor.setText(
            "" if self.weapon.current_set_bonus_skill == "0" else self.weapon.current_set_bonus_skill
        )
        self.group_skill_editor.setText(
            "" if self.weapon.current_group_skill == "0" else self.weapon.current_group_skill
        )
        self.current_skills_label.setVisible(False)
        self.skill_editor.setVisible(True)
        self.set_skill_editor.setFocus()
        self.set_skill_editor.selectAll()

    def _commit_skill_edit(self) -> None:
        if not self._skills_edit_in_progress:
            return
        if self.set_skill_editor.has_unresolved_skill() or self.group_skill_editor.has_unresolved_skill():
            QMessageBox.warning(
                self,
                "Unresolved Skills",
                "Weapon skills must be known skills or left blank.",
            )
            if self.set_skill_editor.has_unresolved_skill():
                self.set_skill_editor.setFocus()
            else:
                self.group_skill_editor.setFocus()
            return
        self._skills_edit_in_progress = False
        self.current_skills_changed.emit(
            self.weapon.id,
            self.set_skill_editor.resolved_text(),
            self.group_skill_editor.resolved_text(),
        )
        self.skill_editor.setVisible(False)
        self.current_skills_label.setVisible(True)

    def _finish_skill_edit(self) -> None:
        if not self.skill_editor.isVisible() or not self._skills_edit_in_progress:
            return
        QTimer.singleShot(0, self._commit_skill_edit_if_blurred)

    def _commit_skill_edit_if_blurred(self) -> None:
        if self.set_skill_editor.hasFocus() or self.group_skill_editor.hasFocus():
            return
        self._commit_skill_edit()


def _icon_button(icon_name: str, label: str) -> QToolButton:
    button = QToolButton()
    button.setProperty("buttonRole", "iconAction")
    button.setIcon(font_awesome_icon(icon_name))
    button.setIconSize(QSize(16, 16))
    button.setFixedSize(36, 34)
    button.setToolTip(label)
    button.setAccessibleName(label)
    return button


def _current_skills_summary(weapon: TrackedWeapon) -> str:
    if weapon.current_set_bonus_skill == "0" and weapon.current_group_skill == "0":
        return "Current skills: none"
    parts = []
    if weapon.current_set_bonus_skill != "0":
        parts.append(f"Set: {weapon.current_set_bonus_skill}")
    if weapon.current_group_skill != "0":
        parts.append(f"Group: {weapon.current_group_skill}")
    return "Current skills: " + " | ".join(parts)
