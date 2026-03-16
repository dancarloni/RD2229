"""Check X5 aperture e cerchiature per solai (classificazione, rigidezza, redistribuzione).

Implementazione dict-based coerente con `NTC2018CodeModule.run_check`.
Unita principali (storico interno):
- aree in cm2
- rigidezze in kgf*cm2
- carichi in kgf

Nel payload `details` sono riportate anche conversioni SI utili.
"""

from __future__ import annotations

import uuid
from typing import Any

from src.core.registro_log import registro
from src.methods.ntc2018.models import Apertura, PareteMuraria, Rinforzo
from src.methods.ntc2018.x5_core import (
    compute_EI_post_with_reinforcements,
    compute_modifica_aperture,
)
from src.methods.ntc2018.x5_pushover import (
    PerformanceLevel,
    PushoverSettings,
    StopCriteria,
    build_seismic_combinations,
    compare_ante_post,
    evaluate_performance_levels,
    run_pushover_methods,
)

_KGF_TO_KN = 0.00980665
_KGF_CM2_TO_NM2 = 0.000980665
_MODULO_LOG = "methods.ntc2018.checks_x5"


def _error_result(message: str, norm_refs: list[str]) -> dict[str, Any]:
    run_id = str(uuid.uuid4())
    return {
        "ok": False,
        "value": None,
        "utilisation": None,
        "details": {},
        "steps": [message],
        "trace": {"run_id": run_id},
        "norm_references": norm_refs,
        "warnings": [],
    }


def _push_warning(warnings: list[str], steps: list[str], code: str, detail: str) -> None:
    warnings.append(code)
    steps.append(f"Warning {code}: {detail}")
    registro.avviso(_MODULO_LOG, code, detail)


def _read_thresholds(inputs: dict[str, Any]) -> dict[str, float]:
    cfg = inputs.get("soglie_aperture", {})
    if not isinstance(cfg, dict):
        cfg = {}

    soglie = {
        "piccola": float(cfg.get("piccola", 0.10)),
        "media": float(cfg.get("media", 0.25)),
        "estrema": float(cfg.get("estrema", 0.50)),
        "trigger_fem": float(cfg.get("trigger_fem", 0.25)),
    }

    if not (0.0 < soglie["piccola"] < soglie["media"] <= soglie["estrema"] <= 1.0):
        soglie = {
            "piccola": 0.10,
            "media": 0.25,
            "estrema": 0.50,
            "trigger_fem": 0.25,
        }

    return soglie


def _read_alpha_defaults(inputs: dict[str, Any]) -> dict[str, float]:
    cfg = inputs.get("alpha_ap_default", {})
    if not isinstance(cfg, dict):
        cfg = {}

    alpha = {
        "piccola": float(cfg.get("piccola", 0.05)),
        "media": float(cfg.get("media", 0.20)),
        "grande": float(cfg.get("grande", 0.40)),
        "estrema": float(cfg.get("estrema", 0.60)),
    }

    for key in alpha:
        alpha[key] = min(max(alpha[key], 0.0), 0.95)

    return alpha


def _read_near_support_limit(inputs: dict[str, Any]) -> float:
    cfg = inputs.get("trigger_locali", {})
    if not isinstance(cfg, dict):
        cfg = {}
    value = float(cfg.get("near_support_luce_ratio", 0.10))
    return min(max(value, 0.0), 1.0)


def _manual_area_flag(inputs: dict[str, Any]) -> bool:
    source = str(inputs.get("area_influenza_source", "")).strip().lower()
    return bool(
        inputs.get("area_influenza_manuale", False)
        or inputs.get("usa_area_influenza_manuale", False)
        or source == "manuale"
    )


def _read_area_cm2(inputs: dict[str, Any]) -> tuple[float, float]:
    area_ap_cm2 = float(inputs.get("area_apertura_cm2", 0.0))
    if area_ap_cm2 <= 0.0:
        area_ap_m2 = float(inputs.get("area_apertura_m2", 0.0))
        area_ap_cm2 = area_ap_m2 * 10_000.0

    area_panel_cm2 = float(inputs.get("area_pannello_cm2", 0.0))
    if area_panel_cm2 <= 0.0:
        area_panel_m2 = float(inputs.get("area_pannello_m2", 0.0))
        area_panel_cm2 = area_panel_m2 * 10_000.0
    if area_panel_cm2 <= 0.0:
        l_cm = float(inputs.get("luce_cm", inputs.get("L_cm", 0.0)))
        b_cm = float(inputs.get("larghezza_collaborante_cm", inputs.get("interasse_cm", 0.0)))
        if l_cm > 0.0 and b_cm > 0.0:
            area_panel_cm2 = l_cm * b_cm

    return area_ap_cm2, area_panel_cm2


def _classify_ratio(
    ratio: float,
    soglie: dict[str, float],
    alpha_default: dict[str, float],
) -> tuple[str, float]:
    if ratio < soglie["piccola"]:
        return "piccola", alpha_default["piccola"]
    if ratio < soglie["media"]:
        return "media", alpha_default["media"]
    if ratio <= soglie["estrema"]:
        return "grande", alpha_default["grande"]
    return "estrema", alpha_default["estrema"]


