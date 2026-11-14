# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Washington
"""Tests for timeline zoom helpers and painting."""

from __future__ import annotations

from songcutter.core.demo import demo_project
from songcutter.ui.timeline import (
    SLIDER_MAX,
    TimelineView,
    pps_to_slider,
    slider_to_pps,
)


def test_zoom_mapping_is_monotonic():
    values = [slider_to_pps(value) for value in range(0, SLIDER_MAX + 1, 50)]
    assert values == sorted(values)
    assert slider_to_pps(0) < slider_to_pps(SLIDER_MAX)


def test_zoom_mapping_roundtrip():
    for value in (0, 100, 250, 500, 750, 1000):
        assert abs(pps_to_slider(slider_to_pps(value)) - value) <= 1


def test_fit_shows_whole_project(qapp):
    project = demo_project()
    view = TimelineView(project)
    view.resize(1000, 300)
    view.show()
    view.fit()
    assert view.pixels_per_second > 0
    assert view.visible_seconds() >= project.duration * 0.99


def test_view_paints_without_error(qapp):
    view = TimelineView(demo_project())
    view.resize(900, 320)
    view.show()
    view.fit()
    pixmap = view.grab()
    assert not pixmap.isNull()
    assert pixmap.width() > 0


def test_playhead_is_clamped(qapp):
    view = TimelineView(demo_project())
    view.resize(600, 300)
    view.set_playhead(-50)
    assert view.playhead == 0
    view.set_playhead(10_000_000)
    assert view.playhead == view.duration
