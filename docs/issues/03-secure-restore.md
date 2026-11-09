# Secure restore after a PIN, Touch ID, Windows Hello, or a hotkey

Labels: `enhancement`, `security`

## Description

Putting windows and tabs back should wait for the user. A `clear` event alone does not restore. Unlock is a local PIN, Touch ID, Windows Hello, or a hotkey the user chose.

Roadmap: [Phase 10 — Secure restore](https://github.com/wsiebenthal/silverback/blob/cursor/project-foundation-2eef/ROADMAP.md#phase-secure-restore)

## Acceptance criteria

- The prior window and tab list is held until authentication succeeds.
- The PIN is stored only as a salted hash and never appears in the log.
- macOS can use Touch ID and Windows can use Windows Hello through the OS APIs.
- A user-chosen hotkey unlocks without a PIN.
- The held state is encrypted at rest with a key in the OS keychain or credential manager.
- Tests cover a wrong PIN, a correct PIN, and the hotkey path with a fake authenticator.
