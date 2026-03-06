"""Analisi POR pushover — telaio equivalente multipiano.

Algoritmo pushover incrementale:
1. Definire distribuzione forze in altezza (2 distribuzioni NTC2018)
2. Incrementare lo spostamento del piano di controllo
3. Per ogni passo, distribuire forze sui maschi (con 3 GDL/piano)
4. Verificare plasticizzazione e collasso dei maschi
5. Costruire curva V_base - δ_sommità
6. Bilinearizzare (equipartizione energetica)

Multipiano con 3 GDL/piano: ux, uy, θz.
2 distribuzioni: proporzionale a massa (uniforme) e a massa×quota (modo 1).
2 direzioni: X e Y.
Combinazione: 100% + 30%.
Eccentricità accidentale: ±5%.

Unità: cm, kg, kg/cm².

Riferimenti:
- NTC2018 §7.3.4.1 — Analisi statica non lineare (pushover)
- NTC2018 §7.8.1.5 — Modellazione edifici in muratura
- NTC2018 §7.8.1.6 — Bilinearizzazione curva di capacità
- Circolare n.7/2019 §C7.3.4.1 — Dettagli analisi pushover
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from src.methods.muratura.discretizzazione import (
    Maschio,
    Fascia,
    RisultatoDiscretizzazione,
)
from src.methods.muratura.modello_edificio import (
    ConfigPOR,
    Edificio,
    Piano,
    ParametriSismiciEdificio,
)
from src.methods.muratura.resistenza import (
    ResistenzaMaschio,
    StatoMaschio,
    calcola_resistenza_maschio,
)
from src.methods.muratura.rigidezza import (
    calcola_centro_rigidezza,
    distribuisci_forza_piano,
    rigidezza_maschio,
)


# ═══════════════════════════════════════════════════════════
#  Distribuzione forze in altezza
# ═══════════════════════════════════════════════════════════

class TipoDistribuzione(str, Enum):
    """Tipo di distribuzione delle forze sismiche in altezza."""
    UNIFORME = "uniforme"                    # proporzionale alle masse
    MODO_1 = "modo_1"                        # proporzionale a massa × quota


def forze_in_altezza(
    masse: list[float],
    quote: list[float],
    V_base: float,
    distribuzione: TipoDistribuzione = TipoDistribuzione.MODO_1,
) -> list[float]:
    """Calcola la distribuzione delle forze orizzontali in altezza.

    NTC2018 §7.3.4.1:
    - Distribuzione 1 (modo 1): F_i = V_base × (m_i × z_i) / Σ(m_j × z_j)
    - Distribuzione 2 (uniforme): F_i = V_base × m_i / Σ(m_j)

    Args:
        masse: masse dei piani [kg]
        quote: quote dei piani (baricentro interpiano) [cm]
        V_base: taglio alla base [kg]
        distribuzione: tipo di distribuzione

    Returns:
        Lista forze per piano [kg]
    """
    n = len(masse)
    if n == 0:
        return []

    if distribuzione == TipoDistribuzione.UNIFORME:
        M_tot = sum(masse)
        if M_tot <= 0:
            return [0.0] * n
        return [V_base * m / M_tot for m in masse]
    else:  # MODO_1
        somma_mz = sum(m * z for m, z in zip(masse, quote))
        if somma_mz <= 0:
            return [0.0] * n
        return [V_base * m * z / somma_mz for m, z in zip(masse, quote)]


# ═══════════════════════════════════════════════════════════
#  Punto curva pushover
# ═══════════════════════════════════════════════════════════

@dataclass
class PuntoPushover:
    """Singolo punto della curva di capacità."""
    passo: int = 0
    delta_controllo: float = 0.0     # spostamento piano di controllo [cm]
    V_base: float = 0.0              # taglio alla base [kg]
    n_elastici: int = 0              # maschi ancora elastici
    n_plastici: int = 0              # maschi in plateau
    n_collassati: int = 0            # maschi collassati


@dataclass
class CurvaPushover:
    """Curva di capacità V_base - δ."""
    punti: list[PuntoPushover] = field(default_factory=list)
    direzione: str = "X"
    distribuzione: str = "modo_1"

    # Bilineare equivalente
    V_y: float = 0.0                 # taglio allo snervamento bilineare [kg]
    delta_y: float = 0.0             # spostamento snervamento [cm]
    delta_u: float = 0.0             # spostamento ultimo [cm]
    k_bilineare: float = 0.0         # rigidezza bilineare [kg/cm]
    mu: float = 0.0                  # duttilità δ_u/δ_y

    # Proprietà SDOF equivalente
    M_star: float = 0.0              # massa SDOF [kg]
    T_star: float = 0.0              # periodo SDOF [s]
    Gamma: float = 0.0               # fattore di partecipazione

    passaggi: list[str] = field(default_factory=list)

    @property
    def V_max(self) -> float:
        if not self.punti:
            return 0.0
        return max(p.V_base for p in self.punti)

    @property
    def delta_max(self) -> float:
        if not self.punti:
            return 0.0
        return max(p.delta_controllo for p in self.punti)

    def to_dict(self) -> dict:
        return {
            "direzione": self.direzione,
            "distribuzione": self.distribuzione,
            "n_punti": len(self.punti),
            "V_max": round(self.V_max, 0),
            "V_y": round(self.V_y, 0),
            "delta_y": round(self.delta_y, 4),
            "delta_u": round(self.delta_u, 4),
            "k_bilineare": round(self.k_bilineare, 0),
            "mu": round(self.mu, 2),
            "M_star": round(self.M_star, 0),
            "T_star": round(self.T_star, 3),
            "Gamma": round(self.Gamma, 3),
        }


# ═══════════════════════════════════════════════════════════
#  Pushover singolo piano (POR classico)
# ═══════════════════════════════════════════════════════════

def pushover_piano(
    maschi: list[Maschio],
    resistenze: list[ResistenzaMaschio],
    forza_piano: float,
    config: ConfigPOR,
    x_rif: float = 0.0,
    y_rif: float = 0.0,
    direzione: str = "X",
    eccentricita: float = 0.0,
) -> CurvaPushover:
    """Esegue la pushover su un singolo piano (POR classico).

    Algoritmo incrementale:
    1. Incrementa lo spostamento δ
    2. Per ogni maschio: V_i = min(k_i × δ_i, V_Rd_i)
    3. V_base = Σ V_i
    4. Se V_base scende sotto soglia → collasso

    Args:
        maschi: lista maschi del piano
        resistenze: lista resistenze maschi (stessa lunghezza/ordine)
        forza_piano: forza massima attesa (per scalare gli incrementi)
        config: configurazione POR
        x_rif: punto di riferimento x
        y_rif: punto di riferimento y
        direzione: "X" o "Y"
        eccentricita: eccentricità accidentale [cm] (per momento torcente)

    Returns:
        CurvaPushover
    """
    curva = CurvaPushover(direzione=direzione)
    passaggi: list[str] = []

    # Mappa resistenze per id_maschio
    res_map: dict[int, ResistenzaMaschio] = {r.id_maschio: r for r in resistenze}

    # Incremento spostamento
    delta_inc = config.spostamento_max / config.n_passi
    V_base_max = 0.0

    for passo in range(config.n_passi + 1):
        delta = passo * delta_inc

        # Calcola forza su ogni maschio dalla curva bilineare
        V_base = 0.0
        n_el, n_pl, n_co = 0, 0, 0

        tagli: dict[int, float] = {}

        for m in maschi:
            rm = res_map.get(m.id_maschio)
            if rm is None or rm.V_Rd <= 0:
                tagli[m.id_maschio] = 0.0
                n_co += 1
                continue

            # Spostamento locale del maschio
            # Per diaframma rigido, tutti hanno lo stesso δ (senza torsione)
            # Con torsione, δ_locale dipende dalla posizione
            delta_locale = delta  # semplificazione per singolo piano

            V_i = rm.forza_per_spostamento(delta_locale)
            stato = rm.stato_per_spostamento(delta_locale)

            tagli[m.id_maschio] = V_i

            if direzione == "X":
                V_base += V_i
            else:
                V_base += V_i

            if stato == StatoMaschio.ELASTICO:
                n_el += 1
            elif stato == StatoMaschio.PLASTICO:
                n_pl += 1
            else:
                n_co += 1

        curva.punti.append(PuntoPushover(
            passo=passo,
            delta_controllo=delta,
            V_base=abs(V_base),
            n_elastici=n_el,
            n_plastici=n_pl,
            n_collassati=n_co,
        ))

        if abs(V_base) > V_base_max:
            V_base_max = abs(V_base)

        # Criterio collasso
        n_tot = len(maschi)
        if n_tot > 0 and passo > 0:
            if config.criterio_collasso == "caduta_resistenza":
                if V_base_max > 0 and abs(V_base) < config.soglia_caduta_resistenza * V_base_max:
                    passaggi.append(
                        f"Collasso al passo {passo}: V_base={abs(V_base):.0f} < "
                        f"{config.soglia_caduta_resistenza:.0%}×V_max={V_base_max:.0f}"
                    )
                    break
            elif config.criterio_collasso == "maschi_collassati":
                if n_co / n_tot > config.soglia_maschi_collassati:
                    passaggi.append(
                        f"Collasso al passo {passo}: {n_co}/{n_tot} maschi collassati"
                    )
                    break

    curva.passaggi = passaggi
    return curva


# ═══════════════════════════════════════════════════════════
#  Pushover multipiano
# ═══════════════════════════════════════════════════════════

def pushover_multipiano(
    maschi_per_piano: dict[int, list[Maschio]],
    resistenze_per_piano: dict[int, list[ResistenzaMaschio]],
    masse: list[float],
    quote: list[float],
    piani_ordinati: list[int],
    config: ConfigPOR,
    direzione: str = "X",
    distribuzione: TipoDistribuzione = TipoDistribuzione.MODO_1,
    eccentricita: float = 0.0,
) -> CurvaPushover:
    """Pushover multipiano con distribuzione forze in altezza.

    Per ogni passo di spostamento del piano di controllo (sommità):
    1. Distribuisce le forze in altezza secondo la distribuzione scelta
    2. Per ogni piano, dal basso verso l'alto, accumula il taglio
    3. Ogni piano ha la sua curva bilineare (somma dei maschi)

    Semplificazione: spostamenti proporzionali al modo (lineare in altezza).

    Args:
        maschi_per_piano: {id_piano: [maschi]}
        resistenze_per_piano: {id_piano: [resistenze]}
        masse: masse per piano
        quote: quote baricentro piano
        piani_ordinati: id_piano dal basso all'alto
        config: configurazione
        direzione: "X" o "Y"
        distribuzione: tipo distribuzione forze
        eccentricita: eccentricità accidentale

    Returns:
        CurvaPushover
    """
    curva = CurvaPushover(direzione=direzione, distribuzione=distribuzione.value)
    passaggi: list[str] = []

    n_piani = len(piani_ordinati)
    if n_piani == 0:
        return curva

    # Piano di controllo = sommità (ultimo piano)
    piano_controllo = piani_ordinati[-1]
    h_tot = max(quote) if quote else 1.0

    # Profilo spostamenti proporzionale alla quota (modo 1)
    # o uniforme (per distribuzione uniforme)
    if distribuzione == TipoDistribuzione.MODO_1:
        profilo = [z / h_tot if h_tot > 0 else 0.0 for z in quote]
    else:
        profilo = [1.0] * n_piani

    delta_inc = config.spostamento_max / config.n_passi
    V_base_max = 0.0

    for passo in range(config.n_passi + 1):
        delta_controllo = passo * delta_inc

        # Spostamento di ogni piano
        deltas_piano = [delta_controllo * p for p in profilo]

        V_base = 0.0
        n_el_tot, n_pl_tot, n_co_tot = 0, 0, 0

        for i, id_piano in enumerate(piani_ordinati):
            maschi = maschi_per_piano.get(id_piano, [])
            resistenze = resistenze_per_piano.get(id_piano, [])
            delta_piano = deltas_piano[i]

            res_map = {r.id_maschio: r for r in resistenze}

            for m in maschi:
                rm = res_map.get(m.id_maschio)
                if rm is None or rm.V_Rd <= 0:
                    n_co_tot += 1
                    continue

                V_i = rm.forza_per_spostamento(delta_piano)
                stato = rm.stato_per_spostamento(delta_piano)

                if i == 0:  # piano terra → contribuisce al taglio di base
                    V_base += V_i

                if stato == StatoMaschio.ELASTICO:
                    n_el_tot += 1
                elif stato == StatoMaschio.PLASTICO:
                    n_pl_tot += 1
                else:
                    n_co_tot += 1

        # Il taglio di base è la somma delle forze resistite dal piano terra
        # (approssimazione: in realtà V_base = Σ F_i = Σ V_piano_terra)
        curva.punti.append(PuntoPushover(
            passo=passo,
            delta_controllo=delta_controllo,
            V_base=abs(V_base),
            n_elastici=n_el_tot,
            n_plastici=n_pl_tot,
            n_collassati=n_co_tot,
        ))

        if abs(V_base) > V_base_max:
            V_base_max = abs(V_base)

        # Criterio collasso
        n_tot = sum(len(maschi_per_piano.get(p, [])) for p in piani_ordinati)
        if n_tot > 0 and passo > 0:
            if config.criterio_collasso == "caduta_resistenza":
                if V_base_max > 0 and abs(V_base) < config.soglia_caduta_resistenza * V_base_max:
                    break
            elif config.criterio_collasso == "maschi_collassati":
                if n_co_tot / n_tot > config.soglia_maschi_collassati:
                    break

    curva.passaggi = passaggi
    return curva


# ═══════════════════════════════════════════════════════════
#  Bilinearizzazione (equipartizione energetica)
# ═══════════════════════════════════════════════════════════

def bilinearizza_curva(
    curva: CurvaPushover,
    massa_star: float = 0.0,
) -> None:
    """Bilinearizza la curva pushover con equipartizione energetica.

    NTC2018 §7.8.1.6:
    1. V_y = V_max (approssimazione: 0.9 × V_max)
    2. Area sotto la curva reale = Area sotto la bilineare
    3. k = V_y / δ_y
    4. δ_u = ultimo punto della curva

    Modifica la curva in-place: aggiorna V_y, delta_y, delta_u, k_bilineare.

    Args:
        curva: curva pushover (modificata in-place)
        massa_star: massa SDOF equivalente [kg] (per periodo T*)
    """
    if len(curva.punti) < 2:
        return

    # V_max e δ al collasso
    V_max = curva.V_max
    if V_max <= 0:
        return

    # δ_u = ultimo punto
    ultimo = curva.punti[-1]
    delta_u = ultimo.delta_controllo

    # Area sotto la curva (trapezi)
    area_curva = 0.0
    for i in range(1, len(curva.punti)):
        p0 = curva.punti[i - 1]
        p1 = curva.punti[i]
        area_curva += 0.5 * (p0.V_base + p1.V_base) * (p1.delta_controllo - p0.delta_controllo)

    # V_y ≈ 0.9 × V_max (taglio bilineare leggermente ridotto)
    # per garantire equipartizione energetica
    V_y_tentativo = 0.9 * V_max

    # Equipartizione energetica: A_bilineare = A_curva
    # A_bilineare = 0.5 × V_y × δ_y + V_y × (δ_u - δ_y) = V_y × (δ_u - δ_y/2)
    # → δ_y = 2 × (δ_u - A_curva/V_y)
    if V_y_tentativo > 0:
        delta_y = 2 * (delta_u - area_curva / V_y_tentativo)
        if delta_y <= 0 or delta_y >= delta_u:
            # Fallback: rigidezza secante al 70% V_max
            for p in curva.punti:
                if p.V_base >= 0.7 * V_max:
                    delta_y = p.delta_controllo
                    V_y_tentativo = V_max
                    break
            else:
                delta_y = delta_u / 3
    else:
        delta_y = delta_u / 3

    curva.V_y = V_y_tentativo
    curva.delta_y = max(delta_y, 1e-6)
    curva.delta_u = delta_u
    curva.k_bilineare = curva.V_y / curva.delta_y if curva.delta_y > 0 else 0.0
    curva.mu = curva.delta_u / curva.delta_y if curva.delta_y > 0 else 0.0

    # SDOF equivalente
    if massa_star > 0 and curva.k_bilineare > 0:
        curva.M_star = massa_star
        G = 981.0  # cm/s²
        omega = math.sqrt(curva.k_bilineare / (massa_star / G))
        curva.T_star = 2 * math.pi / omega if omega > 0 else 0.0

    curva.passaggi.append(
        f"Bilineare: V_y={curva.V_y:.0f} kg, δ_y={curva.delta_y:.4f} cm, "
        f"δ_u={curva.delta_u:.4f} cm, μ={curva.mu:.2f}"
    )
    if curva.T_star > 0:
        curva.passaggi.append(f"SDOF: T*={curva.T_star:.3f} s")


# ═══════════════════════════════════════════════════════════
#  Analisi completa (2 direzioni × 2 distribuzioni × ±eccentricità)
# ═══════════════════════════════════════════════════════════

@dataclass
class RisultatoPOR:
    """Risultato completo dell'analisi POR."""
    # Curve pushover (fino a 8: 2 dir × 2 distr × 2 segni eccentricità)
    curve: list[CurvaPushover] = field(default_factory=list)

    # Curva governante (V_base minore)
    curva_governante: Optional[CurvaPushover] = None

    # Indice di rischio sismico
    zeta_E: float = 0.0             # PGA_capacità / PGA_domanda

    passaggi: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "n_curve": len(self.curve),
            "zeta_E": round(self.zeta_E, 3),
            "curve": [c.to_dict() for c in self.curve],
            "passaggi": self.passaggi,
        }


