"""Rigidezza maschi e fasce + assemblaggio matrice globale 3 GDL/piano.

Modello a telaio equivalente:
- Ogni maschio è un elemento trave Timoshenko (flessione + taglio)
- Ogni fascia è un elemento trave (deformabile o biella)
- 3 GDL per piano: ux, uy, θz (traslazione X, traslazione Y, rotazione)

Rigidezza maschio (doppio incastro):
    k = 1 / (h³/(12·E·I) + χ·h/(G·A))

Rigidezza maschio (incastro-cerniera):
    k = 1 / (h³/(3·E·I) + χ·h/(G·A))

con χ = 1.2 (fattore forma taglio sezione rettangolare).

Unità: cm, kg, kg/cm².

Riferimenti:
- Magenes & Calvi (1997): rigidezza maschi murari
- NTC2018 §7.8.1.5: modellazione strutturale
- Lagomarsino et al. (2013): modello a telaio equivalente TREMURI
"""

from __future__ import annotations

from dataclasses import dataclass, field

from src.methods.muratura.discretizzazione import (
    Fascia,
    Maschio,
    TipoVincolo,
    _direzione_maschio,
)

# Fattore forma taglio per sezione rettangolare
CHI_RETTANGOLARE = 1.2


# ═══════════════════════════════════════════════════════════
#  Rigidezza maschio
# ═══════════════════════════════════════════════════════════

def rigidezza_maschio(maschio: Maschio) -> float:
    """Calcola la rigidezza laterale di un maschio murario [kg/cm].

    Modello trave Timoshenko:
    - Doppio incastro: k = 1 / (h³/(12EI) + χh/(GA))
    - Incastro-cerniera: k = 1 / (h³/(3EI) + χh/(GA))
    - Mensola: k = 1 / (h³/(3EI) + χh/(GA))  (come incastro-cerniera)

    Args:
        maschio: elemento maschio con geometria e materiale

    Returns:
        Rigidezza laterale k [kg/cm]
    """
    if maschio.materiale is None:
        return 0.0

    E = maschio.materiale.E
    G = maschio.materiale.G
    h = maschio.h
    I = maschio.I_x
    A = maschio.area

    if h <= 0 or I <= 0 or A <= 0 or E <= 0:
        return 0.0

    # Flessibilità per taglio (sempre presente)
    if G > 0:
        flex_taglio = CHI_RETTANGOLARE * h / (G * A)
    else:
        # Se G non fornito, stima G = 0.4 × E
        G_stimato = 0.4 * E
        flex_taglio = CHI_RETTANGOLARE * h / (G_stimato * A)

    # Flessibilità per flessione (dipende dal vincolo)
    if maschio.vincolo == TipoVincolo.INCASTRO:
        flex_flessione = h ** 3 / (12 * E * I)
    else:
        # Cerniera o mensola
        flex_flessione = h ** 3 / (3 * E * I)

    flex_totale = flex_flessione + flex_taglio
    return 1.0 / flex_totale if flex_totale > 0 else 0.0


def rigidezza_fascia(fascia: Fascia) -> float:
    """Calcola la rigidezza laterale di una fascia [kg/cm].

    Se la fascia è biella (senza cordolo), la rigidezza è solo assiale
    e viene trattata come collegamento di compressione.

    Se ha cordolo, agisce come trave con rigidezza a taglio.

    Args:
        fascia: elemento fascia con geometria e materiale

    Returns:
        Rigidezza k [kg/cm]
    """
    if fascia.materiale is None:
        return 0.0

    if fascia.e_biella:
        # Biella: rigidezza assiale ridotta
        # k_assiale = E × A / L (ma utile solo in compressione)
        E = fascia.materiale.E
        A = fascia.area
        L = fascia.L
        if L > 0 and E > 0:
            return E * A / L * 0.1  # riduzione per biella (contributo limitato)
        return 0.0

    # Fascia con cordolo: trave doppiamente incastrata
    E = fascia.materiale.E
    G = fascia.materiale.G if fascia.materiale.G > 0 else 0.4 * fascia.materiale.E
    h = fascia.h
    I = fascia.I_x
    A = fascia.area
    L = fascia.L  # la "luce" della fascia è la larghezza dell'apertura

    if L <= 0 or I <= 0 or A <= 0 or E <= 0:
        return 0.0

    flex_flessione = L ** 3 / (12 * E * I)
    flex_taglio = CHI_RETTANGOLARE * L / (G * A)

    flex_totale = flex_flessione + flex_taglio
    return 1.0 / flex_totale if flex_totale > 0 else 0.0


