# Master Plan consolidato — Integrazione NTC2018 (PLAN‑ONLY, senza codice)

**Data:** 2026-02-14

## Executive summary

Sintesi compatta: creare un package `codes/ntc2018` + interfaccia `CodeModule` che espone controlli SLU/SLE/sismici, implementare le verifiche *calcestruzzo armato* (incluso il controllo di taglio **senza** staffe — V_Rd,c), aggiungere un modulo per **elementi secondari** (Cap. 7.2), modernizzare GUI/registry/storage e garantire test e CI. Tutto modulare, riuso massimo del codice esistente e separazione netta Core / GUI.

---

## Roadmap sintetica (fasi compatte)

1. Fase 0 — Preparazione & test baseline
2. Fase 1 — API normativa: definire `CodeModule` (contract)
3. Fase 2 — Azioni & combinazioni (generator configurabile NTC2018)
4. Fase 3 — Material registry & adapter NTC2018
5. Fase 4 — Verifiche CA (FL, TAG, N–M) **+ estensione V_Rd,c (No‑stirrups)** — PRIORITÀ ALTA
6. Fase 5 — Sismica: parametri NTC2018, spettro, statica equivalente
7. Fase 6 — Acciaio / Legno / Muratura (stubs + primi check)
8. Fase 6bis — Elementi strutturali secondari (Cap. 7.2) — MODULE DEDICATO
9. Fase 7 — Geotecnica: `GeotechAdapter` (capienza, settlement)
10. Fase 8 — Edifici esistenti (workflow valutazione domanda/capacità)
11. Fase 9 — UI Tkinter: selector norma, editor combinazioni, risultati passo‑passo
12. Fase 10 — Test, demo, documentazione normativa
13. Fase 11 — CI / release / governance
14. Fase 12 — Modernizzazione GUI + registry + storage (armonizzazione retro‑compatibile)

---

## Moduli chiave & responsabilità

- `codes/ntc2018` (CodeModule NTC2018): esposizione `available_checks()`, `run_check(id, input)`, `list_templates()`
- `core/combinations`: generatore combinazioni NTC2018 → produce `LoadCase` per `VerificationEngine`
- `core/materials` (adapter): mapping `material_code` → `MaterialProperties` (reuse `material_sources.py`)
- `codes/ntc2018/secondary_elements`: gestione `SecondaryElementSpec`, checks e templates
- GUI (Tkinter): `main_window.py` + `secondary_editor.py` + `results_panel.py` — SOLO delega al core
- Storage/config: extendere `config/*.jsoncode` e `projects` storage per templates secondary/registry

---

## Fase 4 (RC) — estensione obbligatoria: Taglio senza armatura (V_Rd,c) — dettagli essenziali 🔧

Obiettivo: implementare checks concettuali e test per elementi senza staffe.

- Output richiesto dal check (contract):
  - status ∈ {OK, NOT_OK, NOT_APPLICABLE}
  - utilisation (V_Ed / V_Rd,c), normative references, warnings/messages
- Parametri in input (minimi): `b_w`, `d`, `f_ck`, `ρ_l` (ρ long.), `σ_cp` (axial), `V_Ed`, condizioni di vincolo
- Applicabilità: regole che producono `NOT_APPLICABLE` (es. d < d_min, ρ < ρ_min, sezioni non rettangolari fuori campo)
- SLE: controllo fessurazione automatico quando non ci sono staffe; collegamento con SLU (coerenza risultati)
- Combinazioni: considerare V+M, V+T (warn/ conservative check)
- Output nel `CodeModule`: aggiungere almeno
  - `RC_SLU_VRDc_NoStirrups`
  - `RC_SLE_Cracking_NoStirrups`
  - `RC_SHEAR_Applicability_Check`

Test‑cases (golden): PASS, FAIL, NOT_APPLICABLE, effetto assiale, SLE cracking — definire valori numerici come fixtures nei test unitari.

---

## Modulo “Elementi strutturali secondari” (Fase 6bis) — overview

Posizionamento: inserire come **Fase 6bis** dopo Acciaio. Priorità media‑alta.

