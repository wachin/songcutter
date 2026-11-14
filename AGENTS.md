# AGENTS.md

Working rules for anyone (human or AI) changing this repository.

## Project summary

SongCutter turns a long, multi-song recording (camcorder MP4 720p, often split
into several files, plus phone Full HD MP4) into one exported video per song.
One window: file bin, preview, waveform timeline with two tracks, songs, and a
**Process videos** button. Python 3.10+, PyQt6, FFmpeg/FFprobe. GPL-3.0-or-later.
Source in `src/songcutter/`, tests in `tests/`, docs in `docs/`. The design
source of truth is `designs-ux_ui/*.svg`; `external/kdenlive` is an untracked
reference clone that must never be committed or modified.

## Rules

1. At the start of every session read `AGENTS.md`, `docs/ROADMAP.md` and
   `docs/PROGRESS.md`.
2. Work on **one phase at a time**. Keep the app runnable at the end of every
   phase.
3. Do not add features that are not in the current phase. Put new ideas in the
   Backlog of `docs/ROADMAP.md`.
4. Follow the SVG designs. If you need to deviate, or something in a design is
   unclear, say so in your report and ask; do not silently change the layout.
5. Before finishing a phase: run the tests, update `ROADMAP.md` (tick items),
   `PROGRESS.md`, `SHORTCUTS.md`, `GUI_MAP.md` and `TESTING.md`, then make a
   local Git commit with the message `phase N: short summary`. Do not push
   unless the user asks.
6. Finish with a short report in Spanish: what works, how to test it (point to
   `docs/TESTING.md`), known limits, questions, and the proposed next phase.
   Then wait.
7. If something is ambiguous, make the most reasonable choice, record it in
   `DECISIONS.md`, and continue. Ask the user only if blocked (at most three
   questions at a time).
8. Keep the UI model-driven: UI code never edits data directly; it issues
   commands to an undo stack. Heavy work (FFmpeg, waveform, noise reduction,
   export) runs in background threads or processes, never in the UI thread.
9. Use type hints, small modules, `pathlib` and `logging` (log file in the state
   directory). Write unit tests for the data model, undo commands, profile
   matching and the FFmpeg command builder.
10. When you reuse anything from `external/kdenlive`, check the license header
    of each file first, keep its copyright notice, and list it in `NOTICE.md`.
    Prefer reusing data (for example the profile values) and writing your own
    code over copying source files.

## Conventions

- Code, comments, docs, commit messages and UI source strings: English.
- Every user-visible string goes through `self.tr(...)` or
  `QCoreApplication.translate(context, ...)` from day one, with stable contexts.
  Do not translate during development; translation is Phase 11.
- License header on every Python source file:
  `# SPDX-License-Identifier: GPL-3.0-or-later` plus
  `# Copyright (C) 2026 Washington`.
- Do not commit `external/`, design renders, caches, virtual environments or
  generated media.
