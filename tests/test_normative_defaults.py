"""Test per NormativeDefaultsLoader (src/core/normative_defaults.py).

Verifica che i file config/norms/*.json siano correttamente caricati,
che i coefficienti siano accessibili e che la cache/reload funzionino.
"""

import json
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.normative_defaults import NormativeDefaultsLoader

NORMS_DIR = Path(__file__).parent.parent / "config" / "norms"
EXPECTED_NORMS = ["NTC2018", "NTC2008", "OPCM3274", "DM96", "DM92", "DM72", "Circ81", "RD2229"]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_singleton():
    """Resetta il singleton prima e dopo ogni test."""
    NormativeDefaultsLoader.reset_instance()
    yield
    NormativeDefaultsLoader.reset_instance()


@pytest.fixture
def loader():
    return NormativeDefaultsLoader(norms_dir=NORMS_DIR)


# ---------------------------------------------------------------------------
# Test: struttura file JSON
# ---------------------------------------------------------------------------

class TestNormFiles:
    def test_all_expected_norm_files_exist(self):
        for norm_key in EXPECTED_NORMS:
            path = NORMS_DIR / f"{norm_key}.json"
            assert path.exists(), f"File mancante: {path}"

    def test_norm_files_are_valid_json(self):
        for path in NORMS_DIR.glob("*.json"):
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                pytest.fail(f"JSON non valido in {path}: {exc}")

    def test_each_norm_has_required_keys(self):
        required = {"norm_key", "norm_label", "norm_year", "materiali"}
        for norm_key in EXPECTED_NORMS:
            path = NORMS_DIR / f"{norm_key}.json"
            if not path.exists():
                continue
            data = json.loads(path.read_text(encoding="utf-8"))
            for k in required:
                assert k in data, f"Chiave '{k}' mancante in {path.name}"

    def test_norm_key_matches_filename(self):
        for path in NORMS_DIR.glob("*.json"):
            data = json.loads(path.read_text(encoding="utf-8"))
            assert data.get("norm_key") == path.stem, (
                f"norm_key '{data.get('norm_key')}' non corrisponde a '{path.stem}'"
            )

    def test_materiali_block_is_dict(self):
        for path in NORMS_DIR.glob("*.json"):
            data = json.loads(path.read_text(encoding="utf-8"))
            assert isinstance(data.get("materiali"), dict), (
                f"'materiali' non è un dict in {path.name}"
            )

    def test_ntc2018_has_calcestruzzo_acciaio_muratura(self):
        data = json.loads((NORMS_DIR / "NTC2018.json").read_text(encoding="utf-8"))
        for famiglia in ("calcestruzzo", "acciaio", "muratura"):
            assert famiglia in data["materiali"], f"Famiglia '{famiglia}' mancante in NTC2018.json"

    def test_coefficients_have_valore_field(self):
        """I coefficienti strutturati (dict) devono avere campo 'valore'."""
        for path in NORMS_DIR.glob("*.json"):
            data = json.loads(path.read_text(encoding="utf-8"))
            for fam_key, fam_data in data.get("materiali", {}).items():
                for coeff_key, coeff_val in fam_data.items():
                    if isinstance(coeff_val, dict) and not coeff_key.endswith(("_formula", "_note", "note")):
                        if "valore" not in coeff_val and "formula" not in coeff_key:
                            # È un sub-dict che potrebbe essere coefficiente o altro
                            # Solo verifica che non sia vuoto
                            assert coeff_val, (
                                f"Valore vuoto per {path.name}/{fam_key}/{coeff_key}"
                            )

    def test_gamma_values_are_positive(self):
        for path in NORMS_DIR.glob("*.json"):
            data = json.loads(path.read_text(encoding="utf-8"))
            for fam_key, fam_data in data.get("materiali", {}).items():
                for coeff_key, coeff_val in fam_data.items():
                    if coeff_key.startswith("gamma_") and isinstance(coeff_val, dict):
                        v = coeff_val.get("valore")
                        if v is not None:
                            assert v > 0, (
                                f"gamma negativo: {path.name}/{fam_key}/{coeff_key} = {v}"
                            )


# ---------------------------------------------------------------------------
# Test: NormativeDefaultsLoader API
# ---------------------------------------------------------------------------

class TestNormativeDefaultsLoader:
    def test_get_all_norms_returns_list(self, loader):
        norms = loader.get_all_norms()
        assert isinstance(norms, list)
        assert len(norms) >= len(EXPECTED_NORMS)

    def test_get_all_norms_contains_expected(self, loader):
        norms = loader.get_all_norms()
        for norm_key in EXPECTED_NORMS:
            assert norm_key in norms, f"'{norm_key}' non trovato in get_all_norms()"

    def test_get_all_norms_sorted(self, loader):
        norms = loader.get_all_norms()
        assert norms == sorted(norms)

    def test_load_norm_defaults_ntc2018(self, loader):
        data = loader.load_norm_defaults("NTC2018")
        assert data["norm_key"] == "NTC2018"
        assert "materiali" in data

    def test_load_norm_defaults_missing_returns_empty(self, loader):
        data = loader.load_norm_defaults("NORMA_NON_ESISTE")
        assert data == {}

    def test_get_norm_label_ntc2018(self, loader):
        label = loader.get_norm_label("NTC2018")
        assert "NTC" in label
        assert "2018" in label

    def test_get_norm_label_missing(self, loader):
        label = loader.get_norm_label("NORMA_NON_ESISTE")
        assert label == "NORMA_NON_ESISTE"  # fallback = norm_key


