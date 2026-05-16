from __future__ import annotations

from html import escape

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from app.path_utils import asset_path


def load_weapon_icon(name: str, size: int = 22) -> QPixmap | None:
    return _load_icon("weapons", name, size=size, suffix=".jpeg")


def load_attribute_icon(attribute: str, size: int = 22) -> QPixmap | None:
    for folder in ("elements", "ailments"):
        pixmap = _load_icon(folder, attribute, size=size, suffix=".png")
        if pixmap is not None:
            return pixmap
    return None


def load_skill_type_icon(skill_type: str, size: int = 22) -> QPixmap | None:
    folder_by_type = {
        "set_bonus": "set_bonus_skills",
        "group": "group_skills",
    }
    file_by_type = {
        "set_bonus": "set_bonus_skill",
        "group": "group_skill",
    }
    folder = folder_by_type.get(skill_type)
    name = file_by_type.get(skill_type)
    if folder is None or name is None:
        return None
    return _load_icon(folder, name, size=size, suffix=".png")


def skill_summary_html(
    *,
    set_bonus_skill: str,
    group_skill: str,
    empty_text: str,
    prefix: str = "",
    highlighted: bool = False,
    icon_size: int = 14,
) -> str:
    parts: list[str] = []
    if set_bonus_skill != "0":
        parts.append(f"{_skill_icon_html('set_bonus', icon_size)} {escape(set_bonus_skill)}")
    if group_skill != "0":
        parts.append(f"{_skill_icon_html('group', icon_size)} {escape(group_skill)}")
    if not parts:
        return escape(f"{prefix}{empty_text}")
    suffix = " [highlight]" if highlighted else ""
    text = " | ".join(parts) + escape(suffix)
    if prefix:
        return f"{escape(prefix)}{text}"
    return text


def _load_icon(folder: str, name: str, *, size: int, suffix: str) -> QPixmap | None:
    path = asset_path("icons", folder, f"{_slugify(name)}{suffix}")
    if not path.exists():
        return None
    pixmap = QPixmap(str(path))
    if pixmap.isNull():
        return None
    return pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)


def _skill_icon_html(skill_type: str, size: int) -> str:
    folder_by_type = {
        "set_bonus": "set_bonus_skills",
        "group": "group_skills",
    }
    file_by_type = {
        "set_bonus": "set_bonus_skill",
        "group": "group_skill",
    }
    folder = folder_by_type.get(skill_type)
    name = file_by_type.get(skill_type)
    if folder is None or name is None:
        return ""
    path = asset_path("icons", folder, f"{name}.png")
    if not path.exists():
        return ""
    return (
        f"<img src=\"{escape(path.as_uri())}\" style=\"vertical-align: middle;\" "
        f"width=\"{size}\" height=\"{size}\"/>"
    )


def _slugify(value: str) -> str:
    slug = value.strip().casefold().replace("&", "and")
    for source, replacement in ((" / ", "_"), (" ", "_"), ("-", "_")):
        slug = slug.replace(source, replacement)
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug.strip("_")
