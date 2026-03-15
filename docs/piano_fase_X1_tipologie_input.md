# Fase X1 — Tipologie e Input Solai

## Stato e metadati

| Campo | Valore |
| --- | --- |
| Stato | TODO |
| Commit | — |
| Data | 2026-03-15 |
| Dipendenza master | docs/piano_fase_X.md |
| Test pianificati | ~100 |
| Ambito | Catalogo tipologie, input, validazione |

---

## Scopo del modulo

Definire un contratto dati univoco per tutte le tipologie di solaio in V1:
- laterocemento
- predalles
- getto pieno
- legno
- acciaio
- misti

Il modulo governa validazione input, unità, domini ammessi, metadata normativi e readiness per i moduli X2-X8.

---

## Dipendenze reali del repo

- src/materials/
- src/codes/params/NTC2018.json
- src/codes/clauses/NTC2018.yml
- src/core/registro_log.py

---

## Fonti normative (parafrasi rigorosa)

- NTC2018 §2.5: combinazioni e definizione azioni per stati limite.
- NTC2018 §4.1.2: principi di verifica c.a. (input meccanici minimi).
- NTC2018 §7.2.6: modellazione elementi orizzontali, deformabilità e controlli globali.
- NTC2018 Cap. 8 + §C8.5.4: livelli di conoscenza e fattori FC per esistenti.
- EN 1992-1-1 §5, §6, §7: modellazione, resistenza e deformabilità per elementi in c.a.

---

## Contratto dati del modulo

### Schema input minimo

- tipologia: enum obbligatoria
- norma: enum obbligatoria (NTC2018, DM96, DM16, RD2229)
- edificio_esistente: bool
- geometria: luce, interasse, spessori, campate
- materiali: f_ck, f_yk, E, rho
- carichi: G1, G2, Q, categoria uso
- aperture: lista aperture geometriche
- cerchiature: lista interventi
- lc/fc: opzionali per esistenti

### Validazioni hard

- luce > 0
- interasse > 0
- n_campate >= 1
- f_ck, f_yk, E > 0
- Q >= 0
- coerenza luci_campate con n_campate

---

## Formula usata / fallback / motivo selezione

| Voce | Formula usata | Fallback | Motivo |
| --- | --- | --- | --- |
| Unità carichi | q_s [kgf/m2] -> q_l [kgf/cm] | input diretto q_l | preserva UX storica + calcolo coerente |
| FC esistenti | f_adj = f / FC | override manuale FC | coerenza con NTC Cap.8 |

---

## Warning code del modulo

- X1-INPUT-001: input mancante
- X1-INPUT-002: unità non coerenti
- X1-INPUT-003: tipologia fuori perimetro V1
- X1-INPUT-004: lc/fc incoerente con edificio_esistente

---

## Quick reference testabile

| Test | Input | Output atteso |
| --- | --- | --- |
| X1-T01 | tipologia valida | parsing OK |
| X1-T02 | n_campate=3, luci len=3 | validazione OK |
| X1-T03 | f_ck<=0 | warning X1-INPUT-001 |
| X1-T04 | edificio_esistente=False + LC valorizzato | warning X1-INPUT-004 |

---

## Sub-fasi implementative

## Stato avanzamento sub-fasi

- [ ] X1.1 — Enum e dataclass
- [ ] X1.2 — Validator unità e domini
- [ ] X1.3 — Mapping norme e metadata
- [ ] X1.4 — Test unitari

---

## Domande, risposte e decisioni

- Decisione: convenzione unità per V1 -> input in `cm` / `kgf` / `kgf/cm^2`; tutte le routine normative eseguono conversione in SI all'ingresso delle singole verifiche.

Regola: se esistono trascrizioni brevi verranno copiate qui, altrimenti questo spazio rimane placeholder.

---

## Teoria e fondamenti (riferimenti sintetici)

- Convenzioni unità: input in `cm`/`kgf`/`kgf/cm^2`, conversione in SI all'ingresso delle routine normative.
- Contratto dati: usare `dataclass` con validatore esplicito per unità e range.

---

## Diagramma dipendenze subfasi

```text
X1.1 → X1.2 → X1.3 → X1.4
```

---

## Rischi normativi residui

- Ambiguità tra kgf (forza) e kg (massa) se non normalizzato a livello API.
- Tipologie miste non coperte da formule unificate: richiedono estensione in X8.

---

## Cronologia e decisioni

- 2026-03-15: creato modulo X1 da split master Fase X.

---

## Esempi numerici (estratti da letteratura normativa)

1) Conversione materiale (EN 1992-1-1 / NTC2018): f_ck = 25 MPa → f_cd = f_ck/γ_c = 25/1.5 = 16.67 MPa (usare γ_c=1.5 come riferimento NTC/EN).

2) Indicazione geometrica: solaio laterocemento tipico — luce L = 4.50 m (450 cm), interasse travetti i = 50 cm, spessore h = 20 cm; validazione input: L>0, i>0, n_campate=1 → parsing OK (rif. DM96/NTC2018 per domini geometrici).

3) Conversione carico superficiale (convenzione del progetto): q_s = 300 kgf/m², interasse i = 50 cm → q_l = q_s * i / 10⁴ = 300 * 50 / 10000 = 1.50 kgf/cm (uso pratico per routine storiche).

Riferimenti: NTC2018, EN 1992-1-1, DM96 (estratti per scelta numerica e conversioni).
