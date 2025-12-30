# SegnoMMS Architecture Overview

**Document Purpose**: Baseline architecture analysis for spec-driven development integration
**Created**: 2025-01-25
**Status**: Living document - updated as architecture evolves

## Executive Summary

SegnoMMS is a sophisticated Segno QR code generation plugin that extends basic QR functionality with advanced shape rendering, comprehensive configuration management, and professional SVG output. The architecture follows a multi-phase pipeline design with strict type safety and comprehensive testing frameworks.

## Core Architecture Patterns

### 1. Plugin Architecture Foundation

**Base Integration**:
- Implements Segno plugin interface via `project.entry-points."segno.plugin.converter"`
- Entry point: `segnomms.plugin:write` function
- Maintains backward compatibility with existing Segno workflows

**Key Characteristics**:
- Self-contained plugin that doesn't modify Segno core
- Comprehensive configuration override capabilities
- Professional SVG generation with accessibility features

### 2. Multi-Phase Processing Pipeline

**Phase 1: Configuration & Validation**
- Pydantic v2 models with discriminated unions for shape-specific configs
- Comprehensive input validation and type checking
- Factory pattern for configuration instantiation

**Phase 2: Matrix Processing & Analysis**
- QR matrix manipulation and optimization
- Module clustering and geometric analysis
- Performance monitoring and validation

**Phase 3: Shape Rendering & Geometry**
- 14 different shape renderers with factory pattern
- Type-safe rendering with TypedDict **kwargs patterns
- Visual effects and interactivity layer

**Phase 4: SVG Assembly & Output**
- Accessibility-compliant SVG generation
- Frame effects and visual composition
- Export and serialization with configuration metadata

### 3. Configuration Management System

**Pydantic v2 Architecture**:
- Strict type safety with MyPy compliance
- Enum objects at runtime (no `use_enum_values=True`)
- Discriminated unions for shape-specific configurations
- Comprehensive validation with detailed error messages

**Configuration Hierarchy**:
```
CoreConfig
├── GeometryConfig (size, positioning, scaling)
├── VisualConfig (colors, themes, effects)
├── ShapeSpecificConfig (Union of shape variants)
│   ├── BasicShapeConfig
│   ├── RoundedShapeConfig
│   └── ConnectedShapeConfig
├── AdvancedConfig (performance, accessibility)
└── PhaseConfig (processing pipeline control)
```

## Module Structure Analysis

### Core Modules (`segnomms/`)

**`config/`** - Configuration Management
- `models/` - Pydantic v2 configuration models
- `enums.py` - Type-safe enumeration definitions
- `presets.py` - Pre-defined configuration templates

**`core/`** - Processing Engine
- `advanced_qr.py` - Enhanced QR generation logic
- `detector.py` - QR pattern recognition and analysis
- `performance.py` - Performance monitoring and optimization
- `geometry/` - Geometric analysis and calculations
- `matrix/` - QR matrix manipulation utilities

**`shapes/`** - Shape Rendering System
- `factory.py` - Shape renderer factory pattern
- `basic.py` - Basic geometric shapes (square, circle, etc.)
- `connected.py` - Connected shape variants
- `frames.py` - Frame and border rendering

**`svg/`** - SVG Generation
- `core.py` - Core SVG assembly logic
- `accessibility.py` - WCAG compliance features
- `interactivity.py` - Interactive element support
- `composite.py` - Multi-layer composition

**`validation/`** - Quality Assurance
- `models.py` - Validation rule definitions
- `composition.py` - Composition validation (CompositionValidator)

### Supporting Systems

**`a11y/`** - Accessibility
- Comprehensive accessibility feature implementation
- WCAG 2.1 compliance validation
- Screen reader optimization

**`algorithms/`** - Advanced Processing
- `clustering.py` - Module clustering algorithms
- `models.py` - Algorithm configuration models

**`color/`** - Color Management
- `palette.py` - Color palette generation and validation
- `color_analysis.py` - Color harmony and contrast analysis

**`intents/`** - Content Processing
- Smart content type detection
- Automatic configuration optimization
- Content-aware rendering adjustments

**`degradation/`** - Graceful Degradation
- Fallback strategies for complex features
- Progressive enhancement patterns
- Compatibility mode management

## Technology Stack Integration

### Build and Dependency Management
- **Build System**: Hatchling (PEP 517/518 compliant)
- **Package Manager**: uv for fast dependency resolution
- **Dependencies**: Segno >=1.5.2, Pydantic >=2.7,<3, typing-extensions

### Quality Assurance Stack
- **Type Checking**: MyPy with strict configuration and Pydantic plugin
- **Code Formatting**: Black (110 char limit), isort with Black profile
- **Linting**: flake8 with project-specific ignore patterns
- **Security**: bandit for security scanning
- **Pre-commit**: lefthook for comprehensive quality gates

### Testing Framework
- **Unit Testing**: pytest with comprehensive coverage
- **Visual Regression**: pytest-image-snapshot with baseline validation
- **Performance Testing**: Dedicated performance benchmark suite
- **Integration Testing**: Cross-module compatibility validation
- **Compatibility Testing**: Multi-version Segno compatibility validation

### Documentation System
- **Primary Documentation**: Sphinx with RST format (Sphinx-first policy)
- **API Documentation**: Auto-generated from docstrings
- **Examples**: Comprehensive example generation with JSON configuration
- **Visual Gallery**: Auto-generated visual examples from test baselines

## Architectural Constraints and Design Decisions

### Type Safety Requirements
- All configuration models must pass strict MyPy validation
- Runtime enum objects (no string conversion)
- Discriminated unions for type narrowing
- TypedDict patterns for **kwargs type safety

### Backward Compatibility
- Existing kwargs API must be preserved
- Plugin registration interface cannot change
- Output format compatibility with existing consumers
- Migration paths for configuration changes

### Performance Requirements
- Sub-second QR generation for typical use cases
- Memory usage monitoring and leak prevention
- Scalable algorithms for large QR codes
- Performance regression detection

### Commercial Quality Standards
- Professional SVG output with accessibility features
- Comprehensive error handling and validation
- Security-conscious input processing
- Production-ready logging and monitoring

## Extension Points and Integration Patterns

### Shape Renderer Extension
- Factory pattern allows new shape renderers
- TypedDict defines rendering parameter contracts
- Base classes provide common functionality
- Registration system for automatic discovery

### Configuration Extension
- Pydantic model inheritance for new config types
- Discriminated unions for shape-specific additions
- Validation rule extension through custom validators
- Preset system for common configuration patterns

### Pipeline Extension
- Phase-based processing allows insertion points
- Event system for processing notifications
- Plugin hooks for custom processing logic
- Performance monitoring integration points

## Technical Debt and Modernization Status

### Recently Completed Modernization
- **Pydantic v2 Migration**: 100% complete with enum objects at runtime
- **MyPy Compliance**: Config modules achieve 100% strict compliance
- **Type Safety**: Comprehensive TypedDict and discriminated union patterns

### Ongoing Improvements
- **MyPy Coverage**: 215 errors remain in non-config modules
- **Test Modernization**: Some tests expect string values instead of enum objects
- **Documentation**: Continuous improvement of Sphinx documentation

### Architecture Strengths
- Clean separation of concerns across modules
- Comprehensive testing across multiple categories
- Strong type safety foundation
- Extensible plugin architecture
- Commercial-grade quality standards

This architecture analysis provides the foundation for spec-driven development, ensuring new features integrate seamlessly with existing patterns while maintaining the high quality standards established in the SegnoMMS codebase.
