
Integrazione RD 2229/1939 – GUI, Core di Verifica e Relazione di Calcolo
Status: PIANO OPERATIVO VINCOLANTE – ESTENSIONE MULTI‑NORMATIVA
Questo documento definisce come tutto quanto sviluppato per NTC2018 (GUI, core di verifica, risultati, relazione) debba essere reso disponibile anche per il R.D. 2229/1939, senza duplicare l’architettura, ma integrandosi rigorosamente nelle strutture esistenti.
L’obiettivo è ottenere un motore multi‑normativo in cui:

la GUI è unica;
il ProjectModel è unico;
il VerificationEngine è unico;
cambiano solo:le regole normative;
le verifiche attivabili;
il template di relazione.


1. Principio architetturale fondamentale


NTC2018 e RD2229 sono due istanze della stessa architettura di verifica.


Pertanto:

❌ nessuna duplicazione di GUI;
❌ nessuna duplicazione di flussi;
✅ separazione netta tra:infrastruttura (comune);
contenuto normativo (specifico).


2. Estensione del ProjectModel (vincolante)
Il ProjectModel deve diventare multi‑normativa.
File coinvolto

project_model.py
Estensione obbligatoria

class ProjectModel:
    def __init__(self):
        ...
        # normativa attiva
        self.normativa_attiva = None  # 'NTC2018' | 'RD2229'

        # risultati di verifica
        self.verifiche_cap4 = []      # NTC2018
        self.verifiche_cap7 = []      # NTC2018
        self.verifiche_rd2229 = []    # RD 2229/1939

        # risultati selezionati per relazione
        self.verifiche_in_relazione = []




3. Estensione della GUI – selezione normativa
File GUI già esistente

IMPLEMENTAZIONE_GUI_NTC2018_WORKFLOW.md
Nuovo file da creare

✅ GUI_SELEZIONE_NORMATIVA.md
Contenuto
La GUI deve consentire:

selezione esplicita della normativa:NTC2018
R.D. 2229/1939
blocco automatico delle verifiche incompatibili;
aggiornamento di project_model.normativa_attiva.


4. Verifiche strutturali – RD 2229/1939
Principio
Il RD 2229 non ha:

stati limite moderni;
progettazione in capacità;
distinzione SLU/SLE;
sismica moderna.
Le verifiche sono:

a tensioni ammissibili;
a freddo;
deterministiche.


5. Core di verifica – RD2229
Nuovi file di core da creare

✅ KB_RD2229_1939.md (già previsto)
✅ VERIFICHE_RD2229_TENSIONI_AMMISSIBILI.md
✅ VERIFICATION_FACTORY_RD2229.md
Integrazione con il core esistente

il VerificationEngine resta identico;
cambia la VerificationFactory in funzione della normativa:

if project_model.normativa_attiva == 'RD2229':
    factory = VerificationFactoryRD2229()
elif project_model.normativa_attiva == 'NTC2018':
    factory = VerificationFactoryNTC2018()




6. Binding GUI ↔ Core (estensione)
File già esistente

GUI_VERIFICATION_ENGINE_BINDING.md
Estensione concettuale
Il binding deve:

interrogare project_model.normativa_attiva;
instradare verso:verifiche NTC2018 (CAP_4 / CAP_7), oppure
verifiche RD2229.
Nuovo file di specifica

✅ GUI_VERIFICATION_ENGINE_BINDING_RD2229.md


7. Risultati – RD2229
Integrazione con RisultatiView
La RisultatiView:

resta unica;
visualizza risultati:NTC2018 (CAP_4 / CAP_7), oppure
RD2229 (tensioni ammissibili),
distinguendo la colonna Normativa.
Nessun nuovo file GUI necessario
✅ riuso totale di GUI_RISULTATI_VIEW_CODICE.md.


8. Relazione di calcolo – RD2229
Principio
La relazione RD2229:

è separata da NTC2018;
ha struttura diversa;
ma usa gli stessi VerificationResult.
Nuovi file da creare

✅ RELAZIONE_DI_CALCOLO_RD2229_TEMPLATE.md
✅ REPORT_BUILDER_RD2229.md
Collegamento
Il file già creato:

GUI_RISULTATI_TO_RELAZIONE_BINDING.md
si estende con:

if normativa_attiva == RD2229:
    usa REPORT_BUILDER_RD2229
else:
    usa REPORT_BUILDER_NTC2018




9. Elenco completo dei file MD (riassunto)
Infrastruttura comune (già esistente)

GUI_MAIN_PY_NAVIGAZIONE.md
GUI_VERIFICATION_ENGINE_BINDING.md
GUI_RISULTATI_VIEW_CODICE.md
GUI_RISULTATI_TO_RELAZIONE_BINDING.md
Normativa NTC2018 (già esistente)

RELAZIONE_DI_CALCOLO_NTC2018_TEMPLATE_OPERATIVO.md
VERIFICATION_FACTORY_NTC2018.md
Normativa RD 2229/1939 (da integrare)

✅ KB_RD2229_1939.md
✅ GUI_SELEZIONE_NORMATIVA.md
✅ VERIFICHE_RD2229_TENSIONI_AMMISSIBILI.md
✅ VERIFICATION_FACTORY_RD2229.md
✅ GUI_VERIFICATION_ENGINE_BINDING_RD2229.md
✅ RELAZIONE_DI_CALCOLO_RD2229_TEMPLATE.md
✅ REPORT_BUILDER_RD2229.md


10. Stato finale
✅ Architettura multi‑normativa definita ✅ RD2229 integrabile senza duplicazioni ✅ GUI unica ✅ Core unico ✅ Relazioni separate ma coerenti


Questo file è vincolante per l’estensione dell’intero sistema da NTC2018 a RD 2229/1939.
