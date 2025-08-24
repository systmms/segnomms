"""
Graceful Degradation System for SegnoMMS.

This module provides automatic detection and resolution of incompatible
feature combinations, ensuring QR codes remain scannable while maximizing
visual features.

The degradation system:
- Detects incompatible feature combinations
- Provides clear warnings about what was changed
- Automatically applies safe fallbacks
- Tracks all modifications for transparency

Example:
    from segnomms.degradation import DegradationManager

    manager = DegradationManager()
    safe_config, warnings = manager.apply_degradation(config)

    for warning in warnings:
        print(f"⚠️  {warning.message}")
"""

from .manager import DegradationManager
from .models import DegradationResult, DegradationWarning, WarningLevel
from .rules import DEGRADATION_RULES, DegradationRule, IncompatibilityType

__all__ = [
    "DegradationManager",
    "DegradationRule",
    "IncompatibilityType",
    "DegradationWarning",
    "DegradationResult",
    "WarningLevel",
    "DEGRADATION_RULES",
]
