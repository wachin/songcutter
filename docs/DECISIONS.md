# Technical decisions

Short records of choices that are not obvious from the code. Newest last.

---

## D-001 — License identifier: `GPL-3.0-or-later`

**Date:** 2026-11-14
**Context:** `LICENSE` contains GPL version 3.
**Decision:** every source file starts with
`# SPDX-License-Identifier: GPL-3.0-or-later` and
`# Copyright (C) 2026 Washington`. The README and `NOTICE.md` state the same.
**Consequences:** the project can be combined with GPL-3 code (including
Kdenlive-derived data) and later versions of the GPL. Attribution headers stay.

---

## D-002 — PyQt6, Fusion style and runtime-drawn icons

**Date:** 2026-11-14
**Context:** the designs use a light, flat look with simple colored icons; no
icon files were supplied.
**Decision:** use PyQt6 with the Fusion style, a light `QPalette` and a small
stylesheet (`ui/theme.py`). Icons are painted with QPainter in `ui/icons.py`
and cached. No third-party icon set is bundled.
**Consequences:** the app looks consistent on Linux, Windows and macOS and has
no binary assets to license. Disabled placeholder icons keep their normal
pixmap so the toolbar still resembles the design.

---

## D-003 — Two config files, atomic writes, corrupt-file quarantine

**Date:** 2026-11-14
**Context:** the specification requires exactly two configuration files and
recovery from corruption.
**Decision:** `settings.json` and `shortcuts.json` live in
`platformdirs.user_config_dir("SongCutter")`. `config/json_store.py` writes with
a temporary file in the same directory, `fsync` and `os.replace`. A corrupt
file is renamed to `<name>.corrupt-<timestamp>` and defaults are used. Both
files carry `"schema_version": 1`. Unknown keys are preserved by merging over
defaults; unknown versions are merged and rewritten as version 1.
**Consequences:** no partial writes; the user's broken file is kept for
inspection. Caches and logs live outside the config directory.

---

## D-004 — Action manager owns the complete shortcut catalog from Phase 1

**Date:** 2026-11-14
**Context:** shortcuts must be rebindable and stable across phases.
**Decision:** `ui/actions.py` contains every action from section 6 of the spec
with a stable id, English label, category, default sequence(s) and the phase
that implements it. Actions for later phases are created but disabled; the
Shortcuts dialog still lists them and marks their phase. Exception: **Process
videos** is enabled in Phase 1 so its toolbar button and Ctrl+Enter can explain
that export arrives in Phase 7. Overrides are stored as
`{"overrides": {action_id: ["Ctrl+…"]}}`; only overrides are persisted. A
conflict with another action is rejected with the other action's name. A cleared
shortcut is stored as an empty list (distinct from "no override").
**Consequences:** the shortcut table in `docs/SHORTCUTS.md` can be generated
from the catalog and stays honest about what works.

---

## D-005 — Phase 1 shell paints a read-only sample project

**Date:** 2026-11-14
**Context:** Phase 1 needs placeholder content that looks like the design, but
file import is Phase 2 and the real project model is Phase 4/7.
**Decision:** `core/model.py` defines the final shape (Project, Track, Clip,
Marker, Song) and `core/demo.py` builds three 17:04 clips, three markers and
three songs. The timeline, bin, songs list and status bar read from that model;
nothing in the UI edits it. `core/commands.py` is a documented placeholder for
Phase 4.
**Consequences:** the shell is model-driven from day one; Phase 2 replaces the
demo bin data and Phase 4 adds commands without restructuring the UI.

---

## D-006 — Audio playback through QAudioSink with a software mixer

**Date:** 2026-11-14 (planned; implemented in Phase 4/8)
**Context:** Qt's `QAudioOutput.volume` is limited to 1.0 and cannot reproduce a
+6 dB gain.
**Decision:** decode each source to PCM with FFmpeg (disk cache), then play
through `QAudioSink` with our own mixer that applies gain, fades, mute and the
optional noise-reduced buffer. The video widget is kept silent; video follows
the audio clock.
**Consequences:** gain above 0 dB is audible in preview and matches export.
Phase 1 only displays a placeholder waveform, so no audio code exists yet.

---

## D-007 — Timeline audio lane stretches to fill the block

**Date:** 2026-11-14
**Context:** the spec fixes the top row at about 42% and the timeline at 58%,
while the design's two tracks at fixed heights would leave empty space at the
bottom of the timeline at 1360×768.
**Decision:** the video lane keeps its design height (62 px); the audio lane and
its header stretch to fill the remaining height. Track content stays top-aligned
in the header.
**Consequences:** no dead gray area, a larger waveform to work with, and the
design's structure is preserved. Phase 5 will add user-resizable track heights.

---

