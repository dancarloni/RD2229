"""Test sagomario profili acciaio (EN 10365).

Verifica caricamento, ricerca e proprietà profili IPE, HEA, HEB, HEM, UPN.
"""

import math
from pathlib import Path

import pytest

from src.steel.sagomario import (
    FamigliaProfilo,
    ProfiloAcciaio,
    SagomarioAcciaio,
)

DATA_DIR = Path(__file__).parent.parent / "data" / "steel"


# ───────────────────────── Fixture ─────────────────────────

@pytest.fixture
def sagomario():
    """Sagomario con tutti i profili caricati."""
    s = SagomarioAcciaio()
    n = s.carica_tutti(DATA_DIR)
    assert n > 0, "Nessun profilo caricato"
    return s


# ───────────────────────── Caricamento ─────────────────────────

class TestCaricamento:
    def test_carica_tutti(self, sagomario):
        assert sagomario.count() == 87

    def test_carica_da_singolo_json(self):
        s = SagomarioAcciaio()
        n = s.carica_da_json(DATA_DIR / "sagomario_ipe.json")
        assert n == 18

    def test_carica_directory_inesistente(self):
        s = SagomarioAcciaio()
        n = s.carica_tutti(Path("/nonexistent"))
        assert n == 0

    def test_famiglie_disponibili(self, sagomario):
        famiglie = sagomario.list_famiglie()
        assert set(famiglie) == {"HEA", "HEB", "HEM", "IPE", "UPN"}

    @pytest.mark.parametrize("famiglia,count", [
        ("IPE", 18),
        ("HEA", 19),
        ("HEB", 19),
        ("HEM", 19),
        ("UPN", 12),
    ])
    def test_count_per_famiglia(self, sagomario, famiglia, count):
        profili = sagomario.list_by_famiglia(famiglia)
        assert len(profili) == count


# ───────────────────────── Ricerca ─────────────────────────

class TestRicerca:
    def test_get_profilo_esistente(self, sagomario):
        p = sagomario.get("IPE 200")
        assert p is not None
        assert p.nome == "IPE 200"
        assert p.famiglia == "IPE"

    def test_get_profilo_inesistente(self, sagomario):
        assert sagomario.get("IPE 999") is None

    def test_list_nomi_tutti(self, sagomario):
        nomi = sagomario.list_nomi()
        assert len(nomi) == 87

    def test_list_nomi_per_famiglia(self, sagomario):
        nomi = sagomario.list_nomi("IPE")
        assert all("IPE" in n for n in nomi)
        assert len(nomi) == 18

    def test_cerca_per_Wx_minimo(self, sagomario):
        risultati = sagomario.cerca_per_Wx_minimo(500.0, "IPE")
        assert len(risultati) > 0
        assert all(p.Wx >= 500.0 for p in risultati)
        # ordinati per Wx crescente
        for i in range(len(risultati) - 1):
            assert risultati[i].Wx <= risultati[i + 1].Wx

    def test_cerca_per_altezza(self, sagomario):
        risultati = sagomario.cerca_per_altezza(20.0, 30.0, "IPE")
        assert len(risultati) > 0
        assert all(20.0 <= p.h <= 30.0 for p in risultati)

    def test_profilo_ottimale(self, sagomario):
        p = sagomario.profilo_ottimale(500.0, "IPE")
        assert p is not None
        assert p.Wx >= 500.0
        # è il più leggero tra quelli con Wx >= 500
        candidati = sagomario.cerca_per_Wx_minimo(500.0, "IPE")
        assert p.massa_kg_m == min(c.massa_kg_m for c in candidati)

    def test_profilo_ottimale_impossibile(self, sagomario):
        p = sagomario.profilo_ottimale(999999.0, "IPE")
        assert p is None

    def test_tutti_ordinati(self, sagomario):
        tutti = sagomario.tutti()
        assert len(tutti) == 87
        # ordinati per famiglia poi altezza
        for i in range(len(tutti) - 1):
            if tutti[i].famiglia == tutti[i + 1].famiglia:
                assert tutti[i].h <= tutti[i + 1].h


# ───────────────────────── Proprietà profili noti ─────────────────────────

