#!/usr/bin/env python3
"""
Test: Visual Baseline Generator

Generates visual test baselines for all available shapes with systematic
configurations for visual regression testing.
"""

import sys
from pathlib import Path

import segno

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from segnomms.plugin import write


def generate_visual_baselines():
    """Generate visual test baselines for all shape types."""

    # Output to tests/visual/baseline directory
    baseline_dir = Path(__file__).parent.parent / "tests" / "visual" / "baseline"
    baseline_dir.mkdir(parents=True, exist_ok=True)

    # Test data - consistent across all baselines
    test_url = "https://github.com/segno-project/segno"
    qr = segno.make(test_url, error="h")

    # All available shapes for testing
    shapes = [
        "square",
        "circle",
        "rounded",
        "dot",
        "diamond",
        "star",
        "triangle",
        "hexagon",
        "cross",
        "squircle",
        "connected",
        "connected-extra-rounded",
        "connected-classy",
        "connected-classy-rounded",
    ]

    print(f"🧪 Generating visual test baselines in '{baseline_dir}' directory...")
    print(f"📊 Test content: {test_url}")
    print(f"🎯 Shapes to test: {len(shapes)}")

    success_count = 0
    error_count = 0

    for shape_name in shapes:
        print(f"\n🔍 Testing shape: {shape_name}")

        # Generate baseline with safe mode ON
        safe_filename = baseline_dir / f"{shape_name}_safe_on.baseline.svg"
        try:
            write(
                qr,
                str(safe_filename),
                shape=shape_name,
                scale=10,
                border=2,
                dark="#000000",
                light="#FFFFFF",
                safe_mode=True,
            )
            print(f"  ✓ {safe_filename.name}")
            success_count += 1
        except Exception as e:
            print(f"  ❌ Error with {shape_name} safe on: {e}")
            error_count += 1

        # Generate baseline with safe mode OFF
        unsafe_filename = baseline_dir / f"{shape_name}_safe_off.baseline.svg"
        try:
            write(
                qr,
                str(unsafe_filename),
                shape=shape_name,
                scale=10,
                border=2,
                dark="#000000",
                light="#FFFFFF",
                safe_mode=False,
            )
            print(f"  ✓ {unsafe_filename.name}")
            success_count += 1
        except Exception as e:
            print(f"  ❌ Error with {shape_name} safe off: {e}")
            error_count += 1

    # Generate additional test configurations
    generate_special_baselines(baseline_dir, qr)

    print("\n📊 Baseline Generation Summary:")
    print(f"   ✅ Successful: {success_count}")
    print(f"   ❌ Errors: {error_count}")
    print(f"   📁 Output: {baseline_dir}")

    if error_count == 0:
        print("🎉 All baselines generated successfully!")
    else:
        print("⚠️  Some baselines failed to generate. Check errors above.")

    return error_count == 0


def generate_special_baselines(baseline_dir, qr):
    """Generate special configuration baselines for comprehensive testing."""

    print("\n🎯 Generating special configuration baselines...")

    # Color variations
    color_configs = [
        ("Brand_colors", {"dark": "#1a1a2e", "light": "#eee2dc"}),
        ("Classic_BandW", {"dark": "#000000", "light": "#ffffff"}),
        ("Gray_scale", {"dark": "#333333", "light": "#f0f0f0"}),
        ("Red_on_transparent", {"dark": "#d63031", "light": "transparent"}),
    ]

    for config_name, colors in color_configs:
        filename = baseline_dir / f"colors_{config_name}.baseline.svg"
        try:
            write(qr, str(filename), shape="rounded", scale=8, border=2, **colors)
            print(f"  ✓ Color test: {config_name}")
        except Exception as e:
            print(f"  ❌ Color test error ({config_name}): {e}")

    # Error correction levels
    error_levels = ["L", "M", "Q", "H"]
    for level in error_levels:
        qr_level = segno.make("Error correction test", error=level.lower())
        filename = baseline_dir / f"error_level_{level}.baseline.svg"
        try:
            write(
                qr_level,
                str(filename),
                shape="square",
                scale=8,
                border=2,
            )
            print(f"  ✓ Error level: {level}")
        except Exception as e:
            print(f"  ❌ Error level test ({level}): {e}")

    # Frame configurations
    frame_configs = [
        ("frame_square_hard", {"frame_shape": "square", "frame_clip_mode": "clip"}),
        ("frame_circle_fade", {"frame_shape": "circle", "frame_clip_mode": "fade"}),
        ("frame_rounded_scale", {"frame_shape": "rounded-rect", "frame_clip_mode": "scale"}),
    ]

    for config_name, frame_config in frame_configs:
        filename = baseline_dir / f"{config_name}.baseline.svg"
        try:
            write(qr, str(filename), shape="rounded", scale=8, border=2, **frame_config)
            print(f"  ✓ Frame test: {config_name}")
        except Exception as e:
            print(f"  ❌ Frame test error ({config_name}): {e}")

    # Complex configuration
    filename = baseline_dir / "complex_full_config.baseline.svg"
    try:
        write(
            qr,
            str(filename),
            shape="squircle",
            corner_radius=0.3,
            scale=10,
            border=3,
            dark="#2563eb",
            light="#eff6ff",
            frame_shape="rounded-rect",
            frame_corner_radius=0.2,
            centerpiece_enabled=True,
            centerpiece_size=0.15,
            centerpiece_shape="circle",
            interactive=True,
        )
        print(f"  ✓ Complex configuration test")
    except Exception as e:
        print(f"  ❌ Complex configuration error: {e}")

    # Payload variations
    payloads = [
        ("simple", "Hello World"),
        ("url", "https://example.com/path?param=value"),
        ("email", "mailto:test@example.com"),
        ("phone", "tel:+1234567890"),
        (
            "url_complex",
            "https://very-long-domain-name.com/very/long/path/with/many/segments?param1=value1&param2=value2&param3=value3",
        ),
    ]

    for payload_name, content in payloads:
        qr_payload = segno.make(content, error="M")
        filename = baseline_dir / f"payload_{payload_name}.baseline.svg"
        try:
            write(
                qr_payload,
                str(filename),
                shape="rounded",
                scale=8,
                border=2,
            )
            print(f"  ✓ Payload test: {payload_name}")
        except Exception as e:
            print(f"  ❌ Payload test error ({payload_name}): {e}")

    # Shape configuration variations
    shape_configs = [
        ("shape_config_square", {"shape": "square"}),
        ("shape_config_circle", {"shape": "circle"}),
        ("shape_config_squircle", {"shape": "squircle", "corner_radius": 0.4}),
        ("shape_config_connected", {"shape": "connected", "merge": "soft"}),
    ]

    for config_name, shape_config in shape_configs:
        filename = baseline_dir / f"{config_name}.baseline.svg"
        try:
            write(qr, str(filename), scale=8, border=2, **shape_config)
            print(f"  ✓ Shape config test: {config_name}")
        except Exception as e:
            print(f"  ❌ Shape config error ({config_name}): {e}")


if __name__ == "__main__":
    success = generate_visual_baselines()
    if success:
        print(f"\n✅ Baseline generation completed successfully")
        print(f"🧪 These files can be used for visual regression testing")
    else:
        print(f"\n❌ Baseline generation had errors")
        sys.exit(1)
