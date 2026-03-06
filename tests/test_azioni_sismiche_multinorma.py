"""Test per il package src/codes/seismic — azioni sismiche multinorma.

Copertura:
    TestDistribuzionePiani   — base.py distribuzione_triangolare
    TestAzioneRD2229         — rd2229.py
    TestAzioneDM92           — dm92.py
    TestAzioneDM96           — dm96.py
    TestAzioneOPCM3274       — opcm3274.py
    TestAzioneEC8            — ec8.py
    TestAzioneNTC2008        — ntc2008.py
    TestDispatcher           — dispatcher.py

Valori di riferimento:
    DM96 zona 2, 3 piani W=500 kN cad., h=3/6/9 m:
        F_base = 0.07 * 1500 = 105 kN
        F_piani = [10.5, 21.0, 31.5] kN (triangolare esatta: Wi*hi / sum)

    EC8 Tipo1 cat B, ag=0.25g, T_1=TC=0.5s, q=1.5, xi=5:
        S=1.2, TB=0.15, TC=0.5, TD=2.0; F0=2.5, eta=1
        Se = 0.25*9.81*1.2*2.5 = 7.3575 m/s²
        Sd = 7.3575/1.5 = 4.905 m/s²
        V_b = 4.905*1500/9.81 = 750 kN
"""

import pytest

from src.codes.seismic.base import PianoEdificio, distribuzione_triangolare
from src.codes.seismic.rd2229 import RD2229_COEFF, calcola_azione_sismica_rd2229
from src.codes.seismic.dm92 import calcola_azione_sismica_dm92
from src.codes.seismic.dm96 import calcola_azione_sismica_dm96
from src.codes.seismic.opcm3274 import ZONE_AG, TC_STAR_OPCM, calcola_azione_sismica_opcm3274
from src.codes.seismic.ec8 import EC8_TYPE1, EC8_TYPE2, calcola_azione_sismica_ec8
from src.codes.seismic.ntc2008 import calcola_azione_sismica_ntc2008
from src.codes.seismic.dispatcher import calcola_azione_sismica, NORME_SUPPORTATE


# ---------------------------------------------------------------------------
# Fixture comuni
# ---------------------------------------------------------------------------

def _piani_3(W: float = 500.0) -> list[PianoEdificio]:
    """3 piani uguali: h = 3, 6, 9 m; W = W_kN ciascuno."""
    return [
        PianoEdificio(piano=1, h_m=3.0, W_kN=W),
        PianoEdificio(piano=2, h_m=6.0, W_kN=W),
        PianoEdificio(piano=3, h_m=9.0, W_kN=W),
    ]


def _piani_raw(W: float = 500.0) -> list[dict]:
    return [
        {"piano": 1, "h_m": 3.0, "W_kN": W},
        {"piano": 2, "h_m": 6.0, "W_kN": W},
        {"piano": 3, "h_m": 9.0, "W_kN": W},
    ]


# ---------------------------------------------------------------------------
# TestDistribuzionePiani
# ---------------------------------------------------------------------------

class TestDistribuzionePiani:
    def test_distribuzione_3_piani_uguali(self):
        """Piani con W uguale: forza proporzionale ad h."""
        piani = _piani_3()
        F_base = 105.0  # kN
        dist = distribuzione_triangolare(F_base, piani)
        # sum(W*h) = 500*(3+6+9) = 9000; F_i = 105 * 500*h_i / 9000
        assert len(dist) == 3
        assert abs(dist[0]["F_kN"] - 17.5) < 0.01   # 105*3/18 = 17.5
        assert abs(dist[1]["F_kN"] - 35.0) < 0.01   # 105*6/18 = 35.0
        assert abs(dist[2]["F_kN"] - 52.5) < 0.01   # 105*9/18 = 52.5

    def test_distribuzione_somma_uguale_f_base(self):
        piani = _piani_3()
        F_base = 200.0
        dist = distribuzione_triangolare(F_base, piani)
        assert abs(sum(d["F_kN"] for d in dist) - F_base) < 1e-6

    def test_distribuzione_piani_vuoti(self):
        with pytest.raises(ValueError, match="vuota"):
            distribuzione_triangolare(100.0, [])

    def test_distribuzione_zero_wh(self):
        piani = [PianoEdificio(piano=1, h_m=0.0, W_kN=500.0)]
        with pytest.raises(ValueError):
            distribuzione_triangolare(100.0, piani)

    def test_struttura_output(self):
        dist = distribuzione_triangolare(60.0, _piani_3())
        for item in dist:
            assert "piano" in item
            assert "h_m" in item
            assert "W_kN" in item
            assert "F_kN" in item


# ---------------------------------------------------------------------------
# TestAzioneRD2229
# ---------------------------------------------------------------------------