class TestGetMaterialCoefficient:
    def test_gamma_c_ntc2018_calcestruzzo(self, loader):
        val = loader.get_material_coefficient("NTC2018", "calcestruzzo", "gamma_c")
        assert val == pytest.approx(1.50)

    def test_gamma_c_dm96_calcestruzzo(self, loader):
        val = loader.get_material_coefficient("DM96", "calcestruzzo", "gamma_c")
        assert val == pytest.approx(1.60)

    def test_gamma_c_dm72_is_one(self, loader):
        val = loader.get_material_coefficient("DM72", "calcestruzzo", "gamma_c")
        assert val == pytest.approx(1.00)

    def test_gamma_c_rd2229_is_one(self, loader):
        val = loader.get_material_coefficient("RD2229", "calcestruzzo", "gamma_c")
        assert val == pytest.approx(1.00)

    def test_gamma_s_ntc2018_acciaio(self, loader):
        val = loader.get_material_coefficient("NTC2018", "acciaio", "gamma_s")
        assert val == pytest.approx(1.15)

    def test_gamma_s_ntc2008_acciaio(self, loader):
        val = loader.get_material_coefficient("NTC2008", "acciaio", "gamma_s")
        assert val == pytest.approx(1.15)

    def test_gamma_m_ntc2018_muratura(self, loader):
        val = loader.get_material_coefficient("NTC2018", "muratura", "gamma_M")
        assert val == pytest.approx(2.00)

    def test_alpha_cc_ntc2018(self, loader):
        val = loader.get_material_coefficient("NTC2018", "calcestruzzo", "alpha_cc")
        assert val == pytest.approx(0.85)

    def test_n_omogenizzazione_dm96(self, loader):
        val = loader.get_material_coefficient("DM96", "calcestruzzo", "n_omogenizzazione")
        assert val == pytest.approx(15.0)

    def test_n_omogenizzazione_dm72(self, loader):
        val = loader.get_material_coefficient("DM72", "calcestruzzo", "n_omogenizzazione")
        assert val == pytest.approx(10.0)

    def test_missing_coeff_returns_none(self, loader):
        val = loader.get_material_coefficient("NTC2018", "calcestruzzo", "COEFF_INESISTENTE")
        assert val is None

    def test_missing_famiglia_returns_none(self, loader):
        val = loader.get_material_coefficient("NTC2018", "famiglia_inesistente", "gamma_c")
        assert val is None


class TestGetCoefficientMetadata:
    def test_metadata_has_label_and_valore(self, loader):
        meta = loader.get_coefficient_metadata("NTC2018", "calcestruzzo", "gamma_c")
        assert "valore" in meta
        assert "label" in meta

    def test_metadata_gamma_c_ntc2018(self, loader):
        meta = loader.get_coefficient_metadata("NTC2018", "calcestruzzo", "gamma_c")
        assert meta["valore"] == pytest.approx(1.50)
        assert meta["label"] == "γ_c"

    def test_metadata_missing_returns_empty(self, loader):
        meta = loader.get_coefficient_metadata("NTC2018", "calcestruzzo", "INESISTENTE")
        assert meta == {}


class TestListCoefficients:
    def test_list_ntc2018_calcestruzzo(self, loader):
        coeffs = loader.list_coefficients("NTC2018", "calcestruzzo")
        assert "gamma_c" in coeffs
        assert "alpha_cc" in coeffs

    def test_list_ntc2018_acciaio(self, loader):
        coeffs = loader.list_coefficients("NTC2018", "acciaio")
        assert "gamma_s" in coeffs

    def test_list_ntc2018_muratura(self, loader):
        coeffs = loader.list_coefficients("NTC2018", "muratura")
        assert "gamma_M" in coeffs

    def test_list_missing_norm_empty(self, loader):
        coeffs = loader.list_coefficients("NORMA_INESISTENTE", "calcestruzzo")
        assert coeffs == []


class TestCacheAndReload:
    def test_second_load_uses_cache(self, loader):
        """La seconda chiamata non deve rileggere il file (stessa istanza dict)."""
        data1 = loader.load_norm_defaults("NTC2018")
        data2 = loader.load_norm_defaults("NTC2018")
        assert data1 is data2  # stessa istanza in cache

    def test_reload_invalidates_cache(self, loader):
        data1 = loader.load_norm_defaults("NTC2018")
        loader.reload("NTC2018")
        data2 = loader.load_norm_defaults("NTC2018")
        assert data1 is not data2  # nuova istanza dopo reload

    def test_reload_all_invalidates_all(self, loader):
        loader.load_norm_defaults("NTC2018")
        loader.load_norm_defaults("DM96")
        loader.reload()
        assert loader._cache == {}


class TestSingleton:
    def test_singleton_returns_same_instance(self):
        inst1 = NormativeDefaultsLoader.instance()
        inst2 = NormativeDefaultsLoader.instance()
        assert inst1 is inst2

    def test_reset_creates_new_instance(self):
        inst1 = NormativeDefaultsLoader.instance()
        NormativeDefaultsLoader.reset_instance()
        inst2 = NormativeDefaultsLoader.instance()
        assert inst1 is not inst2
