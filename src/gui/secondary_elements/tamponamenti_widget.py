"""
GUI Qt per Fase S1 — Wizard step-by-step + visualizzatore sezione 2D.

Implementa:
- Wizard multistep per input tamponamento
- Visualizzatore sezione 2D con schema danno
- Integrazione con preset e storage
- Export report HTML/MD

Dipendenze:
- PyQt5/PySide6 per UI
- matplotlib per visualizzazione 2D
"""

import sys
from typing import Optional

try:
    from PyQt5 import QtWidgets
    from PyQt5.QtGui import QFont
    from PyQt5.QtWidgets import (
        QComboBox,
        QDoubleSpinBox,
        QLabel,
        QLineEdit,
        QMainWindow,
        QMessageBox,
        QPushButton,
        QSpinBox,
        QTableWidget,
        QTableWidgetItem,
        QVBoxLayout,
        QWizard,
        QWizardPage,
    )

    BACKEND = "PyQt5"
except ImportError:
    from PySide6 import QtWidgets
    from PySide6.QtGui import QFont
    from PySide6.QtWidgets import (
        QComboBox,
        QDoubleSpinBox,
        QLabel,
        QLineEdit,
        QMainWindow,
        QMessageBox,
        QPushButton,
        QSpinBox,
        QTableWidget,
        QTableWidgetItem,
        QVBoxLayout,
        QWizard,
        QWizardPage,
    )

    BACKEND = "PySide6"

try:
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure

    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

from src.codes.ntc2018.secondary_elements.tamponamenti import (
    ContextoSLE,
    ContextoSLU,
    SpecAncoraggio,
    TamponamentoSpec,
    TipoAncoraggio,
    TipoVincolo,
    export_markdown,
    get_preset,
    lista_preset_disponibili,
    verifica_tamponamento_completa,
)


class WizardPageGeometria(QWizardPage):
    """Pagina 1: input geometria base."""

    def __init__(self):
        super().__init__()
        self.setTitle("Geometria del tamponamento")
        self.setSubTitle("Inserire le dimensioni principali")

        layout = QVBoxLayout()

        # Altezza
        layout.addWidget(QLabel("Altezza (cm):"))
        self.edit_altezza = QDoubleSpinBox()
        self.edit_altezza.setRange(50, 600)
        self.edit_altezza.setValue(300.0)
        layout.addWidget(self.edit_altezza)

        # Larghezza
        layout.addWidget(QLabel("Larghezza (cm):"))
        self.edit_larghezza = QDoubleSpinBox()
        self.edit_larghezza.setRange(50, 600)
        self.edit_larghezza.setValue(400.0)
        layout.addWidget(self.edit_larghezza)

        # Spessore
        layout.addWidget(QLabel("Spessore (cm):"))
        self.edit_spessore = QDoubleSpinBox()
        self.edit_spessore.setRange(5, 50)
        self.edit_spessore.setValue(12.0)
        layout.addWidget(self.edit_spessore)

        # Massa superficiale
        layout.addWidget(QLabel("Massa superficiale (kg/m²):"))
        self.edit_massa = QDoubleSpinBox()
        self.edit_massa.setRange(10, 500)
        self.edit_massa.setValue(240.0)
        layout.addWidget(self.edit_massa)

        layout.addStretch()
        self.setLayout(layout)

        self.registerField("altezza*", self.edit_altezza)
        self.registerField("larghezza*", self.edit_larghezza)
        self.registerField("spessore*", self.edit_spessore)
        self.registerField("massa*", self.edit_massa)


class WizardPageTipologia(QWizardPage):
    """Pagina 2: scelta tipologia e preset."""

    def __init__(self):
        super().__init__()
        self.setTitle("Tipologia material")
        self.setSubTitle("Scegli preset o configura manualmente")

        layout = QVBoxLayout()

        # Preset
        layout.addWidget(QLabel("Carica da preset:"))
        self.combo_preset = QComboBox()
        self.combo_preset.addItem("— Nessuno —")
        for name in lista_preset_disponibili():
            self.combo_preset.addItem(name)
        layout.addWidget(self.combo_preset)

        # Tipologia
        layout.addWidget(QLabel("Tipologia:"))
        self.edit_tipologia = QLineEdit()
        self.edit_tipologia.setText("muratura tradizionale")
        layout.addWidget(self.edit_tipologia)

        # Resistenza compressione
        layout.addWidget(QLabel("Resistenza a compressione (MPa):"))
        self.edit_fc = QDoubleSpinBox()
        self.edit_fc.setRange(0, 50)
        self.edit_fc.setValue(2.5)
        layout.addWidget(self.edit_fc)

        layout.addStretch()
        self.setLayout(layout)

        self.registerField("tipologia*", self.edit_tipologia)
        self.registerField("fc*", self.edit_fc)


