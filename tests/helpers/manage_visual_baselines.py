#!/usr/bin/env python3
"""
Utility script for managing visual regression baselines with configuration tracking.

This script helps:
- Analyze existing baselines and their configurations
- Detect configuration drift
- Regenerate baselines with specific configurations
- Generate reports on visual test coverage
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import segno

from segnomms import write
from segnomms.config import RenderingConfig
from segnomms.plugin import _generate_config_hash


def analyze_baselines(baseline_dir: Path) -> Dict[str, Any]:
    """Analyze all baseline configurations in a directory."""
    print(f"Analyzing baselines in: {baseline_dir}")

    configs = {}
    shape_stats = {}
    feature_stats = {
        "interactive": 0,
        "tooltips": 0,
        "safe_mode": 0,
        "custom_colors": 0,
        "frame": 0,
        "centerpiece": 0,
        "patterns": 0,
    }

    config_files = list(baseline_dir.glob("*.baseline_config.json"))

    for config_file in config_files:
        config_data = json.loads(config_file.read_text())
        test_name = config_data.get("test_name", config_file.stem)
        config = config_data["configuration"]

        configs[test_name] = {"hash": config_data["config_hash"], "file": str(config_file), "config": config}

        # Analyze shape usage
        shape = config.get("geometry", {}).get("shape", "square")
        shape_stats[shape] = shape_stats.get(shape, 0) + 1

        # Analyze feature usage
        if config.get("style", {}).get("interactive"):
            feature_stats["interactive"] += 1
        if config.get("style", {}).get("tooltips"):
            feature_stats["tooltips"] += 1
        if config.get("safe_mode", True):
            feature_stats["safe_mode"] += 1
        if config.get("dark") != "black" or config.get("light") != "white":
            feature_stats["custom_colors"] += 1
        if config.get("frame", {}).get("shape") != "square":
            feature_stats["frame"] += 1
        if config.get("centerpiece", {}).get("enabled"):
            feature_stats["centerpiece"] += 1
        if config.get("patterns", {}).get("enabled"):
            feature_stats["patterns"] += 1

    return {
        "total_baselines": len(configs),
        "configurations": configs,
        "shape_distribution": shape_stats,
        "feature_usage": feature_stats,
    }


def check_config_drift(baseline_dir: Path) -> List[Dict[str, Any]]:
    """Check if any baseline SVGs don't match their configuration hash."""
    drifts = []

    for config_file in baseline_dir.glob("*.baseline_config.json"):
        config_data = json.loads(config_file.read_text())
        saved_hash = config_data["config_hash"]

        # Recreate hash from configuration
        config = RenderingConfig(**config_data["configuration"])
        current_hash = _generate_config_hash(config)

        if saved_hash != current_hash:
            drifts.append(
                {
                    "file": str(config_file),
                    "saved_hash": saved_hash,
                    "current_hash": current_hash,
                    "test_name": config_data.get("test_name"),
                }
            )

    return drifts


def regenerate_baseline(config_file: Path, output_dir: Path = None) -> bool:
    """Regenerate a baseline SVG from its configuration."""
    try:
        config_data = json.loads(config_file.read_text())
        test_name = config_data.get("test_name", config_file.stem)

        # Recreate configuration
        config = RenderingConfig(**config_data["configuration"])

        # Generate QR code (using test name as content)
        qr = segno.make(f"Regenerated: {test_name}", error="M")

        # Determine output path
        if output_dir:
            svg_path = output_dir / f"{test_name}.svg"
        else:
            svg_path = config_file.parent / config_file.name.replace("_config.json", ".svg")

        # Generate SVG
        with open(svg_path, "w") as f:
            write(qr, f, export_config=False, **config.model_dump())

        print(f"Regenerated: {svg_path}")
        return True

    except Exception as e:
        print(f"Failed to regenerate {config_file}: {e}")
        return False


