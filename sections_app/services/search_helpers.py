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
        query: user query (case-insensitive substring match). Empty string returns all sections.
        limit: maximum number of results to return

    Returns:
        List of matching section names (max length = limit)
    """
    q = (query or "").strip().lower()
    try:
        if repo is None:
            # If query is empty, return all; otherwise filter
            if not q:
                return list(names or [])[:limit]
            return [s for s in (names or []) if q in s.lower()][:limit]
        secs = repo.get_all_sections()
        # If query is empty, return all; otherwise filter
        if not q:
            return [s.name for s in secs][:limit]
        return [s.name for s in secs if q in (s.name or "").lower()][:limit]
    except Exception:
        logger.exception("Error searching sections")
        if not q:
            return list(names or [])[:limit]
        return [s for s in (names or []) if q in s.lower()][:limit]


def search_materials(repo, names: Optional[List[str]], query: str, type_filter: Optional[str] = None, limit: int = 200) -> List[str]:
    """Search materials using MaterialRepository or a static list.

    ✅ Ricerca sia nel campo 'name' che nel campo 'code' del materiale.
    
    Args:
        repo: MaterialRepository or None
        names: fallback list of material names
        query: user query (case-insensitive substring match on name OR code). Empty string returns all materials of the type.
        type_filter: "concrete", "steel", or None to disable type filtering
        limit: maximum number of results to return

    Returns:
        List of matching material names (max length = limit), or material name/code combined if available
    """
    q = (query or "").strip().lower()
    try:
        results: List[str] = []
        seen = set()

        # 1) Search in provided MaterialRepository if available
        if repo is not None:
            mats = repo.get_all()
            for m in mats:
                name = m.name if hasattr(m, "name") else (m.get("name") if isinstance(m, dict) else "")
                code = getattr(m, "code", "") or (m.get("code") if isinstance(m, dict) else "")
                mtype = getattr(m, "type", None) or (m.get("type") if isinstance(m, dict) else None)

                # Filtra per tipo se specificato
                if type_filter and mtype is not None and mtype != type_filter:
                    continue

                # If query is empty, include all; otherwise match
                if not q or q in (name or "").lower() or q in (code or "").lower():
                    if name not in seen:
                        seen.add(name)
                        results.append(name)

        # 2) Fallback: if no repo or names provided, also try matching on the 'names' list
        if not results and (names or []):
            for n in (names or []):
                if not q or (q in n.lower()):
                    if n not in seen:
                        seen.add(n)
                        results.append(n)

        # 3) Additionally, include matches from HistoricalMaterialLibrary (if available)
        try:
            from historical_materials import HistoricalMaterialLibrary
            lib = HistoricalMaterialLibrary()
            for hist in lib.get_all():
                hist_name = getattr(hist, "name", "")
                hist_code = getattr(hist, "code", "")
                hist_type = getattr(getattr(hist, "type", None), "value", None) or str(getattr(hist, "type", ""))

                # Filtra per tipo storica se specificato
                if type_filter and hist_type and hist_type != type_filter:
                    continue

                if not q or q in (hist_name or "").lower() or q in (hist_code or "").lower():
                    if hist_name not in seen:
                        seen.add(hist_name)
                        results.append(hist_name)
        except Exception:
            # Historical library not available, ignore
            pass

        return results[:limit]
    except Exception:
        logger.exception("Error searching materials")
        return [n for n in (names or []) if q in n.lower()][:limit]
