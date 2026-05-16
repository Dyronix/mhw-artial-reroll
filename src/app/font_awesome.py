from __future__ import annotations

import logging

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QStyle

from app.theme import DRACULA


logger = logging.getLogger(__name__)

FONT_AWESOME = {
    "edit_rolls": "fa5s.pen",
    "accept_next_roll": "fa5s.check",
    "targets": "fa5s.crosshairs",
    "delete_weapon": "fa5s.trash-alt",
}

FALLBACK_STANDARD_ICONS = {
    "edit_rolls": QStyle.StandardPixmap.SP_FileDialogDetailedView,
    "accept_next_roll": QStyle.StandardPixmap.SP_DialogApplyButton,
    "targets": QStyle.StandardPixmap.SP_FileDialogContentsView,
    "delete_weapon": QStyle.StandardPixmap.SP_TrashIcon,
}


def font_awesome_icon(name: str, color: str = DRACULA["foreground"]) -> QIcon:
    icon_id = FONT_AWESOME[name]
    try:
        import qtawesome as qta

        icon = qta.icon(icon_id, color=color)
        if not icon.isNull():
            return icon
        logger.warning("Font Awesome icon %s resolved to a null QIcon", icon_id)
    except Exception:
        logger.exception("Font Awesome icon %s could not be loaded", icon_id)

    return _fallback_icon(name)


def _fallback_icon(name: str) -> QIcon:
    app = QApplication.instance()
    if app is None:
        return QIcon()

    standard_icon = FALLBACK_STANDARD_ICONS.get(name, QStyle.StandardPixmap.SP_TitleBarMenuButton)
    fallback = app.style().standardIcon(standard_icon)
    if not fallback.isNull():
        return fallback

    pixmap = fallback.pixmap(QSize(18, 18))
    pixmap.fill(Qt.transparent)
    return QIcon(pixmap)
