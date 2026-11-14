# Keyboard shortcuts

Defaults follow Kdenlive where it makes sense. Rebind any action in
**View → Keyboard Shortcuts…**. Changes are saved to `shortcuts.json` and
survive a restart. A shortcut already used by another action is rejected with
the other action's name.

Status: **active** = works in the current phase; **registered** = the action
exists in the manager and is listed in the dialog, but is disabled until its
phase implements the feature.

## Playback

| Action id | Action | Default | Priority | Status |
| --- | --- | --- | --- | --- |
| `playback.play_stop` | Play / Stop | Space | Must | Registered (Phase 3) |
| `playback.pause` | Pause | K | Should | Registered (Phase 3) |
| `playback.forward` | Forward (cycles speeds) | L | Should | Registered (Phase 3) |
| `playback.rewind` | Rewind | J | Should | Registered (Phase 3) |
| `playback.frame_forward` | Forward one frame | Right | Must | Registered (Phase 3) |
| `playback.frame_back` | Back one frame | Left | Must | Registered (Phase 3) |
| `playback.second_forward` | Forward one second | Shift+Right | Must | Registered (Phase 3) |
| `playback.second_back` | Back one second | Shift+Left | Must | Registered (Phase 3) |
| `playback.prev_snap` | Previous snap point | Alt+Left | Should | Registered (Phase 4) |
| `playback.next_snap` | Next snap point | Alt+Right | Should | Registered (Phase 4) |
| `playback.prev_marker` | Previous marker | Ctrl+Left | Must | Registered (Phase 4) |
| `playback.next_marker` | Next marker | Ctrl+Right | Must | Registered (Phase 4) |
| `playback.clip_start` | Clip start | Home | Should | Registered (Phase 4) |
| `playback.clip_end` | Clip end | End | Should | Registered (Phase 4) |
| `playback.project_start` | Project start | Ctrl+Home | Must | Registered (Phase 4) |
| `playback.project_end` | Project end | Ctrl+End | Must | Registered (Phase 4) |
| `playback.align_playhead` | Align playhead to mouse | P | Should | Registered (Phase 4) |
| `playback.play_zone` | Play zone | Ctrl+Space | Should | Registered (Phase 4) |
| `playback.loop_zone` | Loop zone | Ctrl+Shift+Space | Should | Registered (Phase 4) |

## Zone

| Action id | Action | Default | Priority | Status |
| --- | --- | --- | --- | --- |
| `zone.set_in` | Set zone in | I | Must | Registered (Phase 4) |
| `zone.set_out` | Set zone out | O | Must | Registered (Phase 4) |
| `zone.go_start` | Go to zone start | Shift+I | Should | Registered (Phase 4) |
| `zone.go_end` | Go to zone end | Shift+O | Should | Registered (Phase 4) |

## Tools

| Action id | Action | Default | Priority | Status |
| --- | --- | --- | --- | --- |
| `tool.selection` | Selection tool | S | Must | **Active** (Phase 1, toggle) |
| `tool.razor` | Razor tool | X | Must | **Active** (Phase 1, toggle) |
| `tool.spacer` | Spacer tool | M | Must | **Active** (Phase 1, toggle) |
| `tool.escape` | Back to selection tool | Esc | Must | **Active** (Phase 1) |

## Editing

