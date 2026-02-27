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
from src.methods.checks_rd2229 import (
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


def _make_error_result(template_id: str, message: str, limit_state: str = "TA") -> SingleCheckResult:
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


def check_flessione_ta_dm96(calc_input: CalcInput, template: VerificationTemplate) -> SingleCheckResult:
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
            f"  sigma_c,max = {abs(stresses.sigma_c_max):.1f} kg/cm2" f" (ammissibile: {adm.sigma_c_allow:.1f} kg/cm2)",
            f"  sigma_s,max = {abs(stresses.sigma_s_max):.1f} kg/cm2" f" (ammissibile: {adm.sigma_s_allow:.1f} kg/cm2)",
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


def check_pressoflessione_ta_dm96(calc_input: CalcInput, template: VerificationTemplate) -> SingleCheckResult:
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
        sigma_c_adm_rid, slenderness_details = apply_slenderness_reduction_ta(adm.sigma_c_allow, b_cm, h_cm)

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
            f"  sigma_c,max = {abs(stresses.sigma_c_max):.1f} kg/cm2" f" (ammissibile: {sigma_c_adm_rid:.1f} kg/cm2)",
            f"  sigma_s,max = {abs(stresses.sigma_s_max):.1f} kg/cm2" f" (ammissibile: {adm.sigma_s_allow:.1f} kg/cm2)",
        ]
        if slenderness_details.get("reduced", False):
            messages_it.append(
                f"  Riduzione snellezza applicata: sigma_c_adm {adm.sigma_c_allow:.1f}" f" -> {sigma_c_adm_rid:.1f} kg/cm2"
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


def check_taglio_ta_dm96(calc_input: CalcInput, template: VerificationTemplate) -> SingleCheckResult:
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


def check_minimi_armatura_ta_dm96(calc_input: CalcInput, template: VerificationTemplate) -> SingleCheckResult:
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


def check_flessione_slu_dm96(calc_input: CalcInput, template: VerificationTemplate) -> SingleCheckResult:
    """Verifica a flessione SLU - DM 9/1/1996.

    Stesso algoritmo di NTC2018 ma con gamma_c = 1.6 (vs 1.5).
    - f_cd = 0.85 * f_ck / 1.6
    - f_yd = f_yk / 1.15
    - Stress block: lambda=0.8, eta=1.0
    - Duttilita: x/d <= 0.45

    NormReference: DM 9/1/1996 Cap. 3 - Verifica SLU flessione
    """
    if calc_input.section is None or calc_input.material is None:
        return _make_error_result(template.template_id, "Sezione o materiale non specificati", "SLU")

    section = calc_input.section
    if not (hasattr(section, "width") and hasattr(section, "height")):
        return _make_error_result(template.template_id, "Geometria sezione non disponibile", "SLU")

    b = section.width  # mm
    h = section.height  # mm

    material = calc_input.material
    f_ck_base = getattr(material, "f_ck", None)
    f_yk_base = getattr(material, "f_yk", None)
    if f_ck_base is None or f_yk_base is None:
        return _make_error_result(template.template_id, "Proprieta materiale (f_ck, f_yk) non disponibili", "SLU")

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
            ((As_mm2 - As_prime_mm2) * f_yd) / (lambda_factor * b * f_cd) if (lambda_factor * b * f_cd) > 0 else 0.0
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
        f"Sezione: {b/10:.1f} x {h/10:.1f} cm, d = {d:.1f} cm",
        f"Materiali: f_ck={f_ck:.0f} MPa, f_yk={f_yk:.0f} MPa",
        f"DM96: gamma_c={gamma_c}, gamma_s={gamma_s}",
        f"  f_cd = 0.85*f_ck/gamma_c = {f_cd:.1f} MPa",
        f"  f_yd = f_yk/gamma_s = {f_yd:.0f} MPa",
        "",
        f"Asse neutro: x = {x:.1f} mm (x/d = {x/d_mm:.3f})",
    ]
    if x_limited:
        messages_it.append(f"  x/d = {x/d_mm:.3f} > {x_d_limit}: sezione sovra-armata")
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


