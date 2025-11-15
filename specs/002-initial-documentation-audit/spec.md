# Feature Specification: Initial Documentation Audit

**Feature Branch**: `002-initial-documentation-audit`
**Created**: 2025-01-15
**Status**: Draft
**Input**: User description: "Systematically fix 27 documentation issues identified in comprehensive audit, including critical contradictions (package naming, repository URLs, author attribution), high-priority fixes (Python 3.14 support, import paths, dependency installation), and completeness improvements (API docs, examples, cross-references)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - New Developer Installation Success (Priority: P1)

A developer discovers SegnoMMS through GitHub or PyPI and wants to install it for their QR code generation project. They need accurate installation instructions, correct repository URLs, and consistent package naming to successfully set up the library.

**Why this priority**: Critical blocking issues prevent users from installing or finding the correct package. Without these fixes, users cannot even start using SegnoMMS, leading to immediate abandonment and lost adoption.

**Independent Test**: Can be fully tested by following README.md installation instructions on a fresh environment and verifying successful installation, correct repository clone, and package import with consistent naming.

**Acceptance Scenarios**:

1. **Given** a developer reads README.md installation section, **When** they follow the repository URL to clone the project, **Then** they successfully clone from `github.com/systmms/segnomms` (not broken `your-org` URL)
2. **Given** a developer installs the package, **When** they import it, **Then** they see consistent "SegnoMMS" branding (not "Segno Interactive SVG Plugin")
3. **Given** a developer checks package metadata, **When** they view `__author__` attribute, **Then** it matches pyproject.toml author "SYSTMMS" consistently
4. **Given** a developer follows installation docs, **When** they install for Python 3.14, **Then** the package works correctly and is documented as supported
5. **Given** a developer reads Segno dependency requirements, **When** they check multiple doc sources (README, installation.rst, conf.py), **Then** all sources consistently state "Segno >= 1.5.2"

---

### User Story 2 - Dependency Installation Clarity (Priority: P1)

A developer wants to set up SegnoMMS for development or production use and needs clear, accurate instructions about dependency management, especially understanding the uv-based workflow versus traditional pip installation.

**Why this priority**: Incorrect dependency instructions cause immediate setup failures. Developers following outdated pip extras syntax `[docs,test]` will encounter errors since the project migrated to `[dependency-groups]`.

**Independent Test**: Can be tested by attempting installation following both development and production paths in README.md, verifying uv installation instructions work, and confirming deprecated pip extras are removed.

**Acceptance Scenarios**:

1. **Given** a developer wants to install for production, **When** they follow README.md, **Then** they see clear instructions for `pip install segnomms` with correct Segno >= 1.5.2 requirement
2. **Given** a developer wants to contribute, **When** they read installation.rst, **Then** they see uv installation prerequisites documented before `uv sync` usage
3. **Given** a developer tries to install dev dependencies, **When** they follow current docs, **Then** they use `make setup` or `uv sync` (not broken `pip install segnomms[docs,test]`)
4. **Given** a developer reads README development section, **When** they see dependency references, **Then** no mentions of deprecated `[project.optional-dependencies]` extras exist

---

### User Story 3 - API Usage and Import Path Consistency (Priority: P2)

A developer wants to use SegnoMMS configuration features in their code and needs consistent, working import paths across all documentation examples to successfully integrate the library.

**Why this priority**: Contradictory import paths in examples cause confusion and trial-and-error debugging. Developers waste time figuring out which import syntax actually works, reducing confidence in documentation quality.

**Independent Test**: Can be tested by extracting all import statements from README.md, quickstart.rst, and examples.rst, running them in a test script, and verifying they all work consistently.

**Acceptance Scenarios**:

1. **Given** a developer reads quickstart.rst configuration example, **When** they see import statements, **Then** they use `from segnomms.config import RenderingConfig` (short path)
2. **Given** a developer copies README.md examples, **When** they use AccessibilityConfig imports, **Then** the import path `from segnomms.a11y.accessibility import AccessibilityConfig` is verified to work
3. **Given** a developer follows any documentation example, **When** they copy import statements, **Then** all imports use consistent paths (no mixing of `segnomms.config` vs `segnomms.config.models.core`)

