"""
Secondary element editor bindings (skeleton).
This file contains form->model bindings and UI helpers only; all normative computing is delegated to `src/codes/ntc2018` modules.
Refer to `docs/MEGAPLAN/PLAN_GUI_SECONDARY_ELEMENTS.md` and `docs/MEGAPLAN/SPEC_SecondaryElementSpec.md` for field definitions and required traceability.
"""


def build_form_schema(element_type: str) -> dict:
    """Return a form schema (SKELETON)."""
    return {"element_type": element_type, "fields": ["width", "height", "material"]}


def serialize_form(inputs: dict) -> dict:
    """Sanitize/serialize user inputs for the engine. GUI must not apply normative conversions here."""
    return inputs
