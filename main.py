"""Entry point — `python main.py`."""
from __future__ import annotations

import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from app import APP_NAME
from app.core.settings_store import SettingsStore
from app.core.trial import Trial
from app.i18n import set_language
from app.ui import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("Admin-Kh")

    store = SettingsStore()
    trial = Trial()
    set_language(store.get("language", "en"))

    w = MainWindow(store, trial)
    w.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
