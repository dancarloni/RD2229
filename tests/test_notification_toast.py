"""Test Qt per toast overlay nel NotificationCenterWindow."""

from __future__ import annotations

from typing import Any

import pytest

pytest.importorskip("pytestqt")

from src.ui.qt.notification_center import NotificationCenterWindow


@pytest.fixture
def notification_widget(qtbot: Any) -> NotificationCenterWindow:
    widget = NotificationCenterWindow()
    qtbot.addWidget(widget)
    widget.resize(800, 500)
    widget.show()
    return widget


def test_notify_shows_toast(notification_widget: NotificationCenterWindow) -> None:
    notification_widget.notify("warning", "Verifica completata con avvisi")

    assert notification_widget.list_widget.count() == 1
    assert notification_widget._toast.isVisible() is True


def test_explicit_toast_api(notification_widget: NotificationCenterWindow) -> None:
    notification_widget.show_toast("info", "Salvataggio automatico", duration_ms=500)

    assert notification_widget._toast.isVisible() is True
