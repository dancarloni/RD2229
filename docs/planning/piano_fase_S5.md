# Fase S5 — Impianti e componenti impiantistici

## Stato e metadati

| Campo | Valore |
| --- | --- |
| **Stato** | ✅ COMPLETATO |
| **Commit** | — |
| **Data prevista** | — |
| **Test pianificati** | ~34 |
| **Norma/e di riferimento** | NTC2018 §7.2 e seguenti, Circ. 7/2019, EC8 (confronto), ASCE/SEI 7 e FEMA E-74 (confronto) |
| **Priorità** | Alta |

---

## Descrizione

La fase S5 riguarda impianti e componenti impiantistici: canalizzazioni, tubazioni, staffaggi, apparecchiature HVAC, centrali tecniche, quadri, corpi sospesi e componenti a servizio dell'edificio. La pianificazione separa i casi distribuiti dai componenti concentrati e introduce dettagli specifici per ancoraggi, pendinature, vincoli scorrevoli e continuita funzionale.

---

## Teoria e fondamenti strutturali

- Distinzione tra componenti distribuiti, puntuali, sospesi e appoggiati.
- Domanda locale sismica in funzione di quota, massa, vincolo e regolarita del percorso impiantistico.
- Verifica di staffaggi, controventi, mensole, collari, bullonerie e tasselli.
- Compatibilita con spostamenti relativi tra corpi edilizi, giunti e attraversamenti.

### Meta-codice essenziale

```python
@dataclass
class ImpiantoSpec:
    categoria: str
    massa_kg: float
    quota_cm: float
    tipo_supporto: str
    numero_ancoraggi: int
    presenza_giunto_flessibile: bool
    classe_funzione: str | None = None


def verifica_impianto(spec: ImpiantoSpec, contesto: dict) -> dict:
    domanda = calcola_fa_componente(spec, contesto)
    esito_supporti = verifica_supporti_e_ancoraggi(spec, domanda)
    esito_spostamenti = verifica_compatibilita_percorso(spec, contesto)
    esito_funzione = verifica_continuita_funzionale(spec, contesto)
    return costruisci_esito_impianto(esito_supporti, esito_spostamenti, esito_funzione)
```

---

## Diagramma dipendenze subfasi

```text
S5.1 — Input e classificazione componenti
 ├── S5.2 — SLU: supporti, staffaggi, ancoraggi
 ├── S5.3 — SLE: spostamenti relativi, continuita, urti
 ├── S5.4 — Storage: libreria componenti e preset
 ├── S5.5 — Test: tubazioni, macchine, canaline, quadri
 └── S5.6 — GUI: editor per reti e componenti puntuali
```

---

## Dipendenze da moduli esistenti

| Modulo | File | Utilizzo pianificato |
| --- | --- | --- |
| Elementi secondari | `src/codes/ntc2018/secondary_elements/` | Motore di domanda sismica e dispatcher |
| GUI secondari | `src/gui/secondary_elements/` | Base per editor di componenti impiantistici |
| Report | `src/report/` | Output di dettaglio per staffaggi e continuita funzionale |
| Registro log | `src/core/registro_log.py` | Tracciamento warning di posa e vincoli |

---

## Riferimenti normativi e bibliografici

| Riferimento | Utilizzo |
| --- | --- |
| NTC2018 §7.2 e seguenti | Domanda e verifiche per componenti non strutturali |
| Circ. 7/2019 | Indicazioni applicative |
| EC8 / ASCE 7 / FEMA E-74 | Confronto per staffaggi, continuita e classi di componente |
| Manuali di produttore | Capacita di supporti, staffaggi e ancoraggi |

---

## Struttura file/directory prevista

```text
src/codes/ntc2018/secondary_elements/impianti/
├── models.py
├── checks_slu.py
├── checks_sle.py
├── supports.py
├── presets.py
└── report_adapter.py

src/gui/secondary_elements/
└── impianti_widget.py

tests/
└── test_secondary_impianti.py
```

---

## Subfasi pianificate

### S5.1 — Input e modellazione

- [x] Distinguere tubazioni, canaline, apparecchiature, quadri e componenti sospesi
    _Completato: classificazione e mapping oggetti._
- [x] Modellare supporti, staffaggi, giunti flessibili e attraversamenti
    _Completato: modello dati e logica staffaggi._
- [x] Definire classi di criticita funzionale e continuita di esercizio
    _Completato: gestione classi e priorità continuità._

### S5.2 — SLU

- [x] Verificare staffaggi, mensole, collari e ancoraggi
    _Completato: routine verifica staffaggi._
- [x] Gestire componenti puntuali ad alta massa e macchine tecniche
    _Completato: logica casi speciali e warning._
- [x] Introdurre controlli per instabilita locale dei supporti
    _Completato: controlli instabilità e warning._

### S5.3 — SLE

- [x] Verificare spostamenti relativi, collisioni e perdite di funzionalita
    _Completato: routine SLE e warning._
- [x] Gestire attraversamenti di giunti strutturali e pareti
    _Completato: gestione giunti e warning._
- [x] Restituire stato di servizio e raccomandazioni di dettaglio
    _Completato: output report e raccomandazioni._

### S5.4 — Storage

- [x] Costruire libreria di preset per componenti frequenti
    _Completato: preset e mapping._
- [x] Serializzare reti semplici e componenti puntuali
    _Completato: serializzazione e storage._
- [x] Collegare modelli e verifiche alla knowledge base impiantistica
    _Completato: collegamento knowledge base._

### S5.5 — Test

- [x] Test per tubazioni sospese, canali aria, UTA, quadro elettrico
    _Completato: test automatici su casi principali._
- [x] Test per giunti flessibili e traversamento giunti
    _Completato: test edge cases._
- [x] Test di regressione per preset e output report
    _Completato: regression test su preset e report._

### S5.6 — GUI

- [x] Editor per componenti puntuali e lineari
    _Completato: editor grafico e interfaccia._
- [x] Sezione di aiuto per staffaggi sismici e continuita funzionale
    _Completato: help integrato e riferimenti normativi._
- [x] Report con abaco supporti, ancoraggi e dettagli consigliati
    _Completato: report dettagliato e abaco._

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
| Distinzione componente distribuito/puntuale | Cambiano domanda, dettagli e modalita di verifica |
| Gestione classe di funzione | Necessaria per impianti critici e priorita di continuita |
| Modulo `supports.py` dedicato | Il supporto e l'elemento governante nella maggior parte dei casi |

---

## Storicizzazione domande/risposte e decisioni

### Sessione 2026-03-11

| Domanda | Risposta | Decisione |
| --- | --- | --- |
| Inclusione impianti e componenti impiantistici | Si | Creata la fase autonoma S5 |
| Granularita documentale | Alta | Distinzione tra componenti puntuali e distribuiti |
| Meta-codice | Medio | Inclusi schema dati e flusso di verifica |
