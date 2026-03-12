"""
Verifiche secondo DM 9/1/1996 e DM 14/02/1992 - Metodi TA, SLU, SLE e c.a.p.

Implementa le verifiche per strutture in cemento armato normale e precompresso
secondo il DM 9/1/1996 (che rimanda al DM 14/02/1992 per il metodo TA).

Struttura del modulo:
A) Utility DM96-specifiche (lettura tensioni ammissibili da materiale)
B) Check TA DM96 (4 funzioni): flessione, pressoflessione, taglio, minimi armatura
   - Riutilizzano il motore historical_ta/ e utility da checks_rd2229.py
   - Differenza principale: tensioni ammissibili da DM92.jsoncode (non da RD2229)
C) Check SLU DM96 (4 funzioni base): flessione, taglio, minimi flessione, minimi taglio
   - Pattern da checks_ntc2018.py con gamma_c=1.6 (vs 1.5 NTC2018)
D) Check SLE DM96 (2 funzioni): fessurazione, deformazioni
   - Parametri (w_amm, limiti frecce) da config utente, NON hardcodati
E) Check SLU aggiuntivi (3 funzioni): torsione, punzonamento, instabilita
   - Logica base con TODO per parti normative da confermare
F) Ganci precompressione c.a.p. (4 funzioni placeholder)
   - Firme + docstring + TODO per implementazione futura

NormReference principali:
- DM 14/02/1992 (metodo TA, Cap. 2-5)
- DM 9/1/1996 (metodo SLU/SLE, Cap. 3-5)
- EC2 Parte 1-1 (formule generali di riferimento)

Dipendenze:
- historical_ta/ (motore TA)
- src.methods.checks_rd2229 (utility conversione unita)
- src.core_calculus.contracts (CalcInput, SingleCheckResult, VerificationTemplate)
- src.core_calculus.lc_fc_adjustments (per strutture esistenti)

Tutti i messaggi utente sono in italiano.
"""

from __future__ import annotations

import logging
import math
from typing import Any

from historical_ta.checks import (
    AllowableStresses,
    check_allowable_stresses_ta,
    compute_long_rebar_limits_ta,
)
from historical_ta.geometry import compute_section_properties
from historical_ta.stress import LoadState, compute_normal_stresses_ta
from src.core_calculus.contracts import (
    CalcInput,
    NormReference,
    SingleCheckResult,
    VerificationTemplate,
)
from src.core_calculus.lc_fc_adjustments import apply_lc_fc_adjustments
from src.methods.rd2229.checks import (
    AllowableStressesExtracted,
    apply_slenderness_reduction_ta,
    build_concrete_law_ta,
    build_steel_law_ta,
    convert_loads_to_ta_units,
    convert_section_to_ta_geometry,
)

logger = logging.getLogger(__name__)


# ==============================================================================
# SEZIONE A: UTILITY DM96-SPECIFICHE
# ==============================================================================


def get_dm96_allowable_stresses(material: Any) -> AllowableStressesExtracted:
    """Estrae tensioni ammissibili DM92/DM96 da material object.

    Legge sigma_c_adm, sigma_s_adm, tau_c0, tau_c1 dal materiale DM92.
    Se il materiale ha campi DM92 specifici (sigma_c_adm_kg_cm2, ecc.)
    li usa direttamente. Altrimenti stima da fck usando le formule DM92:
    - sigma_c_adm = 0.30 * Rck_kg_cm2
    - sigma_s_adm = min(2/3 * sigma_sn, 2600) kg/cm2

    Parametri
    ---------
    material : Any
        Oggetto materiale con proprieta DM92 (sigma_c_adm_kg_cm2, ecc.)
        oppure proprieta moderne (f_ck, f_yk).

    Ritorna
    -------
    AllowableStressesExtracted
        Tensioni ammissibili in kg/cm2.

    NormReference: DM 14/02/1992, Tabella tensioni ammissibili
    """
    # --- Calcestruzzo ---
    if hasattr(material, "sigma_c_adm_kg_cm2") and material.sigma_c_adm_kg_cm2:
        sigma_c_allow = material.sigma_c_adm_kg_cm2
    elif hasattr(material, "sigma_c_adm") and material.sigma_c_adm:
        sigma_c_allow = material.sigma_c_adm
    elif hasattr(material, "Rck_kg_cm2") and material.Rck_kg_cm2:
        sigma_c_allow = 0.30 * material.Rck_kg_cm2
    elif hasattr(material, "f_ck") and material.f_ck:
        # Stima Rck da fck: Rck ≈ fck / 0.83 (in MPa), poi converti in kg/cm2
        Rck_MPa = material.f_ck / 0.83
        Rck_kg_cm2 = Rck_MPa * 10.197
        sigma_c_allow = 0.30 * Rck_kg_cm2
    else:
        # Fallback: impossibile determinare, ritorna 0 con avviso
        sigma_c_allow = 0.0

    # sigma_c_med_allow (tensione media ammissibile) - tipicamente uguale a sigma_c_allow
    sigma_c_med_allow = sigma_c_allow

    # --- Acciaio ---
    if hasattr(material, "sigma_s_adm_kg_cm2") and material.sigma_s_adm_kg_cm2:
        sigma_s_allow = material.sigma_s_adm_kg_cm2
    elif hasattr(material, "sigma_s_adm") and material.sigma_s_adm:
        sigma_s_allow = material.sigma_s_adm
    elif hasattr(material, "sigma_sn_kg_cm2") and material.sigma_sn_kg_cm2:
        sigma_s_allow = min(material.sigma_sn_kg_cm2 * 2.0 / 3.0, 2600.0)
    elif hasattr(material, "f_yk") and material.f_yk:
        sigma_sn = material.f_yk * 10.197
        sigma_s_allow = min(sigma_sn * 2.0 / 3.0, 2600.0)
    else:
        sigma_s_allow = 0.0

    return AllowableStressesExtracted(
        sigma_c_allow=sigma_c_allow,
        sigma_s_allow=sigma_s_allow,
        sigma_c_med_allow=sigma_c_med_allow,
    )


def _get_dm96_tau_limits(material: Any) -> tuple[float, float]:
    """Estrae limiti tau_c0 e tau_c1 dal materiale DM92/DM96.

    Parametri
    ---------
    material : Any
        Oggetto materiale con proprieta DM92.

    Ritorna
    -------
    tuple[float, float]
        (tau_c0_kg_cm2, tau_c1_kg_cm2)

    NormReference: DM 14/02/1992, Tabella tensioni tangenziali ammissibili
    """
    tau_c0 = 0.0
    tau_c1 = 0.0

    if hasattr(material, "tau_c0_kg_cm2") and material.tau_c0_kg_cm2:
        tau_c0 = material.tau_c0_kg_cm2
    elif hasattr(material, "tau_c0") and material.tau_c0:
        tau_c0 = material.tau_c0
    elif hasattr(material, "Rck_kg_cm2") and material.Rck_kg_cm2:
        # Stima approssimativa da Rck (formula semplificata)
        # TODO: verificare con tabella esatta DM 14/02/1992
        tau_c0 = 0.36 * math.sqrt(material.Rck_kg_cm2)
    elif hasattr(material, "f_ck") and material.f_ck:
        Rck_kg_cm2 = (material.f_ck / 0.83) * 10.197
        tau_c0 = 0.36 * math.sqrt(Rck_kg_cm2)

    if hasattr(material, "tau_c1_kg_cm2") and material.tau_c1_kg_cm2:
        tau_c1 = material.tau_c1_kg_cm2
    elif hasattr(material, "tau_c1") and material.tau_c1:
        tau_c1 = material.tau_c1
    elif tau_c0 > 0:
        # Stima tau_c1 ≈ 3.5 * tau_c0 (approssimazione DM92)
        # TODO: verificare con tabella esatta DM 14/02/1992
        tau_c1 = 3.5 * tau_c0

    return (tau_c0, tau_c1)


def _make_error_result(
    template_id: str, message: str, limit_state: str = "TA"
) -> SingleCheckResult:
    """Helper per creare un risultato di errore."""
    return SingleCheckResult(
        template_id=template_id,
        ok=False,
        utilisation=None,
        details={},
        messages_it=[message],
        limit_state=limit_state,
    )


# ==============================================================================
# SEZIONE B: CHECK TA DM96 (riuso historical_ta)
# ==============================================================================


