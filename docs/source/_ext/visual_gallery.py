"""Sphinx extension to auto-generate a visual gallery from test baselines.

Scans ``tests/visual/baseline`` for representative images, copies them into
``docs/_static/visual-baselines/``, and generates an ``.rst`` page that is
included in the documentation.

Configuration (optional via conf.py):
 - visual_gallery_baseline_dir: Absolute or relative path to baseline dir.
 - visual_gallery_output: Relative to docs source (default: 'visual-gallery.rst').
 - visual_gallery_copy_to_static: Whether to copy images to _static (default: True).
 - visual_gallery_max_shape_pairs: Limit number of shape pairs (0 = no limit).
"""

from __future__ import annotations

import os
import re
import shutil
from glob import glob
from typing import Any, Dict, List, Tuple


def _title_from_slug(slug: str) -> str:
    slug = slug.replace("_", " ").replace("-", " ")
    return slug.strip().title()


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _default_baseline_dir(confdir: str) -> str:
    # confdir is docs/source. Baselines are at repo_root/tests/visual/baseline
    repo_root = os.path.abspath(os.path.join(confdir, "..", ".."))
    return os.path.join(repo_root, "tests", "visual", "baseline")


def _find_shape_pairs(baseline_dir: str) -> List[Tuple[str, str, str]]:
    """Find (shape_name, safe_on_path, safe_off_path) pairs.

    Deduplicates by shape name and prefers SVG over PNG when both exist.
    """
    pairs: List[Tuple[str, str, str]] = []
    seen: set[str] = set()

    # Process SVG first to ensure preference, then PNG as fallback
    for pattern in ("*_safe_on.baseline.svg", "*_safe_on.baseline.png"):
        for on_path in sorted(glob(os.path.join(baseline_dir, pattern))):
            base = os.path.basename(on_path)
            stem = re.sub(r"_safe_on\.baseline\.(svg|png)$", "", base)

            if stem in seen:
                continue

            off_svg = os.path.join(baseline_dir, f"{stem}_safe_off.baseline.svg")
            off_png = os.path.join(baseline_dir, f"{stem}_safe_off.baseline.png")

            # Prefer SVG for ON if available
            svg_candidate_on = os.path.join(baseline_dir, f"{stem}_safe_on.baseline.svg")
            on_final = svg_candidate_on if os.path.exists(svg_candidate_on) else on_path

            # Prefer SVG for OFF if available
            if os.path.exists(off_svg):
                off_final = off_svg
            elif os.path.exists(off_png):
                off_final = off_png
            else:
                continue

            pairs.append((stem, on_final, off_final))
            seen.add(stem)

    return pairs


def _find_colors(baseline_dir: str) -> List[str]:
    # Prefer SVG colors_*.baseline.svg; fall back to PNG
    svgs = sorted(glob(os.path.join(baseline_dir, "colors_*.baseline.svg")))
    if svgs:
        return svgs
    return sorted(glob(os.path.join(baseline_dir, "colors_*.png")))


def _find_complex(baseline_dir: str) -> List[str]:
    candidates = [
        "complex_full_config.baseline.svg",
        "combined_effects.png",
        "complex_content_qr.png",
    ]
    results: List[str] = []
    for name in candidates:
        path = os.path.join(baseline_dir, name)
        if os.path.exists(path):
            results.append(path)
    return results


def _copy_to_static(paths: List[str], static_dir: str) -> Dict[str, str]:
    """Copy given files to static_dir and return a map src_path -> web_path."""
    _ensure_dir(static_dir)
    mapping: Dict[str, str] = {}
    for src in paths:
        # Keep original filename
        filename = os.path.basename(src)
        dst = os.path.join(static_dir, filename)
        shutil.copy2(src, dst)
        # Use relative path so it works regardless of base URL
        mapping[src] = f"_static/visual-baselines/{filename}"
    return mapping