class WizardPageVincoli(QWizardPage):
    """Pagina 3: vincoli e controventi."""

    def __init__(self):
        super().__init__()
        self.setTitle("Vincoli e controventi")
        self.setSubTitle("Configurare i vincoli agli estremi")

        layout = QVBoxLayout()

        # Vincolo superiore
        layout.addWidget(QLabel("Vincolo superiore:"))
        self.combo_vincolo_sup = QComboBox()
        for tv in TipoVincolo:
            self.combo_vincolo_sup.addItem(tv.value)
        layout.addWidget(self.combo_vincolo_sup)

        # Vincolo inferiore
        layout.addWidget(QLabel("Vincolo inferiore:"))
        self.combo_vincolo_inf = QComboBox()
        for tv in TipoVincolo:
            self.combo_vincolo_inf.addItem(tv.value)
        layout.addWidget(self.combo_vincolo_inf)

        # Controvento laterale
        self.check_controvento = QtWidgets.QCheckBox("Controvento laterale elastico presente")
        layout.addWidget(self.check_controvento)

        layout.addWidget(QLabel("Rigidezza controvento (kg/cm):"))
        self.edit_k_controvento = QDoubleSpinBox()
        self.edit_k_controvento.setRange(0, 100)
        self.edit_k_controvento.setValue(5.0)
        self.edit_k_controvento.setEnabled(False)
        self.check_controvento.toggled.connect(self.edit_k_controvento.setEnabled)
        layout.addWidget(self.edit_k_controvento)

        layout.addStretch()
        self.setLayout(layout)

        self.registerField("vincolo_sup*", self.combo_vincolo_sup)
        self.registerField("vincolo_inf*", self.combo_vincolo_inf)
        self.registerField("controvento*", self.check_controvento)


class WizardPageAncoraggi(QWizardPage):
    """Pagina 4: configurazione ancoraggi."""

    def __init__(self):
        super().__init__()
        self.setTitle("Ancoraggi")
        self.setSubTitle("Configurare fissaggi (viete, tasselli, saldature)")

        layout = QVBoxLayout()

        # Tabella ancoraggi
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Tipo", "Diametro (mm)", "N° fissaggi", "Resistenza traz. (MPa)", "Interasse (mm)"]
        )
        layout.addWidget(self.table)

        # Bottoni
        btn_add = QPushButton("+ Aggiungi ancoraggio")
        btn_add.clicked.connect(self.add_ancoraggio)
        layout.addWidget(btn_add)

        layout.addStretch()
        self.setLayout(layout)

        # Aggiungi default una riga
        self.add_ancoraggio()

    def add_ancoraggio(self):
        """Aggiungi riga ancoraggio."""
        row = self.table.rowCount()
        self.table.insertRow(row)

        # Tipo combo
        combo = QComboBox()
        for ta in TipoAncoraggio:
            combo.addItem(ta.value)
        self.table.setCellWidget(row, 0, combo)

        # Diametro
        spinbox = QDoubleSpinBox()
        spinbox.setValue(10.0)
        self.table.setCellWidget(row, 1, spinbox)

        # N° fissaggi
        spinbox_n = QSpinBox()
        spinbox_n.setValue(4)
        self.table.setCellWidget(row, 2, spinbox_n)

        # Resistenza
        spinbox_r = QDoubleSpinBox()
        spinbox_r.setValue(400.0)
        self.table.setCellWidget(row, 3, spinbox_r)

        # Interasse
        spinbox_i = QDoubleSpinBox()
        spinbox_i.setValue(100.0)
        self.table.setCellWidget(row, 4, spinbox_i)


class WizardPageDeformabilita(QWizardPage):
    """Pagina 5: deformabilità e capacità."""

    def __init__(self):
        super().__init__()
        self.setTitle("Deformabilità")
        self.setSubTitle("Proprietà di compatibilità sismica")

        layout = QVBoxLayout()

        # Drift capacity
        layout.addWidget(QLabel("Drift capacity (% altezza):"))
        self.edit_drift = QDoubleSpinBox()
        self.edit_drift.setRange(0.1, 5.0)
        self.edit_drift.setValue(1.5)
        layout.addWidget(self.edit_drift)

        # Aperture
        layout.addWidget(QLabel("Area aperture (cm²):"))
        self.edit_aperture_area = QDoubleSpinBox()
        self.edit_aperture_area.setRange(0, 100000)
        self.edit_aperture_area.setValue(0)
        layout.addWidget(self.edit_aperture_area)

        layout.addWidget(QLabel("Numero aperture:"))
        self.edit_num_aperture = QSpinBox()
        self.edit_num_aperture.setRange(0, 10)
        self.edit_num_aperture.setValue(0)
        layout.addWidget(self.edit_num_aperture)

        layout.addStretch()
        self.setLayout(layout)

        self.registerField("drift*", self.edit_drift)


