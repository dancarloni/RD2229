"""
MaterialRepository — Gestione materiali, parametri, override, audit
"""

import uuid
import json
import copy
from typing import List, Dict, Any

class MaterialRepository:
    def __init__(self):
        self.materials: List[Dict[str, Any]] = []
        self.audit_log: List[Dict[str, Any]] = []
        self.layout_prefs: Dict[str, Any] = {}
        self._undo_stack: List[List[Dict[str, Any]]] = []
        self._redo_stack: List[List[Dict[str, Any]]] = []

    def load_from_file(self, path: str):
        with open(path, 'r', encoding='utf-8') as f:
            self.materials = json.load(f)

    def save_to_file(self, path: str):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.materials, f, indent=2)

    def add_material(self, data: Dict[str, Any]):
        self._push_undo_state()
        self._clear_redo()
        data['id'] = self._generate_id(data)
        self.materials.append(data)
        self._log_audit('add', data)

    def update_material(self, idx: int, data: Dict[str, Any]):
        self._push_undo_state()
        self._clear_redo()
        old = self.materials[idx].copy()
        self.materials[idx].update(data)
        self._log_audit('update', {'old': old, 'new': self.materials[idx]})

    def batch_update(self, indices: List[int], key: str, value: Any):
        self._push_undo_state()
        self._clear_redo()
        for idx in indices:
            old = self.materials[idx].get(key)
            self.materials[idx][key] = value
            self._log_audit('batch_update', {'idx': idx, 'key': key, 'old': old, 'new': value})

    def delete_material(self, idx: int):
        self._push_undo_state()
        self._clear_redo()
        mat = self.materials.pop(idx)
        self._log_audit('delete', mat)

    def filter_materials(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        result = self.materials
        for k, v in filters.items():
            result = [m for m in result if m.get(k) == v]
        return result

    def sort_materials(self, key: str, reverse: bool = False):
        self.materials.sort(key=lambda m: m.get(key, ''), reverse=reverse)

    def _generate_id(self, data: Dict[str, Any]) -> str:
        return str(uuid.uuid5(uuid.NAMESPACE_OID, json.dumps(data, sort_keys=True)))

    def _log_audit(self, action: str, data: Any):
        self.audit_log.append({'action': action, 'data': data})

    def export_material(self, idx: int, fmt: str = 'HTML') -> str:
        mat = self.materials[idx]
        if fmt == 'HTML':
            return '<br>'.join(f'<b>{k}</b>: {v}' for k, v in mat.items())
        elif fmt == 'Markdown':
            return '\n'.join(f'**{k}**: {v}' for k, v in mat.items())
        elif fmt == 'CSV':
            return ','.join(str(mat[k]) for k in mat.keys())
        else:
            return '\n'.join(f'{k}: {v}' for k, v in mat.items())

    def import_material(self, text: str, fmt: str = 'CSV'):
        # Placeholder: implement parsing for each format
        pass

    def reset_layout(self):
        self.layout_prefs = {}
        self._log_audit('reset_layout', {})

    def save_layout(self, prefs: Dict[str, Any]):
        self.layout_prefs = prefs
        self._log_audit('save_layout', prefs)

    def undo(self):
        if not self._undo_stack:
            return
        # push current state to redo
        self._redo_stack.append(copy.deepcopy(self.materials))
        state = self._undo_stack.pop()
        self.materials = copy.deepcopy(state)
        self._log_audit('undo', {})

    def redo(self):
        if not self._redo_stack:
            return
        self._undo_stack.append(copy.deepcopy(self.materials))
        state = self._redo_stack.pop()
        self.materials = copy.deepcopy(state)
        self._log_audit('redo', {})

    def _push_undo_state(self):
        self._undo_stack.append(copy.deepcopy(self.materials))

    def _clear_redo(self):
        self._redo_stack.clear()