def check_taglio_slu_dm96(calc_input: CalcInput, template: VerificationTemplate) -> SingleCheckResult:
    """Verifica a taglio SLU - DM 9/1/1996.

    Stesso algoritmo NTC2018 ma con gamma_c=1.6.
    V_Rd = min(V_Rd,s, V_Rd,max)
    theta = 21.8 gradi (conservativo).

    NormReference: DM 9/1/1996 Cap. 4 - Verifica SLU taglio
    """
    if calc_input.section is None or calc_input.material is None:
        return _make_error_result(template.template_id, "Sezione o materiale non specificati", "SLU")

    section = calc_input.section
    b = section.width  # mm
    h = section.height  # mm

    material = calc_input.material
    f_ck_base = getattr(material, "f_ck", None)
    f_yk_base = getattr(material, "f_yk", None)
    if f_ck_base is None or f_yk_base is None:
        return _make_error_result(template.template_id, "Proprieta materiale non disponibili", "SLU")

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
        return _make_error_result(template.template_id, "Dati staffe mancanti: diametro non specificato", "SLU")
    if not staffe_passo or staffe_passo <= 0:
        return _make_error_result(template.template_id, "Dati staffe mancanti: passo non specificato", "SLU")

    s_mm = staffe_passo * 10.0
    A_sw = staffe_num_bracci * math.pi * (staffe_diametro**2) / 4.0
    Asw_over_s = A_sw / s_mm

    Tx = calc_input.Tx or 0.0
    Ty = calc_input.Ty or 0.0
    V_Ed = max(abs(Tx), abs(Ty))
    V_Ed_N = V_Ed * 1000.0

    if V_Ed <= 0:
        return _make_error_result(template.template_id, "Taglio agente V_Ed non specificato o nullo", "SLU")

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
        f"Sezione: {b/10:.1f} x {h/10:.1f} cm, d = {d:.1f} cm",
        f"DM96 SLU: gamma_c={gamma_c}, f_cd={f_cd:.1f} MPa, f_yd={f_yd:.0f} MPa",
        f"Staffe: phi{staffe_diametro:.0f}/{staffe_passo:.0f}cm, {staffe_num_bracci} bracci",
        "",
        f"V_Rd,s = {V_Rd_s/1000:.1f} kN, V_Rd,max = {V_Rd_max/1000:.1f} kN",
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


