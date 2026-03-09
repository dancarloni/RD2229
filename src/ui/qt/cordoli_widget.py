"""GUI Qt — Cordoli Metallici, CA e Reticolari.

Widget embeddabile (QWidget) per la verifica di cordoli in muratura:
- Metallico: profilo singolo EN 10365 (IPE/HEA/HEB/HEM/UPN/CUSTOM)
- CA: calcestruzzo armato con verifiche NTC2018 §7.8.1.6
- Reticolare: traliccio piano Howe/Pratt

Struttura tab:
  Tab 1 — Selezione / Parametri  (metallico: tabella profili; CA/Reticolare: form completo)
  Tab 2 — Visualizzazione sezione (QPainter custom)
  Tab 3 — Sollecitazioni          (solo per tipo Metallico)
  Tab 4 — Output verifiche        (ASCII + esporta HTML)

Unita': cm geometria, kg forze, kg/cm² tensioni.
"""

from __future__ import annotations

from pathlib import Path

try:
    from PyQt6.QtCore import QPointF, QRectF, Qt
    from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPen
    from PyQt6.QtWidgets import (
        QComboBox,
        QDoubleSpinBox,
        QFileDialog,
        QFormLayout,
        QFrame,
        QGroupBox,
        QHBoxLayout,
        QHeaderView,
        QLabel,
        QLineEdit,
        QMessageBox,
        QPushButton,
        QScrollArea,
        QSizePolicy,
        QSpinBox,
        QStackedWidget,
        QTableWidget,
        QTableWidgetItem,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
    _PYQT6 = True
except ImportError:
    from PySide6.QtCore import QPointF, QRectF, Qt  # type: ignore[no-redef]
    from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen  # type: ignore[no-redef]
    from PySide6.QtWidgets import (  # type: ignore[no-redef]
        QComboBox,
        QDoubleSpinBox,
        QFileDialog,
        QFormLayout,
        QFrame,
        QGroupBox,
        QHBoxLayout,
        QHeaderView,
        QLabel,
        QLineEdit,
        QMessageBox,
        QPushButton,
        QScrollArea,
        QSizePolicy,
        QSpinBox,
        QStackedWidget,
        QTableWidget,
        QTableWidgetItem,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
    _PYQT6 = False

from src.elements.cordolo import (
    Cordolo,
    CordoloCA,
    CordoloMetallico,
    PosizioneCordolo,
    TipoCordolo,
    verifica_cordolo,
)
from src.elements.cordolo_reticolare import (
    CordoloReticolare,
    SchemaReticolare,
    verifica_cordolo_reticolare,
)
from src.report.tabulati_calcolo import TabulatoCalcolo
from src.steel.sagomario import ProfiloAcciaio, SagomarioAcciaio
from src.steel.sezione_asta import SezioneAsta
from src.steel.verifiche_ta import SIGMA_ADM_TA

try:
    from src.core.registro_log import registro as _registro
except ImportError:
    _registro = None


# ── Costanti ─────────────────────────────────────────────────────────────────

_TIPI_CORDOLO = ["Metallico", "CA", "Reticolare"]
_TIPI_ACCIAIO = ["Fe360", "Fe430", "Fe510", "S235", "S275", "S355"]
_SCHEMI_RETICOLARI = ["Howe", "Pratt"]
_POSIZIONI = ["sommitale", "intermedio", "fondazione"]
_POSIZIONE_MAP = {
    "sommitale": PosizioneCordolo.SOMMITALE,
    "intermedio": PosizioneCordolo.INTERMEDIO,
    "fondazione": PosizioneCordolo.FONDAZIONE,
}


# ── _SezioneVisualizzatore ────────────────────────────────────────────────────

class _SezioneVisualizzatore(QWidget):
    """Disegno QPainter della sezione trasversale del cordolo."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._tipo = "placeholder"
        self._profilo: ProfiloAcciaio | None = None
        self._ca_params: dict = {}
        self._ret_params: dict = {}
        self.setMinimumSize(280, 200)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

    def aggiorna_metallico(self, profilo: ProfiloAcciaio | None) -> None:
        self._tipo = "metallico"
        self._profilo = profilo
        self.update()

    def aggiorna_ca(
        self, b: float, h: float, n_sup: int, n_inf: int,
        phi_long: float, c: float,
    ) -> None:
        self._tipo = "ca"
        self._ca_params = {"b": b, "h": h, "n_sup": n_sup, "n_inf": n_inf,
                           "phi_long": phi_long, "c": c}
        self.update()

    def aggiorna_reticolare(
        self, L: float, h: float, n_campate: int, schema: str,
    ) -> None:
        self._tipo = "reticolare"
        self._ret_params = {"L": L, "h": h, "n_campate": n_campate, "schema": schema}
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(250, 250, 252))

        margin = 35
        w = self.width() - 2 * margin
        h_widget = self.height() - 2 * margin

        if self._tipo == "metallico" and self._profilo:
            self._disegna_metallico(painter, margin, w, h_widget)
        elif self._tipo == "ca" and self._ca_params:
            self._disegna_ca(painter, margin, w, h_widget)
        elif self._tipo == "reticolare" and self._ret_params:
            self._disegna_reticolare(painter, margin, w, h_widget)
        else:
            painter.setPen(QColor(160, 160, 160))
            painter.setFont(QFont("Arial", 10))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter,
                             "Selezionare un profilo")
        painter.end()

    def _disegna_metallico(
        self, painter: QPainter, margin: int, area_w: int, area_h: int,
    ) -> None:
        p = self._profilo
        if p is None:
            return
        scala = min(area_w / max(p.b, 0.1), area_h / max(p.h, 0.1)) * 0.85
        ox = margin + (area_w - p.b * scala) / 2
        oy = margin + (area_h - p.h * scala) / 2

        fill = QColor(140, 140, 155)
        border = QPen(QColor(60, 60, 80), 1)
        painter.setPen(border)
        painter.setBrush(QBrush(fill))

        # Ala inferiore
        painter.drawRect(QRectF(ox, oy + (p.h - p.tf) * scala,
                                p.b * scala, p.tf * scala))
        # Ala superiore
        painter.drawRect(QRectF(ox, oy, p.b * scala, p.tf * scala))
        # Anima
        x_anima = ox + (p.b - p.tw) / 2 * scala
        painter.drawRect(QRectF(x_anima, oy + p.tf * scala,
                                p.tw * scala, (p.h - 2 * p.tf) * scala))

        # Etichette
        painter.setPen(QColor(40, 40, 40))
        painter.setFont(QFont("Arial", 8))
        cx = self.width() / 2
        # h= (verticale a sinistra)
        painter.save()
        painter.translate(margin - 10, oy + p.h * scala / 2)
        painter.rotate(-90)
        painter.drawText(QRectF(-40, -10, 80, 20), Qt.AlignmentFlag.AlignCenter,
                         f"h={p.h:.0f}")
        painter.restore()
        # b= (sopra)
        painter.drawText(QRectF(cx - 30, oy - 18, 60, 16),
                         Qt.AlignmentFlag.AlignCenter, f"b={p.b:.0f}")
        # tw=
        x_label = x_anima + p.tw * scala / 2
        painter.drawText(QRectF(x_label - 20, oy + p.h * scala / 2 - 8, 40, 16),
                         Qt.AlignmentFlag.AlignCenter, f"tw={p.tw:.2f}")

    def _disegna_ca(
        self, painter: QPainter, margin: int, area_w: int, area_h: int,
    ) -> None:
        d = self._ca_params
        b, h = d["b"], d["h"]
        if b <= 0 or h <= 0:
            return
        scala = min(area_w / b, area_h / h) * 0.85
        ox = margin + (area_w - b * scala) / 2
        oy = margin + (area_h - h * scala) / 2

        # Sezione cls
        painter.setPen(QPen(QColor(80, 80, 80), 1))
        painter.setBrush(QBrush(QColor(200, 200, 200)))
        painter.drawRect(QRectF(ox, oy, b * scala, h * scala))

        # Armatura
        phi = d["phi_long"]
        c = d["c"]
        r_px = max(phi * scala / 2, 3.0)
        painter.setBrush(QBrush(QColor(30, 30, 30)))
        painter.setPen(QPen(QColor(0, 0, 0), 1))

        n_sup = min(d["n_sup"], 4)
        n_inf = min(d["n_inf"], 4)
        y_sup = oy + (c + phi / 2) * scala
        y_inf = oy + (h - c - phi / 2) * scala

        for row_n, y_barre in [(n_sup, y_sup), (n_inf, y_inf)]:
            if row_n <= 0:
                continue
            spacing = (b - 2 * c) / max(row_n - 1, 1) if row_n > 1 else 0.0
            for i in range(row_n):
                x_barra = ox + (c + i * spacing) * scala
                painter.drawEllipse(
                    QPointF(x_barra, y_barre), r_px, r_px,
                )

        # Etichette
        painter.setPen(QColor(40, 40, 40))
        painter.setFont(QFont("Arial", 8))
        cx = self.width() / 2
        painter.drawText(QRectF(cx - 30, oy - 18, 60, 16),
                         Qt.AlignmentFlag.AlignCenter, f"b={b:.0f}")
        painter.save()
        painter.translate(margin - 10, oy + h * scala / 2)
        painter.rotate(-90)
        painter.drawText(QRectF(-30, -10, 60, 20),
                         Qt.AlignmentFlag.AlignCenter, f"h={h:.0f}")
        painter.restore()

    def _disegna_reticolare(
        self, painter: QPainter, margin: int, area_w: int, area_h: int,
    ) -> None:
        d = self._ret_params
        n = max(d["n_campate"], 2)
        n_show = min(n, 6)  # max 6 pannelli visibili
        schema = d["schema"]

        ox = margin + area_w * 0.05
        oy_top = margin + area_h * 0.2
        oy_bot = margin + area_h * 0.8
        largh = area_w * 0.9
        passo = largh / n_show

        pen_corr = QPen(QColor(60, 100, 160), 3)
        pen_diag = QPen(QColor(160, 80, 40), 2)

        # Correnti
        painter.setPen(pen_corr)
        painter.drawLine(QPointF(ox, oy_top), QPointF(ox + largh, oy_top))
        painter.drawLine(QPointF(ox, oy_bot), QPointF(ox + largh, oy_bot))

        # Montanti e diagonali
        painter.setPen(pen_diag)
        for i in range(n_show):
            x_sx = ox + i * passo
            x_dx = ox + (i + 1) * passo
            # Montante verticale
            painter.drawLine(QPointF(x_sx, oy_top), QPointF(x_sx, oy_bot))
            # Diagonale (Howe: verso il centro; Pratt: verso l'esterno)
            if schema == "Howe":
                painter.drawLine(QPointF(x_sx, oy_bot), QPointF(x_dx, oy_top))
            else:  # Pratt
                painter.drawLine(QPointF(x_sx, oy_top), QPointF(x_dx, oy_bot))
        # Ultimo montante
        painter.drawLine(
            QPointF(ox + n_show * passo, oy_top),
            QPointF(ox + n_show * passo, oy_bot),
        )

        # Etichette
        painter.setPen(QColor(40, 40, 40))
        painter.setFont(QFont("Arial", 8))
        cx = self.width() / 2
        painter.drawText(QRectF(cx - 40, oy_bot + 4, 80, 16),
                         Qt.AlignmentFlag.AlignCenter,
                         f"L={d['L']:.0f} cm  ({n} camp.)")
        painter.save()
        painter.translate(margin - 10, (oy_top + oy_bot) / 2)
        painter.rotate(-90)
        painter.drawText(QRectF(-30, -10, 60, 20),
                         Qt.AlignmentFlag.AlignCenter, f"h={d['h']:.0f}")
        painter.restore()


# ── _TabellaProfiloInfo ───────────────────────────────────────────────────────

class _TabellaProfiloInfo(QWidget):
    """Tabella key-value con le proprieta' geometriche del profilo selezionato."""

    _CAMPI = [
        ("h [cm]", "h"), ("b [cm]", "b"), ("A [cm²]", "A"),
        ("Ix [cm⁴]", "Ix"), ("Wx [cm³]", "Wx"),
        ("Iy [cm⁴]", "Iy"), ("Wy [cm³]", "Wy"),
        ("It [cm⁴]", "It"), ("massa [kg/m]", "massa_kg_m"),
    ]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QFormLayout(self)
        layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        self._labels: dict[str, QLabel] = {}
        for etichetta, attr in self._CAMPI:
            lbl = QLabel("—")
            layout.addRow(etichetta, lbl)
            self._labels[attr] = lbl

    def aggiorna(self, profilo: ProfiloAcciaio | None) -> None:
        for attr, lbl in self._labels.items():
            if profilo is None:
                lbl.setText("—")
            else:
                v = getattr(profilo, attr, 0.0)
                lbl.setText(f"{v:.3g}")


# ── _InputSollecitazioni (pagina Metallico) ───────────────────────────────────

class _InputSollecitazioni(QWidget):
    """Form input sollecitazioni — usato solo per tipo Metallico."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)

        grp = QGroupBox("Sollecitazioni di progetto")
        form = QFormLayout(grp)

        self._combo_acciaio = QComboBox()
        self._combo_acciaio.addItems(_TIPI_ACCIAIO)
        self._combo_acciaio.setCurrentText("Fe430")
        form.addRow("Tipo acciaio:", self._combo_acciaio)

        self._spin_sigma = QDoubleSpinBox()
        self._spin_sigma.setRange(0, 5000)
        self._spin_sigma.setDecimals(0)
        self._spin_sigma.setValue(1900.0)
        self._spin_sigma.setSuffix(" kg/cm²")
        form.addRow("σ_adm:", self._spin_sigma)

        self._spin_M = QDoubleSpinBox()
        self._spin_M.setRange(-1e9, 1e9)
        self._spin_M.setDecimals(0)
        self._spin_M.setSuffix(" kg·cm")
        form.addRow("M (momento):", self._spin_M)

        self._spin_V = QDoubleSpinBox()
        self._spin_V.setRange(-1e7, 1e7)
        self._spin_V.setDecimals(0)
        self._spin_V.setSuffix(" kg")
        form.addRow("V (taglio):", self._spin_V)

        self._spin_N = QDoubleSpinBox()
        self._spin_N.setRange(-1e7, 1e7)
        self._spin_N.setDecimals(0)
        self._spin_N.setSuffix(" kg")
        form.addRow("N (assiale):", self._spin_N)

        self._combo_pos = QComboBox()
        self._combo_pos.addItems(_POSIZIONI)
        form.addRow("Posizione:", self._combo_pos)

        layout.addWidget(grp)
        layout.addStretch()

        # Auto-aggiorna sigma quando cambia tipo acciaio
        self._combo_acciaio.currentTextChanged.connect(self._aggiorna_sigma)

    def _aggiorna_sigma(self, tipo: str) -> None:
        sigma = SIGMA_ADM_TA.get(tipo, 1900.0)
        self._spin_sigma.setValue(sigma)

    def get_input(self) -> dict:
        return {
            "tipo_acciaio": self._combo_acciaio.currentText(),
            "sigma_adm": self._spin_sigma.value(),
            "M": self._spin_M.value(),
            "V": self._spin_V.value(),
            "N": self._spin_N.value(),
            "posizione": self._combo_pos.currentText(),
        }


# ── _OutputVerifiche ──────────────────────────────────────────────────────────

class _OutputVerifiche(QWidget):
    """Tab output: testo ASCII + etichetta esito + esporta HTML."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)

        self._label_esito = QLabel("In attesa di calcolo...")
        self._label_esito.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont("Arial", 14)
        font.setBold(True)
        self._label_esito.setFont(font)
        layout.addWidget(self._label_esito)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(sep)

        self._testo_output = QTextEdit()
        self._testo_output.setReadOnly(True)
        self._testo_output.setFont(QFont("Courier New", 9))
        layout.addWidget(self._testo_output)

        self._btn_html = QPushButton("Esporta HTML...")
        self._btn_html.setEnabled(False)
        self._btn_html.clicked.connect(self._esporta_html)
        layout.addWidget(self._btn_html)

        self._tabulato: TabulatoCalcolo | None = None

    def mostra_risultato(self, tabulato: TabulatoCalcolo, verificato: bool) -> None:
        self._tabulato = tabulato
        self._testo_output.setPlainText(tabulato.come_ascii())
        self._btn_html.setEnabled(True)
        if verificato:
            self._label_esito.setText("VERIFICATO ✓")
            self._label_esito.setStyleSheet("color: #2e7d32; font-weight: bold;")
        else:
            self._label_esito.setText("NON VERIFICATO ✗")
            self._label_esito.setStyleSheet("color: #c62828; font-weight: bold;")

    def _esporta_html(self) -> None:
        if self._tabulato is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Salva relazione HTML", "relazione_cordolo.html", "HTML (*.html)"
        )
        if not path:
            return
        Path(path).write_text(self._tabulato.come_html(), encoding="utf-8")
        if _registro is not None:
            try:
                _registro.operazione(
                    modulo="cordoli_widget",
                    operazione=f"Esportato HTML: {path}",
                )
            except Exception:
                pass
        QMessageBox.information(self, "Esportazione", f"Relazione salvata in:\n{path}")


# ── Pagine form CA e Reticolare ───────────────────────────────────────────────

class _FormCA(QWidget):
    """Form completo per cordolo CA (parametri + sollecitazioni)."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        inner = QWidget()
        form = QFormLayout(inner)

        def spin(minv, maxv, dec, default, suffix=""):
            s = QDoubleSpinBox()
            s.setRange(minv, maxv)
            s.setDecimals(dec)
            s.setValue(default)
            if suffix:
                s.setSuffix(f" {suffix}")
            return s

        def ispin(minv, maxv, default):
            s = QSpinBox()
            s.setRange(minv, maxv)
            s.setValue(default)
            return s

        self._b = spin(1, 500, 1, 30.0, "cm")
        self._h = spin(1, 500, 1, 50.0, "cm")
        self._n_sup = ispin(0, 20, 2)
        self._n_inf = ispin(0, 20, 2)
        self._phi_long = spin(0.1, 5.0, 1, 1.6, "cm")
        self._phi_staffe = spin(0.1, 3.0, 1, 0.8, "cm")
        self._passo = spin(1, 100, 0, 20.0, "cm")
        self._c = spin(1, 10, 1, 3.0, "cm")
        self._sigma_c = spin(0, 500, 0, 60.0, "kg/cm²")
        self._sigma_s = spin(0, 10000, 0, 2600.0, "kg/cm²")
        self._M = spin(-1e9, 1e9, 0, 0.0, "kg·cm")
        self._V = spin(-1e7, 1e7, 0, 0.0, "kg")
        self._N = spin(-1e7, 1e7, 0, 0.0, "kg")
        self._pos = QComboBox()
        self._pos.addItems(_POSIZIONI)

        form.addRow("b (larghezza):", self._b)
        form.addRow("h (altezza):", self._h)
        form.addRow("n barre sup:", self._n_sup)
        form.addRow("n barre inf:", self._n_inf)
        form.addRow("φ_long:", self._phi_long)
        form.addRow("φ_staffe:", self._phi_staffe)
        form.addRow("Passo staffe:", self._passo)
        form.addRow("Copriferro:", self._c)
        form.addRow("σ_c_adm:", self._sigma_c)
        form.addRow("σ_s_adm:", self._sigma_s)
        form.addRow("M (momento):", self._M)
        form.addRow("V (taglio):", self._V)
        form.addRow("N (assiale):", self._N)
        form.addRow("Posizione:", self._pos)

        scroll.setWidget(inner)
        layout = QVBoxLayout(self)
        layout.addWidget(scroll)

    def get_input(self) -> dict:
        return {
            "b": self._b.value(), "h": self._h.value(),
            "n_barre_sup": self._n_sup.value(), "n_barre_inf": self._n_inf.value(),
            "phi_long": self._phi_long.value(), "phi_staffe": self._phi_staffe.value(),
            "passo_staffe": self._passo.value(), "c": self._c.value(),
            "sigma_c_adm": self._sigma_c.value(), "sigma_s_adm": self._sigma_s.value(),
            "M": self._M.value(), "V": self._V.value(), "N": self._N.value(),
            "posizione": self._pos.currentText(),
        }

    def get_ca_params_vis(self) -> dict:
        return {
            "b": self._b.value(), "h": self._h.value(),
            "n_sup": self._n_sup.value(), "n_inf": self._n_inf.value(),
            "phi_long": self._phi_long.value(), "c": self._c.value(),
        }


class _FormReticolare(QWidget):
    """Form completo per cordolo reticolare (geometria + carichi)."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        inner = QWidget()
        form = QFormLayout(inner)

        def spin(minv, maxv, dec, default, suffix=""):
            s = QDoubleSpinBox()
            s.setRange(minv, maxv)
            s.setDecimals(dec)
            s.setValue(default)
            if suffix:
                s.setSuffix(f" {suffix}")
            return s

        self._L = spin(10, 5000, 0, 400.0, "cm")
        self._h = spin(10, 500, 0, 30.0, "cm")
        self._n_campate = QSpinBox()
        self._n_campate.setRange(2, 20)
        self._n_campate.setValue(4)
        self._schema = QComboBox()
        self._schema.addItems(_SCHEMI_RETICOLARI)
        self._acciaio = QComboBox()
        self._acciaio.addItems(_TIPI_ACCIAIO)
        self._acciaio.setCurrentText("Fe430")
        self._F_y = spin(0, 1e7, 0, 5000.0, "kg")
        # Sezione corrente (piatto b x t)
        self._b_corr = spin(1, 50, 1, 5.0, "cm")
        self._t_corr = spin(0.1, 20, 1, 1.0, "cm")
        # Sezione diagonale (piatto b x t)
        self._b_diag = spin(1, 50, 1, 4.0, "cm")
        self._t_diag = spin(0.1, 20, 1, 0.8, "cm")
        self._pos = QComboBox()
        self._pos.addItems(_POSIZIONI)

        form.addRow("L (lunghezza cordolo):", self._L)
        form.addRow("h (profondita'/spessore muro):", self._h)
        form.addRow("N. campate:", self._n_campate)
        form.addRow("Schema:", self._schema)
        form.addRow("Tipo acciaio:", self._acciaio)
        form.addRow("F_y (forza sismica orizzontale):", self._F_y)
        form.addRow(QLabel("— Sezione corrente (piatto b×t) —"), QLabel(""))
        form.addRow("  b corrente:", self._b_corr)
        form.addRow("  t corrente:", self._t_corr)
        form.addRow(QLabel("— Sezione diagonale (piatto b×t) —"), QLabel(""))
        form.addRow("  b diagonale:", self._b_diag)
        form.addRow("  t diagonale:", self._t_diag)
        form.addRow("Posizione:", self._pos)

        scroll.setWidget(inner)
        layout = QVBoxLayout(self)
        layout.addWidget(scroll)

    def get_input(self) -> dict:
        return {
            "L": self._L.value(), "h_traliccio": self._h.value(),
            "n_campate": self._n_campate.value(),
            "schema": self._schema.currentText(),
            "tipo_acciaio": self._acciaio.currentText(),
            "F_y": self._F_y.value(),
            "b_corrente": self._b_corr.value(), "t_corrente": self._t_corr.value(),
            "b_diagonale": self._b_diag.value(), "t_diagonale": self._t_diag.value(),
            "posizione": self._pos.currentText(),
        }

    def get_ret_params_vis(self) -> dict:
        return {
            "L": self._L.value(), "h": self._h.value(),
            "n_campate": self._n_campate.value(),
            "schema": self._schema.currentText(),
        }


# ── CordoliWidget ─────────────────────────────────────────────────────────────

class CordoliWidget(QWidget):
    """Widget embeddabile per verifica cordoli metallici, CA e reticolari."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._sagomario = SagomarioAcciaio()
        self._sagomario.carica_tutti()
        self._tipo_corrente = "Metallico"
        self._profilo_corrente: ProfiloAcciaio | None = None
        self._mappa_righe: dict[int, ProfiloAcciaio] = {}
        self._tabulato: TabulatoCalcolo | None = None

        self._init_ui()
        self._connetti_segnali()
        self._popola_tabella()

    # ── UI setup ─────────────────────────────────────────────────────────────

    def _init_ui(self) -> None:
        main_layout = QVBoxLayout(self)

        # ─ Tabs ─
        self._tabs = QTabWidget()
        self._tabs.addTab(self._build_tab_selezione(), "Selezione / Parametri")
        self._tabs.addTab(self._build_tab_sezione(), "Sezione")
        self._tabs.addTab(self._build_tab_sollecitazioni(), "Sollecitazioni")
        self._tabs.addTab(self._build_tab_output(), "Verifiche")
        main_layout.addWidget(self._tabs)

        # ─ Bottone calcola (sempre visibile sotto le tab) ─
        row = QHBoxLayout()
        row.addStretch()
        self.btn_calcola = QPushButton("Calcola verifiche")
        self.btn_calcola.setMinimumHeight(32)
        row.addWidget(self.btn_calcola)
        row.addStretch()
        main_layout.addLayout(row)

        # Tab 3 (Sollecitazioni) visibile solo per Metallico
        self._aggiorna_visibilita_tab3()

    def _build_tab_selezione(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)

        # Combo tipo (sempre visibile)
        tipo_row = QHBoxLayout()
        tipo_row.addWidget(QLabel("Tipo cordolo:"))
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(_TIPI_CORDOLO)
        tipo_row.addWidget(self.combo_tipo)
        tipo_row.addStretch()
        layout.addLayout(tipo_row)

        # Stack: pagina 0 Metallico, 1 CA, 2 Reticolare
        self._stack_sel = QStackedWidget()

        # ── Pagina 0 — Metallico ──
        pag_met = QWidget()
        pag_layout = QVBoxLayout(pag_met)

        filtri_row = QHBoxLayout()
        filtri_row.addWidget(QLabel("Famiglia:"))
        self.combo_famiglia = QComboBox()
        famiglie = self._sagomario.list_famiglie()
        self.combo_famiglia.addItems(famiglie if famiglie else ["(nessuna)"])
        filtri_row.addWidget(self.combo_famiglia)
        filtri_row.addWidget(QLabel("Wx ≥"))
        self._wx_min = QLineEdit("0")
        self._wx_min.setMaximumWidth(60)
        filtri_row.addWidget(self._wx_min)
        filtri_row.addWidget(QLabel("h min:"))
        self._h_min = QLineEdit("0")
        self._h_min.setMaximumWidth(50)
        filtri_row.addWidget(self._h_min)
        filtri_row.addWidget(QLabel("max:"))
        self._h_max = QLineEdit("999")
        self._h_max.setMaximumWidth(50)
        filtri_row.addWidget(self._h_max)
        filtri_row.addStretch()
        pag_layout.addLayout(filtri_row)

        self.tabella_profili = QTableWidget()
        self.tabella_profili.setColumnCount(6)
        self.tabella_profili.setHorizontalHeaderLabels(
            ["Nome", "h [cm]", "b [cm]", "A [cm²]", "Wx [cm³]", "massa [kg/m]"]
        )
        self.tabella_profili.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.tabella_profili.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.tabella_profili.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        pag_layout.addWidget(self.tabella_profili)

        btn_row = QHBoxLayout()
        self.btn_importa_csv = QPushButton("Importa CSV...")
        self.btn_genera_template = QPushButton("Genera template CSV")
        btn_row.addWidget(self.btn_importa_csv)
        btn_row.addWidget(self.btn_genera_template)
        btn_row.addStretch()
        pag_layout.addLayout(btn_row)

        # ── Pagina 1 — CA ──
        self._form_ca = _FormCA()

        # ── Pagina 2 — Reticolare ──
        self._form_ret = _FormReticolare()

        self._stack_sel.addWidget(pag_met)
        self._stack_sel.addWidget(self._form_ca)
        self._stack_sel.addWidget(self._form_ret)
        layout.addWidget(self._stack_sel)

        return container

    def _build_tab_sezione(self) -> QWidget:
        container = QWidget()
        layout = QHBoxLayout(container)
        self._vis = _SezioneVisualizzatore()
        layout.addWidget(self._vis, stretch=3)
        self._info_profilo = _TabellaProfiloInfo()
        layout.addWidget(self._info_profilo, stretch=1)
        return container

    def _build_tab_sollecitazioni(self) -> QWidget:
        self._input_soll = _InputSollecitazioni()
        return self._input_soll

    def _build_tab_output(self) -> QWidget:
        self._output = _OutputVerifiche()
        return self._output

    # ── Segnali ──────────────────────────────────────────────────────────────

    def _connetti_segnali(self) -> None:
        self.combo_tipo.currentTextChanged.connect(self._on_tipo_cambiato)
        self.combo_famiglia.currentTextChanged.connect(self._popola_tabella)
        self._wx_min.textChanged.connect(self._filtra_tabella)
        self._h_min.textChanged.connect(self._filtra_tabella)
        self._h_max.textChanged.connect(self._filtra_tabella)
        self.tabella_profili.currentCellChanged.connect(
            lambda row, _col, _prev_row, _prev_col: self._on_profilo_selezionato(row)
        )
        self.btn_importa_csv.clicked.connect(self._importa_csv)
        self.btn_genera_template.clicked.connect(self._genera_template)
        self.btn_calcola.clicked.connect(self._esegui_calcolo)

    # ── Handlers ─────────────────────────────────────────────────────────────

    def _on_tipo_cambiato(self, tipo: str) -> None:
        self._tipo_corrente = tipo
        idx = _TIPI_CORDOLO.index(tipo)
        self._stack_sel.setCurrentIndex(idx)
        self._aggiorna_visibilita_tab3()
        self.combo_famiglia.setVisible(tipo == "Metallico")
        self._profilo_corrente = None
        self._info_profilo.aggiorna(None)
        self._vis.aggiorna_metallico(None)
        if tipo == "Metallico":
            self._popola_tabella()
        elif tipo == "CA":
            d = self._form_ca.get_ca_params_vis()
            self._vis.aggiorna_ca(**d)
        elif tipo == "Reticolare":
            d = self._form_ret.get_ret_params_vis()
            self._vis.aggiorna_reticolare(**d)

    def _aggiorna_visibilita_tab3(self) -> None:
        """Mostra Tab 3 solo per tipo Metallico."""
        visibile = self._tipo_corrente == "Metallico"
        try:
            self._tabs.setTabVisible(2, visibile)
        except AttributeError:
            self._tabs.setTabEnabled(2, visibile)

    def _popola_tabella(self) -> None:
        if self._tipo_corrente != "Metallico":
            return
        famiglia = self.combo_famiglia.currentText()
        try:
            wx_min = float(self._wx_min.text() or "0")
        except ValueError:
            wx_min = 0.0
        try:
            h_min = float(self._h_min.text() or "0")
        except ValueError:
            h_min = 0.0
        try:
            h_max = float(self._h_max.text() or "9999")
        except ValueError:
            h_max = 9999.0

        profili = self._sagomario.list_by_famiglia(famiglia)
        profili = [
            p for p in profili
            if p.Wx >= wx_min and h_min <= p.h <= h_max
        ]

        self.tabella_profili.setUpdatesEnabled(False)
        self.tabella_profili.setRowCount(len(profili))
        self._mappa_righe = {}
        for row, p in enumerate(profili):
            self._mappa_righe[row] = p
            self.tabella_profili.setItem(row, 0, QTableWidgetItem(p.nome))
            self.tabella_profili.setItem(row, 1, QTableWidgetItem(f"{p.h:.1f}"))
            self.tabella_profili.setItem(row, 2, QTableWidgetItem(f"{p.b:.1f}"))
            self.tabella_profili.setItem(row, 3, QTableWidgetItem(f"{p.A:.2f}"))
            self.tabella_profili.setItem(row, 4, QTableWidgetItem(f"{p.Wx:.1f}"))
            self.tabella_profili.setItem(row, 5, QTableWidgetItem(f"{p.massa_kg_m:.1f}"))
        self.tabella_profili.setUpdatesEnabled(True)

    def _filtra_tabella(self) -> None:
        self._popola_tabella()

    def _on_profilo_selezionato(self, riga: int) -> None:
        profilo = self._mappa_righe.get(riga)
        self._profilo_corrente = profilo
        self._vis.aggiorna_metallico(profilo)
        self._info_profilo.aggiorna(profilo)

    def _importa_csv(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Importa profili CSV", "", "CSV (*.csv);;Tutti i file (*)"
        )
        if not path:
            return
        n, warnings = self._sagomario.carica_da_csv(path)
        self._popola_tabella()
        # Aggiorna famiglie combo
        famiglie = self._sagomario.list_famiglie()
        self.combo_famiglia.blockSignals(True)
        self.combo_famiglia.clear()
        self.combo_famiglia.addItems(famiglie)
        self.combo_famiglia.blockSignals(False)

        if warnings:
            msg = f"{n} profili caricati.\n\nWarning:\n" + "\n".join(f"• {w}" for w in warnings)
            QMessageBox.warning(self, "Import CSV", msg)
        else:
            QMessageBox.information(self, "Import CSV", f"{n} profili caricati con successo.")

    def _genera_template(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Salva template CSV", "template_profili_acciaio.csv", "CSV (*.csv)"
        )
        if not path:
            return
        SagomarioAcciaio.genera_template_csv(path)
        QMessageBox.information(self, "Template CSV",
                                f"Template salvato in:\n{path}")

    def _esegui_calcolo(self) -> None:
        try:
            if self._tipo_corrente == "Metallico":
                tabulato, verificato = self._calcola_metallico()
            elif self._tipo_corrente == "CA":
                tabulato, verificato = self._calcola_ca()
            else:
                tabulato, verificato = self._calcola_reticolare()
        except Exception as exc:
            QMessageBox.critical(self, "Errore calcolo", str(exc))
            return

        self._tabulato = tabulato
        self._output.mostra_risultato(tabulato, verificato)
        if self._tabs.count() > 3:
            self._tabs.setCurrentIndex(3)

    def _calcola_metallico(self) -> tuple[TabulatoCalcolo, bool]:
        if self._profilo_corrente is None:
            raise ValueError("Selezionare un profilo dalla tabella prima di calcolare.")
        p = self._profilo_corrente
        d = self._input_soll.get_input()

        met = CordoloMetallico(
            nome_profilo=p.nome,
            A=p.A,
            Wx=p.Wx,
            Wy=p.Wy,
            Ix=p.Ix,
            h=p.h,
            tipo_acciaio=d["tipo_acciaio"],
            sigma_adm=d["sigma_adm"],
        )
        cord = Cordolo(
            tipo=TipoCordolo.METALLICO_SINGOLO,
            posizione=_POSIZIONE_MAP[d["posizione"]],
            Mx=d["M"],
            V=d["V"],
            N=d["N"],
            metallico=met,
        )
        ris = verifica_cordolo(cord)

        tab = TabulatoCalcolo(
            titolo=f"Verifica Cordolo Metallico — {p.nome}",
            normativa="TA DM 14/02/1992 / CNR 10011",
            modulo="cordoli_widget",
        )
        tab.aggiungi_sezione_input({
            "profilo": ("Profilo", p.nome, ""),
            "Wx": ("Modulo elastico Wx", p.Wx, "cm³"),
            "sigma_adm": ("Tensione ammissibile", d["sigma_adm"], "kg/cm²"),
            "Mx": ("Momento agente", d["M"], "kg·cm"),
            "V": ("Taglio agente", d["V"], "kg"),
        })
        for passo in ris.passaggi:
            tab.aggiungi_riga_calcolo(descrizione=passo)
        tab.imposta_esito(
            domanda=abs(d["M"]),
            capacita=met.M_Rd,
            unita="kg·cm",
            nome_domanda="|Mx|",
            nome_capacita="M_Rd",
        )
        return tab, ris.verifica_globale

    def _calcola_ca(self) -> tuple[TabulatoCalcolo, bool]:
        d = self._form_ca.get_input()
        ca = CordoloCA(
            b=d["b"], h=d["h"],
            n_barre_sup=d["n_barre_sup"], n_barre_inf=d["n_barre_inf"],
            phi_long=d["phi_long"], phi_staffe=d["phi_staffe"],
            passo_staffe=d["passo_staffe"], c=d["c"],
            sigma_c_adm=d["sigma_c_adm"], sigma_s_adm=d["sigma_s_adm"],
        )
        cord = Cordolo(
            tipo=TipoCordolo.CA,
            posizione=_POSIZIONE_MAP[d["posizione"]],
            Mx=d["M"],
            V=d["V"],
            N=d["N"],
            ca=ca,
        )
        ris = verifica_cordolo(cord)

        tab = TabulatoCalcolo(
            titolo=f"Verifica Cordolo CA — {d['b']:.0f}×{d['h']:.0f} cm",
            normativa="NTC2018 §7.8.1.6 / TA DM 1992",
            modulo="cordoli_widget",
        )
        tab.aggiungi_sezione_input({
            "b": ("Larghezza", d["b"], "cm"),
            "h": ("Altezza", d["h"], "cm"),
            "A_s_inf": ("Armatura inf.", ca.A_s_inf, "cm²"),
            "sigma_s_adm": ("σ_s ammissibile", d["sigma_s_adm"], "kg/cm²"),
            "Mx": ("Momento agente", d["M"], "kg·cm"),
        })
        for passo in ris.passaggi:
            tab.aggiungi_riga_calcolo(descrizione=passo)

        M_Rd = ca.sigma_s_adm * ca.A_s_inf * 0.9 * ca.d
        tab.imposta_esito(
            domanda=abs(d["M"]),
            capacita=max(M_Rd, 0.001),
            unita="kg·cm",
            nome_domanda="|Mx|",
            nome_capacita="M_Rd",
        )
        return tab, ris.verifica_globale

    def _calcola_reticolare(self) -> tuple[TabulatoCalcolo, bool]:
        d = self._form_ret.get_input()
        sec_corr = SezioneAsta.da_piatto(d["b_corrente"], d["t_corrente"])
        sec_diag = SezioneAsta.da_piatto(d["b_diagonale"], d["t_diagonale"])
        schema = (SchemaReticolare.HOWE if d["schema"] == "Howe"
                  else SchemaReticolare.PRATT)
        cret = CordoloReticolare(
            schema=schema,
            n_campate=d["n_campate"],
            L=d["L"],
            h=d["h_traliccio"],
            sezione_corrente=sec_corr,
            sezione_diagonale=sec_diag,
            tipo_acciaio=d["tipo_acciaio"],
        )
        ris = verifica_cordolo_reticolare(cret, d["F_y"])

        tab = TabulatoCalcolo(
            titolo=f"Verifica Cordolo Reticolare — {d['schema']} {d['n_campate']} campate",
            normativa="NTC2018 §8.7 / TA DM 1992",
            modulo="cordoli_widget",
        )
        tab.aggiungi_sezione_input({
            "L": ("Lunghezza cordolo", d["L"], "cm"),
            "h": ("Profondita'", d["h_traliccio"], "cm"),
            "n_campate": ("N. campate", d["n_campate"], ""),
            "F_y": ("Forza sismica", d["F_y"], "kg"),
        })
        for passo in ris.passaggi:
            tab.aggiungi_riga_calcolo(descrizione=passo)
        tab.imposta_esito(
            domanda=d["F_y"],
            capacita=max(ris.F_ritegno_disponibile, 0.001),
            unita="kg",
            nome_domanda="F_y",
            nome_capacita="F_ritegno",
        )
        return tab, ris.verificato


# ── Auto-discovery ────────────────────────────────────────────────────────────

MODULE_SPEC = {
    "key": "cordoli",
    "name": "Cordoli Metallici e CA",
    "description": (
        "Verifica e progetto di cordoli metallici, in c.a. e reticolari "
        "per edifici in muratura (NTC2018 §7.8.1.6 / TA DM1992)"
    ),
}


def create_module(master: QWidget | None = None, **context) -> CordoliWidget:
    """Factory per auto-discovery moduli Qt."""
    return CordoliWidget(parent=master)
