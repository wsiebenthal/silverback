# Tamper resistance: signed config and a local alert

Labels: `enhancement`, `security`

## Description

Encrypt and sign the rules file. Refuse a file whose signature does not match. If Silver Back is quit, or the rules change outside the app, show a local alert. Nothing is sent to a server.

Roadmap: [Phase 15 — Tamper resistance](https://github.com/wsiebenthal/silverback/blob/cursor/project-foundation-2eef/ROADMAP.md#phase-tamper-resistance)

## Acceptance criteria

- The rules file is encrypted at rest. The key is in the OS keychain or credential manager.
- A bad signature is rejected on load.
- Quitting the process, or editing the rules outside the app, raises a local alert the user can see.
- A test that flips a byte expects rejection. A test simulates the quit alert. There is no remote telemetry.
