# SongCutter

SongCutter is a small desktop editor for one very specific job: taking a long
recording of a church service (several songs, usually six) and turning it into
**one video per song**, quickly and from a single window.

It loads the camcorder files in order, places them back to back on a timeline,
shows a zoomable waveform so you can find where each song starts and ends, lets
you cut and join pieces, raise the low camcorder volume, fade in/out, reduce the
camera's continuous hum, and export one MP4 per song with one button.

The application is built with Python 3.10+ and PyQt6, uses FFmpeg/FFprobe for
media work, and runs offline without telemetry.

> Status: Phase 1 (application shell and layout). The window, menus, shortcuts,
> configuration and layout persistence work; media features arrive in later
> phases. See `docs/ROADMAP.md` and `docs/PROGRESS.md`.

## Requirements

### All systems

- Python 3.10 or newer
- FFmpeg and FFprobe on `PATH` (or configured later in Settings)
- Python packages listed in `requirements.txt`

### Debian / Ubuntu

```bash
sudo apt install python3 python3-venv python3-pip ffmpeg
# Recommended: Qt's own translations (Spanish Open/Save dialogs, buttons, etc.)
sudo apt install qt6-translations-l10n
# Optional: second noise-reduction engine
sudo apt install sox
```

On Debian, PyQt6 may be installed as a system package (`python3-pyqt6`). If you
prefer a virtual environment, create it with access to the system packages so Qt
is found, or install PyQt6 inside it with pip:

```bash
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### Windows

1. Install Python 3.10+ from <https://www.python.org/> (check "Add Python to PATH").
2. Install FFmpeg (for example with `winget install Gyan.FFmpeg`) and make sure
   `ffmpeg.exe` and `ffprobe.exe` are on `PATH`.
3. In a terminal:

```bat
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

### macOS

```bash
brew install python ffmpeg
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

SoX is optional on all platforms (`brew install sox` on macOS).

## Install and run

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install -r requirements-dev.txt
python -m pip install -e .
python -m songcutter
```

Without installing the package, `scripts/run.sh` puts `src/` on `PYTHONPATH`:

```bash
./scripts/run.sh
```

Run the tests with:

```bash
python -m pytest
```

## Configuration files

SongCutter stores exactly two configuration files, plus caches and logs:

| What | Linux | Windows | macOS |
| --- | --- | --- | --- |
| `settings.json` | `$XDG_CONFIG_HOME/SongCutter` (default `~/.config/SongCutter`) | `%AppData%\SongCutter` | `~/Library/Application Support/SongCutter` |
| `shortcuts.json` | same folder | same folder | same folder |
| Cache (peaks, PCM, noise profiles) | `$XDG_CACHE_HOME/SongCutter` (default `~/.cache/SongCutter`) | `%LocalAppData%\SongCutter\Cache` | `~/Library/Caches/SongCutter` |
| Log file | `$XDG_STATE_HOME/SongCutter/logs` (default `~/.local/state/SongCutter/logs`) | `%LocalAppData%\SongCutter\logs` | `~/Library/Logs/SongCutter` |

Both files are written atomically with a schema version. If a file is corrupt it
is renamed aside and the defaults are used.

## Keyboard shortcuts

The full table lives in `docs/SHORTCUTS.md`. Shortcuts can be rebound in
**View → Keyboard Shortcuts…**; changes are saved to `shortcuts.json`.

## Documentation

- `docs/SPEC.md` — the complete specification (source of truth)
- `docs/ROADMAP.md` — phases, acceptance criteria, backlog
- `docs/PROGRESS.md` — what is done, newest first
- `docs/GUI_MAP.md` — design region → widget/class/file map
- `docs/DECISIONS.md` — technical decisions and reasons
- `docs/TESTING.md` — manual test checklist per phase
- `docs/SHORTCUTS.md` — keyboard shortcuts

## Packaging notes

The app can be bundled with PyInstaller once the media features exist:

```bash
python -m pip install pyinstaller
pyinstaller --name SongCutter --windowed --add-data "src/songcutter:i18n" src/songcutter/__main__.py
```

FFmpeg/FFprobe are external programs and are not bundled; ship them next to the
executable or document their installation. Packaging is reviewed in Phase 10.

## Acknowledgements

- **Kdenlive** (<https://kdenlive.org>, GPL-3.0-or-later): the timeline concept,
  shortcuts, effect-card layout and the video profile database come from
  Kdenlive. Profile data is reused with credit; see `NOTICE.md`.
- **Qt 6 / PyQt6** — application framework.
- **FFmpeg** — decoding, analysis and export.
- **noisereduce**, **SoX** — noise reduction engines.
- **numpy**, **platformdirs** — supporting libraries.

## License

GPL-3.0-or-later. See `LICENSE`. The SPDX identifier used in source headers is
`GPL-3.0-or-later`, recorded in `docs/DECISIONS.md`.
