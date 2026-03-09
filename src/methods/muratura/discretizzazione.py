"""Discretizzazione parete in maschi murari e fasce di piano.

Algoritmo per generare automaticamente maschi e fasce dalla geometria
della parete (coordinate + aperture), oppure accettare input manuale.

Il modello a telaio equivalente decompone ogni parete in:
- **Maschi**: elementi verticali tra le aperture (resistono a forze orizzontali)
- **Fasce**: elementi orizzontali sopra/sotto le aperture (accoppiano i maschi)
- **Nodi rigidi**: zone di intersezione maschio-fascia

Schema tipico di una parete con 2 aperture:

    ┌───────┬──────────┬───────┬──────────┬───────┐
    │       │  fascia  │       │  fascia  │       │
    │maschio├──────────┤maschio├──────────┤maschio│
    │  (1)  │ apertura │  (2)  │ apertura │  (3)  │
    │       │    (A)   │       │    (B)   │       │
    │       ├──────────┤       ├──────────┤       │
    │       │  fascia  │       │  fascia  │       │
    └───────┴──────────┴───────┴──────────┴───────┘

Unità: cm per geometria, kg per forze.

Riferimenti:
- Lagomarsino et al. (2013): TREMURI — modello a telaio equivalente
- Magenes & Della Fontana (1998): POR semplificato
- NTC2018 §7.8.1.5 — Modellazione edifici in muratura
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from src.methods.muratura.modello_edificio import (
    Apertura,
    MaterialeMuratura,
    Parete,
    Piano,
)

# ═══════════════════════════════════════════════════════════
#  Enumerazioni
# ═══════════════════════════════════════════════════════════

class TipoElemento(str, Enum):
    """Tipo di elemento nel telaio equivalente."""
    MASCHIO = "maschio"
    FASCIA = "fascia"


class TipoVincolo(str, Enum):
    """Tipo di vincolo alle estremità del maschio."""
    INCASTRO = "incastro"        # doppio incastro (fascia forte)
    CERNIERA = "cerniera"        # incastro-cerniera (fascia debole)
    MENSOLA = "mensola"          # mensola (nessuna fascia)


# ═══════════════════════════════════════════════════════════
#  Maschio murario
# ═══════════════════════════════════════════════════════════

@dataclass
class Maschio:
    """Elemento maschio murario (pannello verticale tra aperture).

    Resiste a:
    - Compressione verticale (N da carichi gravitazionali)
    - Taglio orizzontale (V da azione sismica)
    - Pressoflessione nel piano
    """
    id_maschio: int = 0
    id_parete: int = 0
    id_piano: int = 0

    # Geometria
    L: float = 0.0               # lunghezza (larghezza del maschio) [cm]
    t: float = 0.0               # spessore [cm]
    h: float = 0.0               # altezza [cm]

    # Posizione in pianta (baricentro)
    x_baricentro: float = 0.0
    y_baricentro: float = 0.0

    # Posizione lungo la parete
    x_ini_locale: float = 0.0   # coordinata locale inizio lungo la parete [cm]
    x_fin_locale: float = 0.0   # coordinata locale fine lungo la parete [cm]

    # Materiale
    materiale: Optional[MaterialeMuratura] = None

    # Carichi verticali
    N_gravitazionale: float = 0.0  # sforzo normale da carichi gravitazionali [kg]
    N_override: bool = False       # True se N impostato manualmente

    # Vincoli (determinati automaticamente o override manuale)
    vincolo: TipoVincolo = TipoVincolo.INCASTRO
    vincolo_override: bool = False  # True se vincolo impostato manualmente

    # Drift limite (configurabili, default NTC2018)
    drift_taglio: float = 0.005           # 0.5% (NTC2018 §7.8.2.2.2)
    drift_pressoflessione: float = 0.010  # 1.0% (NTC2018 §7.8.2.2.1)

    @property
    def area(self) -> float:
        """Area sezione trasversale [cm²]."""
        return self.L * self.t

    @property
    def I_x(self) -> float:
        """Momento d'inerzia flessionale nel piano [cm⁴]."""
        return self.t * self.L ** 3 / 12

    @property
    def spostamento_limite_taglio(self) -> float:
        """Spostamento limite per taglio [cm]."""
        return self.drift_taglio * self.h

    @property
    def spostamento_limite_pflex(self) -> float:
        """Spostamento limite per pressoflessione [cm]."""
        return self.drift_pressoflessione * self.h

    def to_dict(self) -> dict:
        return {
            "id_maschio": self.id_maschio,
            "id_parete": self.id_parete,
            "id_piano": self.id_piano,
            "L": round(self.L, 1),
            "t": round(self.t, 1),
            "h": round(self.h, 1),
            "x_baricentro": round(self.x_baricentro, 1),
            "y_baricentro": round(self.y_baricentro, 1),
            "N_gravitazionale": round(self.N_gravitazionale, 0),
            "vincolo": self.vincolo.value,
            "area": round(self.area, 1),
        }


