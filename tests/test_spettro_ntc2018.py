"""Test modulo spettro NTC2018 — src/codes/ntc2018/spectrum.py.

Valori di riferimento Roma (NTC2018 Allegato B, SLV, VR=50a, cat B, T1):
  ag_g = 0.168, F0 = 2.398, TC* = 0.327 s
  SS_B = 1.0 + 0.40*(2.398*0.168 - 0.22) = 1.0 + 0.40*0.182864 = 1.07315
  CC_B = 1.1 * 0.327^(-0.20) = 1.1 * 1.25049 = 1.37554
  TC   = CC * TC* = 1.37554 * 0.327 = 0.44980 s
  TB   = TC / 3 = 0.14993 s
  TD   = 4 * 0.168 + 1.6 = 2.272 s
  alpha_S = ag_g * SS * ST = 0.168 * 1.07315 * 1.0 = 0.18029

Riferimenti:
  NTC2018 §3.2.3, Tab. 3.2.IV, 3.2.V, 3.2.VI, 2.4.II
"""

import pytest

from src.codes.ntc2018.spectrum import (
    CategoriaSuolo,
    CategoriaTopografica,
    ClasseUso,
    calcola_CC,
    calcola_S_d_T1,
    calcola_ST,
    calcola_SS,
    calcola_VR,
    calcola_alpha_S,
    calcola_periodi,
    spettro_da_hazard_row,
    spettro_elastico,
    spettro_progetto,
)

# ---------------------------------------------------------------------------
# Fixture: HazardRow Roma di riferimento
# ---------------------------------------------------------------------------

class _FakeHazardRow:
    """Sostituto di Ntc2018HazardRow per i test (evita dipendenza da EdiLus-MS)."""
    def __init__(self, ag_g, f0, tc_star_s, limit_state_label="SLV", tr_years=475):
        self.ag_g = ag_g
        self.f0 = f0
        self.tc_star_s = tc_star_s
        self.limit_state_label = limit_state_label
        self.tr_years = tr_years


# Parametri Roma SLV
_AG = 0.168
_F0 = 2.398
_TC_STAR = 0.327
_ROW_ROMA = _FakeHazardRow(ag_g=_AG, f0=_F0, tc_star_s=_TC_STAR)

# Valori attesi Roma cat B / T1
_SS_ROMA_B = 1.0 + 0.40 * (_F0 * _AG - 0.22)  # 1.07315
_CC_ROMA_B = 1.1 * (_TC_STAR ** -0.20)          # 1.37554
_TC_ROMA = _CC_ROMA_B * _TC_STAR                # 0.44980 s
_TB_ROMA = _TC_ROMA / 3.0                       # 0.14993 s
_TD_ROMA = 4.0 * _AG + 1.6                      # 2.272 s


# ---------------------------------------------------------------------------
# TestCalcolaVR
# ---------------------------------------------------------------------------

class TestCalcolaVR:
    def test_classe_ii_vn50(self):
        assert calcola_VR(50, ClasseUso.II) == 50

    def test_classe_i_vn50(self):
        # VR = int(50 * 0.7) = 35; max(35, 35) = 35
        assert calcola_VR(50, ClasseUso.I) == 35

    def test_classe_iii_vn50(self):
        assert calcola_VR(50, ClasseUso.III) == 75

    def test_classe_iv_vn50(self):
        assert calcola_VR(50, ClasseUso.IV) == 100

    def test_minimo_35_anni(self):
        # VN=10, Cu=0.7 -> VR=7 -> min 35
        assert calcola_VR(10, ClasseUso.I) == 35


# ---------------------------------------------------------------------------
# TestCalcolaSS
# ---------------------------------------------------------------------------

