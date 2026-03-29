"""Normalizzazione unità di misura per il protocollo I/O CalcInput/CalcOutput.

Pipeline di conversione unità::

    Input utente (unità GUI)
      → [gestore_unita.da_input()]
    Catalogo (kg/cm² storage)
      → [normalize_to_mpa()]          ← QUESTO MODULO
    CalcInput (MPa interno, SI)
      → [ENGINE DI VERIFICA — tutte in MPa]
    CalcOutput (MPa/SI interno)
      → [denormalize_for_output()]     ← QUESTO MODULO
    Output (unità GUI)

Fattore di conversione esatto:
    1 kg/cm² = 0.0980665 MPa  (da g_n = 9.80665 m/s²)
    1 MPa    = 10.19716 kg/cm²

Questo modulo opera su ``CalcInput``/``CalcOutput`` **senza** modificare
gli oggetti originali: restituisce sempre nuove istanze (principio di
immutabilità funzionale).

Dipendenze:
    - ``src.core.adapter_unita_misura`` per le conversioni base
    - ``src.core_calculus.contracts`` per CalcInput/CalcOutput
"""

from __future__ import annotations

import copy
import dataclasses
import logging
from typing import Any

from src.core.adapter_unita_misura import (
    kg_cm2_to_mpa,
    mpa_to_kg_cm2,
)

logger = logging.getLogger(__name__)

# ==============================================================================
# COSTANTI
# ==============================================================================

#: Unità supportate per output
UNITA_SUPPORTATE = frozenset({
    "mpa", "MPa", "N/mm2", "N/mm²",
    "kg/cm2", "kg/cm²", "kgf/cm2",
    "kPa", "kpa",
})

#: Soglia per auto-detection unità (f_ck): > 200 → presumibilmente kg/cm²
_SOGLIA_FCK_KG_CM2 = 200.0

#: Soglia per auto-detection unità (f_yk): > 1000 → presumibilmente kg/cm²
_SOGLIA_FYK_KG_CM2 = 1000.0

#: Soglia per auto-detection unità (E): > 10000 → presumibilmente kg/cm²
_SOGLIA_E_KG_CM2 = 10000.0


# ==============================================================================
# NORMALIZZAZIONE INPUT (catalogo → MPa interno)
# ==============================================================================


def normalize_material_to_mpa(material: Any) -> Any:
    """Normalizza le proprietà di tensione di un materiale a MPa.

    Crea una **copia** del materiale con le proprietà di tensione
    convertite da kg/cm² (catalogo storico) a MPa (standard interno).

    Rileva automaticamente l'unità di partenza in base alla grandezza
    del valore, seguendo le soglie del progetto:
    - f_ck > 200 → kg/cm²
    - f_yk > 1000 → kg/cm²
    - E > 10000 → kg/cm²

    Parametri
    ----------
    material : Any
        Oggetto materiale con attributi di tensione.

    Restituisce
    -----------
    Any
        Copia del materiale con tensioni normalizzate a MPa.
        Se il materiale è un dict, restituisce un dict.
        Se è un oggetto con attributi, restituisce una copia con attributi modificati.
    """
    if material is None:
        return None

    # Gestione dict (cataloghi JSON)
    if isinstance(material, dict):
        return _normalize_dict_material(material)

    # Gestione dataclass / oggetti con attributi
    try:
        mat_copy = copy.copy(material)
    except TypeError:
        logger.warning(
            "normalize_material_to_mpa: impossibile copiare materiale tipo %s, "
            "conversione in-place (non raccomandato)",
            type(material).__name__,
        )
        mat_copy = material

    # f_ck
    f_ck = getattr(mat_copy, "f_ck", None)
    if f_ck is not None and f_ck > _SOGLIA_FCK_KG_CM2:
        f_ck_mpa = kg_cm2_to_mpa(f_ck)
        logger.debug("normalize: f_ck %.1f kg/cm² → %.4f MPa", f_ck, f_ck_mpa)
        try:
            mat_copy.f_ck = f_ck_mpa
        except AttributeError:
            pass  # Frozen dataclass, skip

    # f_yk
    f_yk = getattr(mat_copy, "f_yk", None)
    if f_yk is not None and f_yk > _SOGLIA_FYK_KG_CM2:
        f_yk_mpa = kg_cm2_to_mpa(f_yk)
        logger.debug("normalize: f_yk %.1f kg/cm² → %.4f MPa", f_yk, f_yk_mpa)
        try:
            mat_copy.f_yk = f_yk_mpa
        except AttributeError:
            pass

    # E (modulo elastico)
    e_val = getattr(mat_copy, "E", None)
    if e_val is not None and e_val > _SOGLIA_E_KG_CM2:
        e_mpa = kg_cm2_to_mpa(e_val)
        logger.debug("normalize: E %.1f kg/cm² → %.4f MPa", e_val, e_mpa)
        try:
            mat_copy.E = e_mpa
        except AttributeError:
            pass

    # sigma_c_adm (tensioni ammissibili storiche)
    sigma_c_adm = getattr(mat_copy, "sigma_c_adm", None)
    if sigma_c_adm is not None and sigma_c_adm > 0:
        # Le sigma_adm sono sempre in kg/cm² nei cataloghi storici
        sigma_c_adm_mpa = kg_cm2_to_mpa(sigma_c_adm)
        logger.debug(
            "normalize: sigma_c_adm %.1f kg/cm² → %.4f MPa",
            sigma_c_adm, sigma_c_adm_mpa,
        )
        try:
            mat_copy.sigma_c_adm = sigma_c_adm_mpa
        except AttributeError:
            pass

    return mat_copy


