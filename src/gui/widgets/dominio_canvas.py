"""Widget Qt per visualizzazione interattiva dominio N-Mx-My (FASE J).

Tre viste selezionabili: 3D surface, 2D Mx-My, 2D N-M.
Slider per N_fisso e theta_fisso.

Richiede: PySide6 o PyQt6 + matplotlib[backend_qt]
"""

from __future__ import annotations

from typing import Any

# Importazione opzionale Qt + matplotlib backend
try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure

    try:
        from PySide6.QtWidgets import (
            QComboBox, QHBoxLayout, QLabel, QSizePolicy,
            QSlider, QVBoxLayout, QWidget,
        )
        from PySide6.QtCore import Qt
        _QT_AVAILABLE = True
    except ImportError:
        try:
            from PyQt6.QtWidgets import (
                QComboBox, QHBoxLayout, QLabel, QSizePolicy,
                QSlider, QVBoxLayout, QWidget,
            )
            from PyQt6.QtCore import Qt
            _QT_AVAILABLE = True
        except ImportError:
            _QT_AVAILABLE = False

    _MPL_QT_AVAILABLE = True
except ImportError:
    _MPL_QT_AVAILABLE = False
    _QT_AVAILABLE = False


def _check_available() -> None:
    if not _QT_AVAILABLE or not _MPL_QT_AVAILABLE:
        raise ImportError(
            "DominioNMyCanvas richiede PySide6/PyQt6 e matplotlib. "
            "Installa con: pip install PySide6 matplotlib"
        )


if _QT_AVAILABLE and _MPL_QT_AVAILABLE:

    class DominioNMyCanvas(QWidget):
        """Widget per visualizzazione interattiva dominio N-Mx-My.

        Tre viste selezionabili:
          - 3D surface (N-Mx-My)
          - 2D Mx-My a N costante
          - 2D N-M a theta costante
        """

        _VISTE = ["3D Surface", "2D Mx-My", "2D N-M"]

        def __init__(self, parent: QWidget | None = None) -> None:
            _check_available()
            super().__init__(parent)

            self._dominio: Any = None
            self._fig = Figure(figsize=(8, 6), dpi=100)
            self._canvas = FigureCanvas(self._fig)
            self._canvas.setSizePolicy(QSizePolicy.Policy.Expanding,
                                       QSizePolicy.Policy.Expanding)

            # Controlli
            self._combo_vista = QComboBox()
            self._combo_vista.addItems(self._VISTE)
            self._combo_vista.currentIndexChanged.connect(self._ridisegna)

            self._slider_N = QSlider(Qt.Orientation.Horizontal)
            self._slider_N.setRange(0, 100)
            self._slider_N.setValue(0)
            self._slider_N.valueChanged.connect(self._ridisegna)
            self._label_N = QLabel("N: 0")

            self._slider_theta = QSlider(Qt.Orientation.Horizontal)
            self._slider_theta.setRange(0, 360)
            self._slider_theta.setValue(0)
            self._slider_theta.valueChanged.connect(self._ridisegna)
            self._label_theta = QLabel("theta: 0 deg")

            # Layout
            ctrl_layout = QHBoxLayout()
            ctrl_layout.addWidget(QLabel("Vista:"))
            ctrl_layout.addWidget(self._combo_vista)
            ctrl_layout.addWidget(self._label_N)
            ctrl_layout.addWidget(self._slider_N)
            ctrl_layout.addWidget(self._label_theta)
            ctrl_layout.addWidget(self._slider_theta)

            main_layout = QVBoxLayout(self)
            main_layout.addLayout(ctrl_layout)
            main_layout.addWidget(self._canvas)

        def aggiorna(self, dominio: Any) -> None:
            """Aggiorna il dominio e ridisegna."""
            self._dominio = dominio
            if dominio and dominio.N_levels_kg:
                self._slider_N.setRange(0, len(dominio.N_levels_kg) - 1)
            self._ridisegna()

        def _ridisegna(self) -> None:
            """Ridisegna in base alla vista selezionata."""
            self._fig.clear()
            dom = self._dominio
            if dom is None or not dom.N_levels_kg:
                ax = self._fig.add_subplot(111)
                ax.text(0.5, 0.5, "Nessun dominio", ha="center", va="center")
                self._canvas.draw()
                return

            vista = self._combo_vista.currentIndex()

            if vista == 0:
                self._draw_3d(dom)
            elif vista == 1:
                self._draw_2d_mxmy(dom)
            else:
                self._draw_2d_nm(dom)

            self._canvas.draw()

        def _draw_3d(self, dom: Any) -> None:
            import numpy as np
            Mx = np.array(dom.Mx_Rd_kgcm)
            My = np.array(dom.My_Rd_kgcm)
            N_grid = np.tile(
                np.array(dom.N_levels_kg)[:, np.newaxis],
                (1, Mx.shape[1]),
            )
            ax = self._fig.add_subplot(111, projection="3d")
            ax.plot_surface(Mx, My, N_grid, cmap="viridis", alpha=0.7)
            ax.set_xlabel("Mx [kg·cm]")
            ax.set_ylabel("My [kg·cm]")
            ax.set_zlabel("N [kg]")
            ax.set_title(f"Dominio N-Mx-My ({dom.norma})")

        def _draw_2d_mxmy(self, dom: Any) -> None:
            idx = self._slider_N.value()
            idx = min(idx, len(dom.N_levels_kg) - 1)
            N_val = dom.N_levels_kg[idx]
            self._label_N.setText(f"N: {N_val:.0f} kg")

            mx = list(dom.Mx_Rd_kgcm[idx]) + [dom.Mx_Rd_kgcm[idx][0]]
            my = list(dom.My_Rd_kgcm[idx]) + [dom.My_Rd_kgcm[idx][0]]

            ax = self._fig.add_subplot(111)
            ax.plot(mx, my, "b-", linewidth=1.5)
            ax.fill(mx, my, alpha=0.15, color="blue")
            ax.set_xlabel("Mx [kg·cm]")
            ax.set_ylabel("My [kg·cm]")
            ax.set_title(f"Dominio Mx-My a N={N_val:.0f} kg")
            ax.set_aspect("equal")
            ax.grid(True, alpha=0.3)

        def _draw_2d_nm(self, dom: Any) -> None:
            import math
            import numpy as np

            theta_deg = self._slider_theta.value()
            self._label_theta.setText(f"theta: {theta_deg} deg")
            theta_rad = math.radians(theta_deg)

            theta_arr = np.array(dom.theta_rad)
            j = int(np.argmin(np.abs(theta_arr - theta_rad)))

            Mx_arr = np.array(dom.Mx_Rd_kgcm)
            My_arr = np.array(dom.My_Rd_kgcm)
            M_vals = [
                math.sqrt(Mx_arr[i, j] ** 2 + My_arr[i, j] ** 2)
                for i in range(len(dom.N_levels_kg))
            ]

            ax = self._fig.add_subplot(111)
            ax.plot(M_vals, dom.N_levels_kg, "r-", linewidth=1.5)
            ax.fill_betweenx(dom.N_levels_kg, 0, M_vals, alpha=0.15, color="red")
            ax.set_xlabel("M [kg·cm]")
            ax.set_ylabel("N [kg]")
            ax.set_title(f"Dominio N-M a theta={theta_deg} deg")
            ax.grid(True, alpha=0.3)

        def salva(self, percorso: str, dpi: int = 150) -> None:
            """Salva la figura corrente su file."""
            self._fig.savefig(percorso, dpi=dpi, bbox_inches="tight")
