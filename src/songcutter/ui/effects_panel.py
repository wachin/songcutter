# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Washington
"""Effects tab (static layout for Phase 1).

The split panel, the search box and the effects tree exist so the design can be
evaluated. Effect cards and drag-and-drop arrive in Phase 8/9.
"""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QLabel,
    QLineEdit,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from songcutter.ui.panel import PanelFrame


class EffectsPanel(PanelFrame):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(self.tr("Effects"), parent)

        self.splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.splitter.setChildrenCollapsible(False)

        left = QWidget(self.splitter)
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 4, 0)
        left_layout.setSpacing(4)

        self.search = QLineEdit(left)
        self.search.setPlaceholderText(self.tr("Search effects..."))
        self.search.setClearButtonEnabled(True)
        left_layout.addWidget(self.search)

        self.tree = QTreeWidget(left)
        self.tree.setObjectName("effectsTree")
        self.tree.setHeaderHidden(True)
        self.tree.setRootIsDecorated(True)
        self.tree.setIndentation(12)
        audio = QTreeWidgetItem(self.tree, [self.tr("Audio")])
        for name in (
            self.tr("Volume (gain)"),
            self.tr("Fade in"),
            self.tr("Fade out"),
            self.tr("Camera noise reduction"),
            self.tr("Normalize"),
            self.tr("Mute"),
        ):
            QTreeWidgetItem(audio, [name])
        QTreeWidgetItem(self.tree, [self.tr("Video")])
        QTreeWidgetItem(self.tree, [self.tr("Favorites")])
        audio.setExpanded(True)
        left_layout.addWidget(self.tree, 1)

        hint = QLabel(
            self.tr(
                "Drag an effect onto the audio track\n"
                "(or double-click it to add it to the selected clip)"
            ),
            left,
        )
        hint.setStyleSheet("color: #666666; font-size: 7.5pt;")
        hint.setWordWrap(True)
        left_layout.addWidget(hint)

        right = QWidget(self.splitter)
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(4, 0, 0, 0)
        right_layout.setSpacing(4)

        self.header = QLabel(self.tr("Effects of: (no clip selected)"), right)
        self.header.setStyleSheet("font-weight: bold;")
        right_layout.addWidget(self.header)

        placeholder = QFrame(right)
        placeholder.setFrameShape(QFrame.Shape.StyledPanel)
        placeholder.setStyleSheet("background: #fafafa; border: 1px solid #cccccc;")
        placeholder_layout = QVBoxLayout(placeholder)
        message = QLabel(
            self.tr("Select an audio clip to edit its effects."),
            placeholder,
        )
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message.setWordWrap(True)
        message.setStyleSheet("color: #666666;")
        placeholder_layout.addWidget(message)
        right_layout.addWidget(placeholder, 1)

        self.splitter.addWidget(left)
        self.splitter.addWidget(right)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setSizes([210, 470])
        self.add_widget(self.splitter, 1)
