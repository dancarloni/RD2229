"""Confronto risultati multi-norma (Fase Q.7)."""

from __future__ import annotations

from typing import Any

from src.core.results import ResultsModel


def build_norms_table(results: ResultsModel) -> str:
    """Genera tabella comparativa norme in Markdown.

    Attende dati in ``results.extra['norm_comparison']`` con struttura:
    ``{element_id: {norma: {M_Rd: ..., V_Rd: ..., N_Rd: ..., ok: ...}}}``
    """
    payload = results.extra.get("norm_comparison")
    if not isinstance(payload, dict) or not payload:
        return ""

    lines = [
        "## Confronto multi-norma",
        "",
        "| Elemento | Norma | M_Rd | V_Rd | N_Rd | Esito | Note |",
        "|---|---|---:|---:|---:|---|---|",
    ]
    for element_id in sorted(payload):
        by_norm = payload[element_id]
        if not isinstance(by_norm, dict):
            continue
        for norm_name in sorted(by_norm):
            values = by_norm[norm_name]
            if not isinstance(values, dict):
                continue
            status = "OK" if bool(values.get("ok", False)) else "NON OK"
            note = _significant_delta_note(values)
            lines.append(
                f"| {element_id} | {norm_name} | {_fmt(values.get('M_Rd'))} | "
                f"{_fmt(values.get('V_Rd'))} | {_fmt(values.get('N_Rd'))} | {status} | {note} |"
            )
    if len(lines) <= 4:
        return ""
    return "\n".join(lines)


def _significant_delta_note(values: dict[str, Any]) -> str:
    delta = values.get("delta_pct")
    if isinstance(delta, (int, float)) and abs(delta) > 10:
        return f"Delta {delta:.1f}%"
    return str(values.get("note", "-") or "-")


def _fmt(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)
