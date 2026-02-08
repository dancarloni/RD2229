"""Module Selector View Component.

This module provides the GUI view component for the Module Selector,
handling the layout and display of module cards in a responsive grid.
"""

import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk

from .components.flow_wrap import FlowWrapFrame


@dataclass
class ModuleCardSpec:
    """Specifica per una card del modulo.

    Definisce il contenuto e i comportamenti di una singola card
    nel selettore moduli.
    """

    title: str
    description: str
    button_text: str | None
    callback: callable
    extra_buttons: list[tuple[str, callable]] | None = None  # es. TA/SLU/SLE


class ModuleSelectorView(ttk.Frame):
    """Vista del selettore moduli.

    Gestisce il layout responsive delle card dei moduli utilizzando
    un FlowWrapFrame per il wrapping automatico.
    """

    def __init__(self, master, specs: list[ModuleCardSpec]):
        """Inizializza la vista del selettore moduli.

        Args:
            master: Il widget padre
            specs: Lista delle specifiche delle card da visualizzare
        """
        super().__init__(master, padding=12)
        # Title
        tk.Label(self, text="Select a module to start", font=(None, 12, "bold")).pack(
            anchor="w", pady=(0, 8)
        )
        # Flow container
        self.flow = FlowWrapFrame(self)
        self.flow.pack(fill="both", expand=True)
        # Build cards
        for spec in specs:
            self._add_card(spec)

    def _add_card(self, spec: ModuleCardSpec):
        """Aggiunge una card del modulo al layout.

        Args:
            spec: La specifica della card da aggiungere
        """
        lf = tk.LabelFrame(self.flow, text=spec.title)
        # testo
        wrap = 250
        tk.Label(lf, text=spec.description, justify="left", wraplength=wrap).pack(
            padx=8, pady=8, anchor="w"
        )
        # pulsanti
        if spec.button_text:
            tk.Button(lf, text=spec.button_text, command=spec.callback).pack(
                pady=(0, 8), anchor="w"
            )
        if spec.extra_buttons:
            for txt, cb in spec.extra_buttons:
                tk.Button(lf, text=txt, command=cb).pack(pady=(0, 6), anchor="w")
        self.flow.add(lf)
