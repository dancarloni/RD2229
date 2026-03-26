"""
Models per gestione condizioni di carico.

Ogni condizione ha:
- Nome identificativo (PP, Perm, Acc_Q1, SismaX, etc.)
- Stato limite (SLU, SLE_rara, SLE_freq, SLE_qp, SLV, SLD)
- Componenti sollecitazione: N, Mx, My, Tx, Ty, Mt
- Flag sismico (per combinazioni)
- Coefficienti psi (applicabili per combinazioni)

Questo modello consente di definire N condizioni indipendenti,
ognuna associata a uno stato limite, e di calcolare inviluppi
per ogni stato limite separatamente.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class LimitState(str, Enum):
    """Stati limite principali (NTC2018)."""

    SLU = "SLU"  # Stato limite ultimo (portanza)
    SLE_rara = "SLE_rara"  # SLE rara (combinazione rara)
    SLE_freq = "SLE_freq"  # SLE frequente
    SLE_qp = "SLE_qp"  # SLE quasi-permanente
    SLV = "SLV"  # SLE sismico (verifica durabilità)
    SLD = "SLD"  # SLE dinamico (limite di danno)


@dataclass
class LoadCondition:
    """
    Singola condizione di carico con sollecitazioni e stato limite.

    Rappresenta un insieme di sollecitazioni (N, M, T, Mt) con:
    - Nome descrittivo (PP, Perm, Acc_Q1, SismaX)
    - Stato limite di riferimento (SLU, SLE_rara, etc.)
    - Indicazione se sismica (per calcoli speciali)
    - Coefficienti psi (ψ0, ψ1, ψ2) per combinazioni
    """

    name: str  # Nome condizione
    limit_state: LimitState  # Stato limite
    N: float = 0.0  # Forza assiale [kN]
    Mx: float = 0.0  # Momento intorno asse x [kN·m]
    My: float = 0.0  # Momento intorno asse y [kN·m]
    Tx: float = 0.0  # Taglio asse x [kN]
    Ty: float = 0.0  # Taglio asse y [kN]
    Mt: float = 0.0  # Momento torcente [kN·m]
    is_seismic: bool = False  # Condizione sismica?
    psi0: Optional[float] = None  # Coefficiente ψ0 (combinazioni)
    psi1: Optional[float] = None  # Coefficiente ψ1
    psi2: Optional[float] = None  # Coefficiente ψ2
    gamma: float = 1.0  # Coefficiente parziale di sicurezza

    def to_dict(self) -> dict:
        """Serializza per salvataggio."""
        return {
            "name": self.name,
            "limit_state": self.limit_state.value,
            "N": self.N,
            "Mx": self.Mx,
            "My": self.My,
            "Tx": self.Tx,
            "Ty": self.Ty,
            "Mt": self.Mt,
            "is_seismic": self.is_seismic,
            "psi0": self.psi0,
            "psi1": self.psi1,
            "psi2": self.psi2,
            "gamma": self.gamma,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LoadCondition":
        """Ricrea dall'oggetto serializzato."""
        return cls(
            name=data["name"],
            limit_state=LimitState(data["limit_state"]),
            N=data.get("N", 0.0),
            Mx=data.get("Mx", 0.0),
            My=data.get("My", 0.0),
            Tx=data.get("Tx", 0.0),
            Ty=data.get("Ty", 0.0),
            Mt=data.get("Mt", 0.0),
            is_seismic=data.get("is_seismic", False),
            psi0=data.get("psi0"),
            psi1=data.get("psi1"),
            psi2=data.get("psi2"),
            gamma=data.get("gamma", 1.0),
        )


@dataclass
class LoadConditionManager:
    """
    Gestore di N condizioni di carico × M stati limite.

    Permette di:
    - Definire multiple condizioni (una per ogni nome)
    - Associare ogni condizione a uno stato limite
    - Calcolare inviluppo (massimo/minimo) per ogni stato limite
    - Filtrare condizioni per stato limite
    """

    conditions: list[LoadCondition] = field(default_factory=list)

    def add_condition(self, condition: LoadCondition) -> None:
        """Aggiunge una condizione di carico."""
        self.conditions.append(condition)

    def remove_condition(self, name: str) -> None:
        """Rimuove condizione per nome."""
        self.conditions = [c for c in self.conditions if c.name != name]

    def get_by_limit_state(self, limit_state: LimitState) -> list[LoadCondition]:
        """Filtra condizioni per stato limite."""
        return [c for c in self.conditions if c.limit_state == limit_state]

    def get_by_name(self, name: str) -> Optional[LoadCondition]:
        """Trova condizione per nome."""
        for c in self.conditions:
            if c.name == name:
                return c
        return None

    def limit_states(self) -> set[LimitState]:
        """Elenca tutti gli stati limite presenti."""
        return set(c.limit_state for c in self.conditions)

    def count_by_state(self) -> dict[LimitState, int]:
        """Conta condizioni per stato limite."""
        result = {}
        for state in self.limit_states():
            result[state] = len(self.get_by_limit_state(state))
        return result

    def to_dict(self) -> list[dict]:
        """Serializza tutte le condizioni."""
        return [c.to_dict() for c in self.conditions]

    @classmethod
    def from_dict(cls, data: list[dict]) -> "LoadConditionManager":
        """Ricrea dal serializzato."""
        manager = cls()
        for item in data:
            manager.add_condition(LoadCondition.from_dict(item))
        return manager


# Re-export per comodità

__all__ = [
    "LimitState",
    "LoadCondition",
    "LoadConditionManager",
]
