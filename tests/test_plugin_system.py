"""Tests for the new plugin system (PluginSpec, ActionSpec, PluginRegistry, loader)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure src is importable
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ---------------------------------------------------------------------------
# Contract tests
# ---------------------------------------------------------------------------


def test_plugin_spec_defaults():
    from src.plugins import PluginSpec

    spec = PluginSpec(id="test", title="Test Plugin")
    assert spec.id == "test"
    assert spec.title == "Test Plugin"
    assert spec.version == "0.1.0"
    assert spec.category == "general"
    assert spec.actions == []


def test_action_spec_defaults():
    from src.plugins import ActionSpec

    action = ActionSpec(id="do_thing", label="Do Thing")
    assert action.id == "do_thing"
    assert action.handler is None
    assert action.params == []


def test_param_spec_defaults():
    from src.plugins import ParamSpec

    param = ParamSpec(name="path", label="Path")
    assert param.type == "string"
    assert param.required is False
    assert param.default is None


def test_registry_register_and_get():
    from src.plugins import PluginRegistry, PluginSpec

    registry = PluginRegistry()
    spec = PluginSpec(id="my_plugin", title="My Plugin")
    registry.register(spec)

    assert registry.get("my_plugin") is spec
    assert registry.get("nonexistent") is None


def test_registry_list_plugins():
    from src.plugins import PluginRegistry, PluginSpec

    registry = PluginRegistry()
    registry.register(PluginSpec(id="a", title="A"))
    registry.register(PluginSpec(id="b", title="B"))

    ids = {p.id for p in registry.list_plugins()}
    assert ids == {"a", "b"}


def test_registry_clear():
    from src.plugins import PluginRegistry, PluginSpec

    registry = PluginRegistry()
    registry.register(PluginSpec(id="tmp", title="Tmp"))
    registry.clear()
    assert registry.list_plugins() == []


# ---------------------------------------------------------------------------
# Loader tests
# ---------------------------------------------------------------------------


def test_load_plugins_from_folder_sample_info():
    """The sample_info plugin in plugins/ should load correctly."""
    from src.plugins.loader import load_plugins_from_folder

    plugins_dir = ROOT / "plugins"
    specs = load_plugins_from_folder(plugins_dir)

    ids = {s.id for s in specs}
    assert "sample_info" in ids


def test_load_plugins_from_folder_all_three():
    from src.plugins.loader import load_plugins_from_folder

    plugins_dir = ROOT / "plugins"
    specs = load_plugins_from_folder(plugins_dir)

    ids = {s.id for s in specs}
    assert {"sample_info", "run_pipeline", "report_export"}.issubset(ids)


def test_load_plugins_from_folder_nonexistent():
    from src.plugins.loader import load_plugins_from_folder

    specs = load_plugins_from_folder(Path("/nonexistent/path"))
    assert specs == []


def test_load_plugins_from_entry_points_returns_list():
    """Should return a list (possibly empty) without raising."""
    from src.plugins.loader import load_plugins_from_entry_points

    result = load_plugins_from_entry_points()
    assert isinstance(result, list)


def test_load_all_plugins_both():
    from src.plugins.loader import load_all_plugins

    config = {"discovery": "both", "folder": str(ROOT / "plugins")}
    specs = load_all_plugins(config)
    assert isinstance(specs, list)
    ids = {s.id for s in specs}
    assert "sample_info" in ids


def test_load_all_plugins_folder_only():
    from src.plugins.loader import load_all_plugins

    config = {"discovery": "folder", "folder": str(ROOT / "plugins")}
    specs = load_all_plugins(config)
    ids = {s.id for s in specs}
    assert "sample_info" in ids


def test_load_all_plugins_entry_points_only():
    from src.plugins.loader import load_all_plugins

    specs = load_all_plugins({"discovery": "entry_points"})
    assert isinstance(specs, list)


# ---------------------------------------------------------------------------
# Sample plugin action smoke-test
# ---------------------------------------------------------------------------


def test_sample_info_action_handler():
    from src.plugins.loader import load_plugins_from_folder

    plugins_dir = ROOT / "plugins"
    specs = load_plugins_from_folder(plugins_dir)
    info_spec = next(s for s in specs if s.id == "sample_info")

    assert info_spec.actions
    action = info_spec.actions[0]
    assert action.handler is not None

    result = action.handler(project="test.json")
    assert result["status"] == "ok"
    assert result["project"] == "test.json"
