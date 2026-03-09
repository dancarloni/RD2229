"""Solutore traliccio piano 2D — metodo degli spostamenti (rigidezza diretta).

Risolve tralicci piani isostatici e iperstatici con il metodo della rigidezza.
Ogni asta ha solo sforzo assiale (2 gdl per nodo: ux, uy).

Unità: cm per geometria, kg per forze, kg/cm² per tensioni.

Riferimenti:
- Scienze delle costruzioni (Odone Belluzzi)
- Tecnica delle costruzioni (Pozzati/Ceccoli)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .sezione_asta import SezioneAsta


class TipoVincolo(str, Enum):
    """Tipo di vincolo nodale."""
    LIBERO = "libero"                  # nessun vincolo
    CERNIERA = "cerniera"              # bloccato ux, uy
    CARRELLO_X = "carrello_x"          # bloccato uy, libero ux
    CARRELLO_Y = "carrello_y"          # bloccato ux, libero uy


@dataclass
class Nodo:
    """Nodo del traliccio piano."""
    id: int
    x: float               # coordinata x [cm]
    y: float               # coordinata y [cm]
    vincolo: TipoVincolo = TipoVincolo.LIBERO
    Fx: float = 0.0        # forza esterna x [kg]
    Fy: float = 0.0        # forza esterna y [kg]


@dataclass
class Asta:
    """Asta del traliccio piano."""
    id: int
    nodo_i: int             # id nodo inizio
    nodo_j: int             # id nodo fine
    A: float                # area sezione [cm²]
    E: float = 2100000.0    # modulo elastico [kg/cm²] (acciaio default)
    nome_profilo: str = ""  # nome profilo (opzionale)

    @property
    def EA(self) -> float:
        return self.E * self.A


@dataclass
class RisultatoAsta:
    """Risultato per singola asta."""
    id_asta: int
    nome_profilo: str
    nodo_i: int
    nodo_j: int
    L: float                # lunghezza [cm]
    N: float                # sforzo normale [kg] (+ trazione, - compressione)
    sigma: float            # tensione σ = N/A [kg/cm²]
    allungamento: float     # ΔL [cm]


@dataclass
class RisultatoTraliccio:
    """Risultato completo dell'analisi del traliccio."""
    n_nodi: int
    n_aste: int
    n_gdl: int
    n_vincoli: int

    # Spostamenti nodali [cm]
    spostamenti: dict[int, tuple[float, float]]     # {id_nodo: (ux, uy)}

    # Reazioni vincolari [kg]
    reazioni: dict[int, tuple[float, float]]        # {id_nodo: (Rx, Ry)}

    # Risultati aste
    aste: list[RisultatoAsta]

    # Rigidezza globale e spostamento massimo (D.3.2)
    K_globale: float = 0.0   # F_tot_y / |uy_max| [kg/cm]
    delta_max: float = 0.0   # spostamento massimo in Y [cm]

    # Diagnostica
    passaggi: list[str] = field(default_factory=list)
    convergenza: bool = True
    errore: str = ""

    def to_dict(self) -> dict:
        return {
            "n_nodi": self.n_nodi,
            "n_aste": self.n_aste,
            "n_gdl": self.n_gdl,
            "n_vincoli": self.n_vincoli,
            "spostamenti": {
                str(k): {"ux": v[0], "uy": v[1]}
                for k, v in self.spostamenti.items()
            },
            "reazioni": {
                str(k): {"Rx": v[0], "Ry": v[1]}
                for k, v in self.reazioni.items()
            },
            "aste": [
                {
                    "id": a.id_asta,
                    "nome_profilo": a.nome_profilo,
                    "L": round(a.L, 2),
                    "N": round(a.N, 2),
                    "sigma": round(a.sigma, 2),
                    "allungamento": round(a.allungamento, 6),
                }
                for a in self.aste
            ],
            "convergenza": self.convergenza,
            "passaggi": self.passaggi,
        }


def _lunghezza(n1: Nodo, n2: Nodo) -> float:
    """Lunghezza asta tra due nodi."""
    return math.sqrt((n2.x - n1.x) ** 2 + (n2.y - n1.y) ** 2)


