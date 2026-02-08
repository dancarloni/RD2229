#!/usr/bin/env python3
"""Simple EventBus for notifying UI windows of repository changes.

This provides a lightweight pub/sub system to decouple the repository
operations from the UI update logic.
"""

import logging
from collections.abc import Callable
from typing import Optional

logger = logging.getLogger(__name__)


class EventBus:
    """Simple event bus for application-wide events."""

    _instance: Optional["EventBus"] = None

    def __new__(cls) -> "EventBus":
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._initialized = True
        self._listeners: dict[str, list[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable) -> None:
        """Subscribe to an event type.

        Args:
            event_type: Type of event (e.g., "sections_changed", "materials_changed")
            callback: Function to call when event is emitted

        """
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)
        logger.debug(f"Subscribed to event: {event_type}")

    def unsubscribe(self, event_type: str, callback: Callable) -> None:
        """Unsubscribe from an event type.

        Args:
            event_type: Type of event
            callback: Function to unsubscribe

        """
        if event_type in self._listeners:
            try:
                self._listeners[event_type].remove(callback)
                logger.debug(f"Unsubscribed from event: {event_type}")
            except ValueError:
                logger.warning(f"Callback not found for event: {event_type}")

    def emit(self, event_type: str, *args, **kwargs) -> None:
        """Emit an event.

        Args:
            event_type: Type of event
            *args, **kwargs: Arguments to pass to callbacks

        """
        if event_type not in self._listeners:
            logger.debug(f"No listeners for event: {event_type}")
            return

        logger.debug(f"Emitting event: {event_type}")
        for callback in self._listeners[event_type]:
            try:
                callback(*args, **kwargs)
            except Exception as e:
                logger.exception(f"Error calling callback for {event_type}: {e}")

    def clear(self) -> None:
        """Clear all listeners (useful for testing)."""
        self._listeners.clear()
        logger.debug("Cleared all event listeners")


# Event types
SECTIONS_ADDED = "sections_added"
SECTIONS_UPDATED = "sections_updated"
SECTIONS_DELETED = "sections_deleted"
SECTIONS_CLEARED = "sections_cleared"

MATERIALS_ADDED = "materials_added"
MATERIALS_UPDATED = "materials_updated"
MATERIALS_DELETED = "materials_deleted"
MATERIALS_CLEARED = "materials_cleared"

# Generic notification event for user-facing non-blocking messages
NOTIFICATION = "notification"
