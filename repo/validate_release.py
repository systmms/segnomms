#!/usr/bin/env python3
"""
Validate segnomms release packages before publishing.

This script performs comprehensive validation of built packages including:
- Package structure and contents
- Version consistency
- Import testing
- Basic functionality testing
"""

import argparse
import os
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import List, Optional


class PackageValidator:
    """Validates segnomms packages for release."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def log(self, message: str, level: str = "INFO"):
        """Log a message if verbose mode is enabled."""
        if self.verbose or level in ["ERROR", "WARNING"]:
            print(f"[{level}] {message}")

    def validate_wheel(self, wheel_path: str) -> bool:
        """Validate a wheel package."""
        self.log(f"Validating wheel: {wheel_path}")

        if not os.path.exists(wheel_path):
            self.errors.append(f"Wheel file not found: {wheel_path}")
            return False

        # Check wheel naming convention
        wheel_name = os.path.basename(wheel_path)
        if not re.match(r"segnomms-\d+\.\d+\.\d+-py3-none-any\.whl", wheel_name):
            self.warnings.append(f"Non-standard wheel name: {wheel_name}")

        # Extract and validate contents
        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(wheel_path, "r") as zf:
                zf.extractall(tmpdir)

                # Check for required files
                required_files = [
                    "segnomms/__init__.py",
                    "segnomms/plugin.py",
                    "segnomms-*.dist-info/METADATA",
                    "segnomms-*.dist-info/WHEEL",
                    "segnomms-*.dist-info/RECORD",
                ]

                for pattern in required_files:
                    if not any(Path(tmpdir).glob(pattern)):
                        self.errors.append(f"Missing required file: {pattern}")

                # Validate metadata
                metadata_files = list(Path(tmpdir).glob("segnomms-*.dist-info/METADATA"))
                if metadata_files:
                    metadata_content = metadata_files[0].read_text()

                    # Check required metadata fields
                    required_metadata = [
                        "Name: segnomms",
                        "Version:",
                        "Summary:",
                        "License:",
                        "Requires-Dist: segno",
                    ]

                    for field in required_metadata:
                        if field not in metadata_content:
                            self.errors.append(f"Missing metadata field: {field}")

                    # Extract version from metadata
                    version_match = re.search(r"Version: (.+)", metadata_content)
                    if version_match:
                        self.wheel_version = version_match.group(1)
                        self.log(f"Wheel version: {self.wheel_version}")

        return len(self.errors) == 0

    def validate_sdist(self, sdist_path: str) -> bool:
        """Validate a source distribution."""
        self.log(f"Validating sdist: {sdist_path}")

        if not os.path.exists(sdist_path):
            self.errors.append(f"Sdist file not found: {sdist_path}")
            return False

        # Check naming convention
        sdist_name = os.path.basename(sdist_path)
        if not re.match(r"segnomms-\d+\.\d+\.\d+\.tar\.gz", sdist_name):
            self.warnings.append(f"Non-standard sdist name: {sdist_name}")

        # Extract and validate contents
        with tempfile.TemporaryDirectory() as tmpdir:
            subprocess.run(["tar", "-xzf", sdist_path, "-C", tmpdir], check=True)

            # Find the extracted directory
            extracted_dirs = [d for d in os.listdir(tmpdir) if d.startswith("segnomms-")]
            if not extracted_dirs:
                self.errors.append("No segnomms directory found in sdist")
                return False

            sdist_dir = Path(tmpdir) / extracted_dirs[0]

            # Check for required files
            required_files = [
                "pyproject.toml",
                "README.md",
                "LICENSE",
                "segnomms/__init__.py",
                "segnomms/plugin.py",
            ]

            for file in required_files:
                if not (sdist_dir / file).exists():
                    self.errors.append(f"Missing required file in sdist: {file}")

        return len(self.errors) == 0

    def validate_version_consistency(self, wheel_path: str, expected_version: Optional[str] = None) -> bool:
        """Validate version consistency across package files."""
        self.log("Validating version consistency")

        versions = {}

        # Extract version from wheel filename
        wheel_name = os.path.basename(wheel_path)
        version_match = re.search(r"segnomms-(\d+\.\d+\.\d+)-", wheel_name)
        if version_match:
            versions["wheel_filename"] = version_match.group(1)

        # Extract version from wheel metadata (already done in validate_wheel)
        if hasattr(self, "wheel_version"):
            versions["wheel_metadata"] = self.wheel_version

        # Check if all versions match
        unique_versions = set(versions.values())
        if len(unique_versions) > 1:
            self.errors.append(f"Version mismatch: {versions}")
            return False

        if expected_version and expected_version not in unique_versions:
            self.errors.append(f"Version mismatch: expected {expected_version}, found {unique_versions}")
            return False

        self.log(f"All versions consistent: {list(unique_versions)[0]}")
        return True

    def test_installation(self, wheel_path: str) -> bool:
        """Test package installation in a clean environment."""
        self.log("Testing package installation")

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a virtual environment
            venv_path = Path(tmpdir) / "venv"
            subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)

            # Get the python executable in the venv
            if sys.platform == "win32":
                python_exe = venv_path / "Scripts" / "python.exe"
            else:
                python_exe = venv_path / "bin" / "python"

            # Install the wheel
            result = subprocess.run(
                [str(python_exe), "-m", "pip", "install", wheel_path], capture_output=True, text=True
            )

            if result.returncode != 0:
                self.errors.append(f"Installation failed: {result.stderr}")
                return False

            # Test import and basic functionality
            test_script = """
