# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Washington
"""Timeline block: toolbar, ruler, two track lanes and track headers.

Phase 1 paints a read-only sample project. The widget already reads everything
from the model, so later phases can edit the model and repaint.
"""

from __future__ import annotations

import math

import numpy as np
from PyQt6.QtCore import QPointF, QRect, QRectF, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QPainter, QPainterPath, QPen, QPolygonF
from PyQt6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QScrollBar,
    QSizePolicy,
    QSlider,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from songcutter.config.settings import Settings
from songcutter.core.model import Project, format_clock, format_timecode
from songcutter.ui.actions import ActionManager
from songcutter.ui.icons import icon

RULER_HEIGHT = 26
VIDEO_LANE_HEIGHT = 62
AUDIO_LANE_HEIGHT = 170
HEADER_WIDTH = 96

ZOOM_MIN = 0.02  # pixels per second
ZOOM_MAX = 400.0
SLIDER_MAX = 1000

RULER_STEPS = (1, 2, 5, 10, 15, 30, 60, 120, 300, 600, 900, 1800, 3600)


def slider_to_pps(value: int) -> float:
    ratio = max(0, min(SLIDER_MAX, value)) / SLIDER_MAX
    return math.exp(math.log(ZOOM_MIN) + ratio * (math.log(ZOOM_MAX) - math.log(ZOOM_MIN)))


def pps_to_slider(pps: float) -> int:
    pps = max(ZOOM_MIN, min(ZOOM_MAX, pps))
    ratio = (math.log(pps) - math.log(ZOOM_MIN)) / (math.log(ZOOM_MAX) - math.log(ZOOM_MIN))
    return int(round(ratio * SLIDER_MAX))


