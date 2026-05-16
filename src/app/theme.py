from __future__ import annotations

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

from app.path_utils import asset_path


DRACULA = {
    "background": "#282a36",
    "panel": "#343746",
    "panel_alt": "#3f4254",
    "foreground": "#f8f8f2",
    "muted": "#b7b9c7",
    "selection": "#44475a",
    "purple": "#bd93f9",
    "pink": "#ff79c6",
    "green": "#50fa7b",
    "cyan": "#8be9fd",
    "orange": "#ffb86c",
    "red": "#ff5555",
}


def apply_dracula_theme(app: QApplication) -> None:
    spinbox_plus_icon = asset_path("icons", "ui", "spinbox_plus.svg").as_posix()
    spinbox_minus_icon = asset_path("icons", "ui", "spinbox_minus.svg").as_posix()

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(DRACULA["background"]))
    palette.setColor(QPalette.WindowText, QColor(DRACULA["foreground"]))
    palette.setColor(QPalette.Base, QColor("#21222c"))
    palette.setColor(QPalette.AlternateBase, QColor(DRACULA["panel"]))
    palette.setColor(QPalette.ToolTipBase, QColor(DRACULA["panel_alt"]))
    palette.setColor(QPalette.ToolTipText, QColor(DRACULA["foreground"]))
    palette.setColor(QPalette.Text, QColor(DRACULA["foreground"]))
    palette.setColor(QPalette.Button, QColor(DRACULA["panel"]))
    palette.setColor(QPalette.ButtonText, QColor(DRACULA["foreground"]))
    palette.setColor(QPalette.BrightText, QColor(DRACULA["red"]))
    palette.setColor(QPalette.Highlight, QColor(DRACULA["purple"]))
    palette.setColor(QPalette.HighlightedText, QColor("#191a21"))
    app.setPalette(palette)

    app.setStyleSheet(
        f"""
        QWidget {{
            background: {DRACULA["background"]};
            color: {DRACULA["foreground"]};
            font-size: 13px;
        }}
        QToolTip {{
            background: {DRACULA["panel_alt"]};
            color: {DRACULA["foreground"]};
            border: 1px solid {DRACULA["purple"]};
            border-radius: 4px;
            padding: 4px 6px;
        }}
        QMainWindow, QDialog {{
            background: {DRACULA["background"]};
        }}
        QLabel[role="title"] {{
            background: transparent;
            font-size: 24px;
            font-weight: 700;
            color: {DRACULA["green"]};
        }}
        QLabel[role="subtitle"] {{
            background: transparent;
            color: {DRACULA["muted"]};
            font-size: 13px;
        }}
        QLabel[role="section"] {{
            background: transparent;
            font-size: 15px;
            font-weight: 700;
            color: {DRACULA["foreground"]};
        }}
        QLabel[role="muted"] {{
            background: transparent;
            color: {DRACULA["muted"]};
        }}
        QLabel:disabled {{
            color: #777989;
        }}
        QLabel[role="warning"] {{
            background: transparent;
            color: {DRACULA["orange"]};
            font-weight: 700;
        }}
        QLabel[role="banner"] {{
            background: #3d3328;
            border: 1px solid {DRACULA["orange"]};
            border-radius: 6px;
            color: {DRACULA["orange"]};
            font-weight: 700;
            padding: 8px 12px;
        }}
        QPushButton {{
            background: {DRACULA["panel_alt"]};
            border: 1px solid {DRACULA["selection"]};
            border-radius: 6px;
            min-height: 32px;
            min-width: 132px;
            padding: 7px 14px;
        }}
        QPushButton:hover {{
            border-color: {DRACULA["purple"]};
        }}
        QPushButton:pressed {{
            background: {DRACULA["selection"]};
        }}
        QPushButton:disabled {{
            background: #2d2f3a;
            border-color: #3a3d4b;
            color: #777989;
        }}
        QToolButton {{
            background: transparent;
            border: 0;
            color: {DRACULA["foreground"]};
            font-weight: 700;
            padding: 2px;
            text-align: left;
        }}
        QToolButton:hover {{
            color: {DRACULA["cyan"]};
        }}
        QToolButton[buttonRole="iconAction"] {{
            background: {DRACULA["panel_alt"]};
            border: 1px solid {DRACULA["selection"]};
            border-radius: 6px;
            padding: 4px;
        }}
        QToolButton[buttonRole="iconAction"]:hover {{
            border-color: {DRACULA["purple"]};
        }}
        QToolButton[buttonRole="iconAction"]:pressed {{
            background: {DRACULA["selection"]};
        }}
        QMenu {{
            background: {DRACULA["panel"]};
            border: 1px solid {DRACULA["selection"]};
            border-radius: 8px;
            padding: 6px;
        }}
        QMenu::item {{
            background: transparent;
            border-radius: 5px;
            padding: 8px 12px;
            margin: 2px 0;
        }}
        QMenu::item:selected {{
            background: {DRACULA["selection"]};
            color: {DRACULA["cyan"]};
        }}
        QLineEdit, QComboBox, QSpinBox, QTableWidget {{
            background: #21222c;
            border: 1px solid {DRACULA["selection"]};
            border-radius: 5px;
            padding: 5px;
            selection-background-color: {DRACULA["purple"]};
            selection-color: #191a21;
        }}
        QComboBox::drop-down {{
            border: 0;
            width: 24px;
        }}
        QSpinBox {{
            padding-right: 28px;
            min-width: 72px;
        }}
        QSpinBox::up-button {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 24px;
            height: 14px;
            border-left: 1px solid {DRACULA["selection"]};
            border-top-right-radius: 5px;
            background: {DRACULA["panel_alt"]};
        }}
        QSpinBox::down-button {{
            subcontrol-origin: padding;
            subcontrol-position: bottom right;
            width: 24px;
            height: 14px;
            border-left: 1px solid {DRACULA["selection"]};
            border-top: 1px solid {DRACULA["selection"]};
            border-bottom-right-radius: 5px;
            background: {DRACULA["panel_alt"]};
        }}
        QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
            background: {DRACULA["selection"]};
        }}
        QSpinBox::up-arrow {{
            image: url("{spinbox_plus_icon}");
            width: 10px;
            height: 10px;
        }}
        QSpinBox::down-arrow {{
            image: url("{spinbox_minus_icon}");
            width: 10px;
            height: 10px;
        }}
        QHeaderView::section {{
            background: {DRACULA["panel"]};
            border: 0;
            border-right: 1px solid {DRACULA["selection"]};
            border-bottom: 1px solid {DRACULA["selection"]};
            padding: 6px;
            color: {DRACULA["foreground"]};
        }}
        QScrollArea, QTableWidget::viewport {{
            background: transparent;
            border: 0;
        }}
        QScrollBar:horizontal {{
            background: #21222c;
            height: 12px;
            border-radius: 6px;
        }}
        QScrollBar::handle:horizontal {{
            background: {DRACULA["selection"]};
            border-radius: 6px;
            min-width: 48px;
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0;
        }}
        QFrame[frameRole="card"] {{
            background: {DRACULA["panel"]};
            border: 1px solid {DRACULA["selection"]};
            border-radius: 8px;
        }}
        QFrame[frameRole="card"]:disabled {{
            background: #2b2d38;
            border-color: #3a3d4b;
        }}
        QFrame[frameRole="foldout"] {{
            background: {DRACULA["panel"]};
            border: 1px solid {DRACULA["selection"]};
            border-radius: 8px;
        }}
        QWidget[frameRole="foldoutContent"] {{
            background: transparent;
            border: 0;
        }}
        QFrame[frameRole="header"] {{
            background: {DRACULA["panel"]};
            border: 1px solid {DRACULA["selection"]};
            border-radius: 8px;
        }}
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
        }}
        """
    )
