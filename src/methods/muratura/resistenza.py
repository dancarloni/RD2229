"""Resistenza maschi e fasce — curva bilineare per pushover.

Per ogni maschio/fascia calcola:
1. Resistenza a taglio V_Rd (minimo tra i 3 criteri di E.2)
2. Criterio di rottura dominante (determina il drift limite)
3. Curva bilineare: rigidezza elastica → plateau V_Rd → collasso a drift limite

Integrazione con moduli esistenti:
- ``verifiche.py`` (E.2): taglio_diagonale, taglio_scorrimento, taglio_pressoflessione
- ``cordolo.py`` (E.5): per determinare la resistenza delle fasce con cordolo

Unità: cm, kg, kg/cm².

Riferimenti:
- NTC2018 §7.8.2.2 — Resistenza pannelli murari
- NTC2018 §7.8.2.2.4 — Resistenza fasce
- Circolare n.7/2019 §C8.7.1.3.1.1 — Parametri meccanici muratura esistente
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from src.methods.muratura.discretizzazione import (
    Fascia,
    Maschio,
    TipoVincolo,
)
from src.methods.muratura.rigidezza import rigidezza_fascia, rigidezza_maschio
from src.methods.muratura.verifiche import (
    InputTaglio,
    taglio_diagonale,
    taglio_pressoflessione,
    taglio_scorrimento,
)

# ═══════════════════════════════════════════════════════════
#  Stato maschio nella pushover
# ═══════════════════════════════════════════════════════════

class StatoMaschio(str, Enum):
    """Stato dell'elemento nella curva pushover."""
    ELASTICO = "elastico"           # δ < δ_y
    PLASTICO = "plastico"           # δ_y ≤ δ < δ_u
    COLLASSATO = "collassato"       # δ ≥ δ_u


# ═══════════════════════════════════════════════════════════
#  Risultato resistenza maschio
# ═══════════════════════════════════════════════════════════

@dataclass
class ResistenzaMaschio:
    """Resistenza e curva bilineare di un maschio."""
    id_maschio: int = 0

    # Resistenza a taglio (minimo dei 3 criteri)
    V_Rd: float = 0.0               # resistenza a taglio di progetto [kg]
    criterio_dominante: str = ""     # "diagonale", "scorrimento", "pressoflessione"

    # Rigidezza e curve bilineare
    k_elastico: float = 0.0         # rigidezza elastica [kg/cm]
    delta_y: float = 0.0            # spostamento a snervamento [cm]
    delta_u: float = 0.0            # spostamento ultimo (collasso) [cm]
    drift_limite: float = 0.0       # drift limite dominante

    # Dettaglio criteri
    V_Rd_diagonale: float = 0.0
    V_Rd_scorrimento: float = 0.0
    V_Rd_pressoflessione: float = 0.0

    passaggi: list[str] = field(default_factory=list)

    def forza_per_spostamento(self, delta: float) -> float:
        """Forza sulla curva bilineare per un dato spostamento.

        - δ < 0: forza negativa (simmetria)
        - 0 ≤ δ ≤ δ_y: tratto elastico V = k × δ
        - δ_y < δ ≤ δ_u: plateau V = V_Rd
        - δ > δ_u: collasso V = 0

        Args:
            delta: spostamento [cm]

        Returns:
            Forza V [kg]
        """
        segno = 1.0 if delta >= 0 else -1.0
        d = abs(delta)

        if d <= self.delta_y:
            return segno * self.k_elastico * d
        elif d <= self.delta_u:
            return segno * self.V_Rd
        else:
            return 0.0

    def stato_per_spostamento(self, delta: float) -> StatoMaschio:
        """Stato del maschio per un dato spostamento."""
        d = abs(delta)
        if d <= self.delta_y:
            return StatoMaschio.ELASTICO
        elif d <= self.delta_u:
            return StatoMaschio.PLASTICO
        else:
            return StatoMaschio.COLLASSATO

    def to_dict(self) -> dict:
        return {
            "id_maschio": self.id_maschio,
            "V_Rd": round(self.V_Rd, 1),
            "criterio_dominante": self.criterio_dominante,
            "k_elastico": round(self.k_elastico, 1),
            "delta_y": round(self.delta_y, 4),
            "delta_u": round(self.delta_u, 4),
            "drift_limite": round(self.drift_limite, 4),
            "V_Rd_diagonale": round(self.V_Rd_diagonale, 1),
            "V_Rd_scorrimento": round(self.V_Rd_scorrimento, 1),
            "V_Rd_pressoflessione": round(self.V_Rd_pressoflessione, 1),
        }


# ═══════════════════════════════════════════════════════════
#  Calcolo resistenza maschio
# ═══════════════════════════════════════════════════════════

