"""Test roundtrip ProjectModel: crea → save → load → verifica uguaglianza campi."""

from __future__ import annotations

import pytest

pytest.importorskip("pydantic")

import json
import os

from src.project.repository import load_project, save_project
from src.project.schema import (
    CodeSettings,
    GeometryEntry,
    LoadEntry,
    MaterialEntry,
    ProjectInfo,
    ProjectModel,
    SeismicInputs,
)


def _make_minimal_project() -> ProjectModel:
    """Crea un ProjectModel minimale ma completo per i test."""
    return ProjectModel(
        project_info=ProjectInfo(
            name="Test Project",
            description="Progetto di test roundtrip",
            author="Pytest",
            created_at="2026-01-01T00:00:00",
            updated_at="2026-01-01T00:00:00",
        ),
        geometry=[
            GeometryEntry(id="P1", type="RECTANGULAR", width=30.0, height=50.0),
        ],
        materials=[
            MaterialEntry(id="C25", type="concrete", material_class="C25/30", f_ck=25.0),
            MaterialEntry(id="B450C", type="steel", material_class="B450C", f_yk=450.0),
        ],
        loads=[
            LoadEntry(element_id="P1", N=100.0, Mx=50.0, description="Combo 1"),
        ],
        seismic_inputs=SeismicInputs(class_of_use="II", vita_nominale_years=50),
        code_settings=CodeSettings(norm_code="RD2229", limit_states=["TA"]),
    )


def test_project_roundtrip_key_fields(tmp_path):
    """save_project → load_project non deve perdere i campi principali."""
    project = _make_minimal_project()
    path = str(tmp_path / "test_project.json")

    save_project(project, path)
    loaded = load_project(path)

    # Campi chiave del ProjectModel
    assert loaded.schema_version == project.schema_version
    assert loaded.project_info.name == project.project_info.name
    assert loaded.project_info.author == project.project_info.author

    # Geometria
    assert len(loaded.geometry) == 1
    assert loaded.geometry[0].id == "P1"
    assert loaded.geometry[0].width == 30.0
    assert loaded.geometry[0].height == 50.0

    # Materiali
    assert len(loaded.materials) == 2
    conc = next(m for m in loaded.materials if m.id == "C25")
    assert conc.f_ck == 25.0
    assert conc.material_class == "C25/30"

    # Carichi
    assert len(loaded.loads) == 1
    assert loaded.loads[0].element_id == "P1"
    assert loaded.loads[0].N == 100.0
    assert loaded.loads[0].Mx == 50.0

    # CodeSettings
    assert loaded.code_settings.norm_code == "RD2229"
    assert "TA" in loaded.code_settings.limit_states


def test_project_roundtrip_json_file_exists(tmp_path):
    """Il file JSON deve essere creato e avere contenuto non vuoto."""
    project = _make_minimal_project()
    path = str(tmp_path / "project.json")

    save_project(project, path)

    assert os.path.exists(path)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    assert data["schema_version"] == project.schema_version
    assert data["project_info"]["name"] == "Test Project"


def test_project_roundtrip_no_tmp_file_left(tmp_path):
    """Dopo il salvataggio non devono restare file temporanei .tmp."""
    project = _make_minimal_project()
    path = str(tmp_path / "project.json")

    save_project(project, path)

    assert not os.path.exists(path + ".tmp")
