"""Builder relazione professionale (Fase Q)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from html import escape
from typing import Callable

from src.core.results import ResultsModel
from src.project.schema import ProjectModel

from .citazioni_normative import build_citation_index, collect_citations, render_appendice
from .comparison import build_norms_table
from .custom import get_custom_sections
from .pipeline import PipelineReport
from .sections import (
    capitolo_analisi,
    capitolo_azioni,
    capitolo_conclusioni,
    capitolo_introduzione,
    capitolo_materiali,
    capitolo_risultati,
    capitolo_verifiche,
    sommario_ancore,
)
from .template_a4 import TemplateA4

SectionFn = Callable[[ProjectModel, ResultsModel], str]


@dataclass(slots=True)
class ReportConfig:
    """Configurazione di build del report professionale."""

    title: str = "Relazione di calcolo"
    committente: str = ""
    professionista: str = ""
    numero_pratica: str = ""
    include_comparison: bool = False
    include_custom_sections: bool = True
    include_appendix: bool = True
    selected_sections: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ReportArtifact:
    """Artefatto completo renderizzato nei formati principali."""

    title: str
    generated_at: str
    markdown: str
    html: str
    ascii_text: str
    citations: list[str] = field(default_factory=list)
    section_order: list[str] = field(default_factory=list)


def build_report(
    project: ProjectModel,
    results: ResultsModel,
    config: ReportConfig | None = None,
) -> ReportArtifact:
    """Costruisce un report professionale completo da modello e risultati."""
    cfg = config or ReportConfig()
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    title = cfg.title or project.project_info.name or "Relazione di calcolo"

    citations = collect_citations(results)
    citation_index = build_citation_index(citations)

    base_sections: list[tuple[str, str]] = [
        ("dati_generali", capitolo_introduzione(project, results)),
        ("materiali", capitolo_materiali(project, results)),
        ("azioni", capitolo_azioni(project, results)),
        ("analisi", capitolo_analisi(project, results)),
        (
            "verifiche",
            capitolo_verifiche(project, results, citation_index=citation_index),
        ),
        ("risultati", capitolo_risultati(project, results)),
        ("conclusioni", capitolo_conclusioni(project, results)),
    ]

    if cfg.include_comparison:
        comparison_md = build_norms_table(results)
        if comparison_md.strip():
            base_sections.append(("confronto_norme", comparison_md))

    if cfg.include_custom_sections:
        for custom in get_custom_sections():
            custom_content = custom.generator(project, results) or ""
            if custom_content.strip():
                base_sections.append((custom.name, custom_content.strip()))

    dynamic_pipeline = PipelineReport.from_registry()
    for key, content in dynamic_pipeline.build_sections(project, results):
        base_sections.append((key, content))

    selected = set(cfg.selected_sections)
    if selected:
        base_sections = [item for item in base_sections if item[0] in selected]

    toc_entries = [(title_for_key(key), anchor_for_key(key)) for key, _ in base_sections]

    markdown_lines: list[str] = [f"# {title}", "", f"**Generato:** {generated_at}", ""]
    markdown_lines.append(sommario_ancore(toc_entries))
    markdown_lines.append("")
    for key, section_content in base_sections:
        markdown_lines.append(f'<a id="{anchor_for_key(key)}"></a>')
        markdown_lines.append(section_content)
        markdown_lines.append("")

    if cfg.include_appendix:
        markdown_lines.append(render_appendice(citations))

    markdown_content = "\n".join(markdown_lines).strip() + "\n"
    ascii_content = markdown_to_ascii(markdown_content)
    html_content = _build_a4_html(
        title=title,
        markdown=markdown_content,
        cfg=cfg,
        generated_at=generated_at,
    )

    return ReportArtifact(
        title=title,
        generated_at=generated_at,
        markdown=markdown_content,
        html=html_content,
        ascii_text=ascii_content,
        citations=citations,
        section_order=[key for key, _ in base_sections],
    )


def title_for_key(key: str) -> str:
    parts = key.replace("_", " ").strip().split()
    return " ".join(word.capitalize() for word in parts) if parts else key


def anchor_for_key(key: str) -> str:
    return key.lower().replace(" ", "-").replace("_", "-")


def markdown_to_ascii(markdown: str) -> str:
    """Converte markdown in plain text leggibile a larghezza 80."""
    lines: list[str] = []
    for raw in markdown.splitlines():
        line = raw.strip()
        if line.startswith("#"):
            line = line.lstrip("#").strip().upper()
            lines.append(line)
            lines.append("-" * min(80, max(10, len(line))))
            continue
        if line.startswith("|"):
            lines.append(line.replace("|", " ").strip())
            continue
        if line.startswith("- "):
            lines.append(f"* {line[2:]}")
            continue
        if line.startswith("<a id="):
            continue
        lines.append(line)
    return "\n".join(lines).strip() + "\n"


def _build_a4_html(
    *,
    title: str,
    markdown: str,
    cfg: ReportConfig,
    generated_at: str,
) -> str:
    template = TemplateA4()
    content_html = markdown_to_basic_html(markdown)
    page_chunks = split_html_by_h2(content_html)
    header = template.render_header(
        progetto=title,
        professionista=cfg.professionista,
        committente=cfg.committente,
        numero_pratica=cfg.numero_pratica,
        data_stampa=generated_at,
    )
    footer = template.render_footer(data_stampa=generated_at)
    pages = [
        template.render_page(
            content_html=chunk,
            header_html=header,
            footer_html=footer,
            page_id=f"pag-{index + 1}",
        )
        for index, chunk in enumerate(page_chunks)
    ]
    return template.render_document(title=title, pages_html=pages)


def split_html_by_h2(html: str) -> list[str]:
    """Suddivide HTML in blocchi per capitolo H2 (fallback: pagina unica)."""
    parts = html.split("<h2>")
    if len(parts) <= 1:
        return [html]
    pages: list[str] = [parts[0]]
    for part in parts[1:]:
        pages.append("<h2>" + part)
    return [page for page in pages if page.strip()]


def markdown_to_basic_html(markdown: str) -> str:
    """Conversione Markdown basilare senza dipendenze esterne."""
    html_lines: list[str] = []
    in_table = False
    for raw in markdown.splitlines():
        line = raw.rstrip()
        if line.startswith("<a id="):
            html_lines.append(line)
            continue
        if line.startswith("# "):
            if in_table:
                html_lines.append("</table>")
                in_table = False
            html_lines.append(f"<h1>{escape(line[2:].strip())}</h1>")
            continue
        if line.startswith("## "):
            if in_table:
                html_lines.append("</table>")
                in_table = False
            html_lines.append(f"<h2>{escape(line[3:].strip())}</h2>")
            continue
        if line.startswith("### "):
            if in_table:
                html_lines.append("</table>")
                in_table = False
            html_lines.append(f"<h3>{escape(line[4:].strip())}</h3>")
            continue
        if line.startswith("|"):
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if all(set(cell) <= {"-", ":"} for cell in cells):
                continue
            if not in_table:
                html_lines.append("<table>")
                in_table = True
            tag = "th" if "<th>" not in "".join(html_lines[-1:]) else "td"
            html_lines.append(
                "<tr>" + "".join(f"<{tag}>{escape(c)}</{tag}>" for c in cells) + "</tr>"
            )
            continue

        if in_table:
            html_lines.append("</table>")
            in_table = False

        if line.startswith("- "):
            html_lines.append(f"<p>• {escape(line[2:])}</p>")
            continue
        if not line:
            continue
        html_lines.append(f"<p>{escape(line)}</p>")
    if in_table:
        html_lines.append("</table>")
    return "\n".join(html_lines)
