# Modulo: `domain`

## 1. Scopo e ambito

Modelli di dominio: `VerificationInput`, funzioni di accesso alle proprietà di calcestruzzo/acciaio e alla geometria di sezione.

## 2. Stato reale

**PARZIALE**

Motivazione oggettiva: `models.py`, `materials.py`, `sections.py` hanno logica reale. Tuttavia i test `tests/test_domain_materials.py` e `tests/test_domain_sections.py` importano da `verification_table` (root-level), NON da `src.domain`. Il modulo non è testato direttamente tramite il suo percorso di importazione.

## 3. Evidenze

- `src/domain/domain/models.py` — `VerificationInput` dataclass (100 righe)
- `src/domain/domain/materials.py` — `get_concrete_properties()`, `get_steel_properties()` (77 righe)
- `src/domain/domain/sections.py` — `get_section_geometry()` (96 righe)
- I test `tests/test_domain_*.py` usano percorso root-level, non `src.domain`

## 4. Input/parametri

- `get_concrete_properties(fck: float, norm_code: str) -> ConcreteProps`
- `get_steel_properties(fyk: float) -> SteelProps`
- `get_section_geometry(section_id: str) -> SectionGeometry`

## 5. Output

- Dataclass di proprietà materiali e geometria sezione

## 6. Dipendenze

- Repository materiali/sezioni (TBD — dipendenza esatta non verificata)

## 7. Fonti normative collegate

Nessuna trovata come stringa nel codice del modulo.

## 8. Gap/TODO/Limitazioni

- Percorso di importazione `src.domain.domain.*` è confuso (cartella annidata)
- Test non usano `src.domain` come percorso di import → rischio di disallineamento
- Dipendenza da repository materiali non chiara

## 9. Next steps

- [ ] Verificare se `src/domain/domain/` è intenzionale o artefatto di migrazione
- [ ] Riscrivere test `test_domain_*.py` per importare da `src.domain`
- [ ] Documentare la dipendenza dal repository materiali