# ═══════════════════════════════════════════════════════════
#  Fascia di piano
# ═══════════════════════════════════════════════════════════

@dataclass
class Fascia:
    """Elemento fascia di piano (pannello orizzontale sopra/sotto apertura).

    Accoppia i maschi adiacenti. La resistenza dipende dalla presenza
    di cordolo CA/metallico.
    """
    id_fascia: int = 0
    id_parete: int = 0
    id_piano: int = 0

    # Geometria
    L: float = 0.0               # lunghezza (luce dell'apertura sottostante) [cm]
    t: float = 0.0               # spessore [cm]
    h: float = 0.0               # altezza fascia [cm]

    # Posizione
    x_baricentro: float = 0.0
    y_baricentro: float = 0.0
    posizione: str = "superiore"  # "superiore" o "inferiore" rispetto all'apertura

    # Maschi collegati
    id_maschio_sx: int = -1      # maschio a sinistra
    id_maschio_dx: int = -1      # maschio a destra

    # Materiale
    materiale: Optional[MaterialeMuratura] = None

    # Cordolo accoppiato (auto-detect da E.5)
    ha_cordolo: bool = False
    tipo_cordolo: str = ""       # "ca", "metallico_singolo"

    @property
    def area(self) -> float:
        """Area sezione [cm²]."""
        return self.L * self.t

    @property
    def I_x(self) -> float:
        """Momento d'inerzia flessionale [cm⁴]."""
        return self.t * self.h ** 3 / 12

    @property
    def e_biella(self) -> bool:
        """True se la fascia agisce come biella (senza cordolo).

        NTC2018 §7.8.2.2.4: fascia senza cordolo non ha resistenza
        a trazione → non può trasferire momento.
        """
        return not self.ha_cordolo

    def to_dict(self) -> dict:
        return {
            "id_fascia": self.id_fascia,
            "id_parete": self.id_parete,
            "id_piano": self.id_piano,
            "L": round(self.L, 1),
            "t": round(self.t, 1),
            "h": round(self.h, 1),
            "posizione": self.posizione,
            "id_maschio_sx": self.id_maschio_sx,
            "id_maschio_dx": self.id_maschio_dx,
            "ha_cordolo": self.ha_cordolo,
            "e_biella": self.e_biella,
        }


# ═══════════════════════════════════════════════════════════
#  Risultato discretizzazione
# ═══════════════════════════════════════════════════════════

@dataclass
class RisultatoDiscretizzazione:
    """Risultato della discretizzazione di un piano."""
    maschi: list[Maschio] = field(default_factory=list)
    fasce: list[Fascia] = field(default_factory=list)
    passaggi: list[str] = field(default_factory=list)

    @property
    def n_maschi(self) -> int:
        return len(self.maschi)

    @property
    def n_fasce(self) -> int:
        return len(self.fasce)

    def maschi_in_direzione(self, direzione: str) -> list[Maschio]:
        """Filtra maschi per direzione della parete a cui appartengono."""
        # Usiamo la posizione: se x_baricentro varia di più tra i maschi
        # della stessa parete → parete in X
        return [m for m in self.maschi
                if _direzione_maschio(m) == direzione]

    def to_dict(self) -> dict:
        return {
            "n_maschi": self.n_maschi,
            "n_fasce": self.n_fasce,
            "maschi": [m.to_dict() for m in self.maschi],
            "fasce": [f.to_dict() for f in self.fasce],
            "passaggi": self.passaggi,
        }


def _direzione_maschio(maschio: Maschio) -> str:
    """Determina la direzione del maschio dalla parete di appartenenza.

    Semplificazione: usiamo un attributo interno. In mancanza,
    fallback su 'X'.
    """
    return getattr(maschio, '_direzione', 'X')


# ═══════════════════════════════════════════════════════════
#  Discretizzazione automatica
# ═══════════════════════════════════════════════════════════

