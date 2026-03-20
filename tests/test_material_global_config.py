"""Test per GlobalMaterialCoefficientsManager (src/core/material_global_config.py).

Verifica la gerarchia Level 1 (default normativo) + Level 2 (override globale utente),
inclusi set/reset/persist degli override.
"""

import json
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.normative_defaults import NormativeDefaultsLoader
from core.user_config import UserConfig
from core.material_global_config import GlobalMaterialCoefficientsManager

NORMS_DIR = Path(__file__).parent.parent / "config" / "norms"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_singletons():
    NormativeDefaultsLoader.reset_instance()
    GlobalMaterialCoefficientsManager.reset_instance()
    yield
    NormativeDefaultsLoader.reset_instance()
    GlobalMaterialCoefficientsManager.reset_instance()


@pytest.fixture
def loader():
    return NormativeDefaultsLoader(norms_dir=NORMS_DIR)


@pytest.fixture
def cfg_no_overrides():
    """UserConfig senza override materiali."""
    return UserConfig()


@pytest.fixture
def cfg_with_overrides():
    """UserConfig con override gamma_c per NTC2018/calcestruzzo."""
    cfg = UserConfig()
    cfg.material_coefficients_overrides = {
        "NTC2018": {
            "calcestruzzo": {"gamma_c": 1.60, "alpha_cc": 0.90}
        }
    }
    return cfg


@pytest.fixture
def mgr_no_overrides(cfg_no_overrides, loader):
    return GlobalMaterialCoefficientsManager(user_config=cfg_no_overrides, loader=loader)


@pytest.fixture
def mgr_with_overrides(cfg_with_overrides, loader):
    return GlobalMaterialCoefficientsManager(user_config=cfg_with_overrides, loader=loader)


# ---------------------------------------------------------------------------
# Test: Level 1 default (nessun override)
# ---------------------------------------------------------------------------

class TestLevel1Default:
    def test_gamma_c_ntc2018_default(self, mgr_no_overrides):
        val = mgr_no_overrides.get_coefficient("NTC2018", "calcestruzzo", "gamma_c")
        assert val == pytest.approx(1.50)

    def test_gamma_c_dm96_default(self, mgr_no_overrides):
        val = mgr_no_overrides.get_coefficient("DM96", "calcestruzzo", "gamma_c")
        assert val == pytest.approx(1.60)

    def test_gamma_s_ntc2018_default(self, mgr_no_overrides):
        val = mgr_no_overrides.get_coefficient("NTC2018", "acciaio", "gamma_s")
        assert val == pytest.approx(1.15)

    def test_gamma_m_ntc2018_default(self, mgr_no_overrides):
        val = mgr_no_overrides.get_coefficient("NTC2018", "muratura", "gamma_M")
        assert val == pytest.approx(2.00)

    def test_missing_coeff_returns_none(self, mgr_no_overrides):
        val = mgr_no_overrides.get_coefficient("NTC2018", "calcestruzzo", "INESISTENTE")
        assert val is None


# ---------------------------------------------------------------------------
# Test: Level 2 override (prevale sul Level 1)
# ---------------------------------------------------------------------------

class TestLevel2Override:
    def test_override_gamma_c_prevale(self, mgr_with_overrides):
        """Override Level 2 deve prevalere sul default Level 1."""
        val = mgr_with_overrides.get_coefficient("NTC2018", "calcestruzzo", "gamma_c")
        assert val == pytest.approx(1.60)  # override, non default 1.50

    def test_override_alpha_cc_prevale(self, mgr_with_overrides):
        val = mgr_with_overrides.get_coefficient("NTC2018", "calcestruzzo", "alpha_cc")
        assert val == pytest.approx(0.90)  # override, non default 0.85

    def test_non_overridden_coeff_usa_default(self, mgr_with_overrides):
        """Coefficiente non in override deve restituire Level 1."""
        val = mgr_with_overrides.get_coefficient("NTC2018", "calcestruzzo", "alpha_ct")
        # alpha_ct non overridden → usa default dal file
        assert val == pytest.approx(1.00)

    def test_override_altra_norma_non_affetta_ntc2018(self, mgr_with_overrides):
        """Override su NTC2018 non deve affettare DM96."""
        val = mgr_with_overrides.get_coefficient("DM96", "calcestruzzo", "gamma_c")
        assert val == pytest.approx(1.60)  # default DM96, non override NTC2018


# ---------------------------------------------------------------------------
# Test: get_coefficient_with_source
# ---------------------------------------------------------------------------

