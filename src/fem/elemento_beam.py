"""Elemento beam 2D Euler-Bernoulli e carichi nodali equivalenti.

Convenzione dei segni locale, esplicita e coerente con la FEM classica:
- asse locale x: dal nodo i al nodo j
- asse locale y: positivo verso l'alto nel sistema locale dell'elemento
- forza assiale positiva: trazione lungo +x
- forza trasversale positiva: lungo +y
- momento nodale positivo: antiorario

Nota di interoperabilita con il repo:
- i diagrammi grafici in src/grafici/spostamenti.py usano freccia positiva verso il basso
- questo modulo mantiene la convenzione FEM classica per rigidezza e carichi equivalenti
- la conversione verso convenzioni grafiche resta responsabilita dei livelli successivi

Unita attese:
- lunghezze: cm
- E: kg/cm^2
- A: cm^2
- I: cm^4
- carichi distribuiti trasversali: kg/cm
- forze concentrate: kg
- momenti: kg*cm
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Literal

import numpy as np

Vector6 = np.ndarray


def _vector6(values: list[float] | tuple[float, ...] | np.ndarray) -> Vector6:
    vector = np.asarray(values, dtype=float)
    if vector.shape != (6,):
        raise ValueError(f"Atteso vettore di shape (6,), ricevuto {vector.shape}.")
    return vector


@dataclass(frozen=True)
class CaricoEquivalente:
    """Risultato di un carico equivalente locale 6x1."""

    vettore_locale: Vector6
    descrizione: str
    passaggi: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "vettore_locale", _vector6(self.vettore_locale))

    def __add__(self, other: CaricoEquivalente) -> CaricoEquivalente:
        return CaricoEquivalente(
            vettore_locale=self.vettore_locale + other.vettore_locale,
            descrizione=f"{self.descrizione} + {other.descrizione}",
            passaggi=self.passaggi + other.passaggi,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "descrizione": self.descrizione,
            "vettore_locale": [round(float(value), 6) for value in self.vettore_locale],
            "passaggi": list(self.passaggi),
        }


@dataclass(frozen=True)
class ElementoBeam:
    """Elemento beam piano Euler-Bernoulli a 6 GDL locali.

    L'angolo puo essere fornito in gradi o radianti; internamente viene
    normalizzato in radianti.
    """

    E: float
    A: float
    I: float
    L: float
    angolo: float = 0.0
    unita_angolo: Literal["rad", "deg"] = "rad"
    id_nodo_iniziale: int | None = None
    id_nodo_finale: int | None = None
    etichetta: str = ""
    passaggi_calcolo: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        for name in ("E", "A", "I", "L"):
            value = getattr(self, name)
            if value <= 0.0:
                raise ValueError(f"{name} deve essere positivo, ricevuto {value}.")
        if self.unita_angolo not in {"rad", "deg"}:
            raise ValueError("unita_angolo deve essere 'rad' oppure 'deg'.")

    @property
    def angolo_rad(self) -> float:
        if self.unita_angolo == "deg":
            return math.radians(self.angolo)
        return float(self.angolo)

    @property
    def coseno(self) -> float:
        return math.cos(self.angolo_rad)

    @property
    def seno(self) -> float:
        return math.sin(self.angolo_rad)

    @property
    def rigidezza_assiale(self) -> float:
        return self.E * self.A / self.L

    @property
    def rigidezza_flessionale(self) -> float:
        return self.E * self.I

    def matrice_rigidezza_locale(self) -> np.ndarray:
        ea_l = self.rigidezza_assiale
        ei = self.rigidezza_flessionale
        l = self.L
        l2 = l * l
        l3 = l2 * l

        matrix = np.array(
            [
                [ea_l, 0.0, 0.0, -ea_l, 0.0, 0.0],
                [0.0, 12.0 * ei / l3, 6.0 * ei / l2, 0.0, -12.0 * ei / l3, 6.0 * ei / l2],
                [0.0, 6.0 * ei / l2, 4.0 * ei / l, 0.0, -6.0 * ei / l2, 2.0 * ei / l],
                [-ea_l, 0.0, 0.0, ea_l, 0.0, 0.0],
                [0.0, -12.0 * ei / l3, -6.0 * ei / l2, 0.0, 12.0 * ei / l3, -6.0 * ei / l2],
                [0.0, 6.0 * ei / l2, 2.0 * ei / l, 0.0, -6.0 * ei / l2, 4.0 * ei / l],
            ],
            dtype=float,
        )
        return matrix

    def matrice_trasformazione(self) -> np.ndarray:
        c = self.coseno
        s = self.seno
        return np.array(
            [
                [c, s, 0.0, 0.0, 0.0, 0.0],
                [-s, c, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, c, s, 0.0],
                [0.0, 0.0, 0.0, -s, c, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
            ],
            dtype=float,
        )

    def matrice_rigidezza_globale(self) -> np.ndarray:
        transform = self.matrice_trasformazione()
        local = self.matrice_rigidezza_locale()
        return np.asarray(transform.T @ local @ transform, dtype=float)

    def spostamenti_imposti_equivalenti(self, spostamenti_locali: Vector6) -> CaricoEquivalente:
        vector = _vector6(spostamenti_locali)
        fixed_end = self.matrice_rigidezza_locale() @ vector
        return CaricoEquivalente(
            vettore_locale=fixed_end,
            descrizione="Spostamenti/rotazioni imposte",
            passaggi=(
                "f_eq = k_locale * d_imposto",
                "d_imposto = [u_i, v_i, theta_i, u_j, v_j, theta_j] locale",
            ),
        )

    def combina_carichi(self, carichi: list[BaseCaricoBeam]) -> CaricoEquivalente:
        totale = np.zeros(6, dtype=float)
        passaggi: list[str] = []
        descrizioni: list[str] = []
        for carico in carichi:
            equivalente = carico.calcola_vettore_equivalente(self)
            totale += equivalente.vettore_locale
            passaggi.extend(equivalente.passaggi)
            descrizioni.append(equivalente.descrizione)
        return CaricoEquivalente(
            vettore_locale=totale,
            descrizione=" + ".join(descrizioni) if descrizioni else "Nessun carico",
            passaggi=tuple(passaggi),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "E": round(self.E, 6),
            "A": round(self.A, 6),
            "I": round(self.I, 6),
            "L": round(self.L, 6),
            "angolo": round(self.angolo, 6),
            "unita_angolo": self.unita_angolo,
            "angolo_rad": round(self.angolo_rad, 12),
            "id_nodo_iniziale": self.id_nodo_iniziale,
            "id_nodo_finale": self.id_nodo_finale,
            "etichetta": self.etichetta,
        }


class BaseCaricoBeam(ABC):
    """Interfaccia comune per carichi equivalenti locali di un elemento beam."""

    @abstractmethod
    def calcola_vettore_equivalente(self, elemento: ElementoBeam) -> CaricoEquivalente:
        raise NotImplementedError


def _shape_functions_bending(x: float, l: float) -> np.ndarray:
    xi = x / l
    n1 = 1.0 - 3.0 * xi**2 + 2.0 * xi**3
    n2 = l * (xi - 2.0 * xi**2 + xi**3)
    n3 = 3.0 * xi**2 - 2.0 * xi**3
    n4 = l * (-(xi**2) + xi**3)
    return np.array([n1, n2, n3, n4], dtype=float)


def _integrate_transverse_load(
    elemento: ElementoBeam,
    funzione_carico: Callable[[float], float],
    n_punti: int = 8,
) -> np.ndarray:
    nodi, pesi = np.polynomial.legendre.leggauss(n_punti)
    risultato = np.zeros(4, dtype=float)
    for nodo, peso in zip(nodi, pesi, strict=True):
        x = 0.5 * elemento.L * (nodo + 1.0)
        shape = _shape_functions_bending(x, elemento.L)
        qx = funzione_carico(x)
        risultato += peso * shape * qx
    return risultato * (0.5 * elemento.L)


def _embed_transverse(vector4: np.ndarray) -> Vector6:
    return _vector6([0.0, vector4[0], vector4[1], 0.0, vector4[2], vector4[3]])


def _embed_axial(vector2: np.ndarray) -> Vector6:
    return _vector6([vector2[0], 0.0, 0.0, vector2[1], 0.0, 0.0])


@dataclass(frozen=True)
class CaricoDistribuitoUniforme(BaseCaricoBeam):
    intensita: float
    direzione_locale: Literal["y", "x"] = "y"

    def calcola_vettore_equivalente(self, elemento: ElementoBeam) -> CaricoEquivalente:
        l = elemento.L
        q = self.intensita
        if self.direzione_locale == "x":
            vector = _embed_axial(np.array([q * l / 2.0, q * l / 2.0], dtype=float))
        else:
            vector = _embed_transverse(
                np.array([q * l / 2.0, q * l**2 / 12.0, q * l / 2.0, -q * l**2 / 12.0])
            )
        return CaricoEquivalente(
            vettore_locale=vector,
            descrizione="Carico distribuito uniforme",
            passaggi=(f"q = {q}", f"L = {l}", "Formula chiusa beam 2D Euler-Bernoulli"),
        )


@dataclass(frozen=True)
class CaricoAssialeDistribuito(BaseCaricoBeam):
    intensita: float

    def calcola_vettore_equivalente(self, elemento: ElementoBeam) -> CaricoEquivalente:
        q = self.intensita
        l = elemento.L
        return CaricoEquivalente(
            vettore_locale=_embed_axial(np.array([q * l / 2.0, q * l / 2.0], dtype=float)),
            descrizione="Carico assiale distribuito",
            passaggi=("f_eq = qL/2 [1, 1] asse locale x",),
        )


@dataclass(frozen=True)
class CaricoTriangolare(BaseCaricoBeam):
    intensita_massima: float

    def calcola_vettore_equivalente(self, elemento: ElementoBeam) -> CaricoEquivalente:
        l = elemento.L
        qmax = self.intensita_massima
        vector = _embed_transverse(
            np.array(
                [
                    3.0 * qmax * l / 20.0,
                    qmax * l**2 / 30.0,
                    7.0 * qmax * l / 20.0,
                    -qmax * l**2 / 20.0,
                ]
            )
        )
        return CaricoEquivalente(
            vettore_locale=vector,
            descrizione="Carico triangolare crescente i->j",
            passaggi=("q(x) = qmax * x / L", "Formula chiusa beam 2D"),
        )


@dataclass(frozen=True)
class CaricoTriangolareInverso(BaseCaricoBeam):
    intensita_massima: float

    def calcola_vettore_equivalente(self, elemento: ElementoBeam) -> CaricoEquivalente:
        l = elemento.L
        qmax = self.intensita_massima
        vector = _embed_transverse(
            np.array(
                [
                    7.0 * qmax * l / 20.0,
                    qmax * l**2 / 20.0,
                    3.0 * qmax * l / 20.0,
                    -qmax * l**2 / 30.0,
                ]
            )
        )
        return CaricoEquivalente(
            vettore_locale=vector,
            descrizione="Carico triangolare decrescente i->j",
            passaggi=("q(x) = qmax * (1 - x / L)", "Formula chiusa beam 2D"),
        )


@dataclass(frozen=True)
class CaricoTrapezoidale(BaseCaricoBeam):
    intensita_i: float
    intensita_j: float

    def calcola_vettore_equivalente(self, elemento: ElementoBeam) -> CaricoEquivalente:
        uniforme = CaricoDistribuitoUniforme(self.intensita_i)
        delta = self.intensita_j - self.intensita_i
        triangolare = CaricoTriangolare(delta)
        risultato = uniforme.calcola_vettore_equivalente(
            elemento
        ) + triangolare.calcola_vettore_equivalente(elemento)
        return CaricoEquivalente(
            vettore_locale=risultato.vettore_locale,
            descrizione="Carico trapezoidale",
            passaggi=(
                f"q_i = {self.intensita_i}",
                f"q_j = {self.intensita_j}",
                "Decomposizione in uniforme + triangolare",
            ),
        )


@dataclass(frozen=True)
class CaricoDistribuitoGenerico(BaseCaricoBeam):
    funzione_intensita: Callable[[float, float], float]
    descrizione: str = "Carico distribuito generico"
    n_punti_integrazione: int = 8

    def calcola_vettore_equivalente(self, elemento: ElementoBeam) -> CaricoEquivalente:
        vector4 = _integrate_transverse_load(
            elemento,
            lambda x: self.funzione_intensita(x, elemento.L),
            n_punti=self.n_punti_integrazione,
        )
        return CaricoEquivalente(
            vettore_locale=_embed_transverse(vector4),
            descrizione=self.descrizione,
            passaggi=("Integrazione numerica Gauss-Legendre del carico distribuito",),
        )


@dataclass(frozen=True)
class CaricoParabolico(BaseCaricoBeam):
    intensita_massima: float

    def calcola_vettore_equivalente(self, elemento: ElementoBeam) -> CaricoEquivalente:
        generico = CaricoDistribuitoGenerico(
            funzione_intensita=lambda x, l: self.intensita_massima * (x / l) ** 2,
            descrizione="Carico parabolico",
        )
        risultato = generico.calcola_vettore_equivalente(elemento)
        return CaricoEquivalente(
            vettore_locale=risultato.vettore_locale,
            descrizione="Carico parabolico",
            passaggi=("q(x) = qmax * (x/L)^2", "Fallback numerico Gauss-Legendre"),
        )


@dataclass(frozen=True)
class CaricoConcentrato(BaseCaricoBeam):
    valore: float
    posizione_x: float
    tipo: Literal["forza_y", "forza_x", "momento"] = "forza_y"

    def calcola_vettore_equivalente(self, elemento: ElementoBeam) -> CaricoEquivalente:
        a = self.posizione_x
        l = elemento.L
        if not 0.0 <= a <= l:
            raise ValueError(f"posizione_x deve stare in [0, L], ricevuto {a} con L={l}.")
        b = l - a
        if self.tipo == "forza_x":
            vector = _embed_axial(np.array([self.valore * b / l, self.valore * a / l], dtype=float))
        elif self.tipo == "momento":
            vector4 = np.array(
                [
                    -6.0 * self.valore * a * b / l**3,
                    self.valore * b * (2.0 * a - b) / l**2,
                    6.0 * self.valore * a * b / l**3,
                    self.valore * a * (2.0 * b - a) / l**2,
                ],
                dtype=float,
            )
            vector = _embed_transverse(vector4)
        else:
            shape = _shape_functions_bending(a, l)
            vector = _embed_transverse(self.valore * shape)
        return CaricoEquivalente(
            vettore_locale=vector,
            descrizione=f"Carico concentrato {self.tipo}",
            passaggi=(f"a = {a}", f"b = {b}", "Interpolazione esatta con shape functions"),
        )


@dataclass(frozen=True)
class CedimentiNodali(BaseCaricoBeam):
    u_i: float = 0.0
    v_i: float = 0.0
    theta_i: float = 0.0
    u_j: float = 0.0
    v_j: float = 0.0
    theta_j: float = 0.0

    def calcola_vettore_equivalente(self, elemento: ElementoBeam) -> CaricoEquivalente:
        return elemento.spostamenti_imposti_equivalenti(
            _vector6([self.u_i, self.v_i, self.theta_i, self.u_j, self.v_j, self.theta_j])
        )


@dataclass(frozen=True)
class CaricoRotazioniImposte(BaseCaricoBeam):
    theta_i: float = 0.0
    theta_j: float = 0.0

    def calcola_vettore_equivalente(self, elemento: ElementoBeam) -> CaricoEquivalente:
        return elemento.spostamenti_imposti_equivalenti(
            _vector6([0.0, 0.0, self.theta_i, 0.0, 0.0, self.theta_j])
        )


@dataclass(frozen=True)
class CaricoVariazioneTermicaAssiale(BaseCaricoBeam):
    deformazione_imposta: float

    def calcola_vettore_equivalente(self, elemento: ElementoBeam) -> CaricoEquivalente:
        forza = elemento.E * elemento.A * self.deformazione_imposta
        return CaricoEquivalente(
            vettore_locale=_vector6([-forza, 0.0, 0.0, forza, 0.0, 0.0]),
            descrizione="Variazione termica assiale equivalente",
            passaggi=("N = EA * epsilon_imp",),
        )
