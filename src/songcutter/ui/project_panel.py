# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Washington
"""Project files panel: filter row, thumbnail bin and folder row."""

from __future__ import annotations

from PyQt6.QtCore import QRect, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QIcon
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QStyle,
    QStyledItemDelegate,
    QToolButton,
    QWidget,
)

from songcutter.core.model import Project, format_clock
from songcutter.ui.icons import icon
from songcutter.ui.panel import PanelFrame

META_ROLE = Qt.ItemDataRole.UserRole + 1


class BinItemDelegate(QStyledItemDelegate):
    """Two-line bin item: filmstrip thumbnail, bold name, gray metadata."""

    def sizeHint(self, option, index) -> QSize:  # noqa: N802 (Qt naming)
        return QSize(172, 108)

    def paint(self, painter, option, index) -> None:  # noqa: N802 (Qt naming)
        painter.save()
        rect = option.rect.adjusted(2, 2, -2, -2)

        if option.state & QStyle.StateFlag.State_Selected:
            painter.fillRect(rect, QColor("#cfe3ff"))
        elif option.state & QStyle.StateFlag.State_MouseOver:
            painter.fillRect(rect, QColor("#f2f7ff"))

        icon_rect = QRect(rect.x() + 6, rect.y() + 4, rect.width() - 12, 64)
        decoration = index.data(Qt.ItemDataRole.DecorationRole)
        if isinstance(decoration, QIcon):
            decoration.paint(
                painter, icon_rect, Qt.AlignmentFlag.AlignCenter, QIcon.Mode.Normal
            )

        name = str(index.data(Qt.ItemDataRole.DisplayRole) or "")
        meta = str(index.data(META_ROLE) or "")

        name_font = QFont(option.font)
        name_font.setBold(True)
        name_font.setPointSizeF(max(7.5, name_font.pointSizeF() - 1.0))
        painter.setFont(name_font)
        painter.setPen(QColor("#111111"))
        metrics = QFontMetrics(name_font)
        elided = metrics.elidedText(name, Qt.TextElideMode.ElideRight, rect.width() - 12)
        painter.drawText(
            QRect(rect.x() + 6, rect.y() + 70, rect.width() - 12, 16),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            elided,
        )

        meta_font = QFont(option.font)
        meta_font.setPointSizeF(max(6.5, meta_font.pointSizeF() - 2.0))
        painter.setFont(meta_font)
        painter.setPen(QColor("#555555"))
        metrics = QFontMetrics(meta_font)
        meta_elided = metrics.elidedText(meta, Qt.TextElideMode.ElideRight, rect.width() - 12)
        painter.drawText(
            QRect(rect.x() + 6, rect.y() + 86, rect.width() - 12, 14),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            meta_elided,
        )
        painter.restore()


class ProjectFilesPanel(PanelFrame):
    """Top-left panel in its Projects state."""

    message = pyqtSignal(str)

    def __init__(self, project: Project, parent: QWidget | None = None):
        super().__init__(self.tr("Project files"), parent)
        self._project = project

        filters = QHBoxLayout()
        filters.setSpacing(3)
        self._filter_group = QButtonGroup(self)
        self._filter_group.setExclusive(True)
        for index, label in enumerate(
            (self.tr("Show all"), self.tr("Video"), self.tr("Audio"), self.tr("Image"))
        ):
            button = QToolButton(self)
            button.setText(label)
            button.setCheckable(True)
            button.setChecked(index == 0)
            self._filter_group.addButton(button, index)
            filters.addWidget(button)
        self.filter_edit = QLineEdit(self)
        self.filter_edit.setPlaceholderText(self.tr("Filter"))
        filters.addWidget(self.filter_edit, 1)
        self.add_layout(filters)

        self.bin = QListWidget(self)
        self.bin.setObjectName("fileBin")
        self.bin.setViewMode(QListWidget.ViewMode.IconMode)
        self.bin.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.bin.setMovement(QListWidget.Movement.Static)
        self.bin.setUniformItemSizes(True)
        self.bin.setGridSize(QSize(176, 112))
        self.bin.setSpacing(2)
        self.bin.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.bin.setItemDelegate(BinItemDelegate(self.bin))
        self.bin.setFrameShape(QListWidget.Shape.NoFrame)
        self.add_widget(self.bin, 1)
        self._populate_bin()

        folder_row = QHBoxLayout()
        folder_row.setSpacing(4)
        folder_row.addWidget(QLabel(self.tr("Folder:"), self))
        self.folder_edit = QLineEdit(project.source_dir, self)
        self.folder_edit.setReadOnly(True)
        folder_row.addWidget(self.folder_edit, 1)
        for text in (self.tr("Browse..."), self.tr("Import folder"), self.tr("Add to timeline")):
            button = QToolButton(self)
            button.setText(text)
            button.clicked.connect(self._not_available)
            folder_row.addWidget(button)
        self.add_layout(folder_row)

    def _populate_bin(self) -> None:
        track = self._project.track("video")
        for clip in (track.clips if track else []):
            item = QListWidgetItem()
            item.setIcon(icon("film", 130))
            item.setText(clip.name)
            meta = (
                f"{format_clock(clip.duration)} | "
                f"{self._project.width}x{self._project.height} "
                f"{self._project.fps:.0f} fps"
            )
            item.setData(META_ROLE, meta)
            item.setToolTip(f"{clip.name}\n{meta}")
            self.bin.addItem(item)

    def _not_available(self) -> None:
        self.message.emit(self.tr("File import will be available in Phase 2."))
