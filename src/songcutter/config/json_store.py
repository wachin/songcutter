# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Washington
"""Atomic JSON file storage with schema versioning and corrupt-file recovery."""

from __future__ import annotations

import contextlib
import copy
import json
import logging
import os
import tempfile
import time
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

SCHEMA_VERSION = 1


class JsonStore:
    """Load and save a JSON object atomically.

    ``defaults`` is a nested dictionary used to fill in missing keys and to
    recover when the file is missing or corrupt. A corrupt file is renamed to
    ``<name>.corrupt-<timestamp>`` so the user can inspect it.
    """

    def __init__(self, path: Path, defaults: dict[str, Any], schema_version: int = SCHEMA_VERSION):
        self.path = Path(path)
        self.defaults = copy.deepcopy(defaults)
        self.schema_version = schema_version

    # -- loading ---------------------------------------------------------
    def load(self) -> dict[str, Any]:
        """Return the stored data merged over the defaults."""
        data = self._read()
        if data is None:
            result = copy.deepcopy(self.defaults)
            result["schema_version"] = self.schema_version
            return result
        merged = copy.deepcopy(self.defaults)
        _deep_merge(merged, data)
        merged["schema_version"] = self.schema_version
        return merged

    def _read(self) -> dict[str, Any] | None:
        if not self.path.exists():
            return None
        try:
            with self.path.open("r", encoding="utf-8") as handle:
                raw = json.load(handle)
        except (OSError, ValueError) as exc:
            log.warning("Could not read %s: %s", self.path, exc)
            self._quarantine()
            return None
        if not isinstance(raw, dict):
            log.warning("%s does not contain a JSON object; using defaults", self.path)
            self._quarantine()
            return None
        stored_version = raw.get("schema_version")
        if stored_version != self.schema_version:
            log.info(
                "Schema version %r in %s differs from %r; merging over defaults",
                stored_version,
                self.path,
                self.schema_version,
            )
        return raw

    def _quarantine(self) -> None:
        """Move a corrupt file aside instead of deleting the user's data."""
        stamp = time.strftime("%Y%m%d-%H%M%S")
        target = self.path.with_name(f"{self.path.name}.corrupt-{stamp}")
        try:
            self.path.replace(target)
            log.warning("Moved corrupt configuration to %s", target)
        except OSError as exc:  # pragma: no cover - unusual filesystem error
            log.warning("Could not move corrupt configuration aside: %s", exc)

    # -- saving ----------------------------------------------------------
    def save(self, data: dict[str, Any]) -> None:
        """Write ``data`` atomically, creating the directory if needed."""
        payload = copy.deepcopy(data)
        payload["schema_version"] = self.schema_version
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(
            prefix=f".{self.path.name}.", suffix=".tmp", dir=str(self.path.parent)
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, indent=2, ensure_ascii=False, sort_keys=False)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(tmp_name, self.path)
        except BaseException:
            with contextlib.suppress(OSError):
                os.unlink(tmp_name)
            raise


def _deep_merge(target: dict[str, Any], source: dict[str, Any]) -> None:
    """Merge ``source`` into ``target`` recursively, keeping target types."""
    for key, value in source.items():
        if key == "schema_version":
            continue
        current = target.get(key)
        if isinstance(current, dict) and isinstance(value, dict):
            _deep_merge(current, value)
        else:
            target[key] = value
