
IMPLEMENTAZIONE GUI NTC2018 – Workflow Operativo
Status: IMPLEMENTAZIONE ATTIVA – INTERFACCIA GRAFICA (GUI)
Questo file avvia nel canvas lo sviluppo dell’interfaccia grafica (GUI) del software di verifica strutturale NTC2018, tenendo conto integralmente di tutto quanto già sviluppato:

Core di verifica
Motore combinazioni
Verifiche CAP_4 (SLU / SLE)
Verifiche CAP_7 (gerarchia, capacità)
Calcolo ζE
Template di relazione di calcolo
La GUI non replica la logica normativa: la orchestra.


1. Principi architetturali della GUI (vincolanti)
La GUI deve rispettare i seguenti principi non negoziabili:

Separazione totale GUI / logicala GUI non contiene formule;
la GUI non applica norme;
la GUI invoca solo moduli software già definiti.
Workflow guidatol’utente procede per STEP coerenti con NTC2018;
non è possibile saltare STEP obbligatori (es. ζE senza Rd).
Tracciabilità completaogni scelta utente è registrata;
ogni output è ricostruibile.
Blocco normativo automaticola GUI deve impedire combinazioni non ammesse (CAP_4 vs CAP_7).


2. Architettura generale della GUI

GUI
│
├── ProjectWizard
│   ├── DatiGeneraliView
│   ├── SceltaNormativaView
│   ├── ModelloStrutturaleView
│   └── MetodoAnalisiView
│
├── AzioniCombinazioniView
│
├── VerificheCAP4View
│   ├── SLUView
│   └── SLEView
│
├── VerificheCAP7View
│   ├── SismicaParametriView
│   ├── GerarchiaView
│   └── CapacitaView
│
├── ZetaEView
│
├── RisultatiView
│
└── RelazioneView


Ogni View è stateless: i dati risiedono nel ProjectModel.


3. Modello dati centrale (ProjectModel)

class ProjectModel:
    def __init__(self):
        self.dati_generali = {}
        self.normativa = "NTC2018"
        self.tipologia = None  # nuova / esistente

        self.modello_strutturale = {}
        self.metodo_analisi = None

        self.azioni = []
        self.combinazioni = []

        self.verifiche_cap4 = []
        self.verifiche_cap7 = []

        self.capacita_rd = None
        self.zeta_e = None

        self.report = None


📌 Tutte le View leggono e scrivono solo qui.


4. Workflow GUI obbligatorio
STEP A – Dati generali

Oggetto
Ubicazione
Tipologia opera (nuova / esistente)
→ necessario per abilitare CAP_7 e ζE


STEP B – Modello e analisi

scelta metodo (Cross / FEM / altro)
ipotesi elastiche
→ collegato a KB_NTC2018_ANALISI


STEP C – Azioni e combinazioni

input azioni
generazione automatica combinazioni (STEP 3)
→ GUI non consente modifiche manuali delle combinazioni


STEP D – Verifiche CAP_4

SLU c.a.
SLE c.a.
→ disponibile sempre


STEP E – Verifiche CAP_7
Abilitato solo se:

opera esistente oppure nuova in zona sismica;
completate verifiche CAP_4;
disponibili combinazioni sismiche.
Include:

gerarchia delle resistenze (STEP 5)
capacità sismica Rd


STEP F – ζE (solo edifici esistenti)
Abilitato solo se:

LC definito;
FC definito;
Rd disponibile.
→ calcolo tramite ZetaECalculator


STEP G – Relazione di calcolo

preview relazione
esportazione DOCX / PDF
→ basata su RELAZIONE_DI_CALCOLO_NTC2018_TEMPLATE_OPERATIVO.md


5. Blocco normativo nella GUI (regole hard)
La GUI deve impedire:

accesso a CAP_7 se CAP_4 non è completo;
uso di q se gerarchia NON OK;
calcolo ζE senza LC / FC / Rd;
esportazione relazione incompleta.
Questi blocchi non sono opzionali.


6. Tecnologie suggerite

Python + Tkinter (coerente con progetto)
pattern MVC semplificato
ogni View in file separato
Esempio:

gui/
├── main.py
├── project_model.py
├── views/
│   ├── dati_generali.py
│   ├── modello.py
│   ├── azioni.py
│   ├── verifiche_cap4.py
│   ├── verifiche_cap7.py
│   ├── zeta_e.py
│   └── relazione.py




7. Integrazione con la relazione di calcolo
La GUI:

non scrive la relazione;
passa i dati al ReportBuilder;
mostra un’anteprima strutturata;
consente esportazione controllata.


8. Stato dell’implementazione GUI
✅ GUI definita architetturalmente ✅ Workflow coerente con NTC2018 ✅ Blocco normativo integrato ✅ Pronta per implementazione codice reale


9. Prossimo STEP suggerito
Procedere con implementazione reale della GUI:

ProjectModel
main.py
prima View: DatiGeneraliView


Questo file è vincolante per lo sviluppo dell’interfaccia grafica del software NTC2018.
