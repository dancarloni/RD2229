from __future__ import annotations

import logging
import tkinter as tk
from tkinter import ttk
from typing import Callable

from sections_app.ui.main_window import MainWindow
from sections_app.ui.historical_main_window import HistoricalModuleMainWindow
from sections_app.services.repository import CsvSectionSerializer, SectionRepository

logger = logging.getLogger(__name__)


class ModuleSelectorWindow(tk.Tk):
    """Finestra iniziale per selezionare il modulo da avviare."""

    def __init__(self, repository: SectionRepository, serializer: CsvSectionSerializer):
        super().__init__()
        self.title("Module Selector - RD2229 Tools")
        self.geometry("540x260")
        self.repository = repository
        self.serializer = serializer
        self._build_ui()

    def _build_ui(self) -> None:
        frame = tk.Frame(self)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        label = tk.Label(frame, text="Select a module to start", font=(None, 12, "bold"))
        label.pack(anchor="w", pady=(0, 8))

        modules_frame = tk.Frame(frame)
        modules_frame.pack(fill="both", expand=True)

        geom_frame = tk.LabelFrame(modules_frame, text="Geometry module")
        geom_frame.pack(side="left", fill="both", expand=True, padx=(0, 6))
        tk.Label(
            geom_frame,
            text="Compute and manage section geometry\n(areas, centroids, inertia, drawings, CSV archive)",
            justify="left",
        ).pack(padx=8, pady=8)
        tk.Button(geom_frame, text="Open Geometry", command=self._open_geometry).pack(pady=(0, 8))

        hist_frame = tk.LabelFrame(modules_frame, text="Historical RD 2229 / Santarella")
        hist_frame.pack(side="left", fill="both", expand=True, padx=(6, 0))
        tk.Label(
            hist_frame,
            text="Historical allowable-stress verifications\n(stubs and data connectors for now)",
            justify="left",
        ).pack(padx=8, pady=8)
        tk.Button(hist_frame, text="Open Historical", command=self._open_historical).pack(pady=(0, 8))

    def _open_geometry(self) -> None:
        logger.debug("Opening Geometry module")
        self.withdraw()
        win = MainWindow(self.repository, self.serializer)
        win.protocol("WM_DELETE_WINDOW", self._on_child_close)

    def _open_historical(self) -> None:
        logger.debug("Opening Historical module")
        self.withdraw()
        win = HistoricalModuleMainWindow(self, self.repository)
        win.protocol("WM_DELETE_WINDOW", self._on_child_close)

    def _on_child_close(self) -> None:
        """Callback when a child window is closed: safely restore the selector window.

        We guard against the case where the application has been destroyed and calling
        `deiconify` would raise a TclError.
        """
        try:
            if self.winfo_exists():
                self.deiconify()
        except tk.TclError:
            logger.debug("Cannot deiconify Module Selector: application already destroyed")

