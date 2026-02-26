"""Feature registry per la GUI moderna RD2229.

Pattern:
    - :class:`FeatureSpec` – interfaccia base per una "scheda"
    - :func:`register` – registra una scheda nel registry
    - :func:`get_all` – restituisce la lista ordinata di schede

Aggiungere una nuova scheda::

    from src.ui.modern.features.registry import register, FeatureSpec

    class MyFeature(FeatureSpec):
        feature_id = "my_feature"
        label = "La Mia Scheda"
        icon = "📐"
        order = 50

        def create_widget(self, parent, project_vm, run_vm, results_vm):
            from src.ui.modern.features.my_feature.widget import MyWidget
            return MyWidget(parent, project_vm, run_vm, results_vm)

    register(MyFeature())
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass

_REGISTRY: list["FeatureSpec"] = []


@dataclass
class FeatureSpec:
    """Specifica di una feature/scheda registrabile nella sidebar.

    Ogni scheda deve definire :attr:`feature_id`, :attr:`label` e
    implementare :meth:`create_widget`.
    """

    feature_id: str = ""
    label: str = ""
    icon: str = "📋"
    order: int = 100
    enabled: bool = True
    tooltip: str = ""

    def create_widget(
        self,
        parent: Any,
        project_vm: Any,
        run_vm: Any,
        results_vm: Any,
    ) -> Any:
        """Crea e restituisce il widget Qt per questa feature.

        Implementato dalle sottoclassi.  Deve restituire un QWidget.

        Args:
            parent: Widget genitore Qt.
            project_vm: ProjectViewModel.
            run_vm: RunViewModel.
            results_vm: ResultsViewModel.

        Returns:
            QWidget o compatibile.
        """
        raise NotImplementedError(f"FeatureSpec '{self.feature_id}' non implementa create_widget")


def register(spec: FeatureSpec) -> None:
    """Registra una :class:`FeatureSpec` nel registry globale.

    Se una spec con lo stesso :attr:`feature_id` è già registrata,
    viene sostituita silenziosamente.

    Args:
        spec: Feature da registrare.
    """
    global _REGISTRY
    _REGISTRY = [s for s in _REGISTRY if s.feature_id != spec.feature_id]
    _REGISTRY.append(spec)
    _REGISTRY.sort(key=lambda s: s.order)


def get_all() -> list[FeatureSpec]:
    """Restituisce tutte le feature registrate, ordinate per :attr:`order`."""
    return list(_REGISTRY)


def clear() -> None:
    """Svuota il registry (utile nei test)."""
    global _REGISTRY
    _REGISTRY = []