def discretizza_parete(
    parete: Parete,
    altezza_interpiano: float,
    id_piano: int = 0,
    id_maschio_start: int = 0,
    id_fascia_start: int = 0,
) -> tuple[list[Maschio], list[Fascia], list[str]]:
    """Discretizza una parete in maschi e fasce.

    Algoritmo:
    1. Ordina le aperture per x_offset crescente
    2. Identifica i maschi come zone verticali tra le aperture
    3. Identifica le fasce come zone orizzontali sopra/sotto le aperture

    Args:
        parete: parete con aperture
        altezza_interpiano: altezza del piano [cm]
        id_piano: identificativo del piano
        id_maschio_start: id di partenza per maschi (per continuità numerazione)
        id_fascia_start: id di partenza per fasce

    Returns:
        (maschi, fasce, passaggi)
    """
    passaggi: list[str] = []
    maschi: list[Maschio] = []
    fasce: list[Fascia] = []

    L_parete = parete.lunghezza
    t = parete.spessore
    materiale = parete.materiale
    angolo = parete.angolo

    passaggi.append(
        f"Parete {parete.id_parete}: L={L_parete:.0f} cm, t={t:.0f} cm, "
        f"dir={parete.direzione_principale}"
    )

    # Caso senza aperture: un unico maschio
    if not parete.aperture:
        m = Maschio(
            id_maschio=id_maschio_start,
            id_parete=parete.id_parete,
            id_piano=id_piano,
            L=L_parete,
            t=t,
            h=altezza_interpiano,
            x_baricentro=parete.x_baricentro,
            y_baricentro=parete.y_baricentro,
            x_ini_locale=0.0,
            x_fin_locale=L_parete,
            materiale=materiale,
        )
        m._direzione = parete.direzione_principale  # type: ignore[attr-defined]
        maschi.append(m)
        passaggi.append(f"  Nessuna apertura → maschio unico L={L_parete:.0f}")
        return maschi, fasce, passaggi

    # Ordina aperture per x_offset
    aperture = parete.aperture_ordinate()
    passaggi.append(f"  {len(aperture)} aperture trovate")

    # Identifica zone maschio (tra inizio parete e aperture, tra aperture, dopo ultima)
    import math as _math
    cos_a = _math.cos(angolo)
    sin_a = _math.sin(angolo)

    # Confini maschi in coordinate locali (lungo la parete)
    confini_maschi: list[tuple[float, float]] = []

    # Prima del primo foro
    x_corrente = 0.0
    for ap in aperture:
        if ap.x_offset > x_corrente:
            confini_maschi.append((x_corrente, ap.x_offset))
        x_corrente = ap.x_offset + ap.larghezza

    # Dopo l'ultimo foro
    if x_corrente < L_parete:
        confini_maschi.append((x_corrente, L_parete))

    # Crea maschi
    id_m = id_maschio_start
    for x_ini, x_fin in confini_maschi:
        L_maschio = x_fin - x_ini
        if L_maschio < 1.0:  # ignora maschi troppo piccoli
            continue

        # Baricentro in coordinate globali
        x_centro_locale = (x_ini + x_fin) / 2
        xg = parete.x_ini + x_centro_locale * cos_a
        yg = parete.y_ini + x_centro_locale * sin_a

        m = Maschio(
            id_maschio=id_m,
            id_parete=parete.id_parete,
            id_piano=id_piano,
            L=L_maschio,
            t=t,
            h=altezza_interpiano,
            x_baricentro=xg,
            y_baricentro=yg,
            x_ini_locale=x_ini,
            x_fin_locale=x_fin,
            materiale=materiale,
        )
        m._direzione = parete.direzione_principale  # type: ignore[attr-defined]
        maschi.append(m)
        passaggi.append(
            f"  Maschio {id_m}: x=[{x_ini:.0f}÷{x_fin:.0f}], L={L_maschio:.0f} cm"
        )
        id_m += 1

    # Crea fasce (sopra e sotto ogni apertura)
    id_f = id_fascia_start
    for i, ap in enumerate(aperture):
        # Fascia superiore: dalla sommità dell'apertura alla sommità del piano
        h_fascia_sup = altezza_interpiano - ap.z_offset - ap.altezza
        if h_fascia_sup > 1.0:
            # Trova maschi adiacenti
            id_sx, id_dx = _trova_maschi_adiacenti(maschi, ap, parete)

            x_centro = ap.x_offset + ap.larghezza / 2
            xg = parete.x_ini + x_centro * cos_a
            yg = parete.y_ini + x_centro * sin_a

            f = Fascia(
                id_fascia=id_f,
                id_parete=parete.id_parete,
                id_piano=id_piano,
                L=ap.larghezza,
                t=t,
                h=h_fascia_sup,
                x_baricentro=xg,
                y_baricentro=yg,
                posizione="superiore",
                id_maschio_sx=id_sx,
                id_maschio_dx=id_dx,
                materiale=materiale,
            )
            fasce.append(f)
            passaggi.append(
                f"  Fascia sup {id_f}: L={ap.larghezza:.0f}, h={h_fascia_sup:.0f} cm"
            )
            id_f += 1

        # Fascia inferiore: dal pavimento alla base dell'apertura
        h_fascia_inf = ap.z_offset
        if h_fascia_inf > 1.0:
            id_sx, id_dx = _trova_maschi_adiacenti(maschi, ap, parete)

            x_centro = ap.x_offset + ap.larghezza / 2
            xg = parete.x_ini + x_centro * cos_a
            yg = parete.y_ini + x_centro * sin_a

            f = Fascia(
                id_fascia=id_f,
                id_parete=parete.id_parete,
                id_piano=id_piano,
                L=ap.larghezza,
                t=t,
                h=h_fascia_inf,
                x_baricentro=xg,
                y_baricentro=yg,
                posizione="inferiore",
                id_maschio_sx=id_sx,
                id_maschio_dx=id_dx,
                materiale=materiale,
            )
            fasce.append(f)
            passaggi.append(
                f"  Fascia inf {id_f}: L={ap.larghezza:.0f}, h={h_fascia_inf:.0f} cm"
            )
            id_f += 1

    return maschi, fasce, passaggi