class TestCalcolaSS:
    def test_categoria_A(self):
        assert calcola_SS(0.168, 2.398, CategoriaSuolo.A) == pytest.approx(1.0, rel=1e-6)

    def test_categoria_B_bassa_ag(self):
        # ag=0.168, F0=2.398: SS = 1+0.40*(2.398*0.168-0.22) = 1.07315
        ss = calcola_SS(0.168, 2.398, CategoriaSuolo.B)
        assert ss == pytest.approx(_SS_ROMA_B, rel=1e-3)

    def test_categoria_B_alta_ag(self):
        # ag=0.30 > 0.25 -> cap = 1.0
        assert calcola_SS(0.30, 2.5, CategoriaSuolo.B) == pytest.approx(1.0, rel=1e-3)

    def test_categoria_C(self):
        # ag=0.1, F0=2.4: SS = 1+0.50*(2.4*0.1-0.22) = 1+0.50*0.02 = 1.01
        ss = calcola_SS(0.1, 2.4, CategoriaSuolo.C)
        assert ss == pytest.approx(1.01, rel=1e-3)

    def test_categoria_D_puo_essere_minore_1(self):
        # ag=0.05, F0=2.5: SS = 0.9+0.90*(2.5*0.05-0.22) = 0.9+0.90*(-0.095) = 0.8145
        ss = calcola_SS(0.05, 2.5, CategoriaSuolo.D)
        assert ss == pytest.approx(0.8145, rel=1e-3)
        assert ss < 1.0  # categoria D ammette SS < 1

    def test_categoria_E(self):
        # ag=0.1, F0=2.4: SS = 1+0.60*(2.4*0.1-0.22) = 1+0.60*0.02 = 1.012
        ss = calcola_SS(0.1, 2.4, CategoriaSuolo.E)
        assert ss == pytest.approx(1.012, rel=1e-3)


# ---------------------------------------------------------------------------
# TestCalcolaST
# ---------------------------------------------------------------------------

class TestCalcolaST:
    def test_T1(self):
        assert calcola_ST(CategoriaTopografica.T1) == pytest.approx(1.0)

    def test_T2(self):
        assert calcola_ST(CategoriaTopografica.T2) == pytest.approx(1.2)

    def test_T3(self):
        assert calcola_ST(CategoriaTopografica.T3) == pytest.approx(1.2)

    def test_T4(self):
        assert calcola_ST(CategoriaTopografica.T4) == pytest.approx(1.4)


# ---------------------------------------------------------------------------
# TestCalcolaCC
# ---------------------------------------------------------------------------

class TestCalcolaCC:
    def test_categoria_A(self):
        assert calcola_CC(CategoriaSuolo.A, 0.327) == pytest.approx(1.0, rel=1e-6)

    def test_categoria_B(self):
        # CC = 1.1 * 0.327^(-0.20)
        assert calcola_CC(CategoriaSuolo.B, 0.327) == pytest.approx(_CC_ROMA_B, rel=1e-3)

    def test_categoria_C(self):
        # CC = 1.05 * 0.327^(-0.33)
        import math
        cc = 1.05 * (0.327 ** -0.33)
        assert calcola_CC(CategoriaSuolo.C, 0.327) == pytest.approx(cc, rel=1e-3)

    def test_categoria_D(self):
        # CC = 1.25 * 0.327^(-0.50) = 1.25 / sqrt(0.327)
        import math
        cc = 1.25 / math.sqrt(0.327)
        assert calcola_CC(CategoriaSuolo.D, 0.327) == pytest.approx(cc, rel=1e-3)

    def test_categoria_E(self):
        # CC = 1.15 * 0.327^(-0.40)
        cc = 1.15 * (0.327 ** -0.40)
        assert calcola_CC(CategoriaSuolo.E, 0.327) == pytest.approx(cc, rel=1e-3)

    def test_tc_star_zero_raises(self):
        with pytest.raises(ValueError):
            calcola_CC(CategoriaSuolo.B, 0.0)


# ---------------------------------------------------------------------------
# TestCalcolaPeriodi
# ---------------------------------------------------------------------------

class TestCalcolaPeriodi:
    def test_TB_TC_TD_roma(self):
        TB, TC, TD = calcola_periodi(_TC_STAR, _CC_ROMA_B, _AG)
        assert TC == pytest.approx(_TC_ROMA, rel=1e-3)
        assert TB == pytest.approx(_TB_ROMA, rel=1e-3)
        assert TD == pytest.approx(2.272, rel=1e-3)

    def test_TB_e_un_terzo_TC(self):
        TB, TC, TD = calcola_periodi(0.30, 1.0, 0.25)
        assert TB == pytest.approx(TC / 3.0, rel=1e-9)

    def test_TD_dipende_da_ag(self):
        _, _, TD = calcola_periodi(0.30, 1.2, 0.3)
        assert TD == pytest.approx(4.0 * 0.3 + 1.6, rel=1e-6)


