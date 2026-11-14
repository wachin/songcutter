# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Washington
"""Preview video panel (static shell; playback arrives in Phase 3)."""

from __future__ import annotations

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from songcutter.core.model import format_timecode
from songcutter.ui.icons import icon
from songcutter.ui.panel import PanelFrame


class PreviewPanel(PanelFrame):
    message = pyqtSignal(str)

    def __init__(self, fps: float = 30.0, parent: QWidget | None = None):
        super().__init__(self.tr("Preview video"), parent)
        self._fps = fps

        self.video_area = QFrame(self)
        self.video_area.setObjectName("videoArea")
        self.video_area.setMinimumHeight(120)
        video_layout = QVBoxLayout(self.video_area)
        self.video_placeholder = QLabel(self.tr("Video"), self.video_area)
        self.video_placeholder.setObjectName("videoPlaceholder")
        self.video_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        video_layout.addWidget(self.video_placeholder)
        self.add_widget(self.video_area, 1)

        self.seek = QSlider(Qt.Orientation.Horizontal, self)
        self.seek.setRange(0, 1000)
        self.seek.setValue(0)
        self.add_widget(self.seek)

        controls = QHBoxLayout()
        controls.setSpacing(4)

        for label in (self.tr("In"), self.tr("Out"), self.tr("Mark")):
            button = QPushButton(label, self)
            button.setFixedHeight(24)
            button.setToolTip(self.tr("%1 (available in Phase 3)").replace("%1", label))
            button.clicked.connect(self._not_available)
            controls.addWidget(button)

        for icon_name, tooltip in (
            ("rewind", self.tr("Rewind (Phase 3)")),
            ("play", self.tr("Play / Stop (Phase 3)")),
            ("forward", self.tr("Forward (Phase 3)")),
            ("rewind", self.tr("Fourth transport icon: duplicate rewind in the design")),
        ):
            button = QToolButton(self)
            button.setIcon(icon(icon_name, 26))
            button.setIconSize(QSize(26, 26))
            button.setFixedSize(32, 28)
            button.setAutoRaise(True)
            button.setToolTip(tooltip)
            button.clicked.connect(self._not_available)
            controls.addWidget(button)

        self.timecode = QLabel(format_timecode(0, self._fps), self)
        self.timecode.setObjectName("timecode")
        self.timecode.setMinimumWidth(92)
        self.timecode.setAlignment(Qt.AlignmentFlag.AlignCenter)
        controls.addWidget(self.timecode)

        self.speed = QComboBox(self)
        self.speed.addItems(["0.5x", "1x", "1.5x", "2x"])
        self.speed.setCurrentText("1x")
        self.speed.setFixedWidth(52)
        self.speed.setToolTip(self.tr("Playback speed (available in Phase 3)"))
        controls.addWidget(self.speed)

        volume_icon = QLabel(self)
        volume_icon.setPixmap(icon("speaker", 16).pixmap(16, 16))
        volume_icon.setToolTip(self.tr("Preview volume"))
        controls.addWidget(volume_icon)

        self.volume = QSlider(Qt.Orientation.Horizontal, self)
        self.volume.setRange(0, 100)
        self.volume.setValue(100)
        self.volume.setFixedWidth(60)
        controls.addWidget(self.volume)

        for label in (self.tr("Save frame"), self.tr("Copy frame")):
            button = QPushButton(label, self)
            button.setFixedHeight(24)
            button.setToolTip(self.tr("%1 (available in Phase 3)").replace("%1", label))
            button.clicked.connect(self._not_available)
            controls.addWidget(button)

        self.add_layout(controls)

    def set_timecode(self, seconds: float) -> None:
        self.timecode.setText(format_timecode(seconds, self._fps))

    def _not_available(self) -> None:
        self.message.emit(self.tr("Preview playback and frame capture arrive in Phase 3."))
