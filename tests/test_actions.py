# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Washington
"""Tests for the action manager and shortcut persistence."""

from __future__ import annotations

import json

import pytest
from PyQt6.QtGui import QKeySequence

from songcutter.ui.actions import CATALOG, ActionManager


def test_catalog_ids_are_unique():
    ids = [spec.id for spec in CATALOG]
    assert len(ids) == len(set(ids))


def test_every_default_parses():
    for spec in CATALOG:
        for value in spec.default:
            sequence = QKeySequence(value)
            assert not sequence.isEmpty(), f"{spec.id}: {value}"


def test_all_actions_created(qapp, shortcuts_path):
    manager = ActionManager(store_path=shortcuts_path)
    assert len(manager.actions()) == len(CATALOG)
    assert manager.action("file.quit").shortcut().toString() == "Ctrl+Q"


def test_phase_one_actions_enabled_others_disabled(qapp, shortcuts_path):
    manager = ActionManager(store_path=shortcuts_path)
    assert manager.action("tool.selection").isEnabled()
    assert manager.action("view.toggle_menu").isEnabled()
    assert not manager.action("playback.play_stop").isEnabled()
    assert not manager.action("edit.undo").isEnabled()


def test_rebind_persists(qapp, shortcuts_path):
    manager = ActionManager(store_path=shortcuts_path)
    ok, error = manager.set_shortcuts("file.quit", ["Ctrl+Alt+Q"])
    assert ok, error
    assert manager.action("file.quit").shortcut().toString() == "Ctrl+Alt+Q"

    reloaded = ActionManager(store_path=shortcuts_path)
    assert reloaded.action("file.quit").shortcut().toString() == "Ctrl+Alt+Q"
    data = json.loads(shortcuts_path.read_text(encoding="utf-8"))
    assert data["overrides"]["file.quit"] == ["Ctrl+Alt+Q"]


def test_conflict_is_rejected(qapp, shortcuts_path):
    manager = ActionManager(store_path=shortcuts_path)
    ok, error = manager.set_shortcuts("file.quit", ["Ctrl+S"])
    assert not ok
    assert "Save Project" in error
    assert manager.action("file.quit").shortcut().toString() == "Ctrl+Q"


def test_invalid_shortcut_is_rejected(qapp, shortcuts_path):
    manager = ActionManager(store_path=shortcuts_path)
    ok, _ = manager.set_shortcuts("file.quit", ["NotAKey"])
    assert not ok


def test_clear_shortcut(qapp, shortcuts_path):
    manager = ActionManager(store_path=shortcuts_path)
    ok, error = manager.set_shortcuts("file.quit", [])
    assert ok, error
    assert manager.action("file.quit").shortcuts() == []


def test_reset_shortcut(qapp, shortcuts_path):
    manager = ActionManager(store_path=shortcuts_path)
    manager.set_shortcuts("file.quit", ["Ctrl+Alt+Q"])
    manager.reset_shortcut("file.quit")
    assert manager.action("file.quit").shortcut().toString() == "Ctrl+Q"


def test_reset_all_shortcuts(qapp, shortcuts_path):
    manager = ActionManager(store_path=shortcuts_path)
    manager.set_shortcuts("file.quit", ["Ctrl+Alt+Q"])
    manager.reset_all_shortcuts()
    assert manager.action("file.quit").shortcut().toString() == "Ctrl+Q"
    assert manager.overrides_snapshot() == {}


def test_snapshot_restore(qapp, shortcuts_path):
    manager = ActionManager(store_path=shortcuts_path)
    snapshot = manager.overrides_snapshot()
    manager.set_shortcuts("file.quit", ["Ctrl+Alt+Q"])
    manager.restore_snapshot(snapshot)
    assert manager.action("file.quit").shortcut().toString() == "Ctrl+Q"


@pytest.mark.parametrize(
    "action_id",
    [
        "playback.play_stop",
        "playback.frame_forward",
        "playback.frame_back",
        "playback.second_forward",
        "playback.second_back",
        "playback.prev_marker",
        "playback.next_marker",
        "playback.project_start",
        "playback.project_end",
        "zone.set_in",
        "zone.set_out",
        "tool.selection",
        "tool.razor",
        "tool.spacer",
        "tool.escape",
        "edit.cut",
        "edit.cut_all",
        "edit.delete",
        "edit.extract",
        "edit.group",
        "edit.ungroup",
        "edit.select_all",
        "edit.undo",
        "edit.redo",
        "marker.add",
        "view.zoom_in",
        "view.zoom_out",
        "file.save",
        "file.open",
        "file.save_as",
        "file.process",
        "view.toggle_menu",
    ],
)
def test_must_actions_exist(action_id):
    assert any(spec.id == action_id for spec in CATALOG)
