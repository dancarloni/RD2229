"""Sagomario profili in acciaio laminati a caldo (EN 10365).

Gestisce il caricamento, la ricerca e il filtraggio di profili
strutturali IPE, HEA, HEB, HEM, UPN da archivi JSON.

Unità: cm per lunghezze, cm² per aree, cm³ per moduli resistenti,
       cm⁴ per momenti d'inerzia, cm⁶ per costante di ingobbamento,
       kg/m per massa lineare.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Optional


class FamigliaProfilo(str, Enum):
    """Famiglie di profili laminati a caldo."""
    IPE = "IPE"
    HEA = "HEA"
    HEB = "HEB"
    HEM = "HEM"
    UPN = "UPN"


@dataclass
class ProfiloAcciaio:
    """Profilo laminato a caldo con proprietà geometriche e statiche.

    Tutte le dimensioni in cm, aree in cm², moduli in cm³,
    inerzie in cm⁴, massa in kg/m.
    """
    nome: str                    # es. "IPE 200"
    famiglia: str                # es. "IPE"

    # Dimensioni geometriche
    h: float                     # altezza totale [cm]
    b: float                     # larghezza ala [cm]
    tw: float                    # spessore anima [cm]
    tf: float                    # spessore ala [cm]
    r: float                     # raggio raccordo [cm]

    # Proprietà della sezione
    A: float                     # area [cm²]
    massa_kg_m: float            # massa per metro [kg/m]

    # Asse forte (x-x)
    Ix: float                    # momento d'inerzia [cm⁴]
    Wx: float                    # modulo elastico [cm³]
    Wpl_x: float                 # modulo plastico [cm³]
    ix: float                    # raggio d'inerzia [cm]

    # Asse debole (y-y)
    Iy: float                    # momento d'inerzia [cm⁴]
    Wy: float                    # modulo elastico [cm³]
    Wpl_y: float                 # modulo plastico [cm³]
    iy: float                    # raggio d'inerzia [cm]

    # Proprietà torsionali (opzionali)
    It: float = 0.0              # costante di torsione (St. Venant) [cm⁴]
    Iw: float = 0.0              # costante di ingobbamento [cm⁶]

    # Proprietà aggiuntive
    hi: float = 0.0              # altezza anima (h - 2·tf) [cm]
    d: float = 0.0               # altezza diritta anima (h - 2·tf - 2·r) [cm]
    AL: float = 0.0              # superficie laterale per metro [m²/m]

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> ProfiloAcciaio:
        known = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in known}
        return cls(**filtered)

    @property
    def rapporto_hw_tw(self) -> float:
        """Rapporto altezza anima / spessore anima (per classe sezione)."""
        hw = self.h - 2 * self.tf
        return hw / self.tw if self.tw > 0 else 0.0

    @property
    def rapporto_cf_tf(self) -> float:
        """Rapporto sbalzo ala / spessore ala (per classe sezione)."""
        c = (self.b - self.tw) / 2 - self.r
        return c / self.tf if self.tf > 0 else 0.0


class SagomarioAcciaio:
    """Repository profili in acciaio con ricerca e filtraggio."""

    def __init__(self) -> None:
        self._profili: dict[str, ProfiloAcciaio] = {}

    def count(self) -> int:
        return len(self._profili)

    def carica_da_json(self, path: str | Path) -> int:
        """Carica profili da file JSON. Ritorna il numero di profili caricati."""
        path = Path(path)
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        count = 0
        for item in data:
            profilo = ProfiloAcciaio.from_dict(item)
            self._profili[profilo.nome] = profilo
            count += 1
        return count

    def carica_tutti(self, directory: str | Path | None = None) -> int:
        """Carica tutti i file sagomario_*.json dalla directory data."""
        if directory is None:
            directory = Path(__file__).parent.parent.parent / "data" / "steel"
        directory = Path(directory)
        if not directory.exists():
            return 0

        total = 0
        for f in sorted(directory.glob("sagomario_*.json")):
            total += self.carica_da_json(f)
        return total

    def get(self, nome: str) -> Optional[ProfiloAcciaio]:
        """Cerca profilo per nome esatto (es. 'IPE 200')."""
        return self._profili.get(nome)

    def list_famiglie(self) -> list[str]:
        """Ritorna le famiglie disponibili."""
        return sorted({p.famiglia for p in self._profili.values()})

    def list_by_famiglia(self, famiglia: str) -> list[ProfiloAcciaio]:
        """Ritorna profili di una famiglia, ordinati per altezza."""
        result = [p for p in self._profili.values() if p.famiglia == famiglia]
        return sorted(result, key=lambda p: p.h)

    def list_nomi(self, famiglia: str | None = None) -> list[str]:
        """Ritorna lista nomi profili, opzionalmente filtrati per famiglia."""
        if famiglia:
            return [p.nome for p in self.list_by_famiglia(famiglia)]
        return sorted(self._profili.keys())

    def cerca_per_Wx_minimo(
        self, Wx_min: float, famiglia: str | None = None
    ) -> list[ProfiloAcciaio]:
        """Cerca profili con Wx >= Wx_min, ordinati per Wx crescente."""
        profili = (
            self.list_by_famiglia(famiglia) if famiglia
            else list(self._profili.values())
        )
        result = [p for p in profili if p.Wx >= Wx_min]
        return sorted(result, key=lambda p: p.Wx)

    def cerca_per_altezza(
        self, h_min: float, h_max: float, famiglia: str | None = None
    ) -> list[ProfiloAcciaio]:
        """Cerca profili con h_min <= h <= h_max."""
        profili = (
            self.list_by_famiglia(famiglia) if famiglia
            else list(self._profili.values())
        )
        result = [p for p in profili if h_min <= p.h <= h_max]
        return sorted(result, key=lambda p: p.h)

    def profilo_ottimale(
        self, Wx_min: float, famiglia: str | None = None
    ) -> Optional[ProfiloAcciaio]:
        """Ritorna il profilo più leggero con Wx >= Wx_min."""
        candidati = self.cerca_per_Wx_minimo(Wx_min, famiglia)
        if not candidati:
            return None
        return min(candidati, key=lambda p: p.massa_kg_m)

    def tutti(self) -> list[ProfiloAcciaio]:
        """Ritorna tutti i profili caricati."""
        return sorted(self._profili.values(), key=lambda p: (p.famiglia, p.h))

    def esporta_json(self, path: str | Path) -> None:
        """Esporta tutti i profili in un file JSON."""
        path = Path(path)
        data = [p.to_dict() for p in self.tutti()]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
