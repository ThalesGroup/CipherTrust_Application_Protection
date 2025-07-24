"""
Oracle TDE Setup From Scratch
Complete TDE setup with HSM + auto-login configuration
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

async def setup_tde_from_scratch(db_handler, ssh_manager, hsm_credentials: str, software_wallet_password: str, auto_restart: bool = False, wallet_location: str = "") -> Dict[str, Any]:
    """
    Setup TDE from scratch with the exact 12-step sequence:
    1. Set WALLET_ROOT and restart
    2. Configure HSM and create MEK
    3. Create software wallet with HSM credentials
    4. Create auto-login keystore
    5. Final HSM|FILE configuration and restart
    """
    try:
        result = {
            "success": False,
            "operation": "setup_tde_from_scratch",
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
        
        # Step 1: Set WALLET_ROOT parameter
        wallet_root_sql = f"ALTER SYSTEM SET WALLET_ROOT='{final_wallet_location}' SCOPE=SPFILE"
        wallet_root_result = await db_handler.execute_sql(wallet_root_sql, "CDB$ROOT")
        
        if not wallet_root_result["success"]:
            result["errors"].append(f"Failed to set WALLET_ROOT: {wallet_root_result.get('error')}")
            return result
        
        result["steps"].append({
            "step": "set_wallet_root", 
            "sql": wallet_root_sql,
            "success": True
        })
        
        # Step 2: Database restart (REQUIRED for WALLET_ROOT to take effect)
        if not ssh_manager:
            result["errors"].append("SSH manager is required for database restart after WALLET_ROOT change")
            return result
            
        oracle_sid = db_handler.connection.oracle_config.oracle_sid
        restart_result = ssh_manager.restart_oracle_database(oracle_sid)
        
        if not restart_result["success"]:
            result["errors"].append(f"Database restart failed: {restart_result.get('error')}")
            return result
            
        result["steps"].append({
            "step": "database_restart_1",
            "reason": "WALLET_ROOT parameter change (REQUIRED)", 
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
        
        # Step 3: Set TDE configuration to HSM
        tde_hsm_sql = "ALTER SYSTEM SET TDE_CONFIGURATION='KEYSTORE_CONFIGURATION=HSM' SCOPE=BOTH"
        tde_hsm_result = await db_handler.execute_sql(tde_hsm_sql, "CDB$ROOT")
        
        if not tde_hsm_result["success"]:
            result["errors"].append(f"Failed to set TDE configuration to HSM: {tde_hsm_result.get('error')}")
            return result
            
        result["steps"].append({
            "step": "set_tde_config_hsm",
            "sql": tde_hsm_sql,
            "success": True
        })
        
        # Step 4: Open HSM keystore
        open_hsm_sql = f"ADMINISTER KEY MANAGEMENT SET KEYSTORE OPEN IDENTIFIED BY \"{hsm_credentials}\" CONTAINER=ALL"
        open_hsm_result = await db_handler.execute_sql(open_hsm_sql, "CDB$ROOT")
        
        if not open_hsm_result["success"]:
            result["errors"].append(f"Failed to open HSM keystore: {open_hsm_result.get('error')}")
            return result
            
        result["steps"].append({
            "step": "open_hsm_keystore",
            "sql": open_hsm_sql,
            "success": True
        })
        
        # Step 5: Create Master Encryption Key in HSM
        create_mek_sql = f"ADMINISTER KEY MANAGEMENT SET KEY IDENTIFIED BY \"{hsm_credentials}\" WITH BACKUP CONTAINER=ALL"
        create_mek_result = await db_handler.execute_sql(create_mek_sql, "CDB$ROOT")
        
        if not create_mek_result["success"]:
            result["errors"].append(f"Failed to create MEK in HSM: {create_mek_result.get('error')}")
            return result
            
        result["steps"].append({
            "step": "create_mek_hsm",
            "sql": create_mek_sql, 
            "success": True
        })
        
        # Step 6: Close HSM keystore
        close_hsm_sql = f"ADMINISTER KEY MANAGEMENT SET KEYSTORE CLOSE IDENTIFIED BY \"{hsm_credentials}\" CONTAINER=ALL"
        close_hsm_result = await db_handler.execute_sql(close_hsm_sql, "CDB$ROOT")
        
        if not close_hsm_result["success"]:
            result["errors"].append(f"Failed to close HSM keystore: {close_hsm_result.get('error')}")
            return result
            
        result["steps"].append({
            "step": "close_hsm_keystore",
            "sql": close_hsm_sql,
            "success": True
        })
        
        # Step 7: Set TDE configuration to FILE|HSM
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
        
        # Step 8: Create software wallet
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
        
        # Step 9: Open software wallet
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
        
        # Step 10: Add HSM credentials to software wallet
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
        
        # Step 11: Create auto-login keystore
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
        
        # Step 12: Set final TDE configuration to HSM|FILE
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
        
        # Step 13: Final database restart (REQUIRED for final TDE configuration)
        if not ssh_manager:
            result["errors"].append("SSH manager is required for final database restart")
            return result
            
        oracle_sid = db_handler.connection.oracle_config.oracle_sid
        final_restart_result = ssh_manager.restart_oracle_database(oracle_sid)
        
        if not final_restart_result["success"]:
            result["errors"].append(f"Final database restart failed: {final_restart_result.get('error')}")
            return result
            
        result["steps"].append({
            "step": "database_restart_final",
            "reason": "Final TDE configuration (REQUIRED)",
            "success": True
        })
        
        # Open all pluggable databases after final restart
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
        result["message"] = "TDE setup from scratch completed successfully with auto-login"
        
        return result
        
    except Exception as e:
        logger.error(f"TDE setup from scratch failed: {e}", exc_info=True)
        return {
            "success": False,
            "operation": "setup_tde_from_scratch",
            "error": f"Setup failed: {e}",
            "steps": result.get("steps", []) if 'result' in locals() else []
        } 