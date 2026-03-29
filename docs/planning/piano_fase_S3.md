# Fase S3 — Parapetti e balaustre secondari

## Stato e metadati

| Campo | Valore |
| --- | --- |
| **Stato** | ✅ COMPLETATO |
| **Commit** | — (implementazione 2026-03-11) |
| **Data prevista** | — |
| **Test pianificati** | ~28 |
| **Norma/e di riferimento** | NTC2018 §7.2 e seguenti, Circ. 7/2019, EC1/EC8 (confronto), norme prodotto |
| **Priorità** | Alta |

---

## Descrizione

La fase S3 copre parapetti, balaustre, recinzioni tecniche di copertura e sistemi assimilabili. La pianificazione include sia le azioni sismiche sugli elementi secondari sia le azioni orizzontali d'uso e i problemi di ancoraggio locale, distinguendo i dispositivi con montanti puntuali dai parapetti continui.

---

## Teoria e fondamenti strutturali

- Domanda combinata: carico orizzontale d'uso + inerzia sismica locale.
- Verifica di montanti, correnti, piastre di base, tasselli e fissaggi chimici o meccanici.
- Compatibilita con spostamenti del bordo solaio o del cordolo di ancoraggio.
- Vulnerabilita di vetri, pannelli di tamponamento e sistemi misti acciaio-vetro.

### Meta-codice essenziale

```python
@dataclass
class ParapettoSpec:
    altezza_cm: float
    tipologia: str
    interasse_montanti_cm: float | None
    massa_lineare_kg_m: float
    tipo_ancoraggio: str
    resistenza_ancoraggio_kN: float | None


def verifica_parapetto(spec: ParapettoSpec, contesto: dict) -> dict:
    domanda_sismica = calcola_fa_lineare(spec, contesto)
    domanda_uso = carico_orizzontale_normativo(spec)
    combinazione = combina_domande(domanda_sismica, domanda_uso)
    return verifica_montanti_e_ancoraggi(spec, combinazione)
```

---

## Diagramma dipendenze subfasi

```text
S3.1 — Input e classificazione parapetti
 ├── S3.2 — SLU: montanti, piastre, ancoraggi
 ├── S3.3 — SLE: spostamenti, vibrazioni, integrita pannelli
 ├── S3.4 — Storage: preset per acciaio, vetro, muratura
 ├── S3.5 — Test: lineari, puntuali, misti
 └── S3.6 — GUI: configuratore e tabella dettagli costruttivi
```

---

## Dipendenze da moduli esistenti

| Modulo | File | Utilizzo pianificato |
| --- | --- | --- |
| Wind special structures | `src/wind/special_structures.py` | Supporto per parapetti e recinzioni esposte al vento |
| Elementi secondari | `src/codes/ntc2018/secondary_elements/` | Calcolo domanda sismica locale |
| Acciaio | `src/steel/` | Verifiche di montanti metallici e piastre |
| Report | `src/report/` | Restituzione dei dettagli di ancoraggio |

---

## Riferimenti normativi e bibliografici

| Riferimento | Utilizzo |
| --- | --- |
| NTC2018 §7.2 e seguenti | Domanda sismica locale per elementi secondari |
| Norme d'uso parapetti | Azioni orizzontali di servizio |
| EC1 / EC8 | Confronto su carichi e componenti non strutturali |
| ETA / manuali ancoranti | Capacita locali di fissaggio |

---

## Struttura file/directory prevista

```text
src/codes/ntc2018/secondary_elements/parapetti/
├── models.py
├── checks_slu.py
├── checks_sle.py
├── anchorage.py
└── report_adapter.py

src/gui/secondary_elements/
└── parapetti_widget.py

tests/
└── test_secondary_parapetti.py
```

---

## Subfasi pianificate


### S3.1 — Input e modellazione

- [x] Distinti parapetti continui, a montanti, vetrati e recinzioni tecniche (`ParapettoSpec`, `TipoParapetto`)
- [x] Modellata geometria, massa e dettagli di ancoraggio (parametri e metodi dedicati)
- [x] Definita interazione con bordo solaio o cordolo (campo dedicato, logica checks)

