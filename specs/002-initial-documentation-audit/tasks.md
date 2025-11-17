# Tasks: Initial Documentation Audit

**Input**: Design documents from `/specs/002-initial-documentation-audit/`
**Prerequisites**: plan.md, spec.md, quickstart.md

**Tests**: Not requested in specification - documentation validation only
**Organization**: Tasks grouped by user story to enable independent implementation and testing

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

SegnoMMS plugin structure:
- Root level: `README.md`, `pyproject.toml`
- Documentation: `docs/source/` (Sphinx/RST)
- Python source: `segnomms/`

---

## Phase 1: Setup (Validation Infrastructure)

**Purpose**: Create validation scripts for documentation fixes

- [X] T001 Create contradiction check script in `scripts/check_doc_contradictions.sh`
- [X] T002 [P] Create code example extraction script in `scripts/extract_code_examples.py`
- [X] T003 [P] Create comprehensive validation script in `scripts/verify_documentation_fixes.py`

---

## Phase 2: Foundational (No Blocking Prerequisites)

**Purpose**: N/A - Documentation feature has no foundational blocking tasks

**Note**: This phase is empty for documentation-only features. Proceed directly to user story implementation.

---

## Phase 3: User Story 1 - New Developer Installation Success (Priority: P1) 🎯 MVP

**Goal**: Fix critical contradictions that block installation or cause immediate user confusion

**Independent Test**: Follow README.md installation on fresh environment, verify correct repository clone, consistent package naming, and successful import

### Implementation for User Story 1

- [X] T004 [P] [US1] Fix package name in `docs/source/index.rst` - replace "Segno Interactive SVG Plugin" with "SegnoMMS"
- [X] T005 [P] [US1] Fix repository URL in `docs/source/contributing.rst` - change `your-org/segnomms` to `systmms/segnomms`
- [X] T006 [P] [US1] Fix author attribution in `segnomms/__init__.py` - change `__author__` from "QRCodeMMS" to "SYSTMMS"
- [X] T007 [P] [US1] Fix Segno version in `docs/source/installation.rst` - ensure states ">= 1.5.2"
- [X] T008 [P] [US1] Fix Segno version in `README.md` - ensure states ">= 1.5.2"
- [X] T009 [P] [US1] Fix Segno version in `docs/source/conf.py` - ensure consistent ">= 1.5.2" reference
- [X] T010 [P] [US1] Fix Segno version in `segnomms/__init__.py` - update docstring to state ">= 1.5.2"
- [X] T011 [US1] Validate contradiction fixes using `scripts/check_doc_contradictions.sh`

**Checkpoint**: Critical fixes complete - users can now find package, clone repo, and see consistent naming

---

## Phase 4: User Story 2 - Dependency Installation Clarity (Priority: P1)

**Goal**: Clear, accurate dependency management instructions for both development and production

**Independent Test**: Attempt installation following both dev and production paths in README.md, verify uv instructions work, confirm no pip extras references

### Implementation for User Story 2

- [X] T012 [P] [US2] Add Python 3.14 classifier to `pyproject.toml` - add "Programming Language :: Python :: 3.14"
- [X] T013 [P] [US2] Document Python 3.14 support in `README.md` features section
- [X] T014 [P] [US2] Add uv installation prerequisites to `docs/source/installation.rst` before uv sync documentation
- [X] T015 [P] [US2] Remove pip extras `[docs,test]` references from `README.md` development section
- [X] T016 [P] [US2] Clarify uv requirement for dev dependencies in `README.md`
- [X] T017 [US2] Test fresh installation following updated README.md instructions

**Checkpoint**: Dependency instructions clear - developers know exactly how to install for dev/production

---

## Phase 5: User Story 3 - API Usage and Import Path Consistency (Priority: P2)

**Goal**: Consistent, working import paths across all documentation examples

**Independent Test**: Extract all import statements from docs, run them in test script, verify all work consistently

### Implementation for User Story 3

