# Desktop companion

Python package that turns a Silver Back approach event into window actions. Develop and test it with `silverback trigger` and `listen --stdin`. A serial port is optional and unused until the later hardware phase. It runs on the standard library plus [pyserial](https://pypi.org/project/pyserial/). Python 3.11 or newer.

The root [README](../README.md) is the project overview. This file is how to run this package.

## Install

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e "./desktop[dev]"
```

## Config

Copy [silverback.config.example.json](silverback.config.example.json) to `silverback.config.json` (repo root or this directory) or to `~/.config/silverback/config.json`. You can also point `--config` or `SILVERBACK_CONFIG` at a file.

`match` is a case-insensitive substring of the window title. `minimize` is the action that runs. `hide`, `close`, and `focus` are accepted in the file and reported as stubs.

## Commands

```bash
python -m silverback trigger --config silverback.config.example.json --dry-run
python -m silverback trigger --config silverback.config.example.json
python -m silverback listen --stdin --dry-run --config silverback.config.example.json \
  < ../docs/examples/session.ndjson
python -m silverback listen --port /dev/ttyUSB0 --config silverback.config.json
python -m silverback doctor --config silverback.config.example.json
python -m silverback check-config --config silverback.config.example.json
```

`trigger` is the simulated approach. It does not read the serial port. With a visible window titled `SilverBack Demo` (see `make demo` in the repo root), the real `trigger` command minimizes that window on X11.

`listen` reads USB serial when you pass a port, or NDJSON on stdin with `--stdin`. Debounce uses the computer's clock, not `uptime_ms`. Restore-on-clear is not implemented.

Exit codes for `trigger`: `0` when every implemented action succeeded, `1` when an implemented action failed, `2` when the config is unusable. `listen` stays running after a missed window and returns `0` on EOF or Ctrl-C. A bad port returns `2`.

## Operating systems

| OS | Minimize | Exercised here |
| --- | --- | --- |
| Linux X11 | `xdotool` | Yes, when a display and `xmessage` are available |
| Linux Wayland | future backend | No |
| macOS | `osascript` via System Events, needs Accessibility permission | Code only |
| Windows | `ShowWindow(SW_MINIMIZE)` on visible top-level windows | Code only |

## Tests

```bash
cd desktop && python -m pytest
```
