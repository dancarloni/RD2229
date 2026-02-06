"""Compatibility shim for legacy imports from `verification_table`.

This module re-exports a small set of stable names from the new `app`
package to preserve backwards compatibility. Implementation has been
moved to `app.domain`, `app.verification` and `app.ui`.
"""

from __future__ import annotations

from typing import List
import logging

logger = logging.getLogger(__name__)
logger.warning("verification_table is deprecated; import from 'app' package (e.g., 'app.domain'/'app.verification'/'app.ui') instead.")

# Re-export common names for backward compatibility
from app.domain.models import VerificationInput, VerificationOutput
from app.domain.sections import get_section_geometry
from app.domain.materials import get_concrete_properties, get_steel_properties
from app.verification.engine_adapter import compute_with_engine
from app.verification.dispatcher import compute_verification_result
from app.verification.methods_ta import compute_ta_verification
from app.verification.methods_slu import compute_slu_verification
from app.verification.methods_sle import compute_sle_verification
from app.ui.verification_table_app import COLUMNS, VerificationTableApp, VerificationTableWindow

__all__: List[str] = [
    "VerificationInput",
    "VerificationOutput",
    "get_section_geometry",
    "get_concrete_properties",
    "get_steel_properties",
    "compute_with_engine",
    "compute_verification_result",
    "compute_ta_verification",
    "compute_slu_verification",
    "compute_sle_verification",
    "VerificationTableApp",
    "VerificationTableWindow",
    "COLUMNS",
]


def run_demo() -> None:
    """Launch the legacy demo window (delegates to new entrypoint)."""
    from app.entrypoints.run_demo import run_demo as _run

    _run()


if __name__ == "__main__":
    run_demo()

