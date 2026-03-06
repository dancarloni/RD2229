# PIANO DI LAVORO — RD2229 Software di Calcolo Strutturale

> **⭐ QUESTO FILE È LA FONTE DI VERITÀ DEL PROGETTO.**
>
> Funzioni di questo documento:
> 1. **Registro attività** — ogni completamento è marcato con hash commit
> 2. **Guida operativa** — ogni fase ha sub-plan dettagliati con checkbox [x]/[ ]
> 3. **Stato avanzamento** — contatori test, moduli, norme sempre aggiornati
> 4. **Continuità tra sessioni** — dopo compattazione contesto, rileggi questo file
>
> **Regola**: PRIMA di lavorare su qualsiasi fase, leggere questo file.
> **Regola**: DOPO aver completato qualsiasi sotto-punto, aggiornare questo file.
> **Riferimento**: `CLAUDE.md` alla radice del repo punta a questo file.

**Ultimo aggiornamento**: 2026-03-06
**Branch**: `claude/materials-database-structure-Fh726`

---

## Stato Generale

| Indicatore | Valore |
|---|---|
| Test totali | ~1435+ |
| Test falliti | 0 |
| Moduli implementati | 35+ |
| Norme coperte | 9 (RD2229, DM72, DM87, DM92, DM96, NTC2008, NTC2018, Circ81, OPCM3274) |

---

## FASE A — Database Materiali Multi-Normativa

### A.1 Cataloghi JSON per tutte le norme ✅
**Stato**: COMPLETATO — commit `a0f05aa`

| Catalogo | File | Materiali | Note |
|---|---|---|---|
| NTC2018 | `data/materials/catalogo_ntc2018.json` | 18 | C12/15→C50/60, B450C/A, muratura |
| RD2229 | `data/materials/catalogo_rd2229.json` | 10 | Cls storici Rck 120-300, Aq.42/50/60 |
| DM72 | `data/materials/catalogo_dm72.json` | 8 | Cls Rck 150-350, Aq.42/50/60, FeB32k |
| DM87 | `data/materials/catalogo_dm87_muratura.json` | 9 | Muratura: mattoni, blocchi, tufo, pietra |
| DM92 | `data/materials/catalogo_dm92.json` | 10 | Cls Rck 150-400, FeB22k/32k/38k/44k |
| DM96 | `data/materials/catalogo_dm96.json` | 12 | Come DM92 + classi alte (Rck 450, 500) |
| NTC2008 | `data/materials/catalogo_ntc2008.json` | 12 | C12/15→C50/60, B450C/A |
| Circ81 | `data/materials/catalogo_circ81_muratura.json` | 5 | Muratura storica, γ_M≥5.0 |
| Legno | `data/materials/catalogo_legno.json` | 6 | EN 338/14080 |
| OPCM3274 | `data/materials/catalogo_opcm3274.json` | 7 | Stessi valori DM96, γ_c=1.60, γ_s=1.15 |
| **Totale** | | **97** | |

- `material_repo.py`: metodi `list_by_norma()`, `list_norme_disponibili()`, `carica_tutti_cataloghi()`
- Test: `tests/test_cataloghi_materiali.py` (22 test)

### A.2 MaterialSource strutturata
**Stato**: TODO
- [ ] Aggiungere entità `MaterialSource` con norma, articolo, paragrafo, tabella
- [ ] Collegare a `Material` model
- [ ] Persistenza JSON

### A.3 Adapter unità (kg/cm² ↔ MPa)
**Stato**: COMPLETATO — `src/materials/adapter.py` (112 righe)

---

## FASE B — Torsione RD2229 TA

### B.1 Modulo torsione TA ✅
**Stato**: COMPLETATO — commit 394dc31

**File**: `src/methods/rd2229/torsione.py` (~310 righe)

Tradotto da VB `Sub Torsione()` (PrincipCA_TA.bas riga 3818).