# ---------------------------------------------------------------------------
# TestCalcolaAlphaS
# ---------------------------------------------------------------------------

class TestCalcolaAlphaS:
    def test_roma_cat_B_T1(self):
        alpha = calcola_alpha_S(_AG, _SS_ROMA_B, 1.0)
        assert alpha == pytest.approx(_AG * _SS_ROMA_B, rel=1e-6)

    def test_con_topografica_T4(self):
        alpha = calcola_alpha_S(0.2, 1.3, 1.4)
        assert alpha == pytest.approx(0.2 * 1.3 * 1.4, rel=1e-6)

    def test_categoria_A_pianeggiante(self):
        alpha = calcola_alpha_S(0.1, 1.0, 1.0)
        assert alpha == pytest.approx(0.1, rel=1e-6)


# ---------------------------------------------------------------------------
# TestSpettroElastico
# ---------------------------------------------------------------------------

class TestSpettroElastico:
    """Test spettro elastico con parametri Roma cat B / T1 (xi=5%)."""

    def _params(self):
        return dict(
            ag_g=_AG, F0=_F0, SS=_SS_ROMA_B, ST=1.0,
            TB=_TB_ROMA, TC=_TC_ROMA, TD=_TD_ROMA, xi=5.0,
        )

    def test_T0_uguale_ag_S(self):
        # T=0 < TB: Se = ag*S*(1+0*(eta*F0-1)) = ag*S
        p = self._params()
        Se = spettro_elastico(**p, T=0.0)
        ag_S = _AG * 9.81 * _SS_ROMA_B * 1.0
        assert Se == pytest.approx(ag_S, rel=1e-3)

    def test_ramo_ascendente(self):
        # T = TB/2 < TB
        p = self._params()
        T = _TB_ROMA / 2.0
        Se = spettro_elastico(**p, T=T)
        ag_S = _AG * 9.81 * _SS_ROMA_B
        eta = 1.0
        expected = ag_S * (1.0 + (T / _TB_ROMA) * (eta * _F0 - 1.0))
        assert Se == pytest.approx(expected, rel=1e-3)

    def test_plateau(self):
        # TB <= T < TC: Se = ag*S*eta*F0
        p = self._params()
        T = (_TB_ROMA + _TC_ROMA) / 2.0
        Se = spettro_elastico(**p, T=T)
        expected = _AG * 9.81 * _SS_ROMA_B * 1.0 * _F0
        assert Se == pytest.approx(expected, rel=1e-3)

    def test_ramo_discendente(self):
        # TC <= T < TD: Se *= TC/T
        p = self._params()
        T = 0.9
        Se_plateau = _AG * 9.81 * _SS_ROMA_B * _F0
        expected = Se_plateau * (_TC_ROMA / T)
        Se = spettro_elastico(**p, T=T)
        assert Se == pytest.approx(expected, rel=1e-3)

    def test_ramo_spostamento_costante(self):
        # T >= TD: Se *= TC*TD/T^2
        p = self._params()
        T = 3.0
        Se_plateau = _AG * 9.81 * _SS_ROMA_B * _F0
        expected = Se_plateau * (_TC_ROMA * _TD_ROMA / T ** 2)
        Se = spettro_elastico(**p, T=T)
        assert Se == pytest.approx(expected, rel=1e-3)

    def test_eta_smorzamento_diverso(self):
        # xi=10%: eta = sqrt(10/(5+10)) = sqrt(0.667) = 0.8165 (>= 0.55)
        import math
        xi = 10.0
        eta = math.sqrt(10.0 / (5.0 + xi))
        T = (_TB_ROMA + _TC_ROMA) / 2.0
        Se = spettro_elastico(
            ag_g=_AG, F0=_F0, SS=_SS_ROMA_B, ST=1.0,
            TB=_TB_ROMA, TC=_TC_ROMA, TD=_TD_ROMA, xi=xi, T=T
        )
        expected = _AG * 9.81 * _SS_ROMA_B * eta * _F0
        assert Se == pytest.approx(expected, rel=1e-3)

    def test_T_negativo_raises(self):
        p = self._params()
        with pytest.raises(ValueError):
            spettro_elastico(**p, T=-0.1)