def calcola_resistenza_maschio(maschio: Maschio) -> ResistenzaMaschio:
    """Calcola la resistenza a taglio e la curva bilineare di un maschio.

    Procedura:
    1. Calcola V_Rd per ogni criterio (diagonale, scorrimento, pressoflessione)
       riutilizzando le funzioni di ``verifiche.py`` (E.2)
    2. V_Rd = min(V_Rd_diag, V_Rd_scorr, V_Rd_pflex)
    3. Il criterio dominante determina il drift limite
    4. δ_y = V_Rd / k, δ_u = drift_limite × h

    Args:
        maschio: elemento maschio con geometria, materiale e N

    Returns:
        ResistenzaMaschio
    """
    passaggi: list[str] = []
    res = ResistenzaMaschio(id_maschio=maschio.id_maschio)

    if maschio.materiale is None:
        passaggi.append(f"Maschio {maschio.id_maschio}: nessun materiale → V_Rd = 0")
        res.passaggi = passaggi
        return res

    mat = maschio.materiale

    # ψ per altezza di taglio: 1.0 per doppio incastro (h₀=h), 0.5 per cerniera
    if maschio.vincolo == TipoVincolo.INCASTRO:
        psi = 1.0  # h₀ = h (doppio incastro: punto di flesso a metà)
    else:
        psi = 0.5  # mensola: h₀ = h/2 (no, per mensola h₀=h e taglio = M_base/h)
        # In realtà per incastro-cerniera, la luce di taglio è h
        psi = 1.0

    # Coefficiente b per distribuzione tensioni tangenziali
    h_L = maschio.h / maschio.L if maschio.L > 0 else 1.0
    b_coeff = max(1.0, min(h_L, 1.5))

    # Input comune per le funzioni di verifica E.2
    inp = InputTaglio(
        L=maschio.L,
        t=maschio.t,
        h=maschio.h,
        V=0.0,  # non verifichiamo, calcoliamo solo V_Rd
        N=maschio.N_gravitazionale,
        tau_0=mat.tau_0d * mat.gamma_M * mat.FC,  # riscala perché la funzione divide per γ_M
        fd=mat.fd * mat.gamma_M * mat.FC,          # idem
        fvk0=mat.fvk0d * mat.gamma_M * mat.FC,    # idem
        mu=mat.mu,
        gamma_M=mat.gamma_M,
        b_coeff=b_coeff,
        psi=psi,
    )

    passaggi.append(
        f"Maschio {maschio.id_maschio}: L={maschio.L:.0f}, t={maschio.t:.0f}, "
        f"h={maschio.h:.0f} cm, N={maschio.N_gravitazionale:.0f} kg"
    )

    # Criterio 1: Taglio diagonale (Turnšek-Čačovič)
    V_Rd_diag = 0.0
    if mat.tau_0 > 0:
        ris_diag = taglio_diagonale(inp)
        V_Rd_diag = ris_diag.V_Rd
        res.V_Rd_diagonale = V_Rd_diag
        passaggi.append(f"  Diagonale: V_Rd = {V_Rd_diag:.0f} kg")

    # Criterio 2: Scorrimento (Mohr-Coulomb)
    V_Rd_scorr = 0.0
    if mat.fvk0 > 0:
        ris_scorr = taglio_scorrimento(inp)
        V_Rd_scorr = ris_scorr.V_Rd
        res.V_Rd_scorrimento = V_Rd_scorr
        passaggi.append(f"  Scorrimento: V_Rd = {V_Rd_scorr:.0f} kg")

    # Criterio 3: Pressoflessione
    V_Rd_pflex = 0.0
    if mat.f > 0 and maschio.N_gravitazionale > 0:
        ris_pflex = taglio_pressoflessione(inp)
        V_Rd_pflex = ris_pflex.V_Rd
        res.V_Rd_pressoflessione = V_Rd_pflex
        passaggi.append(f"  Pressoflessione: V_Rd = {V_Rd_pflex:.0f} kg")

    # V_Rd = minimo tra i criteri calcolati
    criteri = {}
    if V_Rd_diag > 0:
        criteri["diagonale"] = V_Rd_diag
    if V_Rd_scorr > 0:
        criteri["scorrimento"] = V_Rd_scorr
    if V_Rd_pflex > 0:
        criteri["pressoflessione"] = V_Rd_pflex

    if not criteri:
        passaggi.append("  Nessun criterio applicabile → V_Rd = 0")
        res.passaggi = passaggi
        return res

    criterio_min = min(criteri, key=criteri.get)
    res.V_Rd = criteri[criterio_min]
    res.criterio_dominante = criterio_min

    passaggi.append(
        f"  → V_Rd = {res.V_Rd:.0f} kg (criterio: {criterio_min})"
    )

    # Drift limite in base al criterio dominante
    if criterio_min == "pressoflessione":
        res.drift_limite = maschio.drift_pressoflessione
    else:
        res.drift_limite = maschio.drift_taglio

    # Curva bilineare
    k = rigidezza_maschio(maschio)
    res.k_elastico = k

    if k > 0:
        res.delta_y = res.V_Rd / k
    else:
        res.delta_y = 0.0

    res.delta_u = res.drift_limite * maschio.h

    passaggi.append(
        f"  k = {k:.0f} kg/cm, δ_y = {res.delta_y:.4f} cm, "
        f"δ_u = {res.delta_u:.4f} cm (drift {res.drift_limite:.1%})"
    )

    res.passaggi = passaggi
    return res


