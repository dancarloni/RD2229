
GUI – Collegamento Risultati ↔ Relazione di Calcolo
Status: FILE OPERATIVO – BINDING RISULTATI / RELAZIONE (VINCOLANTE)
Questo documento definisce il collegamento formale e operativo tra:

i risultati delle verifiche (VerificationResult) visualizzati in RisultatiView,
e la Relazione di Calcolo NTC2018 basata sul template:
RELAZIONE_DI_CALCOLO_NTC2018_TEMPLATE_OPERATIVO.md.

L’obiettivo è garantire che ogni verifica eseguita:

sia tracciabile,
sia classificata per Capitolo NTC,
possa essere inclusa o esclusa consapevolmente dalla relazione,
confluisca nella relazione senza rielaborazioni manuali.


1. Principio fondamentale (hard rule)


La Relazione di Calcolo NON ricalcola nulla.


Essa:

legge esclusivamente oggetti VerificationResult già validati;
non interpreta gli esiti;
non modifica i valori di Ed, Rd o dei rapporti.
La GUI agisce solo come selettore e orchestratore.


2. Flusso dati completo

VerificationEngine
        ↓
VerificationResult[*]
        ↓
ProjectModel.verifiche_cap4 / verifiche_cap7
        ↓
RisultatiView (visualizzazione)
        ↓
Selezione risultati da includere
        ↓
ReportBuilder
        ↓
Relazione di Calcolo (NTC2018)




3. Estensione del ProjectModel (vincolante)
Per consentire il collegamento controllato alla relazione, il ProjectModel deve includere:

class ProjectModel:
    def __init__(self):
        ...
        self.verifiche_cap4 = []
        self.verifiche_cap7 = []

        # risultati selezionati per la relazione
        self.verifiche_in_relazione = []




4. Comportamento della RisultatiView
La RisultatiView:

mostra tutte le verifiche disponibili;
consente (in una versione estesa) la selezione delle verifiche da includere;
aggiorna project_model.verifiche_in_relazione.
Nota
Nella versione base, tutte le verifiche eseguite sono considerate automaticamente incluse.


5. Interfaccia ReportBuilder (contratto)
La GUI non genera la relazione: delega a un oggetto dedicato.

class ReportBuilder:
    def __init__(self, project_model):
        self.project_model = project_model

    def build(self):
        """
        Genera la relazione di calcolo utilizzando:
        - verifiche_cap4
        - verifiche_cap7
        - verifiche_in_relazione (se presente)
        """
        raise NotImplementedError




6. Mappatura VerificationResult → Relazione
Ogni VerificationResult fornisce direttamente i campi necessari:

Campo VerificationResult	Uso in relazione
reference.norma	Norma di riferimento
reference.capitolo	Capitolo NTC
reference.paragrafo	Titolo verifica
demand	Effetto di progetto Ed
capacity	Resistenza Rd
ratio	Rapporto Ed/Rd
status	Esito verifica
capitolo_ntc	Classificazione CAP_4 / CAP_7



7. Inserimento nella Relazione di Calcolo
Nel template RELAZIONE_DI_CALCOLO_NTC2018_TEMPLATE_OPERATIVO.md:

CAPITOLO 4 utilizza verifiche_cap4;
CAPITOLO 7 utilizza verifiche_cap7;
CAPITOLO 8 (ζE) utilizza i risultati aggregati.
Ogni verifica viene riportata come:

descrizione normativa;
tabella Ed / Rd / Ed/Rd;
esito.


8. Regole di sicurezza normativa

nessuna verifica può entrare in relazione se non è stata eseguita;
è vietata la modifica manuale dei risultati;
la relazione deve riportare il Capitolo NTC corretto;
i risultati CAP_4 e CAP_7 non possono essere mescolati.


9. Integrazione con la GUI (main.py)
Nel flusso GUI:

# dopo l’esecuzione delle verifiche
self.project_model.verifiche_in_relazione = (
    self.project_model.verifiche_cap4
    + self.project_model.verifiche_cap7
)

# generazione relazione
report = ReportBuilder(self.project_model)
report.build()




10. Stato finale
✅ Collegamento risultati → relazione formalizzato ✅ Tracciabilità completa garantita ✅ Separazione GUI / calcolo / report rispettata ✅ Pronto per esportazione PDF / DOCX


Questo file è vincolante per il collegamento tra i risultati di verifica e la Relazione di Calcolo NTC2018.
