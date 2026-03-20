# ARCHITECTURE_MATERIAL_GOVERNANCE.md

## Panoramica — Governance dei Coefficienti Normativi dei Materiali

Questo documento descrive l'architettura a 3 livelli di override per la gestione
centralizzata dei coefficienti normativi (γ_c, γ_s, γ_M, α_cc, n, ecc.) nel software RD2229.

**Riferimento piano di lavoro**: `docs/PIANO_LAVORO.md` § GUI-M
**Riferimento design editor**: `docs/MATERIAL_EDITOR_DESIGN.md` § 14

---

## Gerarchia 3-Level Override

```
Level 1 (Default normativo, immutabile nel repo)
  └── config/norms/<norma>.json
        Fonte di verità per ogni norma. Committato nel repo. Mai modificato manualmente.
        Contiene: gamma_c, gamma_s, gamma_M, alpha_cc, range min/max, formule.

Level 2 (Override globale utente)
  └── ~/.rd2229/config.json  →  campo: material_coefficients_overrides
        Impostabile da: File → Impostazioni → Scheda "Coefficienti normativi globali"
        Applicato a TUTTI i materiali di quella norma/famiglia.
        Resettabile per norma o globalmente.

Level 3 (Override per-materiale)
  └── campo nel dict materiale  →  es. "gamma_c": 1.70, "gamma_c_override": true
        Impostabile dal Material Editor (checkbox Override accanto al campo).
        Applicato SOLO al singolo materiale.
        Audit tracciabile: campo *_override = true nel dict.

Priorità di risoluzione (dal più alto al più basso):
  Level 3 > Level 2 > Level 1
```

### Flowchart: risoluzione di un coefficiente

```
MaterialConfigLoader.compute_derived(material, norm_schema, famiglia="calcestruzzo")
  │
  ├── Per ogni parametro_specifico (es. gamma_c):
  │     │
  │     ├── 1. material.get("gamma_c") → int/float?  →  USA Level 3
  │     │
  │     ├── 2. GlobalMaterialCoefficientsManager.get_coefficient(
  │     │         "NTC2018", "calcestruzzo", "gamma_c")
  │     │      → UserConfig.material_coefficients_overrides presente?  →  USA Level 2
  │     │
  │     └── 3. NormativeDefaultsLoader.get_material_coefficient(
  │               "NTC2018", "calcestruzzo", "gamma_c")
  │              → config/norms/NTC2018.json  →  USA Level 1 (default)
  │
  └── eval(formula, namespace)  →  valore derivato (es. E, f_cd, f_yd)
```

---

## Schema file `config/norms/<norma>.json`

```json
{
  "norm_key": "NTC2018",
  "norm_label": "NTC 2018 (D.M. 17/01/2018 + Circ. n.7/2019)",
  "norm_year": 2018,
  "riferimento": "D.M. 17 gennaio 2018 (G.U. n.42 del 20/02/2018)",
  "note": "...",
  "materiali": {
    "calcestruzzo": {
      "gamma_c": {
        "valore": 1.50,
        "label": "γ_c",
        "unita": "-",
        "descrizione": "Coefficiente parziale calcestruzzo (SLU)",
        "riferimento": "NTC2018 Tab.4.1.II"
      },
      "alpha_cc": { "valore": 0.85, "label": "α_cc", ... },
      "f_ck_min_MPa": 12,
      "f_ck_max_MPa": 90,
      "E_formula": "22000 * pow((f_ck / 10.197 + 8.0) / 10.0, 0.3) * 10.197"
    },
    "acciaio": {
      "gamma_s": { "valore": 1.15, "label": "γ_s", ... },
      ...
    },
    "muratura": {
      "gamma_M": { "valore": 2.00, "label": "γ_M", ... }
    }
  }
}
```

**Norme disponibili**: NTC2018, NTC2008, OPCM3274, DM96, DM92, DM72, Circ81, RD2229

---

## Schema campo `~/.rd2229/config.json` (Level 2)

```json
{
  "theme": "light",
  "default_norm_code": "NTC2018",
  "material_coefficients_overrides": {
    "NTC2018": {
      "calcestruzzo": {
        "gamma_c": 1.60,
        "alpha_cc": 0.90
      },
      "acciaio": {
        "gamma_s": 1.20
      }
    },
    "DM96": {
      "calcestruzzo": {
        "gamma_c": 1.65
      }
    }
  }
}
```

