from __future__ import annotations

from .models import RisultatoControsoffitto


def adatta_per_report(risultato: RisultatoControsoffitto) -> dict:
    """Adapt result to report format."""
    return {
        "titolo": f"Verifica controsoffitto {risultato.spec.tipo.value}",
        "descrizione": f"Area {risultato.spec.area_m2} m², massa {risultato.spec.massa_superficiale_kg_m2} kg/m²",
        "input": risultato.spec.__dict__,
        "slu": {},
        "sle": {},
        "passaggi": risultato.passaggi_calcolo,
    }


def export_markdown(risultato: RisultatoControsoffitto) -> str:
    """Export result as markdown."""
    lines = [
        f"# Verifica Controsoffitto {risultato.spec.tipo.value}",
        "",
        f"- Area: {risultato.spec.area_m2} m²",
        f"- Massa superficiale: {risultato.spec.massa_superficiale_kg_m2} kg/m²",
        "",
    ]
    lines.extend(risultato.passaggi_calcolo)
    return "\n".join(lines)
