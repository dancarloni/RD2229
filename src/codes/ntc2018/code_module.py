"""Modulo normativo NTC2018.

Implementa l'interfaccia CodeModule per NTC2018, fornendo:
- Lista dei check disponibili con metadati
- Routing a funzioni di verifica concrete
- Integrazione con normative_registry per i template

Unita: dipendono dal check selezionato (storico cm/kgf o SI).
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
            {
                "id": "x3_slu_flessione",
                "short": "X3 Flessione SLU",
                "norm_ref": "NTC2018 §4.1.2.4",
                "limit_state": "SLU",
                "status": "implemented",
            },
            {
                "id": "x3_slu_taglio",
                "short": "X3 Taglio SLU",
                "norm_ref": "NTC2018 §4.1.2.5",
                "limit_state": "SLU",
                "status": "implemented",
            },
            {
                "id": "x3_slu_punzonamento",
                "short": "X3 Punzonamento SLU",
                "norm_ref": "NTC2018 §4.1.2.5",
                "limit_state": "SLU",
                "status": "implemented",
            },
            {
                "id": "x3_dm96_laterocemento",
                "short": "X3 Fallback DM96 Laterocemento",
                "norm_ref": "DM 9/1/1996",
                "limit_state": "SLU",
                "status": "implemented",
            },
            {
                "id": "x3_dm16_legno",
                "short": "X3 Fallback DM16 Legno",
                "norm_ref": "DM 16/1/1996",
                "limit_state": "SLU",
                "status": "implemented",
            },
            {
                "id": "x4_sle_deformabilita",
                "short": "X4 Deformabilita SLE",
                "norm_ref": "NTC2018 §4.1.2.2.4",
                "limit_state": "SLE",
                "status": "implemented",
            },
            {
                "id": "x4_sle_tensioni",
                "short": "X4 Tensioni/Fessurazione SLE",
                "norm_ref": "NTC2018 §4.1.2.2.5",
                "limit_state": "SLE",
                "status": "implemented",
            },
            {
                "id": "x4_sle_vibrazioni",
                "short": "X4 Vibrazioni SLE",
                "norm_ref": "NTC2018 §C7.10.5",
                "limit_state": "SLE",
                "status": "implemented",
            },
            {
                "id": "x5_aperture_classificazione",
                "short": "X5 Classificazione aperture",
                "norm_ref": "NTC2018 §7.2.6.2",
                "limit_state": "SLE",
                "status": "implemented",
            },
            {
                "id": "x5_aperture_rigidezza",
                "short": "X5 Rigidezza efficace aperture",
                "norm_ref": "NTC2018 §7.2.6.2",
                "limit_state": "SLE",
                "status": "implemented",
            },
            {
                "id": "x5_cerchiatura_redistribuzione",
                "short": "X5 Redistribuzione cerchiatura",
                "norm_ref": "NTC2018 §7.2.6.2",
                "limit_state": "SLE",
                "status": "implemented",
            },
            {
                "id": "x5_parete_rigidezza_ante_post",
                "short": "X5 Parete rigidezza ante/post",
                "norm_ref": "NTC2018 §8.3-§8.7",
                "limit_state": "SLE",
                "status": "implemented",
            },
            {
                "id": "x5_parete_pushover_ante_post",
                "short": "X5 Parete pushover ante/post",
                "norm_ref": "NTC2018 §7.8.2, §8.3-§8.7",
                "limit_state": "SLV",
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

        if check_id in {
            "x3_slu_flessione",
            "x3_slu_taglio",
            "x3_slu_punzonamento",
            "x3_dm96_laterocemento",
            "x3_dm16_legno",
        }:
            from src.methods.ntc2018.checks_x3 import (
                x3_dm16_legno,
                x3_dm96_laterocemento,
                x3_slu_flessione,
                x3_slu_punzonamento,
                x3_slu_taglio,
            )

            router = {
                "x3_slu_flessione": x3_slu_flessione,
                "x3_slu_taglio": x3_slu_taglio,
                "x3_slu_punzonamento": x3_slu_punzonamento,
                "x3_dm96_laterocemento": x3_dm96_laterocemento,
                "x3_dm16_legno": x3_dm16_legno,
            }
            result = router[check_id](inputs)
            if "trace" in result:
                result["trace"]["run_id"] = result["trace"].get("run_id", run_id)
            else:
                result["trace"] = {"run_id": run_id}
            if "norm_references" not in result:
                result["norm_references"] = ["NTC2018"]
            return result

        if check_id in {
            "x4_sle_deformabilita",
            "x4_sle_tensioni",
            "x4_sle_vibrazioni",
        }:
            from src.methods.ntc2018.checks_x4 import (
                x4_sle_deformabilita,
                x4_sle_tensioni,
                x4_sle_vibrazioni,
            )

            router = {
                "x4_sle_deformabilita": x4_sle_deformabilita,
                "x4_sle_tensioni": x4_sle_tensioni,
                "x4_sle_vibrazioni": x4_sle_vibrazioni,
            }
            result = router[check_id](inputs)
            if "trace" in result:
                result["trace"]["run_id"] = result["trace"].get("run_id", run_id)
            else:
                result["trace"] = {"run_id": run_id}
            if "norm_references" not in result:
                result["norm_references"] = ["NTC2018"]
            return result

        if check_id in {
            "x5_aperture_classificazione",
            "x5_aperture_rigidezza",
            "x5_cerchiatura_redistribuzione",
            "x5_parete_rigidezza_ante_post",
            "x5_parete_pushover_ante_post",
        }:
            from src.methods.ntc2018.checks_x5 import (
                x5_aperture_classificazione,
                x5_aperture_rigidezza,
                x5_cerchiatura_redistribuzione,
                x5_parete_pushover_ante_post,
                x5_parete_rigidezza_ante_post,
            )

            router = {
                "x5_aperture_classificazione": x5_aperture_classificazione,
                "x5_aperture_rigidezza": x5_aperture_rigidezza,
                "x5_cerchiatura_redistribuzione": x5_cerchiatura_redistribuzione,
                "x5_parete_rigidezza_ante_post": x5_parete_rigidezza_ante_post,
                "x5_parete_pushover_ante_post": x5_parete_pushover_ante_post,
            }
            result = router[check_id](inputs)
            if "trace" in result:
                result["trace"]["run_id"] = result["trace"].get("run_id", run_id)
            else:
                result["trace"] = {"run_id": run_id}
            if "norm_references" not in result:
                result["norm_references"] = ["NTC2018"]
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