def _generate_rst(
    shapes: List[Tuple[str, str, str]],
    path_map: Dict[str, str],
    colors: List[str],
    complex_items: List[str],
) -> str:
    lines: List[str] = []
    lines.append("Visual Baselines")
    lines.append("=" * len("Visual Baselines"))
    lines.append("")
    lines.append(
        "This page is auto-generated from the visual regression baselines in ``tests/visual/baseline``."
    )
    lines.append("")

    if shapes:
        lines.append("Safe Mode Comparisons")
        lines.append("----------------------")
        lines.append("")
        for shape, on_src, off_src in shapes:
            title = _title_from_slug(shape)
            lines.append(title)
            lines.append("~" * len(title))
            lines.append("")
            on_url = path_map.get(on_src, on_src)
            off_url = path_map.get(off_src, off_src)
            lines.append(".. list-table::")
            lines.append("   :header-rows: 1")
            lines.append("")
            lines.append("   * - Safe Mode ON")
            lines.append("     - Safe Mode OFF")
            lines.append(
                f"   * - .. image:: {on_url}\n"
                f"         :width: 220\n"
                f"         :alt: {title} safe mode on\n"
                f"     - .. image:: {off_url}\n"
                f"         :width: 220\n"
                f"         :alt: {title} safe mode off"
            )
            lines.append("")

    if colors:
        lines.append("Color Palettes")
        lines.append("---------------")
        lines.append("")
        for path in colors:
            title = _title_from_slug(os.path.splitext(os.path.basename(path))[0])
            url = path_map.get(path, path)
            lines.append(title)
            lines.append("~" * len(title))
            lines.append("")
            lines.append(f".. image:: {url}")
            lines.append("   :width: 300")
            lines.append(f"   :alt: {title}")
            lines.append("")

    if complex_items:
        lines.append("Complex Examples")
        lines.append("----------------")
        lines.append("")
        for path in complex_items:
            title = _title_from_slug(os.path.splitext(os.path.basename(path))[0])
            url = path_map.get(path, path)
            lines.append(title)
            lines.append("~" * len(title))
            lines.append("")
            lines.append(f".. image:: {url}")
            lines.append("   :width: 320")
            lines.append(f"   :alt: {title}")
            lines.append("")

    if not (shapes or colors or complex_items):
        lines.append("No baselines found.")
        lines.append("Ensure tests/visual/baseline exists and is checked into the repository.")

    return "\n".join(lines) + "\n"


def _limit_pairs(pairs: List[Tuple[str, str, str]], limit: int) -> List[Tuple[str, str, str]]:
    if limit and limit > 0:
        return pairs[:limit]
    return pairs


def on_builder_inited(app: Any) -> None:
    confdir = app.confdir  # docs/source
    srcdir = app.srcdir
    out_page = getattr(app.config, "visual_gallery_output", "visual-gallery.rst")
    copy_to_static = getattr(app.config, "visual_gallery_copy_to_static", True)
    max_pairs = getattr(app.config, "visual_gallery_max_shape_pairs", 0)

    baseline_dir = getattr(app.config, "visual_gallery_baseline_dir", None)
    if not baseline_dir:
        baseline_dir = _default_baseline_dir(confdir)
    if not os.path.isabs(baseline_dir):
        baseline_dir = os.path.abspath(os.path.join(confdir, baseline_dir))

    shapes = _find_shape_pairs(baseline_dir)
    shapes = _limit_pairs(shapes, max_pairs)
    colors = _find_colors(baseline_dir)
    complex_items = _find_complex(baseline_dir)

    all_paths: List[str] = []
    for _, onp, offp in shapes:
        all_paths.extend([onp, offp])
    all_paths.extend(colors)
    all_paths.extend(complex_items)

    path_map: Dict[str, str] = {}
    if copy_to_static and all_paths:
        static_dir = os.path.join(srcdir, "_static", "visual-baselines")
        path_map = _copy_to_static(all_paths, static_dir)

    rst = _generate_rst(shapes, path_map, colors, complex_items)
    out_path = os.path.join(srcdir, out_page)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(rst)


def setup(app: Any) -> Dict[str, Any]:
    app.add_config_value("visual_gallery_baseline_dir", default=None, rebuild="html")
    app.add_config_value("visual_gallery_output", default="visual-gallery.rst", rebuild="html")
    app.add_config_value("visual_gallery_copy_to_static", default=True, rebuild="html")
    app.add_config_value("visual_gallery_max_shape_pairs", default=0, rebuild="html")
    app.connect("builder-inited", on_builder_inited)
    return {"version": "0.1", "parallel_read_safe": True}
