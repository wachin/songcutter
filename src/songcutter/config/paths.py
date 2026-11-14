# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Washington
"""Platform directories used by SongCutter.

The layout follows the specification:

* config: ``settings.json`` and ``shortcuts.json`` (exactly two files)
* cache: waveform peaks, decoded PCM, noise profiles, proxies
* state: log files
"""

from __future__ import annotations

from pathlib import Path

import platformdirs

from songcutter import APP_NAME

APP_AUTHOR = False  # Do not append an organisation folder on Windows/macOS.


def config_dir() -> Path:
    """Directory for the two configuration files."""
    return Path(platformdirs.user_config_dir(APP_NAME, appauthor=APP_AUTHOR))


def cache_dir() -> Path:
    """Directory for regenerable caches (peaks, PCM, noise profiles)."""
    return Path(platformdirs.user_cache_dir(APP_NAME, appauthor=APP_AUTHOR))


def state_dir() -> Path:
    """Directory for application state that is not configuration."""
    return Path(platformdirs.user_state_dir(APP_NAME, appauthor=APP_AUTHOR))


def log_dir() -> Path:
    """Directory for log files."""
    return state_dir() / "logs"


def settings_path() -> Path:
    return config_dir() / "settings.json"


def shortcuts_path() -> Path:
    return config_dir() / "shortcuts.json"


def ensure_dir(path: Path) -> Path:
    """Create ``path`` (and parents) and return it."""
    path.mkdir(parents=True, exist_ok=True)
    return path
