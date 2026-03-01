# Modulo: `tests` (src/tests/)

## 1. Scopo e ambito

Test co-locati in `src/tests/` per i moduli STUB S2: smoke test minimali per verificare che le classi/funzioni stub esistano e abbiano la firma attesa.

## 2. Stato reale

**PARZIALE**

Motivazione oggettiva: 7 file di test reali con assertion. Tutti esplicitamente marcati STUB S2. Verificano solo struttura (smoke) dei moduli stub. Non eseguono calcoli reali.

## 3. Evidenze

- `src/tests/test_shear_area.py` (51 righe) — importa `compute_shear_area`, verifica fallback
- `src/tests/test_material_repo.py` (25 righe) — importa `Material`, `MaterialRepository`
- `src/tests/test_elements_repo.py` (18 righe) — importa `Element`, `ElementRepository`
- `src/tests/test_code_routing.py` (24 righe) — importa `get_code`, `register_code`
- `src/tests/test_reporting.py` (22 righe) — importa renderer HTML/MD
- `src/tests/test_resolve_inputs.py` (29 righe) — importa `resolve_verification_inputs`
- `src/tests/__init__.py` — 6 righe, marcato STUB S2

## 4. Input/parametri

N/A — modulo di test.

## 5. Output

N/A — risultati pytest.

## 6. Dipendenze

- `src/calc`, `src/materials`, `src/elements`, `src/codes`, `src/report` — tutti STUB

## 7. Fonti normative collegate

Nessuna.

## 8. Gap/TODO/Limitazioni

- Solo smoke test per stub — nessun test funzionale
- Non aggiornati man mano che le implementazioni progrediscono
- Separati dalla suite principale `tests/`

## 9. Next steps

- [ ] Aggiornare i test in `src/tests/` quando le implementazioni diventano reali
- [ ] Valutare se migrare i test in `tests/` per uniformità
- [ ] Aggiungere assertion su valori attesi (non solo smoke)
