"""Assemblaggio globale sparso per elementi beam 2D Euler-Bernoulli.

Questo modulo implementa la subfase M.2 della Fase M:
- definizione dei nodi FEM indipendenti dal modulo telai
- contenitore ModelloFEM con connettivita e serializzazione JSON/CSV
- assemblaggio di matrice globale sparsa K_G e vettore dei carichi F_G

Unita coerenti con il repository:
- lunghezze: cm
- forze: kg
- momenti: kg*cm
- E: kg/cm^2
- A: cm^2
- I: cm^4
"""

from __future__ import annotations

import csv
import json
import logging
import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from scipy.sparse import csr_matrix, lil_matrix

from .elemento_beam import (
    BaseCaricoBeam,
    CaricoAssialeDistribuito,
    CaricoConcentrato,
    CaricoDistribuitoUniforme,
    CaricoParabolico,
    CaricoRotazioniImposte,
    CaricoTrapezoidale,
    CaricoTriangolare,
    CaricoTriangolareInverso,
    CaricoVariazioneTermicaAssiale,
    CedimentiNodali,
    ElementoBeam,
)

logger = logging.getLogger(__name__)

Vector3 = np.ndarray
ElementoKey = int | str
VincoliSerializzati = list[dict[str, object]] | dict[str, object] | None


def _vector3(values: list[float] | tuple[float, ...] | np.ndarray) -> Vector3:
    vector = np.asarray(values, dtype=float)
    if vector.shape != (3,):
        raise ValueError(f"Atteso vettore di shape (3,), ricevuto {vector.shape}.")
    return vector


def _float_if_present(value: object, default: float = 0.0) -> float:
    if value in (None, ""):
        return default
    return float(value)


def _int_required(mapping: dict[str, object], key: str) -> int:
    if key not in mapping or mapping[key] in (None, ""):
        raise ValueError(f"Campo obbligatorio mancante: {key}")
    return int(mapping[key])


def _float_required(mapping: dict[str, object], key: str) -> float:
    if key not in mapping or mapping[key] in (None, ""):
        raise ValueError(f"Campo obbligatorio mancante: {key}")
    return float(mapping[key])


def _normalize_record(raw: dict[str, object]) -> dict[str, object]:
    return {str(key): value for key, value in raw.items()}


def _angle_components_close(elemento: ElementoBeam, coseno: float, seno: float) -> bool:
    return math.isclose(elemento.coseno, coseno, abs_tol=1e-9) and math.isclose(
        elemento.seno, seno, abs_tol=1e-9
    )


def _serialize_carico(carico: BaseCaricoBeam) -> dict[str, object]:
    if isinstance(carico, CaricoDistribuitoUniforme):
        return {
            "tipo": "carico_distribuito_uniforme",
            "intensita": carico.intensita,
            "direzione_locale": carico.direzione_locale,
        }
    if isinstance(carico, CaricoAssialeDistribuito):
        return {
            "tipo": "carico_assiale_distribuito",
            "intensita": carico.intensita,
        }
    if isinstance(carico, CaricoTriangolare):
        return {
            "tipo": "carico_triangolare",
            "intensita_massima": carico.intensita_massima,
        }
    if isinstance(carico, CaricoTriangolareInverso):
        return {
            "tipo": "carico_triangolare_inverso",
            "intensita_massima": carico.intensita_massima,
        }
    if isinstance(carico, CaricoTrapezoidale):
        return {
            "tipo": "carico_trapezoidale",
            "intensita_i": carico.intensita_i,
            "intensita_j": carico.intensita_j,
        }
    if isinstance(carico, CaricoParabolico):
        return {
            "tipo": "carico_parabolico",
            "intensita_massima": carico.intensita_massima,
        }
    if isinstance(carico, CaricoConcentrato):
        return {
            "tipo": "carico_concentrato",
            "valore": carico.valore,
            "posizione_x": carico.posizione_x,
            "tipo_forza": carico.tipo,
        }
    if isinstance(carico, CedimentiNodali):
        return {
            "tipo": "cedimenti_nodali",
            "u_i": carico.u_i,
            "v_i": carico.v_i,
            "theta_i": carico.theta_i,
            "u_j": carico.u_j,
            "v_j": carico.v_j,
            "theta_j": carico.theta_j,
        }
    if isinstance(carico, CaricoRotazioniImposte):
        return {
            "tipo": "carico_rotazioni_imposte",
            "theta_i": carico.theta_i,
            "theta_j": carico.theta_j,
        }
    if isinstance(carico, CaricoVariazioneTermicaAssiale):
        return {
            "tipo": "carico_variazione_termica_assiale",
            "deformazione_imposta": carico.deformazione_imposta,
        }
    raise ValueError(
        f"Carico non serializzabile in M.2: {type(carico).__name__}. "
        "Usare carichi espliciti supportati o istanziare il modello in memoria."
    )


