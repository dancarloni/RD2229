"""Test cordolo reticolare — verifica Howe, Pratt, nodo angolo, dimensionamento.

Caso golden principale:
  Howe 4 campate, L=400 cm, h=30 cm, F_tot=1000 kg, Piatto 80x8
  q_y = 2.5 kg/cm; a = 100 cm; theta_diag = arctan(30/100) = 16.70°
  N_corrente_max ≈ M_max/h = q*L²/(8h) = 2.5*160000/(8*30) ≈ 1667 kg
  Montanti e diagonali assorbono la componente di taglio.
"""

from __future__ import annotations

import math

import pytest

from src.elements.cordolo_reticolare import (
    CordoloReticolare,
    InputNodoAngolo,
    SchemaReticolare,
    calcola_F_ritegno,
    dimensiona_cordolo_reticolare,
    verifica_cordolo_reticolare,
    verifica_nodo_angolo,
)
from src.steel.sezione_asta import SezioneAsta


@pytest.fixture
def piatto_80x8():
    return SezioneAsta.da_piatto(b=8.0, t=0.8)


@pytest.fixture
def cordolo_howe_base(piatto_80x8):
    return CordoloReticolare(
        schema=SchemaReticolare.HOWE,
        n_campate=4,
        L=400.0,
        h=30.0,
        sezione_corrente=piatto_80x8,
        sezione_diagonale=piatto_80x8,
        tipo_acciaio="Fe430",
        n_ancoraggi_per_nodo=2,
        phi_ancoraggio=1.6,
    )


# ───────────────────────────────────────────────
#  Verifica cordolo Howe (caso golden)
# ───────────────────────────────────────────────

class TestVerificaCordoloHowe:
    def test_convergenza(self, cordolo_howe_base):
        res = verifica_cordolo_reticolare(cordolo_howe_base, F_y=1000.0)
        assert res.convergenza is True

    def test_N_corrente_max_approx(self, cordolo_howe_base):
        res = verifica_cordolo_reticolare(cordolo_howe_base, F_y=1000.0)
        # N_corrente max ≈ M_max / h = q*L²/(8h) ≈ 1667 kg
        N_max_abs = max(abs(res.N_max_compressione), abs(res.N_max_trazione))
        assert 1200.0 <= N_max_abs <= 2500.0

    def test_K_globale_positivo(self, cordolo_howe_base):
        res = verifica_cordolo_reticolare(cordolo_howe_base, F_y=1000.0)
        assert res.K_globale > 0.0

    def test_delta_max_positivo(self, cordolo_howe_base):
        res = verifica_cordolo_reticolare(cordolo_howe_base, F_y=1000.0)
        assert res.delta_max > 0.0

    def test_verifiche_aste_17(self, cordolo_howe_base):
        res = verifica_cordolo_reticolare(cordolo_howe_base, F_y=1000.0)
        # 4+4 correnti + 5 montanti + 4 diagonali = 17 = 4n+1
        assert len(res.verifiche_aste) == 17

    def test_verifica_collegamento_presente(self, cordolo_howe_base):
        res = verifica_cordolo_reticolare(cordolo_howe_base, F_y=1000.0)
        assert "verificato" in res.verifica_collegamento

    def test_verifica_collegamento_f3_formula(self, cordolo_howe_base):
        # A_tot = 2 * pi * (1.6/2)^2 ≈ 4.021 cm²
        res = verifica_cordolo_reticolare(cordolo_howe_base, F_y=1000.0)
        vc = res.verifica_collegamento
        A_atteso = 2 * math.pi * (1.6 / 2) ** 2
        assert abs(vc["A_tot"] - A_atteso) < 0.01

    def test_tau_adm_formula(self, cordolo_howe_base):
        res = verifica_cordolo_reticolare(cordolo_howe_base, F_y=1000.0)
        vc = res.verifica_collegamento
        tau_adm_atteso = 1900.0 / math.sqrt(3)
        assert abs(vc["tau_adm"] - tau_adm_atteso) < 1.0

    def test_F_ritegno_disponibile_positivo(self, cordolo_howe_base):
        res = verifica_cordolo_reticolare(cordolo_howe_base, F_y=1000.0)
        assert res.F_ritegno_disponibile > 0.0

    def test_to_dict_keys(self, cordolo_howe_base):
        res = verifica_cordolo_reticolare(cordolo_howe_base, F_y=1000.0)
        d = res.to_dict()
        for chiave in ["convergenza", "K_globale", "delta_max", "N_max_compressione",
                       "N_max_trazione", "F_ritegno_disponibile", "verifiche_aste",
                       "verifica_collegamento", "verificato"]:
            assert chiave in d

    def test_passaggi_non_vuoti(self, cordolo_howe_base):
        res = verifica_cordolo_reticolare(cordolo_howe_base, F_y=1000.0)
        assert len(res.passaggi) > 0

    def test_F_y_proporzionale_N(self, piatto_80x8):
        # Raddoppiare F_y raddoppia N (linearità)
        c = CordoloReticolare(
            schema=SchemaReticolare.HOWE, n_campate=4,
            L=400.0, h=30.0,
            sezione_corrente=piatto_80x8, sezione_diagonale=piatto_80x8,
        )
        res1 = verifica_cordolo_reticolare(c, F_y=500.0)
        res2 = verifica_cordolo_reticolare(c, F_y=1000.0)
        if res1.N_max_trazione > 0 and res2.N_max_trazione > 0:
            ratio = res2.N_max_trazione / res1.N_max_trazione
            assert abs(ratio - 2.0) < 0.15

    def test_K_globale_inversamente_proporzionale_L(self, piatto_80x8):
        # Aumentando L a parità di schema: K diminuisce
        c1 = CordoloReticolare(
            schema=SchemaReticolare.HOWE, n_campate=4,
            L=400.0, h=30.0,
            sezione_corrente=piatto_80x8, sezione_diagonale=piatto_80x8,
        )
        c2 = CordoloReticolare(
            schema=SchemaReticolare.HOWE, n_campate=4,
            L=800.0, h=30.0,
            sezione_corrente=piatto_80x8, sezione_diagonale=piatto_80x8,
        )
        res1 = verifica_cordolo_reticolare(c1, F_y=1000.0)
        res2 = verifica_cordolo_reticolare(c2, F_y=1000.0)
        assert res1.convergenza and res2.convergenza
        assert res1.K_globale > res2.K_globale

    def test_incastro_piu_rigido_di_cerniera(self, piatto_80x8):
        c_cern = CordoloReticolare(
            schema=SchemaReticolare.HOWE, n_campate=4,
            L=400.0, h=30.0,
            sezione_corrente=piatto_80x8, sezione_diagonale=piatto_80x8,
            tipo_estremi="cerniera",
        )
        c_incastro = CordoloReticolare(
            schema=SchemaReticolare.HOWE, n_campate=4,
            L=400.0, h=30.0,
            sezione_corrente=piatto_80x8, sezione_diagonale=piatto_80x8,
            tipo_estremi="incastro",
        )
        res_c = verifica_cordolo_reticolare(c_cern, F_y=1000.0)
        res_i = verifica_cordolo_reticolare(c_incastro, F_y=1000.0)
        assert res_c.convergenza and res_i.convergenza
        # Incastro → meno spostamento → K maggiore
        assert res_i.K_globale >= res_c.K_globale


