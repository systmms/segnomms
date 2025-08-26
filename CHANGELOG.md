# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-01-26

### Added
- Complete Pydantic v2 integration with strict MyPy compliance across 67 modules
- Modern enum object handling with discriminated unions for shape configurations
- TypedDict patterns for type-safe **kwargs usage in shape renderers
- Comprehensive error handling with structured exceptions
- Intent-based API with graceful degradation
- Capability discovery system
- Performance monitoring and memory leak detection
- Visual regression testing framework

### Changed
- Modernized configuration system from Pydantic v1 to v2
- Removed `use_enum_values=True` - enums now return objects at runtime
- Updated build system to use `uv` and `Hatchling`
- Enhanced type safety throughout codebase
- Improved development workflow with strict pre-commit hooks

### Fixed
- Memory leak detection test matrix dimension issue
- Unused import cleanup across modules
- Line length violations in docstrings and comments
- MyPy compliance issues in core modules

### Technical Improvements
- 1,079 comprehensive tests with excellent coverage
- Zero MyPy errors across all core modules
- Modern Python packaging with PEP 517/518 compliance
- Automated visual regression testing
- Cross-platform compatibility testing

## [0.1.0-beta] - 2024-01-17

### Added
- Initial release of SegnoMMS
- Custom shape support: square, circle, rounded, dot, diamond, hexagon, star, cross, and more
- Connected module patterns for flowing QR code designs
- Safe mode for ensuring QR code scannability
- Interactive SVG features with CSS classes and hover effects
- Support for different shapes per QR component (finder patterns, data modules, etc.)
- Comprehensive test suite with visual regression testing
- Full documentation with examples
- Pyodide compatibility for browser-based usage

### Changed
- Renamed from segno-interactive-svg to segnomms
- Updated author information to SYSTMMS

[0.1.0]: https://github.com/systmms/segnomms/releases/tag/v0.1.0
[0.1.0-beta]: https://github.com/systmms/segnomms/releases/tag/v0.1.0-beta
