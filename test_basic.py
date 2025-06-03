#!/usr/bin/env python3
"""
Basic test to verify the project structure is correct.
"""

import sys
import os
from pathlib import Path

def test_project_structure():
    """Test that all required files and directories exist."""
    
    required_files = [
        "README.md",
        "requirements.txt",
        "setup.py",
        "config.yaml",
        "install.sh",
        "src/k1ngb0b_recon/__init__.py",
        "src/k1ngb0b_recon/__main__.py",
        "src/k1ngb0b_recon/main.py",
        "src/k1ngb0b_recon/config.py",
        "src/k1ngb0b_recon/subdomain_discovery.py",
        "src/k1ngb0b_recon/utils.py",
        "tests/__init__.py",
        "tests/test_utils.py",
        "scripts/quick_install.sh"
    ]
    
    required_dirs = [
        "src",
        "src/k1ngb0b_recon",
        "tests",
        "scripts"
    ]
    
    print("Testing project structure...")
    
    # Test directories
    for directory in required_dirs:
        if Path(directory).exists() and Path(directory).is_dir():
            print(f"✓ Directory exists: {directory}")
        else:
            print(f"✗ Directory missing: {directory}")
            return False
    
    # Test files
    for file_path in required_files:
        if Path(file_path).exists() and Path(file_path).is_file():
            print(f"✓ File exists: {file_path}")
        else:
            print(f"✗ File missing: {file_path}")
            return False
    
    print("\n✓ All required files and directories exist!")
    return True

def test_file_contents():
    """Test that key files have expected content."""

    print("\nTesting file contents...")

    try:
        # Test that main files have expected classes/functions
        files_to_check = {
            "src/k1ngb0b_recon/config.py": ["class Config", "class ToolConfig"],
            "src/k1ngb0b_recon/utils.py": ["def validate_domain", "def sanitize_filename"],
            "src/k1ngb0b_recon/subdomain_discovery.py": ["class SubdomainDiscovery"],
            "src/k1ngb0b_recon/main.py": ["class ReconApp", "def main"],
            "requirements.txt": ["click", "requests", "aiohttp"],
            "setup.py": ["name=\"k1ngb0b-recon\"", "version=\"2.0.0\""]
        }

        for file_path, expected_content in files_to_check.items():
            if not Path(file_path).exists():
                print(f"✗ File missing: {file_path}")
                return False

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            for expected in expected_content:
                if expected in content:
                    print(f"✓ Found '{expected}' in {file_path}")
                else:
                    print(f"✗ Missing '{expected}' in {file_path}")
                    return False

        print("✓ All files have expected content")
        return True

    except Exception as e:
        print(f"✗ Error checking file contents: {e}")
        return False

def main():
    """Run all tests."""
    print("K1NGB0B Recon Script - Basic Project Test")
    print("=" * 50)
    
    structure_ok = test_project_structure()
    content_ok = test_file_contents()

    print("\n" + "=" * 50)
    if structure_ok and content_ok:
        print("✓ All basic tests passed!")
        print("\nNext steps:")
        print("1. Run: chmod +x install.sh")
        print("2. Run: ./install.sh")
        print("3. Test: python -m k1ngb0b_recon --help")
        return 0
    else:
        print("✗ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
