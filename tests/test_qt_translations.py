# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Washington
"""Tests for Qt translation discovery."""

from __future__ import annotations

from songcutter.i18n.qt_translations import (
    find_translation_files,
    install_qt_translations,
    language_candidates,
    qt_translation_status,
)


def test_language_candidates():
    assert language_candidates("es_EC") == ["es_EC", "es"]
    assert language_candidates("es") == ["es"]
    assert language_candidates("es-ES") == ["es_ES", "es"]


def test_find_translations_returns_list():
    files = find_translation_files("es")
    assert isinstance(files, list)


def test_install_does_not_raise(qapp):
    loaded = install_qt_translations(qapp, "es")
    assert isinstance(loaded, list)


def test_status_is_a_string():
    assert "translation" in qt_translation_status("es").lower()
