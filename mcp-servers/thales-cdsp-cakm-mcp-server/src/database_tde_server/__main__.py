"""
Main entry point for Database TDE MCP Server
"""

import os
import sys
from pathlib import Path

# Try to load .env file before anything else
def load_env_file():
    """Load .env file from various locations"""
    # Try current directory first
    env_path = Path.cwd() / ".env"
    
    # If not found, try the installation directory
    if not env_path.exists():
        # Get the directory where this script is located
        script_dir = Path(__file__).parent.parent.parent
        env_path = script_dir / ".env"
    
    # Try known location
    if not env_path.exists():
        env_path = Path("C:/database-tde-mcp-server/.env")
    
    if env_path.exists():
        print(f"Loading .env from: {env_path}", file=sys.stderr)
        try:
            from dotenv import load_dotenv
            load_dotenv(env_path)
            return True
        except ImportError:
            # If python-dotenv not installed, manually parse
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        os.environ[key] = value
            return True
    else:
        print(f"Warning: .env file not found. Checked: {env_path}", file=sys.stderr)
        return False

# Load environment before importing anything else
load_env_file()

# Now import and run the server
from .server import main

if __name__ == "__main__":
    main()