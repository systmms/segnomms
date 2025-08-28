#!/usr/bin/env python3
"""Build a wheel package for the segnomms plugin."""

import subprocess
import sys
from pathlib import Path


def build_wheel():
    """Build wheel and source distribution packages using standard Python tools."""

    # Ensure we're in the project root
    project_root = Path(__file__).parent.parent

    print(f"Building packages from: {project_root}")
    print("=" * 50)

    try:
        # Clean any previous builds
        print("🧹 Cleaning previous builds...")
        dist_dir = project_root / "dist"
        if dist_dir.exists():
            import shutil

            shutil.rmtree(dist_dir)

        # Build using python -m build (modern standard)
        print("📦 Building wheel and source distribution...")
        result = subprocess.run(
            [sys.executable, "-m", "build"], cwd=project_root, capture_output=True, text=True
        )

        if result.returncode != 0:
            print(f"❌ Build failed: {result.stderr}")
            return False

        # List built packages
        print("\n✅ Build completed successfully!")
        print("\nBuilt packages:")
        for file in dist_dir.glob("*"):
            print(f"  📦 {file.name}")

        print("\n💡 Next steps:")
        print("  • Run validation: python repo/validate_release.py dist/")
        print("  • Test installation: pip install dist/*.whl")
        print("  • Publish to PyPI: twine upload dist/*")

        return True

    except Exception as e:
        print(f"❌ Error during build: {e}")
        return False


if __name__ == "__main__":
    success = build_wheel()
    sys.exit(0 if success else 1)
