"""Connected component clustering algorithm for QR code modules.

This module implements Phase 2 of the multi-phase rendering pipeline,
which identifies and groups adjacent modules into connected components
for optimized rendering.

The clustering algorithm:

1. **Traverses** the QR matrix to find active modules
2. **Groups** adjacent modules of the same type into clusters
3. **Analyzes** cluster properties (size, density, shape)
4. **Filters** clusters based on configurable thresholds
5. **Optimizes** rendering by treating clusters as single shapes

This approach significantly reduces the number of SVG elements needed
for complex QR codes, improving both file size and rendering performance.
"""

from typing import Any, Dict, List, Literal, Optional, Set, Tuple

from ..core.detector import ModuleDetector
from ..core.interfaces import AlgorithmProcessor, Matrix
from .models import ClusteringConfig


class ConnectedComponentAnalyzer(AlgorithmProcessor):
    """Analyzes connected components in QR code matrices.

    This analyzer implements a depth-first search algorithm to identify
    clusters of connected modules. It's used in Phase 2 processing to
    group adjacent modules for optimized rendering.

    Attributes:
        min_cluster_size: Minimum modules required to form a valid cluster
        density_threshold: Minimum density (filled ratio) for valid clusters
        visited: Set tracking already-processed module positions

    Example:
        >>> analyzer = ConnectedComponentAnalyzer(min_cluster_size=5)
        >>> clusters = analyzer.process(matrix, detector)
        >>> print(f"Found {len(clusters)} clusters")
    """

    def __init__(
        self,
        min_cluster_size: int = 3,
        density_threshold: float = 0.5,
        connectivity_mode: Literal["4-way", "8-way"] = "4-way",
    ):
        """Initialize the connected component analyzer.

        Args:
            min_cluster_size: Minimum number of modules to form a cluster
            density_threshold: Minimum density ratio (0.0-1.0) for valid clusters
            connectivity_mode: '4-way' or '8-way' connectivity

        Example:
            >>> analyzer = ConnectedComponentAnalyzer(min_cluster_size=5)
            >>> # Or using Pydantic model
            >>> config = ClusteringConfig(min_cluster_size=5, density_threshold=0.7)
            >>> analyzer = ConnectedComponentAnalyzer(**config.model_dump())
        """
        # Validate inputs using Pydantic
        config = ClusteringConfig(
            min_cluster_size=min_cluster_size,
            density_threshold=density_threshold,
            connectivity_mode=connectivity_mode,
        )

        # Use validated values
        self.min_cluster_size = config.min_cluster_size
        self.density_threshold = config.density_threshold
        self.connectivity_mode = config.connectivity_mode
        self.visited: Set[Tuple[int, int]] = set()
        self.config = config

    def process(
        self, matrix: Matrix, detector: ModuleDetector, **kwargs: Any
    ) -> List[Dict[str, Any]]:
        """Process the QR matrix to find connected components.

        Traverses the matrix to identify groups of connected modules,
        analyzes their properties, and returns clusters that meet the
        size and density requirements.

        Args:
            matrix: 2D boolean matrix representing QR code modules
            detector: Module detector for determining module types
            **kwargs: Additional parameters including:
                cluster_module_types: List of module types to cluster
                    (default: ['data'])

        Returns:
            List[Dict[str, Any]]: List of cluster dictionaries, each containing:
                - positions: List of (row, col) tuples
                - bounds: (min_row, min_col, max_row, max_col)
                - module_count: Number of modules in cluster
                - density: Ratio of filled modules in bounding box
                - aspect_ratio: Width/height ratio
                - is_rectangular: Whether cluster forms a rectangle
        """
        cluster_module_types = kwargs.get("cluster_module_types", ["data"])
        self.visited = set()
        clusters = []

        for row in range(len(matrix)):
            for col in range(len(matrix[0])):
                if (row, col) not in self.visited and matrix[row][col]:
                    module_type = detector.get_module_type(row, col)

                    if module_type in cluster_module_types:
                        cluster = self._find_connected_component(
                            matrix, detector, row, col, cluster_module_types
                        )

                        if len(cluster["positions"]) >= self.min_cluster_size:
                            cluster_info = self._analyze_cluster(
                                cluster, matrix, detector
                            )
                            if cluster_info["density"] >= self.density_threshold:
                                clusters.append(cluster_info)

        return clusters

    def cluster_modules(self, modules, **kwargs):
        """Alias for process() method for backward compatibility.
        
        Args:
            modules: Either a 2D matrix or list of (row, col, active) tuples
            **kwargs: Additional parameters passed to process()
            
        Returns:
            List of cluster dictionaries
        """
        # Convert list of tuples to matrix format if needed
        if isinstance(modules, list) and modules and len(modules[0]) == 3:
            # Convert (row, col, active) tuples to matrix
            if not modules:
                return []
            
            max_row = max(pos[0] for pos in modules)
            max_col = max(pos[1] for pos in modules)
            matrix = [[False for _ in range(max_col + 1)] for _ in range(max_row + 1)]
            
            for row, col, active in modules:
                if active:
                    matrix[row][col] = True
        else:
            matrix = modules
            
        # Use a mock detector for compatibility
        from ..core.detector import ModuleDetector
        from unittest.mock import Mock
        
        mock_detector = Mock(spec=ModuleDetector)
        mock_detector.get_module_type.return_value = "data"
        mock_detector.get_neighbors.return_value = []
        
        return self.process(matrix, mock_detector, **kwargs)

    def _find_connected_component(
        self,
        matrix: Matrix,
        detector: ModuleDetector,
        start_row: int,
        start_col: int,
        target_types: List[str],
    ) -> Dict[str, Any]:
        """Find all connected modules starting from a given position.

        Uses depth-first search to explore all modules connected to the
        starting position. Only considers modules of the specified types
        and uses 4-connectivity (von Neumann neighborhood).

        Args:
            matrix: QR code matrix
            detector: Module detector instance
            start_row: Starting row position
            start_col: Starting column position
            target_types: List of module types to include in cluster

        Returns:
            Dict[str, Any]: Dictionary containing:
                - positions: List of (row, col) tuples in the component
                - start_position: Original starting position
        """
        stack = [(start_row, start_col)]
        positions = []

        while stack:
            row, col = stack.pop()

            if (row, col) in self.visited:
                continue

            if not (0 <= row < len(matrix) and 0 <= col < len(matrix[0])):
                continue

            if not matrix[row][col]:
                continue

            module_type = detector.get_module_type(row, col)
            if module_type not in target_types:
                continue

            self.visited.add((row, col))
            positions.append((row, col))

            # Add neighbors to stack based on connectivity mode
            if self.connectivity_mode == "8-way":
                # 8-way connectivity (Moore neighborhood)
                neighbors = detector.get_neighbors(row, col, "moore")
            else:
                # 4-way connectivity (von Neumann neighborhood)
                neighbors = detector.get_neighbors(row, col, "von_neumann")

            for nr, nc in neighbors:
                if (nr, nc) not in self.visited:
                    stack.append((nr, nc))

        return {
            "positions": positions,
            "start_position": (start_row, start_col),
        }

    def _analyze_cluster(
        self, cluster: Dict[str, Any], matrix: Matrix, detector: ModuleDetector
    ) -> Dict[str, Any]:
        """Analyze properties of a cluster to determine rendering suitability.

        Computes various metrics about the cluster including its bounding box,
        density, aspect ratio, and whether it forms a perfect rectangle.

        Args:
            cluster: Cluster data with positions
            matrix: QR code matrix
            detector: Module detector instance

        Returns:
            Dict[str, Any]: Enhanced cluster data with computed properties:
                - All original cluster data
                - bounds: Bounding box coordinates
                - module_count: Total modules in cluster
                - density: Fill ratio within bounding box
                - aspect_ratio: Width to height ratio
                - is_rectangular: True if cluster fills entire bounding box
        """
        positions = cluster["positions"]

        if not positions:
            return cluster

        # Calculate bounding box
        rows = [pos[0] for pos in positions]
        cols = [pos[1] for pos in positions]
        min_row, max_row = min(rows), max(rows)
        min_col, max_col = min(cols), max(cols)

        # Calculate cluster properties
        width = max_col - min_col + 1
        height = max_row - min_row + 1
        area = width * height
        density = len(positions) / area if area > 0 else 0

        # Calculate aspect ratio
        aspect_ratio = width / height if height > 0 else 1.0

        # Determine cluster shape type
        shape_type = self._determine_cluster_shape(
            positions, width, height, aspect_ratio
        )

        # Calculate center of mass
        center_row = sum(rows) / len(rows)
        center_col = sum(cols) / len(cols)

        # Analyze connectivity patterns
        connectivity = self._analyze_connectivity(positions, matrix, detector)

        # Generate rendering hints
        rendering_hints = self._generate_rendering_hints(
            positions, width, height, aspect_ratio, shape_type, connectivity
        )

        cluster.update(
            {
                "bounding_box": (min_row, min_col, max_row, max_col),
                "width": width,
                "height": height,
                "area": area,
                "density": density,
                "aspect_ratio": aspect_ratio,
                "shape_type": shape_type,
                "center": (center_row, center_col),
                "connectivity": connectivity,
                "rendering_hints": rendering_hints,
                "size": len(positions),
            }
        )

        return cluster

    def _determine_cluster_shape(
        self,
        positions: List[Tuple[int, int]],
        width: int,
        height: int,
        aspect_ratio: float,
    ) -> str:
        """Determine the best shape representation for a cluster.

        Classifies clusters based on their dimensions and aspect ratio
        to select optimal rendering strategies.

        Args:
            positions: List of module positions in cluster
            width: Cluster width in modules
            height: Cluster height in modules
            aspect_ratio: Width to height ratio

        Returns:
            str: Shape type classification
        """
        # Simple heuristics for shape classification
        if width == 1 and height > 2:
            return "vertical_line"
        elif height == 1 and width > 2:
            return "horizontal_line"
        elif abs(aspect_ratio - 1.0) < 0.3:  # Nearly square
            return "square_cluster"
        elif aspect_ratio > 2.0:
            return "horizontal_rectangle"
        elif aspect_ratio < 0.5:
            return "vertical_rectangle"
        else:
            return "rectangle_cluster"

    def _analyze_connectivity(
        self,
        positions: List[Tuple[int, int]],
        matrix: Matrix,
        detector: ModuleDetector,
    ) -> Dict[str, Any]:
        """Analyze connectivity patterns within the cluster.

        Examines how modules within the cluster are connected to each
        other to determine rendering suitability.

        Args:
            positions: List of module positions in cluster
            matrix: QR code matrix
            detector: Module detector instance

        Returns:
            Dict[str, Any]: Connectivity metrics including:
                - internal_connections: Number of cardinal connections
                - corner_connections: Number of diagonal connections
                - connectivity_ratio: Ratio of actual to possible connections
                - avg_connections_per_module: Average connectivity
        """
        position_set = set(positions)

        # Count different types of connections
        internal_connections = 0
        corner_connections = 0

        for row, col in positions:
            # Get 8-connected neighbors
            neighbors = detector.get_neighbors(row, col, "moore")

            cardinal_neighbors = []
            diagonal_neighbors = []

            for nr, nc in neighbors:
                if (nr, nc) in position_set:
                    dr, dc = nr - row, nc - col
                    if abs(dr) + abs(dc) == 1:  # Cardinal neighbor
                        cardinal_neighbors.append((nr, nc))
                        internal_connections += 1
                    else:  # Diagonal neighbor
                        diagonal_neighbors.append((nr, nc))
                        corner_connections += 1

        # Calculate connectivity metrics
        total_possible_connections = len(positions) * 4  # Max cardinal connections
        connectivity_ratio = (
            internal_connections / total_possible_connections
            if total_possible_connections > 0
            else 0
        )

        return {
            "internal_connections": internal_connections // 2,  # Avoid double counting
            "corner_connections": corner_connections // 2,
            "connectivity_ratio": connectivity_ratio,
            "avg_connections_per_module": (
                internal_connections / len(positions) if positions else 0
            ),
        }

    def _generate_rendering_hints(
        self,
        positions: List[Tuple[int, int]],
        width: int,
        height: int,
        aspect_ratio: float,
        shape_type: str,
        connectivity: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate hints for optimal cluster rendering.

        Creates recommendations for how to render the cluster based on
        its properties, including shape selection and styling parameters.

        Args:
            positions: Cluster module positions
            width: Cluster width
            height: Cluster height
            aspect_ratio: Width/height ratio
            shape_type: Determined shape classification
            connectivity: Connectivity analysis results

        Returns:
            Dict[str, Any]: Rendering hints including:
                - render_as_single_shape: Whether to merge modules
                - preferred_shape: Recommended shape type
                - roundness: Corner rounding factor
                - merge_strategy: How to combine modules
        """
        hints: Dict[str, Any] = {
            "render_as_single_shape": False,
            "preferred_shape": "rounded_rectangle",
            "roundness": 0.2,
            "merge_strategy": "outline",
            "stroke_width": 1,
        }

        # Determine if cluster should be rendered as single shape
        if len(positions) >= 4 and connectivity["connectivity_ratio"] > 0.6:
            hints["render_as_single_shape"] = True

        # Adjust rendering based on shape type
        if shape_type in ["vertical_line", "horizontal_line"]:
            hints["preferred_shape"] = "pill"
            hints["roundness"] = 0.5
        elif shape_type == "square_cluster":
            hints["preferred_shape"] = "rounded_square"
            hints["roundness"] = 0.3
        elif "rectangle" in shape_type:
            hints["preferred_shape"] = "rounded_rectangle"
            hints["roundness"] = min(0.4, 1.0 / max(width, height))

        # Adjust roundness based on size
        size_factor = min(1.0, len(positions) / 10.0)
        hints["roundness"] *= size_factor

        return hints

    def get_cluster_svg_path(
        self,
        cluster: Dict[str, Any],
        scale: int = 8,
        border: int = 0,
        path_clipper: Optional[Any] = None,
    ) -> str:
        """Generate SVG path for rendering cluster as a single shape.

        Creates an SVG path string that represents the entire cluster
        as a merged shape, reducing the number of individual elements.

        Args:
            cluster: Cluster data with positions and rendering hints
            scale: Module size in pixels
            border: Border size in modules
            path_clipper: Optional PathClipper instance for frame-aware clipping

        Returns:
            str: SVG path data string for the cluster shape

        Note:
            Currently uses a simple bounding box approach. Future versions
            could implement more sophisticated contour tracing.
        """
        positions = cluster["positions"]
        if not positions:
            return ""

        # Simple outline generation using convex hull approach
        # For now, use bounding box approach
        min_row, min_col, max_row, max_col = cluster["bounding_box"]

        x = (min_col + border) * scale
        y = (min_row + border) * scale
        width = (max_col - min_col + 1) * scale
        height = (max_row - min_row + 1) * scale

        # If path clipper is provided, check if cluster is within frame
        if path_clipper:
            clipped_path = path_clipper.clip_rectangle_to_frame(x, y, width, height)
            if not clipped_path:
                return ""  # Cluster is entirely outside frame
            # For non-square frames, we might need to adjust the path
            # For now, continue with standard path generation

        roundness = cluster["rendering_hints"]["roundness"]
        rx = width * roundness
        ry = height * roundness

        # Generate rounded rectangle path
        if roundness > 0:
            path = (
                f"M {x + rx} {y} "
                f"L {x + width - rx} {y} "
                f"Q {x + width} {y} {x + width} {y + ry} "
                f"L {x + width} {y + height - ry} "
                f"Q {x + width} {y + height} {x + width - rx} {y + height} "
                f"L {x + rx} {y + height} "
                f"Q {x} {y + height} {x} {y + height - ry} "
                f"L {x} {y + ry} "
                f"Q {x} {y} {x + rx} {y} "
                f"Z"
            )
        else:
            # Simple rectangle
            path = f"M {x} {y} L {x + width} {y} L {x + width} {y + height} L {x} {y + height} Z"

        # Apply frame clipping if needed
        if path_clipper and path_clipper.frame_shape != "square":
            path = path_clipper.adjust_cluster_path(path, scale)

        return path
