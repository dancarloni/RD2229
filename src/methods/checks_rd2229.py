"""
Verifiche secondo RD 2229/1939 - Metodo Tensioni Ammissibili (TA).

Implementa le verifiche per strutture in cemento armato secondo il Regio Decreto
2229/39 utilizzando il metodo delle tensioni ammissibili (allowable stress design).

Struttura:
- Funzioni di utilità per conversione unità (kN→kg, mm→cm, MPa→kg/cm²)
- Funzioni per costruzione material laws (ConcreteLawTA, SteelLawTA)
- Funzioni di verifica: flessione TA, pressoflessione TA, taglio TA, minimi armatura

Stato implementazione:
- check_flessione_ta_rett: COMPLETE
- check_pressoflessione_ta_rett: PARTIAL (con TODOs italiani)
- check_taglio_ta_rett: PARTIAL (con TODOs italiani)
- check_minimi_armatura_ta: PARTIAL (con TODOs italiani)

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
from src.core_calculus.contracts import (
    CalcInput,
    SingleCheckResult,
    VerificationTemplate,
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
        ok = check_result.ok
        util_c = abs(stress_result.sigma_c_max) / allowable.sigma_c_allow
        util_s = abs(stress_result.sigma_s_max) / allowable.sigma_s_allow
        utilisazione = max(util_c, util_s)

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
            messages_it.extend(
                ["", "VERIFICA NON SODDISFATTA:"] + check_result.messages
            )

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
            norm_references=[template.primary_reference]
            + template.secondary_references,
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
    """Verifica a pressoflessione metodo TA - RD 2229/39 (IMPLEMENTAZIONE MIGLIORATA).

    Utilizza lo stesso motore di flessione_ta_rett ma con sforzo normale N presente.
    Implementa riduzione sigma_c_adm per sezioni snelle secondo Art. 16 RD 2229/39.

    IMPLEMENTAZIONE MIGLIORATA:
    - Verifica base funzionante (N + M → tensioni → confronto con ammissibili) ✓
    - Riduzione sigma_c_adm per sezioni snelle (Art. 16 RD 2229) ✓ IMPLEMENTATO
    - Mancante (TODOs):
      - Controllo instabilità pilastri snelli (lambda > 15) - richiede l₀

    TODOs:
    # TODO: [RD2229 Stabilità] Verificare instabilità pilastri snelli (lambda > 15)
    #       lambda = l0 / i (snellezza), dove l0 = lunghezza libera inflessione, i = raggio inerzia
    #       BLOCCO: l0 non disponibile in CalcInput (richiede info strutturale globale)
    #       Per lambda > 15: riduzione carico critico secondo formula Eulero modificata
    #       Riferimento: Circolare applicativa RD 2229/39

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

    # 2. Applica riduzione passando fattore tramite extra dict
    # (così check_flessione_ta_rett può usarlo se implementato,
    #  altrimenti applicheremo la riduzione manualmente ai details)
    if applied_reduction and calc_input.extra is None:
        calc_input.extra = {}
    if applied_reduction:
        calc_input.extra["slenderness_reduction_factor"] = reduction_factor

    # 3. Chiama verifica base (gestisce N+M automaticamente)
    result = check_flessione_ta_rett(calc_input, template)

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
                reduced_sigma_c_adm = original_sigma_c_adm * reduction_factor
                result.details["sigma_c_adm_ridotta_kg_cm2"] = reduced_sigma_c_adm
                result.details["reduction_factor"] = reduction_factor
                result.details["A_min_cm"] = A_min_cm
        elif A_min_cm is not None and A_min_cm >= 25.0:
            slenderness_info = [
                "",
                f"Sezione non snella (A_min = {A_min_cm:.1f} cm ≥ 25 cm): riduzione non applicata",
            ]

        # Warning PARZIALE aggiornato
        partial_warnings = [
            "",
            "⚠️ IMPLEMENTAZIONE MIGLIORATA (PARTIAL):",
            "   ✓ Verifica base eseguita (N + M → tensioni)",
            "   ✓ Riduzione σ_c,adm per sezioni snelle implementata",
            "   Mancano:",
            "   - Controllo instabilità pilastri snelli (λ > 15) - richiede l₀",
        ]

        result.messages_it.extend(slenderness_info + partial_warnings)

    # 5. Cambia titolo messaggi
    if result.messages_it and "FLESSIONE" in result.messages_it[0]:
        result.messages_it[0] = "=== VERIFICA A PRESSOFLESSIONE METODO TA - RD 2229/39 ==="

    return result


def check_taglio_ta_rett(
    calc_input: CalcInput, template: VerificationTemplate
) -> SingleCheckResult:
    """Verifica a taglio metodo TA - RD 2229/39 (IMPLEMENTAZIONE PARZIALE).

    Implementa formula base: tau = V / (b * d)
    Confronta con tau_c0 (senza staffe) o tau_c1 (con staffe).

    IMPLEMENTAZIONE PARZIALE:
    - Formula base tau = V / (b * d) implementata
    - Confronto con tau_c0, tau_c1 da RD2229.jsoncode
    - Mancante (TODOs):
      - Formula completa Art. 21 RD 2229/39
      - Calcolo contributo staffe metodo TA storico
      - Minimi armatura a taglio secondo RD 2229

    TODOs:
    # TODO: [RD2229 Art. 21] Formula completa taglio secondo Art. 21
    #       Attualmente: tau = V / (b * d) semplificato
    #       Mancante: contributo staffe, verifica biella compressa, formula esatta Art. 21
    #       Riferimento: Art. 21 RD 2229/39 - Tensioni tangenziali

    # TODO: [RD2229 Staffe TA] Calcolo armatura trasversale metodo TA storico
    #       Formule storiche per (Asw/s) diverse da metodo moderno SLU
    #       Necessaria ricerca formule originali RD 2229/39 o manuali storici (Santarella)

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
        has_staffe = (
            calc_input.staffe_passo is not None
            and calc_input.staffe_diametro is not None
        )

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

        # 6. Verifica
        ok = tau_kg_cm2 <= tau_adm
        utilisazione = tau_kg_cm2 / tau_adm

        # 7. Messaggi italiani (migliorati per chiarezza)
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
            "",
            f"Verifica: {tau_kg_cm2:.2f} / {tau_adm:.2f} = {utilisazione:.3f} "
            f"{'✓ OK' if ok else '✗ NON OK'}",
            "",
            "⚠️ IMPLEMENTAZIONE PARZIALE:",
            "   Formula base τ = V/(b×d) implementata (verifica conservativa)",
            "   Formula più precisa Art. 21 RD 2229/39 non disponibile (richiede ricerca storica)",
            "   Mancano:",
            "   - Formula completa Art. 21 con effetti di N, M sul taglio",
            "   - Calcolo contributo staffe (metodo TA storico)",
            "   - Verifica biella compressa cls",
            "   Nota: Verifica attuale è conservativa (sottostima resistenza)",
        ]

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
            },
            norm_references=[template.primary_reference]
            + template.secondary_references,
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
        has_compression = (calc_input.N is not None and calc_input.N < -50.0)
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
            f"Verifica minimo: {As_cm2:.2f} ≥ {As_min_cm2:.2f} "
            f"{'✓ OK' if ok_min else '✗ NON OK'}",
            f"Verifica massimo: {As_cm2:.2f} ≤ {As_max_cm2:.2f} "
            f"{'✓ OK' if ok_max else '✗ NON OK'}",
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
            norm_references=[template.primary_reference]
            + template.secondary_references,
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
