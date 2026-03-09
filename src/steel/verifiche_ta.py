"""Verifiche acciaio con metodo TA (Tensioni Ammissibili).

Verifiche per profili in acciaio laminato a caldo secondo:
- DM 14/02/1992 (strutture in acciaio)
- DM 09/01/1996
- CNR 10011 (Costruzioni in acciaio)

Unità: kg/cm² per tensioni, cm per geometria.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .sezione_asta import SezioneAsta

from .sagomario import ProfiloAcciaio


class TipoAcciaio(str, Enum):
    """Tipo di acciaio strutturale."""
    Fe360 = "Fe360"    # fyk = 2350 kg/cm², sigma_adm = 1600 kg/cm²
    Fe430 = "Fe430"    # fyk = 2750 kg/cm², sigma_adm = 1900 kg/cm²
    Fe510 = "Fe510"    # fyk = 3550 kg/cm², sigma_adm = 2400 kg/cm²
    S235 = "S235"      # equivalente Fe360
    S275 = "S275"      # equivalente Fe430
    S355 = "S355"      # equivalente Fe510


# Tensioni ammissibili TA per tipo acciaio [kg/cm²]
SIGMA_ADM_TA: dict[str, float] = {
    "Fe360": 1600.0,
    "Fe430": 1900.0,
    "Fe510": 2400.0,
    "S235": 1600.0,
    "S275": 1900.0,
    "S355": 2400.0,
}

# Tensione di snervamento [kg/cm²]
FYK_ACCIAIO: dict[str, float] = {
    "Fe360": 2350.0,
    "Fe430": 2750.0,
    "Fe510": 3550.0,
    "S235": 2395.0,   # 235 MPa
    "S275": 2804.0,   # 275 MPa
    "S355": 3620.0,   # 355 MPa
}

# Modulo elastico acciaio strutturale
E_ACCIAIO = 2100000.0  # kg/cm²
G_ACCIAIO = 810000.0   # kg/cm²

# Coefficiente di sicurezza per instabilità
OMEGA_1_BASE = 1.0  # fattore di sicurezza base


class VincoloEstremita(str, Enum):
    """Vincoli alle estremità dell'asta per calcolo lunghezza libera."""
    INCASTRO_INCASTRO = "incastro-incastro"        # beta = 0.5
    INCASTRO_CERNIERA = "incastro-cerniera"        # beta = 0.7
    CERNIERA_CERNIERA = "cerniera-cerniera"        # beta = 1.0
    INCASTRO_LIBERO = "incastro-libero"            # beta = 2.0
    INCASTRO_CARR_TRASL = "incastro-carr_trasl"    # beta = 1.0


BETA_VINCOLI: dict[str, float] = {
    "incastro-incastro": 0.5,
    "incastro-cerniera": 0.7,
    "cerniera-cerniera": 1.0,
    "incastro-libero": 2.0,
    "incastro-carr_trasl": 1.0,
}


@dataclass
class InputVerificaAcciaio:
    """Dati di input per verifica profilo acciaio TA."""
    profilo: ProfiloAcciaio
    tipo_acciaio: str = "Fe430"

    # Sollecitazioni
    N: float = 0.0               # sforzo assiale [kg] (positivo = trazione)
    Mx: float = 0.0              # momento flettente asse forte [kg·cm]
    My: float = 0.0              # momento flettente asse debole [kg·cm]
    Vx: float = 0.0              # taglio asse x [kg]
    Vy: float = 0.0              # taglio asse y [kg]
    Mt: float = 0.0              # momento torcente [kg·cm]

    # Per instabilità
    L: float = 0.0               # lunghezza asta [cm]
    vincolo: str = "cerniera-cerniera"
    beta_x: float | None = None  # coefficiente lunghezza libera (se diverso da vincolo)
    beta_y: float | None = None

    # Override tensione ammissibile (se diversa dal default)
    sigma_adm_override: float | None = None
    tau_adm_override: float | None = None


