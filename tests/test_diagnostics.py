"""Tests for src/rd2229/diagnostics.py – DiagnosticsService."""

from __future__ import annotations

import json
import sys
import threading
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.rd2229.diagnostics import (
    DiagnosticEvent,
    DiagnosticsService,
    get_diagnostics,
    reset_diagnostics,
)


@pytest.fixture(autouse=True)
def fresh_diagnostics():
    """Reset singleton before each test."""
    reset_diagnostics()
    yield
    reset_diagnostics()


# ---------------------------------------------------------------------------
# Singleton behaviour
# ---------------------------------------------------------------------------


class TestSingleton:
    def test_same_instance(self):
        d1 = get_diagnostics()
        d2 = get_diagnostics()
        assert d1 is d2

    def test_reset_creates_new_instance(self):
        d1 = get_diagnostics()
        reset_diagnostics()
        d2 = get_diagnostics()
        assert d1 is not d2


# ---------------------------------------------------------------------------
# Session management
# ---------------------------------------------------------------------------


class TestSessions:
    def test_start_session_returns_id(self):
        diag = get_diagnostics()
        sid = diag.start_session()
        assert isinstance(sid, str)
        assert sid.startswith("diag_")

    def test_explicit_session_id(self):
        diag = get_diagnostics()
        sid = diag.start_session(session_id="run_20260101_120000_abc1234")
        assert sid == "run_20260101_120000_abc1234"

    def test_session_stored(self):
        diag = get_diagnostics()
        sid = diag.start_session(session_id="test_sess")
        s = diag.get_session(sid)
        assert s is not None
        assert s["session_id"] == "test_sess"

    def test_session_metadata(self):
        diag = get_diagnostics()
        sid = diag.start_session(metadata={"project_id": "proj_1", "norm": "NTC2018"})
        s = diag.get_session(sid)
        assert s["metadata"]["project_id"] == "proj_1"

    def test_list_sessions(self):
        diag = get_diagnostics()
        diag.start_session(session_id="s1")
        diag.start_session(session_id="s2")
        sessions = diag.list_sessions()
        ids = [s["session_id"] for s in sessions]
        assert "s1" in ids
        assert "s2" in ids

    def test_end_session(self):
        diag = get_diagnostics()
        sid = diag.start_session(session_id="sess_end")
        diag.end_session(sid)
        s = diag.get_session(sid)
        assert "ended" in s


# ---------------------------------------------------------------------------
# Event recording
# ---------------------------------------------------------------------------


class TestRecordEvent:
    def test_record_returns_event(self):
        diag = get_diagnostics()
        sid = diag.start_session()
        ev = diag.record_event(sid, "verifier", "check_result", {"ok": True})
        assert isinstance(ev, DiagnosticEvent)
        assert ev.session_id == sid
        assert ev.source == "verifier"
        assert ev.event_type == "check_result"
        assert ev.payload["ok"] is True

    def test_event_has_timestamp(self):
        diag = get_diagnostics()
        sid = diag.start_session()
        ev = diag.record_event(sid, "tool", "info")
        assert ev.timestamp  # non-empty ISO timestamp

    def test_session_event_count_incremented(self):
        diag = get_diagnostics()
        sid = diag.start_session(session_id="count_test")
        diag.record_event(sid, "verifier", "a")
        diag.record_event(sid, "verifier", "b")
        s = diag.get_session(sid)
        assert s["event_count"] == 2


# ---------------------------------------------------------------------------
# Querying
# ---------------------------------------------------------------------------