def _deserialize_carico(raw: dict[str, object]) -> BaseCaricoBeam:
    tipo = str(raw.get("tipo", "")).strip().lower()
    if tipo == "carico_distribuito_uniforme":
        return CaricoDistribuitoUniforme(
            intensita=float(raw["intensita"]),
            direzione_locale=str(raw.get("direzione_locale", "y")),
        )
    if tipo == "carico_assiale_distribuito":
        return CaricoAssialeDistribuito(intensita=float(raw["intensita"]))
    if tipo == "carico_triangolare":
        return CaricoTriangolare(intensita_massima=float(raw["intensita_massima"]))
    if tipo == "carico_triangolare_inverso":
        return CaricoTriangolareInverso(intensita_massima=float(raw["intensita_massima"]))
    if tipo == "carico_trapezoidale":
        return CaricoTrapezoidale(
            intensita_i=float(raw["intensita_i"]),
            intensita_j=float(raw["intensita_j"]),
        )
    if tipo == "carico_parabolico":
        return CaricoParabolico(intensita_massima=float(raw["intensita_massima"]))
    if tipo == "carico_concentrato":
        return CaricoConcentrato(
            valore=float(raw["valore"]),
            posizione_x=float(raw["posizione_x"]),
            tipo=str(raw.get("tipo_forza", "forza_y")),
        )
    if tipo == "cedimenti_nodali":
        return CedimentiNodali(
            u_i=float(raw.get("u_i", 0.0)),
            v_i=float(raw.get("v_i", 0.0)),
            theta_i=float(raw.get("theta_i", 0.0)),
            u_j=float(raw.get("u_j", 0.0)),
            v_j=float(raw.get("v_j", 0.0)),
            theta_j=float(raw.get("theta_j", 0.0)),
        )
    if tipo == "carico_rotazioni_imposte":
        return CaricoRotazioniImposte(
            theta_i=float(raw.get("theta_i", 0.0)),
            theta_j=float(raw.get("theta_j", 0.0)),
        )
    if tipo == "carico_variazione_termica_assiale":
        return CaricoVariazioneTermicaAssiale(
            deformazione_imposta=float(raw["deformazione_imposta"])
        )
    raise ValueError(f"Tipo di carico non supportato in M.2: {tipo!r}")


@dataclass(slots=True)
class Nodo:
    id: int
    x: float
    y: float
    etichetta: str = ""
    z: float = 0.0
    massa: float = 0.0

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "x": round(float(self.x), 6),
            "y": round(float(self.y), 6),
            "etichetta": self.etichetta,
            "z": round(float(self.z), 6),
            "massa": round(float(self.massa), 6),
        }

    @staticmethod
    def from_dict(data: dict[str, object]) -> "Nodo":
        mapping = _normalize_record(data)
        return Nodo(
            id=_int_required(mapping, "id"),
            x=_float_required(mapping, "x"),
            y=_float_required(mapping, "y"),
            etichetta=str(mapping.get("etichetta", "")),
            z=_float_if_present(mapping.get("z"), default=0.0),
            massa=_float_if_present(mapping.get("massa"), default=0.0),
        )


