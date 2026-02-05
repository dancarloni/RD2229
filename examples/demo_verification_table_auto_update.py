#!/usr/bin/env python3
"""
Demo: Mostra l'aggiornamento automatico della VerificationTable
quando vengono aggiunte/modificate sezioni e materiali.
"""

import os
import tempfile
import tkinter as tk
from tkinter import ttk, messagebox

from sections_app.models.sections import RectangularSection, CircularSection
from sections_app.services.repository import SectionRepository
from core_models.materials import Material, MaterialRepository
from verification_table import VerificationTableWindow


class DemoControlPanel(tk.Tk):
    """Pannello di controllo per testare l'aggiornamento automatico."""
    
    def __init__(self):
        super().__init__()
        
        self.title("Demo: Auto-Aggiornamento VerificationTable")
        self.geometry("600x500")
        
        # Create temp repositories
        self.temp_dir = tempfile.mkdtemp()
        self.sections_file = os.path.join(self.temp_dir, "demo_sections.json")
        self.materials_file = os.path.join(self.temp_dir, "demo_materials.json")
        
        self.section_repo = SectionRepository(json_file=self.sections_file)
        self.material_repo = MaterialRepository(json_file=self.materials_file)
        
        # Initialize with some data
        self._initialize_data()
        
        # Build UI
        self._build_ui()
        
        # Reference to VerificationTableWindow
        self.vt_window = None
        
        # Auto-open VerificationTable
        self.after(500, self._open_verification_table)

    def _initialize_data(self):
        """Inizializza alcuni dati di esempio."""
        # Sezioni
        rect1 = RectangularSection(name="Rettangolare 20x30", width=20, height=30)
        rect2 = RectangularSection(name="Rettangolare 25x40", width=25, height=40)
        self.section_repo.add_section(rect1)
        self.section_repo.add_section(rect2)
        
        # Materiali
        mat1 = Material(name="C25/30", type="concrete", properties={"fck": 25})
        mat2 = Material(name="A500", type="steel", properties={"fyk": 500})
        self.material_repo.add(mat1)
        self.material_repo.add(mat2)

    def _build_ui(self):
        """Costruisce l'interfaccia utente."""
        # Title
        title = tk.Label(
            self,
            text="Demo: Auto-Aggiornamento VerificationTable",
            font=("Arial", 14, "bold"),
            pady=10,
        )
        title.pack()
        
        instructions = tk.Label(
            self,
            text="Usa i pulsanti sotto per aggiungere/modificare/eliminare\n"
                 "sezioni e materiali. La VerificationTable si aggiornerà\n"
                 "automaticamente in tempo reale!",
            justify="center",
            pady=10,
        )
        instructions.pack()
        
        # Section operations
        section_frame = tk.LabelFrame(self, text="Operazioni Sezioni", padx=10, pady=10)
        section_frame.pack(fill="x", padx=20, pady=10)
        
        btn_add_section = tk.Button(
            section_frame,
            text="➕ Aggiungi Sezione Random",
            command=self._add_random_section,
            width=30,
        )
        btn_add_section.pack(pady=5)
        
        btn_update_section = tk.Button(
            section_frame,
            text="✏️ Modifica Prima Sezione",
            command=self._update_first_section,
            width=30,
        )
        btn_update_section.pack(pady=5)
        
        btn_delete_section = tk.Button(
            section_frame,
            text="🗑️ Elimina Prima Sezione",
            command=self._delete_first_section,
            width=30,
        )
        btn_delete_section.pack(pady=5)
        
        # Material operations
        material_frame = tk.LabelFrame(self, text="Operazioni Materiali", padx=10, pady=10)
        material_frame.pack(fill="x", padx=20, pady=10)
        
        btn_add_material = tk.Button(
            material_frame,
            text="➕ Aggiungi Materiale Random",
            command=self._add_random_material,
            width=30,
        )
        btn_add_material.pack(pady=5)
        
        btn_update_material = tk.Button(
            material_frame,
            text="✏️ Modifica Primo Materiale",
            command=self._update_first_material,
            width=30,
        )
        btn_update_material.pack(pady=5)
        
        btn_delete_material = tk.Button(
            material_frame,
            text="🗑️ Elimina Primo Materiale",
            command=self._delete_first_material,
            width=30,
        )
        btn_delete_material.pack(pady=5)
        
        # Status
        status_frame = tk.LabelFrame(self, text="Stato Archivi", padx=10, pady=10)
        status_frame.pack(fill="x", padx=20, pady=10)
        
        self.status_label = tk.Label(
            status_frame,
            text="",
            justify="left",
            anchor="w",
        )
        self.status_label.pack(fill="x")
        
        btn_refresh_status = tk.Button(
            status_frame,
            text="🔄 Aggiorna Stato",
            command=self._update_status,
        )
        btn_refresh_status.pack(pady=5)
        
        # Update initial status
        self._update_status()

    def _open_verification_table(self):
        """Apre la VerificationTableWindow."""
        if self.vt_window is not None and self.vt_window.winfo_exists():
            self.vt_window.lift()
            return
        
        self.vt_window = VerificationTableWindow(
            master=self,
            section_repository=self.section_repo,
            material_repository=self.material_repo,
        )

    def _add_random_section(self):
        """Aggiunge una sezione random."""
        import random
        w = random.randint(20, 50)
        h = random.randint(25, 60)
        
        if random.choice([True, False]):
            # Rectangular
            section = RectangularSection(name=f"Rect {w}x{h}", width=w, height=h)
        else:
            # Circular
            d = random.randint(20, 50)
            section = CircularSection(name=f"Circ d={d}", diameter=d)
        
        if self.section_repo.add_section(section):
            messagebox.showinfo("Successo", f"Sezione aggiunta: {section.name}")
            self._update_status()
        else:
            messagebox.showwarning("Attenzione", "Sezione duplicata")

    def _update_first_section(self):
        """Modifica la prima sezione."""
        sections = self.section_repo.get_all_sections()
        if not sections:
            messagebox.showwarning("Attenzione", "Nessuna sezione da modificare")
            return
        
        section = sections[0]
        import random
        w = random.randint(20, 50)
        h = random.randint(25, 60)
        
        updated = RectangularSection(name=f"{section.name} MODIFICATA", width=w, height=h)
        self.section_repo.update_section(section.id, updated)
        
        messagebox.showinfo("Successo", f"Sezione modificata: {updated.name}")
        self._update_status()

    def _delete_first_section(self):
        """Elimina la prima sezione."""
        sections = self.section_repo.get_all_sections()
        if not sections:
            messagebox.showwarning("Attenzione", "Nessuna sezione da eliminare")
            return
        
        section = sections[0]
        self.section_repo.delete_section(section.id)
        
        messagebox.showinfo("Successo", f"Sezione eliminata: {section.name}")
        self._update_status()

    def _add_random_material(self):
        """Aggiunge un materiale random."""
        import random
        
        if random.choice([True, False]):
            # Concrete
            fck = random.choice([20, 25, 30, 35, 40])
            material = Material(
                name=f"C{fck}/{fck+5}",
                type="concrete",
                properties={"fck": fck}
            )
        else:
            # Steel
            fyk = random.choice([400, 450, 500])
            material = Material(
                name=f"B{fyk}C",
                type="steel",
                properties={"fyk": fyk}
            )
        
        self.material_repo.add(material)
        messagebox.showinfo("Successo", f"Materiale aggiunto: {material.name}")
        self._update_status()

    def _update_first_material(self):
        """Modifica il primo materiale."""
        materials = self.material_repo.get_all()
        if not materials:
            messagebox.showwarning("Attenzione", "Nessun materiale da modificare")
            return
        
        material = materials[0]
        updated = Material(
            name=f"{material.name} MODIFICATO",
            type=material.type,
            properties=material.properties,
        )
        
        self.material_repo.update(material.id, updated)
        messagebox.showinfo("Successo", f"Materiale modificato: {updated.name}")
        self._update_status()

    def _delete_first_material(self):
        """Elimina il primo materiale."""
        materials = self.material_repo.get_all()
        if not materials:
            messagebox.showwarning("Attenzione", "Nessun materiale da eliminare")
            return
        
        material = materials[0]
        self.material_repo.delete(material.id)
        
        messagebox.showinfo("Successo", f"Materiale eliminato: {material.name}")
        self._update_status()

    def _update_status(self):
        """Aggiorna lo status label."""
        sections = self.section_repo.get_all_sections()
        materials = self.material_repo.get_all()
        
        status_text = f"Sezioni: {len(sections)}\n"
        for s in sections[:5]:
            status_text += f"  • {s.name}\n"
        if len(sections) > 5:
            status_text += f"  ... e altre {len(sections) - 5}\n"
        
        status_text += f"\nMateriali: {len(materials)}\n"
        for m in materials[:5]:
            status_text += f"  • {m.name}\n"
        if len(materials) > 5:
            status_text += f"  ... e altri {len(materials) - 5}\n"
        
        self.status_label.config(text=status_text)

    def destroy(self):
        """Clean up on close."""
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except Exception:
            pass
        super().destroy()


if __name__ == "__main__":
    print("=" * 70)
    print("DEMO: Auto-Aggiornamento VerificationTable")
    print("=" * 70)
    print("\nAprendo pannello di controllo...")
    print("La VerificationTable si aprirà automaticamente.")
    print("\nUsa i pulsanti per aggiungere/modificare/eliminare")
    print("sezioni e materiali. La VerificationTable si aggiornerà")
    print("automaticamente in tempo reale!")
    print("=" * 70 + "\n")
    
    app = DemoControlPanel()
    app.mainloop()
