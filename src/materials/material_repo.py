"""Repository dei materiali.

Gestisce CRUD, persistenza JSON, e integrazione con le fonti normative.

Funzionalità:
- Caricamento/salvataggio materiali da/su file JSON
- CRUD completo (add, get, remove, list)
- Filtro per famiglia (calcestruzzo, acciaio, muratura)
- Validazione integrata
- Caricamento materiali di default
- Integrazione con material_sources.json
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from .material_model import (
    Material,
    crea_acciaio_ntc2018,
    crea_calcestruzzo_ntc2018,
    crea_muratura_ntc2018,
)
from .validation import validate_material

logger = logging.getLogger(__name__)


class MaterialRepository:
    """Repository per i materiali strutturali.

    Gestisce una collezione in-memory di Material con persistenza JSON.
    """

    def __init__(self) -> None:
        self._materials: dict[str, Material] = {}
        self._sources: list[dict[str, Any]] = []

    # --- CRUD ---

    def add_material(self, material: Material) -> None:
        """Aggiunge un materiale al repository.

        Se esiste già un materiale con lo stesso ID, viene sovrascritto
        con un warning nel log.

        Parametri:
            material: Materiale da aggiungere.
        """
        if material.material_id in self._materials:
            logger.warning(
                "Materiale '%s' già presente, verrà sovrascritto.",
                material.material_id,
            )
        self._materials[material.material_id] = material
        logger.info("Materiale aggiunto: %s", material.material_id)

    def get(self, material_id: str) -> Material | None:
        """Restituisce il materiale richiesto.

        Parametri:
            material_id: Identificatore univoco del materiale.

        Restituisce:
            Material se trovato, None altrimenti.
        """
        mat = self._materials.get(material_id)
        if mat is None:
            logger.debug("Materiale '%s' non trovato.", material_id)
        return mat

    def remove(self, material_id: str) -> bool:
        """Rimuove un materiale dal repository.

        Parametri:
            material_id: Identificatore del materiale da rimuovere.

        Restituisce:
            True se il materiale è stato rimosso, False se non trovato.
        """
        if material_id in self._materials:
            del self._materials[material_id]
            logger.info("Materiale rimosso: %s", material_id)
            return True
        logger.warning("Materiale '%s' non trovato per rimozione.", material_id)
        return False

    def list_all(self) -> list[Material]:
        """Restituisce tutti i materiali caricati."""
        return list(self._materials.values())

    def list_by_famiglia(self, famiglia: str) -> list[Material]:
        """Restituisce i materiali di una specifica famiglia.

        Parametri:
            famiglia: "calcestruzzo", "acciaio", o "muratura".
        """
        return [m for m in self._materials.values() if m.famiglia == famiglia]

    def count(self) -> int:
        """Restituisce il numero di materiali nel repository."""
        return len(self._materials)

    # --- Validazione ---

    def validate_all(self) -> dict[str, list[str]]:
        """Valida tutti i materiali nel repository.

        Restituisce:
            Dizionario {material_id: [lista errori]}.
            Le chiavi con lista vuota indicano materiali validi.
        """
        results: dict[str, list[str]] = {}
        for m in self._materials.values():
            errors = validate_material(m)
            results[m.material_id] = errors
            if errors:
                logger.warning(
                    "Materiale '%s' ha %d errori di validazione.",
                    m.material_id,
                    len(errors),
                )
        return results

    # --- Persistenza JSON ---

    def load_from_json(self, path: str | Path) -> int:
        """Carica materiali da un file JSON.

        Il file deve contenere un array JSON di oggetti materiale,
        ciascuno serializzato con Material.to_dict().

        Parametri:
            path: Percorso del file JSON.

        Restituisce:
            Numero di materiali caricati.
        """
        path = Path(path)
        if not path.exists():
            logger.warning("File materiali non trovato: %s", path)
            return 0

        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            logger.error("Il file %s non contiene un array JSON.", path)
            return 0

        count = 0
        for item in data:
            try:
                mat = Material.from_dict(dict(item))
                self._materials[mat.material_id] = mat
                count += 1
            except Exception:
                logger.exception("Errore nel caricamento di un materiale da %s", path)

        logger.info("Caricati %d materiali da %s", count, path)
        return count

    def save_to_json(self, path: str | Path) -> int:
        """Salva tutti i materiali su un file JSON.

        Parametri:
            path: Percorso del file JSON di destinazione.

        Restituisce:
            Numero di materiali salvati.
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        data = [m.to_dict() for m in self._materials.values()]

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info("Salvati %d materiali su %s", len(data), path)
        return len(data)

    # --- Fonti normative ---

    def load_sources(self, sources_path: str | Path) -> int:
        """Carica il catalogo fonti normative da material_sources.json.

        Parametri:
            sources_path: Percorso del file material_sources.json.

        Restituisce:
            Numero di fonti caricate.
        """
        sources_path = Path(sources_path)
        if not sources_path.exists():
            logger.warning("File fonti non trovato: %s", sources_path)
            return 0

        with open(sources_path, encoding="utf-8") as f:
            self._sources = json.load(f)

        logger.info("Caricate %d fonti normative da %s", len(self._sources), sources_path)
        return len(self._sources)

    def get_sources(self) -> list[dict[str, Any]]:
        """Restituisce il catalogo fonti normative caricato."""
        return list(self._sources)

    def get_source(self, source_id: str) -> dict[str, Any] | None:
        """Restituisce una fonte normativa per ID.

        Parametri:
            source_id: Identificatore della fonte (es. "NTC2018", "RD2229").
        """
        for src in self._sources:
            if src.get("id") == source_id:
                return dict(src)
        return None

    # --- Materiali di default ---

    def carica_defaults(self) -> int:
        """Popola il repository con materiali di default.

        Crea materiali standard per calcestruzzo (NTC2018 e TA),
        acciaio (NTC2018 e TA), e muratura (NTC2018).

        Restituisce:
            Numero di materiali aggiunti.
        """
        defaults: list[Material] = []

        # Calcestruzzo NTC2018
        for classe in ["C20/25", "C25/30", "C28/35", "C30/37", "C35/45"]:
            defaults.append(crea_calcestruzzo_ntc2018(classe))

        # Calcestruzzo TA (RD2229) — valori storici
        for rck, sigma_c28, sigma_c, tau_c0, tau_c1, n in [
            (200, 200.0, 50.0, 5.0, 14.0, 10),
            (250, 250.0, 62.5, 5.5, 16.0, 10),
            (300, 300.0, 75.0, 6.0, 18.0, 10),
        ]:
            mat = Material(
                material_id=f"cls_Rck{rck}_RD2229",
                descrizione=f"Calcestruzzo Rck {rck} — RD 2229/39",
                famiglia="calcestruzzo",
                norma_riferimento="RD2229",
                densita_kg_m3=2400.0,
                sigma_c28=float(sigma_c28),
                sigma_c_adm=float(sigma_c),
                tau_c0_adm=float(tau_c0),
                tau_c1_adm=float(tau_c1),
                n_omogenizzazione=float(n),
                gamma_c=1.0,
                alpha_cc=1.0,
                nu=0.20,
            )
            defaults.append(mat)

        # Acciaio NTC2018
        for tipo in ["B450C", "B450A"]:
            defaults.append(crea_acciaio_ntc2018(tipo))

        # Acciaio TA (RD2229) — valori storici
        for nome, sigma_s, es_val in [
            ("Aq42", 1400.0, 2100000.0),
            ("Aq50", 1600.0, 2100000.0),
            ("Aq60", 2000.0, 2100000.0),
        ]:
            mat = Material(
                material_id=f"acc_{nome}_RD2229",
                descrizione=f"Acciaio {nome} — RD 2229/39",
                famiglia="acciaio",
                norma_riferimento="RD2229",
                densita_kg_m3=7850.0,
                sigma_s_adm=sigma_s,
                gamma_s=1.0,
                E=es_val,
                nu=0.30,
            )
            defaults.append(mat)

        # Muratura NTC2018
        defaults.append(crea_muratura_ntc2018("mattoni_pieni", "M10"))
        defaults.append(crea_muratura_ntc2018("blocchi_cls", "M5"))

        for mat in defaults:
            self._materials[mat.material_id] = mat

        logger.info("Caricati %d materiali di default.", len(defaults))
        return len(defaults)
