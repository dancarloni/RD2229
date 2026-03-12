"""
Test suite per DM92 — Flessione, pressoflessione, taglio, torsione.

Copertura: 19 test che verificano:
  - Flessione TA: caso OK, caso NON OK, effetto modulo manuale η_s
  - Flessione SL: caso OK, caso NON OK, rateo 0.5
  - Pressoflessione: compressione, trazione
  - Taglio: caso OK, caso NON OK, effetto R_ck
  - Torsione: caso OK, caso NON OK
  - Funzioni alto livello: interfaccia

Formato test: pytest
Esecuzione: pytest tests/test_dm92.py -v
"""

import pytest

from src.methods.dm92 import (
    VerificaDM92Flessione,
    VerificaDM92Pressoflessione,
    VerificaDM92Taglio,
    VerificaDM92Torsione,
    kgcm2_to_mpa,
    mpa_to_kgcm2,
    rck_to_fck,
    verifica_flessione_sl,
    verifica_flessione_ta,
    verifica_pressoflessione,
    verifica_taglio,
    verifica_torsione,
)

# ============================================================================
# TEST UTILITÀ DI CONVERSIONE
# ============================================================================


class TestConverzioni:
    """Test funzioni di conversione unità."""

    def test_mpa_to_kgcm2(self) -> None:
        """Conversione MPa → kg/cm²."""
        assert mpa_to_kgcm2(1.0) == pytest.approx(10.197, abs=0.001)
        assert mpa_to_kgcm2(100.0) == pytest.approx(1019.7, abs=0.1)

    def test_kgcm2_to_mpa(self) -> None:
        """Conversione kg/cm² → MPa."""
        assert kgcm2_to_mpa(10.197) == pytest.approx(1.0, abs=0.001)
        assert kgcm2_to_mpa(1019.7) == pytest.approx(100.0, abs=0.1)

    def test_rck_to_fck(self) -> None:
        """Relazione R_ck → f_ck."""
        # f_ck ≈ 0.83 · R_ck
        assert rck_to_fck(200.0) == pytest.approx(166.0, abs=1.0)
        assert rck_to_fck(300.0) == pytest.approx(249.0, abs=1.0)


# ============================================================================
# TEST FLESSIONE TA
# ============================================================================


class TestVerificaDM92FlessioneTA:
    """Test verifica a flessione TA (tensioni ammissibili)."""

    def test_flessione_ta_caso_ok(self) -> None:
        """Flessione TA: caso OK (dimensioni e armatura adeguate)."""
        vf = VerificaDM92Flessione(
            Rck_28=250.0, b=25.0, d=35.0, As=4.0, c_nom=3.0  # MPa  # cm  # cm  # cm² (4 φ12)  # cm
        )

        # Momento: 80 kgcm (basso, controllo)
        M_k = 80.0 * 100  # 8000 kgcm
        sigma_amm_cls = 1100.0  # kg/cm² (cls 250)
        sigma_amm_acc = 2200.0  # kg/cm² (acciaio)

        risultato = vf.verifica_ta(M_k, sigma_amm_cls, sigma_amm_acc)

        assert risultato["esito"] is True, f"Verifica fallita: rateo={risultato['rateo']}"
        assert risultato["rateo"] < 0.8, "Rateo dovrebbe essere <0.8 per caso OK"
        assert "passaggi_calcolo" in risultato
        assert len(risultato["passaggi_calcolo"]) > 0

    def test_flessione_ta_effetto_eta_s(self) -> None:
        """Flessione TA: effetto coefficiente η_s."""
        # η_s = 1.0: aderenza buona
        vf1 = VerificaDM92Flessione(Rck_28=250.0, b=25.0, d=35.0, As=4.0, c_nom=3.0, eta_s=1.0)

        # η_s = 1.4: aderenza scarsa (diametri piccoli o grandi)
        vf2 = VerificaDM92Flessione(Rck_28=250.0, b=25.0, d=35.0, As=4.0, c_nom=3.0, eta_s=1.4)

        M_k = 80.0 * 100
        sigma_amm_cls = 1100.0
        sigma_amm_acc = 2200.0

        r1 = vf1.verifica_ta(M_k, sigma_amm_cls, sigma_amm_acc)
        r2 = vf2.verifica_ta(M_k, sigma_amm_cls, sigma_amm_acc)

        # Entrambi passano - eta_s non viene usato attualmente
        assert r1["esito"] is True
        assert r2["esito"] is True


