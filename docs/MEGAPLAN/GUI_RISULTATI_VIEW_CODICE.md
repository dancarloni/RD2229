
GUI – RisultatiView (Tabella Verifiche)
Status: FILE OPERATIVO – TKINTER (VINCOLANTE)
Questo file definisce la View GUI dei risultati di verifica, responsabile della visualizzazione tabellare degli esiti provenienti dal VerificationEngine.
La View:

è sola lettura;
non contiene alcuna logica normativa o di calcolo;
legge esclusivamente i dati dal ProjectModel;
è compatibile con CAP_4 e CAP_7;
è progettata per l’invio diretto dei risultati alla relazione di calcolo.


1. Responsabilità della RisultatiView
La RisultatiView deve:

visualizzare tutte le verifiche eseguite;
distinguere chiaramente il Capitolo NTC (CAP_4 / CAP_7);
mostrare:nome della verifica;
esito (OK / NOT OK / N.A.);
rapporto Ed/Rd (se applicabile);
consentire l’aggiornamento sincrono dopo l’esecuzione delle verifiche;
non modificare in alcun modo i risultati.


2. Dipendenze (vincolanti)
Questa View presuppone l’esistenza di:

ProjectModelverifiche_cap4: list[VerificationResult]
verifiche_cap7: list[VerificationResult]
VerificationResult
VerificationStatus
NTCCapitol


3. Codice – gui/views/risultati.py

import tkinter as tk
from tkinter import ttk


class RisultatiView(ttk.Frame):
    """
    View di sola lettura per la visualizzazione
    dei risultati delle verifiche strutturali
    (CAP_4 e CAP_7).
    """

    def __init__(self, parent, project_model):
        super().__init__(parent)
        self.project_model = project_model
        self._build_ui()

    # --------------------------------------------------
    # UI BUILD
    # --------------------------------------------------

    def _build_ui(self):
        frame = ttk.LabelFrame(self, text="Risultati verifiche")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = (
            "verifica",
            "capitolo",
            "esito",
            "ratio",
        )

        self.tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            selectmode="browse",
        )

        self.tree.heading("verifica", text="Verifica")
        self.tree.heading("capitolo", text="Capitolo NTC")
        self.tree.heading("esito", text="Esito")
        self.tree.heading("ratio", text="Ed/Rd")

        self.tree.column("verifica", width=320)
        self.tree.column("capitolo", width=120, anchor="center")
        self.tree.column("esito", width=90, anchor="center")
        self.tree.column("ratio", width=90, anchor="center")

        self.tree.pack(fill="both", expand=True)

        btn_refresh = ttk.Button(
            frame,
            text="Aggiorna risultati ▶",
            command=self.refresh,
        )
        btn_refresh.pack(pady=5)

    # --------------------------------------------------
    # DATA REFRESH
    # --------------------------------------------------

    def refresh(self):
        """
        Ricarica i risultati dal ProjectModel.
        """
        for row in self.tree.get_children():
            self.tree.delete(row)

        results = []
        results.extend(self.project_model.verifiche_cap4)
        results.extend(self.project_model.verifiche_cap7)

        for r in results:
            self.tree.insert(
                "",
                "end",
                values=(
                    r.reference.paragrafo,
                    r.capitolo_ntc.value,
                    r.status.value,
                    f"{r.ratio:.3f}" if r.ratio is not None else "—",
                ),
            )




4. Integrazione con main.py
Nel file GUI_MAIN_PY_NAVIGAZIONE.md, la View è già correttamente istanziata:

self.views["risultati"] = RisultatiView(
    self.container,
    self.project_model,
)


Dopo l’esecuzione delle verifiche:

self.verification_binding.run_verifications()
self.show_view("risultati")


l’utente può aggiornare la tabella tramite il pulsante Aggiorna risultati ▶.


5. Regole di sicurezza normativa

nessuna modifica dei risultati è consentita;
nessuna verifica viene eseguita dalla View;
i risultati sono sempre marcati con il Capitolo NTC;
la View non interpreta l’esito (nessuna logica OK/NO).


6. Stato finale
✅ View risultati completa ✅ Allineata al ProjectModel ✅ Integrata nel workflow GUI ✅ Pronta per esportazione in relazione di calcolo


Questo file è vincolante per la visualizzazione dei risultati di verifica nel software NTC2018.
