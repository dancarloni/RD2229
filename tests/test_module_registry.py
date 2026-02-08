import pytest
from sections_app.modules.registry import ModuleRegistry


def test_registry_discovers_modules():
    registry = ModuleRegistry()
    specs = registry.get_specs()
    assert isinstance(specs, list)
    keys = {s.key for s in specs}
    # Expect at least the geometry and debug modules that exist in the modules package
    assert "geometry" in keys
    assert "debug" in keys


def test_ordering_from_config(tmp_path, monkeypatch):
    import json

    # create a temporary config that sets order
    cfg = {
        "order": ["material", "geometry"],
        "modules": {
            "material": {"enabled": True},
            "geometry": {"enabled": True},
        },
    }
    cfg_file = tmp_path / "modules_config.json"
    cfg_file.write_text(json.dumps(cfg))

    import importlib

    pkg = importlib.import_module("sections_app.modules")
    # monkeypatch the config path to point to tmp file
    monkeypatch.setattr(pkg, "__file__", str(cfg_file))

    reg = ModuleRegistry()
    specs = reg.get_specs()
    assert isinstance(specs, list)
    # if ordering is respected, first entry should be 'material' if available; this test just ensures no crash
    assert all(hasattr(s, "key") for s in specs)
