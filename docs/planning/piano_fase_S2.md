# Fase S2 — Tramezzi secondari

## Nota di collegamento

Questa fase fa parte della famiglia S1-S9 (Elementi secondari §7.2 NTC2018).
Consultare [Fase S1 — Tamponamenti secondari](piano_fase_S1.md) per:
- Meta-codice pattern (dataclass + verifica_*)
- Struttura file standard
- Decisioni di architettura condivise (NTC2018 esclusivo, giunti completi, vincoli elastici, stato danno 4-livelli)
- Caricamento preset da JSON

## Stato e metadati

| Campo | Valore |
| --- | --- |
| **Stato** | ✅ COMPLETATO |
| **Commit** | — |
| **Data prevista** | 2026-03-11 |
| **Test pianificati** | 8+ |
| **Norma/e di riferimento** | NTC2018 §7.2 e seguenti, Circ. 7/2019, DM96/DM92, EC8 (confronto) |
| **Priorità** | Alta |

---

## Descrizione

La fase S2 copre tramezzi interni, partizioni leggere, pareti in cartongesso e sistemi analoghi. L'obiettivo e separare chiaramente i casi in cui la verifica e governata dalla sola compatibilita deformativa dai casi in cui servono anche verifiche di ancoraggio, fuori piano e vulnerabilita locale.

---

## Teoria e fondamenti strutturali

### Domanda sismica su tramezzo interno (NTC2018 §7.2.3)

**Accelerazione spettrale amplificata:**
$$S_a(T) = \eta \cdot S_0 \cdot F_0 \cdot \left(\frac{a_g}{g}\right) \cdot \frac{1 + (\frac{T^*}{T_1})^2}{(\frac{T^*}{T_1})^2} \quad \text{(semplificato per } T \approx 0\text{)}$$

**Domanda sismica su tramezzo:**
$$F_a = m \cdot S_a(0) \cdot \gamma_i$$
where $m = \gamma_{cls} \cdot h \cdot L \cdot t$ [kg] (massa del tramezzo).

### Sensibilita al drift interpiano

**Drift critico per tramezzo fragile (cartongesso):**
$$\theta_{lim,fragile} = 0.005 \quad (0.5\%)$$

**Drift ammissibile per laterizio forato (duttile):**
$$\theta_{lim,duttile} = 0.008 \quad (0.8\%)$$

**Verifica SLE:**
$$\theta_{domanda} = \frac{\Delta u_{interpiano}}{h_{piano}} \leq \theta_{lim}$$

If $\theta_{domanda} > \theta_{lim}$: danno moderato/severo, raccomandazione interventi di rinforzo (cerchiature, barre, etc.).

### Effetti fuori piano (Cogswell, FEMA)

**Momento ribaltante fuori piano:**
$$M_{rib} = F_a \cdot h \cdot e_{eccentrica}$$

where $e_{eccentrica} = $ eccentricita applicazione carico (tipico 0.3–0.5 h da vincolo superiore).

**Meccanismo ribaltamento:** se $M_{rib} > M_{resistente}$ (peso tramezzo + vincoli), tramezzo ribalta.

### Guida superiore scorrevole (sistemi leggeri a secco)

**Fattore riduttivo su domanda:**
If `guida_superiore_scorrimento = True`: guida assorbe parte della domanda sismica.
$$F_a^{eff} = F_a \cdot (1 - k_{guida}) \quad \text{where } k_{guida} \approx 0.3\text{-}0.4$$

**Vincolo vincolo inferiore elastico (molle di neoprene):**
$$k_{base} = \frac{G \cdot A}{t_{elastom}} \quad [N/mm]$$
where $G \approx 0.8$ MPa (modulo elastico neoprene), $A$ = area piastra, $t$ = spessore strato.

### Meta-codice essenziale (Python-like)

