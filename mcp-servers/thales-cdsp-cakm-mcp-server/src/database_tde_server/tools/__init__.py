"""
Database TDE tools package - CONSOLIDATED with unified tools

AUTO-LOGIN TOOLS CONSOLIDATION:
- All auto-login functionality is now consolidated in manage_oracle_autologin
- Removed redundant tools: enable_oracle_autologin, configure_oracle_autologin_hsm
- Use manage_oracle_autologin with appropriate operation parameter:
  * operation="setup" - Complete auto-login setup from scratch
  * operation="setup_hsm" - Setup auto-login for HSM migration
  * operation="create" - Create auto-login wallet from existing keystore
  * operation="update" - Update auto-login wallet password
  * operation="update_secret" - Update HSM credentials in auto-login wallet
  * operation="remove" - Remove auto-login wallet

ORACLE RELIABILITY IMPROVEMENTS:
- Added oracle_reliable_tools for bulletproof TDE operations
- Fixed container switching logic to handle "ALL" correctly
- Improved error handling and rollback mechanisms
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