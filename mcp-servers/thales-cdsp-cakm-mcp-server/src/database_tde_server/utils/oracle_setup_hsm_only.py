"""
Oracle TDE Setup HSM Only
Simple HSM-only TDE setup without auto-login
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

async def setup_tde_hsm_only(db_handler, ssh_manager, hsm_credentials: str, auto_restart: bool = False, wallet_location: str = "") -> Dict[str, Any]:
    """
    Setup TDE with HSM only (no auto-login) - exact 5-step sequence
    """
    try:
        result = {
            "success": False,
            "operation": "setup_tde_hsm_only",
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
            "step": "database_restart",
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
            "step": "open_pluggable_databases",
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
        
        result["success"] = True
        result["message"] = "TDE HSM-only setup completed successfully"
        
        return result
        
    except Exception as e:
        logger.error(f"TDE HSM-only setup failed: {e}", exc_info=True)
        return {
            "success": False,
            "operation": "setup_tde_hsm_only",
            "error": f"Setup failed: {e}",
            "steps": result.get("steps", []) if 'result' in locals() else []
        } 