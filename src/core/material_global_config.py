"""Gestore globale dei coefficienti normativi per i materiali strutturali.

Implementa il livello 2 della gerarchia di governance materiali:

  Level 1 — Default normativo (``config/norms/<norma>.json``, immutabile nel repo)
  Level 2 — Override globale utente (``~/.rd2229/config.json``, modificabile in Impostazioni)
  Level 3 — Override per-materiale (campo nel dict materiale, modificabile nel Material Editor)

Questo modulo gestisce il merge Level 1 + Level 2.
Il Level 3 viene applicato dal Material Editor stesso al momento della visualizzazione/salvataggio.

Riferimento architettura: docs/ARCHITECTURE_MATERIAL_GOVERNANCE.md
"""

from __future__ import annotations

import logging
from typing import Any

from .normative_defaults import NormativeDefaultsLoader
from .user_config import UserConfig

logger = logging.getLogger(__name__)


class GlobalMaterialCoefficientsManager:
    """Singleton che espone i coefficienti normativi con override globali applicati.

    Flusso di risoluzione coefficiente::

        get_coefficient("NTC2018", "calcestruzzo", "gamma_c")
          1. Cerca in UserConfig.material_coefficients_overrides["NTC2018"]["calcestruzzo"]["gamma_c"]
          2. Se non trovato, cerca in NormativeDefaultsLoader Level 1
          3. Se non trovato, restituisce None

    Uso tipico::

        mgr = GlobalMaterialCoefficientsManager.instance()
        gamma_c = mgr.get_coefficient("NTC2018", "calcestruzzo", "gamma_c")
        # → 1.50 (default) oppure valore override utente

        mgr.set_coefficient_override("NTC2018", "calcestruzzo", "gamma_c", 1.60)
        gamma_c = mgr.get_coefficient("NTC2018", "calcestruzzo", "gamma_c")
        # → 1.60

        mgr.reset_coefficient_to_default("NTC2018", "calcestruzzo", "gamma_c")
        gamma_c = mgr.get_coefficient("NTC2018", "calcestruzzo", "gamma_c")
        # → 1.50 (torna al default)
    """

    _instance: GlobalMaterialCoefficientsManager | None = None

    def __init__(
        self,
        user_config: UserConfig | None = None,
        loader: NormativeDefaultsLoader | None = None,
        user_config_path: str | None = None,
    ) -> None:
        self._loader = loader or NormativeDefaultsLoader.instance()
        self._user_config_path = user_config_path
        if user_config is not None:
            self._cfg = user_config
        else:
            self._cfg = UserConfig.load(path=user_config_path)

    # ------------------------------------------------------------------
    # Singleton
    # ------------------------------------------------------------------

    @classmethod
    def instance(cls) -> "GlobalMaterialCoefficientsManager":
        """Restituisce l'istanza singleton."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Resetta il singleton (utile nei test)."""
        cls._instance = None

    # ------------------------------------------------------------------
    # Query (Level 1 + Level 2)
    # ------------------------------------------------------------------

    def get_coefficient(
        self, norm_key: str, famiglia: str, coeff_key: str
    ) -> Any:
        """Restituisce il coefficiente applicando la priorità Level 2 > Level 1.

        Args:
            norm_key: Chiave norma (es. "NTC2018").
            famiglia: Famiglia materiale (es. "calcestruzzo").
            coeff_key: Chiave coefficiente (es. "gamma_c").

        Returns:
            Valore numerico/stringa, o ``None`` se non trovato in nessun livello.
        """
        # Level 2: override globale utente
        override = (
            self._cfg.material_coefficients_overrides
            .get(norm_key, {})
            .get(famiglia, {})
            .get(coeff_key)
        )
        if override is not None:
            return override

        # Level 1: default normativo
        return self._loader.get_material_coefficient(norm_key, famiglia, coeff_key)

    def get_coefficient_with_source(
        self, norm_key: str, famiglia: str, coeff_key: str
    ) -> tuple[Any, str]:
        """Come :meth:`get_coefficient` ma restituisce anche la sorgente.

        Returns:
            Tupla ``(valore, sorgente)`` dove sorgente è ``"override"`` o ``"default"``.
        """
        override = (
            self._cfg.material_coefficients_overrides
            .get(norm_key, {})
            .get(famiglia, {})
            .get(coeff_key)
        )
        if override is not None:
            return override, "override"

        val = self._loader.get_material_coefficient(norm_key, famiglia, coeff_key)
        return val, "default"

    def get_default_coefficient(
        self, norm_key: str, famiglia: str, coeff_key: str
    ) -> Any:
        """Restituisce il valore di Level 1 (ignora gli override utente)."""
        return self._loader.get_material_coefficient(norm_key, famiglia, coeff_key)

    def get_all_coefficients(self, norm_key: str, famiglia: str) -> dict[str, Any]:
        """Restituisce tutti i coefficienti per norma/famiglia con override applicati.

        Returns:
            Dict ``{coeff_key: valore_effettivo}`` per tutti i coefficienti Level 1,
            con eventuali valori Level 2 sovrapposti.
        """
        result = {}
        # Popola con Level 1
        for coeff_key in self._loader.list_coefficients(norm_key, famiglia):
            result[coeff_key] = self._loader.get_material_coefficient(
                norm_key, famiglia, coeff_key
            )
        # Applica Level 2
        overrides = (
            self._cfg.material_coefficients_overrides
            .get(norm_key, {})
            .get(famiglia, {})
        )
        result.update(overrides)
        return result

    def build_formula_namespace(self, norm_key: str, famiglia: str) -> dict[str, Any]:
        """Costruisce il namespace per la valutazione delle formule config.

        Da usare in MaterialConfigLoader.compute_derived() per popolare il namespace
        eval() con i coefficienti normativi corretti (con override applicati).

        Returns:
            Dict da passare come namespace a eval() nelle formule.
        """
        return self.get_all_coefficients(norm_key, famiglia)

    # ------------------------------------------------------------------
    # Mutazione (Level 2)
    # ------------------------------------------------------------------

    def set_coefficient_override(
        self,
        norm_key: str,
        famiglia: str,
        coeff_key: str,
        value: float | int | str,
        save: bool = True,
    ) -> None:
        """Imposta un override globale per un coefficiente.

        Args:
            norm_key: Chiave norma.
            famiglia: Famiglia materiale.
            coeff_key: Chiave coefficiente.
            value: Nuovo valore.
            save: Se True, persiste immediatamente su ``~/.rd2229/config.json``.
        """
        overrides = self._cfg.material_coefficients_overrides
        if norm_key not in overrides:
            overrides[norm_key] = {}
        if famiglia not in overrides[norm_key]:
            overrides[norm_key][famiglia] = {}
        overrides[norm_key][famiglia][coeff_key] = value
        logger.info(
            "Override globale impostato: %s/%s/%s = %s", norm_key, famiglia, coeff_key, value
        )
        if save:
            self._save_config()

    def reset_coefficient_to_default(
        self,
        norm_key: str,
        famiglia: str,
        coeff_key: str,
        save: bool = True,
    ) -> None:
        """Rimuove l'override per un coefficiente (ripristina il default Level 1).

        Args:
            norm_key: Chiave norma.
            famiglia: Famiglia materiale.
            coeff_key: Chiave coefficiente.
            save: Se True, persiste immediatamente.
        """
        overrides = self._cfg.material_coefficients_overrides
        try:
            del overrides[norm_key][famiglia][coeff_key]
            # Pulizia struttura vuota
            if not overrides[norm_key][famiglia]:
                del overrides[norm_key][famiglia]
            if not overrides[norm_key]:
                del overrides[norm_key]
        except KeyError:
            pass  # Override non esisteva
        logger.info(
            "Override rimosso: %s/%s/%s → ripristinato default", norm_key, famiglia, coeff_key
        )
        if save:
            self._save_config()

    def reset_all_norm(self, norm_key: str, save: bool = True) -> None:
        """Rimuove tutti gli override per una norma intera.

        Args:
            norm_key: Chiave norma (es. "NTC2018").
            save: Se True, persiste immediatamente.
        """
        self._cfg.material_coefficients_overrides.pop(norm_key, None)
        logger.info("Tutti gli override rimossi per norma: %s", norm_key)
        if save:
            self._save_config()

    def reset_all(self, save: bool = True) -> None:
        """Rimuove tutti gli override globali (ripristina tutti i defaults Level 1)."""
        self._cfg.material_coefficients_overrides.clear()
        logger.info("Tutti gli override globali rimossi")
        if save:
            self._save_config()

    # ------------------------------------------------------------------
    # Reload
    # ------------------------------------------------------------------

    def reload_user_config(self, path: str | None = None) -> None:
        """Ricarica UserConfig da file (es. dopo modifica esterna)."""
        self._cfg = UserConfig.load(path=path or self._user_config_path)
        logger.debug("UserConfig ricaricata")

    def reload_norm_defaults(self, norm_key: str | None = None) -> None:
        """Invalida la cache del NormativeDefaultsLoader."""
        self._loader.reload(norm_key)

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def has_override(self, norm_key: str, famiglia: str, coeff_key: str) -> bool:
        """Restituisce True se esiste un override Level 2 per il coefficiente."""
        return (
            coeff_key in self._cfg.material_coefficients_overrides
            .get(norm_key, {})
            .get(famiglia, {})
        )

    def get_overrides_for_norm(self, norm_key: str) -> dict:
        """Restituisce tutti gli override per una norma."""
        return dict(self._cfg.material_coefficients_overrides.get(norm_key, {}))

    def _save_config(self) -> None:
        try:
            self._cfg.save(path=self._user_config_path)
        except Exception as exc:
            logger.error("Errore salvataggio UserConfig: %s", exc)
