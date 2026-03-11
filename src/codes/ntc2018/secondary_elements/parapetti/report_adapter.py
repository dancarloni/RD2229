from __future__ import annotations

from .models import RisultatoParapetto


def adatta_per_report(risultato: RisultatoParapetto) -> dict:
    """Adapt result to report format."""
    return {
        "titolo": f"Verifica parapetto {risultato.spec.tipo.value}",
        "descrizione": f"Altezza {risultato.spec.altezza_cm} cm, lunghezza {risultato.spec.lunghezza_cm} cm",
        "input": risultato.spec.__dict__,
        "slu": (
            risultato.risultato_slu.to_dict() if hasattr(risultato.risultato_slu, "to_dict") else {}
        ),
        "sle": (
            risultato.risultato_sle.to_dict() if hasattr(risultato.risultato_sle, "to_dict") else {}
        ),
        "passaggi": risultato.passaggi_calcolo,
    }


def export_markdown(risultato: RisultatoParapetto) -> str:
    """Export result as markdown table."""
    slu = risultato.risultato_slu
    sle = risultato.risultato_sle

    lines = [
        f"# Verifica Parapetto {risultato.spec.tipo.value}",
        "",
        "## Dati",
        f"- Altezza: {risultato.spec.altezza_cm} cm",
        f"- Lunghezza: {risultato.spec.lunghezza_cm} cm",
        f"- Massa lineare: {risultato.spec.massa_lineare_kg_m} kg/m",
        "",
        "## SLU",
        f"| Parametro | Valore |",
        f"|-----------|--------|",
        f"| Domanda sismica | {slu.domanda_sismica_kg:.2f} kg |",
        f"| Domanda d'uso | {slu.domanda_servizio_kg:.2f} kg |",
        f"| Resistenza | {slu.resistenza_ancoraggio_kg:.2f} kg |",
        f"| Rapporto D/R | {slu.rapporto_domanda_resistenza:.3f} |",
        f"| Esito | {'✓ OK' if slu.esito else '✗ NON OK'} |",
        "",
        "## SLE",
        f"| Parametro | Valore |",
        f"|-----------|--------|",
        f"| Spostamento bordo | {sle.spostamento_bordo_cm:.2f} cm |",
        f"| Spostamento ammissibile | {sle.spostamento_ammissibile_cm:.2f} cm |",
        f"| Rapporto spostamento | {sle.rapporto_spostamento:.3f} |",
        f"| Stato danno | {sle.stato_danno.value} |",
        "",
        "## Passaggi di calcolo",
        "",
    ]

    for passaggio in risultato.passaggi_calcolo:
        lines.append(f"- {passaggio}")

    return "\n".join(lines)