- [X] T018 [P] [US3] Standardize RenderingConfig import in `docs/source/quickstart.rst` to `from segnomms.config import RenderingConfig`
- [X] T019 [P] [US3] Standardize RenderingConfig import in `README.md` to `from segnomms.config import RenderingConfig`
- [X] T020 [P] [US3] Verify AccessibilityConfig import path in `README.md` - test `from segnomms.a11y.accessibility import AccessibilityConfig`
- [X] T021 [P] [US3] Fix AccessibilityConfig import if incorrect in `README.md`
- [X] T022 [US3] Extract and test all import statements using `scripts/extract_code_examples.py`

**Checkpoint**: Import paths consistent - developers can copy examples without trial-and-error

---

## Phase 6: User Story 4 - Contributor Development Workflow (Priority: P2)

**Goal**: Clear development environment setup and git hooks documentation

**Independent Test**: Follow contributing.rst from scratch, verify Lefthook setup works, confirm dev workflow commands execute

### Implementation for User Story 4

- [X] T023 [P] [US4] Document Lefthook setup in `docs/source/contributing.rst` - replace pre-commit references
- [X] T024 [P] [US4] Add `make help` reference to `docs/source/contributing.rst` for Makefile target discovery
- [X] T025 [P] [US4] Document test script discoverability policy in `docs/source/contributing.rst` - permanent scripts need Makefile targets
- [X] T026 [US4] Verify Lefthook installation instructions work

**Checkpoint**: Contributor workflow clear - new contributors can set up environment without confusion

---

## Phase 7: User Story 5 - API Reference Completeness (Priority: P2)

**Goal**: Complete API documentation for constants module

**Independent Test**: Build Sphinx docs, navigate to API section, verify constants.rst exists with all symbols documented

### Implementation for User Story 5

- [X] T027 [US5] Create `docs/source/api/constants.rst` with Sphinx autodoc directives
- [X] T028 [US5] Document ModuleShape enum in `docs/source/api/constants.rst`
- [X] T029 [US5] Document TEST_COLORS constant in `docs/source/api/constants.rst`
- [X] T030 [US5] Document QR_PAYLOADS constant in `docs/source/api/constants.rst`
- [X] T031 [US5] Document DEFAULT_SCALE constant in `docs/source/api/constants.rst`
- [X] T032 [US5] Document DEFAULT_BORDER constant in `docs/source/api/constants.rst`
- [X] T033 [US5] Add constants module reference to `docs/source/api/index.rst`
- [X] T034 [US5] Build Sphinx docs and verify constants module appears in API section

**Checkpoint**: Constants module fully documented - developers can find all symbols in API reference

---

## Phase 8: User Story 6 - Complete Working Examples (Priority: P3)

**Goal**: Complete, executable code examples for FastAPI integration and decoder testing

**Independent Test**: Extract examples from docs, run as standalone scripts, verify they execute without errors

### Implementation for User Story 6

- [X] T035 [P] [US6] Add complete FastAPI integration example to `docs/source/examples.rst` with all imports
- [X] T036 [P] [US6] Add complete decoder compatibility test script to `docs/source/decoder_compatibility.rst`
- [X] T037 [US6] Test FastAPI example extracts and runs successfully
- [X] T038 [US6] Test decoder test script extracts and runs successfully

**Checkpoint**: Examples work - developers can copy and run code successfully

---

## Phase 9: User Story 7 - Documentation Navigation and Discoverability (Priority: P3)

**Goal**: Easy navigation via cross-references, comprehensive feature lists, proper syntax highlighting

**Independent Test**: Audit RST files for cross-references, verify links work, check Phase 4 features documented, ensure code blocks have language tags

### Implementation for User Story 7

- [X] T039 [P] [US7] Add Sphinx cross-references to `docs/source/shapes.rst` using `:doc:` and `:ref:`
- [X] T040 [P] [US7] Document safe mode scope in `docs/source/shapes.rst` - explicit list of protected vs unprotected patterns
- [X] T041 [P] [US7] Add ECC level table to `docs/source/decoder_compatibility.rst` (L=7%, M=15%, Q=25%, H=30%)
- [X] T042 [P] [US7] Create comprehensive Phase 4 feature reference in one location (choose appropriate RST file)
- [X] T043 [P] [US7] Fix or remove shape gallery references in `docs/source/shapes.rst`
- [X] T044 [P] [US7] Fix or remove Nix environment references in `README.md`
- [X] T045 [P] [US7] Document performance testing framework in `docs/source/testing/` (create directory if needed)
- [X] T046 [P] [US7] Audit code blocks in all RST files for proper language tags (python, bash, css)
- [X] T047 [US7] Validate cross-references resolve using `python repo/validate_docs_references.py`

