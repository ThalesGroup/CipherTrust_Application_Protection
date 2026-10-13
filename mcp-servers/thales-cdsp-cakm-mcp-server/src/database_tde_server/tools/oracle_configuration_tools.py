"""
Oracle TDE configuration management tools

This module provides tools for configuring Oracle Transparent Data Encryption (TDE) settings.
Database encryption and encryption key management are handled by Thales CipherTrust Application Key Management (CAKM)
connector, which is integrated with Thales CDSP (CipherTrust Data Security Platform).

Available tools:
- manage_oracle_configuration: Manage Oracle TDE configuration parameters
  - Operations: get, set, verify
  - Manages TDE configuration parameters like wallet_root and tde_configuration
  - Supports SPFILE and memory parameter management
  - Provides configuration validation and recommendations
"""

import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

def register_oracle_configuration_tools(server: FastMCP, db_manager):
    """Register Oracle TDE configuration tools with the MCP server"""

    @server.tool()
    async def manage_oracle_configuration(
        oracle_connection: str,
        operation: str,
        include_spfile: bool = True,
        wallet_root: Optional[str] = None,
        tde_configuration: Optional[str] = None,
        encrypt_new_tablespaces: Optional[str] = None,
        force_restart: bool = False,
        validate_only: bool = False
    ) -> str:
        """
        Manage Oracle TDE configuration parameters.

        ---
        **Operations:**
        - `get`: Retrieves current TDE configuration parameters.
        - `set`: Sets TDE-related parameters like wallet_root.
        - `verify`: Verifies the TDE setup and provides recommendations.
        ---

        Args:
            oracle_connection: Oracle database connection name
            operation: Configuration operation - "get" | "set" | "verify"
            include_spfile: Include SPFILE values that may differ from memory (for get operation)
            wallet_root: Wallet root directory path (for set operation)
            tde_configuration: "HSM" | "FILE" | "HSM|FILE" | "FILE|HSM" (for set operation)
            encrypt_new_tablespaces: "DDL" | "ALWAYS" | "CLOUD_ONLY" | "MANUAL" (for set operation)
            force_restart: Automatically restart database if required (for set operation)
            validate_only: Only validate parameters without setting them (for set operation)

        Returns:
            JSON string containing the results of the configuration operation.
        """
        try:
            logger.info(f"=== manage_oracle_configuration called with operation: {operation} ===")
            db_handler = db_manager.get_database_handler(oracle_connection)
            
            if operation == "get":
                # Get TDE configuration using existing method
                config_params = await db_handler.get_tde_configuration()
                
                # Get additional relevant parameters
                additional_sql = """
                SELECT 
                    NAME,
                    VALUE,
                    ISDEFAULT,
                    ISMODIFIED,
                    ISADJUSTED,
                    ISSYS_MODIFIABLE,
                    DESCRIPTION
                FROM V$PARAMETER
                WHERE NAME IN ('tde_configuration', 'wallet_root', 'encrypt_new_tablespaces', 'compatible')
                ORDER BY NAME
                """
                
                additional_result = await db_handler.execute_sql(additional_sql, "CDB$ROOT")
                
                if additional_result["success"]:
                    for row in additional_result["results"][0]["data"]:
                        param_name = row["NAME"]
                        config_params[param_name] = {
                            "value": row["VALUE"],
                            "is_default": row["ISDEFAULT"] == "TRUE",
                            "is_modified": row["ISMODIFIED"] == "TRUE",
                            "is_adjusted": row["ISADJUSTED"] == "TRUE",
                            "is_sys_modifiable": row.get("ISSYS_MODIFIABLE", ""),
                            "description": row.get("DESCRIPTION", "")
                        }
                
                # Get SPFILE values if requested
                spfile_values = {}
                if include_spfile:
                    spfile_sql = """
                    SELECT NAME, VALUE
                    FROM V$SPPARAMETER
                    WHERE NAME IN ('tde_configuration', 'wallet_root', 'encrypt_new_tablespaces')
                    AND VALUE IS NOT NULL
                    """
                    
                    spfile_result = await db_handler.execute_sql(spfile_sql, "CDB$ROOT")
                    if spfile_result["success"]:
                        for row in spfile_result["results"][0]["data"]:
                            spfile_values[row["NAME"]] = row["VALUE"]
                
                # Check wallet status
                wallet_status = await db_handler.get_wallet_status("v$", "CDB$ROOT")
                wallet_configured = any(w["STATUS"] == "OPEN" for w in wallet_status)
                
                result_data = {
                    "success": True,
                    "operation": "get_oracle_tde_configuration",
                    "connection": oracle_connection,
                    "configuration": config_params,
                    "spfile_values": spfile_values,
                    "wallet_status": {
                        "configured": wallet_configured,
                        "status": wallet_status
                    },
                    "summary": {
                        "wallet_root_set": bool(config_params.get("wallet_root", {}).get("value")),
                        "wallet_root_value": config_params.get("wallet_root", {}).get("value"),
                        "tde_configuration": config_params.get("tde_configuration", {}).get("value"),
                        "encrypt_new_tablespaces": config_params.get("encrypt_new_tablespaces", {}).get("value", "MANUAL"),
                        "requires_restart": any(
                            spfile_values.get(p) != config_params.get(p, {}).get("value")
                            for p in ["wallet_root", "tde_configuration"]
                        )
                    },
                    "timestamp": datetime.now().isoformat()
                }
                
            elif operation == "set":
                # Validate parameters
                validation_errors = []
                
                if tde_configuration:
                    valid_tde_configs = ["HSM", "FILE", "HSM|FILE", "FILE|HSM"]
                    if tde_configuration not in valid_tde_configs:
                        validation_errors.append(f"Invalid tde_configuration: {tde_configuration}. Valid values: {valid_tde_configs}")
                
                if encrypt_new_tablespaces:
                    valid_encrypt_values = ["DDL", "ALWAYS", "CLOUD_ONLY", "MANUAL"]
                    if encrypt_new_tablespaces.upper() not in valid_encrypt_values:
                        validation_errors.append(f"Invalid encrypt_new_tablespaces: {encrypt_new_tablespaces}. Valid values: {valid_encrypt_values}")
                
                if validation_errors:
                    return json.dumps({
                        "success": False,
                        "operation": "validate_parameters",
                        "errors": validation_errors
                    })
                
                if validate_only:
                    return json.dumps({
                        "success": True,
                        "operation": "validate_parameters",
                        "message": "All parameters are valid"
                    })
                
                steps = []
                restart_required = False
                
                # Set WALLET_ROOT if provided
                if wallet_root:
                    wallet_sql = f"ALTER SYSTEM SET WALLET_ROOT='{wallet_root}' SCOPE=SPFILE"
                    wallet_result = await db_handler.execute_sql(wallet_sql, "CDB$ROOT")
                    
                    steps.append({
                        "parameter": "WALLET_ROOT",
                        "value": wallet_root,
                        "scope": "SPFILE",
                        "success": wallet_result.get("success", False),
                        "requires_restart": True
                    })
                    
                    if wallet_result.get("success", False):
                        restart_required = True
                
                # Set TDE_CONFIGURATION if provided
                if tde_configuration:
                    # Check if current value requires restart
                    current_sql = "SELECT VALUE FROM V$PARAMETER WHERE NAME = 'tde_configuration'"
                    current_result = await db_handler.execute_sql(current_sql, "CDB$ROOT")
                    current_value = None
                    
                    if current_result["success"] and current_result["results"][0]["data"]:
                        current_value = current_result["results"][0]["data"][0]["VALUE"]
                    
                    if current_value != tde_configuration:
                        # Convert short format to full Oracle parameter format
                        full_tde_config = f"KEYSTORE_CONFIGURATION={tde_configuration}"
                        tde_sql = f"ALTER SYSTEM SET TDE_CONFIGURATION='{full_tde_config}' SCOPE=BOTH"
                        tde_result = await db_handler.execute_sql(tde_sql, "CDB$ROOT")
                        
                        steps.append({
                            "parameter": "TDE_CONFIGURATION",
                            "value": tde_configuration,
                            "previous_value": current_value,
                            "scope": "BOTH",
                            "success": tde_result.get("success", False)
                        })
                
                # Set ENCRYPT_NEW_TABLESPACES if provided
                if encrypt_new_tablespaces:
                    encrypt_sql = f"ALTER SYSTEM SET ENCRYPT_NEW_TABLESPACES={encrypt_new_tablespaces.upper()} SCOPE=BOTH"
                    encrypt_result = await db_handler.execute_sql(encrypt_sql, "CDB$ROOT")
                    
                    steps.append({
                        "parameter": "ENCRYPT_NEW_TABLESPACES",
                        "value": encrypt_new_tablespaces.upper(),
                        "scope": "BOTH",
                        "success": encrypt_result.get("success", False),
                        "requires_restart": False
                    })
                
                # Handle restart if required
                restart_performed = False
                if restart_required and force_restart:
                    logger.info("Performing database restart...")
                    
                    # Shutdown
                    shutdown_result = await db_handler.execute_sql("SHUTDOWN IMMEDIATE", "CDB$ROOT")
                    
                    # Startup
                    startup_result = await db_handler.execute_sql("STARTUP", "CDB$ROOT")
                    
                    # Open PDBs
                    if startup_result.get("success", False):
                        await db_handler.execute_sql("ALTER PLUGGABLE DATABASE ALL OPEN READ WRITE", "CDB$ROOT")
                    
                    restart_performed = startup_result.get("success", False)
                    
                    steps.append({
                        "action": "database_restart",
                        "shutdown_success": shutdown_result.get("success", False),
                        "startup_success": startup_result.get("success", False),
                        "restart_performed": restart_performed
                    })
                
                # Verify final configuration
                final_config = await db_handler.get_tde_configuration()
                
                result_data = {
                    "success": all(s.get("success", True) for s in steps if "success" in s),
                    "operation": "set_oracle_tde_parameters",
                    "connection": oracle_connection,
                    "parameters_set": {
                        "wallet_root": wallet_root,
                        "tde_configuration": tde_configuration,
                        "encrypt_new_tablespaces": encrypt_new_tablespaces
                    },
                    "steps": steps,
                    "restart_required": restart_required and not restart_performed,
                    "restart_performed": restart_performed,
                    "final_configuration": {
                        "wallet_root": final_config.get("wallet_root", {}).get("value"),
                        "tde_configuration": final_config.get("tde_configuration", {}).get("value"),
                        "encrypt_new_tablespaces": final_config.get("encrypt_new_tablespaces", {}).get("value")
                    },
                    "timestamp": datetime.now().isoformat()
                }
                
                if restart_required and not restart_performed:
                    result_data["restart_instructions"] = {
                        "required": True,
                        "reason": "WALLET_ROOT parameter change requires restart",
                        "commands": [
                            "sqlplus / as sysdba",
                            "SHUTDOWN IMMEDIATE;",
                            "STARTUP;",
                            "ALTER PLUGGABLE DATABASE ALL OPEN READ WRITE;",
                            "EXIT;"
                        ]
                    }
                
            elif operation == "verify":
                checks = []
                recommendations = []
                
                # Check 1: TDE parameters
                config = await db_handler.get_tde_configuration()
                
                wallet_root = config.get("wallet_root", {}).get("value")
                tde_config = config.get("tde_configuration", {}).get("value")
                encrypt_new = config.get("encrypt_new_tablespaces", {}).get("value")
                
                checks.append({
                    "check": "TDE Parameters",
                    "status": "CONFIGURED" if wallet_root and tde_config else "NOT_CONFIGURED",
                    "details": {
                        "wallet_root": wallet_root or "Not set",
                        "tde_configuration": tde_config or "Not set",
                        "encrypt_new_tablespaces": encrypt_new or "MANUAL"
                    }
                })
                
                if not wallet_root:
                    recommendations.append({
                        "priority": "HIGH",
                        "recommendation": "Set WALLET_ROOT parameter",
                        "command": "ALTER SYSTEM SET WALLET_ROOT='<path>' SCOPE=SPFILE"
                    })
                
                # Check 2: Wallet status
                wallet_status = await db_handler.get_wallet_status("v$", "CDB$ROOT")
                wallet_open = any(w["STATUS"] == "OPEN" for w in wallet_status)
                
                checks.append({
                    "check": "Wallet Status",
                    "status": "OPEN" if wallet_open else "CLOSED",
                    "details": wallet_status
                })
                
                if not wallet_open and wallet_root:
                    recommendations.append({
                        "priority": "HIGH",
                        "recommendation": "Open wallet or configure auto-login",
                        "command": 'ADMINISTER KEY MANAGEMENT SET KEYSTORE OPEN IDENTIFIED BY "<password>"'
                    })
                
                # Check 3: MEKs
                mek_sql = """
                SELECT 
                    COUNT(*) AS TOTAL_MEKS
                FROM V$ENCRYPTION_KEYS
                """
                
                mek_result = await db_handler.execute_sql(mek_sql, "CDB$ROOT")
                mek_stats = {"total": 0, "active": 0}
                
                if mek_result["success"] and mek_result["results"][0]["data"]:
                    row = mek_result["results"][0]["data"][0]
                    mek_stats = {
                        "total": row["TOTAL_MEKS"],
                        "active": row["TOTAL_MEKS"]  # In Oracle 21c, all keys are considered active
                    }
                
                checks.append({
                    "check": "Master Encryption Keys",
                    "status": "CONFIGURED" if mek_stats["active"] > 0 else "NOT_CONFIGURED",
                    "details": mek_stats
                })
                
                if mek_stats["active"] == 0:
                    recommendations.append({
                        "priority": "HIGH",
                        "recommendation": "Generate Master Encryption Key",
                        "command": 'ADMINISTER KEY MANAGEMENT SET KEY IDENTIFIED BY "<password>" WITH BACKUP'
                    })
                
                # Check 4: Encrypted tablespaces
                ts_sql = """
                SELECT 
                    (SELECT COUNT(*) FROM V$TABLESPACE vt
                     INNER JOIN V$CONTAINERS c ON vt.CON_ID = c.CON_ID
                     WHERE vt.NAME NOT IN ('SYSTEM', 'SYSAUX', 'TEMP', 'UNDOTBS1', 'UNDOTBS2', 'USERS')
                     AND vt.NAME NOT LIKE 'SYS%'
                     AND vt.NAME NOT LIKE 'AUX%'
                     AND vt.NAME NOT LIKE 'TEMP%'
                     AND vt.NAME NOT LIKE 'UNDO%'
                     AND vt.NAME NOT LIKE 'USERS%'
                     AND vt.NAME NOT LIKE 'PDB$SEED%'
                     AND c.OPEN_MODE = 'READ WRITE') AS TOTAL_TABLESPACES,
                    (SELECT COUNT(*) 
                     FROM V$TABLESPACE vt
                     INNER JOIN V$ENCRYPTED_TABLESPACES vet ON vt.TS# = vet.TS# AND vt.CON_ID = vet.CON_ID
                     INNER JOIN V$CONTAINERS c ON vt.CON_ID = c.CON_ID
                     WHERE vt.NAME NOT IN ('SYSTEM', 'SYSAUX', 'TEMP', 'UNDOTBS1', 'UNDOTBS2', 'USERS')
                     AND vt.NAME NOT LIKE 'SYS%'
                     AND vt.NAME NOT LIKE 'AUX%'
                     AND vt.NAME NOT LIKE 'TEMP%'
                     AND vt.NAME NOT LIKE 'UNDO%'
                     AND vt.NAME NOT LIKE 'USERS%'
                     AND vt.NAME NOT LIKE 'PDB$SEED%'
                     AND c.OPEN_MODE = 'READ WRITE') AS ENCRYPTED_TABLESPACES
                FROM DUAL
                """
                
                ts_result = await db_handler.execute_sql(ts_sql, "CDB$ROOT")
                ts_stats = {"total": 0, "encrypted": 0}
                
                if ts_result["success"] and ts_result["results"][0]["data"]:
                    row = ts_result["results"][0]["data"][0]
                    ts_stats = {
                        "total": row["TOTAL_TABLESPACES"],
                        "encrypted": row["ENCRYPTED_TABLESPACES"]
                    }
                
                checks.append({
                    "check": "Tablespace Encryption",
                    "status": f"{ts_stats['encrypted']}/{ts_stats['total']} encrypted",
                    "details": ts_stats
                })
                
                if ts_stats["encrypted"] < ts_stats["total"] and encrypt_new == "MANUAL":
                    recommendations.append({
                        "priority": "MEDIUM",
                        "recommendation": "Enable automatic tablespace encryption",
                        "command": "ALTER SYSTEM SET ENCRYPT_NEW_TABLESPACES=DDL SCOPE=BOTH"
                    })
                
                # Overall status
                tde_ready = (
                    wallet_root and 
                    tde_config and 
                    wallet_open and 
                    mek_stats["active"] > 0
                )
                
                result_data = {
                    "success": True,
                    "operation": "verify_oracle_tde_setup",
                    "connection": oracle_connection,
                    "tde_ready": tde_ready,
                    "checks": checks,
                    "recommendations": recommendations,
                    "summary": {
                        "parameters_configured": bool(wallet_root and tde_config),
                        "wallet_operational": wallet_open,
                        "meks_configured": mek_stats["active"] > 0,
                        "encryption_in_use": ts_stats["encrypted"] > 0
                    },
                    "next_steps": [r["recommendation"] for r in recommendations if r["priority"] == "HIGH"],
                    "timestamp": datetime.now().isoformat()
                }
            
            else:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid operation: {operation}. Must be 'get', 'set', or 'verify'"
                })

            logger.info(f"=== manage_oracle_configuration completed ===")
            return json.dumps(result_data, indent=2)
            
        except Exception as e:
            logger.error(f"Error in Oracle configuration management: {e}", exc_info=True)
            return json.dumps({
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }) 