#### Sub-plan B.1:
- [x] Dataclass `InputTorsione` con tutti i parametri geometrici e materiali
- [x] Enum `TipoSezione` (Rettangolare, Circolare, T, T rovescia, Doppio T, Scatolare)
- [x] Enum `EsitoTorsione` (nessuna_armatura, armatura_necessaria, sezione_insufficiente)
- [x] `calcola_tau_max_rettangolare()` — Ψ = 3 + 2.6/(0.45 + a/b)
- [x] `calcola_tau_max_circolare()` — τ = 2·|Mx|·Re / (π·(Re⁴-Ri⁴))
- [x] `calcola_tau_max_T()` — τ = 3·|Mx|·b_max / (a1·b1³ + a2·b2³)
- [x] `calcola_tau_max_doppio_T()` — denominatore con 2·a1·b1³
- [x] `calcola_tau_max_scatolare()` — τ = |Mx| / (2·Am·s_min)
- [x] Calcolo area/perimetro tubolare equivalente per tutte le sezioni
- [x] `verifica_torsione_ta()` — flusso completo verifica/progetto
- [x] Interazione T+V: τ_c1,t = τ_c1 × 1.1
- [x] Progetto armatura (Al_to, Pst_to, n_barre)
- [x] Verifica armatura esistente (σ_l, σ_st vs σ_s_adm)
- [x] `RisultatoTorsione.to_dict()` per report
- [x] Passaggi di calcolo tracciabili

**Test**: `tests/test_torsione_rd2229.py` (23 test)

---

## FASE C — Instabilità RD2229 TA

### C.1 Modulo instabilità (carico di punta) ✅
**Stato**: COMPLETATO — commit 394dc31

**File**: `src/methods/rd2229/instabilita.py` (~270 righe)

Tradotto da VB `Sub VerifStabilitàAstaCA()` (riga 4057) e `Function f_OmegaCA()` (riga 4272).

#### Sub-plan C.1:
- [x] `omega_ca(lambda)` — tabella interpolata (λ=50→140, ω=1.0→3.0)
- [x] `sigma_c_adm_ridotta()` — riduzione per sezioni snelle (a < 25 cm)
- [x] Dataclass `InputStabilita` con geometria, sollecitazioni, materiali, vincoli
- [x] Calcolo snellezza λ = L₀/r in entrambi i piani
- [x] Carico critico Euleriano Pcr = π²·(0.4·Ec)·I/L₀²
- [x] Verifica compressione semplice: σ_c = ω·|N|/A_ci
- [x] Verifica pressoflessione (3 verifiche):
  - [x] 1ª: N amplificato (ω·N)
  - [x] 2ª: N e M amplificati (ω·N, α_M·M)
  - [x] 3ª: solo M amplificato (N, α_M·M)
- [x] α_M = 1/(1 - |N|/Pcr_y)
- [x] `RisultatoStabilita.to_dict()` per report
- [x] Passaggi di calcolo tracciabili

**Test**: `tests/test_instabilita_rd2229.py` (23 test)

---

## FASE D — Cordoli Metallici

**Stato**: PARZIALMENTE COMPLETATO

### D.1 Sagomario EN 10365 ✅
**Stato**: COMPLETATO — commit corrente
- [x] Database profili IPE (18), HEA (19), HEB (19), HEM (19), UPN (12) in JSON — 87 profili totali
- [ ] Import CSV custom utente
- [x] Ricerca e filtro profili (per famiglia, Wx minimo, altezza, profilo ottimale)

**File**: `src/steel/sagomario.py` (~188 righe), `data/steel/sagomario_*.json`
**Test**: `tests/test_sagomario_acciaio.py` (32 test)

### D.2 Verifiche profilo singolo ✅
**Stato**: COMPLETATO — commit corrente
- [x] Flessione (σ = M/W ≤ σ_adm)
- [x] Taglio (τ = V/A_anima ≤ τ_adm)
- [x] Instabilità (ω·N/A, tabella CNR 10011)
- [x] Pressoflessione (N + Mx + My)
- [x] Combinata Von Mises (σ_VM = √(σ² + 3τ²))
- [x] Selezione profilo ottimale per momento