## D-008 — Zoom is display-only in Phase 1

**Date:** 2026-11-14
**Context:** the zoom controls and Ctrl+=/Ctrl+- are Must items but real
multi-resolution waveform zoom is Phase 5.
**Decision:** the slider, buttons, Fit and Ctrl+wheel change the timeline's
pixels-per-second and scroll offset; the waveform is the synthetic placeholder.
Zoom centers on the playhead (buttons) or the mouse (Ctrl+wheel). When the
window is resized while the whole project is visible, the view re-fits itself.
**Consequences:** the shell feels alive without pretending to have peak data.
Phase 5 replaces the peaks and the fit heuristic.

---

## D-009 — Effects tab is a static split layout in Phase 1

**Date:** 2026-11-14
**Context:** the design shows effect cards, but effects are Phase 8/9.
**Decision:** the Effects tab contains the search box, the effects tree and the
split panel; the right side says "Select an audio clip to edit its effects."
No fake gain controls are shown.
**Consequences:** the layout can be evaluated now; the card stack and drag/drop
arrive with the real feature.

---

## D-010 — F11 toggles the whole window for now

**Date:** 2026-11-14
**Context:** the spec asks for "Fullscreen preview" (Should).
**Decision:** in Phase 1 F11 toggles the main window fullscreen. Phase 3, when
the preview has a real video surface, restricts it to the preview panel.
**Consequences:** the action and its shortcut exist and can be tested now.

---

## D-011 — Qt's own translations at startup, application strings later

**Date:** 2026-11-14
**Context:** standard dialogs should follow the user's language, but the app is
developed in English first.
**Decision:** `i18n/qt_translations.py` searches `QLibraryInfo`'s translations
path, the PyQt6 wheel and `/usr/share/qt6/translations`, then installs
`qtbase_<lang>`, `qt_<lang>` and `qtmultimedia_<lang>` with `QTranslator`.
`Settings.language` is `"system"` by default. The About dialog reports whether
Qt translations were found. SongCutter's own strings use `tr()` and are
translated in Phase 11.
**Consequences:** Spanish Qt dialogs work as soon as
`qt6-translations-l10n` is installed; no app translation files exist yet.

---

## D-012 — Unknown design elements stay disabled and are asked about

**Date:** 2026-11-14
**Context:** six toolbar icons, the fourth transport icon and the "Title" menu
have no clear meaning in the designs.
**Decision:** draw the shapes faithfully, leave the toolbar buttons disabled
with a tooltip saying the meaning is to be confirmed, keep the fourth transport
button as the duplicate rewind from the design, and put a single disabled item
in the Title menu. Ask the user in the first report.
**Consequences:** nothing is invented. The layout is complete and the user can
name the actions before Phase 3/6.

---

## D-013 — Preview and window minimum sizes

**Date:** 2026-11-14
**Context:** the preview control row needs about 700 px; below that, labels and
buttons clip.
**Decision:** the main window minimum is 1280×720, the preview minimum width is
700 px, and both splitters use equal stretch factors so resizing the window
keeps the 45/55 and 42/58 proportions instead of crushing the preview.
**Consequences:** no clipped controls at the supported sizes; the primary
1360×768 target has room to spare.

---

## D-014 — Synthetic waveform in Phase 1

**Date:** 2026-11-14
**Context:** the design shows a waveform, but peak extraction is Phase 5.
**Decision:** `TimelineView` generates a deterministic 4000-sample peak array
per clip and channel (seeded by the clip id), with a smooth noise floor and a
slow envelope. It is cached in memory and drawn only for the visible range.
**Consequences:** the visual result is stable across runs and cheap to paint;
Phase 5 swaps the source of peaks without touching the painter.

---

## D-015 — Tests run Qt with the offscreen platform

**Date:** 2026-11-14
**Context:** the test suite must run on a headless Debian machine and in CI.
**Decision:** `tests/conftest.py` sets `QT_QPA_PLATFORM=offscreen` and clears
`QT_QPA_PLATFORMTHEME` before importing PyQt6, and provides a session
`QApplication`. Widget tests show windows, process events and use `grab()` to
verify painting.
**Consequences:** tests are deterministic and do not open windows. The offscreen
screen is 800×800, so tests that compare splitter pixels resize the window
explicitly.

---

## D-016 — Placeholder strings name the phase

**Date:** 2026-11-14
**Context:** clicking an unimplemented control must do something understandable
without pretending the feature works.
**Decision:** unimplemented but visible controls show a status-bar message such
as "Preview playback and frame capture arrive in Phase 3." Actions that would
imply data changes are disabled instead. The status text returns to "Ready"
after five seconds.
**Consequences:** the shell is honest and testable; these strings are temporary
and will be removed with each phase.
