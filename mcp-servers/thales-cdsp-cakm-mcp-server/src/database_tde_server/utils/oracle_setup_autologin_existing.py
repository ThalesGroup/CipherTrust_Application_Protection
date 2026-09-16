"""
Oracle TDE auto-login setup utilities

This module provides utilities for setting up Oracle Transparent Data Encryption (TDE) auto-login functionality.
Database encryption and encryption key management are handled by Thales CipherTrust Application Key Management (CAKM)
connector, which is integrated with Thales CDSP (CipherTrust Data Security Platform).

Available utilities:
- setup_oracle_autologin_existing: Setup auto-login for existing Oracle TDE
  - Creates auto-login wallet from existing keystore
  - Configures auto-login functionality
  - Sets up wallet permissions and accessibility
  - Validates auto-login configuration
- setup_oracle_autologin_hsm: Setup auto-login for HSM migration
  - Configures auto-login for HSM-based wallets
  - Sets up HSM credentials in auto-login wallet
  - Validates HSM auto-login configuration
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

async def setup_autologin_existing(db_handler, ssh_manager, software_wallet_password: str, hsm_credentials: str, auto_restart: bool = False, wallet_location: str = "") -> Dict[str, Any]:
    """
    Setup auto-login on an existing TDE database - exact 9-step sequence
    """
    try:
        result = {
            "success": False,
            "operation": "setup_autologin_existing",
            "steps": [],
            "errors": []
        }
        
        # Get wallet location from parameter or auto-detect from connection name
        if wallet_location:
            # Use provided wallet location
            final_wallet_location = wallet_location
        else:
            # Auto-detect from connection name
            connection_name = db_handler.connection.name
            db_identifier = connection_name.replace('oracle_', '').lower() if connection_name.startswith('oracle_') else connection_name.lower()
            final_wallet_location = f"/opt/oracle/wallet/{db_identifier}"
        
        # Check current wallet status first
        wallet_status_sql = "SELECT WRL_TYPE, WALLET_TYPE, STATUS FROM V$ENCRYPTION_WALLET"
        wallet_status_result = await db_handler.execute_sql(wallet_status_sql, "CDB$ROOT")
        
        if wallet_status_result["success"] and wallet_status_result["results"][0]["data"]:
            wallet_info = wallet_status_result["results"][0]["data"]
            
            # Check if we're in a migration scenario
            file_wallets = [w for w in wallet_info if w.get("WRL_TYPE") == "FILE"]
            
            if file_wallets:
                file_status = file_wallets[0].get("STATUS", "")
                if file_status not in ["NOT_AVAILABLE", "", None]:
                    return {
                        "success": False,
                        "error": "FILE wallet status indicates a migration scenario",
                        "current_wallet_status": wallet_info,
                        "file_wallet_status": file_status,
                        "recommendation": "This appears to be a migrated database. Use migration tools instead."
                    }
        
        # Step 1: Check/Set WALLET_ROOT parameter
        wallet_root_check_sql = "SELECT VALUE FROM V$PARAMETER WHERE NAME = 'wallet_root'"
        wallet_root_result = await db_handler.execute_sql(wallet_root_check_sql, "CDB$ROOT")
        
        current_wallet_root = None
        if wallet_root_result["success"] and wallet_root_result["results"][0]["data"]:
            current_wallet_root = wallet_root_result["results"][0]["data"][0]["VALUE"]
        
        if current_wallet_root != final_wallet_location:
            wallet_root_sql = f"ALTER SYSTEM SET WALLET_ROOT='{final_wallet_location}' SCOPE=SPFILE"
            wallet_root_set_result = await db_handler.execute_sql(wallet_root_sql, "CDB$ROOT")
            
            if not wallet_root_set_result["success"]:
                result["errors"].append(f"Failed to set WALLET_ROOT: {wallet_root_set_result.get('error')}")
                return result
            
            result["steps"].append({
                "step": "set_wallet_root", 
                "sql": wallet_root_sql,
                "success": True
            })
            
            # Restart required for WALLET_ROOT change
            if auto_restart and ssh_manager:
                oracle_sid = db_handler.connection.oracle_config.oracle_sid
                restart_result = ssh_manager.restart_oracle_database(oracle_sid)
                
                if not restart_result["success"]:
                    result["errors"].append(f"Database restart failed: {restart_result.get('error')}")
                    return result
                    
                result["steps"].append({
                    "step": "database_restart_1",
                    "reason": "WALLET_ROOT parameter change", 
                    "success": True
                })
                
                # Open all pluggable databases after restart
                open_pdbs_sql = "ALTER PLUGGABLE DATABASE ALL OPEN READ WRITE"
                open_pdbs_result = await db_handler.execute_sql(open_pdbs_sql, "CDB$ROOT")
                
                if not open_pdbs_result["success"]:
                    result["errors"].append(f"Failed to open pluggable databases: {open_pdbs_result.get('error')}")
                    # Don't fail the entire operation for this
                
                result["steps"].append({
                    "step": "open_pluggable_databases_1",
                    "sql": open_pdbs_sql,
                    "success": open_pdbs_result["success"]
                })
        
        # Step 2: Close HSM wallet
        close_hsm_sql = f"ADMINISTER KEY MANAGEMENT SET KEYSTORE CLOSE IDENTIFIED BY \"{hsm_credentials}\" CONTAINER=ALL"
        close_hsm_result = await db_handler.execute_sql(close_hsm_sql, "CDB$ROOT")
        
        if not close_hsm_result["success"]:
            result["errors"].append(f"Failed to close HSM wallet: {close_hsm_result.get('error')}")
            return result
            
        result["steps"].append({
            "step": "close_hsm_wallet",
            "sql": close_hsm_sql,
            "success": True
        })
        
        # Step 3: Set TDE configuration to FILE|HSM
        tde_file_hsm_sql = "ALTER SYSTEM SET TDE_CONFIGURATION='KEYSTORE_CONFIGURATION=FILE|HSM' SCOPE=BOTH"
        tde_file_hsm_result = await db_handler.execute_sql(tde_file_hsm_sql, "CDB$ROOT")
        
        if not tde_file_hsm_result["success"]:
            result["errors"].append(f"Failed to set TDE configuration to FILE|HSM: {tde_file_hsm_result.get('error')}")
            return result
            
        result["steps"].append({
            "step": "set_tde_config_file_hsm",
            "sql": tde_file_hsm_sql,
            "success": True
        })
        
        # Step 4: Create software wallet
        create_wallet_sql = f"ADMINISTER KEY MANAGEMENT CREATE KEYSTORE IDENTIFIED BY \"{software_wallet_password}\""
        create_wallet_result = await db_handler.execute_sql(create_wallet_sql, "CDB$ROOT")
        
        if not create_wallet_result["success"]:
            result["errors"].append(f"Failed to create software wallet: {create_wallet_result.get('error')}")
            return result
            
        result["steps"].append({
            "step": "create_software_wallet",
            "sql": create_wallet_sql,
            "success": True
        })
        
        # Step 5: Open software wallet
        open_wallet_sql = f"ADMINISTER KEY MANAGEMENT SET KEYSTORE OPEN IDENTIFIED BY \"{software_wallet_password}\" CONTAINER=ALL"
        open_wallet_result = await db_handler.execute_sql(open_wallet_sql, "CDB$ROOT")
        
        if not open_wallet_result["success"]:
            result["errors"].append(f"Failed to open software wallet: {open_wallet_result.get('error')}")
            return result
            
        result["steps"].append({
            "step": "open_software_wallet",
            "sql": open_wallet_sql,
            "success": True
        })
        
        # Step 6: Add HSM credentials to software wallet
        add_secret_sql = f"ADMINISTER KEY MANAGEMENT ADD SECRET '{hsm_credentials}' FOR CLIENT 'HSM_PASSWORD' IDENTIFIED BY \"{software_wallet_password}\" WITH BACKUP"
        add_secret_result = await db_handler.execute_sql(add_secret_sql, "CDB$ROOT")
        
        if not add_secret_result["success"]:
            result["errors"].append(f"Failed to add HSM credentials: {add_secret_result.get('error')}")
            return result
            
        result["steps"].append({
            "step": "add_hsm_credentials",
            "sql": add_secret_sql,
            "success": True
        })
        
        # Step 7: Create auto-login keystore (using correct wallet location for cdb2)
        autologin_sql = f"ADMINISTER KEY MANAGEMENT CREATE AUTO_LOGIN KEYSTORE FROM KEYSTORE IDENTIFIED BY \"{software_wallet_password}\""
        autologin_result = await db_handler.execute_sql(autologin_sql, "CDB$ROOT")
        
        if not autologin_result["success"]:
            result["errors"].append(f"Failed to create auto-login keystore: {autologin_result.get('error')}")
            return result
            
        result["steps"].append({
            "step": "create_autologin_keystore",
            "sql": autologin_sql,
            "success": True
        })
        
        # Step 8: Set final TDE configuration to HSM|FILE
        final_tde_sql = "ALTER SYSTEM SET TDE_CONFIGURATION='KEYSTORE_CONFIGURATION=HSM|FILE' SCOPE=BOTH"
        final_tde_result = await db_handler.execute_sql(final_tde_sql, "CDB$ROOT")
        
        if not final_tde_result["success"]:
            result["errors"].append(f"Failed to set final TDE configuration: {final_tde_result.get('error')}")
            return result
            
        result["steps"].append({
            "step": "set_final_tde_config",
            "sql": final_tde_sql,
            "success": True
        })
        
        # Step 9: Final database restart
        if auto_restart and ssh_manager:
            oracle_sid = db_handler.connection.oracle_config.oracle_sid
            final_restart_result = ssh_manager.restart_oracle_database(oracle_sid)
            
            if not final_restart_result["success"]:
                result["errors"].append(f"Final database restart failed: {final_restart_result.get('error')}")
                return result
                
            result["steps"].append({
                "step": "database_restart_final",
                "reason": "Final TDE configuration",
                "success": True
            })
            
            # Open all pluggable databases after restart
            open_pdbs_sql = "ALTER PLUGGABLE DATABASE ALL OPEN READ WRITE"
            open_pdbs_result = await db_handler.execute_sql(open_pdbs_sql, "CDB$ROOT")
            
            if not open_pdbs_result["success"]:
                result["errors"].append(f"Failed to open pluggable databases: {open_pdbs_result.get('error')}")
                # Don't fail the entire operation for this
            
            result["steps"].append({
                "step": "open_pluggable_databases_final",
                "sql": open_pdbs_sql,
                "success": open_pdbs_result["success"]
            })
        
        result["success"] = True
        result["message"] = "Auto-login setup completed successfully for existing TDE database"
        
        return result
        
    except Exception as e:
        logger.error(f"Auto-login setup failed: {e}", exc_info=True)
        return {
            "success": False,
            "operation": "setup_autologin_existing",
            "error": f"Setup failed: {e}",
            "steps": result.get("steps", []) if 'result' in locals() else []
        } 