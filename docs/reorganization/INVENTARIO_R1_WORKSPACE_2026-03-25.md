---
title: Inventario R1 Workspace RD2229
date: 2026-03-25
phase: R1
author: GitHub Copilot
related:
  - docs/reorganization/MASTERPLAN_RISTRUTTURAZIONE_WORKSPACE_2026-03-25.md
  - docs/PIANO_LAVORO.md
  - docs/PIANO_LAVORO_GUI.md
---

# Inventario R1 Workspace 2026-03-25

## 1. Scopo

Documentare la classificazione iniziale dei contenuti root e indicare le azioni
keep/move/archive/delete-progressive eseguite o pianificate.

## 2. Regole di classificazione usate

- KEEP: contenuto attivo, sorgente o governance corrente.
- MOVE: contenuto valido ma collocato in area non corretta.
- ARCHIVE: contenuto storico informativo, non operativo.
- DELETE-PROGRESSIVE: contenuto legacy da eliminare per fasi dopo verifica riferimenti.

## 3. Azioni eseguite (R1-R2 iniziale)

| Categoria | Elemento | Azione |
|---|---|---|
| Demo progetto | 00_Progetto_di_test.jsonp (+ backup/migrated) | MOVE -> examples/projects |
| Report demo | 00_Progetto_di_test_report.html/.md | MOVE -> examples/reports |
| Output CI | ci_pytest_report.xml | MOVE -> docs/generated/ci |
| Riferimenti docs | README comandi avvio demo | UPDATE path |
| Governance repo | .gitignore | UPDATE per artifact CI XML |
| Sessioni storiche | Session_*.md | MOVE -> docs/archived/session_notes |
| Blocchi lavoro | BLOCCO 01..12.txt | MOVE -> docs/archived/session_notes |
| Summary storico | COMPLETAMENTO_TASK.md | MOVE -> docs/archived/summaries |
| Planning storico | Plan_master*.md, PLANCODE.md | MOVE -> docs/archived/planning |
| Compatibilita transitoria | Plan_master*.md, PLANCODE.md | STUB in root |

## 4. Classificazione sintetica root (delta)

### 4.1 KEEP (attivo)

- src/, tests/, data/, config/, scripts/, docs/
- README.md, pyproject.toml, pytest.ini, requirements*.txt
- docs/PIANO_LAVORO.md, docs/PIANO_LAVORO_GUI.md

### 4.2 MOVE (prossime tranche)

- Session_*.md -> docs/archived/session_notes/
- BLOCCO 01..12.txt -> docs/archived/session_notes/
- COMPLETAMENTO_TASK.md -> docs/archived/summaries/
- Plan_master*.md, PLANCODE.md -> docs/archived/planning/
- output vari *.txt tecnici da root -> docs/generated/ o docs/archived/ in base al contenuto

### 4.3 ARCHIVE (prossime tranche)

- report storici non operativi in root
- note di migrazione obsolete duplicate
- snapshot di struttura e tree dump storici

### 4.4 DELETE-PROGRESSIVE (con checklist)

- componenti Tkinter non piu necessari in deprecated/ e legacy/
- entrypoint/selector obsoleti, dopo completamento GUI centrale
- tests_legacy non piu giustificati dal prodotto attivo

## 5. Rischi rilevati in R1

1. Diversi documenti storici contengono riferimenti ai file root pre-migrazione.
2. Le evidenze storiche in docs/MEGAPLAN e report legacy possono restare non allineate ai path attuali.
3. Prima di migrare i blocchi sessione conviene introdurre una policy esplicita per i link storici.

## 6. Prossimo step operativo immediato

1. Classificare e migrare i restanti file root candidati (summary/report/output).
2. Avviare R3: indice documentale per temi (`docs/architecture`, `docs/gui`, `docs/modules`, `docs/audit`, `docs/archived`).
3. Definire backlog R4 di split servizi da `src/ui/modern/services/__init__.py`.
4. Progettare schema registry esteso per dashboard card-based e factory widget.
