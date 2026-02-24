"""Pipeline di calcolo RD2229.

Funzione principale: :func:`run_pipeline`.

La pipeline è:
    1. Normalizzazione e validazione minimale del progetto
    2. (opzionale) Integrazione con NTC2018 spectrum paste service
    3. Calcolo verifiche per ogni elemento/carico
    4. Aggregazione risultati in :class:`ResultsModel`

La pipeline è **deterministica** e **testabile**: non ha side-effect su file,
non modifica il :class:`ProjectModel` in ingresso e gestisce input incompleti
restituendo un :class:`ResultsModel` con warnings anziché sollevare eccezioni.
"""

from __future__ import annotations

import datetime
import logging
from typing import Any

from src.core.results import ElementResult, ResultsModel
from src.project.schema import ProjectModel

logger = logging.getLogger(__name__)


def run_pipeline(project: ProjectModel) -> ResultsModel:
    """Esegui la pipeline di calcolo su *project*.

    Args:
        project: Modello del progetto (non viene modificato).

    Returns:
        :class:`ResultsModel` con esito globale, risultati per elemento,
        warnings e traccia minimale.  Non solleva eccezioni per input
        incompleto: i problemi vengono registrati in ``warnings``.
    """
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    warnings: list[str] = []
    trace: list[str] = []
    element_results: list[ElementResult] = []

    trace.append("pipeline:start")

    # ------------------------------------------------------------------
    # Step 1 – validazione minimale del progetto
    # ------------------------------------------------------------------
    if not project.code_settings.norm_code:
        warnings.append("code_settings.norm_code non impostato; uso default 'RD2229'.")

    if not project.loads:
        warnings.append("Nessun carico definito nel progetto; pipeline produce risultati vuoti.")

    if not project.geometry:
        warnings.append("Nessun elemento geometrico definito nel progetto.")

    trace.append("pipeline:validation_done")

    # ------------------------------------------------------------------
    # Step 2 – (soft) integrazione NTC2018 spectrum paste service
    # ------------------------------------------------------------------
    seismic_ok = _try_integrate_seismic(project, warnings, trace)

    # ------------------------------------------------------------------
    # Step 3 – calcolo verifiche per ogni carico
    # ------------------------------------------------------------------
    norm_code = project.code_settings.norm_code or "RD2229"

    for load in project.loads:
        elem_id = load.element_id or "(senza id)"
        elem_result = _run_element_check(elem_id, load, project, norm_code, warnings, trace)
        element_results.append(elem_result)

    trace.append("pipeline:checks_done")

    # ------------------------------------------------------------------
    # Step 5 – integrazione motore di calcolo reale (verification_service)
    # Arricchisce le metriche con i valori numerici dal motore di verifica.
    # Non sostituisce l'esito ok/non-ok del passo 3: lo integra.
    # ------------------------------------------------------------------
    step5_ok, step5_reasons = _can_run_step5(project)
    if step5_ok:
        step5_results, step5_warnings, step5_trace = _run_step5(project)
        warnings.extend(step5_warnings)
        trace.extend(step5_trace)
        if step5_results:
            step5_by_id = {r.element_id: r for r in step5_results}
            element_results = [
                merge_element_results(base, step5_by_id.get(base.element_id))
                for base in element_results
            ]
    else:
        trace.append(f"step5:skip({'; '.join(step5_reasons)})")

    # ------------------------------------------------------------------
    # Step 4 – aggregazione
    # ------------------------------------------------------------------
    global_ok = bool(element_results) and all(r.ok for r in element_results)

    # ------------------------------------------------------------------
    # Step F – pipeline incendio (opzionale)
    # ------------------------------------------------------------------
    fire_results: list[Any] = []
    if project.fire.enabled:
        fire_results, fire_warnings, fire_trace = _run_fire_pipeline(project)
        warnings.extend(fire_warnings)
        trace.extend(fire_trace)

    # ------------------------------------------------------------------
    # Step W – pipeline vento (opzionale)
    # ------------------------------------------------------------------
    wind_result: Any = None
    if getattr(project, "wind", None) is not None:
        wind_result, wind_warnings, wind_trace = _run_wind_pipeline(project)
        warnings.extend(wind_warnings)
        trace.extend(wind_trace)

    trace.append("pipeline:complete")

    result = ResultsModel(
        ok=global_ok,
        elements=element_results,
        warnings=warnings,
        trace=trace,
        timestamp=timestamp,
        schema_version_input=project.schema_version,
    )
    if fire_results:
        result.extra["fire"] = [
            {"element_id": r.element_id, "status": r.status,
             "metrics": r.metrics, "messages": r.messages}
            for r in fire_results
        ]
    if wind_result is not None:
        result.extra["wind"] = wind_result
    return result


