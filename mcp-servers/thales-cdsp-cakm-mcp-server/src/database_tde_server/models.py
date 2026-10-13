"""
Data models and enums for Database TDE MCP Server

This module provides the data models and enumerations for the Database Transparent Data Encryption (TDE)
server. The encryption and key management functionality is powered by Thales CipherTrust Application
Key Management (CAKM) connector, which is integrated with Thales CDSP (CipherTrust Data Security Platform).

Includes models for database connections, encryption status, TDE operations, and configuration management.
"""

from typing import Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field

class DatabaseType(str, Enum):
    """Supported database types"""
    SQLSERVER = "sqlserver"
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    ORACLE = "oracle"

class EncryptionState(int, Enum):
    """TDE encryption states from sys.dm_database_encryption_keys"""
    NO_DEK = 0  # No database encryption key present, no encryption
    UNENCRYPTED = 1  # Unencrypted
    ENCRYPTION_IN_PROGRESS = 2  # Encryption in progress
    ENCRYPTED = 3  # Encrypted
    KEY_CHANGE_IN_PROGRESS = 4  # Key change in progress
    DECRYPTION_IN_PROGRESS = 5  # Decryption in progress

class KeyType(str, Enum):
    """Key types supported"""
    RSA = "RSA"
    AES = "AES"

class SSHConfig(BaseModel):
    """SSH configuration for remote database operations"""
    host: str = Field(description="SSH hostname or IP")
    username: str = Field(description="SSH username")
    password: Optional[str] = Field(default=None, description="SSH password")
    private_key_path: Optional[str] = Field(default=None, description="Path to SSH private key")
    port: int = Field(default=22, description="SSH port")
    timeout: int = Field(default=30, description="SSH connection timeout")
    
    class Config:
        extra = "allow"

class OracleConfig(BaseModel):
    """Oracle-specific configuration"""
    oracle_home: str = Field(description="Oracle Home directory")
    oracle_sid: str = Field(description="Oracle SID")
    service_name: Optional[str] = Field(default=None, description="Oracle service name")
    mode: str = Field(default="SYSDBA", description="Connection mode - SYSDBA, SYSOPER, or None")
    tns_admin: Optional[str] = Field(default=None, description="TNS_ADMIN directory (auto-detected if not specified)")
    wallet_root: Optional[str] = Field(default=None, description="Default wallet root directory")
    
    class Config:
        extra = "allow"

class DatabaseConnection(BaseModel):
    """Enhanced database connection configuration"""
    name: str = Field(description="Connection name identifier")
    db_type: DatabaseType = Field(description="Database type")
    host: str = Field(description="Database server hostname or IP")
    port: int = Field(description="Database server port")
    instance: Optional[str] = Field(default=None, description="SQL Server instance name or Oracle service name")
    database: Optional[str] = Field(default=None, description="Database name")
    username: str = Field(description="Database username")
    password: str = Field(description="Database password", exclude=True)
    driver: Optional[str] = Field(default=None, description="Database driver")
    connection_string: Optional[str] = Field(default=None, description="Custom connection string")
    
    # Enhanced configuration options
    ssh_config: Optional[SSHConfig] = Field(default=None, description="SSH configuration for remote operations")
    oracle_config: Optional[OracleConfig] = Field(default=None, description="Oracle-specific configuration")
    additional_params: Optional[Dict[str, Any]] = Field(default=None, description="Additional connection parameters")

    class Config:
        # Allow additional fields for flexibility
        extra = "allow"

class TDEOperationResult(BaseModel):
    """Result of a TDE operation"""
    success: bool
    operation: str
    database: Optional[str] = None
    connection: Optional[str] = None
    key_name: Optional[str] = None
    algorithm: Optional[str] = None
    steps: Optional[list] = None
    error: Optional[str] = None
    timestamp: Optional[str] = None

class EncryptionStatusInfo(BaseModel):
    """Database encryption status information"""
    database_name: str
    database_id: int
    is_encrypted: bool
    encryption_state: Optional[int] = None
    encryption_state_desc: Optional[str] = None
    percent_complete: Optional[float] = None
    key_algorithm: Optional[str] = None
    key_length: Optional[int] = None
    encryptor_name: Optional[str] = None
    encryptor_type: Optional[str] = None

class OracleConnectionParams(BaseModel):
    """Oracle-specific connection parameters"""
    service_name: Optional[str] = Field(default=None, description="Oracle service name")
    mode: Optional[str] = Field(default=None, description="Connection mode - SYSDBA, SYSOPER, or None")
    wallet_location: Optional[str] = Field(default=None, description="Wallet directory location")
    
    class Config:
        extra = "allow"