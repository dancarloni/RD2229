"""Caricatore dei valori predefiniti normativi per materiali strutturali.

Gestisce il livello 1 della gerarchia di governance materiali:
  Level 1 (Default): config/norms/<norma>.json — immutabile, nel repo
  Level 2 (Global):  ~/.rd2229/config.json        — override utente globale
  Level 3 (Per-mat): campo nel materiale            — override singolo materiale

Riferimento architettura: docs/ARCHITECTURE_MATERIAL_GOVERNANCE.md
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Directory contenente i file JSON per norma (relativa alla radice del repo)
_DEFAULT_NORMS_DIR = Path(__file__).parent.parent.parent / "config" / "norms"


class NormativeDefaultsLoader:
    """Singleton che carica e gestisce i defaults normativi da config/norms/.

    Uso tipico::

        loader = NormativeDefaultsLoader.instance()
        gamma_c = loader.get_material_coefficient("NTC2018", "calcestruzzo", "gamma_c")
        # → 1.50

    I valori sono caricati in modo lazy (al primo accesso) e cachati.
    Chiamare :meth:`reload` per invalidare la cache (utile nei test).
    """

    _instance: NormativeDefaultsLoader | None = None

    def __init__(self, norms_dir: Path | str | None = None) -> None:
        self._norms_dir = Path(norms_dir) if norms_dir else _DEFAULT_NORMS_DIR
        self._cache: dict[str, dict] = {}

    # ------------------------------------------------------------------
    # Singleton
    # ------------------------------------------------------------------

    @classmethod
    def instance(cls, norms_dir: Path | str | None = None) -> "NormativeDefaultsLoader":
        """Restituisce l'istanza singleton (creandola se necessario)."""
        if cls._instance is None:
            cls._instance = cls(norms_dir=norms_dir)
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Resetta il singleton (utile nei test)."""
        cls._instance = None

    # ------------------------------------------------------------------
    # Caricamento
    # ------------------------------------------------------------------

    def load_norm_defaults(self, norm_key: str) -> dict:
        """Carica e restituisce il dizionario completo per una norma.

        Il risultato è cachato; usare :meth:`reload` per forzare il ricaricamento.

        Args:
            norm_key: Chiave norma (es. "NTC2018", "DM96", "RD2229").

        Returns:
            Dizionario con struttura ``{"norm_key": ..., "materiali": {...}}``.
            Dizionario vuoto se il file non esiste.
        """
        if norm_key in self._cache:
            return self._cache[norm_key]

        path = self._norms_dir / f"{norm_key}.json"
        if not path.exists():
            logger.warning("File norma non trovato: %s", path)
            self._cache[norm_key] = {}
            return {}

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            self._cache[norm_key] = data
            logger.debug("Norma '%s' caricata da %s", norm_key, path)
            return data
        except Exception as exc:
            logger.error("Errore lettura norma '%s': %s", norm_key, exc)
            self._cache[norm_key] = {}
            return {}

    def reload(self, norm_key: str | None = None) -> None:
        """Invalida la cache.

        Args:
            norm_key: Se fornito, invalida solo quella norma. Altrimenti tutte.
        """
        if norm_key is not None:
            self._cache.pop(norm_key, None)
        else:
            self._cache.clear()

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def get_all_norms(self) -> list[str]:
        """Restituisce la lista di chiavi norma disponibili (da file .json in norms_dir)."""
        if not self._norms_dir.exists():
            return []
        return sorted(p.stem for p in self._norms_dir.glob("*.json"))

    def get_norm_label(self, norm_key: str) -> str:
        """Restituisce l'etichetta leggibile della norma."""
        data = self.load_norm_defaults(norm_key)
        return data.get("norm_label", norm_key)

    def get_material_defaults(self, norm_key: str, famiglia: str) -> dict:
        """Restituisce il blocco parametri per una famiglia di materiali in una norma.

        Args:
            norm_key: Es. "NTC2018".
            famiglia: Es. "calcestruzzo", "acciaio", "muratura".

        Returns:
            Dizionario con i parametri (coefficienti, formule, limiti range, ecc.).
            Dizionario vuoto se non trovato.
        """
        data = self.load_norm_defaults(norm_key)
        return data.get("materiali", {}).get(famiglia, {})

    def get_material_coefficient(
        self, norm_key: str, famiglia: str, coeff_key: str
    ) -> Any:
        """Restituisce il valore di un coefficiente normativo.

        Il coefficiente può essere:
        - Un dict con campo ``"valore"`` (es. ``{"valore": 1.50, "label": "γ_c"}``)
        - Un valore scalare diretto (int, float, str)

        Args:
            norm_key: Es. "NTC2018".
            famiglia: Es. "calcestruzzo".
            coeff_key: Chiave coefficiente (es. "gamma_c", "alpha_cc").

        Returns:
            Valore numerico/stringa del coefficiente, o ``None`` se non trovato.

        Example::

            loader.get_material_coefficient("NTC2018", "calcestruzzo", "gamma_c")
            # → 1.50
        """
        mat_defaults = self.get_material_defaults(norm_key, famiglia)
        raw = mat_defaults.get(coeff_key)
        if raw is None:
            return None
        if isinstance(raw, dict) and "valore" in raw:
            return raw["valore"]
        return raw

    def get_coefficient_metadata(
        self, norm_key: str, famiglia: str, coeff_key: str
    ) -> dict:
        """Restituisce metadati completi del coefficiente (label, unita, descrizione, ecc.).

        Returns:
            Dizionario con chiavi opzionali: ``label``, ``unita``, ``descrizione``, ``valore``, ``riferimento``.
            Dizionario vuoto se non trovato.
        """
        mat_defaults = self.get_material_defaults(norm_key, famiglia)
        raw = mat_defaults.get(coeff_key)
        if raw is None:
            return {}
        if isinstance(raw, dict):
            return raw
        return {"valore": raw}

    def list_coefficients(self, norm_key: str, famiglia: str) -> list[str]:
        """Restituisce la lista di chiavi coefficienti per norma/famiglia.

        Restituisce solo le chiavi il cui valore è un dict con campo "valore" o uno scalare numerico
        (esclude campi formula/formula_string, note, ecc.).
        """
        mat_defaults = self.get_material_defaults(norm_key, famiglia)
        result = []
        for k, v in mat_defaults.items():
            if isinstance(v, dict) and "valore" in v:
                result.append(k)
            elif isinstance(v, (int, float)) and not k.endswith(("_min", "_max", "_formula")):
                result.append(k)
        return result
