import importlib
import json
import os
import sys
import types

import pytest

MODULES = [
    "project_editor",
    "pipeline_runner",
    "report_viewer",
    "material_editor",
    "code_settings",
    # Add more as needed from MODULES_MAPPING.md
]

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "modules", "modules_config.json")
MODULES_PATH = os.path.join(os.path.dirname(__file__), "..", "modules")

@pytest.mark.parametrize("mod_key", MODULES)
def test_module_registered_and_launchable(mod_key):
    sys.path.insert(0, MODULES_PATH)
    mod = importlib.import_module(mod_key)
    assert hasattr(mod, "MODULE_SPEC"), f"{mod_key} missing MODULE_SPEC"
    assert hasattr(mod, "create_module"), f"{mod_key} missing create_module()"
    # Should return a placeholder or real window without error
    win = mod.create_module(master=None)
    assert win is not None
    if hasattr(win, "mainloop"):
        win.mainloop()
    sys.path.pop(0)

def test_modules_config_json_complete():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
    for key in MODULES:
        assert key in config, f"{key} missing in modules_config.json"
        assert config[key]["enabled"] is True



