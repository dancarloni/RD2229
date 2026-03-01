# Modulo: `utils`

## 1. Scopo e ambito

Utilities generali: `BackgroundExecutor` — wrapper ThreadPoolExecutor con callback scheduling per Tkinter.

## 2. Stato reale

**COMPLETO**

Motivazione oggettiva: `background.py` (76 righe) ha `BackgroundExecutor` con implementazione completa di `submit()`, `shutdown()`, callback scheduling via `widget.after()`. Test presenti.

## 3. Evidenze

- `src/utils/background.py` — `BackgroundExecutor` (76 righe); metodi `submit()`, `shutdown()` completi
- Test: `tests/test_background_executor.py` — importa e testa `BackgroundExecutor`

## 4. Input/parametri

- `BackgroundExecutor(widget, max_workers: int = 2)`
- `submit(fn: Callable, *args, callback: Callable | None = None)`

## 5. Output

- `None` — esecuzione asincrona; risultato consegnato tramite callback

## 6. Dipendenze

- `concurrent.futures.ThreadPoolExecutor` (stdlib)
- Tkinter `widget.after()` per callback scheduling

## 7. Fonti normative collegate

Nessuna.

## 8. Gap/TODO/Limitazioni

- Dipende da Tkinter per scheduling callback — non usabile senza widget Tkinter
- Nessun equivalente per Qt (UI moderna usa approccio diverso)

## 9. Next steps

- [ ] Considerare astrazione `BackgroundExecutor` che funzioni sia con Tkinter che con Qt
- [ ] Aggiungere test per caso `shutdown()` con task in corso
