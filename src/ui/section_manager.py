from __future__ import annotations

import logging
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Callable, Dict, Optional, Tuple

from sections_app.models.sections import CSV_HEADERS, Section  # type: ignore[import]
from sections_app.services.event_bus import (
    SECTIONS_ADDED,
    SECTIONS_CLEARED,
    SECTIONS_DELETED,
    SECTIONS_UPDATED,
    EventBus,
)
from sections_app.services.notification import (
    ask_confirm,
    notify_info,
)
from sections_app.services.repository import CsvSectionSerializer, SectionRepository  # type: ignore[import]

logger = logging.getLogger(__name__)

# Pylint: UI code here uses protected access for interop and broad exception
# handling for robustness; suppress these noisy warnings when not actionable.
# pylint: disable=broad-exception-caught, protected-access, unused-argument, logging-fstring-interpolation


class TreeviewTooltip:
    """Gestisce tooltip su celle del Treeview al passaggio del mouse."""

    def __init__(self, tree: ttk.Treeview):
        self.tree = tree
        self.tipwindow: Optional[tk.Toplevel] = None
        self.current_item: Optional[str] = None
        self.current_column: Optional[str] = None

        self.tree.bind("<Motion>", self.on_motion)
        self.tree.bind("<Leave>", self.on_leave)

    def on_motion(self, event: tk.Event) -> None:
        row_id = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)
        if not row_id or not col_id:
            self.hide_tip()
            return

        if (row_id, col_id) == (self.current_item, self.current_column):
            return

        self.current_item, self.current_column = row_id, col_id

        # Converti col_id (es. "#1", "#2") in nome colonna
        columns = list(self.tree["columns"])
        try:
            col_index = int(col_id.replace("#", "")) - 1
            if 0 <= col_index < len(columns):
                col_name = columns[col_index]
                value = self.tree.set(row_id, col_name)
            else:
                value = ""
        except Exception:
            value = ""

        if not value:
            self.hide_tip()
            return

        self.show_tip(value, event.x_root + 10, event.y_root + 10)

    def show_tip(self, text: str, x: int, y: int) -> None:
        self.hide_tip()
        self.tipwindow = tw = tk.Toplevel(self.tree)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw,
            text=text,
            background="lightyellow",
            relief="solid",
            borderwidth=1,
            justify="left",
        )
        label.pack(ipadx=2, ipady=1)

    def hide_tip(self) -> None:
        if self.tipwindow is not None:
            self.tipwindow.destroy()
            self.tipwindow = None
            self.current_item = None
            self.current_column = None

    def on_leave(self, event: tk.Event) -> None:
        self.hide_tip()


def sort_treeview(tree: ttk.Treeview, col: str, reverse: bool) -> None:
    """Ordina il Treeview per colonna. Supporta numeri e stringhe.

    Rileva automaticamente il tipo di dato (numerico o testuale) e ordina di conseguenza.
    Il click ripetuto alterna l'ordinamento crescente/decrescente.

    Args:
        tree: Il Treeview da ordinare
        col: Nome della colonna su cui ordinare
        reverse: True per ordinamento decrescente

    """
    data = [(tree.set(item, col), item) for item in tree.get_children("")]

    def try_num(value: str) -> float | str:
        """Tenta di convertire il valore a numero, altrimenti lo mantiene stringa."""
        if value == "":
            return ""
        try:
            return float(value.replace(",", "."))
        except (ValueError, AttributeError):
            return value

    # Ordina con key che gestisce sia numeri che stringhe
    data.sort(key=lambda t: (isinstance(try_num(t[0]), str), try_num(t[0])), reverse=reverse)

    # Ricrea l'ordine delle righe nel Treeview
    for index, (_, item) in enumerate(data):
        tree.move(item, "", index)

    # Aggiorna il heading con il nuovo ordinamento alternato
    tree.heading(col, command=lambda: sort_treeview(tree, col, not reverse))


