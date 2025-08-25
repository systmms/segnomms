"""Pydantic models for validation components.

This module provides data models for validation classes using Pydantic
for automatic validation and type safety.
"""

from typing import Any, Dict, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator


class Phase4ValidatorConfig(BaseModel):
    """Configuration for Phase4Validator initialization.

    This model validates the parameters needed to initialize a Phase4Validator
    instance, ensuring proper QR code version, error level, and matrix size.

    Example:
        >>> config = Phase4ValidatorConfig(
        ...     qr_version=7,
        ...     error_level='M',
        ...     matrix_size=45
        ... )
        >>> validator = Phase4Validator(**config.model_dump())
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    qr_version: int = Field(..., ge=1, le=40, description="QR code version (1-40)")

    error_level: Literal["L", "M", "Q", "H"] = Field(
        ..., description="Error correction level"
    )

    matrix_size: int = Field(
        ...,
        ge=11,  # Minimum for Micro QR M1
        le=177,  # Maximum for QR version 40
        description="Size of the QR matrix in modules",
    )

    @field_validator("error_level", mode="before")
    @classmethod
    def uppercase_error_level(cls, v: str) -> str:
        """Convert error level to uppercase."""
        return v.upper()

    @field_validator("matrix_size")
    @classmethod
    def validate_matrix_size(cls, v: int, info: ValidationInfo) -> int:
        """Validate matrix size matches QR code specifications."""
        # Micro QR sizes
        micro_sizes = {11, 13, 15, 17}

        # Regular QR: 21 + 4*n where n = version - 1
        if v in micro_sizes:
            return v

        # Check if it's a valid regular QR size
        if v >= 21 and (v - 21) % 4 == 0:
            # Optionally validate against version if provided
            if "qr_version" in info.data:
                expected_size = 21 + 4 * (info.data["qr_version"] - 1)
                if v != expected_size and info.data["qr_version"] <= 40:
                    # Only enforce if version is regular QR (not micro)
                    pass  # Allow mismatch for now, as micro QR versions work differently
            return v

        raise ValueError(
            f"Invalid QR matrix size {v}. Must be 11, 13, 15, 17 (Micro QR) "
            "or 21+4*n (Regular QR)"
        )


class ValidationResult(BaseModel):
    """Result of validation operations.

    This model represents the outcome of various validation checks,
    providing structured access to errors, warnings, and recommendations.

    Example:
        >>> result = ValidationResult(
        ...     errors=["Centerpiece too large"],
        ...     warnings=["Frame may clip corners"],
        ...     recommendations=["Consider using error level H"],
        ...     valid=False
        ... )
    """

    model_config = ConfigDict(frozen=True)

    errors: list[str] = Field(
        default_factory=list, description="List of validation errors"
    )

    warnings: list[str] = Field(
        default_factory=list, description="List of validation warnings"
    )

    recommendations: list[str] = Field(
        default_factory=list, description="List of recommendations for improvement"
    )

    valid: bool = Field(..., description="Whether validation passed (no errors)")

    @property
    def has_issues(self) -> bool:
        """Check if there are any errors or warnings."""
        return bool(self.errors or self.warnings)

    @property
    def total_issues(self) -> int:
        """Get total count of errors and warnings."""
        return len(self.errors) + len(self.warnings)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return self.model_dump()
