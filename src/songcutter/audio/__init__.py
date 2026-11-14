# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Washington
"""Audio subsystem.

Planned modules:

* ``decoding`` — decode a source to PCM with FFmpeg, cached on disk
* ``waveform`` — multi-resolution peak pyramid and cache
* ``effects`` — gain, fades, mute and the effect stack
* ``noise`` — noisereduce and SoX engines, noise-profile cache
* ``engine`` — QAudioSink playback engine with a software mixer

Phase 1 contains no audio code yet; the shell draws a placeholder waveform.
"""
