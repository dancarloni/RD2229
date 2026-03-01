"""Test migrazione ProjectModel.

Verifica che un dizionario di una versione precedente (simulata, senza
schema_version) venga correttamente migrato alla versione corrente.
"""

from __future__ import annotations

import json

from src.project.repository import load_project, migrate_dict
from src.project.schema import CURRENT_SCHEMA_VERSION, ProjectModel


def _legacy_dict_no_version() -> dict:
    """Simula un file progetto senza schema_version (versione pre-1.0.0)."""
    return {
        # schema_version assente intenzionalmente
        "project_info": {"name": "Legacy Project", "author": "Old Author"},
        "geometry": [{"id": "T1", "type": "RECTANGULAR", "width": 25.0, "height": 40.0}],
        "materials": [{"id": "C20", "type": "concrete", "f_ck": 20.0}],
        # loads, seismic_inputs, code_settings, results_ref assenti
    }


def test_migrate_adds_schema_version():
    """migrate_dict deve aggiungere schema_version se mancante."""
    data = _legacy_dict_no_version()
    assert "schema_version" not in data

    migrated = migrate_dict(data)

    assert migrated["schema_version"] == CURRENT_SCHEMA_VERSION


def test_migrate_adds_missing_sections():
    """migrate_dict deve aggiungere sezioni mancanti con valori di default."""
    data = _legacy_dict_no_version()
    migrated = migrate_dict(data)

    assert "loads" in migrated
    assert "seismic_inputs" in migrated
    assert "code_settings" in migrated
    assert "results_ref" in migrated


def test_migrate_preserves_existing_fields():
    """migrate_dict non deve sovrascrivere campi già presenti."""
    data = _legacy_dict_no_version()
    migrated = migrate_dict(data)

    assert migrated["project_info"]["name"] == "Legacy Project"
    assert migrated["geometry"][0]["id"] == "T1"
    assert migrated["materials"][0]["f_ck"] == 20.0


def test_migrate_idempotent():
    """Applicare migrate_dict due volte deve dare lo stesso risultato."""
    data = _legacy_dict_no_version()
    migrated_once = migrate_dict(data.copy())
    migrated_twice = migrate_dict(migrated_once.copy())

    assert migrated_once["schema_version"] == migrated_twice["schema_version"]


def test_load_project_migrates_legacy_file(tmp_path):
    """load_project deve migrare automaticamente un file legacy e restituire ProjectModel."""
    data = _legacy_dict_no_version()
    path = str(tmp_path / "legacy.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)

    project = load_project(path)

    assert isinstance(project, ProjectModel)
    assert project.schema_version == CURRENT_SCHEMA_VERSION
    assert project.project_info.name == "Legacy Project"
    # Sezioni mancanti devono avere valori di default sensati
    assert project.loads == []
    assert project.code_settings.norm_code == "RD2229"
