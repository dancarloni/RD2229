"""Test FASE I — Sezione omogeneizzata, asse neutro fessurato, tensioni SLE.

Copre:
    - norme_n.py: rapporto n per norma
    - omogenizzata.py: sezione integra, fessurata, tensioni SLE
    - composita.py: sezione composta acciaio-cls
    - disegno_sezione.py: generazione figura matplotlib (headless)
    - pipeline completa per tutti i tipi di sezione
"""

from __future__ import annotations

import math
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.codes.section_params.norme_n import (
    RD2229_N_OPTIONS,
    get_n_for_norm,
)
from src.codes.section_params.omogenizzata import (
    BarraArmatura,
    calcola_asse_neutro_fessurato,
    calcola_parametri_sezione_completi,
    calcola_sezione_omogenizzata,
    calcola_tensioni_sle,
)
from src.codes.section_params.composita import (
    IPE_TABLE,
    calcola_sezione_composta,
    calcola_tensioni_sle_composita,
)


# ---------------------------------------------------------------------------
# Helper mock sezione rettangolare
# ---------------------------------------------------------------------------

def _rect(width: float = 30.0, height: float = 50.0):
    return SimpleNamespace(section_type="RECTANGULAR", width=width, height=height)


def _circ(diameter: float = 40.0):
    return SimpleNamespace(section_type="CIRCULAR", diameter=diameter)


def _t_sec(bf=40.0, tf=10.0, tw=15.0, hw=35.0):
    return SimpleNamespace(
        section_type="T_SECTION",
        flange_width=bf,
        flange_thickness=tf,
        web_thickness=tw,
        web_height=hw,
    )


# ===========================================================================
# TestNormaHnParams
# ===========================================================================

class TestNormaHnParams:
    """Test get_n_for_norm per tutte le norme."""

    def test_rd2229_default_n15(self) -> None:
        p = get_n_for_norm("RD2229")
        assert p.n == 15.0

    def test_rd2229_n_options(self) -> None:
        assert RD2229_N_OPTIONS == [8, 10, 12, 15]

    def test_rd2229_user_n8(self) -> None:
        p = get_n_for_norm("RD2229", n_user=8)
        assert p.n == 8.0

    def test_rd2229_user_n10(self) -> None:
        p = get_n_for_norm("RD2229", n_user=10)
        assert p.n == 10.0

    def test_rd2229_calcolo_automatico(self) -> None:
        p = get_n_for_norm("RD2229", E_s=2_100_000, E_c=210_000)
        assert p.n == pytest.approx(10.0, rel=1e-4)

    def test_dm96_default_n10(self) -> None:
        p = get_n_for_norm("DM96")
        assert p.n == 10.0

    def test_dm92_default_n10(self) -> None:
        p = get_n_for_norm("DM92")
        assert p.n == 10.0

    def test_dm96_calcolo_automatico(self) -> None:
        p = get_n_for_norm("DM96", E_s=2_100_000, E_c=300_000)
        assert p.n == pytest.approx(7.0, rel=1e-4)

    def test_ntc2018_default_n15(self) -> None:
        p = get_n_for_norm("NTC2018")
        assert p.n == 15.0

    def test_ntc2008_default_n15(self) -> None:
        p = get_n_for_norm("NTC2008")
        assert p.n == 15.0

    def test_ntc2018_calcolo_automatico(self) -> None:
        # E_s=200000 MPa, E_c=30000 MPa → n=6.667
        p = get_n_for_norm("NTC2018", E_s=200_000, E_c=30_000)
        assert p.n == pytest.approx(200_000 / 30_000, rel=1e-4)

    def test_ec2_default_n15(self) -> None:
        p = get_n_for_norm("EC2")
        assert p.n == 15.0

    def test_ec2_con_phi(self) -> None:
        # E_s=200000, E_c=30000, phi=2 → E_c_eff=10000 → n=20
        p = get_n_for_norm("EC2", E_s=200_000, E_c=30_000, phi=2.0)
        assert p.n == pytest.approx(20.0, rel=1e-4)

    def test_norma_invalida_raise(self) -> None:
        with pytest.raises(ValueError, match="non supportata"):
            get_n_for_norm("DM87_FANTASMA")

    def test_case_insensitive(self) -> None:
        p = get_n_for_norm("ntc2018")
        assert p.n == 15.0

    def test_ntc2018_fonte_contiene_par(self) -> None:
        p = get_n_for_norm("NTC2018")
        assert "4.1.2" in p.note or "15" in p.note

    def test_user_n_ha_precedenza_su_E(self) -> None:
        p = get_n_for_norm("DM96", n_user=12, E_s=2_100_000, E_c=210_000)
        assert p.n == 12.0  # user vince su E_s/E_c


