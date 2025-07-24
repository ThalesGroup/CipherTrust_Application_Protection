# Testing Guide for CipherTrust Manager MCP Server

This document provides comprehensive testing instructions for the CipherTrust Manager MCP Server using the Model Context Protocol Inspector and Python unit tests.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Testing Methods](#testing-methods)
- [Configuration](#configuration)
- [Test Scenarios](#test-scenarios)
- [Automation](#automation)
- [Troubleshooting](#troubleshooting)

## Overview

The CipherTrust Manager MCP Server includes multiple testing approaches:

- **Interactive UI Testing**: Visual interface for manual testing and debugging
- **CLI Automated Testing**: Command-line automation for CI/CD integration
- **Python Unit Tests**: Comprehensive unit testing for server components
- **Integration Tests**: End-to-end testing with real CipherTrust Manager instances

## Prerequisites

### Required Software

1. **Node.js** (v18 or higher) - for MCP Inspector
   ```bash
   # Windows (using winget)
   winget install OpenJS.NodeJS
   
   # Verify installation
   node --version
   npm --version
   npx --version
   ```

2. **Python 3.11+** and **UV** - already covered in main [README.md](README.md)

3. **Git** - for repository management

### Environment Setup

Ensure your environment variables are configured:

```bash
# Required
CIPHERTRUST_URL=https://your-ciphertrust-manager.example.com
CIPHERTRUST_USER=your-username
CIPHERTRUST_PASSWORD=your-password

# Optional
CIPHERTRUST_NOSSLVERIFY=true  # for test environments
CIPHERTRUST_TIMEOUT=30
LOG_LEVEL=DEBUG  # for testing
```

## Quick Start

### 1. Install Testing Dependencies

```bash
# Install Node.js packages for MCP Inspector
npm install

# Install Python testing dependencies
uv pip install pytest pytest-asyncio
```

### 2. Run Quick Test

```bash
# Interactive UI testing (opens browser)
npx @modelcontextprotocol/inspector --config tests/mcp_inspector_config.json --server ciphertrust-local

# Quick CLI testing
# Get tools
npx @modelcontextprotocol/inspector --cli --config tests/mcp_inspector_config.json --server ciphertrust-local --method tools/list
# Get system information
npx @modelcontextprotocol/inspector --cli --config tests/mcp_inspector_config.json --server ciphertrust-local --method tools/call --tool-name system_information --tool-arg action=get
# Get 2 keys
npx @modelcontextprotocol/inspector --cli --config tests/mcp_inspector_config.json --server ciphertrust-local --method tools/call --tool-name key_management --tool-arg action=list --tool-arg limit=2
```

### 3. Try Example AI Assistant Prompts

For hands-on testing with AI assistants like Claude Desktop or Cursor, see [EXAMPLE_PROMPTS.md](EXAMPLE_PROMPTS.md) for ready-to-use prompts covering:
- Key management operations
- User and group management  
- CTE operations
- Crypto operations
- And many more scenarios

### 3. Using Test Scripts

```bash
# Windows
scripts\test_with_inspector.bat

# Unix/Linux/macOS
chmod +x scripts/test_with_inspector.sh
./scripts/test_with_inspector.sh
```

**Available Options:**
1. **Interactive UI Testing** - Real CipherTrust connection, opens browser
2. **CLI Automated Testing** - Real CipherTrust connection, command line
3. **Python Unit Tests** - Fast mock testing (~0.11s, no external connections)
4. **Full Mock Test Suite** - Comprehensive mock testing with validation
5. **Full Integration Test Suite** - Real CipherTrust Manager testing

## Testing Methods

### 1. Manual JSON-RPC Testing (Direct stdin/stdout)

You can test the MCP server directly by sending JSON-RPC commands to it via stdin. This is useful for debugging and development without additional tools.

#### Setup for Manual Testing

1. **Start the server** in one terminal:
   ```bash
   uv run ciphertrust-mcp-server
   ```
   
   You should see output like:
   ```
   2025-06-17 17:37:19,394 - ciphertrust_mcp_server.server - INFO - Successfully connected to CipherTrust Manager
   2025-06-17 17:37:19,396 - ciphertrust_mcp_server.server - INFO - MCP server ready and waiting for JSON-RPC messages on stdin...
   ```

2. **Send commands** to the server (in the same terminal where the server is running)

#### Manual Test Commands

⚠️ **Important**: Each JSON command must be on a single line and end with Enter. Copy and paste these commands one by one:

**1. Initialize the server:**
```json
{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "clientInfo": {"name": "test-client", "version": "1.0.0"}, "capabilities": {"tools": {}}}}
```

**2. Send initialized notification:** (Server does not respond)
```json
{"jsonrpc": "2.0", "method": "notifications/initialized"}
```

**3. List available tools:**
```json
{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
```

**4. Test key management:**
```json
{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "key_management", "arguments": {"action": "list", "limit": 5}}}
```

**5. Test system information:**
```json
{"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "system_information", "arguments": {"action": "get"}}}
```

#### Expected Responses

Each command (except notifications) should return a JSON-RPC response:
```json
{"jsonrpc": "2.0", "id": 1, "result": {...}}
```

#### Manual Testing Troubleshooting

- **No response after initialize**: Check that all required environment variables are set
- **"Method not found" error**: Ensure you send the initialize command first
- **Tool call failures**: Verify connectivity to your CipherTrust Manager instance

#### Prerequisites for Manual Testing

- Server must be running (see "How to Start the Server" in main README)
- Required environment variables must be set (`CIPHERTRUST_URL`, credentials, etc.)

### 2. Interactive UI Testing

The MCP Inspector provides a web-based interface for testing:

```bash
# Start with default configuration
npx @modelcontextprotocol/inspector uv run ciphertrust-mcp-server

# Start with custom configuration
npx @modelcontextprotocol/inspector --config tests/mcp_inspector_config.json --server ciphertrust-local
```

**Features:**
- Visual tool testing interface
- Real-time request/response viewing
- Resource and prompt exploration
- Connection management
- Debug logging

**Access:** Open http://localhost:6274 in your browser

### 3. CLI Automated Testing

Command-line testing for automation and scripting:

```bash
# List available tools
npx @modelcontextprotocol/inspector --cli \
  --config tests/mcp_inspector_config.json \
  --server ciphertrust-local \
  --method tools/list

# Test specific tool
npx @modelcontextprotocol/inspector --cli \
  --config tests/mcp_inspector_config.json \
  --server ciphertrust-local \
  --method tools/call \
  --tool-name system_information \
  --tool-arg action=get

# Test with environment variables
npx @modelcontextprotocol/inspector --cli \
  -e CIPHERTRUST_URL=https://test.example.com \
  -e LOG_LEVEL=DEBUG \
  uv run ciphertrust-mcp-server \
  --method tools/list
```

### 3. Python Unit Tests

Comprehensive testing of server components:

```bash
# Run all tests
uv run python -m pytest tests/test_server.py -v

# Run specific test categories
uv run python -m pytest tests/test_server.py::TestCipherTrustMCPServer -v
uv run python -m pytest tests/test_server.py::TestToolFunctions -v

# Run with coverage
uv run python -m pytest tests/test_server.py --cov=ciphertrust_mcp_server

# Run integration tests (requires real environment)
uv run python -m pytest tests/test_server.py -m integration -v
```

### 5. Full Test Suite

Run comprehensive testing using the test scripts:

```bash
# Using test scripts (recommended)
scripts\test_with_inspector.bat    # Windows
./scripts/test_with_inspector.sh   # Unix/Linux/macOS

# Choose from 5 testing options:
# 3. Python Unit Tests (Mock - Fast, no external connections) 
# 4. Full Mock Test Suite (Comprehensive mock testing)
# 5. Full Integration Test Suite (Real CipherTrust Manager testing)

# Manual execution
uv run python -m pytest tests/test_server.py -v                    # Unit tests
uv run python -m pytest tests/test_integration_simple.py -v -s     # Integration tests
```

## Configuration

### Inspector Configuration

Edit `tests/mcp_inspector_config.json` to customize testing environments:

```json
{
  "mcpServers": {
    "ciphertrust-local": {
      "command": "uv",
      "args": ["run", "ciphertrust-mcp-server"],
      "env": {
        "CIPHERTRUST_URL": "https://test.example.com",
        "CIPHERTRUST_USER": "test-user",
        "CIPHERTRUST_PASSWORD": "test-password",
        "LOG_LEVEL": "DEBUG"
      }
    },
    "ciphertrust-staging": {
      "command": "uv",
      "args": ["run", "ciphertrust-mcp-server"],
      "env": {
        "CIPHERTRUST_URL": "https://test.example.com",
        "CIPHERTRUST_USER": "test-user",
        "CIPHERTRUST_PASSWORD": "test-password",
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

### Test Scenarios

Customize `tests/test_scenarios.json` for your testing needs:

```json
{
  "test_scenarios": [
    {
      "name": "Key Management Workflow",
      "description": "Test complete key lifecycle",
      "commands": [
        {
          "method": "tools/call",
          "tool": "key_management",
          "args": {"action": "list", "limit": 5}
        },
        {
          "method": "tools/call", 
          "tool": "key_management",
          "args": {
            "action": "create",
            "name": "test-key-{{timestamp}}",
            "algorithm": "AES",
            "size": 256
          }
        }
      ]
    }
  ]
}
```

## Test Scenarios

### Manual JSON-RPC Test Scenarios

#### Basic Server Validation

**Scenario 1: Server Initialization and Tool Discovery**
```bash
# 1. Start server
uv run ciphertrust-mcp-server

# 2. Initialize (copy-paste each line one by one)
{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "clientInfo": {"name": "manual-test", "version": "1.0.0"}, "capabilities": {"tools": {}}}}

# 3. Send initialized notification (No response from serrver for this notification)
{"jsonrpc": "2.0", "method": "notifications/initialized"}

# 4. List tools to verify server is working
{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
```

**Expected Result:** Should return a list of available tools including `key_management`, `system_information`, `cte_client_management`, etc.

**Scenario 2: Basic Tool Functionality Test**
```bash
# Test system information (after initialization above)
{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "system_information", "arguments": {"action": "get"}}}

# Test key management list
{"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "key_management", "arguments": {"action": "list", "limit": 5}}}
```

**Expected Result:** Should return system information and a list of keys (up to 5) from your CipherTrust Manager.

#### Error Handling Tests

**Scenario 3: Invalid Tool Test**
```bash
# Test invalid tool name (after initialization)
{"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "nonexistent_tool", "arguments": {}}}
```

**Expected Result:** Should return an error response indicating the tool doesn't exist.

**Scenario 4: Invalid Arguments Test**
```bash
# Test invalid arguments (after initialization)
{"jsonrpc": "2.0", "id": 6, "method": "tools/call", "params": {"name": "key_management", "arguments": {"invalid_action": "test"}}}
```

**Expected Result:** Should return an error response about invalid arguments.

### MCP Inspector Test Scenarios

#### Basic Functionality Tests

1. **Server Initialization**
   ```bash
   npx @modelcontextprotocol/inspector --cli --config tests/mcp_inspector_config.json --server ciphertrust-local --method tools/list
   ```

2. **Tool Execution**
   ```bash
   npx @modelcontextprotocol/inspector --cli --config tests/mcp_inspector_config.json --server ciphertrust-local --method tools/call --tool-name system_information --tool-arg action=get
   ```

3. **Error Handling**
   ```bash
   npx @modelcontextprotocol/inspector --cli --config tests/mcp_inspector_config.json --server ciphertrust-local --method tools/call --tool-name invalid_tool
   ```

### More Test Scenarios

1. **Key Management Workflow**
   - List existing keys
   - Create new key
   - Verify key creation
   - Delete test key

2. **CTE Client Management**
   - List CTE clients
   - Create new clients
   - Test client operations

3. **Connection Management**
   - Test database connections
   - Verify LDAP connectivity
   - Test authentication

## Automation

### NPM Scripts

Add these to your workflow:

```bash
# Available npm scripts
npm run test:inspector:ui      # Open UI testing interface
npm run test:inspector:cli     # Run CLI automated tests
npm run test:python           # Run Python unit tests
npm run test:full             # Run complete test suite
```

## Troubleshooting

### Common Issues

1. **Node.js Not Found**
   ```bash
   # Error: 'node' is not recognized
   # Solution: Install Node.js or add to PATH
   winget install OpenJS.NodeJS
   ```

2. **Manual JSON-RPC Testing Issues**
   ```bash
   # Error: No response after initialize command
   # Solution: Check environment variables
   echo $CIPHERTRUST_URL
   echo $CIPHERTRUST_USER
   
   # Error: "Method not found"
   # Solution: Ensure you send the initialize command first
   
   # Error: Tool call failures
   # Solution: Verify CipherTrust Manager connectivity
   ```

3. **MCP Inspector Connection Failed**
   ```bash
   # Error: Failed to connect to MCP server
   # Check: Environment variables and CipherTrust Manager connectivity
   echo $CIPHERTRUST_URL
   ```

4. **Python Import Errors**
   ```bash
   # Error: Module not found
   # Solution: Ensure virtual environment is activated
   uv venv
   source .venv/bin/activate  # Unix/Linux/macOS
   .venv\Scripts\activate     # Windows
   uv pip install -e .
   ```

5. **Permission Errors**
   ```bash
   # Error: Permission denied
   # Solution: Run as administrator or fix permissions
   chmod +x scripts/test_with_inspector.sh
   ```

### Debug Mode

Enable verbose logging for troubleshooting:

```bash
# Set debug environment
export LOG_LEVEL=DEBUG
export CIPHERTRUST_NOSSLVERIFY=true

# Run with verbose output
npx @modelcontextprotocol/inspector --cli \
  --config tests/mcp_inspector_config.json \
  --server ciphertrust-local \
  --method tools/list \
  --verbose
```

## Resources

- [Example AI Assistant Prompts](EXAMPLE_PROMPTS.md) - Ready-to-use prompts for testing with Claude Desktop/Cursor
- [MCP Inspector Documentation](https://github.com/modelcontextprotocol/inspector)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Python pytest Documentation](https://docs.pytest.org/)
- [Node.js](https://nodejs.org/en)

---
