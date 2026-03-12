"""Carichi verticali multipiano — distribuzione per aree di influenza.

Modella i carichi di solaio gravanti sulle pareti in muratura e li distribuisce
sui maschi tramite aree di influenza geometriche.

Input per parete: G1 (peso proprio solaio), G2 (permanenti non strutturali),
Q (variabile), luce_sx e luce_dx del solaio che appoggia.

L'accumulo dei carichi verticali avviene dall'alto verso il basso,
sommando per ogni maschio:
- Peso proprio della muratura (γ×L×t×h)
- Quota parte del carico solaio (proporzionale all'area di influenza)
- Carico cumulato dal piano superiore

Unità: cm per geometria, kg per forze, kg/cm² per tensioni, kg/cm³ per γ.

Riferimenti:
- NTC2018 §7.8.1.5.2 — Carichi verticali per analisi sismica
- NTC2018 §2.5.3 — Combinazioni di carico
- NTC2018 §4.5.6 — Resistenza a compressione muratura
"""

from __future__ import annotations

from dataclasses import dataclass

from src.methods.muratura.discretizzazione import Maschio

# ═══════════════════════════════════════════════════════════
#  Modello carichi solaio
# ═══════════════════════════════════════════════════════════


@dataclass
class CaricoSolaio:
    """Carico del solaio gravante su una parete.

    Il solaio appoggia sulla parete con luci luce_sx e luce_dx
    (distanza dal bordo parete al supporto successivo).
    Il carico sulla parete è: q_tot × (luce_sx + luce_dx) / 2 × L_parete.
    """

    id_parete: int = 0
    id_piano: int = 0

    # Carichi superficiali [kg/cm²]
    G1: float = 0.0  # peso proprio solaio (strutturale)
    G2: float = 0.0  # permanenti non strutturali (pavimento, massetto)
    Q: float = 0.0  # variabile (abitazione, uffici)

    # Luci di influenza [cm]
    luce_sx: float = 0.0  # luce solaio lato sinistro
    luce_dx: float = 0.0  # luce solaio lato destro

    # Categoria d'uso (per ψ₀)
    categoria: str = "A"  # A=residenziale, B=uffici, C=affollamento, ecc.

    @property
    def luce_influenza(self) -> float:
        """Larghezza di influenza totale [cm]: (luce_sx + luce_dx) / 2."""
        return (self.luce_sx + self.luce_dx) / 2

    @property
    def q_lineare_G1(self) -> float:
        """Carico lineare G1 sulla parete [kg/cm]."""
        return self.G1 * self.luce_influenza

    @property
    def q_lineare_G2(self) -> float:
        """Carico lineare G2 sulla parete [kg/cm]."""
        return self.G2 * self.luce_influenza

    @property
    def q_lineare_Q(self) -> float:
        """Carico lineare Q sulla parete [kg/cm]."""
        return self.Q * self.luce_influenza

    @property
    def q_lineare_totale(self) -> float:
        """Carico lineare caratteristico totale [kg/cm]."""
        return (self.G1 + self.G2 + self.Q) * self.luce_influenza

    def to_dict(self) -> dict:
        return {
            "id_parete": self.id_parete,
            "id_piano": self.id_piano,
            "G1": round(self.G1, 4),
            "G2": round(self.G2, 4),
            "Q": round(self.Q, 4),
            "luce_sx": round(self.luce_sx, 1),
            "luce_dx": round(self.luce_dx, 1),
            "luce_influenza": round(self.luce_influenza, 1),
            "q_lineare_totale": round(self.q_lineare_totale, 2),
        }


# ═══════════════════════════════════════════════════════════
#  Distribuzione carichi su maschi
# ═══════════════════════════════════════════════════════════