---

## Moduli implementati

| Modulo | Responsabilità |
|--------|---------------|
| `src/core/normative_defaults.py` | `NormativeDefaultsLoader` — carica `config/norms/*.json`, cache, query |
| `src/core/material_global_config.py` | `GlobalMaterialCoefficientsManager` — merge Level 1+2, set/reset override |
| `src/core/user_config.py` | `UserConfig` — persiste `material_coefficients_overrides` in `~/.rd2229/config.json` |
| `src/ui/qt/material_editor/logic/material_config.py` | `MaterialConfigLoader.compute_derived()` — applica gerarchia nel namespace eval |
| `src/ui/qt/settings/material_coefficients_settings_widget.py` | UI per impostazioni coefficienti globali (tab in Impostazioni) |

---

## API Usage Examples

```python
# --- Level 1: leggere un default normativo ---
from src.core.normative_defaults import NormativeDefaultsLoader

loader = NormativeDefaultsLoader.instance()
gamma_c = loader.get_material_coefficient("NTC2018", "calcestruzzo", "gamma_c")
# → 1.50

# --- Level 2: impostare un override globale ---
from src.core.material_global_config import GlobalMaterialCoefficientsManager

mgr = GlobalMaterialCoefficientsManager.instance()
mgr.set_coefficient_override("NTC2018", "calcestruzzo", "gamma_c", 1.60)
# Persiste in ~/.rd2229/config.json

# --- Level 2: leggere con sorgente ---
val, source = mgr.get_coefficient_with_source("NTC2018", "calcestruzzo", "gamma_c")
# → (1.60, "override")

# --- Reset a default ---
mgr.reset_coefficient_to_default("NTC2018", "calcestruzzo", "gamma_c")
# → gamma_c torna a 1.50

# --- Build namespace per formula eval ---
ns = mgr.build_formula_namespace("NTC2018", "calcestruzzo")
# → {"gamma_c": 1.50, "alpha_cc": 0.85, ...}

# --- Calcolo derivati con gerarchia ---
from src.ui.qt.material_editor.logic.material_config import MaterialConfigLoader

derived = MaterialConfigLoader.compute_derived(
    material={"f_ck": 254.9, "nu": 0.2},
    norm_schema=MaterialConfigLoader.get_norm_schema("calcestruzzo", "NTC2018"),
    famiglia="calcestruzzo",
)
# → {"E": ..., "f_cd": ..., "f_ctm": ..., "_formula_warnings": []}
```

---

## Come aggiungere una nuova norma

1. Creare `config/norms/<NUOVA_NORMA>.json` seguendo lo schema sopra
2. Il file viene rilevato automaticamente da `NormativeDefaultsLoader.get_all_norms()`
3. Il tab corrispondente appare automaticamente in Impostazioni → Coefficienti normativi globali
4. Aggiungere la norma in `config/materials/<famiglia>_config.json` nella sezione `norme`

## Come aggiungere un nuovo coefficiente a una norma

1. Aggiungere la voce nel file `config/norms/<norma>.json` sotto il blocco `materiali/<famiglia>`
2. Il coefficiente appare automaticamente nel widget settings come spin box
3. Il `GlobalMaterialCoefficientsManager` lo espone via `get_coefficient()`
4. Aggiungere il coefficiente come `parametri_specifici` in `config/materials/<famiglia>_config.json`
   perché venga incluso nel namespace di eval delle formule

---

## Validazione normativa

I valori inseriti dall'utente sono validati su tre livelli:

1. **Range** — da `config/materials/<famiglia>_config.json` campo `validation.{min,max}`
2. **Coerenza** — `validate_coherence()` in `material_validation_logic.py` (es. f_cd ≤ f_ck)
3. **Normativa** — `validate_normative()` in `material_validation_logic.py` (tabelle per norma)

La validazione è integrata in `MaterialEditorController.on_save_clicked()`:
- Errori → bloccano il salvataggio
- Warning → chiedono conferma all'utente

---

*Generato automaticamente — aggiornare contestualmente alle modifiche ai moduli di governance.*
