# Manual testing checklist

Written so a non-expert can follow it on Debian. Run each phase's checklist
after the phase is reported. Report failures with the step number, what you saw
and, if possible, the log file (path in step 12).

---

## Phase 0 — Bootstrap

### 0.1 Open a terminal

Press `Ctrl+Alt+T`, or open the application menu and search for **Terminal**.

### 0.2 Go to the project folder

```bash
cd ~/Dev4/songcutter-Dev/songcutter
```

(Change the path if your copy lives elsewhere.)

### 0.3 Install the system programs (once)

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip ffmpeg qt6-translations-l10n
```

`sox` is optional:

```bash
sudo apt install sox
```

### 0.4 Create the virtual environment and install

```bash
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

The prompt should now start with `(.venv)`.

### 0.5 Run the tests

```bash
python -m pytest
```

Expected: a line with `74 passed` (the number grows with later phases) and no
failures.

### 0.6 Start the program

```bash
python -m songcutter
```

Expected: the SongCutter window opens. **Acceptance for Phase 0:** it starts
without an error dialog, and these files exist:

- `README.md`
- `AGENTS.md`
- `docs/SPEC.md`
- `docs/ROADMAP.md`
- `docs/PROGRESS.md`
- `docs/GUI_MAP.md`
- `docs/DECISIONS.md`
- `docs/SHORTCUTS.md`
- `docs/TESTING.md`

Close the window with the X button.

---

## Phase 1 — Shell and layout

Start the program again (step 0.6). Keep the terminal visible; errors are logged
there and in the log file.

### 1.1 Window title and menu bar

1. The title bar reads `Untitled [HD 720p 30 fps] - SongCutter`.
2. The menu bar shows **File, Edit, Title, View, Help**.
3. Click each menu. File has New/Open/Save/Save As/Process videos/Quit; Edit has
   the editing commands; Title has one greyed-out placeholder; View has the menu
   bar toggle, Fullscreen, Zoom and Keyboard Shortcuts; Help has About entries.

### 1.2 Toolbar

1. Left side: new, open, save icons, then the six design icons (arrows, green
   plus, red stop, three circles). The six design icons are greyed out on
   purpose; hover them: the tooltip says the meaning must be confirmed.
2. Right side: `Profile:` with `HD 720p 30 fps`, then the green
   **Process videos (Ctrl+Enter)** button.
3. Click **Process videos**: the status bar shows
   "Video export arrives in Phase 7." and returns to "Ready" after a few
   seconds. Press **Ctrl+Enter** as well: the same message appears.

### 1.3 Project files panel

1. Title **Project files** with two small corner squares (disabled).
2. Filter buttons **Show all / Video / Audio / Image**, with **Show all**
   selected, and a **Filter** box.
3. Three filmstrip thumbnails, each with a file name, `00:17:04`,
   `1280x720 30 fps`.
4. Bottom row: **Folder:** with a path, **Browse...**, **Import folder**,
   **Add to timeline**.
5. Click **Browse...**: the status bar says file import arrives in Phase 2.

### 1.4 Preview panel

1. Title **Preview video**, a large white video area with a blue border and the
   word **Video**.
2. A seek bar under it.
3. A row with **In / Out / Mark**, four transport buttons (rewind, play,
   forward, rewind), the timecode `00:00:00,00`, speed `1x`, a speaker icon and
   volume slider, and **Save frame** / **Copy frame**.
4. Nothing is clipped at 1360×768: all buttons and labels are fully visible.
5. Click **Play**: the status bar says preview playback arrives in Phase 3.

### 1.5 Tabs

1. Below the panels: **Projects, Transitions, Effects, Emojis, Songs**.
2. Click **Transitions** → "Not available yet".
3. Click **Emojis** → "Not available yet".
4. Click **Effects** → the panel splits: search box and effects tree on the
   left (Audio with Volume (gain), Fade in, Fade out, Camera noise reduction,
   Normalize, Mute; Video; Favorites), and on the right
   "Effects of: (no clip selected)" with a placeholder box.
5. Click **Songs** → three songs with their start/end times and a hint about
   detection.
6. Click **Projects** to return.

### 1.6 Timeline

1. Toolbar: add/remove/razor/drop/arrow/close icons, the **S X M** toggles with
   **S** active, **Join / Group / Ungroup / Marker**, **Snap** checked, zoom
   **−** slider **+**, **Fit**, and a horizontal scroll bar.
2. Click **X**: the X button becomes active and S turns off. Press **Esc**: S is
   active again.
3. Ruler with timecode labels; current-time box `00:00:00,00` at the left; red
   playhead at the start; green **Song 1/2/3** flags.