# ═══════════════════════════════════════════════════════════
#  Resistenza fascia
# ═══════════════════════════════════════════════════════════

@dataclass
class ResistenzaFascia:
    """Resistenza e curva bilineare di una fascia."""
    id_fascia: int = 0
    V_Rd: float = 0.0
    M_Rd: float = 0.0               # momento resistente (se con cordolo) [kg·cm]
    k_elastico: float = 0.0
    delta_y: float = 0.0
    delta_u: float = 0.0
    e_biella: bool = False

    passaggi: list[str] = field(default_factory=list)

    def forza_per_spostamento(self, delta: float) -> float:
        """Forza sulla curva bilineare."""
        segno = 1.0 if delta >= 0 else -1.0
        d = abs(delta)
        if d <= self.delta_y:
            return segno * self.k_elastico * d
        elif d <= self.delta_u:
            return segno * self.V_Rd
        else:
            return 0.0

    def to_dict(self) -> dict:
        return {
            "id_fascia": self.id_fascia,
            "V_Rd": round(self.V_Rd, 1),
            "M_Rd": round(self.M_Rd, 1),
            "k_elastico": round(self.k_elastico, 1),
            "e_biella": self.e_biella,
        }


def calcola_resistenza_fascia(fascia: Fascia) -> ResistenzaFascia:
    """Calcola la resistenza di una fascia.

    NTC2018 §7.8.2.2.4:
    - Fascia senza cordolo (biella): V_Rd basato solo su compressione
      V_Rd = h × t × fhd / 2  (resistenza a taglio limitata)
    - Fascia con cordolo: V_Rd dipende dal momento resistente del cordolo
      e dal taglio per equilibrio

    Args:
        fascia: elemento fascia

    Returns:
        ResistenzaFascia
    """
    passaggi: list[str] = []
    res = ResistenzaFascia(id_fascia=fascia.id_fascia)

    if fascia.materiale is None:
        res.passaggi = passaggi
        return res

    mat = fascia.materiale
    k = rigidezza_fascia(fascia)
    res.k_elastico = k
    res.e_biella = fascia.e_biella

    if fascia.e_biella:
        # Fascia biella (senza cordolo): resistenza limitata
        # V_Rd ≈ 0.5 × h × t × fhd (taglio per sola compressione)
        fhd = mat.fd
        V_Rd = 0.5 * fascia.h * fascia.t * fhd if fhd > 0 else 0.0
        res.V_Rd = V_Rd
        passaggi.append(
            f"Fascia {fascia.id_fascia} (biella): "
            f"V_Rd = 0.5×h×t×fhd = 0.5×{fascia.h:.0f}×{fascia.t:.0f}×{fhd:.1f} "
            f"= {V_Rd:.0f} kg"
        )
    else:
        # Fascia con cordolo: resistenza a pressoflessione
        # M_Rd ≈ h_p × t × fhd × L / 4 (semplificazione)
        # dove h_p = min(h_fascia, spessore fascia) zona compressa
        fhd = mat.fd
        h_p = min(fascia.h, fascia.t) / 2  # altezza zona compressa stimata
        M_Rd = h_p * fascia.t * fhd * fascia.h / 4 if fhd > 0 else 0.0
        V_Rd = 2 * M_Rd / fascia.L if fascia.L > 0 else 0.0

        res.M_Rd = M_Rd
        res.V_Rd = V_Rd
        passaggi.append(
            f"Fascia {fascia.id_fascia} (con cordolo): "
            f"M_Rd = {M_Rd:.0f} kg·cm, V_Rd = 2M_Rd/L = {V_Rd:.0f} kg"
        )

    # Curva bilineare
    if k > 0 and res.V_Rd > 0:
        res.delta_y = res.V_Rd / k
    # Drift limite fasce: 0.6% (valore tipico)
    res.delta_u = 0.006 * fascia.L if fascia.L > 0 else 0.0

    res.passaggi = passaggi
    return res


# ═══════════════════════════════════════════════════════════
#  Calcolo resistenza tutti maschi di un piano
# ═══════════════════════════════════════════════════════════

def calcola_resistenze_piano(
    maschi: list[Maschio],
    fasce: list[Fascia],
) -> tuple[list[ResistenzaMaschio], list[ResistenzaFascia]]:
    """Calcola le resistenze di tutti i maschi e fasce di un piano.

    Returns:
        (resistenze_maschi, resistenze_fasce)
    """
    res_maschi = [calcola_resistenza_maschio(m) for m in maschi]
    res_fasce = [calcola_resistenza_fascia(f) for f in fasce]
    return res_maschi, res_fasce
