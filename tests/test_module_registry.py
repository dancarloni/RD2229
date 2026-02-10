from apps.sections.modules.registry import ModuleRegistry


def test_registry_discovers_modules():
    registry = ModuleRegistry()
    specs = registry.get_specs()
    assert isinstance(specs, list)
    keys = {s.key for s in specs}
    # Expect at least the carbon_fiber_placeholder and debug modules that exist in the modules package
    assert "carbon_fiber_placeholder" in keys
    assert "debug" in keys


def test_ordering_from_config(tmp_path, monkeypatch):
    import json

    # create a temporary config that sets order
    cfg = {
        "order": ["material", "carbon_fiber_placeholder"],
        "modules": {
            "material": {"enabled": True},
            "carbon_fiber_placeholder": {"enabled": True},
        },
    }
    cfg_file = tmp_path / "modules_config.json"
    cfg_file.write_text(json.dumps(cfg))

    import importlib

    pkg = importlib.import_module("apps.sections.modules")
    # monkeypatch the config path to point to tmp file
    monkeypatch.setattr(pkg, "__file__", str(cfg_file))

    reg = ModuleRegistry()
    specs = reg.get_specs()
    assert isinstance(specs, list)
    # if ordering is respected, first entry should be 'material' if available; this test just ensures no crash
    assert all(hasattr(s, "key") for s in specs)
