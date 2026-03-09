"""Sagomario profili in acciaio laminati a caldo (EN 10365).

Gestisce il caricamento, la ricerca e il filtraggio di profili
strutturali IPE, HEA, HEB, HEM, UPN da archivi JSON.

Unità: cm per lunghezze, cm² per aree, cm³ per moduli resistenti,
       cm⁴ per momenti d'inerzia, cm⁶ per costante di ingobbamento,
       kg/m per massa lineare.
"""

from __future__ import annotations

import csv
import json
import logging
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path

try:
    from src.core.registro_log import registro as _registro
except ImportError:
    _registro = None  # ambienti headless / test

_logger = logging.getLogger(__name__)


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


# ── Costanti per import CSV ──────────────────────────────────────────────────

_CAMPI_OBBLIGATORI: tuple[str, ...] = (
    "nome", "famiglia", "h", "b", "tw", "tf", "r",
    "A", "massa_kg_m", "Ix", "Wx", "Wpl_x", "ix",
    "Iy", "Wy", "Wpl_y", "iy",
)
_CAMPI_OPZIONALI: tuple[str, ...] = ("It", "Iw", "hi", "d", "AL")
_POSITIVI: frozenset[str] = frozenset(
    "h b tw tf r A massa_kg_m Ix Wx Wpl_x ix Iy Wy Wpl_y iy".split()
)

_TEMPLATE_CSV_HEADER = """\
# Template importazione profili acciaio custom — RD2229
# Compilare una riga per profilo. Righe che iniziano con # sono ignorate.
# Campi obbligatori: nome, famiglia, h, b, tw, tf, r, A, massa_kg_m, Ix, Wx, Wpl_x, ix, Iy, Wy, Wpl_y, iy
# Campi opzionali (default=0): It, Iw, hi, d, AL
# Unita': lunghezze cm | aree cm2 | moduli cm3 | inerzie cm4 | ingobbamento cm6 | massa kg/m
# Famiglia: stringa libera (IPE, HEA, CUSTOM, L_100x100, piatto_20x5, ecc.)
# ATTENZIONE: nomi gia' presenti nel sagomario vengono sovrascritti con warning nel log
nome,famiglia,h,b,tw,tf,r,A,massa_kg_m,Ix,Wx,Wpl_x,ix,Iy,Wy,Wpl_y,iy,It,Iw,hi,d,AL
IPE200_custom,CUSTOM,20.0,10.0,0.56,0.85,1.20,28.5,22.4,1943.0,194.0,221.0,8.26,142.0,28.5,44.6,2.24,6.98,13000.0,18.3,15.9,0.0
"""


class SagomarioAcciaio:
    """Repository profili in acciaio con ricerca e filtraggio."""

    def __init__(self) -> None:
        self._profili: dict[str, ProfiloAcciaio] = {}
        self._custom_names: set[str] = set()

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

    def get(self, nome: str) -> ProfiloAcciaio | None:
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
    ) -> ProfiloAcciaio | None:
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

    # ── CSV custom ───────────────────────────────────────────────────────────

    @staticmethod
    def _valida_riga_csv(
        riga: dict[str, str], numero_riga: int
    ) -> tuple[ProfiloAcciaio | None, str | None]:
        """Valida una riga CSV e restituisce (ProfiloAcciaio, None) o (None, errore)."""
        # Campi obbligatori presenti
        for campo in _CAMPI_OBBLIGATORI:
            if campo not in riga:
                return None, f"riga {numero_riga}: campo obbligatorio '{campo}' mancante"

        # Conversione numerica
        valori: dict[str, float] = {}
        for campo in _CAMPI_OBBLIGATORI[2:]:  # skip "nome" e "famiglia"
            raw = riga.get(campo, "").strip()
            try:
                valori[campo] = float(raw)
            except ValueError:
                return None, f"riga {numero_riga}: campo '{campo}' non numerico: '{raw}'"

        for campo in _CAMPI_OPZIONALI:
            raw = riga.get(campo, "0").strip() or "0"
            try:
                valori[campo] = float(raw)
            except ValueError:
                valori[campo] = 0.0

        # Range fisici: tutti i campi in _POSITIVI devono essere > 0
        for campo in _POSITIVI:
            if valori.get(campo, 0.0) <= 0.0:
                return None, (
                    f"riga {numero_riga}: campo '{campo}' deve essere > 0, "
                    f"trovato {valori.get(campo, 0.0)}"
                )

        dati = {
            "nome": riga["nome"].strip(),
            "famiglia": riga.get("famiglia", "CUSTOM").strip(),
            **valori,
        }
        return ProfiloAcciaio.from_dict(dati), None

    def _salva_custom(self, directory: Path | None = None) -> None:
        """Salva i profili custom in sagomario_custom.json."""
        if not self._custom_names:
            return
        if directory is None:
            directory = Path(__file__).parent.parent.parent / "data" / "steel"
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        custom = [
            self._profili[nome].to_dict()
            for nome in sorted(self._custom_names)
            if nome in self._profili
        ]
        dest = directory / "sagomario_custom.json"
        with open(dest, "w", encoding="utf-8") as f:
            json.dump(custom, f, indent=2, ensure_ascii=False)

    def carica_da_csv(
        self,
        path: str | Path,
        custom_dir: str | Path | None = None,
    ) -> tuple[int, list[str]]:
        """Carica profili custom da file CSV.

        Args:
            path: Percorso del file CSV.
            custom_dir: Directory dove salvare sagomario_custom.json.
                        Se None usa la directory data/steel/ di default.

        Returns:
            (n_caricati, lista_warnings)
        """
        path = Path(path)
        warnings: list[str] = []
        n = 0

        with open(path, encoding="utf-8", newline="") as f:
            righe_filtrate = (r for r in f if not r.lstrip().startswith("#"))
            reader = csv.DictReader(righe_filtrate)
            for i, riga in enumerate(reader, start=2):
                profilo, errore = self._valida_riga_csv(riga, i)
                if errore:
                    warnings.append(errore)
                    continue
                assert profilo is not None
                if profilo.nome in self._profili:
                    msg = f"Profilo '{profilo.nome}' già presente — sovrascrittura"
                    warnings.append(msg)
                    _logger.warning("sagomario: %s", msg)
                    if _registro is not None:
                        try:
                            _registro.operazione(
                                modulo="sagomario",
                                operazione=msg,
                                livello="WARNING",
                            )
                        except Exception:
                            pass
                self._profili[profilo.nome] = profilo
                self._custom_names.add(profilo.nome)
                n += 1

        if custom_dir is not None:
            self._salva_custom(Path(custom_dir))
        else:
            self._salva_custom()
        return n, warnings

    @staticmethod
    def genera_template_csv(path: str | Path) -> None:
        """Genera un file CSV template auto-esplicativo per l'import custom.

        Args:
            path: Percorso di destinazione del file template.
        """
        path = Path(path)
        path.write_text(_TEMPLATE_CSV_HEADER, encoding="utf-8")