def _near_support_trigger(inputs: dict[str, Any], limit_ratio: float) -> tuple[bool, float | None]:
    if bool(inputs.get("apertura_vicino_appoggi", False) or inputs.get("near_support", False)):
        return True, None

    luce_cm = float(inputs.get("luce_cm", inputs.get("L_cm", 0.0)))
    distanza_cm = float(inputs.get("distanza_apertura_appoggio_cm", -1.0))

    if distanza_cm < 0.0:
        luce_m = float(inputs.get("luce_m", 0.0))
        distanza_m = float(inputs.get("distanza_apertura_appoggio_m", -1.0))
        if luce_m > 0.0 and distanza_m >= 0.0:
            ratio = distanza_m / luce_m
            return ratio <= limit_ratio, ratio

    if luce_cm > 0.0 and distanza_cm >= 0.0:
        ratio = distanza_cm / luce_cm
        return ratio <= limit_ratio, ratio

    return False, None


def _near_peak_shear_trigger(inputs: dict[str, Any]) -> bool:
    return bool(
        inputs.get("apertura_in_zona_picco_taglio", False)
        or inputs.get("apertura_vicino_picco_taglio", False)
        or inputs.get("near_peak_shear", False)
    )


def _optional_ratio(inputs: dict[str, Any]) -> float | None:
    ratio_raw = inputs.get("rapporto_apertura", None)
    if ratio_raw is not None:
        return float(ratio_raw)

    area_ap_cm2, area_panel_cm2 = _read_area_cm2(inputs)
    if area_ap_cm2 > 0.0 and area_panel_cm2 > 0.0:
        return area_ap_cm2 / area_panel_cm2
    return None


def x5_aperture_classificazione(inputs: dict[str, Any]) -> dict[str, Any]:
    """Classifica l'apertura rispetto al pannello e determina trigger FEM locale."""

    norm_refs = [
        "NTC2018 §7.2.6.2",
        "EN 1992-1-1 §7.3",
        "Modello interno cautelativo RD2229 X5",
    ]
    area_ap_cm2, area_panel_cm2 = _read_area_cm2(inputs)
    if area_ap_cm2 <= 0.0 or area_panel_cm2 <= 0.0:
        return _error_result(
            "Errore: parametri area non validi (area_apertura_cm2/m2, area_pannello_cm2/m2).",
            norm_refs,
        )

    run_id = str(uuid.uuid4())
    steps: list[str] = []
    warnings: list[str] = []

    soglie = _read_thresholds(inputs)
    alpha_default = _read_alpha_defaults(inputs)
    near_support_limit = _read_near_support_limit(inputs)

    ratio = area_ap_cm2 / area_panel_cm2
    classe, alpha_ap = _classify_ratio(ratio, soglie, alpha_default)

    near_support, near_support_ratio = _near_support_trigger(inputs, near_support_limit)
    near_peak = _near_peak_shear_trigger(inputs)
    cerchiatura_significativa = bool(
        inputs.get("cerchiatura_redistribuzione_significativa", False)
        or inputs.get("cerchiatura_significativa", False)
    )

    fem_trigger = (
        ratio > soglie["trigger_fem"] or near_support or near_peak or cerchiatura_significativa
    )
    trigger_reasons: list[str] = []
    if ratio > soglie["trigger_fem"]:
        trigger_reasons.append("rapporto_apertura_superiore_trigger")
    if near_support:
        trigger_reasons.append("apertura_vicina_appoggi")
    if near_peak:
        trigger_reasons.append("apertura_in_zona_picco_taglio")
    if cerchiatura_significativa:
        trigger_reasons.append("redistribuzione_cerchiatura_significativa")

    steps.append(
        f"rapporto_apertura = area_apertura/area_pannello = {area_ap_cm2:.3f}/{area_panel_cm2:.3f} = {ratio:.6f}"
    )
    steps.append(
        "classi default: piccola<0.10, media<0.25, grande<=0.50, estrema>0.50; "
        f"classe={classe}, alpha_ap={alpha_ap:.3f}"
    )
    if near_support_ratio is not None:
        steps.append(
            "near_support_ratio = distanza_apertura_appoggio/luce = "
            f"{near_support_ratio:.4f} (limite {near_support_limit:.4f})"
        )
    steps.append(f"trigger FEM locale: {'SI' if fem_trigger else 'NO'}")

    if _manual_area_flag(inputs):
        _push_warning(
            warnings,
            steps,
            "X5-AREA-001",
            "Area di influenza impostata manualmente: verificare tracciabilita del dato.",
        )
    if ratio > soglie["trigger_fem"]:
        _push_warning(
            warnings,
            steps,
            "X5-APE-001",
            "Rapporto apertura oltre soglia trigger FEM locale.",
        )
    if ratio > soglie["estrema"]:
        _push_warning(
            warnings,
            steps,
            "X5-APE-002",
            "Apertura estrema: verifica locale/manuale obbligatoria.",
        )

    utilisation = ratio / soglie["trigger_fem"] if soglie["trigger_fem"] > 0 else None
    ok = ratio <= 1.0

    return {
        "ok": ok,
        "value": round(ratio, 6),
        "utilisation": round(utilisation, 4) if utilisation is not None else None,
        "details": {
            "classe_apertura": classe,
            "alpha_ap": round(alpha_ap, 6),
            "rapporto_apertura": round(ratio, 6),
            "area_apertura_cm2": round(area_ap_cm2, 4),
            "area_pannello_cm2": round(area_panel_cm2, 4),
            "area_apertura_m2": round(area_ap_cm2 / 10_000.0, 6),
            "area_pannello_m2": round(area_panel_cm2 / 10_000.0, 6),
            "trigger_fem": fem_trigger,
            "trigger_reasons": trigger_reasons,
            "near_support_luce_ratio": round(near_support_limit, 6),
            "near_support_ratio": (
                round(near_support_ratio, 6) if near_support_ratio is not None else None
            ),
        },
        "steps": steps,
        "warnings": warnings,
        "trace": {"run_id": run_id},
        "norm_references": norm_refs,
    }


