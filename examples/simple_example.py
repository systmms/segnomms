#!/usr/bin/env python3
"""
Simple example showing basic usage of the segno interactive SVG plugin.
This file is used by CI for package installation testing.
"""

import segno

from segnomms import write
from segnomms.constants import DEFAULT_BORDER, DEFAULT_SCALE, TEST_COLORS, ModuleShape


def main():
    """Generate a simple QR code example."""

    # Create a QR code
    qr = segno.make("Hello, World!", error="h")

    print("Generating simple QR code example...")

    # Generate a simple rounded QR code
    write(
        qr,
        "simple_test.svg",
        shape=ModuleShape.ROUNDED.value,
        dark=TEST_COLORS["blue"],
        light=TEST_COLORS["white"],
        scale=DEFAULT_SCALE,
        border=DEFAULT_BORDER,
    )

    print("✓ Generated simple_test.svg")
    print("✅ Simple example completed successfully!")


if __name__ == "__main__":
    main()