**File**: `src/steel/verifiche_ta.py` (~410 righe)
**Test**: `tests/test_verifiche_acciaio_ta.py` (33 test)

### D.3 Piatti saldati/bullonati
- [ ] Sezione composta saldata
- [ ] Sezione composta bullonata

### D.4 Solutore traliccio 2D ✅
**Stato**: COMPLETATO — commit corrente
- [x] Metodo della rigidezza diretta (Gauss con pivoting parziale)
- [x] Input nodi + aste + vincoli (cerniera, carrello_x, carrello_y) + carichi
- [x] Sforzi normali nelle aste (trazione/compressione)
- [x] Reazioni vincolari con verifica equilibrio globale
- [x] Verifiche a compressione/trazione con instabilità (ω)

**File**: `src/steel/traliccio_2d.py` (~330 righe)
**Test**: `tests/test_traliccio_2d.py` (19 test)

### D.5 Connessioni ✅
**Stato**: COMPLETATO — commit corrente
- [x] Saldature a cordone d'angolo (frontale, laterale, combinata)
- [x] Saldature testa a testa (completa penetrazione)
- [x] Bullonature: taglio (gambo/filetto)
- [x] Bullonature: trazione
- [x] Bullonature: interazione taglio+trazione (V/V_Rd)²+(N/N_Rd)²≤1
- [x] Bullonature: rifollamento lamiera
- [x] Coefficienti β_w (CNR 10011), classi 4.6÷10.9, M12÷M36

**File**: `src/steel/connessioni.py` (~380 righe)
**Test**: `tests/test_connessioni_acciaio.py` (24 test)

### D.6 GUI Qt cordoli
- [ ] Interfaccia selezione profilo
- [ ] Visualizzazione sezione
- [ ] Input sollecitazioni
- [ ] Output verifiche

---

## FASE E — Muratura Verifiche Locali

**Stato**: PARZIALMENTE COMPLETATO

### E.1 Compressione + snellezza ✅
**Stato**: COMPLETATO — commit corrente
- [x] σ ≤ f_d / γ_M con riduzione snellezza Φ
- [x] Tabella Φ da NTC2018 Tab 4.5.V (interpolazione bilineare λ×e/t)
- [x] Eccentricità e/t da momento flettente
- [x] Fattore vincolo ρ per altezza efficace

### E.2 Taglio nel piano ✅
**Stato**: COMPLETATO — commit corrente
- [x] Criterio diagonale (Turnšek-Čačovič) — NTC2018 §7.8.2.2.1
- [x] Criterio di scorrimento (Mohr-Coulomb: fvk = fvk0 + μ·σ_n)
- [x] Pressoflessione nel piano — V_pf = (L²×t×σ₀)/(2h₀)×(1-σ₀/(0.85fd))
- [x] Verifica combinata con ordinamento per V_Rd (criterio più restrittivo)

### E.3 Fuori piano + ribaltamento
- [ ] Cinematica lineare
- [ ] Cinematica non lineare
- [ ] Ribaltamento semplice e composto

### E.4 Spanciamento ✅
**Stato**: COMPLETATO — commit corrente
- [x] Verifica snellezza muro λ = h_eff/t ≤ λ_max
- [x] Limiti configurabili (20 ordinario, 15 esistente, 12 sismico)

**File**: `src/methods/muratura/verifiche.py` (~400 righe)
**Test**: `tests/test_muratura_verifiche.py` (34 test)

### E.5 Catene e paletti
- [ ] Tipi piastre (circolare, quadrata, a L)
- [ ] Verifica trazione catena
- [ ] Verifica punzonamento locale

### E.6 Apertura cantonali
- [ ] Riduzione resistenza per aperture

