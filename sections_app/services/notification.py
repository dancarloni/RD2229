"""
Notification service: non-blocking user notifications that emit EventBus NOTIFICATION
and also append to the in-memory log so the Debug Viewer can display them.

This provides convenience functions `notify_info`, `notify_warning`, `notify_error`
and a non-blocking `ask_confirm` which emits a confirm payload including a
`respond` callback that UI code (NotificationCenter) can call.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Callable, Dict, Optional

from sections_app.services.debug_log_stream import emit_to_in_memory_buffer
from sections_app.services.event_bus import NOTIFICATION, EventBus

logger = logging.getLogger(__name__)


def _emit(payload: Dict[str, Any]) -> None:
    """Emit a NOTIFICATION event and write to in-memory log."""
    EventBus().emit(NOTIFICATION, payload)
    try:
        level = payload.get("level", "info")
        title = payload.get("title", "")
        message = payload.get("message", "")
        text = f"{title}: {message}"
        if level == "info":
            emit_to_in_memory_buffer(logging.INFO, text)
        elif level == "warning":
            emit_to_in_memory_buffer(logging.WARNING, text)
        else:
            emit_to_in_memory_buffer(logging.ERROR, text)
    except Exception:
        logger.exception("Failed to emit notification log")


def notify_info(
    title: str, message: str, *, source: Optional[str] = None, meta: Optional[dict] = None
) -> None:
    _emit(
        {
            "level": "info",
            "title": title,
            "message": message,
            "source": source,
            "meta": meta,
            "timestamp": time.time(),
        }
    )


def notify_warning(
    title: str, message: str, *, source: Optional[str] = None, meta: Optional[dict] = None
) -> None:
    _emit(
        {
            "level": "warning",
            "title": title,
            "message": message,
            "source": source,
            "meta": meta,
            "timestamp": time.time(),
        }
    )


def notify_error(
    title: str, message: str, *, source: Optional[str] = None, meta: Optional[dict] = None
) -> None:
    _emit(
        {
            "level": "error",
            "title": title,
            "message": message,
            "source": source,
            "meta": meta,
            "timestamp": time.time(),
        }
    )


def ask_confirm(
    title: str,
    message: str,
    *,
    callback: Optional[Callable[[bool], None]] = None,
    default: bool = False,
    source: Optional[str] = None,
    meta: Optional[dict] = None,
) -> Callable[[bool], None]:
    """Emit a confirm notification payload and return a responder function.

    The caller may provide a `callback` which will be invoked when the user
    responds (NotificationCenter should call `respond(True|False)` when the
    user clicks Yes/No). For test-friendly behavior the function returns the
    `respond` closure so tests can simulate a response.
    """
    responded = {"done": False}

    def respond(answer: bool) -> None:
        responded["done"] = True
        try:
            if callback:
                callback(answer)
            # Also log a small note for traceability
            emit_to_in_memory_buffer(
                logging.INFO, f"Confirm '{title}': {'Yes' if answer else 'No'}"
            )
        except Exception:
            logger.exception("Error in confirm callback")

    payload = {
        "level": "confirm",
        "title": title,
        "message": message,
        "respond": respond,
        "source": source,
        "meta": meta,
        "timestamp": time.time(),
    }
    _emit(payload)
    # Return responder for programmatic handling (tests or non-UI flows)
    return respond
