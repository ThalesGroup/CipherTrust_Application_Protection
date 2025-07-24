"""
Oracle TDE Migration to HSM
Migrate existing software wallet to HSM with or without auto-login
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

async def migrate_to_hsm(db_handler, ssh_manager, hsm_credentials: str, software_wallet_password: str, auto_restart: bool = False, wallet_location: str = "") -> Dict[str, Any]:
    """
    Migrate existing software wallet to HSM with auto-login detection
    """
    try:
        result = {
            "success": False,
            "operation": "migrate_to_hsm",
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
        
        # Step 1: Check current wallet status
        wallet_status_sql = "SELECT WRL_TYPE, WALLET_TYPE, STATUS FROM V$ENCRYPTION_WALLET ORDER BY WRL_TYPE"
        wallet_status_result = await db_handler.execute_sql(wallet_status_sql, "CDB$ROOT")
        
        if not wallet_status_result["success"]:
            result["errors"].append(f"Failed to check wallet status: {wallet_status_result.get('error')}")
            return result
        
        wallet_info = wallet_status_result["results"][0]["data"] if wallet_status_result["results"][0]["data"] else []
        
        # Check if HSM is already present
        hsm_wallets = [w for w in wallet_info if w.get("WRL_TYPE") == "HSM"]
        if hsm_wallets:
            return {
                "success": False,
                "error": "HSM wallet already exists - migration not needed",
                "current_wallet_status": wallet_info
            }
        
        # Check if auto-login is present
        autologin_wallets = [w for w in wallet_info if w.get("WALLET_TYPE") == "AUTOLOGIN"]
        has_autologin = len(autologin_wallets) > 0
        
        result["steps"].append({
            "step": "check_wallet_status",
            "has_autologin": has_autologin,
            "current_wallets": wallet_info,
            "success": True
        })
        
        # Get wallet root parameter
        wallet_root_sql = "SELECT VALUE FROM V$PARAMETER WHERE NAME = 'wallet_root'"
        wallet_root_result = await db_handler.execute_sql(wallet_root_sql, "CDB$ROOT")
        
        wallet_root = None
        if wallet_root_result["success"] and wallet_root_result["results"][0]["data"]:
            wallet_root = wallet_root_result["results"][0]["data"][0]["VALUE"]
        
        if not wallet_root:
            result["errors"].append("WALLET_ROOT parameter is not set")
            return result
        
        if has_autologin:
            # Migration WITH auto-login preservation
            result["migration_type"] = "with_autologin"
            
            # Step 1: Add HSM secret to existing auto-login wallet
            tde_location = f"{wallet_root}/tde"  # /tde is important here
            add_secret_sql = f"ADMINISTER KEY MANAGEMENT ADD SECRET '{hsm_credentials}' FOR CLIENT 'HSM_PASSWORD' TO AUTO_LOGIN KEYSTORE '{tde_location}' WITH BACKUP"
            add_secret_result = await db_handler.execute_sql(add_secret_sql, "CDB$ROOT")
            
            if not add_secret_result["success"]:
                result["errors"].append(f"Failed to add HSM secret to auto-login wallet: {add_secret_result.get('error')}")
                return result
                
            result["steps"].append({
                "step": "add_hsm_secret_to_autologin",
                "sql": add_secret_sql,
                "success": True
            })
            
            # Step 2: Update TDE config to HSM|FILE
            tde_config_sql = "ALTER SYSTEM SET TDE_CONFIGURATION='KEYSTORE_CONFIGURATION=HSM|FILE' SCOPE=BOTH"
            tde_config_result = await db_handler.execute_sql(tde_config_sql, "CDB$ROOT")
            
            if not tde_config_result["success"]:
                result["errors"].append(f"Failed to set TDE configuration to HSM|FILE: {tde_config_result.get('error')}")
                return result
                
            result["steps"].append({
                "step": "set_tde_config_hsm_file",
                "sql": tde_config_sql,
                "success": True
            })
            
            # Step 3: Migrate key (with auto-login, no FORCE needed)
            migrate_key_sql = f"ADMINISTER KEY MANAGEMENT SET ENCRYPTION KEY IDENTIFIED BY \"{hsm_credentials}\" MIGRATE USING \"{software_wallet_password}\" WITH BACKUP"
            migrate_key_result = await db_handler.execute_sql(migrate_key_sql, "CDB$ROOT")
            
            if not migrate_key_result["success"]:
                result["errors"].append(f"Failed to migrate encryption key: {migrate_key_result.get('error')}")
                return result
                
            result["steps"].append({
                "step": "migrate_encryption_key",
                "sql": migrate_key_sql,
                "success": True
            })
            
            # Step 4: Database restart (REQUIRED to complete migration)
            if not ssh_manager:
                result["errors"].append("SSH manager is required for database restart to complete migration")
                return result
                
            oracle_sid = db_handler.connection.oracle_config.oracle_sid
            restart_result = ssh_manager.restart_oracle_database(oracle_sid)
                
            if not restart_result["success"]:
                result["errors"].append(f"Database restart failed: {restart_result.get('error')}")
                return result
                
            result["steps"].append({
                "step": "database_restart",
                "reason": "Complete migration (REQUIRED)",
                "success": True
            })
            
            # Step 5: Open all pluggable databases
            open_pdbs_sql = "ALTER PLUGGABLE DATABASE ALL OPEN READ WRITE"
            open_pdbs_result = await db_handler.execute_sql(open_pdbs_sql, "CDB$ROOT")
            
            if not open_pdbs_result["success"]:
                result["errors"].append(f"Failed to open pluggable databases: {open_pdbs_result.get('error')}")
                # Don't fail the entire operation for this
            
            result["steps"].append({
                "step": "open_pluggable_databases",
                "sql": open_pdbs_sql,
                "success": open_pdbs_result["success"]
            })
        
        else:
            # Migration WITHOUT auto-login
            result["migration_type"] = "without_autologin"
            
            # Step 1: Update TDE config to HSM|FILE
            tde_config_sql = "ALTER SYSTEM SET TDE_CONFIGURATION='KEYSTORE_CONFIGURATION=HSM|FILE' SCOPE=BOTH"
            tde_config_result = await db_handler.execute_sql(tde_config_sql, "CDB$ROOT")
            
            if not tde_config_result["success"]:
                result["errors"].append(f"Failed to set TDE configuration to HSM|FILE: {tde_config_result.get('error')}")
                return result
                
            result["steps"].append({
                "step": "set_tde_config_hsm_file",
                "sql": tde_config_sql,
                "success": True
            })
            
            # Step 2: Migrate key (FORCE required without auto-login)
            migrate_key_sql = f"ADMINISTER KEY MANAGEMENT SET ENCRYPTION KEY IDENTIFIED BY \"{hsm_credentials}\" FORCE KEYSTORE MIGRATE USING \"{software_wallet_password}\" WITH BACKUP"
            migrate_key_result = await db_handler.execute_sql(migrate_key_sql, "CDB$ROOT")
            
            if not migrate_key_result["success"]:
                result["errors"].append(f"Failed to migrate encryption key: {migrate_key_result.get('error')}")
                return result
                
            result["steps"].append({
                "step": "migrate_encryption_key_force",
                "sql": migrate_key_sql,
                "success": True
            })
            
            # Step 3: Set TDE configuration to HSM only
            tde_hsm_sql = "ALTER SYSTEM SET TDE_CONFIGURATION='KEYSTORE_CONFIGURATION=HSM' SCOPE=BOTH"
            tde_hsm_result = await db_handler.execute_sql(tde_hsm_sql, "CDB$ROOT")
            
            if not tde_hsm_result["success"]:
                result["errors"].append(f"Failed to set TDE configuration to HSM: {tde_hsm_result.get('error')}")
                return result
                
            result["steps"].append({
                "step": "set_tde_config_hsm_only",
                "sql": tde_hsm_sql,
                "success": True
            })
            
            # Step 4: Database restart (REQUIRED to complete migration)
            if not ssh_manager:
                result["errors"].append("SSH manager is required for database restart to complete migration")
                return result
                
            oracle_sid = db_handler.connection.oracle_config.oracle_sid
            restart_result = ssh_manager.restart_oracle_database(oracle_sid)
                
            if not restart_result["success"]:
                result["errors"].append(f"Database restart failed: {restart_result.get('error')}")
                return result
                    
            result["steps"].append({
                "step": "database_restart",
                "reason": "Complete migration (REQUIRED)",
                "success": True
            })
                
            # Step 4: Open all pluggable databases after restart
            open_pdbs_sql = "ALTER PLUGGABLE DATABASE ALL OPEN READ WRITE"
            open_pdbs_result = await db_handler.execute_sql(open_pdbs_sql, "CDB$ROOT")
            
            if not open_pdbs_result["success"]:
                result["errors"].append(f"Failed to open pluggable databases: {open_pdbs_result.get('error')}")
                # Don't fail the entire operation for this
            
            result["steps"].append({
                "step": "open_pluggable_databases",
                "sql": open_pdbs_sql,
                "success": open_pdbs_result["success"]
            })
            
            # Step 6: Open HSM wallet
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
        
        # Final step: Check wallet status
        final_status_sql = "SELECT WRL_TYPE, WALLET_TYPE, STATUS FROM V$ENCRYPTION_WALLET ORDER BY WRL_TYPE"
        final_status_result = await db_handler.execute_sql(final_status_sql, "CDB$ROOT")
        
        if final_status_result["success"]:
            result["final_wallet_status"] = final_status_result["results"][0]["data"]
        
        result["success"] = True
        result["message"] = f"Migration to HSM completed successfully ({result['migration_type']})"
        
        return result
        
    except Exception as e:
        logger.error(f"Migration to HSM failed: {e}", exc_info=True)
        return {
            "success": False,
            "operation": "migrate_to_hsm",
            "error": f"Migration failed: {e}",
            "steps": result.get("steps", []) if 'result' in locals() else []
        } 