*Completato: 2026-03-11 — vedi meta-codice e struttura dati*

### S3.2 — SLU

- [x] Verificata domanda combinata su montanti e correnti (`checks_slu.py`)
- [x] Verificate piastre, tasselli e ancoraggi chimici/meccanici (fattori riduzione, n_ancoraggi)
- [x] Gestiti casi con pannelli vetrati o tamponamenti inseriti (logica in RisultatoSLUParapetto)

*Completato: 2026-03-11 — vedi formule e meta-codice*

### S3.3 — SLE

- [x] Verificati spostamenti ammissibili e vibrazioni locali (`checks_sle.py`)
- [x] Gestita integrità di pannelli fragili e vetri (mapping su stato_danno)
- [x] Restituiti warning su dettagli costruttivi insufficienti (report_adapter)

*Completato: 2026-03-11 — vedi meta-codice e benchmark*

### S3.4 — Storage

- [x] Definiti preset per tipologie comuni di parapetto (`data/parapetti_presets.json`)
- [x] Serializzati dettagli di ancoraggio e componenti (API pubblica, metodi to_dict)
- [x] Collegate le schede a knowledge base e report (report_adapter)

*Completato: 2026-03-11 — vedi struttura file/directory prevista*

### S3.5 — Test

- [x] Test per parapetto metallico, vetrato, muretto con ringhiera (`test_secondary_parapetti.py`)
- [x] Test su ancoraggi con capacità nota e incerta (sensibilità parametri)
- [x] Test di combinazione vento + sisma + carico d'uso dove richiesto (dispatcher routing)

*Completato: 2026-03-11 — vedi sezione Validazione e benchmark numerici*

### S3.6 — GUI

- [x] Configuratore rapido di tipologia e fissaggio (`parapetti_widget.py`)
- [x] Help su dettagli ETA e posa in opera (docstring inline, aiuto contestuale)
- [x] Report con check-list e viste schematiche (report_adapter.py)

*Completato: 2026-03-11 — vedi struttura file/directory prevista*

---

## Letteratura e provenienza formule

- Normativa primaria: NTC2018 §7.2.x (specifico per fase), Circ. 7/2019; confronti EC8/FEMA/EN dove pertinente.
- Formula principale: descrizione generica (domanda sismica, fattori modificatori, etc.) con riferimenti a [SECONDARY_ELEMENTS_EXPANDED_PLAN.md].
- Le formule adottate derivano direttamente dai paragrafi normativi citati e da letteratura tecnica (FEMA E-74, EN, manuali di prodotto).

## Validazione e benchmark numerici

- La validazione segue la strategia in `docs/SECONDARY_ELEMENTS_VALIDATION.md`: test unitari per modelli, test di integrazione per pipeline, test di stato danno, test su dispatcher, benchmark contro casi noti.
- Esempio benchmark (fase specifica) viene fornito nel documento di validazione; i risultati numerici esatti sono replicabili dai casi di test dedicati.

## Edge cases e scenari limite

- Elenco non esaustivo di edge cases che devono essere considerati in fase di sviluppo e test (es. geometrie fuori range, dati mancanti, materiali fragili, vincoli assenti).
- Gli scenari limite sono documentati anche in `docs/SECONDARY_ELEMENTS_VALIDATION.md` e verificati tramite test specifici.

---

## Decisioni architetturali

| Decisione | Motivazione |
| --- | --- |
| Domanda combinata d'uso e sisma | Per parapetti l'uso ordinario non e separabile dalla sicurezza locale |
| Modulo `anchorage.py` dedicato | Il dettaglio di fissaggio e spesso l'elemento governante |
| Preset per sistemi vetrati | Casi pratici frequenti e delicati |

---

## Storicizzazione domande/risposte e decisioni

### Sessione 2026-03-11

| Domanda | Risposta | Decisione |
| --- | --- | --- |
| Inclusione parapetti e balaustre | Si | Creata la fase autonoma S3 |
| Struttura file di piano | Come gli altri `piano_fase_*.md` | Applicata integralmente |
| Meta-codice | Medio | Inclusi dataclass e pseudocodice |
