# Roadmap

The repository today is the foundation: a USB-serial PIR sketch, a desktop listener with a simulated trigger and a working minimize action, an extension that can switch or close tabs when something inside the browser messages it, and the version-1 event protocol.

The phases below are the remaining product. The hour figures are engineering-scope estimates so a reader can see the size of the work. They are not a delivery schedule. Added up, the remaining phases are well over twenty hours, and a careful pass at the hardware and the three operating systems is closer to a hundred.

## Phase 0 — Foundation

Done in this repository.

- Monorepo layout, protocol spec, example session, and config format
- ESP32 sketch: digital pin, debounce, `hello` / `presence` / `heartbeat` on USB serial
- Desktop: parse, debounce, `trigger`, `listen --stdin`, `listen` on a serial port, minimize by window title
- Extension: MV3 skeleton, tab policy, popup test trigger, options page
- Desktop unit tests, an X11 integration test when a display is present, extension tests, CI

## Phase 1 — Firmware you can trust on a bench

Scope: about 12 hours.

- Flash `esp32dev`, capture a real session, and check it against [docs/protocol.md](docs/protocol.md)
- Measure HC-SR501 OUT with a meter and record the voltage next to the wiring notes
- Warmup window: suppress or flag edges for the sensor's first minute
- Status LED patterns for booting, armed, triggered, and a stuck pin
- Host-testable debounce state machine, shared with the sketch instead of only living inside `loop()`
- Time-of-flight alternative (VL53L0X on I2C) that emits the same `presence` events from a distance threshold
- PlatformIO compile on CI for `esp32dev`

## Phase 2 — Leave the USB cable

Scope: about 16 hours.

- BLE GATT service: notify the version-1 JSON line, or a framed equivalent written into the protocol doc first
- Bonding and a desktop allow-list of sensor identities
- Wi-Fi station mode and a small socket or websocket the desktop dials
- Reconnect, heartbeat timeout, and a visible "sensor offline" state
- Rule for which transport is live when USB is plugged in and when it is not
- Desktop client for the chosen wireless transport, with a replay test that uses the same action path as serial

## Phase 3 — Battery and power

Scope: about 12 hours.

- Pack voltage on an ADC pin through a divider, and a `battery` event added to the protocol on purpose
- Deep sleep between edges, with the PIR as the wake source, including the sensor's own warmup after power is removed
- A written current budget: asleep, advertising, and connected
- Charge-while-running behavior when VBUS appears, and what the firmware does during that handoff
- Low-battery policy the desktop can show

## Phase 4 — Desktop actions on each operating system

Scope: about 16 hours.

- Implement `hide`, `close`, and `focus` (launch the safe app when it is not running), next to the minimize path that exists now
- Remember what was minimized and restore it on `clear`
- Match process name as well as window title, and document the difference per OS
- macOS: detect a missing Accessibility permission and tell the user which toggle to enable
- Windows: per-user startup without an administrator install
- Linux: keep the X11 `xdotool` path, and add a Wayland backend or a documented limit
- One manual script per OS plus the fake-backend tests that already guard the planner

## Phase 5 — The extension as a real companion

Scope: about 12 hours.

- Native messaging host installed by the desktop app, speaking the browser message already documented in the protocol
- Chrome and Firefox host-manifest install paths
- One config: the desktop file is the source of truth and the extension mirrors the tab patterns
- Policy for pinned tabs and for the last open window
- Packed zip builds and a load-unpacked document that stays accurate
- More cases around multi-window sessions

## Phase 6 — Config UI

Scope: about 12 hours.

- A desktop window to edit actions, debounce, the serial port, and the extension patterns
- Validate before save, using the same checks as `check-config`
- Profiles (a lab bench and a cubicle, for example)
- Import and export of the JSON file
- A tray or menu-bar presence so `listen` is not only a foreground terminal

## Phase 7 — False triggers

Scope: about 8 hours.

- Firmware hold time: the pin must stay active, not just be stable for 200 ms
- Desktop occupancy: ignore a new approach while the sensor is already occupied, and arm again on `clear`
- Optional second sample or a time-of-flight range gate so a hallway passer does not fire the desk
- Quiet hours
- A local log that `silverback listen --stdin` can replay

## Phase 8 — Enclosure and mounting

Scope: about 12 hours.

- A printable enclosure: PIR aperture, USB strain relief, and a flat base
- Mounts for a monitor top, a cubicle rail, and the outside of a door frame
- Fastener list, print settings, and an assembly sequence with photos
- CAD source in the repo (the model, not only a mesh)
- Move the bill of materials from "reference design" to "what was actually built" only after a print exists

## Phase 9 — Tests, docs, and releases

Scope: about 10 hours.

- A hardware checklist a contributor can run without guessing pin numbers
- CI matrix for the desktop tests, with the live window test staying opt-in where there is no display
- Protocol changes versioned in [docs/protocol.md](docs/protocol.md) in the same change as the firmware and the parser
- GitHub releases that attach a firmware binary, a desktop package, and an extension zip
- A user guide that starts from an empty desk and ends with one real trigger

## How to pick up a phase

Each phase can land as its own change. Keep the status table in [README.md](README.md) honest when a stub becomes a working path. Update the protocol doc in the same change as any new event field.
