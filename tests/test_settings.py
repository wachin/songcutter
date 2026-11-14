# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Washington
"""Tests for user settings."""

from __future__ import annotations

import json

from songcutter.config.settings import Settings


def test_defaults(settings_path):
    settings = Settings(settings_path)
    assert settings.menu_bar_visible is True
    assert settings.timeline_channel == "left"
    assert settings.half_wave is True
    assert settings.language == "system"
    assert settings.splitter_sizes("main") == []


def test_window_and_splitters_roundtrip(settings_path):
    settings = Settings(settings_path)
    settings.set_window("geo", "state", True)
    settings.set_splitter_sizes("main", [300, 400])
    settings.set_splitter_sizes("top", [500, 600])
    settings.save()

    reloaded = Settings(settings_path)
    assert reloaded.window_geometry == "geo"
    assert reloaded.window_state == "state"
    assert reloaded.window_maximized is True
    assert reloaded.splitter_sizes("main") == [300, 400]
    assert reloaded.splitter_sizes("top") == [500, 600]


def test_splitter_sizes_are_sanitized(settings_path):
    settings = Settings(settings_path)
    settings.set("splitters", "main", ["bad", 12])
    assert settings.splitter_sizes("main") == []
    settings.set("splitters", "main", "not-a-list")
    assert settings.splitter_sizes("main") == []


def test_channel_and_half_wave_persist(settings_path):
    settings = Settings(settings_path)
    settings.timeline_channel = "right"
    settings.half_wave = False
    settings.save()
    reloaded = Settings(settings_path)
    assert reloaded.timeline_channel == "right"
    assert reloaded.half_wave is False


def test_corrupt_settings_fall_back_to_defaults(settings_path):
    settings_path.write_text("broken", encoding="utf-8")
    settings = Settings(settings_path)
    assert settings.menu_bar_visible is True
    settings.save()
    data = json.loads(settings_path.read_text(encoding="utf-8"))
    assert data["schema_version"] == 1
