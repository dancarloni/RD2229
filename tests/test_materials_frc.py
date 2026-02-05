#!/usr/bin/env python3
"""Test per il supporto FRC nella persistenza dei materiali."""

import json
import os
import tempfile

from core_models.materials import Material, MaterialRepository


def test_material_frc_persistence_roundtrip():
    """Crea un materiale con campi FRC, salva e ricarica dal repository."""
    with tempfile.TemporaryDirectory() as tmpdir:
        json_file = os.path.join(tmpdir, "test_materials_frc.json")
        repo = MaterialRepository(json_file=json_file)

        # Crea materiale con FRC
        mat = Material(
            name="CFRP_1",
            type="frc",
            properties={"Ec": 30000},
            frc_enabled=True,
            frc_fFts=2500.0,
            frc_fFtu=3000.0,
            frc_eps_fu=0.02,
            frc_note="Carbon fiber, manual entry"
        )
        repo.add(mat)

        # Verifica file creato
        assert os.path.isfile(json_file), "File JSON non creato"

        # Ricarica repository
        repo2 = MaterialRepository(json_file=json_file)
        loaded = repo2.find_by_name("CFRP_1")
        assert loaded is not None, "Materiale FRC non ricaricato"
        assert loaded.frc_enabled is True
        assert loaded.frc_fFts == 2500.0
        assert loaded.frc_fFtu == 3000.0
        assert loaded.frc_eps_fu == 0.02
        assert loaded.frc_note == "Carbon fiber, manual entry"


def test_material_frc_defaults_for_legacy_json():
    """Se i campi FRC mancano nel JSON, devono avere valori di default (disabled/None)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        json_file = os.path.join(tmpdir, "legacy_materials.json")
        # Simula file legacy senza campi FRC
        data = [
            {"id": "m1", "name": "C120", "type": "concrete", "properties": {"fck": 120}},
        ]
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        repo = MaterialRepository(json_file=json_file)
        m = repo.find_by_name("C120")
        assert m is not None
        assert m.frc_enabled is False
        assert m.frc_fFts is None
        assert m.frc_fFtu is None
        assert m.frc_eps_fu is None


def test_material_to_from_dict_roundtrip():
    mat = Material(
        name="CFRP_2",
        type="frc",
        frc_enabled=True,
        frc_fFts=1200.0,
        frc_fFtu=1500.0,
        frc_eps_fu=0.015,
        frc_note="Sample"
    )
    d = mat.to_dict()
    m2 = Material.from_dict(d)

    assert m2.frc_enabled is True
    assert m2.frc_fFts == 1200.0
    assert m2.frc_fFtu == 1500.0
    assert m2.frc_eps_fu == 0.015
    assert m2.frc_note == "Sample"
