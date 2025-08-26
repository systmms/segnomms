#!/usr/bin/env python3
"""Test all HTML example pages to verify they're working."""

from pathlib import Path
from urllib.parse import urljoin

import requests


def test_example_pages():
    """Test all HTML example pages."""
    examples_dir = Path(__file__).parent
    base_url = "http://localhost:8000/examples/"

    # Find all HTML files
    html_files = sorted(examples_dir.glob("*.html"))

    print(f"Found {len(html_files)} HTML files to test")
    print("-" * 60)

    results = []

    for html_file in html_files:
        if html_file.name.startswith(("_", ".")):
            continue

        url = urljoin(base_url, html_file.name)
        print(f"\nTesting: {html_file.name}")
        print(f"URL: {url}")

        try:
            # Check if page loads
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                # Check for common error patterns in the response
                content = response.text.lower()
                errors = []

                if "failed to fetch" in content:
                    errors.append("Contains 'failed to fetch' error")
                if "404" in content and "not found" in content:
                    errors.append("Contains 404 error")
                if "error:" in content:
                    # Check if it's a real error (not just in comments or examples)
                    error_lines = [
                        line
                        for line in response.text.split("\n")
                        if "error:" in line.lower() and not line.strip().startswith(("<!--", "//", "*"))
                    ]
                    if error_lines:
                        errors.append(f"Contains error messages: {len(error_lines)} occurrences")

                if errors:
                    status = "FAIL - " + ", ".join(errors)
                else:
                    status = "PASS"
            else:
                status = f"FAIL - HTTP {response.status_code}"

        except requests.exceptions.RequestException as e:
            status = f"FAIL - {type(e).__name__}: {str(e)}"

        results.append((html_file.name, status))
        print(f"Status: {status}")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, status in results if status == "PASS")
    failed = len(results) - passed

    print(f"\nTotal: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed > 0:
        print("\nFailed pages:")
        for name, status in results:
            if status != "PASS":
                print(f"  - {name}: {status}")

    return failed == 0


if __name__ == "__main__":
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000", timeout=2)
        print("Server is running")
    except:
        print("ERROR: Server not running at http://localhost:8000")
        print("Please start the server with: python -m http.server 8000")
        exit(1)

    success = test_example_pages()
    exit(0 if success else 1)
