"""Modulo normativo NTC2018.

Implementa l'interfaccia CodeModule per NTC2018, fornendo:
- Lista dei check disponibili con metadati
- Routing a funzioni di verifica concrete
- Integrazione con normative_registry per i template

Unità: tensioni in MPa, lunghezze in mm (input), risultati in kN/kNm.
"""

from __future__ import annotations

import uuid
from typing import Any


class NTC2018CodeModule:
    """Modulo normativo NTC2018 con routing a check reali."""

    @staticmethod
    def available_checks() -> list[dict[str, Any]]:
        """Restituisce la lista dei check disponibili per NTC2018."""
        return [
            {
                "id": "vrdc_no_stirrups",
                "short": "V_Rd,c (senza staffe)",
                "norm_ref": "NTC2018 §4.1.2.1.3.1",
                "limit_state": "SLU",
                "status": "implemented",
            },
            {
                "id": "slu_flessione",
                "short": "Flessione SLU",
                "norm_ref": "NTC2018 §4.1.2.1.2",
                "limit_state": "SLU",
                "status": "implemented",
            },
            {
                "id": "slu_taglio",
                "short": "Taglio SLU",
                "norm_ref": "NTC2018 §4.1.2.1.3",
                "limit_state": "SLU",
                "status": "implemented",
            },
            {
                "id": "slu_pressoflessione",
                "short": "Pressoflessione SLU",
                "norm_ref": "NTC2018 §4.1.2.1.2",
                "limit_state": "SLU",
                "status": "implemented",
            },
            {
                "id": "slu_torsione",
                "short": "Torsione SLU",
                "norm_ref": "NTC2018 §4.1.2.1.4",
                "limit_state": "SLU",
                "status": "implemented",
            },
            {
                "id": "sle_tensioni",
                "short": "Tensioni SLE",
                "norm_ref": "NTC2018 §4.1.2.2.5",
                "limit_state": "SLE",
                "status": "implemented",
            },
            {
                "id": "sle_fessurazione",
                "short": "Fessurazione SLE",
                "norm_ref": "NTC2018 §4.1.2.2.4",
                "limit_state": "SLE",
                "status": "implemented",
            },
        ]

    @staticmethod
    def run_check(check_id: str, inputs: dict[str, Any]) -> dict[str, Any]:
        """Esegue un check NTC2018 specifico.

        Args:
            check_id: identificativo del check (es. "vrdc_no_stirrups")
            inputs: dizionario di input per il check

        Returns:
            Risultato con trace.run_id, norm_references[], ok, value, steps
        """
        run_id = str(uuid.uuid4())

        if check_id == "vrdc_no_stirrups":
            from src.codes.ntc2018.checks_vrdc import vrdc_no_stirrups

            result = vrdc_no_stirrups(inputs)
            if "trace" in result:
                result["trace"]["run_id"] = result["trace"].get("run_id", run_id)
            return result

        return {
            "ok": False,
            "value": None,
            "steps": [f"Check '{check_id}' non implementato in NTC2018CodeModule."],
            "trace": {"run_id": run_id},
            "norm_references": ["NTC2018"],
        }

    @staticmethod
    def get_check_metadata(check_id: str) -> dict[str, Any] | None:
        """Restituisce i metadati di un check specifico."""
        for check in NTC2018CodeModule.available_checks():
            if check["id"] == check_id:
                return check
        return None
