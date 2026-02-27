from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from typing import Any

from .models import (
    CheckRequest,
    Combination,
    Element,
    LoadCase,
    Material,
    Project,
    Section,
    TraceRecord,
    VerificationResult,
)


def _dump(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True)


def _load_dict(data: str) -> dict[str, Any]:
    raw = json.loads(data)
    if not isinstance(raw, dict):
        raise ValueError("Serialized payload must be a dict")
    return raw


class ProjectRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def save(self, project: Project) -> None:
        self.conn.execute(
            """
            INSERT OR REPLACE INTO projects(id, name, norma_attiva, created_at, schema_version)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                project.id,
                project.name,
                project.norma_attiva,
                project.created_at,
                project.schema_version,
            ),
        )
        self.conn.commit()

    def get(self, project_id: str) -> Project | None:
        row = self.conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
        if row is None:
            return None
        return Project(
            id=row["id"],
            name=row["name"],
            norma_attiva=row["norma_attiva"],
            created_at=row["created_at"],
            schema_version=int(row["schema_version"]),
        )


class MaterialRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def save(self, material: Material) -> None:
        self.conn.execute(
            """
            INSERT OR REPLACE INTO materials(id, project_id, code, kind, properties_json)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                material.id,
                material.project_id,
                material.code,
                material.kind,
                _dump(material.properties),
            ),
        )
        self.conn.commit()

    def list_by_project(self, project_id: str) -> list[Material]:
        rows = self.conn.execute("SELECT * FROM materials WHERE project_id = ? ORDER BY id", (project_id,)).fetchall()
        return [
            Material(
                id=r["id"],
                project_id=r["project_id"],
                code=r["code"],
                kind=r["kind"],
                properties=_load_dict(r["properties_json"]),
            )
            for r in rows
        ]


class SectionRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def save(self, section: Section) -> None:
        self.conn.execute(
            """
            INSERT OR REPLACE INTO sections(id, project_id, kind, dimensions_json)
            VALUES (?, ?, ?, ?)
            """,
            (section.id, section.project_id, section.kind, _dump(section.dimensions)),
        )
        self.conn.commit()

    def list_by_project(self, project_id: str) -> list[Section]:
        rows = self.conn.execute("SELECT * FROM sections WHERE project_id = ? ORDER BY id", (project_id,)).fetchall()
        return [
            Section(
                id=r["id"],
                project_id=r["project_id"],
                kind=r["kind"],
                dimensions=_load_dict(r["dimensions_json"]),
            )
            for r in rows
        ]


class ElementRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def save(self, element: Element) -> None:
        self.conn.execute(
            """
            INSERT OR REPLACE INTO elements(
                id, project_id, section_id, material_id, role, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                element.id,
                element.project_id,
                element.section_id,
                element.material_id,
                element.role,
                _dump(element.metadata),
            ),
        )
        self.conn.commit()

    def get(self, element_id: str) -> Element | None:
        row = self.conn.execute("SELECT * FROM elements WHERE id = ?", (element_id,)).fetchone()
        if row is None:
            return None
        return Element(
            id=row["id"],
            project_id=row["project_id"],
            section_id=row["section_id"],
            material_id=row["material_id"],
            role=row["role"],
            metadata=_load_dict(row["metadata_json"]),
        )


class LoadCaseRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def save(self, load_case: LoadCase) -> None:
        self.conn.execute(
            """
            INSERT OR REPLACE INTO load_cases(
                id, project_id, name, category, actions_json, environmental_json
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                load_case.id,
                load_case.project_id,
                load_case.name,
                load_case.category,
                _dump(load_case.actions),
                _dump(load_case.environmental),
            ),
        )
        self.conn.commit()

    def get(self, load_case_id: str) -> LoadCase | None:
        row = self.conn.execute("SELECT * FROM load_cases WHERE id = ?", (load_case_id,)).fetchone()
        if row is None:
            return None
        return LoadCase(
            id=row["id"],
            project_id=row["project_id"],
            name=row["name"],
            category=row["category"],
            actions=_load_dict(row["actions_json"]),
            environmental=_load_dict(row["environmental_json"]),
        )


class CombinationRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def save(self, combination: Combination) -> None:
        self.conn.execute(
            """
            INSERT OR REPLACE INTO combinations(id, project_id, name, factors_json)
            VALUES (?, ?, ?, ?)
            """,
            (combination.id, combination.project_id, combination.name, _dump(combination.factors)),
        )
        self.conn.commit()

    def get(self, combination_id: str) -> Combination | None:
        row = self.conn.execute("SELECT * FROM combinations WHERE id = ?", (combination_id,)).fetchone()
        if row is None:
            return None
        return Combination(
            id=row["id"],
            project_id=row["project_id"],
            name=row["name"],
            factors=_load_dict(row["factors_json"]),
        )


class CheckRequestRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def save(self, request: CheckRequest) -> None:
        self.conn.execute(
            """
            INSERT OR REPLACE INTO check_requests(
                id, project_id, element_id, combination_id, check_code, parameters_json
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                request.id,
                request.project_id,
                request.element_id,
                request.combination_id,
                request.check_code,
                _dump(request.parameters),
            ),
        )
        self.conn.commit()


class VerificationResultRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def save(self, result: VerificationResult) -> None:
        self.conn.execute(
            """
            INSERT OR REPLACE INTO verification_results(
                id, request_id, project_id, status, value, trace_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                result.id,
                result.request_id,
                result.project_id,
                result.status,
                result.value,
                _dump(asdict(result.trace)),
                result.created_at,
            ),
        )
        self.conn.commit()

    def list_by_project(self, project_id: str) -> list[VerificationResult]:
        rows = self.conn.execute(
            "SELECT * FROM verification_results WHERE project_id = ? ORDER BY created_at",
            (project_id,),
        ).fetchall()
        items: list[VerificationResult] = []
        for row in rows:
            trace_raw = _load_dict(row["trace_json"])
            trace = TraceRecord(
                run_id=str(trace_raw["run_id"]),
                norm_code=str(trace_raw["norm_code"]),
                norm_references=list(trace_raw["norm_references"]),
                method_id=str(trace_raw["method_id"]),
                assumptions=list(trace_raw.get("assumptions") or []),
                warnings=list(trace_raw.get("warnings") or []),
            )
            items.append(
                VerificationResult(
                    id=row["id"],
                    request_id=row["request_id"],
                    project_id=row["project_id"],
                    status=row["status"],
                    value=float(row["value"]),
                    trace=trace,
                    created_at=row["created_at"],
                )
            )
        return items