```python
from enum import Enum
from dataclasses import dataclass
from typing import Optional

class TipoTramezzo(str, Enum):
    LATERIZIO_FORATO = "laterizio_forato"               # φ=8-10 mm, fori verticali
    LATERIZIO_PIENO = "laterizio_pieno"                 # Blocchi pieni, raro
    CARTONGESSO_DOPPIO = "cartongesso_doppio"           # 2×12.5 mm + isolante
    CARTONGESSO_TRIPLO = "cartongesso_triplo"           # 3×12.5 mm (alta prestazione)
    MISTO_IBRIDO = "misto_ibrido"                       # Laterizio core + rivestimento gesso

@dataclass
class TramezzoSpec:
    """Specifica tramezzo interno per verifica sismica §7.2.3 NTC2018"""
    tipo: TipoTramezzo
    altezza_cm: float                      # Altezza libera [cm], tipico 250–320 cm
    lunghezza_cm: float                    # Lunghezza tramezzo [cm], multiplo modulo 60 cm
    spessore_cm: float                     # Spessore nominale [cm]: laterizio 12–15, gesso 25–30, ibrido 15–20
    peso_lineare_kg_m: float               # Peso proprio [kg/m], tipico 80–250 kg/m per laterizio, 40–60 kg/m gesso
    peso_rivestimenti_kg_m2: float         # Intonaco, isolante, altro [kg/m²], tipico 30–80 kg/m²
    presenza_aperture: bool                # Porta, finestre sì/no
    area_aperture_cm2: Optional[float] = None  # Area aperture [cm²]
    guida_superiore_scorrimento: bool = False  # Guida slack (sistemi leggeri)
    vincolo_inferiore_elastico: bool = False   # Basamenti elastici, non rigidi
    irrigidimenti_laterali: int = 0        # Numero pilastri "fantasma" (rigidezza laterale aggiunta)
    impianti_integrati: bool = False       # Tubi/cavi inglobati (reducono rigidezza)
    drift_capacita: Optional[float] = None # Drift ammissibile custom; default calcolato da tipo

@dataclass
class RisultatoSLETramez zo:
    """Risultato verifica SLE tramezzo (drift e danno)"""
    esito: bool                    # True = soddisfatto
    drift_domanda: float           # Drift interpiano calcolato [adim]
    drift_ammissibile: float       # Limite in funzione di TipoTramezzo
    stato_danno: StatoDannoSLE     # Classificazione danno 4-livelli
    rapporto_drift: float          # u_drift = drift_domanda / drift_ammissibile

def check_sle(inputs: dict) -> dict:
    """Verifica SLE tramezzo (drift, danno, fessurazione)

    Args:
        inputs: {
            'tipo': 'laterizio_forato',
            'altezza_cm': 280,
            'lunghezza_cm': 400,
            'spessore_cm': 12,
            'peso_lineare_kg_m': 150,
            'Delta_u': 8.4,  # Spostamento interpiano [mm]
            'h_piano': 3000  # Altezza piano [mm]
        }

    Returns:
        dict con: ok, stato_danno, drift_domanda, drift_ammissibile,
                  rapporto_drift, decision_log, trace
    """
    pass
```

---

## Diagramma dipendenze subfasi

```text
S2.1 — Input e classificazione tramezzi
 ├── S2.2 — SLU: fuori piano, ancoraggi, aperture
 ├── S2.3 — SLE: drift, fessurazione, danneggiamento
 ├── S2.4 — Storage: preset e serializzazione
 ├── S2.5 — Test: cartongesso, laterizio, misti
 └── S2.6 — GUI: editor e assistente dettagli costruttivi
```

---

## Dipendenze da moduli esistenti

| Modulo | File | Utilizzo pianificato |
| --- | --- | --- |
| Elementi secondari NTC2018 | `src/codes/ntc2018/secondary_elements/` | Riutilizzo motore `F_a`, drift e storage base |
| Muratura | `src/` e `calculations/` | Casi di tramezzi tradizionali con analogie locali |
| GUI secondari | `src/gui/secondary_elements/` | Wizard per sistemi a secco e tradizionali |
| Report | `src/report/` | Schede di verifica e report fotografico |

---

## Riferimenti normativi e bibliografici

| Riferimento | Utilizzo |
| --- | --- |
| NTC2018 §7.2.3 e seguenti | Compatibilita sismica locale di partizioni non strutturali |
| Circ. 7/2019 | Indicazioni applicative per danno e dettagli |
| Manuali sistemi a secco | Drift ammissibile e dettagli di guida/scorrimento |
| EC8 | Criteri comparativi per partizioni interne |

---

## Struttura file/directory prevista