def generate_coverage_report(analysis: Dict[str, Any], output_file: Path = None):
    """Generate a coverage report for visual tests."""
    report = []
    report.append("Visual Regression Test Coverage Report")
    report.append("=" * 50)
    report.append(f"\nTotal Baselines: {analysis['total_baselines']}")

    # Shape coverage
    report.append("\nShape Distribution:")
    for shape, count in sorted(analysis["shape_distribution"].items()):
        percentage = (count / analysis["total_baselines"]) * 100
        report.append(f"  {shape:25} {count:3d} ({percentage:5.1f}%)")

    # Feature coverage
    report.append("\nFeature Usage:")
    total = analysis["total_baselines"]
    for feature, count in sorted(analysis["feature_usage"].items()):
        percentage = (count / total) * 100 if total > 0 else 0
        report.append(f"  {feature:25} {count:3d} ({percentage:5.1f}%)")

    # Configuration details
    report.append("\nConfiguration Details:")
    for test_name, info in sorted(analysis["configurations"].items()):
        report.append(f"\n  {test_name}:")
        report.append(f"    Hash: {info['hash']}")
        config = info["config"]
        report.append(f"    Shape: {config.get('geometry', {}).get('shape', 'square')}")
        report.append(f"    Scale: {config.get('scale', 8)}")

        features = []
        if config.get("style", {}).get("interactive"):
            features.append("interactive")
        if config.get("style", {}).get("tooltips"):
            features.append("tooltips")
        if not config.get("safe_mode", True):
            features.append("unsafe")

        if features:
            report.append(f"    Features: {', '.join(features)}")

    report_text = "\n".join(report)

    if output_file:
        output_file.write_text(report_text)
        print(f"Report saved to: {output_file}")
    else:
        print(report_text)


def find_similar_configs(baseline_dir: Path, threshold: float = 0.9):
    """Find configurations that are very similar (potential duplicates)."""
    configs = []

    for config_file in baseline_dir.glob("*.baseline_config.json"):
        config_data = json.loads(config_file.read_text())
        configs.append({"file": config_file, "data": config_data, "config": config_data["configuration"]})

    similar_pairs = []

    for i, config1 in enumerate(configs):
        for j, config2 in enumerate(configs[i + 1 :], i + 1):
            similarity = calculate_config_similarity(config1["config"], config2["config"])

            if similarity >= threshold:
                similar_pairs.append(
                    {
                        "file1": config1["file"].name,
                        "file2": config2["file"].name,
                        "similarity": similarity,
                        "differences": find_differences(config1["config"], config2["config"]),
                    }
                )

    return similar_pairs


def calculate_config_similarity(config1: Dict, config2: Dict) -> float:
    """Calculate similarity score between two configurations."""
    # Simple similarity based on matching fields
    all_keys = set()

    def extract_keys(d, prefix=""):
        for k, v in d.items():
            key = f"{prefix}.{k}" if prefix else k
            all_keys.add(key)
            if isinstance(v, dict):
                extract_keys(v, key)

    extract_keys(config1)
    extract_keys(config2)

    matches = 0
    for key in all_keys:
        val1 = get_nested_value(config1, key)
        val2 = get_nested_value(config2, key)
        if val1 == val2:
            matches += 1

    return matches / len(all_keys) if all_keys else 0


def get_nested_value(d: Dict, key: str, default=None):
    """Get value from nested dict using dot notation."""
    keys = key.split(".")
    value = d

    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return default

    return value


def find_differences(config1: Dict, config2: Dict) -> List[str]:
    """Find differences between two configurations."""
    differences = []

    def compare_dicts(d1, d2, path=""):
        all_keys = set(d1.keys()) | set(d2.keys())

        for key in all_keys:
            current_path = f"{path}.{key}" if path else key

            if key not in d1:
                differences.append(f"{current_path}: missing in config1")
            elif key not in d2:
                differences.append(f"{current_path}: missing in config2")
            elif isinstance(d1[key], dict) and isinstance(d2[key], dict):
                compare_dicts(d1[key], d2[key], current_path)
            elif d1[key] != d2[key]:
                differences.append(f"{current_path}: {d1[key]} != {d2[key]}")

    compare_dicts(config1, config2)
    return differences


