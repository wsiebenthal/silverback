import json

import pytest

from silverback.actions import (
    dispatch,
    exit_code_for,
    format_result,
    run_actions,
    title_matches,
)
from silverback.config import Action, load_config


class RecordingBackend:
    def __init__(self):
        self.matches = []

    def minimize_matching(self, match):
        self.matches.append(match)
        from silverback.actions import ActionResult

        return ActionResult("minimize", match, True, True, "recorded")


def _config(tmp_path, actions):
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "version": 1,
                "actions": actions,
            }
        ),
        encoding="utf-8",
    )
    return load_config(path)


def test_title_matches_is_case_insensitive():
    assert title_matches("Project Notes - Editor", "notes")
    assert title_matches("NOTES", "Notes")
    assert not title_matches("Mail", "Notes")
    assert not title_matches("", "Notes")
    assert not title_matches("Notes", "")


def test_minimize_is_dispatched():
    backend = RecordingBackend()
    result = dispatch(Action("minimize", "Notes"), backend)
    assert result.ok
    assert result.implemented
    assert backend.matches == ["Notes"]


@pytest.mark.parametrize("action_type", ["hide", "close", "focus"])
def test_stub_actions_do_not_touch_the_backend(action_type):
    backend = RecordingBackend()
    result = dispatch(Action(action_type, "Notes"), backend)
    assert result.implemented is False
    assert result.ok is False
    assert "not implemented" in result.detail
    assert backend.matches == []
    assert format_result(result).startswith("[stub]")


def test_unknown_action_is_reported():
    result = dispatch(Action("explode", "Notes"), RecordingBackend())
    assert result.implemented is False
    assert "unknown action type" in result.detail


def test_run_actions_skips_disabled_and_dry_run(tmp_path):
    config = _config(
        tmp_path,
        [
            {"type": "minimize", "match": "Notes", "enabled": False},
            {"type": "minimize", "match": "Mail", "enabled": True},
            {"type": "hide", "match": "Chat", "enabled": True},
        ],
    )
    backend = RecordingBackend()
    results = run_actions(config, backend, dry_run=True)
    assert backend.matches == []
    assert [result.match for result in results] == ["Mail", "Chat"]
    assert results[0].ok and results[0].detail == "dry-run: not executed"
    assert results[1].implemented is False
    assert exit_code_for(results) == 0


def test_exit_code_fails_when_an_implemented_action_fails():
    from silverback.actions import ActionResult

    results = [
        ActionResult("minimize", "Notes", True, False, "missing"),
        ActionResult("hide", "Chat", False, False, "stub"),
    ]
    assert exit_code_for(results) == 1
    assert format_result(results[0]).startswith("[failed]")
