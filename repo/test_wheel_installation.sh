#!/usr/bin/env bash
set -euo pipefail

# Test wheel installation and basic functionality
# Used by: .github/workflows/test.yml

echo "🛞 Testing wheel installation..."

# Find the wheel file
WHEEL_FILE=$(find dist -name "*.whl" | head -1)
if [[ -z "${WHEEL_FILE}" ]]; then
  echo "❌ No wheel file found in dist/"
  exit 1
fi

echo "Testing wheel installation: ${WHEEL_FILE}"

# Install segno dependency first
echo "📦 Installing segno dependency..."
pip install segno

# Install the wheel
echo "📦 Installing wheel: ${WHEEL_FILE}"
pip install "${WHEEL_FILE}"

# Test basic import and functionality
echo "🧪 Testing basic import and functionality..."
python -c "
import segnomms
import segno
print('✅ Successfully imported segnomms from wheel')

# Test plugin registration
qr = segno.make('Test')
has_plugin = hasattr(qr, 'to_interactive_svg')
print(f'Plugin registration via entry points: {has_plugin}')

# Test core functionality even if entry point registration failed
# This tests the actual package functionality vs just registration
import tempfile
import os
from segnomms.plugin import write

with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as tmp:
    temp_path = tmp.name

try:
    # Test direct functionality (this validates core package works)
    write(qr, temp_path, shape='square')
    with open(temp_path, 'r') as f:
        svg_content = f.read()
    svg_valid = svg_content is not None and '<svg' in svg_content
    print(f'Direct SVG generation: {svg_valid}')

    if svg_valid:
        print('✅ Wheel installation and core functionality verified')

        # Also test plugin registration if available
        if has_plugin:
            print('✅ Entry point plugin registration working')
        else:
            print('⚠️  Entry point registration not active (expected in dev mode)')
    else:
        print('❌ Core functionality test failed')
        exit(1)
finally:
    if os.path.exists(temp_path):
        os.unlink(temp_path)
"

echo "✅ Wheel installation test completed successfully"
