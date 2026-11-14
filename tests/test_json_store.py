# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Washington
"""Tests for the atomic JSON store."""

from __future__ import annotations

import json

from songcutter.config.json_store import JsonStore


def test_missing_file_returns_defaults(tmp_path):
    store = JsonStore(tmp_path / "missing.json", {"a": 1, "nested": {"b": 2}})
    assert store.load() == {"a": 1, "nested": {"b": 2}, "schema_version": 1}


def test_roundtrip_and_atomic_write(tmp_path):
    path = tmp_path / "config.json"
    store = JsonStore(path, {"value": 0})
    store.save({"value": 7, "text": "ñandú"})
    assert json.loads(path.read_text(encoding="utf-8"))["value"] == 7
    assert JsonStore(path, {"value": 0}).load()["value"] == 7
    assert not list(tmp_path.glob("*.tmp"))


def test_missing_keys_are_filled_from_defaults(tmp_path):
    path = tmp_path / "config.json"
    path.write_text('{"window": {"geometry": "abc"}}', encoding="utf-8")
    data = JsonStore(path, {"window": {"geometry": "", "maximized": False}}).load()
    assert data["window"]["geometry"] == "abc"
    assert data["window"]["maximized"] is False


def test_corrupt_file_is_quarantined(tmp_path):
    path = tmp_path / "config.json"
    path.write_text("{not json", encoding="utf-8")
    store = JsonStore(path, {"value": 1})
    assert store.load()["value"] == 1
    assert not path.exists()
    assert list(tmp_path.glob("config.json.corrupt-*"))


def test_non_object_json_is_quarantined(tmp_path):
    path = tmp_path / "config.json"
    path.write_text("[1, 2, 3]", encoding="utf-8")
    store = JsonStore(path, {"value": 1})
    assert store.load()["value"] == 1
    assert list(tmp_path.glob("config.json.corrupt-*"))


def test_unknown_schema_version_still_merges(tmp_path):
    path = tmp_path / "config.json"
    path.write_text('{"schema_version": 99, "value": 5}', encoding="utf-8")
    data = JsonStore(path, {"value": 1, "other": 2}).load()
    assert data["value"] == 5
    assert data["other"] == 2
    assert data["schema_version"] == 1
