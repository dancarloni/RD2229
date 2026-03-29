# Fase S8 — Scaffalature, arredi fissati e contenuti

## Stato e metadati

| Campo | Valore |
| --- | --- |
| **Stato** | ✅ COMPLETATO |
| **Commit** | — |
| **Data prevista** | — |
| **Test pianificati** | ~25 |
| **Norma/e di riferimento** | NTC2018 §7.2 e seguenti, Circ. 7/2019, FEMA E-74 (confronto), linee guida di prodotto |
| **Priorità** | Media-Alta |

---

## Descrizione

La fase S8 riguarda scaffalature, arredi tecnici fissati, archivi, librerie, armadiature industriali e contenuti significativi suscettibili di ribaltamento, scorrimento o espulsione del contenuto. L'obiettivo e gestire in modo distinto il telaio secondario dell'oggetto e la sua interazione col contenuto immagazzinato.

---

## Teoria e fondamenti strutturali

- Meccanismi principali: ribaltamento, scorrimento, rottura degli ancoraggi, perdita del contenuto.
- Domanda sismica locale dipendente da massa totale, posizione del baricentro e quota.
- Necessita di distinguere sistema fissato e sistema libero o parzialmente vincolato.
- Verifica del contenuto come massa partecipante o come carico mobile interno.

### Meta-codice essenziale

```python
@dataclass
class ScaffalaturaSpec:
    altezza_cm: float
    larghezza_cm: float
    profondita_cm: float
    massa_vuota_kg: float
    massa_contenuto_kg: float
    ancorata: bool
    tipo_ancoraggio: str | None = None


def verifica_scaffalatura(spec: ScaffalaturaSpec, contesto: dict) -> dict:
    massa_tot = spec.massa_vuota_kg + spec.massa_contenuto_kg
    domanda = calcola_fa_massa_concentrata(massa_tot, contesto)
    esito_rib = verifica_ribaltamento(spec, domanda)
    esito_scor = verifica_scorrimento(spec, domanda)
    esito_anc = verifica_ancoraggi_scaffalatura(spec, domanda)
    return sintetizza_scaffalatura(esito_rib, esito_scor, esito_anc)
```

---

## Diagramma dipendenze subfasi

```text
S8.1 — Input e classificazione oggetti fissati
 ├── S8.2 — SLU: ribaltamento, scorrimento, ancoraggi
 ├── S8.3 — SLE: perdita contenuto, deformazioni, servizio
 ├── S8.4 — Storage: preset per scaffali, armadi, archivi
 ├── S8.5 — Test: sistemi ancorati e non ancorati
 └── S8.6 — GUI: editor geometria e contenuto
```

---

## Dipendenze da moduli esistenti

| Modulo | File | Utilizzo pianificato |
| --- | --- | --- |
| Elementi secondari | `src/codes/ntc2018/secondary_elements/` | Domanda sismica locale e dispatcher |
| GUI secondari | `src/gui/secondary_elements/` | Editor dedicato per arredi tecnici |
| Report | `src/report/` | Tavole di verifica e warning sul contenuto |
| Registro log | `src/core/registro_log.py` | Segnalazione di casi non ancorati o critici |

---

## Riferimenti normativi e bibliografici

| Riferimento | Utilizzo |
| --- | --- |
| NTC2018 §7.2 e seguenti | Domanda locale per elementi non strutturali |
| Circ. 7/2019 | Indicazioni applicative |
| FEMA E-74 | Dettagli su arredi, scaffalature e contenuti |
| Manuali di prodotto | Capacita di ancoraggi e configurazioni di scaffalatura |

---

## Struttura file/directory prevista

```text
src/codes/ntc2018/secondary_elements/scaffalature/
├── models.py
├── checks_slu.py
├── checks_sle.py
├── content_models.py
└── report_adapter.py

src/gui/secondary_elements/
└── scaffalature_widget.py

tests/
└── test_secondary_scaffalature.py
```

---

## Subfasi pianificate

### S8.1 — Input e modellazione

- [x] Distinguere scaffali industriali, armadi tecnici, arredi fissati e archivi
    _Completato: classificazione e mapping oggetti._
- [x] Modellare geometria, massa vuota, massa contenuto e baricentro equivalente
    _Completato: modello dati e logica baricentro._
- [x] Distinguere sistemi ancorati, non ancorati e parzialmente vincolati
    _Completato: gestione classi e mapping vincoli._

### S8.2 — SLU

- [x] Verificare ribaltamento e scorrimento
    _Completato: routine verifica e test._
- [x] Verificare ancoraggi e collegamenti locali
    _Completato: logica ancoraggi e warning._
- [x] Gestire distribuzione del contenuto su piu livelli
    _Completato: gestione distribuzione e warning._

### S8.3 — SLE

- [x] Verificare perdita di contenuto e danni di servizio
    _Completato: routine SLE e warning._
- [x] Gestire spostamenti relativi e apertura accidentale di vani
    _Completato: output report e warning._
- [x] Restituire priorita di messa in sicurezza e livelli di danno
    _Completato: warning automatici su priorità._

### S8.4 — Storage

- [x] Definire preset per tipologie comuni di arredo tecnico
    _Completato: preset e mapping arredi._
- [x] Serializzare contenuto e configurazioni di ancoraggio
    _Completato: serializzazione e storage._
- [x] Collegare il modello a checklist di posa e manutenzione
    _Completato: collegamento checklist e knowledge base._

### S8.5 — Test

- [x] Test per armadio non ancorato, scaffale industriale ancorato, archivio compatto
    _Completato: test automatici su casi principali._
- [x] Test con diverse distribuzioni del contenuto
    _Completato: test edge cases._
- [x] Test di regressione su soglie di ribaltamento e scorrimento
    _Completato: regression test su soglie e storage._

### S8.6 — GUI

- [x] Editor con livelli e contenuto distribuito
    _Completato: editor grafico e interfaccia._
- [x] Help contestuale su ancoraggi minimi e rischio espulsione contenuto
    _Completato: help integrato e riferimenti normativi._
- [x] Report con classifica priorita di intervento
    _Completato: report dettagliato e classifica._

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
| Modello esplicito del contenuto | Il contenuto governa spesso la massa partecipante |
| Distinzione ancorato/non ancorato | Cambia radicalmente il meccanismo di crisi |
| Report con priorita di intervento | Utile in contesti di sicurezza d'esercizio |

---

## Storicizzazione domande/risposte e decisioni

### Sessione 2026-03-11

| Domanda | Risposta | Decisione |
| --- | --- | --- |
| Inclusione scaffalature e contenuti | Si | Creata la fase autonoma S8 |
| Livello di dettaglio | Granulare | Separati telaio e contenuto |
| Meta-codice | Medio | Inclusi schema dati e flusso di verifica |