@dataclass
class RisultatoVerificaAcciaio:
    """Risultato verifica profilo acciaio TA."""
    nome_profilo: str
    tipo_acciaio: str

    # Tensioni ammissibili
    sigma_adm: float             # [kg/cm²]
    tau_adm: float               # [kg/cm²]

    # Tensioni calcolate
    sigma_N: float = 0.0         # σ da sforzo normale [kg/cm²]
    sigma_Mx: float = 0.0        # σ da momento Mx [kg/cm²]
    sigma_My: float = 0.0        # σ da momento My [kg/cm²]
    sigma_id: float = 0.0        # σ ideale (combinata) [kg/cm²]
    tau_Vy: float = 0.0          # τ da taglio Vy [kg/cm²]
    tau_Vx: float = 0.0          # τ da taglio Vx [kg/cm²]
    tau_Mt: float = 0.0          # τ da torsione [kg/cm²]
    tau_max: float = 0.0         # τ massimo [kg/cm²]

    # Instabilità
    lambda_x: float = 0.0        # snellezza asse forte
    lambda_y: float = 0.0        # snellezza asse debole
    omega: float = 1.0           # coefficiente ω per carico di punta
    sigma_N_omega: float = 0.0   # σ amplificata = ω·N/A [kg/cm²]

    # Verifiche (True = verificato)
    verifica_flessione: bool = False
    verifica_taglio: bool = False
    verifica_pressoflessione: bool = False
    verifica_instabilita: bool = False
    verifica_globale: bool = False

    # Sfruttamento
    sfruttamento_sigma: float = 0.0   # σ_id / σ_adm
    sfruttamento_tau: float = 0.0     # τ_max / τ_adm

    passaggi: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "nome_profilo": self.nome_profilo,
            "tipo_acciaio": self.tipo_acciaio,
            "sigma_adm": self.sigma_adm,
            "tau_adm": self.tau_adm,
            "sigma_N": self.sigma_N,
            "sigma_Mx": self.sigma_Mx,
            "sigma_My": self.sigma_My,
            "sigma_id": self.sigma_id,
            "tau_max": self.tau_max,
            "lambda_x": self.lambda_x,
            "lambda_y": self.lambda_y,
            "omega": self.omega,
            "verifica_flessione": self.verifica_flessione,
            "verifica_taglio": self.verifica_taglio,
            "verifica_pressoflessione": self.verifica_pressoflessione,
            "verifica_instabilita": self.verifica_instabilita,
            "verifica_globale": self.verifica_globale,
            "sfruttamento_sigma": round(self.sfruttamento_sigma, 4),
            "sfruttamento_tau": round(self.sfruttamento_tau, 4),
            "passaggi": self.passaggi,
        }


def omega_acciaio(lam: float) -> float:
    """Coefficiente ω per instabilità acciaio (CNR 10011, Tab. 2).

    Interpolazione lineare dalla tabella standard.

    Args:
        lam: snellezza λ = L₀/i

    Returns:
        ω >= 1.0
    """
    # Tabella ω per acciaio (valori tipici CNR 10011)
    tabella = [
        (0, 1.000),
        (20, 1.040),
        (30, 1.065),
        (40, 1.100),
        (50, 1.150),
        (60, 1.220),
        (70, 1.310),
        (80, 1.430),
        (90, 1.590),
        (100, 1.800),
        (110, 2.070),
        (120, 2.420),
        (130, 2.850),
        (140, 3.370),
        (150, 3.990),
        (160, 4.730),
        (170, 5.590),
        (180, 6.590),
        (190, 7.750),
        (200, 9.080),
    ]

    if lam <= 0:
        return 1.0
    if lam >= 200:
        return tabella[-1][1]

    for i in range(len(tabella) - 1):
        l0, w0 = tabella[i]
        l1, w1 = tabella[i + 1]
        if l0 <= lam <= l1:
            t = (lam - l0) / (l1 - l0)
            return w0 + t * (w1 - w0)

    return tabella[-1][1]


