# SegnoMMS Spec-Kit Developer Workflow

**Document Purpose**: Comprehensive guide for using GitHub Spec-Kit in SegnoMMS development
**Created**: 2025-01-25
**Audience**: SegnoMMS developers, contributors, and maintainers
**Prerequisites**: Familiarity with SegnoMMS architecture and development standards

## Overview

This workflow integrates GitHub Spec-Kit with established SegnoMMS development practices, providing a structured approach to feature development while maintaining all existing quality standards and architectural principles.

## Prerequisites and Setup

### Required Knowledge
- Understanding of SegnoMMS architecture (see `.specify/memory/architecture-overview.md`)
- Familiarity with Pydantic v2 + MyPy patterns
- Experience with SegnoMMS testing framework
- Knowledge of Segno plugin architecture

### Environment Setup
```bash
# Verify spec-kit installation
make spec-check

# Review available spec-kit commands
make spec-help

# Validate existing specifications (if any)
make spec-validate
```

### Documentation References
- **Primary Context**: `CLAUDE.md` - Development standards and practices
- **Architecture**: `.specify/memory/architecture-overview.md` - System architecture
- **Technology Stack**: `.specify/memory/research.md` - Technology decisions
- **Cross-Module Patterns**: `.specify/memory/cross-module-dependencies.md` - Integration patterns
- **Constitution**: `.specify/memory/constitution.md` - Development principles

## Spec-Driven Development Workflow

### Phase 1: Feature Specification

#### Step 1.1: Initialize Feature Specification

**Command**: `/speckit.specify [feature description]`

**Best Practices**:
- Focus on WHAT users need and WHY (not HOW to implement)
- Use natural language descriptions of user value
- Consider integration with existing SegnoMMS capabilities

**Example**:
```
/speckit.specify Add QR code rotation configuration to allow users to rotate generated QR codes by 90, 180, or 270 degrees while maintaining visual quality and module positioning accuracy
```

**Expected Outputs**:
- `specs/[N]-[feature-name]/spec.md` - Feature specification
- `specs/[N]-[feature-name]/checklists/requirements.md` - Quality checklist
- Automatic branch creation and checkout

#### Step 1.2: Review and Refine Specification

**Validation Points**:
- [ ] User scenarios are independently testable
- [ ] Requirements are measurable and technology-agnostic
- [ ] SegnoMMS integration requirements are addressed
- [ ] Success criteria align with commercial quality standards
- [ ] No [NEEDS CLARIFICATION] markers remain (or max 3)

**Common SegnoMMS Considerations**:
- Backward compatibility with existing plugin API
- Integration with multi-phase processing pipeline
- Visual regression testing requirements
- Performance impact on QR generation

#### Step 1.3: Clarification (if needed)

**Command**: `/speckit.clarify`

**Use When**:
- Technical architecture decisions need exploration
- Cross-module integration patterns unclear
- Performance requirements need definition
- Compatibility concerns require resolution

### Phase 2: Technical Planning

#### Step 2.1: Generate Implementation Plan

**Command**: `/speckit.plan`

**Expected Outputs**:
- `specs/[N]-[feature-name]/plan.md` - Technical implementation plan
- `specs/[N]-[feature-name]/research.md` - Research findings
- `specs/[N]-[feature-name]/data-model.md` - Data model design
- `specs/[N]-[feature-name]/contracts/` - API contracts
- `specs/[N]-[feature-name]/quickstart.md` - Implementation guide

**Validation Points**:
- [ ] Technical context reflects SegnoMMS stack
- [ ] Cross-module dependencies properly mapped
- [ ] Architecture patterns follow established conventions
- [ ] Type safety requirements addressed
- [ ] Testing strategy comprehensive

#### Step 2.2: Architecture Compliance Review

**Manual Checks**:
1. **Plugin Architecture**: Maintains Segno plugin compatibility
2. **Configuration System**: Uses Pydantic v2 patterns correctly
3. **Shape Rendering**: Follows factory pattern (if applicable)
4. **SVG Generation**: Integrates with existing pipeline
5. **Testing**: Covers all required categories

**Documentation Cross-References**:
- Compare against patterns in `cross-module-dependencies.md`
- Validate against constitutional principles
- Ensure alignment with technology decisions in `research.md`

#### Step 2.3: Quality Assessment (optional)

**Command**: `/speckit.checklist`

**Use When**:
- Complex features requiring quality validation
- First-time spec-kit usage for learning
- Features affecting core architecture
- Commercial quality assurance needed

### Phase 3: Task Implementation

#### Step 3.1: Generate Implementation Tasks

**Command**: `/speckit.tasks`

**Expected Outputs**:
- `specs/[N]-[feature-name]/tasks.md` - Actionable implementation tasks
- Task breakdown respecting SegnoMMS module boundaries
- Testing tasks integrated throughout implementation

**Validation Points**:
- [ ] Tasks respect multi-module dependency order
- [ ] Configuration changes precede processing logic
- [ ] Visual regression tests planned for rendering changes
- [ ] Documentation tasks included

#### Step 3.2: Execute Implementation

**Command**: `/speckit.implement`

