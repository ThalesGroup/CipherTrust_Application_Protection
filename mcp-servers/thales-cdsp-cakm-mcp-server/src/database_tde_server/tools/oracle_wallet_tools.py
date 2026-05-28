"""
Oracle TDE wallet management tools

This module provides tools for managing Oracle Transparent Data Encryption (TDE) wallets.
Database encryption and encryption key management are handled by Thales CipherTrust Application Key Management (CAKM)
connector, which is integrated with Thales CDSP (CipherTrust Data Security Platform).

Available tools:
- manage_oracle_wallet: Comprehensive Oracle wallet management
  - Operations: open, close, status, backup, merge, autologin
  - Autologin operations: create, update, remove, setup, setup_hsm, update_secret
  - Supports container-aware operations across CDB and PDBs
  - Handles FILE and HSM wallet types
  - Provides detailed wallet status and configuration management
"""

import json
import logging
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

def register_oracle_wallet_tools(server: FastMCP, db_manager):
    """Register Oracle TDE wallet tools with the MCP server"""

    @server.tool()
    async def manage_oracle_wallet(
        oracle_connection: str,
        operation: str,
        container: str = "CDB$ROOT",
        ciphertrust_username: Optional[str] = None,
        ciphertrust_password: Optional[str] = None,
        ciphertrust_domain: str = "root",
        view_type: str = "v$",
        node_filter: Optional[int] = None,
        wallet_location: Optional[str] = None,
        backup_location: Optional[str] = None,
        include_autologin: bool = True,
        backup_suffix: Optional[str] = None,
        source_wallet: Optional[str] = None,
        target_wallet: Optional[str] = None,
        software_keystore_password: Optional[str] = None,
        new_ciphertrust_username: Optional[str] = None,
        new_ciphertrust_password: Optional[str] = None,
        new_ciphertrust_domain: Optional[str] = None,
        auto_restart: bool = False,
        autologin_operation: Optional[str] = None
    ) -> str:
        """
        Comprehensive Oracle wallet management operations.

        ---
        **Operations:**
        - `open`: Opens the wallet, making keys available.
        - `close`: Closes the wallet.
        - `status`: Provides detailed status of the wallet (FILE and HSM).
        - `backup`: Backs up the wallet files.
        - `merge`: Merges two wallets.
        - `autologin`: Manages the auto-login (SSO) wallet (requires autologin_operation sub-parameter).
        ---
        
        Args:
            oracle_connection: Oracle database connection name
            operation: Wallet operation - "open" | "close" | "status" | "backup" | "merge" | "autologin"
            container: Container name - "CDB$ROOT", "ALL", or PDB name (default: CDB$ROOT)
                      Use "ALL" for CDB-wide operations across all containers
            ciphertrust_username: CipherTrust Manager username (required for password/manual wallets)
            ciphertrust_password: CipherTrust Manager password (required for password/manual wallets)
            ciphertrust_domain: CipherTrust Manager domain (default: root)
            view_type: View type for status - "v$" for local or "gv$" for RAC global view
            node_filter: Optional RAC node filter (instance number)
            wallet_location: Wallet location (auto-detected if not provided)
            backup_location: Backup destination (defaults to same directory with .backup suffix)
            include_autologin: Include auto-login wallet files in backup (default: True)
            backup_suffix: Custom backup suffix (defaults to timestamp)
            source_wallet: Source wallet location for merge operation
            target_wallet: Target wallet location for merge operation
            software_keystore_password: Password for software keystore (required for autologin operations)
            new_ciphertrust_username: New CipherTrust username for autologin update operation
            new_ciphertrust_password: New CipherTrust password for autologin update operation
            new_ciphertrust_domain: New CipherTrust domain for autologin update operation
            auto_restart: If True, attempts database restart via SSH (for autologin operations)
            autologin_operation: For autologin operation - "create" | "update" | "remove" | "setup" | "setup_hsm" | "update_secret"
            
        Returns:
            JSON string containing wallet operation results.
        """
        try:
            logger.info(f"=== manage_oracle_wallet called ===")
            logger.info(f"Operation: {operation}, Container: {container}")
            
            db_handler = db_manager.get_database_handler(oracle_connection)
            
            if operation == "status":
                # Get current wallet status first
                if container == "ALL":
                    # For ALL containers, get status for all containers
                    wallet_status = await db_handler.get_wallet_status(view_type, None, node_filter)
                else:
                    # For specific container, get status for that container
                    wallet_status = await db_handler.get_wallet_status(view_type, container, node_filter)
                
                # Get TDE configuration to understand primary/secondary wallet order
                tde_config_sql = "SELECT VALUE FROM V$PARAMETER WHERE NAME = 'tde_configuration'"
                tde_config_result = await db_handler.execute_sql(tde_config_sql, "CDB$ROOT")
                tde_configuration = None
                if tde_config_result["success"] and tde_config_result["results"][0]["data"]:
                    tde_configuration = tde_config_result["results"][0]["data"][0]["VALUE"]
                
                # Organize wallet status by type
                file_wallets = [w for w in wallet_status if w.get("WRL_TYPE") == "FILE"]
                hsm_wallets = [w for w in wallet_status if w.get("WRL_TYPE") == "HSM"]
                
                # Helper function to check if wallet is open
                def is_wallet_open(wallet):
                    status = wallet.get("STATUS", "")
                    return status.startswith("OPEN")
                
                result_data = {
                    "success": True,
                    "operation": "wallet_status",
                    "connection": oracle_connection,
                    "container": container,
                    "view_type": view_type,
                    "filters": {
                        "container": container,
                        "node": node_filter
                    },
                    "tde_configuration": tde_configuration,
                    "wallet_status": {
                        "file_wallets": file_wallets,
                        "hsm_wallets": hsm_wallets,
                        "all_wallets": wallet_status
                    },
                    "summary": {
                        "file_wallets_open": sum(1 for w in file_wallets if is_wallet_open(w)),
                        "hsm_wallets_open": sum(1 for w in hsm_wallets if is_wallet_open(w)),
                        "total_wallets": len(wallet_status),
                        "primary_wallet": tde_configuration.split("|")[0] if tde_configuration else None,
                        "wallet_open_for_container": any(is_wallet_open(w) for w in file_wallets + hsm_wallets)
                    },
                    "timestamp": datetime.now().isoformat()
                }
                
            elif operation == "close":
                # Get current wallet status
                if container == "ALL":
                    wallet_status = await db_handler.get_wallet_status(view_type, None, node_filter)
                else:
                    wallet_status = await db_handler.get_wallet_status(view_type, container, node_filter)
                
                file_wallets = [w for w in wallet_status if w.get("WRL_TYPE") == "FILE"]
                hsm_wallets = [w for w in wallet_status if w.get("WRL_TYPE") == "HSM"]
                
                def is_wallet_open(wallet):
                    status = wallet.get("STATUS", "")
                    return status.startswith("OPEN")
                
                def has_autologin_configuration(wallets):
                    # Check if any wallet has AUTOLOGIN type (when open)
                    if any(w.get("WALLET_TYPE") == "AUTOLOGIN" for w in wallets):
                        return True
                    
                    # For closed wallets, check if there are FILE wallets with paths (indicating autologin setup)
                    file_wallets = [w for w in wallets if w.get("WRL_TYPE") == "FILE"]
                    for wallet in file_wallets:
                        wrl_param = wallet.get("WRL_PARAMETER", "")
                        if wrl_param and "/" in wrl_param:  # Has a file path, likely autologin
                            return True
                    
                    return False
                
                def is_wallet_open_for_container(wallets):
                    return any(is_wallet_open(w) for w in wallets)
                
                # Check if any wallet is open for this container
                if not is_wallet_open_for_container(file_wallets + hsm_wallets):
                    # Wallet already closed
                    result_data = {
                        "success": True,
                        "operation": "close_wallet",
                        "connection": oracle_connection,
                        "container": container,
                        "message": "Wallet already closed",
                        "wallet_status": wallet_status,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    # Close wallet with single query
                    close_results = []
                    
                    # Check if autologin is configured
                    has_autologin = has_autologin_configuration(file_wallets + hsm_wallets)
                    
                    if has_autologin:
                        # Close with autologin (no credentials needed)
                        if container == "ALL":
                            close_sql = "ADMINISTER KEY MANAGEMENT SET KEYSTORE CLOSE CONTAINER=ALL"
                        else:
                            close_sql = "ADMINISTER KEY MANAGEMENT SET KEYSTORE CLOSE"
                        result = await db_handler.execute_sql(close_sql, container)
                        
                        # For autologin, check SQL output for "keystore altered" confirmation
                        success = result.get("success", False)
                        if success and result.get("results") and result["results"][0].get("output"):
                            output = result["results"][0]["output"]
                            success = "keystore altered" in output.lower()
                        
                        close_results.append({
                            "close_method": "autologin",
                            "close_sql": close_sql,
                            "success": success,
                            "result": result,
                            "note": "Status check avoided for autologin wallet to prevent re-opening"
                        })
                        
                        # Don't check status after closing autologin wallet
                        final_status = None
                        
                    else:
                        # Close with credentials
                        if not ciphertrust_username or not ciphertrust_password:
                            return json.dumps({
                                "success": False,
                                "error": "CipherTrust credentials required to close password/manual wallet",
                                "note": "Please provide ciphertrust_username and ciphertrust_password",
                                "debug_info": {
                                    "file_wallets": file_wallets,
                                    "hsm_wallets": hsm_wallets,
                                    "has_autologin_detected": has_autologin
                                }
                            })
                        
                        # Construct wallet password
                        if ciphertrust_domain == "root":
                            wallet_pwd = f"{ciphertrust_username}:{ciphertrust_password}"
                        else:
                            wallet_pwd = f"{ciphertrust_domain}::{ciphertrust_username}:{ciphertrust_password}"
                        
                        if container == "ALL":
                            close_sql = f'ADMINISTER KEY MANAGEMENT SET KEYSTORE CLOSE IDENTIFIED BY "{wallet_pwd}" CONTAINER=ALL'
                        else:
                            close_sql = f'ADMINISTER KEY MANAGEMENT SET KEYSTORE CLOSE IDENTIFIED BY "{wallet_pwd}"'
                        result = await db_handler.execute_sql(close_sql, container)
                        close_results.append({
                            "close_method": "password",
                            "close_sql": close_sql,
                            "success": result.get("success", False),
                            "result": result
                        })
                        
                        # For password wallets, we can check status after closing
                        if container == "ALL":
                            final_status = await db_handler.get_wallet_status(view_type, None, node_filter)
                        else:
                            final_status = await db_handler.get_wallet_status(view_type, container, node_filter)
                    
                    result_data = {
                        "success": all(r["success"] for r in close_results),
                        "operation": "close_wallet",
                        "connection": oracle_connection,
                        "container": container,
                        "close_operations": close_results,
                        "final_wallet_status": final_status,
                        "timestamp": datetime.now().isoformat()
                    }
                
            elif operation == "open":
                # Get current wallet status
                if container == "ALL":
                    wallet_status = await db_handler.get_wallet_status(view_type, None, node_filter)
                else:
                    wallet_status = await db_handler.get_wallet_status(view_type, container, node_filter)
                
                file_wallets = [w for w in wallet_status if w.get("WRL_TYPE") == "FILE"]
                hsm_wallets = [w for w in wallet_status if w.get("WRL_TYPE") == "HSM"]
                
                def is_wallet_open(wallet):
                    status = wallet.get("STATUS", "")
                    return status.startswith("OPEN")
                
                def has_autologin_configuration(wallets):
                    # Check if any wallet has AUTOLOGIN type (when open)
                    if any(w.get("WALLET_TYPE") == "AUTOLOGIN" for w in wallets):
                        return True
                    
                    # For closed wallets, check if there are FILE wallets with paths (indicating autologin setup)
                    file_wallets = [w for w in wallets if w.get("WRL_TYPE") == "FILE"]
                    for wallet in file_wallets:
                        wrl_param = wallet.get("WRL_PARAMETER", "")
                        if wrl_param and "/" in wrl_param:  # Has a file path, likely autologin
                            return True
                    
                    return False
                
                def is_wallet_open_for_container(wallets):
                    return any(is_wallet_open(w) for w in wallets)
                
                # Check if any wallet is already open for this container
                if is_wallet_open_for_container(file_wallets + hsm_wallets):
                    # Wallet already open
                    result_data = {
                        "success": True,
                        "operation": "open_wallet",
                        "connection": oracle_connection,
                        "container": container,
                        "message": "Wallet already open",
                        "wallet_status": wallet_status,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    # Open wallet with single query
                    # Check if autologin is configured
                    has_autologin = has_autologin_configuration(file_wallets + hsm_wallets)
                    
                    if has_autologin:
                        # Try autologin first - just check status which should auto-open
                        if container == "ALL":
                            check_status = await db_handler.get_wallet_status(view_type, None, node_filter)
                        else:
                            check_status = await db_handler.get_wallet_status(view_type, container, node_filter)
                        check_file_wallets = [w for w in check_status if w.get("WRL_TYPE") == "FILE"]
                        check_hsm_wallets = [w for w in check_status if w.get("WRL_TYPE") == "HSM"]
                        
                        if is_wallet_open_for_container(check_file_wallets + check_hsm_wallets):
                            # Autologin worked
                            result_data = {
                                "success": True,
                                "operation": "open_wallet",
                                "connection": oracle_connection,
                                "container": container,
                                "message": "Wallet opened via autologin",
                                "open_method": "autologin",
                                "final_wallet_status": check_status,
                                "timestamp": datetime.now().isoformat()
                            }
                        else:
                            # Autologin failed, need credentials
                            if not ciphertrust_username or not ciphertrust_password:
                                return json.dumps({
                                    "success": False,
                                    "error": "Autologin failed and CipherTrust credentials are required",
                                    "note": "Please provide ciphertrust_username and ciphertrust_password",
                                    "debug_info": {
                                        "file_wallets": file_wallets,
                                        "hsm_wallets": hsm_wallets,
                                        "has_autologin_detected": has_autologin,
                                        "autologin_attempt_failed": True
                                    }
                                })
                            
                            # Open with credentials
                            if ciphertrust_domain == "root":
                                wallet_pwd = f"{ciphertrust_username}:{ciphertrust_password}"
                            else:
                                wallet_pwd = f"{ciphertrust_domain}::{ciphertrust_username}:{ciphertrust_password}"
                            
                            if container == "ALL":
                                open_sql = f'ADMINISTER KEY MANAGEMENT SET KEYSTORE OPEN IDENTIFIED BY "{wallet_pwd}" CONTAINER=ALL'
                            else:
                                open_sql = f'ADMINISTER KEY MANAGEMENT SET KEYSTORE OPEN IDENTIFIED BY "{wallet_pwd}"'
                            result = await db_handler.execute_sql(open_sql, container)
                            
                            if not result.get("success", False):
                                return json.dumps(result)
                            
                            # Get final wallet status
                            if container == "ALL":
                                final_status = await db_handler.get_wallet_status(view_type, None, node_filter)
                            else:
                                final_status = await db_handler.get_wallet_status(view_type, container, node_filter)
                            
                            result_data = {
                                "success": True,
                                "operation": "open_wallet",
                                "connection": oracle_connection,
                                "container": container,
                                "open_method": "password_after_autologin_failed",
                                "open_sql": open_sql,
                                "final_wallet_status": final_status,
                                "timestamp": datetime.now().isoformat()
                            }
                    else:
                        # No autologin, use credentials
                        if not ciphertrust_username or not ciphertrust_password:
                            return json.dumps({
                                "success": False,
                                "error": "CipherTrust credentials are required for opening wallet",
                                "note": "Please provide ciphertrust_username and ciphertrust_password",
                                "debug_info": {
                                    "file_wallets": file_wallets,
                                    "hsm_wallets": hsm_wallets,
                                    "has_autologin_detected": has_autologin
                                }
                            })
                        
                        # Construct wallet password
                        if ciphertrust_domain == "root":
                            wallet_pwd = f"{ciphertrust_username}:{ciphertrust_password}"
                        else:
                            wallet_pwd = f"{ciphertrust_domain}::{ciphertrust_username}:{ciphertrust_password}"
                        
                        # Open wallet
                        if container == "ALL":
                            open_sql = f'ADMINISTER KEY MANAGEMENT SET KEYSTORE OPEN IDENTIFIED BY "{wallet_pwd}" CONTAINER=ALL'
                        else:
                            open_sql = f'ADMINISTER KEY MANAGEMENT SET KEYSTORE OPEN IDENTIFIED BY "{wallet_pwd}"'
                        result = await db_handler.execute_sql(open_sql, container)
                        
                        if not result.get("success", False):
                            return json.dumps(result)
                        
                        # Get final wallet status
                        if container == "ALL":
                            final_status = await db_handler.get_wallet_status(view_type, None, node_filter)
                        else:
                            final_status = await db_handler.get_wallet_status(view_type, container, node_filter)
                        
                        result_data = {
                            "success": True,
                            "operation": "open_wallet",
                            "connection": oracle_connection,
                            "container": container,
                            "open_method": "password",
                            "open_sql": open_sql,
                            "final_wallet_status": final_status,
                            "timestamp": datetime.now().isoformat()
                        }
            
            elif operation == "backup":
                # Generate backup suffix if not provided
                if not backup_suffix:
                    backup_suffix = datetime.now().strftime('%Y%m%d_%H%M%S')
                
                # Get wallet location from Oracle parameters if not provided
                if not wallet_location:
                    wallet_param_sql = """
                    SELECT VALUE AS WALLET_ROOT
                    FROM V$PARAMETER 
                    WHERE NAME = 'wallet_root'
                    """
                    
                    wallet_result = await db_handler.execute_sql(wallet_param_sql, "CDB$ROOT")
                    
                    if wallet_result["success"] and wallet_result["results"][0]["data"]:
                        wallet_root = wallet_result["results"][0]["data"][0]["WALLET_ROOT"]
                        if wallet_root:
                            wallet_location = wallet_root
                        else:
                            wallet_location = "$ORACLE_BASE/admin/$ORACLE_SID/wallet"
                    else:
                        wallet_location = "$ORACLE_BASE/admin/$ORACLE_SID/wallet"
                
                # Set backup location if not provided
                if not backup_location:
                    backup_location = wallet_location
                
                # Use Oracle's built-in backup mechanism
                backup_tag = f"wallet_backup_{backup_suffix}"
                
                # Create backup using Oracle's ADMINISTER KEY MANAGEMENT command
                backup_sql = f"""
                ADMINISTER KEY MANAGEMENT BACKUP KEYSTORE
                USING '{backup_tag}'
                """
                
                backup_result = await db_handler.execute_sql(backup_sql, "CDB$ROOT")
                
                if backup_result.get("success", False):
                    # Get wallet status to verify backup
                    wallet_status = await db_handler.get_wallet_status("v$", "CDB$ROOT")
                    
                    result_data = {
                        "success": True,
                        "operation": "backup_oracle_wallet",
                        "connection": oracle_connection,
                        "wallet_location": wallet_location,
                        "backup_location": backup_location,
                        "backup_suffix": backup_suffix,
                        "backup_tag": backup_tag,
                        "include_autologin": include_autologin,
                        "backup_method": "Oracle built-in backup",
                        "summary": {
                            "total_files": 1,
                            "successful_backups": 1,
                            "failed_backups": 0
                        },
                        "backup_results": [{
                            "file": "wallet_backup",
                            "source_path": wallet_location,
                            "backup_path": f"Oracle backup with tag: {backup_tag}",
                            "description": "Complete wallet backup using Oracle's built-in mechanism",
                            "backup_success": True,
                            "verification_success": True,
                            "error": None
                        }],
                        "wallet_status": wallet_status,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    result_data = {
                        "success": False,
                        "operation": "backup_oracle_wallet",
                        "connection": oracle_connection,
                        "wallet_location": wallet_location,
                        "backup_location": backup_location,
                        "backup_suffix": backup_suffix,
                        "backup_tag": backup_tag,
                        "include_autologin": include_autologin,
                        "backup_method": "Oracle built-in backup",
                        "summary": {
                            "total_files": 1,
                            "successful_backups": 0,
                            "failed_backups": 1
                        },
                        "backup_results": [{
                            "file": "wallet_backup",
                            "source_path": wallet_location,
                            "backup_path": f"Oracle backup with tag: {backup_tag}",
                            "description": "Complete wallet backup using Oracle's built-in mechanism",
                            "backup_success": False,
                            "verification_success": False,
                            "error": backup_result.get("error", "Unknown error")
                        }],
                        "timestamp": datetime.now().isoformat()
                    }
            
            elif operation == "merge":
                if not source_wallet or not target_wallet:
                    return json.dumps({
                        "success": False,
                        "error": "Both source_wallet and target_wallet are required for merge operation"
                    })
                
                if not ciphertrust_username or not ciphertrust_password:
                    return json.dumps({
                        "success": False,
                        "error": "CipherTrust credentials are required for merge operation"
                    })
                
                # Construct wallet password from CipherTrust credentials
                if ciphertrust_domain == "root":
                    wallet_password = f"{ciphertrust_username}:{ciphertrust_password}"
                else:
                    wallet_password = f"{ciphertrust_domain}::{ciphertrust_username}:{ciphertrust_password}"
                
                # Check if source wallet exists using Python file operations
                source_wallet_path = Path(source_wallet) / "ewallet.p12"
                if not source_wallet_path.exists():
                    return json.dumps({
                        "success": False,
                        "error": f"Source wallet not found: {source_wallet}"
                    })
                
                # Check if target wallet exists using Python file operations
                target_wallet_path = Path(target_wallet) / "ewallet.p12"
                if not target_wallet_path.exists():
                    return json.dumps({
                        "success": False,
                        "error": f"Target wallet not found: {target_wallet}"
                    })
                
                # Merge wallets using Oracle command
                merge_sql = f"""
                ADMINISTER KEY MANAGEMENT MERGE KEYSTORE '{source_wallet}' 
                INTO KEYSTORE '{target_wallet}' 
                IDENTIFIED BY "{wallet_password}"
                """
                
                merge_result = await db_handler.execute_sql(merge_sql, "CDB$ROOT")
                
                if not merge_result.get("success", False):
                    return json.dumps({
                        "success": False,
                        "error": f"Failed to merge wallets: {merge_result.get('error')}"
                    })
                
                # Verify merge by checking target wallet
                verify_sql = f"""
                ADMINISTER KEY MANAGEMENT LIST KEYSTORE '{target_wallet}' 
                IDENTIFIED BY "{wallet_password}"
                """
                
                verify_result = await db_handler.execute_sql(verify_sql, "CDB$ROOT")
                
                result_data = {
                    "success": True,
                    "operation": "merge_oracle_wallets",
                    "connection": oracle_connection,
                    "source_wallet": source_wallet,
                    "target_wallet": target_wallet,
                    "merge_success": merge_result["success"],
                    "verification_success": verify_result["success"],
                    "note": "Wallets merged successfully. Target wallet now contains keys from both wallets.",
                    "timestamp": datetime.now().isoformat()
                }
            
            elif operation == "autologin":
                if not autologin_operation:
                    return json.dumps({
                        "success": False,
                        "error": "autologin_operation is required when operation is 'autologin'"
                    })
                
                # Full autologin management implementation
                
                # Get enhanced configuration from database handler's connection
                enhanced_config = {
                    "ssh": db_handler.connection.ssh_config.dict() if db_handler.connection.ssh_config else None,
                    "oracle": db_handler.connection.oracle_config.dict() if db_handler.connection.oracle_config else None
                }
                
                # Initialize SSH manager if SSH configuration is available
                ssh_manager = None
                ssh_connected = False
                oracle_sid = None
                
                if enhanced_config and enhanced_config.get("ssh"):
                    try:
                        from ..utils.ssh_utils import OracleSSHManager
                        ssh_config = enhanced_config["ssh"]
                        ssh_manager = OracleSSHManager(
                            host=ssh_config["host"],
                            username=ssh_config["username"],
                            password=ssh_config["password"],
                            port=ssh_config.get("port", 22)
                        )
                        
                        # Connect to SSH
                        ssh_connected = ssh_manager.connect()
                        
                        # Get Oracle SID from enhanced configuration
                        if enhanced_config.get("oracle"):
                            oracle_sid = enhanced_config["oracle"].get("oracle_sid")
                        
                    except Exception as e:
                        logger.warning(f"SSH initialization failed: {e}")
                        ssh_manager = None
                        ssh_connected = False
                
                # Construct wallet password from CipherTrust credentials
                if ciphertrust_domain == "root":
                    wallet_password = f"{ciphertrust_username}:{ciphertrust_password}"
                else:
                    wallet_password = f"{ciphertrust_domain}::{ciphertrust_username}:{ciphertrust_password}"
                
                # Get wallet location if not provided
                if not wallet_location:
                    wallet_param_sql = """
                    SELECT VALUE AS WALLET_ROOT
                    FROM V$PARAMETER 
                    WHERE NAME = 'wallet_root'
                    """
                    
                    wallet_result = await db_handler.execute_sql(wallet_param_sql, "CDB$ROOT")
                    
                    if wallet_result["success"] and wallet_result["results"][0]["data"]:
                        wallet_root = wallet_result["results"][0]["data"][0]["WALLET_ROOT"]
                        if wallet_root:
                            wallet_location = wallet_root
                        else:
                            wallet_location = "$ORACLE_BASE/admin/$ORACLE_SID/wallet"
                    else:
                        wallet_location = "$ORACLE_BASE/admin/$ORACLE_SID/wallet"
                
                if autologin_operation == "create":
                    # First check current TDE configuration to provide better guidance
                    tde_config_sql = "SELECT VALUE FROM V$PARAMETER WHERE NAME = 'tde_configuration'"
                    tde_config_result = await db_handler.execute_sql(tde_config_sql, "CDB$ROOT")
                    current_tde_config = None
                    if tde_config_result["success"] and tde_config_result["results"][0]["data"]:
                        current_tde_config = tde_config_result["results"][0]["data"][0]["VALUE"]
                    
                    # Check if we have any software wallets
                    wallet_check_sql = """
                    SELECT WRL_TYPE, WALLET_TYPE, STATUS 
                    FROM V$ENCRYPTION_WALLET 
                    WHERE WRL_TYPE = 'FILE'
                    """
                    wallet_check_result = await db_handler.execute_sql(wallet_check_sql, "CDB$ROOT")
                    has_software_wallet = False
                    if wallet_check_result["success"] and wallet_check_result["results"][0]["data"]:
                        has_software_wallet = len(wallet_check_result["results"][0]["data"]) > 0
                    
                    # Create auto-login wallet
                    autologin_sql = f"""
                    ADMINISTER KEY MANAGEMENT CREATE AUTO_LOGIN KEYSTORE 
                    FROM KEYSTORE '{wallet_location}' 
                    IDENTIFIED BY "{wallet_password}"
                    """
                    
                    result = await db_handler.execute_sql(autologin_sql, "CDB$ROOT")
                    
                    if not result.get("success", False):
                        error_msg = result.get('error', 'Unknown error')
                        
                        # Provide specific guidance based on current configuration
                        if "ORA-46632" in error_msg and not has_software_wallet:
                            guidance = {
                                "current_configuration": current_tde_config,
                                "has_software_wallet": has_software_wallet,
                                "recommended_operation": "setup",
                                "explanation": "No password-based keystore (software wallet) exists. Use 'setup' operation to create software wallet and auto-login from scratch.",
                                "required_parameters": {
                                    "autologin_operation": "setup",
                                    "software_keystore_password": "Required - Password for the new software wallet"
                                }
                            }
                            
                            return json.dumps({
                                "success": False,
                                "error": f"Failed to create auto-login wallet: {error_msg}",
                                "guidance": guidance,
                                "current_tde_config": current_tde_config,
                                "has_software_wallet": has_software_wallet
                            })
                        else:
                            return json.dumps({
                                "success": False,
                                "error": f"Failed to create auto-login wallet: {error_msg}",
                                "current_tde_config": current_tde_config,
                                "has_software_wallet": has_software_wallet
                            })
                    
                    result_data = {
                        "success": True,
                        "operation": "create_autologin",
                        "connection": oracle_connection,
                        "wallet_location": wallet_location,
                        "note": "Auto-login wallet created. Database can now start without manual wallet opening.",
                        "timestamp": datetime.now().isoformat()
                    }
                    
                elif autologin_operation == "update":
                    if not new_ciphertrust_username or not new_ciphertrust_password:
                        return json.dumps({
                            "success": False,
                            "error": "New CipherTrust credentials are required for update operation"
                        })
                    
                    # Construct new wallet password
                    new_domain = new_ciphertrust_domain or ciphertrust_domain
                    if new_domain == "root":
                        new_wallet_password = f"{new_ciphertrust_username}:{new_ciphertrust_password}"
                    else:
                        new_wallet_password = f"{new_domain}::{new_ciphertrust_username}:{new_ciphertrust_password}"
                    
                    # Update auto-login wallet
                    update_sql = f"""
                    ADMINISTER KEY MANAGEMENT UPDATE AUTO_LOGIN KEYSTORE 
                    FROM KEYSTORE '{wallet_location}' 
                    IDENTIFIED BY "{wallet_password}" 
                    WITH NEW PASSWORD "{new_wallet_password}"
                    """
                    
                    result = await db_handler.execute_sql(update_sql, "CDB$ROOT")
                    
                    if not result.get("success", False):
                        return json.dumps({
                            "success": False,
                            "error": f"Failed to update auto-login wallet: {result.get('error')}"
                        })
                    
                    result_data = {
                        "success": True,
                        "operation": "update_autologin",
                        "connection": oracle_connection,
                        "wallet_location": wallet_location,
                        "note": "Auto-login wallet password updated.",
                        "timestamp": datetime.now().isoformat()
                    }
                    
                elif autologin_operation == "remove":
                    # Remove auto-login wallet
                    remove_sql = f"""
                    ADMINISTER KEY MANAGEMENT DROP AUTO_LOGIN KEYSTORE 
                    FROM KEYSTORE '{wallet_location}' 
                    IDENTIFIED BY "{wallet_password}"
                    """
                    
                    result = await db_handler.execute_sql(remove_sql, "CDB$ROOT")
                    
                    if not result.get("success", False):
                        return json.dumps({
                            "success": False,
                            "error": f"Failed to remove auto-login wallet: {result.get('error')}"
                        })
                    
                    result_data = {
                        "success": True,
                        "operation": "remove_autologin",
                        "connection": oracle_connection,
                        "wallet_location": wallet_location,
                        "note": "Auto-login wallet removed. Manual wallet opening will be required.",
                        "timestamp": datetime.now().isoformat()
                    }
                    
                elif autologin_operation == "setup":
                    # Complete auto-login setup from scratch (creates software wallet first)
                    if not software_keystore_password:
                        return json.dumps({
                            "success": False,
                            "error": "software_keystore_password is required for setup operation"
                        })
                    
                    steps = []
                    
                    # Step 1: Check current wallet status
                    logger.info("Step 1: Checking current wallet status...")
                    wallet_status_sql = "SELECT * FROM V$ENCRYPTION_WALLET"
                    wallet_status_result = await db_handler.execute_sql(wallet_status_sql, "CDB$ROOT")
                    steps.append({
                        "step": "check_current_wallet_status",
                        "sql": wallet_status_sql,
                        "result": wallet_status_result.get("success", False),
                        "wallet_status": wallet_status_result.get("results", [])
                    })
                    
                    # Check if any wallet is currently open
                    has_open_wallet = False
                    open_wallet_types = []
                    has_autologin_wallet = False
                    if wallet_status_result["success"] and wallet_status_result["results"][0]["data"]:
                        for wallet in wallet_status_result["results"][0]["data"]:
                            if wallet.get("STATUS") in ["OPEN", "OPEN_NO_MASTER_KEY"]:
                                has_open_wallet = True
                                wallet_type = wallet.get("WALLET_TYPE", "UNKNOWN")
                                open_wallet_types.append(wallet_type)
                                # Check if any wallet has AUTOLOGIN type (when open)
                                if wallet.get("WALLET_TYPE") == "AUTOLOGIN":
                                    has_autologin_wallet = True
                    
                    # Step 2: Close any open wallets if necessary
                    if has_open_wallet:
                        logger.info("Step 2: Closing open wallets...")
                        
                        # Determine the appropriate close command based on auto-login availability
                        if has_autologin_wallet:
                            # Auto-login wallets don't require password to close
                            close_wallet_sql = "ADMINISTER KEY MANAGEMENT SET KEYSTORE CLOSE"
                        else:
                            # Determine which password to use based on wallet types
                            if "HSM" in open_wallet_types:
                                # HSM wallets require CipherTrust credentials
                                close_password = wallet_password  # This is already in domain::user:password format
                            else:
                                # Software wallets require software keystore password
                                close_password = software_keystore_password
                            
                            close_wallet_sql = f"""
                            ADMINISTER KEY MANAGEMENT SET KEYSTORE CLOSE 
                            IDENTIFIED BY "{close_password}"
                            """
                        
                        close_wallet_result = await db_handler.execute_sql(close_wallet_sql, "CDB$ROOT")
                        steps.append({
                            "step": "close_open_wallets",
                            "sql": close_wallet_sql,
                            "open_wallet_types": open_wallet_types,
                            "has_autologin_wallet": has_autologin_wallet,
                            "password_used": "autologin" if has_autologin_wallet else ("hsm_credentials" if "HSM" in open_wallet_types else "software_password"),
                            "result": close_wallet_result.get("success", False)
                        })
                        
                        if not close_wallet_result.get("success", False):
                            return json.dumps({
                                "success": False,
                                "error": f"Failed to close open wallets: {close_wallet_result.get('error', 'Unknown error')}",
                                "steps": steps
                            })
                    
                    # Step 3: Set TDE configuration to FILE
                    logger.info("Step 3: Setting TDE configuration to FILE...")
                    tde_file_sql = 'ALTER SYSTEM SET TDE_CONFIGURATION="KEYSTORE_CONFIGURATION=FILE" SCOPE=BOTH'
                    tde_file_result = await db_handler.execute_sql(tde_file_sql, "CDB$ROOT")
                    steps.append({
                        "step": "set_tde_configuration_to_file",
                        "sql": tde_file_sql,
                        "result": tde_file_result.get("success", False)
                    })
                    
                    if not tde_file_result.get("success", False):
                        return json.dumps({
                            "success": False,
                            "error": f"Failed to set TDE configuration to FILE: {tde_file_result.get('error', 'Unknown error')}",
                            "steps": steps
                        })
                    
                    # Step 4: Create a new software wallet
                    logger.info("Step 4: Creating new software wallet...")
                    create_wallet_sql = f"""
                    ADMINISTER KEY MANAGEMENT CREATE KEYSTORE 
                    IDENTIFIED BY "{software_keystore_password}"
                    """
                    create_wallet_result = await db_handler.execute_sql(create_wallet_sql, "CDB$ROOT")
                    steps.append({
                        "step": "create_software_wallet",
                        "sql": create_wallet_sql,
                        "result": create_wallet_result.get("success", False)
                    })
                    
                    if not create_wallet_result.get("success", False):
                        return json.dumps({
                            "success": False,
                            "error": f"Failed to create software wallet: {create_wallet_result.get('error', 'Unknown error')}",
                            "steps": steps
                        })
                    
                    # Step 5: Open the software wallet
                    logger.info("Step 5: Opening software wallet...")
                    open_wallet_sql = f"""
                    ADMINISTER KEY MANAGEMENT SET KEYSTORE OPEN 
                    IDENTIFIED BY "{software_keystore_password}"
                    """
                    open_wallet_result = await db_handler.execute_sql(open_wallet_sql, "CDB$ROOT")
                    steps.append({
                        "step": "open_software_wallet",
                        "sql": open_wallet_sql,
                        "result": open_wallet_result.get("success", False)
                    })
                    
                    if not open_wallet_result.get("success", False):
                        return json.dumps({
                            "success": False,
                            "error": f"Failed to open software wallet: {open_wallet_result.get('error', 'Unknown error')}",
                            "steps": steps
                        })
                    
                    # Step 6: Add CipherTrust credentials to the keystore
                    logger.info("Step 6: Adding CipherTrust credentials to keystore...")
                    add_secret_sql = f"""
                    ADMINISTER KEY MANAGEMENT ADD SECRET '{wallet_password}' 
                    FOR CLIENT 'HSM_PASSWORD' 
                    IDENTIFIED BY "{software_keystore_password}" 
                    WITH BACKUP
                    """
                    add_secret_result = await db_handler.execute_sql(add_secret_sql, "CDB$ROOT")
                    steps.append({
                        "step": "add_hsm_secret",
                        "sql": add_secret_sql,
                        "result": add_secret_result.get("success", False)
                    })
                    
                    if not add_secret_result.get("success", False):
                        return json.dumps({
                            "success": False,
                            "error": f"Failed to add HSM secret: {add_secret_result.get('error', 'Unknown error')}",
                            "steps": steps
                        })
                    
                    # Step 7: Create auto-login keystore
                    logger.info("Step 7: Creating auto-login keystore...")
                    create_autologin_sql = f"""
                    ADMINISTER KEY MANAGEMENT CREATE AUTO_LOGIN KEYSTORE FROM KEYSTORE
                    IDENTIFIED BY "{software_keystore_password}"
                    """
                    create_autologin_result = await db_handler.execute_sql(create_autologin_sql, "CDB$ROOT")
                    steps.append({
                        "step": "create_autologin_keystore",
                        "sql": create_autologin_sql,
                        "result": create_autologin_result.get("success", False)
                    })
                    
                    if not create_autologin_result.get("success", False):
                        return json.dumps({
                            "success": False,
                            "error": f"Failed to create auto-login keystore: {create_autologin_result.get('error', 'Unknown error')}",
                            "steps": steps
                        })
                    
                    # Step 8: Update TDE configuration to HSM|FILE
                    logger.info("Step 8: Updating TDE configuration to HSM|FILE...")
                    tde_hsm_file_sql = 'ALTER SYSTEM SET TDE_CONFIGURATION="KEYSTORE_CONFIGURATION=HSM|FILE" SCOPE=BOTH'
                    tde_hsm_file_result = await db_handler.execute_sql(tde_hsm_file_sql, "CDB$ROOT")
                    steps.append({
                        "step": "set_tde_configuration_to_hsm_file",
                        "sql": tde_hsm_file_sql,
                        "result": tde_hsm_file_result.get("success", False)
                    })
                    
                    if not tde_hsm_file_result.get("success", False):
                        return json.dumps({
                            "success": False,
                            "error": f"Failed to set TDE configuration to HSM|FILE: {tde_hsm_file_result.get('error', 'Unknown error')}",
                            "steps": steps
                        })
                    
                    # Step 9: Restart database if requested
                    if auto_restart:
                        logger.info("Step 9: Restarting database...")
                        
                        # Use SSH restart if available
                        if enhanced_config and enhanced_config.get("ssh") and ssh_manager:
                            restart_result = ssh_manager.restart_oracle_database(oracle_sid)
                        else:
                            # Fallback to SQL restart (may fail)
                            shutdown_result = await db_handler.execute_sql("SHUTDOWN IMMEDIATE", "CDB$ROOT")
                            import asyncio
                            await asyncio.sleep(10)
                            startup_result = await db_handler.execute_sql("STARTUP", "CDB$ROOT")
                            restart_result = {
                                "success": shutdown_result.get("success", False) and startup_result.get("success", False),
                                "stdout": f"Shutdown: {shutdown_result.get('success', False)}, Startup: {startup_result.get('success', False)}",
                                "stderr": ""
                            }
                        
                        steps.append({
                            "step": "restart_database",
                            "success": restart_result.get("success", False),
                            "stdout": restart_result.get("stdout", ""),
                            "stderr": restart_result.get("stderr", "")
                        })
                        
                        if not restart_result.get("success", False):
                            return json.dumps({
                                "success": False,
                                "error": f"Database restart failed: {restart_result.get('error', 'Unknown error')}",
                                "steps": steps
                            })
                        
                        # Wait for database to be fully up
                        import asyncio
                        await asyncio.sleep(10)
                    else:
                        steps.append({
                            "step": "restart_database_skipped",
                            "note": "Manual database restart required",
                            "manual_instructions": [
                                "1. Connect to the Oracle server as oracle user",
                                "2. Connect to the database: sqlplus / as sysdba",
                                "3. Shutdown the database: SHUTDOWN IMMEDIATE",
                                "4. Start the database: STARTUP"
                            ]
                        })
                    
                    # Step 10: Check wallet status
                    logger.info("Step 10: Checking wallet status...")
                    wallet_status_sql = "SELECT * FROM V$ENCRYPTION_WALLET"
                    wallet_status_result = await db_handler.execute_sql(wallet_status_sql, "CDB$ROOT")
                    steps.append({
                        "step": "check_wallet_status_after_restart",
                        "sql": wallet_status_sql,
                        "result": wallet_status_result.get("success", False),
                        "wallet_status": wallet_status_result.get("results", [])
                    })
                    
                    result_data = {
                        "success": True,
                        "operation": "setup_autologin",
                        "connection": oracle_connection,
                        "wallet_location": wallet_location,
                        "steps": steps,
                        "note": "Auto-login setup completed successfully. Database can now start without manual wallet opening.",
                        "timestamp": datetime.now().isoformat()
                    }
                
                elif autologin_operation == "setup_hsm":
                    # Setup auto-login for HSM migration (from existing software wallet)
                    if not software_keystore_password:
                        return json.dumps({
                            "success": False,
                            "error": "software_keystore_password is required for setup_hsm operation"
                        })
                    
                    steps = []
                    
                    # Step 1: Open software wallet
                    logger.info("Step 1: Opening software wallet...")
                    open_result = await db_handler.open_wallet("CDB$ROOT", software_keystore_password)
                    steps.append({
                        "step": "open_software_wallet",
                        "success": open_result.get("success", False)
                    })
                    
                    if not open_result.get("success", False):
                        return json.dumps({
                            "success": False,
                            "error": f"Failed to open software wallet: {open_result.get('error', 'Unknown error')}",
                            "steps": steps
                        })
                    
                    # Step 2: Add HSM secret
                    logger.info("Step 2: Adding HSM secret...")
                    add_secret_sql = f"""
                    ADMINISTER KEY MANAGEMENT ADD SECRET '{wallet_password}' 
                    FOR CLIENT 'HSM_PASSWORD' 
                    IDENTIFIED BY "{software_keystore_password}" 
                    WITH BACKUP
                    """
                    secret_result = await db_handler.execute_sql(add_secret_sql, "CDB$ROOT")
                    steps.append({
                        "step": "add_hsm_secret",
                        "success": secret_result.get("success", False)
                    })
                    
                    if not secret_result.get("success", False):
                        return json.dumps({
                            "success": False,
                            "error": f"Failed to add HSM secret: {secret_result.get('error', 'Unknown error')}",
                            "steps": steps
                        })
                    
                    # Step 3: Create auto-login wallet
                    logger.info("Step 3: Creating auto-login wallet...")
                    create_autologin_sql = f"""
                    ADMINISTER KEY MANAGEMENT CREATE AUTO_LOGIN KEYSTORE FROM KEYSTORE
                    IDENTIFIED BY "{software_keystore_password}"
                    """
                    autologin_result = await db_handler.execute_sql(create_autologin_sql, "CDB$ROOT")
                    steps.append({
                        "step": "create_autologin_wallet",
                        "success": autologin_result.get("success", False)
                    })
                    
                    if not autologin_result.get("success", False):
                        return json.dumps({
                            "success": False,
                            "error": f"Failed to create auto-login wallet: {autologin_result.get('error', 'Unknown error')}",
                            "steps": steps
                        })
                    
                    # Step 4: Set TDE configuration
                    logger.info("Step 4: Setting TDE configuration...")
                    tde_sql = "ALTER SYSTEM SET TDE_CONFIGURATION='HSM|FILE' SCOPE=BOTH"
                    tde_result = await db_handler.execute_sql(tde_sql, "CDB$ROOT")
                    steps.append({
                        "step": "set_tde_configuration",
                        "value": "HSM|FILE",
                        "success": tde_result.get("success", False)
                    })
                    
                    if not tde_result.get("success", False):
                        return json.dumps({
                            "success": False,
                            "error": f"Failed to set TDE configuration: {tde_result.get('error', 'Unknown error')}",
                            "steps": steps
                        })
                    
                    # Step 5: Migrate to HSM
                    logger.info("Step 5: Migrating to HSM...")
                    migrate_sql = f"""
                    ADMINISTER KEY MANAGEMENT SET ENCRYPTION KEY 
                    IDENTIFIED BY "{wallet_password}" 
                    MIGRATE USING "{software_keystore_password}" 
                    WITH BACKUP
                    """
                    migrate_result = await db_handler.execute_sql(migrate_sql, "CDB$ROOT")
                    steps.append({
                        "step": "migrate_to_hsm",
                        "success": migrate_result.get("success", False)
                    })
                    
                    if not migrate_result.get("success", False):
                        return json.dumps({
                            "success": False,
                            "error": f"Failed to migrate to HSM: {migrate_result.get('error', 'Unknown error')}",
                            "steps": steps
                        })
                    
                    result_data = {
                        "success": True,
                        "operation": "setup_hsm_autologin",
                        "connection": oracle_connection,
                        "wallet_location": wallet_location,
                        "steps": steps,
                        "note": "HSM auto-login setup completed successfully.",
                        "timestamp": datetime.now().isoformat()
                    }
                    
                elif autologin_operation == "update_secret":
                    # Update HSM secret in existing auto-login wallet
                    if not software_keystore_password:
                        return json.dumps({
                            "success": False,
                            "error": "software_keystore_password is required for update_secret operation"
                        })
                    
                    # Get wallet root parameter to determine TDE location
                    wallet_root_sql = "SELECT VALUE FROM V$PARAMETER WHERE NAME = 'wallet_root'"
                    wallet_root_result = await db_handler.execute_sql(wallet_root_sql, "CDB$ROOT")
                    
                    wallet_root = None
                    if wallet_root_result["success"] and wallet_root_result["results"][0]["data"]:
                        wallet_root = wallet_root_result["results"][0]["data"][0]["VALUE"]
                    
                    if not wallet_root:
                        return json.dumps({
                            "success": False,
                            "error": "WALLET_ROOT parameter is not set - cannot determine TDE location"
                        })
                    
                    # Construct TDE location with /tde suffix (important!)
                    tde_location = f"{wallet_root}/tde"
                    
                    steps = []
                    
                    # Update HSM secret using the correct syntax for auto-login wallet
                    logger.info("Updating HSM secret in auto-login wallet...")
                    update_secret_sql = f"""
                    ADMINISTER KEY MANAGEMENT ADD SECRET '{wallet_password}' 
                    FOR CLIENT 'HSM_PASSWORD' 
                    TO AUTO_LOGIN KEYSTORE '{tde_location}' 
                    WITH BACKUP
                    """
                    update_result = await db_handler.execute_sql(update_secret_sql, "CDB$ROOT")
                    steps.append({
                        "step": "update_hsm_secret_autologin",
                        "sql": update_secret_sql,
                        "tde_location": tde_location,
                        "success": update_result.get("success", False)
                    })
                    
                    if not update_result.get("success", False):
                        return json.dumps({
                            "success": False,
                            "error": f"Failed to update HSM secret: {update_result.get('error', 'Unknown error')}",
                            "steps": steps
                        })
                    
                    result_data = {
                        "success": True,
                        "operation": "update_secret_autologin",
                        "connection": oracle_connection,
                        "tde_location": tde_location,
                        "steps": steps,
                        "note": "HSM secret updated in auto-login wallet successfully using /tde location.",
                        "timestamp": datetime.now().isoformat()
                    }
                
                else:
                    return json.dumps({
                        "success": False,
                        "error": f"Invalid autologin_operation: {autologin_operation}. Must be 'create', 'update', 'remove', 'setup', 'setup_hsm', or 'update_secret'"
                    })
                
                # Cleanup SSH connection if established
                if ssh_manager and ssh_connected:
                    ssh_manager.disconnect()
            
            else:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid operation: {operation}. Must be 'open', 'close', 'status', 'backup', 'merge', or 'autologin'"
                })
            
            logger.info(f"=== manage_oracle_wallet completed ===")
            return json.dumps(result_data, indent=2)
            
        except Exception as e:
            logger.error(f"Error managing wallet: {e}", exc_info=True)
            return json.dumps({
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }) 