def verifica_profilo_ta(inp: InputVerificaAcciaio) -> RisultatoVerificaAcciaio:
    """Verifica completa profilo acciaio con metodo TA.

    Esegue:
    1. Flessione semplice e composta
    2. Taglio
    3. Pressoflessione (N + Mx + My)
    4. Instabilità (se L > 0)

    Args:
        inp: dati di input

    Returns:
        RisultatoVerificaAcciaio con tutte le verifiche
    """
    p = inp.profilo
    passaggi: list[str] = []

    # Tensioni ammissibili
    sigma_adm = inp.sigma_adm_override or SIGMA_ADM_TA.get(inp.tipo_acciaio, 1900.0)
    tau_adm = inp.tau_adm_override or (sigma_adm / math.sqrt(3))

    passaggi.append(f"Profilo: {p.nome}, Acciaio: {inp.tipo_acciaio}")
    passaggi.append(f"σ_adm = {sigma_adm:.0f} kg/cm², τ_adm = {tau_adm:.0f} kg/cm²")

    res = RisultatoVerificaAcciaio(
        nome_profilo=p.nome,
        tipo_acciaio=inp.tipo_acciaio,
        sigma_adm=sigma_adm,
        tau_adm=tau_adm,
    )

    # --- 1. Tensione da sforzo normale ---
    if abs(inp.N) > 0 and p.A > 0:
        res.sigma_N = inp.N / p.A
        passaggi.append(f"σ_N = N/A = {inp.N:.0f}/{p.A:.2f} = {res.sigma_N:.1f} kg/cm²")

    # --- 2. Tensione da flessione ---
    if abs(inp.Mx) > 0 and p.Wx > 0:
        res.sigma_Mx = abs(inp.Mx) / p.Wx
        passaggi.append(f"σ_Mx = |Mx|/Wx = {abs(inp.Mx):.0f}/{p.Wx:.1f} = {res.sigma_Mx:.1f} kg/cm²")

    if abs(inp.My) > 0 and p.Wy > 0:
        res.sigma_My = abs(inp.My) / p.Wy
        passaggi.append(f"σ_My = |My|/Wy = {abs(inp.My):.0f}/{p.Wy:.1f} = {res.sigma_My:.1f} kg/cm²")

    # Verifica flessione semplice (solo Mx)
    if abs(inp.N) == 0 and abs(inp.My) == 0:
        res.verifica_flessione = res.sigma_Mx <= sigma_adm
        passaggi.append(
            f"Flessione semplice: σ_Mx = {res.sigma_Mx:.1f} {'≤' if res.verifica_flessione else '>'} "
            f"σ_adm = {sigma_adm:.0f} → {'OK' if res.verifica_flessione else 'NON VERIFICATO'}"
        )

    # --- 3. Tensione ideale (pressoflessione) ---
    # σ_id = |σ_N| + σ_Mx + σ_My  (sovrapposizione effetti per TA)
    sigma_max = abs(res.sigma_N) + res.sigma_Mx + res.sigma_My
    res.sigma_id = sigma_max
    res.sfruttamento_sigma = sigma_max / sigma_adm if sigma_adm > 0 else 0.0

    res.verifica_pressoflessione = sigma_max <= sigma_adm
    passaggi.append(
        f"Pressoflessione: σ_id = |σ_N| + σ_Mx + σ_My = {sigma_max:.1f} "
        f"{'≤' if res.verifica_pressoflessione else '>'} σ_adm = {sigma_adm:.0f} "
        f"→ {'OK' if res.verifica_pressoflessione else 'NON VERIFICATO'} "
        f"(sfruttamento {res.sfruttamento_sigma:.1%})"
    )

    # --- 4. Taglio ---
    # τ = V·S/(I·t) ≈ V/(A_anima) per profili standard
    A_anima = p.h * p.tw  # area anima approssimata
    if A_anima > 0:
        if abs(inp.Vy) > 0:
            # Taglio asse y (forza lungo y, reazione su anima)
            res.tau_Vy = abs(inp.Vy) / A_anima
            passaggi.append(
                f"τ_Vy = |Vy|/A_anima = {abs(inp.Vy):.0f}/({p.h:.1f}×{p.tw:.2f}) = {res.tau_Vy:.1f} kg/cm²"
            )

    if abs(inp.Vx) > 0 and p.b > 0 and p.tf > 0:
        A_ali = 2 * p.b * p.tf
        if A_ali > 0:
            res.tau_Vx = abs(inp.Vx) / A_ali
            passaggi.append(f"τ_Vx = |Vx|/A_ali = {abs(inp.Vx):.0f}/{A_ali:.2f} = {res.tau_Vx:.1f} kg/cm²")

    # Torsione (approssimata per profili aperti)
    if abs(inp.Mt) > 0 and p.It > 0:
        t_max = max(p.tf, p.tw)
        res.tau_Mt = abs(inp.Mt) * t_max / p.It
        passaggi.append(f"τ_Mt = |Mt|·t_max/It = {abs(inp.Mt):.0f}×{t_max:.2f}/{p.It:.2f} = {res.tau_Mt:.1f} kg/cm²")

    res.tau_max = math.sqrt(res.tau_Vy**2 + res.tau_Vx**2) + res.tau_Mt
    res.sfruttamento_tau = res.tau_max / tau_adm if tau_adm > 0 else 0.0

    res.verifica_taglio = res.tau_max <= tau_adm
    passaggi.append(
        f"Taglio: τ_max = {res.tau_max:.1f} {'≤' if res.verifica_taglio else '>'} "
        f"τ_adm = {tau_adm:.0f} → {'OK' if res.verifica_taglio else 'NON VERIFICATO'}"
    )

    # --- 5. Instabilità (se L > 0 e N < 0 compressione) ---
    res.verifica_instabilita = True  # default se non applicabile
    if inp.L > 0 and inp.N < 0:
        beta_val = BETA_VINCOLI.get(inp.vincolo, 1.0)
        beta_x = inp.beta_x if inp.beta_x is not None else beta_val
        beta_y = inp.beta_y if inp.beta_y is not None else beta_val

        L0_x = beta_x * inp.L
        L0_y = beta_y * inp.L

        if p.ix > 0:
            res.lambda_x = L0_x / p.ix
        if p.iy > 0:
            res.lambda_y = L0_y / p.iy

        lambda_max = max(res.lambda_x, res.lambda_y)
        res.omega = omega_acciaio(lambda_max)

        passaggi.append(
            f"Instabilità: L₀_x = {beta_x}×{inp.L:.0f} = {L0_x:.0f} cm, "
            f"L₀_y = {beta_y}×{inp.L:.0f} = {L0_y:.0f} cm"
        )
        passaggi.append(
            f"  λ_x = {res.lambda_x:.1f}, λ_y = {res.lambda_y:.1f}, "
            f"λ_max = {lambda_max:.1f} → ω = {res.omega:.3f}"
        )

        res.sigma_N_omega = res.omega * abs(inp.N) / p.A
        sigma_inst = res.sigma_N_omega + res.sigma_Mx + res.sigma_My
        res.verifica_instabilita = sigma_inst <= sigma_adm

        passaggi.append(
            f"  σ = ω·|N|/A + σ_Mx + σ_My = {res.sigma_N_omega:.1f} + {res.sigma_Mx:.1f} + {res.sigma_My:.1f} "
            f"= {sigma_inst:.1f} {'≤' if res.verifica_instabilita else '>'} "
            f"σ_adm = {sigma_adm:.0f} → {'OK' if res.verifica_instabilita else 'NON VERIFICATO'}"
        )

        # Aggiorna sigma_id se instabilità dà valore più alto
        if sigma_inst > res.sigma_id:
            res.sigma_id = sigma_inst
            res.sfruttamento_sigma = sigma_inst / sigma_adm

    # --- 6. Verifica globale ---
    res.verifica_globale = (
        res.verifica_pressoflessione
        and res.verifica_taglio
        and res.verifica_instabilita
    )

    # Verifica combinata σ-τ (criterio Von Mises semplificato)
    if res.tau_max > 0 and res.sigma_id > 0:
        sigma_vm = math.sqrt(res.sigma_id**2 + 3 * res.tau_max**2)
        verifica_vm = sigma_vm <= sigma_adm * 1.1  # 10% bonus per combinata
        passaggi.append(
            f"Von Mises: σ_VM = √(σ² + 3τ²) = {sigma_vm:.1f} "
            f"{'≤' if verifica_vm else '>'} 1.1·σ_adm = {sigma_adm * 1.1:.0f} "
            f"→ {'OK' if verifica_vm else 'NON VERIFICATO'}"
        )
        if not verifica_vm:
            res.verifica_globale = False

    stato = "VERIFICATO" if res.verifica_globale else "NON VERIFICATO"
    passaggi.append(f"═══ ESITO GLOBALE: {stato} ═══")

    res.passaggi = passaggi
    return res


