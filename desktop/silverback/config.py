"""Load the desktop JSON config."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

IMPLEMENTED_ACTIONS = frozenset({"minimize"})
STUB_ACTIONS = frozenset({"hide", "close", "focus"})
KNOWN_ACTIONS = IMPLEMENTED_ACTIONS | STUB_ACTIONS


class ConfigError(Exception):
    """The config file is missing or invalid."""


@dataclass(frozen=True)
class Action:
    type: str
    match: str
    enabled: bool = True


@dataclass(frozen=True)
class SerialSettings:
    port: str | None
    baud: int


@dataclass(frozen=True)
class AppConfig:
    version: int
    debounce_ms: int
    serial: SerialSettings
    actions: tuple[Action, ...]


def resolve_config_path(explicit: str | None) -> Path:
    """Find a config file.

    Order: --config, SILVERBACK_CONFIG, ./silverback.config.json,
    ~/.config/silverback/config.json.
    """
    if explicit:
        return Path(explicit).expanduser()
    env = os.environ.get("SILVERBACK_CONFIG")
    if env:
        return Path(env).expanduser()
    local = Path("silverback.config.json")
    if local.is_file():
        return local.resolve()
    home = Path.home() / ".config" / "silverback" / "config.json"
    if home.is_file():
        return home
    raise ConfigError(
        "no config file found. Pass --config, set SILVERBACK_CONFIG, "
        "or copy desktop/silverback.config.example.json to silverback.config.json"
    )


def load_config(path: Path) -> AppConfig:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigError(f"could not read {path}: {exc.strerror or exc}") from exc
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ConfigError(f"invalid JSON in {path}: {exc.msg}") from exc
    if not isinstance(data, dict):
        raise ConfigError("config must be a JSON object")

    version = data.get("version")
    if isinstance(version, bool) or version != 1:
        raise ConfigError(f"unsupported config version: {version!r}")

    debounce = data.get("debounce_ms", 2000)
    if isinstance(debounce, bool) or not isinstance(debounce, int) or debounce < 0:
        raise ConfigError("debounce_ms must be an integer >= 0")

    serial_data = data.get("serial", {})
    if serial_data is None:
        serial_data = {}
    if not isinstance(serial_data, dict):
        raise ConfigError("serial must be a JSON object")
    port = serial_data.get("port")
    if port is not None and not isinstance(port, str):
        raise ConfigError("serial.port must be a string or null")
    if isinstance(port, str):
        port = port.strip() or None
    baud = serial_data.get("baud", 115200)
    if isinstance(baud, bool) or not isinstance(baud, int) or baud <= 0:
        raise ConfigError("serial.baud must be a positive integer")

    raw_actions = data.get("actions", [])
    if not isinstance(raw_actions, list):
        raise ConfigError("actions must be a list")
    actions = tuple(_parse_action(item, index) for index, item in enumerate(raw_actions))
    return AppConfig(
        version=1,
        debounce_ms=debounce,
        serial=SerialSettings(port=port, baud=baud),
        actions=actions,
    )


def _parse_action(item: object, index: int) -> Action:
    label = f"actions[{index}]"
    if not isinstance(item, dict):
        raise ConfigError(f"{label} must be a JSON object")
    action_type = item.get("type")
    if not isinstance(action_type, str) or not action_type.strip():
        raise ConfigError(f"{label}.type must be a non-empty string")
    action_type = action_type.strip()
    match = item.get("match")
    if not isinstance(match, str) or not match.strip():
        raise ConfigError(f"{label}.match must be a non-empty string")
    enabled = item.get("enabled", True)
    if not isinstance(enabled, bool):
        raise ConfigError(f"{label}.enabled must be a boolean")
    return Action(type=action_type, match=match.strip(), enabled=enabled)