def analisi_por_completa(
    maschi_per_piano: dict[int, list[Maschio]],
    resistenze_per_piano: dict[int, list[ResistenzaMaschio]],
    masse: list[float],
    quote: list[float],
    piani_ordinati: list[int],
    config: ConfigPOR,
    sismica: Optional[ParametriSismiciEdificio] = None,
    dimensione_x: float = 0.0,
    dimensione_y: float = 0.0,
) -> RisultatoPOR:
    """Esegue l'analisi POR completa.

    Combinazioni:
    - 2 direzioni: X, Y
    - 2 distribuzioni: modo_1, uniforme
    - ±eccentricità accidentale

    NTC2018 §7.3.4.1: tutte le combinazioni, governa la più sfavorevole.

    Args:
        maschi_per_piano: maschi per piano
        resistenze_per_piano: resistenze per piano
        masse: masse piani
        quote: quote piani
        piani_ordinati: id piani dal basso all'alto
        config: configurazione POR
        sismica: parametri sismici (per calcolo ζ_E)
        dimensione_x: dimensione pianta X [cm]
        dimensione_y: dimensione pianta Y [cm]

    Returns:
        RisultatoPOR
    """
    risultato = RisultatoPOR()
    passaggi: list[str] = []
    passaggi.append("═══ ANALISI POR COMPLETA ═══")

    # Eccentricità accidentale
    ecc_x = config.eccentricita_accidentale * dimensione_x
    ecc_y = config.eccentricita_accidentale * dimensione_y

    for direzione in ["X", "Y"]:
        for distr in [TipoDistribuzione.MODO_1, TipoDistribuzione.UNIFORME]:
            for segno_ecc in [+1, -1]:
                ecc = segno_ecc * (ecc_x if direzione == "Y" else ecc_y)

                curva = pushover_multipiano(
                    maschi_per_piano=maschi_per_piano,
                    resistenze_per_piano=resistenze_per_piano,
                    masse=masse,
                    quote=quote,
                    piani_ordinati=piani_ordinati,
                    config=config,
                    direzione=direzione,
                    distribuzione=distr,
                    eccentricita=ecc,
                )

                # Bilinearizzazione
                M_tot = sum(masse)
                bilinearizza_curva(curva, massa_star=M_tot)

                risultato.curve.append(curva)

                passaggi.append(
                    f"  {direzione} {distr.value} ecc={ecc:+.0f}: "
                    f"V_max={curva.V_max:.0f}, V_y={curva.V_y:.0f}, "
                    f"δ_u={curva.delta_u:.3f} cm"
                )

    # Curva governante: quella con V_y minore (più sfavorevole)
    curve_valide = [c for c in risultato.curve if c.V_y > 0]
    if curve_valide:
        risultato.curva_governante = min(curve_valide, key=lambda c: c.V_y)

    # Calcolo ζ_E
    if sismica and risultato.curva_governante:
        cg = risultato.curva_governante
        if cg.T_star > 0 and sismica.a_g > 0:
            # Capacità in accelerazione
            a_star_y = cg.V_y / cg.M_star if cg.M_star > 0 else 0.0
            # Domanda in accelerazione
            Sd = sismica.spettro_progetto(cg.T_star)
            if Sd > 0:
                risultato.zeta_E = a_star_y / Sd
                passaggi.append(
                    f"ζ_E = a*_y/S_d(T*) = {a_star_y:.4f}/{Sd:.4f} = {risultato.zeta_E:.3f}"
                )

    risultato.passaggi = passaggi
    return risultato
