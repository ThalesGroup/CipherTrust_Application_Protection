"""
Database TDE utility modules

This package provides utility modules for supporting Transparent Data Encryption (TDE) operations.
Database encryption and encryption key management are handled by Thales CipherTrust Application Key Management (CAKM)
connector, which is integrated with Thales CDSP (CipherTrust Data Security Platform).

Available utilities:
- exceptions: Custom exception classes for database connections, TDE operations, and configuration errors
- validation: Input validation utilities for database connections, TDE parameters, and configuration settings
- sql_utils: SQL query building utilities for SQL Server and Oracle TDE operations, connection string builders
- ssh_utils: SSH connectivity utilities for remote Oracle database operations, command execution, and file operations
- oracle_setup_from_scratch: Complete Oracle TDE setup utilities from scratch with wallet creation and automation
- oracle_setup_autologin_existing: Oracle TDE auto-login setup utilities for existing TDE implementations
- oracle_setup_hsm_only: Oracle TDE HSM-only setup utilities for enhanced security implementations
- oracle_migrate_to_hsm: Oracle TDE migration utilities for transitioning from software to HSM-based key management
"""

from .exceptions import (
    DatabaseTDEError,
    DatabaseConnectionError,
    TDEOperationError,
    ConfigurationError,
    KeyManagementError,
    ValidationError
)
from .validation import (
    validate_database_name,
    validate_key_name,
    validate_connection_name,
    validate_key_parameters,
    parse_database_list
)
from .sql_utils import (
    SQLQueryBuilder,
    escape_sql_identifier,
    build_connection_string,
    format_algorithm_name
)

__all__ = [
    # Exceptions
    "DatabaseTDEError",
    "DatabaseConnectionError", 
    "TDEOperationError",
    "ConfigurationError",
    "KeyManagementError",
    "ValidationError",
    # Validation
    "validate_database_name",
    "validate_key_name",
    "validate_connection_name",
    "validate_key_parameters",
    "parse_database_list",
    # SQL Utils
    "SQLQueryBuilder",
    "escape_sql_identifier",
    "build_connection_string",
    "format_algorithm_name"
]

