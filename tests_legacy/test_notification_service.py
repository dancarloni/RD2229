from sections_app.services.event_bus import EventBus, NOTIFICATION
from sections_app.services.notification import notify_info, ask_confirm
from sections_app.services.debug_log_stream import get_log_buffer


def test_notify_info_emits_event_and_logs():
    bus = EventBus()
    collected = []

    def cb(payload):
        collected.append(payload)

    # Ensure a clean bus
    bus.clear()
    bus.subscribe(NOTIFICATION, cb)

    notify_info("Test", "Hello world", source="test")

    assert len(collected) == 1
    p = collected[0]
    assert p["level"] == "info"
    assert "Hello world" in p["message"]

    # Debug buffer should contain our message
    buf = get_log_buffer()
    assert any("Test: Hello world" in s for s in buf)


def test_ask_confirm_returns_responder_and_can_invoke_callback():
    results = []

    def cb(answer: bool):
        results.append(answer)

    responder = ask_confirm("Confirm me", "Are you sure?", callback=cb, default=False, source="test")
    # Simulate user clicking 'Yes'
    responder(True)
    assert results == [True]