### E.7 Muratura multipiano
- [ ] Distribuzione carichi
- [ ] Verifica piano per piano

---

## FASE F — Metodo POR (Telaio Equivalente)

**Stato**: TODO

### F.1 Discretizzazione
- [ ] Maschi murari
- [ ] Fasce di piano

### F.2 Matrice rigidezza
- [ ] Rigidezza maschio
- [ ] Rigidezza fascia

### F.3 Assemblaggio e soluzione
- [ ] Matrice globale
- [ ] Forze orizzontali
- [ ] Spostamenti e sforzi

### F.4 Verifica maschi singoli
- [ ] Taglio, pressoflessione, scorrimento

---

## FASE G — Elementi Secondari

**Stato**: PARZIALMENTE COMPLETATO (commit 45e4648)

### G.1 SLU forza inerziale F_a ✅
**Completato** — `checks_ntc2018.py`

### G.2 SLE compatibilità spostamento ✅
**Completato** — `checks_ntc2018.py`

### G.3 Storage adapter CRUD ✅
**Completato** — commit 45e4648

### G.4 Verifiche elementi secondari per normative storiche
- [ ] Elementi secondari RD2229
- [ ] Elementi secondari DM92/DM96

---

## FASI SUCCESSIVE (PRIORITÀ DECRESCENTE)

### FASE H — Riorganizzazione methods/
- [ ] Package per norma (rd2229/, ntc2018/, dm96/, ec2/)
- [ ] Migrazione checks esistenti nei rispettivi package

### FASE I — Sezioni parametri statici completi
- [ ] Sezione omogenizzata (cls + n·A_s)
- [ ] Parametri torsionali completi
- [ ] Disegno sezione con armature

### FASE J — Pressoflessione deviata
- [ ] Dominio N-Mx-My
- [ ] Bresler per sezioni rettangolari

### FASE K — Grafici
- [ ] Sollecitazioni, inviluppi
- [ ] Diagrammi di interazione
- [ ] Spostamenti

### FASE L — Cross-Pozzati (telai piani)
- [ ] Carichi fissi
- [ ] Predisposizione carichi mobili

### FASE M — FEM beam 2D
- [ ] scipy sparse
- [ ] Assemblaggio matrice globale

### FASE N — Carote cls in sito
- [ ] 9 formulazioni note
- [ ] Export Excel

### FASE O — Griglia sismica INGV
- [ ] Import dati INGV
- [ ] Import Edilus

### FASE P — Fondazioni e geotecnica
- [ ] Portanza, cedimenti, pali, muri, liquefazione

### FASE Q — Report relazione di calcolo professionale
- [ ] Citazione automatica norma/articolo/paragrafo
- [ ] Confronto tra norme

### FASE R — Edifici esistenti
- [ ] LC/FC, vulnerabilità, miglioramento/adeguamento

### FASE S — Normative aggiuntive
- [ ] DM92 verifiche complete, NTC2008 verifiche, EC2/3/8, CNR-DT 200

### FASE T — Fuoco avanzato
- [ ] Isoterma 500°C, FEM termico

### FASE U — Sismica dettagliata
- [ ] q, duttilità, gerarchia, nodi

### FASE V — Solai, Scale
- [ ] Laterocemento, alveolari, rampe

### FASE W — OCR manuali tecnici
- [ ] Pipeline OCR per Santarella/Giangreco

---

## GIÀ COMPLETATO (da sessioni precedenti)

