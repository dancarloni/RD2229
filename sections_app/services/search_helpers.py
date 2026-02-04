"""Helper functions for repository-backed search operations.

This module centralizes searchable helpers used by the UI (Verification Table)
so they can be reused and tested independently.
"""
from __future__ import annotations

from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


def search_sections(repo, names: Optional[List[str]], query: str, limit: int = 200) -> List[str]:
    """Search section names using SectionRepository or a static list.

    Args:
        repo: SectionRepository or None
        names: fallback list of section names
        query: user query (case-insensitive substring match)
        limit: maximum number of results to return

    Returns:
        List of matching section names (max length = limit)
    """
    q = (query or "").strip().lower()
    if not q:
        return []
    try:
        if repo is None:
            return [s for s in (names or []) if q in s.lower()][:limit]
        secs = repo.get_all_sections()
        return [s.name for s in secs if q in (s.name or "").lower()][:limit]
    except Exception:
        logger.exception("Error searching sections")
        return [s for s in (names or []) if q in s.lower()][:limit]


def search_materials(repo, names: Optional[List[str]], query: str, type_filter: Optional[str] = None, limit: int = 200) -> List[str]:
    """Search materials using MaterialRepository or a static list.

    Args:
        repo: MaterialRepository or None
        names: fallback list of material names
        query: user query (case-insensitive substring match)
        type_filter: "concrete", "steel", or None to disable type filtering
        limit: maximum number of results to return

    Returns:
        List of matching material names (max length = limit)
    """
    q = (query or "").strip().lower()
    if not q:
        return []
    try:
        results: List[str] = []
        if repo is not None:
            mats = repo.get_all()
            for m in mats:
                name = m.name if hasattr(m, "name") else (m.get("name") if isinstance(m, dict) else "")
                mtype = getattr(m, "type", None) or (m.get("type") if isinstance(m, dict) else None)
                if type_filter and mtype is not None and mtype != type_filter:
                    continue
                if q in (name or "").lower():
                    results.append(name)
            return results[:limit]
        # fallback to static names list
        names_list = names or []
        return [n for n in names_list if q in n.lower()][:limit]
    except Exception:
        logger.exception("Error searching materials")
        return [n for n in (names or []) if q in n.lower()][:limit]
