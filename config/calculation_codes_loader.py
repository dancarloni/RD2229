"""Loader for calculation code configuration files (.jsoncode).

This module loads and validates calculation code parameters from .jsoncode files
for TA (Tensioni Ammissibili), SLU (Stato Limite Ultimo), and SLE (Stato Limite Esercizio).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class CalculationCodeLoader:
    """Loader for calculation code configuration files."""

    def __init__(self, config_dir: Path | None = None):
        """Initialize the loader.

        Args:
            config_dir: Directory containing .jsoncode files.
                       Defaults to config/calculation_codes/ in project root.

        """
        if config_dir is None:
            # Try to find config directory relative to this file
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent
            config_dir = project_root / "config" / "calculation_codes"

        self.config_dir = Path(config_dir)
        self._cache: dict[str, dict[str, Any]] = {}

        if not self.config_dir.exists():
            logger.warning(f"Config directory not found: {self.config_dir}")

    def load_code(self, code_name: str) -> dict[str, Any]:
        """Load configuration for a specific calculation code.

        Args:
            code_name: Name of the code (e.g., 'TA', 'SLU', 'SLE')

        Returns:
            Dictionary with code configuration

        Raises:
            FileNotFoundError: If the .jsoncode file is not found
            json.JSONDecodeError: If the file contains invalid JSON

        """
        code_name = code_name.upper()

        # Return cached version if available
        if code_name in self._cache:
            return self._cache[code_name]

        # Load from file
        file_path = self.config_dir / f"{code_name}.jsoncode"

        if not file_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found for code '{code_name}': {file_path}"
            )

        try:
            with open(file_path, encoding="utf-8") as f:
                config = json.load(f)

            # Validate basic structure
            if "code_name" not in config:
                logger.warning(f"Missing 'code_name' in {file_path}")

            # Cache the configuration
            self._cache[code_name] = config

            logger.info(f"Loaded configuration for {code_name} from {file_path}")
            return config

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {file_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            raise

    def get_safety_coefficients(self, code_name: str) -> dict[str, Any]:
        """Get safety coefficients for a specific code.

        Args:
            code_name: Name of the code (e.g., 'TA', 'SLU', 'SLE')

        Returns:
            Dictionary with safety coefficients

        """
        config = self.load_code(code_name)
        return config.get("safety_coefficients", {})

    def get_stress_limits(self, code_name: str) -> dict[str, Any]:
        """Get stress limits for a specific code.

        Args:
            code_name: Name of the code

        Returns:
            Dictionary with stress limits

        """
        config = self.load_code(code_name)
        return config.get("stress_limits", {})

    def get_strain_limits(self, code_name: str) -> dict[str, Any]:
        """Get strain limits for a specific code.

        Args:
            code_name: Name of the code

        Returns:
            Dictionary with strain limits

        """
        config = self.load_code(code_name)
        return config.get("strain_limits", {})

    def get_homogenization_coefficient(self, code_name: str) -> float | None:
        """Get default homogenization coefficient for a specific code.

        Args:
            code_name: Name of the code

        Returns:
            Default homogenization coefficient (n = Es/Ec), or None if not defined

        """
        config = self.load_code(code_name)
        homog = config.get("homogenization", {})
        return homog.get("n_default")

    def get_verification_types(self, code_name: str) -> dict[str, Any]:
        """Get available verification types for a specific code.

        Args:
            code_name: Name of the code

        Returns:
            Dictionary with verification types

        """
        config = self.load_code(code_name)
        return config.get("verification_types", {})

    def get_material_sources(self, code_name: str) -> dict[str, Any]:
        """Get material sources for a specific code.

        Args:
            code_name: Name of the code

        Returns:
            Dictionary with material sources (e.g., RD2229, DM92, NTC2008, NTC2018)

        """
        config = self.load_code(code_name)
        return config.get("material_sources", {})

    def list_available_codes(self) -> list[str]:
        """List all available calculation codes.

        Returns:
            List of code names

        """
        if not self.config_dir.exists():
            return []

        codes = []
        for file_path in self.config_dir.glob("*.jsoncode"):
            code_name = file_path.stem
            codes.append(code_name)

        return sorted(codes)

    def clear_cache(self):
        """Clear the configuration cache."""
        self._cache.clear()


# Global instance for convenience
_default_loader: CalculationCodeLoader | None = None


def get_default_loader() -> CalculationCodeLoader:
    """Get the default global loader instance."""
    global _default_loader
    if _default_loader is None:
        _default_loader = CalculationCodeLoader()
    return _default_loader


# Convenience functions using the default loader
def load_code(code_name: str) -> dict[str, Any]:
    """Load configuration for a specific calculation code using the default loader."""
    return get_default_loader().load_code(code_name)


def get_safety_coefficients(code_name: str) -> dict[str, Any]:
    """Get safety coefficients for a specific code using the default loader."""
    return get_default_loader().get_safety_coefficients(code_name)


def get_stress_limits(code_name: str) -> dict[str, Any]:
    """Get stress limits for a specific code using the default loader."""
    return get_default_loader().get_stress_limits(code_name)


def get_strain_limits(code_name: str) -> dict[str, Any]:
    """Get strain limits for a specific code using the default loader."""
    return get_default_loader().get_strain_limits(code_name)


def list_available_codes() -> list[str]:
    """List all available calculation codes using the default loader."""
    return get_default_loader().list_available_codes()
