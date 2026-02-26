
GUI – Selezione Normativa di Verifica
Status: FILE OPERATIVO – GUI (VINCOLANTE)
Questo documento definisce la View GUI per la selezione della normativa di verifica, integrata nel workflow esistente e comune a tutte le normative.
La selezione della normativa:

governa quali verifiche sono attivabili;
governa quale VerificationFactory viene utilizzata;
governa quale template di relazione di calcolo viene generato;
non modifica sezioni, materiali o sollecitazioni.
La View è progettata per supportare NTC2018 e R.D. 2229/1939, ed è estendibile a normative future.


1. Principio architetturale (hard rule)


La normativa è una proprietà del progetto, non della sezione.


Pertanto:

la selezione normativa non duplica le View;
la selezione normativa non modifica i dati geometrici o meccanici;
la normativa influisce solo su:verifiche eseguibili;
logica del core;
struttura della relazione.


2. Integrazione nel ProjectModel (vincolante)
File coinvolto

project_model.py
Attributo obbligatorio

class ProjectModel:
    def __init__(self):
        ...
        self.normativa_attiva = None  # 'NTC2018' | 'RD2229'




3. Normative supportate
La GUI deve consentire la selezione esplicita tra:

✅ NTC2018 – Norme Tecniche per le Costruzioni (DM 17/01/2018)
✅ R.D. 2229/1939 – Norme per il calcolo delle costruzioni in cemento armato
La normativa selezionata deve essere sempre visibile nel layout principale della GUI.


4. View: SelezioneNormativaView
Mockup funzionale

┌──────────── SELEZIONE NORMATIVA ────────────┐
│ Normativa di verifica                       │
│                                            │
│  (●) NTC2018                                │
│      ▸ SLU / SLE                            │
│      ▸ Sismica (CAP_7)                      │
│                                            │
│  (○) R.D. 2229/1939                         │
│      ▸ Tensioni ammissibili                 │
│      ▸ Verifiche statiche a freddo          │
│                                            │
│ [ Applica normativa ▶ ]                     │
└─────────────────────────────────────────────┘




5. Comportamento della View
Alla selezione e conferma della normativa:

viene aggiornato:

   project_model.normativa_attiva



la GUI:abilita/disabilita le voci di workflow incompatibili;
aggiorna i messaggi di contesto (es. sismica non disponibile per RD2229);
eventuali risultati già presenti non vengono cancellati automaticamente, ma:non sono più utilizzabili se incompatibili con la nuova normativa;
il binding GUI ↔ core utilizzerà automaticamente la VerificationFactory corretta.


6. Codice – gui/views/selezione_normativa.py

import tkinter as tk
from tkinter import ttk, messagebox


class SelezioneNormativaView(ttk.Frame):
    """
    View per la selezione della normativa di verifica.
    Aggiorna esclusivamente project_model.normativa_attiva.
    """

    def __init__(self, parent, project_model):
        super().__init__(parent)
        self.project_model = project_model
        self._normativa = tk.StringVar(value=project_model.normativa_attiva)
        self._build_ui()

    def _build_ui(self):
        frame = ttk.LabelFrame(self, text="Selezione normativa")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Radiobutton(
            frame,
            text="NTC2018 – SLU / SLE / Sismica",
            variable=self._normativa,
            value="NTC2018",
        ).pack(anchor="w", pady=5)

        ttk.Radiobutton(
            frame,
            text="R.D. 2229/1939 – Tensioni ammissibili",
            variable=self._normativa,
            value="RD2229",
        ).pack(anchor="w", pady=5)

        ttk.Button(
            frame,
            text="Applica normativa ▶",
            command=self._apply,
        ).pack(pady=10)

    def _apply(self):
        normativa = self._normativa.get()

        if not normativa:
            messagebox.showerror("Errore", "Selezionare una normativa")
            return

        self.project_model.normativa_attiva = normativa

        messagebox.showinfo(
            "Normativa impostata",
            f"Normativa di verifica impostata: {normativa}",
        )




7. Collegamento con main.py
Nel file GUI_MAIN_PY_NAVIGAZIONE.md:

la SelezioneNormativaView deve essere:istanziata come le altre View;
posizionata prima di SezioniMaterialiView nel workflow.
Esempio:

self.views["normativa"] = SelezioneNormativaView(
    self.container,
    self.project_model,
)




8. Regole di sicurezza normativa

non è possibile eseguire verifiche senza normativa selezionata;
RD2229 esclude automaticamente:sismica;
progettazione in capacità;
ζE;
la relazione generata deve corrispondere alla normativa attiva.


9. Stato finale
✅ Selezione normativa formalizzata ✅ Integrazione con ProjectModel ✅ Compatibile con GUI e core esistenti ✅ Pronta per estensione a normative future


Questo file è vincolante per la gestione multi‑normativa della GUI di verifica strutturale.
