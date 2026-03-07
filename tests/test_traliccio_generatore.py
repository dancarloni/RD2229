"""Test per traliccio_generatore — Howe, Pratt, predimensionamento, validazione."""

from __future__ import annotations

import pytest

from src.steel.sezione_asta import SezioneAsta
from src.steel.traliccio_2d import TipoVincolo
from src.steel.traliccio_generatore import (
    genera_howe,
    genera_pratt,
    applica_vincoli_cordolo,
    n_campate_default,
    valida_geometria,
    predimensiona_sezione,
)


@pytest.fixture
def sezione_base():
    return SezioneAsta.da_piatto(b=8.0, t=0.8)


# ───────────────────────────────────────────────
#  Schema Howe — topologia
# ───────────────────────────────────────────────

class TestHowe:
    def test_howe_4_campate_nodi(self, sezione_base):
        nodi, _ = genera_howe(400.0, 30.0, 4, sezione_base, sezione_base)
        assert len(nodi) == 10  # 5 inf + 5 sup

    def test_howe_4_campate_aste(self, sezione_base):
        _, aste = genera_howe(400.0, 30.0, 4, sezione_base, sezione_base)
        # 4 correnti inf + 4 correnti sup + 5 montanti + 4 diagonali = 17 = 4n+1
        assert len(aste) == 17

    def test_howe_nodi_corrente_inf_y0(self, sezione_base):
        nodi, _ = genera_howe(400.0, 30.0, 4, sezione_base, sezione_base)
        assert len([n for n in nodi if abs(n.y) < 1e-6]) == 5

    def test_howe_nodi_corrente_sup_yh(self, sezione_base):
        nodi, _ = genera_howe(400.0, 30.0, 4, sezione_base, sezione_base)
        assert len([n for n in nodi if abs(n.y - 30.0) < 1e-6]) == 5

    def test_howe_x_corrette(self, sezione_base):
        nodi, _ = genera_howe(400.0, 30.0, 4, sezione_base, sezione_base)
        x_attesi = [0.0, 100.0, 200.0, 300.0, 400.0]
        x_inf = sorted(n.x for n in nodi if abs(n.y) < 1e-6)
        assert all(abs(xi - xa) < 1e-6 for xi, xa in zip(x_inf, x_attesi))

    def test_howe_id_aste_unici(self, sezione_base):
        _, aste = genera_howe(400.0, 30.0, 4, sezione_base, sezione_base)
        ids = [a.id for a in aste]
        assert len(ids) == len(set(ids))

    def test_howe_2_campate(self, sezione_base):
        nodi, aste = genera_howe(200.0, 30.0, 2, sezione_base, sezione_base)
        assert len(nodi) == 6   # 3+3
        assert len(aste) == 9   # 4n+1 = 9

    def test_howe_6_campate(self, sezione_base):
        nodi, aste = genera_howe(600.0, 40.0, 6, sezione_base, sezione_base)
        assert len(nodi) == 14  # 7+7
        assert len(aste) == 25  # 4n+1 = 25

    def test_howe_area_corrente(self, sezione_base):
        sc = SezioneAsta.da_piatto(b=10.0, t=1.0)
        sd = SezioneAsta.da_piatto(b=6.0, t=0.6)
        _, aste = genera_howe(400.0, 30.0, 4, sc, sd)
        # Prime 4+4 correnti hanno area = sc.A
        for a in aste[:8]:
            assert abs(a.A - sc.A) < 1e-6

    def test_howe_area_diagonale(self, sezione_base):
        sc = SezioneAsta.da_piatto(b=10.0, t=1.0)
        sd = SezioneAsta.da_piatto(b=6.0, t=0.6)
        _, aste = genera_howe(400.0, 30.0, 4, sc, sd)
        # Ultime 4 aste sono diagonali con area = sd.A
        for a in aste[-4:]:
            assert abs(a.A - sd.A) < 1e-6


# ───────────────────────────────────────────────
#  Schema Pratt — topologia
# ───────────────────────────────────────────────

class TestPratt:
    def test_pratt_4_campate_aste(self, sezione_base):
        _, aste = genera_pratt(400.0, 30.0, 4, sezione_base, sezione_base)
        # 4+4+5+4 = 17 = 4n+1
        assert len(aste) == 17

    def test_pratt_4_campate_nodi(self, sezione_base):
        nodi, _ = genera_pratt(400.0, 30.0, 4, sezione_base, sezione_base)
        assert len(nodi) == 10

    def test_pratt_2_campate(self, sezione_base):
        _, aste = genera_pratt(200.0, 30.0, 2, sezione_base, sezione_base)
        assert len(aste) == 9   # 4n+1

    def test_pratt_6_campate(self, sezione_base):
        _, aste = genera_pratt(600.0, 40.0, 6, sezione_base, sezione_base)
        assert len(aste) == 25  # 4n+1

    def test_pratt_montante_sezione_diversa(self, sezione_base):
        sm = SezioneAsta.da_piatto(b=6.0, t=0.6)
        _, aste = genera_pratt(400.0, 30.0, 4, sezione_base, sezione_base, sm)
        # Aste 8..12 (posizioni 8-12 = 5 montanti) hanno area = sm.A
        montanti = aste[8:13]
        assert len(montanti) == 5
        for a in montanti:
            assert abs(a.A - sm.A) < 1e-6

    def test_pratt_diagonali_diverse_da_howe(self, sezione_base):
        _, aste_h = genera_howe(400.0, 30.0, 4, sezione_base, sezione_base)
        _, aste_p = genera_pratt(400.0, 30.0, 4, sezione_base, sezione_base)
        # Le diagonali (ultime 4 barre) collegano nodi diversi
        diag_h = sorted((a.nodo_i, a.nodo_j) for a in aste_h[-4:])
        diag_p = sorted((a.nodo_i, a.nodo_j) for a in aste_p[-4:])
        assert diag_h != diag_p


