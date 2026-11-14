# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Washington
"""Main window: title, menus, toolbar, top panels, timeline and status bar."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QByteArray, QEvent, QSize, Qt, QTimer
from PyQt6.QtGui import QActionGroup, QCloseEvent
from PyQt6.QtWidgets import (
    QComboBox,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from songcutter import __version__
from songcutter.config.paths import config_dir, log_dir
from songcutter.config.settings import Settings
from songcutter.core.demo import demo_project
from songcutter.i18n.qt_translations import qt_translation_status
from songcutter.ui.actions import ActionManager, install_action_icons
from songcutter.ui.icons import icon
from songcutter.ui.preview_panel import PreviewPanel
from songcutter.ui.shortcuts_dialog import ShortcutsDialog
from songcutter.ui.timeline import TimelinePanel
from songcutter.ui.workspace import WorkspacePanel

DEFAULT_WINDOW_SIZE = QSize(1360, 768)
MAIN_SPLIT_RATIO = 0.42
TOP_SPLIT_RATIO = 0.45


class MainWindow(QMainWindow):
    def __init__(
        self,
        settings: Settings | None = None,
        shortcuts_file: Path | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self._settings = settings or Settings()
        self._project = demo_project()
        self._actions = ActionManager(self, store_path=shortcuts_file)
        install_action_icons(self._actions)
        self._state_text = self.tr("Ready")
        self._status_timer = QTimer(self)
        self._status_timer.setSingleShot(True)
        self._status_timer.timeout.connect(self._reset_state_text)
        self._sizes_applied = False

        self.setWindowTitle(
            self.tr("%1 [%2] - SongCutter")
            .replace("%1", self._project.name)
            .replace("%2", self._project.profile_name)
        )
        self.setWindowIcon(icon("film", 32))
        self.setMinimumSize(1280, 720)
        self.resize(DEFAULT_WINDOW_SIZE)

        self._build_central()
        self._build_menus()
        self._build_toolbar()
        self._build_status_bar()
        self._setup_tool_group()
        # Actions must belong to the window for their shortcuts to be active,
        # even when they are only reachable from the timeline toolbar.
        for action in self._actions.actions():
            self.addAction(action)
        self._connect_actions()
        # The primary call to action is visible in the toolbar, so its shortcut
        # should at least explain itself until Phase 7 implements export.
        process_action = self._actions.action("file.process")
        process_action.setEnabled(True)
        process_action.triggered.connect(self._process_videos)
        self._restore_window_state()
        self._update_status()

    # -- construction ----------------------------------------------------
    def _build_central(self) -> None:
        central = QWidget(self)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(4, 4, 4, 2)
        layout.setSpacing(4)

        self.main_splitter = QSplitter(Qt.Orientation.Vertical, central)
        self.main_splitter.setChildrenCollapsible(False)
        self.main_splitter.setHandleWidth(5)

        self.top_splitter = QSplitter(Qt.Orientation.Horizontal, self.main_splitter)
        self.top_splitter.setChildrenCollapsible(False)
        self.top_splitter.setHandleWidth(5)

        self.workspace = WorkspacePanel(self._project, self._settings, self.top_splitter)
        self.workspace.setMinimumWidth(500)
        self.preview = PreviewPanel(self._project.fps, self.top_splitter)
        self.preview.setMinimumWidth(700)

        self.top_splitter.addWidget(self.workspace)
        self.top_splitter.addWidget(self.preview)
        self.top_splitter.setStretchFactor(0, 1)
        self.top_splitter.setStretchFactor(1, 1)

        self.timeline = TimelinePanel(
            self._project, self._actions, self._settings, self.main_splitter
        )
        self.main_splitter.addWidget(self.top_splitter)
        self.main_splitter.addWidget(self.timeline)
        self.main_splitter.setStretchFactor(0, 1)
        self.main_splitter.setStretchFactor(1, 1)

        layout.addWidget(self.main_splitter)
        self.setCentralWidget(central)

        self.workspace.message.connect(self.flash_status)
        self.preview.message.connect(self.flash_status)
        self.timeline.message.connect(self.flash_status)
        self.timeline.playhead_changed.connect(self._playhead_changed)

    def _build_menus(self) -> None:
        menu = self.menuBar()
        actions = self._actions

        file_menu = menu.addMenu(self.tr("&File"))
        for action_id in ("file.new", "file.open", "file.save", "file.save_as"):
            file_menu.addAction(actions.action(action_id))
        file_menu.addSeparator()
        file_menu.addAction(actions.action("file.process"))
        file_menu.addSeparator()
        file_menu.addAction(actions.action("file.quit"))

        edit_menu = menu.addMenu(self.tr("&Edit"))
        edit_menu.addAction(actions.action("edit.undo"))
        edit_menu.addAction(actions.action("edit.redo"))
        edit_menu.addSeparator()
        for action_id in (
            "edit.cut",
            "edit.cut_all",
            "edit.delete",
            "edit.extract",
            "edit.group",
            "edit.ungroup",
            "edit.select_all",
            "edit.copy",
            "edit.paste",
            "edit.duplicate",
        ):
            edit_menu.addAction(actions.action(action_id))

        title_menu = menu.addMenu(self.tr("&Title"))
        pending = title_menu.addAction(self.tr("Title tools (pending design decision)"))
        pending.setEnabled(False)

        view_menu = menu.addMenu(self.tr("&View"))
        view_menu.addAction(actions.action("view.toggle_menu"))
        view_menu.addAction(actions.action("view.fullscreen"))
        view_menu.addSeparator()
        view_menu.addAction(actions.action("view.zoom_in"))
        view_menu.addAction(actions.action("view.zoom_out"))
        view_menu.addSeparator()
        view_menu.addAction(actions.action("view.shortcuts"))

        help_menu = menu.addMenu(self.tr("&Help"))
        help_menu.addAction(actions.action("help.about"))
        help_menu.addAction(actions.action("help.about_qt"))

    def _build_toolbar(self) -> None:
        toolbar = QToolBar(self.tr("Main toolbar"), self)
        toolbar.setObjectName("mainToolBar")
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setIconSize(QSize(20, 20))
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)
        self.main_toolbar = toolbar

        for action_id in ("file.new", "file.open", "file.save"):
            toolbar.addAction(self._actions.action(action_id))

        # Icons from the design whose meaning is not confirmed. They are
        # disabled until the user describes them.
        unknown = (
            ("move_vertical", self.tr("Design icon: up/down arrows — meaning to confirm")),
            ("add", self.tr("Design icon: green plus — meaning to confirm")),
            ("stop", self.tr("Design icon: red stop — meaning to confirm")),
            ("circle_red", self.tr("Design icon: red circle — meaning to confirm")),
            ("circle_yellow", self.tr("Design icon: yellow circle — meaning to confirm")),
            ("circle_blue", self.tr("Design icon: blue circle — meaning to confirm")),
        )
        for icon_name, tooltip in unknown:
            button = QToolButton(toolbar)
            button.setIcon(icon(icon_name, 20))
            button.setIconSize(QSize(20, 20))
            button.setAutoRaise(True)
            button.setFixedSize(26, 26)
            button.setEnabled(False)
            button.setToolTip(tooltip)
            toolbar.addWidget(button)

        spacer = QWidget(toolbar)
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)

        profile_label = QLabel(self.tr("Profile:"), toolbar)
        toolbar.addWidget(profile_label)

        self.profile_combo = QComboBox(toolbar)
        self.profile_combo.addItem(self._project.profile_name)
        self.profile_combo.setMinimumWidth(170)
        self.profile_combo.setToolTip(self.tr("Project profile (selection arrives in Phase 2)"))
        toolbar.addWidget(self.profile_combo)

        self.process_button = QPushButton(toolbar)
        self.process_button.setObjectName("processButton")
        self.process_button.setText(self._process_button_text())
        self.process_button.setToolTip(self.tr("Export one video per song (Phase 7)"))
        self.process_button.clicked.connect(self._process_videos)
        toolbar.addWidget(self.process_button)

    def _build_status_bar(self) -> None:
        bar = self.statusBar()
        bar.setSizeGripEnabled(True)
        self.status_label = QLabel(bar)
        bar.addWidget(self.status_label, 1)

        self.wave_label = QLabel(self.tr("Waveform 72%"), bar)
        bar.addPermanentWidget(self.wave_label)
        self.wave_progress = QProgressBar(bar)
        self.wave_progress.setRange(0, 100)
        self.wave_progress.setValue(72)
        self.wave_progress.setTextVisible(False)
        self.wave_progress.setFixedSize(150, 12)
        self.wave_progress.setToolTip(self.tr("Background waveform progress (Phase 5)"))
        bar.addPermanentWidget(self.wave_progress)

    def _setup_tool_group(self) -> None:
        self._tool_group = QActionGroup(self)
        self._tool_group.setExclusive(True)
        for action_id in ("tool.selection", "tool.razor", "tool.spacer"):
            self._tool_group.addAction(self._actions.action(action_id))
        self._actions.action("tool.selection").setChecked(True)

    def _connect_actions(self) -> None:
        actions = self._actions
        actions.action("file.quit").triggered.connect(self.close)
        actions.action("view.toggle_menu").toggled.connect(self._set_menu_visible)
        actions.action("view.fullscreen").toggled.connect(self._set_fullscreen)
        actions.action("view.zoom_in").triggered.connect(self.timeline.zoom_in)
        actions.action("view.zoom_out").triggered.connect(self.timeline.zoom_out)
        actions.action("view.shortcuts").triggered.connect(self.show_shortcuts)
        actions.action("help.about").triggered.connect(self.show_about)
        actions.action("help.about_qt").triggered.connect(lambda: QMessageBox.aboutQt(self))
        actions.action("tool.escape").triggered.connect(
            actions.action("tool.selection").trigger
        )

    # -- state -----------------------------------------------------------
    def _restore_window_state(self) -> None:
        geometry = self._settings.window_geometry
        if geometry:
            data = QByteArray.fromBase64(geometry.encode("ascii"))
            if not data.isEmpty():
                self.restoreGeometry(data)
        state = self._settings.window_state
        if state:
            data = QByteArray.fromBase64(state.encode("ascii"))
            if not data.isEmpty():
                self.restoreState(data)

        visible = self._settings.menu_bar_visible
        self.menuBar().setVisible(visible)
        action = self._actions.action("view.toggle_menu")
        action.blockSignals(True)
        action.setChecked(visible)
        action.blockSignals(False)
        if self._settings.window_maximized:
            self.setWindowState(self.windowState() | Qt.WindowState.WindowMaximized)

    def showEvent(self, event) -> None:  # noqa: N802 (Qt naming)
        super().showEvent(event)
        if not self._sizes_applied:
            self._sizes_applied = True
            QTimer.singleShot(0, self._apply_splitter_sizes)

    def _apply_splitter_sizes(self) -> None:
        main_sizes = self._settings.splitter_sizes("main")
        if len(main_sizes) == 2 and all(size > 0 for size in main_sizes):
            self.main_splitter.setSizes(main_sizes)
        else:
            height = max(self.main_splitter.height(), 600)
            top = int(height * MAIN_SPLIT_RATIO)
            self.main_splitter.setSizes([top, max(1, height - top)])

        top_sizes = self._settings.splitter_sizes("top")
        if len(top_sizes) == 2 and all(size > 0 for size in top_sizes):
            self.top_splitter.setSizes(top_sizes)
        else:
            width = max(self.top_splitter.width(), 1000)
            left = int(width * TOP_SPLIT_RATIO)
            self.top_splitter.setSizes([left, max(1, width - left)])

        effects_sizes = self._settings.splitter_sizes("effects")
        if len(effects_sizes) == 2 and all(size > 0 for size in effects_sizes):
            self.workspace.effects_splitter.setSizes(effects_sizes)

    def _save_window_state(self) -> None:
        geometry = bytes(self.saveGeometry().toBase64()).decode("ascii")
        state = bytes(self.saveState().toBase64()).decode("ascii")
        self._settings.set_window(geometry, state, self.isMaximized())
        self._settings.set_splitter_sizes("main", self.main_splitter.sizes())
        self._settings.set_splitter_sizes("top", self.top_splitter.sizes())
        self._settings.set_splitter_sizes(
            "effects", self.workspace.effects_splitter.sizes()
        )
        self._settings.set_menu_bar_visible(self.menuBar().isVisible())
        self._settings.save()

    # -- slots -----------------------------------------------------------
    def _set_menu_visible(self, visible: bool) -> None:
        self.menuBar().setVisible(visible)
        self._settings.set_menu_bar_visible(visible)
        self._settings.save()

    def _set_fullscreen(self, enabled: bool) -> None:
        if enabled:
            self.showFullScreen()
        else:
            self.showNormal()

    def _playhead_changed(self, seconds: float) -> None:
        self.preview.set_timecode(seconds)
        duration = max(self._project.duration, 1.0)
        self.preview.seek.setValue(int(max(0.0, min(1.0, seconds / duration)) * 1000))

    def _process_videos(self) -> None:
        self.flash_status(self.tr("Video export arrives in Phase 7."))

    def _process_button_text(self) -> str:
        shortcut = self._actions.shortcut_display("file.process").replace("Return", "Enter")
        if shortcut:
            return self.tr("Process videos") + f"  ({shortcut})"
        return self.tr("Process videos")

    def show_shortcuts(self) -> None:
        dialog = ShortcutsDialog(self._actions, self)
        dialog.exec()

    def show_about(self) -> None:
        text = self.tr(
            "<b>SongCutter %1</b><br>"
            "Cut a multi-song recording into one video per song.<br><br>"
            "License: GPL-3.0-or-later<br>"
            "Configuration: %2<br>"
            "Logs: %3<br>"
            "Qt translations: %4"
        )
        language = None if self._settings.language == "system" else self._settings.language
        text = (
            text.replace("%1", __version__)
            .replace("%2", str(config_dir()))
            .replace("%3", str(log_dir()))
            .replace("%4", qt_translation_status(language))
        )
        QMessageBox.about(self, self.tr("About SongCutter"), text)

    def flash_status(self, message: str, timeout: int = 5000) -> None:
        self._state_text = message
        self._update_status()
        self._status_timer.start(timeout)

    def _reset_state_text(self) -> None:
        self._state_text = self.tr("Ready")
        self._update_status()

    def _update_status(self) -> None:
        clips = self._project.clip_count
        songs = self._project.enabled_song_count
        text = self.tr("%1  |  %2 clips  |  %3 songs detected  |  %4")
        text = (
            text.replace("%1", self._project.profile_name)
            .replace("%2", str(clips))
            .replace("%3", str(songs))
            .replace("%4", self._state_text)
        )
        self.status_label.setText(text)

    # -- events ----------------------------------------------------------
    def changeEvent(self, event) -> None:  # noqa: N802 (Qt naming)
        super().changeEvent(event)
        if event.type() == QEvent.Type.WindowStateChange:
            action = self._actions.action("view.fullscreen")
            action.blockSignals(True)
            action.setChecked(self.isFullScreen())
            action.blockSignals(False)

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802 (Qt naming)
        self._save_window_state()
        super().closeEvent(event)
