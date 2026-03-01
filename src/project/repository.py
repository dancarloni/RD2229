"""Repository JSON per il ProjectModel – load / save / migrate.

Funzioni pubbliche:
    - :func:`load_project` – legge un file JSON e restituisce un :class:`ProjectModel`.
    - :func:`save_project` – serializza un :class:`ProjectModel` su file JSON.
    - :func:`migrate_dict` – applica la catena di migrazioni a un dizionario raw.

Migrazioni:
    Ogni funzione ``_migrate_X_to_Y`` riceve un ``dict`` e restituisce un ``dict``
    già migrato. La catena viene eseguita in ordine da :func:`migrate_dict`.
    Aggiungere nuove funzioni di migrazione qui e registrarle in ``_MIGRATIONS``.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

import yaml  # type: ignore[import-untyped]

from src.project.schema import (
    CURRENT_SCHEMA_VERSION,
    CodeSettings,
    FireSettings,
    GeometryEntry,
    LoadEntry,
    MaterialEntry,
    ProjectInfo,
    ProjectModel,
    ResultsRef,
    SeismicInputs,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Migration chain
# ---------------------------------------------------------------------------


def _migrate_none_to_1_0_0(data: dict[str, Any]) -> dict[str, Any]:
    """Migra file senza schema_version a 1.0.0.

    Aggiunge i campi mancanti con i loro default.
    """
    data.setdefault("schema_version", "1.0.0")
    data.setdefault("project_info", {})
    data.setdefault("geometry", [])
    data.setdefault("materials", [])
    data.setdefault("loads", [])
    data.setdefault("seismic_inputs", {})
    data.setdefault("code_settings", {})
    data.setdefault("results_ref", {})
    logger.info("Migrazione applicata: None → 1.0.0")
    return data


def _migrate_1_0_0_to_1_1_0(data: dict[str, Any]) -> dict[str, Any]:
    """Migra schema v1.0.0 a v1.1.0.

    Aggiunge:
    - code_settings.existing_structure (default False)
    - code_settings.lc (default None)
    - fire settings block
    - geometry[].fire_selected (default False)
    - geometry[].fire_override (default None)
    """
    data["schema_version"] = "1.1.0"

    # CodeSettings: nuovi campi
    cs = data.setdefault("code_settings", {})
    cs.setdefault("existing_structure", False)
    cs.setdefault("lc", None)

    # FireSettings: nuovo blocco
    data.setdefault(
        "fire",
        {
            "enabled": False,
            "scenario": "ISO_834",
            "required_rating_minutes": 60,
            "cover_mm_default": None,
            "exposure_sides_default": None,
        },
    )

    # GeometryEntry: nuovi campi
    for geom in data.get("geometry", []):
        geom.setdefault("fire_selected", False)
        geom.setdefault("fire_override", None)

    logger.info("Migrazione applicata: 1.0.0 → 1.1.0")
    return data


# Mappatura: (versione_corrente) -> funzione di migrazione alla versione successiva
_MIGRATIONS: list[tuple[str | None, Any]] = [
    (None, _migrate_none_to_1_0_0),
    ("1.0.0", _migrate_1_0_0_to_1_1_0),
]


def migrate_dict(data: dict[str, Any]) -> dict[str, Any]:
    """Applica la catena di migrazioni fino a :data:`CURRENT_SCHEMA_VERSION`.

    Args:
        data: Dizionario raw letto dal file JSON.

    Returns:
        Dizionario aggiornato alla versione corrente dello schema.
    """
    version = data.get("schema_version")
    if version == CURRENT_SCHEMA_VERSION:
        return data

    for from_version, migration_fn in _MIGRATIONS:
        if data.get("schema_version") == from_version:
            data = migration_fn(data)
            logger.debug(
                "Migrazione '%s' applicata → schema_version=%s",
                migration_fn.__name__,
                data.get("schema_version"),
            )

    if data.get("schema_version") != CURRENT_SCHEMA_VERSION:
        logger.warning(
            "schema_version '%s' non corrisponde alla versione corrente '%s'; "
            "alcuni campi potrebbero essere mancanti.",
            data.get("schema_version"),
            CURRENT_SCHEMA_VERSION,
        )
    return data


def _migrate_sections_elements_to_geometry_loads(data: dict[str, Any]) -> dict[str, Any]:
    """Normalize legacy keys `sections` and `elements` into `geometry` and `loads`.

    This transformation is non-destructive: the caller may save a backup of the
    original file before applying. The function returns a new dict with
    `geometry` and `loads` populated when possible.
    """
    migrated = dict(data)  # shallow copy

    # Migrate `sections` -> `geometry`
    sections = migrated.get("sections")
    if sections and not migrated.get("geometry"):
        geom_list: list[dict[str, Any]] = []
        for s in sections:
            if not isinstance(s, dict):
                continue
            # Apply sensible defaults for missing dimensions to allow checks
            width = s.get("width") or 30.0
            height = s.get("height") or 30.0
            geom_list.append(
                {
                    "id": s.get("id", ""),
                    "type": s.get("type", ""),
                    "width": float(width),
                    "height": float(height),
                    "fire_selected": s.get("fire_selected", False),
                    "fire_override": s.get("fire_override"),
                    "extra": s.get("extra", {}) or {},
                }
            )
        migrated["geometry"] = geom_list

    # Migrate `elements` -> `loads`
    elements = migrated.get("elements")
    if elements and not migrated.get("loads"):
        loads_list: list[dict[str, Any]] = []
        for e in elements:
            if not isinstance(e, dict):
                continue
            # Prefer linking load to the section id when present so geometry
            # (migrated from `sections`) can be found by element lookups.
            element_id = e.get("section_id") or e.get("id") or e.get("element_id") or ""
            loads_list.append(
                {
                    "element_id": element_id,
                    "N": e.get("N"),
                    "Mx": e.get("Mx"),
                    "My": e.get("My"),
                    "Mz": e.get("Mz"),
                    "Tx": e.get("Tx"),
                    "Ty": e.get("Ty"),
                    "description": e.get("name") or e.get("description") or "",
                }
            )
        migrated["loads"] = loads_list

    # Ensure code_settings.existing_structure=True to allow historical templates
    cs = migrated.get("code_settings") or {}
    cs.setdefault("existing_structure", True)
    cs.setdefault("lc", "LC1")
    migrated["code_settings"] = cs

    return migrated


# ---------------------------------------------------------------------------
# Deserialization helpers
# ---------------------------------------------------------------------------


def _dict_to_project(data: dict[str, Any]) -> ProjectModel:
    """Converte un dizionario (già migrato) in un :class:`ProjectModel`.

    I campi mancanti vengono sostituiti con i valori di default del dataclass.
    """

    def _get(d: dict[str, Any], key: str, default: Any) -> Any:
        return d.get(key, default) if d else default

    pi_raw = data.get("project_info") or {}
    project_info = ProjectInfo(
        name=pi_raw.get("name", ""),
        description=pi_raw.get("description", ""),
        author=pi_raw.get("author", ""),
        created_at=pi_raw.get("created_at", ""),
        updated_at=pi_raw.get("updated_at", ""),
    )

    geometry = [
        GeometryEntry(
            id=g.get("id", ""),
            type=g.get("type", ""),
            width=g.get("width", 0.0),
            height=g.get("height", 0.0),
            fire_selected=g.get("fire_selected", False),
            fire_override=g.get("fire_override"),
            extra=g.get("extra") or {},
        )
        for g in (data.get("geometry") or [])
    ]

    # Normalize legacy `materials` format: some older project files store materials
    # as a dict like {"cls": [...], "steel": [...]} instead of a list.
    materials_raw = data.get("materials") or []
    if isinstance(materials_raw, dict):
        materials_list: list[dict[str, Any]] = []
        for mat_type, entries in materials_raw.items():
            if not isinstance(entries, list):
                continue
            for item in entries:
                if isinstance(item, dict):
                    materials_list.append(
                        {
                            "id": item.get("id", ""),
                            "type": mat_type,
                            "material_class": item.get("name", ""),
                            "f_ck": item.get("f_ck"),
                            "f_yk": item.get("f_yk"),
                            "extra": item.get("extra", {}),
                        }
                    )
                else:
                    materials_list.append({"id": str(item), "type": mat_type, "material_class": ""})
    else:
        materials_list = materials_raw

    materials = [
        MaterialEntry(
            id=m.get("id", ""),
            type=m.get("type", ""),
            material_class=m.get("material_class", ""),
            f_ck=m.get("f_ck"),
            f_yk=m.get("f_yk"),
            extra=m.get("extra") or {},
        )
        for m in materials_list
    ]

    loads = [
        LoadEntry(
            element_id=ld.get("element_id", ""),
            N=ld.get("N"),
            Mx=ld.get("Mx"),
            My=ld.get("My"),
            Mz=ld.get("Mz"),
            Tx=ld.get("Tx"),
            Ty=ld.get("Ty"),
            description=ld.get("description", ""),
        )
        for ld in (data.get("loads") or [])
    ]

    si_raw = data.get("seismic_inputs") or {}
    seismic_inputs = SeismicInputs(
        class_of_use=si_raw.get("class_of_use", ""),
        vita_nominale_years=si_raw.get("vita_nominale_years", 0),
        vr_years=si_raw.get("vr_years", 0),
        site_label=si_raw.get("site_label", ""),
        hazard_profile=si_raw.get("hazard_profile") or {},
    )

    cs_raw = data.get("code_settings") or {}
    code_settings = CodeSettings(
        norm_code=cs_raw.get("norm_code", "RD2229"),
        limit_states=cs_raw.get("limit_states") or ["TA"],
        units_force=cs_raw.get("units_force", "kN"),
        units_length=cs_raw.get("units_length", "cm"),
        existing_structure=cs_raw.get("existing_structure", False),
        lc=cs_raw.get("lc"),
    )

    fire_raw = data.get("fire") or {}
    fire = FireSettings(
        enabled=fire_raw.get("enabled", False),
        scenario=fire_raw.get("scenario", "ISO_834"),
        required_rating_minutes=fire_raw.get("required_rating_minutes", 60),
        cover_mm_default=fire_raw.get("cover_mm_default"),
        exposure_sides_default=fire_raw.get("exposure_sides_default"),
    )

    rr_raw = data.get("results_ref") or {}
    results_ref = ResultsRef(
        results_path=rr_raw.get("results_path", ""),
        computed_at=rr_raw.get("computed_at", ""),
        schema_version_input=rr_raw.get("schema_version_input", ""),
        summary=rr_raw.get("summary", ""),
    )

    return ProjectModel(
        schema_version=data.get("schema_version", CURRENT_SCHEMA_VERSION),
        project_info=project_info,
        geometry=geometry,
        materials=materials,
        loads=loads,
        seismic_inputs=seismic_inputs,
        code_settings=code_settings,
        fire=fire,
        results_ref=results_ref,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def load_project(path: str) -> ProjectModel:
    """Carica un progetto da file JSON/YAML applicando le migrazioni necessarie.

    Args:
        path: Percorso del file ``.json`` o ``.jsonp`` del progetto.

    Returns:
        :class:`ProjectModel` popolato.

    Raises:
        FileNotFoundError: Se il file non esiste.
        json.JSONDecodeError: Se il file non è JSON valido.
    """
    with open(path, encoding="utf-8") as f:
        if path.lower().endswith((".yml", ".yaml")):
            loaded = yaml.safe_load(f)
            data = loaded if isinstance(loaded, dict) else {}
        else:
            data = json.load(f)

    # Normalize legacy structural keys automatically. If migration applies,
    # write a backup and an exported migrated file next to the original.
    normalized = _migrate_sections_elements_to_geometry_loads(data)
    if normalized is not data:
        logger.info(
            "Formato legacy rilevato: applicata normalizzazione sections/elements → geometry/loads"
        )
        try:
            backup_path = path + ".backup"
            with open(backup_path, "w", encoding="utf-8") as bf:
                json.dump(data, bf, ensure_ascii=False, indent=2)
            migrated_path = path + ".migrated.json"
            with open(migrated_path, "w", encoding="utf-8") as mf:
                json.dump(normalized, mf, ensure_ascii=False, indent=2)
            logger.info(
                "Backup salvato su '%s' e progetto migrato su '%s'", backup_path, migrated_path
            )
        except Exception as exc:  # pragma: no cover - IO problems are external
            logger.warning("Impossibile scrivere backup/migrated file: %s", exc)
    data = migrate_dict(normalized)
    project = _dict_to_project(data)
    logger.info("Progetto caricato da '%s' (schema_version=%s)", path, project.schema_version)
    return project


def save_project(project: ProjectModel, path: str) -> None:
    """Serializza un :class:`ProjectModel` su file JSON/YAML.

    Scrive atomicamente tramite file temporaneo per evitare file corrotti.

    Args:
        project: Modello da salvare.
        path: Percorso destinazione.
    """
    data = project.model_dump(mode="json")
    from pathlib import Path

    path_obj = Path(path) if not isinstance(path, Path) else path
    tmp_path = path_obj.with_suffix(path_obj.suffix + ".tmp")
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            path_str = str(path)
            if path_str.lower().endswith((".yml", ".yaml")):
                yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
            else:
                json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise
    logger.info(
        "Progetto salvato su '%s' (schema_version=%s)",
        path,
        getattr(getattr(project, "meta", project), "schema_version", "N/A"),
    )
