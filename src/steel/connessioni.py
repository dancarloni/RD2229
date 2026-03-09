"""Verifiche connessioni acciaio: saldature e bullonature.

Verifiche secondo:
- CNR 10011 (metodo TA)
- NTC2018 §4.2.8 (metodo SLU, predisposizione)

Unità: kg/cm² per tensioni, cm per geometria, kg per forze.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum

# ═══════════════════════ SALDATURE ═══════════════════════

class TipoSaldatura(str, Enum):
    """Tipo di saldatura."""
    CORDONE_ANGOLO = "cordone_angolo"       # a cordone d'angolo
    TESTA_TESTA = "testa_testa"             # a completa penetrazione
    PARZIALE = "parziale"                   # a parziale penetrazione


class PosizioneSaldatura(str, Enum):
    """Posizione saldatura rispetto alla forza."""
    FRONTALE = "frontale"       # cordone perpendicolare alla forza
    LATERALE = "laterale"       # cordone parallelo alla forza


# Coefficiente di riduzione per saldatura a cordone d'angolo
# β_w da CNR 10011 (per acciai Fe360/Fe430/Fe510)
BETA_W: dict[str, float] = {
    "Fe360": 0.85,
    "Fe430": 0.85,
    "Fe510": 0.90,
    "S235": 0.85,
    "S275": 0.85,
    "S355": 0.90,
}


@dataclass
class InputSaldatura:
    """Input per verifica saldatura a cordone d'angolo."""
    tipo: TipoSaldatura = TipoSaldatura.CORDONE_ANGOLO

    # Geometria cordone
    a: float = 0.0          # altezza di gola [cm]
    L: float = 0.0          # lunghezza cordone [cm]
    n_cordoni: int = 1      # numero cordoni paralleli

    # Sollecitazioni sul cordone
    N: float = 0.0          # forza assiale [kg] (perpendicolare per frontale)
    V: float = 0.0          # taglio [kg] (parallelo per laterale)

    # Materiale
    tipo_acciaio: str = "Fe430"
    sigma_adm_acciaio: float = 1900.0  # σ_adm materiale base [kg/cm²]


@dataclass
class RisultatoSaldatura:
    """Risultato verifica saldatura."""
    tipo: str
    a: float                    # gola [cm]
    L: float                    # lunghezza [cm]
    A_gola: float               # area resistente = a × L [cm²]
    sigma_perp: float = 0.0     # tensione perpendicolare [kg/cm²]
    tau_perp: float = 0.0       # taglio perpendicolare [kg/cm²]
    tau_par: float = 0.0        # taglio parallelo [kg/cm²]
    sigma_id: float = 0.0       # tensione ideale [kg/cm²]
    sigma_adm_w: float = 0.0    # tensione ammissibile saldatura [kg/cm²]
    sfruttamento: float = 0.0
    verificato: bool = False
    passaggi: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "tipo": self.tipo,
            "a": self.a,
            "L": self.L,
            "A_gola": round(self.A_gola, 2),
            "sigma_id": round(self.sigma_id, 1),
            "sigma_adm_w": round(self.sigma_adm_w, 1),
            "sfruttamento": round(self.sfruttamento, 4),
            "verificato": self.verificato,
            "passaggi": self.passaggi,
        }