def x5_aperture_rigidezza(inputs: dict[str, Any]) -> dict[str, Any]:
    """Calcola la rigidezza efficace del solaio con modello cautelativo EI_eff."""

    norm_refs = [
        "NTC2018 §7.2.6.2",
        "EN 1992-1-1 §7.3",
        "Modello interno cautelativo RD2229 X5",
    ]
    ei_lordo_kgf_cm2 = float(inputs.get("EI_lordo_kgf_cm2", 0.0))
    if ei_lordo_kgf_cm2 <= 0.0:
        ei_lordo_nm2 = float(inputs.get("EI_lordo_Nm2", 0.0))
        if ei_lordo_nm2 > 0.0:
            ei_lordo_kgf_cm2 = ei_lordo_nm2 / _KGF_CM2_TO_NM2

    if ei_lordo_kgf_cm2 <= 0.0:
        return _error_result(
            "Errore: fornire EI_lordo_kgf_cm2 oppure EI_lordo_Nm2 > 0.",
            norm_refs,
        )

    run_id = str(uuid.uuid4())
    steps: list[str] = []
    warnings: list[str] = []

    soglie = _read_thresholds(inputs)
    alpha_default = _read_alpha_defaults(inputs)

    ratio = _optional_ratio(inputs)
    alpha_raw = inputs.get("alpha_ap", None)
    if alpha_raw is None:
        if ratio is None:
            return _error_result(
                "Errore: fornire alpha_ap oppure dati sufficienti per rapporto apertura.",
                norm_refs,
            )
        classe, alpha_ap = _classify_ratio(ratio, soglie, alpha_default)
    else:
        alpha_ap = min(max(float(alpha_raw), 0.0), 0.95)
        classe = "manuale"

    ei_eff_kgf_cm2 = ei_lordo_kgf_cm2 * (1.0 - alpha_ap)
    ei_eff_nm2 = ei_eff_kgf_cm2 * _KGF_CM2_TO_NM2
    ei_lordo_nm2 = ei_lordo_kgf_cm2 * _KGF_CM2_TO_NM2

    near_support_limit = _read_near_support_limit(inputs)
    near_support, _ = _near_support_trigger(inputs, near_support_limit)
    near_peak = _near_peak_shear_trigger(inputs)
    cerchiatura_significativa = bool(
        inputs.get("cerchiatura_redistribuzione_significativa", False)
        or inputs.get("cerchiatura_significativa", False)
    )
    fem_trigger = (
        (ratio is not None and ratio > soglie["trigger_fem"])
        or near_support
        or near_peak
        or cerchiatura_significativa
    )

    steps.append(f"EI_eff = EI_lordo*(1-alpha_ap) = {ei_lordo_kgf_cm2:.3f}*(1-{alpha_ap:.3f})")
    steps.append(f"EI_eff = {ei_eff_kgf_cm2:.3f} kgf*cm2 = {ei_eff_nm2:.3f} N*m2")
    if ratio is not None:
        steps.append(f"rapporto_apertura = {ratio:.6f}, classe={classe}")
    steps.append(f"trigger FEM locale: {'SI' if fem_trigger else 'NO'}")

    if _manual_area_flag(inputs):
        _push_warning(
            warnings,
            steps,
            "X5-AREA-001",
            "Area di influenza impostata manualmente: verificare tracciabilita del dato.",
        )
    if ratio is not None and ratio > soglie["trigger_fem"]:
        _push_warning(
            warnings,
            steps,
            "X5-APE-001",
            "Rapporto apertura oltre soglia trigger FEM locale.",
        )
    if ratio is not None and ratio > soglie["estrema"]:
        _push_warning(
            warnings,
            steps,
            "X5-APE-002",
            "Apertura estrema: verifica locale/manuale obbligatoria.",
        )

    utilisation = ei_eff_kgf_cm2 / ei_lordo_kgf_cm2 if ei_lordo_kgf_cm2 > 0 else None
    ok = ei_eff_kgf_cm2 > 0.0

    return {
        "ok": ok,
        "value": round(ei_eff_kgf_cm2, 4),
        "utilisation": round(utilisation, 4) if utilisation is not None else None,
        "details": {
            "classe_apertura": classe,
            "alpha_ap": round(alpha_ap, 6),
            "rapporto_apertura": round(ratio, 6) if ratio is not None else None,
            "EI_lordo_kgf_cm2": round(ei_lordo_kgf_cm2, 4),
            "EI_eff_kgf_cm2": round(ei_eff_kgf_cm2, 4),
            "EI_lordo_Nm2": round(ei_lordo_nm2, 4),
            "EI_eff_Nm2": round(ei_eff_nm2, 4),
            "riduzione_percento": round(alpha_ap * 100.0, 4),
            "trigger_fem": fem_trigger,
        },
        "steps": steps,
        "warnings": warnings,
        "trace": {"run_id": run_id},
        "norm_references": norm_refs,
    }


