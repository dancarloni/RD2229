# Fase S9 — Insegne, cancelli e componenti speciali

## Stato e metadati

| Campo | Valore |
| --- | --- |
| **Stato** | ✅ COMPLETATO |
| **Commit** | — |
| **Data prevista** | — |
| **Test pianificati** | ~27 |
| **Norma/e di riferimento** | NTC2018 §7.2 e seguenti, Circ. 7/2019, EC8 (confronto), manuali di prodotto |
| **Priorità** | Media-Alta |

---

## Descrizione

La fase S9 raccoglie le tipologie speciali richieste in sessione e difficilmente riconducibili in modo pulito ai gruppi precedenti: insegne, pannelli sospesi, cancelli, chiusure tecniche leggere, mensole non impiantistiche e altri componenti locali con comportamento peculiare. La fase funge da contenitore rigoroso ma non generico, con famiglie speciali ben tipizzate e tracciate.

---

## Teoria e fondamenti strutturali

- Casi dominati da supporto puntuale, mensola, sospensione o cinematismo di apertura/chiusura.
- Domanda sismica e talvolta vento dominante per elementi esterni esposti.
- Verifica di cerniere, binari, staffe, bracci, piastre, tasselli e supporti secondari.
- Necessita di distinguere casi staticamente determinati da sistemi mobili o semi-mobili.

### Meta-codice essenziale

```python
@dataclass
class ComponenteSpecialeSpec:
    famiglia: str
    massa_kg: float
    schema_statico: str
    esposizione_esterna: bool
    tipo_supporto: str
    grado_mobilita: str


def verifica_componente_speciale(spec: ComponenteSpecialeSpec, contesto: dict) -> dict:
    domanda_sismica = calcola_fa_componente(spec, contesto)
    domanda_vento = calcola_domanda_vento_se_necessario(spec, contesto)
    domanda_tot = combina_domande(domanda_sismica, domanda_vento)
    esito_supporto = verifica_supporto_speciale(spec, domanda_tot)
    esito_esercizio = verifica_mobilita_e_interferenze(spec, contesto)
    return aggrega_risultato_speciale(esito_supporto, esito_esercizio)
```

---

## Diagramma dipendenze subfasi

```text
S9.1 — Input e tipizzazione dei casi speciali
 ├── S9.2 — SLU: supporti, bracci, cerniere, ancoraggi
 ├── S9.3 — SLE: mobilita, interferenze, battute, danni locali
 ├── S9.4 — Storage: libreria famiglie speciali
 ├── S9.5 — Test: insegne, cancelli, pannelli sospesi, mensole
 └── S9.6 — GUI: selettore famiglia e wizard parametri
```

---

## Dipendenze da moduli esistenti

| Modulo | File | Utilizzo pianificato |
| --- | --- | --- |
| Elementi secondari | `src/codes/ntc2018/secondary_elements/` | Domanda sismica locale e storage base |
| Wind | `src/wind/` | Domanda da vento per componenti esposti |
| GUI secondari | `src/gui/secondary_elements/` | Wizard per famiglie speciali |
| Report | `src/report/` | Schede custom con dettagli costruttivi |

---

## Riferimenti normativi e bibliografici

| Riferimento | Utilizzo |
| --- | --- |
| NTC2018 §7.2 e seguenti | Domanda locale e principi generali |
| Circ. 7/2019 | Criteri applicativi e interpretativi |
| EC8 | Confronto per componenti secondari non standard |
| Manuali di prodotto / ETA | Capacita di staffe, cerniere, binari e supporti |

---

## Struttura file/directory prevista

```text
src/codes/ntc2018/secondary_elements/speciali/
├── models.py
├── checks_slu.py
├── checks_sle.py
├── families.py
└── report_adapter.py

src/gui/secondary_elements/
└── speciali_widget.py

tests/
└── test_secondary_speciali.py
```

---

## Subfasi pianificate

### S9.1 — Input e modellazione

- [x] Definire famiglie: insegne, cancelli, pannelli sospesi, mensole leggere, chiusure tecniche
    _Completato: classificazione e mapping famiglie._
- [x] Modellare gradi di mobilita, schemi statici e supporti
    _Completato: modello dati e logica mobilità._
- [x] Collegare i casi speciali a template rapidi di input
    _Completato: integrazione template e input rapido._

### S9.2 — SLU

- [x] Verificare bracci, staffe, cerniere, piastre e ancoraggi
    _Completato: routine verifica e test._
- [x] Gestire combinazione sisma + vento per elementi esposti
    _Completato: logica combinata e warning._
- [x] Gestire casi mobili con carichi accidentali di battuta o arresto
    _Completato: gestione casi mobili e warning._

### S9.3 — SLE

- [x] Verificare mobilita, interferenze, gioco, battute e danni locali
    _Completato: routine SLE e warning._
- [x] Gestire requisiti di servizio per apertura/chiusura dopo sisma
    _Completato: output report e warning._
- [x] Restituire warning su interferenze con altri componenti
    _Completato: warning automatici su interferenze._

### S9.4 — Storage

- [x] Definire libreria famiglie speciali e preset di supporto
    _Completato: preset e mapping famiglie._
- [x] Serializzare schema statico e gradi di mobilita
    _Completato: serializzazione e storage._
- [x] Integrare knowledge base e note di montaggio
    _Completato: collegamento knowledge base e note._

### S9.5 — Test

- [x] Test per insegna a bandiera, cancello scorrevole, pannello sospeso e mensola leggera
    _Completato: test automatici su casi principali._
- [x] Test con componente esposto al vento e non esposto
    _Completato: test edge cases._
- [x] Test di regressione su famiglie e preset
    _Completato: regression test su preset e storage._

### S9.6 — GUI

- [x] Wizard di selezione famiglia speciale
    _Completato: wizard grafico e interfaccia._
- [x] Help contestuale su supporti, binari e cerniere
    _Completato: help integrato e riferimenti normativi._
- [x] Report con dettagli tipologici e note di esercizio
    _Completato: report dettagliato e note._

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
| Contenitore speciali ma tipizzato | Evita un calderone indistinto mantenendo casi fuori catalogo tracciabili |
| Modulo `families.py` dedicato | Centralizza mapping tra famiglia, input e check applicabili |
| Integrazione con vento opzionale | Molti casi speciali sono esterni o parzialmente esposti |

---

## Storicizzazione domande/risposte e decisioni

### Sessione 2026-03-11

| Domanda | Risposta | Decisione |
| --- | --- | --- |
| Inclusione insegne e cancelli | Si | Creata la fase autonoma S9 |
| Gestione casi fuori catalogo | Tipizzata, non generica | Definita famiglia `speciali/` con mapping esplicito |
| Meta-codice | Medio | Inclusi schema dati e flusso di verifica |
