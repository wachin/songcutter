# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Washington
"""Shared look and feel.

A light Fusion palette plus a small stylesheet gets close to the design without
custom skinning. Native widgets are used everywhere.
"""

from __future__ import annotations

from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication

STYLESHEET = """
QMainWindow, QDialog { background: #efefef; }
QWidget#panelFrame {
    background: #ffffff;
    border: 1px solid #a8a8a8;
}
QWidget#panelTitleBar {
    background: #f0f0f0;
    border-bottom: 1px solid #a8a8a8;
}
QLabel#panelTitle {
    font-weight: bold;
    font-size: 9pt;
}
QLabel#timecode {
    font-family: "DejaVu Sans Mono", "Consolas", monospace;
    font-weight: bold;
    font-size: 10pt;
}
QLabel#timecodeBox {
    font-family: "DejaVu Sans Mono", "Consolas", monospace;
    font-weight: bold;
    font-size: 9pt;
    background: #ffffff;
    border: 1px solid #666666;
    padding-left: 4px;
}
QWidget#trackHeader {
    background: #e6e6e6;
    border: 1px solid #9a9a9a;
}
QLabel#trackTitle {
    font-weight: bold;
    font-size: 8pt;
}
QFrame#videoArea {
    background: #ffffff;
    border: 2px solid #1e6fd9;
}
QLabel#videoPlaceholder {
    color: #111111;
    font-weight: bold;
    font-size: 10pt;
}
QPushButton#processButton {
    background: #2e9e44;
    color: #ffffff;
    font-weight: bold;
    border: 1px solid #1f7030;
    border-radius: 3px;
    padding: 4px 12px;
}
QPushButton#processButton:hover { background: #37b350; }
QPushButton#processButton:pressed { background: #247c36; }
QTabBar::tab {
    background: #e8e8e8;
    border: 1px solid #b0b0b0;
    padding: 4px 10px;
    min-width: 80px;
}
QTabBar::tab:selected {
    background: #ffffff;
    border-bottom-color: #ffffff;
}
QScrollBar#timelineScroll:horizontal {
    background: #f2f2f2;
    height: 14px;
    border: 1px solid #b8b8b8;
}
QScrollBar#timelineScroll::handle:horizontal {
    background: #00c8c8;
    min-width: 30px;
}
QScrollBar#timelineScroll::add-line:horizontal,
QScrollBar#timelineScroll::sub-line:horizontal {
    width: 0px;
}
QToolButton#cornerButton {
    background: #ffffff;
    border: 1px solid #555555;
}
QTreeWidget#effectsTree {
    background: #ffffff;
    border: 1px solid #b8b8b8;
}
QListWidget#fileBin {
    background: #ffffff;
    border: 1px solid #b8b8b8;
}
"""


def apply_theme(app: QApplication) -> None:
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#efefef"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#f6f6f6"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#efefef"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#111111"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#111111"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#111111"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#3a7bd5"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    app.setPalette(palette)
    app.setStyleSheet(STYLESHEET)
