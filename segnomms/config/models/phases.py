"""Phase configuration models.

This module contains configuration classes for the multi-phase rendering
pipeline (Phase 1, 2, and 3).
"""

from __future__ import annotations

from typing import Dict, List

from pydantic import BaseModel, ConfigDict, Field

from ..enums import ContourMode, OptimizationLevel


class Phase1Config(BaseModel):
    """Configuration for Phase 1: Enhanced 8-neighbor detection.

    This phase handles context-aware shape rendering based on neighboring modules.

    Attributes:
        enabled: Whether Phase 1 processing is enabled
        use_enhanced_shapes: Use enhanced shape variants
        roundness: Corner roundness factor (0.0-1.0)
        size_ratio: Module size relative to grid size (0.1-1.0)
        flow_weights: Weight factors for different module types
    """

    model_config = ConfigDict(validate_default=True, extra="forbid")

    enabled: bool = False
    use_enhanced_shapes: bool = False
    roundness: float = Field(default=0.3, ge=0.0, le=1.0, description="Corner roundness factor")
    size_ratio: float = Field(default=0.9, ge=0.1, le=1.0, description="Module size relative to grid size")
    flow_weights: Dict[str, float] = Field(
        default_factory=lambda: {
            "finder": 0.5,
            "finder_inner": 0.3,
            "timing": 0.8,
            "data": 1.0,
            "alignment": 0.6,
            "format": 0.7,
        },
        description="Weight factors for different module types",
    )


class Phase2Config(BaseModel):
    """Configuration for Phase 2: Connected component clustering.

    This phase groups connected modules for optimized rendering.

    Attributes:
        enabled: Whether Phase 2 processing is enabled
        use_cluster_rendering: Render clusters as single shapes
        cluster_module_types: Module types to include in clustering
        min_cluster_size: Minimum modules required to form a cluster
        density_threshold: Minimum density for valid clusters (0.0-1.0)
        aspect_ratio_tolerance: Maximum deviation from square clusters (0.0-1.0)
    """

    model_config = ConfigDict(validate_default=True, extra="forbid")

    enabled: bool = False
    use_cluster_rendering: bool = False
    cluster_module_types: List[str] = Field(
        default_factory=lambda: ["data"],
        description="Module types to include in clustering",
    )
    min_cluster_size: int = Field(default=3, ge=1, description="Minimum modules required to form a cluster")
    density_threshold: float = Field(
        default=0.5, ge=0.0, le=1.0, description="Minimum density for valid clusters"
    )
    aspect_ratio_tolerance: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Maximum deviation from square clusters",
    )


class Phase3Config(BaseModel):
    """Configuration for Phase 3: Marching squares with Bezier curves.

    This phase creates smooth contours around module groups.

    Attributes:
        enabled: Whether Phase 3 processing is enabled
        use_marching_squares: Apply marching squares algorithm
        contour_module_types: Module types to generate contours for
        contour_mode: Contour rendering strategy
        contour_smoothing: Smoothing factor for contours (0.0-1.0)
        bezier_optimization: Optimization level for curve generation
        tension: Bezier curve tension (0.0-1.0)
        point_reduction: Factor for reducing control points (0.0-1.0)
    """

    model_config = ConfigDict(validate_default=True, extra="forbid")

    enabled: bool = False
    use_marching_squares: bool = False
    contour_module_types: List[str] = Field(
        default_factory=lambda: ["data"],
        description="Module types to generate contours for",
    )
    contour_mode: ContourMode = ContourMode.BEZIER
    contour_smoothing: float = Field(default=0.3, ge=0.0, le=1.0, description="Smoothing factor for contours")
    bezier_optimization: OptimizationLevel = OptimizationLevel.MEDIUM
    tension: float = Field(default=0.3, ge=0.0, le=1.0, description="Bezier curve tension")
    point_reduction: float = Field(
        default=0.7, ge=0.0, le=1.0, description="Factor for reducing control points"
    )
