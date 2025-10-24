# SegnoMMS Technology Stack Research

**Document Purpose**: Comprehensive technology stack documentation for spec-driven development
**Created**: 2025-01-25
**Last Updated**: 2025-01-25
**Research Scope**: Complete technology analysis for brownfield spec-kit integration

## Technology Stack Overview

### Core Dependencies

**Primary Framework**
- **Segno**: QR code generation library (>=1.5.2)
  - **Decision**: Segno chosen for robust QR code generation capabilities
  - **Rationale**: Industry-standard library with comprehensive format support
  - **Alternatives Considered**: qrcode library (less flexible), custom implementation (too complex)
  - **Integration**: Plugin architecture via entry points

**Configuration Management**
- **Pydantic v2**: Configuration validation and type safety (>=2.7,<3)
  - **Decision**: Pydantic v2 with enum objects at runtime
  - **Rationale**: Superior type safety, validation, and IDE support
  - **Alternatives Considered**: dataclasses (insufficient validation), attrs (less ecosystem support)
  - **Patterns**: Discriminated unions, TypedDict **kwargs, strict MyPy integration

**Type Safety**
- **MyPy**: Static type checking with strict configuration
  - **Decision**: Strict MyPy with Pydantic plugin integration
  - **Rationale**: Catch type errors at development time, improve code quality
  - **Configuration**: `disallow_any_generics=true`, strict mode for config modules
  - **Coverage**: 100% compliance in config modules, gradual adoption elsewhere

### Development Tools

**Build System**
- **Hatchling**: Modern PEP 517/518 build backend
  - **Decision**: Hatchling over setuptools
  - **Rationale**: Modern, fast, better pyproject.toml integration
  - **Alternatives Considered**: setuptools (legacy), poetry (opinionated)

**Package Management**
- **uv**: Fast Python package manager
  - **Decision**: uv for dependency management and virtual environments
  - **Rationale**: Significantly faster than pip, excellent lock file support
  - **Usage**: Development dependencies, tool execution, environment sync

**Code Quality**
- **Black**: Code formatting (110 char limit)
  - **Decision**: Black with 110 character line length
  - **Rationale**: Consistent formatting, community standard
  - **Configuration**: Targets Python 3.9+, extends standard excludes

- **isort**: Import sorting with Black profile
  - **Decision**: isort configured for Black compatibility
  - **Rationale**: Consistent import organization
  - **Configuration**: `profile = "black"`, trailing commas, parentheses usage

- **flake8**: Linting with project-specific ignores
  - **Decision**: flake8 over pylint for performance
  - **Rationale**: Faster execution, extensive plugin ecosystem
  - **Configuration**: 110 char limit, strategic F841 ignore for enhanced validation

- **bandit**: Security scanning
  - **Decision**: bandit for automated security analysis
  - **Rationale**: Industry standard for Python security scanning
  - **Integration**: Pre-commit hooks, excludes test directories

### Testing Framework

**Core Testing**
- **pytest**: Primary testing framework (>=8.0.0)
  - **Decision**: pytest over unittest for flexibility
  - **Rationale**: Better fixtures, parametrization, plugin ecosystem
  - **Extensions**: pytest-cov, pytest-randomly, pytest-timeout, pytest-xdist

**Test Categories**
- **Unit Testing**: Core functionality validation
- **Integration Testing**: Cross-module interaction validation
- **Visual Regression**: pytest-image-snapshot with baseline validation
- **Structural Testing**: SVG structure validation
- **Performance Testing**: Algorithm benchmarking and regression detection
- **Compatibility Testing**: Multi-version Segno compatibility

**Visual Testing**
- **pytest-image-snapshot**: Visual regression testing
  - **Decision**: Image-based visual validation
  - **Rationale**: Catch visual regressions in QR code generation
  - **Supporting Tools**: Pillow (image processing), cairosvg (SVG to PNG conversion)

**Performance Analysis**
- **psutil**: System resource monitoring
  - **Decision**: psutil for memory and CPU monitoring
  - **Rationale**: Cross-platform system monitoring
  - **Usage**: Memory leak detection, performance benchmarking

### Documentation System

**Primary Documentation**
- **Sphinx**: Documentation generation (>=7.0.0)
  - **Decision**: Sphinx-first documentation policy
  - **Rationale**: Professional documentation for commercial service
  - **Theme**: sphinx-rtd-theme for consistency
  - **Extensions**: sphinx-autodoc-typehints, myst-parser

