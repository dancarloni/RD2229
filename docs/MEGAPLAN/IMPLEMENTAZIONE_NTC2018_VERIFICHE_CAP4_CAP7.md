
IMPLEMENTAZIONE_NTC2018_VERIFICHE_CAP4_CAP7.md
Status: IMPLEMENTAZIONE ATTIVA – FILE DI INTEGRAZIONE VINCOLANTE
Ambito normativo:

✅ Capitolo 4 NTC2018 – Costruzioni civili e industriali (verifiche statiche, SLU/SLE)
✅ Capitolo 7 NTC2018 – Progettazione per azioni sismiche (capacità, gerarchia, q)
Questo file è il nodo di collegamento esplicito tra il codice di verifica e le Knowledge Base NTC2018, e chiarisce in modo non ambiguo se una verifica è:

di Capitolo 4 (statica / resistenza / esercizio), oppure
di Capitolo 7 (sismica / capacità / gerarchia).


1. Collegamenti vincolanti con la Knowledge Base
Questo file opera esclusivamente se sono presenti e attivi i seguenti documenti:

KB_NTC2018.md
KB_NTC2018_AZIONI.md
KB_NTC2018_ANALISI.md
KB_NTC2018_CA.md
KB_NTC2018_ESISTENTI.md
KB_NTC2018_SISMICA.md
Qualsiasi implementazione che non richiami esplicitamente uno di questi documenti è da considerarsi NON CONFORME.


2. Regola fondamentale (obbligatoria)


Ogni classe di verifica deve dichiarare esplicitamente il capitolo NTC2018 di riferimento.


Non è ammesso:

mescolare Capitolo 4 e Capitolo 7 nella stessa verifica;
eseguire verifiche sismiche usando criteri di Capitolo 4;
omettere il riferimento di capitolo nel risultato di verifica.


3. Mappatura verifiche → Capitoli NTC2018
3.1 Verifiche di CAPITOLO 4 – Statica
Rientrano nel Capitolo 4 NTC2018:

SLU flessione c.a.
SLU pressoflessione c.a.
SLU taglio / torsione
SLE tensioni
SLE fessurazione
SLE deformazioni
📌 Queste verifiche:

utilizzano combinazioni da KB_NTC2018_AZIONI;
utilizzano analisi coerenti con KB_NTC2018_ANALISI;
NON utilizzano fattore q;
NON applicano progettazione in capacità.


3.2 Verifiche di CAPITOLO 7 – Sismica
Rientrano nel Capitolo 7 NTC2018:

verifica con fattore di comportamento q
gerarchia delle resistenze
progettazione in capacità
verifiche dissipative / non dissipative
valutazione sismica con ζE
📌 Queste verifiche:

richiamano KB_NTC2018_SISMICA;
richiamano KB_NTC2018_ESISTENTI (per edifici esistenti);
NON sono valide senza verifica di capacità;
NON sono eseguibili se q è indefinito.


4. Estensione del modello di risultato di verifica
Ogni VerificationResult deve ora includere esplicitamente il capitolo NTC.

from enum import Enum

class NTCCapitol(Enum):
    CAP_4 = "NTC2018 – Capitolo 4"
    CAP_7 = "NTC2018 – Capitolo 7"



@dataclass
class VerificationResult:
    status: VerificationStatus
    demand: float | None
    capacity: float | None
    ratio: float | None
    reference: NormativeReference
    capitolo_ntc: NTCCapitol
    notes: str = ""


📌 Questo rende il risultato immediatamente difendibile in relazione.


5. Esempio – Verifica SLU flessione (CAPITOLO 4)

return VerificationResult(
    status=status,
    demand=self.m_ed,
    capacity=self.m_rd,
    ratio=ratio,
    reference=NormativeReference(
        norma="NTC2018",
        capitolo="§4.1.4",
        paragrafo="Verifiche a flessione",
    ),
    capitolo_ntc=NTCCapitol.CAP_4,
)


✅ Verifica statica ✅ Capitolo 4 ✅ Nessuna capacità sismica


6. Esempio – Verifica gerarchia (CAPITOLO 7)

return VerificationResult(
    status=status,
    demand=effetto_dissipativo,
    capacity=capacita_non_dissipativa,
    ratio=ratio,
    reference=NormativeReference(
        norma="NTC2018",
        capitolo="§7.4",
        paragrafo="Gerarchia delle resistenze",
    ),
    capitolo_ntc=NTCCapitol.CAP_7,
)


✅ Verifica sismica ✅ Capitolo 7 ✅ Progettazione in capacità


7. Regole di utilizzo nel software (hard rules)
Il motore di verifica deve:

rifiutare risultati senza capitolo_ntc;
impedire confronti CAP_4 vs CAP_7 non dichiarati;
riportare il capitolo in relazione di calcolo;
impedire l’uso di q in verifiche CAP_4.


8. Collegamento con i prossimi STEP di implementazione
Questo file è propedeutico e obbligatorio per:

STEP 2 – SLE c.a. (CAP_4)
STEP 4 – ζE edifici esistenti (CAP_7)
STEP 5 – Gerarchia e capacità sismica (CAP_7)
Generatore automatico di relazione di calcolo


9. Stato del sistema
✅ Implementazione NTC2018 attiva ✅ Distinzione CAP_4 / CAP_7 formalizzata ✅ Output normativamente tracciabile ✅ Base pronta per estensioni FEM L3


Questo file è vincolante per tutta l’implementazione software NTC2018.
