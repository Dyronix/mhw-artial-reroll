from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from data.models import AppConfig, Skill
from widgets.weapon_icon_utils import load_skill_type_icon


@dataclass(frozen=True)
class SkillEncyclopediaRow:
    category: str
    icon_type: str | None
    skill: Skill


class SkillEncyclopediaDialog(QDialog):
    def __init__(self, config: AppConfig, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Skill Encyclopedia")
        self.resize(980, 620)
        self.rows = _skill_rows(config)

        title = QLabel("Skill Encyclopedia")
        title.setProperty("role", "title")

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search skills, sources, or descriptions")
        self.search.textChanged.connect(self.refresh_table)

        self.category = QComboBox()
        self.category.addItem("All Skill Types", "")
        for category in _categories(self.rows):
            self.category.addItem(category, category)
        self.category.currentIndexChanged.connect(self.refresh_table)

        filters = QHBoxLayout()
        filters.setSpacing(8)
        filters.addWidget(self.search, 1)
        filters.addWidget(self.category)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Type", "Skill", "Source", "Description"])
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setWordWrap(True)
        self.table.verticalHeader().setVisible(False)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addLayout(filters)
        layout.addWidget(self.table, 1)
        layout.addWidget(buttons)

        self.refresh_table()

    def refresh_table(self) -> None:
        query = self.search.text().strip().casefold()
        selected_category = str(self.category.currentData() or "")
        visible_rows = [
            row
            for row in self.rows
            if _matches_category(row, selected_category) and _matches_query(row, query)
        ]

        self.table.setRowCount(len(visible_rows))
        for index, row in enumerate(visible_rows):
            values = [
                row.category,
                row.skill.name,
                row.skill.source,
                row.skill.description,
            ]
            for column, value in enumerate(values):
                display_value = value
                if column == 0 and row.icon_type:
                    display_value = ""
                item = QTableWidgetItem(display_value)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                if column == 0:
                    pixmap = load_skill_type_icon(row.icon_type, size=18) if row.icon_type else None
                    if pixmap is not None:
                        item.setIcon(QIcon(pixmap))
                    item.setToolTip(value)
                if column == 3:
                    item.setToolTip(value)
                self.table.setItem(index, column, item)
        self.table.resizeRowsToContents()


def _skill_rows(config: AppConfig) -> list[SkillEncyclopediaRow]:
    rows: list[SkillEncyclopediaRow] = []
    rows.extend(SkillEncyclopediaRow("Set Bonus", "set_bonus", skill) for skill in config.set_bonus_skills)
    rows.extend(SkillEncyclopediaRow("Group Skill", "group", skill) for skill in config.group_skills)
    rows.extend(SkillEncyclopediaRow("Encyclopedia", None, skill) for skill in config.skill_encyclopedia)
    return rows


def _categories(rows: list[SkillEncyclopediaRow]) -> list[str]:
    seen: set[str] = set()
    categories: list[str] = []
    for row in rows:
        if row.category not in seen:
            seen.add(row.category)
            categories.append(row.category)
    return categories


def _matches_category(row: SkillEncyclopediaRow, selected_category: str) -> bool:
    return not selected_category or row.category == selected_category


def _matches_query(row: SkillEncyclopediaRow, query: str) -> bool:
    if not query:
        return True
    haystack = " ".join(
        (
            row.category,
            row.skill.name,
            row.skill.source,
            row.skill.description,
        )
    ).casefold()
    return query in haystack