**Checkpoint**: Navigation improved - developers can find related docs and understand all features

---

## Phase 10: User Story 8 - Beta Software Awareness (Priority: P3)

**Goal**: Clear beta status warnings to set appropriate expectations

**Independent Test**: Read README.md intro and installation.rst to verify prominent beta notices exist

### Implementation for User Story 8

- [X] T048 [P] [US8] Add beta status notice to `README.md` introduction section
- [X] T049 [P] [US8] Add beta status notice to `docs/source/installation.rst`
- [X] T050 [US8] Verify beta notices are prominent and clear

**Checkpoint**: Beta status clear - users have appropriate expectations

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Improvements affecting multiple user stories and final documentation cleanup

- [X] T051 [P] Document spec-kit workflow in `docs/source/contributing.rst`
- [X] T052 [P] Remove all "segno-interactive-svg" references from documentation (comprehensive grep)
- [X] T053 [P] Add "Development Commands" section to `README.md` referencing `make help`
- [X] T054 [P] Fix CHANGELOG.md backslash typo on line 18 (`### refactor\` → `### refactor`)
- [X] T055 [P] Final audit of code block language tags across all RST files
- [X] T056 [P] Final audit of Sphinx cross-references across all RST files
- [X] T057 Build Sphinx documentation and verify zero warnings: `make docs 2>&1 | grep -i warning`
- [X] T058 Run comprehensive validation script: `python scripts/verify_documentation_fixes.py`
- [X] T059 Verify all 27 functional requirements (FR-001 through FR-027) addressed
- [X] T060 Verify all 7 success criteria (SC-001 through SC-007) met

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **User Stories (Phase 3-10)**: No dependencies between stories - all can proceed in parallel
- **Polish (Phase 11)**: Depends on all user stories being complete

### User Story Dependencies

All user stories are **INDEPENDENT** and can be implemented in parallel:

- **User Story 1 (P1)**: Critical fixes - no dependencies
- **User Story 2 (P1)**: Dependency clarity - no dependencies
- **User Story 3 (P2)**: Import paths - no dependencies
- **User Story 4 (P2)**: Contributor workflow - no dependencies
- **User Story 5 (P2)**: API docs - no dependencies
- **User Story 6 (P3)**: Examples - no dependencies
- **User Story 7 (P3)**: Navigation - no dependencies
- **User Story 8 (P3)**: Beta notices - no dependencies

### Within Each User Story

- Most tasks within each story marked [P] can run in parallel (different files)
- Final validation task in each story depends on implementation tasks

### Parallel Opportunities

- **ALL user stories can proceed simultaneously** (if team capacity allows)
- Within each story, almost all tasks are parallelizable (different files)
- Setup phase tasks (T001-T003) can all run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all critical fixes together (all different files):
Task: "Fix package name in docs/source/index.rst"
Task: "Fix repository URL in docs/source/contributing.rst"
Task: "Fix author attribution in segnomms/__init__.py"
Task: "Fix Segno version in docs/source/installation.rst"
Task: "Fix Segno version in README.md"
Task: "Fix Segno version in docs/source/conf.py"
Task: "Fix Segno version in segnomms/__init__.py"
```

---

## Parallel Example: User Story 5

```bash
# Create all constants documentation sections together:
Task: "Document ModuleShape enum in docs/source/api/constants.rst"
Task: "Document TEST_COLORS constant in docs/source/api/constants.rst"
Task: "Document QR_PAYLOADS constant in docs/source/api/constants.rst"
Task: "Document DEFAULT_SCALE constant in docs/source/api/constants.rst"
Task: "Document DEFAULT_BORDER constant in docs/source/api/constants.rst"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only - Both P1)

