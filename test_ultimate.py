#!/usr/bin/env python3
"""
K1NGB0B Ultimate Reconnaissance Suite - Test Script
Author: mrx-arafat (K1NGB0B)

This script tests the functionality of the ultimate reconnaissance suite
without requiring external tools to be installed.
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from k1ngb0b_ultimate_recon import (
    K1NGB0BUltimateRecon, 
    Logger, 
    OutputManager, 
    ProgressTracker,
    Colors
)

def test_logger():
    """Test the Logger class"""
    print(f"{Colors.CYAN}🧪 Testing Logger class...{Colors.END}")
    
    logger = Logger(verbose=True)
    logger.info("This is an info message")
    logger.success("This is a success message", 42)
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    logger.phase("This is a phase message")
    logger.subphase("This is a subphase message")
    
    print(f"{Colors.GREEN}✅ Logger test completed{Colors.END}\n")

def test_progress_tracker():
    """Test the ProgressTracker class"""
    print(f"{Colors.CYAN}🧪 Testing ProgressTracker class...{Colors.END}")
    
    import time
    
    progress = ProgressTracker(100, "Test Progress")
    
    for i in range(0, 101, 10):
        progress.update(10, f"Processing item {i}")
        time.sleep(0.1)  # Simulate work
    
    print(f"{Colors.GREEN}✅ ProgressTracker test completed{Colors.END}\n")

def test_output_manager():
    """Test the OutputManager class"""
    print(f"{Colors.CYAN}🧪 Testing OutputManager class...{Colors.END}")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        output_manager = OutputManager("test.com", temp_dir)
        
        # Test saving results
        test_data = ["subdomain1.test.com", "subdomain2.test.com", "subdomain3.test.com"]
        filename = output_manager.save_results('subdomains', 'test_tool', test_data)
        
        # Verify file was created
        assert os.path.exists(filename), "Output file was not created"
        
        # Verify content
        with open(filename, 'r') as f:
            content = f.read().strip().split('\n')
            assert content == test_data, "Output content doesn't match input"
        
        # Test getting all results
        all_results = output_manager.get_all_results('subdomains')
        assert all_results == set(test_data), "Retrieved results don't match saved data"
    
    print(f"{Colors.GREEN}✅ OutputManager test completed{Colors.END}\n")

def test_ultimate_recon_basic():
    """Test basic functionality of K1NGB0BUltimateRecon"""
    print(f"{Colors.CYAN}🧪 Testing K1NGB0BUltimateRecon basic functionality...{Colors.END}")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        recon = K1NGB0BUltimateRecon("test.com", temp_dir, verbose=False)
        
        # Test banner printing
        recon.print_banner()
        
        # Test dependency checking
        deps_ok = recon.check_dependencies()
        assert deps_ok, "Dependency check failed"
        
        # Test directory structure creation
        expected_dirs = [
            'subdomains', 'dns', 'ports', 'web_content', 'parameters',
            'urls', 'vulnerabilities', 'technology', 'screenshots',
            'network', 'api', 'javascript', 'cloud', 'osint',
            'git_analysis', 'reports'
        ]
        
        for dir_name in expected_dirs:
            dir_path = Path(f"{temp_dir}/{dir_name}")
            assert dir_path.exists(), f"Directory {dir_name} was not created"
    
    print(f"{Colors.GREEN}✅ K1NGB0BUltimateRecon basic test completed{Colors.END}\n")

def test_full_reconnaissance_simulation():
    """Test full reconnaissance with simulated data"""
    print(f"{Colors.CYAN}🧪 Testing full reconnaissance simulation...{Colors.END}")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        recon = K1NGB0BUltimateRecon("example.com", temp_dir, verbose=False)
        
        # Simulate some results
        recon.results['subdomains'] = {"app.example.com", "api.example.com", "www.example.com"}
        recon.results['resolved_domains'] = {
            "app.example.com": "192.168.1.1",
            "api.example.com": "192.168.1.2",
            "www.example.com": "192.168.1.3"
        }
        recon.results['open_ports'] = {
            "192.168.1.1": [80, 443],
            "192.168.1.2": [80, 443, 8080],
            "192.168.1.3": [80, 443]
        }
        
        # Generate report
        import time
        start_time = time.time() - 120  # Simulate 2 minutes
        recon._generate_final_report(start_time)
        
        # Verify report was created
        report_file = f"{temp_dir}/reports/final_report.json"
        assert os.path.exists(report_file), "Final report was not created"
        
        # Verify report content
        with open(report_file, 'r') as f:
            report = json.load(f)
            assert report['target'] == 'example.com', "Target in report is incorrect"
            assert report['summary']['subdomains_found'] == 3, "Subdomain count is incorrect"
            assert report['summary']['domains_resolved'] == 3, "Resolved domain count is incorrect"
    
    print(f"{Colors.GREEN}✅ Full reconnaissance simulation test completed{Colors.END}\n")

def test_command_line_interface():
    """Test command line interface"""
    print(f"{Colors.CYAN}🧪 Testing command line interface...{Colors.END}")
    
    # Test help command
    import subprocess
    result = subprocess.run([
        sys.executable, 'k1ngb0b_ultimate_recon.py', '--help'
    ], capture_output=True, text=True)
    
    assert result.returncode == 0, "Help command failed"
    assert "K1NGB0B Ultimate Reconnaissance Suite" in result.stdout, "Help text is incorrect"
    
    # Test version command
    result = subprocess.run([
        sys.executable, 'k1ngb0b_ultimate_recon.py', '--version'
    ], capture_output=True, text=True)
    
    assert result.returncode == 0, "Version command failed"
    assert "v3.0" in result.stdout, "Version text is incorrect"
    
    print(f"{Colors.GREEN}✅ Command line interface test completed{Colors.END}\n")

def run_all_tests():
    """Run all tests"""
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║           K1NGB0B ULTIMATE RECONNAISSANCE SUITE             ║")
    print("║                      TEST SUITE v3.0                        ║")
    print("║                  Author: mrx-arafat (K1NGB0B)                ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}\n")
    
    tests = [
        test_logger,
        test_progress_tracker,
        test_output_manager,
        test_ultimate_recon_basic,
        test_full_reconnaissance_simulation,
        test_command_line_interface
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"{Colors.RED}❌ Test {test.__name__} failed: {str(e)}{Colors.END}\n")
            failed += 1
    
    print(f"{Colors.BOLD}📊 TEST RESULTS:{Colors.END}")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📊 Total: {passed + failed}")
    
    if failed == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! 🎉{Colors.END}")
        return True
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ SOME TESTS FAILED ❌{Colors.END}")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)