class TimelineView(QWidget):
    """Paints the ruler, the video lane and the audio lane."""

    playhead_moved = pyqtSignal(float)
    view_changed = pyqtSignal()
    scroll_requested = pyqtSignal(float)
    zoom_requested = pyqtSignal(float, float, float)  # factor, anchor time, anchor x

    def __init__(self, project: Project, parent: QWidget | None = None):
        super().__init__(parent)
        self._project = project
        self._pps = 1.0
        self._scroll = 0.0
        self._playhead = 0.0
        self._channel = "left"
        self._half_wave = True
        self._show_db = True
        self._auto_fit = True
        self._last_width = 0
        self._peak_cache: dict[tuple[str, str], np.ndarray] = {}
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMouseTracking(True)
        self.setMinimumHeight(RULER_HEIGHT + VIDEO_LANE_HEIGHT + AUDIO_LANE_HEIGHT)

    # -- state -----------------------------------------------------------
    @property
    def duration(self) -> float:
        return max(self._project.duration, 1.0)

    @property
    def pixels_per_second(self) -> float:
        return self._pps

    @property
    def scroll(self) -> float:
        return self._scroll

    @property
    def playhead(self) -> float:
        return self._playhead

    def visible_seconds(self) -> float:
        return max(self.width(), 1) / self._pps

    def set_pixels_per_second(self, value: float) -> None:
        value = max(ZOOM_MIN, min(ZOOM_MAX, value))
        if abs(value - self._pps) < 1e-9:
            return
        self._pps = value
        self._scroll = max(0.0, min(self._scroll, self._max_scroll()))
        self.update()
        self.view_changed.emit()

    def set_scroll(self, seconds: float) -> None:
        seconds = max(0.0, min(seconds, self._max_scroll()))
        if abs(seconds - self._scroll) < 1e-9:
            return
        self._scroll = seconds
        self.update()
        self.view_changed.emit()

    def set_playhead(self, seconds: float) -> None:
        seconds = max(0.0, min(seconds, self.duration))
        if abs(seconds - self._playhead) < 1e-9:
            return
        self._playhead = seconds
        self.update()
        self.playhead_moved.emit(seconds)

    def set_channel(self, channel: str) -> None:
        self._channel = "right" if channel == "right" else "left"
        self.update()

    def set_half_wave(self, enabled: bool) -> None:
        self._half_wave = bool(enabled)
        self.update()

    def set_show_db(self, enabled: bool) -> None:
        self._show_db = bool(enabled)
        self.update()

    def fit(self) -> None:
        width = max(self.width(), 100)
        self._pps = max(ZOOM_MIN, min(ZOOM_MAX, (width - 4) / self.duration))
        self._scroll = 0.0
        self.update()
        self.view_changed.emit()

    def _max_scroll(self) -> float:
        return max(0.0, self.duration - self.visible_seconds())

    # -- events ----------------------------------------------------------
    def resizeEvent(self, event) -> None:  # noqa: N802 (Qt naming)
        old_width = self._last_width
        self._last_width = self.width()
        was_fit = old_width > 0 and old_width / self._pps >= self.duration * 0.99
        super().resizeEvent(event)
        if self._auto_fit and self.width() > 100:
            self._auto_fit = False
            self.fit()
        elif was_fit and self._scroll <= 0.5:
            # Keep the whole project visible when the window grows or shrinks,
            # as long as the user had not zoomed in.
            self.fit()
        else:
            self._scroll = max(0.0, min(self._scroll, self._max_scroll()))
            self.view_changed.emit()

    def mousePressEvent(self, event) -> None:  # noqa: N802 (Qt naming)
        if event.button() == Qt.MouseButton.LeftButton:
            seconds = self._scroll + event.position().x() / self._pps
            self.set_playhead(seconds)
        super().mousePressEvent(event)

    def wheelEvent(self, event) -> None:  # noqa: N802 (Qt naming)
        delta = event.angleDelta().y()
        if delta == 0:
            return
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            factor = 1.25 if delta > 0 else 0.8
            anchor_time = self._scroll + event.position().x() / self._pps
            self.zoom_requested.emit(factor, anchor_time, event.position().x())
            event.accept()
            return
        step = max(1.0, self.visible_seconds() * 0.08)
        self.scroll_requested.emit(-math.copysign(step, delta))
        event.accept()

    def sizeHint(self) -> QSize:  # noqa: N802 (Qt naming)
        return QSize(900, RULER_HEIGHT + VIDEO_LANE_HEIGHT + AUDIO_LANE_HEIGHT)

    # -- painting --------------------------------------------------------
    def paintEvent(self, event) -> None:  # noqa: N802 (Qt naming)
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#ffffff"))
        self._paint_ruler(painter)
        self._paint_video_lane(painter)
        self._paint_audio_lane(painter)
        self._paint_markers(painter)
        self._paint_playhead(painter)
        painter.end()

    def _x(self, seconds: float) -> float:
        return (seconds - self._scroll) * self._pps

    def _ruler_step(self) -> int:
        for step in RULER_STEPS:
            if step * self._pps >= 90:
                return step
        return RULER_STEPS[-1]

    def _paint_ruler(self, painter: QPainter) -> None:
        width = self.width()
        painter.fillRect(QRect(0, 0, width, RULER_HEIGHT), QColor("#f7f7f7"))
        painter.setPen(QColor("#999999"))
        painter.drawLine(0, RULER_HEIGHT - 1, width, RULER_HEIGHT - 1)

        font = QFont(painter.font())
        font.setPointSizeF(7.5)
        painter.setFont(font)

        step = self._ruler_step()
        start = math.floor(self._scroll / step) * step
        end = self._scroll + self.visible_seconds()
        tick = start
        while tick <= end:
            x = int(self._x(tick))
            painter.setPen(QColor("#999999"))
            painter.drawLine(x, 18, x, RULER_HEIGHT - 1)
            painter.setPen(QColor("#333333"))
            painter.drawText(
                QRect(x + 3, 2, 90, 15),
                int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
                format_clock(tick),
            )
            tick += step

    def _paint_video_lane(self, painter: QPainter) -> None:
        top = RULER_HEIGHT
        width = self.width()
        painter.save()
        painter.setClipRect(QRectF(0, top, width, VIDEO_LANE_HEIGHT))
        painter.fillRect(QRect(0, top, width, VIDEO_LANE_HEIGHT), QColor("#ffffff"))

        track = self._project.track("video")
        for clip in track.clips if track else []:
            self._paint_video_clip(painter, clip, top)

        painter.setPen(QColor("#b0b0b0"))
        painter.drawLine(0, top + VIDEO_LANE_HEIGHT - 1, width, top + VIDEO_LANE_HEIGHT - 1)
        painter.restore()

    def _paint_video_clip(self, painter: QPainter, clip, top: float) -> None:
        x = self._x(clip.start)
        width = clip.duration * self._pps
        if x > self.width() or x + width < 0:
            return
        rect = QRectF(x + 1, top + 3, max(width - 2, 1), VIDEO_LANE_HEIGHT - 7)
        painter.setPen(QPen(QColor("#333333"), 1))
        painter.setBrush(QColor("#ffd700"))
        painter.drawRect(rect)

        name_font = QFont(painter.font())
        name_font.setBold(True)
        name_font.setPointSizeF(8.0)
        painter.setFont(name_font)

        text_left = rect.left() + 8
        if width > 110:
            thumb = QRectF(rect.left() + 6, rect.top() + 5, 40, 40)
            painter.setPen(QPen(QColor("#333333"), 1))
            painter.setBrush(QColor("#ffffff"))
            painter.drawRect(thumb)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("#333333"))
            for hole in range(6):
                hole_x = thumb.left() + 3 + hole * 6
                painter.drawRect(QRectF(hole_x, thumb.top() + 2, 3, 3))
                painter.drawRect(QRectF(hole_x, thumb.bottom() - 5, 3, 3))
            small = QFont(painter.font())
            small.setPixelSize(7)
            painter.setFont(small)
            painter.setPen(QColor("#666666"))
            painter.drawText(thumb, int(Qt.AlignmentFlag.AlignCenter), "foto")
            painter.setFont(name_font)
            text_left = rect.left() + 52

        available = rect.right() - text_left - 4
        metrics = QFontMetrics(name_font)
        name = metrics.elidedText(clip.name, Qt.TextElideMode.ElideRight, int(max(10, available)))
        painter.setPen(QColor("#111111"))
        painter.drawText(
            QRectF(text_left, rect.top(), max(10, available), rect.height()),
            int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
            name,
        )

    def _paint_audio_lane(self, painter: QPainter) -> None:
        top = RULER_HEIGHT + VIDEO_LANE_HEIGHT
        height = self._audio_height()
        width = self.width()
        painter.save()
        painter.setClipRect(QRectF(0, top, width, height))
        painter.fillRect(QRect(0, top, width, int(height)), QColor("#ffffff"))

        track = self._project.track("audio")
        for clip in track.clips if track else []:
            x = self._x(clip.start)
            clip_width = clip.duration * self._pps
            if x > width or x + clip_width < 0:
                continue
            rect = QRectF(x + 1, top + 2, max(clip_width - 2, 1), height - 5)
            painter.setPen(QPen(QColor("#333333"), 1))
            painter.setBrush(QColor("#aaaaff"))
            painter.drawRect(rect)
            painter.save()
            painter.setClipRect(rect)
            self._paint_waveform(painter, clip, rect)
            painter.restore()

        if self._show_db:
            self._paint_db_scale(painter, top, height)

        painter.setPen(QColor("#b0b0b0"))
        painter.drawLine(0, int(top + height - 1), width, int(top + height - 1))
        painter.restore()

    def _audio_height(self) -> float:
        return max(
            float(AUDIO_LANE_HEIGHT),
            float(self.height() - RULER_HEIGHT - VIDEO_LANE_HEIGHT),
        )

    def _peaks(self, clip) -> np.ndarray:
        key = (clip.id, self._channel)
        cached = self._peak_cache.get(key)
        if cached is not None:
            return cached
        seed = (sum((index + 1) * ord(char) for index, char in enumerate(clip.id)) + 17) % (2**32)
        if self._channel == "right":
            seed += 101
        rng = np.random.default_rng(seed)
        count = 4000
        noise = rng.random(count) ** 2.0
        smooth = np.convolve(noise, np.ones(31) / 31.0, mode="same")
        t = np.linspace(0.0, 1.0, count)
        phase = seed % 17
        envelope = (
            0.55
            + 0.22 * np.sin(t * 3.7 + phase * 0.4)
            + 0.15 * np.sin(t * 11.3 + phase * 1.7)
            + 0.08 * np.sin(t * 29.1 + phase * 0.9)
        )
        envelope = np.clip(envelope, 0.12, 1.0)
        peaks = np.clip(smooth * envelope * 2.2, 0.01, 1.0)
        self._peak_cache[key] = peaks
        return peaks

    def _paint_waveform(self, painter: QPainter, clip, rect: QRectF) -> None:
        left = max(rect.left(), 0.0)
        right = min(rect.right(), float(self.width()))
        if right - left < 1:
            return
        step = 1 if right - left <= 4000 else 2
        xs = np.arange(int(left), int(right), step)
        if xs.size < 2:
            return
        fractions = (xs - rect.left()) / max(rect.width(), 1.0)
        peaks = self._peaks(clip)
        indices = np.clip((fractions * (peaks.size - 1)).astype(int), 0, peaks.size - 1)
        gain = 10 ** (clip.gain_db / 20.0)
        values = np.clip(peaks[indices] * gain, 0.0, 1.0)

        baseline = rect.bottom() - 4
        amplitude = rect.height() - 12
        path = QPainterPath()
        if self._half_wave:
            path.moveTo(float(xs[0]), baseline)
            for x, value in zip(xs, values, strict=True):
                path.lineTo(float(x), baseline - float(value) * amplitude)
            path.lineTo(float(xs[-1]), baseline)
        else:
            middle = baseline - amplitude / 2.0
            path.moveTo(float(xs[0]), middle)
            for x, value in zip(xs, values, strict=True):
                path.lineTo(float(x), middle - float(value) * amplitude / 2.0)
            for x, value in reversed(list(zip(xs, values, strict=True))):
                path.lineTo(float(x), middle + float(value) * amplitude / 2.0)
        path.closeSubpath()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#2b2b2b"))
        painter.drawPath(path)

    def _paint_db_scale(self, painter: QPainter, top: float, height: float) -> None:
        font = QFont(painter.font())
        font.setPointSizeF(6.5)
        painter.setFont(font)
        metrics = QFontMetrics(font)
        pen = QPen(QColor("#8a8a8a"), 1, Qt.PenStyle.DashLine)
        for fraction, label in ((0.10, "0 dB (max)"), (0.38, "-6 dB"), (0.62, "-12 dB")):
            y = top + height * fraction
            painter.setPen(pen)
            painter.drawLine(0, int(y), self.width(), int(y))
            label_width = metrics.horizontalAdvance(label) + 6
            painter.fillRect(
                QRectF(2, y - 11, label_width, 11), QColor(255, 255, 255, 205)
            )
            painter.setPen(QColor("#444444"))
            painter.drawText(QPointF(4, y - 2), label)

    def _paint_markers(self, painter: QPainter) -> None:
        font = QFont(painter.font())
        font.setPointSizeF(6.5)
        painter.setFont(font)
        for marker in self._project.markers:
            x = self._x(marker.time)
            if x < -40 or x > self.width() + 40:
                continue
            painter.setPen(QPen(QColor("#2e7d32"), 1))
            painter.drawLine(QPointF(x, 15), QPointF(x, RULER_HEIGHT))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("#3aa856"))
            painter.drawPolygon(
                QPolygonF(
                    [
                        QPointF(x, 16),
                        QPointF(x + 9, 19),
                        QPointF(x, 22),
                    ]
                )
            )
            painter.setPen(QColor("#2e7d32"))
            painter.drawText(QPointF(x + 11, 23), marker.name)

    def _paint_playhead(self, painter: QPainter) -> None:
        x = self._x(self._playhead)
        if x < -4 or x > self.width() + 4:
            return
        painter.setPen(QPen(QColor("#e00000"), 1))
        painter.drawLine(QPointF(x, 0), QPointF(x, self.height()))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#e00000"))
        painter.drawPolygon(
            QPolygonF([QPointF(x - 5, 0), QPointF(x + 5, 0), QPointF(x, 7)])
        )


