#!/usr/bin/env python3
"""Regenerate schemas/project.schema.json from ProjectModel."""

from __future__ import annotations

import json
from pathlib import Path

from src.project.model import ProjectModel


def main() -> None:
    target = Path("schemas") / "project.schema.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(ProjectModel.model_json_schema(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Schema rigenerato: {target}")


if __name__ == "__main__":
    main()
