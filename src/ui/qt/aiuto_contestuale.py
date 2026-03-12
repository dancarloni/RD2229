"""Aiuto Contestuale Dinamico (Qt6).

Finestra di aiuto sensibile al contesto che fornisce:
- Spiegazione della funzionalità del modulo corrente
- Formule utilizzate con significato dei simboli
- Citazioni testuali della normativa (articolo, comma, tabella)
- Passaggi teorici pertinenti
- Esempi numerici di riferimento

L'aiuto viene caricato da file YAML per modulo in docs/help/modulo_xxx.yaml.
Invocabile con F1 o bottone ? da qualsiasi schermata.

Esempio file YAML (docs/help/flessione_ntc2018.yaml)::

    titolo: "Verifica a flessione — NTC2018 SLU"
    modulo: flessione_ntc2018
    normativa:
      - riferimento: "NTC2018 §4.1.2.1.3.2"
        testo: "La resistenza a flessione deve essere calcolata..."
      - riferimento: "Circ. 7/2019 §C4.1.2.1.3.2"
        testo: "Si precisa che il momento resistente..."
    formule:
      - nome: "Momento resistente"
        formula: "M_Rd = A_s × f_yd × (d - 0.4x)"
        simboli:
          A_s: "Area armatura tesa [cm²]"
          f_yd: "Resistenza di calcolo acciaio [kg/cm²]"
          d: "Altezza utile sezione [cm]"
          x: "Profondità asse neutro [cm]"
    parametri:
      - nome: "A_s"
        descrizione: "Area armatura longitudinale tesa"
        unita: "cm²"
        tooltip: "Area totale delle barre di armatura..."
    esempio:
      titolo: "Trave rettangolare 30×50"
      passaggi:
        - "Dati: b=30cm, h=50cm, d=46cm, A_s=6.28cm²"
        - "f_yd = f_yk/γ_s = 4500/1.15 = 3913 kg/cm²"
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import QScrollArea  # noqa: F401
    from PyQt6.QtWidgets import QLabel, QSizePolicy, QTextEdit, QVBoxLayout, QWidget
except ImportError:  # pragma: no cover
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QLabel, QSizePolicy, QTextEdit, QVBoxLayout, QWidget

logger = logging.getLogger(__name__)

# Percorso base per i file di aiuto YAML
_PERCORSO_HELP = Path(__file__).resolve().parents[2] / "docs" / "help"


def carica_help_yaml(nome_modulo: str) -> dict[str, Any] | None:
    """Carica il file YAML di aiuto per un modulo specifico.

    Parametri:
        nome_modulo: Nome del modulo (es. "flessione_ntc2018").
                     Corrisponde al file docs/help/{nome_modulo}.yaml.

    Restituisce:
        Dizionario con i contenuti dell'help, o None se non trovato.
    """
    percorso = _PERCORSO_HELP / f"{nome_modulo}.yaml"
    if not percorso.exists():
        logger.debug("File help non trovato: %s", percorso)
        return None

    try:
        import yaml

        with open(percorso, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except ImportError:
        # Fallback: leggi come testo se PyYAML non disponibile
        logger.warning("PyYAML non installato — help contestuale limitato")
        return _carica_help_testo(percorso)
    except Exception as e:
        logger.error("Errore caricamento help %s: %s", percorso, e)
        return None


def _carica_help_testo(percorso: Path) -> dict[str, Any]:
    """Caricamento fallback: legge il file come testo semplice."""
    with open(percorso, encoding="utf-8") as f:
        contenuto = f.read()
    return {"titolo": percorso.stem, "testo_grezzo": contenuto}


def genera_html_help(dati_help: dict[str, Any], contesto: dict[str, Any] | None = None) -> str:
    """Genera HTML formattato dai dati di help.

    Parametri:
        dati_help: Dizionario dal file YAML dell'help.
        contesto: Informazioni contestuali dalla finestra corrente
                  (parametri visualizzati, valori inseriti, etc.).

    Restituisce:
        Stringa HTML pronta per la visualizzazione.
    """
    html_parti = []

    # Titolo
    titolo = dati_help.get("titolo", "Aiuto")
    html_parti.append(f"<h2>{_escape(titolo)}</h2>")

    # Descrizione
    descrizione = dati_help.get("descrizione", "")
    if descrizione:
        html_parti.append(f"<p>{_escape(descrizione)}</p>")

    # Testo grezzo (fallback senza PyYAML)
    testo_grezzo = dati_help.get("testo_grezzo", "")
    if testo_grezzo:
        html_parti.append(f"<pre>{_escape(testo_grezzo)}</pre>")
        return "\n".join(html_parti)

    # Riferimenti normativi
    normative = dati_help.get("normativa", [])
    if normative:
        html_parti.append("<h3>📋 Riferimenti Normativi</h3>")
        for norma in normative:
            rif = norma.get("riferimento", "")
            testo = norma.get("testo", "")
            html_parti.append(
                f'<div style="margin-left:16px; margin-bottom:8px;">'
                f"<b>{_escape(rif)}</b><br>"
                f'<i>"{_escape(testo)}"</i></div>'
            )

    # Formule
    formule = dati_help.get("formule", [])
    if formule:
        html_parti.append("<h3>📐 Formule</h3>")
        for formula_info in formule:
            nome = formula_info.get("nome", "")
            formula = formula_info.get("formula", "")
            html_parti.append(
                f'<div style="margin-left:16px; margin-bottom:12px;">'
                f"<b>{_escape(nome)}</b><br>"
                f'<code style="font-size:13px; background:#f0f0f0; padding:4px 8px; '
                f'border-radius:4px;">{_escape(formula)}</code>'
            )
            # Simboli
            simboli = formula_info.get("simboli", {})
            if simboli:
                html_parti.append('<table style="margin-left:8px; margin-top:4px;">')
                for sim, desc in simboli.items():
                    html_parti.append(
                        f'<tr><td style="padding-right:12px;">'
                        f"<code>{_escape(sim)}</code></td>"
                        f"<td>{_escape(desc)}</td></tr>"
                    )
                html_parti.append("</table>")
            html_parti.append("</div>")

    # Parametri (con tooltip)
    parametri = dati_help.get("parametri", [])
    if parametri:
        html_parti.append("<h3>📊 Parametri</h3>")
        html_parti.append(
            '<table border="1" cellpadding="4" cellspacing="0" '
            'style="border-collapse:collapse; margin-left:16px;">'
        )
        html_parti.append(
            '<tr style="background:#e0e0e0;">'
            "<th>Parametro</th><th>Descrizione</th><th>Unità</th></tr>"
        )
        for param in parametri:
            html_parti.append(
                f'<tr><td><code>{_escape(param.get("nome", ""))}</code></td>'
                f'<td>{_escape(param.get("descrizione", ""))}</td>'
                f'<td>{_escape(param.get("unita", ""))}</td></tr>'
            )
        html_parti.append("</table>")

    # Esempio numerico
    esempio = dati_help.get("esempio", {})
    if esempio:
        html_parti.append("<h3>📝 Esempio numerico</h3>")
        titolo_es = esempio.get("titolo", "")
        if titolo_es:
            html_parti.append(f"<p><b>{_escape(titolo_es)}</b></p>")
        passaggi_es = esempio.get("passaggi", [])
        if passaggi_es:
            html_parti.append('<ol style="margin-left:16px;">')
            for passo in passaggi_es:
                html_parti.append(f"<li>{_escape(passo)}</li>")
            html_parti.append("</ol>")

    # Contesto corrente (se disponibile)
    if contesto:
        html_parti.append("<h3>🔧 Contesto corrente</h3>")
        html_parti.append(
            '<table border="1" cellpadding="4" cellspacing="0" '
            'style="border-collapse:collapse; margin-left:16px;">'
        )
        for chiave, valore in contesto.items():
            html_parti.append(
                f"<tr><td><b>{_escape(str(chiave))}</b></td>"
                f"<td>{_escape(str(valore))}</td></tr>"
            )
        html_parti.append("</table>")

    return "\n".join(html_parti)


class AiutoContestualeWidget(QWidget):
    """Widget per la visualizzazione dell'aiuto contestuale.

    Può essere aperto come finestra separata o come pannello laterale.

    Parametri:
        nome_modulo: Nome del modulo per cui mostrare l'aiuto.
        contesto: Dizionario con dati contestuali dalla finestra corrente.
        parent: Widget genitore Qt.
    """

    def __init__(
        self,
        nome_modulo: str = "",
        contesto: dict[str, Any] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"Aiuto — {nome_modulo or 'Generale'}")
        self.setMinimumSize(600, 400)
        self._nome_modulo = nome_modulo
        self._contesto = contesto or {}
        self._inizializza_interfaccia()
        self._carica_contenuto()

    def _inizializza_interfaccia(self) -> None:
        """Crea l'interfaccia del widget di aiuto."""
        layout = QVBoxLayout(self)

        # Intestazione
        self._etichetta_titolo = QLabel()
        self._etichetta_titolo.setStyleSheet("font-size: 16px; font-weight: bold; padding: 8px;")
        layout.addWidget(self._etichetta_titolo)

        # Area contenuto (scroll)
        self._area_contenuto = QTextEdit()
        self._area_contenuto.setReadOnly(True)
        self._area_contenuto.setStyleSheet(
            "QTextEdit { background-color: #FAFAFA; border: 1px solid #DDD; " "padding: 8px; }"
        )
        layout.addWidget(self._area_contenuto)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def _carica_contenuto(self) -> None:
        """Carica e visualizza il contenuto dell'help."""
        if not self._nome_modulo:
            self._mostra_help_generico()
            return

        dati = carica_help_yaml(self._nome_modulo)
        if dati:
            self._etichetta_titolo.setText(dati.get("titolo", self._nome_modulo))
            html = genera_html_help(dati, self._contesto)
            self._area_contenuto.setHtml(html)
        else:
            self._mostra_help_non_disponibile()

    def _mostra_help_generico(self) -> None:
        """Mostra un messaggio di aiuto generico."""
        self._etichetta_titolo.setText("Aiuto — RD2229 Calcolo Strutturale")
        self._area_contenuto.setHtml(
            "<h3>Benvenuto nell'aiuto di RD2229</h3>"
            "<p>Premi <b>F1</b> o il bottone <b>?</b> in qualsiasi modulo "
            "per ottenere aiuto contestuale specifico.</p>"
            "<p>L'aiuto mostra:</p>"
            "<ul>"
            "<li>Riferimenti normativi con citazioni testuali</li>"
            "<li>Formule utilizzate con significato dei simboli</li>"
            "<li>Parametri con descrizione e unità di misura</li>"
            "<li>Esempi numerici di riferimento</li>"
            "<li>Contesto corrente (dati inseriti, parametri attivi)</li>"
            "</ul>"
        )

    def _mostra_help_non_disponibile(self) -> None:
        """Mostra messaggio quando l'help non è disponibile per il modulo."""
        self._etichetta_titolo.setText(f"Aiuto — {self._nome_modulo}")
        self._area_contenuto.setHtml(
            f"<p>Aiuto non ancora disponibile per il modulo "
            f"<b>{_escape(self._nome_modulo)}</b>.</p>"
            f"<p>Il file di aiuto verrà creato in:<br>"
            f"<code>docs/help/{_escape(self._nome_modulo)}.yaml</code></p>"
        )

    def aggiorna_contesto(self, contesto: dict[str, Any]) -> None:
        """Aggiorna il contesto e ricarica il contenuto.

        Parametri:
            contesto: Nuovo dizionario di contesto dalla finestra corrente.
        """
        self._contesto = contesto
        self._carica_contenuto()


