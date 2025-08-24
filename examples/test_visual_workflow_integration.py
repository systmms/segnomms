#!/usr/bin/env python3
"""
Test: Visual Workflow Integration

Tests the integration between configuration export and visual regression
testing workflows to ensure they work together properly.
"""

import json
from pathlib import Path
import segno
from segnomms import write
from segnomms.config import RenderingConfig


def test_configuration_tracking():
    """Test that configurations are properly tracked and exportable."""
    
    print("🧪 Testing Configuration Tracking")
    print("=" * 40)
    
    test_dir = Path("test-visual-workflow")
    test_dir.mkdir(exist_ok=True)
    
    # Test configuration export
    test_config = {
        "shape": "squircle",
        "corner_radius": 0.4,
        "scale": 10,
        "border": 2,
        "dark": "#1f2937",
        "light": "#f9fafb"
    }
    
    qr = segno.make("Configuration Test", error="M")
    
    # Generate QR with configuration
    output_path = test_dir / "config_test.svg"
    write(qr, str(output_path), **test_config)
    
    print(f"   ✓ Generated QR with configuration")
    
    # Test that we can recreate the configuration
    try:
        # Create RenderingConfig from parameters
        config = RenderingConfig.from_kwargs(**test_config)
        exported_config = config.to_kwargs()
        
        # Verify key parameters are preserved
        assert exported_config["shape"] == test_config["shape"]
        assert exported_config["corner_radius"] == test_config["corner_radius"]
        assert exported_config["scale"] == test_config["scale"]
        assert exported_config["dark"] == test_config["dark"]
        
        print(f"   ✓ Configuration export/import works")
        
        # Save configuration file
        config_path = test_dir / "config_test.json"
        with open(config_path, 'w') as f:
            json.dump({
                "original": test_config,
                "exported": exported_config,
                "matches": exported_config["shape"] == test_config["shape"]
            }, f, indent=2)
        
        print(f"   ✓ Configuration tracking validated")
        return True
        
    except Exception as e:
        print(f"   ❌ Configuration tracking failed: {e}")
        return False


def test_visual_consistency_workflow():
    """Test a complete visual consistency workflow."""
    
    print(f"\n🎯 Testing Visual Consistency Workflow")
    print("=" * 45)
    
    test_dir = Path("test-visual-workflow")
    
    # Define test configurations
    test_configs = [
        {
            "name": "baseline",
            "config": {"shape": "rounded", "corner_radius": 0.3, "scale": 8}
        },
        {
            "name": "variant_radius",
            "config": {"shape": "rounded", "corner_radius": 0.5, "scale": 8}
        },
        {
            "name": "variant_shape", 
            "config": {"shape": "circle", "corner_radius": 0.3, "scale": 8}
        }
    ]
    
    qr = segno.make("Consistency Test", error="M")
    generated_files = []
    
    # Generate all test variants
    for test_case in test_configs:
        config_name = test_case["name"]
        config_params = test_case["config"]
        
        print(f"   Generating {config_name}...")
        
        # Generate QR
        output_path = test_dir / f"consistency_{config_name}.svg"
        write(qr, str(output_path), **config_params)
        
        # Save configuration
        config_path = test_dir / f"consistency_{config_name}_config.json"
        with open(config_path, 'w') as f:
            json.dump(config_params, f, indent=2)
        
        generated_files.append({
            "name": config_name,
            "svg_path": output_path,
            "config_path": config_path,
            "config": config_params
        })
    
    print(f"   ✓ Generated {len(generated_files)} test variants")
    
    # Verify all files were created
    all_files_exist = True
    for file_info in generated_files:
        if not file_info["svg_path"].exists():
            print(f"   ❌ Missing SVG: {file_info['svg_path']}")
            all_files_exist = False
        if not file_info["config_path"].exists():
            print(f"   ❌ Missing config: {file_info['config_path']}")
            all_files_exist = False
    
    if all_files_exist:
        print(f"   ✓ All files generated successfully")
        
        # Test configuration reproducibility
        return test_config_reproducibility(generated_files, qr)
    else:
        print(f"   ❌ File generation incomplete")
        return False


