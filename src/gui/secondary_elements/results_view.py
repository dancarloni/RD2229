"""
Results view (skeleton): format `VerificationResultItem` for presentation.
Must display `trace.run_id` and `norm_references[]` when present.
"""


def format_result(result: dict) -> str:
    run_id = result.get("trace", {}).get("run_id", "<no-run-id>")
    refs = result.get("norm_references", [])
    return f"Run: {run_id} — refs: {refs} — OK: {result.get('ok')}"