class TestAzioneRD2229:
    def test_zona_non_sismico(self):
        res = calcola_azione_sismica_rd2229(_piani_3(), zona="non_sismico")
        assert res["F_base_kN"] == 0.0
        assert res["esito"] == "OK"

    def test_zona_bassa(self):
        res = calcola_azione_sismica_rd2229(_piani_3(), zona="bassa")
        # F = 0.05 * 1500 = 75 kN
        assert abs(res["F_base_kN"] - 75.0) < 0.01

    def test_zona_media(self):
        res = calcola_azione_sismica_rd2229(_piani_3(), zona="media")
        assert abs(res["F_base_kN"] - 105.0) < 0.01

    def test_zona_alta(self):
        res = calcola_azione_sismica_rd2229(_piani_3(), zona="alta")
        assert abs(res["F_base_kN"] - 150.0) < 0.01

    def test_avviso_nel_decision_log(self):
        res = calcola_azione_sismica_rd2229(_piani_3(), zona="alta")
        assert any("AVVISO" in msg for msg in res["decision_log"])

    def test_contratto_base(self):
        res = calcola_azione_sismica_rd2229(_piani_3(), zona="bassa")
        assert "esito" in res
        assert "norm_references" in res
        assert "decision_log" in res
        assert "trace" in res and "run_id" in res["trace"]

    def test_zona_invalida(self):
        with pytest.raises(ValueError, match="non valida"):
            calcola_azione_sismica_rd2229(_piani_3(), zona="altissima")

    def test_metodo_statico(self):
        res = calcola_azione_sismica_rd2229(_piani_3(), zona="media")
        assert res["metodo"] == "STATICO_EQUIVALENTE"


# ---------------------------------------------------------------------------
# TestAzioneDM92
# ---------------------------------------------------------------------------

class TestAzioneDM92:
    def test_zona_1(self):
        res = calcola_azione_sismica_dm92(_piani_3(), zona_sismica=1)
        assert abs(res["F_base_kN"] - 150.0) < 0.01

    def test_zona_2(self):
        res = calcola_azione_sismica_dm92(_piani_3(), zona_sismica=2)
        assert abs(res["F_base_kN"] - 105.0) < 0.01

    def test_zona_3(self):
        res = calcola_azione_sismica_dm92(_piani_3(), zona_sismica=3)
        assert abs(res["F_base_kN"] - 60.0) < 0.01

    def test_coefficiente_importanza(self):
        res = calcola_azione_sismica_dm92(_piani_3(), zona_sismica=2, I=1.5)
        assert abs(res["F_base_kN"] - 157.5) < 0.01

    def test_epsilon(self):
        res = calcola_azione_sismica_dm92(_piani_3(), zona_sismica=2, epsilon=0.8)
        assert abs(res["F_base_kN"] - 84.0) < 0.01

    def test_distribuzione_3_piani_zona2(self):
        res = calcola_azione_sismica_dm92(_piani_3(), zona_sismica=2)
        dist = res["distribuzione"]
        # F_base=105, piani uguali: forze 17.5/35.0/52.5
        assert abs(dist[0]["F_kN"] - 17.5) < 0.01
        assert abs(dist[1]["F_kN"] - 35.0) < 0.01
        assert abs(dist[2]["F_kN"] - 52.5) < 0.01

    def test_norm_references(self):
        res = calcola_azione_sismica_dm92(_piani_3(), zona_sismica=1)
        assert any("1981" in r or "1992" in r or "DM" in r for r in res["norm_references"])

    def test_zona_invalida(self):
        with pytest.raises(ValueError):
            calcola_azione_sismica_dm92(_piani_3(), zona_sismica=4)


# ---------------------------------------------------------------------------
# TestAzioneDM96
# ---------------------------------------------------------------------------

class TestAzioneDM96:
    def test_zona_1(self):
        res = calcola_azione_sismica_dm96(_piani_3(), zona_sismica=1)
        assert abs(res["F_base_kN"] - 150.0) < 0.01

    def test_zona_2(self):
        res = calcola_azione_sismica_dm96(_piani_3(), zona_sismica=2)
        assert abs(res["F_base_kN"] - 105.0) < 0.01

    def test_zona_3(self):
        res = calcola_azione_sismica_dm96(_piani_3(), zona_sismica=3)
        assert abs(res["F_base_kN"] - 60.0) < 0.01

    def test_norm_reference_dm96(self):
        """DM96 deve avere riferimento diverso da DM92."""
        res_92 = calcola_azione_sismica_dm92(_piani_3(), zona_sismica=2)
        res_96 = calcola_azione_sismica_dm96(_piani_3(), zona_sismica=2)
        assert res_92["norm_references"] != res_96["norm_references"]

    def test_stessi_valori_dm92(self):
        """Stessa formula: F_base identica."""
        res_92 = calcola_azione_sismica_dm92(_piani_3(), zona_sismica=2)
        res_96 = calcola_azione_sismica_dm96(_piani_3(), zona_sismica=2)
        assert res_92["F_base_kN"] == res_96["F_base_kN"]

    def test_metodo(self):
        res = calcola_azione_sismica_dm96(_piani_3(), zona_sismica=2)
        assert res["metodo"] == "STATICO_EQUIVALENTE"


