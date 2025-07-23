"""
Database TDE MCP Server
A Model Context Protocol server for database Transparent Data Encryption (TDE) operations using CipherTrust Application Key Management (CAKM) EKM providers.
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
