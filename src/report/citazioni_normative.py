"""Utility per raccolta e rendering citazioni normative nel report."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from src.core_calculus.contracts import NormReference

_REFERENCE_KEYS = {
    "norm_references",
    "norm_reference",
    "riferimento_normativo",
    "riferimenti_normativi",
    "references",
}


def collect_citations(source: Any) -> list[str]:
    """Estrae, deduplica e ordina le citazioni normative da una struttura arbitraria."""
    found: set[str] = set()
    _walk(source, found, set())
    return sorted(found, key=str.casefold)


def build_citation_index(citations: Iterable[str]) -> dict[str, int]:
    """Crea mappa citazione -> indice progressivo (1-based)."""
    ordered = sorted({c.strip() for c in citations if c and c.strip()}, key=str.casefold)
    return {citation: idx for idx, citation in enumerate(ordered, start=1)}


def render_formula_note(citation: str, citation_index: Mapping[str, int]) -> str:
    """Restituisce markup superscript per il riferimento normativa usato nella formula."""
    key = citation.strip()
    number = citation_index.get(key)
    if number is None:
        return ""
    return f"<sup>[{number}]</sup>"


def render_appendice(citations: Iterable[str], title: str = "Appendice normativa") -> str:
    """Renderizza appendice in formato Markdown con elenco numerato citazioni."""
    cleaned = sorted({c.strip() for c in citations if c and c.strip()}, key=str.casefold)
    lines = [f"## {title}", ""]
    if not cleaned:
        lines.append("Nessuna citazione normativa rilevata.")
        return "\n".join(lines)

    for index, citation in enumerate(cleaned, start=1):
        lines.append(f"{index}. [{citation}]")
    return "\n".join(lines)


def _walk(source: Any, found: set[str], seen: set[int]) -> None:
    if source is None:
        return

    source_id = id(source)
    if source_id in seen:
        return

    if isinstance(source, (str, bytes, int, float, bool)):
        return

    seen.add(source_id)

    if isinstance(source, NormReference):
        citation = _norm_reference_to_string(source)
        if citation:
            found.add(citation)
        return

    if isinstance(source, Mapping):
        for key, value in source.items():
            key_name = str(key).lower()
            if key_name in _REFERENCE_KEYS:
                _collect_references_from_value(value, found)
            else:
                _walk(value, found, seen)
        return

    norm_references = getattr(source, "norm_references", None)
    if norm_references is not None:
        _collect_references_from_value(norm_references, found)

    per_template_results = getattr(source, "per_template_results", None)
    if isinstance(per_template_results, Mapping):
        for value in per_template_results.values():
            _walk(value, found, seen)

    checks = getattr(source, "checks", None)
    if checks is not None:
        _walk(checks, found, seen)

    if hasattr(source, "model_dump") and callable(getattr(source, "model_dump")):
        try:
            dumped = source.model_dump()
            _walk(dumped, found, seen)
        except Exception:
            pass

    if hasattr(source, "__dict__"):
        for value in vars(source).values():
            _walk(value, found, seen)

    if isinstance(source, Iterable):
        for item in source:
            _walk(item, found, seen)


def _collect_references_from_value(value: Any, found: set[str]) -> None:
    if value is None:
        return

    if isinstance(value, (str, NormReference, Mapping)):
        citation = _normalize_reference(value)
        if citation:
            found.add(citation)
        return

    if isinstance(value, Iterable):
        for item in value:
            citation = _normalize_reference(item)
            if citation:
                found.add(citation)


def _normalize_reference(reference: Any) -> str:
    if reference is None:
        return ""
    if isinstance(reference, str):
        return reference.strip()
    if isinstance(reference, NormReference):
        return _norm_reference_to_string(reference)
    if isinstance(reference, Mapping):
        norm_code = str(reference.get("norm_code", "")).strip()
        paragraph = str(reference.get("paragraph", "")).strip()
        chapter = str(reference.get("chapter", "")).strip()
        formula = str(reference.get("formula_label", "")).strip()

        tokens: list[str] = []
        if norm_code:
            tokens.append(norm_code)
        if paragraph:
            tokens.append(paragraph if "\u00a7" in paragraph else f"\u00a7{paragraph}")
        elif chapter:
            tokens.append(chapter if "cap" in chapter.lower() else f"Cap. {chapter}")
        if formula:
            tokens.append(formula)
        return " ".join(tokens).strip()
    return ""


def _norm_reference_to_string(reference: NormReference) -> str:
    paragraph = reference.paragraph.strip()
    chapter = reference.chapter.strip()

    tokens: list[str] = []
    if reference.norm_code.strip():
        tokens.append(reference.norm_code.strip())
    if paragraph:
        tokens.append(paragraph if "\u00a7" in paragraph else f"\u00a7{paragraph}")
    elif chapter:
        tokens.append(chapter if "cap" in chapter.lower() else f"Cap. {chapter}")
    if reference.formula_label:
        tokens.append(reference.formula_label.strip())
    return " ".join(token for token in tokens if token).strip()
