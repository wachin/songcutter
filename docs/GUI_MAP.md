# GUI map — design regions to code

Source designs: `designs-ux_ui/songcutter-gui.svg` (main window),
`songcutter-gui-effects.svg` (Effects tab) and `songcutter-gui-dialogs.svg`
(three dialogs). Coordinates refer to the 1366×768 design canvas.

Status values: **Phase 1** = implemented in the shell; **visual** = present but
inert until its phase; **planned** = not built yet.

## Main window

| Design region (approx.) | Control | Widget / class | File | Status |
| --- | --- | --- | --- | --- |
| Title bar, y=0 | `Project [Profile] - SongCutter` | `QMainWindow.setWindowTitle` | `ui/main_window.py` | Phase 1 |
| Menu bar, y=27 | File, Edit, Title, View, Help | `QMenuBar` + `QAction` | `ui/main_window.py`, `ui/actions.py` | Phase 1 (Title is a placeholder) |
| File menu | New, Open, Save, Save As, Process videos, Quit | `ActionManager` actions | `ui/actions.py` | Quit active; others disabled until Phase 7 |
| Edit menu | Undo, Redo, Cut, Cut all, Delete, Extract, Group, Ungroup, Select all, Copy, Paste, Duplicate | `ActionManager` actions | `ui/actions.py` | Disabled until Phase 4/6 |
| View menu | Menu bar, Fullscreen, Zoom in/out, Keyboard shortcuts | `ActionManager` actions | `ui/actions.py` | Phase 1 |
| Help menu | About SongCutter, About Qt | `ActionManager` actions | `ui/actions.py` | Phase 1 |
| Toolbar, x=640–860 | New, Open, Save | `QToolBar` + `QAction` (drawn icons) | `ui/main_window.py`, `ui/icons.py` | Visual until Phase 7 |
| Toolbar, x=860–895 | Up/down arrows icon | Disabled `QToolButton` | `ui/main_window.py` | Placeholder — meaning to confirm |
| Toolbar, x=900–930 | Green plus | Disabled `QToolButton` | `ui/main_window.py` | Placeholder — meaning to confirm |
| Toolbar, x=935–965 | Red stop | Disabled `QToolButton` | `ui/main_window.py` | Placeholder — meaning to confirm |
| Toolbar, x=970–1010 | Red, yellow, blue circles | Disabled `QToolButton` ×3 | `ui/main_window.py` | Placeholder — meaning to confirm |
| Toolbar, right | `Profile:` + profile combo | `QLabel` + `QComboBox` | `ui/main_window.py` | Visual until Phase 2 |
| Toolbar, right | Process videos (Ctrl+Enter) | `QPushButton#processButton` | `ui/main_window.py` | Status message until Phase 7 |

### Project files panel (top left)

| Design region | Control | Widget / class | File | Status |
| --- | --- | --- | --- | --- |
| Panel frame, x=0–687, y=55–380 | Title, two corner squares | `PanelFrame` | `ui/panel.py` | Phase 1 |
| Filter row, y=90 | Show all / Video / Audio / Image | `QToolButton` + `QButtonGroup` | `ui/project_panel.py` | Visual until Phase 2 |
| Filter row, right | `Filter` box | `QLineEdit` | `ui/project_panel.py` | Visual until Phase 2 |
| Thumbnail bin, y=120–300 | File cards | `QListWidget#fileBin` + `BinItemDelegate` | `ui/project_panel.py` | Demo data; real in Phase 2 |
| Bin card | Filmstrip thumbnail, name, duration/size/fps | `BinItemDelegate.paint` | `ui/project_panel.py` | Phase 1 (demo values) |
| Folder row, y=350 | `Folder:` label, path | `QLabel` + `QLineEdit` | `ui/project_panel.py` | Read-only demo path |
| Folder row | Browse..., Import folder, Add to timeline | `QToolButton` ×3 | `ui/project_panel.py` | Status message until Phase 2 |
| Tab row, y=390–420 | Projects, Transitions, Effects, Emojis, Songs | `QTabBar` + `QStackedWidget` | `ui/workspace.py` | Phase 1 |
| Transitions page | `Not available yet` | `PlaceholderPanel` | `ui/panel.py` | Placeholder (Backlog) |
| Emojis page | `Not available yet` | `PlaceholderPanel` | `ui/panel.py` | Placeholder (Backlog) |

