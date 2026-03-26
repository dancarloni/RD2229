"""
Dispatcher per analisi sismica e pushover.

Supporta:
- Calcolo spettri di risposta (NTC2018)
- Analisi pushover semplificata
- Fattori di struttura
"""

from pipeline.module_registry import ModuleEngine, ModuleResult


class SismicaEngine(ModuleEngine):
    """Engine per calcoli sismici e pushover."""

    def validate_input(self, input_data: dict) -> list[str]:
        """Valida i dati di ingresso."""
        errors = []

        if "site_params" not in input_data:
            errors.append("site_params mancanti")
        if not input_data.get("structure_type"):
            errors.append("structure_type mancante")

        return errors

    def run(self, input_data: dict, norm_code: str) -> ModuleResult:
        """Esegue analisi sismica."""
        errors = self.validate_input(input_data)
        if errors:
            return ModuleResult(
                ok=False,
                element_id=input_data.get("element_id", "unknown"),
                errors=errors,
            )

        if norm_code == "NTC2018":
            return self._run_ntc2018(input_data)
        elif norm_code == "NTC2008":
            return self._run_ntc2008(input_data)
        else:
            return ModuleResult(
                ok=False,
                element_id=input_data.get("element_id", "unknown"),
                errors=[f"Norma non supportata: {norm_code}"],
            )

    def run_batch(self, elements: list[dict], norm_code: str) -> list[ModuleResult]:
        """Esegue analisi su N elementi."""
        results = []
        for elem in elements:
            result = self.run(elem, norm_code)
            results.append(result)
        return results

    def _run_ntc2018(self, input_data: dict) -> ModuleResult:
        """Esegue analisi NTC2018."""
        return ModuleResult(
            ok=False,
            element_id=input_data.get("element_id", "unknown"),
            errors=["Implementazione NTC2018 in progress"],
        )

    def _run_ntc2008(self, input_data: dict) -> ModuleResult:
        """Esegue analisi NTC2008."""
        return ModuleResult(
            ok=False,
            element_id=input_data.get("element_id", "unknown"),
            errors=["Implementazione NTC2008 in progress"],
        )
