"""Optional: CSV/Archive I/O for sections. Keeps persistence separate from GUI."""

from __future__ import annotations
import csv
import json
from typing import Iterable, List
from pathlib import Path
from sections_app.geometry_model import SectionGeometry


def export_sections_to_csv(path: str, sections: Iterable[SectionGeometry]):
    """Export a list of SectionGeometry to CSV using JSON for complex columns.

    Columns: name, type, units, exterior(json), holes(json), meta(json)
    """
    pathp = Path(path)
    pathp.parent.mkdir(parents=True, exist_ok=True)
    with pathp.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "type", "units", "exterior", "holes", "meta"])
        for s in sections:
            writer.writerow(
                [
                    s.meta.get("name", ""),
                    s.meta.get("type", ""),
                    s.units,
                    json.dumps(s.exterior),
                    json.dumps(s.holes),
                    json.dumps(s.meta),
                ]
            )


def import_sections_from_csv(path: str) -> List[SectionGeometry]:
    """Import SectionGeometry list from CSV produced by export_sections_to_csv."""
    pathp = Path(path)
    if not pathp.exists():
        return []
    out: List[SectionGeometry] = []
    with pathp.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                exterior = json.loads(row.get("exterior", "[]"))
                holes = json.loads(row.get("holes", "[]"))
                meta = json.loads(row.get("meta", "{}"))
            except Exception:
                # fallback to safe defaults
                exterior = []
                holes = []
                meta = {}
            geom = SectionGeometry(
                exterior=[tuple(p) for p in exterior],
                holes=[[tuple(p) for p in h] for h in holes],
                units=row.get("units", "cm"),
                meta=meta,
            )
            out.append(geom)
    return out
