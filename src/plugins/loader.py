"""Plugin discovery: folder scanning and importlib.metadata entry_points."""

from __future__ import annotations

import importlib
import json
import logging
import sys
from pathlib import Path
from typing import Any

from src.plugins import PluginRegistry, PluginSpec

logger = logging.getLogger(__name__)


def load_plugins_from_folder(plugins_dir: Path) -> list[PluginSpec]:
    """Scan *plugins_dir* for sub-packages that expose a ``register`` function.

    Each sub-package may contain a ``manifest.json`` that provides metadata.
    The ``register(registry)`` callable receives a :class:`PluginRegistry`
    and is expected to call ``registry.register(spec)``.
    """
    specs: list[PluginSpec] = []
    if not plugins_dir.is_dir():
        logger.debug("plugins_dir %s does not exist; skipping", plugins_dir)
        return specs

    for entry in sorted(plugins_dir.iterdir()):
        if not entry.is_dir():
            continue
        init_file = entry / "__init__.py"
        if not init_file.exists():
            continue
        try:
            spec = _load_plugin_package(entry)
            if spec:
                specs.append(spec)
        except (ImportError, AttributeError, json.JSONDecodeError, TypeError, ValueError) as exc:  # plugin errors must not crash the app
            logger.warning("Failed to load plugin from %s: %s", entry, exc)

    return specs


def _load_plugin_package(package_dir: Path) -> PluginSpec | None:
    """Load a single plugin package directory and return its PluginSpec.

    Plugins are imported as real packages (parent dir added temporarily to
    ``sys.path``) so that relative imports inside the plugin work correctly.
    """
    # Read manifest.json if present
    manifest: dict[str, Any] = {}
    manifest_file = package_dir / "manifest.json"
    if manifest_file.exists():
        with manifest_file.open(encoding="utf-8") as fh:
            manifest = json.load(fh)

    # Import the plugin as a real package by temporarily adding its parent to sys.path
    plugins_root = str(package_dir.parent)
    added_to_path = plugins_root not in sys.path
    if added_to_path:
        sys.path.insert(0, plugins_root)
    try:
        package_name = package_dir.name
        if package_name in sys.modules:
            module = importlib.reload(sys.modules[package_name])
        else:
            module = importlib.import_module(package_name)
    finally:
        if added_to_path and plugins_root in sys.path:
            sys.path.remove(plugins_root)

    register_fn = getattr(module, "register", None)
    if register_fn is None:
        logger.debug("Plugin %s has no register(); skipping", package_dir.name)
        return None

    # Build a temporary registry and call register()
    tmp_registry = PluginRegistry()
    register_fn(tmp_registry)
    loaded = tmp_registry.list_plugins()
    if not loaded:
        # Build a minimal spec from manifest
        plugin_id = manifest.get("id", package_dir.name)
        return PluginSpec(
            id=plugin_id,
            title=manifest.get("title", plugin_id),
            version=manifest.get("version", "0.1.0"),
            category=manifest.get("category", "general"),
            icon=manifest.get("icon", ""),
        )
    return loaded[0]


def load_plugins_from_entry_points() -> list[PluginSpec]:
    """Load plugins registered via ``importlib.metadata`` entry points.

    Plugins should be registered under the ``rd2229.plugins`` group, where
    each entry point value is a callable ``register(registry: PluginRegistry)``.
    """
    specs: list[PluginSpec] = []
    try:
        from importlib.metadata import entry_points

        eps = entry_points(group="rd2229.plugins")
    except Exception as exc:  # ImportError or stdlib unavailability
        logger.debug("entry_points lookup failed: %s", exc)
        return specs

    for ep in eps:
        try:
            register_fn = ep.load()
            tmp_registry = PluginRegistry()
            register_fn(tmp_registry)
            specs.extend(tmp_registry.list_plugins())
        except (ImportError, AttributeError, TypeError, ValueError) as exc:  # plugin errors must not crash the app
            logger.warning("Failed to load entry_point plugin %s: %s", ep.name, exc)

    return specs


def load_all_plugins(config: dict[str, Any] | None = None) -> list[PluginSpec]:
    """Load all plugins according to *config*.

    Config keys (all optional):
      - ``discovery``: ``"folder"``, ``"entry_points"``, or ``"both"`` (default)
      - ``folder``: path to plugins folder (default: ``"plugins"``)
    """
    cfg = config or {}
    discovery = cfg.get("discovery", "both")
    folder_path = Path(cfg.get("folder", "plugins"))

    specs: list[PluginSpec] = []

    if discovery in ("folder", "both"):
        specs.extend(load_plugins_from_folder(folder_path))

    if discovery in ("entry_points", "both"):
        specs.extend(load_plugins_from_entry_points())

    return specs
