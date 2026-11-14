# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Washington
"""Multi-resolution peak pyramid for the timeline waveform.

Planned for Phase 5. Peaks are computed per channel in a background thread and
stored in the cache directory; the timeline draws only the visible range.
"""