def apri_aiuto(
    nome_modulo: str = "",
    contesto: dict[str, Any] | None = None,
    parent: QWidget | None = None,
) -> AiutoContestualeWidget:
    """Apre la finestra di aiuto contestuale.

    Funzione di comodità per aprire l'aiuto da qualsiasi punto del software.

    Parametri:
        nome_modulo: Nome del modulo corrente.
        contesto: Dati contestuali (parametri visualizzati, valori, etc.).
        parent: Widget genitore Qt.

    Restituisce:
        L'istanza del widget di aiuto creata.
    """
    widget = AiutoContestualeWidget(
        nome_modulo=nome_modulo,
        contesto=contesto,
        parent=parent,
    )
    widget.setWindowFlags(Qt.WindowType.Window)  # Finestra separata
    widget.show()
    return widget


def _escape(testo: str) -> str:
    """Escapa caratteri speciali HTML."""
    return testo.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


MODULE_SPEC = {
    "key": "aiuto_contestuale",
    "name": "Aiuto Contestuale",
    "description": "Aiuto dinamico sensibile al contesto con riferimenti normativi e formule (Qt6)",
}


def create_module(master: QWidget | None = None, **context: Any) -> AiutoContestualeWidget:
    """Factory per il modulo selettore."""
    return AiutoContestualeWidget(parent=master)