# End of compatibility shim. Implementation moved to `app` package.


    def import_csv(self, path: str, *, clear: bool = True):
        """Importa righe da CSV; il file deve essere compatibile con `export_csv()`.

        - Legge con `delimiter=';'` e si aspetta la prima riga come intestazione.
        - Se l'intestazione è una permutazione valida delle intestazioni attese,
          si applica automaticamente il mapping delle colonne (opzione utile
          quando il file ha le colonne nello stesso insieme ma in ordine diverso).
        - Per ogni riga successiva converte i campi numerici sostituendo la
          virgola con il punto prima della conversione a float. Se una riga ha
          valori malformati viene saltata; ogni problema viene loggato in modo
          dettagliato e raccolto nella lista `errors`.

        Restituisce una tupla `(imported_count, skipped_count, errors)` per usi
        programmatici.
        """
        import csv
        try:
            with open(path, newline="", encoding="utf-8") as fh:
                reader = csv.reader(fh, delimiter=";")
                rows = list(reader)
        except Exception as e:
            # Gestione più esplicita dei problemi di lettura/parsing CSV
            logger.exception("Import CSV: impossibile leggere/parsare il file '%s': %s", path, e)
            self._show_error("Importa CSV", [f"Impossibile leggere o parsare il file: {e}"])
            return 0, 0, [str(e)]
        if not rows:
            logger.debug("Import CSV: file vuoto o privo di righe: %s", path)
            return 0, 0, []

        expected_header = [c[1] for c in COLUMNS]
        legacy_header = [
            "Sezione",
            "Metodo verifica",
            "Materiale cls",
            "Materiale acciaio",
            "Coeff. n",
            "N [kg]",
            "M [kg·m]",
            "T [kg]",
            "As' [cm²]",
            "As [cm²]",
            "d' [cm]",
            "d [cm]",
            "Passo staffe [cm]",
            "Diametro staffe [mm]",
            "Materiale staffe",
            "NOTE",
        ]
        header = [h.strip() for h in rows[0]]

        # Prepariamo una mappa da index_file -> index_expected
        index_map: List[Optional[int]] = []
        if header == expected_header:
            index_map = list(range(len(header)))
            logger.debug("Import CSV: header corrisponde all'ordine atteso")
            # Supporto retro-compatibilità: alcuni file di esempio possono omettere
            # la colonna 'Metodo verifica' (seconda colonna). Se rileviamo che tutte
            # le righe hanno una colonna in meno rispetto all'header, applichiamo
            # una correzione semplice inserendo un placeholder None per la colonna
            # 'Metodo verifica' (index 1) in modo da non agganciare per posizione
            row_lengths = [len(r) for r in rows[1:]]
            logger.info("Import CSV: header len=%d row lens sample=%s", len(header), row_lengths[:5])
            if any(l == len(header) - 1 for l in row_lengths):
                logger.info("Import CSV: righe con colonna mancante rilevate; applico correzione per 'Metodo verifica'")
                # shift indices after the missing column (keep Elemento and Sezione aligned)
                missing_idx = expected_header.index("Metodo verifica")
                index_map = []
                for i in range(len(header)):
                    if i == missing_idx:
                        index_map.append(None)
                    elif i < missing_idx:
                        index_map.append(i)
                    else:
                        index_map.append(i - 1)
                logger.debug("Import CSV: index_map corretto: %s", index_map)
        elif header == expected_header[1:]:
            # Legacy files without the first "Elemento" column
            index_map = [None] + list(range(len(header)))
            logger.info("Import CSV: header senza 'Elemento' rilevato, applicato mapping: %s", index_map)
        elif header == legacy_header:
            index_map = []
            for h in expected_header:
                if h == "Mx [kg·m]":
                    index_map.append(header.index("M [kg·m]"))
                elif h == "Ty [kg]":
                    index_map.append(header.index("T [kg]"))
                elif h in ("My [kg·m]", "Mz [kg·m]", "Tx [kg]", "At [cm²]"):
                    index_map.append(None)
                else:
                    index_map.append(header.index(h) if h in header else None)
            logger.info("Import CSV: header legacy rilevato, applicato mapping: %s", index_map)
        else:
            # Se il set delle intestazioni coincide, applichiamo mapping automatico
            if set(header) == set(expected_header) and len(header) == len(expected_header):
                # per ogni expected header cerchiamo l'indice nel file
                index_map = [header.index(h) for h in expected_header]
                logger.info("Import CSV: header in ordine diverso, applicato mapping automatico: %s", index_map)
            else:
                # Supporta file CSV che contengono un sottoinsieme di colonne in ordine
                # atteso (per compatibilità retroattiva). In questo caso creiamo una
                # mappa con indici o None per colonne mancanti.
                if set(header).issubset(set(expected_header)) and len(header) < len(expected_header):
                    index_map = [header.index(h) if h in header else None for h in expected_header]
                    logger.info("Import CSV: header incompleto, applicato mapping parziale: %s", index_map)
                else:
                    logger.error("Import CSV: header non valido. Atteso: %s. Trovato: %s", expected_header, header)
                    header_msg = f"Intestazione CSV non corrisponde all'ordine atteso."
                    details = [f"Atteso: {expected_header}", f"Trovato: {rows[0]}"]
                    self._show_error("Importa CSV", details, header=header_msg)
                    return 0, max(0, len(rows) - 1), ["Header mismatch"]

        key_names = [c[0] for c in COLUMNS]
        numeric_attrs = {
            "n_homog",
            "N",
            "Mx",
            "My",
            "Mz",
            "Tx",
            "Ty",
            "At",
            "As_sup",
            "As_inf",
            "d_sup",
            "d_inf",
            "stirrup_step",
            "stirrup_diameter",
        }

        models: List[VerificationInput] = []
        errors: List[str] = []

        for i, row in enumerate(rows[1:], start=2):  # starting from line 2
            # ricaviamo valori usando la mappa di indici
            vals = []
            for idx in index_map:
                if idx is None:
                    vals.append("")
                else:
                    vals.append(row[idx] if idx < len(row) else "")
            # assicurarsi che la lunghezza corrisponda
            vals = vals + [""] * (len(COLUMNS) - len(vals))

            kwargs: Dict[str, object] = {}
            row_bad = False
            for k, idx in zip(key_names, index_map):
                # Se la colonna non è presente nel file (idx is None) saltiamo e
                # lasciamo il valore di default del dataclass (se presente).
                if idx is None:
                    continue
                # idx is the index in the original row; use it directly instead of
                # indexing into 'vals' which holds shifted values.
                v = row[idx] if idx < len(row) else ""
                attr = self._col_to_attr(k)
                if attr in numeric_attrs:
                    s = str(v).strip()
                    if not s:
                        kwargs[attr] = 0.0
                        continue
                    # sostituisco la virgola con il punto per la conversione
                    normalized = s.replace(",", ".")
                    try:
                        kwargs[attr] = float(normalized)
                    except Exception:
                        msg = f"Riga {i}: valore numerico non valido per '{k}': '{v}'"
                        errors.append(msg)
                        logger.error("Import CSV: %s -- riga content: %s", msg, row)
                        row_bad = True
                        break
                else:
                    kwargs[attr] = v
            if row_bad:
                # salto la riga e continuiamo
                continue
            try:
                models.append(VerificationInput(**kwargs))
            except Exception as e:  # pragma: no cover - difensivo
                msg = f"Riga {i}: errore creazione modello: {e}"
                errors.append(msg)
                logger.exception("Import CSV: %s -- riga content: %s", msg, row)

        # Sostituisco le righe della tabella con i modelli importati
        if clear:
            for item in list(self.tree.get_children()):
                self.tree.delete(item)
        self.set_rows(models)

        imported = len(models)
        skipped = max(0, (len(rows) - 1) - imported)

        # Registriamo un log dettagliato e mostriamo messaggi all'utente se ci sono errori
        if errors:
            logger.error("Import CSV: import completato con errori: %s", errors[:20])
            header_msg = "Si sono verificati errori durante l'import:"
            self._show_error("Importa CSV", errors[:20], header=header_msg)
        else:
            logger.info("Import CSV: import completato senza errori. Importate %d righe", imported)

        return imported, skipped, errors

    def _on_compute_all(self) -> None:
        """Handler per il pulsante 'Calcola tutte le righe'.

        Itera su tutte le righe della tabella, per ciascuna:
        - converte la riga in VerificationInput usando table_row_to_model
        - chiama compute_verification_result per ottenere VerificationOutput
        - colleziona i risultati in una stringa descrittiva
        - mostra un messagebox con l'elenco dei risultati

        In futuro potrebbe anche aggiornare colonne della tabella con i risultati
        (es. esito, coeff_sicurezza, ecc.).
        """
        items = list(self.tree.get_children())
        if not items:
            notify_info("Verifica", "Nessuna riga da verificare.", source="verification_table")
            return

        risultati = []
        for row_idx, item in enumerate(items):
            try:
                model = self.table_row_to_model(row_idx)
            except Exception as e:
                logger.exception("Errore conversione riga %s: %s", row_idx + 1, e)
                risultati.append(f"Riga {row_idx + 1}: ERRORE CONVERSIONE – {e}")
                continue

            try:
                result = compute_verification_result(model, self.section_repository, self.material_repository)
            except Exception as e:
                logger.exception("Errore verifica riga %s: %s", row_idx + 1, e)
                risultati.append(f"Riga {row_idx + 1}: ERRORE CALCOLO – {e}")
                continue

            # Formato: "Riga N [METODO]: esito=..., γ=..."
            metodo = model.verification_method or "?"
            risultati.append(
                f"Riga {row_idx + 1} [{metodo}]: esito={result.esito}, "
                f"γ={result.coeff_sicurezza:.2f}"
            )

        # Mostra risultati in un non-blocking notification
        msg = "\n".join(risultati)
        notify_info("Risultati verifiche", msg, source="verification_table")

    def _open_rebar_calculator(self) -> None:
        if self.edit_entry is None or self.edit_column is None:
            return
        self._rebar_target_column = self.edit_column
        # Set flag to avoid losing the edit when the calculator grabs focus
        self._in_rebar_calculator = True
        if self._rebar_window is not None and self._rebar_window.winfo_exists():
            self._rebar_window.lift()
            self._rebar_window.focus_set()
            if self._rebar_entries:
                self._rebar_entries[0].focus_set()
            return

        win = tk.Toplevel(self)
        win.title("Calcolo area armatura")
        win.resizable(False, False)
        win.transient(self.winfo_toplevel())
        win.grab_set()
        self._rebar_window = win

        frame = tk.Frame(win, padx=10, pady=10)
        frame.pack(fill="both", expand=True)

        diameters = [8, 10, 12, 14, 16, 20, 25]
        self._rebar_vars = {}
        self._rebar_entries = []

        tk.Label(frame, text="Ø (mm)", width=8, anchor="w").grid(row=0, column=0, sticky="w")
        tk.Label(frame, text="n barre", width=8, anchor="w").grid(row=0, column=1, sticky="w")

        for i, d in enumerate(diameters, start=1):
            tk.Label(frame, text=f"Ø{d}", width=8, anchor="w").grid(row=i, column=0, sticky="w", pady=2)
            var = tk.StringVar(value="")
            self._rebar_vars[d] = var
            ent = tk.Entry(frame, textvariable=var, width=8)
            self._rebar_entries.append(ent)
            ent.grid(row=i, column=1, sticky="w", pady=2)
            var.trace_add("write", lambda *_: self._update_rebar_total())
            if i == 1:
                ent.focus_set()

        total_frame = tk.Frame(frame)
        total_frame.grid(row=len(diameters) + 1, column=0, columnspan=2, sticky="w", pady=(8, 4))
        tk.Label(total_frame, text="Area totale [cm²]:").pack(side="left")
        tk.Label(total_frame, textvariable=self._rebar_total_var, width=10, anchor="w").pack(side="left")

        btn_frame = tk.Frame(frame)
        btn_frame.grid(row=len(diameters) + 2, column=0, columnspan=2, sticky="e")
        tk.Button(btn_frame, text="Conferma", command=self._confirm_rebar_total).pack(side="right")

        win.bind("<Escape>", lambda _e: self._close_rebar_window())
        win.bind("<Return>", lambda _e: self._confirm_rebar_total())

        self._update_rebar_total()

    def _update_rebar_total(self) -> None:
        total = 0.0
        for d, var in self._rebar_vars.items():
            try:
                n = int(var.get() or 0)
            except ValueError:
                n = 0
            d_cm = d / 10.0
            area = math.pi * (d_cm ** 2) / 4.0
            total += n * area
        self._rebar_total_var.set(f"{total:.2f}")

    def _confirm_rebar_total(self) -> None:
        if self.edit_entry is None or self._rebar_target_column is None:
            # Fallback: if the entry was closed for some reason, try to set the tree cell directly
            try:
                if self.edit_item and self._rebar_target_column:
                    value = self._rebar_total_var.get()
                    self.tree.set(self.edit_item, self._rebar_target_column, value)
            except Exception:
                logger.exception("Unable to apply rebar total in fallback path")
            self._close_rebar_window()
            return
        value = self._rebar_total_var.get()
        self.edit_entry.delete(0, tk.END)
        self.edit_entry.insert(0, value)
        self._commit_edit()
        self._close_rebar_window()

    def _close_rebar_window(self) -> None:
        if self._rebar_window is not None:
            self._rebar_window.destroy()
        self._rebar_window = None
        self._rebar_entries = []
        # Clear flag after the calculator is closed
        self._in_rebar_calculator = False


# Backwards-compatible alias for the window class — prefer `app.ui.VerificationTableWindow`.
try:
    from app.ui.verification_table_app import VerificationTableWindow as VerificationTableWindow
except Exception:
    VerificationTableWindow = None  # type: ignore


def run_demo() -> None:
    from app.entrypoints.run_demo import run_demo as _run

    _run()


if __name__ == "__main__":
    run_demo()
