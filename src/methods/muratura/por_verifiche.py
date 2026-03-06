"""Verifiche POR e report — tabella maschi, ζ_E, grafico pushover.

Genera:
1. Tabella maschi tipo 3Muri/Aedes (N, V_Ed, V_Rd, D/C, criterio)
2. Riepilogo indice rischio ζ_E globale vs locale
3. Grafico matplotlib curva pushover + bilineare

Unità: cm, kg, kg/cm².

Riferimenti:
- NTC2018 §7.8 — Verifiche edifici in muratura
- Circolare n.7/2019 §C8.7.1 — Edifici esistenti in muratura
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from src.methods.muratura.discretizzazione import Maschio
from src.methods.muratura.resistenza import (
    ResistenzaMaschio,
    StatoMaschio,
)
from src.methods.muratura.por_analisi import (
    CurvaPushover,
    RisultatoPOR,
)


# ═══════════════════════════════════════════════════════════
#  Riga tabella maschi
# ═══════════════════════════════════════════════════════════

@dataclass
class RigaMaschio:
    """Riga della tabella verifiche maschi (stile 3Muri/Aedes)."""
    id_maschio: int = 0
    piano: int = 0
    parete: int = 0
    L: float = 0.0                   # [cm]
    t: float = 0.0                   # [cm]
    h: float = 0.0                   # [cm]
    N: float = 0.0                   # sforzo normale [kg]
    V_Ed: float = 0.0               # taglio di progetto [kg]
    V_Rd: float = 0.0               # resistenza a taglio [kg]
    criterio: str = ""               # criterio dominante
    DC: float = 0.0                  # rapporto domanda/capacità
    verificato: bool = True
    stato: str = ""                  # "elastico", "plastico", "collassato"

    def to_dict(self) -> dict:
        return {
            "id": self.id_maschio,
            "piano": self.piano,
            "parete": self.parete,
            "L": round(self.L, 0),
            "t": round(self.t, 0),
            "h": round(self.h, 0),
            "N": round(self.N, 0),
            "V_Ed": round(self.V_Ed, 0),
            "V_Rd": round(self.V_Rd, 0),
            "criterio": self.criterio,
            "D/C": round(self.DC, 3),
            "verificato": self.verificato,
            "stato": self.stato,
        }


# ═══════════════════════════════════════════════════════════
#  Tabella verifiche maschi
# ═══════════════════════════════════════════════════════════

@dataclass
class TabellaVerificheMaschi:
    """Tabella completa delle verifiche maschi per un'analisi."""
    righe: list[RigaMaschio] = field(default_factory=list)
    direzione: str = "X"
    distribuzione: str = "modo_1"

    @property
    def n_verificati(self) -> int:
        return sum(1 for r in self.righe if r.verificato)

    @property
    def n_non_verificati(self) -> int:
        return sum(1 for r in self.righe if not r.verificato)

    @property
    def DC_max(self) -> float:
        if not self.righe:
            return 0.0
        return max(r.DC for r in self.righe)

    def to_dict(self) -> dict:
        return {
            "direzione": self.direzione,
            "distribuzione": self.distribuzione,
            "n_maschi": len(self.righe),
            "n_verificati": self.n_verificati,
            "n_non_verificati": self.n_non_verificati,
            "DC_max": round(self.DC_max, 3),
            "righe": [r.to_dict() for r in self.righe],
        }

    def formato_testo(self) -> str:
        """Genera tabella in formato testo (ASCII) per tabulati."""
        linee: list[str] = []
        sep = "─" * 105
        linee.append(f"TABELLA VERIFICHE MASCHI — Direzione {self.direzione}, {self.distribuzione}")
        linee.append(sep)
        linee.append(
            f"{'ID':>4} {'P':>2} {'Par':>3} "
            f"{'L':>6} {'t':>4} {'h':>6} "
            f"{'N':>10} {'V_Ed':>10} {'V_Rd':>10} "
            f"{'Criterio':>16} {'D/C':>6} {'Esito':>8}"
        )
        linee.append(sep)

        for r in self.righe:
            esito = "OK" if r.verificato else "NO"
            linee.append(
                f"{r.id_maschio:>4} {r.piano:>2} {r.parete:>3} "
                f"{r.L:>6.0f} {r.t:>4.0f} {r.h:>6.0f} "
                f"{r.N:>10.0f} {r.V_Ed:>10.0f} {r.V_Rd:>10.0f} "
                f"{r.criterio:>16} {r.DC:>6.3f} {esito:>8}"
            )

        linee.append(sep)
        linee.append(
            f"Totale: {len(self.righe)} maschi, "
            f"{self.n_verificati} OK, {self.n_non_verificati} NON VERIFICATI, "
            f"D/C max = {self.DC_max:.3f}"
        )
        return "\n".join(linee)


