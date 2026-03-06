"""Test unitari per la struttura dati materiali.

Testa material_model, material_repo e validation.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from materials.material_model import (
    Material,
    ParametroDerivato,
    crea_acciaio_ntc2018,
    crea_calcestruzzo_ntc2018,
    crea_muratura_ntc2018,
)
from materials.material_repo import MaterialRepository
from materials.validation import validate_material


# =====================================================================
# Test Material Model
# =====================================================================


class TestMaterialCreation:
    """Test creazione materiali per ogni famiglia."""

    def test_crea_calcestruzzo_ntc2018(self) -> None:
        mat = crea_calcestruzzo_ntc2018("C25/30")
        assert mat.famiglia == "calcestruzzo"
        assert mat.norma_riferimento == "NTC2018"
        assert mat.f_ck == pytest.approx(254.9, rel=0.01)
        assert mat.gamma_c == 1.50
        assert mat.alpha_cc == 0.85
        assert mat.nu == 0.20

    def test_crea_acciaio_ntc2018(self) -> None:
        mat = crea_acciaio_ntc2018("B450C")
        assert mat.famiglia == "acciaio"
        assert mat.f_yk == pytest.approx(4589.0, rel=0.01)
        assert mat.gamma_s == 1.15
        assert mat.E == pytest.approx(2100000.0)
        assert mat.nu == 0.30

    def test_crea_muratura_ntc2018(self) -> None:
        mat = crea_muratura_ntc2018("mattoni_pieni", "M10")
        assert mat.famiglia == "muratura"
        assert mat.f_k == pytest.approx(36.0)
        assert mat.f_vk0 == pytest.approx(2.0)
        assert mat.gamma_M == 2.0
        assert mat.nu == 0.15

    def test_calcestruzzo_ta_rd2229(self) -> None:
        mat = Material(
            material_id="cls_test_ta",
            famiglia="calcestruzzo",
            norma_riferimento="RD2229",
            sigma_c28=250.0,
            sigma_c_adm=62.5,
            tau_c0_adm=5.5,
            tau_c1_adm=16.0,
            n_omogenizzazione=10.0,
            gamma_c=1.0,
            alpha_cc=1.0,
        )
        assert mat.sigma_c28 == 250.0
        assert mat.sigma_c_adm == 62.5


class TestParametriDerivati:
    """Test parametri derivati automatici."""

    def test_f_cd_calcestruzzo(self) -> None:
        mat = crea_calcestruzzo_ntc2018("C25/30")
        # f_cd = alpha_cc * f_ck / gamma_c = 0.85 * 254.9 / 1.50
        expected = 0.85 * 254.9 / 1.50
        assert mat.f_cd == pytest.approx(expected, rel=0.01)

    def test_f_yd_acciaio(self) -> None:
        mat = crea_acciaio_ntc2018("B450C")
        # f_yd = f_yk / gamma_s = 4589 / 1.15
        expected = 4589.0 / 1.15
        assert mat.f_yd == pytest.approx(expected, rel=0.01)

    def test_G_modulo_taglio(self) -> None:
        mat = crea_acciaio_ntc2018("B450C")
        # G = E / (2 * (1 + nu)) = 2100000 / (2 * 1.30)
        expected = 2100000.0 / (2.0 * 1.30)
        assert mat.G == pytest.approx(expected, rel=0.01)

    def test_f_ctm_calcestruzzo(self) -> None:
        mat = crea_calcestruzzo_ntc2018("C25/30")
        assert mat.f_ctm > 0
        # f_ctm = 0.30 * f_ck_mpa^(2/3) converted to kg/cm²
        f_ck_mpa = 254.9 * 0.0980665
        f_ctm_mpa = 0.30 * f_ck_mpa ** (2.0 / 3.0)
        expected = f_ctm_mpa / 0.0980665
        assert mat.f_ctm == pytest.approx(expected, rel=0.01)

    def test_E_cm_calcestruzzo(self) -> None:
        mat = crea_calcestruzzo_ntc2018("C25/30")
        assert mat.E_cm > 0

    def test_f_d_muratura(self) -> None:
        mat = crea_muratura_ntc2018("mattoni_pieni", "M10")
        expected = 36.0 / 2.0
        assert mat.f_d == pytest.approx(expected)

    def test_f_vd_muratura(self) -> None:
        mat = crea_muratura_ntc2018("mattoni_pieni", "M10")
        expected = 2.0 / 2.0
        assert mat.f_vd == pytest.approx(expected)


class TestOverrideDerivati:
    """Test override manuale e ricalcolo."""

    def test_override_manuale(self) -> None:
        mat = crea_calcestruzzo_ntc2018("C25/30")
        original_fcd = mat.f_cd
        mat.imposta_derivato_manuale("f_cd", 999.0)
        assert mat.f_cd == 999.0
        assert mat.derivato_ha_override("f_cd")
        # Ricalcolo
        mat.ricalcola_singolo_derivato("f_cd")
        assert mat.f_cd == pytest.approx(original_fcd, rel=0.01)
        assert not mat.derivato_ha_override("f_cd")

    def test_aggiorna_da_primario_preserva_override(self) -> None:
        mat = crea_calcestruzzo_ntc2018("C25/30")
        mat.imposta_derivato_manuale("f_cd", 999.0)
        mat.aggiorna_da_primario("f_ck")
        # f_cd should be preserved because it has override
        assert mat.f_cd == 999.0


class TestSerializzazione:
    """Test serializzazione JSON round-trip."""

    def test_round_trip_calcestruzzo(self) -> None:
        mat = crea_calcestruzzo_ntc2018("C30/37")
        json_str = mat.to_json()
        mat2 = Material.from_json(json_str)
        assert mat2.material_id == mat.material_id
        assert mat2.famiglia == mat.famiglia
        assert mat2.f_ck == pytest.approx(mat.f_ck)
        assert mat2.f_cd == pytest.approx(mat.f_cd, rel=0.01)

    def test_round_trip_acciaio(self) -> None:
        mat = crea_acciaio_ntc2018("B450C")
        json_str = mat.to_json()
        mat2 = Material.from_json(json_str)
        assert mat2.f_yk == pytest.approx(mat.f_yk)
        assert mat2.f_yd == pytest.approx(mat.f_yd, rel=0.01)

    def test_round_trip_muratura(self) -> None:
        mat = crea_muratura_ntc2018("mattoni_pieni", "M10")
        json_str = mat.to_json()
        mat2 = Material.from_json(json_str)
        assert mat2.f_k == pytest.approx(mat.f_k)
        assert mat2.f_d == pytest.approx(mat.f_d, rel=0.01)

    def test_round_trip_con_override(self) -> None:
        mat = crea_calcestruzzo_ntc2018("C25/30")
        mat.imposta_derivato_manuale("f_cd", 123.45)
        json_str = mat.to_json()
        mat2 = Material.from_json(json_str)
        assert mat2.f_cd == pytest.approx(123.45)
        assert mat2.derivato_ha_override("f_cd")


# =====================================================================
# Test MaterialRepository
# =====================================================================


class TestMaterialRepository:
    """Test CRUD e operazioni del repository."""

    def test_add_and_get(self) -> None:
        repo = MaterialRepository()
        mat = crea_calcestruzzo_ntc2018("C25/30")
        repo.add_material(mat)
        result = repo.get(mat.material_id)
        assert result is not None
        assert result.material_id == mat.material_id

    def test_get_not_found(self) -> None:
        repo = MaterialRepository()
        assert repo.get("inesistente") is None

    def test_remove(self) -> None:
        repo = MaterialRepository()
        mat = crea_calcestruzzo_ntc2018("C25/30")
        repo.add_material(mat)
        assert repo.remove(mat.material_id) is True
        assert repo.get(mat.material_id) is None

    def test_remove_not_found(self) -> None:
        repo = MaterialRepository()
        assert repo.remove("inesistente") is False

    def test_list_all(self) -> None:
        repo = MaterialRepository()
        repo.add_material(crea_calcestruzzo_ntc2018("C25/30"))
        repo.add_material(crea_acciaio_ntc2018("B450C"))
        assert len(repo.list_all()) == 2

    def test_list_by_famiglia(self) -> None:
        repo = MaterialRepository()
        repo.add_material(crea_calcestruzzo_ntc2018("C25/30"))
        repo.add_material(crea_acciaio_ntc2018("B450C"))
        repo.add_material(crea_muratura_ntc2018("mattoni_pieni", "M10"))
        assert len(repo.list_by_famiglia("calcestruzzo")) == 1
        assert len(repo.list_by_famiglia("acciaio")) == 1
        assert len(repo.list_by_famiglia("muratura")) == 1

    def test_count(self) -> None:
        repo = MaterialRepository()
        assert repo.count() == 0
        repo.add_material(crea_calcestruzzo_ntc2018("C25/30"))
        assert repo.count() == 1

    def test_carica_defaults(self) -> None:
        repo = MaterialRepository()
        n = repo.carica_defaults()
        assert n == 18
        assert repo.count() == 18
        # Verifica famiglie
        assert len(repo.list_by_famiglia("calcestruzzo")) == 8  # 5 NTC + 3 TA
        assert len(repo.list_by_famiglia("acciaio")) == 5       # 2 NTC + 3 TA
        assert len(repo.list_by_famiglia("muratura")) == 2
        assert len(repo.list_by_famiglia("legno")) == 3          # C24, GL24h, GL28h


class TestPersistenzaJSON:
    """Test load/save su file JSON."""

    def test_save_and_load(self) -> None:
        repo = MaterialRepository()
        repo.carica_defaults()

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            tmp_path = f.name

        repo.save_to_json(tmp_path)

        repo2 = MaterialRepository()
        n = repo2.load_from_json(tmp_path)
        assert n == 18
        assert repo2.count() == 18

        # Verifica un materiale specifico
        mat = repo2.get("cls_C25/30")
        assert mat is not None
        assert mat.f_ck == pytest.approx(254.9, rel=0.01)
        assert mat.f_cd > 0

        Path(tmp_path).unlink()

    def test_load_file_inesistente(self) -> None:
        repo = MaterialRepository()
        n = repo.load_from_json("/tmp/inesistente_12345.json")
        assert n == 0

    def test_load_data_materials_json(self) -> None:
        """Verifica che data/materials.json si carichi correttamente."""
        path = Path(__file__).resolve().parent.parent / "data" / "materials.json"
        if not path.exists():
            pytest.skip("data/materials.json non presente")
        repo = MaterialRepository()
        n = repo.load_from_json(path)
        assert n > 0

    def test_load_sources(self) -> None:
        """Verifica caricamento fonti normative."""
        path = Path(__file__).resolve().parent.parent / "data" / "material_sources.json"
        if not path.exists():
            pytest.skip("data/material_sources.json non presente")
        repo = MaterialRepository()
        n = repo.load_sources(path)
        assert n > 0
        ntc = repo.get_source("NTC2018")
        assert ntc is not None
        assert ntc["year"] == 2018


# =====================================================================
# Test Validazione
# =====================================================================


class TestValidazione:
    """Test validazione materiali."""

    def test_materiale_valido_calcestruzzo(self) -> None:
        mat = crea_calcestruzzo_ntc2018("C25/30")
        errors = validate_material(mat)
        assert errors == []

    def test_materiale_valido_acciaio(self) -> None:
        mat = crea_acciaio_ntc2018("B450C")
        errors = validate_material(mat)
        assert errors == []

    def test_materiale_valido_muratura(self) -> None:
        mat = crea_muratura_ntc2018("mattoni_pieni", "M10")
        errors = validate_material(mat)
        assert errors == []

    def test_id_mancante(self) -> None:
        mat = crea_calcestruzzo_ntc2018("C25/30")
        mat.material_id = ""
        errors = validate_material(mat)
        assert any("material_id" in e for e in errors)

    def test_densita_negativa(self) -> None:
        mat = crea_calcestruzzo_ntc2018("C25/30")
        mat.densita_kg_m3 = -100
        errors = validate_material(mat)
        assert any("densità" in e.lower() or "densita" in e.lower() for e in errors)

    def test_famiglia_invalida(self) -> None:
        mat = Material(material_id="test", famiglia="vetro")
        errors = validate_material(mat)
        assert any("famiglia" in e.lower() for e in errors)

    def test_poisson_fuori_range(self) -> None:
        mat = crea_calcestruzzo_ntc2018("C25/30")
        mat.nu = 0.6
        errors = validate_material(mat)
        assert any("Poisson" in e for e in errors)

    def test_calcestruzzo_senza_resistenza(self) -> None:
        mat = Material(
            material_id="cls_vuoto",
            famiglia="calcestruzzo",
            f_ck=0.0,
            sigma_c28=0.0,
        )
        errors = validate_material(mat)
        assert any("calcestruzzo" in e.lower() or "f_ck" in e for e in errors)

    def test_acciaio_senza_resistenza(self) -> None:
        mat = Material(
            material_id="acc_vuoto",
            famiglia="acciaio",
            f_yk=0.0,
            sigma_s_adm=0.0,
        )
        errors = validate_material(mat)
        assert any("acciaio" in e.lower() or "f_yk" in e for e in errors)

    def test_muratura_fk_negativo(self) -> None:
        mat = Material(
            material_id="mur_neg",
            famiglia="muratura",
            f_k=-10.0,
        )
        errors = validate_material(mat)
        assert any("f_k" in e for e in errors)

    def test_repo_validate_all(self) -> None:
        repo = MaterialRepository()
        repo.carica_defaults()
        results = repo.validate_all()
        # Tutti i materiali di default devono essere validi
        for mid, errors in results.items():
            assert errors == [], f"Materiale {mid} ha errori: {errors}"