### Preview video panel (top right)

| Design region | Control | Widget / class | File | Status |
| --- | --- | --- | --- | --- |
| Panel frame, x=694–1350 | Title, corner squares | `PanelFrame` | `ui/panel.py` | Phase 1 |
| Video area, y=85–335 | Blue border and `Video` text | `QFrame#videoArea` + `QLabel#videoPlaceholder` | `ui/preview_panel.py` | Placeholder until Phase 3 |
| Seek bar, y=340 | Seek slider | `QSlider` | `ui/preview_panel.py` | Placeholder until Phase 3 |
| Control row, y=360 | In / Out / Mark | `QPushButton` ×3 | `ui/preview_panel.py` | Placeholder until Phase 3 |
| Control row | Rewind, Play, Forward, duplicate Rewind | `QToolButton` ×4 | `ui/preview_panel.py` | Placeholder until Phase 3; 4th icon to confirm |
| Control row | Timecode `00:00:00,00` | `QLabel#timecode` | `ui/preview_panel.py` | Updates with the playhead |
| Control row | Speed `1x` | `QComboBox` | `ui/preview_panel.py` | Placeholder until Phase 3 |
| Control row | Speaker icon + volume slider | `QLabel` + `QSlider` | `ui/preview_panel.py` | Placeholder until Phase 3 |
| Control row | Save frame, Copy frame | `QPushButton` ×2 | `ui/preview_panel.py` | Placeholder until Phase 3 |

### Effects tab (from `songcutter-gui-effects.svg`)

| Design region | Control | Widget / class | File | Status |
| --- | --- | --- | --- | --- |
| Panel frame | `Effects` title, corner squares | `EffectsPanel` (`PanelFrame`) | `ui/effects_panel.py` | Phase 1 |
| Left column, x=10–250 | Search effects box | `QLineEdit` | `ui/effects_panel.py` | Visual |
| Left column | Audio tree: Volume (gain), Fade in, Fade out, Camera noise reduction, Normalize, Mute | `QTreeWidget#effectsTree` | `ui/effects_panel.py` | Visual until Phase 8/9 |
| Left column | Video, Favorites categories | `QTreeWidgetItem` | `ui/effects_panel.py` | Visual |
| Left bottom | Drag hint | `QLabel` | `ui/effects_panel.py` | Phase 1 text |
| Right column | `Effects of: (no clip selected)` | `QLabel` | `ui/effects_panel.py` | Phase 1 |
| Right column | Effect card stack | Planned `EffectCard` widgets | `ui/effects_*.py` (Phase 8) | Planned |
| Right column, Phase 1 | Placeholder box | `QFrame` + `QLabel` | `ui/effects_panel.py` | Phase 1 |
| Split | Left/right splitter | `QSplitter` | `ui/effects_panel.py` | Phase 1, sizes persisted |

### Songs tab

| Design region | Control | Widget / class | File | Status |
| --- | --- | --- | --- | --- |
| Tab page | Song list with times | `QListWidget` | `ui/songs_panel.py` | Phase 1 (demo songs) |
| Tab page | Detection hint | `QLabel` | `ui/songs_panel.py` | Phase 1 |
| Song rows | Rename, enable/disable, click to jump | Planned | `ui/songs_panel.py` (Phase 7) | Planned |

### Timeline block (y=430–745)

