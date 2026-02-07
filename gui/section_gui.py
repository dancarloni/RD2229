from __future__ import annotations

import tkinter as tk
from enum import Enum
from tkinter import messagebox, simpledialog, ttk
from typing import Dict, List, Optional, Type

import matplotlib.pyplot as plt
from core.geometry import (
    CircularHollowSection,
    CircularSection,
    InvertedTSection,
    ISection,
    LSection,
    PiSection,
    RectangularHollowSection,
    RectangularSection,
    SectionGeometry,
    TSection,
)
from core.section_properties import compute_section_properties
from matplotlib.patches import Circle as MplCircle
from matplotlib.patches import Rectangle as MplRectangle


class SectionType(Enum):
    RECTANGULAR = ("Rettangolare", RectangularSection, ["width", "height"])
    CIRCULAR = ("Circolare", CircularSection, ["diameter"])
    T_SHAPE = ("A T", TSection, ["flange_width", "flange_thickness", "web_thickness", "web_height"])
    I_SHAPE = (
        "A I (doppio T)",
        ISection,
        ["flange_width", "flange_thickness", "web_thickness", "web_height"],
    )
    L_SHAPE = ("A L", LSection, ["leg_x", "leg_y", "thickness"])
    INVERTED_T = (
        "T invertita",
        InvertedTSection,
        ["flange_width", "flange_thickness", "web_thickness", "web_height"],
    )
    PI_SHAPE = ("A Pi", PiSection, ["width", "top_thickness", "leg_thickness", "leg_height"])
    RECTANGULAR_HOLLOW = (
        "Rettangolare cava",
        RectangularHollowSection,
        ["outer_width", "outer_height", "inner_width", "inner_height"],
    )
    CIRCULAR_HOLLOW = (
        "Circolare cava",
        CircularHollowSection,
        ["outer_diameter", "inner_diameter"],
    )

    def __init__(self, display_name: str, cls: Type[SectionGeometry], params: List[str]):
        self.display_name = display_name
        self.cls = cls
        self.params = params


class SectionInputDialog(simpledialog.Dialog):
    def __init__(self, parent, title: str, section_type: SectionType):
        self.section_type = section_type
        self.inputs: Dict[str, tk.Entry] = {}
        self.result: Optional[SectionGeometry] = None
        super().__init__(parent, title=title)

    def body(self, master):
        tk.Label(master, text=f"Tipologia: {self.section_type.display_name}").grid(
            row=0, column=0, columnspan=2, sticky="w"
        )
        row = 1
        for param in self.section_type.params:
            tk.Label(master, text=f"{param.replace('_', ' ').title()} (cm):").grid(row=row, column=0, sticky="w")
            entry = tk.Entry(master)
            entry.grid(row=row, column=1)
            self.inputs[param] = entry
            row += 1
        return self.inputs[self.section_type.params[0]] if self.inputs else None

    def apply(self):
        kwargs = {}
        for param, entry in self.inputs.items():
            value_str = entry.get().strip()
            if not value_str:
                messagebox.showerror("Errore", f"{param} è richiesto")
                return
            try:
                value = float(value_str)
                if value <= 0:
                    raise ValueError("Deve essere positivo")
                # Arrotonda a 1 decimale
                value = round(value, 1)
            except ValueError:
                messagebox.showerror("Errore", f"{param} deve essere un numero positivo con al massimo 1 decimale")
                return
            kwargs[param] = value
        try:
            self.result = self.section_type.cls(**kwargs)
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nella creazione della sezione: {e}")


