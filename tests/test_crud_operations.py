"""Test per le operazioni CRUD del repository sezioni.

Verifica create, update, delete e gestione dei casi limite.
"""

import sys

import pytest

sys.path.insert(0, ".")

from sections_app.models.sections import RectangularSection
from sections_app.services.event_bus import (
    SECTIONS_ADDED,
    SECTIONS_DELETED,
    SECTIONS_UPDATED,
    EventBus,
)
from sections_app.services.repository import GeometryRepository


@pytest.fixture
def tmp_json(tmp_path):
    """Create a temporary JSON file for the repository."""
    p = tmp_path / "test_sections.jsons"
    p.write_text("[]", encoding="utf-8")
    return str(p)


@pytest.fixture
def repo(tmp_json):
    """Create a fresh repository with an empty JSON file."""
    return GeometryRepository(json_file=tmp_json, auto_migrate=False)


class TestCreateSection:
    """Test adding sections to the repository."""

    def test_add_section_returns_true(self, repo):
        sec = RectangularSection("test", 30, 50)
        assert repo.add_section(sec) is True

    def test_add_section_persisted(self, repo):
        sec = RectangularSection("test", 30, 50)
        repo.add_section(sec)
        sections = repo.get_all_sections()
        names = [s.name for s in sections]
        assert "test" in names

    def test_add_section_computes_properties(self, repo):
        sec = RectangularSection("test", 30, 50)
        repo.add_section(sec)
        found = repo.find_by_id(sec.id)
        assert found is not None
        assert found.properties is not None
        assert found.properties.area == pytest.approx(1500.0)

    def test_add_duplicate_returns_false(self, repo):
        sec1 = RectangularSection("test1", 30, 50)
        sec2 = RectangularSection("test2", 30, 50)  # same dimensions = same logical key
        assert repo.add_section(sec1) is True
        assert repo.add_section(sec2) is False

    def test_add_emits_event(self, repo):
        events = []
        bus = EventBus()
        bus.subscribe(SECTIONS_ADDED, lambda *a, **kw: events.append(kw))
        try:
            sec = RectangularSection("test", 30, 50)
            repo.add_section(sec)
            assert len(events) == 1
            assert events[0]["section_name"] == "test"
        finally:
            bus.unsubscribe(SECTIONS_ADDED, events.append)


class TestUpdateSection:
    """Test updating sections in the repository."""

    def test_update_changes_properties(self, repo):
        sec = RectangularSection("original", 30, 50)
        repo.add_section(sec)
        sid = sec.id

        updated = RectangularSection("updated", 40, 60)
        repo.update_section(sid, updated)

        found = repo.find_by_id(sid)
        assert found.name == "updated"
        assert found.properties.area == pytest.approx(2400.0)

    def test_update_preserves_id(self, repo):
        sec = RectangularSection("original", 30, 50)
        repo.add_section(sec)
        sid = sec.id

        updated = RectangularSection("updated", 40, 60)
        repo.update_section(sid, updated)

        assert repo.find_by_id(sid) is not None

    def test_update_nonexistent_raises(self, repo):
        updated = RectangularSection("new", 30, 50)
        with pytest.raises(KeyError):
            repo.update_section("nonexistent-id", updated)

    def test_update_duplicate_key_raises(self, repo):
        sec1 = RectangularSection("first", 30, 50)
        sec2 = RectangularSection("second", 40, 60)
        repo.add_section(sec1)
        repo.add_section(sec2)

        # Try to update sec2 with same dimensions as sec1
        conflict = RectangularSection("conflict", 30, 50)
        with pytest.raises(ValueError):
            repo.update_section(sec2.id, conflict)

    def test_update_emits_event(self, repo):
        events = []
        bus = EventBus()
        handler = lambda *a, **kw: events.append(kw)
        bus.subscribe(SECTIONS_UPDATED, handler)
        try:
            sec = RectangularSection("original", 30, 50)
            repo.add_section(sec)
            updated = RectangularSection("updated", 40, 60)
            repo.update_section(sec.id, updated)
            assert any(e.get("section_name") == "updated" for e in events)
        finally:
            bus.unsubscribe(SECTIONS_UPDATED, handler)


class TestDeleteSection:
    """Test deleting sections from the repository."""

    def test_delete_returns_true(self, repo):
        sec = RectangularSection("test", 30, 50)
        repo.add_section(sec)
        assert repo.delete_section(sec.id) is True

    def test_delete_removes_section(self, repo):
        sec = RectangularSection("test", 30, 50)
        repo.add_section(sec)
        repo.delete_section(sec.id)
        assert repo.find_by_id(sec.id) is None

    def test_delete_nonexistent_returns_false(self, repo):
        assert repo.delete_section("nonexistent-id") is False

    def test_delete_emits_event(self, repo):
        events = []
        bus = EventBus()
        handler = lambda *a, **kw: events.append(kw)
        bus.subscribe(SECTIONS_DELETED, handler)
        try:
            sec = RectangularSection("test", 30, 50)
            repo.add_section(sec)
            repo.delete_section(sec.id)
            assert any(e.get("section_name") == "test" for e in events)
        finally:
            bus.unsubscribe(SECTIONS_DELETED, handler)

    def test_delete_persisted_after_reload(self, tmp_json):
        """Verify deletion persists by reloading from file."""
        repo1 = GeometryRepository(json_file=tmp_json, auto_migrate=False)
        sec = RectangularSection("test", 30, 50)
        repo1.add_section(sec)
        sid = sec.id

        repo1.delete_section(sid)

        # Reload from same file - section should be gone
        repo2 = GeometryRepository(json_file=tmp_json, auto_migrate=False)
        assert repo2.find_by_id(sid) is None


class TestPersistence:
    """Test that repository state is correctly persisted and reloaded."""

    def test_save_and_reload(self, tmp_json):
        repo1 = GeometryRepository(json_file=tmp_json, auto_migrate=False)
        sec = RectangularSection("persisted", 30, 50)
        repo1.add_section(sec)

        # Create new repo from same file
        repo2 = GeometryRepository(json_file=tmp_json, auto_migrate=False)
        found = repo2.find_by_id(sec.id)
        assert found is not None
        assert found.name == "persisted"
        assert found.properties.area == pytest.approx(1500.0)

    def test_logical_key_preserved_after_reload(self, tmp_json):
        repo1 = GeometryRepository(json_file=tmp_json, auto_migrate=False)
        sec1 = RectangularSection("first", 30, 50)
        repo1.add_section(sec1)

        # Reload and try adding duplicate
        repo2 = GeometryRepository(json_file=tmp_json, auto_migrate=False)
        sec2 = RectangularSection("duplicate", 30, 50)
        assert repo2.add_section(sec2) is False  # Should detect duplicate
