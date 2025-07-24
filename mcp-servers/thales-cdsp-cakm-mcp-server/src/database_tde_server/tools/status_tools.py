"""
Unified status and assessment tools for TDE and EKM.
"""
import json
import logging
from typing import Optional
from datetime import datetime

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

def register_status_tools(server: FastMCP, db_manager):
    """Register unified status and assessment tools with the MCP server"""
    
    @server.tool()
    async def status_tde_ekm(
        operation: str,
        connection_name: str,
        database_name: Optional[str] = None,
        format: str = "json",
        include_recommendations: bool = True,
        encrypted_only: bool = False
    ) -> str:
        """
        Get status, assessment, and compliance information for TDE and EKM objects.

        This tool provides a unified interface to monitor the health and configuration
        of Transparent Data Encryption across both SQL Server and Oracle databases.

        ---
        **SQL Server Operations:**
        - `assess_sql`: High-level encryption status for all databases.
        - `compliance_report`: Detailed, audit-ready report on keys, certs, and providers.
        - `best_practices`: Validates the setup against security best practices.
        - `export_config`: Exports a full JSON representation of the TDE configuration.
        - `validate_setup`: Performs a deep validation of the TDE chain for a single database.

        **Oracle Operations:**
        - `assess_oracle`: Comprehensive assessment of wallet, keys, and encrypted tablespaces.
        - `list_containers`: Lists all Pluggable Databases (PDBs) and the root container.
        - `list_tablespaces`: Lists tablespaces, with optional filtering by container and encryption status.
        ---

        Args:
            operation: The monitoring operation to perform (see descriptions above).
            connection_name: The name of the database connection to use.
            database_name: The name of the database (for 'validate_setup') or Oracle container (for 'list_tablespaces').
            format: The output format for reports (e.g., "json").
            include_recommendations: (SQL Server) If true, includes recommendations in 'best_practices' checks.
            encrypted_only: (Oracle) If true, 'list_tablespaces' will only return encrypted tablespaces.

        Returns:
            A JSON string containing the results of the monitoring operation.
        """
        try:
            db_handler = db_manager.get_database_handler(connection_name)
            
            # SQL Server Operations
            if db_handler.db_type == "sqlserver":
                if operation == "assess_sql":
                    status = await db_handler.check_encryption_status()
                    return json.dumps({
                        "success": True, "operation": "assess_sql",
                        "connection": connection_name, "database_status": status,
                        "timestamp": datetime.now().isoformat()
                    }, indent=2, default=str)
                
                elif operation == "compliance_report":
                    report = await db_handler.get_tde_compliance_data()
                    return json.dumps(report, indent=2, default=str)

                elif operation == "best_practices":
                    results = await db_handler.check_best_practices(include_recommendations=include_recommendations)
                    return json.dumps(results, indent=2, default=str)

                elif operation == "export_config":
                    config = await db_handler.export_tde_configuration()
                    return json.dumps(config, indent=2, default=str)

                elif operation == "validate_setup":
                    if not database_name:
                        return json.dumps({"success": False, "error": "database_name is required for 'validate_setup'"})
                    validation = await db_handler.validate_tde_setup(database_name)
                    return json.dumps(validation, indent=2, default=str)
                
                else:
                    return json.dumps({"success": False, "error": f"Invalid operation '{operation}' for SQL Server."})
            
            # Oracle Operations
            elif db_handler.db_type == "oracle":
                if operation == "assess_oracle":
                    assessment = await db_handler.assess_tde_comprehensive()
                    return json.dumps(assessment, indent=2, default=str)

                elif operation == "list_containers":
                    containers = await db_handler.list_databases()
                    return json.dumps({
                        "success": True, "operation": "list_containers",
                        "connection": connection_name, "containers": containers,
                        "timestamp": datetime.now().isoformat()
                    }, indent=2, default=str)

                elif operation == "list_tablespaces":
                    tablespaces = await db_handler.list_tablespaces(database_name, encrypted_only)
                    return json.dumps({
                        "success": True, "operation": "list_tablespaces",
                        "connection": connection_name, "container": database_name or "ALL",
                        "tablespaces": tablespaces, "timestamp": datetime.now().isoformat()
                    }, indent=2, default=str)
                
                else:
                    return json.dumps({"success": False, "error": f"Invalid operation '{operation}' for Oracle."})
            
            else:
                return json.dumps({"success": False, "error": f"Unsupported database type: {db_handler.db_type}"})

        except Exception as e:
            logger.error(f"Error in status_tde_ekm: {e}", exc_info=True)
            return json.dumps({"success": False, "error": str(e), "error_type": type(e).__name__}) 