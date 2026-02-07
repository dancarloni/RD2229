from sections_app.ui.notification_center import NotificationCenter

from sections_app.services import notification as ns
from sections_app.services.event_bus import NOTIFICATION, EventBus


def setup_function(func):
    # Clear listeners between tests
    EventBus().clear()


def test_center_records_info_notifications():
    center = NotificationCenter(master=None)
    EventBus().clear()
    EventBus().subscribe(NOTIFICATION, center._on_notification)
    ns.notify_info("Test", "This is a test")
    # event loop may be synchronous; history should contain payload
    assert any(
        p.get("title") == "Test" and "This is a test" in p.get("message", "")
        for p in center.history
    )


def test_confirm_responder_invokes_callback():
    center = NotificationCenter(master=None)
    EventBus().clear()
    results = []

    def cb(ans):
        results.append(ans)

    responder = ns.ask_confirm("Delete?", "Are you sure?", callback=cb)
    # ask_confirm emitted event, center recorded payload
    assert any(p.get("level") == "confirm" and p.get("title") == "Delete?" for p in center.history)
    # simulate user pressing Yes
    responder(True)
    assert results == [True]