def x5_cerchiatura_redistribuzione(inputs: dict[str, Any]) -> dict[str, Any]:
    """Stima redistribuzione su cerchiatura equivalente e trigger FEM locale."""

    norm_refs = [
        "NTC2018 §7.2.6.2",
        "NTC2018 §4.1.2",
        "Modello interno cautelativo RD2229 X5",
    ]

    run_id = str(uuid.uuid4())
    steps: list[str] = []
    warnings: list[str] = []

    cfg = inputs.get("cerchiature", {})
    if not isinstance(cfg, dict):
        cfg = {}

    soglia_significativa = float(cfg.get("soglia_redistribuzione_significativa", 0.30))
    tipi_ammessi_raw = cfg.get(
        "tipi_ammessi",
        ["acciaio", "calcestruzzo_armato", "mista", "legno", "profilati"],
    )
    tipi_ammessi = (
        [str(item).strip().lower() for item in tipi_ammessi_raw]
        if isinstance(tipi_ammessi_raw, list)
        else ["acciaio", "calcestruzzo_armato", "mista", "legno", "profilati"]
    )

    tipo = str(inputs.get("tipo_cerchiatura", "")).strip().lower()
    schema_coerente = bool(inputs.get("schema_statico_coerente", True))

    q_kgf_m2 = float(
        inputs.get(
            "q_area_kgf_m2",
            inputs.get("q_kgf_m2", inputs.get("carico_superficiale_kgf_m2", 0.0)),
        )
    )
    area_ap_cm2 = float(inputs.get("area_apertura_cm2", 0.0))
    area_ap_m2 = float(inputs.get("area_apertura_m2", 0.0))
    if area_ap_m2 <= 0.0 and area_ap_cm2 > 0.0:
        area_ap_m2 = area_ap_cm2 / 10_000.0

    q_apertura_kgf = float(inputs.get("Q_apertura_kgf", 0.0))
    if q_apertura_kgf <= 0.0 and q_kgf_m2 > 0.0 and area_ap_m2 > 0.0:
        q_apertura_kgf = q_kgf_m2 * area_ap_m2

    quota_raw = inputs.get("quota_redistribuita", None)
    if quota_raw is not None:
        quota_redistribuita = float(quota_raw)
    else:
        k_c = float(inputs.get("k_cerchiatura", 0.0))
        k_s = float(inputs.get("k_solaio", 0.0))
        if k_c <= 0.0:
            k_c = float(inputs.get("k_cerchiatura_kgf_cm", 0.0))
        if k_s <= 0.0:
            k_s = float(inputs.get("k_solaio_kgf_cm", 0.0))

        if k_c > 0.0 and k_s > 0.0:
            quota_redistribuita = k_c / (k_c + k_s)
            steps.append(
                f"quota_redistribuita = k_cerchiatura/(k_cerchiatura+k_solaio) = {quota_redistribuita:.6f}"
            )
        else:
            quota_redistribuita = 0.0
            steps.append("quota_redistribuita non fornita: assunto valore cautelativo 0.0")

    if not (0.0 <= quota_redistribuita <= 1.0):
        return _error_result(
            "Errore: quota_redistribuita deve essere compresa tra 0 e 1.",
            norm_refs,
        )

    q_cerchiatura_kgf = q_apertura_kgf * quota_redistribuita
    q_apertura_kn = q_apertura_kgf * _KGF_TO_KN
    q_cerchiatura_kn = q_cerchiatura_kgf * _KGF_TO_KN

    ratio = _optional_ratio(inputs)
    soglie = _read_thresholds(inputs)
    near_support_limit = _read_near_support_limit(inputs)
    near_support, _ = _near_support_trigger(inputs, near_support_limit)
    near_peak = _near_peak_shear_trigger(inputs)

    redistribuzione_significativa = quota_redistribuita >= soglia_significativa
    fem_trigger = (
        redistribuzione_significativa
        or (ratio is not None and ratio > soglie["trigger_fem"])
        or near_support
        or near_peak
    )

    trigger_reasons: list[str] = []
    if redistribuzione_significativa:
        trigger_reasons.append("redistribuzione_significativa")
    if ratio is not None and ratio > soglie["trigger_fem"]:
        trigger_reasons.append("rapporto_apertura_superiore_trigger")
    if near_support:
        trigger_reasons.append("apertura_vicina_appoggi")
    if near_peak:
        trigger_reasons.append("apertura_in_zona_picco_taglio")

    if _manual_area_flag(inputs):
        _push_warning(
            warnings,
            steps,
            "X5-AREA-001",
            "Area di influenza impostata manualmente: verificare tracciabilita del dato.",
        )
    if ratio is not None and ratio > soglie["trigger_fem"]:
        _push_warning(
            warnings,
            steps,
            "X5-APE-001",
            "Rapporto apertura oltre soglia trigger FEM locale.",
        )
    if ratio is not None and ratio > soglie["estrema"]:
        _push_warning(
            warnings,
            steps,
            "X5-APE-002",
            "Apertura estrema: verifica locale/manuale obbligatoria.",
        )

    tipo_non_ammesso = bool(tipo) and tipo not in tipi_ammessi
    if tipo_non_ammesso or not schema_coerente:
        detail = "cerchiatura non coerente con schema statico"
        if tipo_non_ammesso:
            detail = f"tipo cerchiatura '{tipo}' non ammesso"
        _push_warning(warnings, steps, "X5-CER-001", detail)

    steps.append(
        f"Q_apertura = q_area*area_apertura = {q_kgf_m2:.3f}*{area_ap_m2:.4f} = {q_apertura_kgf:.3f} kgf"
    )
    steps.append(
        f"Q_cerchiatura = quota_redistribuita*Q_apertura = {quota_redistribuita:.4f}*{q_apertura_kgf:.3f} = {q_cerchiatura_kgf:.3f} kgf"
    )
    steps.append(f"trigger FEM locale: {'SI' if fem_trigger else 'NO'}")

    utilisation = quota_redistribuita / soglia_significativa if soglia_significativa > 0.0 else None
    ok = schema_coerente and not tipo_non_ammesso

    return {
        "ok": ok,
        "value": round(quota_redistribuita, 6),
        "utilisation": round(utilisation, 4) if utilisation is not None else None,
        "details": {
            "tipo_cerchiatura": tipo,
            "tipi_ammessi": tipi_ammessi,
            "soglia_redistribuzione_significativa": round(soglia_significativa, 6),
            "quota_redistribuita": round(quota_redistribuita, 6),
            "redistribuzione_significativa": redistribuzione_significativa,
            "Q_apertura_kgf": round(q_apertura_kgf, 6),
            "Q_apertura_kN": round(q_apertura_kn, 6),
            "Q_cerchiatura_kgf": round(q_cerchiatura_kgf, 6),
            "Q_cerchiatura_kN": round(q_cerchiatura_kn, 6),
            "rapporto_apertura": round(ratio, 6) if ratio is not None else None,
            "trigger_fem": fem_trigger,
            "trigger_reasons": trigger_reasons,
        },
        "steps": steps,
        "warnings": warnings,
        "trace": {"run_id": run_id},
        "norm_references": norm_refs,
    }


