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


# ───────────────────────── Import CSV custom ─────────────────────────

_CSV_PROFILO_VALIDO = (
    "nome,famiglia,h,b,tw,tf,r,A,massa_kg_m,Ix,Wx,Wpl_x,ix,Iy,Wy,Wpl_y,iy,It,Iw,hi,d,AL\n"
    "IPE200_custom,CUSTOM,20.0,10.0,0.56,0.85,1.20,28.5,22.4,"
    "1943.0,194.0,221.0,8.26,142.0,28.5,44.6,2.24,6.98,13000.0,18.3,15.9,0.0\n"
)


class TestCSVImport:
    def test_genera_template_csv(self, tmp_path):
        out = tmp_path / "template.csv"
        SagomarioAcciaio.genera_template_csv(out)

        assert out.exists()
        contenuto = out.read_text(encoding="utf-8")
        # Header con tutti i campi obbligatori
        assert "nome,famiglia,h,b" in contenuto
        assert "massa_kg_m" in contenuto
        # Riga esempio presente
        assert "IPE200_custom" in contenuto
        # Righe commento
        assert contenuto.startswith("#")

    def test_carica_da_csv_valido(self, tmp_path):
        csv_path = tmp_path / "profili.csv"
        csv_path.write_text(_CSV_PROFILO_VALIDO, encoding="utf-8")

        s = SagomarioAcciaio()
        n, warnings = s.carica_da_csv(csv_path, custom_dir=tmp_path)

        assert n == 1
        assert warnings == []
        p = s.get("IPE200_custom")
        assert p is not None
        assert p.famiglia == "CUSTOM"
        assert p.h == pytest.approx(20.0)
        assert p.Wx == pytest.approx(194.0)

    def test_carica_da_csv_sovrascrittura_warning(self, tmp_path):
        # Prepara sagomario con IPE 200 originale
        s = SagomarioAcciaio()
        s.carica_tutti(DATA_DIR)
        massa_originale = s.get("IPE 200").massa_kg_m  # type: ignore[union-attr]

        # CSV con stesso nome "IPE 200" ma massa diversa
        csv_content = (
            "nome,famiglia,h,b,tw,tf,r,A,massa_kg_m,Ix,Wx,Wpl_x,ix,Iy,Wy,Wpl_y,iy\n"
            "IPE 200,CUSTOM,20.0,10.0,0.56,0.85,1.20,28.5,99.9,"
            "1943.0,194.0,221.0,8.26,142.0,28.5,44.6,2.24\n"
        )
        csv_path = tmp_path / "sovrascrittura.csv"
        csv_path.write_text(csv_content, encoding="utf-8")

        n, warnings = s.carica_da_csv(csv_path, custom_dir=tmp_path)

        assert n == 1
        assert len(warnings) == 1
        assert "sovrascrittura" in warnings[0].lower() or "già presente" in warnings[0]
        # Il profilo è stato aggiornato
        assert s.get("IPE 200").massa_kg_m == pytest.approx(99.9)  # type: ignore[union-attr]
        assert s.get("IPE 200").massa_kg_m != massa_originale  # type: ignore[union-attr]

    def test_carica_da_csv_campo_mancante(self, tmp_path):
        # CSV senza colonna "h"
        csv_content = (
            "nome,famiglia,b,tw,tf,r,A,massa_kg_m,Ix,Wx,Wpl_x,ix,Iy,Wy,Wpl_y,iy\n"
            "Profilo1,CUSTOM,10.0,0.56,0.85,1.20,28.5,22.4,"
            "1943.0,194.0,221.0,8.26,142.0,28.5,44.6,2.24\n"
        )
        csv_path = tmp_path / "mancante.csv"
        csv_path.write_text(csv_content, encoding="utf-8")

        s = SagomarioAcciaio()
        n, warnings = s.carica_da_csv(csv_path, custom_dir=tmp_path)

        assert n == 0
        assert len(warnings) == 1
        assert "h" in warnings[0]

    def test_carica_da_csv_range_fisici(self, tmp_path):
        # h = -5.0 non ammesso
        csv_content = (
            "nome,famiglia,h,b,tw,tf,r,A,massa_kg_m,Ix,Wx,Wpl_x,ix,Iy,Wy,Wpl_y,iy\n"
            "Profilo1,CUSTOM,-5.0,10.0,0.56,0.85,1.20,28.5,22.4,"
            "1943.0,194.0,221.0,8.26,142.0,28.5,44.6,2.24\n"
        )
        csv_path = tmp_path / "range.csv"
        csv_path.write_text(csv_content, encoding="utf-8")

        s = SagomarioAcciaio()
        n, warnings = s.carica_da_csv(csv_path, custom_dir=tmp_path)

        assert n == 0
        assert len(warnings) == 1
        assert "h" in warnings[0]
        assert ">" in warnings[0] or "0" in warnings[0]

    def test_persistenza_custom_json(self, tmp_path):
        csv_path = tmp_path / "profili.csv"
        csv_path.write_text(_CSV_PROFILO_VALIDO, encoding="utf-8")

        # Primo sagomario: carica e salva
        s1 = SagomarioAcciaio()
        n, _ = s1.carica_da_csv(csv_path, custom_dir=tmp_path)
        assert n == 1

        # Verifica che sagomario_custom.json esista
        custom_json = tmp_path / "sagomario_custom.json"
        assert custom_json.exists()

        # Secondo sagomario: ricarica da directory con solo il custom JSON
        s2 = SagomarioAcciaio()
        n2 = s2.carica_tutti(tmp_path)
        assert n2 >= 1
        assert s2.get("IPE200_custom") is not None