def verifica_saldatura_ta(inp: InputSaldatura) -> RisultatoSaldatura:
    """Verifica saldatura a cordone d'angolo — metodo TA (CNR 10011).

    Per cordone d'angolo:
    - Sezione di gola: A_gola = a × L
    - Tensioni sulla sezione di gola:
      σ⊥ = N⊥ / (a·L)  (perpendicolare al piano di gola)
      τ‖ = V‖ / (a·L)  (parallelo al cordone)
    - σ_id = √(σ⊥² + τ⊥² + τ‖²) ≤ σ_adm,w
    - σ_adm,w = β_w × σ_adm

    Per cordone frontale: σ⊥ = τ⊥ = F/(√2·a·L)
    Per cordone laterale: τ‖ = F/(a·L)
    """
    passaggi: list[str] = []
    beta_w = BETA_W.get(inp.tipo_acciaio, 0.85)
    sigma_adm_w = beta_w * inp.sigma_adm_acciaio

    L_eff = inp.L
    A_gola = inp.a * L_eff * inp.n_cordoni

    passaggi.append(f"Saldatura: {inp.tipo.value}, a={inp.a:.2f} cm, L={inp.L:.1f} cm")
    passaggi.append(f"N. cordoni: {inp.n_cordoni}, A_gola = {A_gola:.2f} cm²")
    passaggi.append(f"β_w = {beta_w}, σ_adm,w = {beta_w}×{inp.sigma_adm_acciaio:.0f} = {sigma_adm_w:.0f} kg/cm²")

    res = RisultatoSaldatura(
        tipo=inp.tipo.value,
        a=inp.a,
        L=L_eff,
        A_gola=A_gola,
        sigma_adm_w=sigma_adm_w,
    )

    if A_gola <= 0:
        res.passaggi = passaggi
        res.passaggi.append("ERRORE: area gola nulla")
        return res

    F_totale = math.sqrt(inp.N ** 2 + inp.V ** 2)

    if inp.tipo == TipoSaldatura.CORDONE_ANGOLO:
        # Forza perpendicolare al cordone (frontale)
        if abs(inp.N) > 0:
            # Cordone frontale: la forza si scompone su piano di gola a 45°
            res.sigma_perp = inp.N / (math.sqrt(2) * A_gola)
            res.tau_perp = inp.N / (math.sqrt(2) * A_gola)
            passaggi.append(
                f"Cordone frontale: σ⊥ = τ⊥ = N/(√2·A_gola) = "
                f"{inp.N:.0f}/(√2×{A_gola:.2f}) = {res.sigma_perp:.1f} kg/cm²"
            )

        # Forza parallela al cordone (laterale)
        if abs(inp.V) > 0:
            res.tau_par = inp.V / A_gola
            passaggi.append(
                f"Cordone laterale: τ‖ = V/A_gola = "
                f"{inp.V:.0f}/{A_gola:.2f} = {res.tau_par:.1f} kg/cm²"
            )

        # Tensione ideale
        res.sigma_id = math.sqrt(
            res.sigma_perp ** 2 + res.tau_perp ** 2 + res.tau_par ** 2
        )

    elif inp.tipo == TipoSaldatura.TESTA_TESTA:
        # A completa penetrazione: si verifica come materiale base
        res.sigma_perp = F_totale / A_gola
        res.sigma_id = res.sigma_perp
        sigma_adm_w = inp.sigma_adm_acciaio  # no riduzione
        res.sigma_adm_w = sigma_adm_w
        passaggi.append(
            f"Testa a testa: σ = F/A = {F_totale:.0f}/{A_gola:.2f} = {res.sigma_id:.1f} kg/cm²"
        )
        passaggi.append("(a completa penetrazione: σ_adm = σ_adm materiale base)")

    res.sfruttamento = res.sigma_id / sigma_adm_w if sigma_adm_w > 0 else 0.0
    res.verificato = res.sigma_id <= sigma_adm_w

    passaggi.append(
        f"σ_id = {res.sigma_id:.1f} {'≤' if res.verificato else '>'} "
        f"σ_adm,w = {sigma_adm_w:.0f} → {'OK' if res.verificato else 'NON VERIFICATO'} "
        f"(sfruttamento {res.sfruttamento:.1%})"
    )

    res.passaggi = passaggi
    return res


# ═══════════════════════ BULLONATURE ═══════════════════════

class ClasseBullone(str, Enum):
    """Classe di resistenza bullone."""
    CL_4_6 = "4.6"
    CL_5_6 = "5.6"
    CL_6_8 = "6.8"
    CL_8_8 = "8.8"
    CL_10_9 = "10.9"


# Tensione di rottura f_ub [kg/cm²] per classe bullone
F_UB: dict[str, float] = {
    "4.6": 4080.0,     # 400 MPa
    "5.6": 5100.0,     # 500 MPa
    "6.8": 6120.0,     # 600 MPa
    "8.8": 8160.0,     # 800 MPa
    "10.9": 10200.0,   # 1000 MPa
}

# Tensione di snervamento f_yb [kg/cm²] per classe bullone
F_YB: dict[str, float] = {
    "4.6": 2448.0,     # 240 MPa
    "5.6": 3060.0,     # 300 MPa
    "6.8": 4896.0,     # 480 MPa
    "8.8": 6528.0,     # 640 MPa
    "10.9": 9180.0,    # 900 MPa
}

# Area resistente a trazione A_res [cm²] per diametro nominale
A_RES_BULLONE: dict[int, float] = {
    12: 0.843,
    14: 1.154,
    16: 1.567,
    18: 1.920,
    20: 2.450,
    22: 3.030,
    24: 3.530,
    27: 4.590,
    30: 5.610,
    36: 8.170,
}

# Area nominale gambo [cm²]
A_GAMBO_BULLONE: dict[int, float] = {
    12: 1.131,
    14: 1.539,
    16: 2.011,
    18: 2.545,
    20: 3.142,
    22: 3.801,
    24: 4.524,
    27: 5.726,
    30: 7.069,
    36: 10.18,
}


class TipoCollegamentoBullonato(str, Enum):
    """Tipo di collegamento bullonato."""
    TAGLIO_GAMBO = "taglio_gambo"                   # gambo nella sezione di taglio
    TAGLIO_FILETTO = "taglio_filetto"               # filetto nella sezione di taglio
    TRAZIONE = "trazione"                           # bullone teso
    INTERAZIONE_TAGLIO_TRAZIONE = "interazione"     # taglio + trazione


