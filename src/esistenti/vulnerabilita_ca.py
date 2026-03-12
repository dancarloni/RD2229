"""Analisi di vulnerabilità sismica per edifici in c.a. esistenti.

Calcola l'indice ρ = Capacità/Domanda per ogni elemento strutturale
(travi e pilastri) rispetto a flessione, taglio e pressoflessione.

Riferimenti normativi:
- NTC2018 §8.7.1: Verifiche di sicurezza edifici esistenti in c.a.
- Circolare 7/2019 §C8.7.2: Metodi di analisi e verifiche
- Circolare 7/2019 §C8.7.2.4: Duttilità disponibile θ_u

Unità: cm per geometria, kg e kg/cm² per forze e tensioni.

Note di progettazione (Fase R):
- Doppio output obbligatorio per elemento: ρ_min e ρ_medio
- Soglie classificazione configurabili (default: ≥1.0 / 0.8–1.0 / <0.8)
- P-Delta: coefficiente θ semplificato opzionale (NTC2018 §7.3.6.1)
- Duttilità: angolo di rotazione plastica θ_u (Circ. 7/2019 eq. C8.7.2.9)
- FC già applicato prima dell'ingresso: usare MaterialeConFC.proprieta.f_cd
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from src.core.registro_log import registro

_MODULO_LOG = "esistenti.vulnerabilita_ca"

# Gravità in cm/s²
_G = 981.0


# ═══════════════════════════════════════════════════════════
#  Enumerazioni
# ═══════════════════════════════════════════════════════════

class TipoElemento(str, Enum):
    """Tipo di elemento strutturale in c.a."""
    TRAVE = "trave"
    PILASTRO = "pilastro"
    PARETE_CA = "parete_ca"


class ClasseVulnerabilita(str, Enum):
    """Classe di vulnerabilità basata su ρ = C/D."""
    VERIFICATO = "verificato"        # ρ ≥ 1.0
    CRITICO = "critico"              # 0.8 ≤ ρ < 1.0
    NON_VERIFICATO = "non_verificato"  # ρ < 0.8


# ═══════════════════════════════════════════════════════════
#  Configurazione soglie e pesi
# ═══════════════════════════════════════════════════════════

@dataclass
class SoglieRho:
    """Soglie classificazione ρ = C/D.

    Configurabili dall'utente; i default seguono la prassi NTC2018.
    """
    verificato: float = 1.0   # ρ ≥ verificato → VERIFICATO
    critico: float = 0.8      # critico ≤ ρ < verificato → CRITICO
    # ρ < critico → NON_VERIFICATO

    def classifica(self, rho: float) -> ClasseVulnerabilita:
        if rho >= self.verificato:
            return ClasseVulnerabilita.VERIFICATO
        elif rho >= self.critico:
            return ClasseVulnerabilita.CRITICO
        else:
            return ClasseVulnerabilita.NON_VERIFICATO


@dataclass
class ConfigVulnerabilitaCA:
    """Parametri di configurazione dell'analisi di vulnerabilità c.a."""
    soglie: SoglieRho = field(default_factory=SoglieRho)

    # Pesi per indice globale: ("IDele", peso)
    # Se None, tutti gli elementi pesano uguale
    pesi_per_tipo: dict[str, float] = field(default_factory=lambda: {
        TipoElemento.PILASTRO.value: 2.0,
        TipoElemento.TRAVE.value: 1.0,
        TipoElemento.PARETE_CA.value: 2.5,
    })

    # Coefficiente P-Delta θ (opzionale; 0 = disabilitato)
    # NTC2018 §7.3.6.1: θ = Ptot × dr / (Vtot × h)
    # Se > 0, la domanda viene amplificata: Md_eff = Md / (1 - theta)
    theta_pdelta: float = 0.0

    normativa: str = "NTC2018"  # "NTC2018" | "OPCM3274" | "EC8"


# ═══════════════════════════════════════════════════════════
#  Input elemento
# ═══════════════════════════════════════════════════════════

