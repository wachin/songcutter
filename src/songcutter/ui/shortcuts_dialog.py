# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Washington
"""Keyboard shortcut editor."""

from __future__ import annotations

from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtGui import QFont, QKeySequence
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from songcutter.ui.actions import CATALOG, CATEGORIES, ActionManager


class ShortcutEditDialog(QDialog):
    """Ask for one key sequence."""

    def __init__(self, manager: ActionManager, action_id: str, parent: QWidget | None = None):
        super().__init__(parent)
        self._manager = manager
        self._action_id = action_id
        spec = manager.spec(action_id)
        self.setWindowTitle(self.tr("Change Shortcut"))
        self.setModal(True)

        layout = QVBoxLayout(self)
        label = QLabel(self.tr("Shortcut for “%1”").replace("%1", spec.text), self)
        label.setWordWrap(True)
        layout.addWidget(label)

        self._edit = QLineEdit(self)
        self._edit.setReadOnly(True)
        self._edit.setPlaceholderText(self.tr("Press a key combination"))
        self._edit.setClearButtonEnabled(True)
        layout.addWidget(self._edit)
        self._edit.installEventFilter(self)

        hint = QLabel(
            self.tr("Click the box and press the new combination. Backspace clears it."),
            self,
        )
        hint.setStyleSheet("color: #666666;")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        current = manager.shortcut_display(action_id)
        self._sequence = current
        self._edit.setText(current)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    # A read-only line edit still receives key events; use an event filter so
    # any combination can be captured without triggering application actions.
    def eventFilter(self, watched, event):  # noqa: N802 (Qt naming)
        if watched is self._edit and event.type() == QEvent.Type.KeyPress:
            key = event.key()
            if key in (Qt.Key.Key_Backspace, Qt.Key.Key_Delete):
                self._sequence = ""
                self._edit.clear()
                return True
            if key == Qt.Key.Key_Escape:
                return False
            modifiers = event.modifiers()
            sequence = QKeySequence(modifiers.value | key)
            text = sequence.toString(QKeySequence.SequenceFormat.NativeText)
            if text and text not in {"Ctrl", "Shift", "Alt", "Meta"}:
                self._sequence = text
                self._edit.setText(text)
            return True
        return super().eventFilter(watched, event)

    def _accept(self) -> None:
        if not self._sequence:
            QMessageBox.warning(
                self, self.tr("Change Shortcut"), self.tr("Press a key combination first.")
            )
            return
        ok, error = self._manager.set_shortcuts(self._action_id, [self._sequence])
        if not ok:
            QMessageBox.warning(self, self.tr("Change Shortcut"), error)
            return
        self.accept()


