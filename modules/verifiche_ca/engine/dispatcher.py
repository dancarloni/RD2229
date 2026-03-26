"""
Dispatcher multi-norma per verifiche c.a.

Coordina le verifiche verso il motore appropriato in base alla norma selezionata.
Supporta:
- RD2229, DM72, DM74, DM76 (Tensioni ammissibili — TA)
- DM92, DM96 (Miste)
- NTC2008, NTC2018 (Stato limite ultimo/esercizio — SLU/SLE)
"""

from dataclasses import dataclass
from typing import Optional

from pipeline.module_registry import CheckResult, ModuleEngine, ModuleResult
from shared.loads.engine.models import LoadCondition


@dataclass
class VerificheCaInput:
    """Dati di ingresso per la verifica c.a."""

    element_id: str  # ID elemento
    section_id: str  # ID sezione (da archivio)
    material_id: str  # ID materiale (da archivio)
    load_manager: object  # LoadConditionManager con N condizioni × M SL


class VerificheCaEngine(ModuleEngine):
    """
    Engine dispatcher multi-norma per verifiche c.a.

    Instrada le verifiche all'implementazione appropriata basata sulla norma.
    Raccoglie e aggrega i risultati.
    """

    def __init__(self):
        """Inizializza il dispatcher e carica le sub-engine per ogni norma."""
        self._ta_engine = None  # Tensioni ammissibili (RD2229, DM72-76)
        self._mixed_engine = None  # Mixed (DM92, DM96)
        self._ntc2008_engine = None  # NTC2008
        self._ntc2018_engine = None  # NTC2018

    def validate_input(self, input_data: dict) -> list[str]:
        """
        Valida i dati di ingresso.

        Returns:
            Lista di errori (vuota = input valido)
        """
        errors = []

        # Controlli base
        if not input_data.get("element_id"):
            errors.append("element_id mancante")
        if not input_data.get("section_id"):
            errors.append("section_id mancante")
        if not input_data.get("material_id"):
            errors.append("material_id mancante")
        if not input_data.get("load_manager"):
            errors.append("load_manager mancante")

        return errors

    def run(self, input_data: dict, norm_code: str) -> ModuleResult:
        """
        Esegue la verifica per un elemento singolo.

        Args:
            input_data: Dati di ingresso (element_id, section_id, material_id, load_manager)
            norm_code: Codice norma (RD2229, NTC2018, ecc.)

        Returns:
            ModuleResult con verifiche (SLU, SLE, ecc.)
        """
        # Validazione
        errors = self.validate_input(input_data)
        if errors:
            return ModuleResult(
                ok=False,
                element_id=input_data.get("element_id", "unknown"),
                errors=errors,
            )

        # Dispatcher per norma
        if norm_code in ("RD2229", "DM72", "DM74", "DM76"):
            return self._run_ta(input_data, norm_code)
        elif norm_code in ("DM92", "DM96"):
            return self._run_mixed(input_data, norm_code)
        elif norm_code == "NTC2008":
            return self._run_ntc2008(input_data)
        elif norm_code == "NTC2018":
            return self._run_ntc2018(input_data)
        else:
            return ModuleResult(
                ok=False,
                element_id=input_data.get("element_id", "unknown"),
                errors=[f"Norma non supportata: {norm_code}"],
            )

    def run_batch(self, elements: list[dict], norm_code: str) -> list[ModuleResult]:
        """
        Esegue verifiche su N elementi.

        Args:
            elements: Lista di elementi da verificare
            norm_code: Codice norma

        Returns:
            Lista di ModuleResult
        """
        results = []
        for elem in elements:
            result = self.run(elem, norm_code)
            results.append(result)
        return results

    def _run_ta(self, input_data: dict, norm_code: str) -> ModuleResult:
        """
        Esegue verifiche per normative Tensioni Ammissibili.

        Placeholder: implementare logica TA quando disponibile.
        """
        return ModuleResult(
            ok=False,
            element_id=input_data.get("element_id", "unknown"),
            errors=[f"Implementazione norma {norm_code} in progress"],
        )

    def _run_mixed(self, input_data: dict, norm_code: str) -> ModuleResult:
        """
        Esegue verifiche per normative miste (DM92, DM96).

        Placeholder: implementare logica mixed quando disponibile.
        """
        return ModuleResult(
            ok=False,
            element_id=input_data.get("element_id", "unknown"),
            errors=[f"Implementazione norma {norm_code} in progress"],
        )

    def _run_ntc2008(self, input_data: dict) -> ModuleResult:
        """
        Esegue verifiche NTC2008 (SLU/SLE).

        Placeholder: implementare logica NTC2008 quando disponibile.
        """
        return ModuleResult(
            ok=False,
            element_id=input_data.get("element_id", "unknown"),
            errors=["Implementazione NTC2008 in progress"],
        )

    def _run_ntc2018(self, input_data: dict) -> ModuleResult:
        """
        Esegue verifiche NTC2018 (SLU/SLE).

        Placeholder: implementare logica NTC2018 quando disponibile.
        """
        return ModuleResult(
            ok=False,
            element_id=input_data.get("element_id", "unknown"),
            errors=["Implementazione NTC2018 in progress"],
        )
