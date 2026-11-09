# Auto-lock the session if a trigger stays, or if you do not return

Labels: `enhancement`, `security`

## Description

Lock the operating system when a trigger stays active past a set time, or when a trigger clears and the user does not come back within a set time. The app does not store account passwords.

Roadmap: [Phase 9 — Auto-lock](https://github.com/wsiebenthal/silverback/blob/cursor/project-foundation-2eef/ROADMAP.md#phase-auto-lock)

## Acceptance criteria

- Windows, macOS, and Linux each have a lock call behind one interface.
- A configured "trigger stays active" timer locks the session when it elapses.
- A configured "did not return" timer starts when the trigger clears and locks if the user does not answer with a hotkey or another explicit action.
- Either timer can be turned off in the rules file.
- Tests use a fake clock and a fake lock function and do not touch a real login session.
