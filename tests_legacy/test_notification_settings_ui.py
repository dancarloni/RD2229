import json
from unittest.mock import patch

from sections_app.services.notification_settings import load_notification_settings
from sections_app.ui.notification_settings_window import NotificationSettingsWindow


def test_ui_save_calls_save_notification_settings(monkeypatch, tmp_path):
    called = {}

    def fake_save(settings, path=None):
        called["settings"] = settings

    monkeypatch.setattr(
        "sections_app.ui.notification_settings_window.save_notification_settings", fake_save
    )
    ns = NotificationSettingsWindow(master=None)
    # programmatically set settings
    ns.set_settings(
        {
            "level": "all",
            "show_toasts": False,
            "silent_sources": ["mod1"],
            "confirm_default": "default_no",
        }
    )
    ns.save()
    assert called["settings"]["level"] == "all"
    assert called["settings"]["show_toasts"] is False
    assert called["settings"]["silent_sources"] == ["mod1"]


def test_center_honors_level_setting(monkeypatch):
    # Make NotificationCenter reload settings to a strict mode
    monkeypatch.setattr(
        "sections_app.services.notification_settings.load_notification_settings",
        lambda: {
            "level": "errors_only",
            "show_toasts": True,
            "silent_sources": [],
            "confirm_default": "ask",
        },
    )
    from sections_app.services import notification as ns
    from sections_app.ui.notification_center import NotificationCenter

    center = NotificationCenter(master=None)
    payload_info = {"level": "info", "title": "Info", "message": "msg"}
    assert center._should_display(payload_info) is False
    payload_error = {"level": "error", "title": "Err", "message": "msg"}
    assert center._should_display(payload_error) is True
