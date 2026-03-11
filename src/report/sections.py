"""Sezioni obbligatorie del report professionale (Fase Q.4)."""

from __future__ import annotations

from html import escape
from typing import Any

from src.core.results import ResultsModel
from src.project.schema import ProjectModel


def capitolo_introduzione(project: ProjectModel, results: ResultsModel) -> str:
    """Genera introduzione con metadati progetto e normativa."""
    info = project.project_info
    settings = project.code_settings
    lines = [
        "## 1. Dati generali",
        "",
        f"- **Progetto:** {info.name or 'Senza nome'}",
        f"- **Descrizione:** {info.description or '-'}",
        f"- **Autore:** {info.author or '-'}",
        f"- **Normativa:** {settings.norm_code}",
        f"- **Stati limite:** {', '.join(settings.limit_states) if settings.limit_states else '-'}",
        f"- **Unità:** forza {settings.units_force}, lunghezza {settings.units_length}",
        f"- **Schema input:** {project.schema_version}",
        f"- **Timestamp risultati:** {results.timestamp or '-'}",
    ]
    return "\n".join(lines)


def capitolo_materiali(project: ProjectModel, _: ResultsModel) -> str:
    """Genera tabella materiali da repository progetto."""
    lines = ["## 2. Materiali", ""]
    if not project.materials:
        lines.append("Nessun materiale definito.")
        return "\n".join(lines)

    lines.extend(
        [
            "| ID | Tipo | Classe | f_ck | f_yk |",
            "|---|---|---|---:|---:|",
        ]
    )
    for mat in project.materials:
        lines.append(
            f"| {mat.id or '-'} | {mat.type or '-'} | {mat.material_class or '-'} | "
            f"{_fmt_number(mat.f_ck)} | {_fmt_number(mat.f_yk)} |"
        )
    return "\n".join(lines)


def capitolo_azioni(project: ProjectModel, _: ResultsModel) -> str:
    """Genera capitolo azioni da carichi di progetto."""
    lines = ["## 3. Azioni", ""]
    if not project.loads:
        lines.append("Nessuna azione inserita.")
        return "\n".join(lines)

    lines.extend(
        [
            "| Elemento | N | Mx | My | Mz | Tx | Ty |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for load in project.loads:
        lines.append(
            f"| {load.element_id or '-'} | {_fmt_number(load.N)} | {_fmt_number(load.Mx)} | "
            f"{_fmt_number(load.My)} | {_fmt_number(load.Mz)} | {_fmt_number(load.Tx)} | "
            f"{_fmt_number(load.Ty)} |"
        )
    return "\n".join(lines)


def capitolo_analisi(project: ProjectModel, results: ResultsModel) -> str:
    """Genera capitolo analisi strutturale con trace pipeline."""
    lines = ["## 4. Analisi strutturale", ""]
    lines.append(f"- **Elementi geometrici:** {len(project.geometry)}")
    lines.append(f"- **Elementi calcolati:** {len(results.elements)}")
    lines.append(f"- **Esito globale:** {'OK' if results.ok else 'NON OK'}")
    if results.trace:
        lines.append("")
        lines.append("**Traccia di calcolo:**")
        lines.append("")
        for item in results.trace:
            lines.append(f"- {item}")
    return "\n".join(lines)


def capitolo_verifiche(
    project: ProjectModel,
    results: ResultsModel,
    citation_index: dict[str, int] | None = None,
) -> str:
    """Genera capitolo verifiche con riferimenti normativi sintetici."""
    _ = project
    lines = ["## 5. Verifiche", ""]
    if not results.elements:
        lines.append("Nessuna verifica disponibile.")
        return "\n".join(lines)

    lines.extend(
        [
            "| Elemento | Esito | Metriche principali | Riferimento |",
            "|---|---|---|---|",
        ]
    )

    norm_map = _extract_norm_refs_by_element(results)
    for element in results.elements:
        status = "OK" if element.ok else "NON OK"
        metrics = _render_metrics(element.metrics)
        citations = norm_map.get(element.element_id, [])
        note = _render_first_citation_note(citations, citation_index or {})
        lines.append(f"| {element.element_id} | {status} | {metrics} | {note or '-'} |")
    return "\n".join(lines)


def capitolo_risultati(project: ProjectModel, results: ResultsModel) -> str:
    """Genera riepilogo risultati e warning principali."""
    _ = project
    total = len(results.elements)
    passed = sum(1 for item in results.elements if item.ok)
    failed = total - passed

    lines = [
        "## 6. Risultati",
        "",
        f"- **Verifiche positive:** {passed}/{total}",
        f"- **Verifiche negative:** {failed}",
    ]
    if results.warnings:
        lines.append("- **Warning:**")
        for warning in results.warnings:
            lines.append(f"  - {warning}")
    return "\n".join(lines)


def capitolo_conclusioni(project: ProjectModel, results: ResultsModel) -> str:
    """Genera conclusioni sintetiche del report."""
    _ = project
    lines = ["## 7. Conclusioni", ""]
    if results.ok:
        lines.append("Il modello risulta complessivamente verificato per le analisi eseguite.")
    else:
        lines.append("Il modello presenta verifiche non soddisfatte e richiede approfondimenti.")
    lines.append("Si raccomanda la revisione ingegneristica finale prima del deposito.")
    return "\n".join(lines)


def sommario_ancore(chapters: list[tuple[str, str]]) -> str:
    """Genera sommario Markdown con ancore locali."""
    lines = ["## Sommario", ""]
    for title, anchor in chapters:
        lines.append(f"- [{escape(title)}](#{anchor})")
    return "\n".join(lines)


def _extract_norm_refs_by_element(results: ResultsModel) -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = {}
    checks = results.extra.get("checks_by_element")
    if isinstance(checks, dict):
        for element_id, payload in checks.items():
            refs: list[str] = []
            if isinstance(payload, list):
                for item in payload:
                    if isinstance(item, dict):
                        for ref in item.get("norm_references", []):
                            rendered = _normalize_ref(ref)
                            if rendered:
                                refs.append(rendered)
            mapping[str(element_id)] = sorted(set(refs), key=str.casefold)
    return mapping


def _normalize_ref(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict):
        norm_code = str(value.get("norm_code", "")).strip()
        paragraph = str(value.get("paragraph", "")).strip()
        if norm_code and paragraph:
            return f"{norm_code} §{paragraph}" if "§" not in paragraph else f"{norm_code} {paragraph}"
    return ""


def _render_first_citation_note(citations: list[str], citation_index: dict[str, int]) -> str:
    if not citations:
        return ""
    first = citations[0]
    index = citation_index.get(first)
    if index is None:
        return first
    return f"{first} [{index}]"


def _render_metrics(metrics: dict[str, Any]) -> str:
    if not metrics:
        return "-"
    items = list(metrics.items())[:3]
    chunks: list[str] = []
    for key, value in items:
        chunks.append(f"{key}: {_fmt_number(value)}")
    return "; ".join(chunks)


def _fmt_number(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)
