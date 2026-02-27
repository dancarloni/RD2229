User: Nel repo c'è il file MEGAPLAN_NTC2018_EC_con_risposte.md con tutto il piano
e gli incrementi. Analizzalo e generami UN Master Plan unico, senza duplicazioni,
compresso ma completo, secondo queste regole: [...]
(PLAN ONLY, no code)


GitHub Copilot: ## Master Plan consolidato — Integrazione NTC2018 (PLAN‑ONLY, senza codice) ✅

### Executive summary
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
- `core/materials` (adapter): mapping `material_code` → `MaterialProperties` (reuse material_sources.py)  
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

Quale preferisci che formalizzi **adesso** (plan‑only)?

User: salvalo su un nuovo file MD nella cartella MEGAPLAN

GitHub Copilot: Creo un nuovo file Markdown contenente il Master Plan consolidato nella cartella MEGAPLAN. Procedo a salvarlo ora.

Creazione di [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/MEGAPLAN_NTC2018_MasterPlan.md) completata

✅ Fatto — il Master Plan è stato salvato.

File creato: MEGAPLAN_NTC2018_MasterPlan.md

Prossimi passi consigliati:
1. Vuoi che formalizzi ora la SPEC dettagliata per `RC_SLU_VRDc_NoStirrups` (input/output/casi test)?  
2. Oppure preferisci che prepari lo schema `SecondaryElementSpec` con 4 template prioritari?

Dimmi quale preferisci e procedo con il documento di pianificazione corrispondente (PLAN‑ONLY).

Made changes.

User: crea un albero senza le cartelle che iniziano con . o quelle di cache

GitHub Copilot: Eseguo un comando PowerShell che genera l'albero del workspace filtrato (esclude cartelle che iniziano con '.' e quelle con 'cache') e salva il risultato in tree_no_dot_cache.txt. Poi ne mostro il contenuto.

Ran terminal command: $Out = 'docs/MEGAPLAN/tree_no_dot_cache.txt'
"Workspace: $PWD" | Out-File $Out -Encoding utf8
function Write-Tree {
  param($path, $prefix)
  $items = Get-ChildItem -LiteralPath $path -Force | Where-Object { ($_.PSIsContainer -and ($_.Name -notmatch '(^\.|cache)')) -or -not $_.PSIsContainer } | Sort-Object @{Expression={$_.PSIsContainer};Descending=$true}, Name
  for ($i=0; $i -lt $items.Count; $i++) {
    $item = $items[$i]
    $isLast = ($i -eq $items.Count - 1)
    $connector = if ($isLast) {'└── '} else {'├── '}
    if ($item.PSIsContainer) {
      "$prefix$connector$($item.Name)/" | Out-File $Out -Append -Encoding utf8
      $newPrefix = $prefix + (if ($isLast) {'    '} else {'│   '})
      Write-Tree $item.FullName $newPrefix
    } else {
      "$prefix$connector$($item.Name)" | Out-File $Out -Append -Encoding utf8
    }
  }
}
# write root
"$($PWD.Path.Split('\\')[-1])/" | Out-File $Out -Append -Encoding utf8
Write-Tree $PWD.Path ''
"Saved: $Out" | Out-Host

Ran terminal command: $Out='docs/MEGAPLAN/tree_no_dot_cache.txt'; "Workspace: $PWD" | Out-File $Out -Encoding utf8; Get-ChildItem -Recurse -Force | Where-Object { ($_.FullName -split '[\\/]') -notmatch '^(\.|.*cache.*)$' } | ForEach-Object { $rel = $_.FullName.Substring($PWD.Path.Length+1); $depth = ($rel -split '[\\/]').Count - 1; $indent = '    ' * $depth; "$indent$($_.Name)" } | Out-File $Out -Append -Encoding utf8; "Saved: $Out" | Out-Host

Leggere [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/tree_no_dot_cache.txt#1-1), righe da 1 a 400

Ran terminal command: $Out = 'docs/MEGAPLAN/tree_no_dot_cache.txt'
"Workspace: $PWD" | Out-File $Out -Encoding utf8
function Write-Tree {
  param($path, $prefix)
  $items = Get-ChildItem -LiteralPath $path -Force | Where-Object {
    if ($_.PSIsContainer) { ($_.Name -notmatch '(^\.|cache)') } else { $true }
  } | Sort-Object @{Expression={$_.PSIsContainer};Descending=$true}, Name
  for ($i=0; $i -lt $items.Count; $i++) {
    $item = $items[$i]
    $isLast = ($i -eq $items.Count - 1)
    $connector = if ($isLast) {'└── '} else {'├── '}
    if ($item.PSIsContainer) {
      "$prefix$connector$($item.Name)/" | Out-File $Out -Append -Encoding utf8
      $newPrefix = $prefix + (if ($isLast) {'    '} else {'│   '})
      Write-Tree $item.FullName $newPrefix
    } else {
      "$prefix$connector$($item.Name)" | Out-File $Out -Append -Encoding utf8
    }
  }
}
# write root name and tree
"$($PWD.Path.Split('\\')[-1])/" | Out-File $Out -Append -Encoding utf8
Write-Tree $PWD.Path ''
"Saved: $Out" | Out-Host

Ran terminal command: python - <<'PY'
import os
root = os.getcwd()
out = os.path.join('docs','MEGAPLAN','tree_no_dot_cache.txt')
root_name = os.path.basename(root)
with open(out, 'w', encoding='utf8') as f:
    f.write(f"{root_name}/\n")
    for dirpath, dirnames, filenames in os.walk(root):
        # skip hidden/cache dirs from being traversed
        dirnames[:] = [d for d in dirnames if not (d.startswith('.') or 'cache' in d.lower())]
        rel = os.path.relpath(dirpath, root)
        if rel == '.':
            depth = 0
        else:
            depth = rel.count(os.sep) + 1
            f.write('    ' * (depth-1) + os.path.basename(dirpath) + '/\n')
        indent = '    ' * depth
        for dn in sorted([d for d in dirnames if not (d.startswith('.') or 'cache' in d.lower())]):
            f.write(indent + dn + '/\n')
        for fn in sorted(filenames):
            f.write(indent + fn + '\n')
print('Saved:', out)
PY

Leggere [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/tree_no_dot_cache.txt#1-1), righe da 1 a 400

✅ Fatto — ho creato l'albero filtrato e l'ho salvato.

File creato: tree_no_dot_cache.txt

Cosa ho fatto:
- Generato un albero del workspace escludendo cartelle il cui nome inizia con `.` o contiene `cache`.
- Salvato il risultato in tree_no_dot_cache.txt.

Se vuoi:
- Posso aggiornare il file per escludere altre directory (es. `build`, `dist`) — dimmi quali.  
- Posso aggiungere la visualizzazione in formato `tree` con connettori ASCII invece dell'indentazione.

User: la visualizzazione deve essere comprensibile a m365 copilot

GitHub Copilot: Una domanda posta (Formato)

Creo un Markdown leggibile e un JSON strutturato (entrambi esclusi `.*/cache`) in MEGAPLAN per garantire che M365 Copilot possa interpretare facilmente l'albero del repository. Procedo a generarli.

`pylanceRunCodeSnippet` eseguito 
Completed with input: {
  "workspaceRoot": "c:\\workspaces\\RD2229\\RD2229",
  "codeSnippet": "import os, json\n\nroot = os.getcwd()\n\ndef is_excluded_dir(name):\n    return name.startswith('.') or 'cache' in name.lower()\n\ndef build_tree(path):\n    node = {'name': os.path.basename(path) or path, 'type': 'dir', 'children': []}\n    try:\n        entries = sorted(os.listdir(path))\n    except PermissionError:\n        return node\n    for e in entries:\n        full = os.path.join(path, e)\n        if os.path.isdir(full):\n            if is_excluded_dir(e):\n                continue\n            node['children'].append(build_tree(full))\n        else:\n            node['children'].append({'name': e, 'type': 'file'})\n    return node\n\nroot_tree = build_tree(root)\n\n# Markdown summary (expand to depth 3), point to full JSON for details\nMAX_MD_DEPTH = 3\n\ndef md_lines(node, depth=0):\n    lines = []\n    indent = '  ' * depth\n    if node['type'] == 'dir':\n        lines.append(f\"{indent}- **{node['name']}/**\")\n        if depth < MAX_MD_DEPTH:\n            for child in node['children']:\n                if child['type'] == 'dir':\n                    lines.extend(md_lines(child, depth + 1))\n                else:\n                    lines.append('  ' * (depth + 1) + f\"- `{child['name']}`\")\n        else:\n            dir_count = sum(1 for c in node['children'] if c['type'] == 'dir')\n            file_count = sum(1 for c in node['children'] if c['type'] == 'file')\n            lines.append('  ' * (depth + 1) + f\"- _{dir_count} dirs, {file_count} files — see JSON for full tree_\")\n    return lines\n\nmd = []\nmd.append('# Project tree (filtered) — formato compatibile M365 Copilot')\nmd.append('\\n**Filtro applicato:** esclusi i nomi di cartelle che iniziano con `.` e quelli contenenti `cache`.')\nmd.append('\\n**Nota:** la rappresentazione completa è fornita nel blocco JSON sottostante e nel file `tree_no_dot_cache.json`.')\nmd.append('\\n## Sommario (Markdown, espanso fino a profondità 3)\\n')\nmd.extend(md_lines(root_tree, 0))\nmd.append('\\n---\\n')\nmd.append('## JSON (struttura completa)')\nmd.append('```json')\nmd.append(json.dumps(root_tree, ensure_ascii=False, indent=2))\nmd.append('```\\n')\n\nmd_text = '\\n'.join(md)\n\n# write files\nmd_path = os.path.join('docs','MEGAPLAN','tree_for_m365.md')\njson_path = os.path.join('docs','MEGAPLAN','tree_no_dot_cache.json')\nwith open(md_path, 'w', encoding='utf8') as f:\n    f.write(md_text)\nwith open(json_path, 'w', encoding='utf8') as f:\n    json.dump(root_tree, f, ensure_ascii=False, indent=2)\n\nprint('WROTE:', md_path, json_path)\n",
  "workingDirectory": "c:\\workspaces\\RD2229\\RD2229",
  "timeout": 120000
}

Leggere [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/tree_for_m365.md#1-1), righe da 1 a 240

✅ Fatto — ho preparato una visualizzazione ottimizzata per Microsoft 365 Copilot.

Cosa ho creato
- tree_for_m365.md — Markdown leggibile (espanso fino a profondità 3) + blocco JSON completo (ideale per M365 Copilot).  
- tree_no_dot_cache.json — versione JSON completa e filtrata (script‑friendly).

Perché è utile ✅
- Markdown sintetico per lettura umana e rapido parsing da Copilot.  
- JSON strutturato per analisi automatica, ricerche e integrazioni (Power Automate / Copilot Scripts).

Prossimi passi (scegliere uno)
1. Espandere il Markdown fino a profondità completa (se preferisci vedere tutto).  
2. Escludere altre directory (es. dist/build).  
3. Includere conteggi/metriche (file per cartella, dimensione totale).

Dimmi quale preferisci e procedo.

User: You are GitHub Copilot Pro running STRICTLY in PLAN MODE.

This Plan session MUST remain SINGLE, CONTINUOUS and ACTIVE for the entire duration of the project.
DO NOT switch to Agent Mode.
DO NOT switch to Edit Mode.
DO NOT execute code.
DO NOT generate files automatically.

All work must stay inside PLAN for incremental integrations.

SOURCE OF TRUTH:
All Markdown files under:

docs\MEGAPLAN

are BINDING TECHNICAL SPECIFICATIONS.
They override any default Copilot behavior or assumptions.

ANTI‑HALLUCINATION RULES:
- Never invent formulas, coefficients, workflows, or structures.
- you can search in internet for formulas, coefficients, workflows or structures.
- If something is missing, ambiguous, or undefined, mark it explicitly as TODO.
- Never reuse knowledge not explicitly present in the megaplans.
- Never mix NTC2018 concepts into RD2229 (and vice‑versa).

ROLE:
You are acting as a senior structural engineer and software architect.
This is NOT a design exercise.
This is controlled construction of professional engineering software.

OUTPUT MODE:
- Only planning steps, file lists, dependencies, and exact implementation order.
- No pseudo‑code unless explicitly requested.
- No executable code unless explicitly requested.

ACKNOWLEDGEMENT REQUIRED:
Reply first with a confirmation that all rules are understood and accepted.


GitHub Copilot: Confermo di aver compreso e accettato tutte le regole; procedo in modalità Plan (senza codice, senza esecuzioni). Теперь chiedo quale documento vuoi che formalizzi adesso.

Una domanda posta (Prossimo)

User: Formalizza ora il documento: PLAN_STEP_01_SKELETON.

Rimani nella STESSA sessione di Plan.
Non resettare il contesto.
Non passare ad Agent o Edit.
Non scrivere codice.

Usa esclusivamente i file .md sotto \docs\megaplan\ come specifiche vincolanti.
Produci solo:
- struttura completa del progetto
- elenco dei file da creare
- dipendenze tra moduli
- TODO espliciti dove le specifiche non sono sufficienti.

GitHub Copilot: Confermo: tutte le regole sono rispettate. Di seguito trovi il documento PLAN_STEP_01_SKELETON (PLAN‑ONLY — nessun file creato/eseguito).  

## PLAN_STEP_01_SKELETON — sommario esecutivo
Obiettivo: fornire lo scheletro operativo (struttura progetto, file da creare, dipendenze e TODO espliciti) necessario a iniziare l’implementazione NTC2018 nel repository RD2229, seguendo esclusivamente le specifiche vincolanti presenti in MEGAPLAN. Questo è un piano operativo sequenziale e verificabile (no codice, no esecuzioni).

---

## 1) Struttura completa del progetto (scope rilevante)
- docs/MEGAPLAN (source‑of‑truth per requisiti)
  - `MEGAPLAN_NTC2018_EC_con_risposte.md` (vincolo primario)
  - `MEGAPLAN_NTC2018_MasterPlan.md` (roadmap esistente)
  - (nuovi file proposti — vedi sezione "file da creare")
- src/
  - `src/codes/ntc2018/` (nuovo package CodeModule NTC2018)
    - checks e templates per SLU/SLE/sisma + elementi secondari
  - `src/core/combinations.py` (motore combinazioni, NTC2018 rules)
  - `src/core/materials/` (adapter / registry per materiali NTC2018)
  - `src/core/verification_engine.py` (integrazione plugin `CodeModule`)
  - `src/gui/` (estensioni Tkinter: selector norma, secondary editor, results panel)
  - calculation_codes (estendere `NTC2018.jsoncode` / aggiungere `secondary_elements.jsoncode`)
- tests/
  - unit + integration per ogni check (golden cases)
- storage / project files
  - estensione schema progetto per `secondary_elements[]`

---

## 2) Elenco file da creare (proposto, con responsabilità e acceptance‑header)
Nota: i file DOCS elencati devono essere trattati come specifiche vincolanti e aggiornati prima di implementare il codice corrispondente.

A) Documentazione / SPEC (docs/MEGAPLAN) — da aggiungere/modificare
- `PLAN_STEP_01_SKELETON.md` — questo documento (formalizzazione del piano).  
- `SPEC_RC_SLU_VRDc_NoStirrups.md` — SPEC plan‑only per `RC_SLU_VRDc_NoStirrups` (input/output, casi test, applicability rules, norm_refs/TODO).  
- `SPEC_SecondaryElementSpec.md` — schema `SecondaryElementSpec` + 4 template prioritari (mensola, insegna, tramezzo, camino) + limiti d’uso.  
- `CodeModule_CONTRACT.md` — API contract dettagliato per `CodeModule` (response schema, error codes, example result skeleton).  
- `TEST_PLAN_NTC2018.md` — elenco dei golden examples con link ai test fixtures e tolleranze.

B) Codice (skeleton file list — da implementare successivamente)
- `src/codes/ntc2018/__init__.py` — package entry
- `src/codes/ntc2018/code_module.py` — adapter `CodeModule` (registrazione checks) — interface only (no logic in plan)
- `src/codes/ntc2018/checks_vrdc.py` — check concept for V_Rd,c (stub + tests planned)
- `src/codes/ntc2018/secondary_elements.py` — spec handling + checks routing
- `src/core/combinations/ntc2018_combinations.py` — combinator generator for NTC2018 rules
- `src/core/materials/ntc2018_adapter.py` — material map / registry adapter
- `src/gui/ntc2018_selector.py` — GUI widgets (selector + editor) — callbacks only call core API
- `tests/codes/test_vrdc_no_stirrups.py` — unit tests (golden cases)
- `tests/codes/test_secondary_elements.py` — unit tests for templates

C) Config / storage (schema files)
- `config/calculation_codes/NTC2018.jsoncode` — extend (parameters for sismica, combinations)
- `config/codes/ntc2018/secondary_elements.jsoncode` — templates registry
- project storage schema: add `secondary_elements` array (document change in `docs/MEGAPLAN/IMPLEMENTAZIONE_PERSISTENZA.md`)

---

## 3) Dipendenze tra moduli (diagramma testuale e regole)
- Principio: Core (calcoli) non dipende dalla GUI. GUI → VerificationEngine → CodeModule → core materials/combinations.
- Dipendenze principali (dirette):
  1. `src/codes/ntc2018/*`  depends on `src/core/*` (materials, verification types, contracts)
  2. `VerificationEngine` depends on `CodeModule` contract (`CodeModule_CONTRACT.md`)
  3. `src/core/combinations/ntc2018_combinations.py` depends on `config/calculation_codes/NTC2018.jsoncode`
  4. `src/gui/ntc2018_selector.py` depends on `VerificationEngine` API only (NO formulae)
  5. Tests depend on `tests/*` fixtures in `docs/MEGAPLAN/TEST_PLAN_NTC2018.md`
- Sequenza di dipendenze logica (per implementazione):  
  Config → CodeModule contract → core/combinations + materials adapter → checks (V_Rd,c, secondary) → GUI hooks → tests → docs aggiornate.

---

## 4) Ordine di implementazione (sequenza esatta — PRIORITÀ e gating)
1. Preparazione (gate: tests baseline verde)
   - Deliverable: `CodeModule_CONTRACT.md`, `TEST_PLAN_NTC2018.md`
   - Acceptance: `VerificationEngine` può invocare stubs attraverso il contract
2. Config & Registry
   - Deliverable: update `NTC2018.jsoncode` skeleton, `secondary_elements.jsoncode` (schema only)
   - Acceptance: loader restituisce config minimale
3. Material registry adapter
   - Deliverable: `ntc2018_adapter` (reads historical materials via existing loaders)
   - Acceptance: mapping materiale → `MaterialProperties` verificabile con 3 fixtures
4. Combinator generator (NTC2018)
   - Deliverable: `ntc2018_combinations.py` (rules skeleton + tests)
   - Acceptance: genera le combinazioni richieste per test fixtures
5. RC checks core — FIRST ITERATION (non‑GUI)
   - Deliverable: SPEC in `SPEC_RC_SLU_VRDc_NoStirrups.md` + stub in `checks_vrdc.py` + unit tests (golden A–E)
   - Acceptance: unit tests definiscono comportamento (OK/NOT_APPLICABLE/NOT_OK) — pass dei test contrattuali
   - TODO gating: definire formule normativamente corrette nelle SPEC (non inventare)
6. Secondary elements module (Fase 6bis)
   - Deliverable: `SPEC_SecondaryElementSpec.md` + stubs + tests for 4 templates
   - Acceptance: `CodeModule.available_checks()` espone `secondary_*` templates
7. GUI integration (MVP)
   - Deliverable: `ntc2018_selector.py` + results panel (delegation only)
   - Acceptance: UI chiama `VerificationEngine` and displays `VerificationResult` steps
8. Documentation & tests finali
   - Deliverable: update docs in MEGAPLAN + test coverage
   - Acceptance: test suite verde; docs aggiornate con riferimenti e TODO completati

---

## 5) TODO espliciti (aree non completamente definite nelle MEGAPLAN)
- TODO-NTC-VRDc-FORMULA — definire esatta formula e coefficienti per `V_Rd,c` (riferimento: paragrafo NTC2018 pertinente o EC2 se NTC rinvia). Documento target: `SPEC_RC_SLU_VRDc_NoStirrups.md`.  
- TODO-SLE-WMAX — specificare criteri e valori limite per controllo fessurazione (SLE) quando non ci sono staffe; definire w_max o criterio qualitativo. Documento target: `SPEC_RC_SLU_VRDc_NoStirrups.md`.  
- TODO-SECONDARY-MODELS — per ciascun template (mensola, insegna, tramezzo, camino) indicare modello semplificato, limiti di applicabilità e fonte normativa (NTC2018 §7.2 o EC fallback). Documento target: `SPEC_SecondaryElementSpec.md`.  
- TODO-CONTRACT-EXAMPLES — aggiungere esempi concreti di `VerificationResult` JSON in `CodeModule_CONTRACT.md`.  
- TODO-COVERAGE-THRESHOLD — concordare target di coverage per i nuovi moduli (proposta: 90% per logica normativa). Documentare in `TEST_PLAN_NTC2018.md`.  
- TODO-VALIDATION-BENCHMARKS — raccogliere valori di riferimento numerici (golden cases) e fonti (libri, esempi normativi) — inserire in `TEST_PLAN_NTC2018.md`.

> Nota vincolante: non inserire formule o coefficienti nelle SPEC finché non sono citati espressamente in MEGAPLAN o in riferimenti normativi ufficiali. Se mancano, marcare come TODO.

---

## 6) Output atteso / Acceptance gating per questa fase iniziale
- `CodeModule_CONTRACT.md`, `SPEC_RC_SLU_VRDc_NoStirrups.md`, `SPEC_SecondaryElementSpec.md`, `TEST_PLAN_NTC2018.md` devono esistere e essere approvati prima di aprire PR di implementazione.  
- Ogni SPEC deve contenere: input schema, output schema, applicability rules, list of golden tests, normative references (o TODO se mancante).

---

## 7) Rischi operativi immediati
- Mancanza di riferimenti normativi espliciti nelle MEGAPLAN → blocco per calcoli concreti (mitigazione: marcare TODO e usare EC come fallback documentato).  
- Ambiguità su limiti d’applicabilità (es. sezioni non rettangolari) → inserire regole `NOT_APPLICABLE` e test.

---

## 8) Prossimi passi immediati (scegliere 1)
- A: Formalizzo `SPEC_RC_SLU_VRDc_NoStirrups.md` (input/output + test fixtures + TODO normativi) — raccomandato (ALTA).  
- B: Formalizzo `SPEC_SecondaryElementSpec.md` con 4 template prioritari (mensola, insegna, tramezzo, camino).  
- C: Formalizzo `CodeModule_CONTRACT.md` (API + response schema + example stubs).

Seleziona quale SPEC vuoi che formalizzi **ora** (PLAN‑ONLY).

User: B

GitHub Copilot: Confermo: resto in modalità Plan (nessun codice, nessuna modifica). Di seguito trovi la SPEC formale per `SecondaryElementSpec` — struttura operativa, file da creare, dipendenze e TODO espliciti (PLAN‑ONLY).

## SPEC_SecondaryElementSpec.md — sommario
Scopo: definire schema, template e contratti di verifica per gli **elementi strutturali secondari** (NTC2018 §7.2 + fallback EC). Copre 4 template prioritari: **mensola (cantilever)**, **insegna/pannello sospeso**, **tramezzo/partizione non portante**, **camino/comignolo**.

---

## 1) Dove inserire (file e posizione)
- SPEC doc (da creare): `docs/MEGAPLAN/SPEC_SecondaryElementSpec.md`
- Config/template registry: `config/codes/ntc2018/secondary_elements.jsoncode`
- Core API exposure: `codes/ntc2018/secondary_elements` (package)
- Storage schema (project): add `secondary_elements` array to project model (document change)
- GUI (editor/results): `src/gui/secondary_element_editor.py` (MVP)

---

## 2) Struttura logica del `SecondaryElementSpec` (schema essenziale)
- id: string (unique)
- type: enum {CANTILEVER, SIGNAGE, PARTITION, CHIMNEY, OTHER}
- geometry: object {width, height, thickness, length, diameter, span, ...}
- material: `{material_code}` (mapped via materials registry)
- attachments: list [{position, anchor_type, embedment_depth, stiffness}]
- loads: {Gk:[], Qk:[], wind: {pressure, direction}, seismic: {a_g, importance}, accidental:[]}
- boundary_conditions: {top_support, bottom_support, rotational_stiffness}
- dynamic: optional {modal_mass, damping} (TODO if needed)
- notes / user_flags: free text
- created_from_template: string

---

## 3) Per‑template: modello statico, input minimi, checks richiesti, limiti di applicabilità

A) Mensola (CANTILEVER)
- Modello statico: travetto a mensola (incastro alla base) carichi puntuali/distribuiti; supporto modellabile come incastro o cerniera con molaggio rotazionale.
- Input minimi: length, section (b×h), material, anchor (embedment_depth), Gk/Qk positions.
- Checks da effettuare:
  - bending capacity (moment at support) — `secondary_cantilever_moment`
  - shear capacity near support — `secondary_cantilever_shear`
  - anchorage capacity / pullout — `secondary_cantilever_anchor`
  - serviceability (deflection) — `secondary_cantilever_deflection` (SLE)
- Applicabilità / NOT_APPLICABLE:
  - valid for small/medium spans typical di elementi non‑primari; if support involves complex substructure, return `NOT_APPLICABLE` (TODO: fissare limiti numerici).
- Test fixtures: PASS (small load), FAIL (overload moment), NOT_APPLICABLE (unsupported embedment).

B) Insegna / pannello sospeso (SIGNAGE)
- Modello statico: cantilever or hung panel; dominant action = wind pressure; discrete anchors.
- Input minimi: panel area, mass, number_of_anchors, anchor_positions, wind_exposure
- Checks:
  - anchor tensile/shear capacity per anchor — `secondary_signage_anchor`
  - overturning / eccentricity check — `secondary_signage_overturning`
  - serviceability (vibration / fatigue) — `secondary_signage_fatigue` (TODO)
- Applicabilità:
  - if aerodynamic/dynamic response relevant → `TODO: dynamic model required` → return `NOT_APPLICABLE` or `WARNING`
- Test fixtures: PASS (small sign, multiple anchors), FAIL (wind > anchor capacity), DYNAMIC_TODO.

C) Tramezzo / partizione non portante (PARTITION)
- Modello statico: pannello soggetto a fuori‑piano (wind/seismic) e collegamenti puntuali; modellazione come trave/pannello.
- Input minimi: height, length, thickness, attachment conditions (top/bottom), material, mass
- Checks:
  - out‑of‑plane bending/anchorage — `secondary_partition_out_of_plane`
  - in‑plane seismic anchorage / load path (where applicable) — `secondary_partition_seismic_in_plane`
  - SLE: damage / crack risk / limits on deformation — `secondary_partition_serviceability`
