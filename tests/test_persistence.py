"""Test round-trip per ProjectIndex."""

from __future__ import annotations

from pathlib import Path

from src.core.persistence import ProjectIndex


def test_project_index_upsert_and_list_recent(tmp_path: Path) -> None:
    db_path = tmp_path / "projects.db"
    project_path = tmp_path / "demo.jsonp"
    project_path.write_text('{"name":"demo"}', encoding="utf-8")

    index = ProjectIndex(db_path)
    index.upsert(project_path, "Demo", "RD2229")

    recent = index.list_recent(limit=5)

    assert len(recent) == 1
    assert recent[0].path == str(project_path)
    assert recent[0].name == "Demo"
    assert recent[0].norm_code == "RD2229"
    assert len(recent[0].sha256) == 64


def test_project_index_upsert_updates_existing_entry(tmp_path: Path) -> None:
    db_path = tmp_path / "projects.db"
    project_path = tmp_path / "demo.jsonp"
    project_path.write_text('{"name":"demo"}', encoding="utf-8")

    index = ProjectIndex(db_path)
    index.upsert(project_path, "Demo", "RD2229")
    index.upsert(project_path, "Demo v2", "NTC2018")

    recent = index.list_recent(limit=5)

    assert len(recent) == 1
    assert recent[0].name == "Demo v2"
    assert recent[0].norm_code == "NTC2018"


def test_project_index_handles_missing_file_digest(tmp_path: Path) -> None:
    db_path = tmp_path / "projects.db"
    missing = tmp_path / "missing.jsonp"

    index = ProjectIndex(db_path)
    index.upsert(missing, "Missing", "DM96")

    recent = index.list_recent(limit=5)

    assert len(recent) == 1
    assert recent[0].sha256 == ""
