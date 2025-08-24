"""Algorithm components for advanced QR code processing.

This package provides sophisticated algorithms for analyzing and
processing QR code matrices to enable advanced rendering techniques.

Key Components:

    :class:`ConnectedComponentAnalyzer`: Identifies and groups connected
        modules into clusters for optimized rendering.

The algorithms enable:

* **Connected component analysis**: Finding groups of adjacent modules
* **Cluster optimization**: Merging small clusters and filtering by size
* **Shape analysis**: Computing cluster properties like density and aspect ratio
* **Bounding box calculation**: Determining cluster boundaries
* **Module type filtering**: Processing specific types of QR modules

These algorithms form the foundation for Phase 2 processing in the
multi-phase rendering pipeline, enabling efficient rendering of large
connected regions as single shapes.

Example:
    Basic usage of the clustering analyzer::

        from segnomms.algorithms import ConnectedComponentAnalyzer
        from segnomms.core.detector import ModuleDetector

        analyzer = ConnectedComponentAnalyzer()
        detector = ModuleDetector(matrix, version)
        clusters = analyzer.analyze(matrix, detector)

        for cluster in clusters:
            print(f"Cluster size: {cluster['module_count']}")
            print(f"Bounding box: {cluster['bounds']}")

See Also:
    :mod:`segnomms.algorithms.clustering`: Clustering implementation
"""

from .clustering import ConnectedComponentAnalyzer
from .models import ClusterInfo, ClusteringConfig, ClusteringResult

__all__ = [
    "ConnectedComponentAnalyzer",
    "ClusteringConfig",
    "ClusterInfo",
    "ClusteringResult",
]