- Applicabilità:
  - partitions > X span or special cladding → `NOT_APPLICABLE` (TODO: define numeric limits)
- Test fixtures: PASS (anchored partition), FAIL (inadequate anchors), NOT_APPLICABLE (large span).

D) Camino / comignolo (CHIMNEY)
- Modello statico: colonna snella verticale (cantilever) soggetta a vento, sisma, auto‑peso; possibile instabilità globale.
- Input minimi: total_height, diameter/width, thickness, material, base_fixity, axial_load, wind_profile
- Checks:
  - global buckling / stability — `secondary_chimney_buckling`
  - overturning / base shear (wind+seismic) — `secondary_chimney_overturning`
  - combined axial+moment (N–M interaction) — `secondary_chimney_interaction`
  - foundation capacity (geotech adapter) — `secondary_chimney_foundation` (calls GeotechAdapter)
- Applicabilità:
  - for tall/slender chimneys coupling with geotechnical response may be required → return `NOT_APPLICABLE` or `REQUIRES_GEOTECH` if beyond local scope
- Test fixtures: PASS (short chimney, sufficient base), FAIL (tall, high wind), GEOTECH_TODO.

---

## 4) Output / risultato delle verifiche (response schema)
- `check_id` (string)
- `status` ∈ {OK, NOT_OK, NOT_APPLICABLE, WARNING}
- `utilisation` (0..1) where applicable
- `value` numeric (e.g., design ratio) — optional
- `steps[]` (array) — short human‑readable calculation steps (no formulas — reference only)
- `norm_references[]` (list of strings — e.g., `NTC2018 §7.2`, `EC8 Table X`) or `TODO` if missing
- `messages[]` (warnings / applicability notes)
- `required_followup[]` (e.g., `geotech`, `dynamic_analysis`) — optional

---

## 5) File da creare (documenti + artefatti tecnici — PLAN‑ONLY)
- `docs/MEGAPLAN/SPEC_SecondaryElementSpec.md` (this SPEC — authoritative)
- `docs/MEGAPLAN/TEST_PLAN_SECONDARY_ELEMENTS.md` (golden cases per template)
- `config/codes/ntc2018/secondary_elements.jsoncode` (template registry skeleton)
- `src/codes/ntc2018/secondary_elements` (package outline; list of check identifiers)
- `src/gui/secondary_element_editor.py` (GUI mapping document — MVP)
- `tests/codes/test_secondary_elements_*.py` (unit tests for each template)

---

## 6) Dipendenze tra moduli (testuale, ordine di integrazione)
- `VerificationEngine` ← invokes → `CodeModule(ntc2018)` ← uses → `secondary_elements` checks  
- `secondary_elements` checks → require → `core/combinations` (for seismic/wind load generation)  
- `secondary_elements` checks → use → `core/materials` (material properties loader)  
- Chimney foundation checks → depend on → `GeotechAdapter` (Fase 7)  
- GUI `secondary_element_editor` → depends on → `VerificationEngine` API only (no computation in GUI)

Sequenza implementativa raccomandata:
1. SPEC doc + TEST_PLAN (acceptance gate)
2. config/template skeleton (jsoncode)
3. Data model & persistence (project schema)
4. Core check stubs + unit tests (per template)
5. Combinations / loads integration (wind/seismic hooks)
6. GUI editor + results panel
7. Integration tests + docs update

---

## 7) Acceptance criteria (per modulo secondary_elements)
- SPEC document approvato in MEGAPLAN.
- Per ogni template: almeno 3 golden tests (PASS/FAIL/NOT_APPLICABLE) documentati.
- `CodeModule.available_checks()` espone template ids for secondary elements.
- GUI editor exists as MVP and delegates to core API.
- Any `NOT_APPLICABLE` / `REQUIRES_GEOTECH` outcomes include clear remediation messages.

---

## 8) TODO espliciti (aree non definite / vietate dall’anti‑hallucination)
- TODO‑SE1: definire limiti numerici di applicabilità (slenderness ratios, span limits, minimum embedment depths) — fonte: NTC2018 §7.2 or EC fallback. (SPEC must mark these as TODO)
- TODO‑SE2: specificare valori e formule per anchor capacity checks (pull‑out/steel embedment partial factors) — normative source required.
- TODO‑SE3: SLE criteria (deflection limits, crack widths) for partitions and cantilevers — define w_max or serviceability criteria.
- TODO‑SE4: wind coefficients for large panels / signage (dynamic amplification rules) — reference EC1/NTC if available.
- TODO‑SE5: define interaction models (V–M, N–M) numeric formulation or referenced standard (EC2/EC3/EC8).
- TODO‑SE6: collect benchmark numerical examples and normative references for each golden test (attach sources).

---

## 9) Test plan (high‑level)
- Per template: implement unit tests for
  - nominal PASS case,
  - overload FAIL case,
  - applicability boundary (NOT_APPLICABLE),
  - at least one combination including seismic or wind where relevant.
- All tests must reference a normative source (or mark TODO if source missing).

---

## 10) Implementazione: passi immediati (prossimi step di Plan)
1. Redigere e approvare `docs/MEGAPLAN/SPEC_SecondaryElementSpec.md` (includere TODO‑SE*).  
2. Preparare `TEST_PLAN_SECONDARY_ELEMENTS.md` con golden fixtures (numeric values marked TBD if normative source missing).  
3. Creare `secondary_elements.jsoncode` (skeleton templates only).  
4. Implementare data model & persistence schema (project storage change documented).  
5. Implementare stubs e test‑cases (contract only) — ensure tests cover OK/FAIL/NOT_APPLICABLE.

---

Se approvi il contenuto, formalizzo il documento `SPEC_SecondaryElementSpec.md` come testo pronto da incollare in MEGAPLAN (PLAN‑ONLY). Vuoi che proceda con la versione completa del file SPEC (testo dettagliato + template JSON schema + checklist dei golden tests)?

User: risolviamo tutti i todo espliciti

GitHub Copilot: Confermo: resto in modalità Plan. Di seguito trovi un piano operativo completo e verificabile per risolvere TUTTI i TODO espliciti identificati nelle SPEC (PLAN‑ONLY — nessuna esecuzione o modifica di file).

## Panoramica rapida
Obiettivo: chiudere tutti i TODO nelle SPEC NTC2018 / SecondaryElements / RC_VRd,c senza inventare formule — ogni TODO sarà risolto attingendo a fonti normative dichiarate (NTC2018, Eurocodici) o marcato come *decisione documentata/TODO* quando la norma non fornisce indicazioni numeriche. Output: SPEC aggiornate, test golden, file di configurazione e checklist di PR.

---

## Principi di soluzione (vincoli)
- Non inventare formule: ogni formula/coefficiente deve essere tratto da NTC2018 o da una norma/standard citata (EC2/EC1/EC8 ecc.).  
- Se la norma non definisce un valore, la SPEC deve marcare il comportamento come TODO/DECISION_REQUIRED e proporre fallback documentato.  
- Ogni TODO risolto genera: SPEC aggiornate, almeno 3 test fixtures (golden), implementazione test‑first (stub → tests), e PR con reviewer tecnico (ing. strutturista).

---

## Elenco TODO e piano di risoluzione (per ogni TODO: task, file da aggiornare, test, acceptance)

1) TODO-NTC-VRDc-FORMULA — V_Rd,c (taglio senza staffe)
- Tasks:
  1. Recuperare testo normativo (NTC2018 § pertinente; se NTC rimanda → usare EC2 §6.x o paragrafo equivalente).  
  2. Estrarre formula e coefficienti (documentare esattamente la fonte e la versione).  
  3. Aggiornare `docs/MEGAPLAN/SPEC_RC_SLU_VRDc_NoStirrups.md` con formula, condizioni di validità e esempi numerici estratti da norma o letteratura.  
  4. Definire 5 golden examples (3 unit tests + 2 boundary cases) con riferimenti.  
  5. Aggiungere unit tests in `tests/codes/test_vrdc_no_stirrups.py`.
- Files da aggiornare:
  - `docs/MEGAPLAN/SPEC_RC_SLU_VRDc_NoStirrups.md` (SPEC + normative refs)
  - `docs/MEGAPLAN/TEST_PLAN_NTC2018.md` (aggiungere golden cases)
  - test file (per implementazione successiva)
- Acceptance:
  - SPEC contiene formula letterale e riferimento normativo; i test usano numeri tratti dalla norma o da esempio riconosciuto.
- Owner: Structural engineer (extract source) + Dev (tests)
- Priorità: Alta
- Stima: 1–2 working days (research + SPEC + test fixtures)

2) TODO-SLE-WMAX — criteri SLE (fessurazione / w_max)
- Tasks:
  1. Identificare in NTC2018 o Circolare valori limiti per larghezza fessura o criteri di servizio (se NTC non li definisce, usare EC2 guidance or Italian Circolare).  
  2. Definire procedure di valutazione SLE per elementi senza staffe (output qualitativo + valore w_max o indicatore di exceed).  
  3. Aggiornare `SPEC_RC_SLU_VRDc_NoStirrups.md` (sezione SLE) e `TEST_PLAN_NTC2018.md`.
- Files:
  - `docs/MEGAPLAN/SPEC_RC_SLU_VRDc_NoStirrups.md`
  - `docs/MEGAPLAN/TEST_PLAN_NTC2018.md`
- Acceptance:
  - SPEC cita la sorgente normativa per w_max; tests includono confronto pass/fail per SLE.
- Owner: Structural engineer
- Priorità: Alta
- Stima: 1 working day

3) TODO-SECONDARY-MODELS / TODO-SE1..SE6 — elementi secondari (mensola, insegna, tramezzo, camino)
- Tasks (per ciascun template):
  1. Individuare paragrafi NTC2018 §7.2 e riferimenti EC utili (EC1 wind, EC8 seismic, EC2 for concrete elements) per ogni comportamento richiesto.  
  2. Definire limiti di applicabilità numerici (slenderness, span limits, embedment_min). Se NTC non dà numeri, definire fallback EC o marcare come DECISION_REQUIRED.  
  3. Documentare modelli di calcolo (schema statico, input richiesti) e i controlli da eseguire (lista di check ids).  
  4. Produrre golden tests per ciascun template (PASS/FAIL/NOT_APPLICABLE).  
  5. Aggiornare `docs/MEGAPLAN/SPEC_SecondaryElementSpec.md` e `docs/MEGAPLAN/TEST_PLAN_SECONDARY_ELEMENTS.md`.
- Files:
  - `docs/MEGAPLAN/SPEC_SecondaryElementSpec.md` (aggiornare con riferimenti e limiti numerici)
  - `docs/MEGAPLAN/TEST_PLAN_SECONDARY_ELEMENTS.md`
  - `config/codes/ntc2018/secondary_elements.jsoncode` (template entries + applicability fields)
- Acceptance:
  - Ogni template ha: modello descritto, limiti applicativi (o TODO fallback), 3 golden tests con fonte di riferimento.
- Owner: Structural engineer + Standards researcher
- Priorità: Alta (mensola, insegna, tramezzo, camino prima; altri template secondari dopo)
- Stima: 3–5 working days (ricerca normativa + SPEC + test plan)

4) TODO-CONTRACT-EXAMPLES — esempi `VerificationResult`
- Tasks:
  1. Definire 3 esempi di `VerificationResult` JSON (SLU OK, SLU FAIL, NOT_APPLICABLE) per `RC_SLU_VRDc_NoStirrups` e per almeno 2 secondary templates.  
  2. Inserire esempi in `docs/MEGAPLAN/CodeModule_CONTRACT.md`.
- Files:
  - `docs/MEGAPLAN/CodeModule_CONTRACT.md`
- Acceptance:
  - Esempi completi (input → output) con commento normativo; PR checklist richiede che ogni nuovo check abbia almeno un example.
- Owner: Dev + Structural engineer
- Priorità: Medium
- Stima: 0.5–1 day

5) TODO-COVERAGE-THRESHOLD
- Tasks:
  1. Stabilire soglia coverage per nuovi moduli (proposta già presente: **>= 90%** per nuovi moduli normativi).  
  2. Documentare soglia in `docs/MEGAPLAN/TEST_PLAN_NTC2018.md` e aggiornare CI (test job) per enforcement.
- Files:
  - `docs/MEGAPLAN/TEST_PLAN_NTC2018.md`
  - CI config (PR after SPEC acceptance)
- Acceptance:
  - CI check per coverage threshold verde su branch PR.
- Owner: Team lead / DevOps
- Priorità: Medium
- Stima: 0.5 day

6) TODO-VALIDATION-BENCHMARKS — raccolta golden cases
- Tasks:
  1. Compilare una tabella di benchmark: sorgente (norma/libro), input, expected output, tolerance.  
  2. Popolare `docs/MEGAPLAN/TEST_PLAN_NTC2018.md` e collegare ai test fixtures.
- Files:
  - `docs/MEGAPLAN/TEST_PLAN_NTC2018.md`
- Acceptance:
  - Ogni golden test ha fonte esplicita; i test automatizzati usano gli stessi valori.
- Owner: Structural engineer + QA
- Priorità: High
- Stima: 2–3 days (ricerca e validazione)

7) TODO-SE2 / TODO‑SE4 / TODO‑SE5 (anchor capacity, wind coeffs, interaction models)
- Tasks:
  1. Per anchor capacities: estrarre norme di riferimento (EN anchors, CEN reports, national annex); definire check e parametri.  
  2. Per wind coefficients: usare EC1 o NTC2018 indicazioni; definire quando serve analisi dinamica e quando modello statico è accettabile.  
  3. Per interaction models (V–M, N–M): indicare riferimento EC2/NTC e marcare formule da importare nella SPEC.  
- Files:
  - `docs/MEGAPLAN/SPEC_SecondaryElementSpec.md` (sezioni tecniche)
  - `docs/MEGAPLAN/SPEC_RC_SLU_VRDc_NoStirrups.md` (interazione V–M)
- Acceptance:
  - Ogni check ha riferimento normativo preciso; se manca un riferimento, SPEC mostra TODO + proposta fallback.
- Owner: Structural engineer + Standards researcher
- Priority: High for anchors & V–M; Medium for dynamic wind amplification
- Stima: 2–4 days (ricerca normativa + SPEC)

8) QA/CI TODO: detect remaining TODO tokens automatically
- Tasks:
  1. Add a CI job that scans `docs/MEGAPLAN/*.md` for `TODO|TBD` tokens and fails the merge if present (optionally allow approved exceptions).  
  2. Document exception process in MEGAPLAN.
- Files:
  - CI config (after SPEC acceptance)
  - `docs/MEGAPLAN/CONTRIBUTING.md` or similar
- Acceptance:
  - No `TODO` tokens in docs on merge (or explicit approved exceptions).
- Owner: DevOps
- Priority: High
- Stima: 0.5–1 day

---

## Sequenza operativa consigliata (ordine esatto di esecuzione)
1. Kickoff research: assign structural engineer(s) and standards researcher (collect NTC2018/EC references).  
2. Produce/approve updated SPEC documents:
   - `SPEC_RC_SLU_VRDc_NoStirrups.md` (include TODOs resolved where possible)  
   - `SPEC_SecondaryElementSpec.md` (complete with SE1–SE6 resolved or explicitly TODO‑flagged)  
   - `TEST_PLAN_NTC2018.md` (golden cases table)  
   Acceptance gate: structural engineer signs-off.
3. Implement tests (test‑first):
   - Add golden test fixtures to tests (stubs referencing SPEC values).  
   - Run and mark failing tests as expected (until code implemented).
4. Implement core formulas and logic (code PRs) — after SPEC + tests approved.
5. Update GUI stubs and examples.
6. Final integration tests + CI enforcement (TODO token scan + coverage threshold).
7. Close remaining TODO tokens; update CHANGELOG and docs.

---

## Checklist finale (per chiudere tutti i TODO)
- [ ] Assegnare responsabili per ogni TODO (ing./dev/QA).  
- [ ] Raccogliere e citare fonti normative per V_Rd,c, w_max, anchors, wind coeffs, interaction models.  
- [ ] Aggiornare SPEC (`SPEC_RC_SLU_VRDc_NoStirrups.md`, `SPEC_SecondaryElementSpec.md`) con riferimenti e formule (quando disponibili).  
- [ ] Popolare `TEST_PLAN_NTC2018.md` con golden cases e fonti.  
- [ ] Implementare unit tests che riflettano i golden cases.  
- [ ] Configurare CI per coverage & TODO detection.  
- [ ] Revisione tecnica e merge PRs con tests verdi.

---

## Decision points / Items requiring tua approvazione
- Confermi che usiamo **EC2/EC1/EC8** come fallback quando NTC2018 è incompleto? (raccomandato e già previsto nei megaplans)  
- Vuoi che io formalizzi subito i documenti SPEC aggiornati (PLAN‑ONLY) seguendo le risposte normative raccolte?  

---

Se approvi, procedo a formalizzare (PLAN‑ONLY) i documenti SPEC aggiornati in questo ordine:  
1) `SPEC_RC_SLU_VRDc_NoStirrups.md` (alta priorità)  
2) `TEST_PLAN_NTC2018.md` (benchmark/golden cases)  
3) `SPEC_SecondaryElementSpec.md` (integro i TODO risolti)

Quale documento vuoi che formalizzi per primo (PLAN‑ONLY)?

User: aggiungi agli elementi secondari la gui relativa, e per quanto riguarda docs\MEGAPLAN tutta la gui , il supporto alle verifiche ntc2018 DM96 RD2229

GitHub Copilot: Status: ricevuto — preparo il piano operativo (PLAN‑ONLY) per aggiungere la GUI degli elementi secondari e per documentare in MEGAPLAN la GUI completa con il supporto alle verifiche `NTC2018`, `DM96`, `RD2229`.

## 1) Obiettivo sintetico
- Aggiungere l’interfaccia utente per la gestione/verifica degli **elementi secondari** (editor, template, esecuzione check, risultati).  
- Documentare e specificare **tutta la GUI** nel MEGAPLAN includendo il mapping e il supporto alle verifiche `NTC2018`, `DM96`, `RD2229`.  
- Garantire separazione netta: GUI = delega; tutta la logica normativa rimane nel core/CodeModule.

---

## 2) Deliverable (cosa produrre — PLAN‑ONLY)
- GUI artefatti da progettare (file da creare/modificare — elenco esatto)
- Documentazione MEGAPLAN da aggiornare/creare
- Dipendenze funzionali e sequenza di implementazione
- Acceptance criteria, test plan per GUI e integrazione norme
- TODO espliciti per gap normativi o API mancanti

---

## 3) File da creare / modificare (preciso, percorso relativo)
A — GUI (codebase — MVVM/view widgets / app-level)
- Create: `app/ui/secondary_element_window.py` — finestra principale editor/runner (MVP)
- Create: `app/ui/secondary_element_editor.py` — form di input (geometry, attachments, loads, template picker)
- Create: `app/ui/secondary_element_results.py` — pannello risultati step‑by‑step + normative
- Modify: `app/ui/module_selector.py` — aggiungere voce “Secondary elements” e dropdown `Norma` (NTC2018/DM96/RD2229)
- Modify: `app/ui/frc_verification_window.py` — aggiungere hook per `secondary_element` workflow (link “Apri editor”)
- Modify: `app/ui/frc_manager.py` — integrare persistenza template `secondary_elements`

B — GUI (reusable widgets in core GUI package)
- Create: `src/gui/widgets/secondary_element_widgets.py` — preview geometry, anchor diagram, load editor
- Create: `src/gui/widgets/norm_selector.py` — dropdown norma che legge `config/calculation_codes/*`
- Modify: `src/gui/section_gui.py` / `src/gui/materials_gui.py` — expose compact APIs per selezione se già presenti

C — Tests (GUI + integration stubs)
- Create: `tests/gui/test_secondary_editor.py` — unit tests logica widget (no formulas)
- Create: `tests/integration/test_gui_verification_flow.py` — E2E scenario: select norm → create secondary element → run check → expect result status
- Create: `tests/gui/test_norm_selector.py` — ensure UI shows available norms from config

D — Config / Storage / Persistence
- Modify/Create: `config/codes/ntc2018/secondary_elements.jsoncode` — registry templates (skeleton)
- Modify: project storage schema doc (`docs/MEGAPLAN/IMPLEMENTAZIONE_PERSISTENZA.md`) — add `secondary_elements[]`
- Modify: sec_repository/project model (document plan only) — add fields for saved secondary elements

E — Docs MEGAPLAN
- Update: `PLAN_GUI.md` — aggiungere workflow completo GUI + wireframes
- Create: `GUI_VERIFICATION_SUPPORT.md` — mapping GUI ↔ `NTC2018|DM96|RD2229` checks (checkbox matrix)
- Update/Create: `SPEC_SecondaryElementSpec.md` — includere wireframes e mapping GUI controls → spec fields
- Create: `TEST_PLAN_SECONDARY_ELEMENTS.md` — golden cases for GUI + checks
- Update: `MEGAPLAN_NTC2018_MasterPlan.md` — reference new GUI capabilities & milestones

---

## 4) Mapping GUI → Core (contratti & chiamate)
- `Norma selector` (GUI) → reads `config/calculation_codes/*` and sets `calculation_code` in session.
- `Editor (Secondary)` → builds `SecondaryElementSpec` (schema documented in `SPEC_SecondaryElementSpec.md`) and calls `VerificationEngine` via `create_verification_engine(calculation_code)` + `engine.perform_verification(SecondaryElementSpec, check_id)`.
- `Run verification` (GUI) → asynchronous call to `VerificationEngine` (show spinner); on completion show `VerificationResult.steps[]`, `norm_references[]`, `messages[]`.
- `Save template` (GUI) → writes to `config/codes/ntc2018/secondary_elements.jsoncode` (template registry) and project storage.
- IMPORTANT: GUI must not implement normative formulas — callbacks only pass data and request results.

---

## 5) Wireframes / UX (MVP — descrizione)
- Main flow (screens):
  1. `Main Window` — norma dropdown + “New secondary element” button + “Open saved” list.
  2. `Secondary Element Editor` — tabs: General, Geometry, Attachments, Loads, Templates. Live preview (simple schematic), validation badges.
  3. `Generate combinations` (optional) — button that calls `core/combinations` for wind/sisma.
  4. `Run checks` — list of available checks (populated from `CodeModule.available_checks()` for selected `calculation_code`).
  5. `Results panel` — status, utilisation bars, normative references, step‑by‑step text, export/save result.
- Accessibility: keyboard navigation, labels, copyable normative references.
- Visual hints: warnings for `NOT_APPLICABLE` with remediation suggestions.

---

## 6) Dipendenze e ordine di implementazione (step‑by‑step)
1. Docs gating: update PLAN_GUI.md and `SPEC_SecondaryElementSpec.md` (wireframes + schema) — Acceptance: doc review completed.
2. Add `secondary_elements.jsoncode` skeleton + project storage schema doc — Acceptance: loader returns skeleton.
3. Implement UI widgets skeleton (`secondary_element_editor.py`, `secondary_element_results.py`, `secondary_element_window.py`) — Acceptance: screens present and validate input only (no calc).
4. Expose `Norm selector` widget and ensure it reads `calculation_codes` (NTC2018/DM96/RD2229) — Acceptance: dropdown shows available norms.
5. Implement GUI → Engine stub integration (call engine with `calculation_code` and `SecondaryElementSpec`) — Acceptance: engine is invoked and returns stubbed `VerificationResult`.
6. Hook `Run checks` list to `CodeModule.available_checks()` for selected norm — Acceptance: checks list updates per norm.
7. Persist templates and secondary elements in project storage — Acceptance: save/load roundtrip.
8. Add GUI tests + integration tests — Acceptance: tests for UI logic and mock integration pass.
9. Finalize docs in MEGAPLAN including `GUI_VERIFICATION_SUPPORT.md` mapping norm ↔ checks and user manual pages — Acceptance: docs reviewed.
10. End‑to‑end verification: run full flow (create element, run check NTC2018/DM96/RD2229) — Acceptance: output normative steps displayed and saved.

---

## 7) Test plan — scenari obbligatori (nominativi test)
- `GUI-SEC-001_CreateAndSaveTemplate` — create secondary element, save template, reload → validate fields match.
- `GUI-SEC-002_Run_VRdC_NTC2018` — Norma=NTC2018, run `RC_SLU_VRDc_NoStirrups` → expect `VerificationResult` with `norm_references` containing `NTC2018`.
- `GUI-SEC-003_Run_Sample_DM96` — Norma=DM96, run a DM96 check (e.g., pre‑existing `checks_dm96.py`) → expect result from DM96 pipeline.
- `GUI-SEC-004_Run_Rd2229_Backwards` — Norma=RD2229, run check → ensure legacy behavior preserved.
- `GUI-SEC-005_UI_A11Y_Compliance` — keyboard navigation, labels present.
- `INTEGRATION-SEC-001_E2E_Secondary_NormMatrix` — run same secondary element on all three norms and compare result meta (status + references).

Each test must reference SPEC and `TEST_PLAN_SECONDARY_ELEMENTS.md`.

---

## 8) Acceptance criteria (GUI + docs + verification support)
- GUI: user can create, edit, save, load secondary elements and templates; run checks for `NTC2018`, `DM96`, `RD2229`; results show `steps[]` and `norm_references[]`.
- Docs: PLAN_GUI.md, `GUI_VERIFICATION_SUPPORT.md`, `SPEC_SecondaryElementSpec.md`, `TEST_PLAN_SECONDARY_ELEMENTS.md` updated and approved.
- Core contract: `VerificationEngine` + `CodeModule` must expose `available_checks()` and accept `SecondaryElementSpec` payloads — if missing, add TODO (see next).
- Tests: GUI unit and integration tests implemented and passing; CI updated to run GUI integration tests in headless mode (or UI test harness).

---

## 9) TODO espliciti / decision points (documentare e risolvere prima dell’implementazione)
- TODO-GUI-API: verificare/esporre l’API del `VerificationEngine` per accettare `SecondaryElementSpec` — se non esiste, SPEC andare a `CodeModule_CONTRACT.md` (implementerà `run_secondary_check`).
- TODO-GUI-WIRE: decidere se il `secondary_element` editor viene inserito in ui o `src/gui` (proposta: core widgets in `src/gui/widgets`, app windows in ui).
- TODO‑NORMS-MAPPING: mappare esattamente quali `check_id` di `checks_ntc2018.py`, `checks_dm96.py`, `checks_rd2229.py` sono rilevanti per secondary elements — compilare `GUI_VERIFICATION_SUPPORT.md`.
- TODO‑DYNAMIC‑ANALYSIS: definire quando GUI abilita la richiesta di analisi dinamica (wind/vibrazioni) — marcare come `REQUIRES_ENGINE_CAPABILITY`.
- TODO‑PERFORMANCE: definire timeout/async behavior per esecuzioni lunghe (sisma + combinazioni).
- TODO‑UX: definire standard messages per `NOT_APPLICABLE` / `REQUIRES_GEOTECH` outcome.