class SectionManager(tk.Toplevel):
    """📊 FINESTRA DI GESTIONE ARCHIVIO SEZIONI - Visualizzazione Completa e Auto-Refresh.

    Responsabilità:
    - VISUALIZZAZIONE: Mostra tutte le proprietà geometriche e calcolate in tabella ottimizzata
    - AUTO-REFRESH: Si aggiorna automaticamente quando il repository cambia (via EventBus)
    - ORDINAMENTO: Click su intestazioni per ordinare colonne (crescente/decrescente)
    - TOOLTIP: Mostra valori completi al passaggio del mouse su celle lunghe
    - IMPORT/EXPORT: Compatibilità CSV mantenuta per interoperabilità
    - RESTA APERTA: Dopo "Nuova sezione", il manager rimane aperto per operazioni multiple

    🎯 RESPONSABILITÀ
    --------------
    Il Section Manager è un **semplice visualizzatore/gestore** dell'archivio sezioni:
    - NON contiene dati hard coded delle sezioni
    - Legge/scrive SEMPRE tramite `SectionRepository` (unico punto di accesso ai dati)
    - Si aggiorna automaticamente quando le sezioni cambiano (grazie all'EventBus)

    🔄 AGGIORNAMENTO AUTOMATICO
    --------------------------
    Quando una sezione viene salvata dal Geometry Module, il repository emette un evento.
    Questo manager si sottoscrive agli eventi e ricarica automaticamente la lista.
    Eventi gestiti: SECTIONS_ADDED, SECTIONS_UPDATED, SECTIONS_DELETED, SECTIONS_CLEARED

    📂 PERSISTENZA DATI
    ------------------
    Tutti i dati delle sezioni sono salvati in `sections.json` tramite `SectionRepository`.
    La struttura JSON è estendibile: ogni sezione è un dizionario con campi geometrici
    e proprietà calcolate (area, baricentro, momenti di inerzia, ecc.).
    """

    def __init__(
        self,
        master: tk.Tk,
        repository: SectionRepository,
        serializer: CsvSectionSerializer,
        on_edit: Callable[[Section], None],
    ) -> None:
        super().__init__(master)
        self.title("Archivio Sezioni - Visualizzazione Completa")

        # ✅ REPOSITORY: unico punto di accesso ai dati delle sezioni
        # Gestisce caricamento/salvataggio da/verso sections.json, backup, validazione
        self.repository = repository
        self.serializer = serializer
        self.on_edit = on_edit

        # Traccia se il sorting è stato mai toccato per la colonna corrente
        self._sort_state: Dict[str, bool] = {}

        # ✅ AUTO-REFRESH: sottoscrizione agli eventi del repository
        # Quando il Geometry Module salva/modifica/elimina una sezione, il repository
        # emette un evento e questo manager ricarica automaticamente la lista
        self._event_bus = EventBus()
        self._event_bus.subscribe(SECTIONS_ADDED, self._on_sections_changed)
        self._event_bus.subscribe(SECTIONS_UPDATED, self._on_sections_changed)
        self._event_bus.subscribe(SECTIONS_DELETED, self._on_sections_changed)
        self._event_bus.subscribe(SECTIONS_CLEARED, self._on_sections_changed)

        # Assicura cleanup quando la finestra viene chiusa
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.bind("<Destroy>", self._on_destroy)

        self._build_ui()
        self._refresh_table()

    def _on_sections_changed(self, *args, **kwargs) -> None:
        """Callback chiamato dall'EventBus quando le sezioni cambiano nel repository.

        Questo metodo ricarica automaticamente la lista delle sezioni nella Treeview,
        così l'utente vede sempre i dati aggiornati senza dover riaprire la finestra.
        """
        logger.debug("Section Manager riceve notifica di cambio dati, ricarico la lista")
        self.refresh_sections()

    def _on_close(self) -> None:
        """Handler per la chiusura della finestra via protocollo WM_DELETE_WINDOW."""
        self._cleanup_event_subscriptions()
        self.destroy()

    def _on_destroy(self, event=None) -> None:
        """Handler per l'evento <Destroy> della finestra."""
        # Assicura cleanup anche se la finestra viene distrutta in altro modo
        if event is None or event.widget == self:
            self._cleanup_event_subscriptions()

    def _cleanup_event_subscriptions(self) -> None:
        """Rimuove le sottoscrizioni agli eventi per evitare memory leak.

        Quando la finestra viene chiusa, è importante disiscriversi dall'EventBus
        per evitare che il callback venga chiamato su una finestra distrutta.
        """
        try:
            self._event_bus.unsubscribe(SECTIONS_ADDED, self._on_sections_changed)
            self._event_bus.unsubscribe(SECTIONS_UPDATED, self._on_sections_changed)
            self._event_bus.unsubscribe(SECTIONS_DELETED, self._on_sections_changed)
            self._event_bus.unsubscribe(SECTIONS_CLEARED, self._on_sections_changed)
            logger.debug("Section Manager: cleanup sottoscrizioni eventi completato")
        except Exception as e:
            logger.debug("Errore durante cleanup sottoscrizioni eventi: %s", e)

    def _build_ui(self) -> None:
        """Costruisce l'interfaccia della finestra con Treeview e bottoni."""
        # Frame principale per il treeview con scrollbar
        tree_frame = tk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=8, pady=8)

        # Scrollbar orizzontale e verticale
        xscroll = tk.Scrollbar(tree_frame, orient="horizontal")
        xscroll.pack(side="bottom", fill="x")

        yscroll = tk.Scrollbar(tree_frame, orient="vertical")
        yscroll.pack(side="right", fill="y")

        # Determina le colonne dinamicamente da un esempio di sezione (to_dict)
        sections_list = self.repository.get_all_sections()
        if sections_list:
            sample = sections_list[0].to_dict()
            # Manteniamo ordine con 'id','name','section_type' iniziali quando presenti
            self.columns = list(sample.keys())
        else:
            # Fallback alle HEADERS predefinite se archivio vuoto
            self.columns = list(CSV_HEADERS)
        logger.debug("Colonne Treeview: %s", self.columns)

        # Creazione Treeview con tutte le colonne
        self.tree = ttk.Treeview(
            tree_frame,
            columns=self.columns,
            show="headings",
            height=14,
            xscrollcommand=xscroll.set,
            yscrollcommand=yscroll.set,
        )
        xscroll.config(command=self.tree.xview)
        yscroll.config(command=self.tree.yview)
        self.tree.pack(fill="both", expand=True)

        # Mappa colonne a larghezze minime e anchor
        col_config: Dict[str, Tuple[int, str]] = {
            "id": (0, "w"),  # invisibile
            "name": (100, "w"),  # nome sezione (sinistra)
            "section_type": (90, "center"),  # tipo sezione
            "width": (65, "center"),  # b (cm)
            "height": (65, "center"),  # h (cm)
            "diameter": (65, "center"),  # d (cm)
            "flange_width": (70, "center"),  # bf (cm)
            "flange_thickness": (70, "center"),  # hf (cm)
            "web_thickness": (70, "center"),  # bw (cm)
            "web_height": (70, "center"),  # hw (cm)
            "t_horizontal": (70, "center"),  # t horizontal (cm)
            "t_vertical": (70, "center"),  # t vertical (cm)
            "outer_diameter": (70, "center"),  # outer diameter (cm)
            "thickness": (70, "center"),  # thickness (cm)
            "rotation_angle_deg": (70, "center"),  # rotation angle (deg)
            "area": (75, "center"),  # Area (cm²)
            "A_y": (75, "center"),  # A_y (cm²)
            "A_z": (75, "center"),  # A_z (cm²)
            "kappa_y": (60, "center"),  # kappa_y (unitless)
            "kappa_z": (60, "center"),  # kappa_z (unitless)
            "x_G": (65, "center"),  # x_G (cm)
            "y_G": (65, "center"),  # y_G (cm)
            "Ix": (80, "center"),  # Ix (cm⁴)
            "Iy": (80, "center"),  # Iy (cm⁴)
            "Ixy": (75, "center"),  # Ixy (cm⁴)
            # Principali inerzie e valori derivati
            "I1": (80, "center"),  # I1 (cm⁴)
            "I2": (80, "center"),  # I2 (cm⁴)
            "principal_angle_deg": (70, "center"),  # angolo (deg)
            "principal_rx": (65, "center"),  # rx principale (cm)
            "principal_ry": (65, "center"),  # ry principale (cm)
            "Qx": (70, "center"),  # Qx (cm³)
            "Qy": (70, "center"),  # Qy (cm³)
            "rx": (65, "center"),  # rx (cm)
            "ry": (65, "center"),  # ry (cm)
            "core_x": (70, "center"),  # x nocciolo (cm)
            "core_y": (70, "center"),  # y nocciolo (cm)
            "ellipse_a": (75, "center"),  # a ellisse (cm)
            "ellipse_b": (75, "center"),  # b ellisse (cm)
            "note": (120, "w"),  # note/commenti
        }

        # Mappa colonne a etichette di intestazione leggibili
        header_labels: Dict[str, str] = {
            "id": "",
            "name": "Nome Sezione",
            "section_type": "Tipo",
            "width": "b (cm)",
            "height": "h (cm)",
            "diameter": "d (cm)",
            "flange_width": "bf (cm)",
            "flange_thickness": "hf (cm)",
            "web_thickness": "bw (cm)",
            "web_height": "hw (cm)",
            "t_horizontal": "t horizontal (cm)",
            "t_vertical": "t vertical (cm)",
            "outer_diameter": "outer d (cm)",
            "thickness": "thickness (cm)",
            "rotation_angle_deg": "rot (deg)",
            "area": "Area (cm²)",
            "A_y": "A_y (cm²)",
            "A_z": "A_z (cm²)",
            "kappa_y": "κ_y",
            "kappa_z": "κ_z",
            "x_G": "x_G (cm)",
            "y_G": "y_G (cm)",
            "Ix": "Ix (cm⁴)",
            "Iy": "Iy (cm⁴)",
            "Ixy": "Ixy (cm⁴)",
            "Qx": "Qx (cm³)",
            "Qy": "Qy (cm³)",
            "rx": "rx (cm)",
            "ry": "ry (cm)",
            "core_x": "x nocciolo (cm)",
            "core_y": "y nocciolo (cm)",
            "ellipse_a": "a ellisse (cm)",
            "ellipse_b": "b ellisse (cm)",
            "note": "Note",
        }

        # Configura ogni colonna
        for col in self.columns:
            width, anchor = col_config.get(col, (70, "center"))
            label = header_labels.get(col, col)

            if col == "id":
                # Colonna ID: completamente invisibile
                self.tree.column(col, width=0, minwidth=0, stretch=False)
                self.tree.heading(col, text="")
            else:
                # Colonne visibili: larghezza stretta, anchor appropriato, no stretch
                self.tree.column(col, width=width, minwidth=width, anchor=anchor, stretch=False)
                # Heading cliccabile per sorting (inizia sempre con False=crescente)
                self.tree.heading(col, text=label, command=lambda c=col: self._on_heading_click(c))

        # Tooltip per le celle
        self.tooltip = TreeviewTooltip(self.tree)

        # OBIETTIVO 1: Calcola larghezza finestra sommando le colonne + margini
        try:
            total_col_width = sum(self.tree.column(col, option="width") for col in self.columns)
            margin = 40  # padx + scrollbar + buffer
            calculated_width = max(total_col_width + margin, 800)
            self.geometry(f"{calculated_width}x550")
            logger.debug(f"Finestra dimensionata: {calculated_width}x550")
        except Exception as e:
            logger.debug(f"Larghezza dinamica fallita: {e}")
            self.geometry("1600x550")

        # Frame per i pulsanti di azione
        buttons_frame = tk.Frame(self)
        buttons_frame.pack(fill="x", padx=8, pady=(0, 8))

        tk.Button(buttons_frame, text="Nuova sezione", command=self._new_section).pack(side="left", padx=4)
        tk.Button(buttons_frame, text="Modifica", command=self._edit_section).pack(side="left", padx=4)
        tk.Button(buttons_frame, text="Elimina", command=self._delete_section).pack(side="left", padx=4)
        tk.Button(buttons_frame, text="Importa CSV", command=self._import_csv).pack(side="left", padx=4)
        tk.Button(buttons_frame, text="Esporta CSV", command=self._export_csv).pack(side="left", padx=4)

    def _on_heading_click(self, col: str) -> None:
        """Handler per il click su un intestazione: alterna ordinamento crescente/decrescente.

        Mantiene stato di toggle per ogni colonna per permettere ordinamenti alternati.

        Args:
            col: Nome della colonna cliccata

        """
        # Se è la prima volta che clicchiamo questa colonna, iniziamo con False (crescente)
        current_state = self._sort_state.get(col, False)
        self._sort_state[col] = not current_state
        sort_treeview(self.tree, col, not current_state)

    def _refresh_table(self) -> None:
        """Svuota il Treeview e lo ricarica con tutte le sezioni dall'archivio.

        Legge i dati da `section.to_dict()` per ottenere tutti i campi, inclusi
        i valori calcolati (area, baricentro, momenti di inerzia, ecc.).
        """
        # Rimuove tutti gli elementi esistenti
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Aggiunge tutte le sezioni come righe nel Treeview
        for section in self.repository.get_all_sections():
            data_dict = section.to_dict()
            # Estrae i valori nell'ordine delle colonne, lasciando vuoto se non presente
            values = [data_dict.get(col, "") for col in self.columns]
            # Usa l'ID della sezione come id della riga (per identificarla dopo)
            self.tree.insert("", "end", iid=section.id, values=values)

        logger.debug("Treeview ricaricato con %d sezioni", len(self.tree.get_children()))

    def refresh_sections(self) -> None:
        """✅ REFRESH MANUALE: ricarica tutte le sezioni dal repository e aggiorna la GUI.

        Questo metodo è il punto centrale per aggiornare la visualizzazione:
        - Legge tutte le sezioni dal repository (che le carica da sections.json)
        - Svuota il widget Treeview
        - Ripopola il widget con i dati aggiornati

        Viene chiamato:
        - All'apertura della finestra (inizializzazione)
        - Automaticamente quando il repository emette eventi di modifica dati
        - Manualmente dopo operazioni locali (import CSV, delete)

        Uso da altre parti del codice:
        - section_manager.refresh_sections()  # dopo aver modificato i dati
        """
        self._refresh_table()

    def reload_sections_in_treeview(self) -> None:
        """Public API legacy: alias per refresh_sections()."""
        self.refresh_sections()

    def _get_selected_section(self) -> Optional[Section]:
        selected = self.tree.focus()
        if not selected:
            notify_info("Info", "Seleziona una sezione", source="section_manager")
            return None
        return self.repository.find_by_id(selected)

    def _new_section(self) -> None:
        """✅ CREA NUOVA SEZIONE: apre il Geometry Module per creare una nuova sezione.

        COMPORTAMENTO CHIAVE:
        - Il Section Manager rimane aperto e attivo
        - Il Geometry Module si apre/va in primo piano
        - Quando l'utente salva la nuova sezione dal Geometry Module:
          → il repository emette un evento SECTIONS_ADDED
          → questo manager riceve l'evento e ricarica automaticamente la lista
          → l'utente vede la nuova sezione apparire senza dover riaprire il manager

        NOTA: NON chiude il Section Manager (a differenza del comportamento precedente).
        """
        # Try multiple strategies to open/reset the geometry editor. Each helper
        # encapsulates one approach and returns True when it handled the request.
        if self._try_reset_master_form():
            return
        if self._try_open_geometry_from_master():
            return
        # Final fallback: ask user confirmation to open editor
        try:
            self._ask_and_open_geometry()
        except Exception:
            logger.exception("Errore mostrando dialogo fallback per nuova sezione")

    def _try_reset_master_form(self) -> bool:
        try:
            if hasattr(self.master, "reset_form") and callable(getattr(self.master, "reset_form")):
                try:
                    self.master.reset_form()
                    try:
                        self.master.lift()
                        self.master.focus_force()
                    except Exception:
                        pass
                    logger.debug("Reset form Geometry per nuova sezione (manager resta aperto)")
                    return True
                except Exception:
                    logger.exception("Errore nel resettare la form del master per nuova sezione")
        except Exception:
            logger.exception("Errore nel controllare reset_form sul master")
        return False

    def _try_open_geometry_from_master(self) -> bool:
        try:
            if hasattr(self.master, "_open_geometry") and callable(getattr(self.master, "_open_geometry")):
                try:
                    self.master._open_geometry()
                    gw = getattr(self.master, "_geometry_window", None)
                    if gw is not None and hasattr(gw, "reset_form") and callable(getattr(gw, "reset_form")):
                        try:
                            gw.reset_form()
                            try:
                                gw.lift()
                                gw.focus_force()
                            except Exception:
                                pass
                            logger.debug("Aperto Geometry per nuova sezione (manager resta aperto)")
                            return True
                        except Exception:
                            logger.exception("Errore nel resettare la form di Geometry dopo apertura da ModuleSelector")
                except Exception:
                    logger.exception("Errore aprendo Geometry dal master per nuova sezione")
        except Exception:
            logger.exception("Errore nel controllare _open_geometry sul master")
        return False

    def _ask_and_open_geometry(self) -> None:

        def _on_confirm_open_editor(ans: bool):
            if not ans:
                return
            try:
                if hasattr(self.master, "_open_geometry") and callable(getattr(self.master, "_open_geometry")):
                    self.master._open_geometry()
                    gw = getattr(self.master, "_geometry_window", None)
                    if gw is not None and hasattr(gw, "reset_form"):
                        try:
                            gw.reset_form()
                            gw.lift()
                            gw.focus_force()
                        except Exception:
                            logger.exception("Errore nel resettare la form di Geometry (fallback)")
                    logger.debug("Aperto Geometry per nuova sezione (fallback, manager resta aperto)")
            except Exception:
                logger.exception("Errore nel fallback per aprire l'editor per nuova sezione")

        ask_confirm(
            "Apri editor",
            "Vuoi aprire l'editor per creare una nuova sezione?",
            callback=_on_confirm_open_editor,
            source="section_manager",
        )

    def _edit_section(self) -> None:
        section = self._get_selected_section()
        if not section:
            return
        self.on_edit(section)
        self.destroy()

    def _delete_section(self) -> None:
        section = self._get_selected_section()
        if not section:
            return
        confirm_msg = (
            f"Sei sicuro di voler eliminare la sezione '{section.name}'?\n\n"
            f"Tipo: {section.section_type}\n"
            f"ID: {section.id}\n\n"
            f"Questa operazione non può essere annullata."
        )

        def _on_confirm_delete(ans: bool):
            if not ans:
                return
            try:
                self.repository.delete_section(section.id)
                self.refresh_sections()
                notify_info(
                    "Eliminazione",
                    f"Sezione '{section.name}' eliminata dall'archivio.",
                    source="section_manager",
                )
                logger.debug("Sezione eliminata tramite UI: %s", section.id)
            except Exception:
                logger.exception("Errore eliminazione sezione dopo conferma")

        try:
            ask_confirm(
                "Conferma eliminazione",
                confirm_msg,
                callback=_on_confirm_delete,
                source="section_manager",
            )
        except Exception:
            logger.exception("Errore mostrando conferma eliminazione")

    def _import_csv(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Importa CSV",
            filetypes=[("CSV", "*.csv"), ("Tutti i file", "*.*")],
        )
        if not file_path:
            return
        sections = self.serializer.import_from_csv(file_path)
        added = 0
        for section in sections:
            if self.repository.add_section(section):
                added += 1
        notify_info("Importa CSV", f"Importate {added} sezioni", source="section_manager")
        self.refresh_sections()
        logger.debug("Import CSV completato: %s sezioni aggiunte", added)

    def _export_csv(self) -> None:
        file_path = filedialog.asksaveasfilename(
            title="Esporta CSV",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
        )
        if not file_path:
            return
        self.serializer.export_to_csv(file_path, self.repository.get_all_sections())
        messagebox.showinfo("Esporta CSV", "Esportazione completata")
