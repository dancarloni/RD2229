"""Fire eligibility – valutazione eleggibilità incendio per elementi RC.

Determina se un elemento è eleggibile per le verifiche al fuoco secondo
il metodo semplificato RC (MVP).  Se non eleggibile, la pipeline salta
l'elemento e registra i motivi.

Criteri MVP (RC rettangolare):
- tipo sezione supportata: RECTANGULAR
- materiale calcestruzzo presente nel progetto
- dimensioni positive (b > 0, h > 0)
- copriferro disponibile (da fire_override o fire.cover_mm_default del progetto)
- numero lati esposti disponibile (da fire_override o fire.exposure_sides_default)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.project.schema import GeometryEntry, ProjectModel

# Tipi sezione supportati per la verifica al fuoco RC MVP
_SUPPORTED_SECTION_TYPES = {"RECTANGULAR", "RETTANGOLARE", "rectangular", "rettangolare"}


def evaluate_fire_eligibility(
    project: ProjectModel,
    element: GeometryEntry,
) -> tuple[bool, list[str]]:
    """Valuta se *element* è eleggibile per la verifica al fuoco RC.

    Args:
        project: Modello progetto (per materiali, impostazioni fuoco, ecc.).
        element: Elemento geometrico da valutare.

    Returns:
        ``(eligible, reasons)`` dove:
        - ``eligible``: True se l'elemento può essere verificato.
        - ``reasons``: lista di motivi di ineleggibilità (vuota se eleggibile).
    """
    reasons: list[str] = []

    # 1. Tipo sezione supportato
    sec_type = (element.type or "").strip()
    if sec_type.upper() not in {s.upper() for s in _SUPPORTED_SECTION_TYPES}:
        reasons.append(
            f"Tipo sezione '{sec_type}' non supportato per verifica al fuoco RC "
            f"(supportati: {', '.join(_SUPPORTED_SECTION_TYPES)})."
        )

    # 2. Dimensioni positive
    if element.width <= 0:
        reasons.append(f"Larghezza non positiva: {element.width}.")
    if element.height <= 0:
        reasons.append(f"Altezza non positiva: {element.height}.")

    # 3. Materiale calcestruzzo presente
    has_concrete = any(m.type == "concrete" for m in project.materials)
    if not has_concrete:
        reasons.append("Nessun materiale calcestruzzo definito nel progetto.")

    # 4. Copriferro disponibile
    cover_mm = _get_cover_mm(project, element)
    if cover_mm is None:
        reasons.append(
            "Copriferro non disponibile: impostare fire.cover_mm_default nel progetto "
            "oppure fire_override.cover_mm nell'elemento."
        )
    elif cover_mm <= 0:
        reasons.append(f"Copriferro non positivo: {cover_mm} mm.")

    # 5. Lati esposti disponibili
    exp_sides = _get_exposure_sides(project, element)
    if exp_sides is None:
        reasons.append(
            "Lati esposti non disponibili: impostare fire.exposure_sides_default nel progetto "
            "oppure fire_override.exposure_sides nell'elemento."
        )
    elif exp_sides < 1 or exp_sides > 4:
        reasons.append(f"Lati esposti non validi: {exp_sides} (atteso 1-4).")

    return (len(reasons) == 0, reasons)


def _get_cover_mm(project: ProjectModel, element: GeometryEntry) -> float | None:
    """Restituisce il copriferro [mm] per l'elemento (override o default progetto)."""
    if element.fire_override is not None:
        val = element.fire_override.get("cover_mm")
        if val is not None:
            return float(val)
    return project.fire.cover_mm_default


def _get_exposure_sides(project: ProjectModel, element: GeometryEntry) -> int | None:
    """Restituisce i lati esposti per l'elemento (override o default progetto)."""
    if element.fire_override is not None:
        val = element.fire_override.get("exposure_sides")
        if val is not None:
            return int(val)
    return project.fire.exposure_sides_default
