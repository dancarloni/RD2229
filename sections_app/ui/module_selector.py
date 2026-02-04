from __future__ import annotations

import logging
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Callable, Optional
from pathlib import Path

from sections_app.ui.main_window import MainWindow
from sections_app.ui.historical_main_window import HistoricalModuleMainWindow
from verification_table import VerificationTableWindow
from sections_app.services.repository import CsvSectionSerializer, SectionRepository
from core_models.materials import MaterialRepository

logger = logging.getLogger(__name__)


class ModuleSelectorWindow(tk.Tk):
    """Finestra iniziale per selezionare il modulo da avviare."""

    def __init__(
        self,
        repository: SectionRepository,
        serializer: CsvSectionSerializer,
        material_repository: Optional[MaterialRepository] = None,
    ):
        super().__init__()
        self.title("Module Selector - RD2229 Tools")
        self.geometry("820x260")
        self.repository = repository
        self.serializer = serializer
        # For compatibility with modules expecting named attributes
        self.section_repository: SectionRepository = repository
        # Usa il material_repository passato, oppure creane uno nuovo
        self.material_repository: MaterialRepository = material_repository or MaterialRepository()
        self._create_menu()
        self._build_ui()

    def _create_menu(self) -> None:
        """Crea il menu della finestra."""
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # Menu File
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Esporta backup...", command=self._export_backup)
        file_menu.add_separator()
        file_menu.add_command(label="Esci", command=self.quit)

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

        verify_frame = tk.LabelFrame(modules_frame, text="Verification Table")
        verify_frame.pack(side="left", fill="both", expand=True, padx=(6, 0))
        tk.Label(
            verify_frame,
            text="Rapid data entry for multiple verifications\n(tabular grid with autocomplete)",
            justify="left",
        ).pack(padx=8, pady=8)
        tk.Button(verify_frame, text="Open Verification Table", command=self._open_verification_table).pack(
            pady=(0, 8)
        )

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

    def _open_verification_table(self) -> None:
        logger.debug("Opening Verification Table module")
        self.withdraw()
        win = VerificationTableWindow(
            master=self,
            section_repository=self.section_repository,
            material_repository=self.material_repository,
        )
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

    def _export_backup(self) -> None:
        """Gestisce l'esportazione del backup."""
        # Chiedi all'utente cosa esportare
        dialog = tk.Toplevel(self)
        dialog.title("Esporta backup")
        dialog.geometry("400x200")
        dialog.transient(self)
        dialog.grab_set()
        
        result = {"choice": None}
        
        def on_choice(choice: str):
            result["choice"] = choice
            dialog.destroy()
        
        frame = tk.Frame(dialog, padx=20, pady=20)
        frame.pack(fill="both", expand=True)
        
        tk.Label(
            frame,
            text="Cosa vuoi esportare?",
            font=(None, 11, "bold")
        ).pack(pady=(0, 20))
        
        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=10)
        
        tk.Button(
            btn_frame,
            text="Sezioni",
            width=15,
            command=lambda: on_choice("sezioni")
        ).pack(pady=5)
        
        tk.Button(
            btn_frame,
            text="Materiali",
            width=15,
            command=lambda: on_choice("materiali")
        ).pack(pady=5)
        
        tk.Button(
            btn_frame,
            text="Entrambi",
            width=15,
            command=lambda: on_choice("entrambi")
        ).pack(pady=5)
        
        tk.Button(
            btn_frame,
            text="Annulla",
            width=15,
            command=dialog.destroy
        ).pack(pady=5)
        
        # Aspetta che l'utente scelga
        self.wait_window(dialog)
        
        if not result["choice"]:
            return
        
        # Determina il nome file predefinito e i filtri
        if result["choice"] == "sezioni":
            default_name = "backup_sezioni"
            filetypes = [
                ("JSON files", "*.json"),
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        elif result["choice"] == "materiali":
            default_name = "backup_materiali"
            filetypes = [
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        else:  # entrambi
            default_name = "backup"
            filetypes = [
                ("JSON files", "*.json"),
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        
        # Mostra il dialogo di salvataggio
        file_path = filedialog.asksaveasfilename(
            parent=self,
            title="Esporta backup",
            defaultextension=".json",
            initialfile=default_name,
            filetypes=filetypes
        )
        
        if not file_path:
            return
        
        # Esegui l'esportazione
        try:
            if result["choice"] == "sezioni":
                self.section_repository.export_backup(file_path)
                messagebox.showinfo(
                    "Export completato",
                    f"Backup sezioni esportato correttamente in:\n{file_path}",
                    parent=self
                )
            elif result["choice"] == "materiali":
                self.material_repository.export_backup(file_path)
                messagebox.showinfo(
                    "Export completato",
                    f"Backup materiali esportato correttamente in:\n{file_path}",
                    parent=self
                )
            else:  # entrambi
                # Salva in due file separati
                path_obj = Path(file_path)
                base_name = path_obj.stem
                extension = path_obj.suffix
                parent_dir = path_obj.parent
                
                # File sezioni
                sections_path = parent_dir / f"{base_name}_sezioni{extension}"
                self.section_repository.export_backup(sections_path)
                
                # File materiali
                materials_path = parent_dir / f"{base_name}_materiali.json"
                self.material_repository.export_backup(materials_path)
                
                messagebox.showinfo(
                    "Export completato",
                    f"Backup esportati correttamente:\n"
                    f"• Sezioni: {sections_path}\n"
                    f"• Materiali: {materials_path}",
                    parent=self
                )
        except Exception as e:
            logger.exception("Errore durante l'esportazione del backup")
            messagebox.showerror(
                "Errore",
                f"Errore durante l'esportazione:\n{str(e)}",
                parent=self
            )