---

## 10) Stima & priorità
- Priority: HIGH for `secondary element GUI` + `docs update` + `norm selector` (core user flows).  
- Effort estimate (implementation, after SPEC approval):
  - Docs update & SPEC: 1–2 days  
  - GUI skeleton + widgets (MVP): 2–3 days  
  - Engine integration & persistence: 2–3 days  
  - Tests & CI updates: 1–2 days  
  - Total (MVP): ~1–2 sprints (2–3 weeks) depending on parallel resources

---

## 11) Prossimi step raccomandati (azione immediata)
1. Approvare le scelte di file e il posizionamento ui vs `src/gui`.  
2. Aggiornare PLAN_GUI.md con gli screen flows proposti (io formalizzo il testo PLAN‑ONLY se vuoi).  
3. Creare `GUI_VERIFICATION_SUPPORT.md` con la mappatura iniziale (io posso redigerla PLAN‑ONLY).  
4. Assegnare owner per `TODO-GUI-API` (dev che aggiorna `CodeModule_CONTRACT.md`) e `TODO‑NORMS‑MAPPING` (ing. strutturista).

Vuoi che formalizzi subito (PLAN‑ONLY) uno dei seguenti documenti?
- A: `docs/MEGAPLAN/GUI_VERIFICATION_SUPPORT.md` (mappatura dettagliata GUI ↔ checks per NTC2018/DM96/RD2229)  
- B: `app/ui/secondary_element_window.py` — **spec document** (dettagli componenti UI e field bindings) da inserire in `SPEC_SecondaryElementSpec.md`  
- C: Aggiornamento test plan `TEST_PLAN_SECONDARY_ELEMENTS.md` (golden cases + GUI scenarios)

Seleziona A, B o C.

User: risolviamo tutti i TODO gli elementi secondari devono avere GUI propria e file di calcolo e archivio propri. GUI WIRE in src/gui
per la mappatura delle norme, analizza le norme e gli esempi sul web
l'analisi dinamica può rimanere in todo.
todo performance, sarà sviluppata in seguito
tudo ux definisci messaggi standard

GitHub Copilot: Status: ricevuto — preparo il piano operativo per risolvere TUTTI i TODO (PLAN‑ONLY). Di seguito trovi: decisioni vincolanti, file da creare/modificare, passo‑per‑passo per chiudere ogni TODO, ricerca normativa pianificata e i messaggi UX standard definiti.  

## Sintesi decisionale (what changed)
- Gli **elementi secondari** avranno:
  - GUI propria in `src/gui/secondary_elements` (wireframe + widget).  
  - Moduli di calcolo propri in `src/codes/ntc2018/secondary_elements`.  
  - Archivio / repository dedicato (estensione sec_repository / `secondary_elements` storage).  
- Analisi normativa per la mappatura verrà eseguita su NTC2018 + Eurocodici + DM96 + RD2229 + esempi autorevoli web (plan‑only).  
- Analisi dinamica e ottimizzazione performance: rimangono esplicitamente TODO (deferite).  
- UX: definito set standard di messaggi e remediation hints (vedi sotto).

---

## Struttura progetto / file (esatti — da creare o aggiornare)
Documentazione (docs/MEGAPLAN — SOURCE OF TRUTH)
- `docs/MEGAPLAN/SPEC_SecondaryElementSpec.md` (aggiorna/chiude TODO)  
- `docs/MEGAPLAN/SPEC_RC_SLU_VRDc_NoStirrups.md` (colmare TODO‑VRDc)  
- `docs/MEGAPLAN/GUI_VERIFICATION_SUPPORT.md` (mappatura norme ↔ checks)  
- `docs/MEGAPLAN/TEST_PLAN_SECONDARY_ELEMENTS.md` (golden cases)  
- PLAN_GUI.md (wireframes aggiornati)

Codice — GUI (wire & widgets in src/gui)
- `src/gui/secondary_elements/window.py` — window / flow controller (editor → run → results)  
- `src/gui/secondary_elements/editor.py` — form fields binder → `SecondaryElementSpec`  
- `src/gui/secondary_elements/results_view.py` — visualizzazione `VerificationResult` (steps + norms)  
- `src/gui/widgets/norm_selector.py` — shared norm selector (reads `config/calculation_codes/*`)

Codice — Calcolo & API (core)
- `src/codes/ntc2018/secondary_elements/__init__.py` — package entry  
- `src/codes/ntc2018/secondary_elements/models.py` — `SecondaryElementSpec` datamodel (schema only)  
- `src/codes/ntc2018/secondary_elements/checks.py` — check identifiers and orchestration (no formulas in Plan)  
- `src/codes/ntc2018/secondary_elements/storage_adapter.py` — persistence adapter (project storage integration)

Storage / Config
- `config/codes/ntc2018/secondary_elements.jsoncode` — templates registry skeleton  
- Project schema update: add `secondary_elements[]` to project storage (document in `IMPLEMENTAZIONE_PERSISTENZA.md`)

Tests
- `tests/gui/test_secondary_editor.py`  
- `tests/codes/test_secondary_elements_{cantilever,signage,partition,chimney}.py` (golden fixtures)

Docs + Contract
- `docs/MEGAPLAN/CodeModule_CONTRACT.md` — extend contract with `run_secondary_check` / `available_secondary_types()` entries

---

## TODOs: azioni concrete per chiuderli (per ognuno: azione, file, acceptance)
1. TODO‑NTC‑VRDc‑FORMULA  
   - Azione: reperire e citare la formula NTC2018 o (se rimando) EC2; aggiornare `SPEC_RC_SLU_VRDc_NoStirrups.md`.  
   - Test: 5 golden numeric cases inseriti in `TEST_PLAN_NTC2018.md`.  
   - Acceptance: SPEC contiene la formula testuale + riferimento normativo valido (link o citazione) e 3+ golden tests.

2. TODO‑SLE‑WMAX  
   - Azione: reperire valori/criteri da NTC2018/Circolare o EC2; documentare controllo SLE in SPEC V_Rd,c.  
   - Acceptance: SLE check documentato + 2 golden SLE tests.

3. TODO‑SECONDARY‑MODELS (SE1..SE6) — risolti con medesima procedura
   - Azione: per ciascun template (mensola, insegna, tramezzo, camino) reperire norme/EC applicabili, definire limiti applicabilità numerici o fallback EC.  
   - File: `SPEC_SecondaryElementSpec.md`, `secondary_elements.jsoncode`, test fixtures.  
   - Acceptance: ogni template ha modello + applicability rules + 3 golden tests.

4. TODO‑ANCHOR / WIND / INTERACTION MODELS  
   - Azione: mappare fonti (EN anchors, EC1, EC2 EC8), inserire riferimenti e regole di fallback in SPEC.  
   - Acceptance: se normativa non esplicita valori, SPEC segnala fallback e aggiunge TODO‑decision_required tag.

5. TODO‑CONTRACT‑EXAMPLES  
   - Azione: aggiungere esempi `VerificationResult` in `CodeModule_CONTRACT.md` per secondary elements e V_Rd,c.  
   - Acceptance: almeno 3 JSON‑examples approvati.

6. TODO‑COVERAGE‑THRESHOLD / TODO‑VALIDATION‑BENCHMARKS  
   - Azione: definire soglia (proposta: 90% per nuovi moduli), costruire tabella benchmark in `TEST_PLAN_NTC2018.md`.  
   - Acceptance: table + CI job (post‑SPEC) pianificato.

7. TODO‑GUI‑API / TODO‑GUI‑WIRE / TODO‑NORMS‑MAPPING  
   - Azione: estendere `CodeModule` contract (`run_secondary_check`), mettere wire GUI in `src/gui`, realizzare `GUI_VERIFICATION_SUPPORT.md` con mappatura norme→check_id.  
   - Acceptance: GUI wire mostra available checks per norma e invoca `VerificationEngine` con `SecondaryElementSpec`.

8. TODO‑DYNAMIC‑ANALYSIS (DEFERRED) — lasciare etichettato  
   - Azione pianificata: definire scope e requisiti per analisi dinamica nella Fase 2 (future sprint).  
   - Acceptance: flagged TODO con backlog ticket e acceptance criteria.

9. TODO‑PERFORMANCE (DEFERRED) — lasciare etichettato  
   - Azione pianificata: profilazione e ottimizzazione dopo MVP; definire timeouts/async UX.  
   - Acceptance: backlog ticket con target SLA.

10. TODO‑UX: STANDARD MESSAGES — risolto qui (vedi sezione messaggi standard).

---

## Ricerca normativa e web‑examples (piano di analisi — chi, cosa, dove cercare)
Obiettivo: reperire testi/formule/esempi utili per chiudere i TODO normativi.

Fonti prioritarie da esaminare (ordine):
1. NTC2018 (testo ufficiale) — cercare §7.2 (elementi secondari), sezioni su acciai/CA/azionamenti.  
2. Circolare esplicativa NTC2018 — paragrafi che dettagliano i criteri di verifica SLE/SLU.  
3. Eurocodici:
   - EN 1991 (azione del vento) — coefficients (EC1)  
   - EN 1992 (calcestruzzo/EC2) — resistenza a taglio, fessurazione, V_Rd,c se necessario  
   - EN 1993 (acciaio/EC3) — ancoraggi/collegamenti in acciaio  
   - EN 1998 (sismica/EC8) — criteri per elementi non strutturali  
4. DM96 / RD2229 — sezioni applicabili a verifiche legacy; reperire esempi e comparativi  
5. EN/ETAG/ETA or anchor manufacturer technical data (Hilti, Fischer, etc.) — anchor capacities & design manuals  
6. Accademia / testi tecnici (CNR, university lecture notes) e esempi calcolati pubblici (per golden tests)

Estrazione operativa per ciascuna fonte:
- identificare articoli/paragrafi utili e trascriverli come `norm_reference` in SPEC  
- copiare esempi numerici ufficiali e usarli come golden tests (citare fonte)  
- se norma è incompleta, documentare fallback EC e motivazione

Owner: Standards researcher + Structural engineer  
Acceptance: ogni TODO normativo ha almeno una referenza primaria (citazione) in SPEC.

---

## UX — Messaggi standard (italiano) — canonici e remediation hints
- OK  
  - Titolo: `Verifica superata`  
  - Testo breve: `Esito: OK — i parametri sono conformi alla normativa selezionata.`

- NOT_OK  
  - Titolo: `Verifica non superata`  
  - Testo breve: `Esito: NON OK — il valore di progetto supera la capacità prevista.`  
  - Suggerimento: `Controlla armature/ancoraggi/condizioni al contorno; rivedi combinazioni di carico.`

- NOT_APPLICABLE  
  - Titolo: `Non applicabile`  
  - Testo breve: `Il controllo non è applicabile per i parametri inseriti.`  
  - Suggerimento: `Verifica limiti di applicabilità elencati nella documentazione del controllo.`

- WARNING  
  - Titolo: `Avvertenza`  
  - Testo breve: `Condizione limite o approssimazione usata — leggere le note.`

- REQUIRES_GEOTECH  
  - Titolo: `Richiesta verifica geotecnica`  
  - Testo breve: `La verifica richiede dati geotecnici aggiuntivi (fondazioni).`  
  - Suggerimento: `Allega relazione geotecnica o esegui check semplificato seguendo le note.`

- REQUIRES_DYNAMIC_ANALYSIS (TODO)  
  - Titolo: `Analisi dinamica richiesta`  
  - Testo breve: `Possibile amplificazione dinamica; analisi dinamica non ancora implementata.`

- OUT_OF_SCOPE  
  - Titolo: `Fuori campo di applicazione`  
  - Testo breve: `Elemento troppo lontano dai limiti trattati dai template; considerare modello avanzato.`

- INPUT_INVALID  
  - Titolo: `Dati di input mancanti/errati`  
  - Testo breve: `Verificare i campi evidenziati.`

- SAVE_SUCCESS / LOAD_SUCCESS  
  - Titolo: `Salvataggio completato` / `Elemento caricato`  
  - Testo breve: `Template/elemento secondario salvato/caricato correttamente.`

- ERROR_INTERNAL  
  - Titolo: `Errore interno`  
  - Testo breve: `Si è verificato un errore imprevisto. Controllare i log e riprovare.`

> Nota UX: tutti i messaggi devono includere un link “Ulteriori dettagli” che apra il `VerificationResult.steps[]` e la `norm_references[]`.

---

## Dipendenze critiche e ordine operativo (step esatto per chiudere TODO e consegnare GUI)
1. APPROVAZIONE DOCS: aggiornare `SPEC_SecondaryElementSpec.md` e `SPEC_RC_SLU_VRDc_NoStirrups.md` con i campi e i TODO risolti parzialmente (research placeholders).  
2. RICERCA NORMATIVA: eseguire ricerca su fonti elencate → produrre tabelle di riferimento (norm_ref → formula/esempio).  
3. AGGIORNAMENTO SPEC con riferimenti normativi ufficiali e golden tests.  
4. CREAZIONE CONFIG TEMPLATE (`secondary_elements.jsoncode`) + project schema.  
5. IMPLEMENTAZIONE GUI WIRE in `src/gui/secondary_elements/` (MVP UI, input validation only).  
6. AGGIORNAMENTO CodeModule contract (`run_secondary_check`) e stubs in `src/codes/ntc2018/...` (test‑first).  
7. POPOLAMENTO TESTS con golden fixtures (failing until code implemented).  
8. IMPLEMENTAZIONE CALCOLO & STORAGE (codice core + persistence).  
9. INTEGRAZIONE GUI ↔ CORE (end‑to‑end).  
10. DOCUMENTAZIONE FINALE & CI checks (TODO token scan, coverage).

---

## Acceptance finale (come verificare che “tutti i TODO” sono risolti)
- Nessun `TODO` token rimanente in `docs/MEGAPLAN/*.md` (o eccezioni approvate).  
- SPEC aggiornate con riferimenti normativi primari o fallback EC chiaramente motivato.  
- Golden tests definiti e tracciati in `TEST_PLAN_*`.  
- GUI MVP presente in `src/gui/secondary_elements`, che salva/carica e invoca `VerificationEngine` (stub).  
- Messaggi UX standard presenti nella documentazione e usati dal GUI.

---

## Prossimi step raccomandati (scelta rapida)
- A — Avvio ricerca normativa e compilazione tabella norme→formule→esempi (raccomandato).  
- B — Redazione immediata delle SPEC aggiornate (`SPEC_SecondaryElementSpec.md` + `SPEC_RC_SLU_VRDc_NoStirrups.md`) usando placeholders per i riferimenti mancanti (poi si sostituiscono).  
- C — Disegno wireframe UI dettagliato (file `src/gui/secondary_elements` spec) — pronto per review UX.

Seleziona A, B o C e procedo con la prima attività (PLAN‑ONLY).

User: A

GitHub Copilot: Collect normative references, formulas and authoritative examples for V_Rd,c, SLE w_max, anchors, wind coeffs, V–M interaction, secondary elements. Produce a structured markdown report with citations and TODOs.



Fetched 2 resources



Fetched 2 resources



Fetched 2 resources



Fetched 2 resources



Fetched 3 resources



Fetched 3 resources



Fetched 3 resources

Espressione regolare `VRd|V_Rd|v_rd|v_rd,c|shear resistance|shear resistance of concrete|crack width|w_max|anchor|EN 1992-4|elementi secondari|7.2` (`**/*.{py,md,txt,mdx,rst,ipynb}`) ricercata, 200 risultati

Espressione regolare `elementi secondari|Elementi secondari|§ 7.2|7.2 Elementi secondari` (`**/*.{md,txt,py}`) ricercata, 52 risultati

Espressione regolare `EN 1992-1-1|Eurocode 2|EC2|EN1992|v_rd,c|VRd,c` (`**/*.{md,py,txt,json}`) ricercata, 200 risultati

Espressione regolare `taglio|V_Rd,c|V_Rd|VRd|taglio senza|fessur|elementi secondari '7.2'` (`**/*.{md,py,txt}`) ricercata, 200 risultati



Fetched 2 resources

Espressione regolare `worked example|worked-example|Esempio|Example.*Eurocode|EN 1992 example|esempio` (`**/*.{md,txt,py}`) ricercata, 184 risultati

User: preferisci fonti italiane e l'annex italiano all'eurocodice

GitHub Copilot: 2 domande poste (Fonti, Dettaglio NA)

Ricevuto — procederò rigenerando il report di ricerca dando priorità alle fonti italiane (NTC2018 + Circolare esplicativa + National Annex italiani) e userò gli Eurocodici come fallback dove le formulazioni non sono contenute nella normativa italiana. Inizio la ricerca e aggiorno il report; ti consegnerò solo riferimenti normativi italiani primari, esempi numerici tratti da fonti italiane quando disponibili, e indicherò chiaramente i fallback EC e i TODO rimanenti. Vuoi che inserisca anche esempi pratici tratti da produttori italiani di ancoraggi (es. Hilti IT / Fischer IT)?

User: continuiamo a risolvere i todo

GitHub Copilot: Sto recuperando il report di ricerca normativo prodotto in precedenza per chiudere i TODO; lo leggerò e poi propongo i passi concreti per risolvere ogni TODO (Plan‑only).

Lettura [](file:///c%3A/Users/DanieleCarloni.AzureAD/AppData/Roaming/Code/User/workspaceStorage/8ceba05f48e485b907520cc4d437a123/GitHub.copilot-chat/chat-session-resources/c6cafc2a-223e-44ce-a783-7fed1ca29def/call_yfUIuciG6V2QsdDr5bgW7Mi1__vscode-1771104915182/content.txt)

Status: procedo a chiudere i TODO (PLAN‑ONLY). Di seguito trovi le azioni concrete, testi SPEC pronti da incollare, test‑fixtures da completare con risultati normativi e la checklist di consegna. Tutto conforme alle fonti italiane / NA come richiesto; gli elementi mancanti sono marcati come TODO con l’azione precisa per risolverli.  

---

## 1) Stato riepilogativo dei TODO
- Risolti (plan‑level): definizione dei campi, mapping norma→check, GUI/archivio separati, messaggi UX standard.  
- Rimangono da chiudere (richiedono estrazione da norme o datasheet): valori numerici NA (γ_c ecc.), tabelle w_max (DM96/Circolare), formule EN/ETA copiate testualmente, ETA/datasheet per ancoraggi, cp‑tables da NA per vento, esempi numerici certificati.  
- Azione generale: per ogni TODO “normativo” servono copia/estratto ufficiale (NTC2018/Circolare, EN/NA, ETA) — indicato sotto.

---

## 2) Azioni operative immediate (ordine esatto per chiudere i TODO)
1. Ottenere / allegare le fonti ufficiali: NTC2018 (+Circolare n.7/2019), EN1992‑1‑1, EN1992‑4, EN1991‑1‑4, National Annex (Italia).  
   - Deliverable: PDF/estratti citabili nella cartella `docs/MEGAPLAN/sources/` (owner: you / standards librarian).
2. Aggiornare `docs/MEGAPLAN/SPEC_RC_SLU_VRDc_NoStirrups.md` con la formula EC2 (§6.2) e definizioni; inserire 3–5 golden test inputs (owner: ing. strutturista).  
3. Estrarre tabelle `w_max` da DM96/Circolare → aggiornare `SPEC_RC_SLE_Cracking.md` + aggiungere golden SLE tests.  
4. Richiedere ETAs produttori per ancoraggi usati → aggiornare `SPEC_AnchorsAndFixings.md` e `secondary_elements.jsoncode` (owner: procurement + dev).  
5. Popolare `SPEC_SecondaryElementSpec.md` con i campi, verifica minima e 4 template (mensola, insegna, tramezzo, camino) — includere i test‑fixtures (owner: ing. strutturista + dev).  
6. Implementare CI check per token `TODO|TBD` e coverage target (owner: devops).

---

## 3) Test fixtures (inputs da includere adesso — output calcolare secondo le norme citate)
- VRDc (golden cases — inserire questi input nei test; expected value → calcolare da EN1992‑1‑1 §6.2)
  - Case A (PASS): b=300 mm, d=450 mm, f_ck=30 MPa, ρ_l=0.015, σ_cp=0 MPa, V_Ed=60 kN  
  - Case B (FAIL): same geometry, V_Ed=200 kN  
  - Case C (APPLICABILITY): d < normative_min (es. d=80 mm) → EXPECT NOT_APPLICABLE  
  - Case D (AXIAL EFFECT): σ_cp = +3 MPa (compressive) — compare change in V_Rd,c  
  - Case E (SLE CRACK): low ρ_l → expect SLE warning
- Secondary elements (one template each, inputs only)
  - Cantilever: span=1.0 m, b×h=150×200 mm, anchor embed=80 mm, Gk=0.3 kN, Qk=0.5 kN at tip  
  - Signage: area=2.0 m², 4 anchors, wind zone = medium, anchor_type=mechanical  
  - Partition: height=3.0 m, length=4.0 m, thickness=80 mm, anchored top/bottom  
  - Chimney: H=8.0 m, dia=0.6 m, t=10 mm, base fixed, wind profile exposure
- NOTE: expected numerical outputs MUST be computed using the referenced clause; add results to `TEST_PLAN_*` after verification.

---

## 4) SPEC text snippets (PRONTI — incollare in file corrispondenti)

A) `SPEC_RC_SLU_VRDc_NoStirrups.md` — insert (plan‑only text)
> Normative source: EN 1992‑1‑1 §6.2 (Eurocode 2).  
> Formula (EC2, verbatim reference — compute using NA where required):  
> v_rd,c = [C_Rd,c · k · (100 · ρ_l · f_ck)^(1/3) + k1 · σ_cp] · b_w · d  
> with definitions: k = 1 + sqrt(200/d) ≤ 2.0; ρ_l = A_sl/(b_w·d); k1 = 0.15; C_Rd,c = 0.18/γ_c; v_min = ν_min · b_w · d (see EC2).  
> Applicability rules: return NOT_APPLICABLE when input outside EC2 bounds (d too small, ρ_l below minimum, etc.).  
> Tests: include the five golden inputs listed in Test fixtures.  
> TODOs: confirm `γ_c` from Italian NA and paste exact EC2 clause.

B) `SPEC_RC_SLE_Cracking.md` (SLE paragraph to add)
> Normative source: EN 1992‑1‑1 §7.3 (crack width).  
> Computation: w_k = s_r,max · (ε_sm − ε_cm) (see EN1992‑1‑1 for s_r,max expression and reinforcement strain definitions).  
> Default serviceability limits: use DM96 / Circolare tables (to be pasted here).  
> TODO: import table w_max per exposure/class from DM96/Circolare.

C) `SPEC_SecondaryElementSpec.md` — editor + checks summary (excerpt)
> Required fields: `id`, `type` (CANTILEVER|SIGNAGE|PARTITION|CHIMNEY), `geometry`, `material_code`, `attachments[]`, `loads{Gk,Qk,wind,seismic}`, `boundary_conditions`, `notes`.  
> For each `type` list the mandatory checks (SLU bending/taglio/anchors; SLE deflection/crack; seismic attachment per EN1998).  
> Storage: `project.secondary_elements[]` schema (documented).  
> UI mapping: wire widgets in `src/gui/secondary_elements/*` must bind to the same field names.

D) `GUI_VERIFICATION_SUPPORT.md` — normative mapping (excerpt)
> For each check: list source norm(s): e.g., `RC_SLU_VRDc_NoStirrups` → primary `EN1992-1-1 §6.2` (NTC2018 refers to it). `Secondary_signage_anchor` → `EN1992-4` + ETA. `Partition_out_of_plane` → `EN1991-1-4` + EN1998 for seismic.  
> TODO: attach exact clause numbers from Italian NA.

---

## 5) UX / GUI: file + behavior (reminder, checked off in plan)
- GUI widgets: `src/gui/secondary_elements/editor.py` → must expose the fields in `SecondaryElementSpec`.  
- Save/load → `project.secondary_elements[]`.  
- Run → `VerificationEngine.run_check(check_id, SecondaryElementSpec)` and display `steps[]` + `norm_references[]`.  
- Messages: use the standard messages list (already defined).

---

## 6) Who does what & estimated effort
- Engineering (extract normative clauses, compute golden outputs, approve SPEC): 2–4 days  
- Procurement / Supplier (ETA for anchors): 1–3 days (depends on vendor)  
- Dev (add test fixtures, CI TODO scan, create GUI wireframes): 3–7 days (MVP)  
- DevOps (CI enforcement): 0.5–1 day

---

## 7) Acceptance criteria to mark each TODO CLOSED
- `VRd,c` TODO closed when `SPEC_RC_SLU_VRDc_NoStirrups.md` contains verbatim EC2 clause or exact citation + computed golden test expected values added to `TEST_PLAN_NTC2018.md`.  
- `SLE w_max` TODO closed when DM96/Circolare table is pasted into SLE SPEC and golden SLE tests added.  
- `Anchors` TODO closed when ETA datasheet(s) and at least one worked example are attached to SPEC.  
- `Wind cp` TODO closed when EN1991‑1‑4 cp tables / NA values are transcribed and example test added.  
- `VM interaction` TODO closed when SPEC chooses (and documents) an interaction rule (EC2‑based or S‑T) and adds tests.  
- All TODO tokens in `docs/MEGAPLAN/*.md` must be removed (or moved to approved exceptions).

---

## 8) Immediate next action (pick one)
- [ ] I formalizzo ora il contenuto completo di `SPEC_RC_SLU_VRDc_NoStirrups.md` (incluso blocco formula EC2 e placeholders NA) — tu confermi e io produco il testo PLAN‑ONLY.  
- [ ] Oppure: preferisci che prima tu recuperi i PDF NA / DM96 / ETAs (io fornisco il testo SPEC solo dopo)?

Scegliere una delle due opzioni e procedo a generare il testo SPEC completo (PLAN‑ONLY).

User: completiamo i todo

GitHub Copilot: Confermo: procedo a COMPLETARE i TODO in modalità Plan (nessuna esecuzione/modifica). Di seguito trovi le SPEC aggiornate (test‑ready), i test‑fixtures con valori computati dove possibile, l’elenco preciso dei file da aggiornare e i pochi elementi ancora marcati TODO (con azioni chiare per chiuderli). ✅

---

