#!/usr/bin/env python3
"""
Deploy beta versions to Google Cloud Artifact Registry.

This script:
1. Reads current version from pyproject.toml
2. Increments beta number (beta001, beta002, etc.)
3. Builds the package with the next version
4. Deploys to Google Cloud Artifact Registry
5. Only updates version in files after successful deployment
"""

import re
import subprocess
import sys
from pathlib import Path
import shutil
from glob import glob


def get_current_version():
    """Read current version from pyproject.toml."""
    pyproject = Path("pyproject.toml").read_text()
    match = re.search(r'version = "([^"]+)"', pyproject)
    if not match:
        raise ValueError("Could not find version in pyproject.toml")
    return match.group(1)


def get_next_beta_version(current_version):
    """Calculate next beta version number using PEP 440 format."""
    # Check if already a beta version (PEP 440 format: 0.0.0b1)
    beta_match = re.match(r'(.+)b(\d+)', current_version)
    
    if beta_match:
        base_version = beta_match.group(1)
        beta_num = int(beta_match.group(2))
        next_beta = beta_num + 1
    else:
        # First beta for this version
        base_version = current_version
        next_beta = 1
    
    # Format using PEP 440 (b1, b2, etc. - no leading zeros)
    return f"{base_version}b{next_beta}"


def update_version_in_file(filepath, old_version, new_version):
    """Update version string in a file."""
    content = Path(filepath).read_text()
    
    # Handle different version patterns
    patterns = [
        (f'version = "{old_version}"', f'version = "{new_version}"'),
        (f'__version__ = "{old_version}"', f'__version__ = "{new_version}"'),
        (f'"{old_version}"', f'"{new_version}"'),  # For .release-please-manifest.json
    ]
    
    updated = False
    for old_pattern, new_pattern in patterns:
        if old_pattern in content:
            content = content.replace(old_pattern, new_pattern)
            updated = True
    
    if updated:
        Path(filepath).write_text(content)
        return True
    return False


def update_all_versions(old_version, new_version):
    """Update version in all project files."""
    files_to_update = [
        "pyproject.toml",
        "segnomms/__init__.py",
        "package.json",
        ".github/.release-please-manifest.json",
        "scripts/build_wheel.py",
    ]
    
    print(f"Updating version from {old_version} to {new_version}")
    
    for filepath in files_to_update:
        if Path(filepath).exists():
            if update_version_in_file(filepath, old_version, new_version):
                print(f"  ✓ Updated {filepath}")
            else:
                print(f"  ⚠ No version found in {filepath}")


def build_package(version):
    """Build the Python package with a specific version."""
    print("\nBuilding package...")
    
    # Clean previous builds
    subprocess.run("rm -rf dist/ build/ *.egg-info", shell=True)
    
    # Create a temporary pyproject.toml with the new version
    pyproject_path = Path("pyproject.toml")
    pyproject_backup = Path("pyproject.toml.backup")
    
    # Backup current pyproject.toml
    shutil.copy2(pyproject_path, pyproject_backup)
    
    try:
        # Update version in pyproject.toml temporarily
        content = pyproject_path.read_text()
        current_version_match = re.search(r'version = "([^"]+)"', content)
        if current_version_match:
            current_version_str = current_version_match.group(0)
            new_version_str = f'version = "{version}"'
            content = content.replace(current_version_str, new_version_str)
            pyproject_path.write_text(content)
        
        # Build wheel and source distribution
        result = subprocess.run(
            [sys.executable, "-m", "build"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"Build failed: {result.stderr}")
            return False
        
        print("  ✓ Package built successfully")
        return True
        
    finally:
        # Always restore the original pyproject.toml
        shutil.move(pyproject_backup, pyproject_path)


def deploy_to_gcloud_registry(version):
    """Deploy package to Google Cloud Artifact Registry."""
    print("\nDeploying to Google Cloud Artifact Registry...")
    
    # Configuration
    project_id = "segnomms"
    location = "us-central1"
    repository = "prerelease"
    
    # Check if gcloud is authenticated
    result = subprocess.run(
        ["gcloud", "auth", "list", "--filter=status:ACTIVE", "--format=value(account)"],
        capture_output=True,
        text=True
    )
    
    if not result.stdout.strip():
        print("  gcloud responded with: " + result.stdout.strip())
        print("  ⚠ Not authenticated with gcloud")
        print("  To deploy, run: gcloud auth login")
        print("\nDeployment cancelled - not authenticated")
        return False
    
    # Configure repository URL
    repository_url = f"https://{location}-python.pkg.dev/{project_id}/{repository}/"
    
    # Upload to Google Cloud Artifact Registry
    cmd = [
        sys.executable, "-m", "twine", "upload",
        "--repository-url", repository_url,
        *glob("dist/*")
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"  ✗ Upload failed: {result.stderr}")
        print("\nTroubleshooting:")
        print("1. Ensure you have the required packages:")
        print("   pip install keyring keyrings.google-artifactregistry-auth")
        print("2. Authenticate with: gcloud auth application-default login")
        return False
    
    print(f"  ✓ Successfully deployed version {version} to Google Cloud Artifact Registry")
    print(f"\nInstall with:")
    print(f"  pip install --index-url {repository_url}simple segnomms=={version}")
    return True


def main():
    """Main deployment process."""
    print("Google Cloud Artifact Registry Beta Deployment")
    print("==============================================\n")
    
    # Ensure we're in the project root
    if not Path("pyproject.toml").exists():
        print("Error: Must run from project root directory")
        sys.exit(1)
    
    # Check if build tool is installed
    try:
        import build
    except ImportError:
        print("Installing build tool...")
        subprocess.run([sys.executable, "-m", "pip", "install", "build", "twine"])
    
    # Get current and next version
    current_version = get_current_version()
    next_version = get_next_beta_version(current_version)
    
    print(f"Current version: {current_version}")
    print(f"Next version: {next_version}")
    
    # Skip confirmation - proceed with deployment
    print("\nProceeding with deployment...")
    
    # Build package with next version (temporarily)
    if not build_package(next_version):
        print("\n❌ Build failed. Version not updated.")
        sys.exit(1)
    
    # Deploy to Google Cloud Artifact Registry
    if not deploy_to_gcloud_registry(next_version):
        print("\n❌ Deployment failed. Version not updated.")
        sys.exit(1)
    
    # Only update versions after successful deployment
    print("\nDeployment successful! Updating version files...")
    update_all_versions(current_version, next_version)
    
    # Show next steps
    project_id = "segnomms"
    location = "us-central1"
    repository = "prerelease"
    repository_url = f"https://{location}-python.pkg.dev/{project_id}/{repository}/"
    
    print("\n✅ Deployment complete!")
    print(f"\nNext steps:")
    print(f"1. Test the package:")
    print(f"   pip install --index-url {repository_url}simple segnomms=={next_version}")
    print(f"2. Commit the version changes:")
    print(f"   git add -A && git commit -m 'chore: release {next_version}'")
    print(f"3. Push the changes:")
    print(f"   git push")


if __name__ == "__main__":
    main()