def check_flessione_ta_dm96(
    calc_input: CalcInput, template: VerificationTemplate
) -> SingleCheckResult:
    """Verifica a flessione metodo TA - DM 14/02/1992.

    Calcola le tensioni normali nella sezione soggetta a flessione semplice
    e le confronta con le tensioni ammissibili DM92/DM96.

    Utilizza il motore historical_ta per il calcolo completo delle tensioni
    su sezione omogeneizzata con calcestruzzo elastico e trazione nulla.

    Parametri
    ---------
    calc_input : CalcInput
        Dati di input (sezione, materiale, sollecitazioni).
    template : VerificationTemplate
        Template della verifica.

    Ritorna
    -------
    SingleCheckResult
        Risultato con tensioni calcolate vs ammissibili.

    NormReference: DM 14/02/1992 Cap. 2 - Tensioni normali ammissibili
    """
    if calc_input.section is None:
        return _make_error_result(template.template_id, "Sezione non specificata")
    if calc_input.material is None:
        return _make_error_result(template.template_id, "Materiale non specificato")

    try:
        # Converti unita
        loads = convert_loads_to_ta_units(calc_input)
        geom = convert_section_to_ta_geometry(calc_input)
        concrete_law = build_concrete_law_ta(calc_input.material)
        steel_law = build_steel_law_ta(calc_input.material)

        # Calcola proprieta sezione
        props = compute_section_properties(geom)

        # Calcola tensioni (solo flessione, N=0)
        load_state = LoadState(Nx=0.0, My=loads["Mx_kg_cm"], Mz=loads["My_kg_cm"])
        stresses = compute_normal_stresses_ta(geom, props, load_state, concrete_law, steel_law)

        # Tensioni ammissibili DM96
        adm = get_dm96_allowable_stresses(calc_input.material)
        if adm.sigma_c_allow <= 0 or adm.sigma_s_allow <= 0:
            return _make_error_result(
                template.template_id,
                "Tensioni ammissibili DM96 non determinabili dal materiale",
            )

        # Verifica
        limits = AllowableStresses(
            sigma_c_allow=adm.sigma_c_allow,
            sigma_s_allow=adm.sigma_s_allow,
            sigma_c_med_allow=adm.sigma_c_med_allow,
        )
        check = check_allowable_stresses_ta(stresses, limits)

        # Utilizzazione
        util_c = abs(stresses.sigma_c_max) / adm.sigma_c_allow if adm.sigma_c_allow > 0 else 0.0
        util_s = abs(stresses.sigma_s_max) / adm.sigma_s_allow if adm.sigma_s_allow > 0 else 0.0
        utilizzazione = max(util_c, util_s)

        section = calc_input.section
        b_cm = section.width / 10.0
        h_cm = section.height / 10.0

        messages_it = [
            f"Sezione: {b_cm:.1f} x {h_cm:.1f} cm",
            f"Momento: Mx = {calc_input.Mx or 0:.2f} kNm",
            "",
            "Tensioni calcolate (DM 14/02/1992 - metodo TA):",
            f"  sigma_c,max = {abs(stresses.sigma_c_max):.1f} kg/cm2"
            f" (ammissibile: {adm.sigma_c_allow:.1f} kg/cm2)",
            f"  sigma_s,max = {abs(stresses.sigma_s_max):.1f} kg/cm2"
            f" (ammissibile: {adm.sigma_s_allow:.1f} kg/cm2)",
            "",
            f"Utilizzazione: {utilizzazione:.3f} {'OK' if check.ok else 'NON OK'}",
        ]

        return SingleCheckResult(
            template_id=template.template_id,
            ok=check.ok,
            utilisation=utilizzazione,
            details={
                "sigma_c_max_kg_cm2": abs(stresses.sigma_c_max),
                "sigma_s_max_kg_cm2": abs(stresses.sigma_s_max),
                "sigma_c_adm_kg_cm2": adm.sigma_c_allow,
                "sigma_s_adm_kg_cm2": adm.sigma_s_allow,
            },
            norm_references=[
                NormReference(
                    norm_code="DM92",
                    chapter="Cap. 2",
                    paragraph="Tensioni normali ammissibili",
                    description_it="Verifica tensioni ammissibili flessione DM 14/02/1992",
                )
            ],
            messages_it=messages_it,
            limit_state="TA",
        )

    except Exception as e:
        logger.error(f"Errore in check_flessione_ta_dm96: {e}")
        return _make_error_result(template.template_id, f"Errore nel calcolo: {e}")


def check_pressoflessione_ta_dm96(
    calc_input: CalcInput, template: VerificationTemplate
) -> SingleCheckResult:
    """Verifica a pressoflessione metodo TA - DM 14/02/1992.

    Come check_flessione_ta_dm96 ma con sforzo normale N presente.
    Include riduzione sigma_c_adm per sezioni snelle.

    NormReference: DM 14/02/1992 Cap. 2, Art. 4
    """
    if calc_input.section is None:
        return _make_error_result(template.template_id, "Sezione non specificata")
    if calc_input.material is None:
        return _make_error_result(template.template_id, "Materiale non specificato")

    try:
        loads = convert_loads_to_ta_units(calc_input)
        geom = convert_section_to_ta_geometry(calc_input)
        concrete_law = build_concrete_law_ta(calc_input.material)
        steel_law = build_steel_law_ta(calc_input.material)
        props = compute_section_properties(geom)

        load_state = LoadState(Nx=loads["N_kg"], My=loads["Mx_kg_cm"], Mz=loads["My_kg_cm"])
        stresses = compute_normal_stresses_ta(geom, props, load_state, concrete_law, steel_law)

        adm = get_dm96_allowable_stresses(calc_input.material)
        if adm.sigma_c_allow <= 0:
            return _make_error_result(
                template.template_id,
                "Tensioni ammissibili DM96 non determinabili",
            )

        # Riduzione snellezza
        section = calc_input.section
        b_cm = section.width / 10.0
        h_cm = section.height / 10.0
        sigma_c_adm_rid, slenderness_details = apply_slenderness_reduction_ta(
            adm.sigma_c_allow, b_cm, h_cm
        )

        limits = AllowableStresses(
            sigma_c_allow=sigma_c_adm_rid,
            sigma_s_allow=adm.sigma_s_allow,
            sigma_c_med_allow=sigma_c_adm_rid,
        )
        check = check_allowable_stresses_ta(stresses, limits)

        util_c = abs(stresses.sigma_c_max) / sigma_c_adm_rid if sigma_c_adm_rid > 0 else 0.0
        util_s = abs(stresses.sigma_s_max) / adm.sigma_s_allow if adm.sigma_s_allow > 0 else 0.0
        utilizzazione = max(util_c, util_s)

        messages_it = [
            f"Sezione: {b_cm:.1f} x {h_cm:.1f} cm",
            f"N = {calc_input.N or 0:.2f} kN, Mx = {calc_input.Mx or 0:.2f} kNm",
            "",
            "Tensioni calcolate (DM 14/02/1992 - pressoflessione TA):",
            f"  sigma_c,max = {abs(stresses.sigma_c_max):.1f} kg/cm2"
            f" (ammissibile: {sigma_c_adm_rid:.1f} kg/cm2)",
            f"  sigma_s,max = {abs(stresses.sigma_s_max):.1f} kg/cm2"
            f" (ammissibile: {adm.sigma_s_allow:.1f} kg/cm2)",
        ]
        if slenderness_details.get("reduced", False):
            messages_it.append(
                f"  Riduzione snellezza applicata: sigma_c_adm {adm.sigma_c_allow:.1f}"
                f" -> {sigma_c_adm_rid:.1f} kg/cm2"
            )
        messages_it.append("")
        messages_it.append(f"Utilizzazione: {utilizzazione:.3f} {'OK' if check.ok else 'NON OK'}")

        return SingleCheckResult(
            template_id=template.template_id,
            ok=check.ok,
            utilisation=utilizzazione,
            details={
                "sigma_c_max_kg_cm2": abs(stresses.sigma_c_max),
                "sigma_s_max_kg_cm2": abs(stresses.sigma_s_max),
                "sigma_c_adm_kg_cm2": sigma_c_adm_rid,
                "sigma_s_adm_kg_cm2": adm.sigma_s_allow,
                "N_kg": loads["N_kg"],
                "slenderness_reduced": slenderness_details.get("reduced", False),
            },
            norm_references=[
                NormReference(
                    norm_code="DM92",
                    chapter="Cap. 2",
                    paragraph="Tensioni ammissibili - Pressoflessione",
                    description_it="Verifica pressoflessione TA DM 14/02/1992",
                )
            ],
            messages_it=messages_it,
            limit_state="TA",
        )

    except Exception as e:
        logger.error(f"Errore in check_pressoflessione_ta_dm96: {e}")
        return _make_error_result(template.template_id, f"Errore nel calcolo: {e}")


def check_taglio_ta_dm96(
    calc_input: CalcInput, template: VerificationTemplate
) -> SingleCheckResult:
    """Verifica a taglio metodo TA - DM 14/02/1992.

    Calcola la tensione tangenziale tau = V / (b * d) e la confronta
    con tau_c0 (senza staffe) e tau_c1 (massimo con staffe) da DM92.jsoncode.

    NormReference: DM 14/02/1992 Cap. 4 - Tensioni tangenziali ammissibili
    """
    if calc_input.section is None:
        return _make_error_result(template.template_id, "Sezione non specificata")
    if calc_input.material is None:
        return _make_error_result(template.template_id, "Materiale non specificato")

    section = calc_input.section
    b_cm = section.width / 10.0
    h_cm = section.height / 10.0

    # Altezza utile
    d_cm = calc_input.d
    if d_cm is None or d_cm <= 0:
        d_cm = 0.9 * h_cm

    # Taglio in kg
    loads = convert_loads_to_ta_units(calc_input)
    V_kg = max(abs(loads["Tx_kg"]), abs(loads["Ty_kg"]))

    if V_kg <= 0:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=True,
            utilisation=0.0,
            details={"V_kg": 0.0},
            messages_it=["Taglio nullo: verifica non necessaria"],
            limit_state="TA",
        )

    # tau = V / (b * d)
    tau_kg_cm2 = V_kg / (b_cm * d_cm)

    # Limiti DM92
    tau_c0, tau_c1 = _get_dm96_tau_limits(calc_input.material)
    if tau_c0 <= 0 or tau_c1 <= 0:
        return _make_error_result(
            template.template_id,
            "Tensioni tangenziali ammissibili (tau_c0, tau_c1) non determinabili",
        )

    # Verifica
    if tau_kg_cm2 <= tau_c0:
        ok = True
        stato = "tau <= tau_c0: non servono staffe"
    elif tau_kg_cm2 <= tau_c1:
        ok = True
        stato = "tau_c0 < tau <= tau_c1: necessarie staffe a taglio"
    else:
        ok = False
        stato = "tau > tau_c1: sezione insufficiente"

    utilizzazione = tau_kg_cm2 / tau_c1 if tau_c1 > 0 else 999.0

    messages_it = [
        f"Sezione: {b_cm:.1f} x {h_cm:.1f} cm, d = {d_cm:.1f} cm",
        f"Taglio: V = {V_kg:.0f} kg",
        f"tau = V/(b*d) = {tau_kg_cm2:.2f} kg/cm2",
        "",
        "Limiti DM 14/02/1992:",
        f"  tau_c0 = {tau_c0:.1f} kg/cm2 (senza staffe)",
        f"  tau_c1 = {tau_c1:.1f} kg/cm2 (massimo con staffe)",
        f"  {stato}",
        "",
        f"Utilizzazione (su tau_c1): {utilizzazione:.3f} {'OK' if ok else 'NON OK'}",
    ]

    return SingleCheckResult(
        template_id=template.template_id,
        ok=ok,
        utilisation=utilizzazione,
        details={
            "tau_kg_cm2": tau_kg_cm2,
            "tau_c0_kg_cm2": tau_c0,
            "tau_c1_kg_cm2": tau_c1,
            "V_kg": V_kg,
        },
        norm_references=[
            NormReference(
                norm_code="DM92",
                chapter="Cap. 4",
                paragraph="Tensioni tangenziali ammissibili",
                description_it="Verifica a taglio TA DM 14/02/1992",
            )
        ],
        messages_it=messages_it,
        limit_state="TA",
    )


