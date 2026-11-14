# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Washington
"""Runtime-drawn icons.

The design uses simple flat icons. They are painted with QPainter so the
application ships no third-party icon set. Icons are cached per name/size.

Disabled icons are given the same pixmap as the normal state so toolbar
placeholders keep the look of the design while remaining non-clickable.
"""

from __future__ import annotations

from collections.abc import Callable

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QFont, QIcon, QPainter, QPainterPath, QPen, QPixmap, QPolygonF

DARK = QColor("#333333")
GREEN = QColor("#2e9e44")
RED = QColor("#d22b2b")
BLUE = QColor("#1e6fd9")
ORANGE = QColor("#ffa500")
YELLOW = QColor("#ffd700")
PURPLE = QColor("#6a5acd")
WHITE = QColor("#ffffff")

_CACHE: dict[tuple[str, int], QIcon] = {}


def icon(name: str, size: int = 20) -> QIcon:
    """Return a cached icon drawn at ``size`` logical pixels."""
    key = (name, size)
    cached = _CACHE.get(key)
    if cached is not None:
        return cached
    scale = 2  # render at 2x for crisp output on HiDPI screens
    pixmap = QPixmap(size * scale, size * scale)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
    try:
        _DRAWERS[name](painter, pixmap.width())
    finally:
        painter.end()
    result = QIcon()
    result.addPixmap(pixmap, QIcon.Mode.Normal, QIcon.State.Off)
    result.addPixmap(pixmap, QIcon.Mode.Active, QIcon.State.Off)
    result.addPixmap(pixmap, QIcon.Mode.Disabled, QIcon.State.Off)
    _CACHE[key] = result
    return result


# -- helpers ------------------------------------------------------------
def _pen(color: QColor, s: float, width: float = 0.055) -> QPen:
    pen = QPen(color)
    pen.setWidthF(max(1.0, s * width))
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    return pen


def _polygon(points: list[tuple[float, float]], s: float) -> QPolygonF:
    return QPolygonF([QPointF(x * s, y * s) for x, y in points])


def _arrow_up(p: QPainter, s: float, x: float, top: float, bottom: float, width: float, color: QColor):
    head = width * 1.7
    body = width * 0.55
    points = [
        (x, top),
        (x + head, top + head),
        (x + body, top + head),
        (x + body, bottom),
        (x - body, bottom),
        (x - body, top + head),
        (x - head, top + head),
    ]
    p.setPen(_pen(DARK, s, 0.03))
    p.setBrush(color)
    p.drawPolygon(_polygon(points, s))


def _arrow_down(p: QPainter, s: float, x: float, top: float, bottom: float, width: float, color: QColor):
    head = width * 1.7
    body = width * 0.55
    points = [
        (x, bottom),
        (x + head, bottom - head),
        (x + body, bottom - head),
        (x + body, top),
        (x - body, top),
        (x - body, bottom - head),
        (x - head, bottom - head),
    ]
    p.setPen(_pen(DARK, s, 0.03))
    p.setBrush(color)
    p.drawPolygon(_polygon(points, s))


def _triangle_right(p: QPainter, s: float, left: float, top: float, right: float, bottom: float, color: QColor):
    points = [(left, top), (right, (top + bottom) / 2), (left, bottom)]
    p.setPen(_pen(DARK, s, 0.03))
    p.setBrush(color)
    p.drawPolygon(_polygon(points, s))


def _triangle_left(p: QPainter, s: float, left: float, top: float, right: float, bottom: float, color: QColor):
    points = [(right, top), (left, (top + bottom) / 2), (right, bottom)]
    p.setPen(_pen(DARK, s, 0.03))
    p.setBrush(color)
    p.drawPolygon(_polygon(points, s))


def _circle(p: QPainter, s: float, color: QColor):
    p.setPen(_pen(DARK, s, 0.035))
    p.setBrush(color)
    p.drawEllipse(QRectF(0.22 * s, 0.22 * s, 0.56 * s, 0.56 * s))


