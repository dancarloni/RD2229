"""
MaterialLayoutLogic — Gestione layout, drag&drop, reset, preferenze

Salva/carica le preferenze di layout (es. dimensioni splitter) in
config/layout_preferences.json nella root del progetto.
"""

import json
import pathlib
from typing import Any, Dict


def _find_config_dir() -> pathlib.Path:
    """Risale le directory finché trova config/ nella root del progetto."""
    here = pathlib.Path(__file__).resolve()
    root = here
    while not (root / "config").is_dir() and root.parent != root:
        root = root.parent
    return root / "config"


_PREFS_FILE = _find_config_dir() / "layout_preferences.json"


class MaterialLayoutLogic:
    @staticmethod
    def save_layout(prefs: Dict[str, Any]) -> None:
        """Salva preferenze layout in config/layout_preferences.json."""
        try:
            _PREFS_FILE.parent.mkdir(parents=True, exist_ok=True)
            _PREFS_FILE.write_text(
                json.dumps(prefs, indent=2, ensure_ascii=False), encoding="utf-8"
            )
        except Exception:
            pass

    @staticmethod
    def load_layout() -> Dict[str, Any]:
        """Carica preferenze layout. Restituisce {} se il file non esiste."""
        try:
            if _PREFS_FILE.exists():
                return json.loads(_PREFS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
        return {}

    @staticmethod
    def reset_layout() -> None:
        """Elimina il file preferenze (reset al default)."""
        try:
            _PREFS_FILE.unlink(missing_ok=True)
        except Exception:
            pass


# Per test rapido
if __name__ == "__main__":
    MaterialLayoutLogic.save_layout({"splitter_sizes": [800, 500]})
    print(MaterialLayoutLogic.load_layout())
    MaterialLayoutLogic.reset_layout()