@dataclass
class CaricoMaschio:
    """Carichi verticali su un singolo maschio, scomposti per tipo."""

    id_maschio: int = 0

    # Componenti [kg]
    peso_proprio: float = 0.0  # γ × L × t × h
    N_solaio_G1: float = 0.0  # da solaio (permanente strutturale)
    N_solaio_G2: float = 0.0  # da solaio (permanente non strutturale)
    N_solaio_Q: float = 0.0  # da solaio (variabile)
    N_superiore: float = 0.0  # cumulato dal piano superiore

    @property
    def N_G1(self) -> float:
        """Totale permanente strutturale G1 = peso proprio + solaio G1 + sup."""
        return self.peso_proprio + self.N_solaio_G1 + self.N_superiore

    @property
    def N_G2(self) -> float:
        """Totale permanente non strutturale G2."""
        return self.N_solaio_G2

    @property
    def N_Q(self) -> float:
        """Totale variabile Q."""
        return self.N_solaio_Q

    @property
    def N_caratteristico(self) -> float:
        """N totale caratteristico (non fattorizzato): G1 + G2 + Q."""
        return self.N_G1 + self.N_G2 + self.N_Q

    def to_dict(self) -> dict:
        return {
            "id_maschio": self.id_maschio,
            "peso_proprio": round(self.peso_proprio, 0),
            "N_solaio_G1": round(self.N_solaio_G1, 0),
            "N_solaio_G2": round(self.N_solaio_G2, 0),
            "N_solaio_Q": round(self.N_solaio_Q, 0),
            "N_superiore": round(self.N_superiore, 0),
            "N_G1": round(self.N_G1, 0),
            "N_G2": round(self.N_G2, 0),
            "N_Q": round(self.N_Q, 0),
            "N_caratteristico": round(self.N_caratteristico, 0),
        }


def _area_influenza_maschio(
    maschio: Maschio,
    maschi_parete: list[Maschio],
) -> float:
    """Calcola l'area di influenza di un maschio [cm²].

    L'area di influenza è la larghezza di competenza del maschio
    (metà distanza dai maschi adiacenti nella stessa parete) × 1 cm
    (il carico lineare viene poi moltiplicato per questa larghezza).

    Se il maschio è l'unico nella parete, l'area è L.
    Se ha adiacenti, la larghezza è dal punto medio sx al punto medio dx.

    Returns:
        Larghezza di competenza [cm]
    """
    # Filtra maschi della stessa parete
    stessa_parete = [
        m
        for m in maschi_parete
        if m.id_parete == maschio.id_parete and m.id_maschio != maschio.id_maschio
    ]

    if not stessa_parete:
        return maschio.L

    # Ordina per posizione locale
    tutti = sorted(
        [maschio] + stessa_parete,
        key=lambda m: m.x_ini_locale,
    )
    idx = next(i for i, m in enumerate(tutti) if m.id_maschio == maschio.id_maschio)

    # Bordo sinistro: metà distanza dal maschio precedente (o inizio parete)
    if idx == 0:
        x_sx = maschio.x_ini_locale
    else:
        m_prec = tutti[idx - 1]
        x_sx = (m_prec.x_fin_locale + maschio.x_ini_locale) / 2

    # Bordo destro: metà distanza dal maschio successivo (o fine parete)
    if idx == len(tutti) - 1:
        x_dx = maschio.x_fin_locale
    else:
        m_succ = tutti[idx + 1]
        x_dx = (maschio.x_fin_locale + m_succ.x_ini_locale) / 2

    return max(x_dx - x_sx, 0.0)


def distribuisci_carichi_solaio(
    maschi: list[Maschio],
    carichi: list[CaricoSolaio],
) -> dict[int, CaricoMaschio]:
    """Distribuisce i carichi solaio sui maschi per aree di influenza.

    Per ogni maschio:
    1. Calcola la larghezza di competenza (area di influenza)
    2. Moltiplica il carico lineare della parete × larghezza

    Args:
        maschi: maschi del piano
        carichi: carichi solaio per parete

    Returns:
        {id_maschio: CaricoMaschio}
    """
    # Mappa carichi per parete
    carico_per_parete: dict[int, CaricoSolaio] = {c.id_parete: c for c in carichi}

    risultato: dict[int, CaricoMaschio] = {}

    for m in maschi:
        cm = CaricoMaschio(id_maschio=m.id_maschio)

        # Peso proprio muratura
        gamma = m.materiale.gamma if m.materiale else 0.0018
        cm.peso_proprio = m.L * m.t * m.h * gamma

        # Carico solaio
        cs = carico_per_parete.get(m.id_parete)
        if cs is not None:
            larghezza = _area_influenza_maschio(m, maschi)
            cm.N_solaio_G1 = cs.q_lineare_G1 * larghezza
            cm.N_solaio_G2 = cs.q_lineare_G2 * larghezza
            cm.N_solaio_Q = cs.q_lineare_Q * larghezza

        risultato[m.id_maschio] = cm

    return risultato


