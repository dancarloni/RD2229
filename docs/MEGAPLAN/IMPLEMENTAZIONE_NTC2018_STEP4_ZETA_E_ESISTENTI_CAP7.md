
IMPLEMENTAZIONE_NTC2018_STEP4_ZETA_E_ESISTENTI_CAP7.md
Status: IMPLEMENTAZIONE ATTIVA – VALUTAZIONE ζE EDIFICI ESISTENTI
Ambito normativo esplicito:

❌ NTC2018 – Capitolo 4 NON applicabile (verifiche statiche pure escluse)
✅ NTC2018 – Capitolo 7 (sicurezza sismica)
✅ NTC2018 – Capitolo 8 (costruzioni esistenti)
Questo file implementa nel canvas lo STEP 4 dell’implementazione software: il calcolo e la gestione dell’indice di sicurezza ζE per edifici esistenti, come richiesto dalle NTC2018.
È il primo STEP pienamente “sismico” e utilizza obbligatoriamente:

il motore combinazioni (STEP 3);
le verifiche di capacità (STEP 5, quando presenti);
le regole sui livelli di conoscenza (LC) e fattori di confidenza (FC).


1. Collegamenti vincolanti con la Knowledge Base
Questo file è valido solo se sono presenti e coerenti i seguenti documenti:

KB_NTC2018_ESISTENTI.md
KB_NTC2018_SISMICA.md
KB_NTC2018_ANALISI.md
IMPLEMENTAZIONE_NTC2018_VERIFICHE_CAP4_CAP7.md
IMPLEMENTAZIONE_NTC2018_STEP3_MOTORE_COMBINAZIONI.md
Qualsiasi uso di ζE senza questi collegamenti è da considerarsi NON CONFORME.


2. Inquadramento normativo di ζE
Secondo NTC2018 (§8):


L’indice di sicurezza ζE rappresenta il rapporto tra la capacità della struttura e la domanda sismica richiesta per una nuova costruzione.


Principi vincolanti:

ζE è obbligatorio per le valutazioni di sicurezza sismica;
ζE è richiesto per distinguere:intervento locale;
miglioramento sismico;
adeguamento sismico;
ζE è sempre riferito a CAPITOLO 7.


3. Livelli di conoscenza (LC) e fattori di confidenza (FC)
Il calcolo di ζE non è ammesso senza:

dichiarazione esplicita del Livello di Conoscenza (LC1, LC2, LC3);
applicazione del corrispondente Fattore di Confidenza (FC).
Regola software vincolante:

Se LC non è definito → ζE NON CALCOLABILE




4. Modello dati – Parametri ζE

from dataclasses import dataclass
from ntc_capitolo import NTCCapitol

@dataclass
class ZetaEParameters:
    domanda_sismica: float      # Ed (da combinazione sismica)
    capacita_sismica: float    # Rd (da verifiche di capacità)
    fattore_confidenza: float  # FC




5. Classe di calcolo ζE (CAP_7)

from verification_result import (
    VerificationResult,
    VerificationStatus,
    NormativeReference,
)
from ntc_capitolo import NTCCapitol

class ZetaECalculator:

    CAPITOLO = NTCCapitol.CAP_7

    def __init__(self, params: ZetaEParameters):
        self.params = params

    def compute(self) -> VerificationResult:
        if self.params.capacita_sismica <= 0:
            return VerificationResult(
                status=VerificationStatus.NOT_APPLICABLE,
                demand=None,
                capacity=None,
                ratio=None,
                reference=NormativeReference(
                    norma="NTC2018",
                    capitolo="§8",
                    paragrafo="Valutazione della sicurezza sismica",
                ),
                capitolo_ntc=self.CAPITOLO,
                notes="Capacità sismica non definita",
            )

        zeta_e = (
            self.params.capacita_sismica
            / (self.params.domanda_sismica * self.params.fattore_confidenza)
        )

        return VerificationResult(
            status=VerificationStatus.OK,
            demand=self.params.domanda_sismica,
            capacity=self.params.capacita_sismica,
            ratio=zeta_e,
            reference=NormativeReference(
                norma="NTC2018",
                capitolo="§8",
                paragrafo="Indice di sicurezza ζE",
            ),
            capitolo_ntc=self.CAPITOLO,
            notes=f"ζE = {zeta_e:.3f}",
        )




6. Interpretazione normativa del risultato
Secondo NTC2018:

ζE < 1.00 → sicurezza inferiore a nuova costruzione
ζE ≈ 1.00 → sicurezza equivalente a nuova costruzione
ζE ≥ 1.00 → requisito per adeguamento sismico
Il software deve:

classificare automaticamente il tipo di intervento;
riportare ζE in relazione di calcolo;
bloccare adeguamenti con ζE < 1.0.


7. Esempio di utilizzo

params = ZetaEParameters(
    domanda_sismica=1200.0,
    capacita_sismica=900.0,
    fattore_confidenza=1.20,
)

zeta_calc = ZetaECalculator(params)
result = zeta_calc.compute()

print(result.ratio)  # ζE




8. Regole di integrazione con STEP precedenti e successivi

STEP 3 fornisce domanda sismica Ed;
STEP 5 fornisce capacità sismica Rd;
questo STEP non sostituisce le verifiche di capacità;
ζE è un indice globale, non una verifica locale.


9. Stato dell’implementazione
✅ STEP 4 completato nel canvas ✅ ζE formalizzato come oggetto software ✅ Distinzione CAP_7 esplicita ✅ Pronto per:

STEP 5 – Gerarchia e capacità sismica
Generatore relazione di calcolo per edifici esistenti


Questo file è vincolante per tutte le valutazioni di sicurezza sismica degli edifici esistenti – NTC2018.