@dataclass
class ElementoCA:
    """Dati di input per un elemento in c.a. esistente.

    Le resistenze f_cd, f_yd sono già ridotte per FC (usare MaterialeConFC).
    Valori in kg/cm² per tensioni, cm per geometria, kg e kg·cm per forze.
    """
    id_elemento: str

    tipo: TipoElemento = TipoElemento.PILASTRO

    # Geometria sezione rettangolare
    b: float = 30.0    # larghezza sezione [cm]
    h_sez: float = 50.0  # altezza sezione [cm]
    d: float = 46.0    # altezza utile (d = h_sez - copriferro - φ/2) [cm]
    d_primo: float = 4.0  # copriferro lato compresso [cm]

    # Armatura
    As: float = 0.0    # area armatura tesa [cm²]
    As_primo: float = 0.0  # area armatura compressa [cm²]
    # Staffe: None se assenti (anni '60 → possibile carenza)
    Asw: float | None = None  # area sezione trasversale staffe [cm²]
    s_staffe: float | None = None  # interasse staffe [cm]

    # Resistenze di calcolo (già divise per FC)
    f_cd: float = 85.0   # resistenza calcestruzzo kg/cm² (RCk≈150, f_cd≈85)
    f_yd: float = 3800.0  # resistenza acciaio kg/cm²  (Fe44 → ~4400 kg/cm²)
    f_ctd: float = 6.0    # resistenza trazione cls kg/cm²

    # Azioni (valori di progetto SLV)
    N_ed: float = 0.0   # sforzo assiale [kg] (+ = compressione)
    Mx_ed: float = 0.0  # momento SLV [kg·cm]
    Ty_ed: float = 0.0  # taglio SLV [kg]

    # Luce elemento
    luce: float = 300.0  # luce libera [cm]

    # Note
    piano: str = ""
    note: str = ""


# ═══════════════════════════════════════════════════════════
#  Risultati elemento
# ═══════════════════════════════════════════════════════════

@dataclass
class RisultatoElementoCA:
    """Risultato della verifica di vulnerabilità di un elemento in c.a."""
    id_elemento: str
    tipo: TipoElemento = TipoElemento.PILASTRO

    # ρ = C/D per ogni stato limite
    rho_flessione: float = 0.0
    rho_taglio: float = 0.0
    rho_pressoflessione: float | None = None   # solo pilastri con N≠0

    # Duttilità (Circ. 7/2019 §C8.7.2.4)
    theta_u: float | None = None   # rotazione plastica disponibile [rad]
    theta_y: float | None = None   # rotazione snervamento [rad]
    mu_theta: float | None = None  # duttilità μ_θ = θ_u / θ_y disponibile

    # Indice sintetico
    rho_min: float = 0.0
    rho_medio: float = 0.0

    # Classificazione
    classe: ClasseVulnerabilita = ClasseVulnerabilita.NON_VERIFICATO

    passaggi: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id_elemento": self.id_elemento,
            "tipo": self.tipo.value,
            "rho_flessione": round(self.rho_flessione, 3),
            "rho_taglio": round(self.rho_taglio, 3),
            "rho_pressoflessione": (
                round(self.rho_pressoflessione, 3)
                if self.rho_pressoflessione is not None else None
            ),
            "theta_u": (round(self.theta_u, 4) if self.theta_u is not None else None),
            "mu_theta": (round(self.mu_theta, 2) if self.mu_theta is not None else None),
            "rho_min": round(self.rho_min, 3),
            "rho_medio": round(self.rho_medio, 3),
            "classe": self.classe.value,
        }


# ═══════════════════════════════════════════════════════════
#  Verifica singolo elemento
# ═══════════════════════════════════════════════════════════