# ═══════════════════════════════════════════════════════════
#  Accumulo multipiano (top-down)
# ═══════════════════════════════════════════════════════════


def calcola_N_multipiano(
    maschi_per_piano: dict[int, list[Maschio]],
    carichi_per_piano: dict[int, list[CaricoSolaio]],
    piani_ordinati: list[int],
) -> tuple[dict[int, dict[int, CaricoMaschio]], list[str]]:
    """Calcola i carichi verticali multipiano con accumulo top-down.

    Per ogni piano, dall'alto verso il basso:
    1. Calcola peso proprio e solaio di ogni maschio
    2. Somma il carico cumulato dal maschio soprastante (stessa parete, stessa posizione)
    3. Aggiorna N_gravitazionale nel maschio

    Args:
        maschi_per_piano: {id_piano: [maschi]}
        carichi_per_piano: {id_piano: [carichi_solaio]}
        piani_ordinati: id piani dal basso all'alto

    Returns:
        ({id_piano: {id_maschio: CaricoMaschio}}, passaggi)
    """
    passaggi: list[str] = []
    passaggi.append("═══ Carichi verticali multipiano (top-down) ═══")

    risultato: dict[int, dict[int, CaricoMaschio]] = {}

    # Dall'alto verso il basso
    for i_piano in reversed(piani_ordinati):
        maschi = maschi_per_piano.get(i_piano, [])
        carichi = carichi_per_piano.get(i_piano, [])

        if not maschi:
            continue

        # Distribuisci carichi solaio
        carichi_maschi = distribuisci_carichi_solaio(maschi, carichi)

        # Accumulo dal piano superiore
        idx = piani_ordinati.index(i_piano)
        if idx < len(piani_ordinati) - 1:
            piano_sup = piani_ordinati[idx + 1]
            carichi_sup = risultato.get(piano_sup, {})

            for m in maschi:
                if m.N_override:
                    continue
                # Trova maschio soprastante (stessa parete, posizione locale simile)
                maschi_sup = maschi_per_piano.get(piano_sup, [])
                for m_sup in maschi_sup:
                    if (
                        m_sup.id_parete == m.id_parete
                        and abs(m_sup.x_ini_locale - m.x_ini_locale) < 1.0
                    ):
                        cm_sup = carichi_sup.get(m_sup.id_maschio)
                        if cm_sup is not None:
                            carichi_maschi[m.id_maschio].N_superiore = cm_sup.N_caratteristico
                        break

        # Aggiorna N_gravitazionale nei maschi (con valore caratteristico)
        for m in maschi:
            if m.N_override:
                passaggi.append(
                    f"  P{i_piano} M{m.id_maschio}: N={m.N_gravitazionale:.0f} kg (override)"
                )
                continue
            cm = carichi_maschi.get(m.id_maschio)
            if cm is not None:
                m.N_gravitazionale = cm.N_caratteristico
                passaggi.append(
                    f"  P{i_piano} M{m.id_maschio}: "
                    f"Wp={cm.peso_proprio:.0f} + G1s={cm.N_solaio_G1:.0f} "
                    f"+ G2s={cm.N_solaio_G2:.0f} + Qs={cm.N_solaio_Q:.0f} "
                    f"+ Nsup={cm.N_superiore:.0f} = {cm.N_caratteristico:.0f} kg"
                )

        risultato[i_piano] = carichi_maschi

    return risultato, passaggi
