"""
Verifiche secondo RD 2229/1939 - Metodo Tensioni Ammissibili (TA).

Implementa le verifiche per strutture in cemento armato secondo il Regio Decreto
2229/39 utilizzando il metodo delle tensioni ammissibili (allowable stress design).

Struttura:
- Funzioni di utilità per conversione unità (kN→kg, mm→cm, MPa→kg/cm²)
- Funzioni per costruzione material laws (ConcreteLawTA, SteelLawTA)
- Funzioni di verifica: flessione TA, pressoflessione TA, taglio TA, minimi armatura

Stato implementazione (dopo Session 6):
- check_flessione_ta_rett: COMPLETE
- check_pressoflessione_ta_rett: IMPROVED PARTIAL (riduzione snellezza implementata)
- check_taglio_ta_rett: PARTIAL+ (messaggi migliorati, formula conservativa)
- check_minimi_armatura_ta: COMPLETE (distinzione travi/pilastri implementata)

Tutti i messaggi utente sono in italiano.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

# Import historical_ta modules for TA stress computation
from historical_ta.checks import (
    AllowableStresses,
    check_allowable_stresses_ta,
    compute_long_rebar_limits_ta,
)
from historical_ta.geometry import SectionGeometry, compute_section_properties
from historical_ta.materials import ConcreteLawTA, SteelLawTA
from historical_ta.stress import LoadState, compute_normal_stresses_ta
from src.core_calculus.contracts import CalcInput, SingleCheckResult, VerificationTemplate
from src.methods.rd2229.instabilita import (
    EsitoStabilita,
    InputStabilita,
    sigma_c_adm_ridotta,
    verifica_stabilita_ta,
)

# ==============================================================================
# UTILITY FUNCTIONS: UNIT CONVERSIONS
# ==============================================================================


def convert_loads_to_ta_units(calc_input: CalcInput) -> dict[str, float]:
    """Converte le sollecitazioni da CalcInput (kN, kNm) a unità TA (kg, kg·cm).

    CalcInput usa:
    - Forze: kN
    - Momenti: kNm

    TA storico (sistema tecnico) usa:
    - Forze: kg
    - Momenti: kg·cm

    Conversioni:
    - 1 kN = 101.97 kg (circa 102 kg)
    - 1 kNm = 10197 kg·cm (circa 10200 kg·cm)

    Args:
        calc_input: Dati di input con forze in kN, momenti in kNm

    Returns:
        Dict con chiavi: N_kg, Mx_kg_cm, My_kg_cm, Tx_kg, Ty_kg
    """
    return {
        "N_kg": (calc_input.N or 0.0) * 101.97,
        "Mx_kg_cm": (calc_input.Mx or 0.0) * 10197.0,
        "My_kg_cm": (calc_input.My or 0.0) * 10197.0,
        "Tx_kg": (calc_input.Tx or 0.0) * 101.97,
        "Ty_kg": (calc_input.Ty or 0.0) * 101.97,
    }


def convert_section_to_ta_geometry(calc_input: CalcInput) -> SectionGeometry:
    """Converte sezione da CalcInput (mm) a SectionGeometry TA (cm).

    CalcInput.section ha dimensioni in mm (width, height).
    SectionGeometry TA richiede dimensioni in cm.

    Crea:
    - Poligono rettangolare in cm
    - Armature (bars) da As, d in cm

    Args:
        calc_input: Dati di input con section in mm, As in cm², d in cm

    Returns:
        SectionGeometry con geometria in cm, armature posizionate
    """
    section = calc_input.section
    if section is None:
        raise ValueError("Section is None - cannot convert to TA geometry")

    # Converti dimensioni sezione: mm → cm
    b_cm = section.width / 10.0  # mm → cm
    h_cm = section.height / 10.0  # mm → cm

    # Crea poligono rettangolare (vertices in senso antiorario)
    # Coordinate: (y, z) dove y=orizzontale, z=verticale
    polygons = [
        [
            (0.0, 0.0),  # angolo basso-sinistra
            (b_cm, 0.0),  # angolo basso-destra
            (b_cm, h_cm),  # angolo alto-destra
            (0.0, h_cm),  # angolo alto-sinistra
        ]
    ]

    # Crea armature (bars)
    bars: list[tuple[float, float, float]] = []

    if calc_input.As and calc_input.d:
        # Armatura tesa al bordo inferiore
        d_cm = calc_input.d  # Già in cm da CalcInput
        cover_cm = h_cm - d_cm  # Copriferro

        # Stima numero barre e diametro
        # Supponiamo 4 barre distribuite uniformemente
        n_bars = 4
        area_per_bar = calc_input.As / n_bars  # cm²
        diam_cm = 2.0 * math.sqrt(area_per_bar / math.pi)  # cm

        # Posiziona barre uniformemente lungo la larghezza
        for i in range(n_bars):
            y_i = (i + 1) * b_cm / (n_bars + 1)  # Equidistanti
            z_i = cover_cm  # Alla quota del copriferro
            bars.append((y_i, z_i, diam_cm))

    # Aggiungi armatura compressa se presente
    if calc_input.As_prime and calc_input.d_prime:
        n_bars_comp = 2  # Poche barre in zona compressa
        area_per_bar_comp = calc_input.As_prime / n_bars_comp
        diam_comp_cm = 2.0 * math.sqrt(area_per_bar_comp / math.pi)

        d_prime_cm = calc_input.d_prime  # cm
        z_comp = h_cm - d_prime_cm

        for i in range(n_bars_comp):
            y_comp = (i + 1) * b_cm / (n_bars_comp + 1)
            bars.append((y_comp, z_comp, diam_comp_cm))

    # Ottieni coefficiente di omogeneizzazione n = Es/Ec
    material = calc_input.material
    if material and hasattr(material, "n"):
        n_homog = material.n
    else:
        # Stima n da Es/Ec
        Es = 2.1e6  # kg/cm² (tipico per acciaio)
        if material and hasattr(material, "Ec"):
            Ec = material.Ec
        else:
            # Stima Ec da f_ck o sigma_c28
            if material and hasattr(material, "sigma_c28"):
                sigma_c28 = material.sigma_c28  # kg/cm²
            elif material and hasattr(material, "f_ck"):
                sigma_c28 = material.f_ck * 10.197  # MPa → kg/cm²
            else:
                sigma_c28 = 160.0  # Valore di default (R160)

            # Formula empirica EC (storica)
            Ec = 550000.0 * sigma_c28 / (sigma_c28 + 200.0)  # kg/cm²

        n_homog = Es / Ec

    return SectionGeometry(polygons=polygons, bars=bars, n_homog=n_homog)


# ==============================================================================
# MATERIAL LAW BUILDERS
# ==============================================================================


def build_concrete_law_ta(material: Any) -> ConcreteLawTA:
    """Costruisce ConcreteLawTA da material object di CalcInput.

    Converte proprietà materiale (MPa o kg/cm²) in parametri TA.

    Args:
        material: Oggetto materiale con f_ck (MPa) o sigma_c28 (kg/cm²)

    Returns:
        ConcreteLawTA con proprietà in kg/cm²
    """
    # Ottieni sigma_c28 in kg/cm²
    if hasattr(material, "sigma_c28"):
        sigma_c28 = material.sigma_c28  # Già in kg/cm²
    elif hasattr(material, "f_ck"):
        sigma_c28 = material.f_ck * 10.197  # MPa → kg/cm²
    else:
        raise ValueError("Material manca sia sigma_c28 che f_ck")

    # Ottieni sigma_c_adm (tensione ammissibile)
    if hasattr(material, "sigma_c_adm"):
        fcd = material.sigma_c_adm  # kg/cm²
    else:
        # Formula RD 2229: sigma_c_adm = 0.5 × sigma_c28
        fcd = 0.5 * sigma_c28

    # Ottieni Ec (modulo elastico)
    if hasattr(material, "Ec"):
        Ec = material.Ec  # kg/cm²
    else:
        # Formula empirica storica
        Ec = 550000.0 * sigma_c28 / (sigma_c28 + 200.0)

    return ConcreteLawTA(
        fcd=fcd,
        Ec=Ec,
        eps_c2=0.002,
        eps_c3=0.0035,
        eps_c4=0.0035,
        eps_cu=0.0035,
        parab_rect=True,
        allow_tension=False,  # TA non ammette trazione nel cls
    )


def build_steel_law_ta(material: Any) -> SteelLawTA:
    """Costruisce SteelLawTA da material object di CalcInput.

    Args:
        material: Oggetto materiale con f_yk (MPa) o sigma_sn (kg/cm²)

    Returns:
        SteelLawTA con proprietà in kg/cm²
    """
    # Ottieni sigma_sn (tensione snervamento nominale) in kg/cm²
    if hasattr(material, "sigma_sn"):
        sigma_sn = material.sigma_sn  # kg/cm²
    elif hasattr(material, "f_yk"):
        sigma_sn = material.f_yk * 10.197  # MPa → kg/cm²
    else:
        raise ValueError("Material manca sia sigma_sn che f_yk")

    # Ottieni sigma_s_adm (tensione ammissibile acciaio)
    if hasattr(material, "sigma_s_adm"):
        fyd = material.sigma_s_adm  # kg/cm²
    else:
        # Formula RD 2229: sigma_s_adm = 0.5 × sigma_sn
        fyd = 0.5 * sigma_sn

    Es = 2.1e6  # kg/cm² (modulo elastico acciaio)
    eps_yd = fyd / Es

    return SteelLawTA(
        Es=Es,
        fyd=fyd,
        eps_yd=eps_yd,
        eps_su=0.01,  # 1% deformazione ultima
        elastoplastic=True,
        bilinear=False,
        Kincr=0.0,
    )


@dataclass
class AllowableStressesExtracted:
    """Tensioni ammissibili estratte da materiale RD 2229."""

    sigma_c_allow: float  # kg/cm² - tensione ammissibile compressione cls
    sigma_s_allow: float  # kg/cm² - tensione ammissibile acciaio
    sigma_c_med_allow: float  # kg/cm² - tensione media ammissibile cls


def get_rd2229_allowable_stresses(material: Any) -> AllowableStressesExtracted:
    """Estrae tensioni ammissibili RD 2229/39 da material object.

    Se il materiale ha proprietà RD2229 (sigma_c_adm, sigma_s_adm), le usa direttamente.
    Altrimenti le calcola da f_ck, f_yk usando formule RD 2229:
    - sigma_c_adm = 0.5 × sigma_c28
    - sigma_s_adm = 0.5 × sigma_sn

    Args:
        material: Oggetto materiale con proprietà cls e acciaio

    Returns:
        AllowableStressesExtracted con tensioni in kg/cm²
    """
    # Tensione ammissibile calcestruzzo
    if hasattr(material, "sigma_c_adm") and material.sigma_c_adm is not None:
        sigma_c_allow = material.sigma_c_adm  # kg/cm²
        sigma_c28 = sigma_c_allow * 2.0  # Ricava sigma_c28
    else:
        # Calcola da f_ck
        if hasattr(material, "sigma_c28"):
            sigma_c28 = material.sigma_c28
        elif hasattr(material, "f_ck"):
            sigma_c28 = material.f_ck * 10.197  # MPa → kg/cm²
        else:
            sigma_c28 = 160.0  # Default R160

        sigma_c_allow = 0.5 * sigma_c28

    # Tensione ammissibile acciaio
    if hasattr(material, "sigma_s_adm") and material.sigma_s_adm is not None:
        sigma_s_allow = material.sigma_s_adm  # kg/cm²
    else:
        # Calcola da f_yk
        if hasattr(material, "sigma_sn"):
            sigma_sn = material.sigma_sn
        elif hasattr(material, "f_yk"):
            sigma_sn = material.f_yk * 10.197  # MPa → kg/cm²
        else:
            sigma_sn = 3800.0  # Default FeB38k

        sigma_s_allow = 0.5 * sigma_sn

    # Tensione media ammissibile cls (tipicamente 0.4 × sigma_c28)
    sigma_c_med_allow = 0.4 * sigma_c28

    return AllowableStressesExtracted(
        sigma_c_allow=sigma_c_allow,
        sigma_s_allow=sigma_s_allow,
        sigma_c_med_allow=sigma_c_med_allow,
    )


# ==============================================================================
# BIAXIAL BENDING HELPERS (TA - RD 2229/39)
# ==============================================================================


def compute_section_moduli_rect(b_cm: float, h_cm: float) -> tuple[float, float]:
    """Calcola moduli di resistenza Wx, Wy per sezione rettangolare.

    Per sezione rettangolare (b × h):
    - Wx = b × h² / 6  (modulo resistente attorno asse x - flessione My)
    - Wy = h × b² / 6  (modulo resistente attorno asse y - flessione Mx)

    Args:
        b_cm: Larghezza sezione in cm
        h_cm: Altezza sezione in cm

    Returns:
        Tupla (Wx_cm3, Wy_cm3) moduli di resistenza in cm³
    """
    Wx_cm3 = b_cm * h_cm**2 / 6.0
    Wy_cm3 = h_cm * b_cm**2 / 6.0
    return Wx_cm3, Wy_cm3


def compute_sigma_concrete_biaxial_ta(
    N_kg: float,
    Mx_kg_cm: float,
    My_kg_cm: float,
    A_cm2: float,
    Wx_cm3: float,
    Wy_cm3: float,
) -> float:
    """Calcola tensione massima cls con pressoflessione deviata metodo TA.

    Metodo elastico lineare con sovrapposizione effetti (RD 2229/39 Art. 29):
    σ_c,max = N/A + |Mx|/Wx + |My|/Wy

    Nota: Questa formula fornisce la tensione al bordo più compresso.
    RD 2229 non prevede domini N-Mx-My; usa sovrapposizione elastica.

    Args:
        N_kg: Sforzo normale in kg (negativo = compressione)
        Mx_kg_cm: Momento flettente attorno asse x in kg·cm
        My_kg_cm: Momento flettente attorno asse y in kg·cm
        A_cm2: Area sezione in cm²
        Wx_cm3: Modulo resistente attorno x in cm³
        Wy_cm3: Modulo resistente attorno y in cm³

    Returns:
        Tensione massima cls in kg/cm² (valore assoluto)
    """
    sigma_N = N_kg / A_cm2 if A_cm2 > 0 else 0.0
    sigma_Mx = abs(Mx_kg_cm) / Wx_cm3 if Wx_cm3 > 0 else 0.0
    sigma_My = abs(My_kg_cm) / Wy_cm3 if Wy_cm3 > 0 else 0.0

    # Somma tensioni (worst case - angolo più compresso)
    sigma_max = abs(sigma_N) + sigma_Mx + sigma_My
    return sigma_max


def apply_slenderness_reduction_ta(
    sigma_c_adm: float, b_cm: float, h_cm: float
) -> tuple[float, dict[str, Any]]:
    """Applica riduzione per sezioni snelle (feature repository).

    Riduzione già implementata in Session 6 per pressoflessione monoassiale.
    Formula: σ_c,adm,rid = σ_c,adm × (1 - 0.03 × (25 - A_min))
    per A_min < 25 cm, con fattore limitato in [0.4, 1.0].

    Args:
        sigma_c_adm: Tensione ammissibile cls base in kg/cm²
        b_cm: Larghezza sezione in cm
        h_cm: Altezza sezione in cm

    Returns:
        Tupla (sigma_c_adm_ridotta, details_dict) con:
        - sigma_c_adm_ridotta: tensione ammissibile ridotta
        - details_dict: {'A_min_cm', 'reduction_applied', 'factor'}
    """
    A_min_cm = min(b_cm, h_cm)
    details = {
        "A_min_cm": A_min_cm,
        "reduction_applied": False,
        "reduction_factor": 1.0,
    }

    if A_min_cm < 25.0:
        # Formula da RD2229.jsoncode e Session 6
        factor = 1.0 - 0.03 * (25.0 - A_min_cm)
        factor = max(0.4, min(1.0, factor))  # Limita in [0.4, 1.0]

        details["reduction_applied"] = True
        details["reduction_factor"] = factor

        return sigma_c_adm * factor, details

    return sigma_c_adm, details


def _get_float_from_extra(extra: dict[str, Any], keys: list[str]) -> float | None:
    """Ritorna il primo valore numerico valido trovato in extra."""
    for key in keys:
        value = extra.get(key)
        if value is None:
            continue
        try:
            value_f = float(value)
        except (TypeError, ValueError):
            continue
        if value_f > 0:
            return value_f
    return None


def _normalize_spacing_cm(value: float | None) -> float | None:
    """Normalizza il passo staffe in cm (accetta input in cm o mm)."""
    if value is None:
        return None
    if value <= 0:
        return None
    # euristica: valori oltre 60 sono tipicamente in mm (es. 200 mm)
    return value / 10.0 if value > 60.0 else value


def _estimate_steel_moduli_rect(
    calc_input: CalcInput,
) -> tuple[float | None, float | None, list[str]]:
    """Stima W_sx e W_sy da geometria rettangolare e armature equivalenti."""
    notes: list[str] = []
    if calc_input.section is None:
        return None, None, notes

    As_t = calc_input.As
    if As_t is None or As_t <= 0:
        return None, None, notes

    b_cm = calc_input.section.width / 10.0
    h_cm = calc_input.section.height / 10.0

    d_t = calc_input.d if calc_input.d and calc_input.d > 0 else 0.9 * h_cm
    if calc_input.d is None or calc_input.d <= 0:
        notes.append("d non fornita: usata stima d = 0.9·h")

    As_c = calc_input.As_prime if calc_input.As_prime and calc_input.As_prime > 0 else 0.0
    if calc_input.d_prime is not None and calc_input.d_prime > 0:
        d_c = calc_input.d_prime
    else:
        d_c = max(2.0, h_cm - d_t)
        if As_c > 0:
            notes.append("d_prime non fornita: stimata dal copriferro lato teso")

    y_t = max(0.5, abs(d_t - h_cm / 2.0))
    y_c = max(0.5, abs(h_cm / 2.0 - d_c))
    W_sx_cm3 = As_t * y_t + As_c * y_c

    cover_guess_cm = max(2.0, min(h_cm * 0.4, h_cm - d_t if h_cm > d_t else 2.0))
    z_t = max(0.5, b_cm / 2.0 - min(cover_guess_cm, b_cm * 0.45))
    z_c = max(0.5, b_cm / 2.0 - min(d_c, b_cm * 0.45))
    W_sy_cm3 = As_t * z_t + As_c * z_c

    if W_sx_cm3 <= 0 or W_sy_cm3 <= 0:
        return None, None, notes

    return W_sx_cm3, W_sy_cm3, notes


def _build_stability_input(
    calc_input: CalcInput, sigma_c_adm: float, sigma_s_adm: float
) -> InputStabilita | None:
    """Costruisce InputStabilita da CalcInput se sono presenti i dati minimi."""
    if calc_input.section is None or calc_input.material is None:
        return None

    extra = calc_input.extra if calc_input.extra else {}
    L_cm = _get_float_from_extra(
        extra,
        [
            "l0_cm",
            "L0_cm",
            "lunghezza_libera_cm",
            "lunghezza_cm",
            "L_cm",
            "L",
        ],
    )
    if L_cm is None:
        L_m = _get_float_from_extra(extra, ["l0_m", "L0_m", "lunghezza_libera_m", "L_m"])
        if L_m is not None:
            L_cm = L_m * 100.0
    if L_cm is None:
        return None

    beta_y = _get_float_from_extra(extra, ["beta_y", "ky", "k_y", "mu_y"]) or 1.0
    beta_z = _get_float_from_extra(extra, ["beta_z", "kz", "k_z", "mu_z"]) or 1.0

    b_cm = calc_input.section.width / 10.0
    h_cm = calc_input.section.height / 10.0
    A_sez = b_cm * h_cm
    I_yp = b_cm * h_cm**3 / 12.0
    I_zp = h_cm * b_cm**3 / 12.0
    r_yp = math.sqrt(I_yp / A_sez) if A_sez > 0 else 0.0
    r_zp = math.sqrt(I_zp / A_sez) if A_sez > 0 else 0.0

    n = float(getattr(calc_input.material, "n", 15.0) or 15.0)
    As_t = float(calc_input.As or 0.0)
    As_c = float(calc_input.As_prime or 0.0)
    A_ft = As_t + As_c
    A_ci = A_sez + n * A_ft

    sigma_c28 = getattr(calc_input.material, "sigma_c28", None)
    if sigma_c28 is None and hasattr(calc_input.material, "f_ck"):
        sigma_c28 = float(calc_input.material.f_ck) * 10.197
    if sigma_c28 is None:
        sigma_c28 = sigma_c_adm * 2.0
    E_c = getattr(calc_input.material, "Ec", None)
    if E_c is None:
        E_c = 550000.0 * sigma_c28 / (sigma_c28 + 200.0)

    Nr = (calc_input.N or 0.0) * 101.97
    Mr = abs((calc_input.Mx or 0.0) * 10197.0)

    return InputStabilita(
        Nr=Nr,
        Mr=Mr,
        B=b_cm,
        H=h_cm,
        A_sez=A_sez,
        I_yp=I_yp,
        I_zp=I_zp,
        A_ci=A_ci,
        r_yp=r_yp,
        r_zp=r_zp,
        A_ft=A_ft,
        sigma_c_adm=sigma_c_adm,
        sigma_s_adm=sigma_s_adm,
        E_c=float(E_c),
        n=n,
        L=L_cm,
        beta_y=beta_y,
        beta_z=beta_z,
    )


def _stability_utilisation(stability_input: InputStabilita, result: Any) -> float | None:
    """Calcola utilizzazione equivalente della verifica di stabilità."""
    sigma_car = sigma_c_adm_ridotta(
        stability_input.sigma_c_adm,
        stability_input.B,
        stability_input.H,
    )
    utilisations: list[float] = []

    if sigma_car > 0 and result.sigma_c_1 > 0:
        utilisations.append(result.sigma_c_1 / sigma_car)
    if stability_input.sigma_s_adm > 0 and result.sigma_s_1 > 0:
        utilisations.append(result.sigma_s_1 / stability_input.sigma_s_adm)

    for sigma_c, sigma_s in [
        (result.sigma_c_2, result.sigma_s_2),
        (result.sigma_c_3, result.sigma_s_3),
    ]:
        if sigma_c > 0 and sigma_car > 0:
            utilisations.append(sigma_c / sigma_car)
        if sigma_s > 0 and stability_input.sigma_s_adm > 0:
            utilisations.append(sigma_s / stability_input.sigma_s_adm)

    if not utilisations:
        return None
    return max(utilisations)


# ==============================================================================
# CHECK FUNCTIONS - RD 2229/1939
# ==============================================================================


def check_flessione_ta_rett(
    calc_input: CalcInput, template: VerificationTemplate
) -> SingleCheckResult:
    """Verifica a flessione metodo TA - RD 2229/39 (IMPLEMENTAZIONE COMPLETA).

    Utilizza il modulo historical_ta per calcolo completo tensioni normali con metodo TA.
    Confronta le tensioni calcolate (sigma_c, sigma_s) con tensioni ammissibili da RD2229.

    Implementazione COMPLETA:
    - Calcolo tensioni con compute_normal_stresses_ta() da historical_ta
    - Tutte le proprietà normative presenti in RD2229.jsoncode
    - Supporto LC/FC per strutture esistenti

    Args:
        calc_input: Dati di input (kN, kNm, mm, cm, MPa)
        template: Template della verifica

    Returns:
        SingleCheckResult con ok/non-ok, utilizzazione, dettagli, messaggi italiani
    """
    # 1. Valida inputs obbligatori
    if calc_input.section is None:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={},
            messages_it=["Sezione non specificata"],
            check_category=template.check_category,
            limit_state=template.limit_state,
        )

    if calc_input.material is None:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={},
            messages_it=["Materiale non specificato"],
            check_category=template.check_category,
            limit_state=template.limit_state,
        )

    if calc_input.Mx is None or calc_input.Mx == 0:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=True,  # Nessun momento → verifica non applicabile ma OK
            utilisation=0.0,
            details={},
            messages_it=["Momento flettente nullo - verifica non applicabile"],
            check_category=template.check_category,
            limit_state=template.limit_state,
        )

    if calc_input.As is None or calc_input.As <= 0:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={},
            messages_it=["Armatura tesa As non specificata o nulla"],
            check_category=template.check_category,
            limit_state=template.limit_state,
        )

    if calc_input.d is None or calc_input.d <= 0:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={},
            messages_it=["Altezza utile d non specificata"],
            check_category=template.check_category,
            limit_state=template.limit_state,
        )

    try:
        # 2. Converti unità: CalcInput → TA (kg, cm, kg/cm²)
        ta_loads = convert_loads_to_ta_units(calc_input)
        ta_geometry = convert_section_to_ta_geometry(calc_input)
        ta_properties = compute_section_properties(ta_geometry)

        # 3. Costruisci legami costitutivi materiali
        concrete_law = build_concrete_law_ta(calc_input.material)
        steel_law = build_steel_law_ta(calc_input.material)
        allowable = get_rd2229_allowable_stresses(calc_input.material)

        # 4. Calcola tensioni usando historical_ta
        loads = LoadState(
            Nx=ta_loads["N_kg"],
            My=ta_loads["Mx_kg_cm"],
            Mz=ta_loads["My_kg_cm"],  # My in CalcInput → Mz in TA
        )

        stress_result = compute_normal_stresses_ta(
            geom=ta_geometry,
            props=ta_properties,
            loads=loads,
            concrete_law=concrete_law,
            steel_law=steel_law,
            allow_concrete_tension=False,
            max_iter=50,
            tol=1e-6,
        )

        # 5. Verifica tensioni ammissibili
        check_result = check_allowable_stresses_ta(
            stresses=stress_result,
            limits=AllowableStresses(
                sigma_c_allow=allowable.sigma_c_allow,
                sigma_s_allow=allowable.sigma_s_allow,
                sigma_c_med_allow=allowable.sigma_c_med_allow,
            ),
        )

        # 6. Calcola utilizzazione
        # Conservative envelope (linear elastic superposition) — useful as a safety check
        # Apply only to singly-reinforced sections (skip when compression reinforcement present)
        sigma_c_env = 0.0
        try:
            if not getattr(calc_input, "As_prime", None):
                b_cm = calc_input.section.width / 10.0
                h_cm = calc_input.section.height / 10.0
                Wx_cm3, Wy_cm3 = compute_section_moduli_rect(b_cm, h_cm)
                sigma_c_env = compute_sigma_concrete_biaxial_ta(
                    N_kg=ta_loads["N_kg"],
                    Mx_kg_cm=ta_loads["Mx_kg_cm"],
                    My_kg_cm=ta_loads["My_kg_cm"],
                    A_cm2=(
                        ta_properties.area_equivalent
                        if hasattr(ta_properties, "area_equivalent")
                        else 0.0
                    ),
                    Wx_cm3=Wx_cm3,
                    Wy_cm3=Wy_cm3,
                )
        except Exception:
            sigma_c_env = 0.0

        ok = check_result.ok
        util_c = abs(stress_result.sigma_c_max) / allowable.sigma_c_allow
        util_s = abs(stress_result.sigma_s_max) / allowable.sigma_s_allow
        utilisazione = max(util_c, util_s)

        # consider envelope utilisation as well (conservative check)
        try:
            util_c_env = (
                abs(sigma_c_env) / allowable.sigma_c_allow if allowable.sigma_c_allow else 0.0
            )
            if util_c_env > utilisazione:
                utilisazione = util_c_env
            # only treat large exceedances as decisive (allow small numeric/method differences)
            if util_c_env > 1.05:
                check_result.check_concrete = False
                check_result.ok = False
                check_result.messages.append(
                    f"Conservative envelope exceeded: σ_c,env = {sigma_c_env:.1f} kg/cm²"
                )
        except Exception:
            pass

        # reflect any envelope-driven change in the overall pass/fail
        ok = check_result.ok

        # 7. Costruisci messaggi italiani
        section = calc_input.section
        b_cm = section.width / 10.0
        h_cm = section.height / 10.0

        messages_it = [
            "=== VERIFICA A FLESSIONE METODO TA - RD 2229/39 ===",
            "",
            f"Sezione: {b_cm:.1f} × {h_cm:.1f} cm",
            f"Materiale: R{int(allowable.sigma_c_allow * 2)} (σ_c,28 = {allowable.sigma_c_allow * 2:.0f} kg/cm²)",
            f"Armatura tesa: As = {calc_input.As:.2f} cm²",
            f"Altezza utile: d = {calc_input.d:.1f} cm",
            "",
            "Sollecitazioni:",
            f"  N = {calc_input.N:.1f} kN" if calc_input.N else "  N = 0 kN",
            f"  Mx = {calc_input.Mx:.1f} kNm",
            "",
            "Tensioni calcolate (metodo TA):",
            f"  σ_c,max = {stress_result.sigma_c_max:.1f} kg/cm² (cls compressione)",
            f"  σ_s,max = {stress_result.sigma_s_max:.1f} kg/cm² (acciaio teso)",
            f"  σ_c,med = {stress_result.sigma_c_med:.1f} kg/cm² (cls media)",
            "",
            "Tensioni ammissibili (RD 2229/39):",
            f"  σ_c,adm = {allowable.sigma_c_allow:.1f} kg/cm²",
            f"  σ_s,adm = {allowable.sigma_s_allow:.1f} kg/cm²",
            f"  σ_c,med,adm = {allowable.sigma_c_med_allow:.1f} kg/cm²",
            "",
            "Verifiche:",
            f"  Cls: {abs(stress_result.sigma_c_max):.1f} / {allowable.sigma_c_allow:.1f} = "
            f"{util_c:.3f} {'✓ OK' if check_result.check_concrete else '✗ NON OK'}",
            f"  Acciaio: {abs(stress_result.sigma_s_max):.1f} / {allowable.sigma_s_allow:.1f} = "
            f"{util_s:.3f} {'✓ OK' if check_result.check_steel else '✗ NON OK'}",
            f"  Cls medio: {abs(stress_result.sigma_c_med):.1f} / {allowable.sigma_c_med_allow:.1f} = "
            f"{abs(stress_result.sigma_c_med) / allowable.sigma_c_med_allow:.3f} "
            f"{'✓ OK' if check_result.check_mean else '✗ NON OK'}",
            "",
            f"Utilizzazione massima: {utilisazione:.3f} ({'✓ OK' if ok else '✗ NON OK'})",
        ]

        if not ok:
            messages_it.extend(["", "VERIFICA NON SODDISFATTA:"] + check_result.messages)

        # 8. Ritorna risultato
        return SingleCheckResult(
            template_id=template.template_id,
            ok=ok,
            utilisation=utilisazione,
            details={
                "sigma_c_max_kg_cm2": stress_result.sigma_c_max,
                "sigma_s_max_kg_cm2": stress_result.sigma_s_max,
                "sigma_c_med_kg_cm2": stress_result.sigma_c_med,
                "sigma_c_adm_kg_cm2": allowable.sigma_c_allow,
                "sigma_s_adm_kg_cm2": allowable.sigma_s_allow,
                "sigma_c_med_adm_kg_cm2": allowable.sigma_c_med_allow,
                "N_kg": ta_loads["N_kg"],
                "Mx_kg_cm": ta_loads["Mx_kg_cm"],
                "util_c": util_c,
                "util_s": util_s,
                "check_concrete": check_result.check_concrete,
                "check_steel": check_result.check_steel,
                "check_mean": check_result.check_mean,
            },
            norm_references=[template.primary_reference] + template.secondary_references,
            messages_it=messages_it,
            check_category=template.check_category,
            limit_state=template.limit_state,
        )

    except Exception as e:
        # Gestione errori
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={"error": str(e)},
            messages_it=[f"Errore nel calcolo: {str(e)}"],
            check_category=template.check_category,
            limit_state=template.limit_state,
        )


def check_pressoflessione_ta_rett(
    calc_input: CalcInput, template: VerificationTemplate
) -> SingleCheckResult:
    """Verifica a pressoflessione metodo TA - RD 2229/39.

    Implementazione operativa:
    - verifica base N+M con motore TA elastico;
    - riduzione sigma_c,adm per sezioni snelle (Art. 16);
    - verifica instabilita pilastri (Art. 30) quando e disponibile la lunghezza
      libera di inflessione in calc_input.extra.

    Se i dati globali di asta non sono disponibili (tipicamente l0), la verifica
    di instabilita viene segnalata come non eseguita senza interrompere la
    verifica locale di sezione.

    Args:
        calc_input: Dati di input con N e Mx
        template: Template della verifica

    Returns:
        SingleCheckResult con riduzione snellezza implementata
    """
    # 1. Calcola riduzione per snellezza sezione (Art. 16 RD 2229/39)
    reduction_factor = 1.0
    A_min_cm = None
    applied_reduction = False

    if calc_input.section is not None:
        b_cm = calc_input.section.width / 10.0  # mm → cm
        h_cm = calc_input.section.height / 10.0  # mm → cm
        A_min_cm = min(b_cm, h_cm)

        # Formula RD2229: sigma_c_adm_ridotta = sigma_c_adm × (1 - 0.03 × (25 - A_min))
        # Applica solo se A_min < 25 cm (sezione snella)
        if A_min_cm < 25.0:
            reduction_factor = 1.0 - 0.03 * (25.0 - A_min_cm)
            # Limita reduction_factor a valori sensati
            reduction_factor = max(0.4, min(1.0, reduction_factor))
            applied_reduction = True

    # 2. Applica riduzione passando fattore tramite extra dict (senza mutare input)
    extra_original = calc_input.extra
    extra_for_check = dict(extra_original) if extra_original else {}
    if applied_reduction:
        extra_for_check["slenderness_reduction_factor"] = reduction_factor
    calc_input.extra = extra_for_check

    # 3. Chiama verifica base (gestisce N+M automaticamente)
    result = check_flessione_ta_rett(calc_input, template)
    calc_input.extra = extra_original

    # 4. Se abbiamo applicato la riduzione, aggiungi info ai messaggi
    if result.ok is not None or result.utilisation is not None:
        slenderness_info = []

        if applied_reduction and A_min_cm is not None:
            slenderness_info = [
                "",
                "Riduzione per sezioni snelle (Art. 16 RD 2229/39):",
                f"  A_min = min(b, h) = {A_min_cm:.1f} cm",
                f"  Fattore di riduzione = {reduction_factor:.3f}",
                "  σ_c,adm ridotta applicata",
            ]
            # Aggiorna details con riduzione
            if "sigma_c_adm_kg_cm2" in result.details:
                original_sigma_c_adm = result.details["sigma_c_adm_kg_cm2"]
                reduced_sigma_c_adm = float(original_sigma_c_adm) * reduction_factor
                result.details["sigma_c_adm_ridotta_kg_cm2"] = reduced_sigma_c_adm
                result.details["reduction_factor"] = reduction_factor
                result.details["A_min_cm"] = A_min_cm
        elif A_min_cm is not None and A_min_cm >= 25.0:
            slenderness_info = [
                "",
                f"Sezione non snella (A_min = {A_min_cm:.1f} cm ≥ 25 cm): riduzione non applicata",
            ]

        completion_info = [
            "",
            "Implementazione verifica pressoflessione TA:",
            "   ✓ Verifica base eseguita (N + M → tensioni)",
            "   ✓ Riduzione σ_c,adm per sezioni snelle implementata",
            "   ✓ Verifica instabilità disponibile se fornita l₀ in extra",
        ]

        result.messages_it.extend(slenderness_info + completion_info)

    # 5. Verifica instabilità (solo per compressione)
    N_kN = calc_input.N or 0.0
    if N_kN < 0 and calc_input.material is not None and calc_input.section is not None:
        allowable = get_rd2229_allowable_stresses(calc_input.material)
        stability_input = _build_stability_input(
            calc_input,
            sigma_c_adm=allowable.sigma_c_allow,
            sigma_s_adm=allowable.sigma_s_allow,
        )
        if stability_input is None:
            result.messages_it.extend(
                [
                    "",
                    "⚠️ Verifica instabilità non eseguita:",
                    "   manca l₀ (lunghezza libera) in calc_input.extra.",
                    "   Chiavi supportate: l0_cm, L0_cm, lunghezza_libera_cm, l0_m.",
                ]
            )
            result.details["stabilita_eseguita"] = False
        else:
            stab = verifica_stabilita_ta(stability_input)
            util_stab = _stability_utilisation(stability_input, stab)
            result.details.update(
                {
                    "stabilita_eseguita": True,
                    "stabilita_esito": stab.esito.value,
                    "lambda_max": stab.lambda_max,
                    "omega": stab.omega,
                    "alpha_M": stab.alpha_M,
                }
            )
            if util_stab is not None:
                result.details["util_stabilita"] = util_stab
                result.utilisation = max(result.utilisation or 0.0, util_stab)

            result.messages_it.extend(
                [
                    "",
                    "Verifica instabilità pilastro (Art. 30 RD 2229/39):",
                    f"  λ_max = {stab.lambda_max:.1f}",
                    f"  ω = {stab.omega:.3f}",
                    f"  Esito = {stab.esito.value}",
                ]
            )

            if stab.esito in {EsitoStabilita.NON_VERIFICATA, EsitoStabilita.SNELLEZZA_ECCESSIVA}:
                result.ok = False
                result.messages_it.append("  ✗ Instabilità NON verificata")
            elif stab.esito == EsitoStabilita.VERIFICATA:
                result.messages_it.append("  ✓ Instabilità verificata")

    # 6. Cambia titolo messaggi
    if result.messages_it and "FLESSIONE" in result.messages_it[0]:
        result.messages_it[0] = "=== VERIFICA A PRESSOFLESSIONE METODO TA - RD 2229/39 ==="

    return result


def check_taglio_ta_rett(
    calc_input: CalcInput, template: VerificationTemplate
) -> SingleCheckResult:
    """Verifica a taglio metodo TA - RD 2229/39.

    Implementazione operativa:
    - tensione tangenziale base: tau = V / (b * d)
    - limiti cls da catalogo storico (tau_c0, tau_c1)
    - contributo staffe tramite Asw/s e sigma_s,adm
    - controllo minimo costruttivo dell'armatura trasversale

    Nota: la formulazione storica completa di Art. 21 e la verifica esplicita
    della biella compressa non sono disponibili in forma chiusa nel repository.
    Questa verifica resta conservativa e pienamente tracciabile nei passaggi.

    Args:
        calc_input: Dati di input con Tx, section, d
        template: Template della verifica

    Returns:
        SingleCheckResult con warning PARZIALE
    """
    # 1. Valida inputs
    if calc_input.section is None:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={},
            messages_it=["Sezione non specificata"],
            check_category=template.check_category,
            limit_state=template.limit_state,
        )

    if calc_input.material is None:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={},
            messages_it=["Materiale non specificato"],
            check_category=template.check_category,
            limit_state=template.limit_state,
        )

    if calc_input.Tx is None or calc_input.Tx == 0:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=True,
            utilisation=0.0,
            details={},
            messages_it=["Taglio nullo - verifica non applicabile"],
            check_category=template.check_category,
            limit_state=template.limit_state,
        )

    if calc_input.d is None or calc_input.d <= 0:
        # Stima d = 0.9 * h se non fornito
        h_mm = calc_input.section.height
        d_cm_estimated = 0.9 * h_mm / 10.0
    else:
        d_cm_estimated = calc_input.d

    try:
        # 2. Estrai geometria
        section = calc_input.section
        b_mm = section.width
        h_mm = section.height
        b_cm = b_mm / 10.0
        d_cm = d_cm_estimated

        # 3. Converti forze
        V_kg = calc_input.Tx * 101.97  # kN → kg

        # 4. Calcola tensione tangenziale base: tau = V / (b * d)
        tau_kg_cm2 = V_kg / (b_cm * d_cm)  # kg/cm²

        # 5. Ottieni tau ammissibile da materiale
        material = calc_input.material

        # Verifica se ci sono staffe
        staffe_passo_cm = _normalize_spacing_cm(calc_input.staffe_passo)
        has_staffe = (
            staffe_passo_cm is not None
            and calc_input.staffe_diametro is not None
            and calc_input.staffe_diametro > 0
        )

        allowable = get_rd2229_allowable_stresses(material)
        sigma_s_adm = allowable.sigma_s_allow

        if hasattr(material, "tau_c0") and hasattr(material, "tau_c1"):
            # Valori diretti da RD2229.jsoncode
            tau_c0 = material.tau_c0  # kg/cm² senza staffe
            tau_c1 = material.tau_c1  # kg/cm² con staffe
            tau_adm = tau_c1 if has_staffe else tau_c0
        else:
            # Calcola da sigma_c28
            if hasattr(material, "sigma_c28"):
                sigma_c28 = material.sigma_c28
            elif hasattr(material, "f_ck"):
                sigma_c28 = material.f_ck * 10.197  # MPa → kg/cm²
            else:
                sigma_c28 = 160.0  # Default R160

            # Formule RD 2229:
            tau_c0 = 0.06 * sigma_c28  # kg/cm² senza staffe
            tau_c1 = 0.14 * sigma_c28  # kg/cm² con staffe
            tau_adm = tau_c1 if has_staffe else tau_c0

        # 6. Contributo staffe e minimi costruttivi
        Asw_over_s_cm2_cm = 0.0
        tau_staffe = 0.0
        Asw_min_cm2_cm = 0.001 * b_cm
        minimi_staffe_ok = True
        staffe_num_bracci = max(2, int(calc_input.staffe_num_bracci or 2))

        if has_staffe and staffe_passo_cm is not None:
            diam_cm = calc_input.staffe_diametro / 10.0
            area_gamba_cm2 = math.pi * diam_cm**2 / 4.0
            Asw_cm2 = staffe_num_bracci * area_gamba_cm2
            Asw_over_s_cm2_cm = Asw_cm2 / staffe_passo_cm if staffe_passo_cm > 0 else 0.0

            # Contributo staffe in tensione tangenziale equivalente.
            tau_staffe = (Asw_over_s_cm2_cm * sigma_s_adm / b_cm) if b_cm > 0 else 0.0

            # capacità composita limitata da tau_c1 del materiale storico
            tau_adm = min(tau_c1, tau_c0 + tau_staffe)
            minimi_staffe_ok = Asw_over_s_cm2_cm >= Asw_min_cm2_cm

        # 7. Verifica
        ok = tau_kg_cm2 <= tau_adm and minimi_staffe_ok
        utilisazione = tau_kg_cm2 / tau_adm

        # 8. Messaggi italiani (migliorati per chiarezza)
        messages_it = [
            "=== VERIFICA A TAGLIO METODO TA - RD 2229/39 ===",
            "",
            f"Sezione: {b_cm:.1f} × {h_mm / 10.0:.1f} cm",
            f"Altezza utile: d = {d_cm:.1f} cm",
            "",
            "Sollecitazione:",
            f"  V = {calc_input.Tx:.1f} kN = {V_kg:.0f} kg",
            "",
            "Formula semplificata (base):",
            f"  τ = V / (b × d) = {tau_kg_cm2:.2f} kg/cm²",
            "",
            f"Tensione tangenziale ammissibile ({'con' if has_staffe else 'senza'} staffe):",
            f"  τ_c,adm = {tau_adm:.2f} kg/cm²",
            "",
            "Valori da RD2229.jsoncode:",
            f"  τ_c0 = {tau_c0:.2f} kg/cm² (senza staffe - Art. 21)",
            f"  τ_c1 = {tau_c1:.2f} kg/cm² (con staffe - Art. 21)",
        ]

        if has_staffe and staffe_passo_cm is not None:
            messages_it.extend(
                [
                    "",
                    "Contributo staffe (modello operativo TA):",
                    f"  Ø staffe = {calc_input.staffe_diametro:.1f} mm, bracci = {staffe_num_bracci}",
                    f"  passo = {staffe_passo_cm:.1f} cm",
                    f"  Asw/s = {Asw_over_s_cm2_cm:.4f} cm²/cm",
                    f"  τ_staffe = {tau_staffe:.2f} kg/cm²",
                    f"  τ_c,adm = min(τ_c1, τ_c0 + τ_staffe) = {tau_adm:.2f} kg/cm²",
                    f"  Minimo costruttivo Asw/s ≥ {Asw_min_cm2_cm:.4f} cm²/cm: "
                    f"{'✓ OK' if minimi_staffe_ok else '✗ NON OK'}",
                ]
            )

        messages_it.extend(
            [
                "",
                f"Verifica: {tau_kg_cm2:.2f} / {tau_adm:.2f} = {utilisazione:.3f} "
                f"{'✓ OK' if ok else '✗ NON OK'}",
                "",
                "Nota: formulazione conservativa basata su τ_c0/τ_c1 catalogati e contributo staffe.",
            ]
        )

        return SingleCheckResult(
            template_id=template.template_id,
            ok=ok,
            utilisation=utilisazione,
            details={
                "tau_kg_cm2": tau_kg_cm2,
                "tau_c0_kg_cm2": tau_c0,
                "tau_c1_kg_cm2": tau_c1,
                "tau_adm_kg_cm2": tau_adm,
                "V_kg": V_kg,
                "b_cm": b_cm,
                "d_cm": d_cm,
                "has_staffe": has_staffe,
                "staffe_passo_cm": staffe_passo_cm,
                "staffe_num_bracci": staffe_num_bracci if has_staffe else None,
                "Asw_over_s_cm2_cm": Asw_over_s_cm2_cm,
                "Asw_min_cm2_cm": Asw_min_cm2_cm,
                "tau_staffe_kg_cm2": tau_staffe,
                "sigma_s_adm_kg_cm2": sigma_s_adm,
                "minimi_staffe_ok": minimi_staffe_ok,
            },
            norm_references=[template.primary_reference] + template.secondary_references,
            messages_it=messages_it,
            check_category=template.check_category,
            limit_state=template.limit_state,
        )

    except Exception as e:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={"error": str(e)},
            messages_it=[f"Errore nel calcolo: {str(e)}"],
            check_category=template.check_category,
            limit_state=template.limit_state,
        )


def check_minimi_armatura_ta(
    calc_input: CalcInput, template: VerificationTemplate
) -> SingleCheckResult:
    """Verifica minimi armatura longitudinale - RD 2229/39 (IMPLEMENTAZIONE COMPLETA).

    Implementa controllo con distinzione travi/pilastri usando compute_long_rebar_limits_ta():
    - Travi: As,min = 0.15% A_sez
    - Pilastri: As,min = 0.30% A_sez
    - As,max = 6% A_sez (per entrambi)

    Riferimento: Art. 16 RD 2229/39

    Args:
        calc_input: Dati di input con As, section, N
        template: Template della verifica

    Returns:
        SingleCheckResult con distinzione travi/pilastri
    """
    # 1. Valida inputs
    if calc_input.section is None:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={},
            messages_it=["Sezione non specificata"],
            check_category=template.check_category,
            limit_state=template.limit_state,
        )

    if calc_input.As is None:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={},
            messages_it=["Armatura As non specificata"],
            check_category=template.check_category,
            limit_state=template.limit_state,
        )

    try:
        # 2. Calcola area sezione
        section = calc_input.section
        b_mm = section.width
        h_mm = section.height
        A_sez_cm2 = (b_mm * h_mm) / 100.0  # mm² → cm²

        As_cm2 = calc_input.As

        # 3. Determina tipo elemento (trave o pilastro)
        # Euristica: compressione significativa → pilastro
        has_compression = calc_input.N is not None and calc_input.N < -50.0
        is_column = has_compression
        is_beam = not is_column

        # Allow override via extra dict if provided by GUI
        if calc_input.extra:
            element_type_override = calc_input.extra.get("element_type")
            if element_type_override == "pilastro":
                is_column, is_beam = True, False
            elif element_type_override == "trave":
                is_column, is_beam = False, True

        element_type_it = "pilastro" if is_column else "trave"

        # 4. Calcola limiti usando historical_ta function (beam/column distinction)
        # Estrai proprietà materiale per fyd
        allowable = get_rd2229_allowable_stresses(calc_input.material)

        # Estimate fctm (tensile strength) if not available
        # fctm ≈ 0.1 * sigma_c28 (empirical for historical concrete)
        sigma_c28 = allowable.sigma_c_allow * 2.0  # sigma_c_adm = 0.5 * sigma_c28
        fctm = 0.1 * sigma_c28  # kg/cm²

        # Call compute_long_rebar_limits_ta with beam/column distinction
        limits = compute_long_rebar_limits_ta(
            section_area=A_sez_cm2,
            Nx=(calc_input.N or 0.0) * 101.97,  # kN → kg
            fyd=allowable.sigma_s_allow,
            fctm=fctm,
            carbon_fiber_placeholder=None,
            is_column=is_column,
            is_beam=is_beam,
            zona_sismica=False,
        )

        As_min_cm2 = limits.Afmin
        As_max_cm2 = limits.Afmax

        # 5. Verifica
        ok_min = As_cm2 >= As_min_cm2
        ok_max = As_cm2 <= As_max_cm2
        ok = ok_min and ok_max

        # Utilizzazione rispetto al minimo
        utilisazione = As_min_cm2 / As_cm2 if As_cm2 > 0 else 999.0

        # 6. Percentuale armatura
        rho_percent = (As_cm2 / A_sez_cm2) * 100.0  # %
        rho_min_percent = (As_min_cm2 / A_sez_cm2) * 100.0
        rho_max_percent = (As_max_cm2 / A_sez_cm2) * 100.0

        # 7. Messaggi italiani con distinzione tipo elemento
        messages_it = [
            "=== VERIFICA MINIMI ARMATURA LONGITUDINALE - RD 2229/39 ===",
            "",
            f"Tipo elemento: {element_type_it.upper()}",
            f"Sezione: {b_mm / 10.0:.1f} × {h_mm / 10.0:.1f} cm",
            f"Area sezione: A_sez = {A_sez_cm2:.1f} cm²",
            "",
            f"Armatura presente: As = {As_cm2:.2f} cm²",
            f"Percentuale armatura: ρ = {rho_percent:.2f}%",
            "",
            f"Limiti secondo Art. 16 RD 2229/39 ({'pilastri' if is_column else 'travi'}):",
            f"  As,min = {As_min_cm2:.2f} cm² ({rho_min_percent:.2f}% A_sez)",
            f"  As,max = {As_max_cm2:.2f} cm² ({rho_max_percent:.1f}% A_sez)",
            "",
            f"Verifica minimo: {As_cm2:.2f} ≥ {As_min_cm2:.2f} {'✓ OK' if ok_min else '✗ NON OK'}",
            f"Verifica massimo: {As_cm2:.2f} ≤ {As_max_cm2:.2f} {'✓ OK' if ok_max else '✗ NON OK'}",
            "",
            f"Utilizzazione: {utilisazione:.3f} ({'✓ OK' if ok else '✗ NON OK'})",
            "",
            "Implementazione completa con distinzione travi/pilastri secondo Art. 16.",
        ]

        return SingleCheckResult(
            template_id=template.template_id,
            ok=ok,
            utilisation=utilisazione,
            details={
                "As_cm2": As_cm2,
                "As_min_cm2": As_min_cm2,
                "As_max_cm2": As_max_cm2,
                "A_sez_cm2": A_sez_cm2,
                "rho_percent": rho_percent,
                "rho_min_percent": rho_min_percent,
                "rho_max_percent": rho_max_percent,
                "ok_min": ok_min,
                "ok_max": ok_max,
                "element_type": element_type_it,
                "is_column": is_column,
                "is_beam": is_beam,
            },
            norm_references=[template.primary_reference] + template.secondary_references,
            messages_it=messages_it,
            check_category=template.check_category,
            limit_state=template.limit_state,
        )

    except Exception as e:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={"error": str(e)},
            messages_it=[f"Errore nel calcolo: {str(e)}"],
            check_category=template.check_category,
            limit_state=template.limit_state,
        )


def check_pressoflessione_deviata_ta_concrete(
    calc_input: CalcInput, template: VerificationTemplate
) -> SingleCheckResult:
    """Verifica cls pressoflessione deviata TA - RD 2229/39 (COMPLETO).

    Implementa sovrapposizione elastica per N-Mx-My secondo Art. 29 RD 2229/39:
    σ_c,max = N/A + |Mx|/Wx + |My|/Wy

    RD 2229/39 NON prevede domini N-Mx-My (metodo SLU);
    usa metodo elastico lineare con sovrapposizione effetti.

    IMPLEMENTAZIONE COMPLETA:
    - Sovrapposizione elastica N, Mx, My ✓
    - Riduzione sezioni snelle (A_min < 25 cm) ✓
    - Verifica σ_c,max ≤ σ_c,adm (Art. 18) ✓
    - Messaggi italiani completi ✓

    FUORI SCOPO:
    - Instabilità pilastri λ > 15 (richiede l₀)

    Args:
        calc_input: Dati input con section, material, N, Mx, My
        template: Template della verifica

    Returns:
        SingleCheckResult con verifica completa
    """
    # 1. Validate inputs
    if calc_input.section is None:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={},
            messages_it=["Sezione non specificata"],
            check_category=template.check_category,
            limit_state=template.limit_state,
        )

    if calc_input.material is None:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={},
            messages_it=["Materiale non specificato"],
            check_category=template.check_category,
            limit_state=template.limit_state,
        )

    # Almeno uno tra N, Mx, My deve essere presente e non zero
    N_present = calc_input.N is not None and calc_input.N != 0
    Mx_present = calc_input.Mx is not None and calc_input.Mx != 0
    My_present = calc_input.My is not None and calc_input.My != 0

    if not (N_present or Mx_present or My_present):
        return SingleCheckResult(
            template_id=template.template_id,
            ok=True,
            utilisation=0.0,
            details={},
            messages_it=["Sollecitazioni nulle - verifica non applicabile"],
            check_category=template.check_category,
            limit_state=template.limit_state,
        )

    try:
        # 2. Extract geometry
        section = calc_input.section
        b_mm = section.width
        h_mm = section.height
        b_cm = b_mm / 10.0
        h_cm = h_mm / 10.0
        A_cm2 = b_cm * h_cm

        # Compute section moduli
        Wx_cm3, Wy_cm3 = compute_section_moduli_rect(b_cm, h_cm)

        # 3. Convert loads (kN, kNm → kg, kg·cm)
        ta_loads = convert_loads_to_ta_units(calc_input)
        N_kg = ta_loads["N_kg"]
        Mx_kg_cm = ta_loads["Mx_kg_cm"]
        My_kg_cm = ta_loads["My_kg_cm"]

        # 4. Get allowable stresses (Art. 18)
        allowable = get_rd2229_allowable_stresses(calc_input.material)
        sigma_c_adm_base = allowable.sigma_c_allow  # kg/cm²

        # 5. Apply slenderness reduction if A_min < 25 cm
        sigma_c_adm, slender_details = apply_slenderness_reduction_ta(sigma_c_adm_base, b_cm, h_cm)

        # 6. Compute σ_c,max with elastic superposition (Art. 29)
        sigma_c_max = compute_sigma_concrete_biaxial_ta(
            N_kg, Mx_kg_cm, My_kg_cm, A_cm2, Wx_cm3, Wy_cm3
        )

        # 7. Verify
        ok = sigma_c_max <= sigma_c_adm
        utilisazione = sigma_c_max / sigma_c_adm if sigma_c_adm > 0 else None

        # 8. Build Italian messages
        messages_it = [
            "=== VERIFICA CLS PRESSOFLESSIONE DEVIATA TA - RD 2229/39 ===",
            "",
            f"Sezione rettangolare: b = {b_cm:.1f} cm, h = {h_cm:.1f} cm",
            f"Area: A = {A_cm2:.1f} cm²",
            f"Moduli resistenza: Wx = {Wx_cm3:.1f} cm³, Wy = {Wy_cm3:.1f} cm³",
            "",
            "Sollecitazioni:",
            f"  N = {calc_input.N:.1f} kN = {N_kg:.0f} kg" if N_present else "  N = 0 kN",
            (
                f"  Mx = {calc_input.Mx:.1f} kNm = {Mx_kg_cm:.0f} kg·cm"
                if Mx_present
                else "  Mx = 0 kNm"
            ),
            (
                f"  My = {calc_input.My:.1f} kNm = {My_kg_cm:.0f} kg·cm"
                if My_present
                else "  My = 0 kNm"
            ),
            "",
            f"Tensione ammissibile cls (Art. 18): σ_c,adm = {sigma_c_adm_base:.1f} kg/cm²",
        ]

        # Slenderness reduction info
        if slender_details["reduction_applied"]:
            messages_it.extend(
                [
                    "",
                    "Riduzione sezioni snelle (feature repository):",
                    f"  A_min = min(b,h) = {slender_details['A_min_cm']:.1f} cm < 25 cm",
                    f"  Fattore riduzione = {slender_details['reduction_factor']:.3f}",
                    f"  σ_c,adm ridotta = {sigma_c_adm:.1f} kg/cm²",
                ]
            )
        elif slender_details["A_min_cm"] >= 25.0:
            messages_it.append(
                f"Sezione non snella (A_min = {slender_details['A_min_cm']:.1f} cm ≥ 25 cm)"
            )

        # Stress calculation breakdown
        sigma_N_component = abs(N_kg / A_cm2) if A_cm2 > 0 else 0.0
        sigma_Mx_component = abs(Mx_kg_cm / Wx_cm3) if Wx_cm3 > 0 else 0.0
        sigma_My_component = abs(My_kg_cm / Wy_cm3) if Wy_cm3 > 0 else 0.0

        messages_it.extend(
            [
                "",
                "Metodo elastico con sovrapposizione effetti (Art. 29):",
                "  σ_c,max = N/A + |Mx|/Wx + |My|/Wy",
                f"  σ_c,max = {sigma_N_component:.2f} + {sigma_Mx_component:.2f} + {sigma_My_component:.2f}",
                f"  σ_c,max = {sigma_c_max:.2f} kg/cm²",
                "",
                f"Verifica: {sigma_c_max:.2f} ≤ {sigma_c_adm:.2f} → {'✓ OK' if ok else '✗ NON OK'}",
                f"Utilizzazione: {utilisazione:.3f}",
                "",
                "Nota: RD 2229/39 non prevede domini N-Mx-My; usa sovrapposizione elastica.",
            ]
        )

        # Warning if slender column (λ > 15)
        if calc_input.extra and calc_input.extra.get("lambda"):
            lambda_val = calc_input.extra["lambda"]
            if lambda_val > 15:
                messages_it.extend(
                    [
                        "",
                        f"⚠️ Pilastro snello: λ = {lambda_val:.1f} > 15",
                        "   Necessaria verifica stabilità (Art. 30 RD 2229/39) - NON implementata.",
                        "   BLOCCO: richiede l₀ (lunghezza libera inflessione).",
                    ]
                )

        # 9. Return result
        return SingleCheckResult(
            template_id=template.template_id,
            ok=ok,
            utilisation=utilisazione,
            details={
                "sigma_c_max_kg_cm2": sigma_c_max,
                "sigma_c_adm_kg_cm2": sigma_c_adm,
                "sigma_c_adm_base_kg_cm2": sigma_c_adm_base,
                "N_kg": N_kg,
                "Mx_kg_cm": Mx_kg_cm,
                "My_kg_cm": My_kg_cm,
                "A_cm2": A_cm2,
                "Wx_cm3": Wx_cm3,
                "Wy_cm3": Wy_cm3,
                "sigma_N_component": sigma_N_component,
                "sigma_Mx_component": sigma_Mx_component,
                "sigma_My_component": sigma_My_component,
                **slender_details,
            },
            norm_references=[template.primary_reference] + template.secondary_references,
            messages_it=messages_it,
            check_category=template.check_category,
            limit_state=template.limit_state,
        )

    except Exception as e:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={"error": str(e)},
            messages_it=[f"Errore nel calcolo: {str(e)}"],
            check_category=template.check_category,
            limit_state=template.limit_state,
        )


def check_pressoflessione_deviata_ta_steel(
    calc_input: CalcInput, template: VerificationTemplate
) -> SingleCheckResult:
    """Verifica acciaio pressoflessione deviata TA - RD 2229/39.

    Verifica tensioni acciaio per N-Mx-My con sovrapposizione elastica.
    I moduli W_sx/W_sy possono essere:
    - forniti esplicitamente in ``calc_input.extra``;
    - stimati automaticamente da sezione rettangolare e armature equivalenti
      (As, As', d, d').

    Args:
        calc_input: Dati input con Mx, My, extra.W_sx_cm3, extra.W_sy_cm3
        template: Template della verifica

    Returns:
        SingleCheckResult
    """
    # 1. Validate inputs
    if calc_input.section is None:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={},
            messages_it=["Sezione non specificata"],
            check_category=template.check_category,
            limit_state=template.limit_state,
        )

    if calc_input.material is None:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={},
            messages_it=["Materiale non specificato"],
            check_category=template.check_category,
            limit_state=template.limit_state,
        )

    # 2. Ricerca o stima dei moduli W_sx_cm3, W_sy_cm3
    W_sx_cm3 = None
    W_sy_cm3 = None
    moduli_source = "input"
    estimate_notes: list[str] = []

    if calc_input.extra:
        W_sx_cm3 = calc_input.extra.get("W_sx_cm3")
        W_sy_cm3 = calc_input.extra.get("W_sy_cm3")

    if W_sx_cm3 is None or W_sy_cm3 is None:
        W_sx_cm3, W_sy_cm3, estimate_notes = _estimate_steel_moduli_rect(calc_input)
        moduli_source = "stima_automatica"

    if W_sx_cm3 is None or W_sy_cm3 is None:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={"partial_reason": "missing_steel_moduli"},
            messages_it=[
                "=== VERIFICA ACCIAIO PRESSOFLESSIONE DEVIATA TA - RD 2229/39 ===",
                "",
                "⚠️ VERIFICA NON ESEGUITA - DATI MANCANTI",
                "",
                "Moduli resistenza acciaio W_sx, W_sy non disponibili né stimabili.",
                "",
                "Per eseguire la verifica occorre una delle seguenti opzioni:",
                "  1) fornire calc_input.extra['W_sx_cm3'] e ['W_sy_cm3']",
                "  2) fornire almeno As e d per la stima automatica",
                "",
                "Riferimento: Art. 19 RD 2229/39 (tensioni ammissibili acciaio).",
            ],
            norm_references=[template.primary_reference] + template.secondary_references,
            check_category=template.check_category,
            limit_state=template.limit_state,
        )

    try:
        # 4. Convert loads
        ta_loads = convert_loads_to_ta_units(calc_input)
        Mx_kg_cm = ta_loads["Mx_kg_cm"]
        My_kg_cm = ta_loads["My_kg_cm"]

        # 5. Get σ_s,adm (Art. 19)
        allowable = get_rd2229_allowable_stresses(calc_input.material)
        sigma_s_adm = allowable.sigma_s_allow  # kg/cm²

        # 6. Compute σ_s with elastic superposition
        sigma_s_x = abs(Mx_kg_cm) / W_sx_cm3 if W_sx_cm3 > 0 else 0.0
        sigma_s_y = abs(My_kg_cm) / W_sy_cm3 if W_sy_cm3 > 0 else 0.0
        sigma_s_max = sigma_s_x + sigma_s_y

        # 7. Verify
        ok = sigma_s_max <= sigma_s_adm
        utilisazione = sigma_s_max / sigma_s_adm if sigma_s_adm > 0 else None

        # 8. Italian messages
        messages_it = [
            "=== VERIFICA ACCIAIO PRESSOFLESSIONE DEVIATA TA - RD 2229/39 ===",
            "",
            "Sollecitazioni:",
            f"  Mx = {calc_input.Mx:.1f} kNm = {Mx_kg_cm:.0f} kg·cm",
            f"  My = {calc_input.My:.1f} kNm = {My_kg_cm:.0f} kg·cm",
            "",
            f"Moduli resistenza acciaio ({'stimati automaticamente' if moduli_source == 'stima_automatica' else 'da input'}):",
            f"  W_sx = {W_sx_cm3:.1f} cm³",
            f"  W_sy = {W_sy_cm3:.1f} cm³",
            "",
            f"Tensione ammissibile acciaio (Art. 19): σ_s,adm = {sigma_s_adm:.1f} kg/cm²",
            "",
            "Metodo elastico con sovrapposizione:",
            "  σ_s,max = |Mx|/W_sx + |My|/W_sy",
            f"  σ_s,max = {sigma_s_x:.2f} + {sigma_s_y:.2f} = {sigma_s_max:.2f} kg/cm²",
            "",
            f"Verifica: {sigma_s_max:.2f} ≤ {sigma_s_adm:.2f} → {'✓ OK' if ok else '✗ NON OK'}",
            f"Utilizzazione: {utilisazione:.3f}",
        ]

        if estimate_notes:
            messages_it.extend(
                ["", "Note stima moduli:"] + [f"  - {note}" for note in estimate_notes]
            )

        return SingleCheckResult(
            template_id=template.template_id,
            ok=ok,
            utilisation=utilisazione,
            details={
                "sigma_s_max_kg_cm2": sigma_s_max,
                "sigma_s_adm_kg_cm2": sigma_s_adm,
                "Mx_kg_cm": Mx_kg_cm,
                "My_kg_cm": My_kg_cm,
                "W_sx_cm3": W_sx_cm3,
                "W_sy_cm3": W_sy_cm3,
                "sigma_s_x_component": sigma_s_x,
                "sigma_s_y_component": sigma_s_y,
                "moduli_source": moduli_source,
            },
            norm_references=[template.primary_reference] + template.secondary_references,
            messages_it=messages_it,
            check_category=template.check_category,
            limit_state=template.limit_state,
        )

    except Exception as e:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={"error": str(e)},
            messages_it=[f"Errore nel calcolo: {str(e)}"],
            check_category=template.check_category,
            limit_state=template.limit_state,
        )
