"""Base contracts for RD2229 plugins with lifecycle hooks."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BasePlugin(ABC):
    """Lifecycle-oriented plugin contract."""

    plugin_id: str = ""
    name: str = ""
    description: str = ""

    def init(self, context: dict[str, Any] | None = None) -> None:
        return None

    @abstractmethod
    def execute(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    def teardown(self) -> None:
        return None

    @abstractmethod
    def to_spec(self) -> Any:
        raise NotImplementedError
