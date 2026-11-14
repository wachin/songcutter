# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Washington
"""Project data model.

Times are stored in seconds as ``float``. The model never touches the source
files: a clip references a source path and an in/out range.
"""

from __future__ import annotations

from dataclasses import dataclass, field

VIDEO = "video"
AUDIO = "audio"


def format_timecode(seconds: float, fps: float) -> str:
    """Format as ``HH:MM:SS,FF`` (the current-time box format)."""
    seconds = max(0.0, float(seconds))
    total_frames = int(round(seconds * max(fps, 1.0)))
    frames_per_second = int(round(fps)) or 1
    frames = total_frames % frames_per_second
    total_seconds = total_frames // frames_per_second
    return f"{total_seconds // 3600:02d}:{total_seconds // 60 % 60:02d}:{total_seconds % 60:02d},{frames:02d}"


def format_clock(seconds: float) -> str:
    """Format as ``HH:MM:SS`` (ruler labels and durations)."""
    total = int(max(0.0, float(seconds)))
    return f"{total // 3600:02d}:{total // 60 % 60:02d}:{total % 60:02d}"


@dataclass
class Clip:
    """A reference to a range of a source file placed on a track."""

    id: str
    name: str
    start: float
    duration: float
    source: str = ""
    gain_db: float = 0.0
    fade_in: float = 0.0
    fade_out: float = 0.0
    muted: bool = False

    @property
    def end(self) -> float:
        return self.start + self.duration


@dataclass
class Track:
    kind: str
    name: str
    clips: list[Clip] = field(default_factory=list)
    locked: bool = False
    muted: bool = False
    hidden: bool = False

    def clip_at(self, time: float) -> Clip | None:
        for clip in self.clips:
            if clip.start <= time < clip.end:
                return clip
        return None


@dataclass
class Marker:
    time: float
    name: str


@dataclass
class Song:
    name: str
    start: float
    end: float
    enabled: bool = True

    @property
    def duration(self) -> float:
        return max(0.0, self.end - self.start)


@dataclass
class Project:
    name: str = "Untitled"
    profile_name: str = "HD 720p 30 fps"
    width: int = 1280
    height: int = 720
    fps: float = 30.0
    source_dir: str = ""
    tracks: list[Track] = field(default_factory=list)
    markers: list[Marker] = field(default_factory=list)
    songs: list[Song] = field(default_factory=list)

    def track(self, kind: str) -> Track | None:
        for track in self.tracks:
            if track.kind == kind:
                return track
        return None

    @property
    def duration(self) -> float:
        ends = [clip.end for track in self.tracks for clip in track.clips]
        return max(ends, default=0.0)

    @property
    def clip_count(self) -> int:
        return sum(len(track.clips) for track in self.tracks if track.kind == "video")

    @property
    def enabled_song_count(self) -> int:
        return sum(1 for song in self.songs if song.enabled)
