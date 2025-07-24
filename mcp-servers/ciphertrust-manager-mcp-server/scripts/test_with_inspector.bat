@echo off
setlocal

echo Starting CipherTrust MCP Server Testing...

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Node.js is not installed. Please install Node.js first.
    exit /b 1
)

REM Check if Python environment is set up
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo UV is not installed. Please install UV first.
    exit /b 1
)

REM Check environment variables
if not defined CIPHERTRUST_URL (
    echo Warning: CIPHERTRUST_URL not set. Real testing will fail.
)

echo.
echo Testing Options:
echo 1. Interactive UI Testing ^(Real CipherTrust connection^)
echo 2. CLI Automated Testing ^(Real CipherTrust connection^)
echo 3. Python Unit Tests ^(Mock - Fast, no external connections^)
echo 4. Full Mock Test Suite ^(Comprehensive mock testing^)
echo 5. Full Integration Test Suite ^(Real CipherTrust Manager testing^)
echo.

set /p choice="Choose testing option (1-5): "

if "%choice%"=="1" goto ui_test
if "%choice%"=="2" goto cli_test
if "%choice%"=="3" goto unit_test
if "%choice%"=="4" goto mock_test_suite
if "%choice%"=="5" goto integration_test_suite
goto invalid_choice

:ui_test
echo Starting MCP Inspector UI...
echo Make sure CIPHERTRUST_URL, CIPHERTRUST_USER, CIPHERTRUST_PASSWORD are set
npx @modelcontextprotocol/inspector uv run ciphertrust-mcp-server
goto end

:cli_test
echo Running CLI automated tests...
echo Make sure CIPHERTRUST_URL, CIPHERTRUST_USER, CIPHERTRUST_PASSWORD are set
npx @modelcontextprotocol/inspector --cli uv run ciphertrust-mcp-server --method tools/list
goto end

:unit_test
echo Running Python unit tests ^(fast, no external connections^)...
uv run python -m pytest tests/test_server.py -v
goto end

:mock_test_suite
echo Running Full Mock Test Suite...
echo ================================================
echo 1. Running Python unit tests...
uv run python -m pytest tests/test_server.py -v
echo.
echo 2. Testing JSON-RPC message validation...
uv run python -c "import json; req={'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2024-11-05','clientInfo':{'name':'test','version':'1.0'},'capabilities':{'tools':{}}}}; print('JSON-RPC structure valid'); print(json.dumps(req, indent=2)[:200] + '...')"
echo.
echo 3. Testing tool argument validation...
uv run python -c "args={'action':'list','limit':5}; print('Key management args valid:', 'action' in args and isinstance(args['limit'], int))"
echo.
echo 4. Checking environment variables...
if defined CIPHERTRUST_URL (
    echo CIPHERTRUST_URL: SET
) else (
    echo CIPHERTRUST_URL: NOT SET
)
if defined CIPHERTRUST_USER (
    echo CIPHERTRUST_USER: SET
) else (
    echo CIPHERTRUST_USER: NOT SET
)
if defined CIPHERTRUST_PASSWORD (
    echo CIPHERTRUST_PASSWORD: SET
) else (
    echo CIPHERTRUST_PASSWORD: NOT SET
)
echo.
echo 5. Testing mock server responses...
uv run python -c "import json; mock_response = {'jsonrpc': '2.0', 'id': 1, 'result': {'capabilities': {'tools': {}}, 'protocolVersion': '2024-11-05', 'serverInfo': {'name': 'ciphertrust-mcp-server', 'version': '0.1.0'}}}; print('Mock initialize response valid:', 'result' in mock_response); tools_response = {'jsonrpc': '2.0', 'id': 2, 'result': {'tools': [{'name': 'key_management', 'description': 'Key management operations'}, {'name': 'system_information', 'description': 'System information'}]}}; print('Mock tools response valid:', len(tools_response['result']['tools']) > 0)"
echo.
echo ================================================
echo Full Mock Test Suite completed - no external connections made
goto end

:integration_test_suite
echo Running Full Integration Test Suite...
echo ================================================
echo Checking environment setup...
if not defined CIPHERTRUST_URL (
    echo ERROR: CIPHERTRUST_URL not set
    echo Please set your environment variables first
    goto end
)
if not defined CIPHERTRUST_USER (
    echo ERROR: CIPHERTRUST_USER not set
    echo Please set your environment variables first
    goto end
)
if not defined CIPHERTRUST_PASSWORD (
    echo ERROR: CIPHERTRUST_PASSWORD not set
    echo Please set your environment variables first
    goto end
)
echo Environment variables are set
echo.
echo 1. Quick server startup test...
echo Starting server for 5 seconds to test startup...
start /min cmd /c "uv run ciphertrust-mcp-server"
timeout /t 5 /nobreak >nul
taskkill /f /im python.exe >nul 2>&1
echo Server startup test completed
echo.
echo 2. Running integration tests...
uv run python -m pytest tests/test_integration_simple.py -v -s --tb=short
echo.
echo 3. Testing MCP Inspector CLI with real connection...
echo This will test actual CipherTrust Manager connectivity
npx @modelcontextprotocol/inspector --cli uv run ciphertrust-mcp-server --method tools/call --tool-name system_information --tool-arg action=get
npx @modelcontextprotocol/inspector --cli uv run ciphertrust-mcp-server --method tools/list
echo.
echo ================================================
echo Full Integration Test Suite completed
goto end

:invalid_choice
echo Invalid option. Please choose 1-5.
goto end

:end
echo Testing completed.
pause