# ---------------------------------------------------------------------------
# Helpers (privati)
# ---------------------------------------------------------------------------


def _try_integrate_seismic(
    project: ProjectModel,
    warnings: list[str],
    trace: list[str],
) -> bool:
    """Tenta l'integrazione con il servizio di spettro NTC2018.

    Se i campi necessari mancano o il modulo non è disponibile, aggiunge un
    warning e restituisce ``False`` senza bloccare la pipeline.

    Returns:
        ``True`` se l'integrazione è avvenuta con successo.
    """
    si = project.seismic_inputs
    if not si.hazard_profile:
        # Nessun dato sismico → skip silenzioso
        trace.append("seismic:skip(no_data)")
        return False

    try:
        from src.codes.ntc2018.spectrum_paste_service import (  # noqa: F401
            Ntc2018HazardProfile,
            build_profile,
        )
    except ImportError:
        warnings.append(
            "Modulo src.codes.ntc2018.spectrum_paste_service non disponibile; "
            "dati sismici non elaborati."
        )
        trace.append("seismic:skip(import_error)")
        return False

    raw_paste = si.hazard_profile.get("raw_paste", "")
    if not raw_paste:
        warnings.append(
            "seismic_inputs.hazard_profile.raw_paste mancante; "
            "impossibile costruire il profilo NTC2018."
        )
        trace.append("seismic:skip(no_raw_paste)")
        return False

    try:
        profile = build_profile(
            class_of_use=si.class_of_use or "II",
            vita_nominale_years=si.vita_nominale_years or 50,
            vr_years=si.vr_years or 50,
            site_label=si.site_label or None,
            raw_paste=raw_paste,
        )
        if profile.quality == "ERROR":
            warnings.append(
                f"Profilo sismico NTC2018 con errori: {'; '.join(profile.messages)}"
            )
            trace.append("seismic:done(quality=ERROR)")
        else:
            trace.append(f"seismic:done(quality={profile.quality})")
        return True
    except Exception as exc:  # pragma: no cover
        warnings.append(f"Errore durante l'elaborazione del profilo sismico: {exc}")
        trace.append("seismic:error")
        return False


def _run_element_check(
    elem_id: str,
    load: Any,
    project: ProjectModel,
    norm_code: str,
    warnings: list[str],
    trace: list[str],
) -> ElementResult:
    """Esegue la verifica su un singolo elemento/carico.

    Implementazione minimale: verifica che la geometria dell'elemento sia
    presente e che i carichi siano definiti.  Una pipeline più completa
    collegherebbe qui il motore di calcolo
    (``src.core_calculus.verification_service``).
    """
    messages: list[str] = []
    metrics: dict[str, Any] = {}

    # Trova la geometria associata all'elemento
    geom = next(
        (g for g in project.geometry if g.id == load.element_id),
        None,
    )
    if geom is None and load.element_id:
        msg = f"Geometria non trovata per elemento '{load.element_id}'."
        messages.append(msg)
        warnings.append(msg)

    # Almeno un'azione interna deve essere presente per una verifica significativa
    has_loads = any(
        v is not None for v in (load.N, load.Mx, load.My, load.Mz, load.Tx, load.Ty)
    )
    if not has_loads:
        messages.append(f"Elemento '{elem_id}': nessuna azione interna definita.")

    ok = geom is not None and has_loads

    if geom is not None:
        metrics["width"] = geom.width
        metrics["height"] = geom.height

    metrics["norm_code"] = norm_code
    trace.append(f"element:{elem_id}:ok={ok}")

    return ElementResult(element_id=elem_id, ok=ok, metrics=metrics, messages=messages)


def _can_run_step5(project: "ProjectModel") -> tuple[bool, list[str]]:  # type: ignore[name-defined]
    """Delega a step5_adapter.can_run_step5 gestendo ImportError."""
    try:
        from src.core.step5_adapter import can_run_step5

        return can_run_step5(project)
    except ImportError:
        return False, ["src.core.step5_adapter non disponibile."]


