from __future__ import annotations

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QComboBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QDialog,
)

from data.models import AppConfig, AppState, TrackedWeapon, weapon_display_name
from data.repository import StateRepository
from services.roll_import_service import (
    ImportStrategy,
    find_matching_weapon,
    import_prerecorded_weapon,
    preview_merge,
)
from services.rolls import (
    accept_next_roll_for_weapon,
    add_weapon_after_craft,
    advance_all,
    reverse_all,
)
from widgets.create_weapon_dialog import CreateWeaponDialog
from widgets.current_rolls_panel import CurrentRollsPanel
from widgets.collapsible_panel import CollapsiblePanel
from widgets.dashboard import Dashboard
from widgets.roll_editor import RollEditorDialog
from widgets.skill_encyclopedia_dialog import SkillEncyclopediaDialog
from widgets.target_skills_dialog import TargetSkillsDialog
from services.skill_display import SKILL_DISPLAY_MODES
from app.app_info import APP_WINDOW_TITLE


class MainWindow(QMainWindow):
    def __init__(self, config: AppConfig, repository: StateRepository, state: AppState) -> None:
        super().__init__()
        self.config = config
        self.repository = repository
        self.state = state
        self.development_mode = False
        self.setWindowTitle(APP_WINDOW_TITLE)

        title = QLabel("Gogmazios Artian Reroll Tracker")
        title.setProperty("role", "title")
        subtitle = QLabel("Track Gogmazios weapon roll tables and plan material usage.")
        subtitle.setProperty("role", "subtitle")

        title_block = QVBoxLayout()
        title_block.setContentsMargins(0, 0, 0, 0)
        title_block.setSpacing(2)
        title_block.addWidget(title)
        title_block.addWidget(subtitle)

        self.create_button = QPushButton("Create New Weapon")
        self.create_button.clicked.connect(self.create_weapon)
        self.advance_button = QPushButton("Advance All Rolls")
        self.advance_button.clicked.connect(self.advance_rolls)
        self.skill_encyclopedia_button = QPushButton("Skill Encyclopedia")
        self.skill_encyclopedia_button.clicked.connect(self.open_skill_encyclopedia)
        self.development_button = QPushButton("Development Mode: Off")
        self.development_button.setCheckable(True)
        self.development_button.clicked.connect(self.toggle_development_mode)

        header = QFrame()
        header.setProperty("frameRole", "header")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(18, 14, 18, 14)
        header_layout.setSpacing(12)
        header_layout.addLayout(title_block, 1)
        header_layout.addWidget(self.create_button)
        header_layout.addWidget(self.advance_button)
        header_layout.addWidget(self.skill_encyclopedia_button)
        header_layout.addWidget(self.development_button)

        self.dev_banner = QLabel(
            "Development Mode Active - manual edits will not automatically advance global roll state."
        )
        self.dev_banner.setProperty("role", "banner")
        self.dev_banner.setVisible(False)

        self.dashboard = Dashboard()
        self.dashboard.edit_requested.connect(self.edit_weapon_rolls)
        self.dashboard.accept_next_requested.connect(self.accept_next_roll)
        self.dashboard.rename_requested.connect(self.rename_weapon)
        self.dashboard.current_skills_changed.connect(self.update_weapon_current_skills)
        self.dashboard.targets_requested.connect(self.edit_weapon_targets)
        self.dashboard.clear_requested.connect(self.clear_weapon_rolls)
        self.dashboard.delete_requested.connect(self.delete_weapon)

        self.current_panel = CurrentRollsPanel()
        self.current_panel.setMinimumWidth(360)

        self.actions_panel = self._build_actions_panel()
        self.settings_panel = self._build_settings_panel()

        side = QVBoxLayout()
        side.setContentsMargins(0, 0, 0, 0)
        side.setSpacing(12)
        side.addWidget(self.current_panel, 1)
        side.addWidget(self.settings_panel, 0)
        side.addWidget(self.actions_panel, 0)

        content = QHBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(12)
        content.addWidget(self.dashboard, 1)
        content.addLayout(side, 0)

        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)
        layout.addWidget(header)
        layout.addWidget(self.dev_banner)
        layout.addLayout(content, 1)
        self.setCentralWidget(root)
        self.refresh()

    def _build_actions_panel(self) -> CollapsiblePanel:
        content = QWidget()
        self.add_prerecorded_button = QPushButton("Add Prerecorded Weapon")
        self.add_prerecorded_button.clicked.connect(self.add_prerecorded_weapon)
        self.reverse_rolls_button = QPushButton("Reverse Roll Progress")
        self.reverse_rolls_button.clicked.connect(self.reverse_rolls)
        self.clear_all_button = QPushButton("Clear All Weapons")
        self.clear_all_button.clicked.connect(self.clear_all_weapons)

        self.actions_mode_note = QLabel()
        self.actions_mode_note.setProperty("role", "muted")
        self.actions_mode_note.setWordWrap(True)
        dev_note = QLabel(
            "Use this only for paper notes or prerecord data. It does not advance live roll progress."
        )
        dev_note.setProperty("role", "muted")
        dev_note.setWordWrap(True)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addWidget(self.actions_mode_note)
        layout.addWidget(self.add_prerecorded_button)
        layout.addWidget(self.reverse_rolls_button)
        layout.addWidget(self.clear_all_button)
        layout.addWidget(dev_note)
        return CollapsiblePanel("Actions / Tools", content, expanded=False)

    def _build_settings_panel(self) -> CollapsiblePanel:
        content = QWidget()
        label = QLabel("Skill entry display")
        label.setProperty("role", "muted")

        self.skill_display_combo = QComboBox()
        for key, label_text in SKILL_DISPLAY_MODES.items():
            self.skill_display_combo.addItem(label_text, key)
        self.skill_display_combo.currentIndexChanged.connect(self.update_skill_display_mode)

        note = QLabel("Autocomplete searches both skill names and armor/source names.")
        note.setProperty("role", "muted")
        note.setWordWrap(True)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addWidget(label)
        layout.addWidget(self.skill_display_combo)
        layout.addWidget(note)
        return CollapsiblePanel("Settings", content, expanded=False)

    def create_weapon(self) -> None:
        dialog = CreateWeaponDialog(
            self.config,
            self,
            skill_display_mode=self.state.skill_display_mode,
        )
        if dialog.exec() != QDialog.Accepted:
            return
        weapon = add_weapon_after_craft(
            self.state,
            weapon_type=dialog.selected_weapon_type(),
            attribute=dialog.selected_attribute(),
            nickname=dialog.selected_nickname(),
        )
        (
            weapon.current_set_bonus_skill,
            weapon.current_group_skill,
        ) = dialog.selected_current_skills()
        self.persist_and_refresh()

    def add_prerecorded_weapon(self) -> None:
        if not self.development_mode:
            QMessageBox.information(
                self,
                "Development Mode Required",
                "Enable Development Mode before adding prerecord roll data.",
            )
            return

        dialog = CreateWeaponDialog(
            self.config,
            self,
            manual_mode=True,
            skill_display_mode=self.state.skill_display_mode,
        )
        if dialog.exec() != QDialog.Accepted:
            return

        incoming = TrackedWeapon(
            weapon_type=dialog.selected_weapon_type(),
            attribute=dialog.selected_attribute(),
            nickname=dialog.selected_nickname(),
        )
        (
            incoming.current_set_bonus_skill,
            incoming.current_group_skill,
        ) = dialog.selected_current_skills()
        editor = RollEditorDialog(
            incoming,
            self.config,
            self,
            manual_mode=True,
            skill_display_mode=self.state.skill_display_mode,
        )
        if editor.exec() != QDialog.Accepted:
            return

        strategy, overwrite_conflicts = self._resolve_prerecord_import(incoming)
        if strategy == ImportStrategy.CANCEL:
            return

        imported = import_prerecorded_weapon(
            self.state,
            incoming,
            strategy=strategy,
            overwrite_conflicts=overwrite_conflicts,
        )
        if imported is not None:
            self.persist_and_refresh()

    def clear_all_weapons(self) -> None:
        if not self.development_mode:
            QMessageBox.information(
                self,
                "Development Mode Required",
                "Enable Development Mode before clearing all tracked weapons.",
            )
            return

        if not self.state.tracked_weapons:
            return

        response = QMessageBox.warning(
            self,
            "Clear All Weapons",
            "Remove every tracked weapon and reset roll history?\n\n"
            "This clears all user-entered weapons, recorded rolls, targets, and history.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if response != QMessageBox.Yes:
            return

        self.state.tracked_weapons.clear()
        self.state.roll_history.clear()
        self.state.next_history_sequence = 1
        self.persist_and_refresh()

    def advance_rolls(self) -> None:
        if not self.state.tracked_weapons:
            return
        advance_all(self.state)
        self.persist_and_refresh()

    def reverse_rolls(self) -> None:
        if not self.development_mode:
            QMessageBox.information(
                self,
                "Development Mode Required",
                "Enable Development Mode before reversing roll progress.",
            )
            return
        if not self.state.roll_history:
            return
        if not reverse_all(self.state):
            QMessageBox.warning(
                self,
                "Reverse Unavailable",
                "The most recent history snapshot no longer matches the tracked weapons. "
                "Reverse roll progress is only available while the same weapon set is still tracked.",
            )
            return
        self.persist_and_refresh()

    def open_skill_encyclopedia(self) -> None:
        SkillEncyclopediaDialog(self.config, self).exec()

    def edit_weapon_rolls(self, weapon_id: str) -> None:
        weapon = next((item for item in self.state.tracked_weapons if item.id == weapon_id), None)
        if weapon is None:
            QMessageBox.warning(self, "Weapon Missing", "The selected weapon no longer exists.")
            return
        dialog = RollEditorDialog(
            weapon,
            self.config,
            self,
            manual_mode=self.development_mode,
            skill_display_mode=self.state.skill_display_mode,
        )
        dialog.setWindowTitle(f"Edit Rolls - {weapon_display_name(self.state, weapon)}")
        if dialog.exec() == QDialog.Accepted:
            self.persist_and_refresh()

    def accept_next_roll(self, weapon_id: str) -> None:
        weapon = self._find_weapon(weapon_id)
        if weapon is None:
            QMessageBox.warning(self, "Weapon Missing", "The selected weapon no longer exists.")
            return
        if not accept_next_roll_for_weapon(
            self.state,
            weapon,
            action=f"Accepted next roll for {weapon_display_name(self.state, weapon)}",
        ):
            QMessageBox.information(
                self,
                "Next Roll Missing",
                f"No recorded next roll is available for {weapon_display_name(self.state, weapon)}.",
            )
            return
        self.persist_and_refresh()

    def rename_weapon(self, weapon_id: str, nickname: str) -> None:
        weapon = self._find_weapon(weapon_id)
        if weapon is None:
            QMessageBox.warning(self, "Weapon Missing", "The selected weapon no longer exists.")
            return
        weapon.nickname = nickname.strip()
        self.persist_and_refresh()

    def update_weapon_current_skills(
        self,
        weapon_id: str,
        set_bonus_skill: str,
        group_skill: str,
    ) -> None:
        weapon = self._find_weapon(weapon_id)
        if weapon is None:
            QMessageBox.warning(self, "Weapon Missing", "The selected weapon no longer exists.")
            return
        weapon.current_set_bonus_skill = set_bonus_skill or "0"
        weapon.current_group_skill = group_skill or "0"
        self.persist_and_refresh()

    def edit_weapon_targets(self, weapon_id: str) -> None:
        weapon = self._find_weapon(weapon_id)
        if weapon is None:
            QMessageBox.warning(self, "Weapon Missing", "The selected weapon no longer exists.")
            return
        dialog = TargetSkillsDialog(
            weapon,
            self.config,
            self,
            skill_display_mode=self.state.skill_display_mode,
        )
        dialog.setWindowTitle(f"Target Skills - {weapon_display_name(self.state, weapon)}")
        if dialog.exec() == QDialog.Accepted:
            self.persist_and_refresh()

    def clear_weapon_rolls(self, weapon_id: str) -> None:
        weapon = self._find_weapon(weapon_id)
        if weapon is None:
            QMessageBox.warning(self, "Weapon Missing", "The selected weapon no longer exists.")
            return
        response = QMessageBox.warning(
            self,
            "Clear Weapon Rolls",
            f"Clear all recorded rolls for {weapon_display_name(self.state, weapon)}?\n\n"
            "The weapon will remain tracked and its current index will be kept.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if response != QMessageBox.Yes:
            return
        weapon.rolls.clear()
        self.persist_and_refresh()

    def delete_weapon(self, weapon_id: str) -> None:
        weapon = self._find_weapon(weapon_id)
        if weapon is None:
            QMessageBox.warning(self, "Weapon Missing", "The selected weapon no longer exists.")
            return
        response = QMessageBox.warning(
            self,
            "Delete Weapon",
            f"Delete {weapon_display_name(self.state, weapon)}?\n\n"
            "This removes the weapon and its recorded rolls from the dashboard.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if response != QMessageBox.Yes:
            return
        self.state.tracked_weapons = [
            item for item in self.state.tracked_weapons if item.id != weapon_id
        ]
        self.persist_and_refresh()

    def _find_weapon(self, weapon_id: str) -> TrackedWeapon | None:
        return next((item for item in self.state.tracked_weapons if item.id == weapon_id), None)

    def update_skill_display_mode(self) -> None:
        mode = self.skill_display_combo.currentData()
        if mode and mode != self.state.skill_display_mode:
            self.state.skill_display_mode = mode
            self.repository.save(self.state)

    def toggle_development_mode(self) -> None:
        if self.development_button.isChecked():
            response = QMessageBox.warning(
                self,
                "Enable Development Mode",
                "Development Mode lets you manually add or edit prerecord roll data. "
                "This is useful for entering notes from paper, but it can desync your "
                "current tracking state if used during live rolling. Only continue if "
                "you know this data should be added manually.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if response != QMessageBox.Yes:
                self.development_button.setChecked(False)
                return
            self.development_mode = True
        else:
            self.development_mode = False
        self.refresh()

    def _resolve_prerecord_import(self, incoming: TrackedWeapon) -> tuple[ImportStrategy, bool]:
        existing = find_matching_weapon(self.state, incoming.weapon_type, incoming.attribute)
        if existing is None:
            return ImportStrategy.ADD, False

        message = QMessageBox(self)
        message.setIcon(QMessageBox.Warning)
        message.setWindowTitle("Existing Weapon Found")
        message.setText(
            f"{weapon_display_name(self.state, existing)} already exists.\n\n"
            "Merge fills missing roll slots and appends new slots. Replace overwrites existing roll data."
        )
        merge_button = message.addButton("Merge", QMessageBox.AcceptRole)
        replace_button = message.addButton("Replace", QMessageBox.DestructiveRole)
        cancel_button = message.addButton("Cancel", QMessageBox.RejectRole)
        message.exec()

        clicked = message.clickedButton()
        if clicked == cancel_button:
            return ImportStrategy.CANCEL, False

        if clicked == replace_button:
            response = QMessageBox.warning(
                self,
                "Replace Roll Data",
                f"Replace all recorded roll data for {weapon_display_name(self.state, existing)}?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            return (
                (ImportStrategy.REPLACE, False)
                if response == QMessageBox.Yes
                else (ImportStrategy.CANCEL, False)
            )

        if clicked == merge_button:
            preview = preview_merge(existing, incoming)
            if not preview.conflicts:
                return ImportStrategy.MERGE, False
            response = QMessageBox.warning(
                self,
                "Merge Conflicts",
                f"{len(preview.conflicts)} incoming roll slot(s) overlap existing non-empty data.\n\n"
                "Overwrite those existing entries while merging?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                QMessageBox.No,
            )
            if response == QMessageBox.Cancel:
                return ImportStrategy.CANCEL, False
            return ImportStrategy.MERGE, response == QMessageBox.Yes

        return ImportStrategy.CANCEL, False

    def persist_and_refresh(self) -> None:
        self.repository.save(self.state)
        self.refresh()

    def refresh(self) -> None:
        self.dashboard.set_state(self.state, self.config)
        self.current_panel.set_state(self.state)
        self.dev_banner.setVisible(self.development_mode)
        self.actions_panel.setVisible(self.development_mode)
        self.actions_panel.set_content_enabled(self.development_mode)
        can_reverse_rolls = self.development_mode and self._can_reverse_rolls()
        self.reverse_rolls_button.setEnabled(can_reverse_rolls)
        self.clear_all_button.setEnabled(self.development_mode and bool(self.state.tracked_weapons))
        self.actions_mode_note.setText(
            "Development Mode is on. Manual additions here will not advance global roll indexes."
            if self.development_mode
            else "Development-only tools are disabled. Enable Development Mode to enter paper notes."
        )
        self.development_button.setChecked(self.development_mode)
        self.development_button.setText(
            "Development Mode: On" if self.development_mode else "Development Mode: Off"
        )
        index = self.skill_display_combo.findData(self.state.skill_display_mode)
        if index < 0:
            index = self.skill_display_combo.findData("source")
        blocked = self.skill_display_combo.blockSignals(True)
        self.skill_display_combo.setCurrentIndex(index)
        self.skill_display_combo.blockSignals(blocked)

    def _can_reverse_rolls(self) -> bool:
        if not self.state.roll_history:
            return False
        current_ids = {weapon.id for weapon in self.state.tracked_weapons}
        snapshot_ids = {weapon.weapon_id for weapon in self.state.roll_history[-1].weapons}
        return bool(current_ids) and current_ids == snapshot_ids