# ===========================================================================
# TestSezOmogenizzataRettangolare
# ===========================================================================

class TestSezOmogenizzataRettangolare:
    """Sezione 30×50 cm, As=10 cm² a d=45 cm, n=10.

    Valori di riferimento calcolati analiticamente:
        A_c = 1500 cm²
        y_G_c = 25 cm
        I_c = 30*50^3/12 = 312500 cm⁴
        A_om = 1500 + 9*10 = 1590 cm²
        y_G_om = (1500*25 + 9*10*45) / 1590 = 41550/1590 ≈ 26.1321 cm
        I_om = 312500 + 1500*(25-26.1321)^2 + 9*10*(45-26.1321)^2
             ≈ 346444 cm⁴
    """

    @pytest.fixture
    def setup(self):
        s = _rect(30.0, 50.0)
        barre = [BarraArmatura(y=45.0, A=10.0, zona="tesa")]
        n = 10.0
        return s, barre, n

    def test_esito_ok(self, setup) -> None:
        s, barre, n = setup
        res = calcola_sezione_omogenizzata(s, barre, n)
        assert res["esito"] == "OK"

    def test_area_cls(self, setup) -> None:
        s, barre, n = setup
        res = calcola_sezione_omogenizzata(s, barre, n)
        assert res["A_cls_cm2"] == pytest.approx(1500.0, rel=0.005)

    def test_area_omogenizzata(self, setup) -> None:
        s, barre, n = setup
        res = calcola_sezione_omogenizzata(s, barre, n)
        expected = 1500.0 + 9.0 * 10.0  # A_c + (n-1)*As
        assert res["A_omogenizzata_cm2"] == pytest.approx(expected, rel=0.005)

    def test_baricentro_omogenizzato(self, setup) -> None:
        s, barre, n = setup
        res = calcola_sezione_omogenizzata(s, barre, n)
        A_om = 1590.0
        y_G_expected = (1500.0 * 25.0 + 9.0 * 10.0 * 45.0) / A_om
        assert res["y_G_omogenizzata_cm"] == pytest.approx(y_G_expected, rel=0.001)

    def test_inerzia_omogenizzata(self, setup) -> None:
        s, barre, n = setup
        res = calcola_sezione_omogenizzata(s, barre, n)
        y_G_om = res["y_G_omogenizzata_cm"]
        I_c = 30.0 * 50.0 ** 3 / 12.0
        I_expected = (
            I_c
            + 1500.0 * (25.0 - y_G_om) ** 2
            + 9.0 * 10.0 * (45.0 - y_G_om) ** 2
        )
        assert res["I_omogenizzata_cm4"] == pytest.approx(I_expected, rel=0.005)

    def test_inerzia_maggiore_di_inerzia_cls(self, setup) -> None:
        s, barre, n = setup
        res = calcola_sezione_omogenizzata(s, barre, n)
        assert res["I_omogenizzata_cm4"] > res["I_cls_cm4"]

    def test_modulo_superiore_positivo(self, setup) -> None:
        s, barre, n = setup
        res = calcola_sezione_omogenizzata(s, barre, n)
        assert res["W_superiore_cm3"] > 0.0

    def test_modulo_inferiore_positivo(self, setup) -> None:
        s, barre, n = setup
        res = calcola_sezione_omogenizzata(s, barre, n)
        assert res["W_inferiore_cm3"] > 0.0

    def test_barre_nel_risultato(self, setup) -> None:
        s, barre, n = setup
        res = calcola_sezione_omogenizzata(s, barre, n)
        assert len(res["barre"]) == 1
        assert res["barre"][0]["y_cm"] == 45.0
        assert res["barre"][0]["A_cm2"] == 10.0

    def test_h_tot(self, setup) -> None:
        s, barre, n = setup
        res = calcola_sezione_omogenizzata(s, barre, n)
        assert res["h_tot_cm"] == pytest.approx(50.0, rel=0.01)

    def test_baricentro_spostato_verso_armatura(self, setup) -> None:
        """L'armatura in zona tesa sposta il baricentro verso il basso."""
        s, barre, n = setup
        res = calcola_sezione_omogenizzata(s, barre, n)
        assert res["y_G_omogenizzata_cm"] > res["y_G_cls_cm"]


