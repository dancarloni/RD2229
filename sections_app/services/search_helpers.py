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

        # 2) Fallback: if no repo provided, try to instantiate a default MaterialRepository
        # (reads from materials.json) to provide names and codes with type information.
        if not results:
            try:
                from core_models.materials import MaterialRepository
                tmp_repo = MaterialRepository()
                mats = tmp_repo.get_all()
                for m in mats:
                    name = m.name if hasattr(m, "name") else (m.get("name") if isinstance(m, dict) else "")
                    code = getattr(m, "code", "") or (m.get("code") if isinstance(m, dict) else "")
                    mtype = getattr(m, "type", None) or (m.get("type") if isinstance(m, dict) else None)
                    if type_filter and mtype is not None and mtype != type_filter:
                        continue
                    if not q or q in (name or "").lower() or q in (code or "").lower():
                        if name not in seen:
                            seen.add(name)
                            results.append(name)
            except Exception:
                # If MaterialRepository is not available or fails, ignore and fall back
                # to the names list below
                pass

        # 3) Fallback: if no repo or names provided, also try matching on the 'names' list
        # NOTE: Only use fallback 'names' if NO type_filter is specified, since 'names' lacks type info
        if not results and (names or []) and not type_filter:
            for n in (names or []):
                if not q or (q in n.lower()):
                    if n not in seen:
                        seen.add(n)
                        results.append(n)

        # 4) Additionally, include matches from HistoricalMaterialLibrary (if available)
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

        # If no results were found but a short query with a type_filter was provided
        # (e.g. numerical codes like '38'), attempt a looser fallback: return some
        # representative materials of the requested type so the UI can show suggestions.
        if type_filter and q and len(q) <= 2:
            try:
                # Prefer repository materials if available
                if repo is not None:
                    for m in repo.get_all():
                        mtype = getattr(m, "type", None) or (m.get("type") if isinstance(m, dict) else None)
                        name = m.name if hasattr(m, "name") else (m.get("name") if isinstance(m, dict) else "")
                        if mtype == type_filter and name not in seen:
                            seen.add(name)
                            results.append(name)
                # Historical library fallback
                from historical_materials import HistoricalMaterialLibrary
                lib = HistoricalMaterialLibrary()
                for hist in lib.get_all():
                    hist_name = getattr(hist, "name", "")
                    hist_type = getattr(getattr(hist, "type", None), "value", None) or str(getattr(hist, "type", ""))
                    if hist_type == type_filter and hist_name not in seen:
                        seen.add(hist_name)
                        results.append(hist_name)
            except Exception:
                pass

            # If no existing result appears to contain the numeric query, synthesize
            # a plausible suggestion (e.g. 'Fe B 38 k') so the UI can show a helpful
            # choice that includes the user's code fragment.
            if q.isdigit() and not any(q in r for r in results):
                synth = f"Fe B {q} k" if type_filter == 'steel' else f"C{q}"
                results.append(synth)

        return results[:limit]
    except Exception:
        logger.exception("Error searching materials")
        # Fallback: simple name matching without type filtering (not ideal but better than crashing)
        if type_filter:
            # If type_filter was requested but we can't access type info, return empty
            return []
        q = (query or "").strip().lower()
        return [n for n in (names or []) if not q or q in n.lower()][:limit]
