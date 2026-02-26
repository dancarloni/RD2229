
GUI – Selezione delle Verifiche da Includere nella Relazione
Status: FILE OPERATIVO – ESTENSIONE GUI (VINCOLANTE)
Questo documento definisce l’estensione della GUI dei risultati per consentire la selezione esplicita delle verifiche da includere nella relazione di calcolo, sia per NTC2018 sia per R.D. 2229/1939.
La selezione delle verifiche:

non altera i risultati di calcolo;
non introduce logica normativa;
governa esclusivamente il contenuto della relazione finale;
opera tramite l’oggetto centrale ProjectModel.


1. Principio fondamentale (hard rule)


La GUI seleziona, il ReportBuilder riporta.



La GUI decide quali verifiche includere;
Il ReportBuilder decide come riportarle (senza ricalcoli);
Il Core di verifica resta completamente invariato.


2. Integrazione nel ProjectModel (vincolante)
File coinvolto

project_model.py
Attributo obbligatorio

class ProjectModel:
    def __init__(self):
        ...
        # verifiche selezionate per la relazione
        self.verifiche_in_relazione: list = []


Questo attributo è:

popolato dalla GUI;
letto dai ReportBuilder (NTC2018 / RD2229);
lasciato vuoto se si desidera includere tutte le verifiche.


3. Comportamento funzionale

Dopo l’esecuzione delle verifiche, tutte le verifiche sono selezionate di default;
L’utente può:deselezionare singole verifiche;
deselezionare gruppi (per normativa o tipologia);
Ogni modifica aggiorna in tempo reale project_model.verifiche_in_relazione.


4. Estensione della RisultatiView
File GUI coinvolto

gui/views/risultati.py
La RisultatiView viene estesa introducendo:

una checkbox per ogni riga di verifica;
un mapping tra riga GUI e oggetto VerificationResult.


5. Modello di interazione GUI
Mockup logico

┌─────────────────────────────────────────────┐
│ ☑  Pressoflessione – Trave T1   CAP_4   OK  │
│ ☑  Taglio – Trave T1            CAP_4   OK  │
│ ☑  Pressoflessione – Pilastro P1 RD2229 OK │
│ ☐  Trazione – Tirante S1        RD2229 NO │
└─────────────────────────────────────────────┘




6. Codice – Estensione RisultatiView

import tkinter as tk
from tkinter import ttk


class RisultatiView(ttk.Frame):
    def __init__(self, parent, project_model):
        super().__init__(parent)
        self.project_model = project_model
        self._selection = {}
        self._build_ui()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())

        results = (
            self.project_model.verifiche_cap4
            + self.project_model.verifiche_cap7
            + getattr(self.project_model, 'verifiche_rd2229', [])
        )

        self._selection.clear()

        for r in results:
            var = tk.BooleanVar(value=True)
            self._selection[r] = var

            self.tree.insert(
                "",
                "end",
                values=(
                    var.get(),
                    r.reference.paragrafo,
                    r.capitolo_ntc,
                    r.status,
                    r.ratio,
                ),
            )

        self._update_project_model()

    def _update_project_model(self):
        self.project_model.verifiche_in_relazione = [
            r for r, v in self._selection.items() if v.get()
        ]




7. Flusso dati completo

VerificationEngine
        ↓
VerificationResult[*]
        ↓
RisultatiView (checkbox)
        ↓
ProjectModel.verifiche_in_relazione
        ↓
ReportBuilder (NTC2018 / RD2229)
        ↓
Relazione di calcolo




8. Integrazione con i ReportBuilder
I ReportBuilder (NTC2018 e RD2229) utilizzano sempre la stessa logica:

results = pm.verifiche_in_relazione or risultati_completi



se verifiche_in_relazione è vuoto → tutte le verifiche;
se è popolato → solo quelle selezionate.


9. Regole di sicurezza

se nessuna verifica è selezionata → errore bloccante;
la selezione non modifica i risultati;
la selezione è completamente tracciabile;
la relazione risultante è sempre coerente con la normativa attiva.


10. Stato finale
✅ Selezione verifiche in GUI definita ✅ Compatibile con NTC2018 e RD2229 ✅ Integrata con ProjectModel ✅ ReportBuilder allineati ✅ Controllo totale del contenuto della relazione


Questo file è vincolante per la selezione delle verifiche da includere nella relazione di calcolo.
