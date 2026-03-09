
GUI – VerificationEngine Binding (Collegamento GUI ↔ Core)
Status: FILE OPERATIVO – BINDING GUI/CORE (VINCOLANTE)
Questo documento definisce in modo completo e non ambiguo il collegamento tra le View GUI (SezioniMaterialiView, SollecitazioniView) e il motore di verifica (VerificationEngine) già implementato.
Obiettivo:

costruire il contesto di verifica a partire dallo stato del ProjectModel;
invocare il core di verifica (CAP_4 / CAP_7);
salvare i VerificationResult nel ProjectModel;
mantenere separazione totale tra GUI e logica normativa.

1. Dipendenze e precondizioni (vincolanti)
Questo binding è valido solo se esistono e sono coerenti:

ProjectModel (stato centrale GUI);
SezioniMaterialiView → assegna project_model.materiale e project_model.sezione;
SollecitazioniView → assegna project_model.sollecitazioni;
VerificationEngine e verifiche atomiche (CAP_4 / CAP_7);
modelli di risultato VerificationResult, NTCCapitol, VerificationStatus.
Regola hard: la GUI non crea formule, non decide la norma, non interpreta risultati.

1. Flusso dati (end‑to‑end)

GUI Views
  ├─ SezioniMaterialiView ──┐
  │                          │
  ├─ SollecitazioniView ─────┼─▶ ProjectModel
  │                          │
  └─ Normativa/Combinazioni ─┘
            │
            ▼
   VerificationEngineBinding
            │
            ▼
     VerificationEngine
            │
            ▼
     VerificationResult[*]
            │
            ▼
        ProjectModel.verifiche_cap4 / verifiche_cap7

1. Responsabilità del Binding
Il binding deve:

verificare la completezza minima dei dati (sezione, materiale, sollecitazioni);
costruire il contesto di verifica (input per il core);
istanziare e popolare VerificationEngine;
eseguire le verifiche pertinenti (CAP_4 / CAP_7);
smistare i risultati per capitolo NTC;
aggiornare il ProjectModel.

1. Codice – gui/binding/verification_engine_binding.py

from core.verification.verification_engine import VerificationEngine
from core.verification.verification_result import VerificationStatus
from ntc_capitolo import NTCCapitol

class VerificationEngineBinding:
    """
    Collega la GUI (ProjectModel) al VerificationEngine.
    Nessuna logica normativa è implementata qui.
    """

    def __init__(self, project_model, verification_factory):
        """
        :param project_model: stato centrale della GUI
        :param verification_factory: factory che crea le verifiche atomiche
        """
        self.project_model = project_model
        self.verification_factory = verification_factory

    # --------------------------------------------------------------
    # API principale
    # --------------------------------------------------------------

    def run_verifications(self):
        self._check_prerequisites()

        engine = VerificationEngine()

        # 1) Costruzione verifiche CAP_4
        if self._cap4_enabled():
            for v in self.verification_factory.create_cap4_verifications(
                sezione=self.project_model.sezione,
                materiale=self.project_model.materiale,
                sollecitazioni=self.project_model.sollecitazioni,
                combinazione=self.project_model.combinazione_attiva,
            ):
                engine.add(v)

        # 2) Costruzione verifiche CAP_7
        if self._cap7_enabled():
            for v in self.verification_factory.create_cap7_verifications(
                sezione=self.project_model.sezione,
                materiale=self.project_model.materiale,
                sollecitazioni=self.project_model.sollecitazioni,
                combinazione=self.project_model.combinazione_attiva,
            ):
                engine.add(v)

        # 3) Esecuzione
        results = engine.run()

        # 4) Smistamento risultati nel ProjectModel
        self._store_results(results)

        return results

    # --------------------------------------------------------------
    # Verifiche preliminari
    # --------------------------------------------------------------

    def _check_prerequisites(self):
        if self.project_model.sezione is None:
            raise RuntimeError("Sezione non assegnata al progetto")

        if self.project_model.materiale is None:
            raise RuntimeError("Materiale non assegnato al progetto")

        if not self.project_model.sollecitazioni:
            raise RuntimeError("Sollecitazioni non definite")

    def _cap4_enabled(self) -> bool:
        return self.project_model.normativa_verifica in (NTCCapitol.CAP_4, NTCCapitol.CAP_7)

    def _cap7_enabled(self) -> bool:
        return self.project_model.normativa_verifica == NTCCapitol.CAP_7

    # --------------------------------------------------------------
    # Gestione risultati
    # --------------------------------------------------------------

    def _store_results(self, results):
        self.project_model.verifiche_cap4 = []
        self.project_model.verifiche_cap7 = []

        for r in results:
            if r.capitolo_ntc == NTCCapitol.CAP_4:
                self.project_model.verifiche_cap4.append(r)
            elif r.capitolo_ntc == NTCCapitol.CAP_7:
                self.project_model.verifiche_cap7.append(r)

5. Factory delle verifiche (contratto richiesto)
Il binding non conosce le singole verifiche. Si appoggia a una factory.

class VerificationFactory:
    def create_cap4_verifications(self, sezione, materiale, sollecitazioni, combinazione):
        """Ritorna una lista di verifiche CAP_4 (SLU/SLE)."""
        raise NotImplementedError

    def create_cap7_verifications(self, sezione, materiale, sollecitazioni, combinazione):
        """Ritorna una lista di verifiche CAP_7 (capacità/gerarchia)."""
        raise NotImplementedError

6. Integrazione con le View GUI

SollecitazioniView → salva project_model.sollecitazioni
SezioniMaterialiView → salva project_model.sezione e project_model.materiale
Bottone “Esegui verifiche” (in GUI controller) → chiama:

binding.run_verifications()

RisultatiView → legge:project_model.verifiche_cap4
project_model.verifiche_cap7

1. Regole di sicurezza normativa

il binding rifiuta l’esecuzione se i dati minimi mancano;
CAP_7 non viene eseguito se non abilitato dal workflow;
i risultati sono sempre marcati con capitolo_ntc;
nessun risultato viene interpretato o modificato dalla GUI.

1. Stato
✅ Binding GUI ↔ Core definito ✅ Separazione responsabilità garantita ✅ Pronto per integrazione in main.py ✅ Nessun refactor richiesto

Questo file è vincolante per il collegamento tra GUI e VerificationEngine nel software NTC2018.