def find_active_baselines(test_files: List[Path]) -> Dict[str, List[str]]:
    """Find all baseline names that are actively used by test files."""
    active_baselines = {"svg": set(), "config": set()}

    for test_file in test_files:
        content = test_file.read_text()

        # Look for baseline usage patterns in test files
        import re

        # Pattern 1: direct baseline file references
        svg_patterns = [
            r'["\']([^"\']+)\.baseline\.svg["\']',
            r'baseline_path.*["\']([^"\']+)["\']',
            r'f["\'][^"\']*{([^}]+)}\.baseline\.svg["\']',
        ]

        config_patterns = [
            r'["\']([^"\']+)\.baseline_config\.json["\']',
            r'baseline_config.*["\']([^"\']+)["\']',
        ]

        # Extract baseline names from test files
        for pattern in svg_patterns:
            matches = re.findall(pattern, content)
            active_baselines["svg"].update(matches)

        for pattern in config_patterns:
            matches = re.findall(pattern, content)
            active_baselines["config"].update(matches)

        # Pattern 2: parameterized test names
        param_patterns = [r"@pytest\.mark\.parametrize.*\[([^\]]+)\]", r"test_[^(]*\(.*([a-zA-Z_]+).*\)"]

        for pattern in param_patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
            for match in matches:
                # Extract test parameter values
                if isinstance(match, str):
                    # Clean up parameter strings to get baseline names
                    cleaned = re.sub(r'["\',\s()]', " ", match)
                    tokens = cleaned.split()
                    for token in tokens:
                        if token and not token.startswith(("True", "False", "None")):
                            if "_" in token or "-" in token:  # Likely a test name
                                active_baselines["svg"].add(token)

    return {"svg": list(active_baselines["svg"]), "config": list(active_baselines["config"])}


def identify_orphaned_baselines(baseline_dir: Path) -> Dict[str, List[Path]]:
    """Identify baseline files that are no longer referenced by any tests."""

    # Find all test files
    test_files = []

    # Get project root from script location
    project_root = Path(__file__).parent.parent

    # Find visual regression test files specifically
    test_files.extend(project_root.glob("tests/test_visual_regression*.py"))
    test_files.extend(project_root.glob("tests/**/test_*visual*.py"))

    print(f"Found {len(test_files)} test files to analyze")

    # Find actively referenced baselines
    active = find_active_baselines(test_files)

    # Find all existing baselines
    existing_svg = list(baseline_dir.glob("*.baseline.svg"))
    existing_config = list(baseline_dir.glob("*.baseline_config.json"))

    # Identify orphans
    orphaned = {"svg": [], "config": [], "pairs": []}  # SVG+Config pairs that are both orphaned

    # Check SVG files
    for svg_file in existing_svg:
        basename = svg_file.stem.replace(".baseline", "")
        if not any(basename in active_name or active_name in basename for active_name in active["svg"]):
            orphaned["svg"].append(svg_file)

    # Check config files
    for config_file in existing_config:
        basename = config_file.stem.replace(".baseline_config", "")
        if not any(basename in active_name or active_name in basename for active_name in active["config"]):
            orphaned["config"].append(config_file)

    # Find orphaned pairs (both SVG and config are orphaned)
    svg_basenames = {f.stem.replace(".baseline", "") for f in orphaned["svg"]}
    config_basenames = {f.stem.replace(".baseline_config", "") for f in orphaned["config"]}

    paired_orphans = svg_basenames & config_basenames
    for basename in paired_orphans:
        orphaned["pairs"].append(baseline_dir / f"{basename}.baseline.svg")
        orphaned["pairs"].append(baseline_dir / f"{basename}.baseline_config.json")

    return orphaned