**Markup Language**
- **reStructuredText**: Primary documentation format
  - **Decision**: RST over Markdown for user-facing documentation
  - **Rationale**: Superior cross-referencing, professional appearance
  - **Exceptions**: Only README.md, CHANGELOG.md, CLAUDE.md allowed in Markdown

### Development Workflow

**Version Control**
- **Git**: Version control with conventional commits
  - **Decision**: Conventional commit format enforcement
  - **Tools**: commitizen patterns, release-please automation
  - **Branching**: Feature branches with comprehensive review

**Pre-commit Hooks**
- **lefthook**: Git hook management
  - **Decision**: lefthook over pre-commit for performance
  - **Rationale**: Faster execution, better parallel processing
  - **Hooks**: Black, isort, flake8, MyPy, bandit, documentation validation

**CI/CD**
- **GitHub Actions**: Continuous integration and deployment
  - **Workflows**: test, docs, coverage, performance, release-please
  - **Strategy**: Comprehensive testing before merge, automated releases
  - **Tools**: act for local testing, comprehensive event validation

### Quality Standards

**Test Coverage**
- **coverage.py**: Code coverage measurement
  - **Target**: >90% test coverage
  - **Reporting**: HTML, XML, terminal output
  - **Configuration**: Branch coverage, comprehensive exclusions

**Type Coverage**
- **MyPy**: Gradual type adoption
  - **Strategy**: Strict compliance for new modules, gradual improvement for existing
  - **Status**: 100% config modules, 215 errors remaining in other modules
  - **Tools**: Pydantic MyPy plugin, strict configuration

**Performance Standards**
- **Benchmarking**: Automated performance regression detection
- **Memory Monitoring**: Leak detection and usage analysis
- **Scaling**: Algorithm performance validation across QR sizes

## Development Patterns and Best Practices

### Configuration Patterns

**Pydantic v2 Best Practices**
```python
# Discriminated unions for shape-specific configs
ShapeSpecificConfig = Annotated[
    Union[BasicShapeConfig, RoundedShapeConfig, ConnectedShapeConfig],
    Field(discriminator="shape"),
]

# TypedDict for type-safe **kwargs
class SquareRenderKwargs(TypedDict, total=False):
    radius: float
    style: str

def render(self, x: float, y: float, size: float, **kwargs: Unpack[SquareRenderKwargs]) -> ET.Element:
    # Type-safe rendering implementation
```

**Factory Pattern Implementation**
- Shape renderers use factory pattern for extensibility
- Registration system for automatic discovery
- Base classes provide common functionality
- Type-safe parameter passing

### Testing Patterns

**Visual Regression Testing**
- Baseline images stored in version control
- Automated comparison with tolerance settings
- Manual baseline updates when changes are intentional
- Cross-platform compatibility validation

**Performance Testing**
- Benchmark baselines for regression detection
- Memory usage monitoring
- Algorithm scaling validation
- Performance data JSON output for tracking

### Documentation Patterns

**Sphinx Integration**
- Auto-generated API documentation from docstrings
- Cross-referenced type information
- Example code with output validation
- Visual gallery generation from test baselines

**Code Documentation**
- Comprehensive docstrings for public APIs
- Type hints for all function signatures
- Configuration examples with JSON output
- Performance characteristics documentation

## Architecture Integration Points

### Plugin Architecture
- Segno plugin registration via entry points
- Backward-compatible API maintenance
- Configuration override capabilities
- Professional SVG output generation

### Multi-Phase Pipeline
- Phase 1: Configuration and validation
- Phase 2: Matrix processing and analysis
- Phase 3: Shape rendering and geometry
- Phase 4: SVG assembly and output

### Extension Mechanisms
- Shape renderer factory for new shapes
- Configuration model inheritance
- Pipeline phase insertion points
- Event system for processing notifications

## Security and Compliance

**Security Practices**
- Input validation through Pydantic models
- No credential logging or storage
- Automated security scanning with bandit
- Defensive programming practices only

**Commercial Standards**
- Professional SVG output quality
- Accessibility compliance (WCAG 2.1)
- Performance benchmarks and monitoring
- Comprehensive error handling

## Performance Characteristics

**Benchmarks**
- Sub-second QR generation for typical use cases
- Memory usage monitoring and leak prevention
- Scalable algorithms for large QR codes
- Performance regression detection automation

**Optimization Strategies**
- Algorithm efficiency validation
- Memory usage profiling
- Cross-platform performance testing
- Benchmark-driven optimization

This comprehensive technology stack analysis provides the foundation for spec-driven development, ensuring new features leverage existing patterns and maintain the high standards established in the SegnoMMS codebase.
