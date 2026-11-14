# SongCutter — Specification

This document is the source of truth for SongCutter. It is split by the sections
of the original brief. Code, comments, documentation, commit messages and UI
source strings are in English; the user writes in Spanish and receives reports
in Spanish.

---

## 1. Repository and first actions

### 1.1 What already exists (do not overwrite or delete)

- `LICENSE`: GPL 3. Source headers use the SPDX identifier
  `GPL-3.0-or-later`; the choice is recorded in `docs/DECISIONS.md`.
- `designs-ux_ui/songcutter-gui.svg`: main window, Projects tab.
- `designs-ux_ui/songcutter-gui-effects.svg`: main window with the Effects tab.
- `designs-ux_ui/songcutter-gui-dialogs.svg`: three dialogs (change project
  profile, project settings, Process videos).
- `external/kdenlive/`: untracked clone of Kdenlive's source
  (<https://github.com/kde/kdenlive>) for research and profile data. Never
  commit it, never modify it, and verify with `git check-ignore external/kdenlive`
  that Git ignores it (otherwise add `external/` to `.gitignore`).

Before creating anything: run `git status`, list the repository, read the three
SVGs, and render them to PNG for visual inspection (Inkscape, otherwise
`cairosvg` in a temporary virtual environment). Renders stay out of Git.

### 1.2 Files to create

Skip any that already exist and never overwrite the user's files.

- `README.md`: what the program is, install steps per OS, run command,
  dependencies (including system packages), config file locations,
  acknowledgements.
- `AGENTS.md`: working rules plus a short project summary. `CLAUDE.md` points to
  it in one line.
- `NOTICE.md`: third-party credits. Credit Kdenlive (name, URL, license, what
  was taken) for anything reused.
- `docs/SPEC.md` (this file), `docs/GUI_MAP.md`, `docs/ROADMAP.md`,
  `docs/PROGRESS.md`, `docs/DECISIONS.md`, `docs/SHORTCUTS.md`,
  `docs/TESTING.md`.
- `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`, `.gitignore`,
  `.editorconfig`.
- Source layout: `src/songcutter/` with `__init__.py`, `__main__.py`, `app.py`
  and sub-packages `ui/`, `core/` (data model, commands), `audio/` (decoding,
  waveform, effects, noise reduction, playback engine), `export/`, `io/`
  (ffprobe, file discovery, profiles), `config/`, `i18n/`, plus `tests/` and
  `scripts/`.

### 1.3 Working rules (mirrored in `AGENTS.md`)

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
10. When reusing anything from `external/kdenlive`, check the license header of
    each file first, keep its copyright notice, and list it in `NOTICE.md`.
    Prefer reusing data (for example profile values) and writing your own code
    over copying source files.

---

## 2. Product context

The user films the songs (alabanzas) of a service, normally about 6 songs per
session. The camcorder records **MP4 in HD (720p)** and often splits one
recording into several files. The camcorder records at a low volume, so the
user always has to raise it. The user also edits videos shot with a phone, which
are **Full HD MP4**. Today the user copies the memory card, imports everything
into Kdenlive or OpenShot, joins the pieces, finds where each song starts and
ends, cuts, exports one project per song with scripts, and renders them one by
one. That is slow and those editors have too many panels.

The new program must do this on one screen:

1. Load the camcorder files from a folder (in order) and place them back to back
   on the timeline as one continuous recording.
2. Let the user listen, zoom into the audio waveform, find where each song
   starts and ends, cut there, and delete what is between songs.
3. Let the user join pieces that belong to the same song.
4. Let the user raise the volume easily, seeing the waveform grow on the
   timeline, plus fade in, fade out, and removal of the camcorder's continuous
   hum using a recorded noise sample.
5. With one button (**Process videos**) export **one video per song**: 4 cut
   songs give 4 videos, 6 give 6.

---

## 3. GUI design (source of truth)

The designs use a 1366×768 canvas. The program must work at **1360×768**
(primary) and scale to larger screens, built with layouts and splitters, never
fixed pixel positions. Use the SVGs for structure, proportions, labels and
controls. Native Qt widgets are fine; no custom skinning.

### 3.1 Main window (`songcutter-gui.svg`)

- **Title bar:** `<project name> [<profile>] - SongCutter`
  (e.g. `Preach Landy Ortega [HD 720p 30 fps] - SongCutter`).
- **Menu bar** (hideable with Ctrl+M): File, Edit, Title, View, Help. The design
  has a menu called Title; ask the user whether it stays or is renamed.
- **Top toolbar:** a row of icons (new, open, save, arrows, add, stop, and so
  on) plus, on the right, the **project profile selector** and the green
  **Process videos (Ctrl+Enter)** button. Several icons have no label in the
  design. **Do not guess their meaning**: ask the user and build only the ones
  the user confirms.
- **Top-left panel** (Project files; the design shows `Archivos del proyecto`):
  filter buttons (Show all, Video, Audio, Image) and a Filter box; a thumbnail
  bin where every file shows its name plus duration, frame size and frame rate;
  a bottom row with the **Folder** path box, **Browse...**, **Import folder** and
  **Add to timeline**.
- **Top-right panel (Preview video):** video area, seek bar, a row with
  **In / Out / Mark**, transport buttons (the fourth transport icon in the
  design is a duplicate rewind; ask the user what it should be), timecode, speed
  selector, volume slider, **Save frame** and **Copy frame**.
- **Tab row** under the top panels: Projects, Transitions, Effects, Emojis,
  Songs. The tabs switch the content of the top-left panel. Build all five as
  in the design; Transitions and Emojis show a placeholder (Not available yet)
  and go to the Backlog. **Songs** lists detected songs (section 8).
- **Timeline toolbar:** existing icons (add, remove, razor, drop, arrows,
  close), tool toggles **S** (selection, default), **X** (razor), **M**
  (spacer), then **Join**, **Group**, **Ungroup**, **Marker**, a **Snap**
  checkbox, **zoom out, zoom slider, zoom in, Fit**, and a horizontal scroll bar
  on the right.
- **Ruler** with timecode and markers (green flags with song names), the
  **current-time box** at its left (`00:03:24,07`), and the red playhead.
- **Two tracks only.** Video header (label, hide and lock icons) and audio
  header (label, **Mute**, **Lock**, channel selector default Left, **Half
  wave** checkbox). Video clips are yellow with a thumbnail and file name.
  Audio clips are lavender with the dark waveform and a **dB scale** with dashed
  lines at 0 dB (maximum), -6 dB and -12 dB. A vertical scroll bar at the right.
- **Status bar:** current profile, number of clips, number of detected songs,
  state, and a small progress bar for background work such as the waveform.
- All panels are separated by splitters the user can drag; save and restore
  sizes. Default proportions at 1360×768: top row about 42% of the height,
  timeline about 58%; file panel about 45% of the width of the top row.

### 3.2 Effects state (`songcutter-gui-effects.svg`)

When the **Effects** tab is active, the top-left panel is split in two:

- **Left (less than half):** search box and a tree: Audio (Volume (gain), Fade
  in, Fade out, Camera noise reduction, Normalize, Mute), Video, Favorites.
- **Right (the rest):** controls of the effects applied to the selected clip,
  as a stack of collapsible cards with an enable checkbox and a remove button,
  like Kdenlive.
- The user adds an effect by **dragging it onto the audio track** (or
  double-clicking it with a clip selected). The controls then appear on the
  right.
- **Volume (gain) card:** gain slider (about -20 to +30 dB) with a number box,
  quick buttons (-6 dB, 0 dB reset, +6 dB, +12 dB), the clip peak in dBFS, the
  peak after gain, the **maximum boost without clipping**, a **Set to maximum**
  button, a **Limit to 0 dBFS** checkbox, and a choice between This clip and All
  clips of the audio track.
- **The waveform follows the gain live** (section 7.2) and the clip shows a
  Gain label.

### 3.3 Dialogs (`songcutter-gui-dialogs.svg`)

1. **Change project profile** (section 5).
2. **Project settings** with a profile drop-down and a long profile list (like
   Kdenlive), the frame size, frame rate, display aspect and scanning of the
   selected profile, and **Add custom profile...**.
3. **Process videos** (section 8).

---

## 4. Technology and constraints

- Python 3.10+, **PyQt6**. Video preview with Qt Multimedia. Camcorder files
  are MP4; if some file (e.g. H.265) does not play, record it in `DECISIONS.md`
  and propose proxy files made with FFmpeg.
- **FFmpeg and FFprobe** as external programs, found on PATH or at a path set in
  Settings, with a clear message and install hints if missing. Run them in the
  background and parse progress (for example `-progress pipe:1`).
- Libraries: `numpy`, `noisereduce` (brings `scipy`), `platformdirs`. **SoX** is
  an optional external program (section 7.4).
- **Audio playback engine (important):** Qt's `QAudioOutput.volume` cannot go
  above 1.0, so it cannot play a +6 dB gain. Decode the audio of each source to
  PCM (cached on disk) and play it through our own engine (for example
  `QAudioSink`), applying gain, fades, mute and the optional noise-reduced
  version while mixing. Keep the video widget silent and keep the video in sync
  with the audio clock. Record this in `DECISIONS.md`.
- Target OS: Debian-based Linux first, also Windows and macOS. Offline, no
  telemetry.

---

## 5. Video profiles and the profile-change message

- Build a **profile database** with many profiles, like Kdenlive's. Research
  `external/kdenlive` and the MLT profile format (description, width, height,
  frame rate numerator and denominator, progressive, sample and display aspect
  ratios) and load the values from there or from a data file derived from it,
  credited in `NOTICE.md`. Include at least HD 720p, FHD 1080p, UHD 2160p and SD
  profiles at 24, 25, 30, 50 and 60 fps. Show a friendly name such as
  `HD 720p 25 fps` or `FHD 1080p 24 fps`.
- When a file is added to the project (dragged to the timeline, **Add to
  timeline**, or **Import folder**), read its size, frame rate, scan type and
  aspect ratio with FFprobe and compare them with the **project profile**. The
  first clip of an empty project always triggers the check.
- If they do not match, show the dialog from the design with:
  `Change project to profile "HD 720p 25 fps" from clip "HDV_0270.MP4"`.
  Buttons: **Change project profile**, **Keep current profile**, **Cancel**, and
  a checkbox to not ask again in this session. If no profile matches the clip
  exactly, offer to create a custom profile with the clip's values.
- Spanish text for later: `Cambiar proyecto al perfil "HD 720p 25 fps" del clip
  "HDV_0270.MP4"`.
- The project profile appears in the window title, toolbar selector, status bar
  and Project settings dialog, and is saved in the project file. Camcorder HD
  (720p) and phone Full HD (1080p) are the common cases; both must match
  correctly.

---

## 6. Timeline tools and shortcuts (Kdenlive style)

The timeline behaves like Kdenlive's. A central **action manager** gives every
command an id and a default key sequence, rebindable in a Shortcuts dialog saved
in `shortcuts.json`. **Must** items go in the phase where the feature exists.

| Area | Action | Default | Priority |
| --- | --- | --- | --- |
| Playback | Play / stop | Space | Must |
| Playback | Pause | K | Should |
| Playback | Forward (cycles speeds) / Rewind | L / J | Should |
| Playback | Forward / back 1 frame | Right / Left | Must |
| Playback | Forward / back 1 second | Shift+Right / Shift+Left | Must |
| Playback | Previous / next snap point | Alt+Left / Alt+Right | Should |
| Playback | Previous / next marker | Ctrl+Left / Ctrl+Right | Must |
| Playback | Clip start / end | Home / End | Should |
| Playback | Project start / end | Ctrl+Home / Ctrl+End | Must |
| Playback | Align playhead to mouse | P | Should |
| Playback | Play zone / loop zone | Ctrl+Space / Ctrl+Shift+Space | Should |
| Zone | Set zone in / out | I / O | Must |
| Zone | Go to zone start / end | Shift+I / Shift+O | Should |
| Tools | Selection / Razor / Spacer / back to Selection | S / X / M / Esc | Must |
| Editing | Cut clip at playhead | Shift+R | Must |
| Editing | Cut all clips at playhead | Ctrl+Shift+R | Must |
| Editing | Trim clip start / end to playhead | ( / ) | Should |
| Editing | Delete | Del | Must |
| Editing | Extract (delete and close the gap) | Shift+Del | Must |
| Editing | Lift / extract timeline zone | Z / Shift+X | Should |
| Editing | Group / ungroup | Ctrl+G / Ctrl+Shift+G | Must |
| Editing | Select all / add to selection | Ctrl+A / Shift+click | Must |
| Editing | Undo / redo | Ctrl+Z / Ctrl+Shift+Z | Must |
| Editing | Copy / paste / duplicate | Ctrl+C / Ctrl+V / Ctrl+D | Should |
| Markers | Add / remove marker at playhead | G | Must |
| Zoom | Zoom in | Ctrl+= or Ctrl++ | Must |
| Zoom | Zoom out | Ctrl+- | Must |
| Zoom | Zoom with the wheel | Ctrl+MouseWheel | Must |
| Navigation | Scroll horizontally / vertically | MouseWheel / Shift+MouseWheel | Must |
| Navigation | Pan | Ctrl+drag or middle-button drag | Should |
| Tracks | Lock / mute-hide track | Shift+L / Ctrl+Shift+H | Should |
| File | Save / open / save as | Ctrl+S / Ctrl+O / Ctrl+Shift+S | Must |
| File | Process videos | Ctrl+Return | Must |
| View | Show / hide the menu bar | Ctrl+M | Must |
| View | Fullscreen preview | F11 | Should |

On macOS Qt maps Ctrl to Cmd, which is fine. Optional setting: a **centered
playhead** that stays in the middle while the waveform scrolls, as in Kdenlive.

---

## 7. Audio features

### 7.1 Waveform, one channel, half wave and zoom (very important)

- Show **only one of the two stereo channels** (selector in the audio track
  header: Left by default, or Right) and show **only the upper half** of the
  wave (amplitude from a baseline up, as drawn in the designs). Both are display
  options (also in Settings); they never change the sound. Mono sources show
  their only channel.
- Extract audio with FFmpeg in a background thread, compute peaks of the
  selected channel and store a **multi-resolution peak pyramid** on disk (cache
  directory) keyed by file path, size, modified time and channel. Show progress
  in the status bar. Draw only the visible range with QPainter so zooming stays
  smooth for recordings of 1 to 2 hours.
- Zoom range: from the whole project to a few milliseconds per pixel, with
  **zoom in/out buttons**, slider, **Fit**, and the section 6 shortcuts. Zoom
  centers on the playhead (or the mouse for Ctrl+MouseWheel).
- Draw the **dB scale** (0 dB = top, maximum possible; dashed lines at -6 dB and
  -12 dB). Options: normalize the waveform display and a vertical scale.
- While playing, the playhead can follow the audio (auto-scroll or centered
  playhead).

### 7.2 Volume gain

- The effect is the **Volume (gain)** card (section 3.2). Slider and number box
  are linked; it works per clip or for all clips of the audio track.
- **Live waveform:** while moving the gain control, the timeline waveform is
  redrawn scaled by 10^(gain/20), with the original level as a dashed outline.
  Anything above 0 dB (the top line) is drawn clipped in red, so the user sees
  how far the volume can go.
- Show the clip's peak, the peak after gain and the maximum boost without
  clipping (from peak data). **Set to maximum** sets the gain to that maximum
  minus a 0.1 dB safety margin. **Limit to 0 dBFS** stops the slider there.
- **Play must let the user hear the difference** at once through the audio
  engine (section 4).
- Each audio clip also has a mute flag. Gain is applied exactly on export.

### 7.3 Fade in and fade out

Each audio clip has fade-in and fade-out lengths, set by dragging a handle at the
top corners of the clip (as in Kdenlive) or by typing the duration in the Fade
in / Fade out card. Draw the fade curve over the waveform, apply it in preview
and on export.

### 7.4 Camcorder noise removal (continuous hum)

- Card **Camera noise reduction** (in Effects, stacked with the others) with a
  **Load camera noise sample** button (WAV, MP3, FLAC, M4A and so on, decoded
  with FFmpeg). Remember the last sample. Optionally use a timeline range as the
  sample.
- **Method selector** with two engines: **noisereduce (default)** and **SoX**.
  - noisereduce: stationary mode with the sample as the noise reference;
    strength mapped to `prop_decrease`.
  - SoX: build a noise profile from the sample (`noiseprof`) and apply
    `noisered` with an amount from 0 to 1. If `sox` is not found, disable this
    option with a tooltip explaining installation (Debian:
    `sudo apt install sox`; macOS: Homebrew; Windows: set the path in Settings).
- **Strength** slider, **Apply on export** checkbox, and a **Preview** that
  processes about 10 seconds around the playhead and lets the user toggle
  original vs processed (A/B) while listening.
- Process per song and in chunks, with bounded memory. Cache noise profiles by
  sample hash. The video stream is never re-encoded because of noise removal
  alone.

---

## 8. Project model, songs and export

- **Non-destructive:** the project stores references to source files and never
  modifies them. Model: Project (with profile), Track, Clip (source, in and out,
  timeline start, gain, fades, mute, effect stack), Group (a song: name, ordered
  clips) and Marker. All edits go through an undo stack (QUndoStack).
- **Join:** merges two adjacent pieces of the same source (one ends exactly
  where the next begins) into a single clip. For pieces from different files,
  grouping them (Ctrl+G) makes them one song.
- **Song detection**, in order: (a) every Group is one song; (b) otherwise every
  continuous block of clips separated by a gap is one song; (c) optionally,
  markers split the timeline like Kdenlive's Markers Multi-Export. The **Songs**
  tab lists them; the user can rename, enable or disable each and click one to
  jump to it.
- **Process videos** dialog: checked songs with start, end and duration; output
  folder (default `export` next to the source files); file name pattern
  (default `{index:02d} - {name}`); MP4; quality **Accurate** (re-encode H.264
  and AAC, exact cuts, default) or **Fast** (copy the video stream, cuts snap to
  keyframes, with a warning); checkboxes for noise reduction and for applying
  each clip's gain and fades; a progress bar per song and an overall one;
  cancel; a summary at the end with a button to open the folder. N checked songs
  produce exactly N files.
- Save and open projects as `.songcutter` JSON with a schema version and
  relative paths when possible. Autosave and crash recovery come in the final
  phase.

---

## 9. Platform requirements

### 9.1 Config files

Use `platformdirs` with the app name `SongCutter`. Exactly two config files:
`settings.json` (general settings, window geometry, splitter sizes, recent
folders, tool paths, noise and export defaults, language) and
`shortcuts.json`. Locations: Windows `%AppData%` (roaming, e.g.
`%AppData%\SongCutter`); Linux `$XDG_CONFIG_HOME/SongCutter` (default
`~/.config/SongCutter`); macOS `~/Library/Application Support/SongCutter`. Write
atomically, include a schema version, recover with defaults if a file is
corrupt. Caches (peaks, PCM, noise profiles, proxies) go in the cache directory.

### 9.2 XDG user folders on Linux

Locate Videos, Music, Pictures and the rest through `QStandardPaths` and, as a
fallback, by parsing `~/.config/user-dirs.dirs` (read as UTF-8, expand `$HOME`).
Folder names are localized (`Vídeos`, `Música`, `Imágenes`, `Descargas`), so
never hard-code English names.

### 9.3 Accented folder names in file dialogs

On Linux the PyQt6 open/save dialog sidebar (places and bookmarks) often shows
accented names wrongly. Investigate the root cause with a small test script and
fix it. Likely causes: bookmark files with percent-encoded UTF-8 paths (e.g.
`~/.config/gtk-3.0/bookmarks` and KDE's `user-places.xbel`), a non-UTF-8 locale,
and `QUrl` or path decoding. Build the sidebar explicitly with
`QFileDialog.setSidebarUrls(...)` from the XDG folders plus decoded bookmarks,
read every file with `encoding='utf-8'`, and use `os.fsdecode` for paths. Test
with `LANG=es_ES.UTF-8` and folders named `Vídeos`, `Música` and
`Canciones de la iglesia`. Use the native dialog on Windows and macOS.

### 9.4 Qt's own translations

Use the Debian package **`qt6-translations-l10n`** so Qt's standard dialogs
(Open, Save As, buttons, system messages) appear in the user's language. At
startup load `qtbase_<lang>.qm` and `qt_<lang>.qm` (and `qtmultimedia_<lang>.qm`
if present) with `QTranslator`, searching in this order: `QLibraryInfo`
translations path, the translations folder bundled in the PyQt6 wheel, and
`/usr/share/qt6/translations` on Linux. List the package in the README as a
recommended system dependency and show a hint in the About or diagnostics dialog
if the files for the selected language are not found.

### 9.5 Windows and macOS

Look for FFmpeg and SoX on PATH and at user-set paths; document installation;
keep packaging notes (e.g. PyInstaller) in the README.

---

## 10. Internationalization (English first)

Develop the whole program **in English first**. From day one wrap every
user-visible string with `self.tr()` or `QCoreApplication.translate()` using
stable contexts, so translation can be added later without refactoring. Do
**not** translate during development. In the last phase add the language
selector (System default, English, Spanish and others), extract strings with
`pylupdate6`, translate with Qt Linguist `.ts` files, compile with `lrelease`,
ship the `.qm` files, and add Spanish plus the other languages the user asks
for.

---

## 11. Roadmap

### Phase 0: Bootstrap

Inspect the repository and SVG designs, create the files in section 1.2 without
overwriting anything, a virtual environment guide, an empty main window that
starts with `python -m songcutter`, and a passing test run.

**Acceptance:** it runs on Debian and the docs exist.

### Phase 1: Shell and layout

Build the static layout from `songcutter-gui.svg`: title, menus, toolbar, the
two top panels, the tab row, the timeline block with its toolbar, ruler, two
track headers and status bar, all with placeholder content; splitters, the two
config files with geometry and splitter persistence, the action manager and
Shortcuts dialog, logging, and `tr()` wrapping. Ask the user the questions in
section 3.1.

**Acceptance:** it looks like the design at 1360×768 and at 1920×1080 without
scrolling the window, and panel sizes survive a restart.

### Phase 2: Files, import and profiles

Thumbnail bin, Folder, Browse, Import folder and Add to timeline, FFprobe info
on each file, natural file ordering, the XDG folders, the accented-folder fix,
FFmpeg detection and the Settings page for tool paths, the **profile database**
from `external/kdenlive`, the project profile selector and the **profile-change
dialog**.

**Acceptance:** HD 720p and Full HD 1080p files are detected correctly, the
message appears with the right profile and file name, and localized folder names
display correctly in all dialogs.

### Phase 3: Preview player

Playback, seek bar, timecode, frame step, speed, volume, In/Out/Mark, and frame
extraction (Save frame and Copy frame, extracted exactly with FFmpeg).

**Acceptance:** the extracted frame matches the paused frame.

### Phase 4: Timeline core

Data model, undo stack, ruler, playhead, current-time box, V1 and A1 tracks with
linked clips, adding files in order as one continuous sequence, zoom, scroll,
pan, snap, zone, markers, and timeline playback across clip boundaries through
the audio engine from section 4.

**Acceptance:** several camcorder files play as one recording with sound.

### Phase 5: Waveform

Background peak extraction, disk cache, multi-resolution drawing, one-channel
and half-wave display, dB scale, zoom in/out buttons, slider, Fit, shortcuts,
follow or centered playhead, resizable track heights.

**Acceptance:** smooth zoom from the whole recording to millisecond detail on a
1-hour file.

### Phase 6: Editing tools

Selection, Razor, Spacer, cut at playhead, cut all, trim to playhead, delete,
extract, multi-select, group and ungroup, Join, duplicate, copy and paste, with
full undo.

**Acceptance:** the user can cut 6 songs out of one recording and remove what is
between them.

### Phase 7: Songs, project files and export (core MVP)

Project save and open, song detection and the Songs tab, the Process videos
dialog, per-song FFmpeg export with progress and cancel, Accurate and Fast modes.

**Acceptance:** 4 cut songs produce exactly 4 correct videos, tested end to end
with a sample recording.

### Phase 8: Effects tab, volume gain and fades

The split Effects panel, the effects tree, drag onto the audio track, the stack
of effect cards, **Volume (gain)** with live waveform and Set to maximum, mute,
fade handles, preview through the audio engine, exact export.

**Acceptance:** raising the gain visibly raises the waveform, shows the maximum,
and is audible when the user presses Play.

### Phase 9: Noise reduction

The Camera noise reduction card, noise sample loading, noisereduce (default) and
SoX engines, strength, A/B preview, chunked processing, caching, tool detection.

**Acceptance:** the camera hum is clearly reduced without damaging voices or
music, and the user can compare both engines.

### Phase 10: Hardening and cross-platform

Tests on Windows and macOS, long-recording performance, autosave and crash
recovery, packaging notes, final shortcut review.

### Phase 11: Internationalization

Everything in section 10 and Qt's own translations from section 9.4.

### Backlog (do not build unless asked)

Transitions and Emojis tabs, notch filter for the hum's exact frequency, Insert
and Overwrite modes, video thumbnails on the track, proxies, hardware encoding.

---

## 12. Definition of done for every phase

The app starts without errors; new code has tests where practical; the docs,
`GUI_MAP.md` and the roadmap are updated; the phase is committed locally; and
the user was reported to in Spanish and is waiting for feedback.
