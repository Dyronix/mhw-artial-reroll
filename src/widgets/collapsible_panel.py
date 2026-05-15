from __future__ import annotations

from PySide6.QtWidgets import QFrame, QToolButton, QVBoxLayout, QWidget
from PySide6.QtCore import Qt


class CollapsiblePanel(QFrame):
    def __init__(self, title: str, content: QWidget, expanded: bool = False, parent=None) -> None:
        super().__init__(parent)
        self.setProperty("frameRole", "foldout")
        self.content = content
        self.content.setProperty("frameRole", "foldoutContent")

        self.toggle_button = QToolButton()
        self.toggle_button.setText(title)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(expanded)
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggle_button.clicked.connect(self.set_expanded)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.content)

        self.set_expanded(expanded)

    def set_expanded(self, expanded: bool) -> None:
        self.toggle_button.setChecked(expanded)
        self.toggle_button.setArrowType(Qt.DownArrow if expanded else Qt.RightArrow)
        self.content.setVisible(expanded)

    def set_content_enabled(self, enabled: bool) -> None:
        self.content.setEnabled(enabled)
