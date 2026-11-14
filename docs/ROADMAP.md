# Roadmap

One phase at a time. The app must run at the end of every phase. See
`docs/SPEC.md` for the full requirements.

Status legend: `[x]` done, `[ ]` pending, `[~]` partial/placeholder.

---

## Phase 0 — Bootstrap ✅ (2026-11-14)

- [x] Inspect repository, `LICENSE` and the three SVG designs; render them to PNG
- [x] Verify `external/kdenlive` is ignored by Git
- [x] `README.md`, `AGENTS.md`, `CLAUDE.md`, `NOTICE.md`
- [x] `docs/SPEC.md`, `GUI_MAP.md`, `ROADMAP.md`, `PROGRESS.md`, `DECISIONS.md`,
      `SHORTCUTS.md`, `TESTING.md`
- [x] `pyproject.toml`, requirements, `.gitignore`, `.editorconfig`
- [x] Source layout under `src/songcutter/`, `tests/`, `scripts/`
- [x] Empty main window starts with `python -m songcutter`
- [x] Virtual environment guide in the README
- [x] Passing test run

**Acceptance:** runs on Debian and the docs exist.

---

## Phase 1 — Shell and layout ✅ (2026-11-14)

- [x] Window title with project name and profile
- [x] Menu bar: File, Edit, Title (placeholder), View, Help; hide with Ctrl+M
- [x] Top toolbar: file icons, design placeholders, profile selector, green
      **Process videos** button
- [x] Project files panel: filter buttons, filter box, thumbnail bin, folder row
- [x] Preview panel: video area, seek bar, In/Out/Mark, transport, timecode,
      speed, volume, Save/Copy frame
- [x] Tab row: Projects, Transitions, Effects, Emojis, Songs
- [x] Effects tab split layout with effects tree and placeholder card area
- [x] Songs tab with detected songs
- [x] Timeline toolbar, ruler, current-time box, playhead, markers
- [x] Video and audio track headers and lanes; yellow/lavender clips; dB scale
- [x] Vertical and horizontal scroll bars, zoom controls (display-only)
- [x] Status bar with profile, clips, songs, state and waveform progress
- [x] Splitters with design proportions and persisted sizes
- [x] `settings.json` and `shortcuts.json` with atomic writes and schema version
- [x] Window geometry, maximized state and menu-bar visibility persisted
- [x] Central action manager with the full shortcut catalog
- [x] Shortcuts dialog with search, rebind, clear, reset, conflict detection
- [x] Logging to the state directory
- [x] `tr()` wrapping for every UI string
- [x] Qt's own translations installed at startup (section 9.4)
- [x] Unit tests for config, settings, actions, model, timeline, window
- [x] Questions about the design sent to the user (report)

**Acceptance:** looks like the design at 1360×768 and 1920×1080 without window
scrolling; panel sizes survive a restart. **Met** (see `TESTING.md`).

---

## Phase 2 — Files, import and profiles

- [ ] FFprobe wrapper: size, fps, scan, aspect, duration
- [ ] Natural file ordering (HDV_2, HDV_10)
- [ ] Thumbnail bin populated from a folder
- [ ] Folder, Browse..., Import folder, Add to timeline
- [ ] XDG user folders via `QStandardPaths` + `user-dirs.dirs` fallback
- [ ] Accented folder names in the file dialog sidebar (root cause + fix)
- [ ] FFmpeg/FFprobe detection and Settings page for tool paths
- [ ] Profile database derived from `external/kdenlive` (720p, 1080p, 2160p, SD
      at 24/25/30/50/60 fps)
- [ ] Profile selector and Project settings dialog
- [ ] Profile-change dialog with Keep/Change/Cancel and "do not ask again"
- [ ] Custom profile from a clip when nothing matches

**Acceptance:** HD 720p and FHD 1080p files are detected correctly; the message
shows the right profile and file name; localized folder names display correctly
in all dialogs.

---

## Phase 3 — Preview player

- [ ] Qt Multimedia playback of the selected source
- [ ] Seek bar, timecode, frame step, speed, volume
- [ ] In / Out / Mark
- [ ] Save frame and Copy frame extracted exactly with FFmpeg
- [ ] Clear message for unsupported codecs; proxy note in DECISIONS

