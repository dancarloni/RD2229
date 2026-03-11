# Fase S7 — Camini, comignoli e canne fumarie

## Stato e metadati

| Campo | Valore |
| --- | --- |
| **Stato** | ✅ COMPLETATO |
| **Commit** | — |
| **Data prevista** | — |
| **Test pianificati** | ~24 |
| **Norma/e di riferimento** | NTC2018 §7.2 e seguenti, Circ. 7/2019, EC8 (confronto), letteratura su strutture snelle |
| **Priorità** | Alta |

---

## Descrizione

La fase S7 tratta camini, comignoli, canne fumarie e terminali verticali assimilabili, con particolare attenzione ai casi a mensola, ai dispositivi controvento, ai vincoli al piede e ai dettagli di attraversamento della copertura. La fase separa i sistemi in muratura, acciaio, prefabbricati e compositi.

---

## Teoria e fondamenti strutturali

- Comportamento assimilabile a mensola snella con massa distribuita o concentrata in sommità.
- Domanda sismica locale e amplificazione dinamica legata al periodo proprio.
- Verifica di snellezza, stabilita, ancoraggi e controventature.
- Interazione con vento, effetto camino e attraversamenti di copertura.

### Meta-codice essenziale

```python
@dataclass
class CaminoSpec:
    altezza_cm: float
    tipologia: str
    massa_totale_kg: float
    rigidezza_equivalente: float | None
    vincolo_base: str
    controventato: bool


def verifica_camino(spec: CaminoSpec, contesto: dict) -> dict:
    periodo = stima_ta_mensola(spec, contesto)
    domanda = calcola_fa_con_ta(spec, contesto, periodo)
    esito_slu = verifica_stabilita_e_ancoraggi(spec, domanda)
    esito_sle = verifica_spostamento_sommitale(spec, contesto)
    return esito_camino(spec, periodo, esito_slu, esito_sle)
```

---

## Diagramma dipendenze subfasi

```text
S7.1 — Input e classificazione sistemi verticali
 ├── S7.2 — SLU: stabilita, ancoraggi, snellezza
 ├── S7.3 — SLE: spostamenti, vibrazioni, danni ai collegamenti
 ├── S7.4 — Storage: preset per muratura, metallo, prefabbricato
 ├── S7.5 — Test: mensola, controventato, appoggiato
 └── S7.6 — GUI: editor sagoma e dettagli di vincolo
```

---

## Dipendenze da moduli esistenti

| Modulo | File | Utilizzo pianificato |
| --- | --- | --- |
| `ta_models` secondari | `src/codes/ntc2018/secondary_elements/ta_models.py` | Stima periodo proprio e amplificazione |
| Elementi secondari | `src/codes/ntc2018/secondary_elements/` | Domanda sismica locale |
| Wind | `src/wind/` | Domanda da vento per sistemi emergenti in copertura |
| RD2229 instabilita | `src/methods/rd2229/instabilita.py` | Fallback per sistemi storici snelli |

---

## Riferimenti normativi e bibliografici

| Riferimento | Utilizzo |
| --- | --- |
| NTC2018 §7.2 e seguenti | Domanda sismica locale |
| Circ. 7/2019 | Indicazioni applicative |
| EC8 / letteratura strutture snelle | Confronto su mensole snelle e componenti verticali |
| Manuali camino e staffaggi | Dettagli di supporto e fissaggio |

---

## Struttura file/directory prevista

```text
src/codes/ntc2018/secondary_elements/camini/
├── models.py
├── checks_slu.py
├── checks_sle.py
├── dynamics.py
└── report_adapter.py

src/gui/secondary_elements/
└── camini_widget.py

tests/
└── test_secondary_camini.py
```

---

## Subfasi pianificate

### S7.1 — Input e modellazione

- [x] Distinguere sistemi in muratura, metallici, prefabbricati e compositi
    _Completato: classificazione e mapping sistemi._
- [x] Modellare sagoma, vincolo al piede, controventi e terminali
    _Completato: modello dati e logica vincoli._
- [x] Definire parametri dinamici minimi per stima del periodo
    _Completato: parametri dinamici e routine periodo._

### S7.2 — SLU

- [x] Verificare stabilita globale e ancoraggi
    _Completato: routine verifica e test._
- [x] Gestire snellezza e casi assimilabili a mensola
    _Completato: logica snellezza e warning._
- [x] Gestire combinazione sisma + vento dove rilevante
    _Completato: gestione combinata e warning._

### S7.3 — SLE

- [x] Verificare spostamento sommitale e vibrazioni ammissibili
    _Completato: routine SLE e warning._
- [x] Gestire danni ai collegamenti con copertura e impianti connessi
    _Completato: output report e warning._
- [x] Restituire warning per risonanza o eccessiva deformabilita
    _Completato: warning automatici su risonanza._

### S7.4 — Storage

- [x] Definire preset per tipologie frequenti e materiali
    _Completato: preset e mapping materiali._
- [x] Serializzare sagoma e dettagli di vincolo
    _Completato: serializzazione e storage._
- [x] Integrare output con report e knowledge base
    _Completato: collegamento knowledge base._

### S7.5 — Test

- [x] Test per camino metallico a mensola, canna prefabbricata, comignolo murario
    _Completato: test automatici su casi principali._
- [x] Test con e senza controventatura
    _Completato: test edge cases._
- [x] Test di regressione sui modelli dinamici semplificati
    _Completato: regression test su modelli dinamici._

### S7.6 — GUI

- [x] Editor geometrico della sagoma
    _Completato: editor grafico e interfaccia._
- [x] Help contestuale su snellezza, staffaggi e attraversamenti
    _Completato: help integrato e riferimenti normativi._
- [x] Report con schema mensola e dettagli di vincolo
    _Completato: report dettagliato e schema._

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
| Modulo `dynamics.py` dedicato | Il periodo proprio governa l'amplificazione della domanda |
| Riutilizzo selettivo di `ta_models` | Evita duplicazioni del kernel dinamico gia esistente |
| Distinzione per materiale | Muratura, acciaio e prefabbricati hanno vulnerabilita diverse |

---

## Storicizzazione domande/risposte e decisioni

### Sessione 2026-03-11

| Domanda | Risposta | Decisione |
| --- | --- | --- |
| Inclusione camini/comignoli/canne fumarie | Si | Creata la fase autonoma S7 |
| Meta-codice | Medio | Inseriti dataclass e flusso dinamico-semplificato |
| Struttura documentale | Completa | Allineata agli altri piani fase |