# ---------------------------------------------------------------------------
# TestSpettroProgetto
# ---------------------------------------------------------------------------

class TestSpettroProgetto:
    def test_sd_uguale_se_diviso_q(self):
        TB, TC, TD = calcola_periodi(_TC_STAR, _CC_ROMA_B, _AG)
        T = 0.5
        Se = spettro_elastico(_AG, _F0, _SS_ROMA_B, 1.0, TB, TC, TD, 5.0, T)
        Sd = spettro_progetto(_AG, _F0, _SS_ROMA_B, 1.0, TB, TC, TD, 2.0, T)
        assert Sd == pytest.approx(Se / 2.0, rel=1e-6)

    def test_q_zero_raises(self):
        TB, TC, TD = calcola_periodi(_TC_STAR, _CC_ROMA_B, _AG)
        with pytest.raises(ValueError):
            spettro_progetto(_AG, _F0, _SS_ROMA_B, 1.0, TB, TC, TD, 0.0, 0.5)


# ---------------------------------------------------------------------------
# TestCalcolaS_d_T1
# ---------------------------------------------------------------------------

class TestCalcolaS_d_T1:
    def test_valore_Roma_T1_0_5s(self):
        # T_1=0.5s in ramo discendente (TC < 0.5 < TD)
        import math
        TB, TC, TD = calcola_periodi(_TC_STAR, _CC_ROMA_B, _AG)
        T_1 = 0.5
        Sd = spettro_progetto(_AG, _F0, _SS_ROMA_B, 1.0, TB, TC, TD, 2.0, T_1)
        expected = Sd * (T_1 / (2.0 * math.pi)) ** 2
        result = calcola_S_d_T1(T_1, _AG, _F0, _SS_ROMA_B, 1.0, TB, TC, TD, 2.0)
        assert result == pytest.approx(expected, rel=1e-6)

    def test_T1_zero_raises(self):
        TB, TC, TD = calcola_periodi(_TC_STAR, _CC_ROMA_B, _AG)
        with pytest.raises(ValueError):
            calcola_S_d_T1(0.0, _AG, _F0, _SS_ROMA_B, 1.0, TB, TC, TD, 2.0)


# ---------------------------------------------------------------------------
# TestSpettroDaHazardRow
# ---------------------------------------------------------------------------

class TestSpettroDaHazardRow:
    def test_chiavi_output_presenti(self):
        result = spettro_da_hazard_row(_ROW_ROMA, CategoriaSuolo.B, CategoriaTopografica.T1)
        for chiave in ("SS", "ST", "S", "CC", "TB", "TC", "TD", "alpha_S",
                       "Se_func", "Sd_func", "decision_log"):
            assert chiave in result

    def test_valori_Roma_cat_B_T1(self):
        result = spettro_da_hazard_row(_ROW_ROMA, CategoriaSuolo.B, CategoriaTopografica.T1)
        assert result["SS"] == pytest.approx(_SS_ROMA_B, rel=1e-3)
        assert result["ST"] == pytest.approx(1.0)
        assert result["CC"] == pytest.approx(_CC_ROMA_B, rel=1e-3)
        assert result["TC"] == pytest.approx(_TC_ROMA, rel=1e-3)
        assert result["TD"] == pytest.approx(2.272, rel=1e-3)
        assert result["alpha_S"] == pytest.approx(_AG * _SS_ROMA_B, rel=1e-3)

    def test_Se_func_e_Sd_func_coerenti(self):
        result = spettro_da_hazard_row(_ROW_ROMA, CategoriaSuolo.B, CategoriaTopografica.T1)
        T = 0.5
        Se = result["Se_func"](T)
        Sd = result["Sd_func"](T, 2.0)
        assert Sd == pytest.approx(Se / 2.0, rel=1e-6)
        assert len(result["decision_log"]) >= 4

    def test_decision_log_contiene_valori(self):
        result = spettro_da_hazard_row(_ROW_ROMA, CategoriaSuolo.B, CategoriaTopografica.T1)
        log = "\n".join(result["decision_log"])
        assert "SS" in log
        assert "ST" in log
        assert "alpha_S" in log