def genera_tabella_maschi(
    maschi: list[Maschio],
    resistenze: list[ResistenzaMaschio],
    tagli_ed: dict[int, float],
    direzione: str = "X",
    distribuzione: str = "modo_1",
) -> TabellaVerificheMaschi:
    """Genera la tabella delle verifiche maschi.

    Args:
        maschi: lista maschi
        resistenze: lista resistenze (stessa lunghezza)
        tagli_ed: {id_maschio: V_Ed} taglio di progetto da analisi
        direzione: direzione analisi
        distribuzione: tipo distribuzione

    Returns:
        TabellaVerificheMaschi
    """
    tabella = TabellaVerificheMaschi(
        direzione=direzione,
        distribuzione=distribuzione,
    )

    res_map = {r.id_maschio: r for r in resistenze}

    for m in maschi:
        rm = res_map.get(m.id_maschio)
        V_Ed = abs(tagli_ed.get(m.id_maschio, 0.0))
        V_Rd = rm.V_Rd if rm else 0.0
        criterio = rm.criterio_dominante if rm else ""
        DC = V_Ed / V_Rd if V_Rd > 0 else float("inf") if V_Ed > 0 else 0.0

        # Stato dal confronto con delta_y e delta_u
        stato = "elastico"
        if rm and rm.k_elastico > 0:
            delta = V_Ed / rm.k_elastico
            stato_enum = rm.stato_per_spostamento(delta)
            stato = stato_enum.value

        riga = RigaMaschio(
            id_maschio=m.id_maschio,
            piano=m.id_piano,
            parete=m.id_parete,
            L=m.L, t=m.t, h=m.h,
            N=m.N_gravitazionale,
            V_Ed=V_Ed,
            V_Rd=V_Rd,
            criterio=criterio,
            DC=DC,
            verificato=DC <= 1.0,
            stato=stato,
        )
        tabella.righe.append(riga)

    return tabella


# ═══════════════════════════════════════════════════════════
#  Riepilogo rischio sismico
# ═══════════════════════════════════════════════════════════

@dataclass
class RiepilogoRischio:
    """Riepilogo indice di rischio sismico globale vs locale."""
    zeta_E_globale: float = 0.0      # da POR
    zeta_E_locale: float = 0.0       # da cinematica (E.3)
    zeta_E_governante: float = 0.0   # min(globale, locale)
    governante: str = ""             # "globale" o "locale"
    passaggi: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "zeta_E_globale": round(self.zeta_E_globale, 3),
            "zeta_E_locale": round(self.zeta_E_locale, 3),
            "zeta_E_governante": round(self.zeta_E_governante, 3),
            "governante": self.governante,
        }


