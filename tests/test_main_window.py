# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Washington
"""Tests for the main window shell and layout persistence."""

from __future__ import annotations

import json

from PyQt6.QtCore import QTimer

from songcutter.config.settings import Settings
from songcutter.ui.actions import ActionManager
from songcutter.ui.main_window import MainWindow
from songcutter.ui.shortcuts_dialog import ShortcutsDialog


def _show(window, qapp):
    window.show()
    qapp.processEvents()
    QTimer.singleShot(0, lambda: None)
    qapp.processEvents()
    qapp.processEvents()


def test_window_builds_with_five_tabs(qapp, settings_path, shortcuts_path):
    window = MainWindow(Settings(settings_path), shortcuts_file=shortcuts_path)
    _show(window, qapp)
    try:
        assert window.workspace.tabs.count() == 5
        assert window.workspace.stack.count() == 5
        assert "SongCutter" in window.windowTitle()
        assert "HD 720p 30 fps" in window.windowTitle()
        assert window.timeline.view.pixels_per_second > 0
    finally:
        window.close()


def test_default_splitter_proportions(qapp, settings_path, shortcuts_path):
    window = MainWindow(Settings(settings_path), shortcuts_file=shortcuts_path)
    _show(window, qapp)
    try:
        main = window.main_splitter.sizes()
        top = window.top_splitter.sizes()
        assert sum(main) > 0
        assert abs(main[0] / sum(main) - 0.42) < 0.08
        assert abs(top[0] / sum(top) - 0.45) < 0.08
    finally:
        window.close()


def test_splitter_sizes_persist(qapp, settings_path, shortcuts_path):
    window = MainWindow(Settings(settings_path), shortcuts_file=shortcuts_path)
    _show(window, qapp)
    window.main_splitter.setSizes([250, 420])
    window.top_splitter.setSizes([520, 700])
    qapp.processEvents()
    expected_main = window.main_splitter.sizes()
    expected_top = window.top_splitter.sizes()
    window.close()

    data = json.loads(settings_path.read_text(encoding="utf-8"))
    assert data["splitters"]["main"] == expected_main
    assert data["splitters"]["top"] == expected_top

    second = MainWindow(Settings(settings_path), shortcuts_file=shortcuts_path)
    # The offscreen test screen is small; keep the same window width so the
    # splitter pixel sizes are comparable.
    second.resize(1360, 768)
    _show(second, qapp)
    try:
        assert second.main_splitter.sizes() == expected_main
        assert second.top_splitter.sizes() == expected_top
    finally:
        second.close()


def test_menu_bar_toggle_persists(qapp, settings_path, shortcuts_path):
    window = MainWindow(Settings(settings_path), shortcuts_file=shortcuts_path)
    _show(window, qapp)
    action = window._actions.action("view.toggle_menu")
    action.setChecked(False)
    qapp.processEvents()
    assert not window.menuBar().isVisible()
    window.close()

    data = json.loads(settings_path.read_text(encoding="utf-8"))
    assert data["window"]["menu_bar_visible"] is False

    second = MainWindow(Settings(settings_path), shortcuts_file=shortcuts_path)
    _show(second, qapp)
    try:
        assert not second.menuBar().isVisible()
        assert not second._actions.action("view.toggle_menu").isChecked()
    finally:
        second.close()


def test_shortcuts_dialog_lists_actions(qapp, settings_path, shortcuts_path):
    manager = ActionManager(store_path=shortcuts_path)
    dialog = ShortcutsDialog(manager)
    try:
        assert dialog._tree.topLevelItemCount() > 0
        total = sum(
            dialog._tree.topLevelItem(index).childCount()
            for index in range(dialog._tree.topLevelItemCount())
        )
        assert total == len(manager.actions())
    finally:
        dialog.close()
        manager.deleteLater()


def test_process_button_and_status(qapp, settings_path, shortcuts_path):
    window = MainWindow(Settings(settings_path), shortcuts_file=shortcuts_path)
    _show(window, qapp)
    try:
        assert "Process videos" in window.process_button.text()
        assert "3 clips" in window.status_label.text()
        assert "3 songs detected" in window.status_label.text()
        window._process_videos()
        assert "Phase 7" in window.status_label.text()
    finally:
        window.close()
