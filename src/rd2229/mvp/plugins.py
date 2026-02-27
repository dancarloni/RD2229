from __future__ import annotations

from src.rd2229 import plugin_registry


def build_default_module_specs() -> list[plugin_registry.ModuleSpec]:
    return [
        plugin_registry.ModuleSpec(
            id="core_structural_checks",
            name="Core Structural Checks",
            version="0.1.0",
            entrypoints={"engine": "rd2229.mvp.engine.PlaceholderVerificationEngine"},
            capabilities={
                "checks": ["MVP_PLACEHOLDER", "MVP_REAL_MIN"],
                "norms": ["TODO(NTC/EC/RD)"],
            },
            data_contracts={
                "result_trace": [
                    "run_id",
                    "norm_references",
                    "method_id",
                    "assumptions",
                    "warnings",
                ]
            },
        ),
        plugin_registry.ModuleSpec(
            id="fire_module",
            name="Fire Module Scaffold",
            version="0.1.0",
            entrypoints={},
            capabilities={"checks": [], "norms": ["TODO:FIRE"]},
            data_contracts={"status": "scaffold"},
        ),
    ]


def register_default_module_specs() -> list[plugin_registry.ModuleSpec]:
    specs = build_default_module_specs()
    for spec in specs:
        plugin_registry.register_spec(spec)
    return specs