# ---------------------------------------------------------------------------
# TestAzioneOPCM3274
# ---------------------------------------------------------------------------

class TestAzioneOPCM3274:
    def test_zona_1_cat_b(self):
        res = calcola_azione_sismica_opcm3274(
            _piani_3(), zona=1, T_1=0.5, cat_suolo="B"
        )
        assert res["F_base_kN"] > 0
        assert res["ag_g"] == pytest.approx(0.35)

    def test_zona_4_ag(self):
        res = calcola_azione_sismica_opcm3274(
            _piani_3(), zona=4, T_1=0.5, cat_suolo="A"
        )
        assert res["ag_g"] == pytest.approx(0.05)

    def test_zona_invalida(self):
        with pytest.raises(ValueError):
            calcola_azione_sismica_opcm3274(_piani_3(), zona=5, T_1=0.5)

    def test_metodo_spettrale(self):
        res = calcola_azione_sismica_opcm3274(_piani_3(), zona=2, T_1=0.5)
        assert res["metodo"] == "SPETTRALE"

    def test_output_se_t1(self):
        res = calcola_azione_sismica_opcm3274(_piani_3(), zona=2, T_1=0.5)
        assert "Se_T1_ms2" in res
        assert res["Se_T1_ms2"] > 0

    def test_q_riduce_vb(self):
        res_q1 = calcola_azione_sismica_opcm3274(_piani_3(), zona=1, T_1=0.5, q=1.0)
        res_q2 = calcola_azione_sismica_opcm3274(_piani_3(), zona=1, T_1=0.5, q=2.0)
        assert res_q1["F_base_kN"] > res_q2["F_base_kN"]


# ---------------------------------------------------------------------------
# TestAzioneEC8
# ---------------------------------------------------------------------------

class TestAzioneEC8:
    def test_tipo1_cat_b_riferimento(self):
        """Valore di riferimento: V_b = 750 kN per ag=0.25g, T_1=TC=0.5s, q=1.5."""
        res = calcola_azione_sismica_ec8(
            _piani_3(),
            ag_g=0.25,
            cat_suolo="B",
            T_1=0.5,
            tipo_spettro="TIPO1",
            q=1.5,
        )
        # Se(T_1=TC=0.5) = ag*S*eta*F0 = 0.25*9.81*1.2*2.5 = 7.3575 m/s²
        # Sd = 7.3575/1.5 = 4.905 m/s²; V_b = 4.905*1500/9.81 = 750 kN
        assert abs(res["F_base_kN"] - 750.0) < 1.0
        assert res["metodo"] == "SPETTRALE"

    def test_tipo1_cat_a(self):
        res = calcola_azione_sismica_ec8(
            _piani_3(), ag_g=0.25, cat_suolo="A", T_1=0.5, tipo_spettro="TIPO1"
        )
        # S=1.0 (cat A), minore di cat B (S=1.2)
        res_b = calcola_azione_sismica_ec8(
            _piani_3(), ag_g=0.25, cat_suolo="B", T_1=0.5, tipo_spettro="TIPO1"
        )
        assert res["F_base_kN"] < res_b["F_base_kN"]

    def test_tipo2_minore_tipo1_per_ag_bassa(self):
        """Per ag basso, Tipo2 ha S superiore ma periodi diversi; verifica solo struttura."""
        res = calcola_azione_sismica_ec8(
            _piani_3(), ag_g=0.1, cat_suolo="B", T_1=0.5, tipo_spettro="TIPO2"
        )
        assert res["F_base_kN"] > 0
        assert res["tipo_spettro"] == "TIPO2"

    def test_q_riduce_vb(self):
        res_q1 = calcola_azione_sismica_ec8(
            _piani_3(), ag_g=0.25, cat_suolo="B", T_1=0.5, q=1.0
        )
        res_q2 = calcola_azione_sismica_ec8(
            _piani_3(), ag_g=0.25, cat_suolo="B", T_1=0.5, q=2.0
        )
        assert res_q1["F_base_kN"] > res_q2["F_base_kN"]

    def test_tipo_spettro_invalido(self):
        with pytest.raises(ValueError, match="non valido"):
            calcola_azione_sismica_ec8(
                _piani_3(), ag_g=0.25, cat_suolo="B", T_1=0.5, tipo_spettro="TIPO3"
            )

    def test_cat_suolo_invalida(self):
        with pytest.raises(ValueError, match="non valida"):
            calcola_azione_sismica_ec8(
                _piani_3(), ag_g=0.25, cat_suolo="Z", T_1=0.5
            )

    def test_contratto_base(self):
        res = calcola_azione_sismica_ec8(
            _piani_3(), ag_g=0.25, cat_suolo="B", T_1=0.5
        )
        assert "esito" in res
        assert "norm_references" in res
        assert "decision_log" in res
        assert "trace" in res

    def test_distribuzione_piani(self):
        res = calcola_azione_sismica_ec8(
            _piani_3(), ag_g=0.25, cat_suolo="B", T_1=0.5
        )
        dist = res["distribuzione"]
        assert len(dist) == 3
        assert abs(sum(d["F_kN"] for d in dist) - res["F_base_kN"]) < 1e-3


