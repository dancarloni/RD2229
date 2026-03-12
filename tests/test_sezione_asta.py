"""Test per SezioneAsta — piatti, angolari e profili standard.

Unità: cm geometria, cm² aree, cm⁴ inerzie, kg/m massa.
"""

from __future__ import annotations

import math

import pytest

from src.steel.sezione_asta import (
    SezioneAsta,
    TipoSezioneAsta,
    carica_catalogo_angolari,
    carica_catalogo_piatti,
)
from src.steel.verifiche_ta import verifica_asta_ta

SQRT12 = math.sqrt(12)


# ───────────────────────────────────────────────
#  Piatto da_piatto()
# ───────────────────────────────────────────────


class TestPiatto:
    def test_piatto_80x8_area(self):
        p = SezioneAsta.da_piatto(b=8.0, t=0.8)
        assert abs(p.A - 6.4) < 1e-6

    def test_piatto_80x8_ix(self):
        p = SezioneAsta.da_piatto(b=8.0, t=0.8)
        assert abs(p.ix - 8.0 / SQRT12) < 1e-4  # ≈ 2.309 cm

    def test_piatto_80x8_iy(self):
        p = SezioneAsta.da_piatto(b=8.0, t=0.8)
        assert abs(p.iy - 0.8 / SQRT12) < 1e-4  # ≈ 0.231 cm

    def test_piatto_80x8_Ix(self):
        # Ix = t * b^3 / 12
        p = SezioneAsta.da_piatto(b=8.0, t=0.8)
        assert abs(p.Ix - 0.8 * 512 / 12) < 1e-3  # ≈ 34.133 cm⁴

    def test_piatto_80x8_Iy(self):
        # Iy = b * t^3 / 12
        p = SezioneAsta.da_piatto(b=8.0, t=0.8)
        assert abs(p.Iy - 8.0 * 0.512 / 12) < 1e-4  # ≈ 0.341 cm⁴

    def test_piatto_80x8_massa(self):
        p = SezioneAsta.da_piatto(b=8.0, t=0.8)
        # massa = A * 0.785 kg/m
        assert abs(p.massa_kg_m - 6.4 * 0.785) < 0.01

    def test_piatto_80x8_nome(self):
        p = SezioneAsta.da_piatto(b=8.0, t=0.8)
        assert p.nome == "Piatto 80x8"

    def test_piatto_tipo(self):
        p = SezioneAsta.da_piatto(b=5.0, t=0.5)
        assert p.tipo == TipoSezioneAsta.PIATTO

    def test_piatto_ix_maggiore_iy(self):
        # ix sempre > iy (b >= t)
        p = SezioneAsta.da_piatto(b=10.0, t=1.0)
        assert p.ix > p.iy

    def test_piatto_t_uguale_b_errore(self):
        with pytest.raises(ValueError):
            SezioneAsta.da_piatto(b=5.0, t=6.0)  # t > b → errore

    def test_piatto_50x5(self):
        p = SezioneAsta.da_piatto(b=5.0, t=0.5)
        assert abs(p.A - 2.5) < 1e-6
        assert abs(p.ix - 5.0 / SQRT12) < 1e-4
        assert abs(p.iy - 0.5 / SQRT12) < 1e-4


# ───────────────────────────────────────────────
#  Angolare da_angolare_pari()
# ───────────────────────────────────────────────