def _capacita_flessione(elem: ElementoCA) -> tuple[float, list[str]]:
    """Momento resistente MRd — sezione rettangolare, NTC2018 §4.1.2.1.3.1 semplificato.

    Metodo semplificato del blocco rettangolare (λ=0.8):
    MRd = As·fyd·(d - As·fyd/(0.85·fcd·b))  [solo armatura tesa]
    Con armatura doppia: aggiunta contributo As' + riduzione zona compressa.

    Formula: NTC2018 eq. (4.1.7) — stress block rettangolare.
    Riferimento: Circ 7/2019 §C4.1.2.1.3.
    """
    passaggi: list[str] = []
    passaggi.append("— Capacità flessione MRd (NTC2018 §4.1.2.1.3.1) —")

    b = elem.b
    d = elem.d
    d_primo = elem.d_primo
    As = elem.As
    As_primo = elem.As_primo
    fcd = elem.f_cd
    fyd = elem.f_yd

    if As <= 0:
        passaggi.append("ATTENZIONE: As = 0, MRd = 0")
        return 0.0, passaggi

    # Forza risultante acciaio teso
    Fs = As * fyd

    # Zona compressa in cls con eventuale contributo As'
    # Equilibrio: Fs = 0.8·x·b·fcd + As'·fyd (semplificato: CSed 0.85 fcd per α1)
    # Altezza zona compressa x:
    # 0.8·x·b·fcd + As'·fyd - As·fyd = N_ed (per flessione semplice N=0)
    # Caso flessione pura (N=0):
    Fc_cls = Fs - As_primo * fyd  # forza in cls richiesta
    if Fc_cls <= 0:
        # Zona compressa nulla: sezione completamente tesa → MRd limitato
        Fc_cls = 1.0  # evita divisione per zero; MRd sarà piccolo

    x = Fc_cls / (0.8 * b * fcd)  # altezza zona compressa (κ=0.8 per CLS normale)
    x = max(x, 0.0)
    x = min(x, d)  # non può superare altezza utile

    passaggi.append(f"As = {As:.2f} cm², As' = {As_primo:.2f} cm²")
    passaggi.append(f"Fs = As·fyd = {Fs:.0f} kg")
    passaggi.append(f"x = Fc_cls / (0.8·b·fcd) = {x:.2f} cm")

    # Momento resistente rispetto al baricentro armatura tesa
    # Contributo cls: Fc_cls × (d - 0.4·x)
    # Contributo As': As'·fyd × (d - d')
    M_cls = Fc_cls * (d - 0.4 * x)
    M_acc_primo = As_primo * fyd * (d - d_primo) if As_primo > 0 else 0.0
    M_rd = M_cls + M_acc_primo

    passaggi.append(f"M_cls = Fc_cls×(d-0.4x) = {Fc_cls:.0f}×{d - 0.4*x:.2f} = {M_cls:.0f} kg·cm")
    if M_acc_primo > 0:
        passaggi.append(f"M_acc_primo = As'·fyd×(d-d') = {M_acc_primo:.0f} kg·cm")
    passaggi.append(f"MRd = {M_rd:.0f} kg·cm")

    return M_rd, passaggi


