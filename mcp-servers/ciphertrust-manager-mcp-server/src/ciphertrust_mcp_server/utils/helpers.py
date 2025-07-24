"""Helper utilities for CipherTrust MCP Server."""

import json
from typing import Any


def format_json_output(data: Any, indent: int = 2) -> str:
    """Format data as pretty-printed JSON.
    
    Args:
        data: Data to format
        indent: Number of spaces for indentation
        
    Returns:
        Formatted JSON string
    """
    if isinstance(data, str):
        try:
            # Try to parse as JSON first
            parsed = json.loads(data)
            return json.dumps(parsed, indent=indent)
        except json.JSONDecodeError:
            # Return as-is if not JSON
            return data
    return json.dumps(data, indent=indent)


def sanitize_command_args(args: list[str]) -> list[str]:
    """Sanitize command arguments for logging.
    
    Removes sensitive information like passwords from command arguments.
    
    Args:
        args: Command arguments
        
    Returns:
        Sanitized arguments safe for logging
    """
    sensitive_flags = ["--password", "--pword", "--jwt", "--refresh-token"]
    sanitized = []
    skip_next = False
    
    for arg in args:
        if skip_next:
            sanitized.append("***")
            skip_next = False
        elif arg in sensitive_flags:
            sanitized.append(arg)
            skip_next = True
        else:
            sanitized.append(arg)
    
    return sanitized
