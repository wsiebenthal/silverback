import json
import sys
from io import StringIO
from pathlib import Path

from silverback.actions import ActionResult
from silverback.cli import main

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "desktop" / "silverback.config.example.json"
SESSION = ROOT / "docs" / "examples" / "session.ndjson"


def test_replay_example_session_dry_run(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", StringIO(SESSION.read_text(encoding="utf-8")))
    code = main(
        [
            "listen",
            "--stdin",
            "--dry-run",
            "--config",
            str(EXAMPLE),
        ]
    )
    captured = capsys.readouterr()
    assert code == 0
    assert captured.err == ""
    assert captured.out.splitlines() == [
        "hello fw=0.1.0 transport=usb-serial",
        "approach",
        "[ok] minimize 'SilverBack Demo': dry-run: not executed",
        "approach suppressed by debounce",
        "heartbeat",
        "clear received; restoring windows is not implemented yet",
    ]


def test_trigger_dry_run_does_not_call_the_backend(monkeypatch, capsys):
    class Boom:
        def minimize_matching(self, _match):
            raise AssertionError("backend called")

    monkeypatch.setattr("silverback.cli.get_backend", lambda: Boom())
    code = main(["trigger", "--config", str(EXAMPLE), "--dry-run"])
    captured = capsys.readouterr()
    assert code == 0
    assert captured.out.splitlines() == [
        "simulated approach",
        "[ok] minimize 'SilverBack Demo': dry-run: not executed",
    ]


def test_trigger_failure_exit_code(monkeypatch, tmp_path, capsys):
    class Missing:
        def minimize_matching(self, match):
            return ActionResult("minimize", match, True, False, "no visible window title matches")

    monkeypatch.setattr("silverback.cli.get_backend", lambda: Missing())
    code = main(["trigger", "--config", str(EXAMPLE)])
    captured = capsys.readouterr()
    assert code == 1
    assert "[failed] minimize 'SilverBack Demo'" in captured.out


def test_stub_action_exits_zero(monkeypatch, tmp_path, capsys):
    class Boom:
        def minimize_matching(self, _match):
            raise AssertionError("backend called")

    path = tmp_path / "config.json"
    path.write_text(
        json.dumps({"version": 1, "actions": [{"type": "hide", "match": "Notes"}]}),
        encoding="utf-8",
    )
    monkeypatch.setattr("silverback.cli.get_backend", lambda: Boom())
    code = main(["trigger", "--config", str(path)])
    captured = capsys.readouterr()
    assert code == 0
    assert captured.out.splitlines()[1].startswith("[stub] hide 'Notes'")


def test_listen_requires_a_port(tmp_path, capsys):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"version": 1, "actions": []}), encoding="utf-8")
    code = main(["listen", "--config", str(path)])
    captured = capsys.readouterr()
    assert code == 2
    assert "no serial port" in captured.err


def test_listen_rejects_stdin_and_port_together(capsys):
    code = main(["listen", "--stdin", "--port", "/dev/ttyUSB0", "--config", str(EXAMPLE)])
    captured = capsys.readouterr()
    assert code == 2
    assert "not both" in captured.err


def test_check_config_prints_the_example(capsys):
    code = main(["check-config", "--config", str(EXAMPLE)])
    captured = capsys.readouterr()
    assert code == 0
    assert "SilverBack Demo" in captured.out
    assert "debounce_ms: 2000" in captured.out


def test_doctor_reports_platform(capsys):
    code = main(["doctor", "--config", str(EXAMPLE)])
    captured = capsys.readouterr()
    assert code == 0
    assert "silverback 0.1.0" in captured.out
    assert "minimize:" in captured.out
    assert "extension bridge: planned" in captured.out
    assert "SilverBack Demo" in captured.out


def test_bad_config_exits_2(tmp_path, capsys):
    path = tmp_path / "config.json"
    path.write_text("{", encoding="utf-8")
    code = main(["trigger", "--config", str(path)])
    captured = capsys.readouterr()
    assert code == 2
    assert "error:" in captured.err