# ───────────────────────────────────────────────
#  Verifica cordolo Pratt
# ───────────────────────────────────────────────

class TestVerificaCordoloPratt:
    def test_pratt_convergenza(self, piatto_80x8):
        c = CordoloReticolare(
            schema=SchemaReticolare.PRATT, n_campate=4,
            L=400.0, h=30.0,
            sezione_corrente=piatto_80x8, sezione_diagonale=piatto_80x8,
        )
        res = verifica_cordolo_reticolare(c, F_y=1000.0)
        assert res.convergenza is True

    def test_pratt_verifiche_aste_17(self, piatto_80x8):
        c = CordoloReticolare(
            schema=SchemaReticolare.PRATT, n_campate=4,
            L=400.0, h=30.0,
            sezione_corrente=piatto_80x8, sezione_diagonale=piatto_80x8,
        )
        res = verifica_cordolo_reticolare(c, F_y=1000.0)
        # 4+4 correnti + 5 montanti + 4 diagonali = 17 = 4n+1
        assert len(res.verifiche_aste) == 17

    def test_pratt_N_corrente_max_approx(self, piatto_80x8):
        c = CordoloReticolare(
            schema=SchemaReticolare.PRATT, n_campate=4,
            L=400.0, h=30.0,
            sezione_corrente=piatto_80x8, sezione_diagonale=piatto_80x8,
        )
        res = verifica_cordolo_reticolare(c, F_y=1000.0)
        N_max_abs = max(abs(res.N_max_compressione), abs(res.N_max_trazione))
        assert 1200.0 <= N_max_abs <= 2500.0


# ───────────────────────────────────────────────
#  Verifica collegamento muro (F3)
# ───────────────────────────────────────────────

class TestCollegamento:
    def test_ancoraggi_3(self, piatto_80x8):
        # Con 3 ancoraggi: A_tot più grande
        c = CordoloReticolare(
            schema=SchemaReticolare.HOWE, n_campate=4,
            L=400.0, h=30.0,
            sezione_corrente=piatto_80x8, sezione_diagonale=piatto_80x8,
            n_ancoraggi_per_nodo=3,
        )
        res = verifica_cordolo_reticolare(c, F_y=1000.0)
        vc = res.verifica_collegamento
        assert abs(vc["A_tot"] - 3 * math.pi * (1.6 / 2) ** 2) < 0.01