@dataclass
class ModelloFEM:
    nodi: list[Nodo]
    elementi: list[ElementoBeam]
    carichi_nodali: dict[int, np.ndarray] = field(default_factory=dict)
    carichi_elementi: dict[ElementoKey, list[BaseCaricoBeam]] = field(default_factory=dict)
    etichetta: str = ""
    metadati: dict[str, object] = field(default_factory=dict)
    vincoli: VincoliSerializzati = None
    _indice_nodo_by_id: dict[int, int] = field(init=False, repr=False, default_factory=dict)

    def __post_init__(self) -> None:
        self._indice_nodo_by_id = {}
        for indice, nodo in enumerate(self.nodi):
            if nodo.id in self._indice_nodo_by_id:
                raise ValueError(f"Id nodo duplicato: {nodo.id}")
            self._indice_nodo_by_id[nodo.id] = indice
        self._valida_elementi()
        self._valida_carichi_nodali()
        self._valida_carichi_elementi()

    @property
    def n_gdl(self) -> int:
        return 3 * len(self.nodi)

    def dof_nodo(self, id_nodo: int) -> tuple[int, int, int]:
        if id_nodo not in self._indice_nodo_by_id:
            raise KeyError(f"Nodo {id_nodo} non presente nel modello.")
        base = 3 * self._indice_nodo_by_id[id_nodo]
        return base, base + 1, base + 2

    def dof_elemento(self, elemento: ElementoBeam) -> tuple[int, int, int, int, int, int]:
        if elemento.id_nodo_iniziale is None or elemento.id_nodo_finale is None:
            raise ValueError("ElementoBeam senza id_nodo_iniziale/id_nodo_finale.")
        return (*self.dof_nodo(elemento.id_nodo_iniziale), *self.dof_nodo(elemento.id_nodo_finale))

    def nodo_by_id(self, id_nodo: int) -> Nodo:
        return self.nodi[self._indice_nodo_by_id[id_nodo]]

    def chiavi_elemento(self, indice: int, elemento: ElementoBeam) -> tuple[ElementoKey, ...]:
        chiavi: list[ElementoKey] = [indice, str(indice)]
        if elemento.etichetta:
            chiavi.append(elemento.etichetta)
        return tuple(chiavi)

    def carichi_per_elemento(self, indice: int, elemento: ElementoBeam) -> list[BaseCaricoBeam]:
        trovati: list[BaseCaricoBeam] = []
        chiavi_trovate: list[ElementoKey] = []
        for chiave in self.chiavi_elemento(indice, elemento):
            if chiave in self.carichi_elementi:
                trovati.extend(self.carichi_elementi[chiave])
                chiavi_trovate.append(chiave)
        if len(chiavi_trovate) > 1:
            raise ValueError(
                f"Carichi elemento definiti piu volte per l'elemento {indice}: {chiavi_trovate}"
            )
        return trovati

    def to_dict(self) -> dict[str, object]:
        data: dict[str, object] = {
            "etichetta": self.etichetta,
            "nodi": [nodo.to_dict() for nodo in self.nodi],
            "elementi": [elemento.to_dict() for elemento in self.elementi],
            "carichi_nodali": {
                str(id_nodo): [round(float(value), 6) for value in vettore]
                for id_nodo, vettore in self.carichi_nodali.items()
            },
            "carichi_elementi": {
                str(chiave): [_serialize_carico(carico) for carico in carichi]
                for chiave, carichi in self.carichi_elementi.items()
            },
        }
        if self.metadati:
            data["metadati"] = self.metadati
        if self.vincoli is not None:
            data["vincoli"] = self.vincoli
        return data

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ModelloFEM":
        if not isinstance(data, dict):
            raise TypeError("ModelloFEM.from_dict richiede un dizionario.")
        raw_nodi = data.get("nodi", [])
        if not isinstance(raw_nodi, list):
            raise ValueError("'nodi' deve essere una lista.")
        nodi = [Nodo.from_dict(item) for item in raw_nodi if isinstance(item, dict)]
        nodi_per_id = {nodo.id: nodo for nodo in nodi}

        raw_elementi = data.get("elementi", [])
        if not isinstance(raw_elementi, list):
            raise ValueError("'elementi' deve essere una lista.")
        elementi = [
            _elemento_from_dict(item, nodi_per_id)
            for item in raw_elementi
            if isinstance(item, dict)
        ]

        carichi_nodali: dict[int, np.ndarray] = {}
        raw_carichi_nodali = data.get("carichi_nodali", {})
        if isinstance(raw_carichi_nodali, dict):
            for chiave, vettore in raw_carichi_nodali.items():
                carichi_nodali[int(chiave)] = _vector3(vettore)  # type: ignore[arg-type]

        carichi_elementi: dict[ElementoKey, list[BaseCaricoBeam]] = {}
        raw_carichi_elementi = data.get("carichi_elementi", {})
        if isinstance(raw_carichi_elementi, dict):
            for chiave, lista_carichi in raw_carichi_elementi.items():
                if not isinstance(lista_carichi, list):
                    raise ValueError("Ogni voce di 'carichi_elementi' deve essere una lista.")
                chiave_norm: ElementoKey
                if isinstance(chiave, str) and chiave.isdigit():
                    chiave_norm = int(chiave)
                else:
                    chiave_norm = chiave
                carichi_elementi[chiave_norm] = [
                    _deserialize_carico(item) for item in lista_carichi if isinstance(item, dict)
                ]

        metadati = data.get("metadati", {})
        if not isinstance(metadati, dict):
            raise ValueError("'metadati' deve essere un dizionario se presente.")

        return cls(
            nodi=nodi,
            elementi=elementi,
            carichi_nodali=carichi_nodali,
            carichi_elementi=carichi_elementi,
            etichetta=str(data.get("etichetta", "")),
            metadati={str(key): value for key, value in metadati.items()},
            vincoli=data.get("vincoli"),
        )

    @classmethod
    def from_json(cls, path: str | Path) -> "ModelloFEM":
        with Path(path).open(encoding="utf-8") as handle:
            data = json.load(handle)
        return cls.from_dict(data)

    @classmethod
    def from_csv(cls, path_nodi: str | Path, path_elementi: str | Path) -> "ModelloFEM":
        with Path(path_nodi).open(encoding="utf-8", newline="") as handle_nodi:
            nodi_rows = [_normalize_record(row) for row in csv.DictReader(handle_nodi)]
        nodi = [Nodo.from_dict(row) for row in nodi_rows]
        nodi_per_id = {nodo.id: nodo for nodo in nodi}

        with Path(path_elementi).open(encoding="utf-8", newline="") as handle_elementi:
            elementi_rows = [
                _normalize_record(
                    {key: value for key, value in row.items() if value not in (None, "")}
                )
                for row in csv.DictReader(handle_elementi)
            ]
        elementi = [_elemento_from_dict(row, nodi_per_id) for row in elementi_rows]
        return cls(nodi=nodi, elementi=elementi)

    def _valida_elementi(self) -> None:
        for indice, elemento in enumerate(self.elementi):
            if elemento.id_nodo_iniziale is None or elemento.id_nodo_finale is None:
                raise ValueError(f"Elemento {indice} senza connettivita nodale completa.")
            if elemento.id_nodo_iniziale not in self._indice_nodo_by_id:
                raise ValueError(
                    f"Elemento {indice} fa riferimento al nodo iniziale assente: "
                    f"{elemento.id_nodo_iniziale}"
                )
            if elemento.id_nodo_finale not in self._indice_nodo_by_id:
                raise ValueError(
                    f"Elemento {indice} fa riferimento al nodo finale assente: "
                    f"{elemento.id_nodo_finale}"
                )
            nodo_i = self.nodo_by_id(elemento.id_nodo_iniziale)
            nodo_j = self.nodo_by_id(elemento.id_nodo_finale)
            dx = nodo_j.x - nodo_i.x
            dy = nodo_j.y - nodo_i.y
            lunghezza = math.hypot(dx, dy)
            if lunghezza <= 0.0:
                raise ValueError(
                    f"Elemento {indice} ha nodi coincidenti ({nodo_i.id}, {nodo_j.id})."
                )
            if not math.isclose(elemento.L, lunghezza, rel_tol=1e-9, abs_tol=1e-6):
                raise ValueError(
                    f"Elemento {indice} incoerente: L={elemento.L} ma distanza nodale={lunghezza}."
                )
            coseno = dx / lunghezza
            seno = dy / lunghezza
            if not _angle_components_close(elemento, coseno, seno):
                raise ValueError(
                    f"Elemento {indice} incoerente: angolo={elemento.angolo_rad} rad non compatibile "
                    f"con i nodi {nodo_i.id}->{nodo_j.id}."
                )

    def _valida_carichi_nodali(self) -> None:
        for id_nodo, vettore in list(self.carichi_nodali.items()):
            if id_nodo not in self._indice_nodo_by_id:
                raise ValueError(f"Carico nodale riferito a nodo assente: {id_nodo}")
            self.carichi_nodali[id_nodo] = _vector3(vettore)

    def _valida_carichi_elementi(self) -> None:
        chiavi_valide: set[ElementoKey] = set()
        for indice, elemento in enumerate(self.elementi):
            chiavi_valide.update(self.chiavi_elemento(indice, elemento))
        for chiave, carichi in self.carichi_elementi.items():
            if chiave not in chiavi_valide:
                raise ValueError(f"Chiave carichi_elementi non risolta: {chiave!r}")
            if not isinstance(carichi, list):
                raise ValueError(f"I carichi dell'elemento {chiave!r} devono essere in lista.")
            for carico in carichi:
                if not isinstance(carico, BaseCaricoBeam):
                    raise TypeError(
                        f"Carico non valido per l'elemento {chiave!r}: {type(carico).__name__}"
                    )


