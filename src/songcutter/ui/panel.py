# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Washington
"""Reusable panel frame with a title bar like the design."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QToolButton, QVBoxLayout, QWidget


class PanelFrame(QWidget):
    """A bordered panel with a bold title and the design's two corner squares.

    The corner squares are the design's float/close controls. Docking is not
    part of Phase 1, so they are disabled placeholders.
    """

    def __init__(self, title: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("panelFrame")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        title_bar = QWidget(self)
        title_bar.setObjectName("panelTitleBar")
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(6, 2, 4, 2)
        title_layout.setSpacing(3)

        self.title_label = QLabel(title, title_bar)
        self.title_label.setObjectName("panelTitle")
        title_layout.addWidget(self.title_label)
        title_layout.addStretch(1)
        for tooltip in (
            self.tr("Float panel (not available yet)"),
            self.tr("Close panel (not available yet)"),
        ):
            button = QToolButton(title_bar)
            button.setObjectName("cornerButton")
            button.setFixedSize(11, 11)
            button.setEnabled(False)
            button.setToolTip(tooltip)
            title_layout.addWidget(button)

        outer.addWidget(title_bar)

        self.body = QWidget(self)
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(6, 4, 6, 4)
        self.body_layout.setSpacing(4)
        outer.addWidget(self.body, 1)

    def set_title(self, text: str) -> None:
        self.title_label.setText(text)

    def add_widget(self, widget: QWidget, stretch: int = 0) -> None:
        self.body_layout.addWidget(widget, stretch)

    def add_layout(self, layout, stretch: int = 0) -> None:
        self.body_layout.addLayout(layout, stretch)


class PlaceholderPanel(PanelFrame):
    """A panel that only says the feature is not available yet."""

    def __init__(self, title: str, message: str | None = None, parent: QWidget | None = None):
        super().__init__(title, parent)
        label = QLabel(message or self.tr("Not available yet"), self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: #666666; font-size: 10pt;")
        self.add_widget(label, 1)