def check_minimi_armatura_ta_dm96(
    calc_input: CalcInput, template: VerificationTemplate
) -> SingleCheckResult:
    """Verifica minimi armatura longitudinale - DM 14/02/1992.

    Utilizza compute_long_rebar_limits_ta con parametri DM96.
    Distinzione travi/pilastri.

    NormReference: DM 14/02/1992 Cap. 5 - Armature minime
    """
    if calc_input.section is None or calc_input.material is None:
        return _make_error_result(template.template_id, "Sezione o materiale non specificati")

    section = calc_input.section
    b_cm = section.width / 10.0
    h_cm = section.height / 10.0
    section_area_cm2 = b_cm * h_cm

    As_cm2 = calc_input.As or 0.0
    N_kg = (calc_input.N or 0.0) * 101.97

    # Determina tipo elemento
    element_type = calc_input.extra.get("element_type", "trave")
    is_column = element_type in ("pilastro", "colonna", "column")
    is_beam = not is_column

    # Proprieta materiale per i limiti
    material = calc_input.material
    fyd = getattr(material, "f_yk", 375.0)
    fctm = getattr(material, "fctm", 2.2)

    limits = compute_long_rebar_limits_ta(
        section_area=section_area_cm2,
        Nx=N_kg,
        fyd=fyd,
        fctm=fctm,
        carbon_fiber_placeholder=None,
        is_column=is_column,
        is_beam=is_beam,
        zona_sismica=False,
    )

    ok = As_cm2 >= limits.Afmin
    As_max_ok = As_cm2 <= limits.Afmax
    overall_ok = ok and As_max_ok
    utilizzazione = limits.Afmin / As_cm2 if As_cm2 > 0 else 999.0

    tipo_str = "pilastro" if is_column else "trave"
    messages_it = [
        f"Sezione: {b_cm:.1f} x {h_cm:.1f} cm ({tipo_str})",
        f"Armatura presente: As = {As_cm2:.2f} cm2",
        f"Armatura minima: As,min = {limits.Afmin:.2f} cm2",
        f"Armatura massima: As,max = {limits.Afmax:.2f} cm2",
        "",
        f"As >= As,min: {'OK' if ok else 'NON OK'}",
        f"As <= As,max: {'OK' if As_max_ok else 'NON OK'}",
        f"Utilizzazione (min): {utilizzazione:.3f}",
    ]

    return SingleCheckResult(
        template_id=template.template_id,
        ok=overall_ok,
        utilisation=utilizzazione,
        details={
            "As_cm2": As_cm2,
            "As_min_cm2": limits.Afmin,
            "As_max_cm2": limits.Afmax,
            "element_type": tipo_str,
        },
        norm_references=[
            NormReference(
                norm_code="DM92",
                chapter="Cap. 5",
                paragraph="Armature minime e massime",
                description_it="Percentuali armatura longitudinale DM 14/02/1992",
            )
        ],
        messages_it=messages_it,
        limit_state="TA",
    )


# ==============================================================================
# SEZIONE C: CHECK SLU DM96 (gamma_c = 1.6)
# ==============================================================================


def check_flessione_slu_dm96(
    calc_input: CalcInput, template: VerificationTemplate
) -> SingleCheckResult:
    """Verifica a flessione SLU - DM 9/1/1996.

    Stesso algoritmo di NTC2018 ma con gamma_c = 1.6 (vs 1.5).
    - f_cd = 0.85 * f_ck / 1.6
    - f_yd = f_yk / 1.15
    - Stress block: lambda=0.8, eta=1.0
    - Duttilita: x/d <= 0.45

    NormReference: DM 9/1/1996 Cap. 3 - Verifica SLU flessione
    """
    if calc_input.section is None or calc_input.material is None:
        return _make_error_result(
            template.template_id, "Sezione o materiale non specificati", "SLU"
        )

    section = calc_input.section
    if not (hasattr(section, "width") and hasattr(section, "height")):
        return _make_error_result(template.template_id, "Geometria sezione non disponibile", "SLU")

    b = section.width  # mm
    h = section.height  # mm

    material = calc_input.material
    f_ck_base = getattr(material, "f_ck", None)
    f_yk_base = getattr(material, "f_yk", None)
    if f_ck_base is None or f_yk_base is None:
        return _make_error_result(
            template.template_id, "Proprieta materiale (f_ck, f_yk) non disponibili", "SLU"
        )

    # LC/FC per strutture esistenti
    if calc_input.lc is not None and calc_input.fc is not None:
        try:
            adjusted = apply_lc_fc_adjustments(material, calc_input.lc, calc_input.fc)
            f_ck = adjusted.f_ck_adjusted
            f_yk = adjusted.f_yk_adjusted
        except ValueError:
            f_ck = f_ck_base
            f_yk = f_yk_base
    else:
        f_ck = f_ck_base
        f_yk = f_yk_base

    # Coefficienti DM96 - gamma_c da template/config, NON hardcodato
    gamma_c = template.extra_params.get("gamma_c", 1.6)
    gamma_s = template.extra_params.get("gamma_s", 1.15)

    f_cd = 0.85 * f_ck / gamma_c  # MPa
    f_yd = f_yk / gamma_s  # MPa

    # Armatura
    As = calc_input.As or 0.0  # cm2
    As_mm2 = As * 100.0
    d = calc_input.d or (h * 0.9 / 10.0)  # cm
    d_mm = d * 10.0

    As_prime = calc_input.As_prime or 0.0
    As_prime_mm2 = As_prime * 100.0
    d_prime = calc_input.d_prime or 4.0  # cm
    d_prime_mm = d_prime * 10.0

    # Momento agente
    Mx = calc_input.Mx or 0.0
    My = calc_input.My or 0.0
    M_Ed = max(abs(Mx), abs(My))  # kNm
    M_Ed_Nmm = M_Ed * 1e6

    # Stress block rettangolare - parametri da template, NON hardcodati
    lambda_factor = template.extra_params.get("lambda_factor", 0.8)

    # Calcolo asse neutro
    if As_prime_mm2 < 0.01:
        x = (As_mm2 * f_yd) / (lambda_factor * b * f_cd) if (lambda_factor * b * f_cd) > 0 else 0.0
        R_s_comp = 0.0
    else:
        x_assumption = (
            ((As_mm2 - As_prime_mm2) * f_yd) / (lambda_factor * b * f_cd)
            if (lambda_factor * b * f_cd) > 0
            else 0.0
        )
        if x_assumption > d_prime_mm:
            x = x_assumption
            R_s_comp = As_prime_mm2 * f_yd
        else:
            x = max(x_assumption, 1.1 * d_prime_mm)
            R_s_comp = As_prime_mm2 * f_yd

    # Limiti duttilita - da template, NON hardcodato
    x_d_limit = template.extra_params.get("x_d_limit", 0.45)
    x_max = x_d_limit * d_mm
    x_limited = x > x_max

    # Bracci e momento resistente
    z_c = d_mm - lambda_factor * x / 2.0
    z_s_comp = d_mm - d_prime_mm
    R_c = lambda_factor * x * b * f_cd
    M_Rd = R_c * z_c + R_s_comp * z_s_comp  # N*mm
    M_Rd_kNm = M_Rd / 1e6

    utilizzazione = M_Ed_Nmm / M_Rd if M_Rd > 0 else 999.0
    ok = utilizzazione <= 1.0 and not x_limited

    messages_it = [
        f"Sezione: {b / 10:.1f} x {h / 10:.1f} cm, d = {d:.1f} cm",
        f"Materiali: f_ck={f_ck:.0f} MPa, f_yk={f_yk:.0f} MPa",
        f"DM96: gamma_c={gamma_c}, gamma_s={gamma_s}",
        f"  f_cd = 0.85*f_ck/gamma_c = {f_cd:.1f} MPa",
        f"  f_yd = f_yk/gamma_s = {f_yd:.0f} MPa",
        "",
        f"Asse neutro: x = {x:.1f} mm (x/d = {x / d_mm:.3f})",
    ]
    if x_limited:
        messages_it.append(f"  x/d = {x / d_mm:.3f} > {x_d_limit}: sezione sovra-armata")
    messages_it.extend(
        [
            "",
            f"M_Ed = {M_Ed:.2f} kNm",
            f"M_Rd = {M_Rd_kNm:.2f} kNm",
            f"Utilizzazione: {utilizzazione:.3f} {'OK' if ok else 'NON OK'}",
        ]
    )

    return SingleCheckResult(
        template_id=template.template_id,
        ok=ok,
        utilisation=utilizzazione,
        details={
            "M_Ed_kNm": M_Ed,
            "M_Rd_kNm": M_Rd_kNm,
            "f_cd_MPa": f_cd,
            "f_yd_MPa": f_yd,
            "gamma_c": gamma_c,
            "gamma_s": gamma_s,
            "x_mm": x,
            "x_over_d": x / d_mm if d_mm > 0 else 0.0,
        },
        norm_references=[
            NormReference(
                norm_code="DM96",
                chapter="Cap. 3",
                paragraph="Verifica SLU flessione",
                description_it="Flessione SLU DM 9/1/1996 (gamma_c=1.6)",
            )
        ],
        messages_it=messages_it,
        limit_state="SLU",
    )