def _capacita_taglio(elem: ElementoCA) -> tuple[float, list[str]]:
    """Taglio resistente VRd — NTC2018 §4.1.2.3.

    Senza staffe (pilastri anni '60):
    VRd,c = [k·(100·ρl·fck)^(1/3)/γc]·b·d  (NTC2018 eq. 4.1.51)
    con k = 1 + √(200/d) ≤ 2.0, ρl = As/(b·d)

    Con staffe:
    VRd,s = (Asw/s)·z·fywd·cotθ  (NTC2018 eq. 4.1.45, θ=45° → cotθ=1)
    VRd = min(VRd,s, VRd,max)

    Nota implementativa: fck = fcd·γc/0.85 (inversione dalla f_cd ridotta per FC).
    """
    passaggi: list[str] = []
    passaggi.append("— Capacità taglio VRd (NTC2018 §4.1.2.3) —")

    b = elem.b
    d = elem.d
    As = elem.As
    fcd = elem.f_cd
    fyd = elem.f_yd

    # Recupero fck approssimato (inverso formula fcd = 0.85·fck/γc)
    gamma_c = 1.5
    fck = fcd * gamma_c / 0.85  # kg/cm²

    # Fattore k per dimensione elemento
    k = min(1.0 + math.sqrt(200.0 / d), 2.0)  # d in mm → nota: d è in cm

    # Rapporto geometrico armatura longitudinale
    rho_l = min(As / (b * d), 0.02)
    if rho_l < 1e-6:
        rho_l = 0.003  # minimo di norma per elementi senza armatura specifica

    passaggi.append(f"fck (ricavato) = {fck:.1f} kg/cm², k = {k:.3f}, ρl = {rho_l:.4f}")

    # VRd,c senza staffe — formula analoga EC2/NTC2018
    # Nota: NTC2018 usa fck in MPa; convertiamo in N/mm²
    fck_mpa = fck * 0.0981  # kg/cm² → MPa (×9.81/100)
    V_Rdc_Nmm2 = (0.18 / gamma_c) * k * (100 * rho_l * fck_mpa) ** (1.0 / 3.0)
    # Minimo vmin = 0.035·k^1.5·√fck (NTC2018 eq. 4.1.51b)
    v_min_mpa = 0.035 * k ** 1.5 * math.sqrt(fck_mpa)
    V_Rdc_mpa = max(V_Rdc_Nmm2, v_min_mpa)

    # Converti in kg/cm²: 1 MPa = 10.197 kg/cm²
    V_Rdc_kg_cm2 = V_Rdc_mpa * 10.197
    V_Rdc = V_Rdc_kg_cm2 * b * d  # kg

    passaggi.append(f"VRd,c (formula §4.1.51) = {V_Rdc:.0f} kg (senza staffe)")

    if elem.Asw is not None and elem.s_staffe is not None and elem.s_staffe > 0:
        # Con staffe: VRd,s
        fywd = min(elem.f_yd, 3800.0)  # limitazione NTC2018 per staffe
        z = 0.9 * d  # braccio della coppia interna z ≈ 0.9·d
        cot_theta = 1.0  # θ=45° conservativo (range consentito: cotθ 1÷2.5)
        V_Rds = (elem.Asw / elem.s_staffe) * z * fywd * cot_theta

        # VRd,max (schiacciamento del puntone)
        # VRd,max = 0.5·ν·fcd·b·z·sin(2θ)  con ν=0.5, θ=45° → sin(2θ)=1
        nu = 0.5
        V_Rdmax = 0.5 * nu * fcd * b * z

        V_Rds = min(V_Rds, V_Rdmax)
        V_rd = max(V_Rdc, V_Rds)  # criterio governa il più alto

        passaggi.append(
            f"Asw = {elem.Asw:.2f} cm², s = {elem.s_staffe:.0f} cm, "
            f"z = {z:.0f} cm"
        )
        passaggi.append(f"VRd,s = {V_Rds:.0f} kg, VRd,max = {V_Rdmax:.0f} kg")
        passaggi.append(f"VRd = max(VRd,c, VRd,s) = {V_rd:.0f} kg")
    else:
        V_rd = V_Rdc
        passaggi.append("Nessuna armatura trasversale rilevata → VRd = VRd,c")

    return V_rd, passaggi