def seleziona_profilo_ottimale(
    famiglia: str,
    Mx: float,
    tipo_acciaio: str = "Fe430",
    sagomario: object | None = None,
) -> ProfiloAcciaio | None:
    """Seleziona il profilo più leggero che verifica la flessione semplice.

    Args:
        famiglia: famiglia profilo (es. "IPE")
        Mx: momento flettente [kg·cm]
        tipo_acciaio: tipo acciaio
        sagomario: istanza SagomarioAcciaio (opzionale)

    Returns:
        Profilo ottimale o None
    """
    sigma_adm = SIGMA_ADM_TA.get(tipo_acciaio, 1900.0)
    Wx_min = abs(Mx) / sigma_adm  # cm³

    if sagomario is None:
        from .sagomario import SagomarioAcciaio
        sagomario = SagomarioAcciaio()
        sagomario.carica_tutti()

    return sagomario.profilo_ottimale(Wx_min, famiglia)


def verifica_asta_ta(
    sezione: SezioneAsta,
    N: float,
    L: float,
    tipo_acciaio: str = "Fe430",
    beta_inpiano: float = 1.0,
    beta_fuoripiano: float = 1.0,
    sigma_adm_override: float | None = None,
) -> dict:
    """Verifica asta di traliccio a sforzo assiale (trazione o compressione).

    Per compressione: instabilità biassiale con λ = max(λ_ip, λ_fp).

    Args:
        sezione:          SezioneAsta (piatto, angolare o profilo standard)
        N:                sforzo normale [kg] (+ trazione, − compressione)
        L:                lunghezza libera asta [cm]
        tipo_acciaio:     tipo acciaio (es. "Fe430")
        beta_inpiano:     coeff. di vincolo in piano (1.0 per cerniera-cerniera)
        beta_fuoripiano:  coeff. di vincolo fuori piano (1.0 per cerniera-cerniera)
        sigma_adm_override: tensione ammissibile override [kg/cm²]

    Returns:
        dict con chiavi: tipo, sigma, sigma_adm, sfruttamento, verificato,
                         (se compressione) lambda_ip, lambda_fp, lambda_max, omega, sigma_eff
    """
    sigma_adm = sigma_adm_override or SIGMA_ADM_TA.get(tipo_acciaio, 1900.0)
    sigma = N / sezione.A if sezione.A > 0 else 0.0

    if N > 0:
        # Trazione pura
        return {
            "tipo": "trazione",
            "N": N,
            "sigma": sigma,
            "sigma_adm": sigma_adm,
            "sfruttamento": abs(sigma) / sigma_adm,
            "verificato": abs(sigma) <= sigma_adm,
        }
    elif N < 0:
        # Compressione — instabilità biassiale
        lambda_ip = beta_inpiano * L / sezione.ix if sezione.ix > 0 else 0.0
        lambda_fp = beta_fuoripiano * L / sezione.iy if sezione.iy > 0 else 0.0
        lambda_max = max(lambda_ip, lambda_fp)
        omega = omega_acciaio(lambda_max)
        sigma_eff = omega * abs(sigma)
        return {
            "tipo": "compressione",
            "N": N,
            "sigma": sigma,
            "sigma_adm": sigma_adm,
            "lambda_ip": lambda_ip,
            "lambda_fp": lambda_fp,
            "lambda_max": lambda_max,
            "omega": omega,
            "sigma_eff": sigma_eff,
            "sfruttamento": sigma_eff / sigma_adm,
            "verificato": sigma_eff <= sigma_adm,
        }
    else:
        return {
            "tipo": "scarica",
            "N": 0.0,
            "sigma": 0.0,
            "sigma_adm": sigma_adm,
            "sfruttamento": 0.0,
            "verificato": True,
        }