@dataclass
class InputBullone:
    """Input per verifica singolo bullone o gruppo."""
    diametro: int = 20               # diametro nominale [mm]
    classe: str = "8.8"              # classe resistenza
    n_bulloni: int = 1               # numero bulloni
    n_piani_taglio: int = 1          # numero piani di taglio

    # Sollecitazioni per bullone
    V: float = 0.0                   # taglio per bullone [kg]
    N: float = 0.0                   # trazione per bullone [kg]

    # Per verifica rifollamento
    t: float = 0.0                   # spessore minimo lamiera [cm]
    e1: float = 0.0                  # distanza dal bordo (dir. forza) [cm]
    e2: float = 0.0                  # distanza dal bordo (perp. forza) [cm]
    p1: float = 0.0                  # interasse bulloni (dir. forza) [cm]
    fu_lamiera: float = 0.0          # resistenza rottura lamiera [kg/cm²]

    # Metodo verifica
    tipo_acciaio: str = "Fe430"      # per σ_adm
    sigma_adm: float = 1900.0        # tensione ammissibile base [kg/cm²]


@dataclass
class RisultatoBullone:
    """Risultato verifica bullone/gruppo."""
    diametro: int
    classe: str
    n_bulloni: int

    # Resistenze
    F_v_Rd: float = 0.0         # resistenza a taglio [kg]
    F_t_Rd: float = 0.0         # resistenza a trazione [kg]
    F_b_Rd: float = 0.0         # resistenza rifollamento [kg]

    # Sfruttamenti
    sfruttamento_taglio: float = 0.0
    sfruttamento_trazione: float = 0.0
    sfruttamento_rifollamento: float = 0.0
    sfruttamento_interazione: float = 0.0

    # Verifiche
    verifica_taglio: bool = True
    verifica_trazione: bool = True
    verifica_rifollamento: bool = True
    verifica_interazione: bool = True
    verifica_globale: bool = True

    passaggi: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "diametro": self.diametro,
            "classe": self.classe,
            "n_bulloni": self.n_bulloni,
            "F_v_Rd": round(self.F_v_Rd, 0),
            "F_t_Rd": round(self.F_t_Rd, 0),
            "F_b_Rd": round(self.F_b_Rd, 0),
            "sfruttamento_taglio": round(self.sfruttamento_taglio, 4),
            "sfruttamento_trazione": round(self.sfruttamento_trazione, 4),
            "sfruttamento_interazione": round(self.sfruttamento_interazione, 4),
            "verifica_globale": self.verifica_globale,
            "passaggi": self.passaggi,
        }


