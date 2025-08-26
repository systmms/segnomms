#!/usr/bin/env python3
"""Build a wheel package for the segnomms plugin."""

import shutil
import subprocess
import tempfile
from pathlib import Path


def build_wheel():
    """Build a wheel package that can be loaded by micropip in Pyodide."""

    # Create temporary build directory
    with tempfile.TemporaryDirectory() as tmpdir:
        build_dir = Path(tmpdir) / "segnomms_wheel"
        build_dir.mkdir()

        # First create the bundle
        print("Creating bundle...")
        subprocess.run(["python", "scripts/bundle_for_pyodide.py"], check=True)

        # Copy bundled file as package
        bundle_src = Path("dist/segnomms_bundled.py")

        # Create package structure
        pkg_dir = build_dir / "segnomms"
        pkg_dir.mkdir()

        # Create __init__.py that imports everything from bundle
        init_content = '''"""Segno Interactive SVG Plugin"""

# Import everything from the bundled module
from .bundle import *

__version__ = "0.0.0-beta003"
__all__ = [
    'write',
    'generate_interactive_svg',
    'RenderingConfig',
    'ModuleDetector',
    'InteractiveSVGBuilder',
    'ShapeRenderer',
]
'''

        (pkg_dir / "__init__.py").write_text(init_content)

        # Copy bundle as bundle.py
        shutil.copy(bundle_src, pkg_dir / "bundle.py")

        # Create setup.py
        setup_content = """from setuptools import setup, find_packages

setup(
    name="segno-interactive-svg",
    version="0.0.0-beta003",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[],  # No dependencies for Pyodide
    description="Interactive SVG plugin for Segno QR codes",
    author="QR Code MMS Team",
    url="https://github.com/yourusername/segno-interactive-svg",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
"""

        (build_dir / "setup.py").write_text(setup_content)

        # Create pyproject.toml for modern packaging
        pyproject_content = """[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "segno-interactive-svg"
version = "0.0.0-beta003"
description = "Interactive SVG plugin for Segno QR codes"
requires-python = ">=3.7"
"""

        (build_dir / "pyproject.toml").write_text(pyproject_content)

        # Build the wheel
        print("Building wheel...")
        subprocess.run(
            [
                "python",
                "-m",
                "pip",
                "wheel",
                "--no-deps",  # Don't include dependencies
                "--wheel-dir",
                "dist",
                str(build_dir),
            ],
            check=True,
        )

    print("Wheel built successfully!")
    print("You can now use: await micropip.install('./dist/segnomms-0.1.0-py3-none-any.whl')")


if __name__ == "__main__":
    build_wheel()
