from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import importlib
import pkgutil
import json
import logging
from typing import Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ModuleSpec:
    key: str
    name: str
    description: str
    icon: Optional[str] = None
    enabled: bool = True


class ModuleRegistry:
    """Discover modules under the `sections_app.modules` package.

    Behavior:
    - Scans package modules using pkgutil.iter_modules
    - Loads MODULE_SPEC and create_module factory from each module
    - Reads optional `modules_config.json` next to the package for ordering/enabling
    """

    def __init__(self, package: str = "sections_app.modules") -> None:
        self.package = package
        self._specs: Dict[str, ModuleSpec] = {}
        self._factories: Dict[str, Callable] = {}
        try:
            pkg = importlib.import_module(self.package)
            self._config_path = Path(pkg.__file__).parent / "modules_config.json"
        except Exception:  # pragma: no cover - defensive
            self._config_path = Path("modules_config.json")
        self._config = self._load_config()
        self.discover()

    def _load_config(self) -> dict:
        if self._config_path.exists():
            try:
                with open(self._config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                if isinstance(cfg, dict):
                    return cfg
            except Exception as e:  # pragma: no cover - defensive
                logger.warning("Errore caricamento modules_config.json: %s", e)
        return {}

    def discover(self) -> None:
        try:
            pkg = importlib.import_module(self.package)
        except Exception as e:  # pragma: no cover - defensive
            logger.exception("Impossible import package %s: %s", self.package, e)
            return

        for finder, modname, ispkg in pkgutil.iter_modules(pkg.__path__):
            full = f"{self.package}.{modname}"
            try:
                mod = importlib.import_module(full)
                spec = getattr(mod, "MODULE_SPEC", None)
                factory = getattr(mod, "create_module", None)
                if isinstance(spec, dict) and callable(factory):
                    key = spec.get("key", modname)
                    conf = self._config.get("modules", {}).get(key, {})
                    enabled = conf.get("enabled", True) if isinstance(conf, dict) else True
                    self._specs[key] = ModuleSpec(
                        key=key,
                        name=spec.get("name", key),
                        description=spec.get("description", ""),
                        icon=spec.get("icon"),
                        enabled=bool(enabled),
                    )
                    self._factories[key] = factory
                else:
                    logger.debug("Modulo %s ignorato: manca MODULE_SPEC o create_module", full)
            except Exception:
                logger.exception("Errore import modulo %s", full)

    def get_specs(self) -> List[ModuleSpec]:
        order = self._config.get("order", [])
        specs = [s for s in self._specs.values() if s.enabled]
        if order:
            ordered: List[ModuleSpec] = []
            keys_in_order = [k for k in order if k in self._specs and self._specs[k].enabled]
            for k in keys_in_order:
                ordered.append(self._specs[k])
            for s in specs:
                if s.key not in keys_in_order:
                    ordered.append(s)
            return ordered
        return sorted(specs, key=lambda s: s.name.lower())

    def get_factory(self, key: str) -> Optional[Callable]:
        return self._factories.get(key)