def _run_step5(
    project: "ProjectModel",  # type: ignore[name-defined]
) -> tuple[list[ElementResult], list[str], list[str]]:
    """Delega a step5_adapter.run_step5 gestendo ImportError."""
    try:
        from src.core.step5_adapter import run_step5

        return run_step5(project)
    except ImportError:
        return [], ["src.core.step5_adapter non disponibile."], ["step5:skip(import_error)"]


def merge_element_results(
    base: ElementResult,
    step5: ElementResult | None,
) -> ElementResult:
    """Unisce i risultati step3 (base) con le metriche step5.

    Regola: il campo ``ok`` viene sempre preservato dal *base* (step3).
    Le metriche step5 vengono aggiunte con prefisso ``"step5."`` per evitare
    collisioni con le metriche base.

    Args:
        base: Risultato dal passo 3 (verifica semplificata).
        step5: Risultato dal passo 5 (motore di verifica reale), può essere None.

    Returns:
        ``ElementResult`` con metriche arricchite e ``ok`` invariato.
    """
    if step5 is None:
        return base

    prefixed_metrics = {
        f"step5.{k}": v for k, v in step5.metrics.items()
    }
    merged_metrics = {**base.metrics, **prefixed_metrics}
    merged_messages = base.messages + [
        m for m in step5.messages if m not in base.messages
    ]
    return ElementResult(
        element_id=base.element_id,
        ok=base.ok,  # ok da step3, invariato
        metrics=merged_metrics,
        messages=merged_messages,
    )


def _run_fire_pipeline(
    project: "ProjectModel",  # type: ignore[name-defined]
) -> tuple[list[Any], list[str], list[str]]:
    """Esegue la pipeline incendio per gli elementi selezionati.

    Returns:
        ``(fire_results, warnings, trace)``
    """
    warnings: list[str] = []
    trace: list[str] = ["fire:start"]
    results: list[Any] = []

    try:
        from src.fire.eligibility import evaluate_fire_eligibility
        from src.fire.rc_fire_check import run_rc_fire_check
    except ImportError as exc:
        warnings.append(f"Modulo src.fire non disponibile: {exc}")
        trace.append("fire:skip(import_error)")
        return results, warnings, trace

    fire_cfg = project.fire
    selected = [g for g in project.geometry if g.fire_selected]
    if not selected:
        trace.append("fire:skip(no_elements_selected)")
        return results, warnings, trace

    for elem in selected:
        eligible, reasons = evaluate_fire_eligibility(project, elem)
        if not eligible:
            msg = (
                f"fire:elemento '{elem.id}' non eleggibile: "
                + "; ".join(reasons)
            )
            warnings.append(msg)
            trace.append(f"fire:{elem.id}:skipped(not_eligible)")
            from src.fire.rc_fire_check import ElementResultFire
            results.append(ElementResultFire(
                element_id=elem.id,
                status="SKIPPED",
                metrics={},
                messages=[msg] + [f"  – {r}" for r in reasons],
            ))
            continue

        fire_result = run_rc_fire_check(project, elem)
        results.append(fire_result)
        trace.append(f"fire:{elem.id}:status={fire_result.status}")

    trace.append(f"fire:done(results={len(results)})")
    return results, warnings, trace


def _run_wind_pipeline(
    project: "ProjectModel",  # type: ignore[name-defined]
) -> tuple[Any, list[str], list[str]]:
    """Esegue la pipeline vento se i dati sono disponibili.

    Returns:
        ``(wind_result_dict_or_None, warnings, trace)``
    """
    warnings: list[str] = []
    trace: list[str] = ["wind:start"]

    try:
        from src.wind.service import WindActionService
    except ImportError as exc:
        warnings.append(f"Modulo src.wind non disponibile: {exc}")
        trace.append("wind:skip(import_error)")
        return None, warnings, trace

    wind_cfg = getattr(project, "wind", None)
    if wind_cfg is None:
        trace.append("wind:skip(no_config)")
        return None, warnings, trace

    try:
        service = WindActionService()
        wind_result = service.compute(wind_cfg)
        trace.append(f"wind:done(method={getattr(wind_cfg, 'method', 'unknown')})")
        import dataclasses
        return dataclasses.asdict(wind_result) if dataclasses.is_dataclass(wind_result) else dict(wind_result), warnings, trace
    except Exception as exc:
        warnings.append(f"Errore pipeline vento: {exc}")
        trace.append("wind:error")
        return None, warnings, trace
