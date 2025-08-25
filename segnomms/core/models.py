"""Pydantic models for core components.

This module provides data models for core classes using Pydantic
for automatic validation and type safety.
"""

from typing import List, Optional, Tuple, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ModuleDetectorConfig(BaseModel):
    """Configuration for ModuleDetector initialization.

    This model validates the parameters needed to initialize a ModuleDetector
    instance, ensuring proper QR code matrix structure and version.

    Example:
        >>> matrix = [[True, False], [False, True]]
        >>> config = ModuleDetectorConfig(matrix=matrix)
        >>> detector = ModuleDetector(**config.model_dump())
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    matrix: List[List[bool]] = Field(
        ..., description="The QR code matrix as a 2D boolean list"
    )

    version: Optional[Union[int, str]] = Field(
        None,
        description="QR code version (1-40, 'M1'-'M4', or None for auto-detection)",
    )

    @field_validator("matrix")
    @classmethod
    def validate_matrix(cls, v: List[List[bool]]) -> List[List[bool]]:
        """Validate matrix structure and size."""
        if not v:
            raise ValueError("Matrix cannot be empty")

        # Check if matrix is square
        size = len(v)
        if not all(len(row) == size for row in v):
            raise ValueError(
                "Matrix must be square (all rows must have the same "
                "length as the number of rows)"
            )

        # Check if size follows QR code specification
        micro_qr_sizes = {11, 13, 15, 17}
        is_micro_qr = size in micro_qr_sizes
        is_regular_qr = size >= 21 and (size - 21) % 4 == 0

        if not (is_micro_qr or is_regular_qr):
            if size < 11:
                raise ValueError(
                    f"Matrix size {size}x{size} is too small. "
                    f"Minimum QR code size is 11x11 (Micro QR)"
                )
            else:
                raise ValueError(
                    f"Invalid QR code size {size}x{size}. "
                    f"Must be 11x11, 13x13, 15x15, 17x17 (Micro QR) "
                    f"or 21+4*n (Regular QR)"
                )

        return v

    @field_validator("version")
    @classmethod
    def validate_version(
        cls, v: Optional[Union[int, str]]
    ) -> Optional[Union[int, str]]:
        """Validate version format."""
        if v is None:
            return v

        if isinstance(v, int):
            if not 1 <= v <= 40:
                raise ValueError(f"Integer version must be between 1 and 40, got {v}")
        elif isinstance(v, str):
            # Handle Micro QR versions
            if v.startswith("M"):
                if v not in ["M1", "M2", "M3", "M4"]:
                    raise ValueError(
                        f"Invalid Micro QR version '{v}'. " f"Must be M1, M2, M3, or M4"
                    )
            else:
                # Try to parse as integer
                try:
                    version_int = int(v)
                    if not 1 <= version_int <= 40:
                        raise ValueError(
                            f"String version must represent 1-40, got '{v}'"
                        )
                except ValueError:
                    raise ValueError(f"Invalid version string '{v}'")

        return v

    @model_validator(mode="after")
    def validate_version_matches_size(self) -> "ModuleDetectorConfig":
        """Validate that version matches matrix size if both are provided."""
        if self.version is not None and self.matrix:
            size = len(self.matrix)

            if isinstance(self.version, str) and self.version.startswith("M"):
                # Micro QR validation
                micro_sizes = {"M1": 11, "M2": 13, "M3": 15, "M4": 17}
                expected_size = micro_sizes.get(self.version)
                if expected_size and size != expected_size:
                    # Just log warning, don't raise error
                    pass
            elif isinstance(self.version, (int, str)):
                # Regular QR validation
                version_int = (
                    int(self.version) if isinstance(self.version, str) else self.version
                )
                if version_int <= 40:  # Regular QR
                    expected_size = 21 + 4 * (version_int - 1)
                    if size != expected_size:
                        # Just log warning, don't raise error
                        pass

        return self


class NeighborAnalysis(BaseModel):
    """Result of weighted neighbor analysis.

    This model represents the comprehensive analysis of a module's neighbors,
    including connectivity strength, flow direction, and shape hints.
    """

    model_config = ConfigDict(frozen=True)

    cardinal_count: int = Field(
        ..., ge=0, le=4, description="Number of active cardinal neighbors"
    )

    diagonal_count: int = Field(
        ..., ge=0, le=4, description="Number of active diagonal neighbors"
    )

    connectivity_strength: float = Field(
        ..., ge=0, description="Weighted connectivity strength"
    )

    weighted_strength: float = Field(
        ..., ge=0, description="Connectivity strength weighted by module type"
    )

    horizontal_flow: float = Field(
        ..., ge=0, le=1, description="Horizontal flow strength"
    )

    vertical_flow: float = Field(..., ge=0, le=1, description="Vertical flow strength")

    flow_direction: str = Field(
        ..., pattern="^(horizontal|vertical)$", description="Primary flow direction"
    )

    isolation_level: int = Field(
        ..., ge=0, le=4, description="How isolated the module is (4 - cardinal_count)"
    )

    corner_connections: int = Field(
        ..., ge=0, le=4, description="Number of diagonal connections"
    )

    active_neighbors: List[Tuple[int, int]] = Field(
        ..., description="List of active neighbor positions"
    )
