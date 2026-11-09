import json

from silverback.actions import ActionResult
from silverback.config import load_config
from silverback.listener import Debouncer, handle_line


class RecordingBackend:
    def __init__(self):
        self.matches = []

    def minimize_matching(self, match):
        self.matches.append(match)
        return ActionResult("minimize", match, True, True, "recorded")


def _config(tmp_path, debounce_ms=2000):
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "version": 1,
                "debounce_ms": debounce_ms,
                "actions": [{"type": "minimize", "match": "Notes"}],
            }
        ),
        encoding="utf-8",
    )
    return load_config(path)


def test_debouncer_window_and_zero():
    debouncer = Debouncer(1000)
    assert debouncer.allow("approach", 0)
    assert not debouncer.allow("approach", 999)
    assert debouncer.allow("approach", 1000)
    assert not debouncer.allow("approach", 1500)
    open_window = Debouncer(0)
    assert open_window.allow("approach", 5)
    assert open_window.allow("approach", 5)


def test_blank_and_invalid_lines(tmp_path):
    config = _config(tmp_path)
    backend = RecordingBackend()
    debouncer = Debouncer(config.debounce_ms)
    assert handle_line("  \n", config, backend, debouncer, 0) is None
    outcome = handle_line("{", config, backend, debouncer, 0)
    assert outcome is not None
    assert outcome.error
    assert outcome.results == ()
    assert backend.matches == []


def test_hello_heartbeat_and_clear_do_not_minimize(tmp_path):
    config = _config(tmp_path)
    backend = RecordingBackend()
    debouncer = Debouncer(config.debounce_ms)
    hello = handle_line(
        '{"v":1,"type":"hello","fw":"0.1.0","transport":"usb-serial"}',
        config,
        backend,
        debouncer,
        0,
    )
    beat = handle_line('{"v":1,"type":"heartbeat"}', config, backend, debouncer, 1)
    clear = handle_line(
        '{"v":1,"type":"presence","state":"clear"}',
        config,
        backend,
        debouncer,
        2,
    )
    assert hello.note == "hello fw=0.1.0 transport=usb-serial"
    assert beat.note == "heartbeat"
    assert "not implemented" in clear.note
    assert backend.matches == []


def test_approach_runs_once_inside_the_debounce_window(tmp_path):
    config = _config(tmp_path, debounce_ms=2000)
    backend = RecordingBackend()
    debouncer = Debouncer(config.debounce_ms)
    line = '{"v":1,"type":"presence","state":"approach"}'
    first = handle_line(line, config, backend, debouncer, 100)
    second = handle_line(line, config, backend, debouncer, 500)
    third = handle_line(line, config, backend, debouncer, 2100, dry_run=True)
    assert first.note == "approach"
    assert first.results[0].detail == "recorded"
    assert second.suppressed
    assert second.results == ()
    assert third.results[0].detail == "dry-run: not executed"
    assert backend.matches == ["Notes"]