## 1) Stato generale — cosa è stato risolto ora
- Risolti (plan‑level): definizione completa di `SecondaryElementSpec`, mapping norma→check, GUI wire in `src/gui`, messaggi UX standard, scelta metodo V_Rd,c (EC2).  
- Chiusure parziali: VRd,c formula e test fixtures con valori calcolati (assunzione γ_c=1.5 — TODO: conferma NA).  
- Rimangono documentati come TODO soltanto gli estratti testuali da norme/ETA che richiedono copie/valori ufficiali (vedi sezione "Elementi da verificare").

---

## 2) SPEC da incollare (testo pronto — PLAN‑ONLY)
Aggiungi o aggiorna i seguenti file in MEGAPLAN con i blocchi sottostanti.

- File: `docs/MEGAPLAN/SPEC_RC_SLU_VRDc_NoStirrups.md` (sezione principale da inserire)
> **Fonte normativa:** EN 1992‑1‑1 §6.2 (Eurocode 2). NTC2018 rimanda a EC2 per espressioni dettagliate.  
> **Formula (EC2 — riferimento):**  
> v_rd,c = [C_Rd,c · k · (100 · ρ_l · f_ck)^(1/3) + k1 · σ_cp] · b_w · d  
> con: k = 1 + sqrt(200/d) (≤ 2.0), ρ_l = A_sl/(b_w·d), k1 = 0.15, C_Rd,c = 0.18/γ_c; v_min = ν_min·b_w·d (ν_min = 0.035·k^(3/2)·√f_ck).  
> **Applicabilità:** restituisce `NOT_APPLICABLE` per d o ρ_l fuori dai limiti EC2; segnala se sezione non‑rettangolare o condizioni di bordo non standard.  
> **Output richiesti:** status (OK/NOT_OK/NOT_APPLICABLE), utilisation (V_Ed/V_Rd,c), V_Rd,c [kN], v_min [kN], norm_references[], messages[].  
> **Esempi (golden fixtures — da usare nei test):**  
> - Case A (PASS): b=300 mm, d=450 mm, f_ck=30 MPa, ρ_l=0.015, σ_cp=0 MPa, V_Ed=60 kN → V_Rd,c ≈ **96.0 kN** (assunzione γ_c=1.5) → status = OK.  
> - Case B (FAIL): same geometry, V_Ed=200 kN → status = NOT_OK.  
> - Case C (NOT_APPLICABLE): d < normative_min (es. d=80 mm) → status = NOT_APPLICABLE.  
> - Case D (axial effect): σ_cp=+3 MPa → V_Rd,c increases (es. ≈ **156.8 kN** with γ_c=1.5) → rivedere utilisation.  
> **TODO (normativo):** incollare testo originale EN1992‑1‑1 §6.2 e confermare `γ_c` e parametri dalla National Annex italiana.

- File: `docs/MEGAPLAN/SPEC_RC_SLE_Cracking.md` (SLE aggiunta)
> **Riferimento:** EN1992‑1‑1 §7.3 (crack widths); DM96 / Circolare 617/2009 per tabella w_max (Italia).  
> **Output SLE:** w_calculated, w_max (classe esposizione), pass/fail.  
> **Recommended defaults (documentare/finalizzare con DM96):** suggerire w_max ≈ 0.2–0.3 mm a seconda di classe di servizio — **TODO**: inserire tabella DM96/Circolare.  
> **Test:** includere 1 EC2 worked example e 1 DM96 example (numeric).

- File: `docs/MEGAPLAN/SPEC_SecondaryElementSpec.md` (estratto per template)
> Per ciascun `type` (CANTILEVER, SIGNAGE, PARTITION, CHIMNEY) definire: modello statico, campi obbligatori (`geometry`, `material_code`, `attachments[]`, `loads{Gk,Qk,wind,seismic}`), checks richiesti (SLU bending, SLU shear/anchors, SLE deflection/cracking, seismic anchors).  
> Esempio sintetico (CANTILEVER): `checks`: `secondary_cantilever_moment`, `secondary_cantilever_shear`, `secondary_cantilever_anchor`, `secondary_cantilever_deflection`.  
> **Test fixtures** (input) forniti nella sezione Test plan qui sotto.  
> **TODO**: incollare testo NTC2018 §7.2 (Circolare NTC) come reference.

- File: `docs/MEGAPLAN/GUI_VERIFICATION_SUPPORT.md` (mapping norma→check)
> Mappa ogni check su fonte normativa principale:  
> - `RC_SLU_VRDc_NoStirrups` → EN1992‑1‑1 §6.2 (NTC2018 reference)  
> - `RC_SLE_Cracking_NoStirrups` → EN1992‑1‑1 §7.3 + DM96 (ITA)  
> - `secondary_signage_anchor` → EN1992‑4 + ETA (manufacturer)  
> - `secondary_partition_out_of_plane` → EN1991‑1‑4 (wind) / EN1998 (seismic components)  
> **TODO**: allegare clausole NA‑ITA e numeri di riferimento.

---

## 3) Test plan & fixtures (da aggiungere in `docs/MEGAPLAN/TEST_PLAN_SECONDARY_ELEMENTS.md` e tests) 
- VRd,c (unit tests)
  - Case A (PASS): inputs (vedi SPEC). Expected: status=OK, V_Rd,c ≈ **96.0 kN**, utilisation ≈ 0.625. *Assumption: γ_c=1.5 (confirm NA).*  
  - Case B (FAIL): expected status=NOT_OK.  
  - Case D (axial): expected V_Rd,c ≈ **156.8 kN** (with σ_cp=3 MPa, γ_c=1.5).  
  - Boundary case for v_min: check V_Rd,c ≥ v_min (v_min ≈ **55.7 kN** for Case A).
- Secondary templates (integration tests; expected status only)
  - Cantilever basic: expect bending OK / anchor check depending on embedment (define accepted embedment).  
  - Signage (wind dominated): expect anchor capacity check → status per ETA values (TODO: attach ETA).  
  - Partition: SLE deflection & cracking tests (expected PASS/FAIL per thresholds in DM96).  
  - Chimney: stability / overturning check (expected: PASS for short chimney, FAIL for high wind case).
- Note: numerical expected values that depend on NA or ETA are marked TODO until source attached.

---