class Assemblatore:
    def __init__(self, modello: ModelloFEM, logger: logging.Logger | None = None):
        self.modello = modello
        self.logger = logger or logging.getLogger(__name__)

    def assembla(self) -> tuple[csr_matrix, np.ndarray]:
        n_gdl = self.modello.n_gdl
        matrice = lil_matrix((n_gdl, n_gdl), dtype=float)
        vettore = np.zeros(n_gdl, dtype=float)

        for id_nodo, carico in self.modello.carichi_nodali.items():
            gdl = self.modello.dof_nodo(id_nodo)
            vettore[list(gdl)] += carico

        for indice, elemento in enumerate(self.modello.elementi):
            gdl = self.modello.dof_elemento(elemento)
            rigidezza = elemento.matrice_rigidezza_globale()
            for riga_locale, gdl_riga in enumerate(gdl):
                for colonna_locale, gdl_colonna in enumerate(gdl):
                    matrice[gdl_riga, gdl_colonna] += rigidezza[riga_locale, colonna_locale]

            carichi = self.modello.carichi_per_elemento(indice, elemento)
            if carichi:
                trasformazione = elemento.matrice_trasformazione()
                for carico in carichi:
                    equivalente = carico.calcola_vettore_equivalente(elemento)
                    vettore_globale = np.asarray(
                        trasformazione.T @ equivalente.vettore_locale,
                        dtype=float,
                    )
                    vettore[list(gdl)] += vettore_globale
                    if self.logger.isEnabledFor(logging.DEBUG):
                        self.logger.debug(
                            "[Assemblatore] elemento=%s indice=%s carico=%s gdl=%s vettore=%s",
                            elemento.etichetta or f"elemento_{indice}",
                            indice,
                            equivalente.descrizione,
                            gdl,
                            np.array2string(vettore_globale, precision=6),
                        )

            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug(
                    "[Assemblatore] elemento=%s indice=%s dof=%s nnz_locali=%s",
                    elemento.etichetta or f"elemento_{indice}",
                    indice,
                    gdl,
                    int(np.count_nonzero(rigidezza)),
                )

        matrice_csr = matrice.tocsr()
        simmetria_ok = _is_symmetric(matrice_csr)
        densita_zeri = 100.0 * (1.0 - (matrice_csr.nnz / (n_gdl * n_gdl))) if n_gdl else 100.0
        self.logger.info(
            "[Assemblatore] n_nodi=%s n_elementi=%s n_gdl=%s nnz=%s sparsita=%.2f%% simmetria_ok=%s",
            len(self.modello.nodi),
            len(self.modello.elementi),
            n_gdl,
            matrice_csr.nnz,
            densita_zeri,
            simmetria_ok,
        )
        return matrice_csr, vettore

    def verifica_connettivita(self) -> list[str]:
        if not self.modello.nodi:
            return ["ModelloFEM senza nodi."]
        if not self.modello.elementi:
            return ["ModelloFEM senza elementi; assemblaggio globale non significativo."]

        adiacenze: dict[int, set[int]] = {nodo.id: set() for nodo in self.modello.nodi}
        for indice, elemento in enumerate(self.modello.elementi):
            if elemento.id_nodo_iniziale is None or elemento.id_nodo_finale is None:
                return [f"Elemento {indice} senza connettivita completa."]
            adiacenze[elemento.id_nodo_iniziale].add(elemento.id_nodo_finale)
            adiacenze[elemento.id_nodo_finale].add(elemento.id_nodo_iniziale)

        warning: list[str] = []
        nodi_isolati = sorted(id_nodo for id_nodo, vicini in adiacenze.items() if not vicini)
        if nodi_isolati:
            warning.append(f"Nodi isolati rilevati: {nodi_isolati}")

        visitati: set[int] = set()
        componenti = 0
        for id_nodo, vicini in adiacenze.items():
            if id_nodo in visitati or not vicini:
                continue
            componenti += 1
            stack = [id_nodo]
            while stack:
                corrente = stack.pop()
                if corrente in visitati:
                    continue
                visitati.add(corrente)
                stack.extend(adiacenze[corrente] - visitati)

        if componenti > 1:
            warning.append(f"Struttura disconnessa: {componenti} componenti con elementi attivi.")
        return warning


