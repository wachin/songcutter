# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Washington
"""Configuration package: paths, atomic JSON stores and settings.

Only two configuration files exist: ``settings.json`` and ``shortcuts.json``.
Caches and logs live in separate platform directories.
"""

from songcutter.config.paths import (
    cache_dir,
    config_dir,
    log_dir,
    settings_path,
    shortcuts_path,
    state_dir,
)

__all__ = [
    "cache_dir",
    "config_dir",
    "log_dir",
    "settings_path",
    "shortcuts_path",
    "state_dir",
]