# ═══════════════════════════════════════════════════════════
#  Centro di rigidezza e massa
# ═══════════════════════════════════════════════════════════

@dataclass
class CentroRigidezzaPiano:
    """Centro di rigidezza di un piano."""
    x_CR: float = 0.0           # coordinata x centro rigidezza [cm]
    y_CR: float = 0.0           # coordinata y centro rigidezza [cm]
    K_x: float = 0.0            # rigidezza totale direzione X [kg/cm]
    K_y: float = 0.0            # rigidezza totale direzione Y [kg/cm]
    K_theta: float = 0.0        # rigidezza torsionale [kg·cm/rad]

    # Centro massa
    x_CM: float = 0.0           # coordinata x centro massa [cm]
    y_CM: float = 0.0           # coordinata y centro massa [cm]

    # Eccentricità
    ex: float = 0.0             # eccentricità in X [cm]
    ey: float = 0.0             # eccentricità in Y [cm]

    passaggi: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "x_CR": round(self.x_CR, 1),
            "y_CR": round(self.y_CR, 1),
            "K_x": round(self.K_x, 1),
            "K_y": round(self.K_y, 1),
            "K_theta": round(self.K_theta, 0),
            "x_CM": round(self.x_CM, 1),
            "y_CM": round(self.y_CM, 1),
            "ex": round(self.ex, 1),
            "ey": round(self.ey, 1),
        }


def calcola_centro_rigidezza(
    maschi: list[Maschio],
    x_CM: float = 0.0,
    y_CM: float = 0.0,
) -> CentroRigidezzaPiano:
    """Calcola centro di rigidezza e rigidezza torsionale di un piano.

    Centro di rigidezza:
    x_CR = Σ(k_yi × x_i) / Σ(k_yi)
    y_CR = Σ(k_xi × y_i) / Σ(k_xi)

    dove k_xi = rigidezza del maschio in direzione X (pareti in dir. X)
         k_yi = rigidezza del maschio in direzione Y (pareti in dir. Y)

    Rigidezza torsionale:
    K_θ = Σ(k_xi × (y_i - y_CR)²) + Σ(k_yi × (x_i - x_CR)²)

    Args:
        maschi: lista maschi del piano con rigidezza calcolata
        x_CM: coordinata x centro massa
        y_CM: coordinata y centro massa

    Returns:
        CentroRigidezzaPiano
    """
    passaggi: list[str] = []

    # Separa maschi per direzione
    maschi_x = [m for m in maschi if _direzione_maschio(m) == "X"]
    maschi_y = [m for m in maschi if _direzione_maschio(m) == "Y"]

    # Rigidezze individuali
    k_vals_x: list[tuple[float, float, float]] = []  # (k, x, y) per maschi X
    k_vals_y: list[tuple[float, float, float]] = []  # (k, x, y) per maschi Y

    for m in maschi_x:
        k = rigidezza_maschio(m)
        k_vals_x.append((k, m.x_baricentro, m.y_baricentro))

    for m in maschi_y:
        k = rigidezza_maschio(m)
        k_vals_y.append((k, m.x_baricentro, m.y_baricentro))

    # Rigidezza totale per direzione
    K_x = sum(k for k, _, _ in k_vals_x)  # maschi in X resistono in X
    K_y = sum(k for k, _, _ in k_vals_y)  # maschi in Y resistono in Y

    passaggi.append(f"K_x = {K_x:.0f} kg/cm ({len(maschi_x)} maschi dir. X)")
    passaggi.append(f"K_y = {K_y:.0f} kg/cm ({len(maschi_y)} maschi dir. Y)")

    # Centro di rigidezza
    if K_y > 0:
        x_CR = sum(k * x for k, x, _ in k_vals_y) / K_y
    else:
        x_CR = x_CM

    if K_x > 0:
        y_CR = sum(k * y for k, _, y in k_vals_x) / K_x
    else:
        y_CR = y_CM

    passaggi.append(f"Centro rigidezza: ({x_CR:.1f}, {y_CR:.1f}) cm")

    # Rigidezza torsionale
    K_theta = 0.0
    for k, _, y in k_vals_x:
        K_theta += k * (y - y_CR) ** 2
    for k, x, _ in k_vals_y:
        K_theta += k * (x - x_CR) ** 2

    passaggi.append(f"K_θ = {K_theta:.0f} kg·cm/rad")

    # Eccentricità
    ex = x_CM - x_CR
    ey = y_CM - y_CR
    passaggi.append(f"Eccentricità: ex={ex:.1f} cm, ey={ey:.1f} cm")

    return CentroRigidezzaPiano(
        x_CR=x_CR, y_CR=y_CR,
        K_x=K_x, K_y=K_y, K_theta=K_theta,
        x_CM=x_CM, y_CM=y_CM,
        ex=ex, ey=ey,
        passaggi=passaggi,
    )