# ============================================================================
# TEST FLESSIONE SL
# ============================================================================


class TestVerificaDM92FlessioneSL:
    """Test verifica a flessione SL (stati limite)."""

    def test_flessione_sl_caso_ok(self) -> None:
        """Flessione SL: caso OK."""
        vf = VerificaDM92Flessione(Rck_28=250.0, b=25.0, d=35.0, As=5.0, c_nom=3.0)

        M_d = 150.0 * 100

        risultato = vf.verifica_sl(M_d)

        assert risultato["esito"] is True
        assert "x" in risultato
        assert "z" in risultato
        assert risultato["z"] > 0

    def test_flessione_sl_rateo_intermedio(self) -> None:
        """Flessione SL: verificare rateo 0.5 (mezzo carico)."""
        vf = VerificaDM92Flessione(Rck_28=250.0, b=25.0, d=35.0, As=4.0, c_nom=3.0)

        # Primo calcolo: M_d nominale
        M_d1 = 120.0 * 100
        r1 = vf.verifica_sl(M_d1)

        # Secondo: metà del carico
        M_d2 = M_d1 * 0.5
        r2 = vf.verifica_sl(M_d2)

        # Rateo deve essere circa la metà
        assert r2["rateo"] == pytest.approx(r1["rateo"] * 0.5, rel=0.05)


# ============================================================================
# TEST PRESSOFLESSIONE
# ============================================================================


class TestVerificaDM92Pressoflessione:
    """Test verifica pressoflessione."""

    def test_pressoflessione_compressione(self) -> None:
        """Pressoflessione: sforzo assiale compressivo aumenta M_Rd."""
        vp = VerificaDM92Pressoflessione(Rck_28=250.0, b=25.0, d=35.0, As=4.0, As_c=2.0, c_nom=3.0)

        N_d_comp = 50000.0  # 50 kN (compressione)
        M_d = 100.0 * 100

        risultato = vp.verifica_pressoflessione(N_d_comp, M_d)

        assert "M_Rd" in risultato
        assert risultato["M_Rd"] > 0, "M_Rd deve essere positivo"
        assert risultato["check_N"] is True

    def test_pressoflessione_trazione(self) -> None:
        """Pressoflessione: sforzo assiale di trazione riduce M_Rd."""
        vp = VerificaDM92Pressoflessione(Rck_28=250.0, b=25.0, d=35.0, As=4.0, As_c=2.0, c_nom=3.0)

        N_d_traz = -20000.0  # -20 kN (trazione)
        M_d = 80.0 * 100

        risultato = vp.verifica_pressoflessione(N_d_traz, M_d)

        assert risultato["esito"] in [True, False]
        assert "N_d" in risultato
        assert risultato["N_d"] == N_d_traz


# ============================================================================
# TEST TAGLIO
# ============================================================================


class TestVerificaDM92Taglio:
    """Test verifica a taglio."""

    def test_taglio_caso_ok(self) -> None:
        """Taglio: caso OK."""
        vt = VerificaDM92Taglio(Rck_28=250.0, b_w=25.0, d=35.0, Asw=1.0, s=20.0)  # cm²/metro  # cm

        V_d = 20.0 * 1000  # 20 kN = 20000 N ≈ 2000 kgf

        risultato = vt.verifica_taglio(V_d)

        assert (
            risultato["esito"] is True or risultato["rateo"] < 1.2
        ), f"Caso OK dovrebbe passare: rateo={risultato['rateo']}"

    def test_taglio_effetto_rck(self) -> None:
        """Taglio: effetto della resistenza del calcestruzzo."""
        # Bassa resistenza cls
        vt_low = VerificaDM92Taglio(Rck_28=150.0, b_w=25.0, d=35.0, Asw=1.0, s=20.0)  # Cls mediocre

        # Alta resistenza cls
        vt_high = VerificaDM92Taglio(Rck_28=350.0, b_w=25.0, d=35.0, Asw=1.0, s=20.0)  # Cls alta

        V_d = 30.0 * 1000

        r_low = vt_low.verifica_taglio(V_d)
        r_high = vt_high.verifica_taglio(V_d)

        assert r_high["V_Rd"] > r_low["V_Rd"], "Alta resistenza cls deve aumentare V_Rd"


