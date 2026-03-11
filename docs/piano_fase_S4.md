# Fase S4 — Controsoffitti sospesi

## Stato e metadati

| Campo | Valore |
| --- | --- |
| **Stato** | ✅ COMPLETATO |
| **Commit** | — |
| **Data prevista** | — |
| **Test pianificati** | ~26 |
| **Norma/e di riferimento** | NTC2018 §7.2 e seguenti, Circ. 7/2019, FEMA E-74 (confronto), manuali produttori |
| **Priorità** | Alta |

---

## Descrizione

La fase S4 tratta controsoffitti modulari e continui, pendinature, controventi e staffaggi secondari. Il focus e sulla stabilita dei sistemi sospesi, sulla compatibilita con il drift interpiano e sulla gerarchia dei dettagli costruttivi che evitano il collasso per perdita di appoggio o instabilita dei pendini.

---

## Teoria e fondamenti strutturali

- Domanda inerziale distribuita sul reticolo sospeso.
- Verifica dei pendini, dei sistemi di controvento e dei nodi di bordo.
- Compatibilita con spostamenti interpiano, urti contro elementi adiacenti e perdita di appoggio.
- Differenziazione tra griglia modulare, lastre continue e sistemi tecnici speciali.

### Meta-codice essenziale

```python
@dataclass
class ControsoffittoSpec:
    area_m2: float
    massa_superficiale_kg_m2: float
    passo_pendini_cm: float
    presenza_controventi: bool
    gioco_perimetrale_mm: float
    tipologia: str


def verifica_controsoffitto(spec: ControsoffittoSpec, contesto: dict) -> dict:
    domanda = calcola_fa_superficiale(spec, contesto)
    verifica_pendini = controlla_pendini(spec, domanda)
    verifica_bordo = controlla_gioco_perimetrale(spec, contesto)
    verifica_drift = controlla_compatibilita_drift(spec, contesto)
    return sintetizza_esiti(verifica_pendini, verifica_bordo, verifica_drift)
```

---

## Diagramma dipendenze subfasi

```text
S4.1 — Input e classificazione sistemi sospesi
 ├── S4.2 — SLU: pendini, controventi, appoggi
 ├── S4.3 — SLE: drift, urti, perdita di funzionalita
 ├── S4.4 — Storage: preset modulari e continui
 ├── S4.5 — Test: griglie, lastre continue, impianti integrati
 └── S4.6 — GUI: editor con layout del reticolo
```

---

## Dipendenze da moduli esistenti

| Modulo | File | Utilizzo pianificato |
| --- | --- | --- |
| Elementi secondari | `src/codes/ntc2018/secondary_elements/` | Domanda sismica e drift base |
| GUI secondari | `src/gui/secondary_elements/` | Struttura editor dedicato |
| Report | `src/report/` | Schede dettagli costruttivi e warning |
| Knowledge base | `docs/MEGAPLAN/` | Recupero criteri e casi d'uso storici |

---

## Riferimenti normativi e bibliografici

| Riferimento | Utilizzo |
| --- | --- |
| NTC2018 §7.2 e seguenti | Domanda sismica locale e requisiti generali |
| Circ. 7/2019 | Chiarimenti applicativi |
| FEMA E-74 | Dettagli di controventatura e perdita di appoggio |
| Manuali produttori | Passi massimi, dettagli di bordo, sistemi pendinati |

---

## Struttura file/directory prevista

```text
src/codes/ntc2018/secondary_elements/controsoffitti/
├── models.py
├── checks_slu.py
├── checks_sle.py
├── layout.py
└── report_adapter.py

src/gui/secondary_elements/
└── controsoffitti_widget.py

tests/
└── test_secondary_controsoffitti.py
```

---

## Subfasi pianificate

### S4.1 — Input e modellazione

- [x] Definire modelli per controsoffitti modulari, continui e tecnici
    _Completato: implementato modello dati e casi principali._
- [x] Rappresentare pendini, controventi, giochi perimetrali e discontinuita
    _Completato: logica di rappresentazione e gestione edge cases._
- [x] Integrare layout e zone con impianti sovrapposti
    _Completato: integrazione layout e mapping impianti._

### S4.2 — SLU

- [x] Verificare pendini, appoggi di bordo e controventi
    _Completato: routine di verifica e test._
- [x] Gestire perdita di appoggio e collasso progressivo locale
    _Completato: gestione casi critici e warning._
- [x] Verificare nodi in presenza di corpi illuminanti o apparecchi sospesi
    _Completato: logica per nodi speciali e carichi aggiuntivi._

### S4.3 — SLE

- [x] Verificare compatibilita con drift e urti contro partizioni/impianti
    _Completato: routine di compatibilità e warning._
- [x] Valutare perdita di funzionalita e danneggiamento estetico
    _Completato: output report e warning estetici._
- [x] Restituire limiti e warning su gioco perimetrale insufficiente
    _Completato: warning automatici su gioco insufficiente._

### S4.4 — Storage

- [x] Definire preset per sistemi comuni e produttori
    _Completato: preset e mapping produttori._
- [x] Salvare reticoli e campi con metadati di posa
    _Completato: serializzazione e metadati._
- [x] Collegare il modello alla knowledge base dedicata
    _Completato: collegamento knowledge base._

### S4.5 — Test

- [x] Test su griglia modulare standard e su lastra continua
    _Completato: test automatici su casi principali._
- [x] Test su presenza/assenza di controventi
    _Completato: test edge cases._
- [x] Test di regressione per layout e serializzazione
    _Completato: regression test su layout e storage._

### S4.6 — GUI

- [x] Editor con schema reticolare e pendinature
    _Completato: editor grafico e interfaccia._
- [x] Help contestuale su dettagli di bordo e controventi
    _Completato: help integrato e riferimenti normativi._
- [x] Output report con check-list di posa e manutenzione
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
| Layout separato in `layout.py` | I controsoffitti richiedono una rappresentazione a campi e reticoli |
| Verifica esplicita del gioco perimetrale | Dettaglio decisivo per il comportamento sismico |
| Distinzione tra funzionalita e collasso | Necessaria per report di rischio e gestione edificio |

---

## Storicizzazione domande/risposte e decisioni

### Sessione 2026-03-11

| Domanda | Risposta | Decisione |
| --- | --- | --- |
| Inclusione controsoffitti | Si | Creata la fase autonoma S4 |
| Livello di meta-codice | Medio | Inclusi schema dati e pseudocodice |
| Struttura documentale | Completa | Inseriti diagrammi, dipendenze, tabelle e struttura file |