| Action id | Action | Default | Priority | Status |
| --- | --- | --- | --- | --- |
| `edit.cut` | Cut clip at playhead | Shift+R | Must | Registered (Phase 6) |
| `edit.cut_all` | Cut all clips at playhead | Ctrl+Shift+R | Must | Registered (Phase 6) |
| `edit.trim_start` | Trim clip start to playhead | ( | Should | Registered (Phase 6) |
| `edit.trim_end` | Trim clip end to playhead | ) | Should | Registered (Phase 6) |
| `edit.delete` | Delete | Del | Must | Registered (Phase 6) |
| `edit.extract` | Extract (delete and close the gap) | Shift+Del | Must | Registered (Phase 6) |
| `edit.lift` | Lift timeline zone | Z | Should | Registered (Phase 6) |
| `edit.extract_zone` | Extract timeline zone | Shift+X | Should | Registered (Phase 6) |
| `edit.group` | Group | Ctrl+G | Must | Registered (Phase 6) |
| `edit.ungroup` | Ungroup | Ctrl+Shift+G | Must | Registered (Phase 6) |
| `edit.select_all` | Select all | Ctrl+A | Must | Registered (Phase 6) |
| `edit.undo` | Undo | Ctrl+Z | Must | Registered (Phase 4) |
| `edit.redo` | Redo | Ctrl+Shift+Z | Must | Registered (Phase 4) |
| `edit.copy` | Copy | Ctrl+C | Should | Registered (Phase 6) |
| `edit.paste` | Paste | Ctrl+V | Should | Registered (Phase 6) |
| `edit.duplicate` | Duplicate | Ctrl+D | Should | Registered (Phase 6) |

## Markers

| Action id | Action | Default | Priority | Status |
| --- | --- | --- | --- | --- |
| `marker.add` | Add / remove marker at playhead | G | Must | Registered (Phase 4) |

## Zoom

| Action id | Action | Default | Priority | Status |
| --- | --- | --- | --- | --- |
| `view.zoom_in` | Zoom in | Ctrl+= or Ctrl++ | Must | **Active** (Phase 1, display zoom) |
| `view.zoom_out` | Zoom out | Ctrl+- | Must | **Active** (Phase 1, display zoom) |

## Tracks

| Action id | Action | Default | Priority | Status |
| --- | --- | --- | --- | --- |
| `track.lock` | Lock / unlock track | Shift+L | Should | Registered (Phase 4) |
| `track.mute` | Mute / hide track | Ctrl+Shift+H | Should | Registered (Phase 4) |

## File

| Action id | Action | Default | Priority | Status |
| --- | --- | --- | --- | --- |
| `file.new` | New project | Ctrl+N | — | Registered (Phase 7) |
| `file.open` | Open project | Ctrl+O | Must | Registered (Phase 7) |
| `file.save` | Save project | Ctrl+S | Must | Registered (Phase 7) |
| `file.save_as` | Save project as | Ctrl+Shift+S | Must | Registered (Phase 7) |
| `file.process` | Process videos | Ctrl+Return | Must | Enabled now; shows a Phase 7 placeholder |
| `file.quit` | Quit | Ctrl+Q | — | **Active** (Phase 1) |

## View and help

| Action id | Action | Default | Priority | Status |
| --- | --- | --- | --- | --- |
| `view.toggle_menu` | Show / hide menu bar | Ctrl+M | Must | **Active** (Phase 1) |
| `view.fullscreen` | Fullscreen | F11 | Should | **Active** (Phase 1, whole window) |
| `view.shortcuts` | Keyboard shortcuts dialog | — | — | **Active** (Phase 1) |
| `help.about` | About SongCutter | — | — | **Active** (Phase 1) |
| `help.about_qt` | About Qt | — | — | **Active** (Phase 1) |

## Mouse and wheel gestures (not QActions)

| Gesture | Behaviour | Status |
| --- | --- | --- |
| Click ruler or lane | Move the playhead | **Active** (Phase 1) |
| Ctrl+MouseWheel over the timeline | Zoom around the mouse | **Active** (Phase 1, display zoom) |
| MouseWheel over the timeline | Scroll horizontally | **Active** (Phase 1) |
| Shift+MouseWheel | Scroll vertically | Registered (Phase 4) |
| Ctrl+drag / middle-button drag | Pan | Registered (Phase 4) |
| Shift+click | Add to selection | Registered (Phase 6) |

## Notes

- On macOS, Qt maps Ctrl to Cmd automatically.
- Single-letter shortcuts do not fire while typing in a text field (Qt's
  `ShortcutOverride` handling).
- Clearing a shortcut in the dialog stores an explicit empty list, so it stays
  cleared after a restart; **Reset** restores the default.
