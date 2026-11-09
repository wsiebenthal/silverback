# Clipboard guard: clear the clipboard on trigger

Labels: `enhancement`, `privacy`

## Description

A trigger clears the OS clipboard. The clipboard text is not stored, logged, or put back later.

Roadmap: [Phase 13 — Clipboard guard](https://github.com/wsiebenthal/silverback/blob/cursor/project-foundation-2eef/ROADMAP.md#phase-clipboard-guard)

## Acceptance criteria

- Windows, macOS, and Linux clipboards are cleared when the rule runs.
- Clipboard contents never appear in the log, the config, or the stats view.
- The previous clipboard value is not restored.
- A test with a fake clipboard shows it was cleared and that its text was not written anywhere.
