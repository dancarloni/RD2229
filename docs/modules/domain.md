# Documentazione Modulo: `domain`

> **Generato automaticamente** da `tools/generate_module_docs.py` — 2026-03-01 00:52 UTC
> Stub iniziale: compilare manualmente le sezioni TBD.
> Non eliminare questo file; aggiornarlo incrementalmente.

---

## 1. Identificazione

| Campo | Valore |
|-------|--------|
| **Nome modulo** | `domain` |
| **Path** | `src/domain` |
| **Tipo** | package |
| **File .py rilevati** | 5 |
| **Stato** | PARZIALE |
| **Maintainer** | TBD |
| **Ultima revisione** | 2026-03-01 |

---

## 2. Scopo

Modelli di dominio: `VerificationInput`, funzioni di accesso alle proprietà di calcestruzzo/acciaio e alla geometria di sezione.

---

## 3. Evidenze

- `src/domain/domain/models.py` — `VerificationInput` dataclass (100 righe)
- `src/domain/domain/materials.py` — `get_concrete_properties()`, `get_steel_properties()` (77 righe)
- `src/domain/domain/sections.py` — `get_section_geometry()` (96 righe)
- I test `tests/test_domain_*.py` usano percorso root-level, non `src.domain`

---

## 4. Input / Output

| Direzione | Formato | Descrizione |
|-----------|---------|-------------|
| Input | `get_concrete_properties(fck: float, norm_code: str) -> ConcreteProps` | Proprietà calcestruzzo |
| Input | `get_steel_properties(fyk: float) -> SteelProps` | Proprietà acciaio |
| Input | `get_section_geometry(section_id: str) -> SectionGeometry` | Geometria sezione |
| Output | Dataclass | Proprietà materiali e geometria sezione |

---

## 5. Test correlati

| File test | Copertura stimata | Note |
|-----------|-------------------|------|
| `tests/test_domain_materials.py` | TBD | — |
| `tests/test_domain_sections.py` | TBD | — |

---

## 6. Fonti normative

Nessuna trovata come stringa nel codice del modulo. TODO: aggiungere riferimenti se identificati.

---

## 7. Dipendenze interne

- Repository materiali/sezioni (TBD — dipendenza esatta non verificata)

---

## 8. Gap / TODO / Limitazioni

- Percorso di importazione `src.domain.domain.*` è confuso (cartella annidata)
- Test non usano `src.domain` come percorso di import → rischio di disallineamento
- Dipendenza da repository materiali non chiara

---

## 9. Next steps

- [ ] Verificare se `src/domain/domain/` è intenzionale o artefatto di migrazione
- [ ] Riscrivere test `test_domain_*.py` per importare da `src.domain`
- [ ] Documentare la dipendenza dal repository materiali
- [ ] Compilare sezioni TBD
