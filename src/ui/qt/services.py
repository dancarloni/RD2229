"""
RD2229 UI Logic - Common GUI Services
Provides singleton access to shared resources for all windows.
"""

import logging

try:
    from PyQt6.QtCore import QObject, pyqtSignal as Signal
except ImportError:  # pragma: no cover
    from PySide6.QtCore import QObject, Signal

from src.materials.material_repo import MaterialRepository
from src.project.schema import ProjectModel

logger = logging.getLogger(__name__)


class ProjectService(QObject):
    """
    Manages the active ProjectModel instance.
    Broadcasts changes to UI components.
    """
    project_changed = Signal(object)

    def __init__(self):
        super().__init__()
        # Ensure we always have a project model object
        self._current_project = ProjectModel()
        logger.debug("ProjectService initialized with default ProjectModel")

    @property
    def current_project(self) -> ProjectModel:
        return self._current_project

    def set_project(self, project: ProjectModel):
        self._current_project = project
        self.project_changed.emit(project)
        # Handle cases where project_info might be missing from schema
        name = getattr(project.project_info, "name", "Unnamed") if project.project_info else "None"
        logger.info("Project set to: %s", name)


class GUIServiceProvider:
    """
    Shared container for services (Project, Materials, Sections).
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            # Singleton pattern
            instance = super(GUIServiceProvider, cls).__new__(cls)
            instance.project_service = ProjectService()
            instance.material_repo = MaterialRepository()
            instance.section_repo = None
            cls._instance = instance
        return cls._instance


def get_services() -> GUIServiceProvider:
    return GUIServiceProvider()