def clean_orphaned_baselines(baseline_dir: Path, dry_run: bool = True) -> Dict[str, int]:
    """Clean up orphaned baseline files."""

    orphaned = identify_orphaned_baselines(baseline_dir)

    results = {"svg_removed": 0, "config_removed": 0, "total_removed": 0}

    all_orphans = orphaned["svg"] + orphaned["config"]

    if not all_orphans:
        print("✅ No orphaned baselines found!")
        return results

    print(f"\n🧹 Found {len(all_orphans)} orphaned baseline files:")

    for orphan in all_orphans:
        print(f"  - {orphan.name}")

        if not dry_run:
            orphan.unlink()
            if orphan.suffix == ".svg":
                results["svg_removed"] += 1
            else:
                results["config_removed"] += 1
            results["total_removed"] += 1

    if dry_run:
        print(f"\n🔍 DRY RUN: Would remove {len(all_orphans)} files")
        print("Run with --no-dry-run to actually delete these files")
    else:
        print(f"\n✅ Removed {results['total_removed']} orphaned baseline files")
        print(f"   - SVG files: {results['svg_removed']}")
        print(f"   - Config files: {results['config_removed']}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Manage visual regression baselines with configuration tracking"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze baseline configurations")
    analyze_parser.add_argument(
        "--baseline-dir",
        type=Path,
        default=Path("tests/visual/baseline"),
        help="Directory containing baseline files",
    )
    analyze_parser.add_argument("--output", type=Path, help="Output file for analysis report")

    # Check drift command
    drift_parser = subparsers.add_parser("check-drift", help="Check for configuration drift")
    drift_parser.add_argument(
        "--baseline-dir",
        type=Path,
        default=Path("tests/visual/baseline"),
        help="Directory containing baseline files",
    )

    # Regenerate command
    regen_parser = subparsers.add_parser("regenerate", help="Regenerate baselines from configurations")
    regen_parser.add_argument("config_file", type=Path, help="Configuration file to regenerate from")
    regen_parser.add_argument("--output-dir", type=Path, help="Output directory for regenerated files")

    # Find similar command
    similar_parser = subparsers.add_parser("find-similar", help="Find similar configurations")
    similar_parser.add_argument(
        "--baseline-dir",
        type=Path,
        default=Path("tests/visual/baseline"),
        help="Directory containing baseline files",
    )
    similar_parser.add_argument("--threshold", type=float, default=0.9, help="Similarity threshold (0-1)")

    # Clean orphaned command
    clean_parser = subparsers.add_parser(
        "clean-orphaned", help="Remove orphaned baseline files no longer used by tests"
    )
    clean_parser.add_argument(
        "--baseline-dir",
        type=Path,
        default=Path("tests/visual/baseline"),
        help="Directory containing baseline files",
    )
    clean_parser.add_argument(
        "--no-dry-run", action="store_true", help="Actually delete files (default is dry-run mode)"
    )

    args = parser.parse_args()

    if args.command == "analyze":
        analysis = analyze_baselines(args.baseline_dir)
        generate_coverage_report(analysis, args.output)

    elif args.command == "check-drift":
        drifts = check_config_drift(args.baseline_dir)
        if drifts:
            print(f"Found {len(drifts)} configuration drifts:")
            for drift in drifts:
                print(f"  {drift['test_name']}: {drift['saved_hash']} != {drift['current_hash']}")
        else:
            print("No configuration drift detected")

    elif args.command == "regenerate":
        success = regenerate_baseline(args.config_file, args.output_dir)
        sys.exit(0 if success else 1)

    elif args.command == "find-similar":
        similar = find_similar_configs(args.baseline_dir, args.threshold)
        if similar:
            print(f"Found {len(similar)} similar configuration pairs:")
            for pair in similar:
                print(f"\n{pair['file1']} <-> {pair['file2']}")
                print(f"  Similarity: {pair['similarity']:.1%}")
                if pair["differences"]:
                    print("  Differences:")
                    for diff in pair["differences"][:5]:  # Show first 5
                        print(f"    - {diff}")
                    if len(pair["differences"]) > 5:
                        print(f"    ... and {len(pair['differences']) - 5} more")
        else:
            print("No similar configurations found")

    elif args.command == "clean-orphaned":
        results = clean_orphaned_baselines(args.baseline_dir, dry_run=not args.no_dry_run)

        if results["total_removed"] > 0:
            print("\n📊 Cleanup Summary:")
            print(f"   Total files processed: {results['total_removed']}")
            print(f"   SVG baselines: {results['svg_removed']}")
            print(f"   Config baselines: {results['config_removed']}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