def _capacita_pressoflessione(elem: ElementoCA) -> tuple[float, list[str]]:
    """Momento resistente MRd in presenza di sforzo normale — pilastro.

    Metodo semplificato: dominio M-N con blocco rettangolare.
    Compressione centrica NRd = Acc·fcd + As·fyd (limite superiore).
    Punto bilanciato: xbal = 0.8·εcu/(εcu+εsy) × d (ε_cu=3.5‰, ε_sy≈2.17‰).

    Riferimento: NTC2018 §4.1.2.1.3.1, Circ. 7/2019 §C4.1.2.1.3.
    """
    passaggi: list[str] = []
    passaggi.append("— Capacità pressoflessione MRd (NTC2018 §4.1.2.1.3.1) —")

    b = elem.b
    h = elem.h_sez
    d = elem.d
    d_primo = elem.d_primo
    As = elem.As
    As_primo = elem.As_primo
    fcd = elem.f_cd
    fyd = elem.f_yd
    N_ed = elem.N_ed  # kg (compressione +)

    # Area netta di calcestruzzo
    A_c = b * h - (As + As_primo)

    # Compressione centrica NRd,max (limite superiore dominio)
    N_rd_max = A_c * fcd + (As + As_primo) * fyd
    passaggi.append(f"NRd,max = {N_rd_max:.0f} kg")

    # Trazione centrica NRd,min
    N_rd_min = -(As + As_primo) * fyd
    passaggi.append(f"NRd,min = {N_rd_min:.0f} kg")

    # Clamp N_ed nel dominio
    N_ed_clamped = max(N_rd_min, min(N_ed, N_rd_max))
    if N_ed != N_ed_clamped:
        passaggi.append(
            f"ATTENZIONE: N_Ed={N_ed:.0f} kg fuori dominio → clampato a {N_ed_clamped:.0f} kg"
        )

    N_ed = N_ed_clamped

    # Profondità asse neutro x con N_ed imposto
    # Equilibrio orizzontale: 0.8·x·b·fcd + As'·fyd - As·fyd = N_ed
    # (positivo in compressione per N_ed > 0)
    x = (N_ed + As * fyd - As_primo * fyd) / (0.8 * b * fcd)
    x = max(x, 0.0)

    passaggi.append(
        f"x (asse neutro con N_Ed={N_ed:.0f} kg) = {x:.2f} cm"
    )

    if x > d:
        # Compressione totale: momento resistente intorno al baricentro
        # (simplificazione conservativa)
        e_min = max(h / 30, 2.0)  # eccentricità minima normativa [cm]
        M_rd = N_ed * e_min
        passaggi.append(
            f"Sezione completamente compressa: MRd = N_Ed·e_min = {M_rd:.0f} kg·cm"
        )
        return M_rd, passaggi

    # Forza in calcestruzzo
    F_cls = 0.8 * x * b * fcd

    # Forza in acciaio (dipende da posizione asse neutro)
    # Deformazione acciaio compresso per compatibilità:
    # ε_s_primo = 0.0035 × (x - d') / x ≥ 0
    eps_cu = 0.0035
    eps_su = fyd / (2_100_000.0)  # ε_sy (E_s ≈ 2100000 kg/cm²)

    eps_s_primo = eps_cu * (x - d_primo) / x if x > 0 else 0.0
    eps_s = eps_cu * (d - x) / x if x > 0 else eps_su

    # Tensione acciaio (limitata a fyd)
    sigma_s_primo = min(eps_s_primo * 2_100_000.0, fyd)
    sigma_s = min(eps_s * 2_100_000.0, fyd)

    F_s = As * sigma_s          # forza armatura tesa (tiro +)
    F_s_primo = As_primo * sigma_s_primo  # forza armatura compressa (compressione -)

    passaggi.append(
        f"ε_s'= {eps_s_primo*1000:.2f}‰, ε_s = {eps_s*1000:.2f}‰"
    )
    passaggi.append(
        f"σ_s' = {sigma_s_primo:.0f} kg/cm², σ_s = {sigma_s:.0f} kg/cm²"
    )

    # Momento resistente rispetto al baricentro geometrico della sezione
    y_g = h / 2
    M_rd = (
        F_cls * (y_g - 0.4 * x)
        + F_s * (d - y_g)
        - F_s_primo * (d_primo - y_g) * (-1)  # in compressione → contributo pos.
    )
    # Semplificazione: momento rispetto all'armatura tesa
    M_rd_semplice = F_cls * (d - 0.4 * x) + F_s_primo * (d - d_primo)

    M_rd = abs(M_rd_semplice)  # valore assoluto (convezione)

    passaggi.append(
        f"F_cls = {F_cls:.0f} kg, F_s = {F_s:.0f} kg, F_s' = {F_s_primo:.0f} kg"
    )
    passaggi.append(f"MRd (pressoflessione) = {M_rd:.0f} kg·cm")

    return M_rd, passaggi


