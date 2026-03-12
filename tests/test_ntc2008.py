"""Test suite NTC2008 wrapper su EC2."""

import pytest

from src.methods.ntc2008 import (
    VerificaNTC2008Flessione,
    coefficiente_spettro_elastico_ntc2008,
    fattore_amplificazione_dinamica_ntc2008,
    genera_combinazioni_ntc2008,
    verifica_flessione,
    verifica_taglio,
)


class TestVerificaNTC2008Flessione:
    """Test funzionali per flessione NTC2008."""

    def test_flessione_response(self) -> None:
        """Verifica struttura output della flessione NTC2008."""
        vf = VerificaNTC2008Flessione(
            fck=30.0,
            b=25.0,
            d=35.0,
            As=4.0,
            c_nom=3.0,  # MPa  # cm  # cm  # cm²  # cm
        )

        risultato = vf.verifica_sl(M_d=100.0 * 100)

        assert "esito" in risultato
        assert "M_Rd" in risultato
        assert "rateo" in risultato
        assert risultato["norma"] == "NTC2008"

    def test_flessione_contiene_riferimento(self) -> None:
        """L'output deve contenere riferimento normativo."""
        vf = VerificaNTC2008Flessione(fck=25.0, b=20.0, d=30.0, As=3.0, c_nom=2.5)

        risultato = vf.verifica_sl(M_d=80.0 * 100)

        assert "riferimento_normativo" in risultato
        assert "NTC2008" in risultato["riferimento_normativo"]


class TestFunzioniNTC2008:
    """Test interfacce funzionali NTC2008."""

    def test_verifica_flessione(self) -> None:
        """Test funzione verifica_flessione()."""
        risultato = verifica_flessione(fck=30.0, b=25.0, d=35.0, As=4.0, c_nom=3.0, M_d=100.0 * 100)

        assert "esito" in risultato
        assert "M_Rd" in risultato
        assert risultato["norma"] == "NTC2008"

    def test_verifica_taglio(self) -> None:
        """Test funzione verifica_taglio()."""
        risultato = verifica_taglio(fck=30.0, b_w=25.0, d=35.0, rho_l=0.01, V_d=20.0 * 1000)

        assert "esito" in risultato
        assert "V_Rd" in risultato
        assert risultato["norma"] == "NTC2008"


class TestCombinazioniEDinamicaNTC2008:
    """Test helper combinazioni e spettro NTC2008."""

    def test_genera_combinazioni(self) -> None:
        risultati = genera_combinazioni_ntc2008(
            {
                "G1": 100.0,
                "G2": 40.0,
                "variable_loads": [
                    {"name": "Q_uso", "value": 60.0, "category": "cat_A"},
                    {"name": "Q_vento", "value": 30.0, "category": "vento"},
                ],
            }
        )

        assert "SLU" in risultati
        assert "SLE_quasi_permanente" in risultati
        assert len(risultati["SLU"]) == 2
        assert risultati["SLE_quasi_permanente"][0]["total"] > 0

    def test_spettro_e_fattore_dinamico(self) -> None:
        se = coefficiente_spettro_elastico_ntc2008(
            ag=0.25,
            T=0.20,
            F0=2.4,
            Tc_star=0.45,
            S=1.2,
            eta=1.0,
        )
        fatt = fattore_amplificazione_dinamica_ntc2008(
            ag=0.25,
            T=0.20,
            F0=2.4,
            Tc_star=0.45,
            S=1.2,
            eta=1.0,
        )

        assert se > 0
        assert fatt > 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
