"""(Legacy) Module Selector View Component (Tkinter).

Copy of original implementation used by the legacy ModuleSelectorWindow.
"""

from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk

from .components.flow_wrap import FlowWrapFrame


@dataclass
class ModuleCardSpec:
    title: str
    description: str
    button_text: str | None
    callback: callable
    extra_buttons: list[tuple[str, callable]] | None = None


class ModuleSelectorView(ttk.Frame):
    def __init__(self, master, specs: list[ModuleCardSpec]):
        super().__init__(master, padding=12)
        tk.Label(self, text="Select a module to start", font=(None, 12, "bold")).pack(anchor="w", pady=(0, 8))
        self.flow = FlowWrapFrame(self)
        self.flow.pack(fill="both", expand=True)
        for spec in specs:
            self._add_card(spec)

    def set_specs(self, specs: list[ModuleCardSpec]) -> None:
        self.flow.clear()
        for spec in specs:
            self._add_card(spec)

    def _add_card(self, spec: ModuleCardSpec):
        lf = tk.LabelFrame(self.flow, text=spec.title)
        wrap = 250
        tk.Label(lf, text=spec.description, justify="left", wraplength=wrap).pack(padx=8, pady=8, anchor="w")
        if spec.button_text:
            tk.Button(lf, text=spec.button_text, command=spec.callback).pack(pady=(0, 8), anchor="w")
        if spec.extra_buttons:
            for txt, cb in spec.extra_buttons:
                tk.Button(lf, text=txt, command=cb).pack(pady=(0, 6), anchor="w")
        self.flow.add(lf)
