"""
Database TDE MCP Server

A Model Context Protocol server for database Transparent Data Encryption (TDE) operations.
Database encryption and encryption key management are handled by Thales CipherTrust Application 
Key Management (CAKM) connector, which is integrated with Thales CDSP (CipherTrust Data Security Platform).

This server provides tools for managing TDE across multiple database platforms including SQL Server and Oracle.
"""

__version__ = "1.0.0"  # Fixed syntax
__author__ = "Sanyam Bassi"  # Fixed syntax

from .server import main
from .config import DatabaseTDESettings
from .models import DatabaseType, EncryptionState, KeyType

__all__ = [  # Fixed syntax
    "main",
    "DatabaseTDESettings", 
    "DatabaseType",
    "EncryptionState",
    "KeyType"
]