def x5_parete_rigidezza_ante_post(inputs: dict[str, Any]) -> dict[str, Any]:
    """Valuta rigidezza ante/post per parete muraria con aperture e rinforzi.

    Check esteso X5 orientato a pareti murarie portanti con aperture preesistenti,
    nuove aperture e rinforzi locali secondo Cap. 8 (modello computazionale modulare).
    """

    norm_refs = [
        "NTC2018 §8.3",
        "NTC2018 §8.4",
        "NTC2018 §8.6",
        "NTC2018 §8.7",
        "Circolare 7/2019 §7.5-7.7",
        "Modello computazionale modulare RD2229 X5",
    ]

    run_id = str(uuid.uuid4())
    steps: list[str] = []
    warnings: list[str] = []

    try:
        parete = PareteMuraria(
            id=str(inputs.get("parete_id", "parete_x5")),
            lunghezza=float(inputs.get("lunghezza_cm", 0.0)),
            altezza=float(inputs.get("altezza_cm", 0.0)),
            spessore=float(inputs.get("spessore_cm", 0.0)),
            E=float(inputs.get("E_kgf_cm2", 0.0)),
        )
    except (TypeError, ValueError):
        return _error_result("Errore: parametri parete non validi.", norm_refs)

    if parete.lunghezza <= 0 or parete.altezza <= 0 or parete.spessore <= 0 or parete.E <= 0:
        return _error_result("Errore: lunghezza/altezza/spessore/E devono essere > 0.", norm_refs)

    aperture_esistenti_data = inputs.get("aperture_esistenti", [])
    aperture_mod_data = inputs.get("aperture_modificate", [])

    if not isinstance(aperture_esistenti_data, list):
        aperture_esistenti_data = []
    if not isinstance(aperture_mod_data, list):
        aperture_mod_data = []

    def _build_apertura(item: dict[str, Any]) -> Apertura:
        return Apertura(
            id=str(item.get("id", str(uuid.uuid4()))),
            tipo=str(item.get("tipo", "nuova")),
            forma=str(item.get("forma", "rettangolo")),
            posizione={
                "x": float(item.get("x_cm", 0.0)),
                "y": float(item.get("y_cm", 0.0)),
            },
            dimensioni={
                "h": float(item.get("h_cm", 0.0)),
                "b": float(item.get("b_cm", 0.0)),
            },
            stato=str(item.get("stato", "attiva")),
            note=item.get("note"),
        )

    aperture_esistenti = [
        _build_apertura(a) for a in aperture_esistenti_data if isinstance(a, dict)
    ]
    aperture_modificate = [_build_apertura(a) for a in aperture_mod_data if isinstance(a, dict)]
    aperture_finali = compute_modifica_aperture(aperture_esistenti, aperture_modificate)
    parete.aperture = aperture_finali

    rinforzi_data = inputs.get("rinforzi", [])
    if not isinstance(rinforzi_data, list):
        rinforzi_data = []
    parete.rinforzi = [
        Rinforzo(
            id=str(r.get("id", str(uuid.uuid4()))),
            tipo=str(r.get("tipo", "cerchiatura")),
            efficacia=(
                float(r.get("efficacia", 0.0)) if r.get("efficacia", None) is not None else None
            ),
            posizione=r.get("posizione", {}) if isinstance(r.get("posizione", {}), dict) else {},
            note=r.get("note"),
        )
        for r in rinforzi_data
        if isinstance(r, dict)
    ]

    result = compute_EI_post_with_reinforcements(parete)
    ratio_post_ante = result["ratio_post_ante"]
    soglia_min = float(inputs.get("soglia_ratio_post_ante", 0.60))

    steps.append(f"EI_ante = {result['EI_ante']:.3f}")
    steps.append(f"EI_post_aperture = {result['EI_post_aperture']:.3f}")
    steps.append(f"delta_EI_rinforzi = {result['delta_EI_rinforzi']:.3f}")
    steps.append(f"EI_post_rinforzo = {result['EI_post_rinforzo']:.3f}")
    steps.append(f"ratio_post_ante = {ratio_post_ante:.4f} (soglia {soglia_min:.4f})")

    if result["rapporto_aperture"] > 0.25:
        _push_warning(
            warnings,
            steps,
            "X5-APE-001",
            "Rapporto aperture elevato: attivare analisi locale/FEM.",
        )
    if result["rapporto_aperture"] > 0.50:
        _push_warning(
            warnings,
            steps,
            "X5-APE-002",
            "Rapporto aperture estremo: verifica specialistica obbligatoria.",
        )
    if ratio_post_ante < soglia_min:
        _push_warning(
            warnings,
            steps,
            "X5-RIG-001",
            "Rigidezza post-intervento sotto soglia minima configurata.",
        )

    ok = ratio_post_ante >= soglia_min
    return {
        "ok": ok,
        "value": round(ratio_post_ante, 6),
        "utilisation": round(ratio_post_ante / soglia_min, 4) if soglia_min > 0 else None,
        "details": {
            "EI_ante": round(result["EI_ante"], 6),
            "EI_post_aperture": round(result["EI_post_aperture"], 6),
            "EI_post_rinforzo": round(result["EI_post_rinforzo"], 6),
            "delta_EI_rinforzi": round(result["delta_EI_rinforzi"], 6),
            "alpha_ap": round(result["alpha_ap"], 6),
            "rapporto_aperture": round(result["rapporto_aperture"], 6),
            "n_aperture": len(aperture_finali),
            "n_rinforzi": len(parete.rinforzi),
            "ratio_post_ante": round(ratio_post_ante, 6),
            "soglia_ratio_post_ante": round(soglia_min, 6),
        },
        "steps": steps,
        "warnings": warnings,
        "trace": {"run_id": run_id},
        "norm_references": norm_refs,
    }


