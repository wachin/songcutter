# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Washington
"""Central action manager.

Every command has a stable id, an English label, a category and a default key
sequence. Shortcut overrides are stored in ``shortcuts.json``. Actions whose
feature is not implemented yet are created but disabled, so the Shortcuts
dialog can already show the complete table.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from pathlib import Path

from PyQt6.QtCore import QCoreApplication, QObject, Qt
from PyQt6.QtGui import QAction, QKeySequence

from songcutter.config.json_store import JsonStore
from songcutter.config.paths import shortcuts_path

CURRENT_PHASE = 1

SHORTCUTS_DEFAULTS = {"schema_version": 1, "overrides": {}}


@dataclass(frozen=True)
class ActionSpec:
    id: str
    text: str
    category: str
    default: tuple[str, ...] = ()
    phase: int = 99
    checkable: bool = False


# The table from the specification. Order defines menu and dialog order.
CATALOG: tuple[ActionSpec, ...] = (
    # Playback
    ActionSpec("playback.play_stop", "Play / Stop", "Playback", ("Space",), 3),
    ActionSpec("playback.pause", "Pause", "Playback", ("K",), 3),
    ActionSpec("playback.forward", "Forward", "Playback", ("L",), 3),
    ActionSpec("playback.rewind", "Rewind", "Playback", ("J",), 3),
    ActionSpec("playback.frame_forward", "Forward One Frame", "Playback", ("Right",), 3),
    ActionSpec("playback.frame_back", "Back One Frame", "Playback", ("Left",), 3),
    ActionSpec("playback.second_forward", "Forward One Second", "Playback", ("Shift+Right",), 3),
    ActionSpec("playback.second_back", "Back One Second", "Playback", ("Shift+Left",), 3),
    ActionSpec("playback.prev_snap", "Previous Snap Point", "Playback", ("Alt+Left",), 4),
    ActionSpec("playback.next_snap", "Next Snap Point", "Playback", ("Alt+Right",), 4),
    ActionSpec("playback.prev_marker", "Previous Marker", "Playback", ("Ctrl+Left",), 4),
    ActionSpec("playback.next_marker", "Next Marker", "Playback", ("Ctrl+Right",), 4),
    ActionSpec("playback.clip_start", "Go to Clip Start", "Playback", ("Home",), 4),
    ActionSpec("playback.clip_end", "Go to Clip End", "Playback", ("End",), 4),
    ActionSpec("playback.project_start", "Go to Project Start", "Playback", ("Ctrl+Home",), 4),
    ActionSpec("playback.project_end", "Go to Project End", "Playback", ("Ctrl+End",), 4),
    ActionSpec("playback.align_playhead", "Align Playhead to Mouse", "Playback", ("P",), 4),
    ActionSpec("playback.play_zone", "Play Zone", "Playback", ("Ctrl+Space",), 4),
    ActionSpec("playback.loop_zone", "Loop Zone", "Playback", ("Ctrl+Shift+Space",), 4),
    # Zone
    ActionSpec("zone.set_in", "Set Zone In", "Zone", ("I",), 4),
    ActionSpec("zone.set_out", "Set Zone Out", "Zone", ("O",), 4),
    ActionSpec("zone.go_start", "Go to Zone Start", "Zone", ("Shift+I",), 4),
    ActionSpec("zone.go_end", "Go to Zone End", "Zone", ("Shift+O",), 4),
    # Tools
    ActionSpec("tool.selection", "Selection Tool", "Tools", ("S",), 1, checkable=True),
    ActionSpec("tool.razor", "Razor Tool", "Tools", ("X",), 1, checkable=True),
    ActionSpec("tool.spacer", "Spacer Tool", "Tools", ("M",), 1, checkable=True),
    ActionSpec("tool.escape", "Back to Selection Tool", "Tools", ("Esc",), 1),
    # Editing
    ActionSpec("edit.cut", "Cut Clip at Playhead", "Editing", ("Shift+R",), 6),
    ActionSpec("edit.cut_all", "Cut All Clips at Playhead", "Editing", ("Ctrl+Shift+R",), 6),
    ActionSpec("edit.trim_start", "Trim Clip Start to Playhead", "Editing", ("(",), 6),
    ActionSpec("edit.trim_end", "Trim Clip End to Playhead", "Editing", (")",), 6),
    ActionSpec("edit.delete", "Delete", "Editing", ("Del",), 6),
    ActionSpec("edit.extract", "Extract (Delete and Close Gap)", "Editing", ("Shift+Del",), 6),
    ActionSpec("edit.lift", "Lift Timeline Zone", "Editing", ("Z",), 6),
    ActionSpec("edit.extract_zone", "Extract Timeline Zone", "Editing", ("Shift+X",), 6),
    ActionSpec("edit.group", "Group", "Editing", ("Ctrl+G",), 6),
    ActionSpec("edit.ungroup", "Ungroup", "Editing", ("Ctrl+Shift+G",), 6),
    ActionSpec("edit.select_all", "Select All", "Editing", ("Ctrl+A",), 6),
    ActionSpec("edit.undo", "Undo", "Editing", ("Ctrl+Z",), 4),
    ActionSpec("edit.redo", "Redo", "Editing", ("Ctrl+Shift+Z",), 4),
    ActionSpec("edit.copy", "Copy", "Editing", ("Ctrl+C",), 6),
    ActionSpec("edit.paste", "Paste", "Editing", ("Ctrl+V",), 6),
    ActionSpec("edit.duplicate", "Duplicate", "Editing", ("Ctrl+D",), 6),
    # Markers
    ActionSpec("marker.add", "Add or Remove Marker at Playhead", "Markers", ("G",), 4),
    # Zoom
    ActionSpec("view.zoom_in", "Zoom In", "Zoom", ("Ctrl+=", "Ctrl++"), 1),
    ActionSpec("view.zoom_out", "Zoom Out", "Zoom", ("Ctrl+-",), 1),
    # Tracks
    ActionSpec("track.lock", "Lock or Unlock Track", "Tracks", ("Shift+L",), 4),
    ActionSpec("track.mute", "Mute or Hide Track", "Tracks", ("Ctrl+Shift+H",), 4),
    # File
    ActionSpec("file.new", "New Project", "File", ("Ctrl+N",), 7),
    ActionSpec("file.open", "Open Project...", "File", ("Ctrl+O",), 7),
    ActionSpec("file.save", "Save Project", "File", ("Ctrl+S",), 7),
    ActionSpec("file.save_as", "Save Project As...", "File", ("Ctrl+Shift+S",), 7),
    ActionSpec("file.process", "Process Videos...", "File", ("Ctrl+Return",), 7),
    ActionSpec("file.quit", "Quit", "File", ("Ctrl+Q",), 1),
    # View
    ActionSpec("view.toggle_menu", "Show or Hide Menu Bar", "View", ("Ctrl+M",), 1, checkable=True),
    ActionSpec("view.fullscreen", "Fullscreen", "View", ("F11",), 1, checkable=True),
    ActionSpec("view.shortcuts", "Keyboard Shortcuts...", "View", (), 1),
    # Help
    ActionSpec("help.about", "About SongCutter", "Help", (), 1),
    ActionSpec("help.about_qt", "About Qt", "Help", (), 1),
)

SPEC_BY_ID = {spec.id: spec for spec in CATALOG}
CATEGORIES: tuple[str, ...] = tuple(dict.fromkeys(spec.category for spec in CATALOG))


class ActionManager(QObject):
    """Owns every QAction and the shortcut overrides."""

    def __init__(self, parent: QObject | None = None, store_path: Path | None = None):
        super().__init__(parent)
        self._store = JsonStore(store_path or shortcuts_path(), SHORTCUTS_DEFAULTS)
        self._overrides: dict[str, list[str]] = {}
        self._actions: dict[str, QAction] = {}
        self._load_overrides()
        for spec in CATALOG:
            action = QAction(QCoreApplication.translate("Actions", spec.text), self)
            action.setObjectName(spec.id)
            action.setCheckable(spec.checkable)
            action.setShortcutContext(Qt.ShortcutContext.WindowShortcut)
            action.setEnabled(spec.phase <= CURRENT_PHASE)
            action.setShortcuts(self._sequence_list(self._overrides.get(spec.id, list(spec.default))))
            action.setToolTip(self._tooltip(spec, action))
            action.setStatusTip(QCoreApplication.translate("Actions", spec.text))
            self._actions[spec.id] = action

    # -- lookup ----------------------------------------------------------
    def action(self, action_id: str) -> QAction:
        return self._actions[action_id]

    def actions(self) -> list[QAction]:
        return [self._actions[spec.id] for spec in CATALOG]

    def spec(self, action_id: str) -> ActionSpec:
        return SPEC_BY_ID[action_id]

    def overrides_snapshot(self) -> dict[str, list[str]]:
        return copy.deepcopy(self._overrides)

    # -- shortcut editing ------------------------------------------------
    def shortcut_strings(self, action_id: str) -> list[str]:
        return [
            sequence.toString(QKeySequence.SequenceFormat.PortableText)
            for sequence in self._actions[action_id].shortcuts()
        ]

    def shortcut_display(self, action_id: str) -> str:
        return self._actions[action_id].shortcut().toString(
            QKeySequence.SequenceFormat.NativeText
        )

    def find_conflict(self, sequences: list[str], exclude_id: str) -> ActionSpec | None:
        wanted = {self._normalize(value) for value in sequences if value}
        if not wanted:
            return None
        for spec in CATALOG:
            if spec.id == exclude_id:
                continue
            current = {
                self._normalize(value)
                for value in self.shortcut_strings(spec.id)
                if value
            }
            if wanted & current:
                return spec
        return None

    def set_shortcuts(self, action_id: str, sequences: list[str]) -> tuple[bool, str]:
        """Apply and persist shortcuts. Returns ``(ok, error message)``."""
        cleaned = [value.strip() for value in sequences if value and value.strip()]
        parsed: list[QKeySequence] = []
        for value in cleaned:
            sequence = QKeySequence(value)
            if sequence.isEmpty() or not sequence.toString():
                return False, QCoreApplication.translate(
                    "ActionManager", "The key sequence “%1” is not valid."
                ).replace("%1", value)
            parsed.append(sequence)
        normalized = [sequence.toString(QKeySequence.SequenceFormat.PortableText) for sequence in parsed]
        if len(set(normalized)) != len(normalized):
            return False, QCoreApplication.translate(
                "ActionManager", "The same key sequence is used twice."
            )
        conflict = self.find_conflict(normalized, action_id)
        if conflict is not None:
            message = QCoreApplication.translate(
                "ActionManager", "This shortcut is already used by “%1”."
            )
            return False, message.replace("%1", conflict.text)
        self._actions[action_id].setShortcuts(parsed)
        self._overrides[action_id] = normalized
        self._refresh_tooltip(action_id)
        self.save()
        return True, ""

    def reset_shortcut(self, action_id: str) -> None:
        spec = SPEC_BY_ID[action_id]
        self._overrides.pop(action_id, None)
        self._actions[action_id].setShortcuts(self._sequence_list(list(spec.default)))
        self._refresh_tooltip(action_id)
        self.save()

    def reset_all_shortcuts(self) -> None:
        self._overrides.clear()
        for spec in CATALOG:
            self._actions[spec.id].setShortcuts(self._sequence_list(list(spec.default)))
            self._refresh_tooltip(spec.id)
        self.save()

    def restore_snapshot(self, snapshot: dict[str, list[str]]) -> None:
        self._overrides = copy.deepcopy(snapshot)
        for spec in CATALOG:
            values = self._overrides.get(spec.id, list(spec.default))
            self._actions[spec.id].setShortcuts(self._sequence_list(values))
            self._refresh_tooltip(spec.id)
        self.save()

    def save(self) -> None:
        self._store.save({"schema_version": 1, "overrides": self._overrides})

    # -- helpers ---------------------------------------------------------
    def _load_overrides(self) -> None:
        data = self._store.load()
        raw = data.get("overrides", {})
        if not isinstance(raw, dict):
            return
        for action_id, value in raw.items():
            if action_id not in SPEC_BY_ID or not isinstance(value, list):
                continue
            self._overrides[action_id] = [str(item) for item in value]

    @staticmethod
    def _normalize(value: str) -> str:
        return QKeySequence(value).toString(QKeySequence.SequenceFormat.PortableText)

    @staticmethod
    def _sequence_list(values: list[str]) -> list[QKeySequence]:
        result: list[QKeySequence] = []
        for value in values:
            if not value:
                continue
            sequence = QKeySequence(value)
            if not sequence.isEmpty():
                result.append(sequence)
        return result

    @staticmethod
    def _tooltip(spec: ActionSpec, action: QAction) -> str:
        text = action.text()
        display = action.shortcut().toString(QKeySequence.SequenceFormat.NativeText)
        if display:
            return f"{text} ({display})"
        return text

    def _refresh_tooltip(self, action_id: str) -> None:
        action = self._actions[action_id]
        action.setToolTip(self._tooltip(SPEC_BY_ID[action_id], action))


def install_action_icons(manager: ActionManager) -> None:
    """Give the toolbar/menu actions their drawn icons."""
    from songcutter.ui.icons import icon

    mapping = {
        "file.new": "new",
        "file.open": "open",
        "file.save": "save",
        "file.process": "play",
        "tool.selection": "select",
        "tool.razor": "razor",
        "tool.spacer": "spacer",
        "edit.group": "film",
        "edit.ungroup": "film",
        "marker.add": "drop",
        "view.zoom_in": "add",
        "view.zoom_out": "remove",
    }
    for action_id, icon_name in mapping.items():
        manager.action(action_id).setIcon(icon(icon_name, 18))


__all__ = [
    "ActionManager",
    "ActionSpec",
    "CATALOG",
    "CATEGORIES",
    "CURRENT_PHASE",
    "SPEC_BY_ID",
    "install_action_icons",
]