class TestGetCoefficientWithSource:
    def test_default_source(self, mgr_no_overrides):
        val, source = mgr_no_overrides.get_coefficient_with_source(
            "NTC2018", "calcestruzzo", "gamma_c"
        )
        assert val == pytest.approx(1.50)
        assert source == "default"

    def test_override_source(self, mgr_with_overrides):
        val, source = mgr_with_overrides.get_coefficient_with_source(
            "NTC2018", "calcestruzzo", "gamma_c"
        )
        assert val == pytest.approx(1.60)
        assert source == "override"

    def test_non_overridden_source_is_default(self, mgr_with_overrides):
        _, source = mgr_with_overrides.get_coefficient_with_source(
            "NTC2018", "calcestruzzo", "alpha_ct"
        )
        assert source == "default"


# ---------------------------------------------------------------------------
# Test: set_coefficient_override
# ---------------------------------------------------------------------------

class TestSetCoefficientOverride:
    def test_set_override_cambia_valore(self, mgr_no_overrides):
        mgr_no_overrides.set_coefficient_override(
            "NTC2018", "calcestruzzo", "gamma_c", 1.70, save=False
        )
        val = mgr_no_overrides.get_coefficient("NTC2018", "calcestruzzo", "gamma_c")
        assert val == pytest.approx(1.70)

    def test_set_override_aggiorna_source(self, mgr_no_overrides):
        mgr_no_overrides.set_coefficient_override(
            "NTC2018", "calcestruzzo", "gamma_c", 1.70, save=False
        )
        _, source = mgr_no_overrides.get_coefficient_with_source(
            "NTC2018", "calcestruzzo", "gamma_c"
        )
        assert source == "override"

    def test_set_override_crea_struttura_annidata(self, mgr_no_overrides):
        mgr_no_overrides.set_coefficient_override(
            "DM96", "acciaio", "n_omogenizzazione", 20.0, save=False
        )
        assert "DM96" in mgr_no_overrides._cfg.material_coefficients_overrides
        assert "acciaio" in mgr_no_overrides._cfg.material_coefficients_overrides["DM96"]
        assert mgr_no_overrides._cfg.material_coefficients_overrides["DM96"]["acciaio"]["n_omogenizzazione"] == 20.0

    def test_has_override_after_set(self, mgr_no_overrides):
        assert not mgr_no_overrides.has_override("NTC2018", "calcestruzzo", "gamma_c")
        mgr_no_overrides.set_coefficient_override(
            "NTC2018", "calcestruzzo", "gamma_c", 1.60, save=False
        )
        assert mgr_no_overrides.has_override("NTC2018", "calcestruzzo", "gamma_c")


# ---------------------------------------------------------------------------
# Test: reset_coefficient_to_default
# ---------------------------------------------------------------------------

class TestResetCoefficientToDefault:
    def test_reset_rimuove_override(self, mgr_with_overrides):
        mgr_with_overrides.reset_coefficient_to_default(
            "NTC2018", "calcestruzzo", "gamma_c", save=False
        )
        val = mgr_with_overrides.get_coefficient("NTC2018", "calcestruzzo", "gamma_c")
        assert val == pytest.approx(1.50)  # torna al default Level 1

    def test_reset_aggiorna_source(self, mgr_with_overrides):
        mgr_with_overrides.reset_coefficient_to_default(
            "NTC2018", "calcestruzzo", "gamma_c", save=False
        )
        _, source = mgr_with_overrides.get_coefficient_with_source(
            "NTC2018", "calcestruzzo", "gamma_c"
        )
        assert source == "default"

    def test_reset_inesistente_non_fallisce(self, mgr_no_overrides):
        """Reset su override non esistente non deve sollevare eccezioni."""
        mgr_no_overrides.reset_coefficient_to_default(
            "NTC2018", "calcestruzzo", "INESISTENTE", save=False
        )

    def test_reset_pulisce_struttura_vuota(self, mgr_with_overrides):
        """Dopo reset di tutti i coefficienti, la struttura annidata deve essere pulita."""
        mgr_with_overrides.reset_coefficient_to_default(
            "NTC2018", "calcestruzzo", "gamma_c", save=False
        )
        mgr_with_overrides.reset_coefficient_to_default(
            "NTC2018", "calcestruzzo", "alpha_cc", save=False
        )
        overrides = mgr_with_overrides._cfg.material_coefficients_overrides
        assert "NTC2018" not in overrides


# ---------------------------------------------------------------------------
# Test: reset_all_norm e reset_all
# ---------------------------------------------------------------------------

