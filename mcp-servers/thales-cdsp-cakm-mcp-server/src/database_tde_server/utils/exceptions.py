"""
Custom exception classes for Database TDE operations

This module defines custom exception classes for handling errors in Transparent Data Encryption (TDE) operations.
Database encryption and encryption key management are handled by Thales CipherTrust Application Key Management (CAKM)
connector, which is integrated with Thales CDSP (CipherTrust Data Security Platform).

Available exception classes:
- DatabaseConnectionError: Raised when database connection operations fail
- TDEOperationError: Raised when TDE-specific operations encounter errors
- ConfigurationError: Raised when configuration validation or loading fails
- ValidationError: Raised when input validation fails
- SSHConnectionError: Raised when SSH connection operations fail
- OracleOperationError: Raised when Oracle-specific operations encounter errors
- SQLServerOperationError: Raised when SQL Server-specific operations encounter errors
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
