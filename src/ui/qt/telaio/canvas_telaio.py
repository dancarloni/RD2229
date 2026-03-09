"""
Canvas Qt per la visualizzazione e l'inserimento grafico del telaio piano.

Funzionalità:
  - Disegno aste (linee colorate per tipo: trave/pilastro)
  - Simboli grafici vincoli esterni (incastro, cerniera, carrello, pattino, pendolo)
  - Simboli rilasci interni (cerniera interna, manicotto)
  - Diagrammi sollecitazioni M/V/N in overlay colorato
  - Tre modalità operative: SELEZIONE, AGGIUNGI_NODO, AGGIUNGI_ASTA
  - Snap a griglia configurabile
  - Zoom e pan via mouse wheel + drag

Coordinate canvas: origine in basso a sinistra (asse Y verso l'alto).
"""

from __future__ import annotations

import math
from enum import Enum, auto

try:
    from PyQt6.QtCore import QPointF, QRectF, Qt  # noqa: F401
    from PyQt6.QtCore import pyqtSignal as Signal
    from PyQt6.QtGui import (
        QBrush,
        QColor,
        QFont,
        QPainter,
        QPainterPath,
        QPen,
        QTransform,
        QWheelEvent,
    )
    from PyQt6.QtWidgets import (
        QGraphicsEllipseItem,
        QGraphicsItem,
        QGraphicsLineItem,
        QGraphicsPathItem,  # noqa: F401
        QGraphicsScene,
        QGraphicsTextItem,
        QGraphicsView,
        QWidget,
    )
except ImportError:
    from PySide6.QtCore import Qt, Signal
    from PySide6.QtGui import (
        QBrush,
        QColor,
        QFont,
        QPainter,
        QPainterPath,
        QPen,
        QTransform,
        QWheelEvent,
    )
    from PySide6.QtWidgets import (
        QGraphicsEllipseItem,
        QGraphicsItem,
        QGraphicsLineItem,
        QGraphicsScene,
        QGraphicsTextItem,
        QGraphicsView,
        QWidget,
    )

from src.methods.rd2229.telaio.modello_telaio import (
    AstaTelaio,
    ModelloTelaio,
    NodoTelaio,
    TipoAsta,
    TipoVincoloEsterno,
)

# ==============================================================================
# ENUMERAZIONI
# ==============================================================================


class ModalitaCanvas(Enum):
    SELEZIONE = auto()
    AGGIUNGI_NODO = auto()
    AGGIUNGI_ASTA = auto()


# ==============================================================================
# COLORI E STILI
# ==============================================================================

COLORI = {
    TipoAsta.TRAVE:     QColor("#1565C0"),   # blu
    TipoAsta.PILASTRO:  QColor("#2E7D32"),   # verde
    TipoAsta.SETTO:     QColor("#4E342E"),   # marrone
    TipoAsta.MENSOLA:   QColor("#6A1B9A"),   # viola
    TipoAsta.INCLINATA: QColor("#E65100"),   # arancione
    TipoAsta.PENDOLO:   QColor("#37474F"),   # grigio scuro
}

COLORE_NODO = QColor("#F57F17")             # giallo scuro
COLORE_NODO_SELEZIONATO = QColor("#D50000")  # rosso
COLORE_ASTA_SELEZIONATA = QColor("#D50000")
COLORE_GRIGLIA = QColor("#E0E0E0")

COLORE_MOMENTO_POS = QColor(50, 150, 250, 120)    # blu semi-trasparente
COLORE_MOMENTO_NEG = QColor(250, 80, 80, 120)     # rosso semi-trasparente
COLORE_TAGLIO = QColor(80, 200, 80, 120)           # verde
COLORE_ASSIALE = QColor(200, 100, 200, 120)        # viola

SCALA_CM_PX = 3.0      # pixel per centimetro (default, modificabile)
RAGGIO_NODO_PX = 6.0


# ==============================================================================
# CANVAS PRINCIPALE
# ==============================================================================