class TestSezOmogenizzataDueFile:
    """Sezione con doppia armatura (compressa + tesa)."""

    def test_doppia_armatura(self) -> None:
        s = _rect(30.0, 50.0)
        barre = [
            BarraArmatura(y=5.0, A=6.0, zona="compressa"),
            BarraArmatura(y=45.0, A=10.0, zona="tesa"),
        ]
        res = calcola_sezione_omogenizzata(s, barre, n=10.0)
        assert res["esito"] == "OK"
        expected_A = 1500.0 + 9.0 * (6.0 + 10.0)
        assert res["A_omogenizzata_cm2"] == pytest.approx(expected_A, rel=0.005)

    def test_senza_armatura(self) -> None:
        """Sezione cls pura: A_om = A_c."""
        s = _rect(30.0, 50.0)
        res = calcola_sezione_omogenizzata(s, [], n=10.0)
        assert res["esito"] == "OK"
        assert res["A_omogenizzata_cm2"] == pytest.approx(res["A_cls_cm2"], rel=0.001)

    def test_n1(self) -> None:
        """n=1: sezione omogenizzata = sezione cls (nessuna trasformazione)."""
        s = _rect(30.0, 50.0)
        barre = [BarraArmatura(y=45.0, A=10.0)]
        res = calcola_sezione_omogenizzata(s, barre, n=1.0)
        assert res["esito"] == "OK"
        # Con n=1: A_om = A_c + 0*As = A_c
        assert res["A_omogenizzata_cm2"] == pytest.approx(res["A_cls_cm2"], rel=0.001)


# ===========================================================================
# TestAssNeutroFessuratoRettangolare
# ===========================================================================

