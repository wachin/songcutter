# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Washington
"""Qt's own translations (Open/Save dialogs, buttons, system messages).

The application is developed in English; this module only installs the
translations that ship with Qt so standard dialogs follow the user's language.
SongCutter's own strings are translated in Phase 11.
"""

from __future__ import annotations

import logging
from pathlib import Path

from PyQt6.QtCore import QLibraryInfo, QLocale, QTranslator
from PyQt6.QtWidgets import QApplication

log = logging.getLogger(__name__)

TRANSLATION_BASES = ("qtbase", "qt", "qtmultimedia")


def _candidate_dirs() -> list[Path]:
    candidates: list[Path] = []

    library_path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
    if library_path:
        candidates.append(Path(library_path))

    try:
        import PyQt6

        wheel_root = Path(PyQt6.__file__).resolve().parent
        candidates.extend(
            [
                wheel_root / "Qt6" / "translations",
                wheel_root / "translations",
            ]
        )
    except Exception:  # pragma: no cover - PyQt6 always importable here
        pass

    candidates.append(Path("/usr/share/qt6/translations"))

    result: list[Path] = []
    seen: set[Path] = set()
    for path in candidates:
        resolved = path.resolve()
        if resolved in seen or not path.is_dir():
            continue
        seen.add(resolved)
        result.append(path)
    return result


def language_candidates(language: str | None) -> list[str]:
    """Return language codes to try, most specific first."""
    if not language:
        language = QLocale.system().name()  # e.g. "es_EC"
    language = language.replace("-", "_")
    codes: list[str] = []
    if language and language != "system":
        codes.append(language)
        base = language.split("_")[0]
        if base and base not in codes:
            codes.append(base)
    return codes


def find_translation_files(language: str | None = None) -> list[Path]:
    """Find available ``.qm`` files for the requested language."""
    codes = language_candidates(language)
    found: list[Path] = []
    for directory in _candidate_dirs():
        for base in TRANSLATION_BASES:
            for code in codes:
                candidate = directory / f"{base}_{code}.qm"
                if candidate.is_file() and candidate not in found:
                    found.append(candidate)
    return found


def install_qt_translations(
    app: QApplication, language: str | None = None
) -> list[Path]:
    """Install the first matching Qt translation for each base module."""
    loaded: list[Path] = []
    keep_alive = getattr(app, "_songcutter_qt_translators", None)
    if keep_alive is None:
        keep_alive = []
        app._songcutter_qt_translators = keep_alive  # type: ignore[attr-defined]

    codes = language_candidates(language)
    for base in TRANSLATION_BASES:
        installed = False
        for directory in _candidate_dirs():
            for code in codes:
                candidate = directory / f"{base}_{code}.qm"
                if not candidate.is_file():
                    continue
                translator = QTranslator(app)
                if translator.load(str(candidate)):
                    app.installTranslator(translator)
                    keep_alive.append(translator)
                    loaded.append(candidate)
                    log.info("Loaded Qt translation %s", candidate)
                    installed = True
                    break
            if installed:
                break

    if not loaded:
        log.info(
            "No Qt translations found for %s (checked %s)",
            ", ".join(codes) or "system language",
            ", ".join(str(path) for path in _candidate_dirs()),
        )
    return loaded


def qt_translation_status(language: str | None = None) -> str:
    """Short diagnostic string for the About/diagnostics dialog."""
    codes = language_candidates(language)
    files = find_translation_files(language)
    if files:
        return f"{len(files)} Qt translation file(s) found for {', '.join(codes)}"
    return f"No Qt translation files found for {', '.join(codes) or 'the system language'}"


__all__ = [
    "find_translation_files",
    "install_qt_translations",
    "language_candidates",
    "qt_translation_status",
]
