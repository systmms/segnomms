"""Pydantic models for algorithm components.

This module provides data models for algorithm classes using Pydantic
for automatic validation and type safety.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, Tuple

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ClusteringConfig(BaseModel):
    """Configuration for ConnectedComponentAnalyzer initialization.

    This model validates the parameters needed to initialize a clustering
    analyzer, ensuring proper thresholds and connectivity modes.

    Example:
        >>> config = ClusteringConfig(
        ...     min_cluster_size=5,
        ...     density_threshold=0.7,
        ...     connectivity_mode='8-way'
        ... )
        >>> analyzer = ConnectedComponentAnalyzer(**config.model_dump())
    """

    model_config = ConfigDict()

    min_cluster_size: int = Field(
        default=3, ge=1, description="Minimum number of modules to form a cluster"
    )

    density_threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Minimum density ratio (0.0-1.0) for valid clusters",
    )

    connectivity_mode: Literal["4-way", "8-way"] = Field(
        default="4-way", description="Connectivity mode for clustering"
    )

    @field_validator("min_cluster_size")
    @classmethod
    def validate_cluster_size(cls, v: int) -> int:
        """Validate reasonable cluster size."""
        if v > 1000:
            raise ValueError(
                f"min_cluster_size of {v} is unusually large. "
                f"Consider using a value < 1000"
            )
        return v


class ClusterInfo(BaseModel):
    """Information about a detected cluster.

    This model represents the analysis results for a single cluster
    of connected modules in the QR code.
    """

    model_config = ConfigDict(frozen=True)

    positions: List[Tuple[int, int]] = Field(
        ..., min_length=1, description="List of (row, col) positions in the cluster"
    )

    bounds: Tuple[int, int, int, int] = Field(
        ..., description="Bounding box as (min_row, min_col, max_row, max_col)"
    )

    module_count: int = Field(..., ge=1, description="Number of modules in the cluster")

    density: float = Field(
        ..., ge=0.0, le=1.0, description="Ratio of filled modules in bounding box"
    )

    aspect_ratio: float = Field(
        ..., gt=0.0, description="Width/height ratio of the cluster"
    )

    is_rectangular: bool = Field(
        ..., description="Whether the cluster forms a perfect rectangle"
    )

    module_type: str = Field(
        default="data", description="Type of modules in this cluster"
    )

    @property
    def width(self) -> int:
        """Get cluster width in modules."""
        return self.bounds[3] - self.bounds[1] + 1

    @property
    def height(self) -> int:
        """Get cluster height in modules."""
        return self.bounds[2] - self.bounds[0] + 1

    @property
    def area(self) -> int:
        """Get bounding box area."""
        return self.width * self.height

    @property
    def fill_ratio(self) -> float:
        """Get ratio of actual modules to bounding box area."""
        return self.module_count / self.area if self.area > 0 else 0.0

    def contains_position(self, row: int, col: int) -> bool:
        """Check if a position is within this cluster."""
        return (row, col) in self.positions

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for compatibility."""
        return {
            "positions": self.positions,
            "bounds": self.bounds,
            "module_count": self.module_count,
            "density": self.density,
            "aspect_ratio": self.aspect_ratio,
            "is_rectangular": self.is_rectangular,
            "module_type": self.module_type,
        }


class ClusteringResult(BaseModel):
    """Result of clustering analysis.

    This model contains all clusters found during the analysis,
    along with metadata about the clustering process.
    """

    model_config = ConfigDict(frozen=True)

    clusters: List[ClusterInfo] = Field(
        default_factory=list, description="List of detected clusters"
    )

    total_modules_clustered: int = Field(
        default=0, ge=0, description="Total number of modules in all clusters"
    )

    clustering_coverage: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Ratio of clustered modules to total active modules",
    )

    parameters_used: ClusteringConfig = Field(
        ..., description="Parameters used for clustering"
    )

    @property
    def cluster_count(self) -> int:
        """Get number of clusters found."""
        return len(self.clusters)

    @property
    def average_cluster_size(self) -> float:
        """Get average size of clusters."""
        if not self.clusters:
            return 0.0
        return sum(c.module_count for c in self.clusters) / len(self.clusters)

    @property
    def largest_cluster(self) -> Optional[ClusterInfo]:
        """Get the largest cluster by module count."""
        if not self.clusters:
            return None
        return max(self.clusters, key=lambda c: c.module_count)

    def get_clusters_by_size(self, min_size: int) -> List[ClusterInfo]:
        """Get clusters with at least min_size modules."""
        return [c for c in self.clusters if c.module_count >= min_size]

    def get_rectangular_clusters(self) -> List[ClusterInfo]:
        """Get only rectangular clusters."""
        return [c for c in self.clusters if c.is_rectangular]
