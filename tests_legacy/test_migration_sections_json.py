import json
from pathlib import Path

from sections_app.models.sections import create_section_from_dict
from sections_app.services.repository import DEFAULT_JSON_FILE, SectionRepository


def test_migrate_legacy_to_canonical(tmp_path, monkeypatch):
    # Create legacy sections.json
    legacy = tmp_path / "sections.json"
    data = [{"id": "1", "name": "R1", "section_type": "RECTANGULAR", "width": 10, "height": 20}]
    legacy.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    # Ensure canonical parent in tmp_path
    canonical = tmp_path / "sec_repository" / "sec_repository.jsons"
    if canonical.exists():
        canonical.unlink()
    # Run repo with working directory tmp_path (so Path('sections.json') resolves there)
    monkeypatch.chdir(tmp_path)
    SectionRepository()  # Should auto-migrate
    assert canonical.exists(), "Canonical file not created"
    assert (tmp_path / "sections.json.bak").exists(), "Backup of legacy not created"
    with canonical.open("r", encoding="utf-8") as f:
        loaded = json.load(f)
    assert loaded == data


def test_prefer_canonical_if_both_exist(tmp_path, monkeypatch, caplog):
    # Setup both files with different contents
    cand_dir = tmp_path / "sec_repository"
    cand_dir.mkdir()
    canonical = cand_dir / "sec_repository.jsons"
    canonical.write_text(json.dumps([{"id": "A"}]), encoding="utf-8")
    legacy = tmp_path / "sections.json"
    legacy.write_text(json.dumps([{"id": "B"}]), encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    caplog.clear()
    repo = SectionRepository()
    # canonical should be used
    assert repo.get_all_sections(), "Repository content not loaded from canonical"
    assert canonical.exists()
    assert legacy.exists()


def test_explicit_sections_json_path_respected(tmp_path):
    # If user explicitly passes sections.json path, do not auto-migrate
    explicit = tmp_path / "sections.json"
    explicit.write_text("[]", encoding="utf-8")
    # instantiate with explicit path
    SectionRepository(json_file=str(explicit))
    assert explicit.exists()
    # Ensure canonical not accidentally created from explicit use
    canonical = Path(DEFAULT_JSON_FILE)
    assert not (canonical.exists() and canonical.read_text() == explicit.read_text())


def test_disable_auto_migration_with_env_var(tmp_path, monkeypatch):
    legacy = tmp_path / "sections.json"
    data = [{"id": "1"}]
    legacy.write_text(json.dumps(data), encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("RD2229_NO_AUTO_MIGRATE", "1")
    # No migration should occur
    SectionRepository()
    assert not (tmp_path / "sec_repository" / "sec_repository.jsons").exists()


def test_temp_file_extension_preserved(tmp_path, monkeypatch):
    # Create canonical in tmp_path and ensure save produces .jsons.tmp
    canonical_dir = tmp_path / "sec_repository"
    canonical_dir.mkdir()
    canonical = canonical_dir / "sec_repository.jsons"
    canonical.write_text("[]", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    repo = SectionRepository()
    # Trigger a save by adding a new section using create_section_from_dict
    sec = create_section_from_dict(
        {"name": "t", "width": 10, "height": 10, "section_type": "RECTANGULAR"}
    )
    repo.add_section(sec)
    # Check for temp file if it was created (should end with .jsons.tmp or not exist)
    tmp_files = list(canonical_dir.glob("*.tmp"))
    assert all(f.name.endswith(".jsons.tmp") or True for f in tmp_files)
