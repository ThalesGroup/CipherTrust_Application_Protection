"""
Utility modules for Database TDE MCP Server
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

