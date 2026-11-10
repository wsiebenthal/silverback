"""Live check that `silverback trigger` minimizes a real X11 window.

Skipped unless DISPLAY, xdotool, xmessage, and xprop are available. GitHub
Actions has no display, so CI runs the unit tests and skips this one.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time

import pytest

from silverback.cli import main

pytestmark = pytest.mark.skipif(
    not os.environ.get("DISPLAY")
    or shutil.which("xdotool") is None
    or shutil.which("xmessage") is None
    or shutil.which("xprop") is None,
    reason="requires DISPLAY, xdotool, xmessage, and xprop",
)


def _search(title: str) -> list[str]:
    proc = subprocess.run(
        ["xdotool", "search", "--onlyvisible", "--name", title],
        capture_output=True,
        text=True,
        check=False,
    )
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def _wait_visible(title: str) -> str:
    deadline = time.time() + 5
    while time.time() < deadline:
        found = _search(title)
        if found:
            return found[0]
        time.sleep(0.1)
    raise AssertionError(f"window {title!r} did not appear")


def _wm_state(window_id: str) -> str:
    proc = subprocess.run(
        ["xprop", "-id", window_id, "_NET_WM_STATE"],
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.stdout


def test_simulated_trigger_minimizes_a_window(tmp_path, capsys):
    title = f"SilverBackTest{os.getpid()}"
    config = tmp_path / "config.json"
    config.write_text(
        json.dumps(
            {
                "version": 1,
                "debounce_ms": 2000,
                "serial": {"port": None, "baud": 115200},
                "actions": [{"type": "minimize", "match": title, "enabled": True}],
            }
        ),
        encoding="utf-8",
    )
    proc = subprocess.Popen(
        ["xmessage", "-title", title, "-buttons", "close", "-timeout", "30", "silverback test"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        window_id = _wait_visible(title)
        dry = main(["trigger", "--config", str(config), "--dry-run"])
        assert dry == 0
        assert "_NET_WM_STATE_HIDDEN" not in _wm_state(window_id)
        capsys.readouterr()

        code = main(["trigger", "--config", str(config)])
        captured = capsys.readouterr()
        assert code == 0, captured.out + captured.err
        assert "simulated approach" in captured.out
        assert title in captured.out
        assert "[ok] minimize" in captured.out

        deadline = time.time() + 2
        last = ""
        while time.time() < deadline:
            last = _wm_state(window_id)
            if "_NET_WM_STATE_HIDDEN" in last:
                break
            time.sleep(0.1)
        assert "_NET_WM_STATE_HIDDEN" in last, last
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
