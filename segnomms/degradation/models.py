"""
Data models for the graceful degradation system.
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class WarningLevel(str, Enum):
    """Severity levels for degradation warnings."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class DegradationWarning(BaseModel):
    """A warning generated during graceful degradation."""

    model_config = ConfigDict(validate_default=True, extra="forbid")

    level: WarningLevel = Field(description="Severity level of the warning")
    feature: str = Field(description="Feature that was affected")
    message: str = Field(description="Human-readable warning message")
    original_value: Any = Field(description="Original configuration value")
    degraded_value: Any = Field(description="Degraded/safe value applied")
    reason: str = Field(description="Reason for the degradation")
    suggestion: Optional[str] = Field(default=None, description="Suggestion for user")

    def __str__(self) -> str:
        """String representation for easy printing."""
        prefix = {
            WarningLevel.INFO: "ℹ️ ",
            WarningLevel.WARNING: "⚠️ ",
            WarningLevel.CRITICAL: "🚨",
        }.get(self.level, "")

        return f"{prefix} {self.message}"


class DegradationResult(BaseModel):
    """Result of applying graceful degradation to a configuration."""

    model_config = ConfigDict(validate_default=True, extra="forbid")

    warnings: List[DegradationWarning] = Field(
        default_factory=list,
        description="List of warnings generated during degradation",
    )
    changes_made: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict, description="Map of configuration paths to their changes"
    )
    degradation_applied: bool = Field(default=False, description="Whether any degradation was applied")

    @property
    def warning_count(self) -> int:
        """Total number of warnings."""
        return len(self.warnings)

    @property
    def critical_count(self) -> int:
        """Number of critical warnings."""
        return sum(1 for w in self.warnings if w.level == WarningLevel.CRITICAL)

    @property
    def has_critical(self) -> bool:
        """Whether there are any critical warnings."""
        return self.critical_count > 0

    def get_warnings_by_level(self, level: WarningLevel) -> List[DegradationWarning]:
        """Get warnings filtered by level."""
        return [w for w in self.warnings if w.level == level]

    def get_warnings_by_feature(self, feature: str) -> List[DegradationWarning]:
        """Get warnings filtered by feature."""
        return [w for w in self.warnings if w.feature == feature]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for easy serialization."""
        return {
            "degradation_applied": self.degradation_applied,
            "warning_count": self.warning_count,
            "critical_count": self.critical_count,
            "warnings": [w.model_dump() for w in self.warnings],
            "changes_made": self.changes_made,
        }
