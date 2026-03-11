"""Decoratori per registrare sezioni nel report professionale."""

from __future__ import annotations

from .pipeline import SectionGenerator, register_section_generator


def contribuisce_report(*, key: str | None = None, order: int = 100):
    """Registra una funzione nel registry sezioni del report.

    Esempio:
        @contribuisce_report(key="materiali", order=20)
        def sezione_materiali(project, results) -> str:
            return "..."
    """

    def _decorator(func: SectionGenerator) -> SectionGenerator:
        register_section_generator(func, key=key, order=order)
        return func

    return _decorator