class TestProprietaProfili:
    """Verifica valori noti di profili standard EN 10365."""

    def test_ipe_200_dimensioni(self, sagomario):
        p = sagomario.get("IPE 200")
        assert p.h == 20.0
        assert p.b == 10.0
        assert p.tw == 0.56
        assert p.tf == 0.85
        assert p.A == pytest.approx(28.5, abs=0.5)
        assert p.massa_kg_m == pytest.approx(22.4, abs=0.5)

    def test_ipe_200_inerzia(self, sagomario):
        p = sagomario.get("IPE 200")
        assert p.Ix == pytest.approx(1943, rel=0.02)
        assert p.Wx == pytest.approx(194, rel=0.02)
        assert p.ix == pytest.approx(8.26, rel=0.02)
        assert p.Iy == pytest.approx(142, rel=0.02)

    def test_ipe_300_dimensioni(self, sagomario):
        p = sagomario.get("IPE 300")
        assert p.h == 30.0
        assert p.b == 15.0
        assert p.tw == 0.71
        assert p.tf == 1.07
        assert p.Wx == pytest.approx(557, rel=0.02)

    def test_hea_200_dimensioni(self, sagomario):
        p = sagomario.get("HEA 200")
        assert p.h == 19.0
        assert p.b == 20.0
        assert p.tw == 0.65
        assert p.tf == 1.00

    def test_hea_200_inerzia(self, sagomario):
        p = sagomario.get("HEA 200")
        assert p.Ix == pytest.approx(3692, rel=0.02)
        assert p.Wx == pytest.approx(389, rel=0.02)
        assert p.Iy == pytest.approx(1336, rel=0.02)

    def test_ipe_coerenza_hi(self, sagomario):
        """hi = h - 2·tf per tutti i profili IPE."""
        for p in sagomario.list_by_famiglia("IPE"):
            hi_calc = p.h - 2 * p.tf
            assert p.hi == pytest.approx(hi_calc, abs=0.01), \
                f"{p.nome}: hi={p.hi} != h-2tf={hi_calc}"

    def test_ipe_coerenza_d(self, sagomario):
        """d = h - 2·tf - 2·r per tutti i profili IPE."""
        for p in sagomario.list_by_famiglia("IPE"):
            d_calc = p.h - 2 * p.tf - 2 * p.r
            assert p.d == pytest.approx(d_calc, abs=0.01), \
                f"{p.nome}: d={p.d} != h-2tf-2r={d_calc}"

    def test_wx_coerente_ix(self, sagomario):
        """Wx ≈ 2·Ix/h per profili simmetrici (tolleranza 5%)."""
        for p in sagomario.tutti():
            if p.h > 0:
                Wx_calc = 2 * p.Ix / p.h
                assert p.Wx == pytest.approx(Wx_calc, rel=0.05), \
                    f"{p.nome}: Wx={p.Wx} vs 2Ix/h={Wx_calc}"


# ───────────────────────── ProfiloAcciaio ─────────────────────────

class TestProfiloAcciaio:
    def test_from_dict_to_dict_roundtrip(self):
        data = {
            "nome": "TEST 100",
            "famiglia": "TEST",
            "h": 10.0, "b": 5.0, "tw": 0.5, "tf": 0.8, "r": 0.7,
            "A": 15.0, "massa_kg_m": 11.8,
            "Ix": 200.0, "Wx": 40.0, "Wpl_x": 46.0, "ix": 3.65,
            "Iy": 18.0, "Wy": 7.2, "Wpl_y": 11.0, "iy": 1.1,
        }
        p = ProfiloAcciaio.from_dict(data)
        assert p.nome == "TEST 100"
        d = p.to_dict()
        assert d["nome"] == "TEST 100"
        assert d["h"] == 10.0

    def test_from_dict_ignora_campi_extra(self):
        data = {
            "nome": "X", "famiglia": "X",
            "h": 1, "b": 1, "tw": 0.1, "tf": 0.1, "r": 0.1,
            "A": 1, "massa_kg_m": 1,
            "Ix": 1, "Wx": 1, "Wpl_x": 1, "ix": 1,
            "Iy": 1, "Wy": 1, "Wpl_y": 1, "iy": 1,
            "campo_sconosciuto": 999,
        }
        p = ProfiloAcciaio.from_dict(data)
        assert p.nome == "X"

    def test_rapporto_hw_tw(self):
        p = ProfiloAcciaio(
            nome="T", famiglia="T",
            h=20.0, b=10.0, tw=0.56, tf=0.85, r=1.2,
            A=28.5, massa_kg_m=22.4,
            Ix=1943, Wx=194, Wpl_x=221, ix=8.26,
            Iy=142, Wy=28.5, Wpl_y=44.6, iy=2.24,
        )
        # hw = 20 - 2*0.85 = 18.3
        assert p.rapporto_hw_tw == pytest.approx(18.3 / 0.56, rel=0.01)

    def test_rapporto_cf_tf(self):
        p = ProfiloAcciaio(
            nome="T", famiglia="T",
            h=20.0, b=10.0, tw=0.56, tf=0.85, r=1.2,
            A=28.5, massa_kg_m=22.4,
            Ix=1943, Wx=194, Wpl_x=221, ix=8.26,
            Iy=142, Wy=28.5, Wpl_y=44.6, iy=2.24,
        )
        # c = (10 - 0.56)/2 - 1.2 = 4.72 - 1.2 = 3.52
        assert p.rapporto_cf_tf == pytest.approx(3.52 / 0.85, rel=0.01)


# ───────────────────────── FamigliaProfilo Enum ─────────────────────────

class TestFamigliaProfilo:
    def test_valori(self):
        assert FamigliaProfilo.IPE.value == "IPE"
        assert FamigliaProfilo.HEA.value == "HEA"
        assert FamigliaProfilo.HEB.value == "HEB"
        assert FamigliaProfilo.HEM.value == "HEM"
        assert FamigliaProfilo.UPN.value == "UPN"


# ───────────────────────── Esportazione ─────────────────────────

class TestEsportazione:
    def test_esporta_reimporta(self, sagomario, tmp_path):
        out = tmp_path / "export.json"
        sagomario.esporta_json(out)

        s2 = SagomarioAcciaio()
        n = s2.carica_da_json(out)
        assert n == sagomario.count()