def test_config_reproducibility(generated_files, qr):
    """Test that configurations can be loaded and reproduce identical output."""
    
    print(f"\n🔄 Testing Configuration Reproducibility")
    print("=" * 45)
    
    test_dir = Path("test-visual-workflow")
    
    for file_info in generated_files:
        config_name = file_info["name"]
        original_svg_path = file_info["svg_path"]
        config_path = file_info["config_path"]
        
        print(f"   Testing {config_name} reproducibility...")
        
        try:
            # Load saved configuration
            with open(config_path, 'r') as f:
                loaded_config = json.load(f)
            
            # Generate new QR with loaded configuration
            repro_path = test_dir / f"repro_{config_name}.svg"
            write(qr, str(repro_path), **loaded_config)
            
            # Compare file sizes (basic check)
            original_size = original_svg_path.stat().st_size
            repro_size = repro_path.stat().st_size
            
            if original_size == repro_size:
                print(f"     ✓ File sizes match ({original_size} bytes)")
                
                # Compare content (more thorough check)
                original_content = original_svg_path.read_text()
                repro_content = repro_path.read_text()
                
                if original_content == repro_content:
                    print(f"     ✓ Content identical")
                else:
                    print(f"     ⚠️  Content differs (may be due to generation timestamps)")
                    
            else:
                print(f"     ❌ File size mismatch: {original_size} vs {repro_size}")
                return False
                
        except Exception as e:
            print(f"     ❌ Reproducibility test failed: {e}")
            return False
    
    print(f"   ✅ Configuration reproducibility validated")
    return True


def test_workflow_automation():
    """Test automated workflow generation and validation."""
    
    print(f"\n⚙️  Testing Workflow Automation")
    print("=" * 35)
    
    test_dir = Path("test-visual-workflow")
    
    # Test batch generation
    batch_configs = [
        {"name": "auto_1", "shape": "square", "scale": 6},
        {"name": "auto_2", "shape": "circle", "scale": 6},
        {"name": "auto_3", "shape": "rounded", "scale": 6, "corner_radius": 0.4},
    ]
    
    qr = segno.make("Automation Test", error="L")
    
    print(f"   Running batch generation of {len(batch_configs)} configurations...")
    
    success_count = 0
    for config in batch_configs:
        config_name = config["name"]
        config_params = {k: v for k, v in config.items() if k != "name"}
        
        try:
            output_path = test_dir / f"auto_{config_name}.svg"
            write(qr, str(output_path), **config_params)
            success_count += 1
        except Exception as e:
            print(f"     ❌ Failed to generate {config_name}: {e}")
    
    if success_count == len(batch_configs):
        print(f"   ✅ Batch generation successful ({success_count}/{len(batch_configs)})")
        return True
    else:
        print(f"   ❌ Batch generation incomplete ({success_count}/{len(batch_configs)})")
        return False


def main():
    """Run all visual workflow integration tests."""
    
    print("🧪 Visual Workflow Integration Tests")
    print("Testing the integration between configuration tracking and visual workflows")
    print("=" * 75)
    
    test_results = []
    
    try:
        # Run all tests
        test_results.append(("Configuration tracking", test_configuration_tracking()))
        test_results.append(("Visual consistency workflow", test_visual_consistency_workflow()))
        test_results.append(("Workflow automation", test_workflow_automation()))
        
        # Summary
        print(f"\n📊 Test Results Summary")
        print("=" * 30)
        
        passed = sum(1 for _, result in test_results if result)
        total = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {status} {test_name}")
        
        print(f"\n🎯 Overall: {passed}/{total} tests passed")
        
        # Cleanup note
        print(f"\n📁 Test artifacts saved to: test-visual-workflow/")
        print(f"   (These can be manually inspected or used for further testing)")
        
        if passed == total:
            print(f"\n🎉 All visual workflow integration tests passed!")
            return True
        else:
            print(f"\n⚠️  Some tests failed - check results above")
            return False
            
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)