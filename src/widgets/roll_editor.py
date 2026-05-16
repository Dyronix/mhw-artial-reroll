from __future__ import annotations

from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtGui import QKeyEvent, QMouseEvent
from PySide6.QtWidgets import (
    QAbstractItemView,
    QAbstractSpinBox,
    QCheckBox,
    QCompleter,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from data.models import AppConfig, RollResult, TrackedWeapon
from services.skill_display import skill_completion_options


class SkillLineEdit(QLineEdit):
    move_requested = None
    UNKNOWN_STYLE = "QLineEdit { border: 1px solid #ffb86c; }"

    def __init__(
        self,
        skills: list[str],
        alias_to_display: dict[str, str],
        table: QTableWidget,
        row: int,
        col: int,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.table = table
        self.row = row
        self.col = col
        self.alias_to_display = alias_to_display
        self.normalized_aliases = {
            alias.casefold(): display for alias, display in alias_to_display.items()
        }
        completer = QCompleter(skills, self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        completer.activated[str].connect(self.apply_completion)
        self.setCompleter(completer)
        self.textEdited.connect(self.show_filtered_completions)
        self.textChanged.connect(self.update_validity)

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

    def apply_completion(self, text: str) -> None:
        self.setText(self._display_for_text(text) or text)

    def normalized_text(self) -> str:
        text = self.text().strip()
        return self._display_for_text(text) or text

    def resolved_text(self) -> str:
        text = self.text().strip()
        if not text or text == "0":
            return ""
        return self._display_for_text(text) or ""

    def has_unresolved_skill(self) -> bool:
        text = self.text().strip()
        return bool(text and text != "0" and self._display_for_text(text) is None)

    def update_validity(self) -> None:
        if self.has_unresolved_skill():
            self.setStyleSheet(self.UNKNOWN_STYLE)
            self.setToolTip("Unknown skill")
        else:
            self.setStyleSheet("")
            self.setToolTip("")

    def completion_count_for_text(self) -> int:
        completer = self.completer()
        if completer is None:
            return 0
        completer.setCompletionPrefix(self.text().strip())
        return completer.completionCount()

    def apply_single_or_current_completion(self) -> bool:
        completer = self.completer()
        if completer is None:
            return False

        popup = completer.popup()
        current = popup.currentIndex() if popup is not None else None
        text = self.text().strip()
        if (
            text
            and completer.completionPrefix() == text
            and current is not None
            and current.isValid()
        ):
            self.apply_completion(str(current.data()))
            if popup is not None:
                popup.hide()
            return True

        completer.setCompletionPrefix(text)
        if completer.completionCount() == 1:
            index = completer.completionModel().index(0, 0)
            self.apply_completion(str(index.data()))
            return True
        return False

    def select_completion(self, step: int) -> bool:
        completer = self.completer()
        if completer is None:
            return False

        completer.setCompletionPrefix(self.text().strip())
        count = completer.completionCount()
        if count <= 0:
            return False

        popup = completer.popup()
        if popup is None:
            return False

        if not popup.isVisible():
            completer.complete()

        current = popup.currentIndex()
        next_row = 0 if step > 0 else count - 1
        if current.isValid():
            next_row = (current.row() + step) % count
        index = completer.completionModel().index(next_row, 0)
        popup.setCurrentIndex(index)
        return True

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if self.apply_single_or_current_completion():
                return
            self.table.setCurrentCell(self.row, min(self.col + 1, self.table.columnCount() - 1))
            self.table.cellWidget(self.row, self.table.currentColumn()).setFocus()
            return
        if event.key() in (Qt.Key_Tab, Qt.Key_Backtab) and self.completion_count_for_text() > 0:
            step = -1 if event.key() == Qt.Key_Backtab else 1
            if self.select_completion(step):
                return
        if event.key() == Qt.Key_Right:
            self.table.setCurrentCell(self.row, min(self.col + 1, self.table.columnCount() - 1))
            self.table.cellWidget(self.row, self.table.currentColumn()).setFocus()
            return
        if event.key() == Qt.Key_Left:
            self.table.setCurrentCell(self.row, max(self.col - 1, 0))
            self.table.cellWidget(self.row, self.table.currentColumn()).setFocus()
            return
        super().keyPressEvent(event)

    def focusInEvent(self, event) -> None:
        super().focusInEvent(event)
        self.show_all_completions()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        super().mousePressEvent(event)
        self.show_all_completions()

    def event(self, event) -> bool:
        if (
            event.type() == QEvent.KeyPress
            and event.key() in (Qt.Key_Tab, Qt.Key_Backtab)
            and self.completion_count_for_text() > 0
        ):
            step = -1 if event.key() == Qt.Key_Backtab else 1
            return self.select_completion(step)
        return super().event(event)

    def _display_for_text(self, text: str) -> str | None:
        return self.normalized_aliases.get(text.strip().casefold())


class RollCountSpinBox(QSpinBox):
    apply_requested = Signal(int)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            previous_value = self.value()
            self.interpretText()
            if self.value() == previous_value:
                self.apply_requested.emit(self.value())
            event.accept()
            return
        super().keyPressEvent(event)


class RollEditorDialog(QDialog):
    def __init__(
        self,
        weapon: TrackedWeapon,
        config: AppConfig,
        parent=None,
        manual_mode: bool = False,
        skill_display_mode: str = "source",
    ) -> None:
        super().__init__(parent)
        self.weapon = weapon
        self.config = config
        self.skill_display_mode = skill_display_mode
        self.original_rolls = [
            RollResult(roll.set_bonus_skill, roll.group_skill, roll.highlighted)
            for roll in weapon.rolls
        ]
        mode_label = "Prerecord Rolls" if manual_mode else "Edit Rolls"
        self.setWindowTitle(f"{mode_label} - {weapon.display_name}")
        self.resize(1120, 420)

        self.roll_count = RollCountSpinBox()
        self.roll_count.setRange(1, 250)
        self.roll_count.setButtonSymbols(QAbstractSpinBox.PlusMinus)
        self.roll_count.setKeyboardTracking(False)
        self.roll_count.setValue(max(20, len(weapon.rolls), weapon.current_index + 2))
        self.roll_count.valueChanged.connect(self.rebuild_table)
        self.roll_count.apply_requested.connect(self.rebuild_table)

        resize_button = QPushButton("Apply Roll Count")
        resize_button.clicked.connect(lambda: self.rebuild_table(self.roll_count.value()))

        controls = QHBoxLayout()
        controls.setSpacing(10)
        controls.addWidget(QLabel("Roll slots"))
        controls.addWidget(self.roll_count)
        controls.addWidget(resize_button)
        controls.addStretch(1)
        if manual_mode:
            note = QLabel("Development Mode: saving does not advance global progression.")
            note.setProperty("role", "warning")
            controls.addWidget(note)

        self.table = QTableWidget()
        self.table.setRowCount(3)
        self.table.setVerticalHeaderLabels(["Set Bonus", "Group Skill", "Highlight"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.table.horizontalHeader().setDefaultSectionSize(154)
        self.table.horizontalHeader().setMinimumSectionSize(154)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(controls)
        layout.addWidget(self.table)
        layout.addWidget(buttons)

        self.rebuild_table(self.roll_count.value())

    def rebuild_table(self, count: int) -> None:
        existing = self._collect_rolls(confirm_blanks=False)
        if not existing:
            existing = list(self.weapon.rolls)

        self.table.clearContents()
        self.table.setColumnCount(count)
        self.table.setHorizontalHeaderLabels([str(index + 1) for index in range(count)])

        set_skills, set_aliases = skill_completion_options(
            self.config.set_bonus_skills,
            self.skill_display_mode,
        )
        group_skills, group_aliases = skill_completion_options(
            self.config.group_skills,
            self.skill_display_mode,
        )
        for col in range(count):
            roll = existing[col] if col < len(existing) else RollResult()
            set_edit = SkillLineEdit(set_skills, set_aliases, self.table, 0, col)
            set_edit.setText("" if roll.set_bonus_skill == "0" else roll.set_bonus_skill)
            group_edit = SkillLineEdit(group_skills, group_aliases, self.table, 1, col)
            group_edit.setText("" if roll.group_skill == "0" else roll.group_skill)

            checkbox = QCheckBox()
            checkbox.setChecked(roll.highlighted and roll.useful())
            checkbox.setEnabled(roll.useful())
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            checkbox_layout.addWidget(checkbox)

            set_edit.textChanged.connect(lambda _text, c=col: self._update_highlight_enabled(c))
            group_edit.textChanged.connect(lambda _text, c=col: self._update_highlight_enabled(c))

            self.table.setCellWidget(0, col, set_edit)
            self.table.setCellWidget(1, col, group_edit)
            self.table.setCellWidget(2, col, checkbox_widget)

    def accept(self) -> None:
        rolls = self._collect_rolls(confirm_blanks=True)
        if rolls is None:
            return
        if not self._confirm_destructive_changes(rolls):
            return
        self.weapon.rolls = rolls
        super().accept()

    def _collect_rolls(self, confirm_blanks: bool) -> list[RollResult] | None:
        if self.table.columnCount() == 0:
            return []
        unresolved_count = self._unresolved_skill_count()
        if confirm_blanks and unresolved_count:
            response = QMessageBox.warning(
                self,
                "Unresolved Skills",
                f"You have {unresolved_count} unresolved skill"
                f"{'' if unresolved_count == 1 else 's'}, saving will clear the unresolved skills. "
                "Are you sure you want to save?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if response != QMessageBox.Yes:
                return None

        has_blank_cells = False
        rolls = []
        for col in range(self.table.columnCount()):
            set_text = self._line_text(0, col)
            group_text = self._line_text(1, col)
            highlighted = self._checkbox_checked(col)
            if not set_text or not group_text:
                has_blank_cells = True
            roll = RollResult(
                set_bonus_skill=set_text or "0",
                group_skill=group_text or "0",
                highlighted=highlighted and bool(set_text or group_text),
            )
            rolls.append(roll)

        if confirm_blanks and has_blank_cells:
            response = QMessageBox.question(
                self,
                "Accept Blank Rolls",
                "Blank skill cells will be saved as 0. Continue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if response != QMessageBox.Yes:
                return None
        return rolls

    def _line_text(self, row: int, col: int) -> str:
        widget = self.table.cellWidget(row, col)
        if isinstance(widget, SkillLineEdit):
            text = widget.resolved_text()
            return "" if text == "0" else text
        if isinstance(widget, QLineEdit):
            text = widget.text().strip()
            return "" if text == "0" else text
        return ""

    def _unresolved_skill_count(self) -> int:
        count = 0
        for row in (0, 1):
            for col in range(self.table.columnCount()):
                widget = self.table.cellWidget(row, col)
                if isinstance(widget, SkillLineEdit) and widget.has_unresolved_skill():
                    count += 1
        return count

    def _checkbox_checked(self, col: int) -> bool:
        checkbox = self._checkbox(col)
        return bool(checkbox and checkbox.isChecked())

    def _checkbox(self, col: int) -> QCheckBox | None:
        wrapper = self.table.cellWidget(2, col)
        if wrapper is None:
            return None
        return wrapper.findChild(QCheckBox)

    def _update_highlight_enabled(self, col: int) -> None:
        checkbox = self._checkbox(col)
        if checkbox is None:
            return
        useful = bool(self._line_text(0, col) or self._line_text(1, col))
        checkbox.setEnabled(useful)
        if not useful:
            checkbox.setChecked(False)

    def _confirm_destructive_changes(self, new_rolls: list[RollResult]) -> bool:
        clearing = 0
        overwriting = 0
        for index, original in enumerate(self.original_rolls):
            new = new_rolls[index] if index < len(new_rolls) else RollResult()
            original_non_empty = original.set_bonus_skill != "0" or original.group_skill != "0"
            new_non_empty = new.set_bonus_skill != "0" or new.group_skill != "0"
            if original_non_empty and not new_non_empty:
                clearing += 1
            elif original_non_empty and new_non_empty and original != new:
                overwriting += 1

        messages = []
        if clearing:
            messages.append(f"{clearing} existing roll entr{'y' if clearing == 1 else 'ies'} will be cleared")
        if overwriting:
            messages.append(
                f"{overwriting} existing roll entr{'y' if overwriting == 1 else 'ies'} will be overwritten"
            )
        if not messages:
            return True

        response = QMessageBox.warning(
            self,
            "Confirm Roll Changes",
            "\n".join(messages) + "\n\nContinue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        return response == QMessageBox.Yes
