"""
Skeleton implementation of the CodeModule interface for NTC2018.
Implements the CodeModule contract (SPEC only). No normative logic — TODOs where behaviour is required.
"""


class NTC2018CodeModule:
    """Contract-conforming skeleton for unit tests and integration wiring."""

    @staticmethod
    def available_checks() -> list[dict]:
        return [
            {"id": "vrdc_no_stirrups", "short": "V_Rd,c (no stirrups) - skeleton"},
        ]

    @staticmethod
    def run_check(check_id: str, inputs: dict) -> dict:
        """Return a VerificationResultItem-like dict. Must include `trace.run_id` and `norm_references[]`.
        This is a SKELETON placeholder only.
        """
        return {
            "ok": True,
            "value": None,
            "steps": [],
            "trace": {"run_id": "TODO:generate-run-id"},
            "norm_references": ["TODO:reference"],
        }
