"""Report builder per RD2229 – produce ReportArtifact serializzabile.

Funzione principale: :func:`build_report`.

Il builder non dipende da GUI né da librerie di PDF:
    - genera contenuto Markdown (default) o HTML
    - include schema_version, timestamp, warnings, trace, risultati elementi
    - usa string templates (nessuna dipendenza da Jinja2)
"""

from __future__ import annotations

import dataclasses
import datetime
import json
from dataclasses import dataclass, field
from typing import Any

from src.core.results import ResultsModel
from src.project.schema import ProjectModel

APP_VERSION = "0.1.0"


@dataclass
class ReportArtifact:
    """Artefatto report prodotto da :func:`build_report`.

    Contiene il testo in formato MD e/o HTML, più i metadati di tracciabilità.
    """

    title: str = ""
    schema_version: str = ""
    timestamp: str = ""
    app_version: str = APP_VERSION
    project_name: str = ""
    norm_code: str = ""
    markdown: str = ""
    html: str = ""
    # Tracciabilità compatta (non log completo)
    warnings: list[str] = field(default_factory=list)
    trace_summary: list[str] = field(default_factory=list)
    element_count: int = 0
    global_ok: bool = False
    extra: dict[str, Any] = field(default_factory=dict)


def build_report(
    project: ProjectModel,
    results: ResultsModel,
    *,
    title: str | None = None,
) -> ReportArtifact:
    """Costruisce un :class:`ReportArtifact` da progetto e risultati.

    Args:
        project: Modello del progetto (per input e settings).
        results: Risultati della pipeline di calcolo.
        title: Titolo opzionale del report (default: nome progetto o "Rapporto RD2229").

    Returns:
        :class:`ReportArtifact` con markdown e html generati.
    """
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
    report_title = title or project.project_info.name or "Rapporto RD2229"
    norm_code = project.code_settings.norm_code or "RD2229"

    # Traccia compatta: solo le voci significative (max 20)
    trace_summary = _compact_trace(results.trace)

    md = _build_markdown(project, results, report_title, norm_code, ts, trace_summary)
    html = _build_html(md, report_title)

    return ReportArtifact(
        title=report_title,
        schema_version=project.schema_version,
        timestamp=ts,
        app_version=APP_VERSION,
        project_name=project.project_info.name,
        norm_code=norm_code,
        markdown=md,
        html=html,
        warnings=list(results.warnings),
        trace_summary=trace_summary,
        element_count=len(results.elements),
        global_ok=results.ok,
    )


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _compact_trace(trace: list[str]) -> list[str]:
    """Restituisce una traccia compatta (max 20 voci, filtra le ridondanti)."""
    important_prefixes = (
        "pipeline:",
        "step5:",
        "seismic:",
        "element:",
    )
    filtered = [
        t for t in trace
        if any(t.startswith(p) for p in important_prefixes)
    ]
    return filtered[:20]


def _build_markdown(
    project: ProjectModel,
    results: ResultsModel,
    title: str,
    norm_code: str,
    ts: str,
    trace_summary: list[str],
) -> str:
    """Genera il contenuto Markdown del report."""
    lines: list[str] = []

    # Intestazione
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"**Schema version:** `{project.schema_version}`  ")
    lines.append(f"**Generato:** {ts}  ")
    lines.append(f"**App version:** {APP_VERSION}  ")
    lines.append(f"**Normativa:** {norm_code}  ")
    lines.append(f"**Esito globale:** {'✅ OK' if results.ok else '❌ NON OK'}  ")
    lines.append("")

    # Informazioni progetto
    lines.append("## Informazioni Progetto")
    lines.append("")
    pi = project.project_info
    if pi.name:
        lines.append(f"- **Nome:** {pi.name}")
    if pi.description:
        lines.append(f"- **Descrizione:** {pi.description}")
    if pi.author:
        lines.append(f"- **Autore:** {pi.author}")
    lines.append("")

    # Impostazioni normativa
    lines.append("## Impostazioni Normativa")
    lines.append("")
    cs = project.code_settings
    lines.append(f"- **Normativa:** {cs.norm_code}")
    lines.append(f"- **Stati limite:** {', '.join(cs.limit_states)}")
    lines.append(f"- **Unità forza:** {cs.units_force}")
    lines.append(f"- **Unità lunghezza:** {cs.units_length}")
    lines.append("")

    # Riepilogo input
    lines.append("## Riepilogo Input")
    lines.append("")
    lines.append(f"- Elementi geometrici: {len(project.geometry)}")
    lines.append(f"- Materiali: {len(project.materials)}")
    lines.append(f"- Combinazioni di carico: {len(project.loads)}")
    lines.append("")

    # Warnings
    if results.warnings:
        lines.append("## ⚠️ Avvisi")
        lines.append("")
        for w in results.warnings:
            lines.append(f"- {w}")
        lines.append("")

    # Risultati elementi
    lines.append("## Risultati Verifiche")
    lines.append("")
    if results.elements:
        lines.append("| Elemento | Esito | Metriche principali |")
        lines.append("|----------|-------|---------------------|")
        for elem in results.elements:
            esito = "✅ OK" if elem.ok else "❌ NON OK"
            # Mostra solo le metriche numeriche più significative
            key_metrics = _format_key_metrics(elem.metrics)
            lines.append(f"| {elem.element_id} | {esito} | {key_metrics} |")
        lines.append("")
    else:
        lines.append("_Nessun risultato disponibile._")
        lines.append("")

    # Traccia calcolo
    if trace_summary:
        lines.append("## Traccia Calcolo")
        lines.append("")
        lines.append("```")
        for t in trace_summary:
            lines.append(t)
        lines.append("```")
        lines.append("")

    return "\n".join(lines)


