"""Centralised diagnostics service for the rd2229 project.

Provides a singleton ``DiagnosticsService`` for session-scoped event
recording, structured querying, and replay.  Events are correlated to a
*session_id* (typically a run-ID from ``src.project.timeline``) so that
all tool/verifier/UI activity can be attributed to a specific run.

Usage::

    from src.rd2229.diagnostics import get_diagnostics

    diag = get_diagnostics()
    sid = diag.start_session(session_id="run_20260101_120000_abc1234")
    diag.record_event(sid, "verifier", "SLU_FLESSIONE", "ok", {"utilisation": 0.72})

    events = diag.query_events(session_id=sid, source="verifier")

Integration points:
    - ``tools/diagnose.py`` – CLI for querying persisted events
    - ``src.project.timeline`` – RunRecord provides run_id as session_id
    - GUI: bind DiagnosticsService.query_events to a log-viewer widget

Thread safety: internal list is append-only; no locks needed for simple
single-process use; multi-threaded writers should use ``thread_safe=True``
(wraps mutations in a ``threading.Lock``).
"""

from __future__ import annotations

import json
import threading
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from src.rd2229.logging_bridge import get_logger

logger = get_logger("diagnostics")


@dataclass
class DiagnosticEvent:
    """A single recorded diagnostic event."""

    session_id: str
    timestamp: str
    source: str       # e.g. "verifier", "pipeline", "gui", "tool"
    event_type: str   # e.g. "check_result", "error", "warning", "info"
    payload: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "timestamp": self.timestamp,
            "source": self.source,
            "event_type": self.event_type,
            "payload": self.payload,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "DiagnosticEvent":
        return cls(
            session_id=d.get("session_id", ""),
            timestamp=d.get("timestamp", ""),
            source=d.get("source", ""),
            event_type=d.get("event_type", ""),
            payload=d.get("payload", {}),
        )


