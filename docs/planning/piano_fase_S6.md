# Fase S6 — Facciate e rivestimenti secondari

## Stato e metadati

| Campo | Valore |
| --- | --- |
| **Stato** | ✅ COMPLETATO |
| **Commit** | — |
| **Data prevista** | — |
| **Test pianificati** | ~32 |
| **Norma/e di riferimento** | NTC2018 §7.2 e seguenti, Circ. 7/2019, EC8 (confronto), linee guida facciate e manuali produttori |
| **Priorità** | Alta |

---

## Descrizione

La fase S6 copre facciate continue, rivestimenti ventilati, pannelli di facciata, sottostrutture metalliche, schermature e chiusure di involucro esterno non modellate come elementi primari. Il focus e sulla verifica di pannelli, sottostrutture, ancoraggi e giunti, distinguendo tra sistemi rigidi, duttili e scorrevoli.

---

## Teoria e fondamenti strutturali

- Domanda combinata sisma + vento per componenti esterni esposti.
- Drift interpiano come causa principale di crisi di giunti, staffe e pannelli fragili.
- Verifica di tasselli, staffe regolabili, sottostrutture secondarie e bordi pannello.
- Interazione con aperture, giunti di facciata, pannelli vetrati o compositi.

### Meta-codice essenziale

```python
@dataclass
class FacciataSpec:
    sistema: str
    modulo_luce_cm: float
    massa_superficiale_kg_m2: float
    tipo_sottostruttura: str
    tipo_ancoraggio: str
    drift_capacita: float | None = None


def verifica_facciata(spec: FacciataSpec, contesto: dict) -> dict:
    domanda_sismica = calcola_fa_superficiale(spec, contesto)
    domanda_vento = calcola_pressione_vento(spec, contesto)
    esito_slu = verifica_pannello_e_ancoraggi(spec, domanda_sismica, domanda_vento)
    esito_sle = verifica_giunti_e_drift(spec, contesto)
    return aggrega_verifiche_facciata(esito_slu, esito_sle)
```

---

## Diagramma dipendenze subfasi

```text
S6.1 — Input e classificazione sistemi di facciata
 ├── S6.2 — SLU: pannelli, sottostrutture, fissaggi
 ├── S6.3 — SLE: drift, giunti, urti, tenuta
 ├── S6.4 — Storage: libreria sistemi e nodi tipo
 ├── S6.5 — Test: ventilate, curtain wall, rivestimenti pesanti
 └── S6.6 — GUI: configuratore nodi e pannelli
```

---

## Dipendenze da moduli esistenti

| Modulo | File | Utilizzo pianificato |
| --- | --- | --- |
| Wind | `src/wind/` | Domanda da vento per involucro esterno |
| Elementi secondari | `src/codes/ntc2018/secondary_elements/` | Domanda sismica, drift e dispatcher |
| GUI secondari | `src/gui/secondary_elements/` | Editor per pannelli e nodi di facciata |
| Report | `src/report/` | Schede nodi, ancoraggi e giunti |

---

## Riferimenti normativi e bibliografici

| Riferimento | Utilizzo |
| --- | --- |
| NTC2018 §7.2 e seguenti | Verifica sismica degli elementi non strutturali |
| Circ. 7/2019 | Indicazioni applicative |
| EC8 | Criteri comparativi per facciate e cladding |
| Manuali e ETA dei sistemi di facciata | Capacita di ancoraggi e giunti |

---

## Struttura file/directory prevista

```text
src/codes/ntc2018/secondary_elements/facciate/
├── models.py
├── checks_slu.py
├── checks_sle.py
├── joints.py
├── presets.py
└── report_adapter.py

src/gui/secondary_elements/
└── facciate_widget.py

tests/
└── test_secondary_facciate.py
```

---

## Subfasi pianificate

### S6.1 — Input e modellazione

- [x] Distinguere curtain wall, facciata ventilata, pannello prefabbricato, rivestimento pesante
    _Completato: classificazione e mapping sistemi._
- [x] Modellare pannelli, sottostrutture, giunti e fissaggi
    _Completato: modello dati e logica giunti._
- [x] Collegare i nodi tipo alla knowledge base di dettaglio
    _Completato: collegamento knowledge base e nodi tipo._

### S6.2 — SLU

- [x] Verificare pannelli, staffe, sottostrutture e fissaggi
    _Completato: routine verifica e test._
- [x] Gestire combinazione sisma + vento dove necessaria
    _Completato: logica combinata e warning._
- [x] Gestire casi con pannelli fragili o elementi vetrati
    _Completato: gestione casi fragili e warning._

### S6.3 — SLE

- [x] Verificare drift interpiano, corsa dei giunti e urti pannello-telaio
    _Completato: routine SLE e warning._
- [x] Gestire perdita di tenuta e danni reversibili/non reversibili
    _Completato: output report e warning._
- [x] Restituire warning su giunto insufficiente e rischio martellamento
    _Completato: warning automatici su giunti._

### S6.4 — Storage

- [x] Definire libreria di nodi tipo e sistemi di facciata
    _Completato: preset e mapping sistemi._
- [x] Serializzare pannelli, staffe e sottostrutture
    _Completato: serializzazione e storage._
- [x] Collegare parametri da produttore e note di montaggio
    _Completato: collegamento knowledge base e note._

### S6.5 — Test

- [x] Test per facciata ventilata, curtain wall e pannello prefabbricato
    _Completato: test automatici su casi principali._
- [x] Test con combinazione sisma-vento
    _Completato: test edge cases._
- [x] Test di regressione su giunti e ancoraggi
    _Completato: regression test su giunti e storage._

### S6.6 — GUI

- [x] Configuratore pannello/nodo tipo
    _Completato: editor grafico e interfaccia._
- [x] Help contestuale su giunti, tolleranze e dettagli di posa
    _Completato: help integrato e riferimenti normativi._
- [x] Report con abaco nodi e check-list di montaggio
    _Completato: report dettagliato e checklist._

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
| Integrazione esplicita con vento | Per le facciate il vento e spesso co-governante |
| Modulo `joints.py` dedicato | I giunti governano il comportamento in esercizio |
| Nodi tipo serializzabili | Necessari per riuso pratico e report coerente |

---

## Storicizzazione domande/risposte e decisioni

### Sessione 2026-03-11

| Domanda | Risposta | Decisione |
| --- | --- | --- |
| Inclusione facciate e rivestimenti | Si | Creata la fase autonoma S6 |
| Necessita di meta-codice | Si | Inseriti schema dati e pseudocodice |
| Struttura documentale | Completa | Allineata agli altri file `piano_fase_*.md` |
