# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Washington
"""Tests for the project data model."""

from __future__ import annotations

from songcutter.core.demo import CLIP_SECONDS, demo_project
from songcutter.core.model import Clip, Marker, Project, Song, Track, format_clock, format_timecode


def test_timecode_formats():
    assert format_timecode(0, 30) == "00:00:00,00"
    assert format_timecode(204.233, 30) == "00:03:24,07"
    assert format_timecode(3661.48, 25) == "01:01:01,12"
    assert format_clock(0) == "00:00:00"
    assert format_clock(256) == "00:04:16"
    assert format_clock(3661) == "01:01:01"


def test_clip_end_and_track_lookup():
    clip = Clip(id="a", name="a.mp4", start=10.0, duration=5.0)
    assert clip.end == 15.0
    track = Track(kind="video", name="Video", clips=[clip])
    assert track.clip_at(12.0) is clip
    assert track.clip_at(15.0) is None
    assert track.clip_at(9.0) is None


def test_demo_project_shape():
    project = demo_project()
    assert project.clip_count == 3
    assert project.enabled_song_count == 3
    assert project.duration == CLIP_SECONDS * 3
    assert project.track("video") is not None
    assert project.track("audio") is not None
    assert len(project.markers) == 3
    assert all(song.end > song.start for song in project.songs)


def test_project_duration_uses_latest_clip():
    project = Project(
        tracks=[
            Track(kind="video", name="Video", clips=[Clip("v", "v", 0.0, 10.0)]),
            Track(kind="audio", name="Audio", clips=[Clip("a", "a", 20.0, 5.0)]),
        ]
    )
    assert project.duration == 25.0


def test_empty_project():
    project = Project()
    assert project.duration == 0.0
    assert project.clip_count == 0
    assert project.track("video") is None
    assert project.markers == []
    assert project.songs == []
    assert Song("x", 0, 0).duration == 0.0
    assert Marker(1.0, "m").name == "m"