class TestAssNeutroFessuratoRettangolare:
    """Asse neutro fessurato per sezione rettangolare 30×50 cm.

    Riferimento analitico:
        b=30, n=10, As=10, d=45
        (b/2)*x^2 + n*As*x - n*As*d = 0
        15*x^2 + 100*x - 4500 = 0
        x = (-100 + sqrt(10000 + 270000)) / 30 = (-100 + 529.15) / 30 = 14.305 cm
    """

    @pytest.fixture
    def setup(self):
        s = _rect(30.0, 50.0)
        barre = [BarraArmatura(y=45.0, A=10.0, zona="tesa")]
        n = 10.0
        return s, barre, n

    def _asse_neutro_analitico(self):
        b, n, As, d = 30.0, 10.0, 10.0, 45.0
        a_q = b / 2.0
        b_q = n * As
        c_q = -(n * As * d)
        disc = b_q ** 2 - 4.0 * a_q * c_q
        return (-b_q + math.sqrt(disc)) / (2.0 * a_q)

    def test_esito_ok(self, setup) -> None:
        s, barre, n = setup
        res = calcola_asse_neutro_fessurato(s, barre, n)
        assert res["esito"] == "OK"

    def test_metodo_analitico(self, setup) -> None:
        s, barre, n = setup
        res = calcola_asse_neutro_fessurato(s, barre, n)
        assert res["metodo_calcolo"] == "ANALITICO_RETTANGOLARE"

    def test_valore_asse_neutro(self, setup) -> None:
        s, barre, n = setup
        res = calcola_asse_neutro_fessurato(s, barre, n)
        x_atteso = self._asse_neutro_analitico()
        assert res["y_na_cm"] == pytest.approx(x_atteso, rel=0.001)

    def test_asse_neutro_tra_0_e_d(self, setup) -> None:
        s, barre, n = setup
        res = calcola_asse_neutro_fessurato(s, barre, n)
        assert 0 < res["y_na_cm"] < 45.0

    def test_inerzia_fessurata(self, setup) -> None:
        s, barre, n = setup
        res = calcola_asse_neutro_fessurato(s, barre, n)
        x = res["y_na_cm"]
        d = 45.0
        As = 10.0
        I_expected = 30.0 * x ** 3 / 3.0 + n * As * (d - x) ** 2
        assert res["I_fess_cm4"] == pytest.approx(I_expected, rel=0.005)

    def test_equilibrio_verifica(self, setup) -> None:
        """Verifica l'equilibrio: b*x^2/2 = n*As*(d-x)."""
        s, barre, n = setup
        res = calcola_asse_neutro_fessurato(s, barre, n)
        x = res["y_na_cm"]
        b, As, d = 30.0, 10.0, 45.0
        lato_sx = b * x ** 2 / 2.0
        lato_dx = n * As * (d - x)
        assert lato_sx == pytest.approx(lato_dx, rel=0.005)

    def test_inerzia_fessurata_positiva(self, setup) -> None:
        s, barre, n = setup
        res = calcola_asse_neutro_fessurato(s, barre, n)
        assert res["I_fess_cm4"] > 0.0

    def test_asse_neutro_varia_con_n(self) -> None:
        """Con n maggiore, l'asse neutro sale (zona compressa piu' piccola)."""
        s = _rect(30.0, 50.0)
        barre = [BarraArmatura(y=45.0, A=10.0)]
        res_n10 = calcola_asse_neutro_fessurato(s, barre, n=10.0)
        res_n15 = calcola_asse_neutro_fessurato(s, barre, n=15.0)
        assert res_n15["y_na_cm"] > res_n10["y_na_cm"]

    def test_asse_neutro_varia_con_As(self) -> None:
        """Con As maggiore, l'asse neutro scende."""
        s = _rect(30.0, 50.0)
        b1 = [BarraArmatura(y=45.0, A=10.0)]
        b2 = [BarraArmatura(y=45.0, A=20.0)]
        r1 = calcola_asse_neutro_fessurato(s, b1, n=10.0)
        r2 = calcola_asse_neutro_fessurato(s, b2, n=10.0)
        assert r2["y_na_cm"] > r1["y_na_cm"]


class TestAssNeutroFessuratoCircolare:
    """Asse neutro per sezione circolare (metodo iterativo)."""

    def test_circolare_ok(self) -> None:
        s = _circ(40.0)
        barre = [BarraArmatura(y=35.0, A=12.0, zona="tesa")]
        res = calcola_asse_neutro_fessurato(s, barre, n=10.0)
        assert res["esito"] == "OK"
        assert res["y_na_cm"] > 0.0
        assert res["y_na_cm"] < 35.0

    def test_circolare_metodo_iterativo(self) -> None:
        s = _circ(40.0)
        barre = [BarraArmatura(y=35.0, A=12.0)]
        res = calcola_asse_neutro_fessurato(s, barre, n=10.0)
        assert res["metodo_calcolo"] == "ITERATIVO_BISECT"

    def test_i_fess_positiva(self) -> None:
        s = _circ(40.0)
        barre = [BarraArmatura(y=35.0, A=12.0)]
        res = calcola_asse_neutro_fessurato(s, barre, n=10.0)
        assert res["I_fess_cm4"] > 0.0


