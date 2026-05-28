#!/usr/bin/env python3
"""
Test Runner for Thales CSM MCP Server

This script runs the test suite for the MCP server.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_tests():
    """Run all tests using pytest."""
    print("🧪 Running Thales CSM MCP Server Tests")
    print("=" * 50)
    
    try:
        # Check if pytest is available
        result = subprocess.run([sys.executable, "-m", "pytest", "--version"], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            print("❌ pytest not found. Installing...")
            subprocess.run([sys.executable, "-m", "pip", "install", "pytest", "pytest-asyncio"], 
                         check=True)
            print("✅ pytest installed successfully")
        
        print("🚀 Running tests...")
        print("=" * 50)
        
        # Run tests with pytest
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/", 
            "-v", 
            "--tb=short",
            "--asyncio-mode=auto"
        ], check=False)
        
        if result.returncode == 0:
            print("\n🎉 All tests passed!")
        else:
            print(f"\n⚠️  Some tests failed. Exit code: {result.returncode}")
            
        return result.returncode
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running tests: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

def run_specific_test(test_file):
    """Run a specific test file."""
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return 1
    
    print(f"🧪 Running specific test: {test_file}")
    print("=" * 50)
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            test_file, 
            "-v", 
            "--tb=short",
            "--asyncio-mode=auto"
        ], check=False)
        
        if result.returncode == 0:
            print("\n🎉 Test passed!")
        else:
            print(f"\n⚠️  Test failed. Exit code: {result.returncode}")
            
        return result.returncode
        
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return 1

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific test file
        test_file = sys.argv[1]
        exit_code = run_specific_test(test_file)
    else:
        # Run all tests
        exit_code = run_tests()
    
    sys.exit(exit_code) 