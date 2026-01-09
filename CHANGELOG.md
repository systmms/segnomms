# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0](https://github.com/systmms/segnomms/compare/v0.1.0...v1.0.0) (2026-01-09)


### ⚠ BREAKING CHANGES

* **deps:** Minimum Python version is now 3.10

### Features

* add public constants module for user-facing documentation ([c30f019](https://github.com/systmms/segnomms/commit/c30f019347f7617fc419b7dc60c412ddc1cf97a6))
* **deps:** drop Python 3.9, add Python 3.14, upgrade dev tools ([b5929d5](https://github.com/systmms/segnomms/commit/b5929d55f6ea4f8f88f3133581c01b8c3327615c))
* integrate GitHub Spec-Kit and validate basic module shapes ([a7832fc](https://github.com/systmms/segnomms/commit/a7832fc6b4e584653b8ba47bb1e3efdad65a7a97))
* integrate GitHub Spec-Kit for spec-driven development ([4a030e2](https://github.com/systmms/segnomms/commit/4a030e2a7f42e27953201ae84839d4f555dd34bd))


### Bug Fixes

* **ci:** resolve conventional commits validation script logging bug ([2cd251c](https://github.com/systmms/segnomms/commit/2cd251c3517a9d2b0f774ec984c443f48e93a080))
* **ci:** resolve package validation and deprecated UV configuration issues ([4a3d792](https://github.com/systmms/segnomms/commit/4a3d792d9fcb32b14db50721bbe51cf3c0717a37))
* **ci:** resolve Windows PowerShell bash syntax error in dependency installation ([a5d6554](https://github.com/systmms/segnomms/commit/a5d6554a85da2a2a4306e528488056ced2f4c315))
* **ci:** resolve Windows-specific test failures across multiple test suites ([11ab0d7](https://github.com/systmms/segnomms/commit/11ab0d7d4a9752cacc2b555b99f926b7a2eaa962))
* **ci:** skip PNG visual regression tests on Windows ([3e87309](https://github.com/systmms/segnomms/commit/3e8730999effb32ee35b73dc32505d8ab9500024))
* correct log output in conventional commits validation script ([a577fa7](https://github.com/systmms/segnomms/commit/a577fa7f3b693ebb67e6f4493b900334f6fc5ce0))
* **docs:** correct validate_docs_references.py path in tasks.md ([b10b0b5](https://github.com/systmms/segnomms/commit/b10b0b585081950293d0f37578d1581ae765be2b))
* **docs:** correct validation scripts and non-existent constant references ([de031da](https://github.com/systmms/segnomms/commit/de031da8d3c8e6dd3bc543a12932a269a88a3c94))
* **docs:** correct validation scripts and non-existent constant references ([912903f](https://github.com/systmms/segnomms/commit/912903fee285ce66f78e448a6d5c0d139a4aa6bf))
* **docs:** prevent visual-gallery.rst from showing as modified after docs build ([b8b0b16](https://github.com/systmms/segnomms/commit/b8b0b163096901e046f34eda54a6d58ce3d6e64d))
* **naming:** address PR review feedback from Copilot and Gemini ([6997d57](https://github.com/systmms/segnomms/commit/6997d5788ef48c66360e229d0642a762c034a476))
* resolve CI installation and validation failures ([82dee7e](https://github.com/systmms/segnomms/commit/82dee7efcf6f41f5b3d934e240475057df784a4e))
* resolve CI workflow configuration errors ([399428f](https://github.com/systmms/segnomms/commit/399428fc036f44f48b1c44896e5971ae2041ff9c))
* resolve CI/CD workflow failures and optimize performance ([20093a9](https://github.com/systmms/segnomms/commit/20093a9b136a679e891e1ecd01b803019ed3eadf))
* resolve CI/CD workflow failures and optimize performance ([bf6e84d](https://github.com/systmms/segnomms/commit/bf6e84dd8011b71c36a81be5bcb959bcdda1e6b6))
* resolve documentation display and formatting issues ([bd265c4](https://github.com/systmms/segnomms/commit/bd265c494eef229d48e0b16b3def721154b0bf01))
* **security:** prevent code injection in spec-kit markdown validation ([d46c5ab](https://github.com/systmms/segnomms/commit/d46c5ab9b3a8cf776bd138884058180630126070))
* **tests:** check for actual QR decoding libraries before scanability tests ([856d8f5](https://github.com/systmms/segnomms/commit/856d8f57b167d3e9d2deb79ee21ed88933ab8088))
* **tests:** update integration test imports for internal plugin functions ([ee898fd](https://github.com/systmms/segnomms/commit/ee898fd894a41d1453f03c7d2758903a8a4ee1b4))
* **tests:** update plugin internal function imports in test_plugin_core ([59f6d55](https://github.com/systmms/segnomms/commit/59f6d552ae509d11adf0d08a5ff0d5706c355c26))
* **tests:** use realistic values in composition validator tests ([ddb0988](https://github.com/systmms/segnomms/commit/ddb0988ea9f30422805df5709361df4071ef4af5))


### Documentation

* add auto-generated visual gallery from test baselines ([2004b81](https://github.com/systmms/segnomms/commit/2004b81a8f8e36b56bb4f3e899af970eff233cd7))
* add comprehensive Phase 4 compatibility guidance and cross-links ([4b967c5](https://github.com/systmms/segnomms/commit/4b967c5cd644f6280244fae0163ba1cacd7d60c3))
* add spec-kit analysis for basic module shapes feature ([7f29f99](https://github.com/systmms/segnomms/commit/7f29f99e568347c19e3c2d10be49fa7a5b589c51))
* add trailing newline to visual-gallery.rst ([7179022](https://github.com/systmms/segnomms/commit/7179022f17fc4e0c5316417410039d9d71a35385))
* add trailing newline to visual-gallery.rst ([ff998a3](https://github.com/systmms/segnomms/commit/ff998a388adf9509e429e0b3ef7e9140262b5523))
* add trailing newline to visual-gallery.rst ([689fe8a](https://github.com/systmms/segnomms/commit/689fe8a792d7cd7577eca19290e8274b9bec28d8))
* add validation scripts for documentation audit ([9f0c881](https://github.com/systmms/segnomms/commit/9f0c88126760453b8d71b310a84a64a8aa268b53))
* comprehensive documentation audit with 27 fixes across 8 user stories ([cc18c5c](https://github.com/systmms/segnomms/commit/cc18c5c42be1223af5885d862c48e41c4594a304))
* **critical:** add Python 3.14 support and clarify uv dependency workflow ([224a017](https://github.com/systmms/segnomms/commit/224a01705dce22f8905dc3fed87ae9f2d937dd7d))
* **critical:** fix contradictions in package name, repo URL, author, and Segno version ([e29b85a](https://github.com/systmms/segnomms/commit/e29b85aee48e00abf543b6a36e56abd3792bc25e))
* enhance parameter reference with ranges and quick lookup ([62c8725](https://github.com/systmms/segnomms/commit/62c8725d96f86d47f40038fa0716dd4f645d199a))
* fix intent examples, align reqs, add docstrings, reduce Sphinx warnings ([e955721](https://github.com/systmms/segnomms/commit/e955721ff3036b8772d218eb21d10f781f4d2bb3))
* fix invalid type annotation any to Any ([8a2a49a](https://github.com/systmms/segnomms/commit/8a2a49a45d2f1209b711977dc308345bc1eb28fa))
* fix Python version and improve README compatibility ([19cebe7](https://github.com/systmms/segnomms/commit/19cebe7c340275c1822e289a5436bfc531e6cf96))
* **high:** add complete constants module API documentation ([ce7e6d0](https://github.com/systmms/segnomms/commit/ce7e6d040045f47d726eafd646e6d2f652e55991))
* **high:** document Lefthook workflow and test script discoverability ([fd26728](https://github.com/systmms/segnomms/commit/fd26728b6ff42aafadc70148f8691a5836c6551f))
* **ideas:** add project naming consistency review backlog ([951ff14](https://github.com/systmms/segnomms/commit/951ff141e804277d0b95952f9271f0eca9660e14))
* improve documentation display and formatting ([bbd060f](https://github.com/systmms/segnomms/commit/bbd060ffffb6fea1958db4ede6a4bb0fcaf0f317))
* **makefile:** fix package name and add docs-validate target ([af59059](https://github.com/systmms/segnomms/commit/af59059a433b798a2039779f23db842b7fb31836))
* **medium:** add complete working examples for FastAPI and decoder testing ([57a8143](https://github.com/systmms/segnomms/commit/57a814371726e4366fe39b9dc867ac85b0c3e52f))
* **polish:** complete navigation, beta notices, and final validation ([8787cff](https://github.com/systmms/segnomms/commit/8787cff957a4ccf7e0468e9399795aba71711d44))
* **spec:** add initial documentation audit specification ([7bf23ad](https://github.com/systmms/segnomms/commit/7bf23adf1f4b58b5697953c87b507c01a6171441))
* **spec:** complete implementation plan for documentation audit ([7433bdf](https://github.com/systmms/segnomms/commit/7433bdfaf592031102cc4b20ef8a6fd9a8d7005b))
* **spec:** generate implementation tasks for documentation audit ([c0eadc5](https://github.com/systmms/segnomms/commit/c0eadc539fe7e1c5233da443924d5801f9adb836))
* **specs:** add naming consistency specification and implementation plan ([051cb51](https://github.com/systmms/segnomms/commit/051cb51ca453faaf768b242ede7525d6b099baaa))
* **specs:** mark all naming consistency tasks as complete ([db854d6](https://github.com/systmms/segnomms/commit/db854d694d9221910f9ba6afbe185df33bad11c7))
* **specs:** update documentation audit status to complete ([e86ba00](https://github.com/systmms/segnomms/commit/e86ba0032875fe7e95ba84f0c4c28444e0fc528b))
* update task completion status for User Stories 1-3 ([5a6be24](https://github.com/systmms/segnomms/commit/5a6be249911c3e23188bdb9560b05baf707287c5))
* update task completion status for User Stories 4-5 ([79e4aa3](https://github.com/systmms/segnomms/commit/79e4aa30ed356c60f42642544609bd0ac0047ca1))


### Miscellaneous Chores

* +1 line to visual-gallery ([701dea7](https://github.com/systmms/segnomms/commit/701dea7061be6260ce9aab2c08f9551e51c71131))
* add ideas backlog for future refactoring opportunities ([d58f349](https://github.com/systmms/segnomms/commit/d58f349e57299603bb88c39b7579818e35eb0a6a))
* enforce repository policies and cleanup dependencies ([7b87a8a](https://github.com/systmms/segnomms/commit/7b87a8ac08dee1e73cb1b9f5059eb5355b5f171f))
* **spec:** renumber feature from 001 to 002 ([e63bebe](https://github.com/systmms/segnomms/commit/e63bebe559660bfe287a2906a75a781e4d662b29))
* updating changelog to appropriate beta vs real release notes ([481b7f1](https://github.com/systmms/segnomms/commit/481b7f112431755258495d05d6754a9c374c277c))


### Code Refactoring

* **naming:** complete phase4 naming consistency audit fixes ([3363f86](https://github.com/systmms/segnomms/commit/3363f868f4918269842ec8a4eb66cea2148a4c45))
* **naming:** rename phase4.py to composition.py for naming consistency ([e2047e9](https://github.com/systmms/segnomms/commit/e2047e9f390c6a33324f830ec089c61475a4ec9e))
* **naming:** standardize naming conventions and add deprecation warnings ([0eb9225](https://github.com/systmms/segnomms/commit/0eb9225b83349ba5294b28bd63a589434b0d8bc4))
* **naming:** standardize naming conventions and add deprecation warnings ([82c1ad9](https://github.com/systmms/segnomms/commit/82c1ad9ac81d375d313e29a6a121ffd045e41d74))


### Continuous Integration

* consolidate workflows and add wheel build job ([1c10544](https://github.com/systmms/segnomms/commit/1c10544deed491aa74d671ecb97df3528cbdf85a))
* **deps:** bump actions/cache from 4 to 5 ([2eb7894](https://github.com/systmms/segnomms/commit/2eb7894a214f701403afcab5b69030525425f297))
* **deps:** bump actions/checkout from 4 to 5 ([07db66c](https://github.com/systmms/segnomms/commit/07db66c42f9d1d9767ab0d3c5e6d5d62d30a2600))
* **deps:** bump actions/checkout from 4 to 5 ([71194d0](https://github.com/systmms/segnomms/commit/71194d0d87d045e074a26354180803303897544c))
* **deps:** bump actions/checkout from 4 to 5 ([b8ebd1f](https://github.com/systmms/segnomms/commit/b8ebd1ff7520bca498b1bfcf7441eb5ff360c891))
* **deps:** bump actions/checkout from 5 to 6 ([2cc6d08](https://github.com/systmms/segnomms/commit/2cc6d08988da2bcb51e7dde009773e26d54d5c31))
* **deps:** bump actions/configure-pages from 4 to 5 ([805e799](https://github.com/systmms/segnomms/commit/805e79932af97c70d71446ff0a05f17619ab4b20))
* **deps:** bump actions/configure-pages from 4 to 5 ([882d9e9](https://github.com/systmms/segnomms/commit/882d9e9b6dfe7f1124fb58fdcbf759abd2ae7c55))
* **deps:** bump actions/configure-pages from 4 to 5 ([4bb3943](https://github.com/systmms/segnomms/commit/4bb3943e9f9cf30de08b32fc8d58799c655581ba))
* **deps:** bump actions/download-artifact from 4 to 5 ([13cfe85](https://github.com/systmms/segnomms/commit/13cfe853a7fcc59b9908a852a4610d322af89686))
* **deps:** bump actions/download-artifact from 4 to 5 ([f3acc0b](https://github.com/systmms/segnomms/commit/f3acc0b0dbe1f85b3afc00a04c8123adcb835172))
* **deps:** bump actions/download-artifact from 4 to 5 ([de6a7e1](https://github.com/systmms/segnomms/commit/de6a7e1dfaa315890ccf207f6364e577285521b4))
* **deps:** bump actions/download-artifact from 5 to 6 ([60e2289](https://github.com/systmms/segnomms/commit/60e2289b12cfeb6fe62765bb21c0fb5c6ae77731))
* **deps:** bump actions/download-artifact from 5 to 6 ([f7f98f9](https://github.com/systmms/segnomms/commit/f7f98f9920684f6aaa327470bc2c9c9c4977f6a1))
* **deps:** bump actions/download-artifact from 6 to 7 ([a6c71ed](https://github.com/systmms/segnomms/commit/a6c71edbd20bf318538f42c7dd96adf378f63e67))
* **deps:** bump actions/github-script from 7 to 8 ([a20969e](https://github.com/systmms/segnomms/commit/a20969e892ce70a00662a1e0373a6760203ddac8))
* **deps:** bump actions/github-script from 7 to 8 ([b896116](https://github.com/systmms/segnomms/commit/b896116fbec85cbc0cc9c133fdd70a001de883e5))
* **deps:** bump actions/github-script from 7 to 8 ([0cc786f](https://github.com/systmms/segnomms/commit/0cc786fe8aad36397e2615a91e4eb60a9308c6ea))
* **deps:** bump actions/setup-node from 4 to 6 ([27d8fd2](https://github.com/systmms/segnomms/commit/27d8fd23dc3e95006a4184616faa96221890a65b))
* **deps:** bump actions/setup-node from 4 to 6 ([18200cc](https://github.com/systmms/segnomms/commit/18200ccf9f75751bd6fd9960d65ec7705c59e30d))
* **deps:** bump actions/setup-node from 4 to 6 ([7ea2f50](https://github.com/systmms/segnomms/commit/7ea2f500fafe08cc6df1adcc3f98283487f007c0))
* **deps:** bump actions/setup-python from 5 to 6 ([9464646](https://github.com/systmms/segnomms/commit/946464627c6ab0b2b6ee8f0ac40c19f74b4b299e))
* **deps:** bump actions/setup-python from 5 to 6 ([0d87cc6](https://github.com/systmms/segnomms/commit/0d87cc6ab97e36b0f9daf1a90dcb841f44982dd4))
* **deps:** bump actions/setup-python from 5 to 6 ([2d5cb42](https://github.com/systmms/segnomms/commit/2d5cb42811bbe84767edeb8b3d112447287a38d3))
* **deps:** bump actions/upload-artifact from 4 to 5 ([970c1fa](https://github.com/systmms/segnomms/commit/970c1fa958aba6b7b7c313e87174c974999ca6ae))
* **deps:** bump actions/upload-artifact from 4 to 5 ([dda9cf0](https://github.com/systmms/segnomms/commit/dda9cf04263d9cc4af1bcc74d399103b04561f88))
* **deps:** bump actions/upload-artifact from 5 to 6 ([ab3a899](https://github.com/systmms/segnomms/commit/ab3a89915642e96a1f90dedfc6e52a9e371eeb35))
* **deps:** bump actions/upload-pages-artifact from 3 to 4 ([83b7c9c](https://github.com/systmms/segnomms/commit/83b7c9ceb69b3174c58eadbdd94f18966925b620))
* **deps:** bump actions/upload-pages-artifact from 3 to 4 ([55e244c](https://github.com/systmms/segnomms/commit/55e244c4ec3cc3fb78ad572d8b8a5c5d2ddc4142))
* **deps:** bump actions/upload-pages-artifact from 3 to 4 ([a6b72c7](https://github.com/systmms/segnomms/commit/a6b72c742bfd78a6e884f6290a7683b79543a400))
* **deps:** bump amannn/action-semantic-pull-request from 5 to 6 ([89610a4](https://github.com/systmms/segnomms/commit/89610a4dca6bb6984130abe21d7a658fc58a65c5))
* **deps:** bump amannn/action-semantic-pull-request from 5 to 6 ([4bdfe76](https://github.com/systmms/segnomms/commit/4bdfe766fdafae283e82df8078b5c4ffb1f7dabb))
* **deps:** bump amannn/action-semantic-pull-request from 5 to 6 ([8ee9c0e](https://github.com/systmms/segnomms/commit/8ee9c0e46c569746c3f1820e5b9bdf3359540d08))
* **deps:** bump astral-sh/setup-uv from 3 to 7 ([bc878b3](https://github.com/systmms/segnomms/commit/bc878b32290ea1429edd6090d5ad11cdd02ff867))
* **deps:** bump astral-sh/setup-uv from 3 to 7 ([daf813f](https://github.com/systmms/segnomms/commit/daf813f398e5876bcfc1aa46e23466142c928c95))
* **deps:** bump astral-sh/setup-uv from 3 to 7 ([7bead40](https://github.com/systmms/segnomms/commit/7bead405a7c20d53e65da97adf724ea2a0012333))
* **deps:** bump codecov/codecov-action from 4 to 5 ([aba1a8f](https://github.com/systmms/segnomms/commit/aba1a8fe6ee99078d8398f287304de701fc60e59))
* **deps:** bump codecov/codecov-action from 4 to 5 ([a36ca38](https://github.com/systmms/segnomms/commit/a36ca388d6875f062609c4cd0ff54537613bb9e9))
* **deps:** bump codecov/codecov-action from 4 to 5 ([3ce1a23](https://github.com/systmms/segnomms/commit/3ce1a23e6e648684e760eaf48ba29886994f5221))
* **docs:** fix documentation CI/CD issues and improve quality enforcement ([791ca73](https://github.com/systmms/segnomms/commit/791ca73a210a7f6fcd0e4210f4415647c3336cdf))
* fix dependency installation and codecov action parameters ([1a2bee9](https://github.com/systmms/segnomms/commit/1a2bee96cca1d4147a89161a22719a6c383ca5e8))
* fix docs build dependency installation flag ([3661be6](https://github.com/systmms/segnomms/commit/3661be6ffaeeba03aa2eef0b966924483f14eb3c))
* removing full test validation from final release ([c377bc8](https://github.com/systmms/segnomms/commit/c377bc8dea7205a9b56f02720497adfad7c3f8ba))
* update release configuration to disable prerelease and remove unused files ([076ebc4](https://github.com/systmms/segnomms/commit/076ebc4abcdef875b5576ddb0964eb7f4f5110b0))

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