class TestAssNeutroFessuratoTSection:
    """Asse neutro per sezione a T (metodo iterativo)."""

    def test_t_section_ok(self) -> None:
        s = _t_sec(bf=40.0, tf=10.0, tw=15.0, hw=35.0)
        barre = [BarraArmatura(y=40.0, A=15.0, zona="tesa")]
        res = calcola_asse_neutro_fessurato(s, barre, n=10.0)
        assert res["esito"] == "OK"

    def test_t_section_an_nella_sezione(self) -> None:
        s = _t_sec(bf=40.0, tf=10.0, tw=15.0, hw=35.0)
        barre = [BarraArmatura(y=40.0, A=15.0)]
        res = calcola_asse_neutro_fessurato(s, barre, n=10.0)
        h_tot = 45.0
        assert 0 < res["y_na_cm"] < h_tot


# ===========================================================================
# TestTensioniSLE
# ===========================================================================

class TestTensioniSLE:
    """Tensioni SLE per sezione fessurata rettangolare 30×50 cm.

    Sezione rettangolare 30×50 cm, n=10, As=10 cm² a d=45 cm.
    x_na ≈ 14.305 cm, I_fess calcolato dall'asse neutro.
    Per M = 10000 kg·m = 1,000,000 kg·cm:
        sigma_c = M * x / I = 1e6 * 14.305 / I_fess
        sigma_s = n * M * (d-x) / I = 10 * 1e6 * 30.695 / I_fess
    """

    @pytest.fixture
    def setup_sle(self):
        s = _rect(30.0, 50.0)
        barre = [BarraArmatura(y=45.0, A=10.0, zona="tesa")]
        n = 10.0
        res_fess = calcola_asse_neutro_fessurato(s, barre, n)
        y_na = res_fess["y_na_cm"]
        I_fess = res_fess["I_fess_cm4"]
        M = 1_000_000.0  # kg·cm
        return y_na, I_fess, M, barre, n

    def test_esito_ok(self, setup_sle) -> None:
        y_na, I_fess, M, barre, n = setup_sle
        res = calcola_tensioni_sle(y_na, I_fess, M, barre, n)
        assert res["esito"] == "OK"

    def test_sigma_c_positiva(self, setup_sle) -> None:
        y_na, I_fess, M, barre, n = setup_sle
        res = calcola_tensioni_sle(y_na, I_fess, M, barre, n)
        assert res["sigma_c_max_kgcm2"] > 0.0

    def test_sigma_c_formula(self, setup_sle) -> None:
        y_na, I_fess, M, barre, n = setup_sle
        res = calcola_tensioni_sle(y_na, I_fess, M, barre, n)
        expected = M * y_na / I_fess
        assert res["sigma_c_max_kgcm2"] == pytest.approx(expected, rel=0.001)

    def test_sigma_s_trazione(self, setup_sle) -> None:
        """Barre tese → sigma_s > 0 (trazione)."""
        y_na, I_fess, M, barre, n = setup_sle
        res = calcola_tensioni_sle(y_na, I_fess, M, barre, n)
        sigma_s = res["barre_sigma"][0]["sigma_s_kgcm2"]
        assert sigma_s > 0.0

    def test_sigma_s_formula(self, setup_sle) -> None:
        y_na, I_fess, M, barre, n = setup_sle
        res = calcola_tensioni_sle(y_na, I_fess, M, barre, n)
        d = barre[0].y
        expected_s = n * M * (d - y_na) / I_fess
        assert res["barre_sigma"][0]["sigma_s_kgcm2"] == pytest.approx(expected_s, rel=0.001)

    def test_rapporto_sigma_s_su_sigma_c(self, setup_sle) -> None:
        """sigma_s/sigma_c = n*(d-x)/x (costante per dato n, x, d)."""
        y_na, I_fess, M, barre, n = setup_sle
        res = calcola_tensioni_sle(y_na, I_fess, M, barre, n)
        sigma_c = res["sigma_c_max_kgcm2"]
        sigma_s = res["barre_sigma"][0]["sigma_s_kgcm2"]
        d = barre[0].y
        expected_ratio = n * (d - y_na) / y_na
        assert sigma_s / sigma_c == pytest.approx(expected_ratio, rel=0.01)

    def test_errore_i_fess_zero(self) -> None:
        barre = [BarraArmatura(y=45.0, A=10.0)]
        res = calcola_tensioni_sle(5.0, 0.0, 1e6, barre, 10.0)
        assert res["esito"] == "ERRORE"

    def test_m_zero_tensioni_zero(self) -> None:
        barre = [BarraArmatura(y=45.0, A=10.0)]
        res = calcola_tensioni_sle(5.0, 100000.0, 0.0, barre, 10.0)
        assert res["esito"] == "OK"
        assert res["sigma_c_max_kgcm2"] == pytest.approx(0.0)
        assert res["barre_sigma"][0]["sigma_s_kgcm2"] == pytest.approx(0.0)