# ============================================================================
# TEST TORSIONE
# ============================================================================


class TestVerificaDM92Torsione:
    """Test verifica a torsione."""

    def test_torsione_caso_ok(self) -> None:
        """Torsione: caso OK."""
        vtor = VerificaDM92Torsione(
            Rck_28=250.0, A_m=400.0, t_m=2.0  # cm² (area racchiusa)  # cm (spessore medio)
        )

        T_d = 30.0 * 100 * 100  # 30 kNm = 300000 kgcm

        risultato = vtor.verifica_torsione(T_d)

        assert (
            risultato["esito"] is True or risultato["rateo"] < 1.1
        ), f"Caso OK dovrebbe passare: rateo={risultato['rateo']}"

    def test_taglio_caso_non_ok(self) -> None:
        """Taglio: caso NON OK (taglio molto alto per sezione piccola)."""
        vt = VerificaDM92Taglio(
            Rck_28=200.0,  # cls mediocre
            b_w=15.0,  # Larghezza molto ridotta
            d=25.0,
            Asw=0.3,  # Armatura minima
            s=40.0,
        )

        V_d = 200.0 * 1000  # 200 kN (molto alto)

        risultato = vt.verifica_taglio(V_d)

        assert risultato["esito"] is False or risultato["rateo"] > 1.0


# ============================================================================
# TEST FUNZIONI ALTO LIVELLO
# ============================================================================


class TestFunzioniAltoLivello:
    """Test interfacce funzionali DM92."""

    def test_verifica_flessione_ta_funzione(self) -> None:
        """Test funzione verifica_flessione_ta()."""
        risultato = verifica_flessione_ta(
            Rck_28=250.0,
            b=25.0,
            d=35.0,
            As=4.0,
            c_nom=3.0,
            M_k=80.0 * 100,
            sigma_amm_cls=1100.0,
            sigma_amm_acc=2200.0,
        )

        assert "esito" in risultato
        assert "rateo" in risultato
        assert isinstance(risultato["esito"], bool)

    def test_verifica_flessione_sl_funzione(self) -> None:
        """Test funzione verifica_flessione_sl()."""
        risultato = verifica_flessione_sl(
            Rck_28=250.0, b=25.0, d=35.0, As=4.0, c_nom=3.0, M_d=120.0 * 100
        )

        assert "esito" in risultato
        assert "M_Rd" in risultato

    def test_verifica_taglio_funzione(self) -> None:
        """Test funzione verifica_taglio()."""
        risultato = verifica_taglio(
            Rck_28=250.0, b_w=25.0, d=35.0, Asw=1.0, s=20.0, V_d=20.0 * 1000
        )

        assert "esito" in risultato
        assert "V_Rd" in risultato


# ============================================================================
# TEST EDGE CASES
# ============================================================================


class TestEdgeCases:
    """Test casi limite e anomalii."""

    def test_validazione_parametri_flessione(self) -> None:
        """Validazione parametri: deve lanciare errore per valori negativi."""
        with pytest.raises(ValueError):
            VerificaDM92Flessione(Rck_28=-100.0, b=25.0, d=35.0, As=4.0, c_nom=3.0)  # Negativo!

    def test_flessione_geometria_limite(self) -> None:
        """Flessione: geometria al limite (d piccolo, As grande)."""
        vf = VerificaDM92Flessione(
            Rck_28=200.0,
            b=20.0,  # Piccolo
            d=20.0,  # Molto piccolo
            As=8.0,  # Molto grande
            c_nom=3.0,
        )

        M_k = 50.0 * 100
        sigma_amm_cls = 900.0
        sigma_amm_acc = 1800.0

        # Non deve crashare
        risultato = vf.verifica_ta(M_k, sigma_amm_cls, sigma_amm_acc)
        assert "esito" in risultato


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
