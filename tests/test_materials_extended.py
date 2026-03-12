"""Test estesi per il modulo materiali: legno, cataloghi, adapter, validazione."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.materials import (
    Material,
    MaterialRepository,
    crea_acciaio_ntc2018,
    crea_calcestruzzo_ntc2018,
    crea_legno_ntc2018,
    crea_muratura_ntc2018,
    validate_material,
)

# ===========================================================================
# Factory legno
# ===========================================================================


class TestCreaLegno:
    def test_c24(self):
        legno = crea_legno_ntc2018("C24")
        assert legno.famiglia == "legno"
        assert legno.f_mk > 0
        assert legno.f_c0k > 0
        assert legno.E_0_mean > 0
        assert legno.gamma_M == pytest.approx(1.45)

    def test_gl28h(self):
        legno = crea_legno_ntc2018("GL28h")
        assert "lamellare" in legno.descrizione
        assert legno.f_mk > 0
        assert legno.G_mean > 0

    def test_default_class(self):
        legno = crea_legno_ntc2018()
        assert legno.material_id == "legno_C24"

    def test_custom_id(self):
        legno = crea_legno_ntc2018("C30", material_id="mio_legno")
        assert legno.material_id == "mio_legno"

    def test_derivati_calcolati(self):
        legno = crea_legno_ntc2018("C24")
        # f_md = k_mod × f_mk / γ_M = 0.8 × f_mk / 1.45
        f_md = legno.f_md
        expected = 0.8 * legno.f_mk / 1.45
        assert f_md == pytest.approx(expected, rel=0.01)

    def test_f_t0d(self):
        legno = crea_legno_ntc2018("C24")
        f_t0d = legno.f_t0d
        expected = 0.8 * legno.f_t0k / 1.45
        assert f_t0d == pytest.approx(expected, rel=0.01)

    def test_f_c0d(self):
        legno = crea_legno_ntc2018("C24")
        f_c0d = legno.f_c0d
        expected = 0.8 * legno.f_c0k / 1.45
        assert f_c0d == pytest.approx(expected, rel=0.01)

    def test_e_0_05(self):
        legno = crea_legno_ntc2018("C24")
        e05 = legno.ottieni_derivato("E_0_05")
        expected = legno.E_0_mean * 2.0 / 3.0
        assert e05 == pytest.approx(expected, rel=0.01)


# ===========================================================================
# Validazione legno
# ===========================================================================


class TestValidazioneLegno:
    def test_valido(self):
        legno = crea_legno_ntc2018("C24")
        errors = validate_material(legno)
        assert errors == []

    def test_f_mk_zero(self):
        legno = Material(material_id="test", famiglia="legno", f_mk=0.0, f_c0k=100.0)
        errors = validate_material(legno)
        assert any("f_mk" in e for e in errors)

    def test_f_c0k_zero(self):
        legno = Material(material_id="test", famiglia="legno", f_mk=100.0, f_c0k=0.0)
        errors = validate_material(legno)
        assert any("f_c0k" in e for e in errors)

    def test_classe_servizio_invalida(self):
        legno = Material(
            material_id="test",
            famiglia="legno",
            f_mk=100.0,
            f_c0k=100.0,
            classe_servizio=5,
        )
        errors = validate_material(legno)
        assert any("classe_servizio" in e for e in errors)


# ===========================================================================
# Serializzazione legno
# ===========================================================================


class TestSerializzazioneLegno:
    def test_to_dict_legno(self):
        legno = crea_legno_ntc2018("C24")
        d = legno.to_dict()
        assert d["famiglia"] == "legno"
        assert d["f_mk"] > 0
        assert d["E_0_mean"] > 0
        assert d["G_mean"] > 0
        assert "classe_servizio" in d

    def test_roundtrip(self):
        legno = crea_legno_ntc2018("GL28h")
        d = legno.to_dict()
        restored = Material.from_dict(dict(d))
        assert restored.famiglia == "legno"
        assert restored.f_mk == pytest.approx(legno.f_mk)
        assert restored.E_0_mean == pytest.approx(legno.E_0_mean)

    def test_json_roundtrip(self):
        legno = crea_legno_ntc2018("C30")
        json_str = legno.to_json()
        restored = Material.from_json(json_str)
        assert restored.material_id == legno.material_id
        assert restored.f_mk == pytest.approx(legno.f_mk)


# ===========================================================================
# Repository con legno
# ===========================================================================


class TestRepositoryLegno:
    def test_defaults_include_legno(self):
        repo = MaterialRepository()
        count = repo.carica_defaults()
        assert count > 0
        legno_list = repo.list_by_famiglia("legno")
        assert len(legno_list) >= 3  # C24, GL24h, GL28h

    def test_load_save_legno(self, tmp_path):
        repo = MaterialRepository()
        legno = crea_legno_ntc2018("C24")
        repo.add_material(legno)
        path = tmp_path / "test_legno.json"
        repo.save_to_json(path)

        repo2 = MaterialRepository()
        count = repo2.load_from_json(path)
        assert count == 1
        restored = repo2.get("legno_C24")
        assert restored is not None
        assert restored.famiglia == "legno"
        assert restored.f_mk == pytest.approx(legno.f_mk)


# ===========================================================================
# Cataloghi JSON
# ===========================================================================


class TestCataloghi:
    _DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "materials"

    def test_catalogo_ntc2018_exists(self):
        path = self._DATA_DIR / "catalogo_ntc2018.json"
        assert path.exists()
        with open(path) as f:
            data = json.load(f)
        assert len(data) >= 15

    def test_catalogo_rd2229_exists(self):
        path = self._DATA_DIR / "catalogo_rd2229.json"
        assert path.exists()
        with open(path) as f:
            data = json.load(f)
        assert len(data) >= 8

    def test_catalogo_legno_exists(self):
        path = self._DATA_DIR / "catalogo_legno.json"
        assert path.exists()
        with open(path) as f:
            data = json.load(f)
        assert len(data) >= 6

    def test_load_ntc2018_catalog(self):
        repo = MaterialRepository()
        path = self._DATA_DIR / "catalogo_ntc2018.json"
        count = repo.load_from_json(path)
        assert count >= 15

        # Verifica un calcestruzzo
        c25 = repo.get("cls_C25/30")
        assert c25 is not None
        assert c25.famiglia == "calcestruzzo"
        assert c25.f_ck == pytest.approx(254.9, abs=1)

    def test_load_legno_catalog(self):
        repo = MaterialRepository()
        path = self._DATA_DIR / "catalogo_legno.json"
        count = repo.load_from_json(path)
        assert count >= 6

        c24 = repo.get("legno_C24")
        assert c24 is not None
        assert c24.famiglia == "legno"


# ===========================================================================
# Adapter core_calculus ↔ materials
# ===========================================================================


class TestAdapter:
    def test_concrete_to_core(self):
        from src.core_calculus.core.materials import Concrete as CoreConcrete
        from src.materials.adapter import material_to_core

        cls = crea_calcestruzzo_ntc2018("C25/30")
        core = material_to_core(cls)
        assert isinstance(core, CoreConcrete)
        # f_ck: 254.9 kg/cm² ≈ 25.0 MPa
        assert core.f_ck == pytest.approx(25.0, abs=0.5)
        assert core.gamma_c == pytest.approx(1.50)

    def test_steel_to_core(self):
        from src.core_calculus.core.materials import Steel as CoreSteel
        from src.materials.adapter import material_to_core

        acc = crea_acciaio_ntc2018("B450C")
        core = material_to_core(acc)
        assert isinstance(core, CoreSteel)
        # f_yk: 4589 kg/cm² ≈ 450 MPa
        assert core.f_yk == pytest.approx(450.0, abs=1.0)

    def test_roundtrip_concrete(self):
        from src.materials.adapter import core_to_material, material_to_core

        original = crea_calcestruzzo_ntc2018("C30/37")
        core = material_to_core(original)
        back = core_to_material(core)
        assert back.famiglia == "calcestruzzo"
        assert back.f_ck == pytest.approx(original.f_ck, rel=0.01)

    def test_roundtrip_steel(self):
        from src.materials.adapter import core_to_material, material_to_core

        original = crea_acciaio_ntc2018("B450C")
        core = material_to_core(original)
        back = core_to_material(core)
        assert back.famiglia == "acciaio"
        assert back.f_yk == pytest.approx(original.f_yk, rel=0.01)

    def test_masonry_to_core_generic(self):
        from src.core_calculus.core.materials import Material as CoreMaterial
        from src.materials.adapter import material_to_core

        mur = crea_muratura_ntc2018("mattoni_pieni", "M10")
        core = material_to_core(mur)
        assert isinstance(core, CoreMaterial)
        assert core.material_type == "muratura"
