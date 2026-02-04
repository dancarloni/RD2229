from __future__ import annotations

import json
import logging
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, Optional

from typing import TYPE_CHECKING

from verification_items import VerificationItem

if TYPE_CHECKING:  # pragma: no cover - typing only
    from verification_table import VerificationInput

logger = logging.getLogger(__name__)


class VerificationItemsRepository:
    """Repository persistente degli elementi soggetti a verifica.

    Questo repository funge da "archivio di progetto" degli elementi (travi,
    pilastri, ecc.) e mantiene separata la logica di persistenza dalla UI.
    La UI legge e scrive esclusivamente tramite questo repository, così è
    possibile aggiungere/modificare/salvare elementi senza toccare la tabella.

    API:
      - get_all() -> List[VerificationItem]
      - get_by_id(item_id) -> Optional[VerificationItem]
      - save(item) -> None  (crea o aggiorna)
      - delete(item_id) -> None
      - clear() -> None
      - load_from_file() -> None
      - save_to_file() -> None
    """

    def __init__(self, path: str = "verification_items.json") -> None:
        self._path = Path(path)
        self._items: Dict[str, VerificationItem] = {}
        self.load_from_file()

    def get_all(self) -> List[VerificationItem]:
        return list(self._items.values())

    def get_by_id(self, item_id: str) -> Optional[VerificationItem]:
        return self._items.get(item_id)

    def save(self, item: VerificationItem) -> None:
        logger.debug("Saving VerificationItem id=%s name=%s", item.id, item.name)
        self._items[item.id] = item
        self.save_to_file()

    def delete(self, item_id: str) -> None:
        if item_id in self._items:
            logger.debug("Deleting VerificationItem id=%s", item_id)
            del self._items[item_id]
            self.save_to_file()

    def clear(self) -> None:
        logger.debug("Clearing all VerificationItems (count=%d)", len(self._items))
        self._items.clear()
        self.save_to_file()

    def load_from_file(self) -> None:
        """Carica gli elementi dal file JSON.

        Se il file non esiste, non genera errore e lascia l'archivio vuoto.
        """
        self._items.clear()
        if not self._path.exists():
            return
        try:
            with self._path.open("r", encoding="utf-8") as fh:
                raw = json.load(fh)
            if not isinstance(raw, list):
                logger.warning("Verification items file %s non contiene una lista", self._path)
                return
            for idx, item in enumerate(raw):
                try:
                    from verification_table import VerificationInput
                    input_data = item.get("input", {}) if isinstance(item, dict) else {}
                    ver_input = VerificationInput(**input_data)
                    ver_item = VerificationItem(
                        id=item.get("id", ""),
                        name=item.get("name", ""),
                        group=item.get("group"),
                        input=ver_input,
                    )
                    if ver_item.id:
                        self._items[ver_item.id] = ver_item
                except Exception:
                    logger.exception("Errore parsing VerificationItem #%s", idx)
        except Exception:
            logger.exception("Errore caricamento VerificationItems da %s", self._path)

    def save_to_file(self) -> None:
        """Salva gli elementi su file JSON con struttura semplice."""
        try:
            if self._path.parent.exists() is False and str(self._path.parent) != ".":
                self._path.parent.mkdir(parents=True, exist_ok=True)
            payload = []
            for item in self._items.values():
                payload.append(
                    {
                        "id": item.id,
                        "name": item.name,
                        "group": item.group,
                        "input": asdict(item.input),
                    }
                )
            tmp = self._path.with_suffix(self._path.suffix + ".tmp")
            with tmp.open("w", encoding="utf-8") as fh:
                json.dump(payload, fh, indent=2, ensure_ascii=False)
            tmp.replace(self._path)
        except Exception:
            logger.exception("Errore salvataggio VerificationItems su %s", self._path)