# ═══════════════════════════════════════════════════════════
#  Matrice rigidezza piano (3 GDL: ux, uy, θz)
# ═══════════════════════════════════════════════════════════

@dataclass
class MatriceRigidezzaPiano:
    """Matrice di rigidezza del piano condensata a 3 GDL."""
    # Matrice 3×3: [[Kxx, Kxy, Kxθ], [Kyx, Kyy, Kyθ], [Kθx, Kθy, Kθθ]]
    K: list[list[float]] = field(default_factory=lambda: [[0.0]*3 for _ in range(3)])

    # Contributi individuali (per debug e report)
    rigidezze_maschi: dict[int, float] = field(default_factory=dict)

    passaggi: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "K": [[round(v, 1) for v in row] for row in self.K],
            "rigidezze_maschi": {
                k: round(v, 1) for k, v in self.rigidezze_maschi.items()
            },
        }


def assembla_matrice_piano(
    maschi: list[Maschio],
    x_rif: float = 0.0,
    y_rif: float = 0.0,
) -> MatriceRigidezzaPiano:
    """Assembla la matrice di rigidezza 3×3 di un piano.

    Per diaframma rigido, 3 GDL: ux (traslazione X), uy (traslazione Y),
    θz (rotazione attorno ad asse Z).

    La matrice K è riferita al punto (x_rif, y_rif), tipicamente il
    centro di massa o di rigidezza.

    Contributo di ogni maschio:
    - Maschio in direzione X (parete lungo X): resiste a forze in X
      k_i contribuisce a Kxx + Kxθ + Kθθ
    - Maschio in direzione Y (parete lungo Y): resiste a forze in Y
      k_i contribuisce a Kyy + Kyθ + Kθθ

    K = Σ [k_i  0    -k_i·Δy_i]   (per maschi in X)
        [0    0     0          ]
        [-k_i·Δy_i  0  k_i·Δy_i²]

      + Σ [0    0     0          ]   (per maschi in Y)
          [0    k_j   k_j·Δx_j  ]
          [0    k_j·Δx_j  k_j·Δx_j²]

    dove Δx_j = x_j - x_rif, Δy_i = y_i - y_rif

    Args:
        maschi: lista maschi del piano
        x_rif: coordinata x punto di riferimento [cm]
        y_rif: coordinata y punto di riferimento [cm]

    Returns:
        MatriceRigidezzaPiano
    """
    passaggi: list[str] = []
    K = [[0.0, 0.0, 0.0],
         [0.0, 0.0, 0.0],
         [0.0, 0.0, 0.0]]

    rigidezze: dict[int, float] = {}

    for m in maschi:
        k = rigidezza_maschio(m)
        rigidezze[m.id_maschio] = k

        if k <= 0:
            continue

        dx = m.x_baricentro - x_rif
        dy = m.y_baricentro - y_rif
        direzione = _direzione_maschio(m)

        if direzione == "X":
            # Maschio in X: resiste a forze in X
            K[0][0] += k
            K[0][2] += -k * dy
            K[2][0] += -k * dy
            K[2][2] += k * dy ** 2
        else:
            # Maschio in Y: resiste a forze in Y
            K[1][1] += k
            K[1][2] += k * dx
            K[2][1] += k * dx
            K[2][2] += k * dx ** 2

        passaggi.append(
            f"  M{m.id_maschio} dir={direzione}: k={k:.0f} kg/cm, "
            f"Δx={dx:.0f}, Δy={dy:.0f}"
        )

    passaggi.append(f"K_piano = [[{K[0][0]:.0f}, {K[0][1]:.0f}, {K[0][2]:.0f}],")
    passaggi.append(f"           [{K[1][0]:.0f}, {K[1][1]:.0f}, {K[1][2]:.0f}],")
    passaggi.append(f"           [{K[2][0]:.0f}, {K[2][1]:.0f}, {K[2][2]:.0f}]]")

    return MatriceRigidezzaPiano(
        K=K,
        rigidezze_maschi=rigidezze,
        passaggi=passaggi,
    )


