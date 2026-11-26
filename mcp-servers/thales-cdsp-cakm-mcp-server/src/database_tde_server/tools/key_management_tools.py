"""
Database TDE key management tools

This module provides tools for managing encryption keys for Transparent Data Encryption (TDE) operations.
Database encryption and encryption key management are handled by Thales CipherTrust Application Key Management (CAKM)
connector, which is integrated with Thales CDSP (CipherTrust Data Security Platform).

Available tools:
- manage_sql_keys: Manage SQL Server cryptographic keys (create, list, drop, rotate)
  - Operations: create, list, drop, drop_unused, rotate_master, rotate_dek
  - Creates asymmetric keys in EKM providers
  - Manages key lifecycle and rotation
  - Handles key cleanup and validation
- manage_oracle_keys: Manage Oracle Master Encryption Keys (generate, rotate, list)
  - Operations: generate, rotate, list
  - Generates Master Encryption Keys (MEK) for Oracle
  - Rotates existing keys with backup creation
  - Lists key information and status
"""

import json
import logging
from typing import Optional
from datetime import datetime

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

def register_key_management_tools(server: FastMCP, db_manager):
    """Register unified key management tools with the MCP server"""
    
    # ============================================================================
    # SQL SERVER KEY MANAGEMENT TOOLS
    # ============================================================================
    
    @server.tool()
    async def manage_sql_keys(
        sql_connection: str,
        operation: str,
        key_name: Optional[str] = None,
        key_type: Optional[str] = None,
        force: bool = False,
        remove_from_provider: bool = False,
        provider_name: Optional[str] = None,
        key_size: Optional[str] = None,
        database_name: Optional[str] = None,
        new_key_name: Optional[str] = None,
        ciphertrust_username: Optional[str] = None,
        ciphertrust_password: Optional[str] = None,
        ciphertrust_domain: str = "root"
    ) -> str:
        """
        Manage the lifecycle of SQL Server cryptographic keys used for TDE.

        This tool handles Asymmetric keys (Master Keys) stored in an EKM provider
        and the Database Encryption Keys (DEKs) that they protect.

        ---
        **Operations:**
        - `create`: Creates a new Asymmetric Key in the EKM and registers it in SQL Server.
        - `list`: Lists all Asymmetric and Symmetric keys, indicating if they are in use.
        - `drop`: Drops a key from SQL Server. Can optionally remove it from the EKM.
        - `drop_unused`: Drops all keys that are not actively encrypting a database.
        - `rotate_master`: Rotates the Asymmetric Key for a specific database.
        - `rotate_dek`: Rotates the Database Encryption Key for a specific database.
        ---

        Args:
            sql_connection: The name of the database connection to use.
            operation: The action to perform (see list above).
            key_name: (For create, drop, rotate_master) The name of the Asymmetric Key.
            key_type: (For create, drop) The key type: "RSA" or "AES". Defaults to "RSA".
            force: (For drop) If true, drops a key even if it's in use.
            remove_from_provider: (For drop) If true, also removes the key from the EKM.
            provider_name: (For create, rotate_master) The name of the EKM cryptographic provider.
            key_size: (For create, rotate_master) Key size in bits (e.g., "2048"). Defaults to 2048 for RSA.
            database_name: (For rotate_dek, rotate_master) The database to perform the rotation on.
            new_key_name: (For rotate_master) The name of the new Asymmetric Key to create.
            ciphertrust_username: (For rotate_master) The CipherTrust Manager username.
            ciphertrust_password: (For rotate_master) The CipherTrust Manager password.
            ciphertrust_domain: (For rotate_master) The CipherTrust Manager domain.

        Returns:
            A JSON string with the results of the key management operation.
        """
        try:
            logger.info(f"=== manage_sql_keys called with operation: {operation} ===")
            db_handler = db_manager.get_database_handler(sql_connection)

            if operation == "create":
                if not provider_name or not key_name:
                    return json.dumps({"success": False, "error": "provider_name and key_name are required for create"})
                
                final_key_size = None
                if key_size is None:
                    key_type = key_type or "RSA"
                    final_key_size = 2048 if key_type.upper() == "RSA" else 256
                else:
                    try:
                        final_key_size = int(key_size)
                    except (ValueError, TypeError):
                        return json.dumps({"success": False, "error": f"Invalid key_size '{key_size}'. Must be a valid integer."})

                # Check if key already exists
                existing_keys = await db_handler.list_master_keys(key_type)
                is_asymmetric = key_type.upper() == "RSA"
                key_list = existing_keys.get("asymmetric_keys" if is_asymmetric else "symmetric_keys", [])
                
                if any(k["name"] == key_name for k in key_list):
                    return json.dumps({
                        "success": False, "error": f"Key '{key_name}' already exists",
                        "existing_key": next(k for k in key_list if k["name"] == key_name)
                    })
                
                create_result = await db_handler.create_master_key(key_name, provider_name, key_name, final_key_size)
                if not create_result.get("success", False): return json.dumps(create_result)
                
                updated_keys = await db_handler.list_master_keys(key_type)
                updated_key_list = updated_keys.get("asymmetric_keys" if is_asymmetric else "symmetric_keys", [])
                new_key = next((k for k in updated_key_list if k["name"] == key_name), None)
                
                return json.dumps({
                    "success": True, "operation": "create_sql_master_key", "key_name": key_name,
                    "key_type": key_type, "key_size": final_key_size, "provider_name": provider_name,
                    "algorithm": create_result.get("algorithm"), "steps": create_result.get("steps", []),
                    "new_key_info": new_key, "timestamp": datetime.now().isoformat()
                }, indent=2)

            elif operation == "list":
                # List master keys
                keys = await db_handler.list_master_keys(key_type)
                
                # Get key usage information
                key_usage_sql = """
                SELECT DISTINCT COALESCE(ak.name, sk.name) as key_name
                FROM sys.dm_database_encryption_keys dek
                LEFT JOIN master.sys.asymmetric_keys ak ON dek.encryptor_thumbprint = ak.thumbprint
                LEFT JOIN master.sys.symmetric_keys sk ON dek.encryptor_thumbprint = sk.key_guid
                WHERE COALESCE(ak.name, sk.name) IS NOT NULL
                """
                usage_result = await db_handler.execute_sql(key_usage_sql)
                used_keys = {row["key_name"] for row in usage_result["results"][0]["data"]} if usage_result["success"] and usage_result["results"][0]["data"] else set()
                
                for key_list_name in ["asymmetric_keys", "symmetric_keys"]:
                    for key in keys.get(key_list_name, []):
                        key["is_used"] = key["name"] in used_keys
                
                return json.dumps({
                    "success": True, "operation": "list_sql_master_keys", "connection": sql_connection,
                    "key_type_filter": key_type, "keys": keys,
                    "summary": {
                        "total_asymmetric_keys": len(keys.get("asymmetric_keys", [])),
                        "total_symmetric_keys": len(keys.get("symmetric_keys", [])),
                        "used_keys": len(used_keys),
                        "unused_keys": len(keys.get("asymmetric_keys", []) + keys.get("symmetric_keys", [])) - len(used_keys)
                    }, "timestamp": datetime.now().isoformat()
                }, indent=2)
                
            elif operation == "drop":
                if not key_name or not key_type:
                    return json.dumps({"success": False, "error": "key_name and key_type are required for drop"})
                
                # Check if key exists
                keys = await db_handler.list_master_keys(key_type)
                is_asymmetric = key_type.upper() == "RSA"
                key_list = keys.get("asymmetric_keys" if is_asymmetric else "symmetric_keys", [])
                if not any(k["name"] == key_name for k in key_list):
                    return json.dumps({"success": False, "error": f"Key '{key_name}' not found"})

                # Check if key is in use
                key_usage_sql = "SELECT DISTINCT COALESCE(ak.name, sk.name) as key_name FROM sys.dm_database_encryption_keys dek LEFT JOIN master.sys.asymmetric_keys ak ON dek.encryptor_thumbprint = ak.thumbprint LEFT JOIN master.sys.symmetric_keys sk ON dek.encryptor_thumbprint = sk.key_guid WHERE COALESCE(ak.name, sk.name) = ?"
                usage_result = await db_handler.execute_sql(key_usage_sql, params=[key_name])
                is_used = usage_result["success"] and usage_result["results"][0]["data"]
                
                if is_used and not force:
                    return json.dumps({"success": False, "error": f"Key '{key_name}' is currently in use. Use force=True to drop anyway."})
                
                drop_result = await db_handler.drop_master_key(key_name, key_type, force, remove_from_provider)
                if not drop_result.get("success", False): return json.dumps(drop_result)
                
                return json.dumps({
                    "success": True, "operation": "drop_sql_master_key", "connection": sql_connection,
                    "key_name": key_name, "key_type": key_type, "force": force,
                    "remove_from_provider": remove_from_provider, "was_used": is_used,
                    "steps": drop_result.get("steps", []), "timestamp": datetime.now().isoformat()
                }, indent=2)
                
            elif operation == "drop_unused":
                keys = await db_handler.list_master_keys(key_type)
                key_usage_sql = "SELECT DISTINCT COALESCE(ak.name, sk.name) as key_name FROM sys.dm_database_encryption_keys dek LEFT JOIN master.sys.asymmetric_keys ak ON dek.encryptor_thumbprint = ak.thumbprint LEFT JOIN master.sys.symmetric_keys sk ON dek.encryptor_thumbprint = sk.key_guid WHERE COALESCE(ak.name, sk.name) IS NOT NULL"
                usage_result = await db_handler.execute_sql(key_usage_sql)
                used_keys = {row["key_name"] for row in usage_result["results"][0]["data"]} if usage_result["success"] and usage_result["results"][0]["data"] else set()

                unused_keys = []
                for key_type_name in ["asymmetric_keys", "symmetric_keys"]:
                    if key_type and key_type_name != f"{key_type.lower()}_keys": continue
                    for key in keys.get(key_type_name, []):
                        if key["name"] not in used_keys:
                            unused_keys.append({"name": key["name"], "type": "RSA" if key_type_name == "asymmetric_keys" else "AES"})
                
                if not unused_keys:
                    return json.dumps({"success": True, "operation": "drop_unused_sql_master_keys", "message": "No unused keys found", "dropped_keys": [], "timestamp": datetime.now().isoformat()})

                dropped_keys, failed_keys = [], []
                for key_info in unused_keys:
                    try:
                        drop_result = await db_handler.drop_master_key(key_info["name"], key_info["type"], False, remove_from_provider)
                        if drop_result.get("success", False): dropped_keys.append(key_info["name"])
                        else: failed_keys.append({"name": key_info["name"], "error": drop_result.get("error")})
                    except Exception as e:
                        failed_keys.append({"name": key_info["name"], "error": str(e)})

                return json.dumps({
                    "success": len(dropped_keys) > 0, "operation": "drop_unused_sql_master_keys",
                    "summary": {"total_unused": len(unused_keys), "dropped": len(dropped_keys), "failed": len(failed_keys)},
                    "dropped_keys": dropped_keys, "failed_keys": failed_keys, "timestamp": datetime.now().isoformat()
                }, indent=2)
            
            elif operation == "rotate_dek":
                if not database_name:
                    return json.dumps({"success": False, "error": "database_name is required for rotate_dek"})
                
                rotation_result = await db_handler.rotate_database_encryption_key(database_name, key_type) # key_type is algorithm here
                updated_status = await db_handler.check_encryption_status(database_name)
                
                return json.dumps({
                    "success": True, "operation": "rotate_sql_database_encryption_key", "database": database_name,
                    "algorithm_used": rotation_result["algorithm_used"], "rotation_result": rotation_result["rotation_result"],
                    "updated_status": [{"database_name": s.database_name, "encryption_state": s.encryption_state, "encryption_state_desc": s.encryption_state_desc, "key_algorithm": s.key_algorithm, "key_length": s.key_length} for s in updated_status],
                    "timestamp": datetime.now().isoformat()
                }, indent=2)

            elif operation == "rotate_master":
                if not all([database_name, new_key_name, provider_name, ciphertrust_username, ciphertrust_password]):
                    return json.dumps({"success": False, "error": "database_name, new_key_name, provider_name, and ciphertrust credentials are required for rotate_master"})
                
                # Always ensure key_type has a default value before use.
                final_key_type = key_type or "RSA"

                final_key_size = None
                if key_size is None:
                    final_key_size = 2048 if final_key_type.upper() == "RSA" else 256
                else:
                    try:
                        final_key_size = int(key_size)
                    except (ValueError, TypeError):
                        return json.dumps({"success": False, "error": f"Invalid key_size '{key_size}'. Must be a valid integer."})

                rotation_result = await db_handler.rotate_master_key(database_name, new_key_name, provider_name, ciphertrust_username, ciphertrust_password, ciphertrust_domain, final_key_size, final_key_type)
                updated_status = await db_handler.check_encryption_status(database_name)

                return json.dumps({
                    "success": True, "operation": "rotate_sql_master_key", "database": database_name, "new_key_name": new_key_name,
                    "algorithm": rotation_result["algorithm"], "steps": rotation_result["steps"],
                    "updated_status": [{"database_name": s.database_name, "encryption_state": s.encryption_state, "encryption_state_desc": s.encryption_state_desc, "key_algorithm": s.key_algorithm, "key_length": s.key_length} for s in updated_status],
                    "timestamp": datetime.now().isoformat()
                }, indent=2)

            else:
                return json.dumps({"success": False, "error": f"Invalid operation '{operation}'. Must be 'create', 'list', 'drop', 'drop_unused', 'rotate_master', or 'rotate_dek'"})
            
        except Exception as e:
            logger.error(f"Error managing SQL keys: {e}", exc_info=True)
            return json.dumps({"success": False, "error": str(e), "error_type": type(e).__name__})
    
    # ============================================================================
    # ORACLE KEY MANAGEMENT TOOLS
    # ============================================================================
    
    @server.tool()
    async def manage_oracle_keys(
        operation: str,
        oracle_connection: str,
        container: str,
        wallet_password: Optional[str] = None,
        backup_tag: Optional[str] = None,
        force: bool = False,
        key_id_filter: Optional[str] = None,
        active_only: bool = True,
        include_history: bool = False
    ) -> str:
        """
        Manage Oracle Master Encryption Keys (MEKs) in the keystore (wallet).

        This tool handles the listing and rotation of the primary keys that protect
        all other keys within an Oracle TDE-enabled database. It is wallet-aware and
        will not require a password for auto-login or HSM wallets during rotation.

        ---
        **Operations:**
        - `rotate`: Generates a new MEK, making it the active key for the container(s).
        - `list`: Lists the MEKs present in the keystore, including their history.
        ---

        Args:
            operation: The action to perform: "rotate" or "list".
            oracle_connection: The name of the Oracle database connection to use.
            container: The container to operate on: "CDB$ROOT", a specific PDB name, or "ALL".
            wallet_password: The wallet password. Only required for rotating keys in a password-protected software wallet.
            backup_tag: (For rotate) An optional identifier for the pre-rotation wallet backup.
            force: (For rotate) If true, forces the key rotation.
            key_id_filter: (For list) An optional filter to list only a specific key ID.
            active_only: (For list) If true, shows only the currently active key.
            include_history: (For list) If true, includes historical (non-active) keys.

        Returns:
            A JSON string containing the results of the MEK operation.
        """
        try:
            db_handler = db_manager.get_database_handler(oracle_connection)

            if operation == "rotate":
                logger.info(f"=== manage_oracle_keys(rotate) called ===")
                
                # The rotate_mek method in the database handler is now wallet-aware
                # and will only use the password if necessary.
                result = await db_handler.rotate_mek(
                    container=container,
                    wallet_password=wallet_password,
                    backup_identifier=backup_tag,
                    force=force
                )
                
                return json.dumps(result, indent=2)

            elif operation == "list":
                logger.info(f"=== manage_oracle_keys(list) called ===")
                # List Oracle encryption keys from v$encryption_keys view.
                # This function was removed from the original file, so we'll re-implement it here.
                logger.info(f"Container: {container}, Active only: {active_only}")
                
                # Build query using the correct V$ENCRYPTION_KEYS view with proper columns
                keys_sql = """
                SELECT 
                    KEY_ID,
                    HEX_MKID,
                    TAG,
                    CREATION_TIME,
                    ACTIVATION_TIME,
                    CREATOR,
                    CREATOR_ID,
                    USER,
                    USER_ID,
                    KEY_USE,
                    KEYSTORE_TYPE,
                    ORIGIN,
                    BACKED_UP,
                    CREATOR_DBNAME,
                    CREATOR_DBID,
                    CREATOR_INSTANCE_NAME,
                    CREATOR_INSTANCE_NUMBER,
                    CREATOR_INSTANCE_SERIAL,
                    CREATOR_PDBNAME,
                    CREATOR_PDBID,
                    CREATOR_PDBUID,
                    CREATOR_PDBGUID,
                    ACTIVATING_DBNAME,
                    ACTIVATING_DBID,
                    ACTIVATING_INSTANCE_NAME,
                    ACTIVATING_INSTANCE_NUMBER,
                    ACTIVATING_INSTANCE_SERIAL,
                    ACTIVATING_PDBNAME,
                    ACTIVATING_PDBID,
                    ACTIVATING_PDBUID,
                    ACTIVATING_PDBGUID,
                    CON_ID
                FROM V$ENCRYPTION_KEYS
                """
                
                where_conditions = []
                
                if key_id_filter:
                    where_conditions.append(f"KEY_ID = '{key_id_filter}'")
                
                if active_only:
                    # For Oracle, we consider keys as active if they have an ACTIVATION_TIME
                    where_conditions.append("ACTIVATION_TIME IS NOT NULL")
                
                if where_conditions:
                    keys_sql += " WHERE " + " AND ".join(where_conditions)
                
                keys_sql += " ORDER BY ACTIVATION_TIME DESC"
                
                keys_result = await db_handler.execute_sql(keys_sql, container or "CDB$ROOT")
                
                keys = []
                if keys_result["success"] and keys_result["results"][0]["data"]:
                    for key in keys_result["results"][0]["data"]:
                        # Convert datetime objects to strings
                        if key.get("CREATION_TIME") and hasattr(key["CREATION_TIME"], "isoformat"):
                            key["CREATION_TIME"] = key["CREATION_TIME"].isoformat()
                        if key.get("ACTIVATION_TIME") and hasattr(key["ACTIVATION_TIME"], "isoformat"):
                            key["ACTIVATION_TIME"] = key["ACTIVATION_TIME"].isoformat()
                        
                        # Convert binary data to string representation
                        if key.get("HEX_MKID") and isinstance(key["HEX_MKID"], bytes):
                            key["HEX_MKID"] = key["HEX_MKID"].hex().upper()
                        
                        # Convert any other binary fields
                        for field_name, field_value in key.items():
                            if isinstance(field_value, bytes):
                                key[field_name] = field_value.hex().upper()
                        
                        keys.append(key)
                
                # Group keys by creator PDB
                keys_by_pdb = {}
                for key in keys:
                    pdb_name = key.get("CREATOR_PDBNAME", "CDB$ROOT")
                    if pdb_name not in keys_by_pdb:
                        keys_by_pdb[pdb_name] = []
                    keys_by_pdb[pdb_name].append(key)
                
                # Summary
                active_keys = [k for k in keys if k.get("ACTIVATION_TIME") is not None]
                
                result_data = {
                    "success": True,
                    "operation": "list_oracle_encryption_keys",
                    "connection": oracle_connection,
                    "container_filter": container,
                    "key_id_filter": key_id_filter,
                    "active_only": active_only,
                    "include_history": include_history,
                    "summary": {
                        "total_keys": len(keys),
                        "active_keys": len(active_keys),
                        "containers_with_keys": len(keys_by_pdb),
                        "latest_activation": keys[0]["ACTIVATION_TIME"] if keys and keys[0].get("ACTIVATION_TIME") else None
                    },
                    "keys_by_container": keys_by_pdb,
                    "all_keys": keys,
                    "timestamp": datetime.now().isoformat()
                }
                
                logger.info(f"=== list_oracle_encryption_keys completed ===")
                return json.dumps(result_data, indent=2)
            
            else:
                return json.dumps({"success": False, "error": f"Invalid operation '{operation}'."})

        except Exception as e:
            logger.error(f"Error managing Oracle keys: {e}", exc_info=True)
            return json.dumps({"success": False, "error": str(e), "error_type": type(e).__name__}) 