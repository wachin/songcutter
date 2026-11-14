# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Washington
"""Logging setup: rotating log file in the state directory plus console."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from songcutter.config.paths import log_dir

LOG_FORMAT = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"
MAX_BYTES = 2 * 1024 * 1024
BACKUP_COUNT = 3


def setup_logging(debug: bool = False) -> Path:
    """Configure the root logger and return the log file path."""
    directory = log_dir()
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "songcutter.log"

    root = logging.getLogger()
    root.setLevel(logging.DEBUG if debug else logging.INFO)

    # Avoid duplicate handlers when main() is called twice (tests).
    for handler in list(root.handlers):
        if getattr(handler, "_songcutter", False):
            root.removeHandler(handler)
            handler.close()

    file_handler = RotatingFileHandler(
        path, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT, encoding="utf-8"
    )
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    file_handler._songcutter = True  # type: ignore[attr-defined]
    root.addHandler(file_handler)

    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG if debug else logging.WARNING)
    console.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
    console._songcutter = True  # type: ignore[attr-defined]
    root.addHandler(console)

    logging.getLogger(__name__).info("Logging to %s", path)
    return path
