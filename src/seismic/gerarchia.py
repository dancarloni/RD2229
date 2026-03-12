"""Fase U.3 - Gerarchia delle resistenze per telai in c.a.

Implementa verifiche base:
- Nodo: somma M_Rc >= gamma_Rd * somma M_Rb
- Taglio di progetto trave/pilastro da gerarchia
- Report sintetico dei nodi non verificati
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field


@dataclass
class RisultatoNodoGerarchia:
    """Esito verifica gerarchia su singolo nodo."""

    somma_m_rc: float
    somma_m_rb: float
    gamma_rd_target: float
    gamma_rd_eff: float
    verificato: bool
    passaggi: list[str] = field(default_factory=list)


@dataclass
class RisultatoGerarchiaGlobale:
    """Esito verifica gerarchia su insieme nodi."""

    nodi_verificati: int
    nodi_non_verificati: int
    esiti: list[RisultatoNodoGerarchia]


def gamma_rd_per_classe(classe_duttilita: str) -> float:
    """Restituisce gamma_Rd target per classe duttilita."""

    classe = classe_duttilita.upper()
    if classe == "CD_A":
        return 1.3
    if classe == "CD_B":
        return 1.2
    if classe == "CD_L":
        return 1.0
    raise ValueError(f"Classe duttilita non supportata: {classe_duttilita}")


def verifica_nodo_gerarchia(
    *,
    momenti_pilastri: Iterable[float],
    momenti_travi: Iterable[float],
    gamma_rd_target: float,
) -> RisultatoNodoGerarchia:
    """Verifica la gerarchia delle resistenze su nodo.

    Criterio: sum(M_Rc) >= gamma_Rd * sum(M_Rb)
    """

    if gamma_rd_target <= 0.0:
        raise ValueError("gamma_rd_target deve essere > 0")

    somma_m_rc = sum(abs(x) for x in momenti_pilastri)
    somma_m_rb = sum(abs(x) for x in momenti_travi)

    if somma_m_rb <= 0.0:
        raise ValueError("La somma dei momenti resistenti travi deve essere > 0")

    gamma_rd_eff = somma_m_rc / somma_m_rb
    verificato = somma_m_rc >= gamma_rd_target * somma_m_rb

    passaggi = [
        f"somma_m_rc = {somma_m_rc:.3f}",
        f"somma_m_rb = {somma_m_rb:.3f}",
        f"gamma_rd_eff = {gamma_rd_eff:.3f}",
        f"criterio: {somma_m_rc:.3f} >= {gamma_rd_target:.3f} * {somma_m_rb:.3f}",
        "Verifica: OK" if verificato else "Verifica: NON OK",
    ]

    return RisultatoNodoGerarchia(
        somma_m_rc=somma_m_rc,
        somma_m_rb=somma_m_rb,
        gamma_rd_target=gamma_rd_target,
        gamma_rd_eff=gamma_rd_eff,
        verificato=verificato,
        passaggi=passaggi,
    )


def calcola_v_cd_trave(
    m_rb_sinistra: float, m_rb_destra: float, luce_netta: float, v_g_pm_e_su_2: float = 0.0
) -> float:
    """Taglio di progetto trave da gerarchia.

    V_CD = (M_Rb,l + M_Rb,r) / L_cl + V_G±E/2
    """

    if luce_netta <= 0.0:
        raise ValueError("luce_netta deve essere > 0")

    return (abs(m_rb_sinistra) + abs(m_rb_destra)) / luce_netta + v_g_pm_e_su_2


def calcola_v_cd_pilastro(
    m_rc_top: float, m_rc_bot: float, altezza_netta: float, gamma_rd_target: float
) -> float:
    """Taglio di progetto pilastro da gerarchia.

    V_CD = gamma_Rd * (M_Rc,top + M_Rc,bot) / H_cl
    """

    if altezza_netta <= 0.0:
        raise ValueError("altezza_netta deve essere > 0")
    if gamma_rd_target <= 0.0:
        raise ValueError("gamma_rd_target deve essere > 0")

    return gamma_rd_target * (abs(m_rc_top) + abs(m_rc_bot)) / altezza_netta


def verifica_gerarchia_globale(
    *,
    nodi: Iterable[tuple[Iterable[float], Iterable[float]]],
    gamma_rd_target: float,
) -> RisultatoGerarchiaGlobale:
    """Verifica tutti i nodi e produce riepilogo."""

    esiti: list[RisultatoNodoGerarchia] = []
    for momenti_pilastri, momenti_travi in nodi:
        esiti.append(
            verifica_nodo_gerarchia(
                momenti_pilastri=momenti_pilastri,
                momenti_travi=momenti_travi,
                gamma_rd_target=gamma_rd_target,
            )
        )

    nodi_verificati = sum(1 for e in esiti if e.verificato)
    nodi_non_verificati = len(esiti) - nodi_verificati

    return RisultatoGerarchiaGlobale(
        nodi_verificati=nodi_verificati,
        nodi_non_verificati=nodi_non_verificati,
        esiti=esiti,
    )