def _trova_maschi_adiacenti(
    maschi: list[Maschio],
    apertura: Apertura,
    parete: Parete,
) -> tuple[int, int]:
    """Trova gli id dei maschi a sinistra e destra di un'apertura.

    Returns:
        (id_maschio_sx, id_maschio_dx), -1 se non trovato
    """
    id_sx = -1
    id_dx = -1

    for m in maschi:
        if m.id_parete != parete.id_parete:
            continue
        # Maschio a sinistra: il suo bordo destro tocca il bordo sinistro dell'apertura
        if abs(m.x_fin_locale - apertura.x_offset) < 1.0:
            id_sx = m.id_maschio
        # Maschio a destra: il suo bordo sinistro tocca il bordo destro dell'apertura
        if abs(m.x_ini_locale - apertura.x_fine) < 1.0:
            id_dx = m.id_maschio

    return id_sx, id_dx


# ═══════════════════════════════════════════════════════════
#  Discretizzazione piano completo
# ═══════════════════════════════════════════════════════════

def discretizza_piano(piano: Piano) -> RisultatoDiscretizzazione:
    """Discretizza tutte le pareti di un piano in maschi e fasce.

    Args:
        piano: piano con tutte le pareti

    Returns:
        RisultatoDiscretizzazione con tutti i maschi e fasce del piano
    """
    passaggi: list[str] = []
    tutti_maschi: list[Maschio] = []
    tutte_fasce: list[Fascia] = []

    passaggi.append(
        f"═══ Discretizzazione Piano {piano.id_piano} "
        f"(quota {piano.quota_z:.0f} cm) ═══"
    )

    id_m = 0
    id_f = 0

    for parete in piano.pareti:
        maschi, fasce, pass_p = discretizza_parete(
            parete=parete,
            altezza_interpiano=piano.altezza_interpiano,
            id_piano=piano.id_piano,
            id_maschio_start=id_m,
            id_fascia_start=id_f,
        )
        tutti_maschi.extend(maschi)
        tutte_fasce.extend(fasce)
        passaggi.extend(pass_p)

        id_m += len(maschi)
        id_f += len(fasce)

    passaggi.append(
        f"Totale: {len(tutti_maschi)} maschi, {len(tutte_fasce)} fasce"
    )

    return RisultatoDiscretizzazione(
        maschi=tutti_maschi,
        fasce=tutte_fasce,
        passaggi=passaggi,
    )


# ═══════════════════════════════════════════════════════════
#  Calcolo automatico N gravitazionale
# ═══════════════════════════════════════════════════════════