class WizardPageCarichi(QWizardPage):
    """Pagina 6: carichi sismici."""

    def __init__(self):
        super().__init__()
        self.setTitle("Carichi sismici")
        self.setSubTitle("Parametri dell'azione sismica")

        layout = QVBoxLayout()

        # Accelerazione spettrale
        layout.addWidget(QLabel("Accelerazione spettrale S_a (g):"))
        self.edit_sa = QDoubleSpinBox()
        self.edit_sa.setRange(0.1, 5.0)
        self.edit_sa.setValue(2.0)
        layout.addWidget(self.edit_sa)

        # Accelerazione progettuale
        layout.addWidget(QLabel("Accelerazione progettuale a_g (g):"))
        self.edit_ag = QDoubleSpinBox()
        self.edit_ag.setRange(0.05, 1.0)
        self.edit_ag.setValue(0.3)
        layout.addWidget(self.edit_ag)

        # Drift calcolato
        layout.addWidget(QLabel("Drift calcolato (% altezza):"))
        self.edit_drift_calc = QDoubleSpinBox()
        self.edit_drift_calc.setRange(0, 5.0)
        self.edit_drift_calc.setValue(0.5)
        layout.addWidget(self.edit_drift_calc)

        layout.addStretch()
        self.setLayout(layout)

        self.registerField("sa*", self.edit_sa)
        self.registerField("ag*", self.edit_ag)
        self.registerField("drift_calc*", self.edit_drift_calc)


