# Screen privacy actions: blur, decoy workspace, mute, and hide notifications

Labels: `enhancement`, `privacy`

## Description

On a trigger, Silver Back should be able to cover the screen, switch to a decoy workspace, mute audio and pause media, and dismiss the user's own notification popups. Nothing is screenshotted or saved. Notification text is not copied into the log.

Roadmap: [Phase 8 — Screen privacy actions](https://github.com/wsiebenthal/silverback/blob/cursor/project-foundation-2eef/ROADMAP.md#phase-screen-privacy-actions)

## Acceptance criteria

- A rule can dim or blur the screen with an overlay Silver Back draws, on Windows, macOS, and Linux, and the user can dismiss that overlay.
- A rule can switch to an empty or prepared virtual desktop and switch back.
- A rule can mute system audio and pause the active media session without recording audio.
- A rule can dismiss or hide the user's notification popups without storing their text.
- `silverback trigger` runs the new rule types. `clear` undoes them only through the restore path.
- Tests cover each action with a fake backend.
