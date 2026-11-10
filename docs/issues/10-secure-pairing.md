# Secure pairing so nearby devices cannot forge triggers

Labels: `enhancement`, `security`

## Description

Pair a phone or sensor with the desktop using a short code. Trigger messages are signed and encrypted, and a replay is rejected. This is defensive only: it does not probe or attack other devices. Pairing does not use a camera.

Roadmap: [Phase 17 — Secure pairing](https://github.com/wsiebenthal/silverback/blob/cursor/project-foundation-2eef/ROADMAP.md#phase-secure-pairing)

## Acceptance criteria

- Pairing is a short code shown on the desktop and entered on the phone or sensor.
- A trigger is accepted only when it is signed and encrypted to the paired key.
- A replayed counter is rejected.
- An unpaired message or a bad signature is ignored and counted locally.
- If heartbeats from a paired device stop while the guard is armed, the desktop shows a local alert.
- Tests use fixture messages for valid, replayed, unsigned, and stale cases, with no radio hardware.
