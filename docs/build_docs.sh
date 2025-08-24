#!/bin/bash
# Build script for Sphinx documentation

set -e  # Exit on error

echo "Building Segno Interactive SVG Plugin documentation..."

# Check if we're in the docs directory
if [ ! -f "Makefile" ]; then
    echo "Error: Must run from docs directory"
    exit 1
fi

# Install documentation dependencies
echo "Installing documentation dependencies..."
pip install -r requirements.txt

# Clean previous builds
echo "Cleaning previous builds..."
make clean

# Build HTML documentation
echo "Building HTML documentation..."
make html

# Check if build was successful
if [ -d "build/html" ]; then
    echo "Documentation built successfully!"
    echo "View at: file://$(pwd)/build/html/index.html"
    
    # Optional: Open in browser
    if command -v open &> /dev/null; then
        read -p "Open in browser? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            open build/html/index.html
        fi
    fi
else
    echo "Error: Documentation build failed"
    exit 1
fi