"""Parser for Silver Back sensor events. See docs/protocol.md."""

from __future__ import annotations

import json
from dataclasses import dataclass

MAX_LINE_CHARS = 1024
EVENT_TYPES = frozenset({"hello", "presence", "heartbeat"})
PRESENCE_STATES = frozenset({"approach", "clear"})


class ProtocolError(Exception):
    """A line is not a version-1 sensor event."""


@dataclass(frozen=True)
class Event:
    v: int
    type: str
    state: str | None = None
    sensor: str | None = None
    transport: str | None = None
    fw: str | None = None
    seq: int | None = None
    uptime_ms: int | None = None


def parse_line(line: str) -> Event:
    """Parse one NDJSON line. Raises ProtocolError when the line is unusable."""
    text = line.strip().lstrip("\ufeff")
    if not text:
        raise ProtocolError("empty line")
    if len(text) > MAX_LINE_CHARS:
        raise ProtocolError(f"line longer than {MAX_LINE_CHARS} characters")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ProtocolError(f"invalid json: {exc.msg}") from exc
    if not isinstance(data, dict):
        raise ProtocolError("event must be a JSON object")

    version = data.get("v")
    if isinstance(version, bool) or not isinstance(version, int) or version != 1:
        raise ProtocolError(f"unsupported version: {version!r}")

    event_type = data.get("type")
    if event_type not in EVENT_TYPES:
        raise ProtocolError(f"unsupported type: {event_type!r}")

    state = _optional_choice(data, "state", PRESENCE_STATES)
    if event_type == "presence" and state is None:
        raise ProtocolError("presence events require state 'approach' or 'clear'")
    if event_type != "presence" and state is not None:
        raise ProtocolError("state is only valid on presence events")

    return Event(
        v=version,
        type=event_type,
        state=state,
        sensor=_optional_str(data, "sensor"),
        transport=_optional_str(data, "transport"),
        fw=_optional_str(data, "fw"),
        seq=_optional_int(data, "seq"),
        uptime_ms=_optional_int(data, "uptime_ms"),
    )


def _optional_choice(data: dict, key: str, allowed: frozenset[str]) -> str | None:
    if key not in data or data[key] is None:
        return None
    value = data[key]
    if value not in allowed:
        raise ProtocolError(f"unsupported {key}: {value!r}")
    return value


def _optional_str(data: dict, key: str) -> str | None:
    if key not in data or data[key] is None:
        return None
    value = data[key]
    if not isinstance(value, str) or not value.strip():
        raise ProtocolError(f"{key} must be a non-empty string")
    return value


def _optional_int(data: dict, key: str) -> int | None:
    if key not in data or data[key] is None:
        return None
    value = data[key]
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ProtocolError(f"{key} must be an integer >= 0")
    return value
