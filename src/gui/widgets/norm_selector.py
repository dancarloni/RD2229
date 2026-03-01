"""
Norm selector widget (skeleton) — reads configuration and returns a selection.
"""


def render_selector(available_codes: list):
    return {
        "available": available_codes,
        "selected": available_codes[0] if available_codes else None,
    }
