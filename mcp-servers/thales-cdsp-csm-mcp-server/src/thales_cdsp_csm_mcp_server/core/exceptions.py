"""
Thales CDSP CSM MCP Server - Custom Exceptions

This module defines custom exceptions for the Thales CDSP CSM MCP server.
"""


class ThalesCDSPCSMError(Exception):
    """Base exception for Thales CDSP CSM MCP server."""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class AuthenticationError(ThalesCDSPCSMError):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed", details: dict = None):
        super().__init__(message, "AUTH_ERROR", details)


class ValidationError(ThalesCDSPCSMError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: str = None, details: dict = None):
        super().__init__(message, "VALIDATION_ERROR", details)
        self.field = field


class APIError(ThalesCDSPCSMError):
    """Raised when API calls fail."""
    
    def __init__(self, message: str, status_code: int = None, response: dict = None):
        super().__init__(message, "API_ERROR", {"status_code": status_code, "response": response})
        self.status_code = status_code
        self.response = response


class ConfigurationError(ThalesCDSPCSMError):
    """Raised when configuration is invalid."""
    
    def __init__(self, message: str, config_field: str = None):
        super().__init__(message, "CONFIG_ERROR", {"config_field": config_field})
        self.config_field = config_field 