---

### User Story 4 - Contributor Development Workflow (Priority: P2)

A contributor wants to set up their development environment, understand git hooks, and follow the project's development workflow to submit quality pull requests.

**Why this priority**: Incorrect git hook documentation (pre-commit vs Lefthook confusion) causes contributors to set up the wrong tooling, leading to commit failures and frustration. Clear documentation accelerates contributor onboarding.

**Independent Test**: Can be tested by following contributing.rst from scratch on a fresh clone, verifying Lefthook setup works, and confirming all development workflow commands execute successfully.

**Acceptance Scenarios**:

1. **Given** a contributor reads contributing.rst, **When** they set up git hooks, **Then** they install and configure Lefthook (not pre-commit)
2. **Given** a contributor follows development setup, **When** they check available commands, **Then** they're directed to `make help` to discover all Makefile targets
3. **Given** a contributor creates test scripts, **When** they read contributing.rst, **Then** they understand all permanent test scripts must have corresponding Makefile targets for discoverability

---

### User Story 5 - API Reference Completeness (Priority: P2)

A developer needs comprehensive API documentation for all modules, especially the constants module which is frequently used in examples but lacks dedicated API reference documentation.

**Why this priority**: Missing API docs for frequently-referenced modules (constants) force developers to read source code instead of documentation, defeating the purpose of Sphinx auto-generated docs.

**Independent Test**: Can be tested by building Sphinx docs, navigating to API section, and verifying docs/source/api/constants.rst exists with complete documentation for all exported symbols.

**Acceptance Scenarios**:

1. **Given** a developer reads examples using `segnomms.constants`, **When** they navigate to API documentation, **Then** they find docs/source/api/constants.rst with documentation for `ModuleShape`, `TEST_COLORS`, `QR_PAYLOADS`, etc.
2. **Given** a developer searches Sphinx docs for constants, **When** they use the search feature, **Then** all constants module symbols are indexed and discoverable

---

### User Story 6 - Complete Working Examples (Priority: P3)

A developer wants to integrate SegnoMMS into their web application (FastAPI) or test decoder compatibility, and needs complete, working code examples that they can copy and run.

**Why this priority**: Incomplete examples (missing imports, skeleton functions) require developers to guess missing pieces, reducing trust in documentation and increasing time-to-integration.

**Independent Test**: Can be tested by extracting all code examples from documentation, running them as standalone scripts, and verifying they execute without errors and produce expected outputs.

**Acceptance Scenarios**:

1. **Given** a developer reads FastAPI integration example, **When** they copy the code, **Then** all imports are included and the example runs successfully
2. **Given** a developer wants to test decoder compatibility, **When** they find the decoder testing section, **Then** they get a complete working script (not just skeleton comments)
3. **Given** a developer copies any code example, **When** they run it, **Then** it executes successfully without missing dependencies or undefined variables

---

### User Story 7 - Documentation Navigation and Discoverability (Priority: P3)

A developer or contributor needs to navigate documentation easily, find related information through cross-references, and discover comprehensive feature lists for different development phases.

**Why this priority**: Poor navigation and missing cross-references force developers to manually search or grep through documentation, reducing productivity and increasing frustration with the docs.

**Independent Test**: Can be tested by auditing all RST files for cross-references, verifying links work, checking that Phase 4 features are comprehensively documented in one location, and ensuring code blocks have proper syntax highlighting.

**Acceptance Scenarios**:

1. **Given** a developer reads shapes.rst, **When** they see references to other documentation, **Then** those references use proper Sphinx `:doc:` or `:ref:` links for navigation
2. **Given** a developer wants to understand Phase 4 features, **When** they navigate to the Phase 4 section, **Then** they find a comprehensive list of all Phase 4 capabilities in one location
3. **Given** a developer reads code examples, **When** syntax highlighting is rendered, **Then** all code blocks use correct language tags (python, bash, css)
4. **Given** a developer reads safe mode documentation, **When** they want to understand scope, **Then** they find an explicit list of which QR module patterns are protected vs unprotected
5. **Given** a developer reads about error correction levels, **When** they want to understand tradeoffs, **Then** they find a table explaining L/M/Q/H levels with recovery percentages (7%, 15%, 25%, 30%)

