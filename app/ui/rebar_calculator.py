"""Rebar calculator helpers.

Provides a pure function `calculate_rebar_total` (usable in tests) and a
`RebarCalculatorWindow` class that encapsulates the Toplevel UI.
"""

from __future__ import annotations

import logging
import math
import tkinter as tk
from typing import Callable, Dict, Optional

DIAMETERS = [6, 8, 10, 12, 14, 16, 18, 20, 22, 24]


def calculate_rebar_total(counts: Dict[int, int]) -> float:
    """Return total rebar area in cm^2 given a mapping diameter(mm) -> count.

    Calculation matches previous logic in `VerificationTableApp`.
    """
    total = 0.0
    for d, n in counts.items():
        try:
            n_int = int(n or 0)
        except Exception:
            n_int = 0
        d_cm = d / 10.0
        area = math.pi * (d_cm**2) / 4.0
        total += n_int * area
    return total


class RebarCalculatorWindow:
    """Toplevel window to edit and compute rebar area.

    - parent: owning Tk widget
    - on_confirm: callable(total_str: str) called when user confirms
    - initial_values: optional mapping diameter->string/int to pre-fill fields
    """

    def __init__(
        self,
        parent: tk.Misc,
        on_confirm: Optional[Callable[[str], None]] = None,
        initial_values: Optional[Dict[int, int]] = None,
    ) -> None:
        self.parent = parent
        self.on_confirm = on_confirm
        self._vars: Dict[int, tk.StringVar] = {}
        self._entries = []
        self._total_var = tk.StringVar(value="0.00")

        self._win = tk.Toplevel(parent)
        self._win.title("Calcolo area armatura")
        self._win.resizable(False, False)
        self._win.transient(parent.winfo_toplevel())
        self._win.grab_set()

        frame = tk.Frame(self._win, padx=10, pady=10)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Ø (mm)", width=8, anchor="w").grid(row=0, column=0, sticky="w")
        tk.Label(frame, text="n barre", width=8, anchor="w").grid(row=0, column=1, sticky="w")

        for i, d in enumerate(DIAMETERS, start=1):
            tk.Label(frame, text=f"Ø{d}", width=8, anchor="w").grid(
                row=i, column=0, sticky="w", pady=2
            )
            var = tk.StringVar(value=str((initial_values or {}).get(d, "")))
            self._vars[d] = var
            ent = tk.Entry(frame, textvariable=var, width=8)
            self._entries.append(ent)
            ent.grid(row=i, column=1, sticky="w", pady=2)
            var.trace_add("write", lambda *_: self._update_total())
            if i == 1:
                ent.focus_set()

        total_frame = tk.Frame(frame)
        total_frame.grid(row=len(DIAMETERS) + 1, column=0, columnspan=2, sticky="w", pady=(8, 4))
        tk.Label(total_frame, text="Area totale [cm²]:").pack(side="left")
        tk.Label(total_frame, textvariable=self._total_var, width=10, anchor="w").pack(side="left")

        btn_frame = tk.Frame(frame)
        btn_frame.grid(row=len(DIAMETERS) + 2, column=0, columnspan=2, sticky="e")
        tk.Button(btn_frame, text="Conferma", command=self._confirm).pack(side="right")

        self._win.bind("<Escape>", lambda _e: self._close())
        self._win.bind("<Return>", lambda _e: self._confirm())

        # initialize
        self._update_total()

    def _gather_counts(self) -> Dict[int, int]:
        counts: Dict[int, int] = {}
        for d, var in self._vars.items():
            try:
                counts[d] = int(var.get() or 0)
            except Exception:
                counts[d] = 0
        return counts

    def _update_total(self) -> None:
        total = calculate_rebar_total(self._gather_counts())
        self._total_var.set(f"{total:.2f}")

    def _confirm(self) -> None:
        total = self._total_var.get()
        if callable(self.on_confirm):
            try:
                self.on_confirm(total)
            except Exception:
                # Ignore errors in callback but log in parent if available
                try:
                    logging.getLogger(__name__).exception("Error in rebar on_confirm callback")
                except Exception:
                    pass
        self._close()

    def _close(self) -> None:
        try:
            self._win.destroy()
        except Exception:
            logging.getLogger(__name__).exception("Error closing rebar window")
        self._win = None
