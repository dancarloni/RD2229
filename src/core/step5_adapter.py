"""Step 5 adapter – collega ProjectModel al motore verification_service.

Funzioni pubbliche:
    - :func:`can_run_step5` – verifica se i dati minimi sono presenti
    - :func:`run_step5` – esegue le verifiche reali e restituisce ElementResult

Il modulo converte:
    1. ``GeometryEntry`` → oggetto sezione compatibile con ``CalcInput``
    2. ``MaterialEntry`` → oggetto materiale compatibile con ``CalcInput``
    3. ``LoadEntry`` + ``GeometryEntry`` + ``MaterialEntry`` → ``CalcInput``
    4. ``CalcOutput`` → ``ElementResult``

Se mancano dati minimi la funzione non solleva eccezioni: inserisce warnings e
restituisce lista vuota di ElementResult.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from src.core.results import ElementResult
from src.project.schema import (
    GeometryEntry,
    LoadEntry,
    MaterialEntry,
    ProjectModel,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Section / material shims
# ---------------------------------------------------------------------------


@dataclass
class _SectionShim:
    """Sezione minimale compatibile con i template di verifica."""

    section_type: str
    width: float  # cm
    height: float  # cm
    extra: dict[str, Any]


@dataclass
class _MaterialShim:
    """Materiale minimale compatibile con i template di verifica."""

    tags: list[str]
    f_ck: float | None = None  # MPa
    f_yk: float | None = None  # MPa
    material_type: str = ""
    extra: dict[str, Any] | None = None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def can_run_step5(project: ProjectModel) -> tuple[bool, list[str]]:
    """Verifica se il progetto ha i dati minimi per eseguire step5.

    Returns:
        ``(ok, reasons)`` dove *ok* è True se si può procedere e
        *reasons* è la lista di problemi trovati.
    """
    reasons: list[str] = []
    if not project.geometry:
        reasons.append("Nessuna geometria definita nel progetto.")
    if not project.loads:
        reasons.append("Nessun carico definito nel progetto.")
    if not project.materials:
        reasons.append("Nessun materiale definito nel progetto.")
    return (len(reasons) == 0, reasons)


def run_step5(
    project: ProjectModel,
) -> tuple[list[ElementResult], list[str], list[str]]:
    """Esegue le verifiche reali per ogni carico nel progetto.

    Usa :func:`src.core_calculus.verification_service.run_verifications_for_element`
    e converte i risultati in :class:`src.core.results.ElementResult`.

    Args:
        project: Modello del progetto.

    Returns:
        ``(element_results, warnings, trace)``
        Non solleva eccezioni per input incompleto.
    """
    warnings: list[str] = []
    trace: list[str] = []
    element_results: list[ElementResult] = []

    trace.append("step5:start")

    # Importa il verification service (può fallire se modulo non disponibile)
    try:
        from src.core_calculus.normative_registry import get_templates_for_norm
        from src.core_calculus.verification_service import run_verifications_for_element
    except ImportError as exc:
        msg = f"Modulo verification_service non disponibile: {exc}"
        warnings.append(msg)
        trace.append("step5:skip(import_error)")
        logger.warning(msg)
        return element_results, warnings, trace

    norm_code = project.code_settings.norm_code or "RD2229"
    limit_states = project.code_settings.limit_states or ["TA"]
    existing_structure = getattr(project.code_settings, "existing_structure", False)
    lc = getattr(project.code_settings, "lc", None)

    # Ottieni i template per la normativa corrente
    templates = get_templates_for_norm(norm_code)
    if not templates:
        warnings.append(f"Nessun template disponibile per la normativa '{norm_code}'; " "step5 non produce risultati.")
        trace.append(f"step5:skip(no_templates_for_{norm_code})")
        return element_results, warnings, trace

    # Filtra template che richiedono struttura esistente / LC
    filtered_templates = []
    skipped_count = 0
    for tmpl in templates:
        t_id = getattr(tmpl, "id", repr(tmpl))
        req_existing = getattr(tmpl, "requires_existing_structure", False)
        if req_existing:
            if not existing_structure:
                if skipped_count == 0:
                    warnings.append(
                        "Uno o più template richiedono struttura esistente "
                        "(code_settings.existing_structure=False); template saltati. "
                        "Impostare code_settings.existing_structure=True per abilitarli."
                    )
                trace.append(f"step5:template:{t_id}:skip(requires_existing_structure)")
                skipped_count += 1
                continue
            if lc is None:
                if skipped_count == 0:
                    warnings.append(
                        "Uno o più template richiedono Livello di Conoscenza "
                        "(code_settings.lc=None); template saltati. "
                        "Impostare code_settings.lc a 'LC1', 'LC2' o 'LC3'."
                    )
                trace.append(f"step5:template:{t_id}:skip(lc_None)")
                skipped_count += 1
                continue
        filtered_templates.append(tmpl)

    if not filtered_templates:
        warnings.append(
            "Nessun template applicabile dopo il filtro existing_structure/LC; "
            "step5 non produce risultati. "
            "Verificare code_settings.existing_structure e code_settings.lc."
        )
        trace.append("step5:skip(no_applicable_templates)")
        return element_results, warnings, trace

    templates = filtered_templates

    # Indici rapidi per geometria e materiali
    geom_by_id = {g.id: g for g in project.geometry}
    # Usa il primo materiale di tipo concrete (o il primo disponibile)
    concrete = _find_material(project.materials, "concrete")
    steel = _find_material(project.materials, "steel")
    default_material = concrete or steel or (project.materials[0] if project.materials else None)

    for load in project.loads:
        elem_id = load.element_id or "(senza id)"
        geom = geom_by_id.get(load.element_id or "")
        mat = default_material

        if geom is None:
            msg = f"step5: geometria non trovata per elemento '{elem_id}'; skip."
            warnings.append(msg)
            trace.append(f"step5:element:{elem_id}:skip(no_geom)")
            continue

        calc_input = _build_calc_input(elem_id, load, geom, mat, norm_code, limit_states, project.code_settings)

        try:
            calc_output = run_verifications_for_element(
                calc_input=calc_input,
                active_norm=norm_code,
                templates_registry=templates,
                enabled_limit_states=limit_states,
            )
        except Exception as exc:
            msg = f"step5: errore verifica elemento '{elem_id}': {exc}"
            warnings.append(msg)
            trace.append(f"step5:element:{elem_id}:error")
            logger.exception("step5 error for element %s", elem_id)
            element_results.append(
                ElementResult(
                    element_id=elem_id,
                    ok=False,
                    metrics={"step5_error": str(exc)},
                    messages=[msg],
                )
            )
            continue

        elem_result = _convert_output(elem_id, calc_output)
        element_results.append(elem_result)
        trace.append(
            f"step5:element:{elem_id}:ok={elem_result.ok}"
            f":checks={calc_output.summary_metrics.get('num_verifiche_eseguite', 0)}"
        )

    trace.append(f"step5:done(results={len(element_results)})")
    return element_results, warnings, trace


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _find_material(materials: list[MaterialEntry], material_type: str) -> MaterialEntry | None:
    """Restituisce il primo materiale del tipo specificato."""
    return next((m for m in materials if m.type == material_type), None)


def _build_calc_input(
    elem_id: str,
    load: LoadEntry,
    geom: GeometryEntry,
    mat: MaterialEntry | None,
    norm_code: str,
    limit_states: list[str],
    code_settings: Any = None,
) -> Any:
    """Costruisce un CalcInput dal modello di progetto."""
    from src.core_calculus.contracts import CalcInput

    # Sezione shim
    section = _SectionShim(
        section_type=geom.type.lower() if geom.type else "rectangular",
        width=geom.width,
        height=geom.height,
        extra=geom.extra or {},
    )

    # Materiale shim
    if mat is not None:
        tags = _material_tags(mat)
        material = _MaterialShim(
            tags=tags,
            f_ck=mat.f_ck,
            f_yk=mat.f_yk,
            material_type=mat.type,
        )
    else:
        material = _MaterialShim(tags=["concrete", "rc"])

    return CalcInput(
        element_name=elem_id,
        section=section,
        material=material,
        norm_code=norm_code,
        limit_states_enabled=list(limit_states),
        # Usa il Livello di Conoscenza da CodeSettings se presente
        lc=getattr(code_settings, "lc", None),
        N=load.N,
        Mx=load.Mx,
        My=load.My,
        Mz=load.Mz,
        Tx=load.Tx,
        Ty=load.Ty,
    )


def _material_tags(mat: MaterialEntry) -> list[str]:
    """Restituisce i tag materiale compatibili con il filtro dei template."""
    tags: list[str] = []
    if mat.type == "concrete":
        tags = ["concrete", "rc"]
    elif mat.type == "steel":
        tags = ["steel"]
    else:
        tags = [mat.type] if mat.type else ["concrete", "rc"]
    return tags


def _convert_output(elem_id: str, calc_output: Any) -> ElementResult:
    """Converte CalcOutput in ElementResult."""
    messages: list[str] = []

    # Messaggi dalla validazione
    if calc_output.validation_result is not None:
        for issue in calc_output.validation_result.issues:
            messages.append(f"[{issue.severity.upper()}] {issue.message_it}")

    # Messaggi dai template
    for check_result in calc_output.per_template_results.values():
        messages.extend(check_result.messages_it)

    # Metriche riepilogative – prefissate con "step5." per evitare collisioni
    metrics: dict[str, Any] = {f"step5.{k}": v for k, v in calc_output.summary_metrics.items()}
    metrics["step5.norm_code"] = calc_output.norm_code

    # Aggiunge metriche di dettaglio per ogni template
    for t_id, cr in calc_output.per_template_results.items():
        if cr.utilisation is not None:
            metrics[f"step5.{t_id}:utilisation"] = cr.utilisation
        metrics[f"step5.{t_id}:ok"] = cr.ok

    return ElementResult(
        element_id=elem_id,
        ok=calc_output.ok,
        metrics=metrics,
        messages=messages,
    )
