# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Washington
"""Internationalization helpers.

Phase 1 wraps every user-visible string in ``self.tr()`` but does not translate
SongCutter itself. Qt's own translations are installed so standard dialogs
follow the system language.
"""

from songcutter.i18n.qt_translations import (
    find_translation_files,
    install_qt_translations,
    language_candidates,
    qt_translation_status,
)

__all__ = [
    "find_translation_files",
    "install_qt_translations",
    "language_candidates",
    "qt_translation_status",
]
