{
  description = "Development environment for segnomms";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        pythonVersion = pkgs.python313.version;

        # Python environment with project dependencies
        pythonEnv = pkgs.python313.withPackages (ps: with ps; [
          # Core dependencies (from pyproject.toml)
          segno
          pydantic  # Configuration validation

          # Development dependencies
          pytest
          pytest-cov
          coverage  # Separate coverage package
          black
          isort
          flake8
          mypy
          
          # Testing dependencies
          hypothesis          # Property-based testing
          pytest-randomly     # Randomized test order
          pytest-timeout      # Prevent hung tests
          pytest-xdist        # Parallel test execution
          # Note: pytest-image-snapshot not available in nixpkgs, installed via uv
          beautifulsoup4      # HTML parsing in tests
          
          # Visual testing and processing
          pillow             # Image processing
          numpy              # Array operations for image comparison
          cairosvg           # SVG to PNG conversion
          lxml               # XML/SVG parsing
          
          # QR code decoding
          # Note: zxing-cpp is available as zxing-cpp in nixpkgs
          zxing-cpp          # Modern QR decoder
          # Note: opencv-python-headless is opencv4 in nixpkgs
          opencv4            # Computer vision library for QR code decoding

          # Documentation dependencies
          sphinx
          sphinx-rtd-theme
          sphinx-autodoc-typehints  # Type hints in docs

          # Basic build tools
          setuptools
          wheel
          
          # Note: The following are better managed by uv:
          # - build (for building packages)
          # - twine (for uploading to registries)
          # - keyrings.google-artifactregistry-auth (for Google Cloud)
          # These will be installed via 'uv sync' from pyproject.toml
        ]);

      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            # Python environment
            pythonEnv

            # Package management
            python313Packages.uv  # Ultra-fast Python package manager

            # Essential development tools
            git
            gnumake
            lefthook     # Git hooks manager
            fswatch      # For 'make watch' command

            # Deployment tools
            google-cloud-sdk  # For Google Cloud deployment

            # Optional tools (comment out if not needed)
            nodejs_20    # For any JS tooling
            docker       # For containerized testing
            
            # GitHub Actions tools (optional - for local testing)
            act          # GitHub Actions local runner
            actionlint   # GitHub Actions workflow linter

            # Visual regression testing tools
            librsvg      # Provides rsvg-convert for SVG to PNG conversion
            
            # System libraries for Python packages
            zbar         # Required for pyzbar QR code decoding
          ];

          shellHook = ''
            echo "segnomms development environment"
            echo "================================"
            echo ""
            echo "Core tools:"
            echo "  • Python ${pythonVersion}"
            echo "  • uv (Ultra-fast Python package manager)"
            echo "  • lefthook (Git hooks manager)"
            echo "  • gcloud (Google Cloud SDK for deployment)"
            echo ""
            echo "Testing capabilities:"
            echo "  • pytest with coverage, randomization, timeout, parallel execution"
            echo "  • hypothesis (Property-based testing)"
            echo "  • Visual regression testing (pytest-image-snapshot)"
            echo "  • QR decoders: zxing-cpp, opencv4"
            echo "  • SVG tools: cairosvg, rsvg-convert"
            echo ""
            echo "Code quality:"
            echo "  • black (formatter)"
            echo "  • isort (import sorter)"
            echo "  • flake8 (linter)"
            echo "  • mypy (type checker)"
            echo ""
            
            # Set up Python environment
            export PYTHONPATH="$PWD:$PYTHONPATH"

            # Check git hooks
            if [ ! -f .git/hooks/pre-commit ]; then
              echo "Installing lefthook git hooks..."
              lefthook install >/dev/null 2>&1 && echo "✅ Git hooks installed" || echo "⚠️  Failed to install git hooks"
            else
              echo "✅ Git hooks already installed"
            fi

            # Check uv environment
            if [ ! -d .venv ]; then
              echo ""
              echo "⚠️  No virtual environment found"
              echo "   Run 'uv sync' to create environment and install dependencies"
            else
              echo "✅ Virtual environment exists (.venv)"
              # Note: .envrc will handle activation and uv sync
            fi
            
            echo ""
            echo "Quick start:"
            echo "  1. uv sync          - Install all dependencies"
            echo "  2. make test-quick  - Run quick tests"
            echo "  3. make help        - See all available commands"
            echo ""
            echo "💡 Tip: The .envrc file will automatically run 'uv sync' when you enter this directory"
            echo ""
          '';
        };
      });
}
