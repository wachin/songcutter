# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Washington
"""User settings stored in ``settings.json``."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from songcutter.config.json_store import JsonStore
from songcutter.config.paths import settings_path

log = logging.getLogger(__name__)

DEFAULTS: dict[str, Any] = {
    "schema_version": 1,
    "window": {
        "geometry": "",
        "state": "",
        "maximized": False,
        "menu_bar_visible": True,
    },
    "splitters": {
        # Ratios are stored as pixel sizes; empty lists mean "use the design
        # proportions for the current window size".
        "main": [],
        "top": [],
        "effects": [],
    },
    "ui": {
        "language": "system",
    },
    "files": {
        "last_folder": "",
        "recent_folders": [],
    },
    "tools": {
        "ffmpeg": "",
        "ffprobe": "",
        "sox": "",
    },
    "timeline": {
        "channel": "left",
        "half_wave": True,
        "show_db_scale": True,
    },
}


class Settings:
    """Typed access to the settings file."""

    def __init__(self, path: Path | None = None):
        self._store = JsonStore(path or settings_path(), DEFAULTS)
        self._data = self._store.load()

    # -- generic ---------------------------------------------------------
    def get(self, section: str, key: str, default: Any = None) -> Any:
        value = self._data.get(section, {})
        if isinstance(value, dict):
            return value.get(key, default)
        return default

    def set(self, section: str, key: str, value: Any) -> None:
        bucket = self._data.setdefault(section, {})
        if not isinstance(bucket, dict):  # corrupt shape: replace it
            bucket = {}
            self._data[section] = bucket
        bucket[key] = value

    def save(self) -> None:
        self._store.save(self._data)

    # -- window ----------------------------------------------------------
    @property
    def window_geometry(self) -> str:
        return str(self.get("window", "geometry", "") or "")

    @property
    def window_state(self) -> str:
        return str(self.get("window", "state", "") or "")

    @property
    def window_maximized(self) -> bool:
        return bool(self.get("window", "maximized", False))

    @property
    def menu_bar_visible(self) -> bool:
        return bool(self.get("window", "menu_bar_visible", True))

    def set_window(self, geometry: str, state: str, maximized: bool) -> None:
        self.set("window", "geometry", geometry)
        self.set("window", "state", state)
        self.set("window", "maximized", maximized)

    def set_menu_bar_visible(self, visible: bool) -> None:
        self.set("window", "menu_bar_visible", visible)

    # -- splitters -------------------------------------------------------
    def splitter_sizes(self, name: str) -> list[int]:
        sizes = self.get("splitters", name, [])
        if not isinstance(sizes, list):
            return []
        result: list[int] = []
        for value in sizes:
            try:
                result.append(int(value))
            except (TypeError, ValueError):
                return []
        return result

    def set_splitter_sizes(self, name: str, sizes: list[int]) -> None:
        self.set("splitters", name, [int(s) for s in sizes])

    # -- misc ------------------------------------------------------------
    @property
    def last_folder(self) -> str:
        return str(self.get("files", "last_folder", "") or "")

    @last_folder.setter
    def last_folder(self, value: str) -> None:
        self.set("files", "last_folder", value)

    @property
    def language(self) -> str:
        return str(self.get("ui", "language", "system") or "system")

    @property
    def timeline_channel(self) -> str:
        channel = str(self.get("timeline", "channel", "left") or "left").lower()
        return channel if channel in {"left", "right"} else "left"

    @timeline_channel.setter
    def timeline_channel(self, value: str) -> None:
        self.set("timeline", "channel", "right" if value == "right" else "left")

    @property
    def half_wave(self) -> bool:
        return bool(self.get("timeline", "half_wave", True))

    @half_wave.setter
    def half_wave(self, value: bool) -> None:
        self.set("timeline", "half_wave", bool(value))

    @property
    def show_db_scale(self) -> bool:
        return bool(self.get("timeline", "show_db_scale", True))

    def tool_path(self, name: str) -> str:
        return str(self.get("tools", name, "") or "")

    def set_tool_path(self, name: str, value: str) -> None:
        self.set("tools", name, value)
