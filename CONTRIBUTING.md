# Contributing

Silver Back is maintained by Wesley Siebenthal. Issues and pull requests are welcome, especially slices of [ROADMAP.md](ROADMAP.md).

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e "./desktop[dev]"
make test
```

`make test` runs the desktop pytest suite and the extension's node tests. The X11 minimize test runs only when `DISPLAY`, `xdotool`, `xmessage`, and `xprop` are present. CI on GitHub Actions does not have a display, so that test is skipped there and the unit tests still run.

The near-term work is the software phases in [ROADMAP.md](ROADMAP.md). Test those with `silverback trigger` and `listen --stdin`. The ESP32 sketch is optional and later. Building it needs [PlatformIO](https://platformio.org/):

```bash
cd firmware
pio run -e esp32dev
```

## Layout

| Path | What changes belong there |
| --- | --- |
| `firmware/` | Sensor sketch and board config |
| `desktop/` | Parser, config, actions, serial listen, CLI |
| `extension/` | Tab policy and the MV3 shell |
| `docs/protocol.md` | The event contract |

## Protocol changes

A new field or event type updates three places in one change: `docs/protocol.md`, the firmware sketch, and `desktop/silverback/protocol.py`, plus a line in `docs/examples/` and a parser test. Receivers ignore unknown fields on purpose, so adding an optional key is compatible. Changing the meaning of an existing key needs a version bump.

## Desktop actions

`minimize` is implemented. `hide`, `close`, and `focus` return an explicit stub result. When you implement one, switch it from the stub set to the implemented set in `desktop/silverback/config.py`, add a fake-backend test, and say in the README which operating systems you actually ran.

## Hardware

Hardware phases are optional and come after the software product. When someone does pick them up: ESP32 GPIO pins are not 5 V tolerant. Measure a sensor's output before it touches a pin, and update the wiring note in `firmware/README.md` if the reference design changes. Do not commit photos of a real desk, serial numbers, or network names from a lab.

## Secrets and personal data

Do not commit `.env` files, `silverback.config.json`, API tokens, or window-title examples taken from a real session. The example config and the extension placeholders use made-up names (`SilverBack Demo`, `calendar.example`).

Do not add a camera, webcam, photo, or video path. Silver Back does not detect people in images and does not process other people's personal data. A trigger is an explicit event.

## Commits

Use an imperative subject line and say why the change is there. The test command you ran belongs in the pull request.
