# A.2 — MaterialSource Strutturata
# Contesto completo per implementazione futura

## Obiettivo
Collegare ogni materiale alla sua fonte normativa con riferimento preciso
(norma, articolo, paragrafo, tabella), abilitando citazione automatica nei tabulati.

## Stato attuale: 3 entita' parallele NON collegate

### 1. MaterialSource (LEGACY — da eliminare)
- File: `src/legacy/material_sources.py` (~330 righe)
- Contiene: MaterialSource dataclass, CalculationMethod enum (TA/SL/SP/SPER),
  MaterialSourceLibrary CRUD, _get_default_sources() con 9 norme,
  logica di calcolo per RD2229/DM72/DM92/DM96
- AZIONE: estrarre dati utili (9 fonti + enum), poi ELIMINARE il file
- La logica di calcolo e' GIA' coperta da material_model.py e concrete_strength.py

### 2. NormRef (MANTENERE — scope: check specifications)
- File: `src/checks/registry.py`
- Struttura: NormRef(source_id, clause, description)
- Usato in: CheckSpec per specificare la norma di riferimento di ogni check

### 3. NormReference (MANTENERE — scope: risultati check)
- File: `src/core_calculus/contracts.py`
- Struttura: NormReference(norm_code, chapter, paragraph, formula_label, ...)
- Usato in: SingleCheckResult per tracciare la norma nel risultato

### Modello Material attuale
- File: `src/materials/material_model.py` (~804 righe)
- Campo: `norma_riferimento: str` (es. "NTC2018") — solo codice, senza dettaglio

### Cataloghi JSON attuali
- 10 file in `data/materials/catalogo_*.json`, 97 materiali totali
- Hanno solo `"norma_riferimento": "NTC2018"` — nessun articolo/paragrafo

### sources.yaml
- File: `docs/normative/sources.yaml`
- Contiene 8 fonti: RD2229, DM92, DM96, NTC2018, ISO834, EN1992_1_2,
  EN1991_1_4, CNR_DT207, NTC2018_CIRC
- Campi: id, title, year, authority, link, copyright_note, freely_available, notes

## Piano di migrazione

### Nuovi file da creare

| File | Contenuto |
|------|-----------|
| `src/materials/material_source.py` | MaterialSource dataclass (nuova), MetodoCalcolo enum (da legacy CalculationMethod), MaterialNormRef dataclass |
| `data/materials/material_sources.json` | 9 fonti da legacy + fonti aggiuntive da sources.yaml |

### File da modificare

| File | Modifica |
|------|----------|
| `src/materials/material_model.py` | Aggiungere `source_refs: list[dict] = field(default_factory=list)`. Aggiornare to_dict()/from_dict(). Default lista vuota per retrocompatibilita'. |
| `src/materials/material_repo.py` | load_sources() da list[dict] a list[MaterialSource]. get_source() tipizzato. |
| `data/materials/catalogo_ntc2018.json` | Aggiungere riferimenti: §4.1 cls, §4.2 acciaio, §4.5 muratura, Tab. 4.1.I, 4.2.I |
| `data/materials/catalogo_rd2229.json` | Aggiungere riferimenti: Art. 10-14 tensioni ammissibili |
| `src/report/tabulati_calcolo.py` | Sezione "Riferimenti normativi materiali" |

### File da eliminare

| File | Motivo |
|------|--------|
| `src/legacy/material_sources.py` | Dati migrati, logica gia' coperta. Verificare prima che nessun import attivo punti a questo file. Aggiornare eventuali import in `src/legacy/ui/historical_material_window.py`. |

## Strutture dati nuove

### MaterialSource (nuova, in src/materials/material_source.py)
```python
@dataclass
class MaterialSource:
    id: str                     # es. "NTC2018", "RD2229"
    name: str                   # es. "Norme Tecniche Costruzioni 2018"
    year: int                   # es. 2018
    calculation_method: MetodoCalcolo  # TA, SL, SP, SPER
    is_historical: bool         # True per RD2229, DM72, etc.
    reference: str              # citazione breve
    description: str            # descrizione
    notes: str = ""             # note aggiuntive

class MetodoCalcolo(str, Enum):
    TA = "tensioni_ammissibili"
    SL = "stati_limite"
    SP = "semi_probabilistico"
    SPER = "sperimentale"
```

### MaterialNormRef (nuova, stesso file)
```python
@dataclass
class MaterialNormRef:
    norma_id: str               # es. "NTC2018"
    articolo: str               # es. "§4.1.2.1.1"
    tabella: str | None = None  # es. "Tab. 4.1.I"
    formula: str | None = None  # es. "f_cd = alpha_cc * f_ck / gamma_c"
    parametro: str = ""         # es. "f_ck", "gamma_c"
    descrizione_it: str = ""    # descrizione in italiano
```

## 9 fonti da migrare dal legacy

Da `_get_default_sources()` in `src/legacy/material_sources.py`:
1. RD2229 — Regio Decreto 1939, TA
2. DM72 — DM 30/05/1972, TA
3. DM92 — DM 14/02/1992, SL
4. DM96 — DM 09/01/1996, SL
5. OPCM3274 — Ordinanza 2003, SL
6. NTC2008 — DM 14/01/2008, SL
7. NTC2018 — DM 17/01/2018, SL
8. LAB_TEST — Prove sperimentali, SPER
9. CUSTOM — Personalizzato, SP

Fonti aggiuntive da sources.yaml non presenti nel legacy:
- DM87 (muratura), Circ81, ISO834, EN1992_1_2, EN1991_1_4, CNR_DT207, NTC2018_CIRC

## Note architetturali

1. MaterialNormRef e' specifica per i materiali. NON unificare ora con NormRef
   o NormReference (scope diversi: check vs risultati vs materiali).
   Eventuale unificazione in Fase H.

2. source_refs opzionale in Material — cataloghi esistenti continuano a
   funzionare senza modifiche (lista vuota = nessun riferimento).

3. JSON nativo per tutto, NO dipendenza PyYAML.

4. Popolare i cataloghi con riferimenti normativi e' incrementale:
   NTC2018 e RD2229 per primi, gli altri progressivamente.