# ===========================================================================
# TestPipelineCompleta
# ===========================================================================

class TestPipelineCompleta:
    """Test pipeline calcola_parametri_sezione_completi."""

    def test_pipeline_ok(self) -> None:
        s = _rect(30.0, 50.0)
        barre = [BarraArmatura(y=45.0, A=10.0)]
        res = calcola_parametri_sezione_completi(s, barre, n=10.0, M_kgcm=500_000.0)
        assert res["esito"] == "OK"

    def test_pipeline_ha_integra(self) -> None:
        s = _rect(30.0, 50.0)
        barre = [BarraArmatura(y=45.0, A=10.0)]
        res = calcola_parametri_sezione_completi(s, barre, n=10.0)
        assert "integra" in res
        assert res["integra"]["A_omogenizzata_cm2"] > 0.0

    def test_pipeline_ha_fessurata(self) -> None:
        s = _rect(30.0, 50.0)
        barre = [BarraArmatura(y=45.0, A=10.0)]
        res = calcola_parametri_sezione_completi(s, barre, n=10.0)
        assert "fessurata" in res
        assert res["fessurata"]["y_na_cm"] is not None

    def test_pipeline_ha_tensioni_con_momento(self) -> None:
        s = _rect(30.0, 50.0)
        barre = [BarraArmatura(y=45.0, A=10.0)]
        res = calcola_parametri_sezione_completi(s, barre, n=10.0, M_kgcm=500_000.0)
        assert "tensioni_sle" in res
        assert res["tensioni_sle"]["sigma_c_max_kgcm2"] > 0.0

    def test_pipeline_norm_references(self) -> None:
        s = _rect(30.0, 50.0)
        barre = [BarraArmatura(y=45.0, A=10.0)]
        res = calcola_parametri_sezione_completi(s, barre, n=10.0, norma="NTC2018")
        assert "NTC2018" in res["norm_references"]

    def test_pipeline_coerenza_integra_fessurata(self) -> None:
        """I_fess deve essere minore di I_om (sez. fessurata piu' rigida)."""
        s = _rect(30.0, 50.0)
        barre = [BarraArmatura(y=45.0, A=10.0)]
        res = calcola_parametri_sezione_completi(s, barre, n=10.0)
        I_om = res["integra"]["I_omogenizzata_cm4"]
        I_fess = res["fessurata"]["I_fess_cm4"]
        assert I_fess < I_om


# ===========================================================================
# TestAllSectionTypes (integra + fessurata)
# ===========================================================================