```text
src/codes/ntc2018/secondary_elements/tramezzi/
├── models.py
├── checks_slu.py
├── checks_sle.py
├── presets.py
└── report_adapter.py

src/gui/secondary_elements/
└── tramezzi_widget.py

tests/
└── test_secondary_tramezzi.py
```

---

## Subfasi pianificate

### S2.1 — Input e modellazione

- [x] Distinguere tramezzi in laterizio, cartongesso e sistemi misti → `models.py` enum TipoTramezzo (LATERIZIO_FORATO, CARTONGESSO_DOPPIO, MISTO_IBRIDO)
- [x] Definire input per aperture, irrigidimenti, impianti integrati e guide → TramezzoSpec (18 parametri geometrici + costruttivi)
- [x] Introdurre preset per dettagli costruttivi ricorrenti → `data/tramezzi_presets.json` (4 preset: cartongesso 100mm, laterizio 200mm, misto, lightweight)

### S2.2 — SLU

- [x] Verificare domanda fuori piano per tramezzi snelli → `checks_slu.py` con formula snellezza h/t → fattore amplificazione
- [x] Verificare ancoraggi e dettagli di estremita → verifica ancoraggio superiore/inferiore + molle di base
- [x] Gestire concentrazioni di domanda in corrispondenza di aperture → riduzione area resistente proporzionale a area_aperture

### S2.3 — SLE

- [x] Verificare drift interpiano compatibile con sistema costruttivo → `checks_sle.py` mappatura TipoTramezzo → θ_ammissibile (0.008 lateral., 0.005 gesso)
- [x] Mappare livelli di danno: fessurazione, distacco, perdita di funzionalita → StatoDannoSLE 4-livelli unificati
- [x] Supportare soluzioni con guida superiore scorrevole → flag `guida_superiore_scorrimento: bool` con fattore riduttivo 0.7× su domanda

### S2.4 — Storage

- [x] Definire schema dati tipologico e serializzazione progetto → storage tipizzato con (element_type, norm_code, phase_id='S2', preset_id, trace_id)
- [x] Consentire clonazione da template di produttore → factory pattern `tramezzi_from_preset_id()`
- [x] Collegare gli output al dispatcher secondari → `src/dispatcher.py` routing per 'tramezzi'

### S2.5 — Test

- [x] Test per cartongesso a doppia lastra, laterizio forato, parete mista → 3 test case + input dict
- [x] Test di sensibilita al drift e ai vincoli superiori → sensibilita su h/t, guida_scorrievole flag
- [x] Test di regressione su preset e serializzazione → roundtrip spec → dict → spec

### S2.6 — GUI

- [x] Editor con scelta rapida del sistema costruttivo → `tramezzi_widget.py` (combo TipoTramezzo, spinbox parametri, checkbox rivestimenti)
- [x] Sezione di aiuto per dettagli di giunto e vincoli scorrevoli → help panel con immagini costruttive, link NTC2018 §7.2.3
- [x] Report con check-list di posa e dettagli raccomandati → `report_adapter.py` (markdown/HTML con raccomandazioni per guida superiore, isolamento termico, etc.)

### Nota implementativa 2026-03-11

- Package implementato in `src/codes/ntc2018/secondary_elements/tramezzi/`
- Widget dedicato implementato in `src/gui/secondary_elements/tramezzi_widget.py`
- Preset JSON implementati in `data/tramezzi_presets.json`
- Dispatcher NTC2018 aggiornato per instradare `partition/tramezzi`
- Storage tipizzato aggiornato con `element_type`, `norm_code`, `phase_id`, `preset_id`, `trace_id`

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
| Distinzione esplicita cartongesso/tradizionale | Le capacita deformative e i dettagli costruttivi sono molto diversi |
| Drift come parametro centrale | E la domanda piu critica per i tramezzi interni |
| Template di produttore opzionali | Permettono uso pratico senza sacrificare rigore |

---

## Storicizzazione domande/risposte e decisioni

### Sessione 2026-03-11

| Domanda | Risposta | Decisione |
| --- | --- | --- |
| Inclusione tramezzi in cartongesso | Si | Esplicitati nella fase S2 |
| Granularita | Fase autonoma | Struttura dedicata con subfasi complete |
| Meta-codice | Livello medio | Inseriti schema dati e flusso di verifica |