def check_minimi_armatura_flessione_slu_dm96(calc_input: CalcInput, template: VerificationTemplate) -> SingleCheckResult:
    """Verifica minimi armatura flessione SLU - DM 9/1/1996.

    As,min = max(0.26 * f_ctm / f_yk * b * d, 0.0013 * b * d)

    NormReference: DM 9/1/1996 Cap. 5 - Armature minime flessione
    """
    if calc_input.section is None or calc_input.material is None:
        return _make_error_result(template.template_id, "Sezione o materiale non specificati", "SLU")

    section = calc_input.section
    b = section.width
    h = section.height
    material = calc_input.material
    f_ck = getattr(material, "f_ck", None)
    f_yk = getattr(material, "f_yk", None)

    if f_ck is None or f_yk is None:
        return _make_error_result(template.template_id, "Proprieta materiale non disponibili", "SLU")

    d = calc_input.d or (0.9 * h / 10.0)
    d_mm = d * 10.0

    f_ctm = getattr(material, "fctm", None)
    if f_ctm is None or f_ctm <= 0:
        f_ctm = 0.30 * (f_ck ** (2.0 / 3.0)) if f_ck <= 50 else 2.12 * math.log(1 + (f_ck + 8) / 10.0)

    As = calc_input.As or 0.0
    As_mm2 = As * 100.0

    As_min_1 = 0.26 * f_ctm / f_yk * b * d_mm
    As_min_2 = 0.0013 * b * d_mm
    As_min_mm2 = max(As_min_1, As_min_2)

    ok = As_mm2 >= As_min_mm2
    utilizzazione = As_min_mm2 / As_mm2 if As_mm2 > 0 else 999.0

    messages_it = [
        f"Sezione: {b/10:.1f} x {h/10:.1f} cm, d = {d:.1f} cm",
        f"Materiali: f_ck={f_ck:.0f} MPa, f_yk={f_yk:.0f} MPa, f_ctm={f_ctm:.2f} MPa",
        f"As presente: {As:.2f} cm2",
        f"As,min = max({As_min_1/100:.2f}, {As_min_2/100:.2f}) = {As_min_mm2/100:.2f} cm2",
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


def check_minimi_armatura_taglio_slu_dm96(calc_input: CalcInput, template: VerificationTemplate) -> SingleCheckResult:
    """Verifica minimi armatura taglio SLU - DM 9/1/1996.

    Asw,min/s = 0.08 * sqrt(f_ck) / f_yk * b

    NormReference: DM 9/1/1996 Cap. 5 - Armature minime taglio
    """
    if calc_input.section is None or calc_input.material is None:
        return _make_error_result(template.template_id, "Sezione o materiale non specificati", "SLU")

    section = calc_input.section
    b = section.width
    material = calc_input.material
    f_ck = getattr(material, "f_ck", None)
    f_yk = getattr(material, "f_yk", None)

    if f_ck is None or f_yk is None:
        return _make_error_result(template.template_id, "Proprieta materiale non disponibili", "SLU")

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


def check_fessurazione_sle_dm96(calc_input: CalcInput, template: VerificationTemplate) -> SingleCheckResult:
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
        return _make_error_result(template.template_id, "Sezione o materiale non specificati", "SLE")

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

    # TODO: calcolo completo di w secondo DM96/EC2
    # Per ora: placeholder con messaggio informativo
    messages_it = [
        f"Ampiezza fessura ammissibile: w_amm = {w_amm} mm",
        "",
        "TODO: implementazione completa calcolo ampiezza fessure w",
        "secondo DM 9/1/1996 / EC2 §7.3.",
        "Richiede: tensione acciaio in esercizio, diametro barre,",
        "passo barre, copriferro effettivo, classe ambientale.",
    ]

    return SingleCheckResult(
        template_id=template.template_id,
        ok=False,
        utilisation=None,
        details={"w_amm_mm": w_amm, "implementation_status": "TODO"},
        messages_it=messages_it,
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


def check_deformazioni_sle_dm96(calc_input: CalcInput, template: VerificationTemplate) -> SingleCheckResult:
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
        return _make_error_result(template.template_id, "Sezione o materiale non specificati", "SLE")

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

    messages_it = [
        f"Luce: L = {span_mm:.0f} mm",
        f"Limite: L/{deflection_limit_ratio:.0f} = {delta_amm:.1f} mm",
        "",
        "TODO: implementazione completa calcolo frecce",
        "con momento di inerzia efficace I_eff, coefficiente di fluage,",
        "deformazione da ritiro, secondo DM 9/1/1996 / EC2 §7.4.",
    ]

    return SingleCheckResult(
        template_id=template.template_id,
        ok=False,
        utilisation=None,
        details={
            "span_mm": span_mm,
            "deflection_limit_ratio": deflection_limit_ratio,
            "delta_amm_mm": delta_amm,
            "implementation_status": "TODO",
        },
        messages_it=messages_it,
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


# ==============================================================================
# SEZIONE E: CHECK SLU AGGIUNTIVI DM96
# ==============================================================================


def check_torsione_slu_dm96(calc_input: CalcInput, template: VerificationTemplate) -> SingleCheckResult:
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
        return _make_error_result(template.template_id, "Sezione o materiale non specificati", "SLU")

    Mz = calc_input.Mz or 0.0
    if abs(Mz) < 1e-6:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=True,
            utilisation=0.0,
            details={"T_Ed_kNm": 0.0},
            messages_it=["Momento torcente nullo: verifica non necessaria"],
            limit_state="SLU",
        )

    messages_it = [
        f"Momento torcente: T_Ed = {abs(Mz):.2f} kNm",
        "",
        "TODO: implementazione completa verifica torsione SLU DM96.",
        "Richiede: area nucleo A_k, spessore efficace t_ef,",
        "armature trasversali e longitudinali a torsione.",
        "Riferimento: DM 9/1/1996, EC2 §6.3.",
    ]

    return SingleCheckResult(
        template_id=template.template_id,
        ok=False,
        utilisation=None,
        details={"T_Ed_kNm": abs(Mz), "implementation_status": "TODO"},
        messages_it=messages_it,
        limit_state="SLU",
        norm_references=[
            NormReference(
                norm_code="DM96",
                chapter="Cap. 4",
                paragraph="Torsione SLU",
                description_it="Verifica torsione SLU DM 9/1/1996",
            )
        ],
    )


def check_punzonamento_slu_dm96(calc_input: CalcInput, template: VerificationTemplate) -> SingleCheckResult:
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
        return _make_error_result(template.template_id, "Sezione o materiale non specificati", "SLU")

    messages_it = [
        "TODO: implementazione completa verifica punzonamento SLU DM96.",
        "Richiede: perimetro critico u_1, altezza utile d della piastra,",
        "percentuale armatura rho_l, dimensioni pilastro.",
        "Riferimento: DM 9/1/1996, EC2 §6.4.",
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
                chapter="Cap. 4",
                paragraph="Punzonamento SLU",
                description_it="Verifica punzonamento SLU DM 9/1/1996",
            )
        ],
    )