import sys
try:
    import segnomms
    import segno

    # Check version
    print(f"Version: {segnomms.__version__}")

    # Check plugin registration
    qr = segno.make("Test")
    if not hasattr(qr, 'interactive_svg'):
        print("ERROR: Plugin not registered")
        sys.exit(1)

    # Test basic functionality
    svg = qr.interactive_svg()
    if not svg or '<svg' not in str(svg):
        print("ERROR: SVG generation failed")
        sys.exit(1)

    print("SUCCESS: All tests passed")
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
"""

            result = subprocess.run([str(python_exe), "-c", test_script], capture_output=True, text=True)

            if result.returncode != 0:
                self.errors.append(f"Functionality test failed: {result.stdout} {result.stderr}")
                return False

            self.log(result.stdout.strip())
            return True

    def validate_all(self, dist_dir: str, expected_version: Optional[str] = None) -> bool:
        """Validate all packages in a distribution directory."""
        self.log(f"Validating packages in: {dist_dir}")

        # Find wheel and sdist files
        wheel_files = list(Path(dist_dir).glob("*.whl"))
        sdist_files = list(Path(dist_dir).glob("*.tar.gz"))

        if not wheel_files:
            self.errors.append("No wheel files found")
            return False

        if not sdist_files:
            self.warnings.append("No sdist files found")

        # Validate each package
        all_valid = True

        for wheel_path in wheel_files:
            if not self.validate_wheel(str(wheel_path)):
                all_valid = False

            if not self.validate_version_consistency(str(wheel_path), expected_version):
                all_valid = False

            if not self.test_installation(str(wheel_path)):
                all_valid = False

        for sdist_path in sdist_files:
            if not self.validate_sdist(str(sdist_path)):
                all_valid = False

        return all_valid

    def print_summary(self):
        """Print validation summary."""
        print("\n" + "=" * 50)
        print("VALIDATION SUMMARY")
        print("=" * 50)

        if self.errors:
            print(f"\nErrors ({len(self.errors)}):")
            for error in self.errors:
                print(f"  ✗ {error}")

        if self.warnings:
            print(f"\nWarnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  ⚠ {warning}")

        if not self.errors:
            print("\n✓ All validations passed!")
        else:
            print(f"\n✗ Validation failed with {len(self.errors)} errors")

        print("=" * 50)


def main():
    parser = argparse.ArgumentParser(description="Validate segnomms release packages")
    parser.add_argument("dist_dir", help="Distribution directory containing packages")
    parser.add_argument("--version", help="Expected version number")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    validator = PackageValidator(verbose=args.verbose)
    success = validator.validate_all(args.dist_dir, args.version)
    validator.print_summary()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