class SectionApp(tk.Frame):
    def __init__(self, master: Optional[tk.Misc] = None):
        super().__init__(master)
        # Annotiamo esplicitamente il tipo per evitare warning di Pylance su 'master'
        self.master: Optional[tk.Misc] = master
        self.pack(fill="both", expand=True)
        self.current_section: Optional[SectionGeometry] = None
        self.create_widgets()

    def create_widgets(self):
        # Selezione tipologia
        tk.Label(self, text="Seleziona tipologia di sezione:").pack(anchor="w", pady=5)
        self.section_var = tk.StringVar(value=SectionType.RECTANGULAR.display_name)
        self.section_combo = ttk.Combobox(self, textvariable=self.section_var, state="readonly")
        self.section_combo["values"] = [st.display_name for st in SectionType]
        self.section_combo.pack(fill="x", padx=10)
        self.section_combo.bind("<<ComboboxSelected>>", self.on_section_change)

        # Frame per input
        self.input_frame = tk.Frame(self)
        self.input_frame.pack(fill="x", padx=10, pady=10)
        self.create_input_fields()

        # Pulsanti
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", padx=10)
        tk.Button(btn_frame, text="Calcola proprietà", command=self.calculate_properties).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Mostra grafica", command=self.show_graphic).pack(side="left", padx=5)

        # Output
        self.output_text = tk.Text(self, height=10)
        self.output_text.pack(fill="both", expand=True, padx=10, pady=10)

    def on_section_change(self, event=None):
        self.create_input_fields()

    def create_input_fields(self):
        # Pulisce il frame
        for widget in self.input_frame.winfo_children():
            widget.destroy()

        selected_name = self.section_var.get()
        section_type = next(st for st in SectionType if st.display_name == selected_name)

        self.inputs: Dict[str, tk.Entry] = {}
        for param in section_type.params:
            tk.Label(self.input_frame, text=f"{param.replace('_', ' ').title()} (cm):").pack(anchor="w")
            entry = tk.Entry(self.input_frame)
            entry.pack(fill="x", padx=10, pady=2)
            self.inputs[param] = entry

    def calculate_properties(self):
        selected_name = self.section_var.get()
        section_type = next(st for st in SectionType if st.display_name == selected_name)

        kwargs = {}
        for param, entry in self.inputs.items():
            value_str = entry.get().strip()
            if not value_str:
                messagebox.showerror("Errore", f"{param} è richiesto")
                return
            try:
                value = float(value_str)
                if value <= 0:
                    raise ValueError("Deve essere positivo")
                value = round(value, 1)
            except ValueError:
                messagebox.showerror("Errore", f"{param} deve essere un numero positivo")
                return
            kwargs[param] = value

        try:
            self.current_section = section_type.cls(**kwargs)
            props = compute_section_properties(self.current_section)
            output = f"""Proprietà della sezione {selected_name}:

Area: {props.area:.2f} cm²
Baricentro: ({props.centroid_x:.2f}, {props.centroid_y:.2f}) cm
Momenti di inerzia:
  Ix: {props.ix:.2f} cm⁴
  Iy: {props.iy:.2f} cm⁴
Momenti statici:
  Qx: {props.qx:.2f} cm³
  Qy: {props.qy:.2f} cm³
"""
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, output)
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nel calcolo: {e}")

    def show_graphic(self):
        if not self.current_section:
            messagebox.showerror("Errore", "Calcola prima le proprietà")
            return

        # Usa Matplotlib per disegnare
        fig, ax = plt.subplots()
        ax.set_aspect("equal")
        ax.set_title(f"Sezione {self.section_var.get()}")

        # Disegna in base al tipo
        if isinstance(self.current_section, RectangularSection):
            ax.add_patch(MplRectangle((0, 0), self.current_section.width, self.current_section.height, fill=False))
        elif isinstance(self.current_section, CircularSection):
            circle = MplCircle(
                (self.current_section.centroid()[0], self.current_section.centroid()[1]),
                self.current_section.diameter / 2,
                fill=False,
            )
            ax.add_patch(circle)
        elif isinstance(self.current_section, TSection):
            # Disegna i rettangoli
            for rect in self.current_section._rects():
                ax.add_patch(
                    MplRectangle(
                        (rect.x, rect.y),
                        rect.width,
                        rect.height,
                        fill=rect.sign > 0,
                        color="blue" if rect.sign > 0 else "white",
                    )
                )
        # Aggiungi altri tipi se necessario, per ora usa un placeholder
        else:
            ax.text(
                0.5,
                0.5,
                "Grafica non implementata per questa sezione",
                transform=ax.transAxes,
                ha="center",
            )

        # Mostra baricentro
        cx, cy = self.current_section.centroid()
        ax.plot(cx, cy, "ro", markersize=5)
        ax.text(cx, cy, "Baricentro", fontsize=8, ha="right")

        plt.show()


def run_section_app():
    root = tk.Tk()
    root.title("Calcolatore Proprietà Sezioni")
    _ = SectionApp(master=root)
    root.geometry("600x600")
    root.mainloop()


if __name__ == "__main__":
    run_section_app()
