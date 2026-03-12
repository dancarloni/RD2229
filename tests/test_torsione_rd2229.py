"""Test per la verifica a torsione TA — RD 2229/39.

Verifica le formule di τ_max per ogni tipo di sezione e il flusso
completo di verifica/progetto armatura a torsione.
"""

import math

import pytest

from src.methods.rd2229.torsione import (
    EsitoTorsione,
    InputTorsione,
    TipoSezione,
    calcola_tau_max_circolare,
    calcola_tau_max_doppio_T,
    calcola_tau_max_rettangolare,
    calcola_tau_max_scatolare,
    calcola_tau_max_T,
    verifica_torsione_ta,
)


class TestTauMaxRettangolare:
    """Test τ_max per sezione rettangolare."""

    def test_sezione_quadrata(self) -> None:
        """Per sezione quadrata a=b → Ψ = 3 + 2.6/(0.45+1) = 4.793."""
        tau, psi = calcola_tau_max_rettangolare(100000.0, 30.0, 30.0)
        assert 4.79 < psi < 4.80
        expected = psi * 100000.0 / (30.0 * 30.0**2)
        assert abs(tau - expected) < 0.01

    def test_sezione_rettangolare_stretta(self) -> None:
        """Sezione 20×50: a=50, b=20."""
        tau, psi = calcola_tau_max_rettangolare(50000.0, 20.0, 50.0)
        # a/b = 50/20 = 2.5 → Ψ = 3 + 2.6/(0.45+2.5) = 3.881
        psi_atteso = 3.0 + 2.6 / (0.45 + 2.5)
        assert abs(psi - psi_atteso) < 0.01
        expected = psi * 50000.0 / (50.0 * 20.0**2)
        assert abs(tau - expected) < 0.01

    def test_scambia_BH(self) -> None:
        """B > H e B < H devono dare lo stesso risultato."""
        tau1, psi1 = calcola_tau_max_rettangolare(80000.0, 25.0, 40.0)
        tau2, psi2 = calcola_tau_max_rettangolare(80000.0, 40.0, 25.0)
        assert abs(tau1 - tau2) < 0.001
        assert abs(psi1 - psi2) < 0.001

    def test_momento_nullo(self) -> None:
        tau, psi = calcola_tau_max_rettangolare(0.0, 30.0, 50.0)
        assert tau == 0.0

    def test_momento_negativo(self) -> None:
        """Il segno del momento non influisce (si usa |Mx|)."""
        tau_pos, _ = calcola_tau_max_rettangolare(50000.0, 30.0, 50.0)
        tau_neg, _ = calcola_tau_max_rettangolare(-50000.0, 30.0, 50.0)
        assert abs(tau_pos - tau_neg) < 0.001


class TestTauMaxCircolare:
    """Test τ_max per sezione circolare."""

    def test_circolare_piena(self) -> None:
        """Sezione piena D=40 cm."""
        tau = calcola_tau_max_circolare(100000.0, 40.0, 0.0)
        Re = 20.0
        expected = 2.0 * 100000.0 * Re / (math.pi * Re**4)
        assert abs(tau - expected) < 0.01

    def test_circolare_cava(self) -> None:
        """Sezione cava D=50, Di=30 cm."""
        tau = calcola_tau_max_circolare(200000.0, 50.0, 30.0)
        Re, Ri = 25.0, 15.0
        expected = 2.0 * 200000.0 * Re / (math.pi * (Re**4 - Ri**4))
        assert abs(tau - expected) < 0.01
        assert tau > 0

    def test_cava_piu_alta_piena(self) -> None:
        """A parità di Mx e D, la cava ha τ_max maggiore (meno materiale)."""
        tau_piena = calcola_tau_max_circolare(100000.0, 40.0, 0.0)
        tau_cava = calcola_tau_max_circolare(100000.0, 40.0, 20.0)
        assert tau_cava > tau_piena


class TestTauMaxT:
    """Test τ_max per sezione a T."""

    def test_sezione_T_tipica(self) -> None:
        """T con ala 60×15 e anima 25×45 (H=60)."""
        tau = calcola_tau_max_T(150000.0, B=60.0, H=60.0, Bo=25.0, S=15.0)
        assert tau > 0

    def test_simmetria_T(self) -> None:
        """Se ala = anima, risultato deterministico."""
        tau = calcola_tau_max_T(100000.0, B=30.0, H=60.0, Bo=30.0, S=30.0)
        # a1=b1=30, a2=b2=30, bmax=30
        # τ = 3·|Mx|·30 / (30·30³ + 30·30³) = 3·Mx·30 / (2·30·27000)
        assert tau > 0


class TestTauMaxDoppioT:
    """Test τ_max per sezione a doppio T (I)."""

    def test_sezione_I_simmetrica(self) -> None:
        tau = calcola_tau_max_doppio_T(200000.0, B=30.0, H=50.0, Bo=15.0, S=10.0)
        assert tau > 0

    def test_doppio_T_coerenza(self) -> None:
        """Il doppio T con ali larghe ha denom maggiore → τ minore."""
        tau_T = calcola_tau_max_T(100000.0, B=40.0, H=60.0, Bo=12.0, S=12.0)
        tau_I = calcola_tau_max_doppio_T(100000.0, B=40.0, H=60.0, Bo=12.0, S=12.0)
        assert tau_I < tau_T