4. Video track: yellow clips with a filmstrip and the file name.
5. Audio track: lavender clips with a dark upper-half waveform, dashed lines at
   0 dB (max), -6 dB and -12 dB, and the dB labels at the left.
6. Click at about 10 minutes on the ruler: the playhead moves there and the
   current-time box and preview timecode update.
7. Click **+** and **−**: the waveform zooms in and out. Drag the zoom slider.
   Click **Fit**: the whole 51-minute project fits again.
8. Hold **Ctrl** and use the mouse wheel over the timeline: it zooms around the
   mouse.
9. Use the horizontal scroll bar: the timeline scrolls.
10. Change **Ch: Left** to **Ch: Right**: the waveform changes shape. Toggle
    **Half wave** off and on: the waveform switches between upper-half and
    mirrored display.
11. Click the eye or lock icon in the Video header: the status bar explains
    track visibility arrives in Phase 4.

### 1.7 Splitters and proportions

1. Drag the vertical divider between the Project files panel and the Preview
   panel; both resize.
2. Drag the horizontal divider between the top row and the timeline.
3. At 1360×768 the top row is roughly 42% of the height and the timeline 58%;
   the file panel is roughly 45% of the top row's width.
4. No scroll bars appear on the main window itself.

### 1.8 Larger screen

1. If your screen is larger than 1360×768, maximise the window.
2. The layout fills the screen; the timeline keeps the whole project visible
   (if you had not zoomed in); no control is clipped; no window scroll bar.

### 1.9 Persistence

1. Drag the splitters to new positions. Resize the window a little.
2. Close the program with the X button.
3. Start it again: the window size, position and splitter positions are the
   same as when you closed it.
4. Hide the menu bar with **Ctrl+M**. Close and restart: the menu bar is still
   hidden. Press **Ctrl+M** to show it again.

### 1.10 Shortcuts dialog

1. Open **View → Keyboard Shortcuts…**.
2. The dialog lists categories (Playback, Zone, Tools, Editing, Markers, Zoom,
   Tracks, File, View, Help) and every action with its shortcut and phase.
3. Type `zoom` in the search box: only zoom actions remain visible. Clear it.
4. Select **Zoom In**, click **Change...**, press `Ctrl+Alt+Z`, click **OK**.
   The shortcut column updates.
5. Try to assign `Ctrl+S` to **Zoom In**: a warning says it is already used by
   "Save Project". Click **OK** on the warning.
6. Click **Cancel**: the dialog closes and the change from step 4 is undone
   (open the dialog again to check Zoom In is back to `Ctrl+=`).
7. Change Zoom In again to `Ctrl+Alt+Z`, click **OK**, close and restart the
   program. Open the dialog: the new shortcut is still there.
8. Click **Reset** for Zoom In, then **OK**.

### 1.11 Configuration and logs

1. Open the settings file:

   ```bash
   cat ~/.config/SongCutter/settings.json
   ```

   It contains `schema_version`, `window` (geometry, state, maximized,
   `menu_bar_visible`) and `splitters` (`main`, `top`, `effects`).

2. Open the shortcut overrides:

   ```bash
   cat ~/.config/SongCutter/shortcuts.json
   ```

   It contains `schema_version` and `overrides`.

3. Open the log:

   ```bash
   tail -n 20 ~/.local/state/SongCutter/logs/songcutter.log
   ```

   It shows the log path and the startup line.

4. Corrupt-file recovery (optional): with the program closed, replace the
   settings file with the text `broken`, start the program. It opens with
   defaults and the old file is renamed to `settings.json.corrupt-<date>`.

### 1.12 Tests

```bash
source .venv/bin/activate
python -m pytest
```

Expected: all tests pass.

---

## Phase 2 — Files, import and profiles

Not implemented yet. This section will list the FFprobe checks, the profile
dialog and the accented-folder tests (`Vídeos`, `Música`,
`Canciones de la iglesia`, `LANG=es_ES.UTF-8`).

---

## Known limits of Phase 1

- The file list, clips, songs, waveform and `Waveform 72%` are sample data.
- Playback, frame capture, import, profiles, editing, effects, noise reduction
  and export are not implemented; the controls either show a status message or
  are disabled.
- The six unidentified toolbar icons are disabled until their meaning is
  confirmed.
- The fourth transport button is the design's duplicate rewind and is disabled.
- The **Title** menu is a placeholder.
- F11 makes the whole window fullscreen; preview-only fullscreen comes with the
  preview player.
- The waveform is drawn from synthetic peaks, not from the real audio.
