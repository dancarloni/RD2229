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
            # Merge metriche step5 nei risultati step3 (non sovrascrive ok)
            step5_by_id = {r.element_id: r for r in step5_results}
            merged: list[ElementResult] = []
            for base in element_results:
                s5 = step5_by_id.get(base.element_id)
                if s5 is not None:
                    merged_metrics = {**base.metrics, **s5.metrics}
                    merged_messages = base.messages + [
                        m for m in s5.messages if m not in base.messages
                    ]
                    merged.append(
                        ElementResult(
                            element_id=base.element_id,
                            ok=base.ok,
                            metrics=merged_metrics,
                            messages=merged_messages,
                        )
                    )
                else:
                    merged.append(base)
            element_results = merged
    else:
        trace.append(f"step5:skip({'; '.join(step5_reasons)})")

    # ------------------------------------------------------------------
    # Step 4 – aggregazione
    # ------------------------------------------------------------------
    global_ok = bool(element_results) and all(r.ok for r in element_results)

    trace.append("pipeline:complete")

    return ResultsModel(
        ok=global_ok,
        elements=element_results,
        warnings=warnings,
        trace=trace,
        timestamp=timestamp,
        schema_version_input=project.schema_version,
    )


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
