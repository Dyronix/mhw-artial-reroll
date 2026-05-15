from __future__ import annotations

import sys
import traceback
import logging

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QMessageBox

from app.app_info import APP_NAME, APP_ORGANIZATION, APP_VERSION
from app.main_window import MainWindow
from app.path_utils import app_icon_path, config_dir, ensure_user_data_dirs, log_file_path, save_state_path
from app.theme import apply_dracula_theme
from data.config_loader import load_app_config
from data.repository import StateRepository


def configure_logging() -> None:
    logging.basicConfig(
        filename=log_file_path(),
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName(APP_ORGANIZATION)
    apply_dracula_theme(app)

    icon = app_icon_path()
    if icon is not None:
        app.setWindowIcon(QIcon(str(icon)))

    try:
        configure_logging()
        logging.info("Starting %s %s", APP_NAME, APP_VERSION)
        ensure_user_data_dirs()
        config = load_app_config(config_dir())
        repository = StateRepository(save_state_path())
        state = repository.load()

        window = MainWindow(config=config, repository=repository, state=state)
        if icon is not None:
            window.setWindowIcon(QIcon(str(icon)))
        window.resize(1280, 820)
        window.show()
        return app.exec()
    except Exception as exc:
        traceback.print_exc()
        logging.exception("Startup failed")
        QMessageBox.critical(
            None,
            "Startup Error",
            f"{APP_NAME} could not start.\n\n{exc}\n\nSee the log file in your app data folder.",
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
