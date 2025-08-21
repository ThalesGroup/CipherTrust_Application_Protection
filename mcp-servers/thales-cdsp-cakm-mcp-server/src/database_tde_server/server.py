"""
Main MCP server for Database TDE operations

This module implements the Model Context Protocol (MCP) server for Database Transparent
Data Encryption (TDE) operations. Database encryption and encryption key management are
handled by Thales CipherTrust Application Key Management (CAKM) connector, which is
integrated with Thales CDSP (CipherTrust Data Security Platform).

Provides the main entry point for the server and handles tool registration and execution.
"""
import asyncio
import logging
from mcp.server.fastmcp import FastMCP
from .tools import (
    register_connection_tools,
    register_security_tools,
    register_encryption_tools,
    register_key_management_tools,
    register_status_tools,
    register_oracle_wallet_tools,
    register_oracle_configuration_tools,
    register_oracle_tde_deployment_tools,
)
from .database_manager import DatabaseManager

logger = logging.getLogger(__name__)

def create_server() -> FastMCP:
    """Create and configure the Database TDE MCP server"""
    # Initialize the MCP server
    server = FastMCP("Database TDE MCP Server")
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    # Register common tools (works for both SQL Server and Oracle)
    register_connection_tools(server, db_manager)
    register_security_tools(server, db_manager)
    
    # Register unified tools (consolidated SQL and Oracle functionality)
    register_encryption_tools(server, db_manager)      # SQL + Oracle encryption/decryption
    register_key_management_tools(server, db_manager)  # SQL + Oracle key management
    register_status_tools(server, db_manager)          # SQL + Oracle monitoring
    register_oracle_wallet_tools(server, db_manager)   # Oracle TDE management
    register_oracle_configuration_tools(server, db_manager)   # Oracle TDE management
    register_oracle_tde_deployment_tools(server, db_manager)    # Oracle reliable TDE operations
    
    logger.info("Database TDE MCP Server initialized with consolidated unified tools")
    
    # Log available connections and their types
    connections = db_manager.config.connections
    sql_server_connections = [name for name, conn in connections.items() if conn.db_type.value == "sqlserver"]
    oracle_connections = [name for name, conn in connections.items() if conn.db_type.value == "oracle"]
    
    logger.info(f"SQL Server connections: {sql_server_connections}")
    logger.info(f"Oracle connections: {oracle_connections}")
    logger.info(f"Total connections loaded: {len(connections)}")
    
    return server

def main():
    """Main entry point for the Database TDE MCP Server"""
    import argparse
    import anyio

    parser = argparse.ArgumentParser(description="Database TDE MCP Server")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--test-connections", action="store_true", help="Test database connections and exit")
    
    args = parser.parse_args()
    
    if args.test_connections:
        # Test connections mode
        db_manager = DatabaseManager()
        print("Testing database connections...")
        for conn_name, conn in db_manager.config.connections.items():
            try:
                success = db_manager.test_connection(conn_name)
                db_type = conn.db_type.value
                status = "✅ SUCCESS" if success else "❌ FAILED"
                print(f"  {conn_name} ({db_type}): {status}")
            except Exception as e:
                print(f"  {conn_name}: ❌ ERROR - {e}")
        return
    
    # Normal server mode
    server = create_server()
    logger.info("Starting Database TDE MCP Server...")
    
    # Run the MCP server
    server.run()

if __name__ == "__main__":
    main()