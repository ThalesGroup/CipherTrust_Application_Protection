"""
Oracle TDE Deployment Tools
Reliable Oracle TDE operations with comprehensive error handling and status detection.
"""

import json
import logging
from typing import Optional
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

def register_oracle_tde_deployment_tools(server: FastMCP, db_manager):
    """Register Oracle TDE deployment tools"""
    
    @server.tool()
    async def oracle_tde_deployment(
        oracle_connection: str,
        operation: str,
        ciphertrust_username: str,
        ciphertrust_password: str,
        ciphertrust_domain: str = "root",
        software_wallet_password: str = "",
        wallet_location: str = "",
        auto_restart: bool = False,
        skip_file_operations: bool = False,
        force: bool = False
    ) -> str:
        """
        Oracle TDE deployment operations for complete database encryption setup.

        OPERATION TYPES & WHEN TO USE THEM:

        1. "setup_hsm_only" - HSM-only TDE setup (NO auto-login)
           - Use when: Setting up TDE with HSM only, skip auto-login creation
           - Creates: HSM keystore only
           - Requires: NO software_wallet_password needed
           - Result: Manual wallet opening required after database restart

        2. "setup_hsm_with_autologin" - Complete TDE setup with HSM + auto-login
           - Use when: Setting up TDE with both HSM and auto-login wallet
           - Creates: HSM keystore + software wallet + auto-login keystore  
           - Requires: software_wallet_password (for software wallet creation)
           - Result: Database can start without manual wallet opening

        3. "add_autologin" - Add auto-login to existing TDE database
           - Use when: Database already has TDE, want to add auto-login capability
           - Creates: Software wallet + auto-login keystore for existing HSM setup
           - Requires: software_wallet_password (for new software wallet)
           - Result: Existing HSM TDE + new auto-login capability

        4. "migrate_software_to_hsm" - Migrate software wallet to HSM
           - Use when: Database has software-based TDE, want to move to HSM
           - Migrates: Existing software wallet keys to HSM
           - Requires: software_wallet_password (for existing software wallet)
           - Result: HSM-based TDE (preserves auto-login if it existed)

        5. "get_tde_status" - Check current TDE status and configuration
           - Use when: Want to see current wallet status and TDE configuration
           - Returns: Comprehensive TDE status information

        Args:
            oracle_connection: Oracle database connection name (e.g., "oracle_cdb2")
            operation: TDE operation type (see above for descriptions)
            ciphertrust_username: CipherTrust Manager username 
            ciphertrust_password: CipherTrust Manager password
            ciphertrust_domain: CipherTrust Manager domain (default: "root")
            software_wallet_password: Software wallet password 
                                    - REQUIRED for: setup_hsm_with_autologin, add_autologin, migrate_software_to_hsm
                                    - NOT NEEDED for: setup_hsm_only, get_tde_status
            wallet_location: Custom wallet location (optional, auto-detected if not provided)
                           - Default: /opt/oracle/wallet/{database_name}
                           - Example: oracle_cdb2 -> /opt/oracle/wallet/cdb2
            auto_restart: Whether to restart database automatically when needed (recommended: true)
            skip_file_operations: Skip SSH file operations (for testing only)
            force: Force operation even if validation fails

        COMMON SCENARIOS:
        
        - "I want TDE with HSM only, no auto-login" -> use "setup_hsm_only"
        - "I want complete TDE setup with auto-login" -> use "setup_hsm_with_autologin"  
        - "I have HSM TDE, want to add auto-login" -> use "add_autologin"
        - "I have software TDE, want to move to HSM" -> use "migrate_software_to_hsm"

        Returns:
            JSON string with operation results, steps performed, and any errors
        """
        try:
            # Initialize ssh_manager to avoid scope issues
            ssh_manager = None
            
            # Get database handler
            db_handler = db_manager.get_database_handler(oracle_connection)
            if not db_handler:
                return json.dumps({
                    "success": False,
                    "error": f"Database connection '{oracle_connection}' not found"
                })

            # Get SSH manager for Oracle operations
            if hasattr(db_handler, 'ssh_manager'):
                ssh_manager = db_handler.ssh_manager

            # Construct HSM credentials
            if ciphertrust_domain == "root":
                hsm_credentials = f"{ciphertrust_username}:{ciphertrust_password}"
            else:
                hsm_credentials = f"{ciphertrust_domain}::{ciphertrust_username}:{ciphertrust_password}"

            # Backwards compatibility mapping for old operation names
            operation_mapping = {
                "setup_tde_from_scratch": "setup_hsm_with_autologin",
                "setup_tde_hsm_only": "setup_hsm_only", 
                "setup_autologin_existing": "add_autologin",
                "migrate_to_hsm": "migrate_software_to_hsm",
                "check_status": "get_tde_status"
            }
            
            # Map old operation names to new ones
            if operation in operation_mapping:
                logger.info(f"Operation '{operation}' is deprecated. Using '{operation_mapping[operation]}' instead.")
                operation = operation_mapping[operation]

            # Execute the requested operation
            if operation == "setup_hsm_only":
                from ..utils.oracle_setup_hsm_only import setup_tde_hsm_only
                result = await setup_tde_hsm_only(
                    db_handler, ssh_manager, hsm_credentials, auto_restart, wallet_location
                )
                
            elif operation == "setup_hsm_with_autologin":
                if not software_wallet_password:
                    return json.dumps({
                        "success": False,
                        "error": "software_wallet_password is required for TDE setup with auto-login"
                    })
                
                from ..utils.oracle_setup_from_scratch import setup_tde_from_scratch
                result = await setup_tde_from_scratch(
                    db_handler, ssh_manager, hsm_credentials, software_wallet_password, auto_restart, wallet_location
                )
                
            elif operation == "add_autologin":
                if not software_wallet_password:
                    return json.dumps({
                        "success": False,
                        "error": "software_wallet_password is required for auto-login setup"
                    })
                
                from ..utils.oracle_setup_autologin_existing import setup_autologin_existing
                result = await setup_autologin_existing(
                    db_handler, ssh_manager, software_wallet_password, hsm_credentials, auto_restart, wallet_location
                )
                
            elif operation == "migrate_software_to_hsm":
                if not software_wallet_password:
                    return json.dumps({
                        "success": False,
                        "error": "software_wallet_password is required for HSM migration"
                    })
                
                from ..utils.oracle_migrate_to_hsm import migrate_to_hsm
                result = await migrate_to_hsm(
                    db_handler, ssh_manager, hsm_credentials, software_wallet_password, auto_restart, wallet_location
                )
                
            elif operation == "get_tde_status":
                # Comprehensive status check with all required queries
                status_result = {"success": True, "current_status": {}}
                
                # 1. Wallet configuration
                wallet_config_sql = """
                SELECT WRL_TYPE, WALLET_TYPE, STATUS, CON_ID, WRL_PARAMETER, WALLET_ORDER
                FROM V$ENCRYPTION_WALLET
                ORDER BY CON_ID, WALLET_ORDER, WRL_TYPE
                """
                wallet_result = await db_handler.execute_sql(wallet_config_sql, "CDB$ROOT")
                if wallet_result["success"]:
                    status_result["current_status"]["wallet_configuration"] = wallet_result["results"][0]["data"]
                
                # 2. TDE configuration parameter
                tde_config_sql = "SELECT VALUE FROM V$PARAMETER WHERE NAME = 'tde_configuration'"
                config_result = await db_handler.execute_sql(tde_config_sql, "CDB$ROOT")
                if config_result["success"] and config_result["results"][0]["data"]:
                    status_result["current_status"]["tde_configuration"] = config_result["results"][0]["data"][0]["VALUE"]
                
                # 3. MEK count
                mek_sql = "SELECT COUNT(*) AS MEK_COUNT FROM V$ENCRYPTION_KEYS"
                mek_result = await db_handler.execute_sql(mek_sql, "CDB$ROOT")
                if mek_result["success"] and mek_result["results"][0]["data"]:
                    status_result["current_status"]["mek_count"] = mek_result["results"][0]["data"][0]["MEK_COUNT"]
                
                # 4. Additional wallet details
                wallet_details_sql = "SELECT * FROM V$ENCRYPTION_WALLET"
                details_result = await db_handler.execute_sql(wallet_details_sql, "CDB$ROOT")
                if details_result["success"]:
                    status_result["current_status"]["wallet_details"] = details_result["results"][0]["data"]
                
                status_result["current_status"]["operation"] = "get_tde_status"
                return json.dumps(status_result)

            else:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid operation: {operation}. Valid operations: setup_hsm_only, setup_hsm_with_autologin, add_autologin, migrate_software_to_hsm, get_tde_status"
                })
            
            return json.dumps(result)
            
        except Exception as e:
            logger.error(f"Oracle TDE reliable operation failed: {e}", exc_info=True)
            return json.dumps({
                "success": False,
                "error": f"Operation failed: {e}"
            })
        finally:
            # Cleanup SSH connections if needed
            if ssh_manager:
                try:
                    await ssh_manager.close()
                except:
                    pass 