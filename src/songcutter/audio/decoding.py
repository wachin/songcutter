# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Washington
"""Decode a source file to PCM with FFmpeg and cache it on disk.

Planned for Phase 4/5. The cache key includes the source path, size, modified
time and the target sample format, so a changed file is decoded again.
"""