# ---------------------------------------------------------------------------
# TestAzioneNTC2008
# ---------------------------------------------------------------------------

class TestAzioneNTC2008:
    _KWARGS = dict(
        ag_g=0.168,
        F0=2.398,
        TC_star=0.327,
        cat_suolo="B",
        cat_topografica="T1",
        T_1=0.5,
        q=1.5,
    )

    def test_f_base_positivo(self):
        res = calcola_azione_sismica_ntc2008(_piani_3(), **self._KWARGS)
        assert res["F_base_kN"] > 0

    def test_metodo_spettrale(self):
        res = calcola_azione_sismica_ntc2008(_piani_3(), **self._KWARGS)
        assert res["metodo"] == "SPETTRALE"

    def test_norm_reference(self):
        res = calcola_azione_sismica_ntc2008(_piani_3(), **self._KWARGS)
        assert any("2008" in r for r in res["norm_references"])

    def test_coerente_con_ntc2018(self):
        """Stessi parametri ag/F0/TC*: NTC2008 e NTC2018 devono dare lo stesso V_b."""
        from src.codes.seismic.dispatcher import calcola_azione_sismica
        spec = {
            "piani": _piani_raw(),
            "ag_g": 0.168,
            "F0": 2.398,
            "TC_star": 0.327,
            "cat_suolo": "B",
            "cat_topografica": "T1",
            "T_1": 0.5,
            "q": 1.5,
        }
        res08 = calcola_azione_sismica("NTC2008", spec)
        res18 = calcola_azione_sismica("NTC2018", spec)
        assert abs(res08["F_base_kN"] - res18["F_base_kN"]) < 0.01

    def test_output_periodi(self):
        res = calcola_azione_sismica_ntc2008(_piani_3(), **self._KWARGS)
        assert "TB_s" in res
        assert "TC_s" in res
        assert "TD_s" in res
        assert res["TC_s"] > res["TB_s"]


# ---------------------------------------------------------------------------
# TestDispatcher
# ---------------------------------------------------------------------------

class TestDispatcher:
    def test_routing_dm96(self):
        res = calcola_azione_sismica("DM96", {
            "piani": _piani_raw(),
            "zona_sismica": 2,
        })
        assert abs(res["F_base_kN"] - 105.0) < 0.01

    def test_routing_rd2229(self):
        res = calcola_azione_sismica("RD2229", {
            "piani": _piani_raw(),
            "zona": "alta",
        })
        assert abs(res["F_base_kN"] - 150.0) < 0.01

    def test_routing_ec8(self):
        res = calcola_azione_sismica("EC8", {
            "piani": _piani_raw(),
            "ag_g": 0.25,
            "cat_suolo": "B",
            "T_1": 0.5,
        })
        assert res["F_base_kN"] > 0

    def test_routing_opcm3274(self):
        res = calcola_azione_sismica("OPCM3274", {
            "piani": _piani_raw(),
            "zona": 2,
            "T_1": 0.5,
        })
        assert res["F_base_kN"] > 0

    def test_norma_invalida(self):
        with pytest.raises(ValueError, match="non supportata"):
            calcola_azione_sismica("DM_SCONOSCIUTA", {"piani": _piani_raw()})

    def test_case_insensitive(self):
        res = calcola_azione_sismica("dm96", {
            "piani": _piani_raw(),
            "zona_sismica": 2,
        })
        assert res["F_base_kN"] > 0

    def test_contratto_base_presente(self):
        res = calcola_azione_sismica("DM92", {
            "piani": _piani_raw(),
            "zona_sismica": 1,
        })
        assert "esito" in res
        assert "norm_references" in res
        assert "decision_log" in res
        assert "trace" in res

    def test_norme_supportate_set(self):
        assert "DM96" in NORME_SUPPORTATE
        assert "EC8" in NORME_SUPPORTATE
        assert "NTC2018" in NORME_SUPPORTATE
