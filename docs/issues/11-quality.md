# Quality: cross-platform tests, signed installers, auto-update, accessibility

Labels: `enhancement`, `security`

## Description

Make the desktop build something you can install and trust on Windows, macOS, and Linux: tests on each OS, signed installers, updates that check a signature, and a settings UI that can be used from the keyboard.

Roadmap: [Phase 18 — Quality](https://github.com/wsiebenthal/silverback/blob/cursor/project-foundation-2eef/ROADMAP.md#phase-quality)

## Acceptance criteria

- Unit tests run on every push. OS-specific tests are opt-in on Windows, macOS, and Linux.
- Installers for those three desktops are signed.
- Auto-update refuses a build whose signature does not check.
- The settings window and the tray or menu are keyboard operable, controls have names, and the UI Silver Back draws meets WCAG AA contrast.
- The user guide lists the commands that verify a release.
