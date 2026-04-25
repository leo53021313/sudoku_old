# tests/unit/test_config_manager.py
import json
import logging
import os
import pytest

from app.config.manager import ConfigManager

MINIMAL_SCHEMA = {
    "test.bool_key": {
        "label": "Bool Key",
        "category": "test",
        "type": "bool",
        "default": True,
        "reload_required": False,
        "description": "A boolean test key",
    },
    "test.int_key": {
        "label": "Int Key",
        "category": "test",
        "type": "int",
        "default": 42,
        "reload_required": False,
        "description": "An integer test key",
    },
    "test.float_key": {
        "label": "Float Key",
        "category": "test",
        "type": "float",
        "default": 3.14,
        "reload_required": True,
        "description": "A float test key (requires restart)",
    },
    "test.str_key": {
        "label": "Str Key",
        "category": "test",
        "type": "str",
        "default": "hello",
        "reload_required": False,
        "description": "A string test key",
    },
}


@pytest.fixture
def cfg(tmp_path):
    path = str(tmp_path / "user_config.json")
    return ConfigManager(MINIMAL_SCHEMA, path)


def test_get_returns_schema_default(cfg):
    assert cfg.get("test.int_key") == 42
    assert cfg.get("test.bool_key") is True
    assert cfg.get("test.float_key") == pytest.approx(3.14)


def test_get_raises_on_unknown_key(cfg):
    with pytest.raises(KeyError):
        cfg.get("nonexistent.key")


def test_set_persists_override(cfg, tmp_path):
    cfg.set("test.int_key", 99)
    assert cfg.get("test.int_key") == 99
    # Reload from disk
    cfg2 = ConfigManager(MINIMAL_SCHEMA, str(tmp_path / "user_config.json"))
    assert cfg2.get("test.int_key") == 99


def test_set_writes_atomically(cfg, tmp_path):
    cfg.set("test.str_key", "world")
    config_path = str(tmp_path / "user_config.json")
    assert os.path.exists(config_path)
    # Temp file should be gone after write
    assert not os.path.exists(config_path + ".tmp")
    with open(config_path) as f:
        data = json.load(f)
    assert data["test.str_key"] == "world"


def test_hot_reload_callback_fires(cfg):
    received = []
    cfg.register_callback("test.int_key", lambda v: received.append(v))
    hot = cfg.set("test.int_key", 77)
    assert hot is True
    assert received == [77]


def test_reload_required_key_no_callback(cfg):
    received = []
    cfg.register_callback("test.float_key", lambda v: received.append(v))
    hot = cfg.set("test.float_key", 2.71)
    assert hot is False
    assert received == []  # callback must NOT fire for reload_required keys


def test_coerce_string_to_bool(cfg):
    cfg.set("test.bool_key", "false")
    assert cfg.get("test.bool_key") is False
    cfg.set("test.bool_key", "true")
    assert cfg.get("test.bool_key") is True


def test_coerce_string_to_int(cfg):
    cfg.set("test.int_key", "10")
    assert cfg.get("test.int_key") == 10


def test_coerce_string_to_float(cfg):
    cfg.set("test.float_key", "1.5")
    assert cfg.get("test.float_key") == pytest.approx(1.5)


def test_reset_to_default(cfg):
    cfg.set("test.int_key", 100)
    cfg.reset_to_default("test.int_key")
    assert cfg.get("test.int_key") == 42


def test_corrupted_json_falls_back_to_empty(tmp_path, caplog):
    config_path = str(tmp_path / "user_config.json")
    with open(config_path, "w") as f:
        f.write("{broken json")
    with caplog.at_level(logging.WARNING):
        cfg2 = ConfigManager(MINIMAL_SCHEMA, config_path)
    assert cfg2.get("test.int_key") == 42  # falls back to schema default
    assert any("損毀" in r.message or "corrupt" in r.message.lower() for r in caplog.records)


def test_callback_exception_is_logged(cfg, caplog):
    def bad_cb(v):
        raise RuntimeError("callback failure")
    cfg.register_callback("test.int_key", bad_cb)
    with caplog.at_level(logging.WARNING):
        cfg.set("test.int_key", 5)
    assert any("callback" in r.message.lower() or "Hot-reload" in r.message for r in caplog.records)
