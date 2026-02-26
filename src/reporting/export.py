"""Export di report RD2229 su file HTML e Markdown.

Funzioni pubbliche:
    - :func:`export_report_html` – scrive l'HTML su file
    - :func:`export_report_md` – scrive il Markdown su file

Entrambe usano scrittura atomica (file .tmp → os.replace) per sicurezza.
"""

from __future__ import annotations

import os


def export_report_html(artifact: "ReportArtifact", path: str) -> None:  # type: ignore[name-defined]
    """Esporta il report in formato HTML.

    Args:
        artifact: :class:`src.reporting.report_builder.ReportArtifact` con html popolato.
        path: Percorso del file destinazione (es. ``/tmp/report.html``).

    Raises:
        ValueError: Se l'artefatto non ha contenuto HTML.
    """
    from src.reporting.report_builder import ReportArtifact

    if not isinstance(artifact, ReportArtifact):
        raise TypeError(f"Atteso ReportArtifact, ricevuto {type(artifact)}")
    if not artifact.html:
        raise ValueError("Il ReportArtifact non contiene HTML. Usa build_report prima.")

    _atomic_write(path, artifact.html, encoding="utf-8")


def export_report_md(artifact: "ReportArtifact", path: str) -> None:  # type: ignore[name-defined]
    """Esporta il report in formato Markdown.

    Args:
        artifact: :class:`src.reporting.report_builder.ReportArtifact` con markdown popolato.
        path: Percorso del file destinazione (es. ``/tmp/report.md``).

    Raises:
        ValueError: Se l'artefatto non ha contenuto Markdown.
    """
    from src.reporting.report_builder import ReportArtifact

    if not isinstance(artifact, ReportArtifact):
        raise TypeError(f"Atteso ReportArtifact, ricevuto {type(artifact)}")
    if not artifact.markdown:
        raise ValueError("Il ReportArtifact non contiene Markdown. Usa build_report prima.")

    _atomic_write(path, artifact.markdown, encoding="utf-8")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _atomic_write(path: str, content: str, encoding: str = "utf-8") -> None:
    """Scrittura atomica: scrive su .tmp poi os.replace."""
    tmp_path = path + ".tmp"
    try:
        with open(tmp_path, "w", encoding=encoding) as f:
            f.write(content)
        os.replace(tmp_path, path)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise
