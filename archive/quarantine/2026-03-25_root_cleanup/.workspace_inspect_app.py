import sys

print("python exe:", sys.executable)
print("sys.path[0]:", sys.path[0])

try:
    import src.ui.modern.app as app

    print("imported src.ui.modern.app -> main:", getattr(app, "main", None))
    print("app.main module:", getattr(getattr(app, "main", None), "__module__", None))
except Exception as e:
    print("import src.ui.modern.app failed:", repr(e))

try:
    import src.ui.modern.registry as registry

    print(
        "imported registry; public attrs:", [a for a in dir(registry) if not a.startswith("_")][:50]
    )
except Exception as e:
    print("import src.ui.modern.registry failed:", repr(e))

try:
    from src.config import app_cfg

    print("app_cfg keys:", list(getattr(app_cfg, "__dict__", {}).keys()))
    print("plugin_discovery:", getattr(app_cfg, "plugin_discovery", None))
    print("plugins_path:", getattr(app_cfg, "plugins_path", None))
except Exception as e:
    print("import app_cfg failed or not present:", repr(e))

try:
    import importlib.metadata as md

    eps = md.entry_points()
    # show a small sample
    sample = []
    for group in eps.groups:
        sample.append((group, len(eps.select(group=group))))
        if len(sample) >= 10:
            break
    print("entry_points groups sample (name, count):", sample[:10])
except Exception as e:
    print("entry_points check failed:", repr(e))

print("done")
