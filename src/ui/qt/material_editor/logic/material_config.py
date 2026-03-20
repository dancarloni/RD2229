"""
MaterialConfigLoader — carica e gestisce i file di configurazione materiali.

File JSON in config/materials/:
  families.json                  — lista famiglie
  <famiglia>_config.json         — schema norma/parametri/formule per famiglia

Le formule nei parametri derivati sono stringhe Python eval-safe.
Namespace disponibile: campi input del materiale + parametri_specifici della norma
+ funzioni matematiche (sqrt, pow, sin, cos, tan, log, exp, pi, abs, round).
"""

from __future__ import annotations

import json
import math
import pathlib
from typing import Any, Dict, List, Optional

# ── namespace sicuro per eval delle formule ────────────────────────────────────
_FORMULA_NAMESPACE: Dict[str, Any] = {
    "__builtins__": {},
    "sqrt": math.sqrt,
    "pow": pow,
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "log": math.log,
    "log10": math.log10,
    "exp": math.exp,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "pi": math.pi,
    "floor": math.floor,
    "ceil": math.ceil,
    "inf": math.inf,
}


def _find_config_dir() -> pathlib.Path:
    """Risale le directory finché trova config/materials/."""
    here = pathlib.Path(__file__).resolve()
    root = here
    while not (root / "config" / "materials").is_dir() and root.parent != root:
        root = root.parent
    return root / "config" / "materials"


class MaterialConfigLoader:
    """Singleton-like loader con cache; chiama `reload()` per invalidare."""

    _config_dir: Optional[pathlib.Path] = None
    _families_cache: Optional[List[Dict[str, Any]]] = None
    _schemas_cache: Dict[str, Dict[str, Any]] = {}

    # ── config dir ─────────────────────────────────────────────────────────────

    @classmethod
    def config_dir(cls) -> pathlib.Path:
        if cls._config_dir is None:
            cls._config_dir = _find_config_dir()
        return cls._config_dir

    # ── famiglie ───────────────────────────────────────────────────────────────

    @classmethod
    def load_families(cls) -> List[Dict[str, Any]]:
        """Carica families.json → [{"key": ..., "label": ...}, ...]."""
        if cls._families_cache is None:
            path = cls.config_dir() / "families.json"
            with open(path, "r", encoding="utf-8") as fh:
                cls._families_cache = json.load(fh)
        return cls._families_cache

    # ── schema famiglia ────────────────────────────────────────────────────────

    @classmethod
    def load_schema(cls, famiglia: str) -> Dict[str, Any]:
        """Carica <famiglia>_config.json (con cache)."""
        if famiglia not in cls._schemas_cache:
            path = cls.config_dir() / f"{famiglia}_config.json"
            with open(path, "r", encoding="utf-8") as fh:
                cls._schemas_cache[famiglia] = json.load(fh)
        return cls._schemas_cache[famiglia]

    @classmethod
    def save_schema(cls, famiglia: str, schema: Dict[str, Any]) -> None:
        """Salva schema modificato su disco e aggiorna cache."""
        path = cls.config_dir() / f"{famiglia}_config.json"
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(schema, fh, indent=2, ensure_ascii=False)
        cls._schemas_cache[famiglia] = schema

    # ── norme per famiglia ─────────────────────────────────────────────────────

    @classmethod
    def get_norms_for_family(cls, famiglia: str) -> List[Dict[str, Any]]:
        """Restituisce le norme attive per una famiglia."""
        try:
            schema = cls.load_schema(famiglia)
            return [n for n in schema.get("norme", []) if n.get("attiva", True)]
        except Exception:
            return []

    @classmethod
    def get_norm_schema(cls, famiglia: str | None, norma: str | None) -> Optional[Dict[str, Any]]:
        """Restituisce lo schema norma o None se non trovato."""
        if not famiglia or not norma:
            return None
        try:
            for n in cls.get_norms_for_family(famiglia):
                if n.get("key") == norma:
                    return n
        except Exception:
            pass
        return None

    # ── calcolo derivati ───────────────────────────────────────────────────────

    @classmethod
    def compute_derived(
        cls,
        material: Dict[str, Any],
        norm_schema: Dict[str, Any],
        overrides: Optional[Dict[str, bool]] = None,
    ) -> Dict[str, Any]:
        """
        Calcola tutti i parametri derivati per un materiale dato lo schema norma.

        I parametri con override=True vengono mantenuti invariati.
        I parametri derivati vengono processati in ordine (supporta dipendenze a catena).

        Returns:
            dict con {key: valore_calcolato} — solo campi non-override.
        """
        if overrides is None:
            overrides = {}

        # Namespace di valutazione: copia sicura delle funzioni math
        ns: Dict[str, Any] = dict(_FORMULA_NAMESPACE)

        # Aggiungi i parametri_specifici dalla norma (default, a meno che il
        # materiale non li sovrascriva esplicitamente)
        for pkey, pinfo in norm_schema.get("parametri_specifici", {}).items():
            if isinstance(pinfo, dict):
                mat_val = material.get(pkey)
                ns[pkey] = (
                    float(mat_val)
                    if isinstance(mat_val, (int, float))
                    else float(pinfo.get("valore", 1.0))
                )
            elif isinstance(pinfo, (int, float)):
                ns[pkey] = float(pinfo)

        # Aggiungi i valori dei campi input del materiale
        for field in norm_schema.get("parametri_input", []):
            key = field["key"]
            val = material.get(key)
            if val is None:
                # usa default dallo schema se il materiale non ha il valore
                val = field.get("default", 0.0)
            if isinstance(val, (int, float)):
                ns[key] = float(val)

        # Calcola i derivati in ordine (catena supportata)
        results: Dict[str, Any] = {}
        warnings: List[str] = []

        for field in norm_schema.get("parametri_derivati", []):
            key = field["key"]
            formula = field.get("formula", "").strip()
            if not formula:
                continue

            # Se override attivo, usa il valore già salvato nel materiale
            if overrides.get(key) or material.get(f"{key}_override", False):
                existing = material.get(key)
                if isinstance(existing, (int, float)):
                    ns[key] = float(existing)
                continue

            try:
                result = eval(formula, {"__builtins__": {}}, ns)  # noqa: S307
                result = float(result)
                ns[key] = result  # disponibile per formule successive
                results[key] = round(result, 6)
            except Exception as exc:
                warnings.append(f"{key}: errore formula ({exc})")

        results["_formula_warnings"] = warnings  # type: ignore[assignment]
        return results

    # ── utilità ────────────────────────────────────────────────────────────────

    @classmethod
    def reload(cls) -> None:
        """Invalida tutte le cache e ricarica da disco alla prossima richiesta."""
        cls._families_cache = None
        cls._schemas_cache = {}
        cls._config_dir = None

    @classmethod
    def get_all_norm_keys(cls) -> List[str]:
        """Restituisce tutte le chiavi norma disponibili (unione di tutte le famiglie)."""
        keys: set[str] = set()
        for fam in cls.load_families():
            for n in cls.get_norms_for_family(fam["key"]):
                keys.add(n["key"])
        return sorted(keys)
