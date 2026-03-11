"""Test pipeline report professionale (Fase Q.2)."""

from __future__ import annotations

import pytest

from src.report.decorators import contribuisce_report
from src.report.pipeline import (
    PipelineReport,
    clear_report_registry,
    get_report_registry,
    register_section_generator,
    register_section_provider,
)


@pytest.fixture(autouse=True)
def _clean_registry():
    clear_report_registry()
    yield
    clear_report_registry()


def test_pipeline_orders_sections_by_priority():
    def intro(project, results):
        return "Introduzione"

    def materiali(project, results):
        return "Materiali"

    def verifiche(project, results):
        return "Verifiche"

    register_section_generator(verifiche, key="verifiche", order=30)
    register_section_generator(intro, key="intro", order=10)
    register_section_generator(materiali, key="materiali", order=20)

    pipeline = PipelineReport.from_registry()
    sections = pipeline.build_sections(project={}, results={})

    assert [key for key, _ in sections] == ["intro", "materiali", "verifiche"]


def test_pipeline_skips_empty_sections():
    def section_valid(project, results):
        return "Sezione valida"

    def section_empty(project, results):
        return "   "

    def section_none(project, results):
        return None

    register_section_generator(section_valid, key="ok", order=1)
    register_section_generator(section_empty, key="vuota", order=2)
    register_section_generator(section_none, key="none", order=3)

    pipeline = PipelineReport.from_registry()
    sections = pipeline.build_sections(project={}, results={})

    assert sections == [("ok", "Sezione valida")]


def test_decorator_registers_section_generator():
    @contribuisce_report(key="capitolo_1", order=5)
    def capitolo_1(project, results):
        return "Capitolo 1"

    assert len(get_report_registry()) == 1
    pipeline = PipelineReport.from_registry()
    report = pipeline.build(project={}, results={})

    assert report == "Capitolo 1"


def test_registry_overwrites_duplicated_keys():
    def old_section(project, results):
        return "Versione vecchia"

    def new_section(project, results):
        return "Versione nuova"

    register_section_generator(old_section, key="summary", order=1)
    register_section_generator(new_section, key="summary", order=1)

    pipeline = PipelineReport.from_registry()
    sections = pipeline.build_sections(project={}, results={})

    assert sections == [("summary", "Versione nuova")]


def test_register_section_provider_supports_object_style():
    class ProviderIntro:
        def genera_sezione(self, project, results):
            return "Sezione da provider"

    register_section_provider(ProviderIntro(), key="provider_intro", order=12)

    pipeline = PipelineReport.from_registry()
    sections = pipeline.build_sections(project={}, results={})

    assert sections == [("provider_intro", "Sezione da provider")]
