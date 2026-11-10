import json
from pathlib import Path

import pytest

from silverback.protocol import ProtocolError, parse_line

ROOT = Path(__file__).resolve().parents[2]


def test_example_session_parses():
    lines = (ROOT / "docs" / "examples" / "session.ndjson").read_text(encoding="utf-8").splitlines()
    events = [parse_line(line) for line in lines if line.strip()]
    assert [event.type for event in events] == [
        "hello",
        "presence",
        "presence",
        "heartbeat",
        "presence",
    ]
    assert events[0].fw == "0.1.0"
    assert events[0].transport == "usb-serial"
    assert events[1].state == "approach"
    assert events[2].state == "approach"
    assert events[4].state == "clear"
    assert events[1].seq == 1


def test_firmware_sketch_uses_protocol_vocabulary():
    text = (ROOT / "firmware" / "src" / "main.cpp").read_text(encoding="utf-8")
    for token in ("hello", "presence", "heartbeat", "approach", "clear", "usb-serial"):
        assert token in text
    assert "SILVERBACK_PIR_PIN" in text
    assert "DEBOUNCE_MS" in text


@pytest.mark.parametrize(
    "line",
    [
        "",
        "   ",
        "not-json",
        "[]",
        "123",
        '{"type":"hello"}',
        '{"v":2,"type":"hello"}',
        '{"v":true,"type":"hello"}',
        '{"v":1,"type":"nope"}',
        '{"v":1,"type":"presence"}',
        '{"v":1,"type":"presence","state":"maybe"}',
        '{"v":1,"type":"hello","state":"approach"}',
        '{"v":1,"type":"heartbeat","state":"clear"}',
        '{"v":1,"type":"hello","seq":-1}',
        '{"v":1,"type":"hello","seq":true}',
        '{"v":1,"type":"hello","seq":"1"}',
        '{"v":1,"type":"hello","sensor":""}',
        '{"v":1,"type":"hello","uptime_ms":1.5}',
    ],
)
def test_rejects_bad_lines(line):
    with pytest.raises(ProtocolError):
        parse_line(line)


def test_rejects_oversized_line():
    payload = {"v": 1, "type": "hello", "sensor": "x" * 2000}
    with pytest.raises(ProtocolError, match="longer"):
        parse_line(json.dumps(payload))


def test_ignores_unknown_fields_and_strips_whitespace():
    event = parse_line('  {"v":1,"type":"heartbeat","extra":true,"seq":4}  \n')
    assert event.type == "heartbeat"
    assert event.seq == 4
    assert event.state is None