def calcola_riepilogo_rischio(
    zeta_E_globale: float = 0.0,
    zeta_E_locale: float = 0.0,
) -> RiepilogoRischio:
    """Confronta ζ_E globale (POR) e ζ_E locale (cinematica).

    Il minimo governa la sicurezza dell'edificio.

    Args:
        zeta_E_globale: indice di rischio dall'analisi POR
        zeta_E_locale: indice di rischio dalla cinematica (min tra meccanismi)

    Returns:
        RiepilogoRischio
    """
    passaggi: list[str] = []
    passaggi.append("═══ RIEPILOGO RISCHIO SISMICO ═══")

    passaggi.append(f"ζ_E globale (POR) = {zeta_E_globale:.3f}")
    passaggi.append(f"ζ_E locale (cinematica) = {zeta_E_locale:.3f}")

    if zeta_E_globale > 0 and zeta_E_locale > 0:
        if zeta_E_globale <= zeta_E_locale:
            governante = "globale"
            zeta_gov = zeta_E_globale
        else:
            governante = "locale"
            zeta_gov = zeta_E_locale
    elif zeta_E_globale > 0:
        governante = "globale"
        zeta_gov = zeta_E_globale
    elif zeta_E_locale > 0:
        governante = "locale"
        zeta_gov = zeta_E_locale
    else:
        governante = ""
        zeta_gov = 0.0

    passaggi.append(f"→ ζ_E governante = {zeta_gov:.3f} ({governante})")

    if zeta_gov >= 1.0:
        passaggi.append("EDIFICIO VERIFICATO (ζ_E ≥ 1.0)")
    elif zeta_gov > 0:
        passaggi.append(f"EDIFICIO NON VERIFICATO (ζ_E = {zeta_gov:.3f} < 1.0)")

    return RiepilogoRischio(
        zeta_E_globale=zeta_E_globale,
        zeta_E_locale=zeta_E_locale,
        zeta_E_governante=zeta_gov,
        governante=governante,
        passaggi=passaggi,
    )


# ═══════════════════════════════════════════════════════════
#  Grafico matplotlib curva pushover
# ═══════════════════════════════════════════════════════════

def plot_curva_pushover(
    curva: CurvaPushover,
    salva_path: str | None = None,
    mostra: bool = False,
) -> Optional[object]:
    """Genera il grafico della curva pushover con bilineare sovrapposta.

    Args:
        curva: curva pushover con bilineare calcolata
        salva_path: percorso file per salvare l'immagine (PNG, PDF, SVG)
        mostra: se True, mostra il grafico a schermo (plt.show())

    Returns:
        Figura matplotlib (o None se matplotlib non disponibile)
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return None

    fig, ax = plt.subplots(1, 1, figsize=(10, 6))

    # Curva reale
    deltas = [p.delta_controllo for p in curva.punti]
    V_bases = [p.V_base for p in curva.punti]
    ax.plot(deltas, V_bases, 'b-', linewidth=2, label='Curva di capacità')

    # Bilineare
    if curva.V_y > 0 and curva.delta_y > 0:
        delta_bil = [0, curva.delta_y, curva.delta_u]
        V_bil = [0, curva.V_y, curva.V_y]
        ax.plot(delta_bil, V_bil, 'r--', linewidth=1.5, label='Bilineare equivalente')

        # Punti notevoli
        ax.plot(curva.delta_y, curva.V_y, 'ro', markersize=8)
        ax.annotate(
            f'δ_y={curva.delta_y:.3f} cm\nV_y={curva.V_y:.0f} kg',
            xy=(curva.delta_y, curva.V_y),
            xytext=(curva.delta_y + 0.3, curva.V_y * 0.85),
            fontsize=9,
        )
        ax.plot(curva.delta_u, curva.V_y, 'rs', markersize=8)
        ax.annotate(
            f'δ_u={curva.delta_u:.3f} cm',
            xy=(curva.delta_u, curva.V_y),
            xytext=(curva.delta_u - 1.5, curva.V_y * 0.7),
            fontsize=9,
        )

    ax.set_xlabel('Spostamento δ [cm]', fontsize=12)
    ax.set_ylabel('Taglio alla base V [kg]', fontsize=12)
    ax.set_title(
        f'Curva Pushover — Direzione {curva.direzione}, {curva.distribuzione}',
        fontsize=13,
    )
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)

    # Info bilineare
    if curva.T_star > 0:
        info = (
            f'T* = {curva.T_star:.3f} s\n'
            f'μ = {curva.mu:.2f}\n'
            f'k = {curva.k_bilineare:.0f} kg/cm'
        )
        ax.text(
            0.98, 0.02, info,
            transform=ax.transAxes,
            fontsize=9,
            verticalalignment='bottom',
            horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
        )

    plt.tight_layout()

    if salva_path:
        fig.savefig(salva_path, dpi=150)

    if mostra:
        plt.show()

    return fig