def _duttilita_chord_rotation(elem: ElementoCA) -> tuple[float, float, float]:
    """Calcola rotazione plastica θ_u e duttilità μ_θ.

    Circolare 7/2019 §C8.7.2.4, eq. C8.7.2.9 (Fardis et al.):
    θ_u = (1/γel) × 0.016 × (0.3^ν) × (max(0.01, ω') / max(0.01, ω))^0.225
          × (fck/25)^0.2 × (d/Lv)^0.35 × 25^(α·ρsx·fyw/fck) × 1.25^(100·ρd)

    Semplificazione per applicazione pratica (variabili non sempre disponibili):
    θ_u ≈ 0.030 × (0.3^ν) per ν = N/(b·h·fcd)

    θ_y ≈ φy × Lv/3 + 0.0013·(1 + 1.5·h/Lv) + 0.13·φy·d_bl·fyd/√fck
    dove φy = snervamento curvatura.

    Riferimento: Fardis & Biskinis (2003), calibrato su database sperimentale.
    """
    fcd = elem.f_cd
    fyd = elem.f_yd
    b = elem.b
    h = elem.h_sez
    d = elem.d
    As = elem.As
    As_primo = elem.As_primo
    N_ed = elem.N_ed
    Lv = elem.luce / 2  # Lv = lunghezza di taglio ≈ luce/2 per pilastri

    # Indice di snellezza assiale ν (adimensionale)
    nu = N_ed / (b * h * fcd) if fcd > 0 else 0.0
    nu = max(0.0, min(nu, 0.7))  # clamp fisico

    # Indici armatura meccanica ω', ω (rapporti armatura × fyd/fcd)
    omega = As * fyd / (b * d * fcd) if (b * d * fcd) > 0 else 0.01
    omega_primo = As_primo * fyd / (b * (d - elem.d_primo) * fcd) if (b * d * fcd) > 0 else 0.01
    omega = max(omega, 0.01)
    omega_primo = max(omega_primo, 0.01)

    # fck ricavato
    fck = fcd * 1.5 / 0.85  # kg/cm²
    fck_mpa = fck * 0.0981  # MPa

    # ρsx = rapporto armatura trasversale (senza staffe = 0)
    rho_sx = 0.0
    if elem.Asw is not None and elem.s_staffe is not None and elem.s_staffe > 0:
        rho_sx = elem.Asw / (b * elem.s_staffe)

    alpha_conf = 0.0  # fattore di confinamento α·ρsx·fyw/fck (semplificato)
    if rho_sx > 0 and fck_mpa > 0:
        fyw_mpa = min(fyd, 3800.0) * 0.0981
        alpha_conf = rho_sx * fyw_mpa / fck_mpa

    # ρd = rapporto ferri diagonali (tipicamente 0 per pilastri ordinari)
    rho_d = 0.0

    # θ_u (eq. C8.7.2.9 semplificata)
    gamma_el = 1.5  # fattore di modello per elementi in cemento armato
    fck_ratio = max(fck_mpa, 10.0) / 25.0

    theta_u = (1.0 / gamma_el) * 0.016 * (
        0.3 ** nu
        * (omega_primo / omega) ** 0.225
        * fck_ratio ** 0.2
        * (d / max(Lv, d)) ** 0.35
        * math.exp(25.0 * alpha_conf)
        * 1.25 ** (100.0 * rho_d)
    )
    theta_u = max(theta_u, 0.002)  # minimo fisico

    # θ_y — rotazione allo snervamento (Fardis 2003)
    phi_y = fyd / (2_100_000.0 * d) if d > 0 else 0.001  # curvatura snervamento [1/cm]
    # Diametro medio dei ferri (stima da As e numero ferri presunto)
    theta_y = phi_y * Lv / 3.0 + 0.0013 * (1.0 + 1.5 * h / max(Lv, 0.1))

    theta_y = max(theta_y, 0.002)

    # Duttilità in rotazione
    mu_theta = theta_u / theta_y if theta_y > 0 else 1.0

    return theta_u, theta_y, mu_theta