**Acceptance:** the extracted frame matches the paused frame.

---

## Phase 4 — Timeline core

- [ ] Real project model and QUndoStack
- [ ] Playhead, current-time box, ruler, snap, zone, markers
- [ ] V1/A1 linked clips; add files in order as one sequence
- [ ] Zoom, scroll, pan
- [ ] Timeline playback across clip boundaries through the audio engine
- [ ] Track lock/hide/mute

**Acceptance:** several camcorder files play as one recording with sound.

---

## Phase 5 — Waveform

- [ ] Background peak extraction with FFmpeg and progress in the status bar
- [ ] Multi-resolution peak cache keyed by path/size/mtime/channel
- [ ] Visible-range drawing, one channel, half wave, dB scale
- [ ] Zoom buttons, slider, Fit, shortcuts, Ctrl+wheel
- [ ] Follow or centered playhead; resizable track heights
- [ ] Display options in Settings

**Acceptance:** smooth zoom from the whole recording to millisecond detail on a
1-hour file.

---

## Phase 6 — Editing tools

- [ ] Selection, Razor, Spacer with real behaviour
- [ ] Cut at playhead, cut all, trim to playhead
- [ ] Delete, extract, lift/extract zone
- [ ] Multi-select, group/ungroup, Join
- [ ] Copy, paste, duplicate
- [ ] Full undo/redo

**Acceptance:** the user can cut 6 songs out of one recording and remove what is
between them.

---

## Phase 7 — Songs, project files and export (MVP)

- [ ] `.songcutter` JSON save/open with schema version and relative paths
- [ ] Song detection (groups → gaps → markers) and Songs tab editing
- [ ] Process videos dialog (songs, folder, pattern, quality, options)
- [ ] FFmpeg command builder, Accurate and Fast modes
- [ ] Per-song and overall progress, cancel, summary, open folder
- [ ] Exactly N files for N checked songs

**Acceptance:** 4 cut songs produce exactly 4 correct videos, tested end to end.

---

## Phase 8 — Effects tab, volume gain and fades

- [ ] Effects tree and drag/double-click to add an effect
- [ ] Stack of collapsible cards with enable/remove
- [ ] Volume (gain): slider, number, quick buttons, peak analysis, max boost,
      Set to maximum, Limit to 0 dBFS, this clip / all clips
- [ ] Live waveform with original outline and red clipping
- [ ] Mute flag, fade handles and fade cards
- [ ] Audible preview through the audio engine; exact export

**Acceptance:** gain visibly raises the waveform, shows the maximum, and is
audible when Play is pressed.

---

## Phase 9 — Noise reduction

- [ ] Noise sample loading and last-sample memory
- [ ] noisereduce engine (default) with `prop_decrease`
- [ ] SoX engine with `noiseprof`/`noisered`, install hints if missing
- [ ] Strength, Apply on export, A/B preview around the playhead
- [ ] Chunked processing, profile cache, bounded memory
- [ ] No video re-encode for noise removal alone

**Acceptance:** hum is clearly reduced without damaging voices or music, and both
engines can be compared.

---

## Phase 10 — Hardening and cross-platform

- [ ] Windows and macOS test pass
- [ ] Long-recording performance (1–2 hours)
- [ ] Autosave and crash recovery
- [ ] Packaging notes (PyInstaller)
- [ ] Final shortcut review and conflict audit

---

## Phase 11 — Internationalization

- [ ] Language selector (System default, English, Spanish, …)
- [ ] `pylupdate6` extraction, `.ts` files, `lrelease`, ship `.qm`
- [ ] Spanish translation of the UI
- [ ] Qt translations from section 9.4 and the missing-files hint
- [ ] RTL/long-string layout check

---

## Backlog (do not build unless asked)

- Transitions tab
- Emojis tab
- Notch filter for the hum's exact frequency
- Insert and Overwrite edit modes
- Video thumbnails on the timeline track
- Proxy files for unsupported codecs
- Hardware encoding (VA-API/NVENC/VideoToolbox)
- Centered-playhead option in Settings
- Waveform normalization and vertical scale options in Settings
