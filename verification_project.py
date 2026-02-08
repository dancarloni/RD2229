from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

DEFAULT_FILE_TYPE = "RD_VerificaSezioni_Project"
DEFAULT_MODULE = "VerificationTable"
DEFAULT_VERSION = 1


@dataclass
class VerificationProject:
    materials: dict[str, dict[str, Any]] = field(default_factory=lambda: {"cls": {}, "steel": {}})
    sections: dict[str, dict[str, Any]] = field(default_factory=dict)
    elements: list[dict[str, Any]] = field(default_factory=list)
    path: str | None = None
    dirty: bool = False
    last_action_was_add_list: bool = False
    created_at: str | None = None

    def new_project(self) -> None:
        self.materials = {"cls": {}, "steel": {}}
        self.sections = {}
        self.elements = []
        self.path = None
        self.dirty = False
        self.last_action_was_add_list = False
        self.created_at = datetime.utcnow().isoformat()

    def _validate_header(self, data: dict[str, Any]) -> None:
        if data.get("file_type") != DEFAULT_FILE_TYPE or data.get("module") != DEFAULT_MODULE:
            raise ValueError("File non riconosciuto come progetto VerificationTable")

    def load_from_file(self, path: str) -> None:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        self._validate_header(data)
        self.created_at = data.get("created_at") or datetime.utcnow().isoformat()

        # Load materials
        mats = data.get("materials") or {}
        cls_list = mats.get("cls") or []
        steel_list = mats.get("steel") or []
        self.materials = {"cls": {}, "steel": {}}
        for m in cls_list:
            if m.get("id"):
                self.materials["cls"][m["id"]] = m
        for m in steel_list:
            if m.get("id"):
                self.materials["steel"][m["id"]] = m

        # Sections
        self.sections = {}
        for s in data.get("sections") or []:
            sid = s.get("id") or s.get("name")
            if sid:
                self.sections[sid] = s

        # Elements
        self.elements = data.get("elements") or []

        self.path = path
        self.dirty = False
        self.last_action_was_add_list = False

    def save_to_file(self, path: str) -> None:
        header = {
            "file_type": DEFAULT_FILE_TYPE,
            "module": DEFAULT_MODULE,
            "version": DEFAULT_VERSION,
            "created_at": self.created_at or datetime.utcnow().isoformat(),
        }
        mats = {
            "cls": list(self.materials.get("cls", {}).values()),
            "steel": list(self.materials.get("steel", {}).values()),
        }
        sections = list(self.sections.values())
        data = {
            **header,
            "materials": mats,
            "sections": sections,
            "elements": self.elements,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self.path = path
        self.dirty = False
        self.last_action_was_add_list = False

    def add_elements_from_file(self, path: str) -> tuple[int, int, int]:
        """Carica un file .jsonp e unisce materiali/sezioni/elementi senza cancellare.

        Returns tuple (new_materials, new_sections, new_elements_added)
        """
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        self._validate_header(data)

        new_mats = 0
        mats = data.get("materials") or {}
        for typ in ("cls", "steel"):
            for m in mats.get(typ) or []:
                mid = m.get("id")
                if mid and mid not in self.materials.get(typ, {}):
                    self.materials.setdefault(typ, {})[mid] = m
                    new_mats += 1

        new_secs = 0
        for s in data.get("sections") or []:
            sid = s.get("id") or s.get("name")
            if sid and sid not in self.sections:
                self.sections[sid] = s
                new_secs += 1

        new_elems = 0
        for e in data.get("elements") or []:
            # avoid identical element ids
            eid = e.get("id")
            if eid and any(existing.get("id") == eid for existing in self.elements):
                continue
            self.elements.append(e)
            new_elems += 1

        self.dirty = True
        self.last_action_was_add_list = True
        return new_mats, new_secs, new_elems
