"""
GUI helper (skeleton) to select calculation code / national annex.
UI must be thin — reads `config/calculation_codes/*` and returns the selected code identifier.
"""


def list_available_codes() -> list:
    return ["NTC2018"]


def select_code(code_id: str) -> dict:
    return {"selected": code_id}
