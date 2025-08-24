#!/usr/bin/env bash
# Setup script for segnomms development environment

set -euo pipefail

echo "Setting up segnomms development environment..."
echo "============================================="
echo ""

# Check if Nix is installed
if ! command -v nix &> /dev/null; then
    echo "Error: Nix is not installed."
    echo "Please install Nix first: https://nixos.org/download.html"
    exit 1
fi

# Check if direnv is installed
if ! command -v direnv &> /dev/null; then
    echo "Error: direnv is not installed."
    echo "Please install direnv: https://direnv.net/docs/installation.html"
    exit 1
fi

# Enable flakes if not already enabled
if ! nix --version 2>&1 | grep -q "flakes"; then
    echo "Enabling Nix flakes..."
    mkdir -p ~/.config/nix
    echo "experimental-features = nix-command flakes" >> ~/.config/nix/nix.conf
fi

# Allow direnv for this directory
echo "Allowing direnv in this directory..."
direnv allow .

# Install lefthook hooks
echo "Installing lefthook hooks..."
if command -v lefthook &> /dev/null; then
    lefthook install
    echo "Lefthook hooks installed successfully!"
else
    echo "Warning: lefthook not found. Run 'pip install lefthook' then 'lefthook install' after entering the dev shell."
fi

# Check Docker
echo ""
echo "Checking Docker status..."
if command -v docker &> /dev/null && docker ps &> /dev/null; then
    echo "✓ Docker is installed and running"
else
    echo "⚠ Docker is not running or not installed"
    echo "  act requires Docker to run GitHub Actions locally"
    echo "  Please install/start Docker Desktop"
fi

echo ""
echo "Setup complete! 🎉"
echo ""
echo "Next steps:"
echo "1. Restart your shell or run: direnv reload"
echo "2. The development environment will activate automatically"
echo "3. Run 'act -l' to list available GitHub Actions"
echo "4. Run 'actionlint' to lint workflow files"
echo ""
echo "For more information, see: docs/github-actions-local-testing.md"