def _elemento_from_dict(data: dict[str, object], nodi_per_id: dict[int, Nodo]) -> ElementoBeam:
    mapping = _normalize_record(data)
    id_nodo_iniziale = _int_required(mapping, "id_nodo_iniziale")
    id_nodo_finale = _int_required(mapping, "id_nodo_finale")
    if id_nodo_iniziale not in nodi_per_id or id_nodo_finale not in nodi_per_id:
        raise ValueError(
            "I nodi referenziati dall'elemento devono essere presenti prima del parsing."
        )

    nodo_i = nodi_per_id[id_nodo_iniziale]
    nodo_j = nodi_per_id[id_nodo_finale]
    dx = nodo_j.x - nodo_i.x
    dy = nodo_j.y - nodo_i.y
    lunghezza_geometrica = math.hypot(dx, dy)
    if lunghezza_geometrica <= 0.0:
        raise ValueError(f"Elemento con nodi coincidenti: {id_nodo_iniziale}->{id_nodo_finale}")

    lunghezza = _float_if_present(mapping.get("L"), default=lunghezza_geometrica)
    angolo_rad = math.atan2(dy, dx)
    if "angolo" in mapping and mapping.get("angolo") not in (None, ""):
        unita_angolo = str(mapping.get("unita_angolo", "rad"))
        angolo_input = float(mapping["angolo"])
        angolo_norm = math.radians(angolo_input) if unita_angolo == "deg" else angolo_input
        if not math.isclose(
            math.cos(angolo_norm), math.cos(angolo_rad), abs_tol=1e-9
        ) or not math.isclose(math.sin(angolo_norm), math.sin(angolo_rad), abs_tol=1e-9):
            raise ValueError(
                f"Angolo elemento incoerente con la geometria nodale: {angolo_input} {unita_angolo}"
            )
        angolo = angolo_input
    else:
        angolo = angolo_rad
        unita_angolo = "rad"

    return ElementoBeam(
        E=_float_required(mapping, "E"),
        A=_float_required(mapping, "A"),
        I=_float_required(mapping, "I"),
        L=lunghezza,
        angolo=angolo,
        unita_angolo=unita_angolo,
        id_nodo_iniziale=id_nodo_iniziale,
        id_nodo_finale=id_nodo_finale,
        etichetta=str(mapping.get("etichetta", "")),
    )


def _is_symmetric(matrix: csr_matrix, tolleranza: float = 1e-9) -> bool:
    if matrix.shape[0] != matrix.shape[1]:
        return False
    differenza = (matrix - matrix.T).tocoo()
    if differenza.nnz == 0:
        return True
    return bool(np.all(np.abs(differenza.data) <= tolleranza))


__all__ = ["Assemblatore", "ModelloFEM", "Nodo"]