# ═══════════════════════════════════════════════════════════
#  Distribuzione forza su maschi (diaframma rigido)
# ═══════════════════════════════════════════════════════════

def distribuisci_forza_piano(
    maschi: list[Maschio],
    Fx: float = 0.0,
    Fy: float = 0.0,
    Mz: float = 0.0,
    x_rif: float = 0.0,
    y_rif: float = 0.0,
) -> dict[int, float]:
    """Distribuisce la forza orizzontale sui maschi del piano.

    Con diaframma rigido e 3 GDL (ux, uy, θz):
    1. Risolve K·u = F per ottenere (ux, uy, θz)
    2. Per ogni maschio: V_i = k_i × (u_dir + θz × braccio_i)

    Se una direzione non ha maschi (es. Kxx=0), il sistema viene
    ridotto ai GDL attivi per evitare singolarità.

    Args:
        maschi: lista maschi del piano
        Fx: forza orizzontale in X [kg]
        Fy: forza orizzontale in Y [kg]
        Mz: momento torcente (da eccentricità) [kg·cm]
        x_rif: coordinata x punto di riferimento
        y_rif: coordinata y punto di riferimento

    Returns:
        {id_maschio: V_i} taglio su ogni maschio [kg]
    """
    if not maschi:
        return {}

    mat = assembla_matrice_piano(maschi, x_rif, y_rif)
    K = mat.K

    # Vettore forze
    F = [Fx, Fy, Mz]

    # Identifica GDL attivi (diagonale K > 0)
    gdl_attivi = [i for i in range(3) if K[i][i] > 1e-12]

    if not gdl_attivi:
        return {m.id_maschio: 0.0 for m in maschi}

    # Risolve sistema ridotto ai soli GDL attivi
    u = [0.0, 0.0, 0.0]

    if len(gdl_attivi) == 3:
        u_sol = _risolvi_3x3(K, F)
        if u_sol is not None:
            u = u_sol
        else:
            return _distribuzione_proporzionale(maschi, Fx, Fy)
    else:
        # Riduci sistema ai GDL attivi
        n = len(gdl_attivi)
        K_rid = [[K[i][j] for j in gdl_attivi] for i in gdl_attivi]
        F_rid = [F[i] for i in gdl_attivi]

        if n == 1:
            if abs(K_rid[0][0]) > 1e-12:
                u[gdl_attivi[0]] = F_rid[0] / K_rid[0][0]
        elif n == 2:
            u_sol = _risolvi_2x2(K_rid, F_rid)
            if u_sol is not None:
                for idx, gi in enumerate(gdl_attivi):
                    u[gi] = u_sol[idx]
            else:
                return _distribuzione_proporzionale(maschi, Fx, Fy)

    ux, uy, theta_z = u

    # Taglio su ogni maschio
    tagli: dict[int, float] = {}
    for m in maschi:
        k = rigidezza_maschio(m)
        if k <= 0:
            tagli[m.id_maschio] = 0.0
            continue

        dx = m.x_baricentro - x_rif
        dy = m.y_baricentro - y_rif
        direzione = _direzione_maschio(m)

        if direzione == "X":
            # Spostamento locale del maschio in X
            delta_locale = ux - theta_z * dy
            tagli[m.id_maschio] = k * delta_locale
        else:
            # Spostamento locale del maschio in Y
            delta_locale = uy + theta_z * dx
            tagli[m.id_maschio] = k * delta_locale

    return tagli