class TestTauMaxScatolare:
    """Test τ_max per sezione scatolare."""

    def test_scatolare_tipica(self) -> None:
        tau = calcola_tau_max_scatolare(300000.0, B=40.0, H=60.0, S=8.0)
        Am = (40.0 - 8.0) * (60.0 - 8.0)
        expected = 300000.0 / (2.0 * Am * 8.0)
        assert abs(tau - expected) < 0.01


class TestVerificaTorsioneTA:
    """Test del flusso completo di verifica/progetto."""

    def _input_rettangolare(self, Mx: float = 50000.0) -> InputTorsione:
        return InputTorsione(
            Mx=Mx,
            tipo_sezione=TipoSezione.RETTANGOLARE,
            tau_c0=5.0,
            tau_c1=14.0,
            sigma_s_adm=1200.0,
            B=30.0,
            H=50.0,
        )

    def test_momento_nullo(self) -> None:
        inp = self._input_rettangolare(Mx=0.0)
        ris = verifica_torsione_ta(inp)
        assert ris.esito == EsitoTorsione.NESSUN_MOMENTO

    def test_tau_basso_nessuna_armatura(self) -> None:
        """Momento piccolo → τ < τ_c0 → nessuna armatura."""
        inp = self._input_rettangolare(Mx=5000.0)
        ris = verifica_torsione_ta(inp)
        assert ris.esito == EsitoTorsione.NESSUNA_ARMATURA
        assert ris.verifica_soddisfatta is True

    def test_tau_alto_sezione_insufficiente(self) -> None:
        """Momento molto grande → τ > τ_c1 → sezione insufficiente."""
        inp = self._input_rettangolare(Mx=5000000.0)
        ris = verifica_torsione_ta(inp)
        assert ris.esito == EsitoTorsione.SEZIONE_INSUFFICIENTE
        assert ris.verifica_soddisfatta is False

    def test_armatura_necessaria_progetto(self) -> None:
        """Momento intermedio → progetto armatura."""
        inp = self._input_rettangolare(Mx=200000.0)
        inp.Asw_to = 0.5  # braccio staffa
        ris = verifica_torsione_ta(inp, modo_verifica=False)
        if ris.esito == EsitoTorsione.ARMATURA_NECESSARIA:
            assert ris.Al_to > 0
            assert ris.n_barre > 0

    def test_interazione_TV(self) -> None:
        """Con taglio concomitante, τ_c1,t = τ_c1 × 1.1."""
        inp = self._input_rettangolare(Mx=200000.0)
        inp.Ty = 5000.0
        ris = verifica_torsione_ta(inp)
        assert ris.tau_c1_t == pytest.approx(14.0 * 1.1)

    def test_verifica_armatura_sufficiente(self) -> None:
        """Verifica con armatura sufficiente."""
        inp = self._input_rettangolare(Mx=200000.0)
        inp.Al_to = 20.0  # cm² abbondante
        inp.Asw_to = 0.5
        inp.Pst_to = 10.0
        ris = verifica_torsione_ta(inp, modo_verifica=True)
        if ris.esito == EsitoTorsione.ARMATURA_NECESSARIA:
            assert ris.sigma_l > 0
            # Con 20 cm² dovrebbe verificare
            assert ris.verifica_soddisfatta is True

    def test_circolare_piena(self) -> None:
        inp = InputTorsione(
            Mx=100000.0,
            tipo_sezione=TipoSezione.CIRCOLARE,
            tau_c0=5.0,
            tau_c1=14.0,
            sigma_s_adm=1200.0,
            D=40.0,
            Di=0.0,
        )
        ris = verifica_torsione_ta(inp)
        assert ris.tau_max > 0
        assert ris.esito != EsitoTorsione.SEZIONE_NON_SUPPORTATA

    def test_scatolare(self) -> None:
        inp = InputTorsione(
            Mx=300000.0,
            tipo_sezione=TipoSezione.SCATOLARE,
            tau_c0=5.0,
            tau_c1=14.0,
            sigma_s_adm=1200.0,
            B=40.0,
            H=60.0,
            S=8.0,
        )
        ris = verifica_torsione_ta(inp)
        assert ris.tau_max > 0

    def test_to_dict(self) -> None:
        inp = self._input_rettangolare(Mx=50000.0)
        ris = verifica_torsione_ta(inp)
        d = ris.to_dict()
        assert "esito" in d
        assert "tau_max_kg_cm2" in d
        assert "passaggi" in d
        assert len(d["passaggi"]) > 0

    def test_passaggi_non_vuoti(self) -> None:
        """Ogni verifica deve produrre passaggi di calcolo."""
        inp = self._input_rettangolare(Mx=200000.0)
        ris = verifica_torsione_ta(inp)
        assert len(ris.passaggi) >= 3
