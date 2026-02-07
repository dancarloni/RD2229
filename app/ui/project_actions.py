# Compatibility shim: re-export project actions from src.ui.ui.project_actions
from src.ui.ui.project_actions import add_list_elements, load_project, save_project  # type: ignore

__all__ = ["load_project", "save_project", "add_list_elements"]
