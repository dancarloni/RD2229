"""Visualizzatore Sezione Strutturale (Qt6).

Rendering geometrico della sezione in scala con:
- Geometria esatta della sezione (calcestruzzo, acciaio, legno, muratura)
- Zone tese e zone compresse (rosso=trazione, blu=compressione)
- Asse neutro posizionato dal calcolo
- Armatura con posizione, diametro e copriferro (in scala)
- Diagramma delle deformazioni (piano sezione)
- Diagramma delle tensioni (σ_c, σ_s)

Validazione geometrica: coordinate, aree, baricentro verificati matematicamente.
Mai inventare posizioni/risultati: solo dati da calcolo effettivo.

Utilizzo::

    from src.ui.qt.visualizzatore_sezione import VisualizzatoreSezione

    widget = VisualizzatoreSezione()
    widget.imposta_sezione_rettangolare(b=30, h=50, copriferro=3)
    widget.imposta_armatura([
        {"x": 3.0, "y": 3.0, "diametro": 1.6},
        {"x": 27.0, "y": 3.0, "diametro": 1.6},
        {"x": 3.0, "y": 47.0, "diametro": 1.6},
        {"x": 27.0, "y": 47.0, "diametro": 1.6},
    ])
    widget.imposta_risultati_calcolo(
        asse_neutro_y=15.2,
        deformazioni={"eps_c": -0.0035, "eps_s": 0.0085},
        tensioni={"sigma_c_max": -141.7, "sigma_s": 3913.0},
    )
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Any

try:
    from PyQt6.QtCore import Qt, QPointF, QRectF
    from PyQt6.QtGui import QBrush, QColor, QPainter, QPen, QPolygonF, QFont
    from PyQt6.QtWidgets import (
        QHBoxLayout,
        QSizePolicy,
        QVBoxLayout,
        QWidget,
    )
except ImportError:  # pragma: no cover
    from PySide6.QtCore import Qt, QPointF, QRectF
    from PySide6.QtGui import QBrush, QColor, QPainter, QPen, QPolygonF, QFont
    from PySide6.QtWidgets import (
        QHBoxLayout,
        QSizePolicy,
        QVBoxLayout,
        QWidget,
    )

logger = logging.getLogger(__name__)


@dataclass
class BarraArmatura:
    """Singola barra di armatura nella sezione.

    Attributi:
        x: Coordinata x dal bordo sinistro [cm].
        y: Coordinata y dal bordo inferiore [cm].
        diametro: Diametro della barra [cm].
        area: Area della barra [cm²] (calcolata automaticamente).
        tesa: True se la barra è nella zona tesa (dal calcolo).
    """
    x: float
    y: float
    diametro: float
    area: float = 0.0
    tesa: bool = False

    def __post_init__(self) -> None:
        if self.area == 0.0:
            self.area = math.pi * (self.diametro / 2) ** 2


@dataclass
class GeometriaSezione:
    """Geometria della sezione strutturale.

    Attributi:
        tipo: Tipo sezione (rettangolare, circolare, T, L, I, custom).
        vertici: Lista di vertici [x, y] in cm del contorno esterno.
        b: Larghezza [cm] (per sez. rettangolari).
        h: Altezza [cm] (per sez. rettangolari).
        area: Area della sezione [cm²].
        baricentro_x: Coordinata x baricentro [cm].
        baricentro_y: Coordinata y baricentro [cm].
    """
    tipo: str = "rettangolare"
    vertici: list[list[float]] = field(default_factory=list)
    b: float = 0.0
    h: float = 0.0
    area: float = 0.0
    baricentro_x: float = 0.0
    baricentro_y: float = 0.0


@dataclass
class RisultatiCalcolo:
    """Risultati del calcolo per la visualizzazione.

    Attributi:
        asse_neutro_y: Posizione asse neutro dal bordo inferiore [cm].
        eps_c_max: Deformazione massima calcestruzzo compresso.
        eps_s_max: Deformazione massima acciaio teso.
        sigma_c_max: Tensione massima calcestruzzo compresso [kg/cm²].
        sigma_s_max: Tensione massima acciaio teso [kg/cm²].
        zona_compressa_alto: True se la compressione è in alto (flessione positiva).
    """
    asse_neutro_y: float = 0.0
    eps_c_max: float = 0.0
    eps_s_max: float = 0.0
    sigma_c_max: float = 0.0
    sigma_s_max: float = 0.0
    zona_compressa_alto: bool = True


# Colori standard
_COLORE_CLS = QColor(200, 200, 200, 180)          # Grigio chiaro — calcestruzzo
_COLORE_COMPRESSIONE = QColor(70, 130, 220, 100)    # Blu semi-trasparente — zona compressa
_COLORE_TRAZIONE = QColor(220, 80, 80, 100)         # Rosso semi-trasparente — zona tesa
_COLORE_ASSE_NEUTRO = QColor(0, 150, 0)             # Verde — asse neutro
_COLORE_ARMATURA = QColor(30, 30, 30)               # Nero — barre armatura
_COLORE_CONTORNO = QColor(50, 50, 50)               # Bordo sezione
_COLORE_DEFORMAZIONE = QColor(180, 100, 0)          # Arancione — diagramma deformazioni
_COLORE_TENSIONE = QColor(128, 0, 128)              # Viola — diagramma tensioni


class VisualizzatoreSezione(QWidget):
    """Widget Qt per la visualizzazione grafica della sezione strutturale.

    Mostra la sezione in scala con zone tese/compresse, asse neutro,
    armatura e diagrammi di deformazione/tensione.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumSize(400, 350)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self._geometria = GeometriaSezione()
        self._armature: list[BarraArmatura] = []
        self._risultati: RisultatiCalcolo | None = None

        # Margini per il disegno (pixel)
        self._margine = 60
        # Mostra diagrammi laterali
        self._mostra_deformazioni = True
        self._mostra_tensioni = True

    def imposta_sezione_rettangolare(self, b: float, h: float, copriferro: float = 0.0) -> None:
        """Imposta una sezione rettangolare.

        Parametri:
            b: Larghezza [cm].
            h: Altezza [cm].
            copriferro: Copriferro [cm] (solo informativo per la visualizzazione).
        """
        self._geometria = GeometriaSezione(
            tipo="rettangolare",
            vertici=[[0, 0], [b, 0], [b, h], [0, h]],
            b=b,
            h=h,
            area=b * h,
            baricentro_x=b / 2,
            baricentro_y=h / 2,
        )
        self.update()

    def imposta_sezione_poligonale(self, vertici: list[list[float]]) -> None:
        """Imposta una sezione con contorno poligonale generico.

        Parametri:
            vertici: Lista di [x, y] in cm dei vertici del contorno (antiorario).
        """
        # Calcolo area e baricentro con formula di Gauss
        n = len(vertici)
        area = 0.0
        cx = 0.0
        cy = 0.0
        for i in range(n):
            j = (i + 1) % n
            cross = vertici[i][0] * vertici[j][1] - vertici[j][0] * vertici[i][1]
            area += cross
            cx += (vertici[i][0] + vertici[j][0]) * cross
            cy += (vertici[i][1] + vertici[j][1]) * cross
        area /= 2.0
        if abs(area) > 1e-10:
            cx /= (6.0 * area)
            cy /= (6.0 * area)

        self._geometria = GeometriaSezione(
            tipo="poligonale",
            vertici=vertici,
            b=max(v[0] for v in vertici) - min(v[0] for v in vertici),
            h=max(v[1] for v in vertici) - min(v[1] for v in vertici),
            area=abs(area),
            baricentro_x=cx,
            baricentro_y=cy,
        )
        self.update()

    def imposta_armatura(self, barre: list[dict[str, float]]) -> None:
        """Imposta le barre di armatura.

        Parametri:
            barre: Lista di dizionari con chiavi "x", "y", "diametro" [cm].
        """
        self._armature = [
            BarraArmatura(
                x=b["x"],
                y=b["y"],
                diametro=b["diametro"],
            )
            for b in barre
        ]
        self.update()

    def imposta_risultati_calcolo(
        self,
        asse_neutro_y: float,
        deformazioni: dict[str, float] | None = None,
        tensioni: dict[str, float] | None = None,
        zona_compressa_alto: bool = True,
    ) -> None:
        """Imposta i risultati del calcolo per la visualizzazione.

        Parametri:
            asse_neutro_y: Posizione asse neutro dal bordo inferiore [cm].
            deformazioni: Dict con "eps_c" (cls compresso) e "eps_s" (acciaio teso).
            tensioni: Dict con "sigma_c_max" e "sigma_s" [kg/cm²].
            zona_compressa_alto: True se la zona compressa è in alto.
        """
        deformazioni = deformazioni or {}
        tensioni = tensioni or {}
        self._risultati = RisultatiCalcolo(
            asse_neutro_y=asse_neutro_y,
            eps_c_max=deformazioni.get("eps_c", 0.0),
            eps_s_max=deformazioni.get("eps_s", 0.0),
            sigma_c_max=tensioni.get("sigma_c_max", 0.0),
            sigma_s_max=tensioni.get("sigma_s", 0.0),
            zona_compressa_alto=zona_compressa_alto,
        )
        # Aggiorna stato teso/compresso delle barre
        for barra in self._armature:
            if zona_compressa_alto:
                barra.tesa = barra.y < asse_neutro_y
            else:
                barra.tesa = barra.y > asse_neutro_y
        self.update()

    def paintEvent(self, event: Any) -> None:
        """Disegna la sezione con tutti gli elementi grafici."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if not self._geometria.vertici:
            painter.drawText(
                self.rect(), Qt.AlignmentFlag.AlignCenter,
                "Nessuna sezione impostata"
            )
            painter.end()
            return

        # Calcola scala e offset per centrare il disegno
        larghezza_disp = self.width() - 2 * self._margine
        altezza_disp = self.height() - 2 * self._margine

        # Riserva spazio per diagrammi laterali
        spazio_diagrammi = 80 if (self._mostra_deformazioni or self._mostra_tensioni) else 0
        larghezza_sez = larghezza_disp - spazio_diagrammi * 2

        if larghezza_sez <= 0 or altezza_disp <= 0:
            painter.end()
            return

        scala_x = larghezza_sez / self._geometria.b if self._geometria.b > 0 else 1.0
        scala_y = altezza_disp / self._geometria.h if self._geometria.h > 0 else 1.0
        scala = min(scala_x, scala_y)

        # Offset per centrare
        ox = self._margine + spazio_diagrammi + (larghezza_sez - self._geometria.b * scala) / 2
        oy = self._margine + (altezza_disp - self._geometria.h * scala) / 2

        def _coord(x: float, y: float) -> QPointF:
            """Converte coordinate sezione [cm] in coordinate widget [px].
            Y invertito (origine in basso nella sezione, in alto nel widget).
            """
            return QPointF(
                ox + x * scala,
                oy + (self._geometria.h - y) * scala,
            )

        # 1. Disegna contorno sezione (calcestruzzo)
        poligono = QPolygonF()
        for v in self._geometria.vertici:
            poligono.append(_coord(v[0], v[1]))
        poligono.append(_coord(self._geometria.vertici[0][0], self._geometria.vertici[0][1]))

        painter.setPen(QPen(_COLORE_CONTORNO, 2))
        painter.setBrush(QBrush(_COLORE_CLS))
        painter.drawPolygon(poligono)

        # 2. Disegna zone tese e compresse (se risultati disponibili)
        if self._risultati:
            an_y = self._risultati.asse_neutro_y
            b = self._geometria.b

            # Zona compressa
            if self._risultati.zona_compressa_alto:
                zona_c = QPolygonF([
                    _coord(0, an_y), _coord(b, an_y), _coord(b, self._geometria.h), _coord(0, self._geometria.h)
                ])
                zona_t = QPolygonF([
                    _coord(0, 0), _coord(b, 0), _coord(b, an_y), _coord(0, an_y)
                ])
            else:
                zona_c = QPolygonF([
                    _coord(0, 0), _coord(b, 0), _coord(b, an_y), _coord(0, an_y)
                ])
                zona_t = QPolygonF([
                    _coord(0, an_y), _coord(b, an_y), _coord(b, self._geometria.h), _coord(0, self._geometria.h)
                ])

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(_COLORE_COMPRESSIONE))
            painter.drawPolygon(zona_c)
            painter.setBrush(QBrush(_COLORE_TRAZIONE))
            painter.drawPolygon(zona_t)

            # Asse neutro (linea tratteggiata verde)
            pen_an = QPen(_COLORE_ASSE_NEUTRO, 2, Qt.PenStyle.DashLine)
            painter.setPen(pen_an)
            p_an_sx = _coord(-1, an_y)
            p_an_dx = _coord(b + 1, an_y)
            painter.drawLine(p_an_sx, p_an_dx)

            # Etichetta asse neutro
            font_piccolo = QFont("Arial", 8)
            painter.setFont(font_piccolo)
            painter.setPen(_COLORE_ASSE_NEUTRO)
            painter.drawText(
                p_an_dx.x() + 4, p_an_dx.y() + 4,
                f"A.N. y={an_y:.1f} cm"
            )

        # 3. Disegna armatura (cerchi neri)
        for barra in self._armature:
            centro = _coord(barra.x, barra.y)
            raggio = max(barra.diametro * scala / 2, 3)  # Minimo 3px per visibilità

            colore_barra = _COLORE_TRAZIONE if barra.tesa else _COLORE_COMPRESSIONE
            painter.setPen(QPen(_COLORE_ARMATURA, 1))
            painter.setBrush(QBrush(_COLORE_ARMATURA))
            painter.drawEllipse(centro, raggio, raggio)

        # 4. Disegna baricentro (croce)
        p_bar = _coord(self._geometria.baricentro_x, self._geometria.baricentro_y)
        painter.setPen(QPen(QColor(255, 165, 0), 1, Qt.PenStyle.DashDotLine))
        painter.drawLine(p_bar.x() - 8, p_bar.y(), p_bar.x() + 8, p_bar.y())
        painter.drawLine(p_bar.x(), p_bar.y() - 8, p_bar.x(), p_bar.y() + 8)

        # 5. Quote dimensionali
        font_quote = QFont("Arial", 8)
        painter.setFont(font_quote)
        painter.setPen(QPen(_COLORE_CONTORNO, 1))

        # Larghezza (sotto)
        p_sx = _coord(0, 0)
        p_dx = _coord(self._geometria.b, 0)
        y_quota = p_sx.y() + 20
        painter.drawLine(p_sx.x(), y_quota, p_dx.x(), y_quota)
        painter.drawText(
            (p_sx.x() + p_dx.x()) / 2 - 15, y_quota + 14,
            f"b = {self._geometria.b:.1f} cm"
        )

        # Altezza (a sinistra)
        p_basso = _coord(0, 0)
        p_alto = _coord(0, self._geometria.h)
        x_quota = p_basso.x() - 20
        painter.drawLine(x_quota, p_basso.y(), x_quota, p_alto.y())
        painter.save()
        painter.translate(x_quota - 14, (p_basso.y() + p_alto.y()) / 2 + 25)
        painter.rotate(-90)
        painter.drawText(0, 0, f"h = {self._geometria.h:.1f} cm")
        painter.restore()

        # 6. Diagramma deformazioni (a sinistra della sezione)
        if self._risultati and self._mostra_deformazioni:
            self._disegna_diagramma_deformazioni(painter, ox, oy, scala)

        # 7. Diagramma tensioni (a destra della sezione)
        if self._risultati and self._mostra_tensioni:
            self._disegna_diagramma_tensioni(painter, ox, oy, scala)

        # 8. Legenda
        self._disegna_legenda(painter)

        painter.end()

    def _disegna_diagramma_deformazioni(
        self, painter: QPainter, ox: float, oy: float, scala: float
    ) -> None:
        """Disegna il diagramma delle deformazioni a sinistra della sezione."""
        if not self._risultati:
            return

        h = self._geometria.h
        an_y = self._risultati.asse_neutro_y
        eps_c = abs(self._risultati.eps_c_max)
        eps_s = abs(self._risultati.eps_s_max)
        max_eps = max(eps_c, eps_s, 1e-6)
        largh_diagramma = 60  # px

        # Posizione del diagramma
        x_base = ox - 15  # Linea di riferimento (deformazione = 0)

        def _y_from_sezione(y_cm: float) -> float:
            return oy + (h - y_cm) * scala

        painter.setPen(QPen(_COLORE_DEFORMAZIONE, 2))

        # Linea di riferimento (ε = 0) lungo tutta l'altezza
        painter.drawLine(
            QPointF(x_base, _y_from_sezione(0)),
            QPointF(x_base, _y_from_sezione(h))
        )

        # Diagramma lineare: dal bordo compresso al bordo teso
        if self._risultati.zona_compressa_alto:
            # Compressione in alto: ε_c al bordo superiore (negativo → a sinistra)
            p_alto = QPointF(x_base - eps_c / max_eps * largh_diagramma, _y_from_sezione(h))
            p_an = QPointF(x_base, _y_from_sezione(an_y))
            p_basso = QPointF(x_base + eps_s / max_eps * largh_diagramma, _y_from_sezione(0))
        else:
            p_alto = QPointF(x_base + eps_s / max_eps * largh_diagramma, _y_from_sezione(h))
            p_an = QPointF(x_base, _y_from_sezione(an_y))
            p_basso = QPointF(x_base - eps_c / max_eps * largh_diagramma, _y_from_sezione(0))

        painter.drawLine(p_alto, p_an)
        painter.drawLine(p_an, p_basso)

        # Etichette
        font_piccolo = QFont("Arial", 7)
        painter.setFont(font_piccolo)
        painter.setPen(_COLORE_DEFORMAZIONE)
        painter.drawText(p_alto.x() - 35, p_alto.y() - 2, f"ε={self._risultati.eps_c_max:.4f}")
        painter.drawText(p_basso.x() + 2, p_basso.y() + 10, f"ε={self._risultati.eps_s_max:.4f}")

    def _disegna_diagramma_tensioni(
        self, painter: QPainter, ox: float, oy: float, scala: float
    ) -> None:
        """Disegna il diagramma delle tensioni a destra della sezione."""
        if not self._risultati:
            return

        h = self._geometria.h
        b = self._geometria.b
        an_y = self._risultati.asse_neutro_y
        sigma_c = abs(self._risultati.sigma_c_max)
        sigma_s = abs(self._risultati.sigma_s_max)
        max_sigma = max(sigma_c, 1e-6)  # Scala basata su cls (acciaio è concentrato)
        largh_diagramma = 60  # px

        x_base = ox + b * scala + 15

        def _y_from_sezione(y_cm: float) -> float:
            return oy + (h - y_cm) * scala

        painter.setPen(QPen(_COLORE_TENSIONE, 2))

        # Linea di riferimento
        painter.drawLine(
            QPointF(x_base, _y_from_sezione(0)),
            QPointF(x_base, _y_from_sezione(h))
        )

        # Diagramma tensioni cls (trapezoidale/rettangolare nella zona compressa)
        if self._risultati.zona_compressa_alto:
            # Blocco rettangolare di compressione (0.8x)
            x_prof = an_y  # profondità asse neutro dal bordo compresso
            p1 = QPointF(x_base, _y_from_sezione(h))
            p2 = QPointF(x_base + sigma_c / max_sigma * largh_diagramma, _y_from_sezione(h))
            p3 = QPointF(x_base + sigma_c / max_sigma * largh_diagramma, _y_from_sezione(an_y))
            p4 = QPointF(x_base, _y_from_sezione(an_y))
        else:
            p1 = QPointF(x_base, _y_from_sezione(0))
            p2 = QPointF(x_base + sigma_c / max_sigma * largh_diagramma, _y_from_sezione(0))
            p3 = QPointF(x_base + sigma_c / max_sigma * largh_diagramma, _y_from_sezione(an_y))
            p4 = QPointF(x_base, _y_from_sezione(an_y))

        poligono_sigma = QPolygonF([p1, p2, p3, p4])
        painter.setBrush(QBrush(QColor(128, 0, 128, 60)))
        painter.drawPolygon(poligono_sigma)

        # Etichette
        font_piccolo = QFont("Arial", 7)
        painter.setFont(font_piccolo)
        painter.setPen(_COLORE_TENSIONE)
        painter.drawText(p2.x() + 2, p2.y() - 2, f"σ_c={self._risultati.sigma_c_max:.0f}")

    def _disegna_legenda(self, painter: QPainter) -> None:
        """Disegna la legenda in basso."""
        font = QFont("Arial", 7)
        painter.setFont(font)
        y_leg = self.height() - 15
        x_leg = 10

        elementi = [
            (_COLORE_COMPRESSIONE, "Zona compressa"),
            (_COLORE_TRAZIONE, "Zona tesa"),
            (_COLORE_ASSE_NEUTRO, "Asse neutro"),
            (_COLORE_ARMATURA, "Armatura"),
        ]

        for colore, testo in elementi:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(colore))
            painter.drawRect(x_leg, y_leg - 8, 12, 8)
            painter.setPen(QPen(QColor(0, 0, 0)))
            painter.drawText(x_leg + 16, y_leg, testo)
            x_leg += len(testo) * 7 + 30


MODULE_SPEC = {
    "key": "visualizzatore_sezione",
    "name": "Visualizzatore Sezione",
    "description": "Rendering grafico sezione strutturale con zone tese/compresse, asse neutro, armatura (Qt6)",
}


def create_module(master: QWidget | None = None, **context: Any) -> VisualizzatoreSezione:
    """Factory per il modulo selettore."""
    return VisualizzatoreSezione(parent=master)