| Funzionalità | Commit | Modulo |
|---|---|---|
| Log centralizzato + listener GUI | edddc19 | `src/core/registro_log.py` |
| Sistema unità selezionabile | edddc19 | `src/core/unita_misura.py` |
| Debug viewer Qt | edddc19 | `src/ui/qt/debug_viewer.py` |
| Help contestuale YAML | edddc19 | `src/ui/qt/aiuto_contestuale.py` |
| Visualizzatore sezione Qt | edddc19 | `src/ui/qt/visualizzatore_sezione.py` |
| Tabulati calcolo ASCII/HTML | edddc19 | `src/report/tabulati_calcolo.py` |
| Material model (804+ righe) | a85e0e3 | `src/materials/material_model.py` |
| Material repo CRUD + JSON | a85e0e3 | `src/materials/material_repo.py` |
| Validazione materiali | a85e0e3 | `src/materials/validation.py` |
| Adapter kg/cm²↔MPa | a85e0e3 | `src/materials/adapter.py` |
| Material editor Qt | a85e0e3 | `src/ui/qt/material_editor.py` |
| 12 tipi sezione + torsionali | bdd8c6a | `src/sections/` |
| Pressoflessione SLU fiber | 2ae516d | `checks_ntc2018.py`, `section_fiber.py` |
| Flessione SLU | 2ae516d | `checks_ntc2018.py` |
| Taglio SLU (V_Rd,s) | 2ae516d | `checks_ntc2018.py` |
| Minimi armatura | 2ae516d | `checks_ntc2018.py` |
| Torsione SLU (thin-walled truss) | 6a76847 | `checks_ntc2018.py` |
| Tensioni SLE | 6a76847 | `checks_ntc2018.py` |
| Fessurazione SLE (w_k) | 6a76847 | `checks_ntc2018.py` |
| Deformazioni SLE | d625efd | `checks_ntc2018.py` |
| Verifiche DM96 complete | 45e4648 | `checks_dm96.py` |
| V_Rd,c senza armatura | 45e4648 | `checks_ntc2018.py` |
| Combinazioni NTC2018 | 45e4648 | `src/combinations/` |
| Elementi secondari SLU/SLE | 45e4648 | `checks_ntc2018.py` |
| Fuoco tabellare | b452ede | `src/fire/rc_fire_check.py` |
| Vento completo (160+ test) | 0a3d436→d8c88b5 | `src/wind/` |
| Registries e routing | c153792 | `section_registry`, `code_registry` |
| Pipeline verifiche + report | cbb07c5 | 6 verification actions, CLI |
| Cataloghi multi-norma (97 mat.) | a0f05aa + corrente | `data/materials/catalogo_*.json` |
| Torsione RD2229 TA | 394dc31 | `src/methods/rd2229/torsione.py` |
| Instabilità RD2229 TA (ω) | 394dc31 | `src/methods/rd2229/instabilita.py` |
| Sagomario acciaio EN 10365 (87 profili) | corrente | `src/steel/sagomario.py`, `data/steel/` |
| Verifiche acciaio TA (flessione, taglio, instabilità) | corrente | `src/steel/verifiche_ta.py` |
| Solutore traliccio 2D (rigidezza diretta) | corrente | `src/steel/traliccio_2d.py` |
| Connessioni acciaio (saldature + bulloni) | corrente | `src/steel/connessioni.py` |
| Verifiche muratura (compressione, taglio, spanciamento) | corrente | `src/methods/muratura/verifiche.py` |

---

## Principi Architetturali (VINCOLI DURI)

1. Modularità estrema — ogni modulo sostituibile senza refactoring globale
2. Zero duplicazione — archivi centralizzati, unica fonte per ogni parametro
3. SOLO Qt (PySide6/PyQt6) — legacy Tkinter deprecato
4. Dropdown + input manuale — sempre entrambi per campi con archivio
5. Log pervasivo — registro_log collegato a tutto
6. Help contestuale — stralci normativi, §, formule
7. Formule nei tabulati — passaggi, risultati, riferimenti normativi
8. Visualizzazione sezioni — zone tese/compresse in scala
9. NTC2018 + Circolare n.7/2019 — sempre insieme
10. No allucinazioni — formula mancante → TODO + chiedi all'utente
11. Rigore scientifico — formule da normativa/letteratura/VB
12. UI in italiano — tutto il testo visibile in italiano
