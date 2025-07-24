"""
Custom exceptions for Database TDE MCP Server
"""

class DatabaseTDEError(Exception):
    """Base exception for Database TDE operations"""
    pass

class DatabaseConnectionError(DatabaseTDEError):
    """Raised when database connection fails"""
    pass

class TDEOperationError(DatabaseTDEError):
    """Raised when TDE operation fails"""
    pass

class ConfigurationError(DatabaseTDEError):
    """Raised when configuration is invalid"""
    pass

class KeyManagementError(DatabaseTDEError):
    """Raised when key management operation fails"""
    pass

class ValidationError(DatabaseTDEError):
    """Raised when validation fails"""
    pass
