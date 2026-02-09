from pathlib import Path

from sections_app.services.notification_settings import (
    load_notification_settings,
    save_notification_settings,
)


def test_load_saves_defaults(tmp_path: Path):
    p = tmp_path / "notif.json"
    assert not p.exists()
    s = load_notification_settings(path=p)
    assert isinstance(s, dict)
    assert s.get("level") == "errors_only"
    # Save a change and re-load
    s["level"] = "all"
    save_notification_settings(s, path=p)
    loaded = load_notification_settings(path=p)
    assert loaded["level"] == "all"


def test_invalid_file_returns_defaults(tmp_path: Path):
    p = tmp_path / "bad.json"
    p.write_text("not json")
    s = load_notification_settings(path=p)
    assert isinstance(s, dict)
    assert s.get("level") == "errors_only"
