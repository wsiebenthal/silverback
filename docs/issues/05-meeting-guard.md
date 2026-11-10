# Meeting guard while Zoom, Meet, or Teams is screen sharing

Labels: `enhancement`, `privacy`

## Description

While Zoom, Google Meet, or Microsoft Teams is sharing the screen, hide the windows in the screen-share profile. A meeting that is not sharing does nothing. Meeting audio and video are not captured.

Roadmap: [Phase 12 — Meeting guard](https://github.com/wsiebenthal/silverback/blob/cursor/project-foundation-2eef/ROADMAP.md#phase-meeting-guard)

## Acceptance criteria

- Screen sharing is detected from local process or window signals on Windows, macOS, and Linux for Zoom, Meet, and Teams.
- Chosen windows hide only while sharing is active.
- When sharing stops, restore follows secure restore if that gate is on, otherwise the normal restore path.
- Joining a meeting without sharing does not hide windows.
- Tests inject a fake sharing signal and do not capture meeting content.
