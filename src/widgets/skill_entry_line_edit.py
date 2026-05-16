from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCompleter, QLineEdit


class SkillEntryLineEdit(QLineEdit):
    UNKNOWN_STYLE = "QLineEdit { border: 1px solid #ffb86c; }"

    def __init__(self, values: list[str], aliases: dict[str, str], parent=None) -> None:
        super().__init__(parent)
        self.aliases = {alias.casefold(): display for alias, display in aliases.items()}
        completer = QCompleter(values, self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        completer.activated[str].connect(self._apply_completion)
        self.setCompleter(completer)
        self.textEdited.connect(self._show_filtered_completions)
        self.textChanged.connect(self._update_validity)

    def resolved_text(self) -> str:
        text = self.text().strip()
        if not text or text == "0":
            return ""
        return self.aliases.get(text.casefold(), "")

    def has_unresolved_skill(self) -> bool:
        text = self.text().strip()
        return bool(text and text != "0" and text.casefold() not in self.aliases)

    def focusInEvent(self, event) -> None:
        super().focusInEvent(event)
        self._show_all_completions()

    def _show_all_completions(self) -> None:
        completer = self.completer()
        if completer is None:
            return
        completer.setCompletionPrefix("")
        completer.complete()

    def _show_filtered_completions(self) -> None:
        completer = self.completer()
        if completer is None:
            return
        completer.setCompletionPrefix(self.text().strip())
        if completer.completionCount() > 0:
            completer.complete()

    def _apply_completion(self, text: str) -> None:
        resolved = self.aliases.get(text.casefold())
        self.setText(resolved or text)

    def _update_validity(self) -> None:
        if self.has_unresolved_skill():
            self.setStyleSheet(self.UNKNOWN_STYLE)
            self.setToolTip("Unknown skill")
            return
        self.setStyleSheet("")
        self.setToolTip("")
