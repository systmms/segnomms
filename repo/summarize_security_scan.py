#!/usr/bin/env python3
"""
Summarize Bandit security scan results to GitHub Step Summary.

Usage:
  python repo/summarize_security_scan.py [--report bandit-report.json]

Behavior:
- Reads the Bandit JSON report (default: bandit-report.json)
- Writes a Markdown summary to $GITHUB_STEP_SUMMARY if set; otherwise stdout
- Includes severity counts and a collapsible table of top findings
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, List


def write_line(dest: str | None, line: str = "") -> None:
    if dest:
        with open(dest, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    else:
        print(line)


def escape_md(text: str | None) -> str:
    if not text:
        return ""
    return text.replace("|", "\\|").replace("\n", " ")


def summarize(report_path: str, summary_path: str | None) -> int:
    write_line(summary_path, "## Security Scan (Bandit)")

    if not os.path.exists(report_path):
        write_line(summary_path, "- No bandit-report.json found")
        return 0

    with open(report_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    results: List[Dict] = data.get("results", [])  # type: ignore[assignment]
    sev_order = ["HIGH", "MEDIUM", "LOW"]
    sev_counts = {s: 0 for s in sev_order}
    for r in results:
        s = str(r.get("issue_severity") or "LOW").upper()
        if s in sev_counts:
            sev_counts[s] += 1

    total = len(results)
    write_line(summary_path, f"- Findings: {total}")
    write_line(summary_path)
    write_line(summary_path, "| Severity | Count |")
    write_line(summary_path, "| --- | ---: |")
    for s in sev_order:
        write_line(summary_path, f"| {s} | {sev_counts[s]} |")

    if results:
        write_line(summary_path, "\n<details><summary>Top findings</summary>\n")
        write_line(summary_path, "| Severity | Confidence | ID | File | Line | Message |")
        write_line(summary_path, "| --- | --- | --- | --- | ---: | --- |")

        sev_rank = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
        conf_rank = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
        top = sorted(
            results,
            key=lambda r: (
                -sev_rank.get(str(r.get("issue_severity") or "LOW").upper(), 0),
                -conf_rank.get(str(r.get("issue_confidence") or "LOW").upper(), 0),
            ),
        )[:10]

        for r in top:
            write_line(
                summary_path,
                "| {} | {} | {} | {} | {} | {} |".format(
                    r.get("issue_severity"),
                    r.get("issue_confidence"),
                    r.get("test_id"),
                    escape_md(r.get("filename")),
                    r.get("line_number"),
                    escape_md(r.get("issue_text")),
                ),
            )
        write_line(summary_path, "\n</details>")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize Bandit results to step summary")
    parser.add_argument(
        "--report",
        default="bandit-report.json",
        help="Path to Bandit JSON report (default: bandit-report.json)",
    )
    args = parser.parse_args()

    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    return summarize(args.report, summary_path)


if __name__ == "__main__":
    sys.exit(main())