# -- drawers ------------------------------------------------------------
def _draw_new(p: QPainter, s: int):
    p.setPen(_pen(DARK, s, 0.045))
    p.setBrush(WHITE)
    path = QPainterPath()
    path.moveTo(0.22 * s, 0.10 * s)
    path.lineTo(0.62 * s, 0.10 * s)
    path.lineTo(0.78 * s, 0.27 * s)
    path.lineTo(0.78 * s, 0.90 * s)
    path.lineTo(0.22 * s, 0.90 * s)
    path.closeSubpath()
    p.drawPath(path)
    p.setPen(_pen(QColor("#888888"), s, 0.035))
    p.drawLine(QPointF(0.32 * s, 0.50 * s), QPointF(0.68 * s, 0.50 * s))
    p.drawLine(QPointF(0.32 * s, 0.64 * s), QPointF(0.68 * s, 0.64 * s))
    p.drawLine(QPointF(0.32 * s, 0.78 * s), QPointF(0.58 * s, 0.78 * s))


def _draw_open(p: QPainter, s: int):
    p.setPen(_pen(DARK, s, 0.045))
    p.setBrush(QColor("#e8a33d"))
    path = QPainterPath()
    path.moveTo(0.10 * s, 0.28 * s)
    path.lineTo(0.42 * s, 0.28 * s)
    path.lineTo(0.50 * s, 0.38 * s)
    path.lineTo(0.88 * s, 0.38 * s)
    path.lineTo(0.88 * s, 0.78 * s)
    path.lineTo(0.10 * s, 0.78 * s)
    path.closeSubpath()
    p.drawPath(path)
    p.setBrush(QColor("#ffc45e"))
    p.drawPolygon(
        _polygon([(0.10, 0.44), (0.92, 0.44), (0.80, 0.84), (0.10, 0.84)], s)
    )


def _draw_save(p: QPainter, s: int):
    p.setPen(_pen(DARK, s, 0.045))
    p.setBrush(BLUE)
    p.drawRoundedRect(QRectF(0.16 * s, 0.14 * s, 0.68 * s, 0.72 * s), 0.05 * s, 0.05 * s)
    p.setBrush(WHITE)
    p.drawRect(QRectF(0.32 * s, 0.16 * s, 0.36 * s, 0.24 * s))
    p.setBrush(QColor("#d8e6fb"))
    p.drawRect(QRectF(0.28 * s, 0.58 * s, 0.44 * s, 0.28 * s))


def _draw_move_vertical(p: QPainter, s: int):
    _arrow_up(p, s, 0.50, 0.10, 0.52, 0.17, QColor("#111111"))
    _arrow_down(p, s, 0.50, 0.48, 0.90, 0.17, WHITE)


def _draw_add(p: QPainter, s: int):
    p.setPen(_pen(GREEN, s, 0.09))
    p.drawLine(QPointF(0.50 * s, 0.18 * s), QPointF(0.50 * s, 0.82 * s))
    p.drawLine(QPointF(0.18 * s, 0.50 * s), QPointF(0.82 * s, 0.50 * s))


def _draw_remove(p: QPainter, s: int):
    p.setPen(_pen(RED, s, 0.09))
    p.drawLine(QPointF(0.18 * s, 0.50 * s), QPointF(0.82 * s, 0.50 * s))


def _draw_stop(p: QPainter, s: int):
    p.setPen(_pen(DARK, s, 0.04))
    p.setBrush(RED)
    p.drawRect(QRectF(0.26 * s, 0.26 * s, 0.48 * s, 0.48 * s))


def _draw_circle_red(p: QPainter, s: int):
    _circle(p, s, RED)


def _draw_circle_yellow(p: QPainter, s: int):
    _circle(p, s, YELLOW)


def _draw_circle_blue(p: QPainter, s: int):
    _circle(p, s, BLUE)