class TestAngolare:
    def test_angolare_L80x80x8_area(self):
        a = SezioneAsta.da_angolare_pari(b=8.0, t=0.8)
        # A = (2*8 - 0.8) * 0.8 = 12.16 cm²
        assert abs(a.A - 12.16) < 1e-4

    def test_angolare_L80x80x8_iy_approx_formula(self):
        a = SezioneAsta.da_angolare_pari(b=8.0, t=0.8)
        # i_v ≈ 0.195 * b (approssimazione EN 10056)
        assert abs(a.iy - 0.195 * 8.0) < 0.05  # tolleranza 5%

    def test_angolare_ix_maggiore_iy(self):
        a = SezioneAsta.da_angolare_pari(b=6.0, t=0.6)
        assert a.ix > a.iy

    def test_angolare_nome(self):
        a = SezioneAsta.da_angolare_pari(b=8.0, t=0.8)
        assert a.nome == "L80x80x8"

    def test_angolare_tipo(self):
        a = SezioneAsta.da_angolare_pari(b=5.0, t=0.5)
        assert a.tipo == TipoSezioneAsta.ANGOLARE

    def test_angolare_L80x80x8_Ix_maggiore_Iy(self):
        a = SezioneAsta.da_angolare_pari(b=8.0, t=0.8)
        assert a.Ix > a.Iy

    def test_angolare_simmetria_ix_iy_da_inerzie(self):
        # ix = sqrt(Ix/A), iy = sqrt(Iy/A)
        a = SezioneAsta.da_angolare_pari(b=10.0, t=1.0)
        assert abs(a.ix - math.sqrt(a.Ix / a.A)) < 1e-6
        assert abs(a.iy - math.sqrt(a.Iy / a.A)) < 1e-6

    def test_angolare_t_uguale_b_errore(self):
        with pytest.raises(ValueError):
            SezioneAsta.da_angolare_pari(b=5.0, t=5.0)

    def test_angolare_L50x50x5_iy(self):
        a = SezioneAsta.da_angolare_pari(b=5.0, t=0.5)
        # i_v ≈ 0.195 * 5 = 0.975 cm
        assert abs(a.iy - 0.195 * 5.0) < 0.05

    def test_angolare_massa(self):
        a = SezioneAsta.da_angolare_pari(b=8.0, t=0.8)
        assert abs(a.massa_kg_m - a.A * 0.785) < 0.05


# ───────────────────────────────────────────────
#  da_profilo()
# ───────────────────────────────────────────────


class TestDaProfilo:
    def test_da_profilo_ipe200(self):
        from src.steel.sagomario import SagomarioAcciaio

        sag = SagomarioAcciaio()
        sag.carica_tutti()
        profilo = sag.get("IPE 200")
        if profilo is None:
            pytest.skip("IPE 200 non trovato nel sagomario")
        s = SezioneAsta.da_profilo(profilo)
        assert s.tipo == TipoSezioneAsta.PROFILO_STANDARD
        assert abs(s.A - profilo.A) < 1e-6
        assert abs(s.ix - profilo.ix) < 1e-6
        assert abs(s.iy - profilo.iy) < 1e-6
        assert s.nome == "IPE 200"

    def test_da_profilo_mantiene_massa(self):
        from src.steel.sagomario import SagomarioAcciaio

        sag = SagomarioAcciaio()
        sag.carica_tutti()
        profilo = sag.get("IPE 200")
        if profilo is None:
            pytest.skip("IPE 200 non trovato nel sagomario")
        s = SezioneAsta.da_profilo(profilo)
        assert abs(s.massa_kg_m - profilo.massa_kg_m) < 1e-6


# ───────────────────────────────────────────────
#  from_dict / to_dict
# ───────────────────────────────────────────────


class TestSerialization:
    def test_round_trip_piatto(self):
        p = SezioneAsta.da_piatto(b=8.0, t=0.8)
        d = p.to_dict()
        p2 = SezioneAsta.from_dict(d)
        assert abs(p2.A - p.A) < 1e-6
        assert abs(p2.ix - p.ix) < 1e-6
        assert p2.tipo == TipoSezioneAsta.PIATTO

    def test_round_trip_angolare(self):
        a = SezioneAsta.da_angolare_pari(b=6.0, t=0.6)
        d = a.to_dict()
        a2 = SezioneAsta.from_dict(d)
        assert abs(a2.iy - a.iy) < 1e-6
        assert a2.tipo == TipoSezioneAsta.ANGOLARE


# ───────────────────────────────────────────────
#  Catalogo piatti.json
# ───────────────────────────────────────────────


class TestCatalogoPiatti:
    def test_catalogo_caricato(self):
        cat = carica_catalogo_piatti()
        assert cat.count() > 0

    def test_catalogo_contiene_80x8(self):
        cat = carica_catalogo_piatti()
        s = cat.get("Piatto 80x8")
        assert s is not None
        assert abs(s.A - 6.4) < 1e-3

    def test_catalogo_ordinato_per_A(self):
        cat = carica_catalogo_piatti()
        areas = [s.A for s in cat.tutti()]
        assert areas == sorted(areas)

    def test_catalogo_cerca_A_minimo(self):
        cat = carica_catalogo_piatti()
        risultati = cat.cerca_A_minimo(6.0)
        assert all(s.A >= 6.0 for s in risultati)