**Implementation Order** (following SegnoMMS patterns):
1. **Configuration Models** (Pydantic v2 with strict MyPy)
2. **Core Processing Logic** (geometric calculations, algorithms)
3. **Shape Rendering** (if applicable, following factory pattern)
4. **SVG Integration** (coordinate systems, accessibility)
5. **Validation Rules** (input validation, output verification)
6. **Testing Suite** (unit, integration, visual, performance)
7. **Documentation** (Sphinx RST, examples, API docs)

**Quality Gates During Implementation**:
- MyPy compliance for each module
- Unit test coverage >90%
- Pre-commit hooks pass
- Performance benchmarks within thresholds
- Visual regression tests validate output

#### Step 3.3: Cross-Module Integration

**Integration Testing Strategy**:
```python
# Example integration test pattern
def test_feature_cross_module_integration():
    """Test feature integration across multiple modules."""
    # Configuration → Core
    config = FeatureConfig(...)
    processor = CoreProcessor(config)

    # Core → Rendering
    result = processor.process()
    renderer = ShapeFactory.create_renderer(config.shape)

    # Rendering → SVG
    svg_element = renderer.render(...)
    svg_doc = SVGComposer.assemble([svg_element])

    # Validation
    assert svg_doc.is_valid()
    assert meets_feature_requirements(svg_doc)
```

## Quality Assurance Integration

### Pre-Commit Validation

**Automated Checks**:
- Black code formatting
- isort import organization
- flake8 linting compliance
- MyPy type checking
- bandit security scanning
- Specification file validation

**Spec-Kit Specific Checks**:
- Specification syntax validation
- Constitution format compliance
- Template consistency verification

### Testing Strategy

**Test Categories for Spec-Driven Features**:

1. **Unit Tests**: Individual module functionality
   ```bash
   make test-unit
   pytest tests/unit/test_[feature]*.py -v
   ```

2. **Integration Tests**: Cross-module interactions
   ```bash
   make test-integration
   pytest tests/integration/test_[feature]*.py -v
   ```

3. **Visual Regression**: Rendering output validation
   ```bash
   make test-visual
   pytest tests/visual/test_[feature]*.py -v --update-baseline
   ```

4. **Structural Tests**: SVG structure validation
   ```bash
   make test-structural
   pytest tests/structural/test_[feature]*.py -v
   ```

5. **Performance Tests**: Benchmark validation
   ```bash
   make test-performance
   pytest tests/perf/test_[feature]*.py -v
   ```

### Documentation Integration

**Sphinx Documentation Requirements**:
- API documentation auto-generated from docstrings
- Configuration examples with JSON validation
- Visual examples from test baselines
- Cross-references to related features

**Example Documentation Structure**:
```rst
Feature Name
============

.. automodule:: segnomms.module.feature
   :members:

Configuration
-------------

.. autoclass:: segnomms.config.models.FeatureConfig
   :members:

Examples
--------

Basic usage:

.. code-block:: python

   config = FeatureConfig(option=value)
   result = generate_qr(config)
```

## Troubleshooting and Common Issues

### Specification Quality Issues

**Problem**: Specifications too implementation-focused
**Solution**: Revise to focus on user value and business requirements

**Problem**: Cross-module dependencies unclear
**Solution**: Consult `cross-module-dependencies.md` for patterns

**Problem**: Type safety requirements not addressed
**Solution**: Reference established Pydantic v2 patterns in codebase

### Implementation Issues

**Problem**: MyPy errors in new code
**Solution**: Follow strict type checking patterns from config modules

**Problem**: Visual regression test failures
**Solution**: Update baselines or adjust tolerance, validate intended changes

**Problem**: Performance degradation
**Solution**: Review performance patterns and benchmarking in existing code

### Integration Issues

**Problem**: Plugin API compatibility breaks
**Solution**: Ensure backward compatibility with existing kwargs API

**Problem**: Multi-module features not working together
**Solution**: Review integration testing patterns and cross-module flows

## Advanced Workflows

### Multi-Repository Features

**For features spanning multiple repositories**:
1. Open all relevant repos in same workspace
2. Use spec-kit to coordinate cross-repository changes
3. Maintain specifications in primary repository
4. Use integration tests to validate cross-repo functionality

### Legacy Code Integration

**For features interacting with legacy components**:
1. Document legacy integration patterns in specifications
2. Plan migration strategies in technical plans
3. Use adapter patterns for compatibility
4. Include regression testing for legacy compatibility

### Performance-Critical Features

**For features with performance requirements**:
1. Include performance benchmarks in specifications
2. Plan performance testing in technical plans
3. Use performance monitoring during implementation
4. Validate benchmarks before feature completion

## Best Practices Summary

### Specification Phase
- Start with user value, not technical implementation
- Reference existing SegnoMMS patterns and constraints
- Plan for comprehensive testing from the beginning
- Consider backward compatibility implications

### Planning Phase
- Leverage existing architecture documentation
- Map cross-module dependencies carefully
- Plan integration points and testing strategies
- Validate against constitutional principles

### Implementation Phase
- Follow established SegnoMMS development patterns
- Maintain strict type safety with MyPy compliance
- Implement comprehensive testing across all categories
- Integrate with existing quality gates and CI/CD

### Validation Phase
- Test across all SegnoMMS test categories
- Validate visual output with regression testing
- Ensure performance meets commercial standards
- Verify documentation integration and examples

This workflow ensures that spec-driven development enhances SegnoMMS development practices while maintaining all established quality standards and architectural principles.