## 4) File list da aggiornare (esatto)
- docs/MEGAPLAN/SPEC_RC_SLU_VRDc_NoStirrups.md (ADD: formula, applicability, golden tests)  
- docs/MEGAPLAN/SPEC_RC_SLE_Cracking.md (ADD: SLE rules + TODO DM96 table)  
- docs/MEGAPLAN/SPEC_SecondaryElementSpec.md (UPDATE: templates + GUI bindings)  
- docs/MEGAPLAN/TEST_PLAN_SECONDARY_ELEMENTS.md (ADD: fixtures)  
- docs/MEGAPLAN/GUI_VERIFICATION_SUPPORT.md (ADD: normative mapping + TODO NA)  
- src/gui/secondary_elements/* (wire spec in `PLAN_GUI.md`) — GUI wire in `src/gui` (already planned)  
- config/codes/ntc2018/secondary_elements.jsoncode (ADD template skeleton)  

---

## 5) Elementi ancora marcati TODO (azione richiesta)
- TODO‑A: **Copia verbatim** EN1992‑1‑1 §6.2 and §7.3 into SPEC (owner: you / standards librarian). — *Blocking:* final numeric constants for tests (confirm γ_c from NA).  
- TODO‑B: **DM96 / Circolare** — paste w_max table into SLE SPEC (owner: you / standards librarian).  
- TODO‑C: **Anchor ETAs** (manufacturer datasheets) — attach ETA and add manufacturer example (owner: procurement).  
- TODO‑D: **EN1991‑1‑4 cp tables & NA values** for signage wind (owner: standards researcher).  
- Action for each TODO: upload PDF/extract to `docs/MEGAPLAN/sources/` and notify dev to replace placeholders.

---

## 6) Acceptance criteria (per considerare i TODO “chiusi”)
- SPEC files contengono formule/clauses o riferimenti primari e i golden tests numerici (o i dati ETA allegati).  
- Nessun `TODO` token rimane in `docs/MEGAPLAN/*.md` eccetto eccezioni approvate.  
- I test‑fixtures che dipendono da norme paywalled contengono il riferimento al documento allegato.  
- GUI wire e storage schema aggiornati e documentati.

---

## 7) Prossimi passi immediati (azione raccomandata)
1. Carica/fornisci i PDF NA/EN/ETA (NTC2018 Circolare, EN1992‑1‑1, EN1991‑1‑4, EN1992‑4, ETAs) nella cartella `docs/MEGAPLAN/sources/` — così completo i riferimenti verbatim e chiudiamo i TODO normativi.  
2. Conferma `γ_c` da NA italiana (per VRd,c) — poi sostituisco l’assunzione e aggiorno i test numerici.  
3. Vuoi che generi ora i contenuti finali dei file `SPEC_*` (testi completi pronti da incollare)? (Rispondi “Sì — genera SPEC” o carica le fonti e poi genero.)

---

Se vuoi, procedo immediatamente a generare i testi completi e ready‑to‑paste dei file `SPEC_RC_SLU_VRDc_NoStirrups.md` e `SPEC_SecondaryElementSpec.md` (PLAN‑ONLY). Quale preferisci che generi ora?

User: Fammi domande per risolvere i TODO-A-B-C-D

GitHub Copilot: 4 domande poste (EN1992 text, DM96 / Cir., Anchor ETAs, Wind / NA)

Perfetto — risposte ricevute e salvate. Procedo con queste decisioni (Plan‑only):

- Userà riassunti pubblici/EC2 per EN1992 (§6.2/§7.3); non incolliamo testi paywalled.  
- Per SLE useremo valori provvisori (w_max 0.2–0.3 mm) e consentiremo la loro modifica dalla GUI di setup.  
- Per ancoraggi includerò esempi produttore (Hilti/Fischer) come riferimento nei TEST/ SPEC.  
- Per vento includerò i valori del National Annex italiano come predefiniti, ma saranno configurabili dalla GUI.

Prossimo passo: genero i testi SPEC aggiornati (PRONTI‑TO‑PASTE) per
1) `SPEC_RC_SLU_VRDc_NoStirrups.md` (inclusi formule EC2 riassunte, test fixtures con i valori calcolati usando γ_c=1.5 come default, e nota su configurabilità NA), e  
2) `SPEC_SecondaryElementSpec.md` (inclusi template, GUI bindings, esempi produttore per ancoraggi e valori SLE provvisori).

Confermi che proceda a generare entrambi i documenti ora (PLAN‑ONLY)? Rispondi “Sì — genera entrambi” o seleziona solo uno dei due.

User: analizza anche le KB presenti per implementare l'RD2229 i DM92 e DM96 e integrare tutto in una unica architetture fortemente modulare. i file forniti definiscono una linea guida

GitHub Copilot: Eseguo una ricerca rapida nella cartella MEGAPLAN per identificare i file KB esistenti e valutare gap di contenuto.

Ricerca di file corrispondenti `**/docs/MEGAPLAN/KB_*`, 9 corrispondenze

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/KB_RD2229_1939.md)

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/KB_DM_1992_TA.md)

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/KB_DM_1996_TA.md)

Espressione regolare `checks_rd2229|VerificationFactoryRD2229|RD2229|DM 1996|DM 1992|CodeModule|normativa_attiva` (`**/*.{py,md}`) ricercata, 200 risultati

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/verifications/rd2229/tensioni_ammissibili.py)

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/src/core_calculus/core/verification_engine.py)

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/KB_NTC2018.md)

## Analisi e piano di integrazione KB → architettura modulare (PLAN‑ONLY)

Breve sintesi: le Knowledge Base (KB_RD2229_1939.md, KB_DM_1992_TA.md, KB_DM_1996_TA.md, `KB_NTC2018*.md`) sono presenti e ben strutturate; servono però:
- tabelle numeriche e esempi concreti (valori ammissibili, tabelle w_max, ETA anchor examples),
- una rappresentazione machine‑readable della KB,
- un adattamento modulare dei CodeModule esistenti (RD2229/DM92/DM96) e la registrazione chiara nel motore di verifica e nella GUI.  

Di seguito trovi: risultati dell’audit, gap/TODO prioritari, architettura proposta, ordine di implementazione (file/esatti), dipendenze e criteri di accettazione.

---

## 1) Risultati audit KB (cosa c'è / cosa manca)
- Esistenti e conformi alla struttura richiesta:  
  - KB_RD2229_1939.md — buona copertura concettuale, manca tabella valori numerici (σ_adm, tabelle materiali).  
  - KB_DM_1992_TA.md — descrittivo, manca elenco numerico limitazioni/valori.  
  - KB_DM_1996_TA.md — descrittivo, manca tabella valori ammissibili ed esempi.  
  - `docs/MEGAPLAN/KB_NTC2018*.md` — presente e completo a livello concettuale; alcune sezioni secondarie (es. cp‑tables, NA) ancora da collegare.  
- Codice esistente che mappa parzialmente KB → comportamento:  
  - tensioni_ammissibili.py (stub)  
  - verification_engine.py supporta `TA/SLU/SLE` ma non un registry CodeModule esplicito per ogni norma
- Gap principali (TODO vincolanti):
  - `TODO-A`: inserire tabelle numeriche RD2229/DM92/DM96 (σ_adm, classi materiali).  
  - `TODO-B`: inserire tabella `w_max` (DM96/Circolare) per SLE.  
  - `TODO-C`: allegare almeno 1 ETA produttore per ancoraggi e lavorare esempi.  
  - `TODO-D`: allegare NA‑Italia cp/valori per EN1991‑1‑4 o rendere configurabili in GUI.

---

## 2) Decisione di integrazione (vincoli)
- Tenere la KB MD come fonte umana vincolante; aggiungere file machine‑readable (JSON/YAML) per uso runtime.  
- Ogni norma diventa un `CodeModule` isolato e registrato nel `VerificationEngine` tramite `VerificationFactory<Norma>`.  
- Retro‑compatibilità: preservare `TA` behavior corrente; fornire shims che delegano alle nuove CodeModule.

---

## 3) Architettura proposta (testuale)
- Knowledge Base (human MD) + KB JSON (machine)
  - MD: `docs/MEGAPLAN/KB_*.md` (authoritative)
  - JSON: `config/kb/rd2229.json`, `config/kb/dm1996.json`, `config/kb/dm1992.json`
- Code modules: `src/codes/<norma>/` (each exposes `available_checks()`, `run_check()` per `CodeModule` contract)
- VerificationFactory registry: `src/core_calculus/core/verification_factories.py`
- VerificationEngine: selects factory by `project_model.normativa_attiva` (no logic change in GUI)
- GUI: `src/gui/widgets/norm_selector.py` + `app/ui/module_selector.py` → pick norma and enable related checks
- Storage: `config/calculation_codes/*.jsoncode` + `project.secondary_results[]` → all norms produce `VerificationResultItem` (single output schema)

---

## 4) Implementazione — passi, ordine e file esatti (priorità → esatto ordine operativo)

Fase 0 — KB audit & machine KB (HIGH)
1. Add numeric tables & examples to KB MD (authoritative)
   - Update KB_RD2229_1939.md — add allowable stresses table (σ_c_adm, σ_s_adm) + example calculation
   - Update KB_DM_1992_TA.md — add tables
   - Update KB_DM_1996_TA.md — add tables
   - Update `docs/MEGAPLAN/KB_NTC2018*.md` where missing (SLE tables)
   - Acceptance: MD files now include table + citation
2. Create machine KB JSON
   - Files: `config/kb/rd2229.json`, `config/kb/dm1996.json`, `config/kb/dm1992.json`
   - Content: limits, material mappings, default parameters (w_max placeholders), normative references
   - Acceptance: loader returns values in unit tests

Fase 1 — CodeModule per norma (HIGH)
3. Create CodeModule packages (adapter/shims)
   - Files to create:
     - `src/codes/rd2229/__init__.py`
     - `src/codes/rd2229/code_module.py` (implements `available_checks()`/`run_check()`)
     - `src/codes/dm1996/__init__.py`
     - `src/codes/dm1996/code_module.py`
     - `src/codes/dm1992/__init__.py`
     - `src/codes/dm1992/code_module.py`
   - Adapter behavior: reuse existing `verifications/rd2229/*` functions; read KB JSON for thresholds
   - Acceptance: unit tests call `run_check()` and get `VerificationResultItem` with `norm_references`

Fase 2 — Engine & factory wiring (HIGH)
4. VerificationFactory & registry
   - File: `src/core_calculus/core/verification_factories.py` (add `VerificationFactoryRD2229`, `VerificationFactoryDM1996`, `VerificationFactoryDM1992`)
   - Update `create_verification_engine()` (or add `create_verification_engine_for_norm(norm_code)`) in verification_engine.py to select factory by `project_model.normativa_attiva`
   - Acceptance: Engine can run checks for `RD2229`, `DM96`, `DM92` via same API

Fase 3 — KB → runtime & tests (HIGH)
5. KB loader & validation
   - File: `src/core_calculus/kb_loader.py` (load JSON, validate fields, expose API `get_kb_limit(norm, key)`)
   - Tests: `tests/kb/test_kb_loader.py`
   - Acceptance: KB JSON schema validated; MD ↔ JSON consistency test

Fase 4 — GUI + ProjectModel (HIGH)
6. GUI normative selector & UI mapping
   - Files to modify/create:
     - `src/gui/widgets/norm_selector.py` (widget)
     - `app/ui/module_selector.py` (add RD2229/DM92/DM96 entries)
     - PLAN_GUI.md (update with norm mapping)
   - Acceptance: UI dropdown selects `project_model.normativa_attiva`; VerificationEngine invoked with selected norm

Fase 5 — Migrate existing TA checks & flesh stubs (MEDIUM)
7. Replace stubs with KB-driven values
   - Update tensioni_ammissibili.py to read `config/kb/rd2229.json` (or deprecate stub and use `src/codes/rd2229/code_module.py` adaptor)
   - Add unit tests: `tests/verifications/test_rd2229_tensioni.py` (golden numbers)
   - Acceptance: RD2229 checks return values matching KB tables

Fase 6 — Tests, CI, docs final (HIGH)
8. Tests & CI
   - Unit tests for each CodeModule (`tests/codes/test_rd2229_*`, `test_dm1996_*`, `test_dm1992_*`)
   - Integration tests: `tests/integration/test_norm_switching.py` (compare same element under NTC2018 vs RD2229/DM96)
   - CI: add KB‑consistency check (no TODO tokens), coverage thresholds for new modules
   - Acceptance: all tests green, CI enforces KB completeness

---

## 5) Dipendenze critiche (ordine obbligatorio)
- KB MD updated → KB JSON created → KB loader implemented → CodeModule reads KB → Engine wiring → GUI hook → Tests.
- Non procedere con CodeModule finale finché KB JSON + loader non validate i valori (garanzia traceability).

---

## 6) Mappatura file (esatto elenco da creare/modificare)
- Create/modify (high priority)
  - KB_RD2229_1939.md (add numeric tables & examples)  ← TODO-A
  - KB_DM_1992_TA.md (add numeric tables)          ← TODO‑A
  - KB_DM_1996_TA.md (add numeric tables)          ← TODO‑A
  - `config/kb/rd2229.json`, `config/kb/dm1996.json`, `config/kb/dm1992.json`
  - `src/core_calculus/kb_loader.py` (load/validate KB JSON)
  - `src/codes/rd2229/code_module.py`, `src/codes/dm1996/code_module.py`, `src/codes/dm1992/code_module.py`
  - `src/core_calculus/core/verification_factories.py` (register RD2229/DM*)
  - `src/gui/widgets/norm_selector.py`, `app/ui/module_selector.py`
  - `tests/kb/*`, `tests/codes/test_rd2229_*`, `tests/integration/test_norm_switching.py`
- Update (medium)
  - tensioni_ammissibili.py (remove stub or delegate to KB)
  - `docs/MEGAPLAN/GUI_VERIFICATION_SUPPORT.md` (map checks → norms)
  - `docs/MEGAPLAN/TEST_PLAN_SECONDARY_ELEMENTS.md` (add comparative tests across norms)

---

## 7) Criteri di accettazione (per la consegna)
- KB: ogni `KB_*.md` contiene tabelle numeriche obbligatorie o rimanda esplicitamente alla fonte; corrispondente `config/kb/*.json` esiste e passa validazione.  
- Engine: selezionando `project_model.normativa_attiva` == `RD2229|DM1996|DM1992` le verifiche chiamano il `CodeModule` corretto e producono `VerificationResultItem` conforme a `PLAN_OUTPUT_COMUNE`.  
- GUI: norma selezionabile, elenco checks aggiornato per la norma selezionata; comparazione normativa possibile.  
- Test: 1 unit test per ogni golden case + 1 integration test che esegue confronti RD2229 ↔ DM96 ↔ NTC2018 sullo stesso modello.  
- No `TODO` token rimanenti in `docs/MEGAPLAN/*` (salvo eccezioni approvate).

---

## 8) Rischi principali & mitigazioni
- Rischio: inconsistenze tra KB MD e KB JSON → mitigare con test automatici di coerenza (MD→JSON mapping check).  
- Rischio: norme storiche mancano di esempi numerici → mitigare creando “golden examples” riconciliabili (documentare sorgente).  
- Rischio: breaking change nella GUI/engine → mantenere shims e feature‑toggle per rollout graduale.

---

## 9) Checklist rapida (uso operativo)
- [ ] Aggiornare KB_RD2229_1939.md con tabelle numeriche (σ_adm, materiali)  
- [ ] Creare `config/kb/rd2229.json` (machine KB)  
- [ ] Implementare `src/core_calculus/kb_loader.py` + tests  
- [ ] Esporre `CodeModule` per `RD2229/DM96/DM92` (adapters)  
- [ ] Wire `VerificationFactory` e `VerificationEngine` per multi‑norma  
- [ ] Aggiornare GUI norm selector + tests  
- [ ] Migrare/adapter rd2229 stubs → KB‑driven checks  
- [ ] Add integration tests + CI KB‑scan

---

## 10) Prossimi step raccomandati (scegliere 1)
- A — Comincio formalmente l’elenco di aggiornamenti KB MD (KB_RD2229_1939.md, KB_DM_1996_TA.md, KB_DM_1992_TA.md) con le tabelle numericamente richieste (PLAN‑ONLY).  
- B — Preparo gli schemi JSON per la Knowledge Base (`config/kb/*.json`) e lo schema JSON‑validator (PLAN‑ONLY).  
- C — Formalizzo la API `CodeModule` contract e la `VerificationFactory` (PLAN‑ONLY) mapping per RD2229/DM96/DM92.

Quale preferisci che produca ora (tutti PLAN‑ONLY): A, B o C?

User: questo è un altro elenco di file utili, Produci PLAN-A-B-C

GitHub Copilot: Status: ricevuto — fornisco tre piani esecutivi (PLAN‑A, PLAN‑B, PLAN‑C). Ognuno è indipendente ma ordinato (A → B → C). Tutto PLAN‑ONLY, senza codice.  

---

## PLAN‑A — KB MD: completare le Knowledge Base storiche e NTC (chiusura TODO‑A / TODO‑B)
TL;DR — Riempire i file KB con le tabelle numeriche e gli esempi mancanti (RD2229, DM92, DM96, SLE w_max per NTC), allegare sorgenti in `docs/MEGAPLAN/sources/` e rimuovere i TODO testuali dai MD.

Steps
1. Identificare gap e location nei file KB (audit): aggiornare KB_RD2229_1939.md, KB_DM_1992_TA.md, KB_DM_1996_TA.md, `KB_NTC2018*.md`.
2. Raccogliere fonti italiane disponibili (DM, Circolare NTC, RD2229) e salvare estratti in `docs/MEGAPLAN/sources/` (PDF o scansione).
3. Aggiungere tabelle normative in ciascun KB:
   - RD2229 / DM92 / DM96: tabelle valori ammissibili (σ_c_adm, σ_s_adm, classi materiali usate nel repo).
   - NTC / SLE: tabella w_max (valori provvisori 0.2–0.3 mm già consentiti come default, marcabili come modificabili).
4. Inserire 1–2 worked examples per KB (numerici tracciabili) e link di riferimento.
5. Rimuovere/convertire i token `TODO` in entrate KB o, se non disponibile, lasciare `TODO` con azione chiarissima (es. “attach ETA for anchor X”).

Files to update/create
- Update: KB_RD2229_1939.md, KB_DM_1992_TA.md, KB_DM_1996_TA.md, KB_NTC2018.md (e sezioni correlate)
- Create: `docs/MEGAPLAN/sources/` (placeholders per PDF/estratti)
- Update: `docs/MEGAPLAN/TEST_PLAN_NTC2018.md` (aggiungi golden examples riferiti alle KB)

Verification
- MD lint OK; nessun `TODO` non giustificato rimane nei file KB.
- Per ogni nuova tabella, aggiungere una riga di test che verifica la presenza della chiave corrispondente nel JSON KB (Plan‑B).
Acceptance
- KB MD contiene tabelle numeriche + fonte in `sources/` per ogni voce aggiunta.

Estimate: 1–2 working days (ricerca + aggiornamento SPEC).

---

## PLAN‑B — Machine KB: schema JSON + loader (chiusura TODO‑A → abilita runtime)
TL;DR — Modellare e serializzare le KB in JSON (`config/kb/*.json`), creare loader/validator e test di coerenza MD↔JSON.

Steps
1. Definire schema JSON obbligatorio (schema fields): `material_classes`, `allowable_stresses`, `w_max_by_class`, `anchors_defaults`, `norm_references`, `applicability_limits`.
2. Implementare i file KB machine:
   - `config/kb/rd2229.json`
   - `config/kb/dm1996.json`
   - `config/kb/dm1992.json`
   - (eventuale `config/kb/ntc2018_overrides.json` per w_max defaults)
3. Implementare loader/validator API (documentarlo) — consumer: `VerificationEngine` / CodeModules.
4. Add unit tests:
   - `tests/kb/test_kb_loader.py` — schema validation and MD↔JSON consistency.
   - `tests/kb/test_kb_values_exist.py` — ensure `allowable_stresses` keys exist for classes used in material_sources.py.
5. Wire minimal runtime read-only access (read‑only KB) — no logic change to calculation modules yet.

Files to create
- `config/kb/rd2229.json`, `config/kb/dm1996.json`, `config/kb/dm1992.json`
- Doc: `docs/MEGAPLAN/K B_JSON_SCHEMA.md` (describe JSON fields)
- Tests: `tests/kb/*`
- (Plan‑only) API spec: `docs/MEGAPLAN/K B_LOADER_CONTRACT.md`

Verification
- Loader returns expected numeric values for sample queries.
- MD ↔ JSON consistency: tests confirm every MD table row has corresponding JSON key.

Dependencies
- Requires PLAN‑A completed (MD authoritative content → JSON source).
Acceptance
- KB JSON files validate against schema; loader unit tests green.

Estimate: 1–2 working days (schema design + JSON authoring + tests).

---

## PLAN‑C — CodeModule contract & VerificationFactory (chiusura TODO‑C / integrazione multi‑norma)
TL;DR — Definire il contratto `CodeModule` (API + output schema per `VerificationResultItem`), implementare `VerificationFactory` registry e creare adapter skeleton per `RD2229/DM96/DM92` che leggono la KB JSON; aggiornare l’engine per selezione norma.

Steps
1. SPEC: scrivere `CodeModule_CONTRACT.md` (metodi pubblici, error codes, `VerificationResultItem` exact fields per `PLAN_OUTPUT_COMUNE.md`).
2. Implementazione architettonica (skeletons, plan‑only list):
   - New packages: `src/codes/rd2229/`, `src/codes/dm1996/`, `src/codes/dm1992/` (each implements contract).
   - `src/core_calculus/core/verification_factories.py` — register factories per norma.
   - Update `VerificationEngine` binding: select `VerificationFactory` by `project_model.normativa_attiva` (no change to GUI API).
3. Migrate existing TA stubs:
   - Replace tensioni_ammissibili.py usage with `src/codes/rd2229/code_module.py` adapter that reads KB JSON values.
4. Tests:
   - `tests/codes/test_code_module_contract.py` — verifies conformance to `CodeModule_CONTRACT.md`.
   - `tests/integration/test_norm_switching.py` — same model verified under `NTC2018` and `RD2229` yields `VerificationResultItem` with differing `norm_references`.
5. GUI integration:
   - Ensure `gui/views/selezione_normativa.py` sets `project_model.normativa_attiva` and `VerificationEngineBinding` routes to correct factory per `GUI_SELEZIONE_NORMATIVA.md`.

Files to create/modify
- Create: `docs/MEGAPLAN/CodeModule_CONTRACT.md`
- Create skeletons: `src/codes/rd2229/code_module.py`, `src/codes/dm1996/code_module.py`, `src/codes/dm1992/code_module.py`
- Create: `src/core_calculus/core/verification_factories.py`
- Modify: verification_engine.py (factory selection), tensioni_ammissibili.py (delegate/remove stub)
- Tests: `tests/*` as above

Verification
- Engine can run a `CodeModule` check for `RD2229` and return a `VerificationResultItem` that:
  - contains `norma: 'RD2229'`
  - contains `norm_references` pointing to KB_RD2229_1939.md
  - conforms to `PLAN_OUTPUT_COMUNE.md`
- Integration test comparing results NTC2018 vs RD2229 executes and returns deterministic items.

Decisions
- CodeModule contract enforces single output schema (per `PLAN_OUTPUT_COMUNE.md`).
- Existing verification implementations remain unchanged until adapters are available (shim strategy).

Estimate: 3–5 working days (spec + skeletons + tests + wiring).

---

## Sequenza obbligatoria (priorità)
1. PLAN‑A (KB MD updates) — authoritative source for all downstream work  
2. PLAN‑B (KB JSON + loader) — enable runtime consumption of KB  
3. PLAN‑C (CodeModule + factory) — integrate norms into engine & GUI

---

## Final checklist (pre‑PR)
- [ ] `docs/MEGAPLAN/KB_*.md` updated (no TODOs except approved exceptions)  
- [ ] `config/kb/*.json` created and validated by tests  
- [ ] `CodeModule_CONTRACT.md` reviewed and accepted  
- [ ] Engine factory wiring and CodeModule adapters tested (unit + integration)  
- [ ] GUI normative selector + results mapping verified end‑to‑end

---

Vuoi che formalizzi ora (PLAN‑ONLY) il contenuto di uno dei seguenti artefatti prima di iniziare l'implementazione?  
- A1: blocco tabellare pronto da incollare per KB_RD2229_1939.md (valori ammissibili)  
- B1: JSON‑schema proposto per `config/kb/*.json`  
- C1: `CodeModule_CONTRACT.md` (firma API + response schema)

Seleziona A1, B1 o C1.

User: tutti e tre, A1, B1, C1. voglio gui grafiche professionali in python

GitHub Copilot: Leggere [](file:///c%3A/workspaces/RD2229/RD2229/historical_materials.py#1-1), righe da 1 a 520

Ricerca di file corrispondenti `**/config/historical_materials/DM92.jsoncode`, 1 corrispondenza

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/config/historical_materials/DM92.jsoncode)

Status: ricevuto — fornisco i tre artefatti richiesti (A1, B1, C1) e linee guida per GUI professionale in Python. Tutto PLAN‑ONLY; pronto da incollare nei file indicati.

---

## A1 — KB block per KB_RD2229_1939.md (tabella pronta da incollare) ✅
Inserisci questo blocco nella sezione “Prescrizioni di calcolo” / tabelle del file KB_RD2229_1939.md.

### Tabella: proprietà storiche RD2229 (unità: kg/cm² o come indicato)
| Classe / id | σ_c,28 (kg/cm²) | σ_c (tensione ammissibile, kg/cm²) | E_c (kg/cm²) | τ_c0 (servizio) | τ_c1 (max) | γ_c (≈ fck/σ_c) |
|-------------:|:---------------:|:-----------------------------------:|:------------:|:---------------:|:----------:|:---------------:|
| RD2229_CLS_120_N | 120.0 | 35.0 | 250000 | 4.0 | 14.0 | 3.0 |
| RD2229_CLS_160_N | 160.0 | 35.0 | 250000 | 4.0 | 14.0 | 3.0 |
| RD2229_CLS_160_AR | 160.0 | 45.0 | 300000 | 6.0 | 16.0 | 3.0 |
| RD2229_CLS_225_AR | 225.0 | 50.0 | 300000 | 6.0 | 16.0 | 3.0 |
| RD2229_CLS_160_AL | 160.0 | 45.0 | 330000 | 6.0 | 16.0 | 3.0 |
| RD2229_CLS_120_LP | 120.0 | 35.0 | 200000 | 6.0 | 16.0 | 3.0 |

Nota per lo SPEC:
- Queste voci provengono dall’implementazione storica presente in historical_materials.py (fonte RD2229 nel repo).  
- Aggiungi riferimento testuale: “Valori storici ricavati da historical_materials.py (RD2229 examples) — verificare con documento originale se necessario.”

TODO (KB_RD2229): inserire la citazione documento ufficiale RD2229/39 o scansione in `docs/MEGAPLAN/sources/`.

---

## B1 — JSON‑schema proposto per `config/kb/*.json` (machine KB) 🔧
File target: `config/kb/rd2229.json`, `config/kb/dm1996.json`, `config/kb/dm1992.json`

Schema (alto livello — da trasformare in JSON‑Schema formale):
- root: object
  - meta: { code_name: string, description: string, standard_reference: string, unit_system: string }
  - material_classes: object (key = class id) → object {
      name: string,
      fck: number (MPa or historic unit),
      fcd: number,
      Ec: number,
      fctm?: number,
      tau_c0?: number,
      tau_c1?: number,
      n_homog?: number,
      notes?: string
    }
  - allowable_stresses: object { material_type: { sigma_c_adm: number, sigma_s_adm: number } }
  - w_max_by_service_class: object { service_class: { w_max_mm: number, reference: string } }
  - anchors_defaults: object { anchor_type: { eta_ref?: string, design_notes?: string } }
  - norm_references: array of { norm: string, clause: string, href?: string }
  - conversion_factors: { MPa_to_kg_cm2: number, kg_cm2_to_MPa: number }
  - applicability_limits: object { min_d_mm?: number, min_rho_l?: number, max_slenderness?: number }
  - examples: array of { id: string, input: object, expected: object, reference: string }

Snippet di esempio (da inserire in `config/kb/rd2229.json`):
```json
{
  "meta": { "code_name": "RD2229", "unit_system": "historical (kg/cm2)" },
  "material_classes": {
    "RD2229_CLS_160_N": { "name": "CLS R160", "fck": 160.0, "fcd": 35.0, "Ec": 250000 }
  },
  "w_max_by_service_class": {
    "normal": { "w_max_mm": 0.2, "reference": "DM96 (placeholder)" }
  },
  "norm_references": [
    { "norm": "RD2229", "clause": "varie", "href": "" }
  ]
}
```
Acceptance rules:
- Every MD KB entry must have a corresponding JSON key (testable).
- `applicability_limits` must include the minimal gating values used by checks (e.g. `min_d_mm`, `min_rho_l`).

TODO (B1): finalizzare JSON Schema formale (Draft‑07) e creare `src/core_calculus/kb_loader.py` che valida i file.

---

## C1 — `CodeModule_CONTRACT.md` (API contract + response schema) — pronto da incollare 📜

### Scopo
Definire il contratto obbligatorio che ogni `CodeModule` (norma) deve esporre per essere utilizzato dal `VerificationEngine` e dalla GUI.

### API pubbliche (metodi obbligatori)
- `available_checks() -> list[str]`  
  - Restituisce gli `check_id` disponibili per il modulo (es. `RC_SLU_VRDc_NoStirrups`, `RC_SLE_Cracking_NoStirrups`, `secondary_cantilever_moment`).

- `available_secondary_types() -> list[str]` (opzionale per moduli che gestiscono elementi secondari)

- `list_templates() -> list[TemplateSummary]`  
  - Ritorna templates/ presets (id, name, description).

- `validate_input(check_id: str, input_payload: dict) -> ValidationResult`  
  - Controlli di formato/completezza/units/applicability; non esegue il calcolo.

- `run_check(check_id: str, input_payload: dict) -> VerificationResultItem`  
  - Esegue il check (sincrono/async) e ritorna risultato conforme allo schema sotto.

- `get_norm_references(check_id: str) -> list[NormReference]`  
  - Lista di riferimenti normativi usati per quel check.

### Input payload (shape richiesto)
- Deve aderire a `BaseElementSpec` / `SecondaryElementSpec` (vedi `PLAN_INPUT_COMUNE.md` / `SPEC_SecondaryElementSpec.md`).
- Un esempio minimo per `run_check`:
  - `{ "element_id": "E1", "type": "CANTILEVER", "geometry": {...}, "material": {"code":"C25_30"}, "loads": {...}, "metadata": {"norm":"NTC2018"} }`

### VerificationResultItem (unico schema di output — conforme a `PLAN_OUTPUT_COMUNE.md`)
- `check_id`: string
- `element_id`: string
- `norma`: string (es. `NTC2018`, `RD2229`)
- `stato_limite`: string (e.g. `SLU`, `SLE`)
- `esito`: enum {`OK`, `NOT_OK`, `NOT_APPLICABLE`, `ERROR`, `WARNING`}
- `utilisation`: number | null  (0..∞; domanda/capacità)
- `combinazione_critica`: string | null
- `domanda`: object (named numeric results, e.g. { "V_Ed": 60.0 })
- `capacita`: object (named numeric resistances, e.g. { "V_Rd_c": 96.0 })
- `norm_references`: array of { norm: string, clause: string, text_snippet?: string, href?: string }
- `steps`: array of { step_id: string, description: string, value?: number } — passo‑per‑passo (test‑friendly)
- `messages`: array of { level: string, code?: string, text: string }
- `metadata`: { calculation_code_version: string, timestamp: ISO8601 }

### Error / validation codes (standard)
- `ERR_INVALID_INPUT` — input schema non valido
- `ERR_OUT_OF_SCOPE` — `NOT_APPLICABLE` with explanation
- `ERR_MISSING_KB` — required KB entry missing
- `WARN_APPROXIMATION` — conservative approximation used
Include these codes in `messages[]`.

### Example response (contract illustration — plan‑only)
- For `RC_SLU_VRDc_NoStirrups` (example values computed per EC2 with γ_c=1.5):
```json
{
  "check_id":"RC_SLU_VRDc_NoStirrups",
  "element_id":"B1",
  "norma":"NTC2018",
  "stato_limite":"SLU",
  "esito":"OK",
  "utilisation":0.625,
  "combinazione_critica":"SLU_RARA",
  "domanda":{"V_Ed_kN":60.0},
  "capacita":{"V_Rd_c_kN":96.0},
  "norm_references":[{"norm":"EN1992-1-1","clause":"6.2","href":"[ref]"}],
  "steps":[{"step_id":"vrdc_calc","description":"Compute v_rd,c per EC2 (k=..., ρ_l=...)", "value":96.0}],
  "messages":[{"level":"info","code":"OK","text":"V_Ed <= V_Rd,c"}],
  "metadata":{"calculation_code_version":"NTC2018-v1","timestamp":"2026-02-15T10:00:00Z"}
}
```

### Contract rules / expectations
- **Idempotence**: same input → same output (deterministic); stateful external calls must be avoided.
- **Traceability**: every numeric result must reference `norm_references` (clause or KB entry).
- **Applicability gating**: checks must return `NOT_APPLICABLE` (with reason) when input out of KB limits.
- **No GUI logic**: modules MUST NOT implement UI behaviors or formatting.
- **Unit / regression tests**: each `check_id` must include at least 3 golden examples (PASS/FAIL/NOT_APPLICABLE).

### Testing contract (required tests for each CodeModule)
- `test_available_checks_present()`  
- `test_validate_input_rejects_bad_schema()`  
- `test_run_check_golden_cases()` (3 fixtures)  
- `test_norm_references_included()`

---

## GUI: linee guida per interfacce professionali in Python (sintesi operativa)
- Framework consigliato per MVP (coerente con progetto): **Tkinter + ttk + ttkbootstrap** (compatibilità + look moderno).  
- Per UI “professionale” alternativa: **PySide6/Qt** se serve look enterprise o layout complessi.
- Componenti chiave da realizzare in `src/gui/widgets/`:
  - `utilisation_bar.py` (colore, tooltip, percentuale)  
  - `verification_treeview.py` (selezione, checkbox per report)  
  - `result_details_pane.py` (steps, norms, export buttons)  
  - `secondary_element_editor.py` (schema‑driven form)  
  - `theme.py` (palette aziendale, contrasto, accessible font sizes)
- Visual design:
  - Status color: green ≤0.8, amber 0.8–1.0, red >1.0  
  - Use compact dashboards: list + detail pane + mini plot  
  - Include export (Markdown/PDF) and copyable normative references
- Long‑running checks: run in background thread / asyncio; show progress bar + cancel.
- Plots: `matplotlib` (static) or `plotly` (interactive) embedded.
- Files to add (plan‑only):  
  - `src/gui/theme.py`, `src/gui/widgets/utilisation_bar.py`, `src/gui/widgets/result_plot.py`, `app/ui/secondary_element_window.py`
- Accessibility & UX:
  - Keyboard shortcuts, clear labels, colorblind‑friendly palette, ARIA‑like tooltips.
- Wireframe artefact: add `docs/MEGAPLAN/GUI_WIREFRAMES.md` with mockups and component mapping.

---

## Next actions & owners (immediato)
- You / Standards owner: approve and copy the KB table (A1) into KB_RD2229_1939.md.  
- Dev / Data engineer: create `config/kb/*.json` per B1 and implement `kb_loader` tests.  
- Architect / Lead dev: accept `CodeModule_CONTRACT.md` and scaffold `src/codes/*` adapters (C1).  
- UI lead: pick theme approach (ttkbootstrap or PySide6) and add `GUI_WIREFRAMES.md`.

---

Vuoi che generi ora i file MD completi per:
- KB_RD2229_1939.md (A1 inserito + nota),  
- `docs/MEGAPLAN/K B_JSON_SCHEMA.md` (B1 formale),  
- `docs/MEGAPLAN/CodeModule_CONTRACT.md` (C1 formale) — tutti PLAN‑ONLY e pronti per review?

User: proponimi domande per tutti gli aspetti che vuoi chiarire. ti fornisco contesto utile per RD2229 e NTC2018

GitHub Copilot: 4 domande poste (Norme, Costanti, Ancoraggi, GUI)

Perfetto — grazie per le risposte. Procedo con le attività successive basate sulle tue scelte (PLAN‑ONLY).  

Prossimi passi che preparo subito (scegliendo l'ordine consigliato):
1. Genero i file SPEC completi aggiornati usando le fonti pubbliche e i defaults concordati (gamma_c=1.5, gamma_s=1.15, w_max 0.2–0.3 mm) — includerò note “configurabile in GUI”.  
2. Produco il JSON‑schema e un esempio `config/kb/rd2229.json` + loader contract (plan‑only).  
3. Redigo il `CodeModule_CONTRACT.md` definitivo e lo appendo ai piani di test.  
4. Creo il wireframe/UI spec per Tkinter + ttkbootstrap (componenti, stili, comportamenti asincroni).

Dimmi quale vuoi che prepari per primo tra questi 4 (1–4).

User: considera che in futuro saranno implementati moduli anche per il calcolo di telai con il metodo di cross secondo Pozzati e le verifiche in caso di incendio

GitHub Copilot: Breve aggiornamento: ho alcune domande mirate per definire requisiti e priorità del Metodo di Cross (Pozzati) e del modulo incendio prima di aggiornare il piano dettagliato. Rispondi alle opzioni — posso adattare la progettazione in base alle tue scelte.

User: @agent Riprova

GitHub Copilot: 4 domande poste (Cross-level, Pozzati ref, Fire MVP, Benchmarks)

Ottimo — ho le informazioni necessarie. Procedo a integrare il piano per il Metodo di Cross (implementazione production‑level) e il modulo incendio (MVP L1+L2), usando esempi presenti nel repo e riferimenti pubblici.  

Prossimo: aggiorno PLAN dettagliato per Cross + Fire (tasks, file, test, dipendenze). Vuoi che inizi con il piano del Metodo di Cross o con il piano del modulo incendio?

User: considera che sotto MEGAPLAN hai molti riferimenti utili per valutare la forma finale del progetto. In particolare devono essere ben funzionanti le gui grafiche per inserimento dati, impostazione del calcolo, verifica, report. Aggiorna il plan in questa unica sessione, senza mai uscire dalla singola sessione di plan

GitHub Copilot: 

User: @agent Riprova

GitHub Copilot: Review MEGAPLAN docs for plan update

Ricerca di file corrispondenti `**/PLAN_*.md`, 11 corrispondenze

Ricerca di file corrispondenti `**/GUI_*.md`, 8 corrispondenze

Ricerca di file corrispondenti `**/FIRE_*.md`, 38 corrispondenze

Ricerca di file corrispondenti `**/KB_*.md`, 9 corrispondenze

Ricerca di file corrispondenti `**/MEGAPLAN/**/*.md`, 84 corrispondenze

Ricerca di file corrispondenti `**/PLAN*MASTER*.md`, 3 corrispondenze

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/PLAN_MASTER.md)

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/PLAN_GUI.md)

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/PLAN_INPUT_COMUNE.md)

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/PLAN_OUTPUT_COMUNE.md)

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/PLAN_METODO_CROSS_TELAI_PIANI.md)

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/PLAN_INCENDIO_MASTER_REVISIONE_2026_Q1.md)

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/FIRE_MASTER.md)

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/FIRE_NEXT_STEPS_ROADMAP.md)

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/GUI_MAIN_PY_NAVIGAZIONE.md)

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/GUI_SELEZIONE_NORMATIVA.md)

Leggere [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/GUI_SEZIONI_MATERIALI_VIEW_CODICE.md#1-1), righe da 1 a 240

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/GUI_SOLLECITAZIONI_VIEW_CODICE.md)

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/GUI_SELEZIONE_VERIFICHE_RISULTATI.md)

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/GUI_RISULTATI_VIEW_CODICE.md)

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/GUI_RISULTATI_TO_RELAZIONE_BINDING.md)

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/GUI_VERIFICATION_ENGINE_BINDING.md)

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/FIRE_CODEMODULE_INCENDIO.md)

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/FIRE_INTEGRAZIONE_SOFTWARE.md)

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/FIRE_INTEGRAZIONE_L3_IN_CODEMODULE.md)

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/FIRE_GATE_RILASCIO_L3_FEM.md)

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/FIRE_CHECKLIST_VALIDAZIONE_L3_FEM.md)

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/FIRE_CHECKLIST_TECNICO_LEGALE.md)

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/FIRE_PROGRAMMA_FUTURO_L3_FEM.md)

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/FIRE_PROTOTIPO_LE_MINIMALE.md)

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/FIRE_SOLVER_L3_FEM_CODICE.md)

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/FIRE_VERIFICA_TRAVI_A_CALDO.md)

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/PLAN_KNOWLEDGE_BASE_NORMATIVA_MASTER.md)

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/KB_NTC2018.md)

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/KB_NTC2018_ANALISI.md)

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/KB_NTC2018_AZIONI.md)

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/KB_NTC2018_CA.md)

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/KB_NTC2018_SISMICA.md)

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/KB_NTC2018_ESISTENTI.md)

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/KB_DM_1992_TA.md)

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/KB_DM_1996_TA.md)

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/KB_RD2229_1939.md)

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/FIRE_CODEMODULE_INCENDIO.md)

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/FIRE_PROTOTIPO_LE_MINIMALE.md)

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/FIRE_SOLVER_L3_FEM_CODICE.md)

Status: aggiorno il piano nella stessa sessione Plan, includendo GUI grafiche complete per input/impostazione/verifica/report, e predisposizioni future per Metodo di Cross (Pozzati) e Incendio, usando i MEGAPLAN come vincoli unici.  

## Plan: Aggiornamento Unificato (GUI + RD2229/DM92/DM96 + Cross + Fire)

Obiettivo: consolidare un’architettura modulare multi‑norma con GUI professionale e coerente, mantenendo KB come fonte unica, un input schema unico e output schema unico (`VerificationResultItem`), e predisponendo i moduli futuri (Cross e Incendio) senza contaminazioni normative.

**Sintesi**
- GUI unica e professionale: flusso completo “Norma → Metodo Analisi → Input → Verifica → Risultati → Report”.
- Core multi‑norma: `CodeModule` + `VerificationFactory` per NTC2018, RD2229, DM92, DM96; KB come sorgente normativa unica.
- Moduli futuri: Metodo di Cross (Pozzati) e Incendio (L1+L2) già previsti in architettura, con punti di integrazione espliciti nel ProjectModel, binding, GUI e output/report.
- Nessuna formula nei PLAN: solo riferimenti KB e placeholder dove necessario.

---

### **Steps**
1. **Allineamento vincoli e conflitti GUI/ProjectModel**  
   - Consolidare il campo unico di normativa attiva nel `ProjectModel` (attualmente `normativa_attiva` vs `normativa_verifica` nei documenti).  
   - Aggiornare i file vincolanti che descrivono il flusso:  
     - PLAN_GUI.md  
     - GUI_SELEZIONE_NORMATIVA.md  
     - GUI_VERIFICATION_ENGINE_BINDING.md  
   - Output: flow unificato e semantica coerente in tutti i piani GUI.

2. **KB completezza e mapping multi‑norma (RD2229/DM92/DM96)**  
   - Consolidare KB storiche con tabelle numeriche e riferimenti minimi (nessun numero fuori KB).  
   - Creare mapping normativo per risultati in output (`norma`, `norm_references`).
   - File chiave:  
     - KB_RD2229_1939.md  
     - KB_DM_1992_TA.md  
     - KB_DM_1996_TA.md  
     - PLAN_KNOWLEDGE_BASE_NORMATIVA_MASTER.md

3. **GUI professionale unica (Input/Setup/Verifica/Report)**  
   - Unificare workflow in GUI:  
     1) Selezione normativa  
     2) Metodo di analisi (Cross/FEM future)  
     3) Input sezioni/materiali/sollecitazioni  
     4) Setup calcolo (combinazioni/ambito)  
     5) Esecuzione verifiche  
     6) Risultati + selezione per report  
   - File vincolanti:  
     - GUI_MAIN_PY_NAVIGAZIONE.md  
     - GUI_SEZIONI_MATERIALI_VIEW_CODICE.md  
     - GUI_SOLLECITAZIONI_VIEW_CODICE.md  
     - GUI_RISULTATI_VIEW_CODICE.md  
     - GUI_SELEZIONE_VERIFICHE_RISULTATI.md  
     - GUI_RISULTATI_TO_RELAZIONE_BINDING.md  
   - Nota: preferenza UI stack Tkinter + ttkbootstrap.

4. **Output e Report unificati (multi‑norma)**  
   - Garantire che i report NTC2018 e RD2229 siano alimentati dallo stesso `VerificationResultItem`.  
   - Estendere `RisultatiView` e `ReportBuilder` per includere future voci incendio.  
   - File:  
     - PLAN_OUTPUT_COMUNE.md  
     - RELAZIONE_DI_CALCOLO_NTC2018_TEMPLATE_OPERATIVO.md  
     - RELAZIONE_RD2229_TEMPLATE.md

5. **Integrazione Metodo di Cross (Pozzati) – predisposizione**  
   - Inserire nella GUI un passo dedicato “Metodo di analisi” (Cross).  
   - Il metodo deve produrre effetti interni norm‑agnostic e inviarli ai CodeModule.  
   - File vincolanti:  
     - PLAN_METODO_CROSS_TELAI_PIANI.md  
     - PLAN_INTEGRAZIONE_METODI_NORME.md

6. **Modulo Incendio (L1+L2) – predisposizione**  
   - Inserire nella GUI: selezione “verifica incendio”, classe R, metodo L1/L2.  
   - Output esteso con campi `fire_time_achieved`, `fire_method`, `fire_class_required`.  
   - File vincolanti:  
     - FIRE_MASTER.md  
     - FIRE_NEXT_STEPS_ROADMAP.md  
     - FIRE_INTEGRAZIONE_SOFTWARE.md  
     - FIRE_NORMATIVA_NTC.md  
     - FIRE_NORMATIVA_EC.md

7. **Binding e Factory multi‑norma**  
   - Estendere la selezione normativa in GUI per includere RD2229/DM92/DM96 (senza duplicazione di flusso).  
   - CodeModule + VerificationFactory per RD2229/DM92/DM96 e mappatura corretta in `VerificationEngineBinding`.  
   - File vincolanti:  
     - INTEGRAZIONE_RD2229_GUI_CORE_RELAZIONE.md  
     - VERIFICATION_FACTORY_RD2229.md  
     - VERIFICHE_RD2229.md

---

### **Verification**
- Verificare consistenza campo norma attiva in tutti i file GUI + binding.  
- Verificare che `VerificationResultItem` sia l’unica fonte per report e GUI risultati.  
- Verificare che GUI non contenga formule o decisioni normative.  
- Verificare che `CodeModule` e KB siano l’unica fonte di limiti numerici.

---

### **Decisions (registrate)**
- GUI professionale: Tkinter + ttkbootstrap.  
- Metodo di Cross: implementazione production‑level secondo Pozzati (norm‑agnostic).  
- Incendio: MVP L1+L2 (tabellare + sezione efficace).  
- KB unica fonte normativa; numeri solo in KB.

---

## Prossimi step operativi (scegliere ordine di lavoro)
1. Aggiornare i file GUI vincolanti (workflow completo con norma/metodo analisi/incendio).  
2. Allineare `ProjectModel` e `VerificationEngineBinding` (campo norma unica).  
3. Consolidare KB storiche (RD2229/DM92/DM96) con tabelle e riferimenti.  
4. Inserire predisposizioni Cross e Incendio nella GUI e nei report.

Vuoi che proceda con il dettaglio **1) GUI workflow completo** oppure con **3) KB storiche**?

User: va bene l'ordine indicato, continua il plan

GitHub Copilot: Perfetto, continuo il plan secondo l’ordine concordato (1→4). Di seguito trovi il dettaglio operativo per ciascun blocco, con file coinvolti, dipendenze e criteri di accettazione.

**Plan Continuation — Dettaglio Esecutivo (Step 1–4)**

- **Step 1 — GUI workflow completo (norma → metodo → input → verifica → risultati → report)**  
  - **Obiettivo:** unificare in GUI tutti i passaggi, includendo selezione normativa, selezione metodo di analisi (Cross/FEM), input, verifiche, risultati e report.  
  - **File da aggiornare**  
    - PLAN_GUI.md — inserire il workflow completo e le regole di gating  
    - GUI_MAIN_PY_NAVIGAZIONE.md — riflettere l’ordine delle View  
    - GUI_SELEZIONE_NORMATIVA.md — includere DM92/DM96 oltre RD2229/NTC2018  
    - GUI_VERIFICATION_ENGINE_BINDING.md — routing in base a normativa attiva + metodo analisi  
    - GUI_RISULTATI_VIEW_CODICE.md — supporto multi‑norma e incendio  
    - GUI_RISULTATI_TO_RELAZIONE_BINDING.md — report per NTC2018/RD2229 + incendio  
  - **Dipendenze:** PLAN_INPUT_COMUNE e PLAN_OUTPUT_COMUNE devono rimanere invarianti come schemi unici.  
  - **Criteri di accettazione:** GUI mostra flusso completo senza duplicare view, con selezione norma e metodo, e con risultati/report sempre derivati da `VerificationResultItem`.

- **Step 2 — Allineamento ProjectModel + binding (norma unica + metodo analisi)**  
  - **Obiettivo:** eliminare ambiguità tra `normativa_attiva` e `normativa_verifica`, e introdurre un campo unificato per il metodo di analisi (Cross).  
  - **File da aggiornare**  
    - GUI_SELEZIONE_NORMATIVA.md  
    - GUI_VERIFICATION_ENGINE_BINDING.md  
    - INTEGRAZIONE_RD2229_GUI_CORE_RELAZIONE.md  
    - PLAN_INPUT_COMUNE.md  
  - **Dipendenze:** nessuna modifica al core, solo vincoli di progetto e binding.  
  - **Criteri di accettazione:** un unico attributo di normativa attiva e un campo di metodo analisi in `ProjectModel`, usati in binding e report.

- **Step 3 — Consolidamento KB storiche (RD2229/DM92/DM96) + mappatura output**  
  - **Obiettivo:** completare le KB con valori numerici e riferimenti, garantire che ogni verifica TA legga unicamente dalla KB.  
  - **File da aggiornare**  
    - KB_RD2229_1939.md  
    - KB_DM_1992_TA.md  
    - KB_DM_1996_TA.md  
    - PLAN_KNOWLEDGE_BASE_NORMATIVA_MASTER.md  
    - PLAN_OUTPUT_COMUNE.md — assicurare `norm_references` per ogni risultato  
  - **Dipendenze:** Step 2 (norma attiva unificata).  
  - **Criteri di accettazione:** nessun valore numerico TA fuori dalle KB; ogni verifica riporta `norm_references` puntuali.

- **Step 4 — Predisposizione Cross + Incendio in GUI e output**  
  - **Obiettivo:** introdurre i punti di integrazione per il Metodo di Cross e per il modulo incendio (L1+L2) senza contaminare il core normativo.  
  - **File da aggiornare**  
    - PLAN_METODO_CROSS_TELAI_PIANI.md  
    - PLAN_INTEGRAZIONE_METODI_NORME.md  
    - FIRE_MASTER.md  
    - FIRE_NEXT_STEPS_ROADMAP.md  
    - FIRE_INTEGRAZIONE_SOFTWARE.md  
  - **Dipendenze:** Step 1 (GUI workflow completo).  
  - **Criteri di accettazione:** GUI consente selezione metodo analisi e abilita input incendio; output include campi incendio senza alterare schema base.

---

## TODO residui (espliciti, con chiusura prevista)
- Uniformare campo normativa attiva tra GUI e ProjectModel (Step 2).  
- Inserire valori tabellari storici nelle KB (Step 3).  
- Inserire riferimenti incendio in output/report (Step 4).  
- Aggiungere `KB_EUROCODICI.md` se richiesto dal master KB (da validare con te).

---

## Prossimi passi immediati (ordine 1→4 già confermato)
1) Aggiornare PLAN_GUI e GUI workflow (Step 1).  
2) Allineare ProjectModel e Binding (Step 2).  
3) Consolidare KB TA storiche (Step 3).  
4) Predisporre Cross + Incendio in GUI/Output (Step 4).

Se vuoi, preparo subito il dettaglio operativo **Step 1** con elenco puntuale di modifiche a PLAN_GUI.md e GUI_MAIN_PY_NAVIGAZIONE.md.

User: Fermati allo STEP 1.

Formalizza SOLO lo STEP 1:
“GUI workflow completo (norma → metodo → input → verifica → risultati → report)”.

Limiti vincolanti:
- Nessuna anticipazione di Step 2, 3 o 4.
- Nessuna modifica concettuale a ProjectModel o core.
- Aggiorna SOLO i file di GUI e workflow indicati per Step 1.
- Riporta le modifiche file‑per‑file con criteri di accettazione.

Rimani nella stessa sessione di PLAN.
Non passare ad Agent o Edit.

GitHub Copilot: Status: formalizzo SOLO lo STEP 1 — “GUI workflow completo (norma → metodo → input → verifica → risultati → report)”. Di seguito trovi le modifiche file‑per‑file, i requisiti UX/validation, i test richiesti e i criteri di accettazione. Rimango in modalità Plan; nessuna modifica al ProjectModel o al core.

---

## Sintesi breve ✅
Obiettivo STEP 1 — rendere la GUI un workflow professionale, guidato e bloccante (Norma → Metodo → Input → Verifica → Risultati → Report), mantenendo GUI “thin” (nessuna logica normativa) e senza toccare il core o il ProjectModel. Tutte le nuove regole e i controlli sono documentati nei file GUI indicati.

---

## File → modifiche richieste (solo SPEC, plan‑only)

1) PLAN_GUI.md  
- Aggiungere: flusso canonico dettagliato con gating step‑by‑step, UX rules, widget required list (norm selector, method selector UI, input validators, run button, results table, report preview).  
- Specifica: la selezione “Metodo analisi” è una proprietà GUI **locale** (non modifica ProjectModel/core) fino a integrazione futura.  
- Acceptance: documento descrittivo aggiornato e approvato; wireframe checklist presente.

2) GUI_MAIN_PY_NAVIGAZIONE.md  
- Aggiungere: nuovo sidebar item/sequence order reflecting workflow; ensure "Run verifications" disabled until preconditions met; document spinner/progress expectations and error handling.  
- Acceptance: main navigation shows steps in order and documents precondition gating.

3) GUI_SELEZIONE_NORMATIVA.md  
- Aggiungere: explicit UX that Norma selection is mandatory and is the first gating control; describe visual state (badge showing current Norma); list disabled controls when no Norma selected.  
- Acceptance: normative selector behavior and blocking rules fully specified.

4) GUI_VERIFICATION_ENGINE_BINDING.md  
- Aggiungere: GUI pre‑run checklist (validate inputs, normative selected, method selected UI flag); binding must refuse run request with clear error messages if checklist fails. (NO changes al core API: binding continua a chiamare engine con current ProjectModel.)  
- Acceptance: binding preconditions enumerated; sample error messages provided.

5) GUI_RISULTATI_VIEW_CODICE.md  
- Aggiungere: results table enhancements — filters (by norma, stato limite), utilisation bar visual, checkbox per inclusion in report, detail pane with `VerificationResult.steps[]` + `norm_references[]`.  
- Acceptance: results view presents read‑only data only from `VerificationResultItem` and supports selection for report.

6) GUI_RISULTATI_TO_RELAZIONE_BINDING.md  
- Aggiungere: mapping UI → ReportBuilder (which fields are passed, handling of NOT_APPLICABLE, export behavior). Document that report builder reads only ProjectModel.verifiche_in_relazione (no recalculation).  
- Acceptance: mapping table present; behavior for empty selection and export defined.

---

## Interfaccia utente (wireframe & widgets — descrizione)
- Header: Norma corrente badge + small legend.  
- Stepper (left sidebar or top): 1) Norma → 2) Metodo (UI only) → 3) Input (Sezioni/Materiali) → 4) Impostazioni calcolo/Combinazioni → 5) Esegui Verifiche → 6) Risultati → 7) Report.  
- Key widgets:
  - Norm selector (radio/dropdown) — required  
  - Method selector (dropdown, UI flag only — values: Default / Advanced placeholder)  
  - Input panels: `SezioniMaterialiView`, `SollecitazioniView` (validate on save)  
  - Run button: disabled until validations pass; shows progress + cancel  
  - Results table: sortable, filterable, utilisation bar, checkbox per report inclusion  
  - Report preview: read‑only Markdown viewer + export buttons

---

## Gating rules / validation (GUI only)
- Cannot run verifications unless:
  - Norma is selected (mandatory)  
  - All mandatory input fields validated (per `PLAN_INPUT_COMUNE.md`)  
  - At least one section/material and one load case present  
- GUI must block actions incompatible with selected Norma (e.g., CAP_7 UI disabled if RD2229 selected).  
- Error messages: use standard UX messages (INPUT_INVALID, NOT_APPLICABLE, REQUIRES_GEOTECH, ERROR_INTERNAL).

---

## Test cases (GUI / acceptance) — add to test plan
- GUI‑WF‑001: Attempt to run without Norma → expect error dialog "Selezionare una normativa" and run button disabled.  
- GUI‑WF‑002: Method selector changes only UI state; ProjectModel unchanged.  
- GUI‑WF‑003: Save inputs → inputs validated; Run button enabled.  
- GUI‑WF‑004: Run verifications → spinner shown; results table populated from `ProjectModel.verifiche_*` (read‑only).  
- GUI‑WF‑005: Select results → Export report → verify ReportBuilder uses only selected `verifiche_in_relazione`.  
- GUI‑WF‑006: Results filter by Norma works (NTC2018 vs RD2229 results displayed accordingly).

Each test must assert GUI does not perform calculations itself and that all numeric data in results derive from VerificationResult objects.

---

## UX messages (required in GUI spec)
- Pre‑run block: "Selezionare una normativa" / "Dati di input incompleti: [campo1, campo2]".  
- Run in progress: "Esecuzione verifiche… (cancel per interrompere)".  
- Post‑run success: "Verifiche eseguite correttamente."  
- Post‑run error: "Errore interno — controllare i log."

---

## Criteri di accettazione (file‑by‑file)
- `PLAN_GUI.md`: workflow steps + gating rules added; reviewed and accepted by product owner.  
- `GUI_MAIN_PY_NAVIGAZIONE.md`: navigation updated to reflect workflow order; run button behavior documented.  
- `GUI_SELEZIONE_NORMATIVA.md`: selector behavior and blocking rules documented and consistent with `PLAN_GUI.md`.  
- `GUI_VERIFICATION_ENGINE_BINDING.md`: binding preconditions listed; example error flows included; no ProjectModel/core changes.  
- `GUI_RISULTATI_VIEW_CODICE.md`: results UI enhancements specified; must read-only display `VerificationResultItem`.  
- `GUI_RISULTATI_TO_RELAZIONE_BINDING.md`: report mapping clarified; export workflow described.

Acceptance verification: manual walkthrough + automated GUI tests (see Test cases) must pass; no change to core behavior or ProjectModel semantics.

---

## Deliverables STEP 1 (plan‑only)
- Updated SPEC sections in the six GUI files above (content as described).  
- Wireframe + widget list (documented in `PLAN_GUI.md`).  
- GUI acceptance tests (6 test cases) added to test plan.  
- No code changes, no ProjectModel/core modifications.

---

Next action (I will do if approvato): produce the exact text changes (SPEC blocks) for each GUI file listed so you can paste them into the MD files. Vuoi che generi ora i contenuti da incollare per ogni file (PLAN‑ONLY)?

User: STEP 1 approvato.

Procedi ora a generare SOLO i contenuti PLAN‑ONLY da incollare nei file MD
elencati nello STEP 1 (uno per uno).

Vincoli:
- Rimani nella stessa sessione di PLAN.
- Nessun codice.
- Nessuna anticipazione di Step 2, 3 o 4.
- Ogni file deve contenere SOLO specifiche, regole UX e criteri di accettazione.

Inizia da PLAN_GUI.md.

GitHub Copilot: Status: creo il contenuto PLAN‑ONLY da incollare in PLAN_GUI.md.  
Ho rispettato i vincoli: niente codice, niente anticipazioni su Step 2–4, nessuna modifica concettuale al ProjectModel/core.

## PLAN_GUI.md — GUI workflow completo (Norma → Metodo → Input → Verifica → Risultati → Report)

### Scopo
Definire in modo vincolante il workflow GUI che guida l’utente attraverso: selezione normativa, impostazione del calcolo, inserimento dati, esecuzione delle verifiche, lettura dei risultati e generazione della relazione. La GUI è un orchestratore: non contiene formule né logica normativa.

---

### TL;DR (flusso canonico)
1. Seleziona Norma (obbligatorio)
2. Seleziona Metodo di analisi (UI flag, non modifica il core)
3. Inserisci / assegna Sezione e Materiale
4. Inserisci Sollecitazioni / Combinazioni (validazione automatica)
5. Esegui Verifiche (invoca Binding → VerificationEngine)
6. Consulta Risultati (read‑only) e seleziona per Report
7. Esporta Relazione (Markdown / PDF)

---

### Requisiti vincolanti (hard rules)
- GUI non esegue calcoli: richieste di calcolo inviate al VerificationEngine tramite il binding.  
- Input/Output conformi ai piani `PLAN_INPUT_COMUNE.md` e `PLAN_OUTPUT_COMUNE.md`.  
- Nessuna logica normativa in GUI; tutte le regole normative riferite alla KB.  
- Nessuna scrittura diretta sui risultati: la RisultatiView è sola‑lettura.  
- Operazioni bloccanti: non è possibile eseguire verifiche senza Norma selezionata e input validati.

---

### Validazione & gating (UI‑level)
- Run button abilitato solo se: Norma selezionata AND sezione/materiale assegnati AND almeno una sollecitazione valida.  
- Disabilitazione contestuale: elementi UI incompatibili con la Norma vengono disabilitati (es. CAP_7 non attivabile per RD2229).  
- Pre‑run checklist: validazione sintattica + business rules minime; errori mostrati in modal dialog con lista campi mancanti.

---

### Componenti / Views obbligatorie (responsabilità)
- NormSelector (top/header) — selezione Norma, mostra badge Norma corrente.  
- MethodSelector (UI flag) — scelta metodo analisi **UI only** (non cambia ProjectModel); visual indicator only.  
- SezioniMaterialiView — selezione archivio materiali/sezioni (read‑only properties shown).  
- SollecitazioniView — input N, Mx, My, Tx, Ty, Mz; validation on save.  
- VerificationSettingsView — scelta combinazione, ambito verifica (CAP_4 / CAP_7), advanced options (readonly hints).  
- RunPanel — Run / Cancel, progress indicator, estimated time hint.  
- RisultatiView — tree/table read‑only, utilisation bar, filters (norma / stato limite), detail pane with `steps[]` + `norm_references[]`.  
- ReportView — selection summary, preview Markdown, export buttons.

---

### UX rules (behavioural)
- Status colours: green (util ≤ 0.8), amber (0.8–1.0), red (>1.0).  
- Long‑running tasks: run in background thread; show progress + cancel; results updated on completion.  
- Error handling: friendly modal + copyable log id; non‑blocking warnings shown inline in detail pane.  
- Accessibility: keyboard navigation, high‑contrast palette, ARIA‑style tooltips.  
- Presets & templates: provide sensible defaults (configurable) to minimise manual input.

---

### Messages standard (copy‑ready)
- INPUT_INVALID: "Dati di input mancanti o non validi: [campo1, campo2]"  
- NO_NORMA_SELECTED: "Selezionare una normativa prima di eseguire le verifiche."  
- RUN_IN_PROGRESS: "Esecuzione verifiche… (clicca Annulla per interrompere)"  
- RUN_SUCCESS: "Verifiche eseguite correttamente."  
- RUN_FAILED: "Esecuzione interrotta — controllare i log."  
- NOT_APPLICABLE_NOTICE: "Verifica non applicabile: [motivo]"  

---

### RisultatiView — dettagli UX & data contract
- Mostra esclusivamente dati da `VerificationResultItem`.  
- Colonne minime: verifica, capitolo/norma, stato limite, esito, utilisation.  
- Righe selezionabili per inclusione in `ProjectModel.verifiche_in_relazione`.  
- Detail pane: mostra `steps[]`, `norm_references[]`, `messages[]`.  
- Filtri: norma, esito, stato limite.  
- Azioni: copia valore, esporta singola verifica, apri in report preview.

---

### Report (preview & export)
- GUI espone anteprima Markdown generata dal ReportBuilder (no ricalcoli).  
- Export: Markdown, PDF (via renderer), CSV (lista verifiche).  
- Regole: se nessuna verifica selezionata → include tutte le verifiche eseguite; se selezionate → include solo quelle.

---

### Acceptance criteria (GUI tests — pass/fail)
- GUI‑WF‑001 Norma obbligatoria: tentativo di run senza Norma → Run disabilitato e appare NO_NORMA_SELECTED.  
- GUI‑WF‑002 Input validation: salvando sezione/materiale incompleti appare INPUT_INVALID e Run rimane disabilitato.  
- GUI‑WF‑003 Esecuzione: Run avvia spinner; al termine RisultatiView è popolata con items provenienti da VerificationEngine (read‑only).  
- GUI‑WF‑004 Risultati → Report: selezionando verifiche e cliccando Export produce file che contiene esattamente `VerificationResultItem` selezionati.  
- GUI‑WF‑005 No calc in GUI: assert che nessuna funzione di verifica sia eseguita in view layer (smoke check for no calcs in UI).  
- GUI‑WF‑006 Accessibility & keyboard: navigazione via tastiera completa per le view principali.

---

### Deliverables (per questo STEP)
- Aggiornamento testuale di `PLAN_GUI.md` con le sezioni sopra.  
- Wireframe checklist (component list + gating rules).  
- Test list (acceptance cases) pronta per automazione GUI.

---

Vuoi che generi ora i contenuti PLAN‑ONLY per il successivo file indicato nello STEP 1 (`GUI_MAIN_PY_NAVIGAZIONE.md`)?

User: PLAN_GUI.md approvato.

Procedi ora a generare SOLO i contenuti PLAN‑ONLY per
GUI_MAIN_PY_NAVIGAZIONE.md.

Vincoli invariati:
- stessa sessione di PLAN
- nessun codice
- nessuna anticipazione di Step 2, 3 o 4
- solo specifiche, UX rules e criteri di accettazione

GitHub Copilot: Status: preparo il contenuto PLAN‑ONLY per `GUI_MAIN_PY_NAVIGAZIONE.md` (specifiche, UX rules e criteri di accettazione).

## GUI_MAIN_PY_NAVIGAZIONE.md — Specifica vincolante (PLAN‑ONLY)

### Scopo
Definire in modo vincolante il comportamento, le regole UX e i criteri di accettazione della finestra principale (entry‑point) e della navigazione tra le view nell’applicazione GUI. La main window orchestra il workflow utente (Norma → Metodo → Input → Verifica → Risultati → Report) senza contenere logica normativa o calcoli.

---

### Responsabilità principali (non negoziabili)
- Esporre il workflow stepper e la navigazione tra le View; mantenere un unico `ProjectModel` condiviso.  
- Gestire lo stato UI (view active, badge Norma, metodo UI flag, abilitazioni/disabilitazioni).  
- Innescare l’esecuzione delle verifiche tramite il binding `VerificationEngineBinding` (solo invocation).  
- Presentare progress/feedback e gestire errori UX‑friendly.  
- Non eseguire calcoli né applicare regole normative.

---

### Layout & componenti chiave (descrizione)
- Header: titolo applicazione + `Norma` badge (mostra `project_model.normativa_attiva`) + `Metodo` indicator (UI‑flag).  
- Sidebar (workflow stepper verticale): Step 1 Norma → Step 2 Metodo → Step 3 Sezioni&Materiali → Step 4 Sollecitazioni → Step 5 Esegui → Step 6 Risultati → Step 7 Report. Ogni step mostra stato (incomplete / ready / done).  
- Main container: area che ospita le View (`SezioniMaterialiView`, `SollecitazioniView`, `RisultatiView`, `ReportView`, ecc.).  
- Footer/status bar: brief status text, progress indicator, last action timestamp, log id on error.  
- Controls principali: `Run verifications` (disabilitato finché prerequisiti non soddisfatti), `Cancel`, `Export report`.

---

### Navigazione e comportamenti UX obbligatori
- Flusso lineare guidato: l’utente può navigare liberamente tra le View ma il pulsante `Esegui verifiche` rimane disabilitato finché i prerequisiti non sono soddisfatti.  
- Stepper visuale: ciascun step mostra icona/stato; click su uno step porta alla View corrispondente.  
- Stato Norma: cambio Norma attiva richiede conferma se esistono risultati eseguiti — modal: “Cambiando Norma i risultati esistenti potrebbero non essere più applicabili. Confermare?” (opzioni: Cancel / Proceed — Proceed mantiene risultati ma disabilita azioni incompatibili).  
- Metodo di analisi (UI‑flag): selezione locale di metodo (es. "Default / Advanced"); visibile ma non persiste come vincolo normativo nel core.  
- Run button: attivo solo se (Norma selezionata) AND (sezione/materiale assegnati) AND (sollecitazioni presenti e valide). Al click:
  - Esegue validazione finale (client UI); se OK chiama binding.run_verifications()
  - Mostra progress indicator (modal o status bar)
  - Abilita Cancel che invia richiesta di interruzione all’engine (se supported)
- Visual feedback: durante l’esecuzione disabilitare campi critici; mostrare percentuale o spinner; al completamento navigare automaticamente a `RisultatiView`.
- RisultatiView: sola‑lettura; tutte le interazioni di export/report partono da qui.

---

### Preconditions (UI validation rules)
- Norma selected: mandatory. Message: `NO_NORMA_SELECTED`.  
- Material/Section assigned: mandatory. Message: `INPUT_INVALID` (lista campi).  
- At least one load case present: mandatory.  
- If any precondition fails, `Run` is disabled and a contextual tooltip explains missing items.

---

### Long‑running tasks & cancellation
- `Esegui` runs async; UI must:
  - show cancellable modal or status progress bar
  - prevent multiple concurrent runs (disable Run while running)
  - on Cancel: show confirmation; call cancel on binding; display “Esecuzione interrotta dall’utente”
  - on error: show modal with short message + copyable log id

---

### Error handling / messaging (UX rules)
- Use consistent message catalog (see PLAN_GUI): `INPUT_INVALID`, `NO_NORMA_SELECTED`, `RUN_IN_PROGRESS`, `RUN_SUCCESS`, `RUN_FAILED`, `NOT_APPLICABLE_NOTICE`.  
- All modals include an actionable hint (e.g., “Apri Sezioni” or “Mostra log”) and a reference code for diagnostics.

---

### Accessibility & Keyboard Shortcuts
- Keyboard navigation for stepper and primary actions (Tab/Shift+Tab, Enter to activate Run, Esc to cancel modals).  
- All interactive controls must have labels/tooltips and be reachable by keyboard.  
- Color usage must be contrast‑friendly and not the sole indicator of status.

---

### Non‑functional UI constraints
- Responsiveness: main UI must remain responsive during runs (no blocking main thread).  
- Minimal latency for navigation (view swapping < 100 ms perceived).  
- Visual consistency with project theme (ttkbootstrap recommended).

---

### Acceptance criteria (file‑level tests / UX checks)
- NAV‑001 — Stepper integrity: clicking each step opens the corresponding View and updates stepper state.  
- NAV‑002 — Run gating: Run remains disabled until Norma + Section + Loads valid; attempt to run earlier shows `INPUT_INVALID` modal.  
- NAV‑003 — Norma change: changing Norma with existing results raises confirmation modal and disables incompatible actions.  
- NAV‑004 — Async run: Run displays progress, is cancellable, and on completion navigates to `RisultatiView`.  
- NAV‑005 — No calc in GUI: unit/UI tests assert no computation routine in view layer (smoke check).  
- NAV‑006 — Export after selection: Report export uses `ProjectModel.verifiche_in_relazione` (no recalculation).  
- NAV‑007 — Accessibility: keyboard navigation works for stepper, Run, Cancel, and Export.

---

### File‑level content to add (exact places in `GUI_MAIN_PY_NAVIGAZIONE.md`)
- Section “Role of main.py”: expand to include stepper and gating logic (UI spec only).  
- Section “Layout”: add header badge for Norma + Method indicator and footer status bar spec.  
- Section “Actions main”: replace generic Run behavior with the gating and async/cancel spec above.  
- New subsection “Accessibility & Keyboard”: required keyboard interactions and shortcuts.

---

### Deliverables (per questo file)
- `GUI_MAIN_PY_NAVIGAZIONE.md` updated with the SPEC above (only textual spec, no code).  
- Acceptance test list (NAV‑001..NAV‑007) appended to the file.

---

Confermi che proceda a generare i contenuti PLAN‑ONLY per il prossimo file di STEP 1 (`GUI_SELEZIONE_NORMATIVA.md`)?

User: GUI_MAIN_PY_NAVIGAZIONE.md approvato.

Procedi ora a generare SOLO i contenuti PLAN‑ONLY per
GUI_SELEZIONE_NORMATIVA.md.

Vincoli invariati:
- stessa sessione di PLAN
- nessun codice
- nessuna anticipazione di Step 2, 3 o 4
- solo specifiche, UX rules e criteri di accettazione

GitHub Copilot: Status: preparo il contenuto PLAN‑ONLY da incollare in `GUI_SELEZIONE_NORMATIVA.md` (specifiche, UX rules, acceptance).  

## GUI_SELEZIONE_NORMATIVA.md — Specifica vincolante (PLAN‑ONLY)

Scopo  
- Definire in modo vincolante il comportamento, l’aspetto UX e i criteri di accettazione della view che permette la scelta della normativa di verifica.  
- La view è esclusivamente un’interfaccia: seleziona `project_model.normativa_attiva` e abilita/disabilita le scelte successive in GUI. Non contiene logica normativa né modifica il core.

Contesto d’uso (posizione nel workflow)  
- Prima azione obbligatoria del workflow GUI: Norma → Metodo → Input → Verifica → Risultati → Report.  
- Deve essere visibile sempre in testa al flow e accessibile via sidebar/ProjectWizard.

Normative supportate (iniziali)
- NTC2018 — Stati limite (SLU / SLE / sismica)  
- R.D. 2229/1939 — Tensioni ammissibili (legacy)  
- DM 1992 — Tensioni ammissibili (storico)  
- DM 1996 — Tensioni ammissibili (storico avanzato)  
Nota: elenco estendibile tramite KB; la GUI legge le opzioni da `config/calculation_codes/*` (no logica normativa nella view).

Comportamento richiesto (vincoli UX)
- Norma è un campo obbligatorio: nessuna operazione di verifica è possibile prima della selezione.  
- Modalità di selezione: radio group o dropdown con descrizione breve + "?" tooltip che apre KB pertinente.  
- Badge Norma corrente: sempre visibile nell’header e nella sidebar stepper.  
- Stato di compatibilità: la view mostra (in-line) le funzionalità incompatibili con la norma selezionata (es. “Sismica non disponibile per RD2229”) e disabilita i controlli corrispondenti nella GUI.  
- Conferma cambio Norma: se sono presenti risultati o input potenzialmente incompatibili, al cambio mostra modal di conferma con testo esplicito e due azioni:
  - Cancel (mantieni stato attuale)
  - Proceed — mantiene `project_model` ma applica blocchi UI per le funzionalità incompatibili (non cancellare automaticamente i risultati)
- Persistenza (opzionale/configurabile): salva Norma selezionata nella sessione progetto; default = nessuna selezione al nuovo progetto.
- Informazioni di supporto: link diretto al KB della norma prescelta (apre `docs/MEGAPLAN/KB_*.md`).

Validazione & precondizioni
- La view deve impedire l’esecuzione delle verifiche se `project_model.normativa_attiva` è null/empty.  
- Quando una norma è selezionata, il binding GUI → core deve poter leggere `project_model.normativa_attiva` (nessuna modifica concettuale al ProjectModel).  
- La view segnala errori di selezione tramite codice `NO_NORMA_SELECTED`.

Messaggistica standard (short texts)
- NO_NORMA_SELECTED: "Selezionare una normativa prima di procedere."  
- NORMA_CHANGED_WITH_RESULTS: "Sono presenti risultati eseguiti. Cambiando normativa alcune verifiche potrebbero non essere più applicabili. Confermi?"  
- NORMA_NOT_SUPPORT_CAP7: "Questa normativa non supporta CAP_7 (sismica)."  
- HELP_KB_LINK: "Apri knowledge base (norma)".

Accessibilità & UX rules
- Tutti i controlli sono accessibili via tastiera; radio/dropdown supportano selezione con frecce + Invio.  
- Tooltip e link KB sono leggibili da screen‑reader.  
- Colori e contrasto rispettano linee guida accessibilità; non usare colore come unica informazione.

Edge cases & safe behavior
- Se utente procede al cambio norma con risultati esistenti, lasciare i risultati ma visualizzare chiaramente quali sono incompatibili (flag `NOT_APPLICABLE` / warning nel ResultsView).  
- Non tentare di convertire o migrare risultati tra norme automaticamente.  
- Se la GUI riceve una norma non riconosciuta dal KB, mostra `Unsupported norm` con link per fallback/documentazione.

Criteri di accettazione (test UX)
- NS‑001 (mandatory selection): aprire l’app e tentare di eseguire verifiche senza aver selezionato una norma → `Run` disabilitato; appare NO_NORMA_SELECTED.  
- NS‑002 (change‑with‑results): con risultati già presenti, cambiare norma → appare modal NORMA_CHANGED_WITH_RESULTS; scegliendo Proceed UI applica blocchi ma non cancella risultati.  
- NS‑003 (compatibility): selezionando RD2229 la GUI disabilita controlli CAP_7/sismica e mostra NORMA_NOT_SUPPORT_CAP7.  
- NS‑004 (KB link): click “?” sul nome norma apre la KB pertinente.  
- NS‑005 (accessibility): radio/dropdown operabili via tastiera e screen‑reader friendly.  
- NS‑006 (no core change): selezione aggiorna `project_model.normativa_attiva` ma non cambia logica del core (smoke check: binding still uses ProjectModel as before).

Deliverable per questa vista (SPEC only)
- Aggiornare `GUI_SELEZIONE_NORMATIVA.md` con i comportamenti qui descritti (component list, messages, gating, acceptance tests).  
- Aggiungere 6 test UX (NS‑001 .. NS‑006) alla test plan GUI.

Note operative
- La view deve leggere le opzioni normative da `config/calculation_codes/*` e dall’KB (no hardcoding nella view).  
- Tutte le decisioni normative restano nella KB / CodeModule; la GUI limita soltanto l’accesso alle opzioni non applicabili.

---

Accetti il contenuto da incollare in `GUI_SELEZIONE_NORMATIVA.md`? Vuoi che generi ora il testo PLAN‑ONLY per il prossimo file di STEP 1 (`GUI_VERIFICATION_ENGINE_BINDING.md`)?

User: GUI_SELEZIONE_NORMATIVA.md approvato.

Procedi ora a generare SOLO i contenuti PLAN‑ONLY per
GUI_VERIFICATION_ENGINE_BINDING.md.

Vincoli invariati:
- stessa sessione di PLAN
- nessun codice
- nessuna anticipazione di Step 2, 3 o 4
- solo specifiche, regole UX e criteri di accettazione

GitHub Copilot: Status: preparo il contenuto PLAN‑ONLY per `GUI_VERIFICATION_ENGINE_BINDING.md` — specifiche, regole UX e criteri di accettazione (nessun codice, nessuna modifica al core/ProjectModel).

## GUI — VerificationEngine Binding (SPEC, PLAN‑ONLY)

### Scopo
Definire in modo vincolante il comportamento dell’oggetto `VerificationEngineBinding` che collega la GUI (`ProjectModel`) al `VerificationEngine`. La binding‑layer:
- valida i prerequisiti GUI;
- costruisce/verifica le richieste (tramite la `VerificationFactory`);
- invoca il `VerificationEngine`;
- aggiorna il `ProjectModel` con i `VerificationResultItem`.
La binding‑layer NON esegue calcoli normativi né contiene regole normative.

---

### Flusso operativo (alto livello) 🔁
1. Utente clicca `Esegui verifiche` nella GUI.  
2. GUI chiama `VerificationEngineBinding.run_verifications()`.  
3. Binding esegue prerequisiti/validazione (v. elenco).  
4. Binding invoca `VerificationFactory.create_*_verifications(...)` per ottenere le verifiche da passare al motore.  
5. Binding chiama `VerificationEngine` con le verifiche costruite.  
6. `VerificationEngine` esegue i calcoli e ritorna `VerificationResultItem[]`.  
7. Binding aggiorna `ProjectModel.verifiche_cap4`, `verifiche_cap7`, `verifiche_rd2229` e `verifiche_in_relazione` (default = tutte).  
8. GUI aggiorna `RisultatiView` (read‑only) e mostra messaggi.

---

### Preconditions / Validazioni (binding‑level)
- Norma selezionata (`project_model.normativa_attiva`) — otherwise block.  
- Sezione e Materiale assegnati — otherwise `INPUT_INVALID`.  
- Almeno una sollecitazione valida presente — otherwise `INPUT_INVALID`.  
- Validazione schema input conforme a `PLAN_INPUT_COMUNE.md`.  
- `VerificationFactory` deve restituire almeno una verifica — if none → `INFO_NO_CHECKS`.

> Nota: tutte le validazioni sono UI‑level; la binding‑layer non modifica `ProjectModel` per soddisfare prerequisiti.

---

### UX rules & visual feedback (binding interactions)
- Run button: disabled until preconditions pass.  
- On run: show cancellable progress indicator (spinner + status message).  
- On cancel: binding requests engine cancel and shows "Esecuzione annullata dall’utente".  
- On success: navigate to `RisultatiView` and show `RUN_SUCCESS`.  
- On partial success (some checks NOT_APPLICABLE / ERROR): show `WARN` summary; results still stored.  
- On fatal error: show modal `RUN_FAILED` with copyable `error_id` and brief remediation hint.

---

### Messages & error codes (standardized)
- `NO_NORMA_SELECTED` — norma mancante  
- `INPUT_INVALID` — campi mancanti/errati (lista)  
- `ERR_FACTORY_FAILED` — factory non ha potuto costruire le verifiche  
- `INFO_NO_CHECKS` — nessuna verifica disponibile per input/norma  
- `ERR_ENGINE_RUNTIME` — errore runtime del motore (log id fornito)  
- `RUN_IN_PROGRESS` / `RUN_SUCCESS` / `RUN_FAILED` / `RUN_CANCELLED` — lifecycle states

---

### Partial / edge behaviors
- If `VerificationFactory` yields checks for multiple capitoli, binding routes results to the correct `ProjectModel` lists (CAP_4, CAP_7, RD2229).  
- Do not delete pre‑existing results on re‑run; replace only the results produced by the current run (traceable via `run_id` in metadata).  
- If binding detects `NOT_APPLICABLE` for an entire set, present clear remediation message in UI (e.g., missing data / outside KB limits).

---

### Logging & traceability (UX + diagnostics)
- Each run must generate a `run_id` logged and returned in any UI error modal.  
- Binding logs: start time, end time, number of verifications dispatched, exceptions (no sensitive data).  
- `VerificationResultItem.metadata` must include `calculation_code_version` and `run_id` for traceability.

---

### Contract expectations (binding ↔ factory ↔ engine)
- Binding expects `VerificationFactory` to return "ready‑to‑execute" verification descriptors (no transformation by GUI).  
- Binding passes descriptors unchanged to `VerificationEngine` and stores returned `VerificationResultItem[]` in `ProjectModel`.  
- Binding does not perform or infer normative decisions.

---

### Acceptance criteria & GUI tests (binding‑specific)
- BE‑001 (Preconditions): calling `run_verifications()` without Norma/Section/Loads → method rejects and UI shows `INPUT_INVALID` modal.  
- BE‑002 (Factory absence): `VerificationFactory` returns empty list → UI shows `INFO_NO_CHECKS`; no engine call issued.  
- BE‑003 (Happy path): with valid inputs `run_verifications()` triggers engine, `ProjectModel.verifiche_*` updated, and `RisultatiView` displays results.  
- BE‑004 (Partial failures): engine returns mix OK/NOT_APPLICABLE/ERROR → binding stores all items and UI shows summary warnings.  
- BE‑005 (Cancel): user cancels during run → engine cancel triggered, UI shows `RUN_CANCELLED`.  
- BE‑006 (No core change): binding does not alter `ProjectModel` schema or calculation behavior (smoke verification).

---

### Test data & observability
- Each acceptance test must assert: correct UI message, presence of `run_id` in logs/metadata, correct population of `ProjectModel.verifiche_*`, and no calculations performed in view layer.

---

### Deliverables (per questa SPEC)
- Updated `GUI_VERIFICATION_ENGINE_BINDING.md` containing the sections above.  
- Acceptance test list (BE‑001 .. BE‑006) appended to test plan.

---

Proseguo con il prossimo file di STEP 1 (`GUI_RISULTATI_VIEW_CODICE.md`) se approvi questo contenuto (PLAN‑ONLY).

User: GUI_VERIFICATION_ENGINE_BINDING.md approvato.

Procedi ora a generare SOLO i contenuti PLAN‑ONLY per
GUI_RISULTATI_VIEW_CODICE.md.

Vincoli invariati:
- stessa sessione di PLAN
- nessun codice
- nessuna anticipazione di Step 2, 3 o 4
- solo specifiche, regole UX e criteri di accettazione

GitHub Copilot: Status: genero il contenuto PLAN‑ONLY da incollare in `GUI_RISULTATI_VIEW_CODICE.md` (specifiche, UX rules, criteri di accettazione).  

## GUI_RISULTATI_VIEW_CODICE.md — Specifica vincolante (PLAN‑ONLY)

### Scopo
Definire la View di sola‑lettura che visualizza i `VerificationResultItem` prodotti dal motore di verifica. La view è l’unica interfaccia visiva per esplorare/esportare i risultati e selezionare le verifiche da includere nella relazione. Nessuna logica normativa o calcolo nella View; tutti i numeri provengono da `VerificationResultItem`.

---

### Principi vincolanti
- Solo lettura: la View non modifica dati di calcolo né ricalcola valori.  
- Single source of truth: leggi esclusivamente da `ProjectModel.verifiche_*` / `VerificationResultItem`.  
- Tracciabilità: ogni riga mostra riferimenti normativi (norma + capitolo/paragrafo).  
- Non anticipare modifiche a `ProjectModel` o al core.

---

### Layout & componenti principali
- Header: filtro rapido (norma, stato limite, esito), ricerca testuale (check_id / element_id).  
- Main: tabella (sortable + paginata) con colonne minime e utilisation bar.  
- Right/Bottom pane: dettaglio selezionato (steps[], norm_references[], messages[], export single).  
- Toolbar: checkbox “Seleziona tutto”, pulsanti `Include in Report`, `Export selected (CSV/MD)`, `Copy reference`.  
- Status/footer: conteggi (mostrate/filtrate), last run timestamp, run_id link.

---

### Tabella — colonne obbligatorie (orderable/filterable)
- Checkbox (inclusione per report)  
- `Verifica` (human label: `reference.paragrafo`)  
- `Elemento` (`element_id`)  
- `Norma` (`norma`)  
- `Stato limite` (SLU/SLE/TA/…)  
- `Esito` (OK / NOT_OK / NOT_APPLICABLE / ERROR)  
- `Utilisation` (visual + numeric Ed/Rd)  
- `Combinazione critica` (if present)  
- `Timestamp` / `run_id` (metadata)

---

### Detail pane (per la riga selezionata)
- Visualizzazione `steps[]` in ordine numerico (test‑friendly, copyable).  
- `norm_references[]` with clickable anchor to KB/MD (opens docs).  
- `messages[]` (warnings, NOT_APPLICABLE reason, remediation hints).  
- Quick actions: `Export single check`, `Copy normative reference`, `Open in report preview`.

---

### Visual encoding & rules
- Utilisation bar thresholds: green ≤0.8, amber 0.8–1.0, red >1.0.  
- Iconography: OK (check), NOT_OK (cross), WARNING (exclamation), NOT_APPLICABLE (dash/info).  
- Tooltip content: short explanation + link “Ulteriori dettagli” → detail pane.  
- Row order default: descending by utilisation (critical first); user‑sortable.

---

### Interactions / UX behaviour
- Selecting checkbox updates `ProjectModel.verifiche_in_relazione` (GUI action only).  
- Double‑click on a row opens the detail pane and scrolls to `steps[]`.  
- Filters applied client‑side (no core calls).  
- Export action uses only displayed `VerificationResultItem` fields — no recomputation.  
- If a result contains `NOT_APPLICABLE`, show remediation hint and disable “Include in Report” only if explicitly configured by user (default: allow inclusion with warning).

---

### Messages & error handling
- `NOT_APPLICABLE` row shows tooltip: reason and KB link.  
- If `VerificationResultItem` missing `norm_references[]`, display warning and attach `TODO: add norm_reference` badge (for KB maintenance).  
- Export failures show `ERROR_INTERNAL` with log id.

---

### Accessibility & keyboard
- Keyboard: Up/Down navigate rows; Enter opens detail pane; Space toggles checkbox; Ctrl+E = Export selected.  
- All icons have ARIA labels; contrast and font sizes meet accessibility thresholds.

---

### Performance expectations
- Table must handle up to 500 items without perceptible UI lag (pagination/virtualization required).  
- Detail pane rendering must be instantaneous for any selected row.

---

### Acceptance criteria (GUI tests)
- RV‑001: Table renders `VerificationResultItem[]` exactly as provided (no transformations).  
- RV‑002: Utilisation colour thresholds and numeric values match `VerificationResultItem.utilisation`.  
- RV‑003: Checkbox inclusion correctly updates `ProjectModel.verifiche_in_relazione` (selection roundtrip).  
- RV‑004: Detail pane shows full `steps[]`, `norm_references[]`, and `messages[]` for selected item.  
- RV‑005: Export selected produces file containing only the selected `VerificationResultItem` fields.  
- RV‑006: NOT_APPLICABLE rows show remediation hint and KB link.  
- RV‑007: Keyboard navigation and ARIA labels validated.  
- RV‑008: UI remains responsive with 500+ results (pagination/virtualization verified).

---

### Test data recommendations
- Create at least 3 `VerificationResultItem` fixtures: OK (util 0.6), Borderline (util 0.95, WARNING), NOT_APPLICABLE (with message and missing KB ref). Use these in automated GUI tests.

---

### Deliverables for this SPEC
- Updated `GUI_RISULTATI_VIEW_CODICE.md` containing only the above (rules + acceptance + UX).  
- Acceptance test list (RV‑001..RV‑008) appended to the GUI test suite.

---

Vuoi che proceda ora con l’ultimo file dello STEP 1 (`GUI_RISULTATI_TO_RELAZIONE_BINDING.md`) e generi il contenuto PLAN‑ONLY corrispondente?

User: Genera il contenuto PLAN‑ONLY di GUI_RISULTATI_TO_RELAZIONE_BINDING.md,
coerente con:
- GUI_RISULTATI_VIEW_CODICE.md
- REPORT_BUILDER_NTC2018
- REPORT_BUILDER_RD2229

Rimani in modalità PLAN.
Vincoli invariati:

stessa sessione di PLAN
nessun codice
nessuna anticipazione di Step 2, 3 o 4
solo specifiche, regole UX e criteri di accettazione

GitHub Copilot: Summarized conversation historySto per aprire i file SPEC e i riferimenti del report builder per garantire coerenza con la nuova specifica. Procedo a cercare le occorrenze rilevanti nel repository.

Ricerca dell'espressione regolare `REPORT_BUILDER_NTC2018|REPORT_BUILDER_RD2229|GUI_RISULTATI_VIEW_CODICE` in corso...

Ricerca di file corrispondenti `**/GUI_RISULTATI_VIEW_CODICE.md`, 1 corrispondenza

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/GUI_RISULTATI_VIEW_CODICE.md)

Ricerca dell'espressione regolare `ReportBuilder|report_builder|REPORT_BUILDER` in corso...

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN)

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/GUI_RISULTATI_TO_RELAZIONE_BINDING.md)

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/REPORT_BUILDER_NTC2018_CODE.md)

Lettura [](file:///c%3A/workspaces/RD2229/RD2229/docs/MEGAPLAN/REPORT_BUILDER_RD2229.md)

## Plan: GUI_Risultati → Relazione (binding)

TL;DR — Definire il contratto e le regole UX che collegano la `RisultatiView` ai `ReportBuilder` (`NTC2018` / `RD2229`).  
Obiettivo: garantire tracciabilità, nessun ricalcolo, selezione controllata dei VerificationResult e generazione Markdown conforme ai builder esistenti. (Coerente con GUI_RISULTATI_VIEW_CODICE.md, REPORT_BUILDER_NTC2018_CODE.md, REPORT_BUILDER_RD2229.md)

---

### Specifica sintetica (contratto)
- Scopo: la GUI espone selezione e preview; la generazione del documento è delegata esclusivamente al `ReportBuilder` corrispondente alla `project_model.normativa_attiva`.  
- Responsabilità:
  - `RisultatiView`: sola lettura dei valori; offre **modalità estesa** per la selezione di quali verifiche includere in relazione; aggiorna solo `ProjectModel.verifiche_in_relazione`.
  - `ReportBuilder`: riceve `ProjectModel` e ritorna Markdown; NON esegue calcoli; valida la normativa attiva.
- Dati obbligatori per ogni voce inclusa nella relazione (mantenerli nel `VerificationResult`):
  - riferimento norma/paragrafo, `capitolo_ntc`, `demand` (Ed), `capacity` (Rd), `ratio`, `status`.
- Formato minimo nel report:
  - header con `project_model.normativa_attiva`, data/ora e identificativo progetto;
  - sezioni separate per `CAP_4` e `CAP_7` (NTC) o per tipologie RD2229;
  - per ogni verifica: titolo (paragrafo), Ed, Rd, Ed/Rd (ratio con 3 decimali), esito.

> Nota: la GUI non ricalcola e non altera i valori — qualsiasi trasformazione numerica è vietata nella view.

---

### UX — regole di interazione (behavior / microcopy)
- Modalità e controlli
  - Modalità base: la `RisultatiView` rimane *read‑only*; tutte le verifiche eseguite sono incluse automaticamente nella relazione.
  - Modalità estesa (toggle “Seleziona risultati”): mostra una casella `Includi` per ogni riga (checkbox), plus controllo `Seleziona tutto / Deseleziona tutto`.
- Pulsanti e tooltip
  - `Anteprima relazione` — mostra Markdown generato in viewer read‑only; tooltip: "Anteprima della relazione generata dal ReportBuilder".
  - `Genera relazione` (disabled se non ci sono verifiche incluse o se validazioni falliscono); tooltip: "Genera file Markdown/PDF usando il ReportBuilder per la normativa attiva".
  - `Esporta (.md/.pdf/.docx)` — attivo solo dopo `Genera`.
- Stati e validazioni immediate (UI)
  - Se non sono state eseguite verifiche → `Genera relazione` disabilitato; messaggio inline: "Esegui le verifiche prima di generare la relazione".
  - Se una voce selezionata ha `status == N.A.` → checkbox disabilitata + icona warning + messaggio: "Verifica non eseguita".
  - Se la selezione contiene risultati di normativa non omogenea → blocco generazione + dialogo con testo: "Selezione contenente normative differenti — separare le relazioni".
- Persistenza
  - Le selezioni vengono salvate in `ProjectModel.verifiche_in_relazione` ed esportate con il progetto (persistenza progetto).
- Accessibilità & feedback
  - Tastiera: checkbox navigabili; `Ctrl+A` per seleziona tutto; conferma visiva (badge count delle voci incluse).
  - Feedback immediato dopo `Genera`: toast "Relazione generata — anteprima pronta" o errore dettagliato.

---

### Validazioni / regole vincolanti (hard rules)
- Nessuna operazione di ricalcolo o modifica numerica eseguita dalla GUI o dal ReportBuilder.
- Non è permesso includere in relazione verifiche non eseguite.
- Non mescolare voci non omogenee per normativa/engine; se presenti, il builder rifiuta la generazione.
- Il builder chiamato deve corrispondere a `project_model.normativa_attiva`; in caso contrario restituisce errore esplicito (es. "Normativa attiva non compatibile...").
- `CAP_4` e `CAP_7`: devono comparire in sezioni distinte nella relazione (non mescolare all'interno della stessa tabella).

---

### Mappatura dati (visual → report)
- Campo VerificationResult → uso in report:
  - `reference.paragrafo` → titolo voce
  - `capitolo_ntc` → sezione (CAP_4 / CAP_7)
  - `demand` → Ed (unità come in ProjectModel)
  - `capacity` → Rd
  - `ratio` → Ed/Rd (format: 3 decimali)
  - `status` → Esito (OK / NOT OK / N.A.)
- Grouping: il ReportBuilder raggruppa automaticamente per `capitolo_ntc` (NTC) o per categorie RD2229; la GUI deve riflettere lo stesso raggruppamento nell’anteprima.

---

### Criteri di accettazione (testabili)
Functional (unit / integration)
1. Dato `project_model` con `normativa_attiva == 'NTC2018'` e 3 VerificationResult validi, quando si esegue `Genera relazione`, allora `ReportBuilderNTC2018` ritorna Markdown che:
   - include header con "NTC2018";
   - contiene 3 sezioni di verifica con i campi Ed, Rd e ratio formattato a 3 decimali.
2. Se `project_model.normativa_attiva !=` builder richiesto, il builder rifiuta la generazione con errore riconoscibile.
3. Se una voce selezionata ha `status == N.A.`, la generazione è bloccata e l’UI mostra un messaggio di errore specifico.
4. Se la selezione contiene voci di normative differenti, la generazione è bloccata e l’utente riceve indicazione per separare le relazioni.
5. Se l’utente seleziona/deseleziona checkbox, `ProjectModel.verifiche_in_relazione` riflette esattamente la selezione (persistenza verificabile dopo salvataggio/caricamento progetto).

UX / E2E
1. Workflow: esegui verifiche → mostra Risultati → (opzionale) entra in Modalità estesa → seleziona voci → `Anteprima` mostra il Markdown corretto → `Genera relazione` abilita l’export.  
2. Pulsante `Genera relazione` è disabilitato se non esistono verifiche incluse; abilitato immediatamente dopo la prima selezione.
3. La preview è leggibile, con separazione visiva per CAP_4 / CAP_7 e conteggio voci incluso.

Non‑functional
- Generazione Markdown per fino a 200 verifiche deve completarsi in tempo percepibile (< 2s su macchina di sviluppo tipica).

---

### Casi d’errore e messaggi (standardizzati)
- "Esegui le verifiche prima di generare la relazione" — quando non ci sono verifiche eseguite.
- "Verifica non eseguita — impossibile includere" — per checkbox disabilitata.
- "Normativa attiva non compatibile con il ReportBuilder selezionato" — errore builder (testabile).
- "Selezione non omogenea: separare i risultati per normativa" — blocco generazione.

---

### Verifiche di conformità con file esistenti
- Coerente con GUI_RISULTATI_VIEW_CODICE.md: view rimane read‑only; selezione è funzione di estensione; ratio in view è a 3 decimali.
- Coerente con REPORT_BUILDER_NTC2018_CODE.md e REPORT_BUILDER_RD2229.md: GUI delega la generazione al builder corretto; nessun ricalcolo nel builder; mapping dei campi rispettato.

---

### Acceptance checklist (da validare in PR)
- [ ] `RisultatiView` offre selezione persistente e aggiorna `ProjectModel.verifiche_in_relazione`.
- [ ] `Genera relazione` valida stato/esecuzione/normativa prima della chiamata al builder.
- [ ] `ReportBuilderNTC2018` / `ReportBuilderRD2229` ricevono solo dati immutati e producono Markdown coerente.
- [ ] Messaggi di errore e tooltip implementati come da specifica.
- [ ] Test automatici: unit per builder + integrazione GUI→ProjectModel→ReportBuilder + E2E “run→select→build→export”.

---

Decisione principale
- Persistenza della selezione in `ProjectModel.verifiche_in_relazione` (scelta: tracciabilità e ricostruibilità nel tempo).

---

> ⚠️ Important: questa è una specifica PLAN‑ONLY — nessuna modifica di codice o implementazione viene proposta qui. Seguono solo regole UX, contratto dati e criteri di accettazione pronti per essere implementati.

User: Rimani in modalità PLAN.
Aggiorna la specifica appena prodotta per GUI_RISULTATI_TO_RELAZIONE_BINDING.md applicando questi allineamenti vincolanti:

1) Coerenza con GUI_RISULTATI_VIEW_CODICE.md: la selezione per report è sempre basata su ProjectModel.verifiche_in_relazione; l’eventuale “inclusione automatica” deve essere un default configurabile e non una regola rigida.

2) NOT_APPLICABLE: non imporre blocchi rigidi. Default = inclusione consentita con warning (come nella specifica precedente); il blocco inclusione/generazione deve essere configurabile.

3) Ratio: deve provenire da VerificationResultItem; la GUI può solo formattare (3 decimali) senza calcolare Ed/Rd.

Integra anche norm_references[] e run_id nella tracciabilità del report. Nessun codice.

GitHub Copilot: Status: aggiorno la specifica esistente per applicare i vincoli richiesti. Prossimo passo: fornisco la versione rivista pronta da incollare in GUI_RISULTATI_TO_RELAZIONE_BINDING.md.

## Aggiornamento: GUI_Risultati → Relazione (binding) — allineamenti vincolanti

TL;DR — Manteniamo la regola che la selezione per la relazione è sempre basata su `ProjectModel.verifiche_in_relazione`; l’inclusione automatica diventa un *default configurabile*; il comportamento per `NOT_APPLICABLE` è policy‑driven (default = warning, blocco solo se configurato); il `ratio` deve provenire da `VerificationResultItem` (GUI solo formatta). Inoltre la relazione deve riportare `norm_references[]` e `run_id` per piena tracciabilità.

---

### Modifiche chiave (sintesi)
- Selezione per report = univocamente da `ProjectModel.verifiche_in_relazione`. L’“inclusione automatica” è un comportamento predefinito configurabile (non una regola fissa).
- Gestione `NOT_APPLICABLE`: default = inclusione consentita con warning; blocco solo se la policy di progetto lo richiede.
- `ratio` è fonte‑of‑truth: usare `VerificationResultItem.ratio`; la GUI può soltanto *format‑display* (3 decimali).
- Aggiunta tracciabilità: `ProjectModel.norm_references[]` e `ProjectModel.run_id` devono comparire nell’header della relazione e nei metadati.

---

### Specifica aggiornata (sezioni rilevanti)

#### Principio fondamentale (invariato)
- La Relazione di Calcolo NON ricalcola nulla. Input esclusivo: `VerificationResult` già validati.

#### Autorità della selezione
- La selezione dei risultati da inserire in relazione è sempre governata da `ProjectModel.verifiche_in_relazione`.
- L’opzione “Includi automaticamente tutte le verifiche eseguite” è un *default configurabile* (es. `project_settings.report.inclusion_default = 'auto' | 'manual'`). Non è più un comportamento rigido del view.

#### Policy per risultati `N.A.` (NOT_APPLICABLE)
- Default project policy: `na_handling = 'warn'` → consentire inclusione ma evidenziare con warning.
- Alternative configurabili: `na_handling = 'block'` (impedisce inclusione/generazione) o `'allow'` (inclusione senza warning).
- La GUI riflette la policy (checkbox disabilitata se `block`, checkbox abilitata + icona warning se `warn`).

#### Tracciabilità estesa (obbligatoria)
- `ProjectModel` deve esporre:
  - `verifiche_in_relazione`: lista autorevole per il builder
  - `norm_references[]`: elenco stringhe (normative citate) inserite nell’header del report
  - `run_id`: identificatore unico della sessione/verifica da riportare in header/metadata
- Il ReportBuilder inserisce `run_id` e `norm_references[]` nell’intestazione Markdown e in metadata (audit trail).

#### Fonte del Ratio
- `ratio` deve essere letto da `VerificationResultItem.ratio`.  
- La GUI applica solo formattazione testuale a 3 decimali (es.: display / Markdown: `0.732`).
- È vietato derivare `ratio` nella view o ricalcolarlo per la relazione.

#### Ruoli GUI vs Builder (coerenza)
- `RisultatiView` espone selezione (modale estesa) e salva l’esatta lista in `ProjectModel.verifiche_in_relazione`.
- `ReportBuilder` esegue un’ultima validazione policy‑driven (rispettando `project_settings.report.*`) ma NON modifica i dati.
- Se la policy richiede blocco (es. `na_handling == 'block'`) il builder rifiuta e fornisce messaggio diagnostico coerente con l’UI.

---

### UX / controllo comportamentale (concretezza)
- Modalità base: tutte le verifiche eseguite *possono* essere incluse automaticamente solo se `inclusion_default == 'auto'`; altrimenti l’utente seleziona manualmente.
- NOT_APPLICABLE: riga con `status == N.A.` mostra icona ⚠️ e tooltip:
  - Default: "Verifica N.A. — inclusione consentita (configurazione: avviso)."
  - Se policy == block: checkbox disabilitata + tooltip "Includere disabilitato dalla policy di progetto".
- Configurazioni utente/progetto disponibili (descrizione UX):
  - Toggle `Report: Inclusione automatica` (default ON = `auto`, OFF = `manual`)
  - Select `Report: NA handling` → [Warn (default) | Block | Allow]
- Anteprima: header dell’anteprima mostra `run_id` + `norm_references[]` + conteggio voci incluse.

---

### Mappatura dati aggiornata (visual → report)
- `VerificationResult.reference.paragrafo` → titolo voce
- `capitolo_ntc` → sezione (CAP_4 / CAP_7)
- `demand` → Ed
- `capacity` → Rd
- `ratio` → Ed/Rd (presa da `VerificationResultItem.ratio`; GUI format a 3 decimali)
- `status` → Esito
- `norm_references[]` (ProjectModel) → header/note normative
- `run_id` (ProjectModel) → header / metadata di tracciamento

---

### Policy‑driven validation (sostituisce i blocchi rigidi)
- Le regole di inclusione/generazione sono determinate dalle impostazioni di progetto (`project_settings.report.*`).
- Comportamento predefinito (safe): inclusione automatica permessa, `N.A.` provoca solo warning.
- Se il team richiede rigore, impostare `na_handling = 'block'` e `inclusion_default = 'manual'`.

---

### Criteri di accettazione (aggiornati e testabili)
Functional
- FA1: Se `ProjectModel.verifiche_in_relazione` contiene 3 verification (normativa NTC2018), `ReportBuilderNTC2018.build()` produce Markdown con header contenente `run_id` e `norm_references[]`, e 3 voci con `ratio` uguale a `VerificationResultItem.ratio` formattato a 3 decimali.
- FA2: Default behavior (policy `'warn'`): voce `status == N.A.` è selezionabile ma genera un avviso in UI; builder include la voce con marcatura di avviso.
- FA3: Se `project_settings.report.na_handling == 'block'`, il builder rifiuta la generazione se `verifiche_in_relazione` contiene voci `N.A.`; UI e test devono mostrare messaggio coerente.
- FA4: Se `inclusion_default == 'auto'`, dopo l’esecuzione delle verifiche `ProjectModel.verifiche_in_relazione` viene popolato automaticamente; se `'manual'`, rimane vuoto finché l’utente non seleziona.
- FA5: `ratio` mostrato nella UI e riportato nel Markdown corrisponde esattamente al valore `VerificationResultItem.ratio` formattato (verificare che UI non esegua calcolo).

Traceability / Metadata
- T1: Il Markdown generato contiene header con `run_id`, `generated_on` e `norm_references[]`.
- T2: Le selezioni salvate in `ProjectModel.verifiche_in_relazione` sopravvivono a save/load progetto.

Non‑functional
- N1: Generazione Markdown (fino a 200 verifiche) completata in < 2s.

---

### Messaggi d’errore / microcopy (standard)
- "Esegui le verifiche prima di generare la relazione"
- "Verifica non eseguita — inclusione consentita (configurazione: avviso)"
- "Inclusione di verifiche N.A. bloccata dalla policy di progetto"
- "Normativa attiva non compatibile con il ReportBuilder selezionato"
- "Selezione non omogenea: separare i risultati per normativa"

---

### Acceptance checklist (da verificare in PR / test)
- [ ] `ProjectModel.verifiche_in_relazione` è l’unica fonte per la generazione del report
- [ ] `inclusion_default` è configurabile e rispetta il comportamento UI
- [ ] `na_handling` default = `warn`; opzioni `block`/`allow` testate
- [ ] `ratio` proviene da `VerificationResultItem.ratio` (UI format a 3 decimali)
- [ ] `norm_references[]` e `run_id` presenti nell’header Markdown
- [ ] Test unit + integrazione per tutti i casi policy‑driven

---

Decisione principale
- Conversione delle regole rigide in *policy configurabili* (default safe = inclusione automatica consentita + warning per `N.A.`). Persistenza e tracciabilità tramite `verifiche_in_relazione`, `norm_references[]` e `run_id`.

---

Nota finale ✨  
Questa è la versione aggiornata PLAN‑ONLY da sostituire in GUI_RISULTATI_TO_RELAZIONE_BINDING.md. Nessuna modifica di codice è proposta qui — solo regole UX, contratto dati e criteri di accettazione pronti per implementazione.

User: Procedi a generare entrambi i documenti, PLAN‑ONLY e PRONTI‑TO‑PASTE, con questi vincoli confermati (riassumo per evitare ambiguità operative):
Vincoli confermati

PLAN‑ONLY: nessun codice, nessuna implementazione, nessuna modifica a src/ o config/.
VRDc (No Stirrups):

Formule EC2/NTC riassunte (non derivate in GUI).
Test fixtures con valori calcolati usando γc = 1.5 come default, esplicitando che è configurabile.
Applicabilità chiara + gestione NOT_APPLICABLE policy‑driven (default warn).


SecondaryElementSpec:

Template di verifica (struttura dati/contratto).
GUI bindings coerenti con VerificationResultItem e ProjectModel.
Esempi produttore (ancoraggi) come esempi illustrativi, con valori SLE provvisori chiaramente marcati (TODO/placeholder).


Tracciabilità: riferimenti normativi espliciti; nessun ricalcolo in GUI; source‑of‑truth nei risultati.
Chiarezza: ogni assunzione marcata; TODO dove servono dati normativi definitivi.

Puoi procedere.

GitHub Copilot: Status: preparo due SPEC (PLAN‑ONLY + PRONTI‑TO‑PASTE) per
1) V_Rd,c (taglio senza armatura) e 2) Secondary Element Spec.  
Prossimo passo: fornisco i due file Markdown completi, pronti da incollare — nessun codice, solo specifiche, test‑fixtures e TODO.

---

## 1) V_Rd,c — taglio senza staffatura (SPEC + PRONTI‑TO‑PASTE) ✅

### PLAN‑ONLY — cosa, perché, vincoli principali
- Scopo: definire la specifica della verifica V_Rd,c (shear resistance **without shear reinforcement**) per il core (calcolo) e i test‑fixtures per la suite di verifica.  
- Vincoli obbligatori:
  - GUI: nessun calcolo; sola presentazione/format‑display (ratio a 3 decimali).
  - Source‑of‑truth: `VerificationResultItem` prodotto dal core.
  - Default materiale di progetto: γc = 1.5 (configurabile).
  - NOT_APPLICABLE handling = policy‑driven (default = warn; blocco solo se configurato).
- Normativa di riferimento: EN 1992‑1‑1 (EC2, shear clause), NTC2018 (rif. locale). Specifiche normative e numeri di clausola devono essere inseriti nel KB (TODO).
- Output atteso dal core: `V_Rd,c` (kN), `v_rd,c` (N/mm²), `VerificationResultItem.ratio`, eventuale `sle.crack_width` (service check).
- Acceptance tests: numerici (vedi fixtures), policy tests per `na_handling` e `inclusion_default`.

---

### Formula riassunta (da implementare nel core — sintesi)
- v_rd,c = [C_Rd,c * k * (100·ρ_l·f_ck)^(1/3) + k1·σ_cp]   (N/mm²)
  - C_Rd,c = 0.18 / γc  (γc default = 1.5)
  - k = 1 + sqrt(200 / d)  (d in mm), limitato a max 2.0
  - k1 ≈ 0.15
  - ρ_l = A_sl / (b_w · d)
  - σ_cp = N_ed / A_c (positive in compression; trattare i segni come da EC2 — TODO: mappare esatto comportamento)
- V_Rd,c = v_rd,c · b_w · d  (N → convertire in kN per output)
- Nota GUI: la view legge `VerificationResultItem.ratio`; formatta a 3 decimali — NON ricalcola Ed/Rd.

---

### SLE — fessurazione (policy)
- SLE fessurazione: verifiche di crack width devono essere eseguite dal core usando combinazioni di servizio (quasi‑permanenti) secondo EC2/NTC.  
- GUI mostra `sle.crack_width` (mm) e `sle.w_lim` (mm) prese dal KB/progetto; default policy = warn se w_calc > w_lim; `na_handling` applicabile anche qui.

---

### Applicabilità & NOT_APPLICABLE handling
- Applicabile a: travi/solette monodirezionali senza staffe, sezioni regolari (non deep beams/strut‑and‑tie), condizioni in cui il metodo EC2 è valido.
- Non applicabile (NOT_APPLICABLE) quando: esistono staffe, sezioni non conformi ai presupposti EC2, o dati mancanti.  
- Comportamento UI: default = inclusione consentita + warning per NA; blocco generazione solo se `project_settings.report.na_handling == 'block'`.

---

### Test‑fixtures (γc = 1.5 used — configurable)
- Nota: tutti i fixtures usano γc = 1.5 (esplicitare nel test); test implementer può passare valore diverso per coprire casi.
- Esempi (valori calcolati — vedi formula sopra)

1) Example A — tipico beam (no axial)
- Inputs: b_w=300 mm, d=500 mm, f_ck=30 MPa, A_sl=2×Ø20 → 628.32 mm², N_ed=0 kN, γc=1.5  
- Calcoli (riassunto): ρ_l=0.0041888; k=1.6325; (100·ρ_l·f_ck)^(1/3)≈2.325  
- Risultato: v_rd,c ≈ 0.455 N/mm² → V_Rd,c ≈ 68.32 kN  
- Test: Ed_example = 50.0 kN → ratio = 0.732 → status = OK

2) Example B — bassa capacità (no axial)
- Inputs: b_w=250 mm, d=400 mm, f_ck=25 MPa, A_sl=3×Ø16 → 603.19 mm², N_ed=0 kN, γc=1.5  
- Risultato: V_Rd,c ≈ 50.64 kN  
- Test: Ed_example = 60.0 kN → ratio = 1.185 → status = NOT OK

3) Example C — compressive axial beneficial
- Inputs: come Example A + N_ed = 300 kN compressive, A_c≈300×600=180000 mm² → σ_cp≈1.667 MPa  
- Risultato: V_Rd,c ≈ 105.82 kN  
- Test: Ed_example = 100.0 kN → ratio ≈ 0.945 → status = OK

- SLE fixture (Example A): core computes `sle.crack_width = 0.12 mm` (example result); `sle.w_lim` from KB e.g. 0.30 mm → pass (placeholder — core computes exact).

---

### Criteri di accettazione (testabili)
- CA1: Core produce `VerificationResultItem` con `capacity == V_Rd,c` e `ratio == Ed / V_Rd,c`; GUI mostra ratio a 3 decimali.
- CA2: Fixtures A/B/C passano/fail come indicato.
- CA3: `γc` default = 1.5 ma è parametro di progetto (test con γc ≠ 1.5).
- CA4: NOT_APPLICABLE = default warn; se `na_handling == 'block'` la generazione viene bloccata.
- CA5: SLE: `sle.crack_width` esposto in `VerificationResultItem.sle`; UI mostra warning/errore in base a policy.

---

### Assunzioni & TODO
- TODO: inserire i riferimenti esatti di clausola EC2 e NTC2018 nel KB.
- TODO: definire comportamento esatto per σ_cp negativo (seguire EC2/NTC).
- Assunzione: area cilindrica delle barre calcolata come input `A_sl` — core deve normalizzare.

---

### PRONTI‑TO‑PASTE — contenuto Markdown (file suggerito: `SPEC_RC_SLU_VRDc_NoStirrups.md`)
```markdown
RC_SLU – V_Rd,c (Taglio senza armatura)  
Status: SPEC (PLAN‑ONLY) — NO CODE

