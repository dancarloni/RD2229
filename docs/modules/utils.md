<<<<<<< HEAD

# Modulo: `utils`

## 1. Scopo e ambito

Utilities generali: `BackgroundExecutor` — wrapper ThreadPoolExecutor con callback scheduling per Tkinter.

## 2. Stato reale

**COMPLETO**

Motivazione oggettiva: `background.py` (76 righe) ha `BackgroundExecutor` con implementazione completa di `submit()`, `shutdown()`, callback scheduling via `widget.after()`. Test presenti.

## 3. Evidenze

- `src/utils/background.py` — `BackgroundExecutor` (76 righe); metodi `submit()`, `shutdown()` completi
- Test: `tests/test_background_executor.py` — importa e testa `BackgroundExecutor`

# Documentazione Modulo: `utils`

> **Generato automaticamente** da `tools/generate_module_docs.py` — 2026-03-01 00:52 UTC
> Stub iniziale: compilare manualmente le sezioni TBD.
> Non eliminare questo file; aggiornarlo incrementalmente.

---

## 1. Identificazione

| Campo | Valore |
|-------|--------|
| **Nome modulo** | `utils` |
| **Path** | `src/utils` |
| **Tipo** | package |
| **File .py rilevati** | 2 |
| **Stato** | COMPLETO |
| **Maintainer** | TBD |
| **Ultima revisione** | 2026-03-01 |

---

## 2. Scopo e ambito

Utilities generali: `BackgroundExecutor` — wrapper ThreadPoolExecutor con callback scheduling per Tkinter.

---

## 3. Stato reale

**COMPLETO**

Motivazione oggettiva: `background.py` (76 righe) ha `BackgroundExecutor` con implementazione completa di `submit()`, `shutdown()`, callback scheduling via `widget.after()`. Test presenti.

---

## 4. Evidenze

- `src/utils/background.py` — `BackgroundExecutor` (76 righe); metodi `submit()`, `shutdown()` completi
- Test: `tests/test_background_executor.py` — importa e testa `BackgroundExecutor`

---

## 5. Input/parametri

- `BackgroundExecutor(widget, max_workers: int = 2)`
- `submit(fn: Callable, *args, callback: Callable | None = None)`

---

## 6. Output

- `None` — esecuzione asincrona; risultato consegnato tramite callback

---

## 7. Dipendenze

- `concurrent.futures.ThreadPoolExecutor` (stdlib)
- Tkinter `widget.after()` per callback scheduling

---

## 8. Fonti normative collegate

Nessuna.

---

## 9. Gap/TODO/Limitazioni

- Dipende da Tkinter per scheduling callback — non usabile senza widget Tkinter
- Nessun equivalente per Qt (UI moderna usa approccio diverso)

---

## 10. Next steps

- [ ] Considerare astrazione `BackgroundExecutor` che funzioni sia con Tkinter che con Qt
- [ ] Aggiungere test per caso `shutdown()` con task in corso
|-----------|-------------------|------|