class TestQueryEvents:
    def _populate(self, diag):
        s1 = diag.start_session(session_id="sess_A")
        s2 = diag.start_session(session_id="sess_B")
        diag.record_event(s1, "verifier", "check_result", {"ok": True})
        diag.record_event(s1, "pipeline", "step_complete")
        diag.record_event(s2, "verifier", "error", {"msg": "failed"})
        diag.record_event(s2, "gui", "click")
        return s1, s2

    def test_query_all(self):
        diag = get_diagnostics()
        self._populate(diag)
        events = diag.query_events()
        assert len(events) == 4

    def test_filter_by_session(self):
        diag = get_diagnostics()
        s1, s2 = self._populate(diag)
        events = diag.query_events(session_id=s1)
        assert all(e.session_id == s1 for e in events)
        assert len(events) == 2

    def test_filter_by_source(self):
        diag = get_diagnostics()
        self._populate(diag)
        events = diag.query_events(source="verifier")
        assert all(e.source == "verifier" for e in events)
        assert len(events) == 2

    def test_filter_by_event_type(self):
        diag = get_diagnostics()
        self._populate(diag)
        events = diag.query_events(event_type="error")
        assert len(events) == 1
        assert events[0].payload["msg"] == "failed"

    def test_limit(self):
        diag = get_diagnostics()
        sid = diag.start_session()
        for i in range(10):
            diag.record_event(sid, "tool", f"ev_{i}")
        events = diag.query_events(limit=3)
        assert len(events) == 3

    def test_combined_filters(self):
        diag = get_diagnostics()
        s1, _ = self._populate(diag)
        events = diag.query_events(session_id=s1, source="verifier")
        assert len(events) == 1


# ---------------------------------------------------------------------------
# Serialisation (to_dict / from_dict)
# ---------------------------------------------------------------------------


class TestSerialization:
    def test_event_to_dict(self):
        diag = get_diagnostics()
        sid = diag.start_session()
        ev = diag.record_event(sid, "verifier", "check", {"x": 1})
        d = ev.to_dict()
        assert d["source"] == "verifier"
        assert d["event_type"] == "check"
        assert d["payload"]["x"] == 1

    def test_event_from_dict_roundtrip(self):
        diag = get_diagnostics()
        sid = diag.start_session()
        ev = diag.record_event(sid, "pipeline", "done", {"steps": 5})
        d = ev.to_dict()
        ev2 = DiagnosticEvent.from_dict(d)
        assert ev2.source == ev.source
        assert ev2.event_type == ev.event_type
        assert ev2.payload == ev.payload

    def test_dump_session(self):
        diag = get_diagnostics()
        sid = diag.start_session(session_id="dump_test")
        diag.record_event(sid, "verifier", "ok")
        dump = diag.dump_session(sid)
        assert dump["session"]["session_id"] == sid
        assert len(dump["events"]) == 1

    def test_dump_all(self):
        diag = get_diagnostics()
        sid = diag.start_session(session_id="all_test")
        diag.record_event(sid, "tool", "run")
        data = diag.dump_all()
        assert any(s["session_id"] == sid for s in data["sessions"])
        assert len(data["events"]) == 1

    def test_save_and_load_file(self, tmp_path):
        diag = get_diagnostics()
        sid = diag.start_session(session_id="file_test")
        diag.record_event(sid, "verifier", "result", {"ok": False})

        save_path = str(tmp_path / "diag.json")
        diag.save_to_file(save_path)

        # Reset and load
        reset_diagnostics()
        diag2 = get_diagnostics()
        count = diag2.load_from_file(save_path)
        assert count == 1
        events = diag2.query_events(session_id=sid)
        assert len(events) == 1
        assert events[0].payload["ok"] is False


# ---------------------------------------------------------------------------
# Thread safety
# ---------------------------------------------------------------------------


class TestThreadSafety:
    def test_concurrent_record(self):
        diag = get_diagnostics()
        sid = diag.start_session()
        errors = []

        def worker(n):
            try:
                for _ in range(20):
                    diag.record_event(sid, "worker", f"ev_{n}")
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors
        events = diag.query_events(session_id=sid)
        assert len(events) == 100  # 5 workers × 20 events


# ---------------------------------------------------------------------------
# Clear
# ---------------------------------------------------------------------------


class TestClear:
    def test_clear_removes_all(self):
        diag = get_diagnostics()
        sid = diag.start_session()
        diag.record_event(sid, "tool", "x")
        diag.clear()
        assert diag.query_events() == []
        assert diag.list_sessions() == []
