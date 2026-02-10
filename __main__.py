from importlib import import_module
import warnings

try:
    # Nuovo launcher modulare
    run = import_module('src.launcher.bootstrap').run_app
except Exception as e:
    # Fallback alla versione precedente per compatibilità
    warnings.warn(f"Falling back to legacy apps.sections.app.run_app: {e}", DeprecationWarning)
    run = import_module('apps.sections.app').run_app

if __name__ == "__main__":
    run()