| Design region | Control | Widget / class | File | Status |
| --- | --- | --- | --- | --- |
| Toolbar, y=435 | Add, remove, razor, drop, arrows, close | `QToolButton` + drawn icons | `ui/timeline.py` | Status message until Phase 6 |
| Toolbar | S / X / M tool toggles | `QToolButton` + `ActionManager` | `ui/timeline.py` | Phase 1 (toggle only) |
| Toolbar | Join, Group, Ungroup, Marker | `QToolButton` | `ui/timeline.py` | Status message until Phase 4/6 |
| Toolbar | Snap checkbox | `QCheckBox` | `ui/timeline.py` | Visual until Phase 4 |
| Toolbar | Zoom −, slider, +, Fit | `QToolButton`, `QSlider` | `ui/timeline.py` | Phase 1 (display zoom) |
| Toolbar, right | Horizontal scroll bar | `QScrollBar#timelineScroll` | `ui/timeline.py` | Phase 1 |
| Ruler left, x=0–96 | Current-time box | `QLabel#timecodeBox` | `ui/timeline.py` | Phase 1, updates with playhead |
| Ruler, x=96+ | Timecode labels and ticks | `TimelineView._paint_ruler` | `ui/timeline.py` | Phase 1 |
| Ruler | Green song flags | `TimelineView._paint_markers` | `ui/timeline.py` | Phase 1 |
| Ruler / lanes | Red playhead | `TimelineView._paint_playhead` | `ui/timeline.py` | Phase 1, click to move |
| Video header, x=0–96 | `Video ▾`, eye, lock | `VideoTrackHeader` | `ui/timeline.py` | Phase 1; buttons placeholder |
| Video lane | Yellow clips with filmstrip and name | `TimelineView._paint_video_clip` | `ui/timeline.py` | Phase 1 (demo) |
| Audio header | `Audio ▾`, Mute, Lock, Ch: Left/Right, Half wave | `AudioTrackHeader` | `ui/timeline.py` | Phase 1; channel/half wave active |
| Audio lane | Lavender clips, dark upper-half waveform | `TimelineView._paint_audio_lane`, `_paint_waveform` | `ui/timeline.py` | Phase 1 (synthetic peaks) |
| Audio lane | dB scale 0 / -6 / -12 dB | `TimelineView._paint_db_scale` | `ui/timeline.py` | Phase 1 |
| Right edge | Vertical scroll bar | `QScrollBar` | `ui/timeline.py` | Placeholder until Phase 5 |

### Status bar (y=746–768)

| Design region | Control | Widget / class | File | Status |
| --- | --- | --- | --- | --- |
| Left | Profile, clips, songs, state | `QLabel` updated by `_update_status` | `ui/main_window.py` | Phase 1 |
| Right | `Waveform 72%` + progress | `QLabel` + `QProgressBar` | `ui/main_window.py` | Static placeholder until Phase 5 |

### Dialogs and auxiliary windows

| Design | Window | Class | File | Status |
| --- | --- | --- | --- | --- |
| `songcutter-gui-dialogs.svg`, top | Change project profile | Planned `ChangeProfileDialog` | `ui/dialogs/profile_change.py` (Phase 2) | Planned |
| Middle | Project settings (profile list, frame size, rate, aspect, scanning, Add custom profile) | Planned `ProjectSettingsDialog` | `ui/dialogs/project_settings.py` (Phase 2) | Planned |
| Right | Process videos (songs table, output folder, pattern, format, quality, options, progress, summary) | Planned `ProcessVideosDialog` | `ui/dialogs/process_videos.py` (Phase 7) | Planned |
| — | Keyboard Shortcuts | `ShortcutsDialog`, `ShortcutEditDialog` | `ui/shortcuts_dialog.py` | Phase 1 |
| — | About SongCutter / About Qt | `QMessageBox` | `ui/main_window.py` | Phase 1 |

## Layout constants

| Item | Value | Source |
| --- | --- | --- |
| Design canvas | 1366×768 | SVGs |
| Primary window | 1360×768 | Spec |
| Window minimum | 1280×720 | D-013 |
| Main splitter | 42% top / 58% timeline | Spec 3.1 |
| Top splitter | 45% files / 55% preview | Spec 3.1 |
| Video lane | 62 px | Design |
| Audio lane | 170 px minimum, stretches to fill | D-007 |
| Header column | 96 px | Design |
| Ruler | 26 px | Design |
| Preview minimum width | 700 px | D-013 |

## Known deviations from the design

1. UI source strings are English; the design's Spanish labels
   (`Archivos del proyecto`) appear only after translation in Phase 11.
2. The effects cards, gain controls and fade curves are not drawn yet
   (Phase 8/9); the tab shows its structure and a placeholder.
3. The toolbar icons whose meaning is unknown are disabled placeholders.
4. The fourth transport icon is the design's duplicate rewind and is disabled
   until the user says what it should be.
5. The audio lane stretches to fill the timeline block instead of leaving empty
   space below the tracks (D-007).
6. The "Title" menu contains one disabled placeholder until the user decides
   what it is for.
7. The waveform and the `Waveform 72%` progress are placeholders (D-014).
