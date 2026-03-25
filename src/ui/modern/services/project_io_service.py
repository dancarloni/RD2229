from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.project.schema import ProjectModel


class ProjectIOService:
    def new_project(self) -> ProjectModel:
        from src.project.schema import ProjectModel

        return ProjectModel()

    def open_project(self, path: str) -> ProjectModel:
        from src.project.repository import load_project

        return load_project(path)

    def save_project(self, project: ProjectModel, path: str) -> None:
        from src.project.repository import save_project

        save_project(project, path)