# ───────────────────────────────────────────────
#  Vincoli cordolo
# ───────────────────────────────────────────────

class TestVincoli:
    def test_vincoli_cerniera(self, sezione_base):
        nodi, _ = genera_howe(400.0, 30.0, 4, sezione_base, sezione_base)
        nodi = applica_vincoli_cordolo(nodi, n_campate=4, tipo_estremi="cerniera")
        m = {n.id: n for n in nodi}
        assert m[0].vincolo == TipoVincolo.CERNIERA    # inf, x=0
        assert m[5].vincolo == TipoVincolo.CERNIERA    # sup, x=0
        assert m[4].vincolo == TipoVincolo.CARRELLO_X  # inf, x=L
        assert m[9].vincolo == TipoVincolo.CARRELLO_X  # sup, x=L

    def test_vincoli_incastro(self, sezione_base):
        nodi, _ = genera_howe(400.0, 30.0, 4, sezione_base, sezione_base)
        nodi = applica_vincoli_cordolo(nodi, n_campate=4, tipo_estremi="incastro")
        m = {n.id: n for n in nodi}
        assert m[0].vincolo == TipoVincolo.CERNIERA   # inf, x=0
        assert m[5].vincolo == TipoVincolo.CERNIERA   # sup, x=0
        assert m[4].vincolo == TipoVincolo.CERNIERA   # inf, x=L (incastro)
        assert m[9].vincolo == TipoVincolo.CERNIERA   # sup, x=L (incastro)

    def test_vincoli_semi_incastro_come_cerniera(self, sezione_base):
        nodi, _ = genera_howe(400.0, 30.0, 4, sezione_base, sezione_base)
        nodi_c = applica_vincoli_cordolo(nodi, 4, tipo_estremi="cerniera")
        nodi_s = applica_vincoli_cordolo(nodi, 4, tipo_estremi="semi_incastro")
        # Semi-incastro usa CARRELLO_X (molla parziale riservata a futura estensione)
        assert nodi_c[4].vincolo == nodi_s[4].vincolo
        assert nodi_c[9].vincolo == nodi_s[9].vincolo


# ───────────────────────────────────────────────
#  n_campate_default
# ───────────────────────────────────────────────

class TestNCampateDefault:
    def test_sempre_pari(self):
        assert n_campate_default(400.0, 30.0) % 2 == 0
        assert n_campate_default(600.0, 25.0) % 2 == 0

    def test_minimo_2(self):
        assert n_campate_default(50.0, 100.0) >= 2

    def test_valore_atteso_L400_h30(self):
        # n_raw = 400/60 ≈ 6.67 → round=7 → pari=8
        assert n_campate_default(400.0, 30.0) == 8


# ───────────────────────────────────────────────
#  valida_geometria
# ───────────────────────────────────────────────

class TestValidaGeometria:
    def test_angolo_piatto_warning(self, sezione_base):
        # h/a = 30/100 = 0.3 → angolo diagonale 16.7° < 20° → warning
        nodi, aste = genera_howe(400.0, 30.0, 4, sezione_base, sezione_base)
        avvisi = valida_geometria(nodi, aste)
        assert any("piatta" in a.lower() for a in avvisi)

    def test_angolo_ok(self, sezione_base):
        # h=100: angolo = atan(100/100) = 45° → nessun warning diagonale piatta
        nodi, aste = genera_howe(400.0, 100.0, 4, sezione_base, sezione_base)
        avvisi = valida_geometria(nodi, aste)
        assert not any("piatta" in a.lower() for a in avvisi)


# ───────────────────────────────────────────────
#  predimensiona_sezione
# ───────────────────────────────────────────────

class TestPredimensiona:
    def test_trazione_trova_profilo(self):
        sez = predimensiona_sezione(2000.0, 100.0, tipo_acciaio="Fe430")
        assert sez is not None

    def test_compressione_trova_profilo(self):
        sez = predimensiona_sezione(-2000.0, 50.0, tipo_acciaio="Fe430")
        assert sez is not None

    def test_forza_zero(self):
        sez = predimensiona_sezione(0.0, 100.0)
        assert sez is not None
