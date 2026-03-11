"""Pipeline per la composizione delle sezioni del report professionale."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

SectionGenerator = Callable[[Any, Any], str | None]


@runtime_checkable
class FornitoreSezione(Protocol):
    """Protocollo per provider OO di sezioni report."""

    def genera_sezione(self, project: Any, results: Any) -> str | None:
        """Restituisce il contenuto della sezione."""


@dataclass(slots=True)
class SectionContribution:
    """Singola registrazione di una sezione report."""

    key: str
    order: int
    generator: SectionGenerator


_REGISTRY: dict[str, SectionContribution] = {}


def register_section_generator(
    generator: SectionGenerator,
    *,
    key: str | None = None,
    order: int = 100,
) -> SectionGenerator:
    """Registra una funzione che contribuisce al report.

    Se ``key`` e' gia' presente, la registrazione viene sovrascritta.
    """
    resolved_key = key or generator.__name__
    _REGISTRY[resolved_key] = SectionContribution(
        key=resolved_key,
        order=order,
        generator=generator,
    )
    return generator


def register_section_provider(
    provider: FornitoreSezione,
    *,
    key: str,
    order: int = 100,
) -> None:
    """Registra un provider OO che implementa ``FornitoreSezione``."""

    def _wrapped(project: Any, results: Any) -> str | None:
        return provider.genera_sezione(project, results)

    register_section_generator(_wrapped, key=key, order=order)


def clear_report_registry() -> None:
    """Pulisce il registry globale; utile nei test."""
    _REGISTRY.clear()


def get_report_registry() -> list[SectionContribution]:
    """Restituisce le sezioni registrate ordinate per priorita'."""
    return sorted(_REGISTRY.values(), key=lambda item: (item.order, item.key))


class PipelineReport:
    """Builder che compone il report iterando sulle sezioni registrate."""

    def __init__(self, sections: list[SectionContribution] | None = None) -> None:
        self._sections: dict[str, SectionContribution] = {}
        for item in sections or []:
            self._sections[item.key] = item

    @classmethod
    def from_registry(cls) -> PipelineReport:
        """Costruisce una pipeline usando il registry globale."""
        return cls(get_report_registry())

    def register(
        self,
        generator: SectionGenerator,
        *,
        key: str | None = None,
        order: int = 100,
    ) -> None:
        """Registra una sezione direttamente nell'istanza."""
        resolved_key = key or generator.__name__
        self._sections[resolved_key] = SectionContribution(
            key=resolved_key,
            order=order,
            generator=generator,
        )

    def build_sections(self, project: Any, results: Any) -> list[tuple[str, str]]:
        """Costruisce sezioni non vuote come lista ``(key, contenuto)``."""
        rendered: list[tuple[str, str]] = []
        for item in sorted(self._sections.values(), key=lambda row: (row.order, row.key)):
            content = item.generator(project, results)
            if content is None:
                continue
            normalized = content.strip()
            if not normalized:
                continue
            rendered.append((item.key, normalized))
        return rendered

    def build(self, project: Any, results: Any, *, joiner: str = "\n\n") -> str:
        """Restituisce l'intero report come concatenazione delle sezioni."""
        return joiner.join(content for _, content in self.build_sections(project, results))