def calcola_N_gravitazionale(
    maschi_per_piano: dict[int, list[Maschio]],
    masse_piani: dict[int, float],
    piani_ordinati: list[int],
) -> list[str]:
    """Calcola lo sforzo normale gravitazionale su ogni maschio.

    Per ogni maschio, N = peso proprio + peso muratura sovrastante
    + quota parte dei carichi di solaio (proporzionale all'area di influenza).

    L'algoritmo procede dall'ultimo piano verso il basso, accumulando
    i carichi.

    Args:
        maschi_per_piano: {id_piano: [maschi]} per ogni piano
        masse_piani: {id_piano: massa_solaio} per ogni piano [kg]
        piani_ordinati: lista id_piano ordinati dal basso (0) all'alto

    Returns:
        Lista passaggi di calcolo
    """
    passaggi: list[str] = []
    passaggi.append("═══ Calcolo N gravitazionale ═══")

    # Accumula N dall'alto verso il basso
    for i_piano in reversed(piani_ordinati):
        maschi = maschi_per_piano.get(i_piano, [])
        massa_solaio = masse_piani.get(i_piano, 0.0)

        if not maschi:
            continue

        # Area totale maschi del piano (per distribuzione carico solaio)
        area_totale = sum(m.area for m in maschi)

        for m in maschi:
            if m.N_override:
                passaggi.append(
                    f"  Maschio {m.id_maschio} (P{i_piano}): N={m.N_gravitazionale:.0f} kg (override)"
                )
                continue

            # Peso proprio maschio
            gamma = m.materiale.gamma if m.materiale else 0.0018
            peso_proprio = m.L * m.t * m.h * gamma

            # Quota parte carico solaio (proporzionale all'area)
            quota_solaio = 0.0
            if area_totale > 0 and massa_solaio > 0:
                quota_solaio = massa_solaio * (m.area / area_totale)

            # Carico dal piano superiore (se esiste)
            N_sup = 0.0
            idx = piani_ordinati.index(i_piano)
            if idx < len(piani_ordinati) - 1:
                piano_sup = piani_ordinati[idx + 1]
                maschi_sup = maschi_per_piano.get(piano_sup, [])
                # Trova maschio soprastante (stessa parete, posizione simile)
                for m_sup in maschi_sup:
                    if (m_sup.id_parete == m.id_parete and
                            abs(m_sup.x_ini_locale - m.x_ini_locale) < 1.0):
                        N_sup = m_sup.N_gravitazionale
                        break

            m.N_gravitazionale = peso_proprio + quota_solaio + N_sup

            passaggi.append(
                f"  Maschio {m.id_maschio} (P{i_piano}): "
                f"Wp={peso_proprio:.0f} + Qs={quota_solaio:.0f} + N_sup={N_sup:.0f} "
                f"= {m.N_gravitazionale:.0f} kg"
            )

    return passaggi


# ═══════════════════════════════════════════════════════════
#  Determinazione automatica vincoli maschi
# ═══════════════════════════════════════════════════════════

def determina_vincoli_maschi(
    maschi: list[Maschio],
    fasce: list[Fascia],
) -> list[str]:
    """Determina i vincoli dei maschi in base alla rigidezza delle fasce.

    Regola:
    - Se il maschio ha fasce rigide sopra e sotto → INCASTRO (doppio incastro)
    - Se il maschio ha fasce deboli (biella) → CERNIERA (incastro-cerniera)
    - Se il maschio non ha fasce → MENSOLA
    - Override manuale rispettato

    Args:
        maschi: lista maschi
        fasce: lista fasce

    Returns:
        Lista passaggi di calcolo
    """
    passaggi: list[str] = []

    for m in maschi:
        if m.vincolo_override:
            passaggi.append(
                f"  Maschio {m.id_maschio}: vincolo={m.vincolo.value} (override)"
            )
            continue

        # Trova fasce collegate a questo maschio
        fasce_collegate = [
            f for f in fasce
            if f.id_maschio_sx == m.id_maschio or f.id_maschio_dx == m.id_maschio
        ]

        if not fasce_collegate:
            m.vincolo = TipoVincolo.MENSOLA
            passaggi.append(
                f"  Maschio {m.id_maschio}: nessuna fascia → mensola"
            )
        elif all(f.e_biella for f in fasce_collegate):
            m.vincolo = TipoVincolo.CERNIERA
            passaggi.append(
                f"  Maschio {m.id_maschio}: fasce biella → cerniera"
            )
        else:
            m.vincolo = TipoVincolo.INCASTRO
            passaggi.append(
                f"  Maschio {m.id_maschio}: fasce con cordolo → incastro"
            )

    return passaggi