def _format_key_metrics(metrics: dict[str, Any]) -> str:
    """Formatta le metriche principali in una stringa compatta."""
    keys_of_interest = ["status", "num_verifiche_eseguite", "utilizzazione_massima", "norm_code"]
    parts: list[str] = []
    for key in keys_of_interest:
        if key in metrics:
            val = metrics[key]
            if isinstance(val, float):
                parts.append(f"{key}: {val:.2f}")
            else:
                parts.append(f"{key}: {val}")
    if not parts:
        # Fallback: prendi le prime 3 metriche
        for k, v in list(metrics.items())[:3]:
            if isinstance(v, float):
                parts.append(f"{k}: {v:.2f}")
            else:
                parts.append(f"{k}: {v}")
    return "; ".join(parts) if parts else "-"


def _build_html(markdown_content: str, title: str) -> str:
    """Converte il Markdown in HTML minimale (senza dipendenze esterne).

    Conversione basica:
    - Titoli (# ## ###)
    - Grassetto (**testo**)
    - Liste (- item)
    - Tabelle (| col |)
    - Code block (``` ... ```)
    """
    import re

    lines = markdown_content.splitlines()
    html_lines: list[str] = [
        "<!DOCTYPE html>",
        "<html lang='it'>",
        "<head>",
        f"  <meta charset='UTF-8'>",
        f"  <title>{_esc(title)}</title>",
        "  <style>",
        "    body { font-family: sans-serif; max-width: 900px; margin: 2em auto; padding: 0 1em; }",
        "    table { border-collapse: collapse; width: 100%; }",
        "    th, td { border: 1px solid #ccc; padding: 0.4em 0.6em; text-align: left; }",
        "    th { background: #f0f0f0; }",
        "    pre { background: #f8f8f8; padding: 1em; overflow-x: auto; }",
        "    code { background: #f8f8f8; padding: 0.1em 0.3em; }",
        "  </style>",
        "</head>",
        "<body>",
    ]

    in_code_block = False
    in_table = False

    def flush_table() -> None:
        nonlocal in_table
        if in_table:
            html_lines.append("</table>")
            in_table = False

    for raw_line in lines:
        line = raw_line

        # Code blocks
        if line.strip() == "```":
            flush_table()
            if in_code_block:
                html_lines.append("</pre>")
                in_code_block = False
            else:
                html_lines.append("<pre>")
                in_code_block = True
            continue
        if in_code_block:
            html_lines.append(_esc(line))
            continue

        # Tables
        if line.startswith("|"):
            if not in_table:
                html_lines.append("<table>")
                in_table = True
            cells = [c.strip() for c in line.strip("|").split("|")]
            # Skip separator rows (|---|---|)
            if all(re.match(r"^[-: ]+$", c) for c in cells):
                continue
            tag = "th" if not any("<td>" in h for h in html_lines[-3:]) else "td"
            row = "".join(f"<{tag}>{_esc(c)}</{tag}>" for c in cells)
            html_lines.append(f"  <tr>{row}</tr>")
            continue

        flush_table()

        # Headings
        m = re.match(r"^(#{1,4})\s+(.*)", line)
        if m:
            level = len(m.group(1))
            text = _inline_md(m.group(2))
            html_lines.append(f"<h{level}>{text}</h{level}>")
            continue

        # Lists
        m_list = re.match(r"^[-*]\s+(.*)", line)
        if m_list:
            html_lines.append(f"<li>{_inline_md(m_list.group(1))}</li>")
            continue

        # Empty line
        if not line.strip():
            html_lines.append("<br>")
            continue

        # Paragraph
        html_lines.append(f"<p>{_inline_md(line)}</p>")

    if in_code_block:
        html_lines.append("</pre>")
    if in_table:
        html_lines.append("</table>")

    html_lines.extend(["</body>", "</html>"])
    return "\n".join(html_lines)


def _esc(text: str) -> str:
    """HTML escape."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _inline_md(text: str) -> str:
    """Processa inline Markdown: **grassetto**, `codice`."""
    import re

    # Grassetto **...**
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # Corsivo *...*
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    # Codice inline `...`
    text = re.sub(r"`(.+?)`", lambda m: f"<code>{_esc(m.group(1))}</code>", text)
    return text
