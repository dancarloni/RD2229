
VERIFICATION_FACTORY_RD2229 – Factory delle verifiche RD 2229/1939
Status: FILE OPERATIVO – CORE DI VERIFICA (VINCOLANTE)
Questo documento definisce la VerificationFactory dedicata al R.D. 2229/1939, responsabile della creazione delle verifiche strutturali a tensioni ammissibili da eseguire tramite il VerificationEngine unico.
La factory RD2229:

non contiene logica di GUI;
non contiene logica di orchestrazione;
non contiene calcolo di sollecitazioni;
istanzia esclusivamente verifiche RD2229, secondo quanto definito in VERIFICHE_RD2229.md.


1. Ruolo della VerificationFactoryRD2229
Nel sistema multi‑normativo:

la GUI seleziona la normativa (project_model.normativa_attiva);
il binding GUI ↔ Core seleziona la factory corretta;
la VerificationFactoryRD2229:costruisce le verifiche compatibili con RD2229;
restituisce oggetti pronti per il VerificationEngine.


La factory non decide se una verifica è necessaria: si limita a crearla quando richiesta.




2. Collegamenti vincolanti
Questo file è valido solo se sono presenti:

VERIFICHE_RD2229.md
KB_RD2229_1939.md
VerificationEngine
VerificationResult
ProjectModel


3. Tipologie di verifiche istanziate
La factory RD2229 deve poter creare le seguenti verifiche:

pressoflessione semplice e composta;
flessione semplice;
taglio;
compressione semplice;
trazione semplice (solo se ammessa).
Ogni verifica è a tensioni ammissibili.


4. Interfaccia della VerificationFactoryRD2229
La factory deve esporre un’interfaccia coerente con il binding GUI ↔ core.

class VerificationFactoryRD2229:
    def create_verifications(
        self,
        sezione,
        materiale,
        sollecitazioni,
        combinazione=None,
    ) -> list:
        """
        Crea e restituisce la lista delle verifiche RD2229
        da eseguire per la sezione e le sollecitazioni fornite.
        """
        raise NotImplementedError




5. Implementazione concettuale
File di riferimento

core/verification/factories/verification_factory_rd2229.py
Struttura consigliata

from core.verification.verification_result import VerificationResult, VerificationStatus
from ntc_capitolo import NTCCapitol

from core.verification.rd2229.verifiche import (
    verifica_pressoflessione_rd2229,
    verifica_flessione_rd2229,
    verifica_taglio_rd2229,
    verifica_compressione_rd2229,
    verifica_trazione_rd2229,
)


class VerificationFactoryRD2229:

    def create_verifications(self, sezione, materiale, sollecitazioni, combinazione=None):
        verifiche = []

        # Pressoflessione / flessione
        verifiche.append(
            verifica_pressoflessione_rd2229(sezione, materiale, sollecitazioni)
        )

        # Taglio
        if 'Tx' in sollecitazioni:
            verifiche.append(
                verifica_taglio_rd2229(sezione, materiale, sollecitazioni)
            )

        # Compressione semplice
        if sollecitazioni.get('N', 0.0) < 0:
            verifiche.append(
                verifica_compressione_rd2229(sezione, materiale, sollecitazioni)
            )

        # Trazione semplice (solo se ammessa)
        if sollecitazioni.get('N', 0.0) > 0:
            verifiche.append(
                verifica_trazione_rd2229(sezione, materiale, sollecitazioni)
            )

        return verifiche




6. Integrazione con il binding GUI ↔ Core
Nel file GUI_VERIFICATION_ENGINE_BINDING.md (già creato), la selezione della factory avviene come segue:

if project_model.normativa_attiva == 'RD2229':
    factory = VerificationFactoryRD2229()
elif project_model.normativa_attiva == 'NTC2018':
    factory = VerificationFactoryNTC2018()


Il VerificationEngine rimane immutato.


7. Output della factory
Ogni verifica restituita:

è un oggetto VerificationResult;
contiene:tensione calcolata;
tensione ammissibile;
rapporto σ/σ_amm;
esito OK / NON OK;
riferimento normativo R.D. 2229/1939;
è marcata con:

capitolo_ntc = NTCCapitol.RD2229




8. Regole di sicurezza normativa
La factory RD2229:

non genera verifiche sismiche;
non genera verifiche SLU / SLE;
non usa fattori di comportamento o capacità;
non accetta combinazioni sismiche;
genera solo verifiche compatibili con la normativa storica.
Ogni uso improprio deve essere bloccato a livello di GUI o binding.


9. Stato finale
✅ VerificationFactory RD2229 definita ✅ Coerente con VERIFICHE_RD2229.md ✅ Integrata nell’architettura multi‑normativa ✅ Pronta per implementazione reale del core


Questo file è vincolante per l’implementazione della VerificationFactory secondo il R.D. 2229/1939.
