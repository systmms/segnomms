"""Geometry-related configuration models.

This module contains configuration classes related to module geometry,
shapes, and finder pattern styling.
"""

from __future__ import annotations

from typing import Literal, Union

from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import Annotated

from ..enums import ConnectivityMode, FinderShape, MergeStrategy, ModuleShape


class GeometryConfig(BaseModel):
    """Geometry and module configuration.

    Controls how modules are connected, merged, and shaped.

    Attributes:
        connectivity: How modules connect to neighbors ('4-way' or '8-way')
        merge: Module merging strategy ('none', 'soft', 'aggressive')
        corner_radius: Relative corner radius (0=square, 1=circle)
        shape: Base module shape type
        min_island_modules: Minimum size for isolated module groups

    Example:
        Creating geometry configuration::

            # Basic rounded modules
            geometry = GeometryConfig(
                shape="rounded",
                corner_radius=0.3
            )

            # Connected modules with merging
            geometry = GeometryConfig(
                shape="connected",
                connectivity="8-way",
                merge="soft"
            )

            # Remove small islands
            geometry = GeometryConfig(
                shape="circle",
                min_island_modules=3
            )
    """

    model_config = ConfigDict(validate_default=True, extra="forbid")

    connectivity: ConnectivityMode = ConnectivityMode.FOUR_WAY
    merge: MergeStrategy = MergeStrategy.NONE
    corner_radius: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Relative corner radius (0=square, 1=circle)",
    )
    shape: ModuleShape = ModuleShape.SQUARE
    min_island_modules: int = Field(
        default=1, ge=1, le=10, description="Minimum size for isolated module groups"
    )


class FinderConfig(BaseModel):
    """Finder pattern styling configuration.

    Controls special styling for the three corner finder patterns.

    Attributes:
        shape: Finder pattern shape type
        inner_scale: Scale of inner filled square (0.1-1.0)
        stroke: Stroke width in module units (0-5)
    """

    model_config = ConfigDict(validate_default=True, extra="forbid")

    shape: FinderShape = FinderShape.SQUARE
    inner_scale: float = Field(
        default=0.6, ge=0.1, le=1.0, description="Scale of inner filled square"
    )
    stroke: float = Field(
        default=0.0, ge=0.0, le=5.0, description="Stroke width in module units"
    )


# Discriminated Union Patterns for Shape-Specific Configurations


class BasicShapeConfig(BaseModel):
    """Configuration for basic shapes (square, circle, diamond, dot)."""

    model_config = ConfigDict(validate_default=True, extra="forbid")

    shape: Literal[
        "square", "circle", "diamond", "dot", "star", "hexagon", "triangle", "cross"
    ]
    connectivity: ConnectivityMode = ConnectivityMode.FOUR_WAY
    merge: MergeStrategy = MergeStrategy.NONE
    min_island_modules: int = Field(
        default=1, ge=1, le=10, description="Minimum size for isolated module groups"
    )


class RoundedShapeConfig(BaseModel):
    """Configuration for shapes with corner radius (rounded, squircle)."""

    model_config = ConfigDict(validate_default=True, extra="forbid")

    shape: Literal["rounded", "squircle"]
    corner_radius: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Relative corner radius (0=square, 1=circle)",
    )
    connectivity: ConnectivityMode = ConnectivityMode.FOUR_WAY
    merge: MergeStrategy = MergeStrategy.NONE
    min_island_modules: int = Field(
        default=1, ge=1, le=10, description="Minimum size for isolated module groups"
    )


class ConnectedShapeConfig(BaseModel):
    """Configuration for connected shapes with merging capabilities."""

    model_config = ConfigDict(validate_default=True, extra="forbid")

    shape: Literal[
        "connected",
        "connected-extra-rounded",
        "connected-classy",
        "connected-classy-rounded",
    ]
    corner_radius: float = Field(
        default=0.2,
        ge=0.0,
        le=1.0,
        description="Relative corner radius for connected elements",
    )
    connectivity: ConnectivityMode = ConnectivityMode.EIGHT_WAY
    merge: MergeStrategy = MergeStrategy.SOFT
    min_island_modules: int = Field(
        default=2, ge=1, le=10, description="Minimum size for isolated module groups"
    )


# Discriminated union type
ShapeSpecificConfig = Annotated[
    Union[BasicShapeConfig, RoundedShapeConfig, ConnectedShapeConfig],
    Field(discriminator="shape"),
]


class ModernGeometryConfig(BaseModel):
    """Modern geometry configuration using discriminated unions.

    This provides type-safe shape-specific configuration while maintaining
    backward compatibility through factory methods.
    """

    model_config = ConfigDict(validate_default=True, extra="forbid")

    config: ShapeSpecificConfig

    @classmethod
    def from_legacy(cls, legacy_config: GeometryConfig) -> "ModernGeometryConfig":
        """Convert legacy GeometryConfig to discriminated union format."""
        shape_value = legacy_config.shape.value

        # Determine which union type to use based on shape
        if shape_value in ["rounded", "squircle"]:
            config = RoundedShapeConfig(
                shape=shape_value,  # type: ignore
                corner_radius=legacy_config.corner_radius,
                connectivity=legacy_config.connectivity,
                merge=legacy_config.merge,
                min_island_modules=legacy_config.min_island_modules,
            )
        elif shape_value.startswith("connected"):
            config = ConnectedShapeConfig(
                shape=shape_value,  # type: ignore
                corner_radius=legacy_config.corner_radius,
                connectivity=legacy_config.connectivity,
                merge=legacy_config.merge,
                min_island_modules=legacy_config.min_island_modules,
            )
        else:
            config = BasicShapeConfig(
                shape=shape_value,  # type: ignore
                connectivity=legacy_config.connectivity,
                merge=legacy_config.merge,
                min_island_modules=legacy_config.min_island_modules,
            )

        return cls(config=config)

    def to_legacy(self) -> GeometryConfig:
        """Convert back to legacy GeometryConfig format."""
        return GeometryConfig(
            connectivity=self.config.connectivity,
            merge=self.config.merge,
            corner_radius=getattr(self.config, "corner_radius", 0.0),
            shape=ModuleShape(self.config.shape),
            min_island_modules=self.config.min_island_modules,
        )
