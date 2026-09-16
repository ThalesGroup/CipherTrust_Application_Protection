"""
Database TDE tools package

This package provides tools for managing database Transparent Data Encryption (TDE).
Database encryption and encryption key management are handled by Thales CipherTrust Application Key Management (CAKM)
connector, which is integrated with Thales CDSP (CipherTrust Data Security Platform).

Available tools:
- list_database_connections: List all configured database connections
- status_tde_ekm: Comprehensive TDE status assessment for SQL Server and Oracle
  - SQL Server operations: assess_sql, compliance_report, best_practices, export_config, validate_setup
  - Oracle operations: assess_oracle, list_containers, list_tablespaces
- manage_sql_ekm_objects: Manage SQL Server EKM objects (providers, credentials, logins)
- manage_sql_keys: Manage SQL Server cryptographic keys (create, list, drop, rotate)
- manage_oracle_keys: Manage Oracle Master Encryption Keys (generate, rotate, list)
- manage_sql_encryption: Encrypt/decrypt SQL Server databases
- manage_oracle_tablespace_encryption: Encrypt Oracle tablespaces and list encryption status
- manage_oracle_wallet: Comprehensive Oracle wallet management
  - Operations: open, close, status, backup, merge, autologin
  - Autologin operations: create, update, remove, setup, setup_hsm, update_secret
- manage_oracle_configuration: Manage Oracle TDE configuration parameters
  - Operations: get, set, verify
- oracle_tde_deployment: Complete Oracle TDE deployment operations
  - Operations: setup_hsm_only, setup_hsm_with_autologin, add_autologin, migrate_software_to_hsm, get_tde_status
"""

from .key_management_tools import register_key_management_tools
from .encryption_tools import register_encryption_tools
from .status_tools import register_status_tools
from .security_tools import register_security_tools
from .oracle_configuration_tools import register_oracle_configuration_tools
from .oracle_wallet_tools import register_oracle_wallet_tools
from .connection_tools import register_connection_tools
from .oracle_tde_deployment_tools import register_oracle_tde_deployment_tools


def register_all_tools(server, db_manager):
    """Register all MCP tools with the server"""
    register_key_management_tools(server, db_manager)
    register_encryption_tools(server, db_manager)
    register_status_tools(server, db_manager)
    register_security_tools(server, db_manager)
    register_oracle_configuration_tools(server, db_manager)
    register_oracle_wallet_tools(server, db_manager)
    register_connection_tools(server, db_manager)
    register_oracle_tde_deployment_tools(server, db_manager)


__all__ = [
    "register_connection_tools",
    "register_security_tools",
    "register_encryption_tools",
    "register_key_management_tools",
    "register_status_tools",
    "register_oracle_configuration_tools",
    "register_oracle_wallet_tools",
    "register_all_tools",
]