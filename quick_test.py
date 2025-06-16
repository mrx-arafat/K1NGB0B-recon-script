#!/usr/bin/env python3
"""
Quick test for K1NGB0B ULTIMATE to verify the KeyError fix
"""

import sys
import asyncio

def test_progress_tracker():
    """Test SmartProgressTracker to ensure no KeyError."""
    try:
        from k1ngb0b_recon import SmartProgressTracker
        
        print("🔍 Testing SmartProgressTracker...")
        tracker = SmartProgressTracker("test.com")
        
        # Test normal flow
        tracker.start_phase("Test Phase", 100)
        tracker.update_progress(50, 100, "Testing...")
        tracker.end_phase()
        
        # Test edge case - update after phase ended (should not crash)
        tracker.update_progress(75, 100, "After phase ended...")
        
        print("✅ SmartProgressTracker test passed!")
        return True
        
    except Exception as e:
        print(f"❌ SmartProgressTracker test failed: {e}")
        return False

async def test_ultimate_hunter():
    """Test UltimateSubdomainHunter instantiation."""
    try:
        from k1ngb0b_recon import UltimateSubdomainHunter
        
        print("🔍 Testing UltimateSubdomainHunter...")
        hunter = UltimateSubdomainHunter("test.com")
        
        # Test basic functionality
        hunter._add_discoveries(["test1.test.com", "test2.test.com"], "Test Source")
        
        print("✅ UltimateSubdomainHunter test passed!")
        return True
        
    except Exception as e:
        print(f"❌ UltimateSubdomainHunter test failed: {e}")
        return False

def main():
    """Run quick tests."""
    print("🔥 K1NGB0B ULTIMATE Quick Test")
    print("=" * 40)
    
    tests = [
        test_progress_tracker,
        test_ultimate_hunter
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🔥 K1NGB0B ULTIMATE is ready!")
        print("🚀 The KeyError issue has been fixed!")
        return 0
    else:
        print("🔧 Some issues remain")
        return 1

if __name__ == "__main__":
    sys.exit(main())
