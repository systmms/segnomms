"""Validation module for SegnoMMS plugin.

This module provides validation components for QR code composition,
including frame shapes and centerpiece reserves.
"""

from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

from .composition import CompositionValidator
from .models import CompositionValidatorConfig, Phase4ValidatorConfig, ValidationResult

if TYPE_CHECKING:
    # For type checking, Phase4Validator is the same as CompositionValidator
    Phase4Validator = CompositionValidator

__all__ = [
    "CompositionValidator",
    "CompositionValidatorConfig",
    "Phase4Validator",  # Deprecated alias, kept for backward compatibility
    "Phase4ValidatorConfig",  # Deprecated alias, kept for backward compatibility
    "ValidationResult",
]


def __getattr__(name: str) -> object:
    """Handle deprecated attribute access.

    This function emits deprecation warnings when deprecated names are
    accessed from the package level.
    """
    if name == "Phase4Validator":
        warnings.warn(
            "Phase4Validator is deprecated, use CompositionValidator instead. "
            "Phase4Validator will be removed in a future version.",
            DeprecationWarning,
            stacklevel=2,
        )
        return CompositionValidator
    if name == "Phase4ValidatorConfig":
        warnings.warn(
            "Phase4ValidatorConfig is deprecated, use CompositionValidatorConfig instead. "
            "Phase4ValidatorConfig will be removed in a future version.",
            DeprecationWarning,
            stacklevel=2,
        )
        return CompositionValidatorConfig
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
