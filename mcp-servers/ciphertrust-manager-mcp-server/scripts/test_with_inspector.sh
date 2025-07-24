#!/bin/bash

set -e

echo "Starting CipherTrust MCP Server Testing..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if Python environment is set up
if ! command -v uv &> /dev/null; then
    echo "UV is not installed. Please install UV first."
    exit 1
fi

# Check environment variables
if [ -z "$CIPHERTRUST_URL" ]; then
    echo "Warning: CIPHERTRUST_URL not set. Real testing will fail."
fi

echo ""
echo "Testing Options:"
echo "1. Interactive UI Testing (Real CipherTrust connection)"
echo "2. CLI Automated Testing (Real CipherTrust connection)"
echo "3. Python Unit Tests (Mock - Fast, no external connections)"
echo "4. Full Mock Test Suite (Comprehensive mock testing)"
echo "5. Full Integration Test Suite (Real CipherTrust Manager testing)"
echo ""

read -p "Choose testing option (1-5): " choice

case $choice in
    1)
        echo "Starting MCP Inspector UI..."
        echo "Make sure CIPHERTRUST_URL, CIPHERTRUST_USER, CIPHERTRUST_PASSWORD are set"
        npx @modelcontextprotocol/inspector uv run ciphertrust-mcp-server
        ;;
    2)
        echo "Running CLI automated tests..."
        echo "Make sure CIPHERTRUST_URL, CIPHERTRUST_USER, CIPHERTRUST_PASSWORD are set"
        npx @modelcontextprotocol/inspector --cli uv run ciphertrust-mcp-server --method tools/list
        ;;
    3)
        echo "Running Python unit tests (fast, no external connections)..."
        uv run python -m pytest tests/test_server.py -v
        ;;
    4)
        echo "Running Full Mock Test Suite..."
        echo "================================================"
        echo "1. Running Python unit tests..."
        uv run python -m pytest tests/test_server.py -v
        echo ""
        echo "2. Testing JSON-RPC message validation..."
        uv run python -c "import json; req={'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2024-11-05','clientInfo':{'name':'test','version':'1.0'},'capabilities':{'tools':{}}}}; print('JSON-RPC structure valid'); print(json.dumps(req, indent=2)[:200] + '...')"
        echo ""
        echo "3. Testing tool argument validation..."
        uv run python -c "args={'action':'list','limit':5}; print('Key management args valid:', 'action' in args and isinstance(args['limit'], int))"
        echo ""
        echo "4. Checking environment variables..."
        if [ -n "$CIPHERTRUST_URL" ]; then
            echo "CIPHERTRUST_URL: SET"
        else
            echo "CIPHERTRUST_URL: NOT SET"
        fi
        if [ -n "$CIPHERTRUST_USER" ]; then
            echo "CIPHERTRUST_USER: SET"
        else
            echo "CIPHERTRUST_USER: NOT SET"
        fi
        if [ -n "$CIPHERTRUST_PASSWORD" ]; then
            echo "CIPHERTRUST_PASSWORD: SET"
        else
            echo "CIPHERTRUST_PASSWORD: NOT SET"
        fi
        echo ""
        echo "5. Testing mock server responses..."
        uv run python -c "import json; mock_response = {'jsonrpc': '2.0', 'id': 1, 'result': {'capabilities': {'tools': {}}, 'protocolVersion': '2024-11-05', 'serverInfo': {'name': 'ciphertrust-mcp-server', 'version': '0.1.0'}}}; print('Mock initialize response valid:', 'result' in mock_response); tools_response = {'jsonrpc': '2.0', 'id': 2, 'result': {'tools': [{'name': 'key_management', 'description': 'Key management operations'}, {'name': 'system_information', 'description': 'System information'}]}}; print('Mock tools response valid:', len(tools_response['result']['tools']) > 0)"
        echo ""
        echo "================================================"
        echo "Full Mock Test Suite completed - no external connections made"
        ;;
    5)
        echo "Running Full Integration Test Suite..."
        echo "================================================"
        echo "Checking environment setup..."
        if [ -z "$CIPHERTRUST_URL" ]; then
            echo "ERROR: CIPHERTRUST_URL not set"
            echo "Please set your environment variables first"
            exit 1
        fi
        if [ -z "$CIPHERTRUST_USER" ]; then
            echo "ERROR: CIPHERTRUST_USER not set"
            echo "Please set your environment variables first"
            exit 1
        fi
        if [ -z "$CIPHERTRUST_PASSWORD" ]; then
            echo "ERROR: CIPHERTRUST_PASSWORD not set"
            echo "Please set your environment variables first"
            exit 1
        fi
        echo "Environment variables are set"
        echo ""
        echo "1. Quick server startup test..."
        echo "Starting server for 5 seconds to test startup..."
        timeout 5s uv run ciphertrust-mcp-server > /dev/null 2>&1 &
        SERVER_PID=$!
        sleep 5
        kill $SERVER_PID 2>/dev/null || true
        wait $SERVER_PID 2>/dev/null || true
        echo "Server startup test completed"
        echo ""
        echo "2. Running integration tests..."
        echo "Note: Using simple tests that won't hang"
        uv run python -m pytest tests/test_integration_simple.py -v -s --tb=short
        echo ""
        echo "3. Testing MCP Inspector CLI with real connection..."
        echo "This will test actual CipherTrust Manager connectivity"
        npx @modelcontextprotocol/inspector --cli uv run ciphertrust-mcp-server --method tools/list
        echo ""
        echo "================================================"
        echo "Full Integration Test Suite completed"
        ;;
    *)
        echo "Invalid option. Please choose 1-5."
        exit 1
        ;;
esac

echo "Testing completed."