
REPORT_BUILDER_RD2229 – Generatore della Relazione di Calcolo (R.D. 2229/1939)
Status: FILE OPERATIVO – GENERAZIONE AUTOMATICA RELAZIONE (VINCOLANTE)
Questo documento definisce il ReportBuilder dedicato al R.D. 16/11/1939 n. 2229, responsabile della generazione automatica della Relazione di Calcolo a partire dai risultati di verifica prodotti dal motore di calcolo.
Il ReportBuilderRD2229:

non esegue alcun calcolo strutturale;
non interpreta gli esiti delle verifiche;
utilizza esclusivamente gli oggetti VerificationResult;
popola il template:
RELAZIONE_RD2229_TEMPLATE.md;

garantisce tracciabilità, riproducibilità e difendibilità tecnico‑legale.

1. Principio fondamentale (hard rule)

Il ReportBuilder RD2229 non ricalcola nulla.

La relazione è una proiezione fedele dello stato del ProjectModel dopo l’esecuzione delle verifiche.
Qualsiasi valore riportato in relazione:

proviene da un VerificationResult;
è già stato validato dal core;
è immutabile a livello di report.

1. Input del ReportBuilderRD2229
Il ReportBuilderRD2229 riceve unicamente:

ProjectModel con:normativa_attiva == 'RD2229';
verifiche_rd2229: list[VerificationResult] oppure
verifiche_in_relazione (se selezione GUI attiva);
dati generali del progetto (anagrafica);
riferimento al template RELAZIONE_RD2229_TEMPLATE.md.

1. Output del ReportBuilderRD2229
Il builder produce:

una Relazione di Calcolo RD2229 completa, strutturata secondo:criteri storici;
metodo delle tensioni ammissibili;
un documento:Markdown (.md) per tracciabilità;
successivamente convertibile in PDF/DOCX.

1. Mappatura dati ProjectModel → Relazione
La relazione viene popolata come segue:

Origine Sezione della relazione
project_model.dati_generali §2 – Inquadramento generale
project_model.materiale §4 – Materiali
project_model.sezione §5 – Modello strutturale
VerificationResult §7 – Verifiche strutturali
esiti aggregati §8 – Esiti complessivi

1. Classificazione delle verifiche RD2229
Il ReportBuilder deve suddividere automaticamente i risultati per tipologia:

Pressoflessione
Flessione semplice
Taglio
Compressione semplice
Trazione semplice (se presente)
La classificazione avviene tramite:

VerificationResult.reference.paragrafo
VerificationResult.nome
Nessuna logica normativa è introdotta nel builder.

1. Struttura del ReportBuilderRD2229
File di implementazione

core/report/report_builder_rd2229.py
Struttura concettuale

class ReportBuilderRD2229:
    def __init__(self, project_model):
        self.project_model = project_model

    def build(self) -> str:
        """
        Genera la relazione di calcolo secondo R.D. 2229/1939
        utilizzando esclusivamente i VerificationResult.
        Ritorna il contenuto della relazione in formato Markdown.
        """
        raise NotImplementedError

7. Esempio di generazione sezione verifiche
Per ogni VerificationResult r:

Elemento: r.reference.paragrafo
Normativa: R.D. 2229/1939
Tensione calcolata: r.demand
Tensione ammissibile: r.capacity
Rapporto σ/σamm: r.ratio
Esito: r.status

Questi dati vengono inseriti nelle tabelle del §7 del template.

1. Integrazione con la GUI
Nel flusso GUI (già definito):

if project_model.normativa_attiva == 'RD2229':
    builder = ReportBuilderRD2229(project_model)
    relazione_md = builder.build()

La GUI:

non modifica la relazione;
può solo:visualizzare un’anteprima;
esportare il file.

1. Regole di sicurezza e coerenza
Il ReportBuilderRD2229 deve:

rifiutare la generazione se:normativa_attiva != 'RD2229';
non esistono verifiche RD2229;
riportare esplicitamente la normativa in intestazione;
mantenere la separazione netta con NTC2018;
produrre una relazione difendibile in sede tecnica e legale.

1. Stato finale
✅ ReportBuilder RD2229 definito ✅ Collegato al template di relazione ✅ Integrato nel flusso GUI → Core → Output ✅ Sistema multi‑normativo completo

Questo file è vincolante per la generazione automatica della Relazione di Calcolo secondo il R.D. 2229/1939.
