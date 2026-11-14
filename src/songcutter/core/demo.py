# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Washington
"""Sample project used by the Phase 1 shell.

This is placeholder content for the static layout: three camcorder files of
17:04 each, placed back to back, with three songs. Real file discovery arrives
in Phase 2 and the real project model in Phase 4/7.
"""

from __future__ import annotations

from pathlib import Path

from songcutter.core.model import AUDIO, VIDEO, Clip, Marker, Project, Song, Track

CLIP_SECONDS = 17 * 60 + 4
FILE_NAMES = (
    "HDV_0264 Predica Hno Landy.MP4",
    "HDV_0265 Predica Hno Landy.MP4",
    "HDV_0266 Predica Hno Landy.MP4",
)


def demo_project() -> Project:
    video_clips: list[Clip] = []
    audio_clips: list[Clip] = []
    markers: list[Marker] = []
    songs: list[Song] = []
    for index, name in enumerate(FILE_NAMES):
        start = index * CLIP_SECONDS
        video_clips.append(
            Clip(id=f"v{index + 1}", name=name, start=start, duration=CLIP_SECONDS, source=name)
        )
        audio_clips.append(
            Clip(id=f"a{index + 1}", name=name, start=start, duration=CLIP_SECONDS, source=name)
        )
        markers.append(Marker(time=start, name=f"Song {index + 1}"))
        songs.append(
            Song(name=f"Song {index + 1}", start=start, end=start + CLIP_SECONDS, enabled=True)
        )

    return Project(
        name="Untitled",
        profile_name="HD 720p 30 fps",
        width=1280,
        height=720,
        fps=30.0,
        source_dir=str(Path.home() / "Videos" / "Culto 2026-11-08"),
        tracks=[
            Track(kind=VIDEO, name="Video", clips=video_clips),
            Track(kind=AUDIO, name="Audio", clips=audio_clips),
        ],
        markers=markers,
        songs=songs,
    )
