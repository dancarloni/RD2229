"""Test per fattore_comportamento.py — Fattore q NTC2018 §7.8.1.3.

Verifica:
- Valori tabulati α_u/α_1 (Tab. 7.3.II)
- Calcolo q = q₀ × K_R
- Limiti per edifici esistenti (α_u/α_1 ≤ 1.50)
- Override manuale
- Regolarità pianta e altezza
- Passaggi di calcolo
"""

import pytest

from src.methods.muratura.fattore_comportamento import (
    ALPHA_U_ALPHA_1_TAB,
    RegolaritaAltezza,
    RegolaritaPianta,
    RisultatoFattoreQ,
    TipoEdificio,
    TipoMuraturaQ,
    calcola_fattore_comportamento,
)


# ═══════════════════════════════════════════════════════════
#  Tabella α_u/α_1
# ═══════════════════════════════════════════════════════════

class TestTabellaAlpha:
    """Test sui valori tabulati α_u/α_1."""

    def test_ordinaria_1_piano(self):
        assert ALPHA_U_ALPHA_1_TAB["ordinaria"]["1_piano"] == 1.4

    def test_ordinaria_2_piani(self):
        assert ALPHA_U_ALPHA_1_TAB["ordinaria"]["2_piani"] == 1.8

    def test_ordinaria_3_piani(self):
        assert ALPHA_U_ALPHA_1_TAB["ordinaria"]["3+_piani"] == 1.3

    def test_armata_1_piano(self):
        assert ALPHA_U_ALPHA_1_TAB["armata"]["1_piano"] == 1.3

    def test_armata_2_piani(self):
        assert ALPHA_U_ALPHA_1_TAB["armata"]["2_piani"] == 1.5

    def test_armata_3_piani(self):
        assert ALPHA_U_ALPHA_1_TAB["armata"]["3+_piani"] == 1.3


# ═══════════════════════════════════════════════════════════
#  Calcolo q — muratura ordinaria
# ═══════════════════════════════════════════════════════════

class TestQOrdinaria:
    """Test calcolo q per muratura ordinaria."""

    def test_ordinaria_2piani_regolare_esistente(self):
        """q = 1.75 × min(1.8, 1.50) × 1.0 = 1.75 × 1.50 = 2.625."""
        ris = calcola_fattore_comportamento(
            tipo_muratura=TipoMuraturaQ.ORDINARIA,
            n_piani=2,
            regolarita_altezza=RegolaritaAltezza.REGOLARE,
            tipo_edificio=TipoEdificio.ESISTENTE,
        )
        # α_u/α_1 tab = 1.8, ma limitato a 1.50 per esistente
        assert ris.alpha_u_alpha_1 == pytest.approx(1.50, abs=0.01)
        assert ris.coefficiente_base == 1.75
        assert ris.K_R == 1.0
        assert ris.q == pytest.approx(1.75 * 1.50, abs=0.01)
        assert not ris.q_override

    def test_ordinaria_1piano_regolare_esistente(self):
        """q = 1.75 × 1.4 × 1.0 = 2.45."""
        ris = calcola_fattore_comportamento(
            tipo_muratura=TipoMuraturaQ.ORDINARIA,
            n_piani=1,
            regolarita_altezza=RegolaritaAltezza.REGOLARE,
            tipo_edificio=TipoEdificio.ESISTENTE,
        )
        assert ris.alpha_u_alpha_1 == pytest.approx(1.40, abs=0.01)
        assert ris.q == pytest.approx(1.75 * 1.40, abs=0.01)

    def test_ordinaria_3piani_regolare_esistente(self):
        """q = 1.75 × 1.3 × 1.0 = 2.275."""
        ris = calcola_fattore_comportamento(
            tipo_muratura=TipoMuraturaQ.ORDINARIA,
            n_piani=3,
            regolarita_altezza=RegolaritaAltezza.REGOLARE,
            tipo_edificio=TipoEdificio.ESISTENTE,
        )
        assert ris.alpha_u_alpha_1 == pytest.approx(1.30, abs=0.01)
        assert ris.q == pytest.approx(2.275, abs=0.01)

    def test_ordinaria_2piani_regolare_nuovo(self):
        """Per edificio nuovo: α_u/α_1 = 1.8, senza limitazione a 1.50."""
        ris = calcola_fattore_comportamento(
            tipo_muratura=TipoMuraturaQ.ORDINARIA,
            n_piani=2,
            regolarita_altezza=RegolaritaAltezza.REGOLARE,
            tipo_edificio=TipoEdificio.NUOVO,
        )
        assert ris.alpha_u_alpha_1 == pytest.approx(1.80, abs=0.01)
        assert ris.q == pytest.approx(1.75 * 1.80, abs=0.01)


# ═══════════════════════════════════════════════════════════
#  Calcolo q — muratura armata
# ═══════════════════════════════════════════════════════════