def _risolvi_3x3(
    K: list[list[float]],
    F: list[float],
) -> list[float] | None:
    """Risolve sistema 3×3 K·u = F con eliminazione di Gauss.

    Returns:
        [ux, uy, θz] oppure None se singolare
    """
    # Copia per non modificare l'originale
    A = [row[:] + [F[i]] for i, row in enumerate(K)]
    n = 3

    for col in range(n):
        # Pivoting parziale
        max_row = col
        max_val = abs(A[col][col])
        for row in range(col + 1, n):
            if abs(A[row][col]) > max_val:
                max_val = abs(A[row][col])
                max_row = row
        if max_val < 1e-12:
            return None
        A[col], A[max_row] = A[max_row], A[col]

        # Eliminazione
        for row in range(col + 1, n):
            factor = A[row][col] / A[col][col]
            for j in range(col, n + 1):
                A[row][j] -= factor * A[col][j]

    # Sostituzione all'indietro
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        s = A[i][n]
        for j in range(i + 1, n):
            s -= A[i][j] * x[j]
        x[i] = s / A[i][i] if abs(A[i][i]) > 1e-12 else 0.0

    return x


def _risolvi_2x2(
    K: list[list[float]],
    F: list[float],
) -> list[float] | None:
    """Risolve sistema 2×2 K·u = F."""
    det = K[0][0] * K[1][1] - K[0][1] * K[1][0]
    if abs(det) < 1e-12:
        return None
    u0 = (K[1][1] * F[0] - K[0][1] * F[1]) / det
    u1 = (K[0][0] * F[1] - K[1][0] * F[0]) / det
    return [u0, u1]


def _distribuzione_proporzionale(
    maschi: list[Maschio],
    Fx: float,
    Fy: float,
) -> dict[int, float]:
    """Distribuzione proporzionale alla rigidezza (fallback).

    Usata quando la matrice 3×3 è singolare (es. tutti maschi in una sola direzione).
    """
    tagli: dict[int, float] = {}

    maschi_x = [(m, rigidezza_maschio(m)) for m in maschi if _direzione_maschio(m) == "X"]
    maschi_y = [(m, rigidezza_maschio(m)) for m in maschi if _direzione_maschio(m) == "Y"]

    K_tot_x = sum(k for _, k in maschi_x)
    K_tot_y = sum(k for _, k in maschi_y)

    for m, k in maschi_x:
        if K_tot_x > 0:
            tagli[m.id_maschio] = Fx * k / K_tot_x
        else:
            tagli[m.id_maschio] = 0.0

    for m, k in maschi_y:
        if K_tot_y > 0:
            tagli[m.id_maschio] = Fy * k / K_tot_y
        else:
            tagli[m.id_maschio] = 0.0

    return tagli