def _normalize_dict_material(material: dict[str, Any]) -> dict[str, Any]:
    """Normalizza un materiale in formato dizionario (catalogo JSON)."""
    mat = dict(material)  # Copia shallow

    if "f_ck" in mat and mat["f_ck"] is not None and mat["f_ck"] > _SOGLIA_FCK_KG_CM2:
        mat["f_ck"] = kg_cm2_to_mpa(mat["f_ck"])
        mat["_f_ck_original_unit"] = "kg/cm²"

    if "f_yk" in mat and mat["f_yk"] is not None and mat["f_yk"] > _SOGLIA_FYK_KG_CM2:
        mat["f_yk"] = kg_cm2_to_mpa(mat["f_yk"])
        mat["_f_yk_original_unit"] = "kg/cm²"

    if "E" in mat and mat["E"] is not None and mat["E"] > _SOGLIA_E_KG_CM2:
        mat["E"] = kg_cm2_to_mpa(mat["E"])
        mat["_E_original_unit"] = "kg/cm²"

    if "sigma_c_adm" in mat and mat["sigma_c_adm"] is not None and mat["sigma_c_adm"] > 0:
        mat["sigma_c_adm"] = kg_cm2_to_mpa(mat["sigma_c_adm"])
        mat["_sigma_c_adm_original_unit"] = "kg/cm²"

    return mat


def normalize_to_mpa(calc_input: Any) -> Any:
    """Normalizza un CalcInput: converte materiali da catalogo (kg/cm²) a MPa.

    Crea una copia del CalcInput con il materiale normalizzato a MPa.
    Gli altri campi (forze, momenti, geometria) restano invariati perché
    già in unità SI standard (kN, kN·m, cm).

    Parametri
    ----------
    calc_input : CalcInput
        Input di calcolo con materiale potenzialmente in kg/cm².

    Restituisce
    -----------
    CalcInput
        Nuova istanza con materiale normalizzato a MPa.
    """
    from src.core_calculus.contracts import CalcInput

    if not isinstance(calc_input, CalcInput):
        raise TypeError(
            f"normalize_to_mpa richiede CalcInput, ricevuto {type(calc_input).__name__}"
        )

    # Copia tutti i campi
    new_input = dataclasses.replace(calc_input)

    # Normalizza materiale
    if new_input.material is not None:
        new_input.material = normalize_material_to_mpa(new_input.material)

    return new_input


# ==============================================================================
# DENORMALIZZAZIONE OUTPUT (MPa interno → unità di output)
# ==============================================================================