def _draw_razor(p: QPainter, s: int):
    # A razor blade with a red handle, readable at 16 px.
    p.setPen(_pen(DARK, s, 0.045))
    p.setBrush(QColor("#d9d9d9"))
    p.drawPolygon(_polygon([(0.30, 0.14), (0.78, 0.14), (0.86, 0.52), (0.38, 0.52)], s))
    p.setBrush(RED)
    p.drawRoundedRect(QRectF(0.40 * s, 0.56 * s, 0.20 * s, 0.30 * s), 0.04 * s, 0.04 * s)


def _draw_drop(p: QPainter, s: int):
    p.setPen(_pen(DARK, s, 0.035))
    p.setBrush(GREEN)
    p.drawPolygon(
        _polygon([(0.50, 0.12), (0.78, 0.44), (0.60, 0.44), (0.60, 0.66), (0.40, 0.66), (0.40, 0.44), (0.22, 0.44)], s)
    )
    p.setPen(_pen(GREEN, s, 0.07))
    p.drawLine(QPointF(0.20 * s, 0.80 * s), QPointF(0.80 * s, 0.80 * s))


def _draw_arrow_left(p: QPainter, s: int):
    p.setPen(_pen(DARK, s, 0.035))
    p.setBrush(PURPLE)
    p.drawPolygon(_polygon([(0.14, 0.50), (0.48, 0.20), (0.48, 0.38), (0.88, 0.38), (0.88, 0.62), (0.48, 0.62), (0.48, 0.80)], s))


def _draw_arrow_right(p: QPainter, s: int):
    p.setPen(_pen(DARK, s, 0.035))
    p.setBrush(QColor("#2fa8c9"))
    p.drawPolygon(_polygon([(0.86, 0.50), (0.52, 0.20), (0.52, 0.38), (0.12, 0.38), (0.12, 0.62), (0.52, 0.62), (0.52, 0.80)], s))


def _draw_close(p: QPainter, s: int):
    p.setPen(_pen(QColor("#111111"), s, 0.08))
    p.drawLine(QPointF(0.24 * s, 0.24 * s), QPointF(0.76 * s, 0.76 * s))
    p.drawLine(QPointF(0.76 * s, 0.24 * s), QPointF(0.24 * s, 0.76 * s))


def _draw_select(p: QPainter, s: int):
    p.setPen(_pen(DARK, s, 0.04))
    p.setBrush(WHITE)
    p.drawPolygon(_polygon([(0.30, 0.14), (0.30, 0.78), (0.44, 0.64), (0.55, 0.88), (0.66, 0.82), (0.55, 0.59), (0.74, 0.56)], s))


def _draw_spacer(p: QPainter, s: int):
    p.setPen(_pen(DARK, s, 0.03))
    p.setBrush(WHITE)
    p.drawPolygon(_polygon([(0.16, 0.50), (0.40, 0.28), (0.40, 0.72)], s))
    p.drawPolygon(_polygon([(0.84, 0.50), (0.60, 0.28), (0.60, 0.72)], s))
    p.setPen(_pen(DARK, s, 0.03))
    p.drawLine(QPointF(0.50 * s, 0.22 * s), QPointF(0.50 * s, 0.78 * s))


def _draw_eye(p: QPainter, s: int):
    p.setPen(_pen(DARK, s, 0.04))
    p.setBrush(WHITE)
    path = QPainterPath()
    path.moveTo(0.12 * s, 0.50 * s)
    path.quadTo(0.50 * s, 0.16 * s, 0.88 * s, 0.50 * s)
    path.quadTo(0.50 * s, 0.84 * s, 0.12 * s, 0.50 * s)
    p.drawPath(path)
    p.setBrush(DARK)
    p.drawEllipse(QRectF(0.42 * s, 0.42 * s, 0.16 * s, 0.16 * s))


