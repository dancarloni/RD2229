
IMPLEMENTAZIONE_NTC2018_STEP3_MOTORE_COMBINAZIONI.md
Status: IMPLEMENTAZIONE ATTIVA – MOTORE COMBINAZIONI DI CARICO NTC2018
Ambito normativo esplicito:

✅ NTC2018 – Capitolo 4 (SLU / SLE statici)
✅ NTC2018 – Capitolo 7 (combinazioni sismiche, se richieste)
Questo file implementa nel canvas lo STEP 3 dell’implementazione software: il motore delle combinazioni di carico secondo NTC2018, come strato intermedio obbligatorio tra:

azioni elementari (KB_NTC2018_AZIONI.md)
analisi strutturale (KB_NTC2018_ANALISI.md)
verifiche (CAP_4 / CAP_7)
Il motore è norma‑driven, parametrico, tracciabile e impedisce qualunque combinazione non ammessa dalle NTC.


1. Ruolo del motore combinazioni
Il motore delle combinazioni:

riceve azioni elementari (G, Q, E, …);
genera combinazioni normative;
associa ogni combinazione a:stato limite;
capitolo NTC;
riferimento normativo;
fornisce le combinazioni ai metodi di analisi e alle verifiche.
📌 Nessuna verifica può essere eseguita senza passare da questo motore.


2. Classificazione delle combinazioni
2.1 Stati Limite supportati

SLU – Stati Limite Ultimi (CAP_4)
SLE-RARA – Stato Limite di Esercizio raro (CAP_4)
SLE-FREQ – Stato Limite di Esercizio frequente (CAP_4)
SLE-QP – Stato Limite di Esercizio quasi‑permanente (CAP_4)
SISMICA – Combinazioni sismiche (CAP_7)


3. Modello dati – Azioni

from dataclasses import dataclass

@dataclass
class Action:
    name: str
    value: float
    type: str   # G1, G2, Q, E, ...




4. Modello dati – Combinazione

from dataclasses import dataclass
from ntc_capitolo import NTCCapitol

@dataclass
class LoadCombination:
    name: str
    actions: dict[str, float]
    stato_limite: str
    capitolo_ntc: NTCCapitol
    reference: str


Ogni combinazione è un oggetto esplicito, serializzabile e citabile.


5. Motore combinazioni – struttura base

class CombinationEngineNTC2018:

    def __init__(self, actions: list[Action]):
        self.actions = actions

    def generate_slu(self) -> list[LoadCombination]:
        ...

    def generate_sle_rara(self) -> list[LoadCombination]:
        ...

    def generate_sle_frequente(self) -> list[LoadCombination]:
        ...

    def generate_sle_quasi_perm(self) -> list[LoadCombination]:
        ...

    def generate_sismica(self) -> list[LoadCombination]:
        ...




6. Regole vincolanti per CAPITOLO 4
Per le combinazioni CAP_4:

vietato includere l’azione sismica E;
vietato l’uso del fattore q;
combinazioni generate solo secondo §2.5 e §4 NTC2018;
distinzione obbligatoria tra:azione principale;
azioni concomitanti (ψ0, ψ1, ψ2).
Ogni combinazione CAP_4 riporta:

NTC2018 – §2.5 / §4




7. Regole vincolanti per CAPITOLO 7
Per le combinazioni CAP_7:

inclusione obbligatoria dell’azione sismica E;
uso consentito del fattore q solo se:sono attive verifiche di capacità;
riferimento esplicito a §7 NTC2018;
collegamento diretto con KB_NTC2018_SISMICA.md.


8. Esempio – Combinazione SLE rara (CAP_4)

LoadCombination(
    name="SLE_RARA",
    actions={"G1": 1.0, "G2": 1.0, "Q": 1.0},
    stato_limite="SLE_RARA",
    capitolo_ntc=NTCCapitol.CAP_4,
    reference="NTC2018 §2.5.3",
)




9. Esempio – Combinazione sismica (CAP_7)

LoadCombination(
    name="SISMICA_ELASTICA",
    actions={"G1": 1.0, "G2": 1.0, "E": 1.0},
    stato_limite="SISMICA",
    capitolo_ntc=NTCCapitol.CAP_7,
    reference="NTC2018 §7.3",
)




10. Integrazione con il motore di verifica
Il flusso è obbligatorio:

Azioni → Motore Combinazioni → Analisi → Verifiche



le verifiche CAP_4 rifiutano combinazioni CAP_7;
le verifiche CAP_7 rifiutano combinazioni CAP_4;
ogni VerificationResult riporta la combinazione utilizzata.


11. Relazione di calcolo
La relazione deve riportare:

elenco delle azioni;
elenco delle combinazioni generate;
stato limite;
capitolo NTC;
riferimento normativo.
La combinazione diventa parte integrante della prova di calcolo.


12. Stato dell’implementazione
✅ STEP 3 completato nel canvas ✅ Motore combinazioni NTC2018 definito ✅ Blocco CAP_4 / CAP_7 garantito ✅ Pronto per:

STEP 4 – ζE edifici esistenti
STEP 5 – Gerarchia e capacità sismica


Questo file è vincolante per tutte le combinazioni di carico utilizzate nel software NTC2018.
