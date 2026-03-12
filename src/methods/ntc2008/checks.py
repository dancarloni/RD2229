"""Verifiche strutturali secondo NTC2008 come wrapper su EC2."""

from dataclasses import dataclass
from typing import Any

from src.methods.ec.ec2 import verifica_flessione_ec2, verifica_taglio_ec2


@dataclass
class VerificaNTC2008Flessione:
    """Verifica a flessione NTC2008 delegata alla formulazione EC2."""

    fck: float  # MPa
    b: float  # cm
    d: float  # cm
    As: float  # cm²
    c_nom: float

    def verifica_sl(self, M_d: float) -> dict[str, Any]:
        """Verifica agli stati limite tramite EC2 §6.1 con coefficienti NTC2008."""
        risultato = verifica_flessione_ec2(
            fck=self.fck,
            b=self.b,
            d=self.d,
            As=self.As,
            c_nom=self.c_nom,
            M_d=M_d,
        )
        risultato["riferimento_normativo"] = "NTC2008 §4.1.2.1.2 / EC2 §6.1"
        risultato["norma"] = "NTC2008"
        return risultato


def verifica_flessione(
    fck: float, b: float, d: float, As: float, c_nom: float, M_d: float
) -> dict[str, Any]:
    """Interfaccia funzionale per flessione NTC2008."""
    verifica = VerificaNTC2008Flessione(fck=fck, b=b, d=d, As=As, c_nom=c_nom)
    return verifica.verifica_sl(M_d=M_d)


def verifica_taglio(fck: float, b_w: float, d: float, rho_l: float, V_d: float) -> dict[str, Any]:
    """Interfaccia funzionale per taglio NTC2008 via EC2 §6.2.2."""
    risultato = verifica_taglio_ec2(
        fck=fck,
        b_w=b_w,
        d=d,
        rho_l=rho_l,
        V_d=V_d,
    )
    risultato["riferimento_normativo"] = "NTC2008 §4.1.2.1.3.1 / EC2 §6.2.2"
    risultato["norma"] = "NTC2008"
    return risultato