class DiagnosticsService:
    """Singleton diagnostics service.

    All public methods are safe to call before ``start_session``; events
    without a session are stored under the ``"_no_session"`` pseudo-ID.
    """

    _instance: "DiagnosticsService | None" = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls) -> "DiagnosticsService":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    inst = super().__new__(cls)
                    inst._initialized = False
                    cls._instance = inst
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self._events: list[DiagnosticEvent] = []
        self._sessions: dict[str, dict[str, Any]] = {}
        self._write_lock = threading.Lock()

    # ------------------------------------------------------------------
    # Session management
    # ------------------------------------------------------------------

    def start_session(
        self,
        session_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Start (or resume) a diagnostics session.

        Parameters
        ----------
        session_id:
            Explicit run-ID (e.g. from ``RunRecord.run_id``).  If omitted a
            timestamp-based ID is generated automatically.
        metadata:
            Arbitrary key/value data attached to the session (project_id,
            python_version, norm_code, …).

        Returns
        -------
        str
            The session_id to pass to :meth:`record_event`.
        """
        if session_id is None:
            session_id = "diag_" + datetime.now(UTC).strftime("%Y%m%d_%H%M%S_%f")
        with self._write_lock:
            self._sessions[session_id] = {
                "session_id": session_id,
                "started": datetime.now(UTC).isoformat(),
                "metadata": metadata or {},
                "event_count": 0,
            }
        logger.info("DiagnosticsService: session started — %s", session_id)
        return session_id

    def end_session(self, session_id: str) -> None:
        """Mark a session as ended."""
        with self._write_lock:
            if session_id in self._sessions:
                self._sessions[session_id]["ended"] = datetime.now(UTC).isoformat()
        logger.info("DiagnosticsService: session ended — %s", session_id)

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        """Return session metadata, or None if not found."""
        return self._sessions.get(session_id)

    def list_sessions(self) -> list[dict[str, Any]]:
        """Return all registered sessions."""
        return list(self._sessions.values())

    # ------------------------------------------------------------------
    # Event recording
    # ------------------------------------------------------------------

    def record_event(
        self,
        session_id: str,
        source: str,
        event_type: str,
        payload: dict[str, Any] | None = None,
    ) -> DiagnosticEvent:
        """Record a diagnostic event.

        Parameters
        ----------
        session_id:
            Session returned by :meth:`start_session`.
        source:
            Component that generated the event (``"verifier"``,
            ``"pipeline"``, ``"gui"``, ``"tool"``, …).
        event_type:
            Event category / name (e.g. ``"check_result"``, ``"error"``).
        payload:
            Arbitrary structured data for the event.
        """
        ev = DiagnosticEvent(
            session_id=session_id,
            timestamp=datetime.now(UTC).isoformat(),
            source=source,
            event_type=event_type,
            payload=payload or {},
        )
        with self._write_lock:
            self._events.append(ev)
            if session_id in self._sessions:
                self._sessions[session_id]["event_count"] = (
                    self._sessions[session_id].get("event_count", 0) + 1
                )
        logger.debug("DiagnosticsService: [%s] %s/%s", session_id, source, event_type)
        return ev

    # ------------------------------------------------------------------
    # Querying
    # ------------------------------------------------------------------

    def query_events(
        self,
        session_id: str | None = None,
        source: str | None = None,
        event_type: str | None = None,
        since: str | None = None,
        limit: int | None = None,
    ) -> list[DiagnosticEvent]:
        """Query recorded events with optional filters.

        Parameters
        ----------
        session_id:
            Filter to a specific session.
        source:
            Filter by source component.
        event_type:
            Filter by event type.
        since:
            ISO-8601 timestamp; only events on or after this time are returned.
        limit:
            Maximum number of results (most-recent first when provided).
        """
        events = list(self._events)

        if session_id is not None:
            events = [e for e in events if e.session_id == session_id]
        if source is not None:
            events = [e for e in events if e.source == source]
        if event_type is not None:
            events = [e for e in events if e.event_type == event_type]
        if since is not None:
            events = [e for e in events if e.timestamp >= since]
        if limit is not None:
            events = events[-limit:]

        return events

    def clear(self) -> None:
        """Remove all events and sessions (for testing / reset)."""
        with self._write_lock:
            self._events.clear()
            self._sessions.clear()
        logger.debug("DiagnosticsService: cleared")

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def dump_session(self, session_id: str) -> dict[str, Any]:
        """Return a serialisable dict for a session and its events."""
        events = self.query_events(session_id=session_id)
        return {
            "session": self._sessions.get(session_id, {"session_id": session_id}),
            "events": [e.to_dict() for e in events],
        }

    def dump_all(self) -> dict[str, Any]:
        """Return all sessions and events as a serialisable dict."""
        return {
            "_generated": datetime.now(UTC).isoformat(),
            "sessions": list(self._sessions.values()),
            "events": [e.to_dict() for e in self._events],
        }

    def save_to_file(self, path: str) -> None:
        """Persist all diagnostics data to a JSON file."""
        from pathlib import Path as _Path
        _Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(self.dump_all(), fh, indent=2, ensure_ascii=False, sort_keys=True)
        logger.info("DiagnosticsService: saved to %s", path)

    def load_from_file(self, path: str) -> int:
        """Load events from a previously saved JSON file.  Returns event count loaded."""
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        count = 0
        for s in data.get("sessions", []):
            sid = s.get("session_id", "")
            if sid and sid not in self._sessions:
                with self._write_lock:
                    self._sessions[sid] = s
        for ev_d in data.get("events", []):
            ev = DiagnosticEvent.from_dict(ev_d)
            with self._write_lock:
                self._events.append(ev)
            count += 1
        logger.info("DiagnosticsService: loaded %d events from %s", count, path)
        return count


def get_diagnostics() -> DiagnosticsService:
    """Return the singleton DiagnosticsService instance."""
    return DiagnosticsService()


def reset_diagnostics() -> None:
    """Reset the singleton (for testing only)."""
    DiagnosticsService._instance = None
