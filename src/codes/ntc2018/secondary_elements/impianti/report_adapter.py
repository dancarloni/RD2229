from __future__ import annotations

from .models import RisultatoImpianto


def adatta_per_report(risultato: RisultatoImpianto) -> dict:
    return {
        "titolo": f"Verifica impianto {risultato.spec.categoria.value}",
        "descrizione": f"Massa {risultato.spec.massa_kg} kg, quota {risultato.spec.quota_cm} cm",
        "input": {},
        "slu": {},
        "sle": {},
        "passaggi": risultato.passaggi_calcolo,
    }


def export_markdown(risultato: RisultatoImpianto) -> str:
    lines = [
        f"# Verifica Impianto {risultato.spec.categoria.value}",
        f"- Massa: {risultato.spec.massa_kg} kg",
        f"- Ancoraggi: {risultato.spec.numero_ancoraggi}",
        "",
    ]
    lines.extend(risultato.passaggi_calcolo)
    return "\n".join(lines)