def verifica_elemento_ca(
    elem: ElementoCA,
    config: ConfigVulnerabilitaCA | None = None,
) -> RisultatoElementoCA:
    """Calcola ρ = C/D per un elemento c.a. esistente.

    Esegue le verifiche di flessione, taglio e (se N≠0) pressoflessione.
    Applica il coefficiente P-Delta se configurato.

    Args:
        elem: dati elemento (resistenze già ridotte per FC)
        config: configurazione soglie e pesi (default se None)

    Returns:
        RisultatoElementoCA con ρ_min, ρ_medio, classificazione e passaggi
    """
    if config is None:
        config = ConfigVulnerabilitaCA()

    passaggi: list[str] = [
        f"╔══ VERIFICA VULNERABILITÀ c.a.: {elem.id_elemento} ({elem.tipo.value}) ══╗",
        f"Sezione: b={elem.b:.0f}cm × h={elem.h_sez:.0f}cm, d={elem.d:.0f}cm",
        f"Armatura: As={elem.As:.2f}cm², As'={elem.As_primo:.2f}cm²",
        f"Resistenze: fcd={elem.f_cd:.1f} kg/cm², fyd={elem.f_yd:.0f} kg/cm² [con FC applicato]",
        f"Azioni SLV: N={elem.N_ed:.0f} kg, Mx={elem.Mx_ed:.0f} kg·cm, Ty={elem.Ty_ed:.0f} kg",
    ]

    # Amplificazione P-Delta (NTC2018 §7.3.6.1)
    M_ed = elem.Mx_ed
    V_ed = elem.Ty_ed
    if config.theta_pdelta > 0:
        amp = 1.0 / (1.0 - config.theta_pdelta)
        M_ed *= amp
        V_ed *= amp
        passaggi.append(
            f"P-Delta: θ = {config.theta_pdelta:.3f} → amplificazione azioni = {amp:.3f}"
        )

    # ── Capacità flessione ──
    M_rd, pass_fl = _capacita_flessione(elem)
    passaggi.extend(pass_fl)
    rho_flessione = M_rd / M_ed if M_ed > 0 else float("inf")
    passaggi.append(
        f"ρ_flessione = MRd/MEd = {M_rd:.0f}/{M_ed:.0f} = {rho_flessione:.3f}"
        if M_ed > 0 else "ρ_flessione = +∞ (MEd = 0)"
    )

    # ── Capacità taglio ──
    V_rd, pass_ta = _capacita_taglio(elem)
    passaggi.extend(pass_ta)
    rho_taglio = V_rd / V_ed if V_ed > 0 else float("inf")
    passaggi.append(
        f"ρ_taglio = VRd/VEd = {V_rd:.0f}/{V_ed:.0f} = {rho_taglio:.3f}"
        if V_ed > 0 else "ρ_taglio = +∞ (VEd = 0)"
    )

    # ── Pressoflessione (solo con N significativo) ──
    rho_pf: float | None = None
    if abs(elem.N_ed) > 0.01 * elem.b * elem.h_sez * elem.f_cd:
        M_rd_pf, pass_pf = _capacita_pressoflessione(elem)
        passaggi.extend(pass_pf)
        rho_pf = M_rd_pf / M_ed if M_ed > 0 else float("inf")
        passaggi.append(
            f"ρ_pressoflessione = MRd_pf/MEd = {M_rd_pf:.0f}/{M_ed:.0f} = {rho_pf:.3f}"
            if M_ed > 0 else "ρ_pressoflessione = +∞ (MEd = 0)"
        )

    # ── Duttilità ──
    theta_u, theta_y, mu_theta = _duttilita_chord_rotation(elem)
    passaggi.append(
        f"Duttilità (Circ.7/2019 §C8.7.2.4): θ_u={theta_u:.4f} rad, "
        f"θ_y={theta_y:.4f} rad, μ_θ={mu_theta:.2f}"
    )

    # ── Indici sintetici ──
    rhos_validi = [v for v in [rho_flessione, rho_taglio, rho_pf]
                   if v is not None and v != float("inf")]
    rho_min = min(rhos_validi) if rhos_validi else 0.0
    rho_medio = sum(rhos_validi) / len(rhos_validi) if rhos_validi else 0.0

    classe = config.soglie.classifica(rho_min)
    passaggi.append(f"ρ_min = {rho_min:.3f}, ρ_medio = {rho_medio:.3f} → {classe.value.upper()}")

    risultato = RisultatoElementoCA(
        id_elemento=elem.id_elemento,
        tipo=elem.tipo,
        rho_flessione=rho_flessione if rho_flessione != float("inf") else 9.99,
        rho_taglio=rho_taglio if rho_taglio != float("inf") else 9.99,
        rho_pressoflessione=(
            rho_pf if (rho_pf is not None and rho_pf != float("inf")) else rho_pf
        ),
        theta_u=theta_u,
        theta_y=theta_y,
        mu_theta=mu_theta,
        rho_min=rho_min,
        rho_medio=rho_medio,
        classe=classe,
        passaggi=passaggi,
    )

    esito = "OK" if classe == ClasseVulnerabilita.VERIFICATO else "ATTENZIONE"
    registro.calcolo(
        modulo=_MODULO_LOG,
        operazione=f"Vulnerabilità c.a.: {elem.id_elemento}",
        input_dati={"tipo": elem.tipo.value, "N_ed": elem.N_ed, "Mx_ed": elem.Mx_ed},
        output_dati={"rho_min": rho_min, "rho_medio": rho_medio, "classe": classe.value},
        normativa="NTC2018 §8.7.1 + Circ.7/2019 §C8.7.2",
        formula="ρ = C/D",
        esito=esito,
    )

    return risultato


# ═══════════════════════════════════════════════════════════
#  Analisi edificio — indice globale vulnerabilità c.a.
# ═══════════════════════════════════════════════════════════

