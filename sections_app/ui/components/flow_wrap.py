"""Flow Wrap Frame Component.

This module provides a responsive layout container that automatically
wraps child widgets into multiple rows based on available width.
"""

import tkinter as tk
from tkinter import ttk


class FlowWrapFrame(ttk.Frame):
    """Frame che dispone i widget figli in un layout responsive.

    Organizza automaticamente i widget figli in righe multiple
    quando la larghezza disponibile non è sufficiente.
    """

    def __init__(self, master, card_width=260, hgap=12, vgap=12, padding=12, **kwargs):
        """Inizializza il FlowWrapFrame.

        Args:
            master: Il widget padre
            card_width: Larghezza di ogni card
            hgap: Spazio orizzontale tra le card
            vgap: Spazio verticale tra le righe
            padding: Padding interno del frame
            **kwargs: Argomenti aggiuntivi per ttk.Frame
        """
        super().__init__(master, **kwargs)
        self.card_width = card_width
        self.hgap = hgap
        self.vgap = vgap
        self.padding = padding
        self._children = []
        self.bind("<Configure>", self._on_configure)

    def add(self, widget: tk.Widget):
        """Aggiunge un widget al layout flow.

        Args:
            widget: Il widget da aggiungere
        """
        self._children.append(widget)
        widget.master = self  # ensure parent
        widget.grid_propagate(False)

    def clear(self):
        """Rimuove tutti i widget dal layout."""
        for w in self._children:
            w.grid_forget()
        self._children.clear()

    def _on_configure(self, _evt=None):
        """Ricalcola il layout quando la dimensione cambia.

        Args:
            _evt: Evento di configurazione (ignorato)
        """
        width = max(1, self.winfo_width())
        usable = max(1, width - 2 * self.padding)
        step = self.card_width + self.hgap
        n_cols = max(1, usable // step)
        # Configure columns with uniform weight for even distribution
        for i in range(int(n_cols)):
            self.grid_columnconfigure(i, weight=1, uniform="cols")
        # Clear previous configurations for extra columns
        for i in range(int(n_cols), len(self._children) if self._children else 0):
            self.grid_columnconfigure(i, weight=0)
        # Place children
        for idx, w in enumerate(self._children):
            r = idx // int(n_cols)
            c = idx % int(n_cols)
            w.grid(
                row=r,
                column=c,
                padx=(0 if c == 0 else self.hgap, 0),
                pady=(0 if r == 0 else self.vgap, 0),
                sticky="nsew",
            )
            # Fix width to card_width while letting height auto
            w.configure(width=self.card_width)
