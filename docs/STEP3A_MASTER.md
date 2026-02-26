# STEP 3A — Consolidamento Normativo (MASTER)

## Scopo dello STEP 3A
Lo STEP 3A consolida il **Kernel Normativo** del software di calcolo strutturale.
Questo step **non introduce nuove feature ingegneristiche**, ma costruisce le fondamenta
necessarie per supportare:

- più normative (NTC2018, EC8, DM92, DM96, RD2229/39) (modern + legacy);
- metodi molto diversi (spettro, forze di piano, modelli legacy);
- tracciabilità e auditabilità completa e difendibilità tecnico‑legale;
- estendibile per evoluzioni future anche radicali delle norme legacy.

## Principi guida
- separazione **Norma / Metodo / Policy**
- output sempre tracciato (`TraceRecord`)
- norme legacy trattate come **moduli isolati**
- modifiche future = nuovi file, non patch invasive

## Struttura documentale
- `ARCH_NORMATIVE_KERNEL.md` → architettura generale
- `NORMATIVE_CAPABILITIES.md` → cosa sa fare ogni norma
- `LEGACY_CODES/` → documentazione norme storiche
  - `RD2229_39/` → modulo legacy completamente isolato

## Stato di completamento
Lo STEP 3A è **DONE** quando:
- il kernel distingue codice, metodo e policy;
- RD2229/39 è presente come modulo documentato e sostituibile;
- le azioni ondulatorie e sussultorie sono concettualmente modellate;
- esistono roadmap e ADR per future modifiche.

## Output attesi
- matrice capabilities per normative e metodi;
- documentazione legacy RD2229/39 (metodi/policy/trace/ADR/roadmap);
- strumenti VS Code per test rapidi.

## Done criteria
- Documentazione presente e coerente.
- VS Code task per `pytest -q` disponibili.
- README aggiornato con sezione STEP 3A.

## Step successivi previsti
- STEP 4: implementazione completa dei metodi legacy (RD2229/39, DM92, DM96) su kernel consolidato.
- STEP 5: periodi propri e modelli dinamici
- STEP 6: esposizione completa dei parametri in GUI