def check_instabilita_compressione_slu_dm96(calc_input: CalcInput, template: VerificationTemplate) -> SingleCheckResult:
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
        return _make_error_result(template.template_id, "Sezione o materiale non specificati", "SLU")

    l_0 = template.extra_params.get("l_0_mm", None)
    if l_0 is None:
        l_0 = calc_input.extra.get("l_0_mm", None)

    section = calc_input.section
    b = section.width
    h = section.height
    i_min = min(b, h) / math.sqrt(12)  # raggio di inerzia minimo (sez. rettangolare)

    if l_0 is not None and l_0 > 0:
        lam = l_0 / i_min
        messages_it = [
            f"Sezione: {b/10:.1f} x {h/10:.1f} cm",
            f"Lunghezza libera: l_0 = {l_0:.0f} mm",
            f"Raggio inerzia minimo: i_min = {i_min:.1f} mm",
            f"Snellezza: lambda = {lam:.1f}",
            "",
            "TODO: implementazione completa verifica instabilita DM96.",
            "Metodo amplificazione momento o analisi 2° ordine.",
            "Riferimento: DM 9/1/1996, EC2 §5.8.",
        ]
        details = {"lambda": lam, "l_0_mm": l_0, "i_min_mm": i_min}
    else:
        messages_it = [
            f"Sezione: {b/10:.1f} x {h/10:.1f} cm",
            "Lunghezza libera l_0 non specificata.",
            "Impostare l_0_mm nel template o CalcInput.extra.",
            "TODO: implementazione completa verifica instabilita DM96.",
        ]
        details = {"i_min_mm": i_min}

    details["implementation_status"] = "TODO"

    return SingleCheckResult(
        template_id=template.template_id,
        ok=False,
        utilisation=None,
        details=details,
        messages_it=messages_it,
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


def check_precompression_stresses_ta_dm96(calc_input: CalcInput, template: VerificationTemplate) -> SingleCheckResult:
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


def check_precompression_slu_dm96(calc_input: CalcInput, template: VerificationTemplate) -> SingleCheckResult:
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
