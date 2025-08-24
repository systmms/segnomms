#!/usr/bin/env python3
"""Test segnomms compatibility with different Segno versions."""

import subprocess
import sys
import tempfile
import os
from pathlib import Path

# Segno versions to test (from releases page)
SEGNO_VERSIONS = [
    "1.3.1",   # Sep 2020
    "1.3.3",   # Mar 2021
    "1.4.0",   # Nov 2021
    "1.4.1",   # Nov 2021
    "1.5.2",   # May 2022
    "1.5.3",   # Oct 2023
    "1.6.0",   # Nov 2023 - Dropped Python 2.7, changed plugin system
    "1.6.1",   # Feb 2024
    "1.6.5",   # Mar 2024
    "1.6.6",   # Mar 2024 (current)
]

def test_segno_version(version):
    """Test compatibility with a specific Segno version."""
    print(f"\n{'='*60}")
    print(f"Testing with Segno {version}")
    print('='*60)
    
    # Create a temporary virtual environment
    with tempfile.TemporaryDirectory() as tmpdir:
        venv_path = Path(tmpdir) / "venv"
        
        # Create virtual environment
        subprocess.run([
            sys.executable, "-m", "venv", str(venv_path)
        ], check=True)
        
        # Get paths for the virtual environment
        if sys.platform == "win32":
            python_path = venv_path / "Scripts" / "python.exe"
            pip_path = venv_path / "Scripts" / "pip.exe"
        else:
            python_path = venv_path / "bin" / "python"
            pip_path = venv_path / "bin" / "pip"
        
        try:
            # Install specific Segno version
            print(f"Installing Segno {version}...")
            result = subprocess.run([
                str(pip_path), "install", f"segno=={version}"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Failed to install Segno {version}")
                print(f"Error: {result.stderr}")
                return False
            
            # Install segnomms in development mode
            print("Installing segnomms...")
            result = subprocess.run([
                str(pip_path), "install", "-e", "."
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
            
            if result.returncode != 0:
                print(f"❌ Failed to install segnomms")
                print(f"Error: {result.stderr}")
                return False
            
            # Create test script
            test_script = """
import segno
from segnomms import write

# Test 1: Basic functionality
print("Test 1: Basic QR code generation")
try:
    qr = segno.make('Hello World')
    write(qr, 'test.svg', shape='square')
    print("✓ Basic generation works")
except Exception as e:
    print(f"✗ Basic generation failed: {e}")
    raise

# Test 2: Plugin registration
print("\\nTest 2: Plugin registration")
try:
    # Check if plugin is registered
    qr = segno.make('Test')
    # Try to use the plugin method if available
    if hasattr(qr, 'to_interactive_svg'):
        qr.to_interactive_svg('test2.svg')
        print("✓ Plugin method registration works")
    else:
        # Fallback to direct import
        write(qr, 'test2.svg')
        print("✓ Direct import works (plugin method not available)")
except Exception as e:
    print(f"✗ Plugin registration failed: {e}")
    raise

# Test 3: Shape variations
print("\\nTest 3: Shape variations")
shapes = ['square', 'circle', 'rounded', 'dot', 'star']
for shape in shapes:
    try:
        qr = segno.make(f'Shape: {shape}')
        write(qr, f'test_{shape}.svg', shape=shape)
        print(f"✓ Shape '{shape}' works")
    except Exception as e:
        print(f"✗ Shape '{shape}' failed: {e}")

# Test 4: Advanced features
print("\\nTest 4: Advanced features")
try:
    qr = segno.make('Advanced Test', error='h')
    write(qr, 'test_advanced.svg', 
          shape='connected',
          scale=10,
          dark='#1a1a2e',
          light='#ffffff',
          safe_mode=False)
    print("✓ Advanced features work")
except Exception as e:
    print(f"✗ Advanced features failed: {e}")

print("\\nAll tests completed!")
"""
            
            # Run test script
            print("\nRunning compatibility tests...")
            test_file = Path(tmpdir) / "test_compat.py"
            test_file.write_text(test_script)
            
            result = subprocess.run([
                str(python_path), str(test_file)
            ], capture_output=True, text=True, cwd=tmpdir)
            
            print(result.stdout)
            if result.stderr:
                print("Errors:", result.stderr)
            
            if result.returncode == 0:
                print(f"\n✅ Segno {version} is COMPATIBLE")
                return True
            else:
                print(f"\n❌ Segno {version} is NOT COMPATIBLE")
                return False
                
        except Exception as e:
            print(f"❌ Error testing Segno {version}: {e}")
            return False

def main():
    """Run compatibility tests for all versions."""
    print("Testing segnomms compatibility with different Segno versions")
    print("This will create temporary virtual environments for each test")
    
    results = {}
    
    for version in SEGNO_VERSIONS:
        try:
            results[version] = test_segno_version(version)
        except Exception as e:
            print(f"Failed to test {version}: {e}")
            results[version] = False
    
    # Summary
    print("\n" + "="*60)
    print("COMPATIBILITY SUMMARY")
    print("="*60)
    
    compatible_versions = []
    incompatible_versions = []
    
    for version, is_compatible in results.items():
        if is_compatible:
            compatible_versions.append(version)
            print(f"✅ Segno {version}: COMPATIBLE")
        else:
            incompatible_versions.append(version)
            print(f"❌ Segno {version}: NOT COMPATIBLE")
    
    if compatible_versions:
        print(f"\nEarliest compatible version: {compatible_versions[0]}")
        print(f"Recommended minimum version: segno>={compatible_versions[0]}")
    
    # Update workflow suggestion
    if compatible_versions:
        print("\nSuggested GitHub Actions matrix:")
        print("```yaml")
        print("strategy:")
        print("  matrix:")
        print("    segno-version:")
        # Select key versions for CI testing
        test_versions = []
        if compatible_versions[0] != SEGNO_VERSIONS[-1]:
            test_versions.append(compatible_versions[0])  # Earliest
        if len(compatible_versions) > 2:
            test_versions.append(compatible_versions[len(compatible_versions)//2])  # Middle
        test_versions.append(SEGNO_VERSIONS[-1])  # Latest
        
        for v in test_versions:
            print(f'      - "{v}"')
        print("```")

if __name__ == "__main__":
    main()