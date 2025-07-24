#!/usr/bin/env python3
"""
Automated test runner for CipherTrust MCP Server
"""

import json
import subprocess
import sys
import os
from pathlib import Path

def run_command(command, capture_output=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=capture_output, 
            text=True, 
            check=True
        )
        return result.stdout if capture_output else None
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {command}")
        print(f"Error: {e.stderr}")
        return None

def test_inspector_cli():
    """Run MCP Inspector CLI tests"""
    print("Running MCP Inspector CLI tests...")
    
    commands = [
        "npx @modelcontextprotocol/inspector --cli --config tests/mcp_inspector_config.json --server ciphertrust-local --method tools/list",
        "npx @modelcontextprotocol/inspector --cli --config tests/mcp_inspector_config.json --server ciphertrust-local --method tools/call --tool-name system_information --tool-arg action=get"
    ]
    
    for cmd in commands:
        print(f"Running: {cmd}")
        result = run_command(cmd)
        if result is None:
            return False
        print("✓ Passed")
    
    return True

def test_python_units():
    """Run Python unit tests"""
    print("Running Python unit tests...")
    result = run_command("uv run python -m pytest tests/test_server.py -v", capture_output=False)
    return result is not None

def main():
    """Main test runner"""
    print("CipherTrust MCP Server Test Runner")
    print("=" * 40)
    
    # Check prerequisites
    if not run_command("node --version"):
        print("❌ Node.js not found. Please install Node.js first.")
        sys.exit(1)
    
    if not run_command("uv --version"):
        print("❌ UV not found. Please install UV first.")
        sys.exit(1)
    
    # Run tests
    tests_passed = 0
    total_tests = 2
    
    if test_python_units():
        print("✓ Python unit tests passed")
        tests_passed += 1
    else:
        print("❌ Python unit tests failed")
    
    if test_inspector_cli():
        print("✓ MCP Inspector CLI tests passed")
        tests_passed += 1
    else:
        print("❌ MCP Inspector CLI tests failed")
    
    print("\n" + "=" * 40)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()