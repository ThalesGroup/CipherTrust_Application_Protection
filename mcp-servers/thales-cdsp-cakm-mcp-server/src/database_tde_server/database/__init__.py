"""
Database implementations for TDE operations
"""

from .base import DatabaseInterface
from .ms_sql_server import MSSQLServerDatabase  # Renamed from sqlserver.py
from .oracle import OracleDatabase

__all__ = ["DatabaseInterface", "MSSQLServerDatabase", "OracleDatabase"]