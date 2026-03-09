
IMPLEMENTAZIONE_NTC2018_STEP2_SLE_CA_CAP4.md
Status: IMPLEMENTAZIONE ATTIVA – VERIFICHE SLE CALCESTRUZZO ARMATO
Ambito normativo esplicito:

✅ NTC2018 – Capitolo 4 (Costruzioni civili e industriali)
❌ Capitolo 7 NON applicabile (nessuna progettazione in capacità, nessun fattore q)
Questo file implementa nel canvas lo STEP 2 dell’implementazione software: verifiche agli Stati Limite di Esercizio (SLE) per il calcestruzzo armato, in conformità a:

KB_NTC2018_CA.md
KB_NTC2018_AZIONI.md
KB_NTC2018_ANALISI.md
IMPLEMENTAZIONE_NTC2018_VERIFICHE_CAP4_CAP7.md
Ogni verifica qui contenuta è formalmente e rigidamente classificata come CAPITOLO 4.

1. Regole vincolanti di ambito (CAPITOLO 4)

tutte le verifiche sono SLE;
vietato l’uso del fattore di comportamento q;
vietata la progettazione in capacità;
combinazioni di carico solo SLE (rara / frequente / quasi‑permanente);
analisi lineare elastica coerente con KB_NTC2018_ANALISI.
Ogni violazione di queste regole rende la verifica NON CONFORME.

1. Tipologie di verifiche SLE implementate
Rientrano in questo STEP:

SLE – limitazione delle tensioni nel c.a.
SLE – controllo della fessurazione
SLE – verifica delle deformazioni
Tutte le verifiche restituiscono un VerificationResult con:

capitolo_ntc = CAP_4
riferimento normativo §4.1 NTC2018

1. Classe base SLE (CAP_4)

from verification_base import VerificationBase
from verification_result import VerificationResult, VerificationStatus, NormativeReference
from ntc_capitolo import NTCCapitol

class SLEBaseCAP4(VerificationBase):
    """
    Classe base per tutte le verifiche SLE – NTC2018 Capitolo 4
    """

    CAPITOLO = NTCCapitol.CAP_4

4. Verifica SLE – Limitazione delle tensioni
Riferimento normativo: NTC2018 §4.1.4 – Stati Limite di Esercizio

class SLETensioniCA(SLEBaseCAP4):

    def __init__(self, sigma_ed: float, sigma_lim: float):
        self.sigma_ed = sigma_ed
        self.sigma_lim = sigma_lim

    def verify(self) -> VerificationResult:
        if self.sigma_lim <= 0:
            return VerificationResult(
                status=VerificationStatus.NOT_APPLICABLE,
                demand=None,
                capacity=None,
                ratio=None,
                reference=NormativeReference(
                    norma="NTC2018",
                    capitolo="§4.1.4",
                    paragrafo="Limitazione delle tensioni",
                ),
                capitolo_ntc=self.CAPITOLO,
                notes="Limite di tensione non definito",
            )

        ratio = self.sigma_ed / self.sigma_lim
        status = VerificationStatus.OK if ratio <= 1.0 else VerificationStatus.NOT_OK

        return VerificationResult(
            status=status,
            demand=self.sigma_ed,
            capacity=self.sigma_lim,
            ratio=ratio,
            reference=NormativeReference(
                norma="NTC2018",
                capitolo="§4.1.4",
                paragrafo="Limitazione delle tensioni",
            ),
            capitolo_ntc=self.CAPITOLO,
        )

5. Verifica SLE – Fessurazione
Riferimento normativo: NTC2018 §4.1.4 – Controllo della fessurazione

class SLEFessurazioneCA(SLEBaseCAP4):

    def __init__(self, w_ed: float, w_lim: float):
        self.w_ed = w_ed
        self.w_lim = w_lim

    def verify(self) -> VerificationResult:
        if self.w_lim <= 0:
            return VerificationResult(
                status=VerificationStatus.NOT_APPLICABLE,
                demand=None,
                capacity=None,
                ratio=None,
                reference=NormativeReference(
                    norma="NTC2018",
                    capitolo="§4.1.4",
                    paragrafo="Controllo della fessurazione",
                ),
                capitolo_ntc=self.CAPITOLO,
                notes="Limite di fessurazione non definito",
            )

        ratio = self.w_ed / self.w_lim
        status = VerificationStatus.OK if ratio <= 1.0 else VerificationStatus.NOT_OK

        return VerificationResult(
            status=status,
            demand=self.w_ed,
            capacity=self.w_lim,
            ratio=ratio,
            reference=NormativeReference(
                norma="NTC2018",
                capitolo="§4.1.4",
                paragrafo="Controllo della fessurazione",
            ),
            capitolo_ntc=self.CAPITOLO,
        )

6. Verifica SLE – Deformazioni
Riferimento normativo: NTC2018 §4.1.4 – Limitazione delle deformazioni

class SLEDeformazioniCA(SLEBaseCAP4):

    def __init__(self, delta_ed: float, delta_lim: float):
        self.delta_ed = delta_ed
        self.delta_lim = delta_lim

    def verify(self) -> VerificationResult:
        if self.delta_lim <= 0:
            return VerificationResult(
                status=VerificationStatus.NOT_APPLICABLE,
                demand=None,
                capacity=None,
                ratio=None,
                reference=NormativeReference(
                    norma="NTC2018",
                    capitolo="§4.1.4",
                    paragrafo="Limitazione delle deformazioni",
                ),
                capitolo_ntc=self.CAPITOLO,
                notes="Limite di deformazione non definito",
            )

        ratio = self.delta_ed / self.delta_lim
        status = VerificationStatus.OK if ratio <= 1.0 else VerificationStatus.NOT_OK

        return VerificationResult(
            status=status,
            demand=self.delta_ed,
            capacity=self.delta_lim,
            ratio=ratio,
            reference=NormativeReference(
                norma="NTC2018",
                capitolo="§4.1.4",
                paragrafo="Limitazione delle deformazioni",
            ),
            capitolo_ntc=self.CAPITOLO,
        )

7. Esempio di utilizzo nel motore di verifica

engine.add_verification(SLETensioniCA(sigma_ed=8.5, sigma_lim=10.0))
engine.add_verification(SLEFessurazioneCA(w_ed=0.25, w_lim=0.30))
engine.add_verification(SLEDeformazioniCA(delta_ed=18.0, delta_lim=20.0))

Tutti i risultati:

sono CAPITOLO 4;
sono SLE;
sono automaticamente separabili dalle verifiche sismiche.

1. Collegamenti con STEP successivi
Questo file è obbligatorio per:

generazione relazione di calcolo SLE (CAP_4);
confronto SLU/SLE;
validazione preliminare prima di verifiche sismiche (CAP_7).

1. Stato dell’implementazione
✅ STEP 2 completato nel canvas ✅ Verifiche SLE c.a. operative ✅ Distinzione CAP_4 formalizzata ✅ Pronto per:

STEP 3 – Motore combinazioni NTC2018
STEP 4 – ζE edifici esistenti (CAP_7)

Questo file è vincolante per tutte le verifiche SLE in calcestruzzo armato – NTC2018 Capitolo 4.