---

### User Story 8 - Beta Software Awareness (Priority: P3)

A developer or organization considering SegnoMMS needs clear indication that this is beta software (version 0.1.0b4) to make informed decisions about production use and set appropriate expectations.

**Why this priority**: Without clear beta status warnings, users may assume production-ready stability, leading to unrealistic expectations and potential negative experience when encountering beta-level issues.

**Independent Test**: Can be tested by reading README.md introduction and installation.rst to verify prominent beta status notices exist.

**Acceptance Scenarios**:

1. **Given** a developer lands on README.md, **When** they read the introduction, **Then** they see a clear notice that this is beta software (version 0.1.0b4)
2. **Given** a developer reads installation.rst, **When** they consider installation, **Then** beta status is mentioned with appropriate expectations set

---

### Edge Cases

- What happens when a developer uses an older Python version (3.8)? → Documentation clearly states Python >= 3.9 with support up to 3.14
- How does the system handle docs referencing the old package name? → All references to "Segno Interactive SVG Plugin" and "segno-interactive-svg" are updated to "SegnoMMS"
- What if developer follows outdated Nix environment instructions? → Either complete Nix documentation is provided or incomplete references are removed
- How does documentation handle spec-kit workflow for contributors? → Spec-kit workflow is documented in contributing.rst for developers who want to use spec-driven development
- What happens when visual gallery reference is broken? → Either the shape gallery generator location is clarified or outdated references are removed

## Requirements *(mandatory)*

### Functional Requirements

