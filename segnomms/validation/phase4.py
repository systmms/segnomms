"""Deprecated module - use segnomms.validation.composition instead.

This module exists only for backward compatibility. All functionality
has been moved to segnomms.validation.composition.

.. deprecated::
    Import from ``segnomms.validation.composition`` instead.
    This module will be removed in a future version.
"""

import warnings

warnings.warn(
    "The 'segnomms.validation.phase4' module is deprecated. "
    "Use 'segnomms.validation.composition' instead. "
    "This module will be removed in a future version.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything from the new module for backward compatibility
from segnomms.validation.composition import (  # noqa: F401, E402
    CompositionValidator,
    Phase4Validator,
)
from segnomms.validation.models import (  # noqa: F401, E402
    CompositionValidatorConfig,
    Phase4ValidatorConfig,
    ValidationResult,
)

__all__ = [
    "CompositionValidator",
    "Phase4Validator",
    "CompositionValidatorConfig",
    "Phase4ValidatorConfig",
    "ValidationResult",
]