def check_taglio_slu_dm96(
    calc_input: CalcInput, template: VerificationTemplate
) -> SingleCheckResult:
    """Verifica a taglio SLU - DM 9/1/1996.

    Stesso algoritmo NTC2018 ma con gamma_c=1.6.
    V_Rd = min(V_Rd,s, V_Rd,max)
    theta = 21.8 gradi (conservativo).

    NormReference: DM 9/1/1996 Cap. 4 - Verifica SLU taglio
    """
    if calc_input.section is None or calc_input.material is None:
        return _make_error_result(
            template.template_id, "Sezione o materiale non specificati", "SLU"
        )

    section = calc_input.section
    b = section.width  # mm
    h = section.height  # mm

    material = calc_input.material
    f_ck_base = getattr(material, "f_ck", None)
    f_yk_base = getattr(material, "f_yk", None)
    if f_ck_base is None or f_yk_base is None:
        return _make_error_result(
            template.template_id, "Proprieta materiale non disponibili", "SLU"
        )

    if calc_input.lc is not None and calc_input.fc is not None:
        try:
            adjusted = apply_lc_fc_adjustments(material, calc_input.lc, calc_input.fc)
            f_ck = adjusted.f_ck_adjusted
            f_yk = adjusted.f_yk_adjusted
        except ValueError:
            f_ck = f_ck_base
            f_yk = f_yk_base
    else:
        f_ck = f_ck_base
        f_yk = f_yk_base

    gamma_c = template.extra_params.get("gamma_c", 1.6)
    gamma_s = template.extra_params.get("gamma_s", 1.15)
    f_cd = 0.85 * f_ck / gamma_c
    f_yd = f_yk / gamma_s

    d = calc_input.d or (0.9 * h / 10.0)
    d_mm = d * 10.0

    # Staffe
    staffe_diametro = calc_input.staffe_diametro
    staffe_passo = calc_input.staffe_passo
    staffe_num_bracci = calc_input.staffe_num_bracci or 2

    if not staffe_diametro or staffe_diametro <= 0:
        return _make_error_result(
            template.template_id, "Dati staffe mancanti: diametro non specificato", "SLU"
        )
    if not staffe_passo or staffe_passo <= 0:
        return _make_error_result(
            template.template_id, "Dati staffe mancanti: passo non specificato", "SLU"
        )

    s_mm = staffe_passo * 10.0
    A_sw = staffe_num_bracci * math.pi * (staffe_diametro**2) / 4.0
    Asw_over_s = A_sw / s_mm

    Tx = calc_input.Tx or 0.0
    Ty = calc_input.Ty or 0.0
    V_Ed = max(abs(Tx), abs(Ty))
    V_Ed_N = V_Ed * 1000.0

    if V_Ed <= 0:
        return _make_error_result(
            template.template_id, "Taglio agente V_Ed non specificato o nullo", "SLU"
        )

    theta_deg = template.extra_params.get("theta_deg", 21.8)
    theta_rad = theta_deg * math.pi / 180.0
    cot_theta = 1.0 / math.tan(theta_rad)
    tan_theta = math.tan(theta_rad)

    V_Rd_s = Asw_over_s * 0.9 * d_mm * f_yd * cot_theta
    nu = 0.6 * (1.0 - f_ck / 250.0)
    V_Rd_max = 0.9 * d_mm * b * nu * f_cd / (cot_theta + tan_theta)
    V_Rd = min(V_Rd_s, V_Rd_max)
    V_Rd_kN = V_Rd / 1000.0

    ok = V_Ed_N <= V_Rd
    utilizzazione = V_Ed_N / V_Rd if V_Rd > 0 else 999.0

    messages_it = [
        f"Sezione: {b / 10:.1f} x {h / 10:.1f} cm, d = {d:.1f} cm",
        f"DM96 SLU: gamma_c={gamma_c}, f_cd={f_cd:.1f} MPa, f_yd={f_yd:.0f} MPa",
        f"Staffe: phi{staffe_diametro:.0f}/{staffe_passo:.0f}cm, {staffe_num_bracci} bracci",
        "",
        f"V_Rd,s = {V_Rd_s / 1000:.1f} kN, V_Rd,max = {V_Rd_max / 1000:.1f} kN",
        f"V_Rd = min(V_Rd,s, V_Rd,max) = {V_Rd_kN:.1f} kN",
        f"V_Ed = {V_Ed:.1f} kN",
        f"Utilizzazione: {utilizzazione:.3f} {'OK' if ok else 'NON OK'}",
    ]

    return SingleCheckResult(
        template_id=template.template_id,
        ok=ok,
        utilisation=utilizzazione,
        details={
            "V_Ed_kN": V_Ed,
            "V_Rd_kN": V_Rd_kN,
            "V_Rd_s_kN": V_Rd_s / 1000.0,
            "V_Rd_max_kN": V_Rd_max / 1000.0,
            "gamma_c": gamma_c,
            "theta_deg": theta_deg,
        },
        norm_references=[
            NormReference(
                norm_code="DM96",
                chapter="Cap. 4",
                paragraph="Verifica SLU taglio",
                description_it="Taglio SLU DM 9/1/1996 (gamma_c=1.6)",
            )
        ],
        messages_it=messages_it,
        limit_state="SLU",
    )


def check_minimi_armatura_flessione_slu_dm96(
    calc_input: CalcInput, template: VerificationTemplate
) -> SingleCheckResult:
    """Verifica minimi armatura flessione SLU - DM 9/1/1996.

    As,min = max(0.26 * f_ctm / f_yk * b * d, 0.0013 * b * d)

    NormReference: DM 9/1/1996 Cap. 5 - Armature minime flessione
    """
    if calc_input.section is None or calc_input.material is None:
        return _make_error_result(
            template.template_id, "Sezione o materiale non specificati", "SLU"
        )

    section = calc_input.section
    b = section.width
    h = section.height
    material = calc_input.material
    f_ck = getattr(material, "f_ck", None)
    f_yk = getattr(material, "f_yk", None)

    if f_ck is None or f_yk is None:
        return _make_error_result(
            template.template_id, "Proprieta materiale non disponibili", "SLU"
        )

    d = calc_input.d or (0.9 * h / 10.0)
    d_mm = d * 10.0

    f_ctm = getattr(material, "fctm", None)
    if f_ctm is None or f_ctm <= 0:
        f_ctm = (
            0.30 * (f_ck ** (2.0 / 3.0)) if f_ck <= 50 else 2.12 * math.log(1 + (f_ck + 8) / 10.0)
        )

    As = calc_input.As or 0.0
    As_mm2 = As * 100.0

    As_min_1 = 0.26 * f_ctm / f_yk * b * d_mm
    As_min_2 = 0.0013 * b * d_mm
    As_min_mm2 = max(As_min_1, As_min_2)

    ok = As_mm2 >= As_min_mm2
    utilizzazione = As_min_mm2 / As_mm2 if As_mm2 > 0 else 999.0

    messages_it = [
        f"Sezione: {b / 10:.1f} x {h / 10:.1f} cm, d = {d:.1f} cm",
        f"Materiali: f_ck={f_ck:.0f} MPa, f_yk={f_yk:.0f} MPa, f_ctm={f_ctm:.2f} MPa",
        f"As presente: {As:.2f} cm2",
        f"As,min = max({As_min_1 / 100:.2f}, {As_min_2 / 100:.2f}) = {As_min_mm2 / 100:.2f} cm2",
        f"Utilizzazione: {utilizzazione:.3f} {'OK' if ok else 'NON OK'}",
    ]

    return SingleCheckResult(
        template_id=template.template_id,
        ok=ok,
        utilisation=utilizzazione,
        details={
            "As_cm2": As,
            "As_min_cm2": As_min_mm2 / 100.0,
            "f_ctm_MPa": f_ctm,
        },
        norm_references=[
            NormReference(
                norm_code="DM96",
                chapter="Cap. 5",
                paragraph="Armature minime flessione",
                description_it="Minimi armatura flessione SLU DM 9/1/1996",
            )
        ],
        messages_it=messages_it,
        limit_state="SLU",
    )


def check_minimi_armatura_taglio_slu_dm96(
    calc_input: CalcInput, template: VerificationTemplate
) -> SingleCheckResult:
    """Verifica minimi armatura taglio SLU - DM 9/1/1996.

    Asw,min/s = 0.08 * sqrt(f_ck) / f_yk * b

    NormReference: DM 9/1/1996 Cap. 5 - Armature minime taglio
    """
    if calc_input.section is None or calc_input.material is None:
        return _make_error_result(
            template.template_id, "Sezione o materiale non specificati", "SLU"
        )

    section = calc_input.section
    b = section.width
    material = calc_input.material
    f_ck = getattr(material, "f_ck", None)
    f_yk = getattr(material, "f_yk", None)

    if f_ck is None or f_yk is None:
        return _make_error_result(
            template.template_id, "Proprieta materiale non disponibili", "SLU"
        )

    staffe_diametro = calc_input.staffe_diametro
    staffe_passo = calc_input.staffe_passo
    staffe_num_bracci = calc_input.staffe_num_bracci or 2

    if not staffe_diametro or staffe_diametro <= 0 or not staffe_passo or staffe_passo <= 0:
        return _make_error_result(template.template_id, "Dati staffe mancanti o non validi", "SLU")

    s_mm = staffe_passo * 10.0
    A_sw = staffe_num_bracci * math.pi * (staffe_diametro**2) / 4.0
    Asw_over_s_actual = A_sw / s_mm

    Asw_min_over_s = 0.08 * math.sqrt(f_ck) / f_yk * b

    ok = Asw_over_s_actual >= Asw_min_over_s
    utilizzazione = Asw_min_over_s / Asw_over_s_actual if Asw_over_s_actual > 0 else 999.0

    messages_it = [
        f"Staffe: phi{staffe_diametro:.0f}/{staffe_passo:.0f}cm, {staffe_num_bracci} bracci",
        f"Asw/s effettivo = {Asw_over_s_actual:.4f} mm2/mm",
        f"Asw,min/s = 0.08*sqrt({f_ck:.0f})/{f_yk:.0f}*{b:.0f} = {Asw_min_over_s:.4f} mm2/mm",
        f"Utilizzazione: {utilizzazione:.3f} {'OK' if ok else 'NON OK'}",
    ]

    return SingleCheckResult(
        template_id=template.template_id,
        ok=ok,
        utilisation=utilizzazione,
        details={
            "Asw_over_s_actual_mm2_mm": Asw_over_s_actual,
            "Asw_min_over_s_mm2_mm": Asw_min_over_s,
        },
        norm_references=[
            NormReference(
                norm_code="DM96",
                chapter="Cap. 5",
                paragraph="Armature minime taglio",
                description_it="Minimi armatura taglio SLU DM 9/1/1996",
            )
        ],
        messages_it=messages_it,
        limit_state="SLU",
    )