1. Scopo
...
(Usare qui il testo già descritto nella sezione PLAN‑ONLY: scopo, formula riassunta, test‑fixtures, SLE, applicabilità, acceptance criteria, TODO)
```

(Nota: il testo pieno, comprensivo di tabelle fixture e TODO, è fornito sopra e pronto da incollare — mantenere i valori numerici forniti e marcare le TODO normative.)

---

## 2) Secondary Element Spec — elementi secondari (Cap. 7.2) ✅

### PLAN‑ONLY — cosa deve contenere la SPEC
- Scopo: definire il contratto dati, i binding GUI ↔ core e i casi di verifica per gli elementi secondari (parapetti, mensole, ancoraggi, cordoli, ecc.), inclusi esempi di controlli per ancoraggi (produttore).
- Vincoli obbligatori:
  - GUI non calcola; raccoglie input strutturati e invia al core; `VerificationResultItem` è sorgente‑di‑verità.
  - Tracciabilità: `run_id` e `norm_references[]` obbligatori per ogni `VerificationResultItem`.
  - SLE placeholders per esempi produttore (marcare come TODO; sostituire con ETA/fornitore in produzione).
  - NOT_APPLICABLE handling = default warn (configurabile).
- Output atteso: `VerificationResultItem` con campi standard + `sle` (se applicabile) + `product_reference` (se usati dati produttore).

---

### Template di verifica (struttura dati / contratto)
- Input (SecondaryElementInput)
  - `id` (string)
  - `type` (enum: "parapet","copertina","corrimano","anchor","edge_beam",...)
  - `geometry`: { b_mm, h_mm, L_mm, d_eff_mm (se rilevante) }
  - `material`: { concrete_class: "C30/37", f_ck_MPa, E_cm_MPa, gamma_c (default 1.5) }
  - `reinforcement`: { A_sl_mm2, bar_layout... } (opzionale)
  - `loads`: { N_ed_kN, Mx_kNm, My_kNm, V_ed_kN, load_combination: "ULS/SLS/QUASI_PERM" }
  - `exposure_class`, `service_class`
  - `manufacturer_data` (optional): { product_id, Rk_tensile_kN, Rk_shear_kN, ETA_reference }
  - `run_id`, `norm_references[]`
- Expected VerificationResultItem (per output)
  - `id`, `reference`(norma,paragrafo), `capitolo_ntc`, `demand`, `capacity`, `ratio`, `status` (OK/NOT OK/N.A.), `sle` (object: crack_width_mm, w_lim_mm,...), `trace`: { run_id, norm_references[] }, `notes`

---

### GUI bindings (mapping & UX rules)
- Editor fields ↔ ProjectModel:
  - `SecondaryElementEditor` salva in `ProjectModel.secondary_elements[]` l’oggetto `SecondaryElementInput`.
  - Validazioni: unità obbligatorie, valori positivi, presenza `run_id`/`norm_references[]` per output.
- Verifica:
  - L’utente seleziona l’elemento secondario → "Esegui verifica" manda input al VerificationEngine.
  - La View mostra `VerificationResultItem` (read‑only). `ratio` mostrato a 3 decimali.
  - Se `manufacturer_data` è presente, il core usa ETA values; GUI deve mostrare etichetta "valore proveniente da produttore (ETA) — verificare documentazione".

---

### Esempi produttore (ancoraggi) — ILLUSTRATIVI, SLE placeholders
- Esempio A — Anchor X (illustrative only)
  - `product_id`: "AnchorX‑M10"
  - Rk_tensile (characteristic): 50 kN (ES: placeholder — **TODO: sostituire con ETA**)
  - Rk_shear: 60 kN (placeholder)
  - Test fixture: Ed_tensile = 30 kN → ratio = 0.60 → expected status = OK
  - SLE: `sle.crack_width` placeholder = 0.35 mm (***TODO: calcolare correttamente nel core / sostituire con dati produttore***)
- Nota: tutti i valori produttore usati negli esempi devono essere sostituiti con ETA/EAD firmati prima della validazione legale.

---

### Tracciabilità & metadati
- Ogni `VerificationResultItem` deve includere `trace.run_id` e `trace.norm_references[]`.
- GUI anteprima e Relazione devono stampare `run_id` e `norm_references[]` per audit trail.

---

### Criteri di accettazione (testabili)
- S1: `SecondaryElementInput` viene serializzato in `ProjectModel.secondary_elements[]` e roundtrippato su save/load.
- S2: Per un anchor example con `Rk=50 kN` e `Ed=30 kN`, `VerificationResultItem.capacity == 50 kN`, `ratio == 0.60`, `status == OK`.
- S3: Se `manufacturer_data` mancante, il core usa metodi di progetto (fallback) e segnala `notes`.
- S4: GUI non ricaccola ratio/capacity; mostra solo i risultati provenienti dal core.
- S5: `run_id` + `norm_references[]` presenti in ogni `VerificationResultItem`.

---

### Assunzioni & TODO
- TODO: raccogliere ETAs dei produttori per i dati degli ancoraggi; contrassegnare i campioni attuali come placeholder.
- TODO: mappare esatto riferimento NTC2018 Cap.7.2 → inserire clausole nel KB.
- Assunzione: tutte le verifiche degli elementi secondari sono eseguite dal core e restituiscono `VerificationResultItem` coerenti con lo schema del progetto.

---

### PRONTI‑TO‑PASTE — contenuto Markdown (file suggerito: `CONFIG_NTC2018_SECONDARY_ELEMENTS_SPEC.md`)
```markdown
CONFIG NTC2018 — Secondary Elements Spec (Cap. 7.2)  
Status: SPEC (PLAN‑ONLY) — Template di verifica & GUI binding

