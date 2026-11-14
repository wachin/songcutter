# Progress log

Newest entry first. Each entry: date, phase, what was done, what is pending,
known issues, test status.

---

## 2026-11-14 — Phase 1: Shell and layout

**Done**

- Static main window from `songcutter-gui.svg`: title, menu bar, toolbar,
  project files panel, preview panel, five tabs, timeline block, status bar.
- Design proportions with draggable splitters (top 42%, timeline 58%, files 45%
  of the top row); sizes and window geometry persist in `settings.json`.
- Effects tab split layout (search, effects tree, placeholder card area) and
  Songs tab with the detected songs.
- Timeline: toolbar, current-time box, ruler, playhead, markers, video and
  audio headers, yellow/lavender clips, synthetic upper-half waveform, dB
  scale, horizontal scroll, display zoom, channel and half-wave options.
- `ActionManager` with the complete shortcut catalog (59 actions), conflict
  detection, clear/reset, atomic `shortcuts.json` overrides.
- Shortcuts dialog with search and rebinding; changes survive a restart.
- `settings.json` / `shortcuts.json` via platformdirs, atomic writes, schema
  version, corrupt-file quarantine.
- Logging to `~/.local/state/SongCutter/logs/songcutter.log`.
- Qt's own translations installed at startup; About dialog reports them.
- Every UI string wrapped with `tr()` / `translate()`.
- 74 unit tests: JSON store, settings, actions/shortcuts, model, timeline zoom
  and painting, main window and splitter persistence, Qt translations.
- Docs: `SPEC.md`, `GUI_MAP.md`, `ROADMAP.md`, `DECISIONS.md`, `SHORTCUTS.md`,
  `TESTING.md`, `PROGRESS.md`; README, AGENTS, CLAUDE, NOTICE.

**Pending**

- Phase 2: files, import, FFprobe, XDG folders, accented-folder fix, profile
  database and the profile-change dialog.

**Known issues / placeholders**

- File list, clips, songs, waveform and `Waveform 72%` are demo content.
- Effects cards, gain controls and fades are Phase 8; noise reduction is
  Phase 9; export is Phase 7; playback is Phase 3.
- The six unidentified toolbar icons are disabled pending the user's answer.
- The fourth transport icon is the design's duplicate rewind (question sent).
- The **Title** menu has one disabled placeholder (question sent).
- F11 toggles the whole window fullscreen for now.
- Zoom is display-only; real multi-resolution peaks are Phase 5.

**Tests:** `python -m pytest` → 74 passed. Ruff clean.

**Commit:** `phase 1: shell and layout`

---

## 2026-11-14 — Phase 0: Bootstrap

**Done**

- Inspected the repository, `LICENSE` (GPL-3) and the three SVG designs;
  rendered them to PNG outside the repository.
- Verified `external/kdenlive` is ignored by Git (`external/` in `.gitignore`).
- Created the documented file set and the `src/songcutter/` package layout
  (`ui`, `core`, `audio`, `export`, `io`, `config`, `i18n`), `tests/`,
  `scripts/`.
- `pyproject.toml` (setuptools, src layout, entry points), requirements,
  `.editorconfig`, `.gitignore`.
- `python -m songcutter` opens the window; the first smoke tests pass.
- Recorded the license identifier and the initial architecture decisions in
  `DECISIONS.md`.

**Pending**

- Phase 1.

**Tests:** initial suite created and passing.

**Commit:** `phase 0: bootstrap`