**Critical Fixes (Issues #2-5):**

- **FR-001**: All documentation files MUST use consistent package name "SegnoMMS" (remove all "Segno Interactive SVG Plugin" references)
- **FR-002**: contributing.rst MUST reference correct repository URL `github.com/systmms/segnomms` (not `your-org/segnomms`)
- **FR-003**: segnomms/__init__.py `__author__` attribute MUST match pyproject.toml author "SYSTMMS"
- **FR-004**: All documentation sources (README.md, installation.rst, conf.py, __init__.py) MUST consistently state Segno version requirement as ">= 1.5.2"

**High Priority Fixes (Issues #6-12):**

- **FR-005**: pyproject.toml classifiers and README.md MUST document Python 3.14 support
- **FR-006**: installation.rst MUST include uv installation prerequisites before documenting `uv sync` usage
- **FR-007**: README.md MUST remove all references to pip extras `[docs,test]` and clarify that uv is required for development dependencies
- **FR-008**: All configuration import examples MUST use consistent short path: `from segnomms.config import RenderingConfig`
- **FR-009**: README.md AccessibilityConfig import path MUST be verified and corrected if incorrect
- **FR-010**: contributing.rst MUST document Lefthook (not pre-commit) for git hooks setup
- **FR-011**: docs/source/api/ MUST include constants.rst with complete API documentation for constants module (ModuleShape, TEST_COLORS, QR_PAYLOADS, DEFAULT_SCALE, DEFAULT_BORDER)

**Medium Priority Enhancements (Issues #13-23):**

- **FR-012**: contributing.rst MUST document spec-kit workflow for spec-driven development
- **FR-013**: All current documentation MUST have zero references to old package name "segno-interactive-svg"
- **FR-014**: Safe mode documentation MUST include explicit list of protected QR module patterns vs unprotected patterns
- **FR-015**: decoder_compatibility.rst MUST include table explaining error correction levels (L=7%, M=15%, Q=25%, H=30%)
- **FR-016**: Documentation MUST provide comprehensive Phase 4 feature reference in one location
- **FR-017**: README.md MUST include "Development Commands" section referencing `make help` for Makefile target discovery
- **FR-018**: Shape gallery documentation MUST either clarify generator script location or remove outdated references
- **FR-019**: Nix development environment documentation MUST either be completed thoroughly or incomplete references removed
- **FR-020**: docs/source/testing/ MUST document performance testing and benchmarking framework
- **FR-021**: examples.rst MUST include complete working FastAPI integration example with all imports
- **FR-022**: decoder_compatibility.rst MUST provide complete working decoder compatibility test script (not skeleton)

**Polish Improvements (Issues #24-28):**

- **FR-023**: All code blocks in RST files MUST have proper language tags for syntax highlighting
- **FR-024**: Documentation MUST use Sphinx cross-references (`:doc:`, `:ref:`) for internal navigation where appropriate
- **FR-025**: CHANGELOG.md MUST have backslash typo fixed (line 18: `### refactor\`)
- **FR-026**: README.md introduction MUST include prominent beta status notice for version 0.1.0b4
- **FR-027**: contributing.rst MUST document test script discoverability policy (all permanent test scripts need Makefile targets)

### Key Entities

- **Documentation File**: Source file containing user-facing or contributor-facing information (README.md, .rst files, pyproject.toml metadata, docstrings)
- **Import Path**: Python import statement pattern used in examples and user code
- **Code Example**: Executable code snippet in documentation that users can copy and run
- **Cross-Reference**: Sphinx link connecting related documentation sections
- **Configuration Model**: Pydantic model imported by users for configuring SegnoMMS behavior

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Zero contradictions exist across all documentation sources (verified by searching for package name, repository URL, author, version requirements)
- **SC-002**: 100% of code examples in documentation execute successfully when extracted and run as standalone scripts
- **SC-003**: New developers can successfully install and import SegnoMMS following README.md instructions in under 5 minutes
- **SC-004**: All API symbols used in documentation examples are documented in docs/source/api/ (verified by cross-referencing examples with API docs)
- **SC-005**: Contributors can set up development environment following contributing.rst in under 10 minutes without encountering incorrect tool references
- **SC-006**: Sphinx documentation builds without warnings or broken cross-references
- **SC-007**: All permanent test scripts have corresponding Makefile targets (verified by comparing scripts/ directory with Makefile)

## SegnoMMS Integration Requirements *(mandatory for SegnoMMS features)*

### Plugin Architecture Compliance
- Feature MUST NOT alter SegnoMMS plugin architecture or runtime behavior
- Documentation fixes are non-code changes with no architectural impact
- Configuration examples MUST continue to demonstrate existing API patterns

### Type Safety Requirements
- Not applicable: Documentation-only changes do not affect type safety
- Import path standardization ensures examples use correct type-safe imports

### Testing Requirements
- MUST verify all code examples execute successfully
- MUST validate Sphinx documentation builds without errors
- MUST check that cross-references resolve correctly
- No visual regression tests needed (no rendering changes)
- No performance tests needed (no code changes)

### Documentation Requirements
- All user-facing documentation changes MUST be in Sphinx/RST format
- README.md changes limited to installation instructions and package metadata
- CHANGELOG.md is excluded (managed by release-please)
- Examples MUST use JSON output validation patterns where applicable

### Quality Gates
- MUST pass all pre-commit hooks (Lefthook)
- Sphinx build MUST complete with zero warnings
- All cross-references MUST resolve
- All code blocks MUST have language tags

### Commercial Standards
- Professional documentation quality appropriate for commercial QR generation service
- Complete API coverage demonstrates enterprise-ready maturity
- Clear installation and contribution guidelines support community growth
- Beta status warnings set appropriate expectations

## Assumptions *(document reasonable defaults)*

### Technology Assumptions
- Uses SegnoMMS existing Sphinx documentation infrastructure
- Follows established documentation policy (Sphinx-first, see CLAUDE.md)
- Leverages existing Lefthook pre-commit hook configuration
- Respects project's three allowed Markdown files policy (README.md, CHANGELOG.md, CLAUDE.md)

### Architecture Assumptions
- Documentation changes do not affect code architecture
- Import paths referenced already exist and work correctly (verification needed)
- Constants module exists and is importable (needs API documentation)
- Spec-kit integration is functional and ready to document

### Quality Assumptions
- Documentation changes are non-breaking
- Existing Sphinx build configuration works correctly
- All code examples can be validated by extraction and execution
- Cross-reference audit can be automated or done manually efficiently