# ==============================================================================
# SEZIONE D: CHECK SLE DM96 (fessurazione e deformazioni)
# ==============================================================================


def check_fessurazione_sle_dm96(
    calc_input: CalcInput, template: VerificationTemplate
) -> SingleCheckResult:
    """Verifica fessurazione SLE - DM 9/1/1996.

    Calcola l'ampiezza delle fessure w in funzione della tensione nell'acciaio,
    del diametro e passo delle barre, della classe ambientale.
    Confronta con w_amm (da template/config, NON hardcodato).

    Parametri configurabili (da template.extra_params o CalcInput.extra):
    - w_amm_mm: ampiezza fessura ammissibile [mm]
    - environmental_class: classe ambientale
    - bar_diameter_mm: diametro barra longitudinale [mm]
    - bar_spacing_mm: passo barre longitudinali [mm]

    NormReference: DM 9/1/1996, EC2 §7.3

    TODO: completare formula calcolo w con parametri specifici DM96.
    Per ora implementazione semplificata.
    """
    if calc_input.section is None or calc_input.material is None:
        return _make_error_result(
            template.template_id, "Sezione o materiale non specificati", "SLE"
        )

    # Parametri da template (NON hardcodati)
    w_amm = template.extra_params.get("w_amm_mm", None)
    if w_amm is None:
        w_amm = calc_input.extra.get("w_amm_mm", None)
    if w_amm is None:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={},
            messages_it=[
                "Ampiezza fessura ammissibile (w_amm) non specificata.",
                "Impostare w_amm_mm nel template o in CalcInput.extra.",
                "TODO: completare implementazione verifica fessurazione DM96.",
            ],
            limit_state="SLE",
            norm_references=[
                NormReference(
                    norm_code="DM96",
                    chapter="Cap. SLE",
                    paragraph="Fessurazione",
                    description_it="Verifica fessurazione SLE DM 9/1/1996",
                )
            ],
        )

    # Dati sezione e materiale
    section = calc_input.section
    material = calc_input.material
    b = section.width  # mm
    h = section.height  # mm
    d_cm = calc_input.d or (h * 0.9 / 10.0)  # cm
    d_mm = d_cm * 10.0
    As_cm2 = calc_input.As or 0.0
    As_mm2 = As_cm2 * 100.0

    # Copriferro e diametro barre
    bar_diameter_mm = template.extra_params.get("bar_diameter_mm", None)
    if bar_diameter_mm is None:
        bar_diameter_mm = calc_input.extra.get("bar_diameter_mm", 16.0)
    c_mm = template.extra_params.get("cover_mm", None)
    if c_mm is None:
        c_mm = calc_input.extra.get("cover_mm", 30.0)

    # Modulo elastico acciaio e calcestruzzo
    Es = getattr(material, "Es", None) or getattr(material, "E_s", 206000.0)  # MPa
    f_ck = getattr(material, "f_ck", 25.0)  # MPa
    Ecm = getattr(material, "Ecm", None) or getattr(
        material, "E_cm", 22000.0 * (f_ck / 10.0) ** 0.3
    )
    f_ct_eff = getattr(material, "f_ctm", None) or 0.30 * f_ck ** (2.0 / 3.0)  # MPa

    # Tensione acciaio in esercizio (EC2 §7.3.4)
    Mx = calc_input.Mx or 0.0
    My = calc_input.My or 0.0
    M_sle = max(abs(Mx), abs(My))  # kNm
    M_sle_Nmm = M_sle * 1e6

    # Coefficiente di omogenizzazione
    n = Es / Ecm if Ecm > 0 else 15.0

    # Asse neutro in esercizio (sezione parzializzata)
    rho = As_mm2 / (b * d_mm) if (b * d_mm) > 0 else 0.0
    if rho > 0:
        xi = n * rho * (-1.0 + math.sqrt(1.0 + 2.0 / (n * rho)))
    else:
        xi = 0.5
    x_sle = xi * d_mm
    z_sle = d_mm - x_sle / 3.0

    # Tensione nell'acciaio
    sigma_s = M_sle_Nmm / (As_mm2 * z_sle) if (As_mm2 * z_sle) > 0 else 0.0

    # Calcolo ampiezza fessure EC2 §7.3.4
    # s_r,max = 3.4*c + 0.425*k1*k2*phi/rho_p_eff
    k1 = 0.8  # barre ad aderenza migliorata
    k2 = 0.5  # flessione
    k_t = 0.6  # carico di breve durata (0.4 per lungo termine)
    k_t = template.extra_params.get("k_t", k_t)

    h_c_ef = min(2.5 * (h - d_mm), (h - x_sle) / 3.0, h / 2.0)
    A_c_eff = b * h_c_ef if h_c_ef > 0 else b * 50.0
    rho_p_eff = As_mm2 / A_c_eff if A_c_eff > 0 else 0.01

    s_r_max = 3.4 * c_mm + 0.425 * k1 * k2 * bar_diameter_mm / rho_p_eff

    # Deformazione media differenziale
    eps_sm_cm = (sigma_s - k_t * f_ct_eff / rho_p_eff * (1.0 + n * rho_p_eff)) / Es
    eps_min = 0.6 * sigma_s / Es
    eps_diff = max(eps_sm_cm, eps_min)

    w_k = s_r_max * eps_diff  # mm
    w_k = max(w_k, 0.0)

    utilizzazione = w_k / w_amm if w_amm > 0 else 999.0
    ok = w_k <= w_amm

    messages_it = [
        f"Sezione: {b / 10:.1f} x {h / 10:.1f} cm, d = {d_cm:.1f} cm",
        f"Armatura tesa: As = {As_cm2:.2f} cm²",
        f"Copriferro: c = {c_mm:.0f} mm, diametro barre: φ = {bar_diameter_mm:.0f} mm",
        "",
        f"Momento SLE: M = {M_sle:.2f} kNm",
        f"Tensione acciaio: σ_s = {sigma_s:.1f} MPa",
        f"Asse neutro SLE: x = {x_sle:.1f} mm",
        "",
        f"s_r,max = {s_r_max:.1f} mm",
        f"w_k = {w_k:.3f} mm",
        f"w_amm = {w_amm} mm",
        f"Utilizzazione: {utilizzazione:.3f} {'OK' if ok else 'NON OK'}",
    ]

    return SingleCheckResult(
        template_id=template.template_id,
        ok=ok,
        utilisation=utilizzazione,
        details={
            "w_k_mm": round(w_k, 4),
            "w_amm_mm": w_amm,
            "sigma_s_MPa": round(sigma_s, 1),
            "s_r_max_mm": round(s_r_max, 1),
            "x_sle_mm": round(x_sle, 1),
        },
        messages_it=messages_it,
        limit_state="SLE",
        norm_references=[
            NormReference(
                norm_code="DM96",
                chapter="Cap. SLE",
                paragraph="Fessurazione",
                description_it="Verifica fessurazione SLE DM 9/1/1996 / EC2 §7.3.4",
            )
        ],
    )