- Package: `codes/ntc2018/secondary_elements`
- Funzionalità principali:
  - `SecondaryElementSpec` schema + preset templates (partition, signage, cantilever, chimney, parapet, etc.)
  - Checks es.: `check_secondary_partition_sismo`, `check_secondary_signage_shear_anchor`, `check_secondary_cantilever_moment`, `check_secondary_chimney_buckling`
  - Storage: templates in `config/codes/ntc2018/secondary_elements.jsoncode`
- Normativa / fallback:
  - usare NTC2018 dove esplicita; altrimenti **fallback** documentato a EC2/EC3/EC8
- GUI: editor per tipo, geometria, attach‑point, pulsante “generate combinations + run checks”
- Limiti di responsabilità: warning `OUT_OF_SCOPE` se massa/snella/condizioni non trattate dai template

---

## CodeModule — scelte di contratto (sintesi)

- Metodi pubblici (plan-only): `available_checks()`, `run_check(check_id, CalcInput)`, `available_templates()`, `validate_input(schema)`
- Risposta standard: `{status, value, utilisation, steps[], norm_references[], messages[]}`
- `VerificationEngine` invoca checks tramite `CodeModule` (nessuna dipendenza diretta su file di implementazione)

---

## GUI / registry / storage — principi di intervento

- GUI: aggiunta selector norma, editor combinazioni e pannelli risultati; callbacks senza logica normativa.
- Storage: estendere `projects` JSON con `secondary_elements[]` e `templates/secondary_elements/*.json`
- Backward compatibility: mantenere shims per RD2229/DM92/DM96; feature‑toggle per nuove funzioni.

---

## Testing, validazione e documentazione

- Per ogni check: unit tests + integration tests + 3+ golden numeric cases con tolleranze documentate.
- Acceptance: test‑suite verde + documentazione `docs/NTC2018.md` con riferimenti e decision flowcharts.
- Coverage target: >90% per nuovi moduli normativi.

---

## Deliverables principali (per milestone)

- API `CodeModule` specificata e documentata
- `codes/ntc2018` with RC checks incl. `V_Rd,c` (specs + tests)
- `codes/ntc2018/secondary_elements` (specs + templates)
- Combination engine NTC2018 + spectrum generator (MVP)
- GUI MVP (selector norma, secondary editor, results panel)
- Full test suite + CI updates + docs

---

## Acceptance criteria (essenziali)

- Tutti i checks esposti da `CodeModule.available_checks()` e invocabili via `VerificationEngine`.
- `RC_SLU_VRDc_NoStirrups` e `RC_SLE_Cracking_NoStirrups`: OK/NOT_OK/NOT_APPLICABLE + normative refs + 3 golden tests.
- `SecondaryElementSpec` supporta min. 4 template e persistence in project storage.
- Nessuna formula normativa dentro i callback GUI; GUI solo delega.

---

## Rischi principali & mitigazioni

- Ambiguità normativa → mitigare con fallback EC e tag `norm_reference`.
- Regressioni numeriche → mitigare con golden examples e test automatici.
- UI complexity → MVP + progressive enhancement, feature‑toggles.

---

## Checklist compatta (azione immediata)

- [ ] Test baseline verde (Fase 0)
- [ ] SPEC `CodeModule` (Fase 1)
- [ ] Combinatore NTC2018 + spectrum generator (Fase 2 / 5)
- [ ] Implementazione pianificata: `RC_SLU_VRDc_NoStirrups` + tests (Fase 4, ALTA)
- [ ] Create `codes/ntc2018/secondary_elements` specs + templates (Fase 6bis)
- [ ] GUI: selector norma + SecondaryElement Editor (Fase 9 / 12)
- [ ] Update docs `docs/NTC2018.md` + CI

---

## Prossimi passi raccomandati (scegliere 1)

1. Formalizzo la SPEC dettagliata per `RC_SLU_VRDc_NoStirrups` (input/output/casi test + norm refs).
2. Redigo lo schema `SecondaryElementSpec` + 4 template prioritari (mensola, insegna, tramezzo, camino).
3. Scrivo la SPEC contrattuale del `CodeModule` (API + risposta standard + mapping dei checks esistenti).

---

*File generato automaticamente dal piano di progettazione (PLAN‑ONLY).*
