import json
from pathlib import Path

import pytest

from silverback.config import ConfigError, load_config, resolve_config_path

ROOT = Path(__file__).resolve().parents[2]


def _write(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "config.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _valid(**overrides) -> dict:
    data = {
        "version": 1,
        "debounce_ms": 2000,
        "serial": {"port": None, "baud": 115200},
        "actions": [{"type": "minimize", "match": "Notes", "enabled": True}],
    }
    data.update(overrides)
    return data


def test_example_config_loads():
    config = load_config(ROOT / "desktop" / "silverback.config.example.json")
    assert config.version == 1
    assert config.debounce_ms == 2000
    assert config.serial.port is None
    assert config.serial.baud == 115200
    assert len(config.actions) == 1
    assert config.actions[0].type == "minimize"
    assert config.actions[0].match == "SilverBack Demo"
    assert config.actions[0].enabled is True


def test_defaults_and_extra_keys(tmp_path):
    path = _write(
        tmp_path,
        {
            "version": 1,
            "actions": [{"type": "hide", "match": "Mail"}],
            "note": "ignored",
        },
    )
    config = load_config(path)
    assert config.debounce_ms == 2000
    assert config.serial.port is None
    assert config.serial.baud == 115200
    assert config.actions[0].enabled is True
    assert config.actions[0].type == "hide"


def test_blank_port_becomes_none(tmp_path):
    path = _write(tmp_path, _valid(serial={"port": "  ", "baud": 9600}))
    config = load_config(path)
    assert config.serial.port is None
    assert config.serial.baud == 9600


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"version": 2, "actions": []},
        {"version": True, "actions": []},
        {"version": 1, "debounce_ms": -1, "actions": []},
        {"version": 1, "serial": [], "actions": []},
        {"version": 1, "serial": {"baud": 0}, "actions": []},
        {"version": 1, "serial": {"port": 7}, "actions": []},
        {"version": 1, "actions": {}},
        {"version": 1, "actions": ["minimize"]},
        {"version": 1, "actions": [{"type": "minimize"}]},
        {"version": 1, "actions": [{"type": "minimize", "match": "  "}]},
        {"version": 1, "actions": [{"type": "", "match": "Notes"}]},
        {"version": 1, "actions": [{"type": "minimize", "match": "Notes", "enabled": "yes"}]},
    ],
)
def test_rejects_invalid_config(tmp_path, payload):
    path = _write(tmp_path, payload)
    with pytest.raises(ConfigError):
        load_config(path)


def test_missing_file(tmp_path):
    with pytest.raises(ConfigError, match="could not read"):
        load_config(tmp_path / "missing.json")


def test_resolve_explicit(tmp_path):
    path = _write(tmp_path, _valid())
    assert resolve_config_path(str(path)) == path


def test_resolve_env(tmp_path, monkeypatch):
    path = _write(tmp_path, _valid())
    monkeypatch.setenv("SILVERBACK_CONFIG", str(path))
    assert resolve_config_path(None) == path


def test_resolve_local_file(tmp_path, monkeypatch):
    monkeypatch.delenv("SILVERBACK_CONFIG", raising=False)
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "silverback.config.json"
    path.write_text(json.dumps(_valid()), encoding="utf-8")
    assert resolve_config_path(None) == path.resolve()


def test_resolve_home_config(tmp_path, monkeypatch):
    monkeypatch.delenv("SILVERBACK_CONFIG", raising=False)
    monkeypatch.chdir(tmp_path)
    home = tmp_path / "home"
    path = home / ".config" / "silverback" / "config.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(_valid()), encoding="utf-8")
    monkeypatch.setattr(Path, "home", lambda: home)
    assert resolve_config_path(None) == path


def test_resolve_missing(tmp_path, monkeypatch):
    monkeypatch.delenv("SILVERBACK_CONFIG", raising=False)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(Path, "home", lambda: tmp_path / "home")
    with pytest.raises(ConfigError, match="no config file"):
        resolve_config_path(None)
