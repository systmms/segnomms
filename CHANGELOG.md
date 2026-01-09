# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0](https://github.com/systmms/segnomms/compare/v0.1.0...v0.1.0) (2025-08-31)


### ⚠ BREAKING CHANGES

* Removed all Pyodide compatibility features and infrastructure
* None - all changes are additive and backward compatible
* Enum fields now return enum objects instead of strings
* Safe mode now protects fewer module types, allowing more design flexibility while preserving QR code functionality.

### refactor

* remove use_enum_values to enable enum objects at runtime ([f14221c](https://github.com/systmms/segnomms/commit/f14221cd1cee644976ab5750afdf279d32dc3644))


### Features

* add comprehensive project infrastructure ([53f428b](https://github.com/systmms/segnomms/commit/53f428bcb9224a907a6f788e506b6761ca2fd772))
* add comprehensive TypedDict patterns for type-safe **kwargs ([0bf1d7c](https://github.com/systmms/segnomms/commit/0bf1d7c3ba2e49a4c386fb2aa723d16e341d7fd3))
* add discriminated unions for shape-specific configurations ([89fffe2](https://github.com/systmms/segnomms/commit/89fffe27ad7e1ef91707fe19fd258213d3f9b8dd))
* add segnomms QR code plugin with advanced shape rendering ([b210b18](https://github.com/systmms/segnomms/commit/b210b1877cbb04bfcce1fc60af69eb6b15e75262))
* add TypedDict patterns for type-safe **kwargs ([9e79c9f](https://github.com/systmms/segnomms/commit/9e79c9f4a205bd035af913b3f32043da924f7b28))
* complete GitHub Actions script extraction and lefthook integration ([da421bf](https://github.com/systmms/segnomms/commit/da421bf23fe1d3a44ebdddeeb04377c0f306e168))
* complete Pyodide removal from codebase ([f9dd7a9](https://github.com/systmms/segnomms/commit/f9dd7a9ab5977d25e85d8ee77112ef03c428c38b))
* consolidate documentation builds with reusable workflow ([23368df](https://github.com/systmms/segnomms/commit/23368dfa49a5f8eb742efb05d40fcecd2563a56a))
* enhance lefthook with automatic fix staging ([1856098](https://github.com/systmms/segnomms/commit/185609875aaece77c945de0f2cf21be6b90c7587))
* F401 unused imports rule elimination - 80%+ rule reduction achieved ([a2bead2](https://github.com/systmms/segnomms/commit/a2bead2dff39b9f4e9ce339dfd61df45cd56f622))
* hierarchical flake8 config - 90% rule reduction achieved! ([2f4e001](https://github.com/systmms/segnomms/commit/2f4e001485ddde28d40f19dfeaa254e4b9908499))
* implement string-compatible enums with case-insensitive handling ([a646926](https://github.com/systmms/segnomms/commit/a64692674bfc81d83ccbe0f627bfb02151263428))
* integrate MyPy type checking into pre-commit hooks ([9b4dadc](https://github.com/systmms/segnomms/commit/9b4dadce1c4f81aff6943b9b1d0a6d379f090b06))
* migrate from aspell to cspell with comprehensive GitHub Actions testing infrastructure ([0f549a9](https://github.com/systmms/segnomms/commit/0f549a95f296e32e7de9750e80d6a0357429454c))
* optimize GitHub workflows and improve documentation build reliability ([19bb2cf](https://github.com/systmms/segnomms/commit/19bb2cffc8cdb09f87401b6a641aa376349162ee))
* refactor documentation scripts and setup GitHub Pages deployment ([87e3879](https://github.com/systmms/segnomms/commit/87e3879b35fd56b7abf7d99fc2ce40d31606fdcd))
* refine safe mode scope to protect only critical QR patterns ([e3abff9](https://github.com/systmms/segnomms/commit/e3abff9ea69a4e62cf768addc6f1d93ef0742eda))
* remove E226, E712, E501 from flake8 ignore list ([7ad93d8](https://github.com/systmms/segnomms/commit/7ad93d88288611f7c50765b7a138dfaee190a37d))
* remove F821 and F811 from flake8 ignore list ([f1acdc8](https://github.com/systmms/segnomms/commit/f1acdc8150ca7ad652c95f6dca8320d54f3ff97d))
* **types:** implement comprehensive MyPy + Pydantic v2 compatibility ([6563472](https://github.com/systmms/segnomms/commit/6563472d3adac30b1a97baacc2104f5039d55a91))


### Bug Fixes

* accessibility and SVG model type annotations ([2d14833](https://github.com/systmms/segnomms/commit/2d14833ffdf3259217676620ae751646c95e1141))
* add complete type annotations to svg/frame_visual.py ([fc05e04](https://github.com/systmms/segnomms/commit/fc05e041cf4a75e0e53cbe8b5a2161b36dc39b87))
* add explicit __str__ methods to all enums for correct string representation ([10e30d8](https://github.com/systmms/segnomms/commit/10e30d82406db51455db4852c07bd5377718d5c8))
* add missing myst-parser dependency for documentation builds ([2e17167](https://github.com/systmms/segnomms/commit/2e1716736f2e75c905b3f2ae44c0a7fe0436f62a))
* add missing skip for rounded shape decoder compatibility issue ([f6cd497](https://github.com/systmms/segnomms/commit/f6cd4975283809347b7383c904bae3d0a0bd6051))
* address remaining GitHub Actions failures and optimize CI pipeline ([2b2dc62](https://github.com/systmms/segnomms/commit/2b2dc6222a2ac0cf1d240f3834a6411cc3be461a))
* complete type annotations for shapes/basic.py (71 → 0 errors) ([cc24347](https://github.com/systmms/segnomms/commit/cc24347c218d1d5bf30e8d2b780c17847911a5a4))
* comprehensive cleanup of project-wide linting and formatting violations ([e283030](https://github.com/systmms/segnomms/commit/e2830306b8a141ed10784b27cf044c8c9396af01))
* comprehensive GitHub Actions failure remediation ([d68ddff](https://github.com/systmms/segnomms/commit/d68ddff95ab9e918547c6d9b60a09ea711854239))
* correct MyPy python_version configuration ([0509e10](https://github.com/systmms/segnomms/commit/0509e10a111a10f6b24fe8719885aa2faef8588e))
* critical MyPy type annotation and enum assertion fixes ([c763f3f](https://github.com/systmms/segnomms/commit/c763f3fffc5a0c30aaf3c449094af3620ff6335d))
* ensure docs workflow uses uv environment for build commands ([51d8829](https://github.com/systmms/segnomms/commit/51d8829f711ec474bc0a46ba90d0ae39f28c688f))
* major progress on test enum assertions - 95.5% pass rate ([7a0d021](https://github.com/systmms/segnomms/commit/7a0d0219dbaf5dc65848d58438146590512fc3f3))
* merge legacy types with new TypedDict patterns ([0db831b](https://github.com/systmms/segnomms/commit/0db831b40e99abe425c585d00505c2871624f482))
* migrate documentation deployment to modern GitHub Actions Pages method ([0514fdf](https://github.com/systmms/segnomms/commit/0514fdf652416be946c271c8c0cdf21b9616eaae))
* remove .value usage from enum comparisons for Pydantic v2 ([25f59a6](https://github.com/systmms/segnomms/commit/25f59a62b2aeedff6e9c1d32e529948d1e53bca2))
* remove invalid 'pure = true' from project.urls section ([f945ba0](https://github.com/systmms/segnomms/commit/f945ba0526f77b1010f2c2870379434e922a377e))
* resolve 18 MyPy errors in core matrix processing modules ([49c18e5](https://github.com/systmms/segnomms/commit/49c18e518f45186030c3a20469ab545541be8d94))
* resolve 28 MyPy errors in core/performance.py and plugin/rendering.py ([6133426](https://github.com/systmms/segnomms/commit/6133426ef0e9f9142cd66306f2dcaf8dc1b9bf5a))
* resolve 8 critical GitHub Actions failures + extract scripts to repo/ ([86a46a5](https://github.com/systmms/segnomms/commit/86a46a5ce4dddfce0a0e48544127ed85b923f2f4))
* resolve actionlint validation issues + optimize workflow triggers ([0e2c44b](https://github.com/systmms/segnomms/commit/0e2c44bad81f8ad8d63d6ecc4334270071c16139))
* resolve critical flake8 violations (Priority 1) ([940f2ca](https://github.com/systmms/segnomms/commit/940f2ca7947ac6141a87a2ba870a4dab94638f10))
* resolve critical GitHub Actions failures + adjust memory test thresholds ([8338d3b](https://github.com/systmms/segnomms/commit/8338d3be1672d4adc84a6147faed6de21b7c2ba5))
* resolve critical GitHub Actions failures and restore CI/CD pipeline ([f5f501a](https://github.com/systmms/segnomms/commit/f5f501afb2285942347224e732785ed3d2b44f10))
* resolve F541 violations and improve performance monitoring ([d9b6053](https://github.com/systmms/segnomms/commit/d9b6053e59f8f01991176807ee2e956d3da2fcf2))
* resolve GitHub Actions payload validation failures ([80b62a2](https://github.com/systmms/segnomms/commit/80b62a2db93a95c5c1fedfadf93f8eca1fd66095))
* resolve GitHub Actions workflow failures ([8e13e05](https://github.com/systmms/segnomms/commit/8e13e053d0aa15715a2ac3b7a2dcf6b97dbf0d94))
* resolve performance test failures and configuration issues ([29f277e](https://github.com/systmms/segnomms/commit/29f277e26a5752579235e904452cfe4f6916f67f))
* resolve Priority 2 style violations (E226, E712) ([45ca011](https://github.com/systmms/segnomms/commit/45ca0115b9ae6d39151b925a707bbbea145160a2))
* resolve remaining GitHub Actions test failures ([72c6ed7](https://github.com/systmms/segnomms/commit/72c6ed7004970baf60de3c8d6b9a47bea08b03cb))
* update deploy script for Hatchling dynamic versioning ([9087bcd](https://github.com/systmms/segnomms/commit/9087bcdfa589c61b5ddadc7b0e83786c341e13bd))


### Performance Improvements

* implement comprehensive caching for GitHub Actions workflows ([f1ba0c1](https://github.com/systmms/segnomms/commit/f1ba0c106673143548b9a45b6dc0eceeef6f97eb))


### Documentation

* add development context and project documentation ([370f903](https://github.com/systmms/segnomms/commit/370f9036d73f7db95493696fc29f4a28aa640dad))
* add validation test file with intentional typo ([5221b6e](https://github.com/systmms/segnomms/commit/5221b6e51920f96ac536d0fd7f144302656983b4))
* adding missing sphinx/docs requirements ([7ba4a58](https://github.com/systmms/segnomms/commit/7ba4a58b7d136098c8f985dcb80279f6cb78be07))
* document successful Pydantic v2 + MyPy modernization achievement ([1ca11d2](https://github.com/systmms/segnomms/commit/1ca11d2a1bfce08c166324fafad466023b1f3f51))
* **rtd,sphinx:** fix RTD build, enable linkify, and resolve Sphinx warnings ([a0b47a4](https://github.com/systmms/segnomms/commit/a0b47a4035b7a47cf8e335124566d789aedfca1c))


### Styles

* automated code formatting with black and isort ([0e9db00](https://github.com/systmms/segnomms/commit/0e9db0016b7e6ca7f9a9b4726bdf8f742f37b09d))


### Miscellaneous Chores

* release 0.1.0 ([6c14158](https://github.com/systmms/segnomms/commit/6c14158137b24a77a9f748f1aff20456d551c368))
* remove test commit hook file ([f948d83](https://github.com/systmms/segnomms/commit/f948d83ac3d646da25c67ac0abc19d8cc13d5282))
* sync version to beta registry ([97c3b7c](https://github.com/systmms/segnomms/commit/97c3b7cba6fb2ca19b935edbc4647d42294506a9))
* update development environment configuration ([8f03443](https://github.com/systmms/segnomms/commit/8f03443a270596905c07b257c5f0e3a79e8683b0))
* updating CLAUDE.md based on the repository state ([fd4f585](https://github.com/systmms/segnomms/commit/fd4f5852a44293da5319c57815d96f4d1f974381))


### Code Refactoring

* major F841 reduction - systematic validation enhancements ([e73add6](https://github.com/systmms/segnomms/commit/e73add6ccb7984152b4cb4c7f9a7fcdd5ad1117f))
* reorganize flake8 configuration for systematic rule reduction ([2b78328](https://github.com/systmms/segnomms/commit/2b783284e2d9ede78eefc0c84b606977d541bbc4))
* reorganize plugin architecture and module imports ([b92d5e2](https://github.com/systmms/segnomms/commit/b92d5e2f93fa25954ca7b773455e51bd2837832f))
* strategic F841 enhancement phase - validation assertions added ([822d735](https://github.com/systmms/segnomms/commit/822d73597ef7af12c6cdea424eb3c0b333a7fd0b))
* strategic F841 improvements - add validation assertions ([8d560ad](https://github.com/systmms/segnomms/commit/8d560ad38ccbc0129c19fbcbc321d55c90e7446b))


### Tests

* add commit hook testing file ([5c389d5](https://github.com/systmms/segnomms/commit/5c389d5860b193ebd90c2627111b39a7a2d35a84))
* fix visual regression test infrastructure and update baselines ([ee6d4a3](https://github.com/systmms/segnomms/commit/ee6d4a3d19d18defc0c818456b899d4e225a9396))


### Build System

* upgrade Pydantic to v2.7+ with MyPy integration ([afaf2aa](https://github.com/systmms/segnomms/commit/afaf2aa3cd6040a074a2f7717fa88b75b44874ad))


### Continuous Integration

* disabling the build minutes user until repository is stable ([18462fa](https://github.com/systmms/segnomms/commit/18462fa4320dba61805ae9b6bdce69519162b0b0))
* extract remaining multi-line scripts from GitHub Actions to repo/ ([9d8c9cf](https://github.com/systmms/segnomms/commit/9d8c9cf165f532fcae2332529082f48aa0ee519f))
* **lefthook:** avoid git index.lock by removing manual 'git add' in end-of-file hook ([5e2f280](https://github.com/systmms/segnomms/commit/5e2f2803b77dbf20911d9f8218b47b82effcda9a))
* **lefthook:** ensure sequential pre-commit hooks; rely on stage_fixed for staging ([1034fe7](https://github.com/systmms/segnomms/commit/1034fe785f344eb414012fa7600da43d78bc2ca3))
* **lefthook:** run hooks sequentially to prevent concurrent staging (index.lock) ([561f858](https://github.com/systmms/segnomms/commit/561f858a2b350c2bb679fe43970270054ebf2f73))
* making bandit security/command exist 0 ([1f51428](https://github.com/systmms/segnomms/commit/1f51428a4530ed05c0427ff1a3414747cd7f3299))
* **security:** add Bandit results summary to step summary\n\n- Parse bandit-report.json and write markdown tables to \n- Include severity counts and top 10 findings; keep artifact upload on failures ([4b8adbf](https://github.com/systmms/segnomms/commit/4b8adbffeefa97c920e8cc0938e8e5118f21f2b8))
* **security:** extract Bandit summary into repo script and invoke from CI\n\n- Add repo/summarize_security_scan.py for reusable step summary generation\n- Update workflow to call the script with --report bandit-report.json ([00efcb5](https://github.com/systmms/segnomms/commit/00efcb59824d14d5be08e46b3dd30c07e10caf42))
* **test-wheel:** install and test local wheel instead of PyPI; harden install script ([8a39e34](https://github.com/systmms/segnomms/commit/8a39e3415a113a7b34cf535a88d6fbe456bc92a1))
* **test-wheel:** use dark='blue' in PyPI functionality test and skip wait\n\n- Replace deprecated 'fill' kwarg to match plugin API\n- Add --no-wait to wheel job step to speed local act runs ([cc477b9](https://github.com/systmms/segnomms/commit/cc477b953f3fcc5cd483857a4b3200e11671495d))

## [0.1.0-beta] - 2025-08-26

### Added
- Initial release of SegnoMMS
- Custom shape support: square, circle, rounded, dot, diamond, hexagon, star, cross, and more
- Connected module patterns for flowing QR code designs
- Safe mode for ensuring QR code scannability
- Interactive SVG features with CSS classes and hover effects
- Support for different shapes per QR component (finder patterns, data modules, etc.)
- Comprehensive test suite with visual regression testing
- Full documentation with examples
- Complete Pydantic v2 integration with strict MyPy compliance across 67 modules
- Modern enum object handling with discriminated unions for shape configurations
- TypedDict patterns for type-safe **kwargs usage in shape renderers
- Comprehensive error handling with structured exceptions
- Intent-based API with graceful degradation
- Capability discovery system
- Performance monitoring and memory leak detection
- Visual regression testing framework

### Changed
- Renamed from segno-interactive-svg to segnomms
- Updated author information to SYSTMMS
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

[0.1.0]: https://github.com/systmms/segnomms/releases/tag/v0.1.0
[0.1.0-beta]: https://github.com/systmms/segnomms/releases/tag/v0.1.0-beta
