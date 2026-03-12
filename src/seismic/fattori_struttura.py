"""Fase U.1/U.1.5 - Fattori di struttura q per edifici in c.a.

Implementa:
- Classe di duttilita CD-A, CD-B, CD-L
- Stima tabellata alpha_u/alpha_1 (NTC2018 Tab. 7.3.II, semplificata)
- Fattore k_w per sistema strutturale
- Calcolo q finale con gestione riduzioni per irregolarita

Nota:
Questa implementazione e volutamente modulare e conservativa.
Il raffinamento di alpha_u/alpha_1 da pushover e previsto in U.6.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ClasseDuttilita(str, Enum):
    """Classe di duttilita NTC/EC8."""

    CD_A = "CD_A"
    CD_B = "CD_B"
    CD_L = "CD_L"


class SistemaStrutturale(str, Enum):
    """Tipologia strutturale per il calcolo di q e alpha_u/alpha_1."""

    TELAIO = "telaio"
    PARETE = "parete"
    MISTO = "misto"


class MetodoAlpha(str, Enum):
    """Metodo di definizione del rapporto alpha_u/alpha_1."""

    TABELLA = "tabella"
    PUSHOVER = "pushover"


# Valori tabellati semplificati coerenti con piano Fase U (NTC2018 Tab. 7.3.II).
ALPHA_U_ALPHA_1_TAB_NTC2018: dict[SistemaStrutturale, tuple[float, float]] = {
    SistemaStrutturale.TELAIO: (1.30, 1.40),
    SistemaStrutturale.PARETE: (1.05, 1.10),
    SistemaStrutturale.MISTO: (1.10, 1.15),
}


@dataclass
class RisultatoFattoriStruttura:
    """Output del calcolo dei fattori di struttura."""

    q: float
    q_0: float
    alpha_u_alpha_1: float
    k_w: float
    fattore_riduzione: float
    warning_q_superiore_6: bool
    passaggi: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, float | bool | list[str]]:
        return {
            "q": round(self.q, 3),
            "q_0": round(self.q_0, 3),
            "alpha_u_alpha_1": round(self.alpha_u_alpha_1, 3),
            "k_w": round(self.k_w, 3),
            "fattore_riduzione": round(self.fattore_riduzione, 3),
            "warning_q_superiore_6": self.warning_q_superiore_6,
            "passaggi": self.passaggi,
        }


def stima_alpha_u_alpha_1(
    sistema: SistemaStrutturale,
    n_piani: int,
) -> float:
    """Stima alpha_u/alpha_1 da tabelle NTC2018 (versione semplificata).

    Regole conservative adottate:
    - Telaio 1 piano: 1.30
    - Telaio >= 2 piani: 1.35 (media 1.30-1.40)
    - Parete: 1.08 (media 1.05-1.10)
    - Misto: 1.12 (media 1.10-1.15)
    """

    if n_piani <= 0:
        raise ValueError("n_piani deve essere >= 1")

    if sistema == SistemaStrutturale.TELAIO:
        return 1.30 if n_piani == 1 else 1.35
    if sistema == SistemaStrutturale.PARETE:
        return 1.08
    if sistema == SistemaStrutturale.MISTO:
        return 1.12
    raise ValueError(f"Sistema strutturale non supportato: {sistema}")


def calcola_q0(classe: ClasseDuttilita, alpha_u_alpha_1: float) -> float:
    """Calcola q_0 in funzione della classe di duttilita."""

    if alpha_u_alpha_1 <= 0.0:
        raise ValueError("alpha_u_alpha_1 deve essere > 0")

    if classe == ClasseDuttilita.CD_A:
        return 4.5 * alpha_u_alpha_1
    if classe == ClasseDuttilita.CD_B:
        return 3.0 * alpha_u_alpha_1
    if classe == ClasseDuttilita.CD_L:
        return 1.5
    raise ValueError(f"Classe di duttilita non supportata: {classe}")


def calcola_k_w(sistema: SistemaStrutturale, alpha_0: float = 1.0) -> float:
    """Calcola il fattore k_w.

    - Telaio: k_w = 1.0
    - Parete/Misto: k_w = min((1 + alpha_0) / 3, 1.0)
    """

    if sistema == SistemaStrutturale.TELAIO:
        return 1.0

    if alpha_0 < 0.0:
        raise ValueError("alpha_0 deve essere >= 0")

    return min((1.0 + alpha_0) / 3.0, 1.0)


def _alpha_da_pushover(taglio_collasso: float, taglio_prima_plasticizzazione: float) -> float:
    """Calcola alpha_u/alpha_1 da risultati pushover semplificati."""

    if taglio_collasso <= 0.0 or taglio_prima_plasticizzazione <= 0.0:
        raise ValueError("I tagli pushover devono essere > 0")
    if taglio_collasso < taglio_prima_plasticizzazione:
        raise ValueError("taglio_collasso deve essere >= taglio_prima_plasticizzazione")
    return taglio_collasso / taglio_prima_plasticizzazione


def calcola_fattori_struttura(
    *,
    classe: ClasseDuttilita,
    sistema: SistemaStrutturale,
    n_piani: int,
    alpha_0: float = 1.0,
    metodo_alpha: MetodoAlpha = MetodoAlpha.TABELLA,
    alpha_u_alpha_1_override: float | None = None,
    taglio_collasso: float | None = None,
    taglio_prima_plasticizzazione: float | None = None,
    riduci_irregolarita: bool = False,
    riduci_eccentricita_torsionale: bool = False,
    fattore_irregolarita: float = 0.80,
    fattore_eccentricita: float = 0.90,
) -> RisultatoFattoriStruttura:
    """Calcola il fattore di struttura q con traccia passaggi.

    La funzione applica:
    1) stima alpha_u/alpha_1 (tabella o pushover o override)
    2) calcolo q_0 (classe duttilita)
    3) calcolo k_w (sistema)
    4) riduzioni opzionali per irregolarita/eccentricita
    5) vincolo q >= 1.5
    """

    passaggi: list[str] = []

    if fattore_irregolarita <= 0.0 or fattore_eccentricita <= 0.0:
        raise ValueError("I fattori di riduzione devono essere > 0")

    if alpha_u_alpha_1_override is not None:
        if alpha_u_alpha_1_override <= 0.0:
            raise ValueError("alpha_u_alpha_1_override deve essere > 0")
        alpha = alpha_u_alpha_1_override
        passaggi.append(f"alpha_u/alpha_1 override = {alpha:.3f}")
    elif classe == ClasseDuttilita.CD_L:
        alpha = 1.0
        passaggi.append("Classe CD_L: alpha_u/alpha_1 non rilevante, posto a 1.0")
    elif metodo_alpha == MetodoAlpha.PUSHOVER:
        if taglio_collasso is None or taglio_prima_plasticizzazione is None:
            raise ValueError(
                "Per metodo pushover servono taglio_collasso e taglio_prima_plasticizzazione"
            )
        alpha = _alpha_da_pushover(taglio_collasso, taglio_prima_plasticizzazione)
        passaggi.append(
            "alpha_u/alpha_1 da pushover = "
            f"{taglio_collasso:.3f}/{taglio_prima_plasticizzazione:.3f} = {alpha:.3f}"
        )
    else:
        alpha = stima_alpha_u_alpha_1(sistema=sistema, n_piani=n_piani)
        passaggi.append(f"alpha_u/alpha_1 tabellato = {alpha:.3f}")

    q_0 = calcola_q0(classe=classe, alpha_u_alpha_1=alpha)
    passaggi.append(f"q_0 = {q_0:.3f}")

    k_w = calcola_k_w(sistema=sistema, alpha_0=alpha_0)
    passaggi.append(f"k_w = {k_w:.3f}")

    q = q_0 * k_w
    passaggi.append(f"q preliminare = q_0 * k_w = {q:.3f}")

    fattore_riduzione = 1.0
    if riduci_irregolarita:
        fattore_riduzione *= fattore_irregolarita
        passaggi.append(f"Riduzione irregolarita: x{fattore_irregolarita:.3f}")
    if riduci_eccentricita_torsionale:
        fattore_riduzione *= fattore_eccentricita
        passaggi.append(f"Riduzione eccentricita torsionale: x{fattore_eccentricita:.3f}")

    q *= fattore_riduzione
    passaggi.append(f"q dopo riduzioni = {q:.3f}")

    if q < 1.5:
        passaggi.append("Applicato limite minimo normativo q = 1.5")
        q = 1.5

    warning_q_superiore_6 = q > 6.0
    if warning_q_superiore_6:
        passaggi.append("Warning: q > 6.0 (verificare limiti EC8/NTC)")

    return RisultatoFattoriStruttura(
        q=q,
        q_0=q_0,
        alpha_u_alpha_1=alpha,
        k_w=k_w,
        fattore_riduzione=fattore_riduzione,
        warning_q_superiore_6=warning_q_superiore_6,
        passaggi=passaggi,
    )