# ---------------------------------------------------------------------------
# TestIntegrazione — spectral_acceleration_floor_from_site
# ---------------------------------------------------------------------------

class TestSpectralAccelerationFloorFromSite:
    """Verifica integrazione spectrum.py con ta_models.py."""

    def test_equivalente_a_alpha_S_manuale(self):
        from src.codes.ntc2018.secondary_elements.ta_models import (
            spectral_acceleration_floor,
            spectral_acceleration_floor_from_site,
        )
        SS = calcola_SS(_AG, _F0, CategoriaSuolo.B)
        ST = calcola_ST(CategoriaTopografica.T1)
        alpha_S = calcola_alpha_S(_AG, SS, ST)

        S_a_manuale = spectral_acceleration_floor(5.0, 10.0, 0.2, 0.5, alpha_S)
        S_a_sito = spectral_acceleration_floor_from_site(
            5.0, 10.0, 0.2, 0.5,
            _AG, _F0, _TC_STAR,
            CategoriaSuolo.B, CategoriaTopografica.T1,
        )
        assert S_a_sito == pytest.approx(S_a_manuale, rel=1e-6)


# ---------------------------------------------------------------------------
# TestIntegrazione — check_slu con parametri sito
# ---------------------------------------------------------------------------

class TestCheckSluDaSito:
    """Verifica integrazione spectrum.py con checks.py."""

    def test_S_a_calcolata_internamente(self):
        from src.codes.ntc2018.secondary_elements.checks import check_slu
        inputs_sito = {
            "W_a": 5.0,
            "ag_g": _AG,
            "F0": _F0,
            "TC_star": _TC_STAR,
            "cat_suolo": CategoriaSuolo.B,
            "cat_topografica": CategoriaTopografica.T1,
            "z": 6.0,
            "H": 12.0,
            "T_a": 0.0,
            "T_1": 0.5,
            "gamma_a": 1.0,
            "q_a": 2.0,
        }
        result = check_slu(inputs_sito)
        assert "F_a_kN" in result
        assert result["F_a_kN"] > 0
        # Verifica che il log menzioni il calcolo interno
        log_str = "\n".join(result["decision_log"])
        assert "S_a calcolata da sito" in log_str

    def test_S_a_esplicita_non_modificata(self):
        from src.codes.ntc2018.secondary_elements.checks import check_slu
        inputs_diretti = {"W_a": 5.0, "S_a": 0.5, "gamma_a": 1.0, "q_a": 2.0}
        result = check_slu(inputs_diretti)
        # F_a = 0.5 * 5.0 * 1.0 / 2.0 = 1.25
        assert result["F_a_kN"] == pytest.approx(1.25, rel=1e-6)


# ---------------------------------------------------------------------------
# TestIntegrazione — parametri_sismici_da_sito
# ---------------------------------------------------------------------------

class TestParametriSismiciDaSito:
    """Verifica integrazione spectrum.py con cinematica.py."""

    def test_S_calcolato_da_sito(self):
        from src.methods.muratura.cinematica import parametri_sismici_da_sito
        sismici = parametri_sismici_da_sito(
            ag_g=_AG, F0=_F0, TC_star=_TC_STAR,
            cat_suolo=CategoriaSuolo.B,
            cat_topografica=CategoriaTopografica.T1,
        )
        SS = calcola_SS(_AG, _F0, CategoriaSuolo.B)
        ST = calcola_ST(CategoriaTopografica.T1)
        assert sismici.a_g == pytest.approx(_AG, rel=1e-9)
        assert sismici.S == pytest.approx(SS * ST, rel=1e-6)

    def test_defaults(self):
        from src.methods.muratura.cinematica import parametri_sismici_da_sito
        sismici = parametri_sismici_da_sito(
            ag_g=0.1, F0=2.4, TC_star=0.3,
            cat_suolo=CategoriaSuolo.A,
            cat_topografica=CategoriaTopografica.T1,
        )
        assert sismici.q == pytest.approx(2.0)
        assert sismici.FC == pytest.approx(1.35)
        assert sismici.T1 == pytest.approx(0.0)