class TamponamentoWizard(QWizard):
    """Wizard multistep per configurazione tamponamento."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Wizard — Verifiche Tamponamenti (Fase S1)")
        self.setWizardStyle(QWizard.ModernStyle)
        self.setMinimumWidth(600)

        self.addPage(WizardPageGeometria())
        self.addPage(WizardPageTipologia())
        self.addPage(WizardPageVincoli())
        self.addPage(WizardPageAncoraggi())
        self.addPage(WizardPageDeformabilita())
        self.addPage(WizardPageCarichi())

    def get_spec(self) -> TamponamentoSpec:
        """Estrai TamponamentoSpec dai valori del wizard."""

        # Pagina 1
        altezza = self.field("altezza")
        larghezza = self.field("larghezza")
        spessore = self.field("spessore")
        massa = self.field("massa")

        # Pagina 2
        tipologia = self.field("tipologia")
        fc = self.field("fc")

        # Pagina 3
        vincolo_sup_str = self.field("vincolo_sup")
        vincolo_inf_str = self.field("vincolo_inf")
        controvento = self.field("controvento")

        # Vincoli enum
        vincolo_sup = TipoVincolo(vincolo_sup_str)
        vincolo_inf = TipoVincolo(vincolo_inf_str)

        # Pagina 4 — ancoraggi
        pages = self.widget(3)
        ancoraggi = []
        for row in range(pages.table.rowCount()):
            tipo_str = pages.table.cellWidget(row, 0).currentText()
            diametro = pages.table.cellWidget(row, 1).value()
            n_fissaggi = pages.table.cellWidget(row, 2).value()
            resistenza = pages.table.cellWidget(row, 3).value()
            interasse = pages.table.cellWidget(row, 4).value()

            tipo = TipoAncoraggio(tipo_str)
            ank = SpecAncoraggio(
                tipo=tipo,
                diametro_mm=diametro,
                materiale="acciaio/resina",
                resistenza_trazione_mpa=resistenza,
                resistenza_taglio_mpa=resistenza * 0.6,  # Approssimazione
                numero_fissaggi=n_fissaggi,
                interasse_mm=interasse if tipo == TipoAncoraggio.VITE_METALLO else None,
            )
            ancoraggi.append(ank)

        # Pagina 5
        drift_cap = self.field("drift")
        aperture_area = pages.edit_aperture_area.value()
        num_aperture = pages.edit_num_aperture.value()

        # Pagina 6
        # (verranno usate per ContextoSLU/SLE alla verifica)

        return TamponamentoSpec(
            altezza_cm=altezza,
            larghezza_cm=larghezza,
            spessore_cm=spessore,
            massa_superficiale_kg_m2=massa,
            tipologia=tipologia,
            resistenza_compressione_mpa=fc,
            vincolo_superiore=vincolo_sup,
            vincolo_inferiore=vincolo_inf,
            controvento_laterale=controvento,
            ancoraggi=ancoraggi,
            drift_capacita_perc=drift_cap,
            area_aperture_cm2=aperture_area,
            numero_aperture=num_aperture,
        )


class VisualizzatoreDanno2D:
    """Visualizzatore sezione 2D con schema danno (matplotlib)."""

    def __init__(self, spec: TamponamentoSpec, stato_danno_str: str):
        self.spec = spec
        self.stato_danno = stato_danno_str

    def genera_figura(self) -> Optional["Figure"]:
        """Genera figura matplotlib con schema pannello + danno."""

        if not HAS_MATPLOTLIB:
            return None

        fig = Figure(figsize=(8, 6))
        ax = fig.add_subplot(111)

        # Disegna rettangolo pannello
        from matplotlib.patches import Rectangle

        # Altezza e larghezza normalizzate
        h_norm = self.spec.altezza_cm
        w_norm = self.spec.larghezza_cm

        # Bordo principale
        rect_main = Rectangle(
            (0, 0), w_norm, h_norm, linewidth=2, edgecolor="black", facecolor="lightgray", alpha=0.3
        )
        ax.add_patch(rect_main)

        # Sovrapposizione danno
        if self.stato_danno == "locale":
            # Danno ai bordi (gialli)
            rect_danno = Rectangle(
                (0, h_norm * 0.9),
                w_norm,
                h_norm * 0.1,
                linewidth=1,
                edgecolor="orange",
                facecolor="yellow",
                alpha=0.5,
            )
            ax.add_patch(rect_danno)
        elif self.stato_danno == "diffuso":
            # Danno diffuso (arancio)
            rect_danno = Rectangle(
                (0, 0), w_norm, h_norm, linewidth=2, edgecolor="red", facecolor="orange", alpha=0.3
            )
            ax.add_patch(rect_danno)
        elif self.stato_danno == "insicurezza":
            # Rischio espulsione (rosso scuro)
            rect_danno = Rectangle(
                (0, 0), w_norm, h_norm, linewidth=3, edgecolor="darkred", facecolor="red", alpha=0.4
            )
            ax.add_patch(rect_danno)

        # Etichette vincoli
        ax.text(w_norm / 2, -10, self.spec.vincolo_inferiore.value, ha="center", fontsize=9)
        ax.text(w_norm / 2, h_norm + 10, self.spec.vincolo_superiore.value, ha="center", fontsize=9)

        # Legenda stato danno
        stato_label = {
            "assente": "Nessun danno",
            "locale": "Danno localizzato ai giunti",
            "diffuso": "Danno diffuso",
            "insicurezza": "CRITICO: Rischio espulsione",
        }
        ax.text(
            w_norm / 2,
            -30,
            f"Stato: {stato_label.get(self.stato_danno, '?')}",
            ha="center",
            fontsize=10,
            fontweight="bold",
            color="red" if self.stato_danno == "insicurezza" else "black",
        )

        ax.set_xlim(-50, w_norm + 50)
        ax.set_ylim(-50, h_norm + 50)
        ax.set_aspect("equal")
        ax.axis("off")

        fig.tight_layout()
        return fig


class FinestraRisultati(QtWidgets.QWidget):
    """Finestra di visualizzazione risultati."""

    def __init__(self, risultato):
        super().__init__()
        self.risultato = risultato
        self.init_ui()

    def init_ui(self):
        """Costruisci UI risultati."""

        layout = QVBoxLayout()

        # Titolo
        title = QLabel(f"Risultati — {self.risultato.spec.tipologia}")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)

        # Tabella SLU
        layout.addWidget(QLabel("SLU (Stato Limite Ultimo):"))
        table_slu = QTableWidget()
        table_slu.setRowCount(4)
        table_slu.setColumnCount(2)
        slu = self.risultato.risultato_slu
        table_slu.setItem(0, 0, QTableWidgetItem("Domanda (kg)"))
        table_slu.setItem(0, 1, QTableWidgetItem(f"{slu.domanda_fuori_piano_kg:.1f}"))
        table_slu.setItem(1, 0, QTableWidgetItem("Resistenza (kg)"))
        table_slu.setItem(1, 1, QTableWidgetItem(f"{slu.resistenza_pannello_kg:.1f}"))
        table_slu.setItem(2, 0, QTableWidgetItem("Rapporto D/R"))
        table_slu.setItem(2, 1, QTableWidgetItem(f"{slu.rapporto_domanda_resistenza:.3f}"))
        table_slu.setItem(3, 0, QTableWidgetItem("Esito"))
        table_slu.setItem(
            3, 1, QTableWidgetItem("✓ VERIFICATO" if slu.esito else "✗ NON VERIFICATO")
        )
        layout.addWidget(table_slu)

        # Tabella SLE
        layout.addWidget(QLabel("SLE (Stato Limite di Esercizio):"))
        table_sle = QTableWidget()
        table_sle.setRowCount(4)
        table_sle.setColumnCount(2)
        sle = self.risultato.risultato_sle
        table_sle.setItem(0, 0, QTableWidgetItem("Stato danno"))
        table_sle.setItem(0, 1, QTableWidgetItem(sle.stato_danno.value.upper()))
        table_sle.setItem(1, 0, QTableWidgetItem("Drift calcolato (%)"))
        table_sle.setItem(1, 1, QTableWidgetItem(f"{sle.drift_calcolato_perc:.2f}"))
        table_sle.setItem(2, 0, QTableWidgetItem("Drift capacità (%)"))
        table_sle.setItem(2, 1, QTableWidgetItem(f"{sle.drift_capacita_perc:.2f}"))
        table_sle.setItem(3, 0, QTableWidgetItem("Intervento necessario"))
        table_sle.setItem(3, 1, QTableWidgetItem("Sì" if sle.intervento_necessario else "No"))
        layout.addWidget(table_sle)

        # Disegno sezione 2D
        if HAS_MATPLOTLIB:
            layout.addWidget(QLabel("Schema sezione:"))
            visualizzatore = VisualizzatoreDanno2D(self.risultato.spec, sle.stato_danno.value)
            fig = visualizzatore.genera_figura()
            if fig:
                canvas = FigureCanvas(fig)
                layout.addWidget(canvas)

        # Bottoni export
        btn_export_md = QPushButton("Esporta Markdown")
        btn_export_md.clicked.connect(self.export_markdown)
        layout.addWidget(btn_export_md)

        layout.addStretch()
        self.setLayout(layout)

    def export_markdown(self):
        """Esporta risultato in Markdown."""
        md_text = export_markdown(self.risultato)

        filepath, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Salva report", "", "Markdown (*.md);;Tutti (*)"
        )

        if filepath:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(md_text)
            QMessageBox.information(self, "Successo", f"Report salvato in {filepath}")


class MainWindow(QMainWindow):
    """Finestra principale applicazione."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fase S1 — Verifiche Tamponamenti Secondari")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Fase S1 — Tamponamenti Secondari (NTC2018 §7.2.3)"))

        # Bottone avvia wizard
        btn_wizard = QPushButton("Avvia wizard di calcolo")
        btn_wizard.clicked.connect(self.open_wizard)
        layout.addWidget(btn_wizard)

        # Bottone carica preset
        btn_preset = QPushButton("Carica preset")
        btn_preset.clicked.connect(self.load_preset)
        layout.addWidget(btn_preset)

        layout.addStretch()

        container = QtWidgets.QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def open_wizard(self):
        """Apri wizard."""
        wizard = TamponamentoWizard(self)
        if wizard.exec_() == QWizard.Accepted:
            spec = wizard.get_spec()

            # Estrai contesti dalle ultime pagine
            sa = wizard.field("sa")
            ag = wizard.field("ag")
            drift_calc = wizard.field("drift_calc")

            contesto_slu = ContextoSLU(
                accelerazione_spettrale_mg=sa,
                accelerazione_progettuale_g=ag,
            )

            contesto_sle = ContextoSLE(
                drift_calcolato_perc=drift_calc,
            )

            # Verifica
            risultato = verifica_tamponamento_completa(spec, contesto_slu, contesto_sle)

            # Mostra risultati
            finestra_risultati = FinestraRisultati(risultato)
            finestra_risultati.show()
            self.window = finestra_risultati

    def load_preset(self):
        """Carica un preset e visualizzalo."""
        lista = lista_preset_disponibili()
        if not lista:
            QMessageBox.warning(self, "Attenzione", "Nessun preset disponibile")
            return

        preset_name, ok = QtWidgets.QInputDialog.getItem(
            self, "Carica preset", "Scegli preset:", lista, 0, False
        )

        if ok and preset_name:
            spec = get_preset(preset_name)
            if spec:
                QMessageBox.information(self, "Preset caricato", f"Preset {preset_name} caricato")
            else:
                QMessageBox.warning(self, "Errore", f"Impossibile caricare preset {preset_name}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_() if BACKEND == "PyQt5" else app.exec())
