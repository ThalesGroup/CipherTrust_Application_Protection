"""
Unified encryption and decryption tools for SQL Server and Oracle databases
"""

import json
import logging
import asyncio
from typing import Optional, List
from datetime import datetime

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

def register_encryption_tools(server: FastMCP, db_manager):
    """Register unified encryption and decryption tools with the MCP server"""
    
    # ============================================================================
    # SQL SERVER ENCRYPTION TOOLS
    # ============================================================================
    
    @server.tool()
    async def manage_sql_encryption(
        operation: str,
        database_names: str,
        sql_connection: str,
        provider_name: Optional[str] = None,
        ciphertrust_username: Optional[str] = None,
        ciphertrust_password: Optional[str] = None,
        key_name: Optional[str] = None,
        ciphertrust_domain: str = "root",
        key_type: str = "RSA",
        key_size: Optional[str] = None
    ) -> str:
        """
        Encrypt or decrypt one or more SQL Server databases.

        This tool manages the encryption state of SQL Server databases. The 'encrypt'
        operation is idempotent and will automatically handle the creation of the
        necessary TDE infrastructure (keys, logins, credentials).

        ---
        **Operations:**
        - `encrypt`: Encrypts the specified databases. Skips any that are already encrypted.
        - `decrypt`: Decrypts the specified databases.

        **Database Targeting (`database_names`):**
        - A single database name: "MyDatabase"
        - A comma-separated list: "DB1,DB2,DB3"
        - All user databases: "all databases" (for encryption)
        - All encrypted databases: "all encrypted databases" (for decryption)
        ---

        Args:
            operation: The action to perform: "encrypt" or "decrypt".
            database_names: The target database(s) for the operation (see above for formats).
            sql_connection: The name of the database connection to use.
            provider_name: (Required for encrypt) The name of the EKM cryptographic provider.
            ciphertrust_username: (Required for encrypt) The CipherTrust Manager username.
            ciphertrust_password: (Required for encrypt) The CipherTrust Manager password.
            key_name: (Required for encrypt) The name of the master key to use/create in the EKM.
            ciphertrust_domain: The CipherTrust Manager domain for the user. Defaults to "root".
            key_type: The type of key to create, either "RSA" or "AES". Defaults to "RSA".
            key_size: The size of the key in bits (e.g., "2048", "3072"). Defaults to 2048 for RSA, 256 for AES.

        Returns:
            A JSON string detailing the outcome of the operation.
        """
        try:
            db_handler = db_manager.get_database_handler(sql_connection)

            if operation == "encrypt":
                if not all([provider_name, ciphertrust_username, ciphertrust_password, key_name]):
                    return json.dumps({"success": False, "error": "Missing required arguments for encryption."})

                if "all databases" in database_names.lower():
                    databases = [db["database_name"] for db in await db_handler.list_databases()]
                else:
                    databases = [db.strip() for db in database_names.split(',') if db.strip()]

                if not databases:
                    return json.dumps({"success": False, "error": "No valid databases specified"})
                
                # Step 1: Check if the cryptographic provider exists
                logger.info(f"Step 1: Checking if provider '{provider_name}' exists")
                providers = await db_handler.list_cryptographic_providers()
                provider_exists = any(p["name"] == provider_name for p in providers)
                logger.info(f"Provider exists: {provider_exists}")

                if not provider_exists:
                    logger.error(f"Cryptographic provider '{provider_name}' not found")
                    return json.dumps({
                        "success": False,
                        "error": f"Cryptographic provider '{provider_name}' not found. Please create it first."
                    })
                
                final_key_size = None
                if key_size is None:
                    final_key_size = 2048 if key_type.upper() == "RSA" else 256
                else:
                    try:
                        final_key_size = int(key_size)
                    except (ValueError, TypeError):
                        return json.dumps({"success": False, "error": f"Invalid key_size '{key_size}'."})

                # Step 2: Create TDE infrastructure (will use existing key or create new)
                logger.info(f"Step 2: Creating TDE infrastructure for key: '{key_name}'")
                infra_result = await db_handler.create_tde_infrastructure(
                    key_name, provider_name, ciphertrust_username, ciphertrust_password,
                    ciphertrust_domain, final_key_size, key_type
                )
                
                # Check if infrastructure creation failed
                if not infra_result.get("success", True):
                    logger.error(f"Infrastructure creation failed: {infra_result.get('error')}")
                    return json.dumps({
                        "success": False,
                        "error": infra_result.get("error"),
                        "existing_credential": infra_result.get("existing_credential"),
                        "attempted_credential": infra_result.get("attempted_credential")
                    })
                
                logger.info(f"Infrastructure result: key_existed={infra_result.get('key_existed', False)}")

                is_asymmetric = infra_result["is_asymmetric"]
                status_check = await db_handler.check_encryption_status()
                already_encrypted = {s.database_name for s in status_check if s.is_encrypted}
                
                target_dbs = [db for db in databases if db not in already_encrypted]
                skipped_dbs = [db for db in databases if db in already_encrypted]

                if not target_dbs:
                    return json.dumps({"success": True, "message": "All specified databases are already encrypted.", "skipped_databases": skipped_dbs})

                encrypted_dbs, failed_dbs = [], []
                for db_name in target_dbs:
                    try:
                        result = await db_handler.encrypt_database(db_name, key_name, is_asymmetric)
                        if result.get("success", False):
                            encrypted_dbs.append(db_name)
                        else:
                            failed_dbs.append({"database": db_name, "error": result.get("error")})
                    except Exception as e:
                        failed_dbs.append({"database": db_name, "error": str(e)})

                return json.dumps({
                    "success": len(failed_dbs) == 0,
                    "encrypted_databases": encrypted_dbs,
                    "failed_databases": failed_dbs,
                    "skipped_databases": skipped_dbs,
                }, indent=2)

            elif operation == "decrypt":
                if "all encrypted databases" in database_names.lower():
                    status_check = await db_handler.check_encryption_status()
                    databases = [s.database_name for s in status_check if s.is_encrypted]
                else:
                    databases = [db.strip() for db in database_names.split(',') if db.strip()]

                if not databases:
                    return json.dumps({"success": False, "error": "No valid databases specified for decryption."})

                decrypted_dbs, failed_dbs = [], []
                for db_name in databases:
                    try:
                        result = await db_handler.decrypt_database(db_name)
                        if result.get("success", False):
                            decrypted_dbs.append(db_name)
                        else:
                            failed_dbs.append({"database": db_name, "error": result.get("error")})
                    except Exception as e:
                        failed_dbs.append({"database": db_name, "error": str(e)})
                
                return json.dumps({
                    "success": len(failed_dbs) == 0,
                    "decrypted_databases": decrypted_dbs,
                    "failed_databases": failed_dbs,
                }, indent=2)

            else:
                return json.dumps({"success": False, "error": f"Invalid operation '{operation}'."})

        except Exception as e:
            logger.error(f"Error managing SQL encryption: {e}", exc_info=True)
            return json.dumps({"success": False, "error": str(e), "error_type": type(e).__name__})

    # ============================================================================
    # ORACLE ENCRYPTION TOOLS
    # ============================================================================
    
    @server.tool()
    async def manage_oracle_tablespace_encryption(
        oracle_connection: str,
        operation: str,
        tablespaces: Optional[str] = None,
        container: str = "CDB$ROOT",
        algorithm: str = "AES256",
        method: str = "online",
        object_type: str = "tablespace",
        tablespace_name: Optional[str] = None
    ) -> str:
        """
        Manage the encryption of Oracle tablespaces with container awareness.

        ---
        **Operations:**
        - `encrypt`: Encrypts the specified tablespace(s) with automatic container detection.
        - `list_tablespaces`: Lists all tablespaces and their encryption status across containers.
        - `list_encrypted`: Lists only encrypted tablespaces across containers.
        - `list`: Lists all encrypted objects (tablespaces, tables, columns).
        - `status`: Checks encryption status of a specific tablespace.
        ---

        **Container Behavior for Encryption:**
        - If container="CDB$ROOT" or not specified: Searches ALL containers for the tablespace
        - If container="ALL": Searches ALL containers for the tablespace  
        - If container=specific PDB name: Only encrypts tablespace in that specific PDB
        - Automatically switches to the correct container where tablespace exists
        - Shows which container each tablespace was encrypted in

        Args:
            oracle_connection: Oracle database connection name.
            operation: The tablespace encryption operation ("encrypt", "list_tablespaces", "list_encrypted", "list", "status").
            tablespaces: Comma-separated list of tablespace names to encrypt.
            container: Container specification:
                     - "CDB$ROOT" (default): Search all containers for tablespace
                     - "ALL": Search all containers for tablespace
                     - Specific PDB name: Only encrypt in that PDB
            algorithm: Encryption algorithm to use (AES256, default: AES256).
            method: Encryption method (online or offline, default: online).
            object_type: Type of objects to list when operation is "list" (tablespace, table, column, all).
            tablespace_name: Specific tablespace name for status operation.

        Examples:
            # Encrypt tablespace wherever it exists (auto-detect container)
            {"operation": "encrypt", "tablespaces": "PLAIN_TS", "container": "CDB$ROOT"}
            
            # Encrypt tablespace only in specific PDB
            {"operation": "encrypt", "tablespaces": "PLAIN_TS", "container": "PDB1"}
            
            # List all tablespaces across all containers
            {"operation": "list_tablespaces"}

        Returns:
            JSON with encryption results, including which container each tablespace was processed in.
        """
        try:
            logger.info(f"=== manage_oracle_tablespace_encryption called with operation: {operation} ===")
            db_handler = db_manager.get_database_handler(oracle_connection)
            
            if operation == "encrypt":
                if not tablespaces:
                    return json.dumps({
                        "success": False,
                        "error": "tablespaces parameter is required for encrypt operation"
                    })
                
                # Parse tablespace names
                tablespace_list = [ts.strip() for ts in tablespaces.split(",")]
                
                results = []
                successful_count = 0
                failed_count = 0
                
                if db_handler.db_type == "oracle":
                    # Oracle tablespace encryption with container awareness
                    for tablespace_name in tablespace_list:
                        # First, find which container(s) contain this tablespace using corrected column names
                        find_tablespace_sql = f"""
                        SELECT 
                            vt.NAME AS TABLESPACE_NAME,
                            CASE 
                                WHEN vet.TS# IS NOT NULL THEN 'YES'
                                ELSE 'NO'
                            END AS ENCRYPTED,
                            vt.ENCRYPT_IN_BACKUP AS TABLESPACE_ENCRYPTION,
                            vt.BIGFILE AS BIGFILE,
                            vt.CON_ID,
                            vet.ENCRYPTIONALG AS ENCRYPTION_ALGORITHM,
                            vet.ENCRYPTEDTS AS ENCRYPTED_TABLESPACE,
                            (SELECT NAME FROM V$CONTAINERS WHERE CON_ID = vt.CON_ID) AS CONTAINER_NAME
                        FROM V$TABLESPACE vt
                        LEFT JOIN V$ENCRYPTED_TABLESPACES vet ON vt.TS# = vet.TS# AND vt.CON_ID = vet.CON_ID
                        WHERE vt.NAME = '{tablespace_name}'
                        AND vt.NAME NOT IN ('SYSTEM', 'SYSAUX', 'TEMP', 'UNDOTBS1', 'UNDOTBS2', 'TEMP_TBS', 'TEMP_TBS1', 'TEMP_TBS2', 'PDB$SEED')
                        """
                        
                        # Search using the same container approach as list_tablespaces
                        search_result = await db_handler.execute_sql(find_tablespace_sql, container)
                        
                        if not (search_result["success"] and search_result["results"][0]["data"]):
                            results.append({
                                "tablespace": tablespace_name,
                                "success": False,
                                "error": f"Tablespace '{tablespace_name}' not found in any accessible container",
                                "debug_info": {
                                    "search_success": search_result.get("success", False) if search_result else False,
                                    "query_result": search_result.get("results", []) if search_result else [],
                                    "container_requested": container
                                }
                            })
                            failed_count += 1
                            continue
                        
                        # Process each instance of the tablespace (could be in multiple PDBs)
                        tablespace_instances = search_result["results"][0]["data"]
                        
                        # Debug: Add information about found instances
                        found_containers = [ts["CONTAINER_NAME"] for ts in tablespace_instances]
                        
                        processed_any = False
                        for ts_info in tablespace_instances:
                            target_container = ts_info["CONTAINER_NAME"] or f"CON_ID_{ts_info['CON_ID']}"
                            
                            # Skip if user specified a specific container and this isn't it
                            if container != "CDB$ROOT" and container and container != target_container:
                                continue
                            
                            processed_any = True
                            
                            if ts_info["ENCRYPTED"] == "YES":
                                results.append({
                                    "tablespace": tablespace_name,
                                    "container": target_container,
                                    "success": False,
                                    "error": "Tablespace is already encrypted",
                                    "skipped": True
                                })
                                continue
                            
                            # Encrypt the tablespace in the correct container
                            encrypt_result = await db_handler.encrypt_tablespace(
                                target_container,
                                tablespace_name,
                                "AES256",  # Fixed to AES256 for Oracle
                                method == "online"
                            )
                            
                            if encrypt_result["success"]:
                                successful_count += 1
                            else:
                                failed_count += 1
                            
                            results.append({
                                "tablespace": tablespace_name,
                                "container": target_container,
                                "success": encrypt_result["success"],
                                "algorithm": "AES256",  # Always AES256 for Oracle
                                "method": encrypt_result.get("method", method),
                                "steps": encrypt_result.get("steps", []),
                                "error": encrypt_result.get("error") if not encrypt_result["success"] else None
                            })
                        
                        # Debug: Check if tablespace was found but filtered out
                        if not processed_any and tablespace_instances:
                            results.append({
                                "tablespace": tablespace_name,
                                "success": False,
                                "error": f"Tablespace '{tablespace_name}' found but not in requested container",
                                "debug_info": {
                                    "found_containers": found_containers,
                                    "requested_container": container,
                                    "available_instances": len(tablespace_instances)
                                }
                            })
                            failed_count += 1

                # Get final encryption status
                final_status_sql = """
                SELECT 
                    vt.NAME AS TABLESPACE_NAME,
                    vt.CON_ID,
                    c.NAME AS CONTAINER_NAME,
                    'YES' AS ENCRYPTED,
                    vet.ENCRYPTION_ALG,
                    vet.ENCRYPTION_ALG_PARAM,
                    vet.ENCRYPTION_ALG_SALT,
                    vet.ENCRYPTION_ALG_INTEGRITY
                FROM V$TABLESPACE vt
                INNER JOIN V$ENCRYPTED_TABLESPACES vet ON vt.TS# = vet.TS# AND vt.CON_ID = vet.CON_ID
                INNER JOIN V$CONTAINERS c ON vt.CON_ID = c.CON_ID
                WHERE vt.NAME NOT IN ('SYSTEM', 'SYSAUX', 'TEMP', 'UNDOTBS1', 'UNDOTBS2', 'TEMP_TBS', 'TEMP_TBS1', 'TEMP_TBS2', 'PDB$SEED')
                AND vt.NAME NOT LIKE 'SYS%'
                AND vt.NAME NOT LIKE 'AUX%'
                AND vt.NAME NOT LIKE 'TEMP%'
                AND vt.NAME NOT LIKE 'UNDO%'
                AND vt.NAME NOT LIKE 'USERS%'
                AND vt.NAME NOT LIKE 'PDB$SEED%'
                AND c.OPEN_MODE = 'READ WRITE'
                ORDER BY c.NAME, vt.NAME
                """
                
                final_result = await db_handler.execute_sql(final_status_sql, container)
                
                encrypted_tablespaces = []
                if final_result["success"] and final_result["results"][0]["data"]:
                    encrypted_tablespaces = [ts["TABLESPACE_NAME"] for ts in final_result["results"][0]["data"]]
                
                result_data = {
                    "success": successful_count > 0,
                    "operation": "encrypt_oracle_tablespace",
                    "connection": oracle_connection,
                    "container": container,
                    "algorithm": "AES256",  # Always AES256 for Oracle
                    "summary": {
                        "requested": len(tablespace_list),
                        "successful": successful_count,
                        "failed": failed_count,
                        "skipped": len([r for r in results if r.get("skipped", False)])
                    },
                    "results": results,
                    "total_encrypted_tablespaces": len(encrypted_tablespaces),
                    "encrypted_tablespaces": encrypted_tablespaces,
                    "timestamp": datetime.now().isoformat()
                }
                
            elif operation == "list":
                results = {}
                
                if object_type in ["tablespace", "all"]:
                    # List encrypted tablespaces using V$ views
                    ts_sql = """
                    SELECT 
                        vt.NAME AS TABLESPACE_NAME,
                        CASE 
                            WHEN vet.TS# IS NOT NULL THEN 'YES'
                            ELSE 'NO'
                        END AS ENCRYPTED,
                        vt.CON_ID
                    FROM V$TABLESPACE vt
                    INNER JOIN V$ENCRYPTED_TABLESPACES vet ON vt.TS# = vet.TS# AND vt.CON_ID = vet.CON_ID
                    WHERE vt.NAME NOT IN (
                        'SYSTEM', 'SYSAUX', 'TEMP', 'UNDOTBS1', 'UNDOTBS2',
                        'TEMP_TBS', 'TEMP_TBS1', 'TEMP_TBS2', 'PDB$SEED'
                    )
                    ORDER BY vt.NAME
                    """
                    
                    ts_result = await db_handler.execute_sql(ts_sql, container)
                    
                    if ts_result["success"] and ts_result["results"][0]["data"]:
                        encrypted_tablespaces = ts_result["results"][0]["data"]
                        
                        # Convert any binary data to string representation
                        for ts in encrypted_tablespaces:
                            for field_name, field_value in ts.items():
                                if isinstance(field_value, bytes):
                                    ts[field_name] = field_value.hex().upper()
                        
                        results["encrypted_tablespaces"] = encrypted_tablespaces
                    else:
                        results["encrypted_tablespaces"] = []
                
                if object_type in ["table", "all"]:
                    # List tables in encrypted tablespaces
                    table_sql = """
                    SELECT 
                        t.OWNER,
                        t.TABLE_NAME,
                        t.TABLESPACE_NAME,
                        ts.ENCRYPTED,
                        t.NUM_ROWS,
                        t.BLOCKS,
                        t.LAST_ANALYZED
                    FROM DBA_TABLES t
                    JOIN DBA_TABLESPACES ts ON t.TABLESPACE_NAME = ts.TABLESPACE_NAME
                    WHERE ts.ENCRYPTED = 'YES'
                    AND ts.TABLESPACE_NAME NOT IN (
                        'SYSTEM', 'SYSAUX', 'TEMP', 'UNDOTBS1', 'UNDOTBS2',
                        'TEMP_TBS', 'TEMP_TBS1', 'TEMP_TBS2',
                        'USERS', 'EXAMPLE', 'PDB$SEED'
                    )
                    AND ts.CONTENTS NOT IN ('UNDO', 'TEMPORARY')
                    AND t.OWNER NOT IN ('SYS', 'SYSTEM', 'OUTLN', 'DIP', 'ORACLE_OCM', 'APPQOSSYS', 'DBSNMP', 'CTXSYS', 'XDB', 'ANONYMOUS', 'EXFSYS', 'MDDATA', 'DBSFWUSER', 'REMOTE_SCHEDULER_AGENT', 'SI_INFORMTN_SCHEMA', 'ORDDATA', 'ORDSYS', 'MDSYS', 'OLAPSYS', 'WMSYS', 'APEX_040000', 'APEX_PUBLIC_USER', 'FLOWS_FILES')
                    ORDER BY t.OWNER, t.TABLE_NAME
                    """
                    
                    table_result = await db_handler.execute_sql(table_sql, container)
                    
                    if table_result["success"] and table_result["results"][0]["data"]:
                        results["encrypted_tables"] = table_result["results"][0]["data"]
                    else:
                        results["encrypted_tables"] = []
                
                if object_type in ["column", "all"]:
                    # List encrypted columns
                    column_sql = """
                    SELECT 
                        c.OWNER,
                        c.TABLE_NAME,
                        c.COLUMN_NAME,
                        c.ENCRYPTION_ALG,
                        c.SALT,
                        c.INTEGRITY_ALG
                    FROM DBA_ENCRYPTED_COLUMNS c
                    ORDER BY c.OWNER, c.TABLE_NAME, c.COLUMN_NAME
                    """
                    
                    column_result = await db_handler.execute_sql(column_sql, container)
                    
                    if column_result["success"] and column_result["results"][0]["data"]:
                        results["encrypted_columns"] = column_result["results"][0]["data"]
                    else:
                        results["encrypted_columns"] = []
                
                # Summary
                summary = {
                    "encrypted_tablespaces": len(results.get("encrypted_tablespaces", [])),
                    "encrypted_tables": len(results.get("encrypted_tables", [])),
                    "encrypted_columns": len(results.get("encrypted_columns", []))
                }
                
                result_data = {
                    "success": True,
                    "operation": "list_oracle_encrypted_objects",
                    "connection": oracle_connection,
                    "container": container,
                    "object_type": object_type,
                    "summary": summary,
                    "results": results,
                    "timestamp": datetime.now().isoformat()
                }
                
            elif operation == "status":
                if not tablespace_name:
                    return json.dumps({"success": False, "error": "tablespace_name is required for status operation"})
                
                # Use container-aware tablespace lookup using correct Oracle view columns
                find_tablespace_sql = f"""
                SELECT 
                    vt.NAME AS TABLESPACE_NAME,
                    CASE 
                        WHEN vet.TS# IS NOT NULL THEN 'YES'
                        ELSE 'NO'
                    END AS ENCRYPTED,
                    vt.ENCRYPT_IN_BACKUP AS TABLESPACE_ENCRYPTION,
                    vt.BIGFILE AS BIGFILE,
                    vt.CON_ID,
                    vet.ENCRYPTIONALG AS ENCRYPTION_ALGORITHM,
                    vet.ENCRYPTEDTS AS ENCRYPTED_TABLESPACE,
                    vet.MASTERKEYID,
                    vet.KEY_VERSION,
                    vet.STATUS AS ENCRYPTION_STATUS,
                    (SELECT NAME FROM V$CONTAINERS WHERE CON_ID = vt.CON_ID) AS CONTAINER_NAME
                FROM V$TABLESPACE vt
                LEFT JOIN V$ENCRYPTED_TABLESPACES vet ON vt.TS# = vet.TS# AND vt.CON_ID = vet.CON_ID
                WHERE vt.NAME = '{tablespace_name}'
                AND vt.NAME NOT IN ('SYSTEM', 'SYSAUX', 'TEMP', 'UNDOTBS1', 'UNDOTBS2', 'TEMP_TBS', 'TEMP_TBS1', 'TEMP_TBS2', 'PDB$SEED')
                """
                
                # Search using the same container approach as list_tablespaces
                search_result = await db_handler.execute_sql(find_tablespace_sql, container)
                
                if not (search_result["success"] and search_result["results"][0]["data"]):
                    return json.dumps({
                        "success": False,
                        "error": f"Tablespace '{tablespace_name}' not found in any accessible container"
                    })
                
                # Get the first instance of the tablespace (or the one in the specified container)
                tablespace_instances = search_result["results"][0]["data"]
                ts_info = None
                target_container = None
                
                # If specific container requested, find tablespace in that container
                if container != "CDB$ROOT" and container:
                    for instance in tablespace_instances:
                        instance_container = instance["CONTAINER_NAME"] or f"CON_ID_{instance['CON_ID']}"
                        if instance_container == container:
                            ts_info = instance
                            target_container = instance_container
                            break
                    
                    if not ts_info:
                        return json.dumps({
                            "success": False,
                            "error": f"Tablespace '{tablespace_name}' not found in container '{container}'"
                        })
                else:
                    # Use first instance found
                    ts_info = tablespace_instances[0]
                    target_container = ts_info["CONTAINER_NAME"] or f"CON_ID_{ts_info['CON_ID']}"
                
                # Get encryption progress if encryption is in progress
                progress_info = None
                if ts_info["ENCRYPTED"] == "ENCRYPTING":
                    progress_sql = f"""
                    SELECT 
                        TABLESPACE_NAME,
                        ENCRYPTION_PROGRESS,
                        ENCRYPTION_STATUS
                    FROM V$ENCRYPTION_PROGRESS
                    WHERE TABLESPACE_NAME = '{tablespace_name}'
                    """
                    
                    progress_result = await db_handler.execute_sql(progress_sql, container)
                    if progress_result["success"] and progress_result["results"][0]["data"]:
                        progress_info = progress_result["results"][0]["data"][0]
                
                # Convert any bytes fields to hex strings for JSON serialization
                master_key_id = ts_info.get("MASTERKEYID")
                if isinstance(master_key_id, bytes):
                    master_key_id = master_key_id.hex().upper()
                
                result_data = {
                    "success": True,
                    "operation": "check_oracle_tablespace_encryption_status",
                    "connection": oracle_connection,
                    "container": target_container,  # Show actual container where tablespace was found
                    "requested_container": container,  # Show what was requested
                    "tablespace_name": tablespace_name,
                    "encryption_status": {
                        "is_encrypted": ts_info["ENCRYPTED"] == "YES",
                        "encryption_state": ts_info["ENCRYPTED"],
                        "tablespace_encryption_enabled": ts_info["TABLESPACE_ENCRYPTION"],
                        "is_bigfile": ts_info["BIGFILE"] == "YES",
                        "algorithm": ts_info.get("ENCRYPTION_ALGORITHM"),
                        "encrypted_tablespace": ts_info.get("ENCRYPTED_TABLESPACE"),
                        "master_key_id": master_key_id,
                        "key_version": ts_info.get("KEY_VERSION"),
                        "encryption_status": ts_info.get("ENCRYPTION_STATUS"),
                        "con_id": ts_info["CON_ID"]
                    },
                    "encryption_progress": progress_info,
                    "timestamp": datetime.now().isoformat()
                }
                
            elif operation == "list_tablespaces":
                # List all tablespaces excluding system tablespaces
                list_sql = """
                SELECT 
                    vt.NAME AS TABLESPACE_NAME,
                    CASE 
                        WHEN vet.TS# IS NOT NULL THEN 'YES'
                        ELSE 'NO'
                    END AS ENCRYPTED,
                    vt.CON_ID
                FROM V$TABLESPACE vt
                LEFT JOIN V$ENCRYPTED_TABLESPACES vet ON vt.TS# = vet.TS# AND vt.CON_ID = vet.CON_ID
                WHERE vt.NAME NOT IN (
                    'SYSTEM', 'SYSAUX', 'TEMP', 'UNDOTBS1', 'UNDOTBS2',
                    'TEMP_TBS', 'TEMP_TBS1', 'TEMP_TBS2', 'PDB$SEED'
                )
                ORDER BY vt.NAME
                """
                
                list_result = await db_handler.execute_sql(list_sql, container)
                
                if not list_result["success"]:
                    return json.dumps({
                        "success": False,
                        "error": f"Failed to list tablespaces: {list_result.get('error', 'Unknown error')}"
                    })
                
                result_data = {
                    "success": True,
                    "operation": "list_tablespaces",
                    "connection": oracle_connection,
                    "container": container,
                    "tablespaces": list_result["results"][0]["data"] if list_result["results"][0]["data"] else [],
                    "count": len(list_result["results"][0]["data"]) if list_result["results"][0]["data"] else 0,
                    "timestamp": datetime.now().isoformat()
                }
                
            elif operation == "list_encrypted":
                # List only encrypted tablespaces excluding system tablespaces
                encrypted_sql = """
                SELECT 
                    vt.NAME AS TABLESPACE_NAME,
                    'YES' AS ENCRYPTED,
                    vt.CON_ID
                FROM V$TABLESPACE vt
                INNER JOIN V$ENCRYPTED_TABLESPACES vet ON vt.TS# = vet.TS# AND vt.CON_ID = vet.CON_ID
                WHERE vt.NAME NOT IN (
                    'SYSTEM', 'SYSAUX', 'TEMP', 'UNDOTBS1', 'UNDOTBS2',
                    'TEMP_TBS', 'TEMP_TBS1', 'TEMP_TBS2', 'PDB$SEED'
                )
                ORDER BY vt.NAME
                """
                
                encrypted_result = await db_handler.execute_sql(encrypted_sql, container)
                
                if not encrypted_result["success"]:
                    return json.dumps({
                        "success": False,
                        "error": f"Failed to list encrypted tablespaces: {encrypted_result.get('error', 'Unknown error')}"
                    })
                
                result_data = {
                    "success": True,
                    "operation": "list_encrypted",
                    "connection": oracle_connection,
                    "container": container,
                    "encrypted_tablespaces": encrypted_result["results"][0]["data"] if encrypted_result["results"][0]["data"] else [],
                    "count": len(encrypted_result["results"][0]["data"]) if encrypted_result["results"][0]["data"] else 0,
                    "timestamp": datetime.now().isoformat()
                }
                
            else:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid operation: {operation}. Must be 'encrypt', 'list', 'list_tablespaces', 'list_encrypted', or 'status'"
                })

            logger.info(f"=== manage_oracle_tablespace_encryption completed ===")
            return json.dumps(result_data, indent=2)

        except Exception as e:
            logger.error(f"Error in Oracle tablespace encryption: {e}", exc_info=True)
            return json.dumps({"success": False, "error": str(e), "error_type": type(e).__name__}) 