class CanvasTelaio(QGraphicsView):
    """Canvas principale per disegno e interazione con il telaio."""

    nodo_cliccato = Signal(int)     # id_nodo
    asta_cliccata = Signal(int)     # id_asta
    nodo_richiesto = Signal(float, float)  # x_cm, y_cm (coordinate telaio)
    asta_richiesta = Signal(int, int)      # id_nodo_i, id_nodo_j

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        self._modello: ModelloTelaio | None = None
        self._modalita = ModalitaCanvas.SELEZIONE
        self._scala = SCALA_CM_PX
        self._griglia_cm = 50.0      # passo griglia in cm
        self._mostra_griglia = True

        # Stato inserimento asta
        self._primo_nodo_id: int | None = None

        # Overlay diagrammi: "M" | "V" | "N" | None
        self._overlay_tipo: str | None = None
        self._overlay_scala = 1.0   # scala amplificazione

        # Configurazione view
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        # Trasformazione: origine in basso a sinistra, Y verso l'alto
        # (Qt usa Y verso il basso, quindi invertiamo)
        t = QTransform()
        t.scale(1.0, -1.0)
        self.setTransform(t)

    # ------------------------------------------------------------------
    # PROPRIETÀ PUBBLICHE
    # ------------------------------------------------------------------

    @property
    def modalita(self) -> ModalitaCanvas:
        return self._modalita

    @modalita.setter
    def modalita(self, m: ModalitaCanvas) -> None:
        self._modalita = m
        self._primo_nodo_id = None
        if m == ModalitaCanvas.SELEZIONE:
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        else:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)

    def imposta_overlay(self, tipo: str | None, scala: float = 1.0) -> None:
        """Imposta overlay diagrammi sollecitazioni: "M" | "V" | "N" | None."""
        self._overlay_tipo = tipo
        self._overlay_scala = scala
        self.aggiorna()

    # ------------------------------------------------------------------
    # CARICAMENTO MODELLO
    # ------------------------------------------------------------------

    def carica_modello(self, modello: ModelloTelaio) -> None:
        """Carica e disegna il modello telaio."""
        self._modello = modello
        self.aggiorna()
        self.fitInView(self._scene.sceneRect().adjusted(-50, -50, 50, 50),
                       Qt.AspectRatioMode.KeepAspectRatio)

    def aggiorna(self) -> None:
        """Ridisegna tutto."""
        self._scene.clear()
        if self._modello is None:
            return

        if self._mostra_griglia:
            self._disegna_griglia()

        for asta in self._modello.aste:
            self._disegna_asta(asta)

        for nodo in self._modello.nodi:
            self._disegna_nodo(nodo)

    # ------------------------------------------------------------------
    # DISEGNO ELEMENTI
    # ------------------------------------------------------------------

    def _disegna_griglia(self) -> None:
        if not self._modello or not self._modello.nodi:
            return

        xs = [n.x for n in self._modello.nodi]
        ys = [n.y for n in self._modello.nodi]
        x_min = min(xs) - self._griglia_cm
        x_max = max(xs) + self._griglia_cm
        y_min = min(ys) - self._griglia_cm
        y_max = max(ys) + self._griglia_cm

        penna = QPen(COLORE_GRIGLIA, 0.5)
        passo = self._griglia_cm

        x = x_min - (x_min % passo)
        while x <= x_max:
            px = x * self._scala
            self._scene.addLine(px, y_min * self._scala, px, y_max * self._scala, penna)
            x += passo

        y = y_min - (y_min % passo)
        while y <= y_max:
            py = y * self._scala
            self._scene.addLine(x_min * self._scala, py, x_max * self._scala, py, penna)
            y += passo

    def _disegna_asta(self, asta: AstaTelaio) -> None:
        nodo_i = self._modello.nodo_by_id(asta.nodo_i)
        nodo_j = self._modello.nodo_by_id(asta.nodo_j)
        if nodo_i is None or nodo_j is None:
            return

        x1 = nodo_i.x * self._scala
        y1 = nodo_i.y * self._scala
        x2 = nodo_j.x * self._scala
        y2 = nodo_j.y * self._scala

        colore = COLORI.get(asta.tipo, QColor("#333333"))
        penna = QPen(colore, 2.5)
        linea = self._scene.addLine(x1, y1, x2, y2, penna)
        linea.setData(0, asta.id)   # id asta per click detection
        linea.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

        # Etichetta asta (a mezzeria)
        if asta.etichetta:
            xm = (x1 + x2) / 2
            ym = (y1 + y2) / 2
            testo = QGraphicsTextItem(asta.etichetta)
            testo.setTransform(QTransform().scale(1.0, -1.0))  # flip Y per testo leggibile
            testo.setPos(xm, ym)
            testo.setDefaultTextColor(colore)
            f = QFont()
            f.setPointSize(7)
            testo.setFont(f)
            self._scene.addItem(testo)

    def _disegna_nodo(self, nodo: NodoTelaio) -> None:
        px = nodo.x * self._scala
        py = nodo.y * self._scala
        r = RAGGIO_NODO_PX

        # Cerchio nodo
        colore_nodo = COLORE_NODO
        brush = QBrush(colore_nodo)
        penna = QPen(colore_nodo.darker(150), 1.0)
        ellisse = self._scene.addEllipse(
            px - r, py - r, 2 * r, 2 * r, penna, brush
        )
        ellisse.setData(0, nodo.id)
        ellisse.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

        # Etichetta nodo
        if nodo.etichetta:
            testo = QGraphicsTextItem(nodo.etichetta)
            testo.setTransform(QTransform().scale(1.0, -1.0))
            testo.setPos(px + r + 2, py + r)
            testo.setDefaultTextColor(QColor("#333"))
            f = QFont()
            f.setPointSize(8)
            f.setBold(True)
            testo.setFont(f)
            self._scene.addItem(testo)

        # Simbolo vincolo esterno
        self._disegna_vincolo(nodo, px, py)

    def _disegna_vincolo(self, nodo: NodoTelaio, px: float, py: float) -> None:
        """Disegna simbolo grafico del vincolo sotto (o accanto) al nodo."""
        v = nodo.vincolo
        if v.tipo == TipoVincoloEsterno.LIBERO:
            return

        s = 12.0    # dimensione simbolo in pixel
        penna_v = QPen(QColor("#333333"), 1.5)

        if v.tipo == TipoVincoloEsterno.INCASTRO:
            # Triangolo pieno verso il basso + tratteggio
            path = QPainterPath()
            path.moveTo(px, py)
            path.lineTo(px - s, py - s)
            path.lineTo(px + s, py - s)
            path.closeSubpath()
            item = self._scene.addPath(path, penna_v, QBrush(QColor("#666")))

            # Tratteggio base
            penna_tratt = QPen(QColor("#333"), 1.5)
            self._scene.addLine(px - s - 3, py - s, px + s + 3, py - s, penna_tratt)

        elif v.tipo == TipoVincoloEsterno.CERNIERA:
            # Triangolo vuoto + cerchietto al vertice
            path = QPainterPath()
            path.moveTo(px, py)
            path.lineTo(px - s, py - s)
            path.lineTo(px + s, py - s)
            path.closeSubpath()
            self._scene.addPath(path, penna_v, QBrush(Qt.BrushStyle.NoBrush))
            self._scene.addLine(px - s - 3, py - s, px + s + 3, py - s, penna_v)

        elif v.tipo in (TipoVincoloEsterno.CARRELLO_X, TipoVincoloEsterno.CARRELLO_Y):
            # Triangolo + ruote
            path = QPainterPath()
            path.moveTo(px, py)
            path.lineTo(px - s, py - s)
            path.lineTo(px + s, py - s)
            path.closeSubpath()
            self._scene.addPath(path, penna_v, QBrush(Qt.BrushStyle.NoBrush))
            # Cerchietti ruote
            r_ruota = 3.0
            for dx in [-s + 3, 0, s - 3]:
                self._scene.addEllipse(
                    px + dx - r_ruota, py - s - 2 * r_ruota,
                    2 * r_ruota, 2 * r_ruota, penna_v, QBrush(Qt.BrushStyle.NoBrush)
                )

        elif v.tipo in (TipoVincoloEsterno.PATTINO_X, TipoVincoloEsterno.PATTINO_Y):
            # Rettangolo + ruote
            self._scene.addRect(px - s, py - s, 2 * s, s * 0.7, penna_v,
                                 QBrush(Qt.BrushStyle.NoBrush))
            r_ruota = 3.0
            for dx in [-s + 4, s - 4]:
                self._scene.addEllipse(
                    px + dx - r_ruota, py - s - 2 * r_ruota,
                    2 * r_ruota, 2 * r_ruota, penna_v, QBrush(Qt.BrushStyle.NoBrush)
                )

        elif v.tipo == TipoVincoloEsterno.PENDOLO:
            # Asta inclinata con cerchietti
            ang = math.radians(v.angolo_pendolo_deg)
            dx = s * math.cos(ang)
            dy = s * math.sin(ang)
            self._scene.addLine(px, py, px - dx, py - dy, penna_v)
            r_c = 3.0
            self._scene.addEllipse(
                px - dx - r_c, py - dy - r_c, 2 * r_c, 2 * r_c, penna_v,
                QBrush(Qt.BrushStyle.NoBrush)
            )

        else:
            # Generico: quadratino
            self._scene.addRect(px - 4, py - 4, 8, 8, penna_v,
                                 QBrush(QColor("#888")))

    # ------------------------------------------------------------------
    # EVENTI MOUSE
    # ------------------------------------------------------------------

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Zoom con rotella del mouse."""
        fattore = 1.15
        if event.angleDelta().y() < 0:
            fattore = 1.0 / fattore
        self.scale(fattore, fattore)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            # Converti da pixel a cm (ricordando che Y è invertita nella scena)
            x_cm = scene_pos.x() / self._scala
            y_cm = scene_pos.y() / self._scala

            if self._modalita == ModalitaCanvas.AGGIUNGI_NODO:
                # Snap a griglia
                if self._griglia_cm > 0:
                    x_cm = round(x_cm / self._griglia_cm) * self._griglia_cm
                    y_cm = round(y_cm / self._griglia_cm) * self._griglia_cm
                self.nodo_richiesto.emit(x_cm, y_cm)
                return

            elif self._modalita == ModalitaCanvas.AGGIUNGI_ASTA:
                # Cerca nodo vicino al click
                id_nodo = self._trova_nodo_vicino(x_cm, y_cm)
                if id_nodo is not None:
                    if self._primo_nodo_id is None:
                        self._primo_nodo_id = id_nodo
                    else:
                        if id_nodo != self._primo_nodo_id:
                            self.asta_richiesta.emit(self._primo_nodo_id, id_nodo)
                        self._primo_nodo_id = None
                return

        super().mousePressEvent(event)

        # Detect click su nodo o asta
        items = self.items(event.pos())
        for item in items:
            id_val = item.data(0)
            if id_val is not None:
                if isinstance(item, QGraphicsEllipseItem):
                    self.nodo_cliccato.emit(id_val)
                elif isinstance(item, QGraphicsLineItem):
                    self.asta_cliccata.emit(id_val)
                break

    def _trova_nodo_vicino(self, x_cm: float, y_cm: float, tol_cm: float = 30.0) -> int | None:
        """Trova il nodo più vicino a (x_cm, y_cm) entro la tolleranza."""
        if not self._modello:
            return None
        min_dist = tol_cm
        id_trovato = None
        for nodo in self._modello.nodi:
            d = math.sqrt((nodo.x - x_cm) ** 2 + (nodo.y - y_cm) ** 2)
            if d < min_dist:
                min_dist = d
                id_trovato = nodo.id
        return id_trovato
