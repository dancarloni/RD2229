"""
Pipeline Module Registry — Interfacce e registry centralizzato per moduli di calcolo.

Ogni modulo implementa questa interfaccia per funzionare autonomamente
e integrarsi con pipeline, dashboard e reporting.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Optional


@dataclass
class ModuleInfo:
    """Metadati del modulo per discovery e UI."""

    id: str  # "verifiche_ca", "sismica", "vento", ...
    name: str  # "Verifiche c.a.", "Sismica NTC2018", ...
    version: str  # "1.0.0"
    category: str  # "strutturale", "azioni", "geotecnica", "supporto"
    icon: str  # "🏗️", "🌊", "🌬️", ...
    description: str  # Descrizione breve
    norms_supported: list[str]  # ["RD2229", "NTC2018", "DM96", ...]
    standalone: bool = True  # Può funzionare da solo?
    requires_libs: list[str] = field(default_factory=list)  # ["Qt", "numpy"]


@dataclass
class KnowledgeLevel:
    """Livello di conoscenza per strutture esistenti (NTC2018 §C8.5.4)."""

    level: str  # "LC1", "LC2", "LC3"
    fc: float  # Fattore di confidenza (1.35, 1.20, 1.00)
    description: str  # "Conoscenza limitata", "adeguata", "accurata"
    material_reduction: str  # Come ridurre le resistenze: f_m / FC


@dataclass
class LoadCondition:
    """Singola condizione di carico con nome e stato limite."""

    name: str  # "PP", "Perm", "Acc_Q1", "SismaX", ...
    limit_state: str  # "SLU", "SLE_rara", "SLE_freq", "SLE_qp", "SLV", "SLD"
    N: float = 0.0  # kN (forza assiale)
    Mx: float = 0.0  # kN·m (momento intorno x)
    My: float = 0.0  # kN·m (momento intorno y)
    Tx: float = 0.0  # kN (taglio x)
    Ty: float = 0.0  # kN (taglio y)
    Mt: float = 0.0  # kN·m (momento torcente)
    is_seismic: bool = False  # Condizione sismica?
    combination_coeffs: Optional[dict] = None  # {"psi0": 0.7, "psi1": 0.5, "psi2": 0.3}


@dataclass
class CheckResult:
    """Singola verifica all'interno di un modulo."""

    name: str  # "Flessione retta", "Taglio", ...
    limit_state: str  # "SLU", "SLE_rara", "SLE_freq", "SLE_qp", "SLV"
    load_condition_name: str  # Nome della condizione di carico più gravosa
    ok: bool  # Verifica OK?
    computed_value: float  # Valore calcolato (es. sigma_c)
    limit_value: float  # Valore limite (es. f_cd)
    utilization: float  # Rapporto di utilizzo (0.0-1.0+)
    unit: str  # "kg/cm²", "kN", ...
    formula: str  # "sigma_c = N/A + M*y/I"
    substitution: str  # "sigma_c = 5000/750 + 200000*25/156250"
    norm_ref: str  # "NTC2018 §4.1.2.1.2"


@dataclass
class ModuleResult:
    """Risultato standard di un modulo di calcolo."""

    ok: bool  # Verifica globale OK?
    element_id: str  # ID elemento elaborato
    knowledge_level: Optional[KnowledgeLevel] = None  # LC/FC per strutture esistenti
    load_conditions: list[LoadCondition] = field(default_factory=list)  # Tutte le condizioni usate
    metrics: dict[str, float] = field(default_factory=dict)  # Valori numerici risultati
    checks_slu: list[CheckResult] = field(default_factory=list)  # Verifiche SLU (inviluppo)
    checks_sle: list[CheckResult] = field(default_factory=list)  # Verifiche SLE (inviluppo)
    checks_slv: list[CheckResult] = field(
        default_factory=list
    )  # Verifiche SLV sismiche (inviluppo)
    envelope_utilization: float = 0.0  # Massimo utilizzo tra tutti i checks
    envelope_check_name: str = ""  # Nome della verifica più gravosa
    calculation_steps: list[str] = field(default_factory=list)  # Passaggi intermedi
    norm_references: list[str] = field(default_factory=list)  # Riferimenti normativi
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Serializza risultato per salvataggio e reporting."""
        return {
            "ok": self.ok,
            "element_id": self.element_id,
            "envelope_utilization": self.envelope_utilization,
            "envelope_check_name": self.envelope_check_name,
            "metrics": self.metrics,
            "num_checks_slu": len(self.checks_slu),
            "num_checks_sle": len(self.checks_sle),
            "num_errors": len(self.errors),
        }


class ModuleEngine(ABC):
    """Interfaccia di calcolo (backend) per ogni modulo."""

    @abstractmethod
    def validate_input(self, input_data: dict) -> list[str]:
        """Valida input, ritorna lista errori (vuota = ok)."""
        ...

    @abstractmethod
    def run(self, input_data: dict, norm_code: str) -> ModuleResult:
        """Esegue il calcolo. Ritorna risultato con passaggi."""
        ...

    @abstractmethod
    def run_batch(self, elements: list[dict], norm_code: str) -> list[ModuleResult]:
        """Esegue il calcolo su N elementi."""
        ...


class ModuleRegistry:
    """Registry centralizzato dei moduli di calcolo disponibili."""

    _instance: Optional["ModuleRegistry"] = None
    _modules: dict[str, tuple[ModuleInfo, Callable, Callable]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def register(
        cls,
        module_info: ModuleInfo,
        engine_factory: Callable[[], ModuleEngine],
        window_factory: Optional[Callable[[], Any]] = None,
    ) -> None:
        """
        Registra un modulo nel registry.

        Args:
            module_info: Metadati modulo
            engine_factory: Callable che ritorna istanza ModuleEngine
            window_factory: Callable che ritorna finestra GUI (opzionale)
        """
        instance = cls()
        instance._modules[module_info.id] = (module_info, engine_factory, window_factory)

    @classmethod
    def get(cls, module_id: str) -> Optional[tuple[ModuleInfo, Callable, Optional[Callable]]]:
        """Recupera modulo dal registry."""
        instance = cls()
        return instance._modules.get(module_id)

    @classmethod
    def list_all(cls) -> list[ModuleInfo]:
        """Elenca tutti i moduli registrati."""
        instance = cls()
        return [info for info, _, _ in instance._modules.values()]

    @classmethod
    def list_by_category(cls, category: str) -> list[ModuleInfo]:
        """Elenca moduli per categoria."""
        instance = cls()
        return [info for info, _, _ in instance._modules.values() if info.category == category]

    @classmethod
    def list_by_norm(cls, norm_code: str) -> list[ModuleInfo]:
        """Elenca moduli che supportano una norma."""
        instance = cls()
        return [
            info for info, _, _ in instance._modules.values() if norm_code in info.norms_supported
        ]
