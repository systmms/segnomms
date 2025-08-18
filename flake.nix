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

        pythonVersion = pkgs.python311.version;

        # Python environment with project dependencies
        pythonEnv = pkgs.python311.withPackages (ps: with ps; [
          # Core dependencies
          segno

          # Development dependencies
          pytest
          pytest-cov
          black
          isort
          flake8
          mypy
          playwright
          pytest-playwright
          pillow

          # Additional useful packages
          pip
          virtualenv
          setuptools
          wheel
        ]);

      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            # Python environment
            pythonEnv

            # GitHub Actions tools
            act          # GitHub Actions local runner
            actionlint   # GitHub Actions workflow linter

            # Pre-commit framework
            pre-commit

            # Additional development tools
            git
            gnumake
            nodejs_20    # For any JS tooling

            # Docker for act (if not already installed)
            docker

            # Google Cloud SDK for deployment
            google-cloud-sdk
          ];

          shellHook = ''
            echo "segnomms development environment"
            echo "================================"
            echo ""
            echo "Available tools:"
            echo "  • Python ${pythonVersion}"
            echo "  • act (GitHub Actions local runner)"
            echo "  • actionlint (GitHub Actions linter)"
            echo "  • pre-commit (Git hooks framework)"
            echo "  • gcloud (Google Cloud SDK)"
            echo ""
            echo "Quick start:"
            echo "  • Run 'pre-commit install' to set up git hooks"
            echo "  • Use 'act' to test GitHub Actions locally"
            echo "  • Use 'actionlint' to lint workflow files"
            echo ""

            # Set up Python environment
            export PYTHONPATH="$PWD:$PYTHONPATH"

            # Install pre-commit hooks if not already installed
            if [ ! -f .git/hooks/pre-commit ]; then
              echo "Installing pre-commit hooks..."
              pre-commit install
            fi

            export VIRTUAL_ENV_DISABLE_PROMPT=1
            virtualenv .venv
            source .venv/bin/activate
          '';
        };
      });
}
