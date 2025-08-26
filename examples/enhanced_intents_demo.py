"""
Demonstration of the enhanced intent-based API with detailed feedback.

This example shows how to use the expanded intent system with:
- New intent categories (interactivity, animation, performance, branding)
- Detailed transformation tracking
- Comprehensive feedback on how intents were processed
"""

from pathlib import Path

from segnomms.intents import (
    AccessibilityIntents,
    AnimationIntents,
    BrandingIntents,
    FrameIntents,
    IntentsConfig,
    InteractivityIntents,
    PayloadConfig,
    PerformanceIntents,
    ReserveIntents,
    StyleIntents,
    render_with_intents,
)


def demo_basic_intents():
    """Demonstrate basic intent usage with feedback."""
    print("=== Basic Intent Demo ===\n")

    # Define payload
    payload = PayloadConfig(
        text="https://example.com/enhanced-demo", error_correction="H"  # High error correction
    )

    # Define intents
    intents = IntentsConfig(
        style=StyleIntents(
            module_shape="squircle",
            merge="soft",
            connectivity="8-way",
            corner_radius=0.3,
            palette={"fg": "#1a1a2e", "bg": "#f5f5f5"},
        ),
        accessibility=AccessibilityIntents(
            ids=True,
            id_prefix="demo",
            title="Enhanced Demo QR Code",
            desc="QR code demonstrating enhanced intent API",
            aria=True,
        ),
    )

    # Render with intents
    result = render_with_intents(payload, intents)

    # Display results
    print(f"SVG Generated: {len(result.svg_content)} characters")
    print(f"Warnings: {result.warning_count}")
    print(f"Degradation Applied: {result.degradation_applied}")

    # Show warnings if any
    if result.has_warnings:
        print("\nWarnings:")
        for warning in result.warnings:
            print(f"  - [{warning.severity}] {warning.path}: {warning.detail}")
            if warning.suggestion:
                print(f"    Suggestion: {warning.suggestion}")

    # Show translation report
    if result.translation_report:
        print("\nTransformation Summary:")
        for key, value in result.translation_report.intent_summary.items():
            print(f"  - {key}: {value}")

    return result


def demo_advanced_intents():
    """Demonstrate advanced intents with detailed feedback."""
    print("\n=== Advanced Intent Demo ===\n")

    payload = PayloadConfig(url="https://example.com/advanced")

    # Complex intent configuration
    intents = IntentsConfig(
        style=StyleIntents(
            module_shape="connected-smooth",
            merge="aggressive",
            patterns={"finder": "rounded", "timing": "square", "alignment": "circle", "data": "squircle"},
        ),
        frame=FrameIntents(
            shape="rounded-rect",
            corner_radius=0.2,
            clip_mode="fade",
            fade_distance=10,  # Will show as unsupported
        ),
        reserve=ReserveIntents(
            area_pct=15.0, shape="circle", placement="center", mode="knockout"  # Will show as unsupported
        ),
        interactivity=InteractivityIntents(
            hover_effects=True,
            hover_scale=1.1,  # Will show as unsupported
            tooltips=True,
            cursor_style="pointer",
        ),
        animation=AnimationIntents(
            fade_in=True, fade_duration=0.5, stagger_animation=True  # Will show as unsupported
        ),
        performance=PerformanceIntents(
            optimize_for="size", max_svg_size_kb=100, simplify_paths=True  # Will show as unsupported
        ),
        branding=BrandingIntents(
            logo_url="https://example.com/logo.png",  # Will enable centerpiece
            brand_colors={"primary": "#007bff", "secondary": "#6c757d"},
            theme_preset="corporate",  # Will show as experimental
        ),
    )

    result = render_with_intents(payload, intents)

    # Detailed feedback
    print(f"SVG Generated: {len(result.svg_content)} characters")
    print(f"Total Warnings: {result.warning_count}")
    print(f"Unsupported Intents: {len(result.unsupported_intents)}")

    # Show transformation details
    if result.translation_report:
        print("\nTransformation Steps:")
        for step in result.translation_report.transformation_steps[:5]:  # First 5
            print(f"  - {step.intent_path}: {step.original_value} → {step.transformed_value}")
            print(f"    Type: {step.transformation_type}, Confidence: {step.confidence}")

        if len(result.translation_report.transformation_steps) > 5:
            print(f"  ... and {len(result.translation_report.transformation_steps) - 5} more")

    # Show degradation details
    if result.translation_report and result.translation_report.degradation_details:
        print("\nDegradation Details:")
        for detail in result.translation_report.degradation_details:
            print(f"  - {detail.intent_path}: {detail.requested_feature}")
            print(f"    Reason: {detail.degradation_reason}")
            print(f"    Impact: {detail.impact_level}")
            if detail.alternatives:
                print(f"    Alternatives: {', '.join(detail.alternatives)}")

    # Show compatibility info
    if result.translation_report and result.translation_report.compatibility_info:
        print("\nCompatibility Information:")
        for info in result.translation_report.compatibility_info:
            print(f"  - {info.intent_path}: {info.support_level}")
            if info.planned_support:
                print(f"    Planned: {info.planned_support}")
            if info.workarounds:
                print(f"    Workarounds: {', '.join(info.workarounds)}")

    # Show feature impact
    if result.feature_impact:
        print("\nFeature Impact Analysis:")
        for feature, impact in result.feature_impact.items():
            print(f"  - {feature}: {impact}")

    # Show scanability prediction
    if result.scanability_prediction:
        print(f"\nPredicted Scanability: {result.scanability_prediction}")

    return result


def demo_comparison():
    """Show difference between requested and used options."""
    print("\n=== Intent Comparison Demo ===\n")

    payload = PayloadConfig(text="Compare requested vs used")

    # Request unsupported features
    intents = IntentsConfig(
        style=StyleIntents(
            module_shape="invalid-shape",  # Will fall back to square
            merge="ultra-aggressive",  # Will fall back to none
            corner_radius=0.7,  # Valid value to test other features
        ),
        animation=AnimationIntents(fade_in=True, pulse_effect=True),
    )

    result = render_with_intents(payload, intents)

    print("Requested vs Used Options:")

    if result.requested_options and result.used_options:
        print("\nRequested:")
        for key, value in result.requested_options.items():
            if value:
                print(f"  {key}: {value}")

        print("\nActually Used:")
        for key, value in result.used_options.items():
            print(f"  {key}: {value}")

    return result


def main():
    """Run all demonstrations."""
    # Basic demo
    basic_result = demo_basic_intents()

    # Advanced demo
    advanced_result = demo_advanced_intents()

    # Comparison demo
    comparison_result = demo_comparison()
    assert comparison_result is not None  # Validate comparison demo completed successfully

    # Save example outputs to proper directory
    output_dir = Path(__file__).parent / "output" / "demos"
    output_dir.mkdir(parents=True, exist_ok=True)

    basic_path = output_dir / "enhanced_basic_demo.svg"
    advanced_path = output_dir / "enhanced_advanced_demo.svg"

    with open(basic_path, "w") as f:
        f.write(basic_result.svg_content)

    with open(advanced_path, "w") as f:
        f.write(advanced_result.svg_content)

    print("\n✅ SVG files saved:")
    print(f"   - {basic_path}")
    print(f"   - {advanced_path}")

    # Show client format
    print("\n=== Client Format Example ===")
    client_data = basic_result.to_client_format()
    print(f"Keys in client format: {list(client_data.keys())}")
    print(f"Metrics: {client_data['metrics']}")


if __name__ == "__main__":
    main()
