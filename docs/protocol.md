# Sensor event protocol

Version 1. This is the event the desktop app acts on. `silverback trigger` synthesizes an approach, and `silverback listen --stdin` reads the same lines from a file, so the app can be built with no sensor attached. The optional ESP32 sketch in `firmware/` emits these lines on USB serial when a board is available. The sample in [examples/session.ndjson](examples/session.ndjson) is a valid session.

## Transport

USB serial, 115200 baud, 8 data bits, no parity, 1 stop bit. Each event is one UTF-8 JSON object followed by a newline (`\n` or `\r\n`). There is no binary frame in version 1.

A receiver may reject a line longer than 1024 characters. The firmware lines are short and contain only fixed tokens plus decimal integers, so they stay well under that limit.

BLE and Wi-Fi are not part of this version. A later revision will choose a frame (the same JSON line inside a notify, or a length prefix). Clients should wait for that revision instead of guessing a frame.

## Object

| Field | Required | Meaning |
| --- | --- | --- |
| `v` | yes | Integer `1`. Booleans and strings are rejected. |
| `type` | yes | `hello`, `presence`, or `heartbeat`. |
| `state` | on `presence` | `approach` or `clear`. Rejected on other types. |
| `sensor` | no | Non-empty string. The current sketch sends `pir`. |
| `transport` | no | Non-empty string. The current sketch sends `usb-serial`. |
| `fw` | no | Non-empty firmware version string. |
| `seq` | no | Integer ≥ 0. The sketch counts every emitted line, including `hello`, and starts at 0 after reset. |
| `uptime_ms` | no | Integer ≥ 0. `millis()` on the sketch. |

Unknown fields are ignored so a later firmware can add keys without breaking an older desktop build. A JSON `null` on an optional field is treated as absent. `seq` and `uptime_ms` have to be integers; a float or a numeric string is rejected.

## What each event means

`hello` is written once from `setup()`. The desktop logs the firmware version and transport. It does not run actions.

`presence` with `state` `approach` means the pin has settled at the active level (HIGH by default) for the firmware debounce, which is 200 ms. The desktop runs the enabled actions, then ignores further `approach` lines until `debounce_ms` has passed on the computer's clock (2000 ms in the example config). A `clear` does not reset that window. The one-shot command `silverback trigger` does not consult the debouncer; it always runs the actions once.

`presence` with `state` `clear` means the pin has settled away from the active level. The desktop logs the line. Putting windows back is not implemented.

`heartbeat` is written every 30 seconds. The desktop logs it. It does not include whether someone is currently present, so a listener that attaches in the middle of an occupancy waits for the next edge. Carrying that state on the heartbeat is future work.

`seq` does not have to be gapless for the desktop to accept a line. A gap is a sign that a line was dropped.

## Desktop behavior that is part of the contract

| Input | Desktop result in 0.1.0 |
| --- | --- |
| `hello` | Log `hello fw=… transport=…`. |
| `presence` / `approach`, outside the debounce window | Run enabled actions. |
| `presence` / `approach`, inside the debounce window | Log `approach suppressed by debounce`. |
| `presence` / `clear` | Log that restore is not implemented. |
| `heartbeat` | Log `heartbeat`. |
| Empty line | Skip. |
| Anything the parser rejects | Log `ignored: …` and keep reading. |

`silverback listen` stays up when an action fails (a window title that is not open, for example). `silverback trigger` exits `1` when an implemented action fails, and exits `2` when the config or the serial port is unusable. Stub actions (`hide`, `close`, `focus`) are reported and do not by themselves change the exit code.

## Browser message

This is separate from the sensor line. The extension service worker accepts a runtime message:

```json
{ "type": "privacy_trigger", "state": "approach" }
```

`state` other than `approach` is acknowledged and ignored. The popup **Send test trigger** button sends this message. The desktop app does not send it yet. When native messaging exists, the host should deliver this same object. The sensor NDJSON stays on the serial port; the browser message is the desktop-to-extension shape.

## Worked example

```json
{"v":1,"type":"hello","sensor":"pir","transport":"usb-serial","fw":"0.1.0","seq":0,"uptime_ms":20}
{"v":1,"type":"presence","state":"approach","sensor":"pir","transport":"usb-serial","fw":"0.1.0","seq":1,"uptime_ms":800}
{"v":1,"type":"presence","state":"clear","sensor":"pir","transport":"usb-serial","fw":"0.1.0","seq":2,"uptime_ms":5400}
{"v":1,"type":"heartbeat","sensor":"pir","transport":"usb-serial","fw":"0.1.0","seq":3,"uptime_ms":30020}
```

Replay the longer sample, which includes a second approach that the desktop debounce drops:

```bash
python -m silverback listen --stdin --dry-run \
  --config desktop/silverback.config.example.json \
  < docs/examples/session.ndjson
```