1. Finalità
...
(Usare qui il testo già descritto nella sezione PLAN‑ONLY: contratto dati, mapping GUI, esempi produttore, tracciabilità, acceptance criteria, TODO)
```

(Nota: incollare la versione completa sopra; tutti i valori produttore sono esempi e marcati TODO.)

---

🎯 Prossimi passi consigliati (se vuoi che proceda dopo approvazione):
1. Inserire i testi pronti‑to‑paste nei file indicati sotto MEGAPLAN.  
2. Aggiornare il KB con clausole EC2/NTC esatte (TODO richiesto).  
3. Creare unit tests che consumano i fixtures numeric sopra.

---

Se vuoi, preparo ora le versioni finali complete (testo Markdown esteso pronto‑to‑paste) per entrambi i file e le salvo in MEGAPLAN — confermi che proceda?


Status: creating the core MEGAPLAN documents first (manifest, application report, CodeModule contract, and test plan). Next step: add config and source skeletons.

Summarized conversation history

Status: adding config + core skeletons for ntc2018 (calculation codes + module stubs). Next: add secondary_elements package and core adapters.

C:/workspaces/RD2229/RD2229/.venv/Scripts/python.exe -m pytest -q
✅ Implementazione completata (sessione unica)
Ho applicato tutte le modifiche approvate in CHAT_PLAN.md e ho creato/aggiornato i file PLAN‑ONLY richiesti (skeletons, SPEC, manifest, report e test‑placeholders).
Nessun valore normativo è stato inventato — tutti i punti non definiti restano marcati con TODO.

🔧 Cosa ho fatto (high level)
Creati i seguenti documenti principali:
MANIFEST_APPLICAZIONE.md (manifest delle azioni) ✅
APPLICATION_REPORT.md (report di applicazione) ✅
CodeModule_CONTRACT.md (contract SPEC) ✅
TEST_PLAN_NTC2018.md (test plan, golden cases placeholder) ✅
Aggiornata la GUI plan spec:
PLAN_GUI_SECONDARY_ELEMENTS.md — wire + file mapping (GUI thin) ✅
Creati skeleton (solo docstring / API / TODO) per:
config (NTC2018 JSONcode skeletons)
ntc2018 (package, CodeModule skeleton, checks stubs, secondary_elements package)
src/gui/secondary_elements/* (window, editor, results_view) + widgets
src/core/* adapters (combinations, materials) — SKELETONS
Aggiunti test‑placeholder in tests (unit + GUI + integration placeholders)
Verificato che i placeholder/TODO rimangono in tutti i punti dove il piano lo richiede (grep TODO eseguito)
Eseguiti i test: pytest eseguito con successo (placeholder tests → pass/skip). ✅
📁 File principali aggiunti / aggiornati
(vedi MANIFEST_APPLICAZIONE.md per elenco completo)

docs/MEGAPLAN/{MANIFEST_APPLICAZIONE.md, APPLICATION_REPORT.md, CodeModule_CONTRACT.md, TEST_PLAN_NTC2018.md}
NTC2018.jsoncode
secondary_elements.jsoncode
src/codes/ntc2018/* (skeletons)
src/gui/secondary_elements/{editor.py,window.py,results_view.py}
src/gui/widgets/{secondary_element_widgets.py,norm_selector.py}
tests/... (placeholders)
⚠️ Stato dei TODO (intenzionale)
Tutti i punti dove la normativa è assente o non approvata sono lasciati come TODO (es. V_Rd,c formula, w_max, golden numeric fixtures, NA coefficients).
CI / QA: suggerito job che scansiona docs/MEGAPLAN/*.md per token TODO|TBD (presenti e voluti).
✅ Verifiche eseguite
Test suite: pytest -q — OK (placeholder/skipped tests present).
Controllo TODO: confermato che le note e i TODO previsti restano nei file SPEC.
Nessun valore normativo inventato o inserito.
Prossimi passi raccomandati (priorità)
Assegnare owner per ciascun TODO (normative owners / structural engineer). 📌
Fornire golden numeric fixtures (update TEST_PLAN_NTC2018.md + tests). 🧪
Implementare i check reali a partire dai skeletons e trasformare i test‑placeholder in test effettivi. 🛠️
Aggiungere CI check per token TODO e coverage gates per i nuovi moduli. 🔁
Se vuoi, preparo subito:

la PR con titolo/descrizione + checklist e file MANIFEST_APPLICAZIONE.md/APPLICATION_REPORT.md collegati, oppure
converto uno o due placeholder test in test concreti se mi fornisci i golden values.
Dimmi quale azione preferisci: apro la PR adesso o primeggi con i TODO/golden fixtures?