def _cos_sin(n1: Nodo, n2: Nodo) -> tuple[float, float]:
    """Coseno e seno dell'angolo dell'asta rispetto all'asse x."""
    L = _lunghezza(n1, n2)
    if L == 0:
        raise ValueError(f"Asta con lunghezza zero tra nodi {n1.id} e {n2.id}")
    return (n2.x - n1.x) / L, (n2.y - n1.y) / L


def _gdl_vincolati(nodo: Nodo) -> tuple[bool, bool]:
    """Ritorna (bloccato_x, bloccato_y) per un nodo."""
    if nodo.vincolo == TipoVincolo.CERNIERA:
        return True, True
    elif nodo.vincolo == TipoVincolo.CARRELLO_X:
        return False, True
    elif nodo.vincolo == TipoVincolo.CARRELLO_Y:
        return True, False
    return False, False


def risolvi_traliccio(
    nodi: list[Nodo],
    aste: list[Asta],
) -> RisultatoTraliccio:
    """Risolve traliccio piano con metodo della rigidezza diretta.

    Assembla la matrice di rigidezza globale K, applica vincoli e
    forze esterne, risolve K·u = F per gli spostamenti.

    Args:
        nodi: lista nodi del traliccio
        aste: lista aste del traliccio

    Returns:
        RisultatoTraliccio con spostamenti, reazioni e sforzi nelle aste
    """
    passaggi: list[str] = []

    # Mappa nodo_id → indice
    nodi_map = {n.id: n for n in nodi}
    nodo_ids = sorted(nodi_map.keys())
    nodo_idx = {nid: i for i, nid in enumerate(nodo_ids)}

    n_nodi = len(nodi)
    n_gdl = 2 * n_nodi
    n_aste = len(aste)

    passaggi.append(f"Traliccio: {n_nodi} nodi, {n_aste} aste, {n_gdl} gdl")

    # Conta vincoli
    n_vinc = 0
    for n in nodi:
        bx, by = _gdl_vincolati(n)
        n_vinc += int(bx) + int(by)

    gdl_liberi = n_gdl - n_vinc
    passaggi.append(f"Vincoli: {n_vinc} gdl vincolati, {gdl_liberi} gdl liberi")

    if gdl_liberi <= 0:
        return RisultatoTraliccio(
            n_nodi=n_nodi, n_aste=n_aste, n_gdl=n_gdl, n_vincoli=n_vinc,
            spostamenti={}, reazioni={}, aste=[],
            convergenza=False, errore="Struttura completamente vincolata",
            passaggi=passaggi,
        )

    # --- Assemblaggio matrice di rigidezza globale ---
    # Uso liste di liste per semplicità (tralicci piccoli)
    K = [[0.0] * n_gdl for _ in range(n_gdl)]
    F = [0.0] * n_gdl

    for asta in aste:
        ni = nodi_map[asta.nodo_i]
        nj = nodi_map[asta.nodo_j]
        L = _lunghezza(ni, nj)
        c, s = _cos_sin(ni, nj)

        if L == 0:
            passaggi.append(f"ERRORE: Asta {asta.id} ha lunghezza zero")
            continue

        k = asta.EA / L

        # Matrice rigidezza locale in coordinate globali (4x4)
        #   [c²  cs  -c² -cs ]
        # k*[cs  s²  -cs -s² ]
        #   [-c² -cs  c²  cs ]
        #   [-cs -s² cs   s² ]
        cc = c * c
        ss = s * s
        cs_val = c * s

        # Indici gdl globali
        i1 = 2 * nodo_idx[asta.nodo_i]      # ux_i
        i2 = i1 + 1                           # uy_i
        j1 = 2 * nodo_idx[asta.nodo_j]       # ux_j
        j2 = j1 + 1                           # uy_j

        # Assemblaggio
        indices = [i1, i2, j1, j2]
        ke = [
            [cc, cs_val, -cc, -cs_val],
            [cs_val, ss, -cs_val, -ss],
            [-cc, -cs_val, cc, cs_val],
            [-cs_val, -ss, cs_val, ss],
        ]

        for r in range(4):
            for col in range(4):
                K[indices[r]][indices[col]] += k * ke[r][col]

    # Vettore forze esterne
    for n in nodi:
        idx = nodo_idx[n.id]
        F[2 * idx] = n.Fx
        F[2 * idx + 1] = n.Fy

    passaggi.append("Matrice di rigidezza K assemblata")

    # --- Applicazione vincoli (metodo per eliminazione) ---
    # Identifico gdl liberi e vincolati
    gdl_liberi_list: list[int] = []
    gdl_vincolati_list: list[int] = []

    for n in nodi:
        idx = nodo_idx[n.id]
        bx, by = _gdl_vincolati(n)
        if bx:
            gdl_vincolati_list.append(2 * idx)
        else:
            gdl_liberi_list.append(2 * idx)
        if by:
            gdl_vincolati_list.append(2 * idx + 1)
        else:
            gdl_liberi_list.append(2 * idx + 1)

    # Estraggo sottomatrice per gdl liberi
    n_lib = len(gdl_liberi_list)
    K_red = [[0.0] * n_lib for _ in range(n_lib)]
    F_red = [0.0] * n_lib

    for r in range(n_lib):
        F_red[r] = F[gdl_liberi_list[r]]
        for col in range(n_lib):
            K_red[r][col] = K[gdl_liberi_list[r]][gdl_liberi_list[col]]

    # --- Risoluzione K_red · u_red = F_red (Gauss con pivoting parziale) ---
    u_red = _gauss_solve(K_red, F_red)

    if u_red is None:
        return RisultatoTraliccio(
            n_nodi=n_nodi, n_aste=n_aste, n_gdl=n_gdl, n_vincoli=n_vinc,
            spostamenti={}, reazioni={}, aste=[],
            convergenza=False, errore="Matrice singolare — struttura labile",
            passaggi=passaggi,
        )

    # Ricostruisco vettore spostamenti completo
    u = [0.0] * n_gdl
    for i, gdl in enumerate(gdl_liberi_list):
        u[gdl] = u_red[i]

    # Spostamenti nodali
    spostamenti: dict[int, tuple[float, float]] = {}
    for nid in nodo_ids:
        idx = nodo_idx[nid]
        spostamenti[nid] = (u[2 * idx], u[2 * idx + 1])

    # --- Calcolo sforzi nelle aste ---
    risultati_aste: list[RisultatoAsta] = []
    for asta in aste:
        ni = nodi_map[asta.nodo_i]
        nj = nodi_map[asta.nodo_j]
        L = _lunghezza(ni, nj)
        c, s = _cos_sin(ni, nj)

        idx_i = nodo_idx[asta.nodo_i]
        idx_j = nodo_idx[asta.nodo_j]

        ui_x = u[2 * idx_i]
        ui_y = u[2 * idx_i + 1]
        uj_x = u[2 * idx_j]
        uj_y = u[2 * idx_j + 1]

        # Allungamento: ΔL = (uj - ui) · versore asta
        delta_L = (uj_x - ui_x) * c + (uj_y - ui_y) * s

        # Sforzo normale: N = EA/L · ΔL (+ = trazione)
        N = asta.EA / L * delta_L
        sigma_asta = N / asta.A if asta.A > 0 else 0.0

        risultati_aste.append(RisultatoAsta(
            id_asta=asta.id,
            nome_profilo=asta.nome_profilo,
            nodo_i=asta.nodo_i,
            nodo_j=asta.nodo_j,
            L=L,
            N=N,
            sigma=sigma_asta,
            allungamento=delta_L,
        ))

        tipo = "trazione" if N > 0 else "compressione" if N < 0 else "scarica"
        passaggi.append(
            f"Asta {asta.id} ({ni.id}→{nj.id}): L={L:.1f} cm, "
            f"N={N:.1f} kg ({tipo}), σ={sigma_asta:.1f} kg/cm²"
        )

    # --- Reazioni vincolari: R = K·u - F ---
    reazioni: dict[int, tuple[float, float]] = {}
    for n in nodi:
        bx, by = _gdl_vincolati(n)
        if bx or by:
            idx = nodo_idx[n.id]
            Rx = 0.0
            Ry = 0.0
            if bx:
                for j in range(n_gdl):
                    Rx += K[2 * idx][j] * u[j]
                Rx -= F[2 * idx]
            if by:
                for j in range(n_gdl):
                    Ry += K[2 * idx + 1][j] * u[j]
                Ry -= F[2 * idx + 1]
            reazioni[n.id] = (Rx, Ry)
            passaggi.append(
                f"Reazione nodo {n.id}: Rx={Rx:.1f} kg, Ry={Ry:.1f} kg"
            )

    # Verifica equilibrio globale
    somma_Fx = sum(n.Fx for n in nodi) + sum(r[0] for r in reazioni.values())
    somma_Fy = sum(n.Fy for n in nodi) + sum(r[1] for r in reazioni.values())
    passaggi.append(
        f"Equilibrio globale: ΣFx={somma_Fx:.4f} kg, ΣFy={somma_Fy:.4f} kg"
    )

    # Rigidezza globale K_globale = F_tot_y / delta_max_y
    F_tot_y = sum(n.Fy for n in nodi)
    uy_vals = [abs(sp[1]) for sp in spostamenti.values()]
    delta_max = max(uy_vals) if uy_vals else 0.0
    K_globale = abs(F_tot_y) / delta_max if delta_max > 1e-12 else 0.0

    return RisultatoTraliccio(
        n_nodi=n_nodi,
        n_aste=n_aste,
        n_gdl=n_gdl,
        n_vincoli=n_vinc,
        spostamenti=spostamenti,
        reazioni=reazioni,
        aste=risultati_aste,
        K_globale=K_globale,
        delta_max=delta_max,
        convergenza=True,
        passaggi=passaggi,
    )


