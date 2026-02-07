# Compatibility shim: re-export SuggestionBox from src.ui.ui.suggestion_box
from src.ui.ui.suggestion_box import SuggestionBox  # type: ignore

__all__ = ["SuggestionBox"]
