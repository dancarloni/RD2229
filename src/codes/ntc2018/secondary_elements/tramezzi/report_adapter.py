from __future__ import annotations

from .models import RisultatoTramezzo


def adatta_per_report(risultato: RisultatoTramezzo) -> dict:
    spec = risultato.spec
    return {
        "titolo": f"Tramezzo — {spec.sistema.value}",
        "descrizione": f"Tramezzo {spec.sistema.value} {spec.altezza_cm:.0f}x{spec.lunghezza_cm:.0f} cm",
        "input": {
            "Sistema": spec.sistema.value,
            "Altezza (cm)": f"{spec.altezza_cm:.1f}",
            "Lunghezza (cm)": f"{spec.lunghezza_cm:.1f}",
            "Spessore (cm)": f"{spec.spessore_cm:.1f}",
            "Peso lineare (kg/m)": f"{spec.peso_lineare_kg_m:.1f}",
            "Guida scorrevole": "Si" if spec.guida_superiore_scorrimento else "No",
            "Impianti integrati": "Si" if spec.impianti_integrati else "No",
        },
        "slu": risultato.to_dict()["slu"],
        "sle": risultato.to_dict()["sle"],
        "passaggi": list(risultato.passaggi_calcolo),
    }


def export_markdown(risultato: RisultatoTramezzo) -> str:
    data = adatta_per_report(risultato)
    rows_input = "\n".join(f"| {key} | {value} |" for key, value in data["input"].items())
    rows_slu = "\n".join(f"| {key} | {value} |" for key, value in data["slu"].items())
    rows_sle = "\n".join(f"| {key} | {value} |" for key, value in data["sle"].items())
    passaggi = "\n".join(f"{index}. {item}" for index, item in enumerate(data["passaggi"], start=1))
    return (
        f"## {data['titolo']}\n\n"
        f"{data['descrizione']}\n\n"
        "### Input\n\n| Parametro | Valore |\n|---|---|\n"
        f"{rows_input}\n\n"
        "### SLU\n\n| Parametro | Valore |\n|---|---|\n"
        f"{rows_slu}\n\n"
        "### SLE\n\n| Parametro | Valore |\n|---|---|\n"
        f"{rows_sle}\n\n"
        "### Passaggi di calcolo\n\n"
        f"{passaggi}\n"
    )
