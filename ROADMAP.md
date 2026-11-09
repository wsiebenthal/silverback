# Roadmap

Silver Back is software-first. You can build and test every near-term phase with `silverback trigger` and `silverback listen --stdin`. No ESP32, no PIR, and no camera.

The repository today is the foundation: a simulated trigger, a rules file, minimize on Linux X11 (macOS and Windows minimize code is present and unverified here), an extension that can switch or close tabs when the popup sends a test message, a version-1 event protocol, and an ESP32 sketch that already compiles and waits for a later, optional phase.

The hour figures are engineering-scope estimates so a reader can see the size of the work. They are not a delivery schedule. The software phases below add up to about ninety hours, which is well over twenty. The phone phase and the optional hardware phases sit on top of that.

There is no camera phase. Silver Back does not open a webcam, take photos, record video, or detect people in images.

## Phase 0 — Foundation

Done in this repository.

- Monorepo layout, protocol spec, example event log, and rules file
- Desktop: parse, debounce, `trigger`, `listen --stdin`, minimize by window title
- Extension: MV3 skeleton, tab policy, popup test trigger, options page
- Desktop unit tests, an X11 integration test when a display is present, extension tests, CI that needs no hardware
- ESP32 sketch left in `firmware/` for the optional hardware phases. It compiles. It is not on the near-term path

## Phase 1 — Hide, close, focus, and restore

Scope: about 18 hours.

Test every action with `silverback trigger` and a `clear` line on stdin. No board.

- Implement `hide`, `close`, and `focus` next to the minimize path that exists now
- `focus` launches the configured safe app when it is not already running
- On `clear`, restore what this session minimized, hid, or closed, from a small session log
- Match process name as well as window title, and document the difference per OS
- macOS: if Accessibility permission is missing, name the toggle in the error
- Windows: actions work as the current user, with no administrator install
- Linux: keep the X11 `xdotool` path, and either add a Wayland backend or document that limit in the status table
- `close` refuses a match that is too broad, so a short string cannot quit a pile of unrelated windows
- Fake-backend unit tests for each action, plus one manual check on macOS, Windows, and Linux

## Phase 2 — Session rules you can rehearse from a log

Scope: about 10 hours.

- Occupancy: a second `approach` while a session is already open does not run the list again
- Cooldown and quiet hours in the rules file
- `clear` ends the session and runs restore from Phase 1
- Write a local log and replay it with `silverback listen --stdin`
- Tests feed NDJSON, including `docs/examples/session.ndjson`, and assert which rules ran

## Phase 3 — Rules list and settings UI

Scope: about 16 hours.

- A window that edits the ordered rules: type, match, enabled, safe app, tab patterns, debounce, quiet hours
- Add, remove, reorder, enable, and disable
- Validate with the same checks as `silverback check-config` before save
- Profiles, for example one for a lab bench and one for a desk
- Import and export the JSON file
- The CLI and the window read and write one file
- UI tests for the rules model, and a manual pass that changes a rule and runs `silverback trigger`

## Phase 4 — Desktop to the browser extension

Scope: about 14 hours.

- A native messaging host the desktop app installs and talks to
- Chrome and Firefox host manifests, with the install path written down
- `silverback trigger` delivers the `privacy_trigger` message already described in [docs/protocol.md](docs/protocol.md)
- The desktop rules file is the source of truth for tab patterns; the extension mirrors it
- Policy for pinned tabs and for the last open window
- A test that speaks the native-messaging length-prefixed frames on a pipe, with no browser
- Load-unpacked steps in `extension/README.md` stay accurate

## Phase 5 — Hotkey and tray or menu bar

Scope: about 12 hours.

- A global hotkey runs the same path as `silverback trigger`
- A second chord, or a menu item, sends `clear` and runs restore
- Windows and Linux: a tray icon. macOS: a menu-bar item. Actions: Trigger now, Restore, Open settings, Pause, Quit
- Pause suppresses rules until it is turned off
- Tests cover the command routing with a fake backend. The global hook itself is a manual check per OS

## Phase 6 — Packaging and installers

Scope: about 14 hours.

- A per-user Windows install that does not ask for an administrator
- A macOS app bundle that can explain the Accessibility prompt
- Linux: a `pipx` install or a simple package, documented either way
- An extension zip attached to the release
- Optional start at login
- One version number across the desktop package, the extension, and the GitHub release
- A clean machine can install and run the simulated trigger from the installed command

## Phase 7 — Tests and the user guide

Scope: about 10 hours.

- CI stays free of hardware and free of a display for the unit tests. The live window test stays opt-in
- A user guide that starts from an empty checkout: install, write one rule, run `silverback trigger`, see the window change, send `clear`, see restore
- Permission prompts on macOS and Windows written as steps, not as a guess
- Any new desktop or extension message is versioned in the protocol doc in the same change as the code and the tests

The seven software phases are the near-term product. They are about ninety hours of work, and none of them need a sensor.

## Phase 8 — Phone as a trigger

Scope: about 14 hours.

Later software, still with no board and no camera. The phone sends the same version-1 JSON the desktop already understands. It does not open the camera, take photos, or run person detection.

- Wi-Fi: the phone and the computer on one network. A small sender (a page with Approach and Clear buttons, or a tiny companion) posts those two events
- BLE: the phone notifies, the desktop subscribes, and pairing is written down before the code ships
- The desktop runs the same debounce and the same rules it runs for `listen --stdin`
- Tests use a local socket fixture and a recorded notify payload. A manual check is one button press on a phone and one window changing on the computer

## Hardware (optional)

Do this only when an ESP32 and a sensor are on the desk. The software product does not wait on it. The `firmware/` folder stays as the sketch for these phases.

### H1 — ESP32 on a bench

Scope: about 12 hours.

- Flash `esp32dev`, capture a real session, and check it against [docs/protocol.md](docs/protocol.md)
- Measure the PIR module's OUT pin and record the voltage next to the wiring notes
- Suppress or flag edges during the sensor's first minute of warmup
- Status LED patterns for booting, armed, triggered, and a stuck pin
- A host-testable debounce state machine, shared with the sketch instead of only living in `loop()`
- A time-of-flight alternative (VL53L0X on I2C) that emits the same `presence` events from a distance threshold
- PlatformIO compile on CI for `esp32dev`

### H2 — Battery and power

Scope: about 12 hours.

- Pack voltage on an ADC pin through a divider, and a `battery` event added to the protocol on purpose
- Deep sleep between edges, with the PIR as the wake source, including the sensor's warmup after power is removed
- A written current budget: asleep, advertising, and connected
- What the firmware does when USB power appears while a pack is attached
- A low-battery state the desktop can show

### H3 — Enclosure and the bill of materials

Scope: about 12 hours.

- A printable enclosure: PIR aperture, USB strain relief, and a flat base
- Mounts for a monitor top, a cubicle rail, and the outside of a door frame
- Fastener list, print settings, and an assembly sequence
- CAD source in the repo, not only a mesh
- Update the README parts table from "planned reference design" to "what was built" only after a print exists

## How to pick up a phase

Software phases land on their own and are tested with `silverback trigger` or a stdin log. The phone phase is software too, and it stays free of camera input. Hardware phases are optional and start only with a board in hand. Keep the status table in [README.md](README.md) honest when a stub becomes a working path. Update the protocol doc in the same change as any new event field.
