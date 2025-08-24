"""Geometry-related configuration models.

This module contains configuration classes related to module geometry,
shapes, and finder pattern styling.
"""

from pydantic import BaseModel, ConfigDict, Field

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

    model_config = ConfigDict(
        use_enum_values=True, validate_default=True, extra="forbid"
    )

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

    model_config = ConfigDict(
        use_enum_values=True, validate_default=True, extra="forbid"
    )

    shape: FinderShape = FinderShape.SQUARE
    inner_scale: float = Field(
        default=0.6, ge=0.1, le=1.0, description="Scale of inner filled square"
    )
    stroke: float = Field(
        default=0.0, ge=0.0, le=5.0, description="Stroke width in module units"
    )
