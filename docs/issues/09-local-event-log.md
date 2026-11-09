# Local-only event log and stats view

Labels: `enhancement`, `privacy`

## Description

A log on this computer of when a rule ran and whether it worked, plus a small stats view. No images, window titles, URLs, clipboard text, notification text, or names.

Roadmap: [Phase 16 — Local-only event log and stats](https://github.com/wsiebenthal/silverback/blob/cursor/project-foundation-2eef/ROADMAP.md#phase-local-event-log)

## Acceptance criteria

- Each record stores time, rule id, action type, and success or failure.
- Window titles, URLs, clipboard contents, notification text, images, and names are not written.
- The stats view shows counts by day and by action type.
- The user can delete the log from that view.
- A test fails if a forbidden field appears in the written record.