class ShortcutsDialog(QDialog):
    """List every action and let the user rebind it."""

    def __init__(self, manager: ActionManager, parent: QWidget | None = None):
        super().__init__(parent)
        self._manager = manager
        self._snapshot = manager.overrides_snapshot()
        self.setWindowTitle(self.tr("Keyboard Shortcuts"))
        self.setModal(True)
        self.resize(680, 520)

        layout = QVBoxLayout(self)

        self._search = QLineEdit(self)
        self._search.setPlaceholderText(self.tr("Search actions..."))
        self._search.setClearButtonEnabled(True)
        self._search.textChanged.connect(self._apply_filter)
        layout.addWidget(self._search)

        self._tree = QTreeWidget(self)
        self._tree.setColumnCount(3)
        self._tree.setHeaderLabels(
            [self.tr("Action"), self.tr("Shortcut"), self.tr("Available in")]
        )
        self._tree.setRootIsDecorated(True)
        self._tree.setUniformRowHeights(True)
        self._tree.setAlternatingRowColors(True)
        self._tree.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        self._tree.itemSelectionChanged.connect(self._update_buttons)
        self._tree.itemDoubleClicked.connect(lambda *_: self._change())
        layout.addWidget(self._tree, 1)

        row = QHBoxLayout()
        self._change_button = QPushButton(self.tr("Change..."), self)
        self._clear_button = QPushButton(self.tr("Clear"), self)
        self._reset_button = QPushButton(self.tr("Reset"), self)
        self._reset_all_button = QPushButton(self.tr("Reset All"), self)
        self._change_button.clicked.connect(self._change)
        self._clear_button.clicked.connect(self._clear)
        self._reset_button.clicked.connect(self._reset)
        self._reset_all_button.clicked.connect(self._reset_all)
        row.addWidget(self._change_button)
        row.addWidget(self._clear_button)
        row.addWidget(self._reset_button)
        row.addWidget(self._reset_all_button)
        row.addStretch(1)
        layout.addLayout(row)

        note = QLabel(
            self.tr(
                "Actions marked with a later phase are listed now but only work once that "
                "phase is implemented."
            ),
            self,
        )
        note.setStyleSheet("color: #666666;")
        note.setWordWrap(True)
        layout.addWidget(note)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._populate()
        self._update_buttons()

    # -- construction ----------------------------------------------------
    def _populate(self) -> None:
        self._tree.clear()
        category_items: dict[str, QTreeWidgetItem] = {}
        for category in CATEGORIES:
            item = QTreeWidgetItem([category, "", ""])
            font = QFont(item.font(0))
            font.setBold(True)
            item.setFont(0, font)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            self._tree.addTopLevelItem(item)
            category_items[category] = item

        for spec in CATALOG:
            parent = category_items[spec.category]
            child = QTreeWidgetItem(parent, [spec.text, "", f"Phase {spec.phase}"])
            child.setData(0, Qt.ItemDataRole.UserRole, spec.id)
            if spec.phase > 1:
                child.setForeground(0, Qt.GlobalColor.darkGray)
        self._tree.expandAll()
        self._tree.resizeColumnToContents(0)
        self._tree.setColumnWidth(1, 150)
        self._tree.setColumnWidth(2, 90)
        self._refresh_shortcuts()

    def _refresh_shortcuts(self) -> None:
        for category_index in range(self._tree.topLevelItemCount()):
            category = self._tree.topLevelItem(category_index)
            for index in range(category.childCount()):
                child = category.child(index)
                action_id = child.data(0, Qt.ItemDataRole.UserRole)
                if action_id:
                    child.setText(1, self._manager.shortcut_display(action_id))

    # -- selection -------------------------------------------------------
    def _selected_id(self) -> str | None:
        items = self._tree.selectedItems()
        if not items:
            return None
        value = items[0].data(0, Qt.ItemDataRole.UserRole)
        return str(value) if value else None

    def _update_buttons(self) -> None:
        has_selection = self._selected_id() is not None
        for button in (self._change_button, self._clear_button, self._reset_button):
            button.setEnabled(has_selection)

    # -- actions ---------------------------------------------------------
    def _change(self) -> None:
        action_id = self._selected_id()
        if not action_id:
            return
        dialog = ShortcutEditDialog(self._manager, action_id, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._refresh_shortcuts()

    def _clear(self) -> None:
        action_id = self._selected_id()
        if not action_id:
            return
        ok, error = self._manager.set_shortcuts(action_id, [])
        if not ok:
            QMessageBox.warning(self, self.tr("Keyboard Shortcuts"), error)
        self._refresh_shortcuts()

    def _reset(self) -> None:
        action_id = self._selected_id()
        if not action_id:
            return
        self._manager.reset_shortcut(action_id)
        self._refresh_shortcuts()

    def _reset_all(self) -> None:
        answer = QMessageBox.question(
            self,
            self.tr("Reset All Shortcuts"),
            self.tr("Restore every shortcut to its default value?"),
        )
        if answer == QMessageBox.StandardButton.Yes:
            self._manager.reset_all_shortcuts()
            self._refresh_shortcuts()

    # -- filtering -------------------------------------------------------
    def _apply_filter(self, text: str) -> None:
        needle = text.strip().lower()
        for category_index in range(self._tree.topLevelItemCount()):
            category = self._tree.topLevelItem(category_index)
            visible_children = 0
            for index in range(category.childCount()):
                child = category.child(index)
                haystack = f"{child.text(0)} {child.text(1)}".lower()
                matches = not needle or needle in haystack
                child.setHidden(not matches)
                visible_children += int(matches)
            category.setHidden(visible_children == 0)
            if needle and visible_children:
                category.setExpanded(True)

    # -- result ----------------------------------------------------------
    def accept(self) -> None:
        self._manager.save()
        super().accept()

    def reject(self) -> None:
        self._manager.restore_snapshot(self._snapshot)
        super().reject()
