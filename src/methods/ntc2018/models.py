from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Literal, Optional


@dataclass
class Apertura:
    id: str
    tipo: Literal["preesistente", "nuova", "modificata"] = "nuova"
    forma: Literal["rettangolo", "cerchio", "poligono"] = "rettangolo"
    posizione: Dict[str, float] = field(default_factory=dict)  # {"x": cm, "y": cm}
    dimensioni: Dict[str, float] = field(default_factory=dict)  # {"h": cm, "b": cm}
    distanza_appoggi: Optional[Dict[str, float]] = None
    stato: Literal["attiva", "chiusa"] = "attiva"
    note: Optional[str] = None
    rigidezza_locale: Optional[Dict[str, float]] = None

    def is_attiva(self) -> bool:
        return self.stato == "attiva"

    def normalized_dimensions(self) -> Dict[str, float]:
        if self.forma == "rettangolo":
            return {
                "h": float(self.dimensioni.get("h", 0.0)),
                "b": float(self.dimensioni.get("b", 0.0)),
            }
        if self.forma == "cerchio":
            r = float(self.dimensioni.get("r", 0.0))
            return {"h": 2.0 * r, "b": 2.0 * r}
        return {"h": 0.0, "b": 0.0}

    def area(self) -> float:
        if not self.dimensioni:
            return 0.0
        if self.forma == "rettangolo":
            return float(self.dimensioni.get("h", 0.0)) * float(self.dimensioni.get("b", 0.0))
        # semplice fallback per poligoni/cerchi
        if self.forma == "cerchio":
            r = self.dimensioni.get("r", 0.0)
            return 3.141592653589793 * r * r
        return 0.0


@dataclass
class Rinforzo:
    id: str
    tipo: Literal["cerchiatura", "intonaco_armato", "betoncino_armato", "FRP", "inserto_metallico"]
    posizione: Dict[str, Any] = field(default_factory=dict)
    dimensioni: Optional[Dict[str, float]] = None
    materiale: Optional[Dict[str, float]] = None
    ancoraggi: Optional[List[Dict[str, Any]]] = None
    efficacia: Optional[float] = None
    note: Optional[str] = None


@dataclass
class PareteMuraria:
    id: str
    lunghezza: float  # cm (lunghezza orizzontale della parete)
    altezza: float  # cm
    spessore: float  # cm (spessore della parete)
    materiale: str = "muratura_generica"
    E: float = 300000.0  # kgf/cm^2 default esempio (da adattare)
    carichi: List[Dict[str, Any]] = field(default_factory=list)
    vincoli: List[Dict[str, Any]] = field(default_factory=list)
    aperture: List[Apertura] = field(default_factory=list)
    rinforzi: List[Rinforzo] = field(default_factory=list)

    def area(self) -> float:
        return float(self.lunghezza) * float(self.altezza)

    def aperture_attive(self) -> List[Apertura]:
        return [a for a in self.aperture if a.is_attiva()]

    def area_aperture_attive(self) -> float:
        return sum(a.area() for a in self.aperture_attive())

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d
