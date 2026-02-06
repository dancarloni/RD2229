from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

DEFAULT_SETTINGS: Dict[str, Any] = {
    "level": "errors_only",  # errors_only | warnings_and_errors | all
    "show_toasts": True,
    "silent_sources": [],
    "confirm_default": "ask",  # ask | default_yes | default_no
}

# Default path: project_root / data / notification_settings.json
SETTINGS_PATH = Path(__file__).resolve().parents[2] / "data" / "notification_settings.json"


def _ensure_dir(path: Path) -> None:
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)


def load_notification_settings(path: Optional[Path] = None) -> Dict[str, Any]:
    """Load settings from JSON; return defaults if missing or invalid."""
    p = Path(path) if path is not None else SETTINGS_PATH
    try:
        if not p.exists():
            # write defaults
            save_notification_settings(DEFAULT_SETTINGS, path=p)
            return dict(DEFAULT_SETTINGS)
        with p.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
            # Merge with defaults to ensure keys
            out = dict(DEFAULT_SETTINGS)
            out.update({k: data.get(k, out[k]) for k in out.keys()})
            return out
    except Exception:
        logger.exception("Failed to load notification settings, returning defaults")
        return dict(DEFAULT_SETTINGS)


def save_notification_settings(settings: Dict[str, Any], path: Optional[Path] = None) -> None:
    p = Path(path) if path is not None else SETTINGS_PATH
    try:
        _ensure_dir(p)
        with p.open("w", encoding="utf-8") as fh:
            json.dump(settings, fh, indent=2, ensure_ascii=False)
    except Exception:
        logger.exception("Failed to save notification settings to %s", p)