def verifica_bullone_ta(inp: InputBullone) -> RisultatoBullone:
    """Verifica bullone/gruppo con metodo TA.

    Metodo TA (CNR 10011):
    - Taglio: τ = V / (n × A_gambo) ≤ τ_adm = σ_adm / √3
    - Trazione: σ = N / (n × A_res) ≤ σ_adm,b = 0.8 × f_yb / γ
    - Interazione: (V/V_Rd)² + (N/N_Rd)² ≤ 1

    Args:
        inp: dati di input

    Returns:
        RisultatoBullone
    """
    passaggi: list[str] = []

    d_cm = inp.diametro / 10.0  # mm → cm
    A_gambo = A_GAMBO_BULLONE.get(inp.diametro, math.pi * d_cm ** 2 / 4)
    A_res = A_RES_BULLONE.get(inp.diametro, 0.75 * A_gambo)
    f_ub = F_UB.get(inp.classe, 8160.0)
    f_yb = F_YB.get(inp.classe, 6528.0)

    passaggi.append(
        f"Bullone M{inp.diametro} classe {inp.classe}, n={inp.n_bulloni}"
    )
    passaggi.append(
        f"A_gambo = {A_gambo:.3f} cm², A_res = {A_res:.3f} cm²"
    )
    passaggi.append(
        f"f_ub = {f_ub:.0f} kg/cm², f_yb = {f_yb:.0f} kg/cm²"
    )

    # Tensioni ammissibili bullone (TA)
    # Taglio: τ_adm = 0.6 × f_ub / γ_Mb (γ_Mb = 1.25 per SLU, ~2.0 per TA)
    # Semplificazione TA: τ_adm_bullone ≈ f_ub / 3
    tau_adm_b = f_ub / 3.0
    # Trazione: σ_adm,b ≈ 0.8 × f_yb / 1.5
    sigma_adm_b = 0.8 * f_yb / 1.5

    passaggi.append(
        f"τ_adm,b = f_ub/3 = {tau_adm_b:.0f} kg/cm², "
        f"σ_adm,b = 0.8·f_yb/1.5 = {sigma_adm_b:.0f} kg/cm²"
    )

    res = RisultatoBullone(
        diametro=inp.diametro,
        classe=inp.classe,
        n_bulloni=inp.n_bulloni,
    )

    # Resistenza a taglio per bullone (TA)
    F_v_1 = tau_adm_b * A_gambo * inp.n_piani_taglio
    res.F_v_Rd = F_v_1 * inp.n_bulloni

    # Resistenza a trazione per bullone
    F_t_1 = sigma_adm_b * A_res
    res.F_t_Rd = F_t_1 * inp.n_bulloni

    passaggi.append(
        f"F_v,Rd (1 bull.) = {F_v_1:.0f} kg × {inp.n_bulloni} = {res.F_v_Rd:.0f} kg"
    )
    passaggi.append(
        f"F_t,Rd (1 bull.) = {F_t_1:.0f} kg × {inp.n_bulloni} = {res.F_t_Rd:.0f} kg"
    )

    # --- Verifica taglio ---
    V_tot = abs(inp.V) * inp.n_bulloni if inp.n_bulloni > 0 else abs(inp.V)
    # inp.V è per singolo bullone
    if res.F_v_Rd > 0:
        res.sfruttamento_taglio = abs(inp.V) / F_v_1
    res.verifica_taglio = abs(inp.V) <= F_v_1

    if abs(inp.V) > 0:
        passaggi.append(
            f"Taglio: V = {abs(inp.V):.0f} {'≤' if res.verifica_taglio else '>'} "
            f"F_v,Rd = {F_v_1:.0f} → {'OK' if res.verifica_taglio else 'NON VERIFICATO'}"
        )

    # --- Verifica trazione ---
    if res.F_t_Rd > 0:
        res.sfruttamento_trazione = abs(inp.N) / F_t_1
    res.verifica_trazione = abs(inp.N) <= F_t_1

    if abs(inp.N) > 0:
        passaggi.append(
            f"Trazione: N = {abs(inp.N):.0f} {'≤' if res.verifica_trazione else '>'} "
            f"F_t,Rd = {F_t_1:.0f} → {'OK' if res.verifica_trazione else 'NON VERIFICATO'}"
        )

    # --- Verifica rifollamento ---
    if inp.t > 0 and inp.fu_lamiera > 0:
        # F_b,Rd = α_b × f_u × d × t (TA: con coefficiente ridotto)
        # α_b = min(e1/(3d0), p1/(3d0)-1/4, f_ub/f_u, 1.0)
        d0 = d_cm + 0.2  # foro standard (d + 2mm)
        alpha_list = [1.0]
        if inp.e1 > 0:
            alpha_list.append(inp.e1 / (3 * d0))
        if inp.p1 > 0:
            alpha_list.append(inp.p1 / (3 * d0) - 0.25)
        alpha_list.append(f_ub / inp.fu_lamiera)
        alpha_b = min(alpha_list)
        alpha_b = max(alpha_b, 0.0)

        F_b_1 = alpha_b * inp.fu_lamiera * d_cm * inp.t / 1.5  # TA
        res.F_b_Rd = F_b_1 * inp.n_bulloni

        if F_b_1 > 0:
            res.sfruttamento_rifollamento = abs(inp.V) / F_b_1
        res.verifica_rifollamento = abs(inp.V) <= F_b_1

        passaggi.append(
            f"Rifollamento: α_b={alpha_b:.3f}, F_b,Rd={F_b_1:.0f} kg, "
            f"sfruttamento={res.sfruttamento_rifollamento:.1%} "
            f"→ {'OK' if res.verifica_rifollamento else 'NON VERIFICATO'}"
        )

    # --- Interazione taglio + trazione ---
    if abs(inp.V) > 0 and abs(inp.N) > 0 and F_v_1 > 0 and F_t_1 > 0:
        interazione = (inp.V / F_v_1) ** 2 + (inp.N / F_t_1) ** 2
        res.sfruttamento_interazione = interazione
        res.verifica_interazione = interazione <= 1.0

        passaggi.append(
            f"Interazione: (V/V_Rd)² + (N/N_Rd)² = ({inp.V/F_v_1:.3f})² + ({inp.N/F_t_1:.3f})² "
            f"= {interazione:.3f} {'≤' if res.verifica_interazione else '>'} 1.0 "
            f"→ {'OK' if res.verifica_interazione else 'NON VERIFICATO'}"
        )

    # Verifica globale
    res.verifica_globale = (
        res.verifica_taglio
        and res.verifica_trazione
        and res.verifica_rifollamento
        and res.verifica_interazione
    )

    stato = "VERIFICATO" if res.verifica_globale else "NON VERIFICATO"
    passaggi.append(f"═══ ESITO: {stato} ═══")

    res.passaggi = passaggi
    return res
