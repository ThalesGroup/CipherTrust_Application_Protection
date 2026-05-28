"""
Database interface implementations for TDE operations

This package provides database-specific implementations for Transparent Data Encryption (TDE) operations.
Database encryption and encryption key management are handled by Thales CipherTrust Application Key Management (CAKM)
connector, which is integrated with Thales CDSP (CipherTrust Data Security Platform).

Available implementations:
- base: Abstract base class defining the interface for database TDE operations
- ms_sql_server: SQL Server implementation with TDE operations and key management
- oracle: Oracle implementation with TDE operations, wallet management, and container support
"""

from .base import DatabaseInterface
from .ms_sql_server import MSSQLServerDatabase  # Renamed from sqlserver.py
from .oracle import OracleDatabase

__all__ = ["DatabaseInterface", "MSSQLServerDatabase", "OracleDatabase"]