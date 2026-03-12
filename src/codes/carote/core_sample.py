"""Dataclass per carote di calcestruzzo, fattori di correzione e risultato conversione.

Unita' interne: MPa per resistenze, mm per geometria carota.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CorrectionFactors:
    """Fattori di correzione applicati alla resistenza della carota.

    Ogni fattore e' >= 1.0 se incrementa la resistenza equivalente,
    < 1.0 se la riduce.  Il prodotto k_total = k_ld * k_dir * k_arm * k_um * k_diam * k_dd
    viene applicato a f_core per ottenere f_is.

    overrides: dizionario libero per sovrascritture utente (es. {"k_ld": 0.95}).
    """

    k_ld: float = 1.0  # snellezza L/D
    k_dir: float = 1.0  # direzione estrazione (1.0 vert, ~1.06-1.08 orizz)
    k_arm: float = 1.0  # presenza armatura
    k_um: float = 1.0  # umidita' (naturale/saturo/asciutto)
    k_diam: float = 1.0  # normalizzazione a diametro 150 mm
    k_dd: float = 1.0  # danno da estrazione
    overrides: dict[str, float] = field(default_factory=dict)

    @property
    def k_total(self) -> float:
        """Prodotto di tutti i fattori (con overrides applicati)."""
        factors = {
            "k_ld": self.k_ld,
            "k_dir": self.k_dir,
            "k_arm": self.k_arm,
            "k_um": self.k_um,
            "k_diam": self.k_diam,
            "k_dd": self.k_dd,
        }
        factors.update(self.overrides)
        result = 1.0
        for v in factors.values():
            result *= v
        return result


@dataclass
class CoreSample:
    """Singola carota di calcestruzzo prelevata in situ.

    Attributi:
        sample_id: identificativo univoco (es. "C1", "C2")
        f_core_mpa: resistenza a compressione da laboratorio [MPa]
        diameter_mm: diametro carota [mm] (default 100)
        length_mm: lunghezza carota [mm] (default 100)
        direction: "verticale" | "orizzontale"
        has_rebar: True se la carota contiene armatura
        rebar_diameter_mm: diametro barra armatura inclusa [mm]
        moisture: "naturale" | "saturo" | "asciutto"
        drilling_damage: "normale" | "severo"
        elemento_origine: descrizione elemento di provenienza
        note: note libere
    """

    sample_id: str
    f_core_mpa: float
    diameter_mm: float = 100.0
    length_mm: float = 100.0
    direction: str = "verticale"
    has_rebar: bool = False
    rebar_diameter_mm: float = 0.0
    moisture: str = "naturale"
    drilling_damage: str = "normale"
    elemento_origine: str = ""
    note: str = ""

    def __post_init__(self) -> None:
        if self.f_core_mpa <= 0:
            raise ValueError(f"f_core_mpa deve essere > 0, ricevuto {self.f_core_mpa}")
        if self.diameter_mm <= 0:
            raise ValueError(f"diameter_mm deve essere > 0, ricevuto {self.diameter_mm}")
        if self.length_mm <= 0:
            raise ValueError(f"length_mm deve essere > 0, ricevuto {self.length_mm}")
        if self.direction not in ("verticale", "orizzontale"):
            raise ValueError(
                f"direction deve essere 'verticale' o 'orizzontale', ricevuto '{self.direction}'"
            )
        if self.moisture not in ("naturale", "saturo", "asciutto"):
            raise ValueError(
                f"moisture deve essere 'naturale', 'saturo' o 'asciutto', ricevuto '{self.moisture}'"
            )

    @property
    def ld_ratio(self) -> float:
        """Rapporto lunghezza/diametro."""
        return self.length_mm / self.diameter_mm


@dataclass
class ConversionResult:
    """Risultato della conversione di una carota con una formulazione specifica.

    Attributi:
        sample_id: identificativo carota
        formulation: nome formulazione usata
        f_core_mpa: resistenza originale da lab [MPa]
        correction_factors: fattori applicati
        k_total: prodotto fattori
        f_is_mpa: resistenza in situ equivalente [MPa]
        passaggi_calcolo: traccia dei passaggi intermedi
    """

    sample_id: str
    formulation: str
    f_core_mpa: float
    correction_factors: CorrectionFactors
    k_total: float
    f_is_mpa: float
    passaggi_calcolo: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Serializza per report/export."""
        return {
            "sample_id": self.sample_id,
            "formulation": self.formulation,
            "f_core_mpa": self.f_core_mpa,
            "k_total": round(self.k_total, 4),
            "f_is_mpa": round(self.f_is_mpa, 3),
            "passaggi_calcolo": self.passaggi_calcolo,
        }