def check_deformazioni_sle_dm96(
    calc_input: CalcInput, template: VerificationTemplate
) -> SingleCheckResult:
    """Verifica deformazioni (frecce) SLE - DM 9/1/1996.

    Calcola frecce istantanee e a lungo termine, confronta con limiti
    (es. L/250, L/300) letti da template/config (NON hardcodati).

    Parametri configurabili (da template.extra_params o CalcInput.extra):
    - span_mm: luce dell'elemento [mm]
    - deflection_limit_ratio: rapporto limite (es. 250 per L/250)
    - creep_coefficient: coefficiente di fluage
    - shrinkage_strain: deformazione da ritiro

    NormReference: DM 9/1/1996, EC2 §7.4

    TODO: implementazione completa calcolo frecce con I_eff, fluage, ritiro.
    """
    if calc_input.section is None or calc_input.material is None:
        return _make_error_result(
            template.template_id, "Sezione o materiale non specificati", "SLE"
        )

    span_mm = template.extra_params.get("span_mm", None)
    if span_mm is None:
        span_mm = calc_input.extra.get("span_mm", None)

    deflection_limit_ratio = template.extra_params.get("deflection_limit_ratio", None)
    if deflection_limit_ratio is None:
        deflection_limit_ratio = calc_input.extra.get("deflection_limit_ratio", None)

    if span_mm is None or deflection_limit_ratio is None:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={},
            messages_it=[
                "Parametri deformazione non specificati.",
                "Impostare span_mm e deflection_limit_ratio nel template o CalcInput.extra.",
                "TODO: completare implementazione verifica deformazioni DM96.",
            ],
            limit_state="SLE",
            norm_references=[
                NormReference(
                    norm_code="DM96",
                    chapter="Cap. SLE",
                    paragraph="Deformazioni",
                    description_it="Verifica deformazioni SLE DM 9/1/1996",
                )
            ],
        )

    delta_amm = span_mm / deflection_limit_ratio

    # Dati sezione e materiale
    section = calc_input.section
    material = calc_input.material
    b = section.width  # mm
    h = section.height  # mm
    d_cm = calc_input.d or (h * 0.9 / 10.0)
    d_mm = d_cm * 10.0
    As_cm2 = calc_input.As or 0.0
    As_mm2 = As_cm2 * 100.0

    f_ck = getattr(material, "f_ck", 25.0)  # MPa
    Es = getattr(material, "Es", None) or getattr(material, "E_s", 206000.0)
    Ecm = getattr(material, "Ecm", None) or getattr(
        material, "E_cm", 22000.0 * (f_ck / 10.0) ** 0.3
    )
    f_ct_eff = getattr(material, "f_ctm", None) or 0.30 * f_ck ** (2.0 / 3.0)

    # Coefficienti fluage e ritiro da config
    phi_creep = template.extra_params.get("creep_coefficient", None)
    if phi_creep is None:
        phi_creep = calc_input.extra.get("creep_coefficient", 2.0)

    # Modulo efficace a lungo termine
    Ec_eff = Ecm / (1.0 + phi_creep)
    n_lt = Es / Ec_eff if Ec_eff > 0 else 15.0

    # Momento di inerzia sezione reagente (stadio I)
    I_g = b * h**3 / 12.0  # mm4

    # Momento di fessurazione
    W_inf = I_g / (h / 2.0) if h > 0 else 1.0
    M_cr = f_ct_eff * W_inf  # N*mm
    M_cr_kNm = M_cr / 1e6

    # Momento agente SLE
    Mx = calc_input.Mx or 0.0
    My = calc_input.My or 0.0
    M_sle = max(abs(Mx), abs(My))
    M_sle_Nmm = M_sle * 1e6

    # Inerzia sezione fessurata (stadio II) con n lungo termine
    rho = As_mm2 / (b * d_mm) if (b * d_mm) > 0 else 0.0
    if rho > 0:
        xi = n_lt * rho * (-1.0 + math.sqrt(1.0 + 2.0 / (n_lt * rho)))
    else:
        xi = 0.5
    x_cr = xi * d_mm
    I_cr = b * x_cr**3 / 3.0 + n_lt * As_mm2 * (d_mm - x_cr) ** 2

    # Inerzia efficace (metodo Branson, EC2 §7.4.3)
    if M_sle_Nmm > 0 and M_sle_Nmm >= M_cr:
        beta_ratio = (M_cr / M_sle_Nmm) ** 3
        I_eff = beta_ratio * I_g + (1.0 - beta_ratio) * I_cr
        I_eff = max(I_eff, I_cr)
    elif M_sle_Nmm > 0:
        I_eff = I_g  # non fessurata
    else:
        I_eff = I_g

    # Freccia istantanea (trave semplicemente appoggiata, carico uniforme equiv.)
    # delta = 5/48 * M * L^2 / (E*I)  (formula semplificata)
    delta_inst = 5.0 / 48.0 * M_sle_Nmm * span_mm**2 / (Ecm * I_eff) if (Ecm * I_eff) > 0 else 0.0

    # Freccia a lungo termine
    delta_lt = delta_inst * (1.0 + phi_creep)

    utilizzazione = delta_lt / delta_amm if delta_amm > 0 else 999.0
    ok = delta_lt <= delta_amm

    messages_it = [
        f"Sezione: {b / 10:.1f} x {h / 10:.1f} cm, d = {d_cm:.1f} cm",
        f"Luce: L = {span_mm:.0f} mm",
        f"Limite: L/{deflection_limit_ratio:.0f} = {delta_amm:.1f} mm",
        "",
        f"Momento SLE: M = {M_sle:.2f} kNm",
        f"Momento di fessurazione: M_cr = {M_cr_kNm:.2f} kNm",
        f"Coeff. fluage: φ = {phi_creep:.1f}",
        "",
        f"I_g = {I_g:.0f} mm⁴, I_cr = {I_cr:.0f} mm⁴, I_eff = {I_eff:.0f} mm⁴",
        f"Freccia istantanea: δ_inst = {delta_inst:.2f} mm",
        f"Freccia lungo termine: δ_lt = {delta_lt:.2f} mm",
        f"Utilizzazione: {utilizzazione:.3f} {'OK' if ok else 'NON OK'}",
    ]

    return SingleCheckResult(
        template_id=template.template_id,
        ok=ok,
        utilisation=utilizzazione,
        details={
            "span_mm": span_mm,
            "deflection_limit_ratio": deflection_limit_ratio,
            "delta_amm_mm": round(delta_amm, 2),
            "delta_inst_mm": round(delta_inst, 2),
            "delta_lt_mm": round(delta_lt, 2),
            "M_cr_kNm": round(M_cr_kNm, 2),
            "I_eff_mm4": round(I_eff, 0),
            "phi_creep": phi_creep,
        },
        messages_it=messages_it,
        limit_state="SLE",
        norm_references=[
            NormReference(
                norm_code="DM96",
                chapter="Cap. SLE",
                paragraph="Deformazioni",
                description_it="Verifica deformazioni SLE DM 9/1/1996 / EC2 §7.4",
            )
        ],
    )


# ==============================================================================
# SEZIONE E: CHECK SLU AGGIUNTIVI DM96
# ==============================================================================


def check_torsione_slu_dm96(
    calc_input: CalcInput, template: VerificationTemplate
) -> SingleCheckResult:
    """Verifica a torsione SLU - DM 9/1/1996.

    Verifica torsione con modello a traliccio (thin-walled analogy).
    T_Rd = 2 * A_k * t_ef * f_cd * sin(theta) * cos(theta)

    Parametri configurabili (da template.extra_params o CalcInput.extra):
    - theta_torsion_deg: angolo inclinazione biella (default da template)

    NormReference: DM 9/1/1996, EC2 §6.3

    TODO: implementazione completa. Richiede definizione A_k (area nucleo),
    t_ef (spessore efficace), armature trasversali e longitudinali a torsione.
    """
    if calc_input.section is None or calc_input.material is None:
        return _make_error_result(
            template.template_id, "Sezione o materiale non specificati", "SLU"
        )

    Mz = calc_input.Mz or 0.0
    if abs(Mz) < 1e-6:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=True,
            utilisation=0.0,
            details={"T_Ed_kNm": 0.0},
            messages_it=["Momento torcente nullo: verifica non necessaria."],
            limit_state="SLU",
        )

    section = calc_input.section
    material = calc_input.material
    b = section.width  # mm
    h = section.height  # mm

    f_ck = getattr(material, "f_ck", 25.0)
    f_yk = getattr(material, "f_yk", 450.0)

    gamma_c = template.extra_params.get("gamma_c", 1.6)
    gamma_s = template.extra_params.get("gamma_s", 1.15)
    f_cd = 0.85 * f_ck / gamma_c
    f_yd = f_yk / gamma_s

    # Copriferro per nucleo
    c_mm = template.extra_params.get("cover_mm", None)
    if c_mm is None:
        c_mm = calc_input.extra.get("cover_mm", 30.0)
    staffe_diam = calc_input.staffe_diametro or 8.0

    # Spessore efficace t_ef (EC2 §6.3.2)
    t_ef = template.extra_params.get("t_ef_mm", None)
    if t_ef is None:
        t_ef = calc_input.extra.get("t_ef_mm", None)
    if t_ef is None:
        A_tot = b * h
        u_tot = 2.0 * (b + h)
        t_ef = max(A_tot / u_tot, 2.0 * c_mm) if u_tot > 0 else 50.0

    # Area nucleo A_k e perimetro u_k
    b_k = b - 2.0 * t_ef
    h_k = h - 2.0 * t_ef
    if b_k <= 0 or h_k <= 0:
        b_k = b - 2.0 * c_mm
        h_k = h - 2.0 * c_mm
    A_k = max(b_k * h_k, 1.0)

    # Angolo inclinazione biella
    theta_deg = template.extra_params.get("theta_torsion_deg", 45.0)
    theta = math.radians(theta_deg)

    T_Ed = abs(Mz)  # kNm
    T_Ed_Nmm = T_Ed * 1e6

    # Resistenza massima della biella compressa (EC2 §6.3.2 eq. 6.30)
    # T_Rd,max = 2 * nu * alpha_cw * f_cd * A_k * t_ef * sin(theta) * cos(theta)
    nu = 0.6 * (1.0 - f_ck / 250.0)
    T_Rd_max = 2.0 * nu * f_cd * A_k * t_ef * math.sin(theta) * math.cos(theta)
    T_Rd_max_kNm = T_Rd_max / 1e6

    utilizzazione = T_Ed_Nmm / T_Rd_max if T_Rd_max > 0 else 999.0
    ok = utilizzazione <= 1.0

    messages_it = [
        f"Sezione: {b / 10:.1f} x {h / 10:.1f} cm",
        f"DM96: gamma_c={gamma_c}, gamma_s={gamma_s}",
        f"  f_cd = {f_cd:.1f} MPa, ν = {nu:.3f}",
        "",
        f"Spessore efficace: t_ef = {t_ef:.1f} mm",
        f"Area nucleo: A_k = {A_k:.0f} mm²",
        f"Angolo biella: θ = {theta_deg:.0f}°",
        "",
        f"T_Ed = {T_Ed:.2f} kNm",
        f"T_Rd,max = {T_Rd_max_kNm:.2f} kNm",
        f"Utilizzazione: {utilizzazione:.3f} {'OK' if ok else 'NON OK'}",
    ]

    return SingleCheckResult(
        template_id=template.template_id,
        ok=ok,
        utilisation=utilizzazione,
        details={
            "T_Ed_kNm": T_Ed,
            "T_Rd_max_kNm": round(T_Rd_max_kNm, 2),
            "t_ef_mm": round(t_ef, 1),
            "A_k_mm2": round(A_k, 0),
            "theta_deg": theta_deg,
            "nu": round(nu, 3),
        },
        messages_it=messages_it,
        limit_state="SLU",
        norm_references=[
            NormReference(
                norm_code="DM96",
                chapter="Cap. 4",
                paragraph="Torsione SLU",
                description_it="Verifica torsione SLU DM 9/1/1996 / EC2 §6.3",
            )
        ],
    )


