# Third-party notices

SongCutter is licensed under GPL-3.0-or-later. It uses or reuses the following
third-party work.

## Kdenlive

- Project: Kdenlive — <https://kdenlive.org> — <https://github.com/kde/kdenlive>
- License: GPL-3.0-or-later (see `external/kdenlive/COPYING` in a local clone).
- What is taken: the video **profile values** (description, frame size, frame
  rate numerator/denominator, progressive flag, sample aspect ratio, display
  aspect ratio) are derived from Kdenlive's/MLT's profile data and shipped as a
  data file. The timeline interaction model, default keyboard shortcuts and the
  effect-card layout are inspired by Kdenlive. No Kdenlive source file is copied
  verbatim; if that changes, the file keeps its copyright header and is listed
  here.
- Kdenlive is a KDE project; thanks to its authors.

## Qt and PyQt6

- Qt 6 — <https://www.qt.io/> — LGPL-3.0 / GPL-3.0 commercial alternatives.
- PyQt6 — <https://riverbankcomputing.com/software/pyqt/> — GPL-3.0.
- Qt translations come from the distribution package `qt6-translations-l10n`.

## FFmpeg

- <https://ffmpeg.org/> — LGPL/GPL depending on the build. Invoked as an
  external program; not linked.

## SoX

- <https://sox.sourceforge.net/> — GPL-2.0/LGPL. Optional external program for
  the second noise-reduction engine.

## Python libraries

- numpy — BSD-3-Clause
- noisereduce — MIT
- scipy (dependency of noisereduce) — BSD-3-Clause
- platformdirs — MIT

## Icons

Toolbar and transport icons are drawn at runtime with QPainter from simple
geometric shapes; no third-party icon set is bundled.
