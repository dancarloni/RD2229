"""
Adattamento dei risultati per report HTML/MD (Fase S1).

Fornisce formattazione, schematizzazione e sezioni dedicate per tabulati di calcolo.
"""

from dataclasses import dataclass
from typing import Optional

from .models import RisultatoTamponamento, StatoDannoSLE


@dataclass
class SezioneReportTamponamento:
    """Sezione di report per un tamponamento."""

    titolo: str
    descrizione: str
    tabella_input: dict
    tabella_slu: dict
    tabella_sle: dict
    immagine_schema: Optional[str] = None  # Path relativo o data URI SVG
    note_tecniche: str = ""


def adatta_per_report(risultato: RisultatoTamponamento) -> SezioneReportTamponamento:
    """
    Converte RisultatoTamponamento in formato report.
    """

    spec = risultato.spec
    slu = risultato.risultato_slu
    sle = risultato.risultato_sle

    # Input e geometria
    tabella_input = {
        "Tipologia": spec.tipologia,
        "Altezza (cm)": f"{spec.altezza_cm:.1f}",
        "Larghezza (cm)": f"{spec.larghezza_cm:.1f}",
        "Spessore (cm)": f"{spec.spessore_cm:.1f}",
        "Massa superficiale (kg/m²)": f"{spec.massa_superficiale_kg_m2:.1f}",
        "Massa totale (kg)": f"{spec.massa_totale_kg():.1f}",
        "Vincolo superiore": spec.vincolo_superiore.value,
        "Vincolo inferiore": spec.vincolo_inferiore.value,
        "Controvento laterale": "Sì" if spec.controvento_laterale else "No",
        "Numero ancoraggi": spec.numero_ancoraggi_totali(),
        "Drift capacita (%)": f"{spec.drift_capacita_perc:.2f}",
    }

    # Verifica SLU
    tabella_slu = {
        "Domanda (kg)": f"{slu.domanda_fuori_piano_kg:.1f}",
        "Resistenza pannello (kg)": f"{slu.resistenza_pannello_kg:.1f}",
        "Resistenza ancoraggi (kg)": f"{slu.resistenza_ancoraggi_kg:.1f}",
        "Rapporto D/R": f"{slu.rapporto_domanda_resistenza:.3f}",
        "Margine di sicurezza (%)": f"{slu.margine_sicurezza_perc:.1f}",
        "Meccanismo critico": slu.meccanismo_critico,
        "Esito": "✓ VERIFICATO" if slu.esito else "✗ NON VERIFICATO",
    }

    # Verifica SLE
    tabella_sle = {
        "Drift calcolato (%)": f"{sle.drift_calcolato_perc:.2f}",
        "Drift capacita (%)": f"{sle.drift_capacita_perc:.2f}",
        "Rapporto drift": f"{sle.rapporto_drift:.3f}",
        "Stato danno": sle.stato_danno.value.upper(),
        "Danno ai giunti": "Sì" if sle.danno_ai_giunti else "No",
        "Danno al pannello": "Sì" if sle.danno_al_pannello else "No",
        "Intervento necessario": "Sì (CRITICO)" if sle.intervento_necessario else "No",
    }

    # Note tecniche
    note_tecniche = (
        f"Analisi secondo NTC2018 §7.2.3 e Circ. 7/2019.\n"
        f"Verifica fuori piano per carico sismico locale.\n"
        f"Classificazione danno su scala 4-livelli.\n"
    )

    if slu.esito and sle.stato_danno != StatoDannoSLE.INSICUREZZA:
        stato_complessivo = "VERIFICATO"
    else:
        stato_complessivo = "NON VERIFICATO"

    note_tecniche += f"\nEsito complessivo: {stato_complessivo}\n"
    note_tecniche += sle.note_sle

    return SezioneReportTamponamento(
        titolo=f"Tamponamento — {spec.tipologia}",
        descrizione=(
            f"Pannello in {spec.tipologia}, {spec.altezza_cm:.0f}×{spec.larghezza_cm:.0f}×{spec.spessore_cm:.0f} cm, "
            f"massa {spec.massa_totale_kg():.0f} kg"
        ),
        tabella_input=tabella_input,
        tabella_slu=tabella_slu,
        tabella_sle=tabella_sle,
        note_tecniche=note_tecniche,
    )


def export_markdown(risultato: RisultatoTamponamento) -> str:
    """
    Esporta risultato in formato Markdown.
    """
    sezione = adatta_per_report(risultato)

    md = f"\n## {sezione.titolo}\n\n"
    md += f"{sezione.descrizione}\n\n"

    # Input
    md += "### Input e geometria\n\n"
    md += "| Parametro | Valore |\n"
    md += "|-----------|--------|\n"
    for k, v in sezione.tabella_input.items():
        md += f"| {k} | {v} |\n"
    md += "\n"

    # SLU
    md += "### Verifica SLU\n\n"
    md += "| Parametro | Valore |\n"
    md += "|-----------|--------|\n"
    for k, v in sezione.tabella_slu.items():
        md += f"| {k} | {v} |\n"
    md += "\n"

    # SLE
    md += "### Verifica SLE\n\n"
    md += "| Parametro | Valore |\n"
    md += "|-----------|--------|\n"
    for k, v in sezione.tabella_sle.items():
        md += f"| {k} | {v} |\n"
    md += "\n"

    # Note
    md += "### Note tecniche\n\n"
    md += sezione.note_tecniche + "\n\n"

    # Passaggi calcolo
    md += "### Passaggi di calcolo\n\n"
    for i, passo in enumerate(risultato.passaggi_calcolo, 1):
        md += f"{i}. {passo}\n"

    return md


def export_html_table(risultato: RisultatoTamponamento) -> str:
    """
    Esporta tabella HTML riepilogativa.
    """
    sezione = adatta_per_report(risultato)

    html = f"\n<section class='tamponamento'>\n"
    html += f"  <h3>{sezione.titolo}</h3>\n"
    html += f"  <p>{sezione.descrizione}</p>\n\n"

    # Risultato complessivo
    esito = "VERIFICATO" if risultato.esito_complessivo() else "NON VERIFICATO"
    html += f"  <div class='esito {esito.lower()}'>{esito}</div>\n\n"

    # Tabella SLU/SLE unificata
    html += "  <table class='risultati'>\n"
    html += "    <tbody>\n"

    # SLU
    html += "      <tr><td colspan='2'><strong>SLU</strong></td></tr>\n"
    for k, v in sezione.tabella_slu.items():
        html += f"      <tr><td>{k}</td><td>{v}</td></tr>\n"

    # SLE
    html += "      <tr><td colspan='2'><strong>SLE</strong></td></tr>\n"
    for k, v in sezione.tabella_sle.items():
        html += f"      <tr><td>{k}</td><td>{v}</td></tr>\n"

    html += "    </tbody>\n"
    html += "  </table>\n"
    html += "\n</section>\n"

    return html
