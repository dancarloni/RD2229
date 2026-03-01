# Modulo: `actions`

## 1. Scopo e ambito

TBD — nessuna docstring di modulo trovata in `src/actions/__init__.py` o `src/actions/action_repo.py`.  
Dal codice: contiene `VerificationAction`, `ActionRepository`, esempi stub (`FlexureCheckAction`). Sembra destinato a rappresentare azioni di verifica strutturale come oggetti eseguibili.

## 2. Stato reale

**STUB**

Motivazione oggettiva: `src/actions/action_repo.py` è esplicitamente marcato "STUB S2". Il metodo `VerificationAction.run()` contiene `raise NotImplementedError("Azione di verifica non implementata.")`. Tutti i metodi di `ActionRepository` hanno corpo `# TODO`.

## 3. Evidenze

- `src/actions/action_repo.py` — ~160 righe; "STUB S2" dichiarato
- `src/actions/action_repo.py:run()` → `raise NotImplementedError`
- Nessun import da altri moduli attivi

## 4. Input/parametri

TBD — firma `run(self, inputs: dict) -> dict` vista nel codice ma nessuno schema validato.

## 5. Output

TBD — `run()` dovrebbe restituire `dict` ma non implementato.

## 6. Dipendenze

- `src/actions/__init__.py` — re-esporta da `action_repo`
- Nessuna dipendenza da altri moduli `src/`

## 7. Fonti normative collegate

Nessuna trovata nel codice del modulo.

## 8. Gap/TODO/Limitazioni

- Tutti i metodi sono TODO/NotImplementedError
- Nessun test
- Nessun entry point attivo

## 9. Next steps

- [ ] Implementare `VerificationAction.run()` con logica concreta
- [ ] Aggiungere test unitari per `ActionRepository`
- [ ] Collegare al dispatcher in `src/methods/verification/`
