# Fase Y — Modulo aree di influenza

## Stato e metadati

| Campo | Valore |
| --- | --- |
| **Stato** | ⬜ TODO |
| **Commit** | — |
| **Data prevista** | — |
| **Test pianificati** | ~20 |
| **Norma/e di riferimento** | NTC2018 §4.1.9, §4.1.12, EC2 §5.7, DM 9/01/1996, EN 1992-1-1 |
| **Priorità** | Alta (modulo trasversale) |

---

## Descrizione

Modulo centralizzato per il calcolo delle aree di influenza, utilizzato da:
- solai (tutte le tipologie)
- scale (rampe in c.a. e metalliche)
- fondazioni e muri (fasi future)

Fornisce funzioni e classi per:
- calcolo area di influenza per travi perimetrali e interne
- gestione casi multipli (campate, aperture, geometrie irregolari)
- output per carichi distribuiti e concentrati
- interfaccia standard per moduli solai, scale, fondazioni

---

## Teoria e fondamenti strutturali

- Definizione di area di influenza secondo NTC2018, EC2, DM storici
- Metodi di calcolo: geometrico (poligoni), analitico (formule), casi particolari (aperture, travi discontinue)
- Applicazione a solai monodirezionali, bidirezionali, scale, platee
- Gestione automatica delle condizioni di bordo e dei vincoli

---

## Diagramma dipendenze subfasi

```text
Y.1 — Definizione casi e parametri area di influenza
 └── Y.2 — Algoritmi di calcolo e casi particolari
      └── Y.3 — Output, validazione e interfacce
```

---

## Dipendenze da moduli esistenti

| Modulo | File | Utilizzo pianificato |
| --- | --- | --- |
| Modulo materiali | `src/materials/` | Dati materiali per carichi |
| Modulo solai | `src/solai/` | Input geometrie e richieste |
| Modulo scale | `src/scale/` | Input geometrie e richieste |
| Modulo fondazioni | `src/fondazioni/` | (futuro) |
| Log | `src/core/registro_log.py` | Log calcolo e warning |

---

## Riferimenti normativi e bibliografici

| Riferimento | Utilizzo |
| --- | --- |
| NTC2018 §4.1.9 | Definizione area influenza solai |
| NTC2018 §4.1.12 | Carichi e deformazioni |
| EN 1992-1-1 §6.2 | Area influenza travi |
| DM 9/01/1996 | Criteri storici |
| Manuali tecnici | Casi particolari |

---

## Subfasi pianificate

### Y.1 — Definizione casi e parametri area di influenza

- [ ] Elenco casi tipici (trave perimetrale, interna, angolo, apertura)
- [ ] Definizione parametri geometrici e condizioni di bordo
- [ ] Formalizzazione input/output standard

### Y.2 — Algoritmi di calcolo e casi particolari

- [ ] Implementazione algoritmi geometrici e analitici
- [ ] Gestione automatica aperture e discontinuità
- [ ] Validazione con esempi normativi e letteratura

### Y.3 — Output, validazione e interfacce

- [ ] Output numerico e grafico (opzionale)
- [ ] Interfacce Python per moduli solai, scale, fondazioni
- [ ] Test unitari e di integrazione

---

## Guida operativa e checklist per ogni subfase

### Y.1 — Definizione casi e parametri area di influenza

- [ ] Elencare e descrivere tutti i casi (bordo, angolo, interno, apertura)
- [ ] Definire parametri geometrici minimi e opzionali
- [ ] Collegare ogni caso a riferimenti normativi
- [ ] Strutturare classi Python e schema dati

### Y.2 — Algoritmi di calcolo e casi particolari

- [ ] Implementare formule e algoritmi per ogni caso
- [ ] Annotare ogni formula con fonte e validità
- [ ] Prevedere override manuale per casi speciali

### Y.3 — Output, validazione e interfacce

- [ ] Generare output numerico e (opzionale) grafico
- [ ] Validare con esempi da letteratura
- [ ] Definire interfacce pubbliche e test

---

## Decisioni architetturali e storicizzazione

- Decisione 2026-03-10: Centralizzazione della logica delle aree di influenza in un modulo autonomo (src/aree_influenza.py), condiviso tra solai, scale e fondazioni, per evitare duplicazioni e garantire coerenza.
- Motivazione: DRY, manutenzione facilitata, tracciabilità delle modifiche, coerenza normativa.
- Tutti i moduli che necessitano il calcolo delle aree di influenza devono dipendere da questo modulo.
- Ogni modifica futura dovrà essere storicizzata qui e nei piani delle fasi che lo utilizzano.

---

## File da creare

| File | Righe stimate | Descrizione |
| --- | --- | --- |
| `src/aree_influenza.py` | 120 | Algoritmi e classi area di influenza |
| `tests/test_aree_influenza.py` | 15 test | Test casi tipici e particolari |

---

## Storicizzazione

- 2026-03-10: Decisione di centralizzazione e creazione modulo trasversale (sessione Copilot, utente DanieleCarloni).
