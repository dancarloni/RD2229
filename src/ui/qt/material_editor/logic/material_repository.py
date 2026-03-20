"""
MaterialRepository — Gestione materiali, parametri, override, audit

Include metodi per la persistenza diretta ai cataloghi di sistema
(data/materials/catalogo_*.json) con backup automatico (.bak).
"""

import copy
import json
import logging
import pathlib
import shutil
import uuid
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def compute_material_code(data: Dict[str, Any]) -> str:
    """
    Calcola un codice hash UUID5 riproducibile dai parametri del materiale.
    Esclude i campi interni ('id', 'codice', chiavi con suffisso '_override').
    """
    excluded = {"id", "codice"}
    filtered = {
        k: v for k, v in sorted(data.items()) if k not in excluded and not k.endswith("_override")
    }
    return str(uuid.uuid5(uuid.NAMESPACE_OID, json.dumps(filtered, sort_keys=True, default=str)))


class MaterialRepository:
    def __init__(self):
        import os

        self.materials: List[Dict[str, Any]] = []
        self.audit_log: List[Dict[str, Any]] = []
        self.layout_prefs: Dict[str, Any] = {}
        self._undo_stack: List[List[Dict[str, Any]]] = []
        self._redo_stack: List[List[Dict[str, Any]]] = []
        # Carica tutti i materiali dai cataloghi JSON in data/materials/
        # Trova la root del progetto risalendo le directory
        import pathlib

        here = pathlib.Path(__file__).resolve()
        root = here
        while not (root / "data" / "materials").is_dir() and root.parent != root:
            root = root.parent
        base_dir = str(root / "data" / "materials")
        for fname in os.listdir(base_dir):
            if fname.startswith("catalogo_") and fname.endswith(".json"):
                fpath = os.path.join(base_dir, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        mats = json.load(f)
                        if isinstance(mats, list):
                            self.materials.extend(mats)
                except Exception:
                    pass

    def load_from_file(self, path: str):
        with open(path, "r", encoding="utf-8") as f:
            self.materials = json.load(f)

    def recompute_all_derived(self, config_loader) -> int:
        """Ricalcola i parametri derivati per tutti i materiali in memoria.

        Non scrive su disco: aggiorna solo i dict in-place per la sessione corrente.
        Utile per correggere valori E=0 presenti nei cataloghi storici.
        Restituisce il numero di materiali aggiornati.
        """
        updated = 0
        for mat in self.materials:
            famiglia = mat.get("famiglia", "")
            norma = mat.get("norma_riferimento") or mat.get("norma", "")
            if not famiglia or not norma:
                continue
            try:
                schema = config_loader.get_norm_schema(famiglia, norma)
                if not schema:
                    continue
                derived = config_loader.compute_derived(mat, schema, famiglia=famiglia)
                derived.pop("_formula_warnings", None)
                mat.update(derived)
                updated += 1
            except Exception:
                pass
        return updated

    def save_to_file(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.materials, f, indent=2)

    def add_material(self, data: Dict[str, Any]):
        self._push_undo_state()
        self._clear_redo()
        data["id"] = self._generate_id(data)
        # Calcola codice se non fornito o vuoto
        if not data.get("codice"):
            data["codice"] = compute_material_code(data)
        self.materials.append(data)
        self._log_audit("add", data)

    def update_material(self, idx: int, data: Dict[str, Any]):
        self._push_undo_state()
        self._clear_redo()
        old = self.materials[idx].copy()
        self.materials[idx].update(data)
        # Ricalcola codice se non fornito o vuoto dopo aggiornamento
        if not self.materials[idx].get("codice"):
            self.materials[idx]["codice"] = compute_material_code(self.materials[idx])
        self._log_audit("update", {"old": old, "new": self.materials[idx]})

    def batch_update(self, indices: List[int], key: str, value: Any):
        self._push_undo_state()
        self._clear_redo()
        for idx in indices:
            old = self.materials[idx].get(key)
            self.materials[idx][key] = value
            self._log_audit("batch_update", {"idx": idx, "key": key, "old": old, "new": value})

    def delete_material(self, idx: int):
        self._push_undo_state()
        self._clear_redo()
        mat = self.materials.pop(idx)
        self._log_audit("delete", mat)

    def filter_materials(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        result = self.materials
        for k, v in filters.items():
            result = [m for m in result if m.get(k) == v]
        return result

    def sort_materials(self, key: str, reverse: bool = False):
        self.materials.sort(key=lambda m: m.get(key, ""), reverse=reverse)

    def _generate_id(self, data: Dict[str, Any]) -> str:
        return str(uuid.uuid5(uuid.NAMESPACE_OID, json.dumps(data, sort_keys=True)))

    def _log_audit(self, action: str, data: Any):
        self.audit_log.append({"action": action, "data": data})

    def export_material(self, idx: int, fmt: str = "HTML") -> str:
        mat = self.materials[idx]
        if fmt == "HTML":
            return "<br>".join(f"<b>{k}</b>: {v}" for k, v in mat.items())
        elif fmt == "Markdown":
            return "\n".join(f"**{k}**: {v}" for k, v in mat.items())
        elif fmt == "CSV":
            return ",".join(str(mat[k]) for k in mat.keys())
        else:
            return "\n".join(f"{k}: {v}" for k, v in mat.items())

    def import_material(self, text: str, fmt: str = "CSV"):
        # Placeholder: implement parsing for each format
        pass

    def reset_layout(self):
        self.layout_prefs = {}
        self._log_audit("reset_layout", {})

    def save_layout(self, prefs: Dict[str, Any]):
        self.layout_prefs = prefs
        self._log_audit("save_layout", prefs)

    def undo(self):
        if not self._undo_stack:
            return
        # push current state to redo
        self._redo_stack.append(copy.deepcopy(self.materials))
        state = self._undo_stack.pop()
        self.materials = copy.deepcopy(state)
        self._log_audit("undo", {})

    def redo(self):
        if not self._redo_stack:
            return
        self._undo_stack.append(copy.deepcopy(self.materials))
        state = self._redo_stack.pop()
        self.materials = copy.deepcopy(state)
        self._log_audit("redo", {})

    def _push_undo_state(self):
        self._undo_stack.append(copy.deepcopy(self.materials))

    def _clear_redo(self):
        self._redo_stack.clear()

    # ------------------------------------------------------------------
    # Persistenza catalogo di sistema (data/materials/catalogo_*.json)
    # ------------------------------------------------------------------

    @staticmethod
    def _find_data_dir() -> pathlib.Path:
        here = pathlib.Path(__file__).resolve()
        root = here
        while not (root / "data" / "materials").is_dir() and root.parent != root:
            root = root.parent
        return root / "data" / "materials"

    def get_catalog_path(self, famiglia: str, norma: str) -> Optional[pathlib.Path]:
        """Restituisce il path del file catalogo corrispondente a (famiglia, norma).

        Cerca in ordine:
        1. ``catalogo_{norma.lower()}.json``
        2. ``catalogo_{famiglia}_{norma.lower()}.json``
        3. Qualsiasi ``catalogo_*.json`` che contiene materiali con quella norma/famiglia.

        Returns:
            Path del file trovato, o None se non trovato.
        """
        data_dir = self._find_data_dir()
        norm_lower = norma.lower()
        fam_lower = famiglia.lower()

        candidates = [
            data_dir / f"catalogo_{norm_lower}.json",
            data_dir / f"catalogo_{fam_lower}_{norm_lower}.json",
            data_dir / f"catalogo_{norm_lower}_{fam_lower}.json",
        ]
        for c in candidates:
            if c.exists():
                return c
        return None

    def save_catalog(
        self,
        famiglia: str,
        norma: str,
        catalog_path: Optional[pathlib.Path | str] = None,
        create_backup: bool = True,
    ) -> pathlib.Path:
        """Salva i materiali del repo (filtrati per famiglia+norma) nel catalogo di sistema.

        Legge il catalogo esistente, sostituisce/aggiunge i materiali con stessa famiglia+norma,
        e riscrive il file con backup atomico.

        Args:
            famiglia: Famiglia da salvare (es. "calcestruzzo").
            norma: Norma da salvare (es. "NTC2018").
            catalog_path: Path esplicito del file catalogo. Se None, cercato automaticamente.
            create_backup: Se True, crea ``<file>.bak`` prima di scrivere.

        Returns:
            Path del file catalogo scritto.

        Raises:
            FileNotFoundError: Se il file catalogo non viene trovato e catalog_path non è fornito.
            IOError: Se la scrittura fallisce.
        """
        if catalog_path is not None:
            path = pathlib.Path(catalog_path)
        else:
            path = self.get_catalog_path(famiglia, norma)
            if path is None:
                # Crea nuovo file
                data_dir = self._find_data_dir()
                path = data_dir / f"catalogo_{norma.lower()}.json"

        # Carica catalogo esistente
        existing: List[Dict[str, Any]] = []
        if path.exists():
            try:
                existing = json.loads(path.read_text(encoding="utf-8"))
                if not isinstance(existing, list):
                    existing = []
            except Exception as exc:
                logger.warning("Catalogo corrotto %s: %s — verrà sovrascritto", path, exc)
                existing = []

        # Backup prima della scrittura
        if create_backup and path.exists():
            bak = path.with_suffix(".bak")
            shutil.copy2(path, bak)
            logger.debug("Backup catalogo: %s", bak)

        # Filtra materiali repo per famiglia+norma
        repo_subset = [
            m for m in self.materials
            if m.get("famiglia") == famiglia
            and (m.get("norma_riferimento") == norma or m.get("norma") == norma)
        ]

        # Merge: rimuovi dal catalogo quelli con stessa famiglia+norma, aggiungi i nuovi
        merged = [
            m for m in existing
            if not (
                m.get("famiglia") == famiglia
                and (m.get("norma_riferimento") == norma or m.get("norma") == norma)
            )
        ]
        merged.extend(repo_subset)

        # Scrittura atomica
        tmp = path.with_suffix(".tmp")
        try:
            tmp.write_text(
                json.dumps(merged, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            tmp.replace(path)
        except Exception as exc:
            tmp.unlink(missing_ok=True)
            raise IOError(f"Scrittura catalogo fallita: {exc}") from exc

        logger.info(
            "Catalogo salvato: %s (%d materiali per %s/%s)", path, len(repo_subset), famiglia, norma
        )
        return path

    def restore_catalog_from_backup(self, path: pathlib.Path | str) -> None:
        """Ripristina un catalogo dal suo file .bak.

        Args:
            path: Path del file catalogo (non del .bak).

        Raises:
            FileNotFoundError: Se il backup non esiste.
        """
        path = pathlib.Path(path)
        bak = path.with_suffix(".bak")
        if not bak.exists():
            raise FileNotFoundError(f"Backup non trovato: {bak}")
        shutil.copy2(bak, path)
        logger.info("Catalogo ripristinato da backup: %s → %s", bak, path)
