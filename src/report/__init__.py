"""Package report — renderer HTML, Markdown e PDF per verifiche strutturali."""

from .citazioni_normative import (
    build_citation_index,
    collect_citations,
    render_appendice,
    render_formula_note,
)
from .comparison import build_norms_table
from .custom import (
    clear_custom_sections,
    get_custom_sections,
    load_section_profile,
    register_custom_section,
    save_section_profile,
    unregister_custom_section,
)
from .decorators import contribuisce_report
from .export import export_ascii, export_docx, export_html, export_md, export_pdf
from .images import image_html_block, image_markdown_block
from .pipeline import (
    FornitoreSezione,
    PipelineReport,
    SectionContribution,
    clear_report_registry,
    get_report_registry,
    register_section_generator,
    register_section_provider,
)
from .renderer_html import HTMLReportRenderer
from .renderer_md import MarkdownReportRenderer
from .renderer_pdf import PDFReportRenderer
from .report_builder import ReportArtifact, ReportConfig, build_report
from .sections import (
    capitolo_analisi,
    capitolo_azioni,
    capitolo_conclusioni,
    capitolo_introduzione,
    capitolo_materiali,
    capitolo_risultati,
    capitolo_verifiche,
)
from .template_a4 import TemplateA4
from .utils import encode_image_base64

__all__ = [
    "TemplateA4",
    "ReportConfig",
    "ReportArtifact",
    "build_report",
    "collect_citations",
    "build_citation_index",
    "render_formula_note",
    "render_appendice",
    "build_norms_table",
    "register_custom_section",
    "unregister_custom_section",
    "clear_custom_sections",
    "get_custom_sections",
    "save_section_profile",
    "load_section_profile",
    "image_html_block",
    "image_markdown_block",
    "encode_image_base64",
    "FornitoreSezione",
    "SectionContribution",
    "PipelineReport",
    "register_section_generator",
    "register_section_provider",
    "get_report_registry",
    "clear_report_registry",
    "contribuisce_report",
    "capitolo_introduzione",
    "capitolo_materiali",
    "capitolo_azioni",
    "capitolo_analisi",
    "capitolo_verifiche",
    "capitolo_risultati",
    "capitolo_conclusioni",
    "export_html",
    "export_md",
    "export_ascii",
    "export_pdf",
    "export_docx",
    "HTMLReportRenderer",
    "MarkdownReportRenderer",
    "PDFReportRenderer",
]
