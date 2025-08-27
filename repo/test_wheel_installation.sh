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
has_plugin = hasattr(qr, 'interactive_svg')
print(f'Plugin registration: {has_plugin}')

if has_plugin:
    svg = qr.interactive_svg()
    svg_valid = svg is not None and '<svg' in str(svg)
    print(f'SVG generation: {svg_valid}')
    print('✅ Wheel test completed successfully')
else:
    print('❌ Plugin not registered properly')
    exit(1)
"

echo "✅ Wheel installation test completed successfully"
