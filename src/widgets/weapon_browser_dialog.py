from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QPainter, QPalette, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QStyledItemDelegate,
    QStyle,
    QStyleOptionViewItem,
    QVBoxLayout,
)

from app.path_utils import asset_path
from data.models import AppConfig, AppState, Skill, weapon_display_name


@dataclass(frozen=True)
class WeaponBrowserRow:
    weapon_id: str
    title: str
    weapon_type: str
    attribute: str
    set_bonus_skill: Skill | None
    group_skill: Skill | None
    weapon_icon: QPixmap | None
    attribute_icon: QPixmap | None


class WeaponBrowserListDelegate(QStyledItemDelegate):
    ICON_SIZE = 22
    H_MARGIN = 10
    V_MARGIN = 8
    GAP = 8

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index) -> None:
        row = index.data(Qt.UserRole)
        if not isinstance(row, WeaponBrowserRow):
            super().paint(painter, option, index)
            return

        painter.save()
        painter.fillRect(option.rect, _row_background(option, index.row()))

        text_rect = QRect(option.rect)
        text_rect.adjust(self.H_MARGIN, self.V_MARGIN, -self.H_MARGIN, -self.V_MARGIN)
        x = text_rect.left()
        center_y = option.rect.center().y()

        x = self._draw_icon_or_text(
            painter,
            option,
            row.weapon_icon,
            row.weapon_type,
            x,
            center_y,
        )
        x = self._draw_icon_or_text(
            painter,
            option,
            row.attribute_icon,
            row.attribute,
            x,
            center_y,
        )

        label_rect = QRect(x, text_rect.top(), text_rect.right() - x, text_rect.height())
        painter.setPen(option.palette.color(_text_role(option)))
        painter.drawText(label_rect, Qt.AlignVCenter | Qt.AlignLeft, row.title)
        painter.restore()

    def sizeHint(self, option: QStyleOptionViewItem, index) -> QSize:
        row = index.data(Qt.UserRole)
        if not isinstance(row, WeaponBrowserRow):
            return super().sizeHint(option, index)
        metrics = option.fontMetrics
        height = max(metrics.height(), self.ICON_SIZE) + (self.V_MARGIN * 2)
        width = metrics.horizontalAdvance(row.title) + (self.H_MARGIN * 2) + (self.GAP * 3)
        width += self._icon_or_text_width(metrics, row.weapon_icon, row.weapon_type)
        width += self._icon_or_text_width(metrics, row.attribute_icon, row.attribute)
        return QSize(width, height)

    def _draw_icon_or_text(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        pixmap: QPixmap | None,
        fallback_text: str,
        x: int,
        center_y: int,
    ) -> int:
        if pixmap is not None:
            rect = QRect(x, center_y - (self.ICON_SIZE // 2), self.ICON_SIZE, self.ICON_SIZE)
            painter.drawPixmap(rect, pixmap)
            return rect.right() + 1 + self.GAP

        metrics = option.fontMetrics
        width = metrics.horizontalAdvance(fallback_text)
        rect = QRect(x, option.rect.top(), width, option.rect.height())
        painter.setPen(option.palette.color(_text_role(option)))
        painter.drawText(rect, Qt.AlignVCenter | Qt.AlignLeft, fallback_text)
        return rect.right() + 1 + self.GAP

    def _icon_or_text_width(self, metrics, pixmap: QPixmap | None, fallback_text: str) -> int:
        return self.ICON_SIZE if pixmap is not None else metrics.horizontalAdvance(fallback_text)


class WeaponBrowserDialog(QDialog):
    def __init__(self, state: AppState, config: AppConfig, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Weapon Browser")
        self.resize(980, 620)
        self.rows = _weapon_rows(state, config)

        title = QLabel("Weapon Browser")
        title.setProperty("role", "title")

        subtitle = QLabel(
            "Browse tracked weapons and review their current readonly skill details."
        )
        subtitle.setProperty("role", "muted")
        subtitle.setWordWrap(True)

        self.weapon_list = QListWidget()
        self.weapon_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.weapon_list.setAlternatingRowColors(True)
        self.weapon_list.setItemDelegate(WeaponBrowserListDelegate(self.weapon_list))
        self.weapon_list.currentRowChanged.connect(self._show_row)

        for row in self.rows:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, row)
            item.setToolTip(_tooltip_label(row))
            self.weapon_list.addItem(item)

        self.weapon_name = QLabel("No weapon selected")
        self.weapon_name.setProperty("role", "section")
        self.weapon_name.setWordWrap(True)

        self.weapon_meta = QLabel("Select a weapon from the list.")
        self.weapon_meta.setProperty("role", "muted")
        self.weapon_meta.setWordWrap(True)

        self.set_skill_name = QLabel("None")
        self.set_skill_name.setStyleSheet("background: transparent;")
        self.set_skill_name.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.set_skill_name.setWordWrap(True)
        self.set_skill_description = QLabel("No set bonus skill recorded.")
        self.set_skill_description.setProperty("role", "muted")
        self.set_skill_description.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.set_skill_description.setWordWrap(True)

        self.group_skill_name = QLabel("None")
        self.group_skill_name.setStyleSheet("background: transparent;")
        self.group_skill_name.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.group_skill_name.setWordWrap(True)
        self.group_skill_description = QLabel("No group skill recorded.")
        self.group_skill_description.setProperty("role", "muted")
        self.group_skill_description.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.group_skill_description.setWordWrap(True)

        detail_panel = QFrame()
        detail_panel.setProperty("frameRole", "card")
        detail_layout = QVBoxLayout(detail_panel)
        detail_layout.setContentsMargins(16, 16, 16, 16)
        detail_layout.setSpacing(12)
        detail_layout.addWidget(self.weapon_name)
        detail_layout.addWidget(self.weapon_meta)
        detail_layout.addWidget(_section_label("Set Bonus Skill"))
        detail_layout.addWidget(self.set_skill_name)
        detail_layout.addWidget(self.set_skill_description)
        detail_layout.addWidget(_section_label("Group Skill"))
        detail_layout.addWidget(self.group_skill_name)
        detail_layout.addWidget(self.group_skill_description)
        detail_layout.addStretch(1)

        body = QHBoxLayout()
        body.setSpacing(12)
        body.addWidget(self.weapon_list, 1)
        body.addWidget(detail_panel, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(body, 1)
        layout.addWidget(buttons)

        if self.rows:
            self.weapon_list.setCurrentRow(0)
            self.weapon_list.setFocus()

    def _show_row(self, index: int) -> None:
        if index < 0 or index >= len(self.rows):
            self.weapon_name.setText("No weapon selected")
            self.weapon_meta.setText("Select a weapon from the list.")
            self.set_skill_name.setText("None")
            self.set_skill_description.setText("No set bonus skill recorded.")
            self.group_skill_name.setText("None")
            self.group_skill_description.setText("No group skill recorded.")
            return

        row = self.rows[index]
        self.weapon_name.setText(row.title)
        self.weapon_meta.setText(
            f"Weapon Type: {row.weapon_type}\nElement / Ailment: {row.attribute}"
        )
        _set_skill_widgets(
            self.set_skill_name,
            self.set_skill_description,
            row.set_bonus_skill,
            empty_text="No set bonus skill recorded.",
        )
        _set_skill_widgets(
            self.group_skill_name,
            self.group_skill_description,
            row.group_skill,
            empty_text="No group skill recorded.",
        )


def _weapon_rows(state: AppState, config: AppConfig) -> list[WeaponBrowserRow]:
    skills_by_name = _skills_by_name(config)
    return [
        WeaponBrowserRow(
            weapon_id=weapon.id,
            title=weapon.nickname.strip() or weapon_display_name(state, weapon).split(" (", 1)[0],
            weapon_type=weapon.weapon_type,
            attribute=weapon.attribute,
            set_bonus_skill=skills_by_name.get(weapon.current_set_bonus_skill),
            group_skill=skills_by_name.get(weapon.current_group_skill),
            weapon_icon=_load_icon("weapons", weapon.weapon_type, suffix=".jpeg"),
            attribute_icon=_load_attribute_icon(weapon.attribute),
        )
        for weapon in state.tracked_weapons
    ]


def _skills_by_name(config: AppConfig) -> dict[str, Skill]:
    skills: dict[str, Skill] = {}
    for skill in config.set_bonus_skills + config.group_skills + config.skill_encyclopedia:
        if skill.name and skill.name not in skills:
            skills[skill.name] = skill
        if skill.source and skill.source not in skills:
            skills[skill.source] = skill
    return skills


def _tooltip_label(row: WeaponBrowserRow) -> str:
    return f"{row.title} | {row.weapon_type} | {row.attribute}"


def _section_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setProperty("role", "muted")
    return label


def _set_skill_widgets(
    name_label: QLabel,
    description_label: QLabel,
    skill: Skill | None,
    *,
    empty_text: str,
) -> None:
    if skill is None:
        name_label.setText("None")
        description_label.setText(empty_text)
        return
    name_label.setText(skill.name)
    description_label.setText(skill.description or "No description available.")


def _text_role(option: QStyleOptionViewItem) -> QPalette.ColorRole:
    return QPalette.Text


def _row_background(option: QStyleOptionViewItem, row_index: int):
    if option.state & QStyle.State_Selected:
        return option.palette.highlight()
    if option.features & QStyleOptionViewItem.Alternate:
        return option.palette.alternateBase()
    if row_index % 2:
        return option.palette.alternateBase()
    return option.palette.base()


def _load_attribute_icon(attribute: str) -> QPixmap | None:
    for folder in ("elements", "ailments"):
        pixmap = _load_icon(folder, attribute, suffix=".png")
        if pixmap is not None:
            return pixmap
    return None


def _load_icon(folder: str, name: str, *, suffix: str) -> QPixmap | None:
    path = asset_path("icons", folder, f"{_slugify(name)}{suffix}")
    if not path.exists():
        return None
    pixmap = QPixmap(str(path))
    if pixmap.isNull():
        return None
    return pixmap.scaled(
        WeaponBrowserListDelegate.ICON_SIZE,
        WeaponBrowserListDelegate.ICON_SIZE,
        Qt.KeepAspectRatio,
        Qt.SmoothTransformation,
    )


def _slugify(value: str) -> str:
    slug = value.strip().casefold().replace("&", "and")
    for source, replacement in ((" / ", "_"), (" ", "_"), ("-", "_")):
        slug = slug.replace(source, replacement)
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug.strip("_")
