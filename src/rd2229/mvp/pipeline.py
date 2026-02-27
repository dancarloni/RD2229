from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from uuid import uuid4

from .engine import PlaceholderVerificationEngine
from .jsoncode_loader import load_jsoncode_config
from .models import CheckRequest, Combination, Element, LoadCase, Material, Project, Section
from .plugins import register_default_module_specs
from .repositories import (
    CheckRequestRepository,
    CombinationRepository,
    ElementRepository,
    LoadCaseRepository,
    MaterialRepository,
    ProjectRepository,
    SectionRepository,
    VerificationResultRepository,
)
from .sqlite_store import SQLiteStore


def run_mvp_demo(
    db_path: str,
    jsoncode_path: str,
    *,
    axial_n: float = 120.0,
    combination_factor: float = 1.0,
    check_code: str | None = None,
    threshold_override: float | None = None,
) -> dict[str, str]:
    store = SQLiteStore(db_path)
    store.initialize()

    config = load_jsoncode_config(jsoncode_path)
    if threshold_override is not None:
        payload = dict(config.payload)
        payload["threshold"] = float(threshold_override)
        config = replace(config, payload=payload)
    plugin_specs = register_default_module_specs()

    with store.connect() as conn:
        project_repo = ProjectRepository(conn)
        material_repo = MaterialRepository(conn)
        section_repo = SectionRepository(conn)
        element_repo = ElementRepository(conn)
        load_case_repo = LoadCaseRepository(conn)
        combination_repo = CombinationRepository(conn)
        request_repo = CheckRequestRepository(conn)
        result_repo = VerificationResultRepository(conn)

        project_id = uuid4().hex
        project = Project(id=project_id, name="MVP Demo", norma_attiva=config.namespace)
        material = Material(
            id=uuid4().hex,
            project_id=project_id,
            code="C25/30",
            kind="concrete",
            properties={"fck": 25.0},
        )
        section = Section(
            id=uuid4().hex,
            project_id=project_id,
            kind="RECT",
            dimensions={"b": 0.30, "h": 0.50},
        )
        element = Element(
            id=uuid4().hex,
            project_id=project_id,
            section_id=section.id,
            material_id=material.id,
            role="PRIMARY",
        )
        load_case = LoadCase(
            id=uuid4().hex,
            project_id=project_id,
            name="LC1",
            category="PERMANENT",
            actions={"N": float(axial_n)},
            environmental={},
        )
        combination = Combination(
            id=uuid4().hex,
            project_id=project_id,
            name="COMB1",
            factors={load_case.id: float(combination_factor)},
        )
        request = CheckRequest(
            id=uuid4().hex,
            project_id=project_id,
            element_id=element.id,
            combination_id=combination.id,
            check_code=(check_code or config.check_code),
            parameters={},
        )

        project_repo.save(project)
        material_repo.save(material)
        section_repo.save(section)
        element_repo.save(element)
        load_case_repo.save(load_case)
        combination_repo.save(combination)
        request_repo.save(request)

        engine = PlaceholderVerificationEngine()
        result = engine.run(
            request=request,
            element=element,
            load_case=load_case,
            combination=combination,
            config=config,
        )
        result_repo.save(result)

    return {
        "db_path": str(Path(db_path)),
        "project_id": project_id,
        "result_id": result.id,
        "status": result.status,
        "check_code": result.trace.method_id,
        "plugins_loaded": str(len(plugin_specs)),
    }