def x5_parete_pushover_ante_post(inputs: dict[str, Any]) -> dict[str, Any]:
    """Esegue analisi pushover multi-metodo ante/post su parete muraria.

    Metodi supportati: bilineare, trilineare, numerico.
    Criteri di arresto: carico ultimo, drift limite, duttilita limite.
    """

    norm_refs = [
        "NTC2018 §7.8.2",
        "NTC2018 §8.3-§8.7",
        "Circolare 7/2019 §7.5-7.7",
        "EN 1998-3 §7.5-7.6",
        "Modello computazionale modulare RD2229 X5 pushover",
    ]

    run_id = str(uuid.uuid4())
    steps: list[str] = []
    warnings: list[str] = []

    try:
        parete = PareteMuraria(
            id=str(inputs.get("parete_id", "parete_x5_push")),
            lunghezza=float(inputs.get("lunghezza_cm", 0.0)),
            altezza=float(inputs.get("altezza_cm", 0.0)),
            spessore=float(inputs.get("spessore_cm", 0.0)),
            E=float(inputs.get("E_kgf_cm2", 0.0)),
        )
    except (TypeError, ValueError):
        return _error_result("Errore: parametri parete non validi per pushover.", norm_refs)

    if parete.lunghezza <= 0 or parete.altezza <= 0 or parete.spessore <= 0 or parete.E <= 0:
        return _error_result(
            "Errore: lunghezza/altezza/spessore/E devono essere > 0 per pushover.",
            norm_refs,
        )

    aperture_esistenti_data = inputs.get("aperture_esistenti", [])
    aperture_mod_data = inputs.get("aperture_modificate", [])
    if not isinstance(aperture_esistenti_data, list):
        aperture_esistenti_data = []
    if not isinstance(aperture_mod_data, list):
        aperture_mod_data = []

    def _build_apertura(item: dict[str, Any]) -> Apertura:
        return Apertura(
            id=str(item.get("id", str(uuid.uuid4()))),
            tipo=str(item.get("tipo", "nuova")),
            forma=str(item.get("forma", "rettangolo")),
            posizione={"x": float(item.get("x_cm", 0.0)), "y": float(item.get("y_cm", 0.0))},
            dimensioni={"h": float(item.get("h_cm", 0.0)), "b": float(item.get("b_cm", 0.0))},
            stato=str(item.get("stato", "attiva")),
            note=item.get("note"),
        )

    aperture_esistenti = [
        _build_apertura(a) for a in aperture_esistenti_data if isinstance(a, dict)
    ]
    aperture_modificate = [_build_apertura(a) for a in aperture_mod_data if isinstance(a, dict)]
    aperture_finali = compute_modifica_aperture(aperture_esistenti, aperture_modificate)
    parete.aperture = aperture_finali

    rinforzi_data = inputs.get("rinforzi", [])
    if not isinstance(rinforzi_data, list):
        rinforzi_data = []
    parete.rinforzi = [
        Rinforzo(
            id=str(r.get("id", str(uuid.uuid4()))),
            tipo=str(r.get("tipo", "cerchiatura")),
            efficacia=(
                float(r.get("efficacia", 0.0)) if r.get("efficacia", None) is not None else None
            ),
            posizione=r.get("posizione", {}) if isinstance(r.get("posizione", {}), dict) else {},
            note=r.get("note"),
        )
        for r in rinforzi_data
        if isinstance(r, dict)
    ]

    ei_data = compute_EI_post_with_reinforcements(parete)
    ei_ante = float(ei_data["EI_ante"])
    ei_post = float(ei_data["EI_post_rinforzo"])
    alpha_ap = float(ei_data["alpha_ap"])
    ratio_delta_ei = float(ei_data["delta_EI_rinforzi"]) / max(ei_ante, 1e-9)

    methods_raw = inputs.get("metodi_pushover", ["bilineare", "trilineare", "numerico"])
    if isinstance(methods_raw, str):
        methods = tuple(m.strip() for m in methods_raw.split(",") if m.strip())
    elif isinstance(methods_raw, list):
        methods = tuple(str(m) for m in methods_raw)
    else:
        methods = ("bilineare", "trilineare", "numerico")

    stop = StopCriteria(
        stop_on_capacity=bool(inputs.get("stop_on_capacity", True)),
        stop_on_drift=bool(inputs.get("stop_on_drift", True)),
        stop_on_ductility=bool(inputs.get("stop_on_ductility", True)),
    )
    if not stop.at_least_one_enabled():
        return _error_result(
            "Errore: almeno un criterio di arresto deve essere attivo (capacity/drift/ductility).",
            norm_refs,
        )

    settings = PushoverSettings(
        methods=methods,
        drift_y=float(inputs.get("drift_y", 0.002)),
        drift_u=float(inputs.get("drift_u", 0.010)),
        ductility_max=float(inputs.get("ductility_max", 5.0)),
        ductility_min=float(inputs.get("ductility_min", 1.8)),
        drift_limit=float(inputs.get("drift_limit", 0.005)),
        post_yield_stiffness_ratio=float(inputs.get("post_yield_stiffness_ratio", 0.10)),
        n_steps_numerical=int(inputs.get("n_steps_numerical", 20)),
        tau_base_kgf_cm2=float(inputs.get("tau_base_kgf_cm2", 6.0)),
        strength_gain_coeff=float(inputs.get("strength_gain_coeff", 0.35)),
        stop_criteria=stop,
    )

    levels = (
        PerformanceLevel(
            name="DL",
            drift_limit=float(inputs.get("drift_limit_dl", 0.0025)),
            demand_factor=float(inputs.get("demand_factor_dl", 0.70)),
        ),
        PerformanceLevel(
            name="SLV",
            drift_limit=float(inputs.get("drift_limit_slv", 0.0050)),
            demand_factor=float(inputs.get("demand_factor_slv", 1.00)),
        ),
        PerformanceLevel(
            name="SLC",
            drift_limit=float(inputs.get("drift_limit_slc", 0.0075)),
            demand_factor=float(inputs.get("demand_factor_slc", 1.30)),
        ),
    )

    seismic = build_seismic_combinations(
        gk_kgf=float(inputs.get("gk_kgf", 0.0)),
        qk_kgf=float(inputs.get("qk_kgf", 0.0)),
        ag_over_g=float(inputs.get("ag_over_g", 0.25)),
        q_factor=float(inputs.get("q_factor", 1.0)),
        levels=levels,
    )

    ante = run_pushover_methods(
        ei_kgf_cm2=ei_ante,
        h_cm=parete.altezza,
        lunghezza_cm=parete.lunghezza,
        spessore_cm=parete.spessore,
        alpha_ap=alpha_ap,
        ratio_delta_ei=0.0,
        settings=settings,
    )
    post = run_pushover_methods(
        ei_kgf_cm2=ei_post,
        h_cm=parete.altezza,
        lunghezza_cm=parete.lunghezza,
        spessore_cm=parete.spessore,
        alpha_ap=alpha_ap,
        ratio_delta_ei=ratio_delta_ei,
        settings=settings,
    )
    compare = compare_ante_post(ante, post)
    perf = evaluate_performance_levels(post, seismic)

    warn_ratio_ap_fem = float(inputs.get("warning_ratio_aperture_fem", 0.25))
    warn_ratio_ap_ext = float(inputs.get("warning_ratio_aperture_estrema", 0.50))
    ratio_ap = float(ei_data["rapporto_aperture"])
    if ratio_ap > warn_ratio_ap_fem:
        _push_warning(
            warnings,
            steps,
            "X5-APE-001",
            "Rapporto aperture elevato: raccomandata analisi locale/FEM di dettaglio.",
        )
    if ratio_ap > warn_ratio_ap_ext:
        _push_warning(
            warnings,
            steps,
            "X5-APE-002",
            "Rapporto aperture estremo: verifica specialistica obbligatoria.",
        )

    drift_limit = settings.drift_limit
    ductility_min = settings.ductility_min
    any_drift_over = False
    any_mu_low = False
    for method, res in post.get("results", {}).items():
        if float(res.get("drift_u", 0.0)) > drift_limit:
            any_drift_over = True
            steps.append(
                f"{method}: drift_u={float(res.get('drift_u', 0.0)):.6f} oltre limite {drift_limit:.6f}"
            )
        if float(res.get("mu", 0.0)) < ductility_min:
            any_mu_low = True
            steps.append(
                f"{method}: duttilita mu={float(res.get('mu', 0.0)):.4f} sotto soglia {ductility_min:.4f}"
            )

    if any_drift_over:
        _push_warning(
            warnings,
            steps,
            "X5-PUSH-001",
            "Drift ultimo oltre il limite configurato almeno in un metodo pushover.",
        )
    if any_mu_low:
        _push_warning(
            warnings,
            steps,
            "X5-PUSH-002",
            "Duttilita insufficiente almeno in un metodo pushover.",
        )

    for lvl_name, by_method in perf.items():
        level_failed = any(not bool(m.get("ok", False)) for m in by_method.values())
        if level_failed:
            _push_warning(
                warnings,
                steps,
                "X5-PUSH-003",
                f"Prestazione {lvl_name} non verificata almeno in un metodo pushover.",
            )

    ratio_post_ante = float(ei_data["ratio_post_ante"])
    soglia_ratio = float(inputs.get("soglia_ratio_post_ante", 0.60))
    if ratio_post_ante < soglia_ratio:
        _push_warning(
            warnings,
            steps,
            "X5-RIG-001",
            "Rapporto rigidezza post/ante sotto soglia configurata.",
        )

    steps.append(
        f"EI_ante={ei_ante:.3f}, EI_post={ei_post:.3f}, ratio_post_ante={ratio_post_ante:.4f}"
    )
    steps.append(f"metodi_pushover_eseguiti={','.join(post.get('results', {}).keys())}")
    steps.append(
        "combinazioni_sismiche: "
        f"base_coeff={float(seismic.get('base_coeff', 0.0)):.4f}, "
        f"livelli={','.join(seismic.get('levels', {}).keys())}"
    )

    ok = (ratio_post_ante >= soglia_ratio) and (not any_mu_low)
    return {
        "ok": ok,
        "value": round(ratio_post_ante, 6),
        "utilisation": round(ratio_post_ante / soglia_ratio, 4) if soglia_ratio > 0 else None,
        "details": {
            "EI_ante": round(ei_ante, 6),
            "EI_post_rinforzo": round(ei_post, 6),
            "alpha_ap": round(alpha_ap, 6),
            "rapporto_aperture": round(ratio_ap, 6),
            "ratio_post_ante": round(ratio_post_ante, 6),
            "soglia_ratio_post_ante": round(soglia_ratio, 6),
            "settings": {
                "methods": list(settings.methods),
                "drift_y": settings.drift_y,
                "drift_u": settings.drift_u,
                "drift_limit": settings.drift_limit,
                "ductility_max": settings.ductility_max,
                "ductility_min": settings.ductility_min,
                "stop_criteria": {
                    "capacity": settings.stop_criteria.stop_on_capacity,
                    "drift": settings.stop_criteria.stop_on_drift,
                    "ductility": settings.stop_criteria.stop_on_ductility,
                },
            },
            "ante": ante,
            "post": post,
            "compare": compare,
            "seismic_combinations": seismic,
            "performance_levels": perf,
            "n_aperture": len(aperture_finali),
            "n_rinforzi": len(parete.rinforzi),
        },
        "steps": steps,
        "warnings": warnings,
        "trace": {"run_id": run_id},
        "norm_references": norm_refs,
    }
