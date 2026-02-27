"""Project model schema for RD2229.

Single source of truth for project persistence and pipeline inputs.
Uses Pydantic models for validation and JSON-Schema generation.
"""

from __future__ import annotations

import json
from typing import Any, cast

from pydantic import BaseModel, Field

CURRENT_SCHEMA_VERSION = "1.1.0"


class ProjectInfo(BaseModel):
    name: str = ""
    description: str = ""
    author: str = ""
    created_at: str = ""
    updated_at: str = ""


class GeometryEntry(BaseModel):
    id: str = ""
    type: str = ""
    width: float = 0.0
    height: float = 0.0
    fire_selected: bool = False
    fire_override: dict[str, Any] | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


class MaterialEntry(BaseModel):
    id: str = ""
    type: str = ""
    material_class: str = ""
    f_ck: float | None = None
    f_yk: float | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


class LoadEntry(BaseModel):
    element_id: str = ""
    N: float | None = None
    Mx: float | None = None
    My: float | None = None
    Mz: float | None = None
    Tx: float | None = None
    Ty: float | None = None
    description: str = ""


class SeismicInputs(BaseModel):
    class_of_use: str = ""
    vita_nominale_years: int = 0
    vr_years: int = 0
    site_label: str = ""
    hazard_profile: dict[str, Any] = Field(default_factory=dict)


class CodeSettings(BaseModel):
    norm_code: str = "RD2229"
    limit_states: list[str] = Field(default_factory=lambda: ["TA"])
    units_force: str = "kN"
    units_length: str = "cm"
    existing_structure: bool = False
    lc: str | None = None


class FireSettings(BaseModel):
    enabled: bool = False
    scenario: str = "ISO_834"
    required_rating_minutes: int = 60
    cover_mm_default: float | None = None
    exposure_sides_default: int | None = None


class ResultsRef(BaseModel):
    results_path: str = ""
    computed_at: str = ""
    schema_version_input: str = ""
    summary: str = ""


class ProjectModel(BaseModel):
    """Validated project container used by pipeline, CLI and GUI."""

    schema_version: str = CURRENT_SCHEMA_VERSION
    project_info: ProjectInfo = Field(default_factory=ProjectInfo)
    geometry: list[GeometryEntry] = Field(default_factory=list)
    materials: list[MaterialEntry] = Field(default_factory=list)
    loads: list[LoadEntry] = Field(default_factory=list)
    seismic_inputs: SeismicInputs = Field(default_factory=SeismicInputs)
    code_settings: CodeSettings = Field(default_factory=CodeSettings)
    fire: FireSettings = Field(default_factory=FireSettings)
    results_ref: ResultsRef = Field(default_factory=ResultsRef)
    pipeline_steps: list[str] = Field(
        default_factory=lambda: ["validate", "seismic", "checks", "step5", "aggregate"]
    )
    plugins: dict[str, dict[str, Any]] = Field(default_factory=dict)
    # Wind configuration (may be populated with src.wind.service.WindConfig)
    wind: Any = Field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return cast(dict[str, Any], self.model_dump(mode="json"))

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProjectModel":
        return cast(ProjectModel, cls.model_validate(data))

    @classmethod
    def json_schema_dict(cls) -> dict[str, Any]:
        return cast(dict[str, Any], cls.model_json_schema())

    @classmethod
    def export_schema(cls, path: str = "schema.json") -> None:
        with open(path, "w", encoding="utf-8") as file_obj:
            json.dump(cls.model_json_schema(), file_obj, ensure_ascii=False, indent=2)