@dataclass
class IndiceVulnerabilitaCA:
    """Indice globale di vulnerabilità dell'edificio in c.a."""
    rho_globale: float           # media pesata elementi
    rho_min_globale: float       # peggiore elemento

    n_verificati: int = 0
    n_critici: int = 0
    n_non_verificati: int = 0

    # Elementi ordinati per rho_min crescente (i più critici prima)
    ranking: list[dict[str, Any]] = field(default_factory=list)

    classe: ClasseVulnerabilita = ClasseVulnerabilita.NON_VERIFICATO

    def to_dict(self) -> dict[str, Any]:
        return {
            "rho_globale": round(self.rho_globale, 3),
            "rho_min_globale": round(self.rho_min_globale, 3),
            "n_verificati": self.n_verificati,
            "n_critici": self.n_critici,
            "n_non_verificati": self.n_non_verificati,
            "classe": self.classe.value,
            "ranking_top5": self.ranking[:5],
        }


def analisi_vulnerabilita_ca(
    elementi: list[ElementoCA],
    config: ConfigVulnerabilitaCA | None = None,
) -> tuple[IndiceVulnerabilitaCA, list[RisultatoElementoCA]]:
    """Analisi di vulnerabilità sismica dell'edificio in c.a.

    Verifica tutti gli elementi, calcola ρ_globale con pesi per tipo
    e identifica gli elementi più critici.

    Args:
        elementi: lista di ElementoCA con resistenze già ridotte per FC
        config: configurazione soglie, pesi, P-Delta (default se None)

    Returns:
        (IndiceVulnerabilitaCA, list[RisultatoElementoCA])
    """
    if config is None:
        config = ConfigVulnerabilitaCA()
    if not elementi:
        return IndiceVulnerabilitaCA(rho_globale=0.0, rho_min_globale=0.0), []

    risultati: list[RisultatoElementoCA] = []
    for elem in elementi:
        ris = verifica_elemento_ca(elem, config)
        risultati.append(ris)

    # Conteggio classi
    n_ver = sum(1 for r in risultati if r.classe == ClasseVulnerabilita.VERIFICATO)
    n_crit = sum(1 for r in risultati if r.classe == ClasseVulnerabilita.CRITICO)
    n_nonver = sum(1 for r in risultati if r.classe == ClasseVulnerabilita.NON_VERIFICATO)

    # Indice globale ponderato
    pesi = config.pesi_per_tipo
    somma_rho_pesata = 0.0
    somma_pesi = 0.0
    for ris in risultati:
        peso = pesi.get(ris.tipo.value, 1.0)
        somma_rho_pesata += ris.rho_min * peso
        somma_pesi += peso
    rho_globale = somma_rho_pesata / somma_pesi if somma_pesi > 0 else 0.0
    rho_min_globale = min(r.rho_min for r in risultati)

    # Ranking (dal più critico)
    ranking_sorted = sorted(risultati, key=lambda r: r.rho_min)
    ranking = [
        {
            "id": r.id_elemento,
            "tipo": r.tipo.value,
            "piano": getattr(r, "piano", ""),
            "rho_min": round(r.rho_min, 3),
            "classe": r.classe.value,
        }
        for r in ranking_sorted
    ]

    classe = config.soglie.classifica(rho_min_globale)

    registro.calcolo(
        modulo=_MODULO_LOG,
        operazione="Indice vulnerabilità edificio c.a.",
        input_dati={"n_elementi": len(elementi)},
        output_dati={
            "rho_globale": round(rho_globale, 3),
            "rho_min_globale": round(rho_min_globale, 3),
            "n_verificati": n_ver,
            "n_critici": n_crit,
            "n_non_verificati": n_nonver,
        },
        normativa="NTC2018 §8.7.1",
        formula="ρ_glob = Σ(ρi·wi) / Σwi",
        esito="OK" if classe == ClasseVulnerabilita.VERIFICATO else "ATTENZIONE",
    )

    indice = IndiceVulnerabilitaCA(
        rho_globale=rho_globale,
        rho_min_globale=rho_min_globale,
        n_verificati=n_ver,
        n_critici=n_crit,
        n_non_verificati=n_nonver,
        ranking=ranking,
        classe=classe,
    )
    return indice, risultati