def _gauss_solve(A: list[list[float]], b: list[float]) -> list[float] | None:
    """Risolve sistema lineare Ax=b con eliminazione di Gauss e pivoting parziale.

    Ritorna None se la matrice è singolare.
    """
    n = len(b)
    # Copia matrici
    M = [row[:] for row in A]
    rhs = b[:]

    for col in range(n):
        # Pivoting parziale
        max_val = abs(M[col][col])
        max_row = col
        for row in range(col + 1, n):
            if abs(M[row][col]) > max_val:
                max_val = abs(M[row][col])
                max_row = row

        if max_val < 1e-12:
            return None  # matrice singolare

        if max_row != col:
            M[col], M[max_row] = M[max_row], M[col]
            rhs[col], rhs[max_row] = rhs[max_row], rhs[col]

        # Eliminazione
        pivot = M[col][col]
        for row in range(col + 1, n):
            factor = M[row][col] / pivot
            for j in range(col, n):
                M[row][j] -= factor * M[col][j]
            rhs[row] -= factor * rhs[col]

    # Sostituzione all'indietro
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        if abs(M[i][i]) < 1e-12:
            return None
        s = rhs[i]
        for j in range(i + 1, n):
            s -= M[i][j] * x[j]
        x[i] = s / M[i][i]

    return x


