# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Washington
"""Top-left workspace: the five tabs that switch the panel content."""

from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QStackedWidget, QTabBar, QVBoxLayout, QWidget

from songcutter.config.settings import Settings
from songcutter.core.model import Project
from songcutter.ui.effects_panel import EffectsPanel
from songcutter.ui.panel import PlaceholderPanel
from songcutter.ui.project_panel import ProjectFilesPanel
from songcutter.ui.songs_panel import SongsPanel


class WorkspacePanel(QWidget):
    message = pyqtSignal(str)

    def __init__(
        self,
        project: Project,
        settings: Settings,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self._settings = settings

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.stack = QStackedWidget(self)
        self.projects_page = ProjectFilesPanel(project, self.stack)
        self.transitions_page = PlaceholderPanel(
            self.tr("Transitions"), self.tr("Not available yet"), self.stack
        )
        self.effects_page = EffectsPanel(self.stack)
        self.emojis_page = PlaceholderPanel(
            self.tr("Emojis"), self.tr("Not available yet"), self.stack
        )
        self.songs_page = SongsPanel(project, self.stack)
        for page in (
            self.projects_page,
            self.transitions_page,
            self.effects_page,
            self.emojis_page,
            self.songs_page,
        ):
            self.stack.addWidget(page)

        self.tabs = QTabBar(self)
        self.tabs.setExpanding(True)
        self.tabs.setDrawBase(True)
        self.tabs.setUsesScrollButtons(False)
        for label in (
            self.tr("Projects"),
            self.tr("Transitions"),
            self.tr("Effects"),
            self.tr("Emojis"),
            self.tr("Songs"),
        ):
            self.tabs.addTab(label)
        self.tabs.currentChanged.connect(self.stack.setCurrentIndex)
        self.tabs.setCurrentIndex(0)

        layout.addWidget(self.stack, 1)
        layout.addWidget(self.tabs)

        self.projects_page.message.connect(self.message.emit)
        self.songs_page.message.connect(self.message.emit)

    @property
    def effects_splitter(self):
        return self.effects_page.splitter