class VideoTrackHeader(QWidget):
    message = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("trackHeader")
        self.setFixedWidth(HEADER_WIDTH)
        self.setFixedHeight(VIDEO_LANE_HEIGHT)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(2)

        title = QLabel(self.tr("Video  ▾"), self)
        title.setObjectName("trackTitle")
        layout.addWidget(title)

        row = QHBoxLayout()
        row.setSpacing(2)
        self.eye_button = QToolButton(self)
        self.eye_button.setIcon(icon("eye", 15))
        self.eye_button.setCheckable(True)
        self.eye_button.setFixedSize(24, 24)
        self.eye_button.setToolTip(self.tr("Hide video track (available in Phase 4)"))
        self.eye_button.clicked.connect(self._not_available)
        self.lock_button = QToolButton(self)
        self.lock_button.setIcon(icon("lock", 15))
        self.lock_button.setCheckable(True)
        self.lock_button.setFixedSize(24, 24)
        self.lock_button.setToolTip(self.tr("Lock video track (available in Phase 4)"))
        self.lock_button.clicked.connect(self._not_available)
        row.addWidget(self.eye_button)
        row.addWidget(self.lock_button)
        row.addStretch(1)
        layout.addLayout(row)
        layout.addStretch(1)

    def _not_available(self) -> None:
        self.message.emit(self.tr("Track visibility and locking arrive in Phase 4."))