# ───────────────────────────────────────────────
#  Nodo d'angolo (H1)
# ───────────────────────────────────────────────

class TestNodoAngolo:
    def test_nodo_90_risultante(self):
        inp = InputNodoAngolo(F_muro1=500.0, F_muro2=500.0, angolo_giunzione=90.0)
        res = verifica_nodo_angolo(inp)
        assert abs(res["F_risultante"] - 500.0 * math.sqrt(2)) < 1.0

    def test_nodo_0_risultante_somma(self):
        inp = InputNodoAngolo(F_muro1=300.0, F_muro2=400.0, angolo_giunzione=0.0)
        res = verifica_nodo_angolo(inp)
        assert abs(res["F_risultante"] - 700.0) < 1.0

    def test_nodo_180_risultante_diff(self):
        inp = InputNodoAngolo(F_muro1=500.0, F_muro2=300.0, angolo_giunzione=180.0)
        res = verifica_nodo_angolo(inp)
        assert abs(res["F_risultante"] - 200.0) < 1.0

    def test_nodo_angolo_contiene_verifica_saldatura(self):
        inp = InputNodoAngolo(
            F_muro1=500.0, F_muro2=500.0,
            a_saldatura=0.6, L_saldatura=10.0, n_cordoni=2,
        )
        res = verifica_nodo_angolo(inp)
        assert "verifica_saldatura" in res
        assert "verificato" in res

    def test_nodo_angolo_saldatura_grande_verifica(self):
        inp = InputNodoAngolo(
            F_muro1=100.0, F_muro2=100.0,
            a_saldatura=2.0, L_saldatura=30.0, n_cordoni=2,
        )
        res = verifica_nodo_angolo(inp)
        assert res["verificato"] is True

    def test_nodo_angolo_saldatura_piccola_non_verifica(self):
        inp = InputNodoAngolo(
            F_muro1=50000.0, F_muro2=50000.0,
            a_saldatura=0.1, L_saldatura=1.0, n_cordoni=1,
        )
        res = verifica_nodo_angolo(inp)
        assert res["verificato"] is False


# ───────────────────────────────────────────────
#  calcola_F_ritegno
# ───────────────────────────────────────────────

class TestCalcolaFRitegno:
    def _make_ris(self, alpha_0, M_stab, M_rib_coeff):
        class FakeRis:
            pass
        r = FakeRis()
        r.alpha_0 = alpha_0
        r.forze_stabilizzanti = M_stab
        r.forze_ribaltanti = M_rib_coeff
        return r

    def test_d1_base(self):
        r = self._make_ris(0.2, 10000.0, 50000.0)
        F = calcola_F_ritegno(r, alpha_0_target=0.3, h_sommita=300.0, metodo="D1")
        assert abs(F - 16.667) < 0.1

    def test_d3_base(self):
        r = self._make_ris(0.2, 10000.0, 50000.0)
        F = calcola_F_ritegno(r, alpha_0_target=0.3, h_sommita=300.0, metodo="D3")
        assert abs(F - 50000.0 * 0.1 / 300.0) < 0.1

    def test_ritegno_zero_se_gia_verificato(self):
        r = self._make_ris(0.5, 20000.0, 50000.0)
        F = calcola_F_ritegno(r, alpha_0_target=0.3, h_sommita=300.0, metodo="D1")
        assert F == 0.0

    def test_h_zero_ritorna_zero(self):
        r = self._make_ris(0.2, 5000.0, 30000.0)
        F = calcola_F_ritegno(r, alpha_0_target=0.4, h_sommita=0.0)
        assert F == 0.0


# ───────────────────────────────────────────────
#  dimensiona_cordolo_reticolare
# ───────────────────────────────────────────────

class TestDimensiona:
    def test_dimensiona_trova_profilo(self):
        cordolo = dimensiona_cordolo_reticolare(
            schema=SchemaReticolare.HOWE,
            n_campate=4,
            L=400.0,
            h=30.0,
            F_y=500.0,
            tipo_acciaio="Fe430",
            famiglia_corrente="PIATTO",
            famiglia_diagonale="PIATTO",
        )
        assert cordolo is not None

    def test_dimensiona_profilo_verifica(self):
        cordolo = dimensiona_cordolo_reticolare(
            schema=SchemaReticolare.HOWE,
            n_campate=4,
            L=400.0,
            h=30.0,
            F_y=500.0,
            tipo_acciaio="Fe430",
        )
        if cordolo is None:
            pytest.skip("Nessun profilo trovato nel catalogo")
        res = verifica_cordolo_reticolare(cordolo, F_y=500.0)
        assert res.verificato is True

    def test_cordolo_to_dict(self, cordolo_howe_base):
        d = cordolo_howe_base.to_dict()
        assert "schema" in d
        assert "L" in d
        assert "n_campate" in d
        assert d["schema"] == "howe"