def distribuisci_carico_corrente(
    nodi: list[Nodo],
    id_nodi_corrente: list[int],
    q_y: float,
) -> list[Nodo]:
    """Converte carico distribuito su corrente in forze nodali equivalenti.

    Per carico uniforme: F_nodo = q_y * a, con a = semiampiezza tra nodi adiacenti.
    I nodi di estremità ricevono metà del contributo del nodo interno.

    Args:
        nodi:             lista di tutti i nodi del traliccio
        id_nodi_corrente: id dei nodi appartenenti al corrente caricato (ordinati per x)
        q_y:              carico per unità di lunghezza in Y [kg/cm]

    Returns:
        Nuova lista di nodi con Fy aggiornata (non modifica in-place).
    """
    import copy
    nodi_map = {n.id: n for n in nodi}
    # Copia nodi
    nodi_out = [copy.copy(n) for n in nodi]
    out_map = {n.id: n for n in nodi_out}

    # Ordina nodi corrente per x crescente
    nodi_corrente = sorted(
        [nodi_map[nid] for nid in id_nodi_corrente if nid in nodi_map],
        key=lambda n: n.x,
    )
    nc = len(nodi_corrente)
    if nc < 2:
        return nodi_out

    for i, nd in enumerate(nodi_corrente):
        # Contributo a sinistra
        if i > 0:
            dx_sx = (nd.x - nodi_corrente[i - 1].x) / 2
        else:
            dx_sx = 0.0
        # Contributo a destra
        if i < nc - 1:
            dx_dx = (nodi_corrente[i + 1].x - nd.x) / 2
        else:
            dx_dx = 0.0
        out_map[nd.id].Fy += q_y * (dx_sx + dx_dx)

    return nodi_out