# ───────────────────────────────────────────────
#  Catalogo angolari.json
# ───────────────────────────────────────────────


class TestCatalogoAngolari:
    def test_catalogo_angolari_caricato(self):
        cat = carica_catalogo_angolari()
        assert cat.count() > 0

    def test_catalogo_contiene_L80(self):
        cat = carica_catalogo_angolari()
        s = cat.get("L80x80x8")
        assert s is not None

    def test_catalogo_angolari_ordinato_per_A(self):
        cat = carica_catalogo_angolari()
        areas = [s.A for s in cat.tutti()]
        assert areas == sorted(areas)


# ───────────────────────────────────────────────
#  verifica_asta_ta()
# ───────────────────────────────────────────────


class TestVerificaAstaTa:
    def test_trazione_verificata(self):
        p = SezioneAsta.da_piatto(b=8.0, t=0.8)
        # N=3000 kg trazione → σ = 3000/6.4 = 468.75 kg/cm² << 1900
        r = verifica_asta_ta(p, N=3000.0, L=100.0, tipo_acciaio="Fe430")
        assert r["tipo"] == "trazione"
        assert r["verificato"] is True
        assert abs(r["sigma"] - 3000.0 / 6.4) < 0.1

    def test_trazione_non_verificata(self):
        p = SezioneAsta.da_piatto(b=3.0, t=0.3)
        # A = 0.9 cm², σ = 20000/0.9 = 22222 kg/cm² >> 1900
        r = verifica_asta_ta(p, N=20000.0, L=50.0, tipo_acciaio="Fe430")
        assert r["verificato"] is False

    def test_compressione_lambda_fuori_piano_governa(self):
        p = SezioneAsta.da_piatto(b=8.0, t=0.8)
        # iy = 0.8/√12 = 0.231 cm (governa)
        # ix = 8/√12 = 2.309 cm
        r = verifica_asta_ta(p, N=-3000.0, L=100.0, tipo_acciaio="Fe430")
        assert r["tipo"] == "compressione"
        # λ_fp = 100 / 0.231 ≈ 433 > λ_ip = 100 / 2.309 ≈ 43
        assert r["lambda_fp"] > r["lambda_ip"]
        assert abs(r["lambda_fp"] - 100.0 / (0.8 / SQRT12)) < 1.0

    def test_compressione_snellezza_elevata(self):
        # Piatto sottile: grande snellezza fuori piano → omega grande
        p = SezioneAsta.da_piatto(b=10.0, t=0.8)
        r = verifica_asta_ta(p, N=-5000.0, L=200.0, tipo_acciaio="Fe430")
        assert r["tipo"] == "compressione"
        assert r["omega"] > 1.0

    def test_scarica(self):
        p = SezioneAsta.da_piatto(b=8.0, t=0.8)
        r = verifica_asta_ta(p, N=0.0, L=100.0, tipo_acciaio="Fe430")
        assert r["tipo"] == "scarica"
        assert r["verificato"] is True
        assert r["sfruttamento"] == 0.0

    def test_beta_fuoripiano_riduce_snellezza(self):
        p = SezioneAsta.da_piatto(b=8.0, t=0.8)
        r_lib = verifica_asta_ta(p, N=-2000.0, L=100.0, beta_fuoripiano=1.0)
        r_incastro = verifica_asta_ta(p, N=-2000.0, L=100.0, beta_fuoripiano=0.5)
        assert r_incastro["lambda_fp"] < r_lib["lambda_fp"]
        assert r_incastro["omega"] <= r_lib["omega"]

    def test_angolare_compressione(self):
        a = SezioneAsta.da_angolare_pari(b=6.0, t=0.6)
        r = verifica_asta_ta(a, N=-5000.0, L=150.0, tipo_acciaio="Fe430")
        assert r["tipo"] == "compressione"
        # λ_fp = 150 / i_v (asse debole dell'angolare)
        assert abs(r["lambda_fp"] - 150.0 / a.iy) < 0.5