class TestAllSectionTypes:
    """Verifica che le funzioni girino senza errori per tutti i tipi di sezione."""

    SECTIONS = [
        SimpleNamespace(section_type="RECTANGULAR", width=30.0, height=50.0),
        SimpleNamespace(section_type="CIRCULAR", diameter=40.0),
        SimpleNamespace(
            section_type="T_SECTION",
            flange_width=40.0, flange_thickness=10.0,
            web_thickness=15.0, web_height=35.0,
        ),
        SimpleNamespace(
            section_type="INVERTED_T_SECTION",
            flange_width=40.0, flange_thickness=10.0,
            web_thickness=15.0, web_height=35.0,
        ),
        SimpleNamespace(
            section_type="I_SECTION",
            flange_width=20.0, flange_thickness=1.5,
            web_thickness=1.0, web_height=30.0,
        ),
        SimpleNamespace(
            section_type="RECTANGULAR_HOLLOW",
            width=30.0, height=50.0, thickness=3.0,
        ),
        SimpleNamespace(
            section_type="C_SECTION",
            width=10.0, height=30.0,
            flange_thickness=1.5, web_thickness=1.0,
        ),
        SimpleNamespace(
            section_type="L_SECTION",
            width=10.0, height=15.0,
            t_horizontal=1.5, t_vertical=1.5,
        ),
    ]

    @pytest.mark.parametrize("s", SECTIONS, ids=[s.section_type for s in SECTIONS])
    def test_omogenizzata_ok(self, s) -> None:
        h = getattr(s, "height", None) or getattr(s, "diameter", None) or (
            getattr(s, "flange_thickness", 0) + getattr(s, "web_height", 0)
        )
        d = h * 0.9
        barre = [BarraArmatura(y=d, A=10.0, zona="tesa")]
        res = calcola_sezione_omogenizzata(s, barre, n=10.0)
        assert res["esito"] == "OK", f"{s.section_type}: {res['decision_log']}"
        assert res["A_omogenizzata_cm2"] > 0.0
        assert res["I_omogenizzata_cm4"] > 0.0

    @pytest.mark.parametrize("s", SECTIONS, ids=[s.section_type for s in SECTIONS])
    def test_asse_neutro_ok(self, s) -> None:
        h = getattr(s, "height", None) or getattr(s, "diameter", None) or (
            getattr(s, "flange_thickness", 0) + getattr(s, "web_height", 0)
        )
        d = h * 0.9
        barre = [BarraArmatura(y=d, A=10.0, zona="tesa")]
        res = calcola_asse_neutro_fessurato(s, barre, n=10.0)
        if res["esito"] == "OK":
            assert res["y_na_cm"] is not None
            assert 0.0 < res["y_na_cm"] < h
            assert res["I_fess_cm4"] > 0.0


# ===========================================================================
# TestSezioneComposta
# ===========================================================================

class TestSezioneComposta:
    """Test sezione composta IPE + soletta."""

    def test_ipe_non_trovato(self) -> None:
        res = calcola_sezione_composta(ipe="IPE999", b_eff=100.0, t_s=15.0, n=15.0)
        assert res["esito"] == "ERRORE"

    def test_ipe300_ok(self) -> None:
        res = calcola_sezione_composta(ipe="IPE300", b_eff=100.0, t_s=15.0, n=15.0)
        assert res["esito"] == "OK"

    def test_area_composta_positiva(self) -> None:
        res = calcola_sezione_composta(ipe="IPE300", b_eff=100.0, t_s=15.0, n=15.0)
        assert res["A_composta_cm2"] > 0.0

    def test_inerzia_composta_maggiore_di_ipe(self) -> None:
        """La soletta incrementa l'inerzia."""
        dati_ipe = IPE_TABLE["IPE300"]
        res = calcola_sezione_composta(ipe="IPE300", b_eff=100.0, t_s=15.0, n=15.0)
        assert res["I_composta_cm4"] > dati_ipe.Iy

    def test_baricentro_alzato_verso_soletta(self) -> None:
        """La soletta sposta il baricentro verso l'alto."""
        dati_ipe = IPE_TABLE["IPE300"]
        res = calcola_sezione_composta(ipe="IPE300", b_eff=100.0, t_s=15.0, n=15.0)
        y_G_ipe = dati_ipe.h / 2.0
        assert res["y_G_composta_cm"] > y_G_ipe  # baricentro si sposta sopra

    def test_w_inf_acciaio(self) -> None:
        res = calcola_sezione_composta(ipe="IPE300", b_eff=100.0, t_s=15.0, n=15.0)
        assert res["W_acciaio_inf_cm3"] > 0.0

    def test_w_cls_sup(self) -> None:
        res = calcola_sezione_composta(ipe="IPE300", b_eff=100.0, t_s=15.0, n=15.0)
        assert res["W_cls_sup_cm3"] > 0.0

    def test_n_invalido(self) -> None:
        res = calcola_sezione_composta(ipe="IPE300", b_eff=100.0, t_s=15.0, n=0.0)
        assert res["esito"] == "ERRORE"

    def test_ipe_case_insensitive(self) -> None:
        res = calcola_sezione_composta(ipe="ipe300", b_eff=100.0, t_s=15.0, n=15.0)
        assert res["esito"] == "OK"

    def test_variante_n_piccolo(self) -> None:
        """n piccolo → soletta pesa di piu' (piu' rigida)."""
        res_n15 = calcola_sezione_composta(ipe="IPE300", b_eff=100.0, t_s=15.0, n=15.0)
        res_n6 = calcola_sezione_composta(ipe="IPE300", b_eff=100.0, t_s=15.0, n=6.0)
        assert res_n6["I_composta_cm4"] > res_n15["I_composta_cm4"]

    def test_ipe_table_contains_standard_profiles(self) -> None:
        for name in ["IPE200", "IPE300", "IPE400", "IPE500"]:
            assert name in IPE_TABLE

    def test_tensioni_sle_composita(self) -> None:
        res = calcola_sezione_composta(ipe="IPE300", b_eff=100.0, t_s=15.0, n=15.0)
        y_G = res["y_G_composta_cm"]
        I = res["I_composta_cm4"]
        h_ipe = res["h_ipe_cm"]
        t_s = res["t_s_cm"]
        M = 5_000_000.0  # kg·cm
        res_sle = calcola_tensioni_sle_composita(y_G, I, M, h_ipe, t_s, 0.0, 15.0)
        assert res_sle["esito"] == "OK"
        assert res_sle["sigma_a_inf_kgcm2"] > 0.0  # trazione acciaio inf.
        assert res_sle["sigma_c_sup_kgcm2"] > 0.0  # compressione cls sup.


