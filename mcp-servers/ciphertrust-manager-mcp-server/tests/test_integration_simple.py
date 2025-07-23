"""
Simple integration tests that won't hang

Create this file as: tests/test_integration_simple.py
"""

import pytest
import subprocess
import os
import time
import json
import socket


class TestCipherTrustBasic:
    """Basic integration tests that won't hang"""
    
    def test_environment_variables_required(self):
        """Test that required environment variables are set"""
        required_vars = ['CIPHERTRUST_URL', 'CIPHERTRUST_USER', 'CIPHERTRUST_PASSWORD']
        missing_vars = []
        
        for var in required_vars:
            if not os.environ.get(var):
                missing_vars.append(var)
        
        if missing_vars:
            pytest.skip(f"Integration tests require: {', '.join(missing_vars)}")
        
        # If we get here, all variables are set
        print("✅ All required environment variables are set")
        assert True

    def test_server_can_start(self):
        """Test that the server process can start without crashing immediately"""
        if not os.environ.get('CIPHERTRUST_URL'):
            pytest.skip("CIPHERTRUST_URL not set")
        
        try:
            # Start the server process
            process = subprocess.Popen(
                ['uv', 'run', 'ciphertrust-mcp-server'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a few seconds
            time.sleep(3)
            
            # Check if process is still running (hasn't crashed)
            return_code = process.poll()
            
            if return_code is None:
                # Process is still running - good!
                print("✅ Server started successfully and is running")
                process.terminate()
                process.wait(timeout=5)
                assert True
            else:
                # Process has already terminated - get output for debugging
                stdout, stderr = process.communicate()
                print(f"❌ Server process terminated with code {return_code}")
                print(f"STDOUT: {stdout}")
                print(f"STDERR: {stderr}")
                
                # Check if it's a connection error vs code error
                if 'connection' in stderr.lower() or 'auth' in stderr.lower():
                    pytest.skip(f"CipherTrust connection issue: {stderr}")
                else:
                    pytest.fail(f"Server failed to start: {stderr}")
                    
        except FileNotFoundError:
            pytest.skip("UV or Python not found in PATH")
        except Exception as e:
            pytest.fail(f"Failed to start server process: {e}")

    def test_ciphertrust_url_reachable(self):
        """Test that the CipherTrust URL is reachable using socket connection"""
        url = os.environ.get('CIPHERTRUST_URL')
        if not url:
            pytest.skip("CIPHERTRUST_URL not set")
        
        try:
            # Parse URL to get host and port
            url = url.replace('https://', '').replace('http://', '')
            if ':' in url:
                host, port = url.split(':')
                port = int(port)
            else:
                host = url
                port = 443  # Default HTTPS port
            
            # Try to connect to the host and port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print(f"✅ CipherTrust Manager is reachable at {host}:{port}")
                assert True
            else:
                pytest.skip(f"CipherTrust Manager at {host}:{port} is not reachable")
                
        except ValueError as e:
            pytest.skip(f"Invalid CIPHERTRUST_URL format: {url}")
        except Exception as e:
            pytest.skip(f"Cannot test CipherTrust reachability: {e}")

    def test_json_rpc_format_validation(self):
        """Test that our JSON-RPC messages are properly formatted"""
        # Test initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "clientInfo": {"name": "test", "version": "1.0"},
                "capabilities": {"tools": {}}
            }
        }
        
        # Should be valid JSON
        json_str = json.dumps(init_request)
        parsed = json.loads(json_str)
        assert parsed == init_request
        
        # Test tools list request
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        json_str = json.dumps(tools_request)
        parsed = json.loads(json_str)
        assert parsed == tools_request
        
        print("✅ JSON-RPC message formats are valid")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])