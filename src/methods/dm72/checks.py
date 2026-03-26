"""Verifiche secondo DM 30/05/1972 - Metodo Tensioni Ammissibili (TA).

Implementa le verifiche per strutture in cemento armato secondo il DM 30/05/1972
utilizzando il metodo delle tensioni ammissibili.

Struttura:
- Funzioni di estrazione tensioni ammissibili (DM72-specifiche)
- Verifiche TA: flessione, pressoflessione, taglio, minimi
- Stub per verifiche specialistiche (torsione, punzonamento)

Il DM72 è caratterizzato da:
- σ_c,adm = Rck/4 (compressione semplice)
- σ_c,adm,infl = Rck/3 (flessione)
- n_omog = 10 (coefficiente omogenizzazione)
- τ_c0,adm, τ_c1,adm da tabelle

Tutti i messaggi sono in italiano.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from historical_ta.checks import AllowableStresses, check_allowable_stresses_ta
from historical_ta.geometry import compute_section_properties
from historical_ta.materials import ConcreteLawTA, SteelLawTA
from historical_ta.stress import LoadState, compute_normal_stresses_ta
from src.core_calculus.contracts import CalcInput, SingleCheckResult, VerificationTemplate
from src.methods.rd2229.checks import (
    AllowableStressesExtracted,
    apply_slenderness_reduction_ta,
    build_concrete_law_ta,
    build_steel_law_ta,
    compute_section_moduli_rect,
    compute_sigma_concrete_biaxial_ta,
    convert_loads_to_ta_units,
    convert_section_to_ta_geometry,
)
from src.methods.rd2229.instabilita import verifica_stabilita_ta

# ==============================================================================
# ALLOWABLE STRESSES FOR DM 30/05/1972
# ==============================================================================


def get_dm72_allowable_stresses(material: Any) -> AllowableStressesExtracted:
    """Estrae tensioni ammissibili DM72 da material object.

    DM 30/05/1972 definisce:
    - σ_c,adm (compressione semplice) = Rck / 4
    - σ_c,adm,infl (flessione) = Rck / 3
    - n = 10 (coefficiente di omogenizzazione)
    - σ_s,adm da tabelle (già nel catalogo)

    Se il materiale ha proprietà DM72 (sigma_c_adm, sigma_s_adm), le usa
    direttamente dal catalogo. Altrimenti calcola da sigma_c28 o f_ck.

    Args:
        material: Oggetto materiale con proprietà cls e acciaio

    Returns:
        AllowableStressesExtracted con tensioni in kg/cm²
    """
    # Tensione ammissibile calcestruzzo
    if hasattr(material, "sigma_c_adm") and material.sigma_c_adm is not None:
        sigma_c_allow = material.sigma_c_adm  # kg/cm² da catalogo
        sigma_c28 = sigma_c_allow * 4.0  # Ricava sigma_c28 = 4 × sigma_c_adm
    else:
        # Calcola da sigma_c28 o f_ck
        if hasattr(material, "sigma_c28"):
            sigma_c28 = material.sigma_c28
        elif hasattr(material, "f_ck"):
            sigma_c28 = material.f_ck * 10.197  # MPa → kg/cm²
        else:
            sigma_c28 = 160.0  # Default Rck 160

        sigma_c_allow = 0.25 * sigma_c28  # Formula DM72: Rck/4

    # Tensione ammissibile acciaio
    if hasattr(material, "sigma_s_adm") and material.sigma_s_adm is not None:
        sigma_s_allow = material.sigma_s_adm  # kg/cm² da catalogo
    else:
        # Calcola da f_yk
        if hasattr(material, "sigma_sn"):
            sigma_sn = material.sigma_sn
        elif hasattr(material, "f_yk"):
            sigma_sn = material.f_yk * 10.197  # MPa → kg/cm²
        else:
            sigma_sn = 3200.0  # Default FeB32k

        sigma_s_allow = 0.5 * sigma_sn  # Formula conservativa

    # Tensione media ammissibile cls (per tensioni medie in zone compresse)
    sigma_c_med_allow = 0.33 * sigma_c28  # Formula DM72: Rck/3

    return AllowableStressesExtracted(
        sigma_c_allow=sigma_c_allow,
        sigma_s_allow=sigma_s_allow,
        sigma_c_med_allow=sigma_c_med_allow,
    )


# ==============================================================================
# VERIFICHE TA: FLESSIONE, PRESSOFLESSIONE, TAGLIO, MINIMI
# ==============================================================================


def _make_error_result(
    template_id: str,
    error_msg: str,
    limit_state: str = "TA",
) -> SingleCheckResult:
    """Helper per creare risultato di errore."""
    return SingleCheckResult(
        template_id=template_id,
        ok=False,
        utilisation=None,
        norm_reference={"decreto": "DM 30/05/1972", "metodo": "TA"},
        messages_it=[error_msg],
        limit_state=limit_state,
        details_json={},
    )


def check_flessione_ta_dm72(
    calc_input: CalcInput, template: VerificationTemplate
) -> SingleCheckResult:
    """Verifica flessione semplice secondo DM 30/05/1972.

    Verifica elastica con distribuzione triangolare di stress.
    Controllano:
    - Tensione massima calcestruzzo ≤ σ_c,adm (Rck/4)
    - Tensione massima acciaio ≤ σ_s,adm

    Args:
        calc_input: CalcInput con sezione, materiale, sollecitazioni
        template: Template di verifica (template_id, limit_state)

    Returns:
        SingleCheckResult con ok, utilisation, messages_it
    """
    # Guard: validazioni iniziali
    if calc_input.section is None:
        return _make_error_result(
            template.template_id,
            "Sezione non definita - impossibile eseguire verifica",
        )

    if calc_input.material is None:
        return _make_error_result(
            template.template_id,
            "Materiale non definito - impossibile eseguire verifica",
        )

    try:
        # 1. Conversione unità: kN→kg, mm→cm
        loads = convert_loads_to_ta_units(calc_input)
        geom = convert_section_to_ta_geometry(calc_input)

        # 2. Proprietà geometriche
        props = compute_section_properties(geom)
        if props.A_cm2 <= 0:
            return _make_error_result(
                template.template_id,
                "Area sezione non valida",
            )

        # 3. Leggi materiale
        concrete_law = build_concrete_law_ta(calc_input.material)
        steel_law = build_steel_law_ta(calc_input.material)

        # 4. Tensioni da flessione monoassiale (momento My attorno asse orizzontale)
        load_state = LoadState(
            N_kg=loads["N_kg"],
            Mx_kg_cm=loads["Mx_kg_cm"],  # Momento attorno x
            My_kg_cm=loads["My_kg_cm"],  # Momento attorno y
            Tx_kg=0.0,  # Non considerato in flessione pura
            Ty_kg=0.0,
        )

        stresses = compute_normal_stresses_ta(
            geom=geom,
            props=props,
            load_state=load_state,
            concrete_law=concrete_law,
            steel_law=steel_law,
        )

        # 5. Tensioni ammissibili DM72
        adm = get_dm72_allowable_stresses(calc_input.material)

        # 6. Verifica ammissibilità
        check_result = check_allowable_stresses_ta(
            stresses=stresses,
            allowables=AllowableStresses(
                sigma_c=adm.sigma_c_allow,
                sigma_s=adm.sigma_s_allow,
            ),
        )

        # 7. Calcolo utilizzazione (rapporto tensione effettiva / ammissibile)
        util_c = abs(stresses.sigma_c_max) / adm.sigma_c_allow if adm.sigma_c_allow > 0 else 0.0
        util_s = abs(stresses.sigma_s_max) / adm.sigma_s_allow if adm.sigma_s_allow > 0 else 0.0
        utilisazione = max(util_c, util_s)

        # 8. Messaggi risultato
        messages_it = []
        messages_it.append(f"Flessione secondo DM 30/05/1972 (metodo TA)")
        messages_it.append(f"Momento flettente My = {abs(load_state.My_kg_cm):.2f} kg·cm")
        messages_it.append(f"Tensione max cls = {abs(stresses.sigma_c_max):.2f} kg/cm²")
        messages_it.append(f"Tensione ammissibile cls = {adm.sigma_c_allow:.2f} kg/cm²")
        messages_it.append(f"Tensione max acciaio = {abs(stresses.sigma_s_max):.2f} kg/cm²")
        messages_it.append(f"Tensione ammissibile acciaio = {adm.sigma_s_allow:.2f} kg/cm²")
        messages_it.append(f"Utilizzazione = {utilisazione:.1%}")

        if utilisazione <= 1.0:
            messages_it.append("✓ VERIFICA SODDISFATTA")
            ok = True
        else:
            messages_it.append(f"✗ VERIFICA NON SODDISFATTA (util={utilisazione:.1%})")
            ok = False

        return SingleCheckResult(
            template_id=template.template_id,
            ok=ok,
            utilisation=utilisazione,
            norm_reference={"decreto": "DM 30/05/1972", "norma": "flessione TA"},
            messages_it=messages_it,
            limit_state="TA",
            details_json={
                "sigma_c_max_kgcm2": abs(stresses.sigma_c_max),
                "sigma_c_adm_kgcm2": adm.sigma_c_allow,
                "sigma_s_max_kgcm2": abs(stresses.sigma_s_max),
                "sigma_s_adm_kgcm2": adm.sigma_s_allow,
                "util_c": util_c,
                "util_s": util_s,
            },
        )

    except Exception as e:
        return _make_error_result(
            template.template_id,
            f"Errore nel calcolo: {str(e)}",
        )


def check_pressoflessione_ta_dm72(
    calc_input: CalcInput, template: VerificationTemplate
) -> SingleCheckResult:
    """Verifica pressoflessione secondo DM 30/05/1972.

    Verifica con carico assiale N + momento flettente M.
    Formula elastica lineare con sovrapposizione degli effetti:
    σ_max = |N/A + M/W|

    Args:
        calc_input: CalcInput con sezione, materiale, N + My
        template: Template di verifica

    Returns:
        SingleCheckResult
    """
    # Guard
    if calc_input.section is None:
        return _make_error_result(
            template.template_id,
            "Sezione non definita",
        )

    if calc_input.material is None:
        return _make_error_result(
            template.template_id,
            "Materiale non definito",
        )

    try:
        # 1. Conversione unità
        loads = convert_loads_to_ta_units(calc_input)
        geom = convert_section_to_ta_geometry(calc_input)

        # 2. Proprietà geometriche
        props = compute_section_properties(geom)
        if props.A_cm2 <= 0:
            return _make_error_result(template.template_id, "Area sezione non valida")

        # 3. Leggi materiale
        concrete_law = build_concrete_law_ta(calc_input.material)
        steel_law = build_steel_law_ta(calc_input.material)

        # 4. Stato di carico
        load_state = LoadState(
            N_kg=loads["N_kg"],
            Mx_kg_cm=loads["Mx_kg_cm"],
            My_kg_cm=loads["My_kg_cm"],
            Tx_kg=0.0,
            Ty_kg=0.0,
        )

        # 5. Tensioni
        stresses = compute_normal_stresses_ta(
            geom=geom,
            props=props,
            load_state=load_state,
            concrete_law=concrete_law,
            steel_law=steel_law,
        )

        # 6. Tensioni ammissibili
        adm = get_dm72_allowable_stresses(calc_input.material)

        # Applica riduzione per snellezza se necessaria
        section = calc_input.section
        b_cm = section.width / 10.0
        h_cm = section.height / 10.0
        sigma_c_adm_ridotta, details_snellezza = apply_slenderness_reduction_ta(
            adm.sigma_c_allow, b_cm, h_cm
        )

        # 7. Utilizazioni
        util_c = abs(stresses.sigma_c_max) / sigma_c_adm_ridotta if sigma_c_adm_ridotta > 0 else 0.0
        util_s = abs(stresses.sigma_s_max) / adm.sigma_s_allow if adm.sigma_s_allow > 0 else 0.0
        utilisazione = max(util_c, util_s)

        # 8. Messaggi
        messages_it = []
        messages_it.append(f"Pressoflessione secondo DM 30/05/1972 (metodo TA)")
        messages_it.append(f"Sforzo normale N = {loads['N_kg']:.2f} kg (negativo = compressione)")
        messages_it.append(f"Momento flettente My = {abs(loads['My_kg_cm']):.2f} kg·cm")
        messages_it.append(f"Tensione max cls = {abs(stresses.sigma_c_max):.2f} kg/cm²")
        messages_it.append(
            f"Tensione ammissibile cls = {sigma_c_adm_ridotta:.2f} kg/cm² (base={adm.sigma_c_allow:.2f})"
        )
        if "riduzione_percentuale" in details_snellezza:
            messages_it.append(
                f"Riduzione snellezza: {details_snellezza['riduzione_percentuale']:.1%}"
            )
        messages_it.append(f"Tensione max acciaio = {abs(stresses.sigma_s_max):.2f} kg/cm²")
        messages_it.append(f"Tensione ammissibile acciaio = {adm.sigma_s_allow:.2f} kg/cm²")
        messages_it.append(f"Utilizzazione = {utilisazione:.1%}")

        ok = utilisazione <= 1.0
        if ok:
            messages_it.append("✓ VERIFICA SODDISFATTA")
        else:
            messages_it.append(f"✗ VERIFICA NON SODDISFATTA")

        return SingleCheckResult(
            template_id=template.template_id,
            ok=ok,
            utilisation=utilizzazione,
            norm_reference={"decreto": "DM 30/05/1972", "norma": "pressoflessione TA"},
            messages_it=messages_it,
            limit_state="TA",
            details_json={
                "N_kg": loads["N_kg"],
                "My_kg_cm": loads["My_kg_cm"],
                "sigma_c_max": abs(stresses.sigma_c_max),
                "sigma_c_adm": sigma_c_adm_ridotta,
                "sigma_s_max": abs(stresses.sigma_s_max),
                "sigma_s_adm": adm.sigma_s_allow,
                "util_c": util_c,
                "util_s": util_s,
            },
        )

    except Exception as e:
        return _make_error_result(template.template_id, f"Errore: {str(e)}")


def check_taglio_ta_dm72(
    calc_input: CalcInput, template: VerificationTemplate
) -> SingleCheckResult:
    """Verifica taglio secondo DM 30/05/1972.

    Verifica conservativa: tensione di taglio τ ≤ τ_c0,adm (senza armatura trasversale)
    o τ ≤ τ_c1,adm (con armatura trasversale).

    Formula: τ = T / A_w dove A_w è l'area resistente a taglio.

    Args:
        calc_input: CalcInput con sezione e taglio Tx, Ty
        template: Template di verifica

    Returns:
        SingleCheckResult
    """
    if calc_input.section is None:
        return _make_error_result(template.template_id, "Sezione non definita")

    if calc_input.material is None:
        return _make_error_result(template.template_id, "Materiale non definito")

    try:
        loads = convert_loads_to_ta_units(calc_input)
        section = calc_input.section

        # Area resistente a taglio (approssimazione: 0.9 × A per sezione rettangolare)
        A_w_cm2 = (section.width / 10.0) * (section.height / 10.0) * 0.9

        # Taglio totale (combinazione vettoriale di Tx e Ty)
        T_total_kg = (loads["Tx_kg"] ** 2 + loads["Ty_kg"] ** 2) ** 0.5  # Risultante

        # Tensione di taglio
        tau_max = T_total_kg / A_w_cm2 if A_w_cm2 > 0 else 0.0

        # Tensioni ammissibili taglio
        material = calc_input.material
        if hasattr(material, "tau_c0_adm") and hasattr(material, "tau_c1_adm"):
            tau_c0_adm = material.tau_c0_adm
            tau_c1_adm = material.tau_c1_adm
        else:
            # Valori di default DM72
            tau_c0_adm = 3.5
            tau_c1_adm = 10.0

        # Scelta limite: conservativo usa tau_c0_adm (senza staffe)
        # Se armatura trasversale presente, usa tau_c1_adm
        has_shear_rebar = calc_input.areaStaffe is not None and calc_input.areaStaffe > 0
        tau_adm = tau_c1_adm if has_shear_rebar else tau_c0_adm

        # Utilizzazione
        util = tau_max / tau_adm if tau_adm > 0 else 0.0

        # Messaggi
        messages_it = []
        messages_it.append(f"Taglio secondo DM 30/05/1972")
        messages_it.append(f"Taglio Tx = {loads['Tx_kg']:.2f} kg, Ty = {loads['Ty_kg']:.2f} kg")
        messages_it.append(f"Taglio risultante = {T_total_kg:.2f} kg")
        messages_it.append(f"Area resistente = {A_w_cm2:.2f} cm²")
        messages_it.append(f"Tensione di taglio = {tau_max:.2f} kg/cm²")
        if has_shear_rebar:
            messages_it.append(f"Armatura trasversale presente → τ_adm = {tau_adm:.2f}")
        else:
            messages_it.append(
                f"Armatura trasversale assente → τ_adm = {tau_adm:.2f} (conservativo)"
            )
        messages_it.append(f"Utilizzazione = {util:.1%}")

        ok = util <= 1.0
        if ok:
            messages_it.append("✓ VERIFICA SODDISFATTA")
        else:
            messages_it.append("✗ VERIFICA NON SODDISFATTA")

        return SingleCheckResult(
            template_id=template.template_id,
            ok=ok,
            utilisation=util,
            norm_reference={"decreto": "DM 30/05/1972", "norma": "taglio TA"},
            messages_it=messages_it,
            limit_state="TA",
            details_json={
                "Tx_kg": loads["Tx_kg"],
                "Ty_kg": loads["Ty_kg"],
                "T_total_kg": T_total_kg,
                "tau_max": tau_max,
                "tau_adm": tau_adm,
                "has_shear_rebar": has_shear_rebar,
            },
        )

    except Exception as e:
        return _make_error_result(template.template_id, f"Errore: {str(e)}")


def check_minimi_ta_dm72(
    calc_input: CalcInput, template: VerificationTemplate
) -> SingleCheckResult:
    """Verifica armatura minima secondo DM 30/05/1972.

    DM72 prescrive:
    - Trazione semplice: A_s,min ≥ 0.4% × A_c (0.003 × A_c per travi)
    - Compressione: A_s,min ≥ 0.3% × A_c
    - Staffe: diametro ≥ 1/3 diametro barre principali, passo ≤ 30 cm

    Args:
        calc_input: CalcInput con sezione e armature
        template: Template di verifica

    Returns:
        SingleCheckResult
    """
    if calc_input.section is None:
        return _make_error_result(template.template_id, "Sezione non definita")

    try:
        section = calc_input.section
        A_c_cm2 = (section.width / 10.0) * (section.height / 10.0)

        # Determine element type: trave vs pilastro
        is_pillar = section.height < 40 and section.width < 40  # Heuristic
        min_ratio = 0.003 if not is_pillar else 0.004  # 0.3% vs 0.4%

        A_s_min = min_ratio * A_c_cm2
        A_s_actual = calc_input.As or 0.0

        # Verifica armatura longitudinale
        util_long = A_s_actual / A_s_min if A_s_min > 0 else 1.0

        # Verifica staffe (se fornite)
        messages_it = []
        messages_it.append("Armature minime secondo DM 30/05/1972")
        messages_it.append(f"Area sezione = {A_c_cm2:.2f} cm²")
        messages_it.append(
            f"Armatura longitudinale minima = {A_s_min:.2f} cm² ({min_ratio*100:.2f}% × A_c)"
        )
        messages_it.append(f"Armatura longitudinale fornita = {A_s_actual:.2f} cm²")
        messages_it.append(f"Utilizzazione = {util_long:.1%}")

        ok_long = A_s_actual >= A_s_min * 0.95  # Tolleranza 5%

        if ok_long:
            messages_it.append("✓ Armatura longitudinale ADEGUATA")
        else:
            messages_it.append(
                f"✗ Armatura longitudinale INSUFFICIENTE (+{(A_s_min - A_s_actual):.2f} cm² mancanti)"
            )

        # Armature trasversali (staffe)
        if calc_input.areaStaffe and calc_input.areaStaffe > 0:
            messages_it.append(f"Staffe presenti: Area = {calc_input.areaStaffe:.2f} cm²/m")
        else:
            messages_it.append("⚠ Staffe non specificate - verificare manualmente")

        return SingleCheckResult(
            template_id=template.template_id,
            ok=ok_long,
            utilisation=util_long,
            norm_reference={"decreto": "DM 30/05/1972", "norma": "armature minime"},
            messages_it=messages_it,
            limit_state="TA",
            details_json={
                "A_c_cm2": A_c_cm2,
                "A_s_min_cm2": A_s_min,
                "A_s_actual_cm2": A_s_actual,
                "is_pillar": is_pillar,
                "min_ratio": min_ratio,
            },
        )

    except Exception as e:
        return _make_error_result(template.template_id, f"Errore: {str(e)}")


# ==============================================================================
# VERIFICHE SPECIALISTICHE (STUB + TODO)
# ==============================================================================


def check_torsione_ta_dm72(
    calc_input: CalcInput, template: VerificationTemplate
) -> SingleCheckResult:
    """Verifica torsione secondo DM 30/05/1972 (STUB).

    TODO: Implementare verifica torsione pura/combinata per DM72.
    Metodo: Navier (analogia con teoria dei fili),
    formula torsionale con controllo tensioni di taglio.

    Returns:
        SingleCheckResult con OK=True (stub - non implementato)
    """
    messages_it = [
        "Torsione DM 30/05/1972 — STUB NON IMPLEMENTATO",
        "TODO: Implementare verifica torsione secondo § DM72",
        "Contattare sviluppatore per implementazione",
    ]

    return SingleCheckResult(
        template_id=template.template_id,
        ok=True,
        utilisation=None,
        norm_reference={"decreto": "DM 30/05/1972", "norma": "torsione TA"},
        messages_it=messages_it,
        limit_state="TA",
        details_json={"status": "NOT_IMPLEMENTED"},
    )


def check_punzonamento_ta_dm72(
    calc_input: CalcInput, template: VerificationTemplate
) -> SingleCheckResult:
    """Verifica punzonamento secondo DM 30/05/1972 (STUB).

    TODO: Implementare verifica punzonamento per pilastri su piastre.
    Metodo: Formula empirica DM72 con controllo tensioni radiali.

    Returns:
        SingleCheckResult con OK=True (stub - non implementato)
    """
    messages_it = [
        "Punzonamento DM 30/05/1972 — STUB NON IMPLEMENTATO",
        "TODO: Implementare verifica punzonamento secondo § DM72",
        "Contattare sviluppatore per implementazione",
    ]

    return SingleCheckResult(
        template_id=template.template_id,
        ok=True,
        utilisation=None,
        norm_reference={"decreto": "DM 30/05/1972", "norma": "punzonamento TA"},
        messages_it=messages_it,
        limit_state="TA",
        details_json={"status": "NOT_IMPLEMENTED"},
    )
