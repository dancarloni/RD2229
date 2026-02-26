"""
Small reusable widgets for secondary element editor (SKELETON).
Widgets are UI-only and must not contain normative logic.
"""

class PreviewWidget:
    def __init__(self):
        self.model = None

    def render(self, model):
        self.model = model
        return f"Preview: {model.get('element_type', 'unknown')}"