class TestResetAll:
    def test_reset_all_norm_rimuove_norma(self, mgr_with_overrides):
        mgr_with_overrides.reset_all_norm("NTC2018", save=False)
        assert "NTC2018" not in mgr_with_overrides._cfg.material_coefficients_overrides

    def test_reset_all_norm_non_rimuove_altre_norme(self, loader):
        cfg = UserConfig()
        cfg.material_coefficients_overrides = {
            "NTC2018": {"calcestruzzo": {"gamma_c": 1.60}},
            "DM96": {"calcestruzzo": {"gamma_c": 1.70}},
        }
        mgr = GlobalMaterialCoefficientsManager(user_config=cfg, loader=loader)
        mgr.reset_all_norm("NTC2018", save=False)
        assert "DM96" in mgr._cfg.material_coefficients_overrides

    def test_reset_all_svuota_tutto(self, mgr_with_overrides):
        mgr_with_overrides.reset_all(save=False)
        assert mgr_with_overrides._cfg.material_coefficients_overrides == {}


# ---------------------------------------------------------------------------
# Test: get_all_coefficients e build_formula_namespace
# ---------------------------------------------------------------------------

class TestGetAllCoefficients:
    def test_get_all_ntc2018_contiene_gamma_c(self, mgr_no_overrides):
        all_coeffs = mgr_no_overrides.get_all_coefficients("NTC2018", "calcestruzzo")
        assert "gamma_c" in all_coeffs
        assert all_coeffs["gamma_c"] == pytest.approx(1.50)

    def test_get_all_applica_overrides(self, mgr_with_overrides):
        all_coeffs = mgr_with_overrides.get_all_coefficients("NTC2018", "calcestruzzo")
        assert all_coeffs["gamma_c"] == pytest.approx(1.60)

    def test_build_formula_namespace_contiene_gamma_c(self, mgr_no_overrides):
        ns = mgr_no_overrides.build_formula_namespace("NTC2018", "calcestruzzo")
        assert "gamma_c" in ns
        assert isinstance(ns["gamma_c"], float)


# ---------------------------------------------------------------------------
# Test: get_overrides_for_norm
# ---------------------------------------------------------------------------

class TestGetOverridesForNorm:
    def test_nessun_override(self, mgr_no_overrides):
        overrides = mgr_no_overrides.get_overrides_for_norm("NTC2018")
        assert overrides == {}

    def test_override_presenti(self, mgr_with_overrides):
        overrides = mgr_with_overrides.get_overrides_for_norm("NTC2018")
        assert "calcestruzzo" in overrides
        assert overrides["calcestruzzo"]["gamma_c"] == pytest.approx(1.60)


# ---------------------------------------------------------------------------
# Test: persistenza su file (round-trip)
# ---------------------------------------------------------------------------

class TestPersistenza:
    def test_round_trip_save_load(self, loader, tmp_path):
        """Override salvati su file devono essere riletti correttamente."""
        cfg_path = tmp_path / "config.json"
        cfg = UserConfig()
        mgr = GlobalMaterialCoefficientsManager(
            user_config=cfg, loader=loader, user_config_path=str(cfg_path)
        )

        mgr.set_coefficient_override("NTC2018", "calcestruzzo", "gamma_c", 1.65, save=True)
        assert cfg_path.exists()

        # Ricarica da file
        cfg2 = UserConfig.load(path=str(cfg_path))
        assert cfg2.material_coefficients_overrides["NTC2018"]["calcestruzzo"]["gamma_c"] == pytest.approx(1.65)

    def test_reset_persiste(self, loader, tmp_path):
        """Dopo reset, il file non deve contenere override."""
        cfg_path = tmp_path / "config.json"
        cfg = UserConfig()
        mgr = GlobalMaterialCoefficientsManager(
            user_config=cfg, loader=loader, user_config_path=str(cfg_path)
        )

        mgr.set_coefficient_override("NTC2018", "calcestruzzo", "gamma_c", 1.65, save=True)
        mgr.reset_coefficient_to_default("NTC2018", "calcestruzzo", "gamma_c", save=True)

        cfg2 = UserConfig.load(path=str(cfg_path))
        assert "NTC2018" not in cfg2.material_coefficients_overrides


# ---------------------------------------------------------------------------
# Test: Singleton
# ---------------------------------------------------------------------------

class TestSingleton:
    def test_singleton_returns_same_instance(self):
        inst1 = GlobalMaterialCoefficientsManager.instance()
        inst2 = GlobalMaterialCoefficientsManager.instance()
        assert inst1 is inst2

    def test_reset_creates_new_instance(self):
        inst1 = GlobalMaterialCoefficientsManager.instance()
        GlobalMaterialCoefficientsManager.reset_instance()
        inst2 = GlobalMaterialCoefficientsManager.instance()
        assert inst1 is not inst2
