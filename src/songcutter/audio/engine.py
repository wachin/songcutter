# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Washington
"""Playback engine built on QAudioSink with a software mixer.

Planned for Phase 4. Applies gain, fades and mute above 0 dB, mixes the audio
clips of the timeline, and provides the clock that the video preview follows.
"""
