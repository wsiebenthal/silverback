# Profiles that switch by time of day or current Wi-Fi name

Labels: `enhancement`, `privacy`

## Description

Rule sets named office, home, cafe, and screen-share (and any name the user adds). The active profile can follow the local time of day or the SSID of the network this computer is joined to. Silver Back reads that one SSID. It does not scan nearby people or devices.

Roadmap: [Phase 11 — Profiles](https://github.com/wsiebenthal/silverback/blob/cursor/project-foundation-2eef/ROADMAP.md#phase-profiles)

## Acceptance criteria

- The four named profiles exist and the user can add more.
- A time-of-day rule selects a profile.
- The current associated SSID selects a profile. Nearby networks are not scanned, and network names are not kept as a history beyond the profile that was chosen.
- The CLI can override the active profile. The tray or menu bar can too, once that control exists.
- Tests use a fake clock and a fake network reader.