# ===========================================================================
# TestDisegnoSezione
# ===========================================================================

class TestDisegnoSezione:
    """Test disegno sezione con matplotlib (headless)."""

    def test_disegna_senza_errori(self) -> None:
        pytest.importorskip("matplotlib", reason="matplotlib non installato")
        from src.codes.section_params.disegno_sezione import disegna_sezione

        s = _rect(30.0, 50.0)
        barre = [BarraArmatura(y=45.0, A=10.0)]
        fig = disegna_sezione(s, barre)
        assert fig is not None

    def test_disegna_con_asse_neutro(self) -> None:
        pytest.importorskip("matplotlib", reason="matplotlib non installato")
        from src.codes.section_params.disegno_sezione import disegna_sezione

        s = _rect(30.0, 50.0)
        barre = [BarraArmatura(y=45.0, A=10.0)]
        fig = disegna_sezione(s, barre, y_na=14.3, sigma_c_max=85.0)
        assert fig is not None
        # Due assi: sezione + diagramma tensioni
        assert len(fig.axes) == 2

    def test_crea_figura_sle(self) -> None:
        pytest.importorskip("matplotlib", reason="matplotlib non installato")
        from src.codes.section_params.disegno_sezione import crea_figura_sezione_sle

        s = _rect(30.0, 50.0)
        barre = [BarraArmatura(y=45.0, A=10.0)]
        dati_sle = calcola_parametri_sezione_completi(s, barre, n=10.0, M_kgcm=500_000.0)
        fig = crea_figura_sezione_sle(s, barre, dati_sle, norma="NTC2018")
        assert fig is not None

    def test_salva_figura(self, tmp_path) -> None:
        pytest.importorskip("matplotlib", reason="matplotlib non installato")
        from src.codes.section_params.disegno_sezione import (
            disegna_sezione,
            salva_figura,
        )

        s = _rect(30.0, 50.0)
        barre = [BarraArmatura(y=45.0, A=10.0)]
        fig = disegna_sezione(s, barre)
        out = str(tmp_path / "sez_test.png")
        salva_figura(fig, out)
        assert (tmp_path / "sez_test.png").exists()