def denormalize_for_output(
    calc_output: Any,
    output_units: str = "MPa",
) -> dict[str, Any]:
    """Converte CalcOutput (MPa interno) a unità di output desiderate.

    Restituisce un dizionario con i valori di tensione convertiti
    nell'unità richiesta dall'utente per la visualizzazione GUI.

    Parametri
    ----------
    calc_output : CalcOutput
        Risultato di verifica in unità interne (MPa).
    output_units : str
        Unità di output desiderata. Valori supportati:
        ``"MPa"``, ``"kg/cm2"``, ``"kg/cm²"``, ``"kPa"``.

    Restituisce
    -----------
    dict
        Dizionario con i campi principali convertiti:
        - ``stress_max``, ``stress_limit``: tensioni nell'unità richiesta
        - ``rapporto_verifica``: adimensionale (invariato)
        - ``ok``: esito (invariato)
        - ``deformation``: in mm (invariato)
        - ``unita_tensione``: stringa dell'unità usata
        - ``passaggi_calcolo``: lista passaggi (invariata)
        - ``formule_usate``: lista formule (invariata)

    Eccezioni
    ---------
    ValueError
        Se ``output_units`` non è un'unità supportata.
    """
    unita_norm = output_units.strip().lower().replace(" ", "")

    if unita_norm in ("mpa", "n/mm2", "n/mm²"):
        convert_fn = lambda x: x  # noqa: E731
        unita_label = "MPa"
    elif unita_norm in ("kg/cm2", "kg/cm²", "kgf/cm2", "kgcm2"):
        convert_fn = mpa_to_kg_cm2
        unita_label = "kg/cm²"
    elif unita_norm in ("kpa",):
        convert_fn = lambda x: x * 1000.0  # noqa: E731 — 1 MPa = 1000 kPa
        unita_label = "kPa"
    else:
        raise ValueError(
            f"Unità di output '{output_units}' non supportata. "
            f"Valori ammessi: MPa, kg/cm², kPa."
        )

    result: dict[str, Any] = {
        "ok": calc_output.ok,
        "rapporto_verifica": calc_output.rapporto_verifica,
        "unita_tensione": unita_label,
        "passaggi_calcolo": list(calc_output.passaggi_calcolo),
        "formule_usate": list(calc_output.formule_usate),
        "warnings": list(calc_output.warnings),
        "errors": list(calc_output.errors),
    }

    # Converti tensioni
    if calc_output.stress_max is not None:
        result["stress_max"] = convert_fn(calc_output.stress_max)
    else:
        result["stress_max"] = None

    if calc_output.stress_limit is not None:
        result["stress_limit"] = convert_fn(calc_output.stress_limit)
    else:
        result["stress_limit"] = None

    # Deformazione sempre in mm (non dipende da unità tensione)
    result["deformation"] = calc_output.deformation

    # Verifiche per-template con tensioni convertite
    result["verifiche"] = {}
    for tid, scr in calc_output.per_template_results.items():
        v = scr.to_dict()
        if scr.stress_max is not None:
            v["stress_max"] = convert_fn(scr.stress_max)
        if scr.stress_limit is not None:
            v["stress_limit"] = convert_fn(scr.stress_limit)
        result["verifiche"][tid] = v

    return result


# ==============================================================================
# ADAPTER PER MODULI LEGACY (dict → CalcOutput)
# ==============================================================================


def dict_to_single_check_result(
    result_dict: dict[str, Any],
    template_id: str = "legacy",
) -> Any:
    """Converte un dizionario legacy in SingleCheckResult.

    Adapter per retrocompatibilità: i moduli vecchi (DM92, RD2229)
    che restituiscono dict possono essere convertiti al protocollo
    standard senza modificare il codice originale.

    Mappatura campi:
    - ``esito`` / ``verificato`` / ``ok`` → ``ok``
    - ``rateo`` / ``rapporto_verifica`` / ``utilisation`` → ``utilisation``
    - ``passaggi_calcolo`` / ``passaggi`` → ``passaggi_calcolo``
    - ``sigma_max`` / ``stress_max`` → ``stress_max``
    - ``sigma_amm`` / ``stress_limit`` → ``stress_limit``

    Parametri
    ----------
    result_dict : dict
        Dizionario risultato dal modulo di verifica legacy.
    template_id : str
        Identificatore del template (default: ``"legacy"``).

    Restituisce
    -----------
    SingleCheckResult
        Risultato nel formato standard.
    """
    from src.core_calculus.contracts import SingleCheckResult

    # Esito
    ok = result_dict.get("esito",
         result_dict.get("verificato",
         result_dict.get("ok", False)))

    # Utilizzazione
    utilisation = result_dict.get("rateo",
                  result_dict.get("rapporto_verifica",
                  result_dict.get("utilisation")))

    # Passaggi calcolo
    passaggi = result_dict.get("passaggi_calcolo",
               result_dict.get("passaggi", []))

    # Tensioni
    stress_max = result_dict.get("sigma_max",
                 result_dict.get("stress_max"))
    stress_limit = result_dict.get("sigma_amm",
                   result_dict.get("stress_limit"))

    # Formule
    formule = result_dict.get("formule_usate",
              result_dict.get("riferimenti_normativi", []))

    # Messaggi
    messages = result_dict.get("messaggi",
               result_dict.get("messages_it", []))

    # Details: tutto il resto
    details = {
        k: v for k, v in result_dict.items()
        if k not in {
            "esito", "verificato", "ok", "rateo", "rapporto_verifica",
            "utilisation", "passaggi_calcolo", "passaggi",
            "sigma_max", "stress_max", "sigma_amm", "stress_limit",
            "formule_usate", "riferimenti_normativi", "messaggi", "messages_it",
        }
        and isinstance(v, (int, float, str, bool))
    }

    return SingleCheckResult(
        template_id=template_id,
        ok=bool(ok),
        utilisation=float(utilisation) if utilisation is not None else None,
        details=details,
        passaggi_calcolo=list(passaggi) if passaggi else [],
        formule_usate=list(formule) if formule else [],
        stress_max=float(stress_max) if stress_max is not None else None,
        stress_limit=float(stress_limit) if stress_limit is not None else None,
        messages_it=list(messages) if messages else [],
    )