def _draw_lock(p: QPainter, s: int):
    p.setPen(_pen(DARK, s, 0.04))
    p.setBrush(QColor("#bfbfbf"))
    p.drawRoundedRect(QRectF(0.26 * s, 0.46 * s, 0.48 * s, 0.38 * s), 0.05 * s, 0.05 * s)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawArc(QRectF(0.34 * s, 0.18 * s, 0.32 * s, 0.42 * s), 0, 180 * 16)
    p.setBrush(DARK)
    p.drawEllipse(QRectF(0.46 * s, 0.60 * s, 0.08 * s, 0.10 * s))


def _draw_speaker(p: QPainter, s: int):
    p.setPen(_pen(DARK, s, 0.035))
    p.setBrush(DARK)
    p.drawPolygon(_polygon([(0.12, 0.40), (0.30, 0.40), (0.46, 0.24), (0.46, 0.76), (0.30, 0.60), (0.12, 0.60)], s))
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawArc(QRectF(0.38 * s, 0.30 * s, 0.34 * s, 0.40 * s), -60 * 16, 120 * 16)
    p.drawArc(QRectF(0.38 * s, 0.18 * s, 0.50 * s, 0.64 * s), -55 * 16, 110 * 16)


def _draw_rewind(p: QPainter, s: int):
    _triangle_left(p, s, 0.10, 0.22, 0.48, 0.78, QColor("#111111"))
    _triangle_left(p, s, 0.48, 0.22, 0.86, 0.78, QColor("#111111"))


def _draw_forward(p: QPainter, s: int):
    _triangle_right(p, s, 0.14, 0.22, 0.52, 0.78, QColor("#111111"))
    _triangle_right(p, s, 0.52, 0.22, 0.90, 0.78, QColor("#111111"))


def _draw_play(p: QPainter, s: int):
    _triangle_right(p, s, 0.28, 0.16, 0.82, 0.84, GREEN)


def _draw_film(p: QPainter, s: int):
    rect = QRectF(0.04 * s, 0.20 * s, 0.92 * s, 0.60 * s)
    p.setPen(_pen(DARK, s, 0.03))
    p.setBrush(QColor("#f2f2f2"))
    p.drawRect(rect)
    inner = rect.adjusted(0.10 * s, 0.10 * s, -0.10 * s, -0.10 * s)
    p.setBrush(QColor("#d0d0d0"))
    p.drawRect(inner)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(DARK)
    holes = 7
    usable = rect.width() - 0.06 * s
    for index in range(holes):
        x = rect.left() + 0.03 * s + index * usable / holes
        width = usable / holes * 0.5
        p.drawRect(QRectF(x, rect.top() + 0.02 * s, width, 0.045 * s))
        p.drawRect(QRectF(x, rect.bottom() - 0.065 * s, width, 0.045 * s))
    if s >= 80:
        font = QFont()
        font.setPixelSize(int(0.10 * s))
        p.setFont(font)
        p.setPen(QColor("#666666"))
        p.drawText(inner, Qt.AlignmentFlag.AlignCenter, "foto")


def _draw_folder_small(p: QPainter, s: int):
    _draw_open(p, s)


_DRAWERS: dict[str, Callable[[QPainter, int], None]] = {
    "new": _draw_new,
    "open": _draw_open,
    "save": _draw_save,
    "move_vertical": _draw_move_vertical,
    "add": _draw_add,
    "remove": _draw_remove,
    "stop": _draw_stop,
    "circle_red": _draw_circle_red,
    "circle_yellow": _draw_circle_yellow,
    "circle_blue": _draw_circle_blue,
    "razor": _draw_razor,
    "drop": _draw_drop,
    "arrow_left": _draw_arrow_left,
    "arrow_right": _draw_arrow_right,
    "close": _draw_close,
    "select": _draw_select,
    "spacer": _draw_spacer,
    "eye": _draw_eye,
    "lock": _draw_lock,
    "speaker": _draw_speaker,
    "rewind": _draw_rewind,
    "forward": _draw_forward,
    "play": _draw_play,
    "film": _draw_film,
    "folder": _draw_folder_small,
}
