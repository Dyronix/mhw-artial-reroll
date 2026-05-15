from __future__ import annotations

import logging
import os
import shutil
import sys
from pathlib import Path

from app.app_info import APP_DATA_DIR_NAME


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def project_root() -> Path:
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def bundled_root() -> Path:
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        return Path(meipass)
    return project_root()


def bundled_path(*parts: str) -> Path:
    return bundled_root().joinpath(*parts)


def user_data_dir() -> Path:
    appdata = os.environ.get("APPDATA")
    if appdata:
        return Path(appdata) / APP_DATA_DIR_NAME
    return Path.home() / f".{APP_DATA_DIR_NAME}"


def user_config_dir() -> Path:
    return user_data_dir() / "config"


def user_saves_dir() -> Path:
    return user_data_dir() / "saves"


def user_logs_dir() -> Path:
    return user_data_dir() / "logs"


def user_exports_dir() -> Path:
    return user_data_dir() / "exported_data"


def save_state_path() -> Path:
    return user_saves_dir() / "current_state.json"


def ensure_user_data_dirs() -> None:
    for path in (user_config_dir(), user_saves_dir(), user_logs_dir(), user_exports_dir()):
        path.mkdir(parents=True, exist_ok=True)
    _copy_default_config_files()


def config_dir() -> Path:
    ensure_user_data_dirs()
    return user_config_dir()


def log_file_path() -> Path:
    user_logs_dir().mkdir(parents=True, exist_ok=True)
    return user_logs_dir() / "app.log"


def asset_path(*parts: str) -> Path:
    user_asset = user_data_dir().joinpath("assets", *parts)
    if user_asset.exists():
        return user_asset
    return bundled_path("assets", *parts)


def app_icon_path() -> Path | None:
    for relative in (("icons", "app_icon.png"), ("icons", "app_icon.ico")):
        path = asset_path(*relative)
        if path.exists():
            return path
    return None


def _copy_default_config_files() -> None:
    source_dir = bundled_path("data", "config")
    destination_dir = user_config_dir()
    if not source_dir.exists():
        logging.warning("Bundled config directory does not exist: %s", source_dir)
        return

    for source in source_dir.glob("*.json"):
        destination = destination_dir / source.name
        if not destination.exists():
            shutil.copy2(source, destination)
