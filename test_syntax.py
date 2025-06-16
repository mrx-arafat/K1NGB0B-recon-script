#!/usr/bin/env python3
"""
K1NGB0B ULTIMATE Verification Script
Tests syntax, imports, and basic functionality
"""

import sys
import os

def test_syntax():
    """Test if the script has valid Python syntax."""
    try:
        print("🔍 Testing K1NGB0B ULTIMATE syntax...")
        with open('k1ngb0b_recon.py', 'r') as f:
            source = f.read()

        compile(source, 'k1ngb0b_recon.py', 'exec')
        print("✅ Script syntax is VALID!")
        return True

    except SyntaxError as e:
        print(f"❌ Syntax Error: {e}")
        print(f"   Line {e.lineno}: {e.text}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_imports():
    """Test if the script can be imported."""
    try:
        print("🔍 Testing imports...")
        import k1ngb0b_recon
        print("✅ All imports successful!")
        return True
    except Exception as e:
        print(f"❌ Import Error: {e}")
        return False

def test_classes():
    """Test if main classes can be instantiated."""
    try:
        print("🔍 Testing ULTIMATE classes...")
        import k1ngb0b_recon

        # Test SmartProgressTracker
        tracker = k1ngb0b_recon.SmartProgressTracker("test.com")
        print("✅ SmartProgressTracker: OK")

        # Test SmartOutputManager
        output_mgr = k1ngb0b_recon.SmartOutputManager("test.com")
        print("✅ SmartOutputManager: OK")

        # Test UltimateSubdomainHunter
        hunter = k1ngb0b_recon.UltimateSubdomainHunter("test.com")
        print("✅ UltimateSubdomainHunter: OK")

        print("✅ All ULTIMATE classes working!")
        return True
    except Exception as e:
        print(f"❌ Class Error: {e}")
        return False

def main():
    """Run all tests."""
    print("🔥 K1NGB0B ULTIMATE Verification")
    print("=" * 50)

    tests = [
        ("Syntax Check", test_syntax),
        ("Import Check", test_imports),
        ("Class Check", test_classes)
    ]

    passed = 0
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} FAILED!")

    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("🔥 K1NGB0B ULTIMATE is ready for maximum subdomain hunting!")
        print("🚀 Run: python3 k1ngb0b_recon.py")
        return 0
    else:
        print("🔧 Please fix issues before running")
        return 1

if __name__ == "__main__":
    sys.exit(main())
