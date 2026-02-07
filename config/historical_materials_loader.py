"""Loader for historical materials configuration files (.jsoncode).

This module loads and validates historical material properties from .jsoncode files
for RD2229/39, DM92, NTC2008, and NTC2018.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class HistoricalMaterialsLoader:
    """Loader for historical materials configuration files."""

    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize the loader.

        Args:
            config_dir: Directory containing .jsoncode files for historical materials.
                       Defaults to config/historical_materials/ in project root.

        """
        if config_dir is None:
            # Try to find config directory relative to this file
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent
            config_dir = project_root / "config" / "historical_materials"

        self.config_dir = Path(config_dir)
        self._cache: Dict[str, Dict[str, Any]] = {}

        if not self.config_dir.exists():
            logger.warning(f"Config directory not found: {self.config_dir}")

    def load_material_source(self, source_name: str) -> Dict[str, Any]:
        """Load configuration for a specific material source.

        Args:
            source_name: Name of the source (e.g., 'RD2229', 'DM92', 'NTC2008', 'NTC2018')

        Returns:
            Dictionary with material source configuration

        Raises:
            FileNotFoundError: If the .jsoncode file is not found
            json.JSONDecodeError: If the file contains invalid JSON

        """
        source_name = source_name.upper()

        # Return cached version if available
        if source_name in self._cache:
            return self._cache[source_name]

        # Load from file
        file_path = self.config_dir / f"{source_name}.jsoncode"

        if not file_path.exists():
            raise FileNotFoundError(f"Material source configuration not found for '{source_name}': {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            # Validate basic structure
            if "code_name" not in config:
                logger.warning(f"Missing 'code_name' in {file_path}")

            # Cache the configuration
            self._cache[source_name] = config

            logger.info(f"Loaded material source configuration for {source_name} from {file_path}")
            return config

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {file_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            raise

    def get_concrete_classes(self, source_name: str) -> Dict[str, Dict[str, Any]]:
        """Get concrete classes for a specific material source.

        Args:
            source_name: Name of the source

        Returns:
            Dictionary with concrete classes (e.g., R120, R160, C20/25, etc.)

        """
        config = self.load_material_source(source_name)
        return config.get("concrete_classes", {})

    def get_concrete_properties(self, source_name: str, concrete_class: str) -> Optional[Dict[str, Any]]:
        """Get properties for a specific concrete class.

        Args:
            source_name: Name of the source (e.g., 'RD2229', 'NTC2008')
            concrete_class: Class name (e.g., 'R160', 'C25_30')

        Returns:
            Dictionary with concrete properties, or None if not found

        """
        classes = self.get_concrete_classes(source_name)
        return classes.get(concrete_class)

    def get_steel_types(self, source_name: str) -> Dict[str, Dict[str, Any]]:
        """Get steel types for a specific material source.

        Args:
            source_name: Name of the source

        Returns:
            Dictionary with steel types (e.g., dolce, FeB38k, B450C, etc.)

        """
        config = self.load_material_source(source_name)
        return config.get("steel_types", {})

    def get_steel_properties(self, source_name: str, steel_type: str) -> Optional[Dict[str, Any]]:
        """Get properties for a specific steel type.

        Args:
            source_name: Name of the source
            steel_type: Steel type name (e.g., 'dolce', 'FeB38k', 'B450C')

        Returns:
            Dictionary with steel properties, or None if not found

        """
        types = self.get_steel_types(source_name)
        return types.get(steel_type)

    def get_cement_types(self, source_name: str) -> Dict[str, Dict[str, Any]]:
        """Get cement types for a specific material source.

        Args:
            source_name: Name of the source

        Returns:
            Dictionary with cement types (e.g., normale, alluminoso, presa_lenta)

        """
        config = self.load_material_source(source_name)
        return config.get("cement_types", {})

    def get_calculation_formulas(self, source_name: str) -> Dict[str, Any]:
        """Get calculation formulas for a specific material source.

        Args:
            source_name: Name of the source

        Returns:
            Dictionary with calculation formulas

        """
        config = self.load_material_source(source_name)
        return config.get("calculation_formulas", {})

    def get_conversion_factors(self, source_name: str) -> Dict[str, float]:
        """Get unit conversion factors for a specific material source.

        Args:
            source_name: Name of the source

        Returns:
            Dictionary with conversion factors

        """
        config = self.load_material_source(source_name)
        return config.get("conversion_factors", {})

    def list_available_sources(self) -> list[str]:
        """List all available material sources.

        Returns:
            List of source names

        """
        if not self.config_dir.exists():
            return []

        sources = []
        for file_path in self.config_dir.glob("*.jsoncode"):
            source_name = file_path.stem
            sources.append(source_name)

        return sorted(sources)

    def clear_cache(self):
        """Clear the configuration cache."""
        self._cache.clear()


# Global instance for convenience
_default_loader: Optional[HistoricalMaterialsLoader] = None


def get_default_loader() -> HistoricalMaterialsLoader:
    """Get the default global loader instance."""
    global _default_loader
    if _default_loader is None:
        _default_loader = HistoricalMaterialsLoader()
    return _default_loader


# Convenience functions using the default loader
def load_material_source(source_name: str) -> Dict[str, Any]:
    """Load material source configuration using the default loader."""
    return get_default_loader().load_material_source(source_name)


def get_concrete_classes(source_name: str) -> Dict[str, Dict[str, Any]]:
    """Get concrete classes for a source using the default loader."""
    return get_default_loader().get_concrete_classes(source_name)


def get_concrete_properties(source_name: str, concrete_class: str) -> Optional[Dict[str, Any]]:
    """Get concrete properties using the default loader."""
    return get_default_loader().get_concrete_properties(source_name, concrete_class)


def get_steel_types(source_name: str) -> Dict[str, Dict[str, Any]]:
    """Get steel types for a source using the default loader."""
    return get_default_loader().get_steel_types(source_name)


def get_steel_properties(source_name: str, steel_type: str) -> Optional[Dict[str, Any]]:
    """Get steel properties using the default loader."""
    return get_default_loader().get_steel_properties(source_name, steel_type)


def list_available_sources() -> list[str]:
    """List all available material sources using the default loader."""
    return get_default_loader().list_available_sources()
