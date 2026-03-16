from __future__ import annotations

from typing import Protocol

from ..models import PareteMuraria, Rinforzo
from ..x5_core import (
    BetoncinoArmatoPlugin,
    CerchiaturaPlugin,
    IntonacoArmatoPlugin,
    ReinforcementRegistry,
    SimpleFRPPlugin,
)


class ReinforcementPluginProtocol(Protocol):
    def rigidezza_aggiunta(self, parete: PareteMuraria, rinforzo: Rinforzo) -> float: ...


__all__ = [
    "ReinforcementPluginProtocol",
    "SimpleFRPPlugin",
    "IntonacoArmatoPlugin",
    "BetoncinoArmatoPlugin",
    "CerchiaturaPlugin",
    "ReinforcementRegistry",
]
