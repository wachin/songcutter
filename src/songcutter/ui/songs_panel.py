# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Washington
"""Songs tab: the detected songs of the project."""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QLabel, QListWidget, QListWidgetItem, QWidget

from songcutter.core.model import Project, format_clock
from songcutter.ui.panel import PanelFrame


class SongsPanel(PanelFrame):
    """Read-only song list for Phase 1; renaming/enabling arrives in Phase 7."""

    message = pyqtSignal(str)

    def __init__(self, project: Project, parent: QWidget | None = None):
        super().__init__(self.tr("Songs"), parent)

        self.list = QListWidget(self)
        self.list.setAlternatingRowColors(True)
        for song in project.songs:
            item = QListWidgetItem(
                self.tr("%1  (%2 – %3)").replace("%1", song.name)
                .replace("%2", format_clock(song.start))
                .replace("%3", format_clock(song.end))
            )
            item.setData(Qt.ItemDataRole.UserRole, song.name)
            item.setToolTip(self.tr("Click to jump to this song (available in Phase 7)."))
            self.list.addItem(item)
        self.list.itemClicked.connect(self._song_clicked)
        self.add_widget(self.list, 1)

        hint = QLabel(
            self.tr(
                "Songs are detected from groups, or from the gaps between clips. "
                "Renaming and enabling songs will be available in Phase 7."
            ),
            self,
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #666666; font-size: 7.5pt;")
        self.add_widget(hint)

    def _song_clicked(self, item: QListWidgetItem) -> None:
        self.message.emit(
            self.tr("Jumping to “%1” will be available in Phase 7.").replace(
                "%1", str(item.data(Qt.ItemDataRole.UserRole))
            )
        )