1. Complete Phase 1: Setup (validation scripts)
2. Complete Phase 3: User Story 1 (critical fixes)
3. Complete Phase 4: User Story 2 (dependency clarity)
4. **STOP and VALIDATE**: Test installation from scratch
5. Can deploy/release if both P1 stories working

### Incremental Delivery

1. Complete Setup → Validation infrastructure ready
2. Add User Story 1 → Test independently → Critical fixes working
3. Add User Story 2 → Test independently → Full P1 complete
4. Add User Stories 3-5 (all P2) → Test independently → High priority complete
5. Add User Stories 6-8 (all P3) → Test independently → All enhancements complete
6. Polish phase → Final validation → Feature complete

### Parallel Team Strategy

With multiple developers:

1. One developer: Setup phase (T001-T003)
2. Once setup complete:
   - Developer A: User Story 1 (T004-T011)
   - Developer B: User Story 2 (T012-T017)
   - Developer C: User Story 3 (T018-T022)
   - Developer D: User Story 4 (T023-T026)
   - Developer E: User Story 5 (T027-T034)
3. Continue parallel work through all user stories
4. Team converges on Polish phase

---

## Validation Checkpoints

### After Each User Story

Run story-specific validation from quickstart.md:

- **US1**: `scripts/check_doc_contradictions.sh` - verify zero contradictions
- **US2**: Fresh install test following README.md
- **US3**: `scripts/extract_code_examples.py` - verify all imports work
- **US4**: Follow contributing.rst from scratch
- **US5**: `make docs` and check API section
- **US6**: Extract and run examples
- **US7**: `python repo/validate_docs_references.py`
- **US8**: Review README.md and installation.rst intro

### Final Validation (Phase 11)

```bash
# Comprehensive validation
python scripts/verify_documentation_fixes.py

# Sphinx build (zero warnings)
make docs 2>&1 | tee build.log
grep -i "warning\|error" build.log

# Cross-reference validation
python repo/validate_docs_references.py

# Success criteria verification
# SC-001: Zero contradictions ✓
# SC-002: 100% examples work ✓
# SC-003: Install time <5min ✓
# SC-004: All API symbols documented ✓
# SC-005: Dev setup time <10min ✓
# SC-006: Sphinx builds without warnings ✓
# SC-007: All test scripts have Makefile targets ✓
```

---

## Commit Strategy

Group by priority for reviewability:

```bash
# Commit 1: Setup
git add scripts/
git commit -m "docs: add validation scripts for documentation audit"

# Commit 2: User Story 1 (Critical)
git add docs/source/index.rst docs/source/contributing.rst segnomms/__init__.py docs/source/installation.rst README.md docs/source/conf.py
git commit -m "docs(critical): fix contradictions (package name, repo URL, author, Segno version)"

# Commit 3: User Story 2 (Critical)
git add pyproject.toml README.md docs/source/installation.rst
git commit -m "docs(critical): add Python 3.14 support, clarify uv dependency workflow"

# Commit 4: User Stories 3-5 (High Priority)
git add docs/source/quickstart.rst README.md docs/source/contributing.rst docs/source/api/
git commit -m "docs(high): fix import paths, update contributor workflow, add constants API docs"

# Commit 5: User Stories 6-8 (Medium Priority)
git add docs/source/examples.rst docs/source/decoder_compatibility.rst docs/source/shapes.rst docs/source/testing/ README.md docs/source/installation.rst
git commit -m "docs(medium): add complete examples, improve navigation, add beta notices"

# Commit 6: Polish
git add docs/source/ README.md CHANGELOG.md
git commit -m "docs(polish): add spec-kit workflow, cross-references, code block tags"
```

---

## Notes

- **[P] tasks**: Different files, no dependencies - can run in parallel
- **[Story] label**: Maps task to specific user story for traceability
- **All 8 user stories are independently completable and testable**
- **Most tasks are parallelizable** - documentation files rarely conflict
- Commit after each user story or logical group
- Stop at any checkpoint to validate story independently
- Feature has **60 total tasks** covering all **27 functional requirements**
- **No tests** to write - validation via Sphinx build and example execution