class TestQArmata:
    """Test calcolo q per muratura armata."""

    def test_armata_2piani_regolare_esistente(self):
        """q = 2.0 × 1.50 × 1.0 = 3.0 (α limitato a 1.50 per esistente)."""
        ris = calcola_fattore_comportamento(
            tipo_muratura=TipoMuraturaQ.ARMATA,
            n_piani=2,
            regolarita_altezza=RegolaritaAltezza.REGOLARE,
            tipo_edificio=TipoEdificio.ESISTENTE,
        )
        assert ris.coefficiente_base == 2.0
        assert ris.alpha_u_alpha_1 == pytest.approx(1.50, abs=0.01)
        assert ris.q == pytest.approx(3.0, abs=0.01)

    def test_armata_1piano_nuovo(self):
        """q = 2.0 × 1.3 × 1.0 = 2.6."""
        ris = calcola_fattore_comportamento(
            tipo_muratura=TipoMuraturaQ.ARMATA,
            n_piani=1,
            tipo_edificio=TipoEdificio.NUOVO,
        )
        assert ris.q == pytest.approx(2.0 * 1.3, abs=0.01)


# ═══════════════════════════════════════════════════════════
#  Irregolarità
# ═══════════════════════════════════════════════════════════

class TestIrregolarita:
    """Test effetto irregolarità su q."""

    def test_irregolare_altezza_KR08(self):
        """K_R = 0.8 per irregolarità in altezza."""
        ris = calcola_fattore_comportamento(
            tipo_muratura=TipoMuraturaQ.ORDINARIA,
            n_piani=3,
            regolarita_altezza=RegolaritaAltezza.IRREGOLARE,
            tipo_edificio=TipoEdificio.ESISTENTE,
        )
        assert ris.K_R == 0.8
        # q = 1.75 × 1.3 × 0.8 = 1.82
        assert ris.q == pytest.approx(1.75 * 1.3 * 0.8, abs=0.01)

    def test_irregolare_pianta_media_alpha(self):
        """Per pianta irregolare: α = (1 + α_tab) / 2."""
        ris = calcola_fattore_comportamento(
            tipo_muratura=TipoMuraturaQ.ORDINARIA,
            n_piani=1,
            regolarita_pianta=RegolaritaPianta.IRREGOLARE,
            tipo_edificio=TipoEdificio.NUOVO,
        )
        # α_tab = 1.4, media = (1+1.4)/2 = 1.2
        assert ris.alpha_u_alpha_1 == pytest.approx(1.2, abs=0.01)
        assert ris.q == pytest.approx(1.75 * 1.2, abs=0.01)

    def test_doppia_irregolarita(self):
        """Pianta + altezza irregolari: α ridotto + K_R = 0.8."""
        ris = calcola_fattore_comportamento(
            tipo_muratura=TipoMuraturaQ.ORDINARIA,
            n_piani=2,
            regolarita_altezza=RegolaritaAltezza.IRREGOLARE,
            regolarita_pianta=RegolaritaPianta.IRREGOLARE,
            tipo_edificio=TipoEdificio.NUOVO,
        )
        # α_tab = 1.8, media pianta = (1+1.8)/2 = 1.4
        assert ris.alpha_u_alpha_1 == pytest.approx(1.4, abs=0.01)
        assert ris.K_R == 0.8
        assert ris.q == pytest.approx(1.75 * 1.4 * 0.8, abs=0.01)


# ═══════════════════════════════════════════════════════════
#  Override
# ═══════════════════════════════════════════════════════════

class TestOverride:
    """Test override manuali."""

    def test_q_override(self):
        """Override diretto di q ignora tutto il resto."""
        ris = calcola_fattore_comportamento(q_override=2.5)
        assert ris.q == pytest.approx(2.5)
        assert ris.q_override is True

    def test_alpha_override(self):
        """Override di α_u/α_1 usa il valore fornito."""
        ris = calcola_fattore_comportamento(
            tipo_muratura=TipoMuraturaQ.ORDINARIA,
            alpha_u_alpha_1_override=1.0,
            tipo_edificio=TipoEdificio.NUOVO,
        )
        assert ris.alpha_u_alpha_1 == pytest.approx(1.0)
        assert ris.q == pytest.approx(1.75 * 1.0, abs=0.01)

    def test_alpha_override_limitato_esistente(self):
        """Override α_u/α_1 = 2.0 → limitato a 1.50 per esistente."""
        ris = calcola_fattore_comportamento(
            alpha_u_alpha_1_override=2.0,
            tipo_edificio=TipoEdificio.ESISTENTE,
        )
        assert ris.alpha_u_alpha_1 == pytest.approx(1.50, abs=0.01)


# ═══════════════════════════════════════════════════════════
#  Proprietà risultato
# ═══════════════════════════════════════════════════════════

class TestRisultatoQ:
    """Test proprietà del risultato."""

    def test_passaggi_non_vuoti(self):
        ris = calcola_fattore_comportamento()
        assert len(ris.passaggi) > 0

    def test_to_dict(self):
        ris = calcola_fattore_comportamento()
        d = ris.to_dict()
        assert "q" in d
        assert "q_0" in d
        assert "alpha_u_alpha_1" in d
        assert "K_R" in d
        assert "passaggi" in d

    def test_q_positivo(self):
        ris = calcola_fattore_comportamento()
        assert ris.q > 0

    def test_n_piani_alto(self):
        """n_piani >= 3 usa la stessa chiave 3+_piani."""
        ris5 = calcola_fattore_comportamento(n_piani=5, tipo_edificio=TipoEdificio.NUOVO)
        ris3 = calcola_fattore_comportamento(n_piani=3, tipo_edificio=TipoEdificio.NUOVO)
        assert ris5.alpha_u_alpha_1 == ris3.alpha_u_alpha_1
