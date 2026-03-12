"""Sezione generica per aste di traliccio.

Dataclass unificato per piatti, angolari e profili standard.
Usato dal modulo cordolo_reticolare per il dimensionamento
di cordoli metallici reticolari in sommità a pareti in muratura.

Convenzioni geometriche per piatto ORIZZONTALE (orientamento confermato):
  b = dimensione grande in Y (spessore muro, nel piano del traliccio) [cm]
  t = dimensione piccola in Z (verticale, fuori piano del traliccio) [cm]
  ix = b/√12  (raggio in piano → instabilità in piano)
  iy = t/√12  (raggio fuori piano → governa, è il minore)

Unità: cm per geometrie, cm² per aree, cm⁴ per inerzie, kg/m per massa.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path


class TipoSezioneAsta(str, Enum):
    """Tipo di sezione per aste di traliccio."""

    PIATTO = "piatto"
    ANGOLARE = "angolare"
    PROFILO_STANDARD = "profilo_standard"


@dataclass
class SezioneAsta:
    """Proprietà di sezione per un'asta di traliccio.

    Attributi:
        A:         area [cm²]
        Ix:        inerzia asse forte (in piano) [cm⁴]
        Iy:        inerzia asse debole (fuori piano) [cm⁴]
        ix:        raggio d'inerzia forte (in piano) [cm]
        iy:        raggio d'inerzia debole (fuori piano) [cm] — governa instabilità
        nome:      denominazione profilo
        tipo:      tipo di sezione
        b:         dimensione grande [cm]
        t:         dimensione piccola [cm]
        massa_kg_m: massa lineare [kg/m]
    """

    A: float
    Ix: float
    Iy: float
    ix: float
    iy: float
    nome: str
    tipo: TipoSezioneAsta
    b: float = 0.0
    t: float = 0.0
    massa_kg_m: float = 0.0

    @classmethod
    def da_piatto(cls, b: float, t: float) -> SezioneAsta:
        """Crea sezione piatto orizzontale.

        Il piatto giace nel piano orizzontale XY del traliccio:
          b = dimensione grande in Y (spessore muro, nel piano del traliccio)
          t = dimensione piccola in Z (verticale, fuori piano)

        Instabilità in piano:  λ_ip = L / ix = L / (b/√12)
        Instabilità fuori piano: λ_fp = L / iy = L / (t/√12)  ← governa
        """
        if b <= 0 or t <= 0:
            raise ValueError(f"Dimensioni piatto non valide: b={b}, t={t}")
        if t > b:
            raise ValueError(f"b deve essere >= t per piatto: b={b}, t={t}")
        A = b * t
        Ix = t * b**3 / 12  # inerzia rispetto asse fuori piano Z → λ_in_piano
        Iy = b * t**3 / 12  # inerzia rispetto asse verticale Y → λ_fuori_piano
        ix = b / math.sqrt(12)
        iy = t / math.sqrt(12)
        massa = A * 7.85e-3 * 100  # A [cm²] × ρ [kg/cm³] × 100 [cm/m]
        return cls(
            A=A,
            Ix=Ix,
            Iy=Iy,
            ix=ix,
            iy=iy,
            nome=f"Piatto {b*10:.0f}x{t*10:.0f}",
            tipo=TipoSezioneAsta.PIATTO,
            b=b,
            t=t,
            massa_kg_m=massa,
        )

    @classmethod
    def da_angolare_pari(cls, b: float, t: float) -> SezioneAsta:
        """Crea sezione angolare pari L b×b×t.

        Calcola geometria esatta (senza raccordi) degli assi centroidali e
        dei momenti principali d'inerzia (u-u forte a 45°, v-v debole).

        Il raggio minimo iy = i_v (asse debole a 45°) governa l'instabilità.
        Approssimazione i_v ≈ 0.195×b è confermata dai valori calcolati.
        """
        if b <= 0 or t <= 0:
            raise ValueError(f"Dimensioni angolare non valide: b={b}, t={t}")
        if t >= b:
            raise ValueError(f"t deve essere < b per angolare pari: b={b}, t={t}")

        # Aree delle due ali (senza sovrapposizione al vertice)
        A_h = b * t  # ala orizzontale
        A_v = (b - t) * t  # ala verticale
        A = A_h + A_v  # = (2b - t) * t

        # Centroide dall'angolo interno (per simmetria x_g = y_g)
        x_g = (A_h * b / 2 + A_v * t / 2) / A

        # Centroide dell'ala verticale: y = t + (b-t)/2 = (b+t)/2
        y_v = (b + t) / 2

        # Inerzia rispetto all'asse orizzontale passante per il centroide
        I_cx = (
            b * t**3 / 12
            + A_h * (x_g - t / 2) ** 2
            + t * (b - t) ** 3 / 12
            + A_v * (x_g - y_v) ** 2
        )

        # Prodotto d'inerzia centroidale (negativo per l'angolo nel 1° quadrante)
        I_xy = A_h * (b / 2 - x_g) * (t / 2 - x_g) + A_v * (t / 2 - x_g) * (y_v - x_g)

        # Momenti principali (assi ruotati di 45° rispetto agli assi geometrici)
        # I_u (forte) = I_cx + |I_xy|, I_v (debole) = I_cx - |I_xy|
        I1 = I_cx + abs(I_xy)
        I2 = I_cx - abs(I_xy)

        ix = math.sqrt(I1 / A) if A > 0 else 0.0
        iy = math.sqrt(I2 / A) if A > 0 else 0.0  # raggio minimo, governa
        massa = A * 7.85e-3 * 100

        return cls(
            A=A,
            Ix=I1,
            Iy=I2,
            ix=ix,
            iy=iy,
            nome=f"L{b*10:.0f}x{b*10:.0f}x{t*10:.0f}",
            tipo=TipoSezioneAsta.ANGOLARE,
            b=b,
            t=t,
            massa_kg_m=massa,
        )

    @classmethod
    def da_profilo(cls, profilo: object) -> SezioneAsta:
        """Crea SezioneAsta da ProfiloAcciaio del sagomario.

        Args:
            profilo: ProfiloAcciaio (da sagomario.py)
        """
        return cls(
            A=profilo.A,
            Ix=profilo.Ix,
            Iy=profilo.Iy,
            ix=profilo.ix,
            iy=profilo.iy,
            nome=profilo.nome,
            tipo=TipoSezioneAsta.PROFILO_STANDARD,
            massa_kg_m=profilo.massa_kg_m,
        )

    @classmethod
    def from_dict(cls, data: dict) -> SezioneAsta:
        """Crea da dizionario (es. da JSON)."""
        tipo = TipoSezioneAsta(data.get("tipo", "profilo_standard"))
        return cls(
            A=data["A"],
            Ix=data["Ix"],
            Iy=data["Iy"],
            ix=data["ix"],
            iy=data["iy"],
            nome=data["nome"],
            tipo=tipo,
            b=data.get("b", 0.0),
            t=data.get("t", 0.0),
            massa_kg_m=data.get("massa_kg_m", 0.0),
        )

    def to_dict(self) -> dict:
        d = asdict(self)
        d["tipo"] = self.tipo.value
        return d


class CatalogoSezioni:
    """Catalogo sezioni caricato da JSON (piatti o angolari)."""

    def __init__(self) -> None:
        self._sezioni: dict[str, SezioneAsta] = {}

    def carica_da_json(self, path: str | Path) -> int:
        import json

        path = Path(path)
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        count = 0
        for item in data:
            s = SezioneAsta.from_dict(item)
            self._sezioni[s.nome] = s
            count += 1
        return count

    def get(self, nome: str) -> SezioneAsta | None:
        return self._sezioni.get(nome)

    def tutti(self) -> list[SezioneAsta]:
        return sorted(self._sezioni.values(), key=lambda s: s.A)

    def list_nomi(self) -> list[str]:
        return [s.nome for s in self.tutti()]

    def cerca_A_minimo(self, A_min: float) -> list[SezioneAsta]:
        """Sezioni con A >= A_min, ordinate per A crescente."""
        return [s for s in self.tutti() if s.A >= A_min]

    def count(self) -> int:
        return len(self._sezioni)


def _default_data_dir() -> Path:
    return Path(__file__).parent.parent.parent / "data" / "steel"


def carica_catalogo_piatti(directory: Path | None = None) -> CatalogoSezioni:
    """Carica il catalogo piatti da piatti.json."""
    cat = CatalogoSezioni()
    d = directory or _default_data_dir()
    path = d / "piatti.json"
    if path.exists():
        cat.carica_da_json(path)
    return cat


def carica_catalogo_angolari(directory: Path | None = None) -> CatalogoSezioni:
    """Carica il catalogo angolari da angolari.json."""
    cat = CatalogoSezioni()
    d = directory or _default_data_dir()
    path = d / "angolari.json"
    if path.exists():
        cat.carica_da_json(path)
    return cat
