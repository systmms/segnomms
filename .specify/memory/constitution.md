# SegnoMMS Constitution

## Core Principles

### I. Pydantic v2 + MyPy Type Safety (NON-NEGOTIABLE)
All configuration models MUST use Pydantic v2 with strict MyPy compliance. No `use_enum_values=True` - configuration models return enum objects at runtime. All new modules MUST pass strict MyPy validation before integration. Use discriminated unions for shape-specific configurations and TypedDict patterns for type-safe **kwargs.

### II. Sphinx-First Documentation Policy
ALL user-facing documentation MUST be written in Sphinx/RST format. Only three Markdown files are permitted: README.md, CHANGELOG.md, and CLAUDE.md. No analysis documents, implementation plans, or API documentation in Markdown. Documentation sprawl is strictly prevented to maintain professional commercial documentation standards.

### III. Test-Driven Development (NON-NEGOTIABLE)
All features MUST include comprehensive test coverage across unit, integration, visual, structural, and performance test categories. Tests MUST pass before committing. Visual regression testing with baseline validation is mandatory for shape renderers. Backward compatibility testing across multiple Segno versions is required.

### IV. Pre-commit Quality Gates
All commits MUST pass pre-commit hooks without `--no-verify` flag. Code MUST be formatted with Black, imports sorted with isort, and pass flake8 linting. MyPy type checking, security scanning with bandit, and documentation validation are enforced at commit time.

### V. Plugin Architecture Integrity
SegnoMMS MUST maintain backward compatibility with existing plugin API. All shape renderers MUST follow the factory pattern. Configuration changes MUST preserve existing kwargs API while adding new Pydantic-based validation. The multi-phase pipeline (Phase 1-4) architecture is fundamental and cannot be compromised.

## Commercial Quality Standards

### Performance Requirements
QR generation MUST complete within performance benchmarks established in the test suite. Memory usage MUST be monitored for leaks. Algorithm scaling MUST be validated across QR code sizes. Performance regressions are detected through automated benchmarking.

### Security & Validation
All external inputs MUST be validated through Pydantic models. No secrets or credentials may be logged or committed. Security scanning with bandit is mandatory. The commercial QR generation service demands defensive security practices only.

### Professional SVG Output
Generated SVG MUST include accessibility features, proper structure validation, and support for interactive elements. Visual output MUST pass regression testing against established baselines. Output quality directly impacts commercial service reputation.

## Development Workflow Standards

### Makefile-Centric Discovery
All permanent test scripts and development tools MUST be represented in the Makefile for discoverability. The `make help` command serves as the authoritative reference for available operations. Temporary or experimental scripts may remain standalone but permanent scripts require Makefile targets.

### Version Control Discipline
Git commits MUST use conventional commit format. Release Please manages automated versioning and changelog generation. Beta deployments require comprehensive review. All development follows GitHub Actions workflows for consistency and quality assurance.

### Specification-Driven Development
When using spec-kit, all specifications MUST align with existing SegnoMMS principles. Specifications supplement but do not replace Sphinx documentation. Technical plans MUST respect the constitution and existing architecture patterns.

## Development Context Integration

### Architectural Foundation References
This constitution builds upon and enforces the comprehensive development standards documented in:

- **CLAUDE.md**: Primary development context and standards (Pydantic v2 + MyPy modernization, documentation policy, testing requirements)
- **Architecture Overview**: `.specify/memory/architecture-overview.md` - Complete architectural analysis and patterns
- **Technology Research**: `.specify/memory/research.md` - Comprehensive technology stack documentation and decisions

### Standards Enforcement Hierarchy
1. **Constitution** (this document) - Non-negotiable principles and governance
2. **CLAUDE.md** - Detailed implementation practices and development context
3. **Architecture Documentation** - Technical patterns and design decisions
4. **Code Standards** - Automated enforcement through pre-commit hooks and CI/CD

### Cross-Reference Requirements
All spec-driven development MUST:
- Consult CLAUDE.md for detailed implementation guidance
- Reference architecture documentation for integration patterns
- Follow technology decisions documented in research.md
- Maintain alignment with established codebase conventions

## Governance

This constitution supersedes all other development practices and guidelines while explicitly integrating with existing architectural documentation. All feature development, code reviews, and architectural decisions MUST comply with these principles AND the referenced documentation hierarchy.

### Amendment Process
Amendments to this constitution require:

1. **Impact Assessment**: Documentation of rationale and impact on existing systems
2. **Documentation Synchronization**: Update of dependent templates, CLAUDE.md, and architecture docs
3. **Commercial Alignment**: Validation that changes align with commercial service requirements
4. **Semantic Versioning**: Constitution changes follow semantic versioning (MAJOR.MINOR.PATCH)
5. **Stakeholder Review**: Changes affecting core principles require comprehensive review

### Compliance Verification
Compliance is enforced through multiple layers:
- **Automated**: Pre-commit hooks, CI/CD pipelines, comprehensive test suite
- **Documentation**: Cross-reference validation between constitution, CLAUDE.md, and architecture docs
- **Review Process**: Code reviews must verify constitutional compliance
- **Continuous**: Regular audit of practices against constitutional principles

### Conflict Resolution
In case of conflicts between documents:
1. Constitution principles take precedence
2. CLAUDE.md provides implementation details
3. Architecture documentation provides technical context
4. When in doubt, err on the side of commercial quality and type safety

The constitution serves as the authoritative governance source while leveraging the comprehensive development context established in the existing SegnoMMS documentation ecosystem.

<!--
Sync Impact Report - Constitution Amendment
===========================================
Version change: 1.1.0 → 1.2.0 (MINOR: Enhanced template integration)
Modified principles: None (clarifications only)
Added sections: None
Removed sections: None
Templates requiring updates:
✅ .specify/templates/plan-template.md - Updated Constitution Check section with specific compliance checklist
⚠ No other template updates required
Follow-up TODOs: None
-->

**Version**: 1.2.0 | **Ratified**: 2025-01-25 | **Last Amended**: 2025-01-25
