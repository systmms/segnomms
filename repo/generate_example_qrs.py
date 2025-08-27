#!/usr/bin/env python3
"""
Generate example QR codes for documentation.

This script creates example QR codes that demonstrate SegnoMMS capabilities
and are used in documentation examples and testing.

Used by GitHub Actions workflow to generate documentation artifacts.
"""

import sys
from pathlib import Path


def main():
    """Generate example QR codes."""
    print("🎨 Generating example QR codes...")

    # Create output directory
    output_dir = Path("example-outputs")
    output_dir.mkdir(exist_ok=True)
    print(f"   📁 Output directory: {output_dir.absolute()}")

    try:
        import segno

        print(f"   ✅ Segno version: {segno.__version__}")
    except ImportError as e:
        print(f"   ❌ Segno not found: {e}")
        print("   💡 Make sure Segno is installed: pip install segno")
        return False

    try:
        # Basic example
        print("   🔲 Creating basic QR code...")
        qr = segno.make("Hello World")
        basic_path = output_dir / "basic.svg"
        qr.save(str(basic_path), scale=10)
        print(f"      ✅ Saved: {basic_path}")

        # Styled example with custom colors
        print("   🎭 Creating styled QR code...")
        styled_path = output_dir / "styled.svg"
        qr.save(str(styled_path), scale=15, dark="#1a1a2e", light="#ffffff")
        print(f"      ✅ Saved: {styled_path}")

        # Additional example for documentation
        print("   📚 Creating documentation example...")
        doc_qr = segno.make("SegnoMMS Documentation Example")
        doc_path = output_dir / "documentation.svg"
        doc_qr.save(str(doc_path), scale=12, dark="#2d3748", light="#f7fafc")
        print(f"      ✅ Saved: {doc_path}")

        print("✅ Example QR codes generated successfully")
        print(f"   📊 Total files created: {len(list(output_dir.glob('*.svg')))}")

        return True

    except Exception as e:
        print(f"❌ Error generating QR codes: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