# TODO D.3.2-ext: supporto molle nodali elastiche (Winkler)
# k_nodo = k_w * a [kg/cm] aggiunto alla diagonale di K prima di solve


def verifica_aste_traliccio(
    risultato: RisultatoTraliccio,
    sigma_adm_traz: float = 1900.0,
    sigma_adm_comp: float = 1900.0,
    lambda_max: float = 200.0,
    aste_input: list[Asta] | None = None,
    nodi_input: list[Nodo] | None = None,
    sezioni: dict[int, SezioneAsta] | None = None,
) -> list[dict]:
    """Verifica le aste del traliccio a trazione e compressione.

    Args:
        risultato: risultato dell'analisi
        sigma_adm_traz: tensione ammissibile a trazione [kg/cm²]
        sigma_adm_comp: tensione ammissibile a compressione [kg/cm²]
        lambda_max: snellezza massima ammissibile
        aste_input: lista aste originali (per dati sezione)
        nodi_input: lista nodi originali (per geometria instabilità)
        sezioni: dict {id_asta: SezioneAsta} — se presente, usa ix/iy reali
                 per instabilità biassiale. Retrocompatibile: default None.

    Returns:
        Lista di dizionari con risultati verifica per ogni asta
    """
    from .verifiche_ta import omega_acciaio

    verifiche = []
    for ra in risultato.aste:
        ver: dict = {
            "id_asta": ra.id_asta,
            "N": ra.N,
            "sigma": ra.sigma,
            "tipo": "trazione" if ra.N > 0 else "compressione" if ra.N < 0 else "scarica",
        }

        if ra.N > 0:
            # Trazione pura
            ver["sigma_adm"] = sigma_adm_traz
            ver["sfruttamento"] = abs(ra.sigma) / sigma_adm_traz
            ver["verificato"] = abs(ra.sigma) <= sigma_adm_traz
        elif ra.N < 0:
            # Compressione — verifica instabilità
            if sezioni and ra.id_asta in sezioni:
                # Instabilità biassiale con dati di sezione reali
                sez = sezioni[ra.id_asta]
                lam_ip = ra.L / sez.ix if sez.ix > 0 else 0.0   # in piano
                lam_fp = ra.L / sez.iy if sez.iy > 0 else 0.0   # fuori piano (governa)
                lam = max(lam_ip, lam_fp)
                omega = omega_acciaio(lam)
                sigma_eff = omega * abs(ra.sigma)
                ver["lambda_ip"] = lam_ip
                ver["lambda_fp"] = lam_fp
                ver["lambda"] = lam
                ver["omega"] = omega
                ver["sigma_eff"] = sigma_eff
                ver["sigma_adm"] = sigma_adm_comp
                ver["sfruttamento"] = sigma_eff / sigma_adm_comp
                ver["verificato"] = sigma_eff <= sigma_adm_comp
                ver["snellezza_ok"] = lam <= lambda_max
            elif aste_input:
                # Fallback: aste_input fornite ma senza SezioneAsta
                A_asta = None
                for ai in aste_input:
                    if ai.id == ra.id_asta:
                        A_asta = ai
                        break
                if A_asta and A_asta.A > 0:
                    # NOTA: senza ix/iy reali usiamo snellezza senza instabilità
                    # (impossibile calcolare i_min senza la forma della sezione)
                    ver["sigma_adm"] = sigma_adm_comp
                    ver["sfruttamento"] = abs(ra.sigma) / sigma_adm_comp
                    ver["verificato"] = abs(ra.sigma) <= sigma_adm_comp
                    ver["avviso"] = "i_min non disponibile — verifica senza instabilità"
                else:
                    ver["sigma_adm"] = sigma_adm_comp
                    ver["sfruttamento"] = abs(ra.sigma) / sigma_adm_comp
                    ver["verificato"] = abs(ra.sigma) <= sigma_adm_comp
            else:
                ver["sigma_adm"] = sigma_adm_comp
                ver["sfruttamento"] = abs(ra.sigma) / sigma_adm_comp
                ver["verificato"] = abs(ra.sigma) <= sigma_adm_comp
        else:
            ver["sigma_adm"] = sigma_adm_traz
            ver["sfruttamento"] = 0.0
            ver["verificato"] = True

        verifiche.append(ver)

    return verifiche


