# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Washington
"""Application bootstrap."""

from __future__ import annotations

import argparse
import logging
import sys
import traceback

from PyQt6.QtWidgets import QApplication, QMessageBox

from songcutter import APP_DISPLAY_NAME, APP_NAME, ORG_NAME, __version__
from songcutter.config.logging_setup import setup_logging
from songcutter.config.settings import Settings
from songcutter.i18n.qt_translations import install_qt_translations
from songcutter.ui.main_window import MainWindow
from songcutter.ui.theme import apply_theme

log = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="songcutter", description=APP_DISPLAY_NAME)
    parser.add_argument("--version", action="version", version=f"SongCutter {__version__}")
    parser.add_argument("--debug", action="store_true", help="enable debug logging")
    return parser


def _install_exception_hook(app: QApplication) -> None:
    def hook(exc_type, exc_value, exc_tb):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_tb)
            return
        log.critical(
            "Unhandled exception:\n%s",
            "".join(traceback.format_exception(exc_type, exc_value, exc_tb)),
        )
        QMessageBox.critical(
            None,
            QApplication.translate("Main", "Unexpected error"),
            QApplication.translate(
                "Main",
                "An unexpected error occurred. The details were written to the log file.",
            ),
        )

    sys.excepthook = hook


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    setup_logging(debug=args.debug)

    app = QApplication([sys.argv[0]])
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(ORG_NAME)
    app.setApplicationDisplayName(APP_DISPLAY_NAME)
    app.setApplicationVersion(__version__)
    app.setDesktopFileName("songcutter")
    _install_exception_hook(app)

    apply_theme(app)
    settings = Settings()
    language = None if settings.language == "system" else settings.language
    install_qt_translations(app, language)

    window = MainWindow(settings=settings)
    window.show()
    log.info("SongCutter %s started", __version__)
    return app.exec()