class AudioTrackHeader(QWidget):
    message = pyqtSignal(str)
    channel_changed = pyqtSignal(str)
    half_wave_changed = pyqtSignal(bool)

    def __init__(
        self,
        channel: str = "left",
        half_wave: bool = True,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.setObjectName("trackHeader")
        self.setFixedWidth(HEADER_WIDTH)
        self.setMinimumHeight(AUDIO_LANE_HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 3)
        layout.setSpacing(3)

        title = QLabel(self.tr("Audio  ▾"), self)
        title.setObjectName("trackTitle")
        layout.addWidget(title)

        self.mute_button = QToolButton(self)
        self.mute_button.setText(self.tr("Mute"))
        self.mute_button.setCheckable(True)
        self.mute_button.setFixedHeight(21)
        self.mute_button.setToolTip(self.tr("Mute this track (available in Phase 8)"))
        self.mute_button.clicked.connect(self._not_available)
        layout.addWidget(self.mute_button)

        self.lock_button = QToolButton(self)
        self.lock_button.setText(self.tr("Lock"))
        self.lock_button.setCheckable(True)
        self.lock_button.setFixedHeight(21)
        self.lock_button.setToolTip(self.tr("Lock this track (available in Phase 4)"))
        self.lock_button.clicked.connect(self._not_available)
        layout.addWidget(self.lock_button)

        self.channel = QComboBox(self)
        self.channel.addItems([self.tr("Ch: Left"), self.tr("Ch: Right")])
        self.channel.setCurrentIndex(1 if channel == "right" else 0)
        self.channel.setFixedHeight(23)
        self.channel.setToolTip(self.tr("Waveform channel (display only)"))
        self.channel.currentIndexChanged.connect(self._channel_changed)
        layout.addWidget(self.channel)

        self.half_wave = QCheckBox(self.tr("Half wave"), self)
        self.half_wave.setChecked(half_wave)
        self.half_wave.setToolTip(self.tr("Show only the upper half of the waveform"))
        self.half_wave.toggled.connect(self.half_wave_changed.emit)
        layout.addWidget(self.half_wave)
        layout.addStretch(1)

    def _channel_changed(self, index: int) -> None:
        self.channel_changed.emit("right" if index == 1 else "left")

    def _not_available(self) -> None:
        self.message.emit(self.tr("Track mute and locking arrive in a later phase."))


class TimelineToolbar(QWidget):
    message = pyqtSignal(str)
    zoom_in_requested = pyqtSignal()
    zoom_out_requested = pyqtSignal()
    fit_requested = pyqtSignal()
    zoom_slider_changed = pyqtSignal(int)
    scroll_changed = pyqtSignal(int)

    def __init__(self, actions: ActionManager, parent: QWidget | None = None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(2)

        editing_tools = (
            ("add", self.tr("Add clip (Phase 6)")),
            ("remove", self.tr("Remove clip (Phase 6)")),
            ("razor", self.tr("Cut (Phase 6)")),
            ("drop", self.tr("Drop / insert (Phase 6)")),
            ("arrow_left", self.tr("Move clip left (Phase 6)")),
            ("arrow_right", self.tr("Move clip right (Phase 6)")),
            ("close", self.tr("Delete clip (Phase 6)")),
        )
        for icon_name, tooltip in editing_tools:
            button = QToolButton(self)
            button.setIcon(icon(icon_name, 18))
            button.setIconSize(QSize(18, 18))
            button.setAutoRaise(True)
            button.setFixedSize(26, 24)
            button.setToolTip(tooltip)
            button.clicked.connect(
                lambda _checked=False, text=tooltip: self.message.emit(text)
            )
            layout.addWidget(button)

        layout.addSpacing(6)
        self._tool_buttons: dict[str, QToolButton] = {}
        self._tool_button_group = QButtonGroup(self)
        self._tool_button_group.setExclusive(True)
        for action_id, label in (
            ("tool.selection", "S"),
            ("tool.razor", "X"),
            ("tool.spacer", "M"),
        ):
            action = actions.action(action_id)
            button = QToolButton(self)
            button.setText(label)
            button.setCheckable(True)
            button.setToolTip(action.toolTip())
            button.setFixedSize(24, 24)
            font = QFont(button.font())
            font.setBold(True)
            button.setFont(font)
            button.setChecked(action.isChecked())
            button.clicked.connect(
                lambda _checked=False, aid=action_id: actions.action(aid).trigger()
            )
            action.toggled.connect(
                lambda checked, aid=action_id: self._sync_tool_button(aid, checked)
            )
            self._tool_button_group.addButton(button)
            self._tool_buttons[action_id] = button
            layout.addWidget(button)

        layout.addSpacing(4)
        for label, tooltip in (
            (self.tr("Join"), self.tr("Join two pieces (Phase 6)")),
            (self.tr("Group"), self.tr("Group clips into a song (Phase 6)")),
            (self.tr("Ungroup"), self.tr("Ungroup clips (Phase 6)")),
            (self.tr("Marker"), self.tr("Add or remove a marker (Phase 4)")),
        ):
            button = QToolButton(self)
            button.setText(label)
            button.setToolTip(tooltip)
            button.setFixedHeight(24)
            button.clicked.connect(lambda _checked=False, text=tooltip: self.message.emit(text))
            layout.addWidget(button)

        self.snap = QCheckBox(self.tr("Snap"), self)
        self.snap.setChecked(True)
        self.snap.setToolTip(self.tr("Snapping arrives in Phase 4"))
        layout.addWidget(self.snap)

        layout.addStretch(1)

        zoom_out = QToolButton(self)
        zoom_out.setText("−")
        zoom_out.setFixedSize(22, 24)
        zoom_out.setToolTip(self.tr("Zoom out (Ctrl+-)"))
        zoom_out.clicked.connect(self.zoom_out_requested.emit)
        layout.addWidget(zoom_out)

        self.zoom_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.zoom_slider.setRange(0, SLIDER_MAX)
        self.zoom_slider.setFixedWidth(120)
        self.zoom_slider.setToolTip(self.tr("Timeline zoom"))
        self.zoom_slider.valueChanged.connect(self.zoom_slider_changed.emit)
        layout.addWidget(self.zoom_slider)

        zoom_in = QToolButton(self)
        zoom_in.setText("+")
        zoom_in.setFixedSize(22, 24)
        zoom_in.setToolTip(self.tr("Zoom in (Ctrl+=)"))
        zoom_in.clicked.connect(self.zoom_in_requested.emit)
        layout.addWidget(zoom_in)

        fit = QToolButton(self)
        fit.setText(self.tr("Fit"))
        fit.setFixedHeight(24)
        fit.setToolTip(self.tr("Fit the whole project in the timeline"))
        fit.clicked.connect(self.fit_requested.emit)
        layout.addWidget(fit)

        self.scroll = QScrollBar(Qt.Orientation.Horizontal, self)
        self.scroll.setObjectName("timelineScroll")
        self.scroll.setMinimumWidth(120)
        self.scroll.valueChanged.connect(self.scroll_changed.emit)
        layout.addWidget(self.scroll, 1)

    def _sync_tool_button(self, action_id: str, checked: bool) -> None:
        button = self._tool_buttons.get(action_id)
        if button is not None:
            button.blockSignals(True)
            button.setChecked(checked)
            button.blockSignals(False)


class TimelinePanel(QWidget):
    """The complete timeline block shown below the top panels."""

    message = pyqtSignal(str)
    playhead_changed = pyqtSignal(float)

    def __init__(
        self,
        project: Project,
        actions: ActionManager,
        settings: Settings,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self._project = project
        self._actions = actions
        self._settings = settings
        self._syncing = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self.toolbar = TimelineToolbar(actions, self)
        layout.addWidget(self.toolbar)

        content = QHBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(0)

        headers = QWidget(self)
        headers.setFixedWidth(HEADER_WIDTH)
        headers_layout = QVBoxLayout(headers)
        headers_layout.setContentsMargins(0, 0, 0, 0)
        headers_layout.setSpacing(0)

        self.time_box = QLabel(format_timecode(0, project.fps), headers)
        self.time_box.setObjectName("timecodeBox")
        self.time_box.setFixedHeight(RULER_HEIGHT)
        self.time_box.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        headers_layout.addWidget(self.time_box)

        self.video_header = VideoTrackHeader(headers)
        self.audio_header = AudioTrackHeader(
            channel=settings.timeline_channel, half_wave=settings.half_wave, parent=headers
        )
        headers_layout.addWidget(self.video_header)
        headers_layout.addWidget(self.audio_header, 1)
        content.addWidget(headers)

        self.view = TimelineView(project, self)
        self.view.set_channel(settings.timeline_channel)
        self.view.set_half_wave(settings.half_wave)
        self.view.set_show_db(settings.show_db_scale)
        content.addWidget(self.view, 1)

        scroll_column = QWidget(self)
        scroll_column.setFixedWidth(15)
        scroll_layout = QVBoxLayout(scroll_column)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(0)
        scroll_layout.addSpacing(RULER_HEIGHT)
        self.vertical_scroll = QScrollBar(Qt.Orientation.Vertical, scroll_column)
        self.vertical_scroll.setRange(0, 0)
        self.vertical_scroll.setToolTip(self.tr("Vertical scroll (track heights arrive in Phase 5)"))
        scroll_layout.addWidget(self.vertical_scroll, 1)
        content.addWidget(scroll_column)

        layout.addLayout(content, 1)

        self.toolbar.message.connect(self.message.emit)
        self.video_header.message.connect(self.message.emit)
        self.audio_header.message.connect(self.message.emit)
        self.toolbar.zoom_in_requested.connect(self.zoom_in)
        self.toolbar.zoom_out_requested.connect(self.zoom_out)
        self.toolbar.fit_requested.connect(self.fit)
        self.toolbar.zoom_slider_changed.connect(self._slider_changed)
        self.toolbar.scroll_changed.connect(self._scrollbar_changed)
        self.view.view_changed.connect(self._sync_controls)
        self.view.playhead_moved.connect(self._playhead_moved)
        self.view.scroll_requested.connect(self._scroll_by)
        self.view.zoom_requested.connect(self._zoom_around)
        self.audio_header.channel_changed.connect(self._channel_changed)
        self.audio_header.half_wave_changed.connect(self._half_wave_changed)
        self._sync_controls()

    # -- public ----------------------------------------------------------
    def fit(self) -> None:
        self.view.fit()

    def zoom_in(self) -> None:
        self._zoom_factor(1.5)

    def zoom_out(self) -> None:
        self._zoom_factor(1.0 / 1.5)

    def set_playhead(self, seconds: float) -> None:
        self.view.set_playhead(seconds)

    # -- internal --------------------------------------------------------
    def _zoom_factor(self, factor: float, anchor_time: float | None = None) -> None:
        old_pps = self.view.pixels_per_second
        new_pps = max(ZOOM_MIN, min(ZOOM_MAX, old_pps * factor))
        if abs(new_pps - old_pps) < 1e-9:
            return
        anchor = self.view.playhead if anchor_time is None else anchor_time
        offset = (anchor - self.view.scroll) * old_pps
        self.view.set_pixels_per_second(new_pps)
        self.view.set_scroll(anchor - offset / new_pps)

    def _zoom_around(self, factor: float, anchor_time: float, anchor_x: float) -> None:
        old_pps = self.view.pixels_per_second
        new_pps = max(ZOOM_MIN, min(ZOOM_MAX, old_pps * factor))
        if abs(new_pps - old_pps) < 1e-9:
            return
        self.view.set_pixels_per_second(new_pps)
        self.view.set_scroll(anchor_time - anchor_x / new_pps)

    def _scroll_by(self, seconds: float) -> None:
        self.view.set_scroll(self.view.scroll + seconds)

    def _slider_changed(self, value: int) -> None:
        if self._syncing:
            return
        self.view.set_pixels_per_second(slider_to_pps(value))

    def _scrollbar_changed(self, value: int) -> None:
        if self._syncing:
            return
        self.view.set_scroll(value / 1000.0)

    def _sync_controls(self) -> None:
        self._syncing = True
        try:
            visible = self.view.visible_seconds()
            maximum = max(0, int(round((self.view.duration - visible) * 1000)))
            self.toolbar.scroll.setRange(0, maximum)
            self.toolbar.scroll.setPageStep(max(1, int(visible * 1000)))
            self.toolbar.scroll.setSingleStep(100)
            self.toolbar.scroll.setValue(int(round(self.view.scroll * 1000)))
            self.toolbar.zoom_slider.setValue(pps_to_slider(self.view.pixels_per_second))
        finally:
            self._syncing = False

    def _playhead_moved(self, seconds: float) -> None:
        self.time_box.setText(format_timecode(seconds, self._project.fps))
        self.playhead_changed.emit(seconds)

    def _channel_changed(self, channel: str) -> None:
        self.view.set_channel(channel)
        self._settings.timeline_channel = channel
        self._settings.save()

    def _half_wave_changed(self, enabled: bool) -> None:
        self.view.set_half_wave(enabled)
        self._settings.half_wave = enabled
        self._settings.save()