def check_punzonamento_slu_dm96(
    calc_input: CalcInput, template: VerificationTemplate
) -> SingleCheckResult:
    """Verifica punzonamento SLU - DM 9/1/1996.

    Verifica resistenza a punzonamento per piastre/solai.
    v_Ed = V_Ed / (u_1 * d)
    v_Rd,c = C_Rd,c * k * (100 * rho_l * f_ck)^(1/3)

    Parametri configurabili (da template.extra_params o CalcInput.extra):
    - column_dimensions: dimensioni pilastro [mm x mm]
    - load_eccentricity: eccentricita del carico

    NormReference: DM 9/1/1996, EC2 §6.4

    TODO: implementazione completa. Richiede perimetro critico u_1,
    percentuale armatura rho_l, coefficiente k.
    """
    if calc_input.section is None or calc_input.material is None:
        return _make_error_result(
            template.template_id, "Sezione o materiale non specificati", "SLU"
        )

    section = calc_input.section
    material = calc_input.material
    b = section.width  # mm (larghezza piastra / lato sezione)
    h = section.height  # mm (spessore piastra)

    d_cm = calc_input.d or (h * 0.9 / 10.0)
    d_mm = d_cm * 10.0
    As_cm2 = calc_input.As or 0.0
    As_mm2 = As_cm2 * 100.0

    f_ck = getattr(material, "f_ck", 25.0)  # MPa

    gamma_c = template.extra_params.get("gamma_c", 1.6)

    # Forza di punzonamento V_Ed
    N = calc_input.N or 0.0  # kN (forza applicata dal pilastro)
    V_Ed = abs(N)
    V_Ed_N = V_Ed * 1000.0

    # Dimensioni pilastro (rettangolare)
    col_dims = template.extra_params.get("column_dimensions", None)
    if col_dims is None:
        col_dims = calc_input.extra.get("column_dimensions", None)
    if col_dims is None:
        # Usa dimensioni sezione come default pilastro
        c1 = b  # mm
        c2 = b  # mm (pilastro quadrato)
    elif isinstance(col_dims, (list, tuple)) and len(col_dims) >= 2:
        c1, c2 = col_dims[0], col_dims[1]
    else:
        c1 = c2 = float(col_dims)

    # Perimetro critico a 2d dal pilastro (EC2 §6.4.2)
    u_1 = 2.0 * (c1 + c2) + 2.0 * math.pi * 2.0 * d_mm

    # Coefficiente beta per eccentricità carico
    beta = template.extra_params.get("punching_beta", 1.15)

    # Tensione di punzonamento v_Ed
    v_Ed = beta * V_Ed_N / (u_1 * d_mm) if (u_1 * d_mm) > 0 else 0.0

    # Resistenza a punzonamento senza armatura (EC2 §6.4.4 eq. 6.47)
    # v_Rd,c = C_Rd,c * k * (100 * rho_l * f_ck)^(1/3) >= v_min
    C_Rd_c = 0.18 / gamma_c
    k = min(1.0 + math.sqrt(200.0 / d_mm), 2.0) if d_mm > 0 else 2.0

    # Percentuale armatura (media delle due direzioni)
    rho_l = As_mm2 / (b * d_mm) if (b * d_mm) > 0 else 0.0
    rho_l = min(rho_l, 0.02)  # EC2 limita a 2%

    v_Rd_c = C_Rd_c * k * (100.0 * rho_l * f_ck) ** (1.0 / 3.0)
    v_min = 0.035 * k**1.5 * f_ck**0.5
    v_Rd_c = max(v_Rd_c, v_min)

    utilizzazione = v_Ed / v_Rd_c if v_Rd_c > 0 else 999.0
    ok = v_Ed <= v_Rd_c

    messages_it = [
        f"Piastra: spessore = {h / 10:.1f} cm, d = {d_cm:.1f} cm",
        f"Pilastro: {c1:.0f} x {c2:.0f} mm",
        f"DM96: gamma_c = {gamma_c}",
        "",
        f"V_Ed = {V_Ed:.2f} kN (β = {beta})",
        f"Perimetro critico: u_1 = {u_1:.0f} mm",
        f"v_Ed = {v_Ed:.3f} MPa",
        "",
        f"k = {k:.3f}, ρ_l = {rho_l:.4f}",
        f"v_Rd,c = {v_Rd_c:.3f} MPa (v_min = {v_min:.3f} MPa)",
        f"Utilizzazione: {utilizzazione:.3f} {'OK' if ok else 'NON OK'}",
    ]

    return SingleCheckResult(
        template_id=template.template_id,
        ok=ok,
        utilisation=utilizzazione,
        details={
            "V_Ed_kN": V_Ed,
            "v_Ed_MPa": round(v_Ed, 4),
            "v_Rd_c_MPa": round(v_Rd_c, 4),
            "u_1_mm": round(u_1, 0),
            "k": round(k, 3),
            "rho_l": round(rho_l, 4),
        },
        messages_it=messages_it,
        limit_state="SLU",
        norm_references=[
            NormReference(
                norm_code="DM96",
                chapter="Cap. 4",
                paragraph="Punzonamento SLU",
                description_it="Verifica punzonamento SLU DM 9/1/1996 / EC2 §6.4",
            )
        ],
    )


def check_instabilita_compressione_slu_dm96(
    calc_input: CalcInput, template: VerificationTemplate
) -> SingleCheckResult:
    """Verifica instabilita/snellezza per elementi compressi - DM 9/1/1996.

    Verifica di instabilita per pilastri compressi snelli.
    lambda = l_0 / i (snellezza)
    Metodo di calcolo: amplificazione momento (metodo semplificato) o
    analisi al secondo ordine.

    Parametri configurabili (da template.extra_params o CalcInput.extra):
    - l_0_mm: lunghezza libera di inflessione [mm]
    - restraint_conditions: condizioni di vincolo

    NormReference: DM 9/1/1996, EC2 §5.8

    TODO: implementazione completa. Richiede lunghezza libera l_0,
    raggio di inerzia i, condizioni di vincolo.
    """
    if calc_input.section is None or calc_input.material is None:
        return _make_error_result(
            template.template_id, "Sezione o materiale non specificati", "SLU"
        )

    l_0 = template.extra_params.get("l_0_mm", None)
    if l_0 is None:
        l_0 = calc_input.extra.get("l_0_mm", None)

    section = calc_input.section
    material = calc_input.material
    b = section.width  # mm
    h = section.height  # mm
    i_min = min(b, h) / math.sqrt(12)  # raggio di inerzia minimo (sez. rettangolare)

    if l_0 is None or l_0 <= 0:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={"i_min_mm": round(i_min, 1)},
            messages_it=[
                f"Sezione: {b / 10:.1f} x {h / 10:.1f} cm",
                "Lunghezza libera l_0 non specificata.",
                "Impostare l_0_mm nel template o CalcInput.extra.",
            ],
            limit_state="SLU",
            norm_references=[
                NormReference(
                    norm_code="DM96",
                    chapter="Cap. 5",
                    paragraph="Instabilita elementi compressi",
                    description_it="Verifica instabilita SLU DM 9/1/1996",
                )
            ],
        )

    lam = l_0 / i_min if i_min > 0 else 999.0

    # Snellezza limite (EC2 §5.8.3.1)
    # lambda_lim = 20 * A * B * C / sqrt(n)
    # Semplificazione: lambda_lim da template o default 75
    lam_lim = template.extra_params.get("lambda_limit", 75.0)

    f_ck = getattr(material, "f_ck", 25.0)
    f_yk = getattr(material, "f_yk", 450.0)
    gamma_c = template.extra_params.get("gamma_c", 1.6)
    gamma_s = template.extra_params.get("gamma_s", 1.15)
    f_cd = 0.85 * f_ck / gamma_c
    f_yd = f_yk / gamma_s

    # Sforzo normale e momento
    N = calc_input.N or 0.0  # kN
    N_N = abs(N) * 1000.0  # N
    Mx = calc_input.Mx or 0.0
    My = calc_input.My or 0.0
    M_Ed = max(abs(Mx), abs(My))  # kNm

    if lam <= lam_lim:
        # Pilastro tozzo: effetti del 2° ordine trascurabili
        ok = True
        utilizzazione = lam / lam_lim
        messages_it = [
            f"Sezione: {b / 10:.1f} x {h / 10:.1f} cm",
            f"Lunghezza libera: l_0 = {l_0:.0f} mm",
            f"Raggio inerzia minimo: i_min = {i_min:.1f} mm",
            f"Snellezza: λ = {lam:.1f} ≤ λ_lim = {lam_lim:.0f}",
            "",
            "Effetti del secondo ordine trascurabili.",
            f"Utilizzazione (snellezza): {utilizzazione:.3f} OK",
        ]
        details = {
            "lambda": round(lam, 1),
            "lambda_limit": lam_lim,
            "l_0_mm": l_0,
            "i_min_mm": round(i_min, 1),
        }
    else:
        # Pilastro snello: metodo amplificazione momento (EC2 §5.8.7)
        # e_a = l_0 / 400 (eccentricità accidentale)
        # e_2 = (1/r) * l_0^2 / c  dove c=10 per carichi costanti
        # M_Ed,tot = M_0 + N * (e_a + e_2)
        A_c = b * h  # mm2
        e_0 = M_Ed * 1e6 / N_N if N_N > 0 else 0.0  # mm
        e_a = l_0 / 400.0  # eccentricità accidentale
        e_min = max(20.0, h / 30.0)  # eccentricità minima

        # Curvatura 1/r (EC2 §5.8.8.3)
        d_mm = (calc_input.d or (h * 0.9 / 10.0)) * 10.0
        eps_yd = f_yd / Es if (Es := getattr(material, "Es", None) or 206000.0) > 0 else 0.002
        one_over_r = 2.0 * eps_yd / (0.45 * d_mm) if d_mm > 0 else 0.0
        c_factor = 10.0  # per carichi costanti
        e_2 = one_over_r * l_0**2 / c_factor

        e_tot = max(e_0, e_min) + e_a + e_2
        M_Ed_tot = N_N * e_tot / 1e6  # kNm

        # Momento resistente semplificato (sezione rettangolare, armatura simmetrica)
        As_cm2 = calc_input.As or 0.0
        As_mm2 = As_cm2 * 100.0
        d_prime_mm = (calc_input.d_prime or 4.0) * 10.0
        z_s = d_mm - d_prime_mm

        # N_Rd = A_c * f_cd + As * f_yd (compressione pura)
        M_Rd_approx = As_mm2 * f_yd * z_s / 2.0 / 1e6  # kNm (approssimazione)

        utilizzazione = M_Ed_tot / M_Rd_approx if M_Rd_approx > 0 else 999.0
        ok = utilizzazione <= 1.0

        messages_it = [
            f"Sezione: {b / 10:.1f} x {h / 10:.1f} cm",
            f"DM96: gamma_c={gamma_c}, gamma_s={gamma_s}",
            f"Lunghezza libera: l_0 = {l_0:.0f} mm",
            f"Snellezza: λ = {lam:.1f} > λ_lim = {lam_lim:.0f} → pilastro snello",
            "",
            f"N_Ed = {abs(N):.2f} kN, M_Ed = {M_Ed:.2f} kNm",
            f"Eccentricità: e_0 = {e_0:.1f} mm, e_a = {e_a:.1f} mm, e_2 = {e_2:.1f} mm",
            f"M_Ed,tot = {M_Ed_tot:.2f} kNm (con effetti 2° ordine)",
            f"M_Rd ≈ {M_Rd_approx:.2f} kNm",
            f"Utilizzazione: {utilizzazione:.3f} {'OK' if ok else 'NON OK'}",
        ]
        details = {
            "lambda": round(lam, 1),
            "lambda_limit": lam_lim,
            "l_0_mm": l_0,
            "i_min_mm": round(i_min, 1),
            "e_0_mm": round(e_0, 1),
            "e_a_mm": round(e_a, 1),
            "e_2_mm": round(e_2, 1),
            "M_Ed_tot_kNm": round(M_Ed_tot, 2),
        }

    return SingleCheckResult(
        template_id=template.template_id,
        ok=ok,
        utilisation=utilizzazione,
        details=details,
        messages_it=messages_it,
        limit_state="SLU",
        norm_references=[
            NormReference(
                norm_code="DM96",
                chapter="Cap. 5",
                paragraph="Instabilita elementi compressi",
                description_it="Verifica instabilita SLU DM 9/1/1996 / EC2 §5.8",
            )
        ],
    )


# ==============================================================================
# SEZIONE F: GANCI PRECOMPRESSIONE (c.a.p.)
# ==============================================================================


def compute_precompression_effects_dm96(
    precompression_data: Any,
    section_geometry: Any,
    concrete_law: Any,
) -> dict:
    """Calcola gli effetti della precompressione su una sezione.

    Calcola N_p (sforzo normale) e M_p (momento) dovuti alla precompressione,
    e le tensioni nel calcestruzzo dovute al solo effetto di precompressione.

    Parametri
    ---------
    precompression_data : PrecompressionData (o compatibile)
        Dati di precompressione dell'elemento.
    section_geometry : SectionGeometry (o compatibile)
        Geometria della sezione.
    concrete_law : ConcreteLawTA (o compatibile)
        Legge costitutiva del calcestruzzo.

    Ritorna
    -------
    dict
        Dizionario con effetti calcolati.
        TODO: definire struttura di ritorno completa.

    NormReference: DM 14/02/1992, DM 9/1/1996, EC2 §5.10

    TODO: implementazione completa. Richiede:
    - calcolo forza di precompressione netta (dopo perdite)
    - eccentricita dei cavi rispetto al baricentro
    - distribuzione tensioni nella sezione
    """
    # TODO: implementazione completa
    return {
        "N_p_kN": 0.0,
        "M_p_kNm": 0.0,
        "sigma_c_top_MPa": 0.0,
        "sigma_c_bottom_MPa": 0.0,
        "implementation_status": "TODO",
        "note": "Funzione placeholder - implementazione da completare",
    }


def estimate_prestress_losses_dm96(
    precompression_data: Any,
    material_concrete: Any,
    material_prestressing: Any,
    user_config: dict | None = None,
) -> dict:
    """Stima le perdite di precompressione (istantanee e differite).

    Nessun coefficiente hardcodato: tutti i parametri di perdita devono
    essere forniti tramite user_config o precompression_data.

    Parametri
    ---------
    precompression_data : PrecompressionData (o compatibile)
        Dati di precompressione con parametri di perdita.
    material_concrete : Any
        Materiale calcestruzzo.
    material_prestressing : Any
        Materiale acciaio da precompressione.
    user_config : dict | None
        Parametri aggiuntivi forniti dall'utente:
        - creep_coefficient, shrinkage_strain, relaxation_class, ecc.

    Ritorna
    -------
    dict
        Dizionario con perdite stimate (istantanee + differite).
        TODO: definire struttura di ritorno completa.

    NormReference: DM 14/02/1992, DM 9/1/1996, EC2 §5.10.5-6

    TODO: implementazione completa. Modelli di perdita:
    - Istantanee: attrito, rientro ancoraggi, accorciamento elastico
    - Differite: fluage, ritiro, rilassamento acciaio
    """
    # TODO: implementazione completa
    return {
        "losses_instantaneous_percent": 0.0,
        "losses_deferred_percent": 0.0,
        "losses_total_percent": 0.0,
        "losses_friction_kN": 0.0,
        "losses_anchor_slip_kN": 0.0,
        "losses_elastic_shortening_kN": 0.0,
        "losses_creep_kN": 0.0,
        "losses_shrinkage_kN": 0.0,
        "losses_relaxation_kN": 0.0,
        "implementation_status": "TODO",
        "note": "Funzione placeholder - implementazione da completare",
    }


def check_precompression_stresses_ta_dm96(
    calc_input: CalcInput, template: VerificationTemplate
) -> SingleCheckResult:
    """Verifica tensioni ammissibili c.a.p. metodo TA - DM 14/02/1992.

    Verifica che le tensioni nel calcestruzzo e nell'acciaio da precompressione
    rispettino i limiti ammissibili nelle varie fasi (tesatura, trasferimento,
    esercizio).

    Parametri da leggere da CalcInput.extra o template.extra_params:
    - precompression_data: dati di precompressione
    - prestress_stage: fase di analisi

    NormReference: DM 14/02/1992, DM 9/1/1996

    TODO: implementazione completa. Richiede:
    - PrecompressionData integrata in CalcInput (campo futuro)
    - limiti tensionali per acciaio da precompressione in tesatura/trasferimento/esercizio
    - calcolo tensioni nella sezione precompressa
    """
    messages_it = [
        "Verifica tensioni ammissibili c.a.p. (DM 14/02/1992)",
        "",
        "TODO: implementazione completa.",
        "Richiede integrazione PrecompressionData in CalcInput.",
        "Verifiche da implementare:",
        "  - sigma_p <= sigma_p,adm in tesatura",
        "  - sigma_p <= sigma_p,adm in trasferimento",
        "  - sigma_c <= sigma_c,adm in esercizio (con precompressione)",
        "  - condizioni di decompressione / precompressione parziale",
    ]

    return SingleCheckResult(
        template_id=template.template_id,
        ok=False,
        utilisation=None,
        details={"implementation_status": "TODO"},
        messages_it=messages_it,
        limit_state="TA",
        norm_references=[
            NormReference(
                norm_code="DM92",
                chapter="Cap. c.a.p.",
                paragraph="Tensioni ammissibili precompressione",
                description_it="Verifica TA per c.a.p. DM 14/02/1992",
            )
        ],
    )


def check_precompression_slu_dm96(
    calc_input: CalcInput, template: VerificationTemplate
) -> SingleCheckResult:
    """Verifica SLU per elementi precompressi - DM 9/1/1996.

    Verifica a flessione/pressoflessione SLU con contributo dei cavi
    di precompressione.

    NormReference: DM 9/1/1996, EC2 §6.1

    TODO: implementazione completa. Richiede:
    - diagramma M-N con contributo precompressione
    - tensione nell'acciaio da precompressione a SLU
    - compatibilita deformativa cavi-sezione
    """
    messages_it = [
        "Verifica SLU per elementi precompressi (DM 9/1/1996)",
        "",
        "TODO: implementazione completa.",
        "Richiede integrazione PrecompressionData in CalcInput.",
        "Verifiche da implementare:",
        "  - diagramma M-N con contributo precompressione",
        "  - tensione acciaio da precompressione a SLU",
        "  - compatibilita deformativa cavi-sezione",
        "  - gamma_c=1.6, gamma_s=1.15, gamma_p da template",
    ]

    return SingleCheckResult(
        template_id=template.template_id,
        ok=False,
        utilisation=None,
        details={"implementation_status": "TODO"},
        messages_it=messages_it,
        limit_state="SLU",
        norm_references=[
            NormReference(
                norm_code="DM96",
                chapter="Cap. 3",
                paragraph="SLU precompressione",
                description_it="Verifica SLU c.a.p. DM 9/1/1996",
            )
        ],
    )
