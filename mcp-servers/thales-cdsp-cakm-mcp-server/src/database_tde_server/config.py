"""
Configuration management for Database TDE MCP Server

This module handles configuration loading and management for the Database Transparent Data Encryption (TDE)
server. Database encryption and encryption key management are handled by Thales CipherTrust Application
Key Management (CAKM) connector, which is integrated with Thales CDSP (CipherTrust Data Security Platform).

Provides configuration validation, environment variable handling, and connection parameter management.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Optional, List, Any
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from pydantic.json import pydantic_encoder

from .models import DatabaseConnection, DatabaseType, SSHConfig, OracleConfig

logger = logging.getLogger(__name__)


def find_env_file():
    """Find .env file in current directory or parent directories"""
    # Check current working directory
    current_dir = Path.cwd()
    env_path = current_dir / ".env"
    if env_path.exists():
        return str(env_path)
    
    # Check script directory (where the MCP server is installed)
    try:
        import database_tde_server
        module_dir = Path(database_tde_server.__file__).parent.parent.parent
        env_path = module_dir / ".env"
        if env_path.exists():
            return str(env_path)
    except:
        pass
    
    # Check common locations
    common_paths = [
        Path("C:/database-tde-mcp-server/.env"),
        Path.home() / "database-tde-mcp-server" / ".env",
        Path(__file__).parent.parent.parent / ".env"
    ]
    
    for path in common_paths:
        if path.exists():
            return str(path)
    
    return None



class DatabaseTDESettings(BaseSettings):
    server_name: str = Field(default="database-tde-mcp")
    log_level: str = Field(default="INFO")
    connection_timeout: int = Field(default=30)
    database_connections: List[Dict[str, Any]] = Field(default_factory=list)
    
    @validator('database_connections', pre=True)
    def parse_database_connections(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return []
        elif isinstance(v, list):
            # It's already a list, just return it
            return v
        return v if v else []
    
    class Config:
        env_prefix = "db_tde_"
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"
    
    @validator("log_level")
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return v.upper()
    
    def __init__(self, **values):
        # Log environment file location for debugging
        env_file = find_env_file()
        if env_file:
            logger.info(f"Loading configuration from: {env_file}")
        else:
            logger.warning("No .env file found, using environment variables or defaults")
        
        super().__init__(**values)


class ConfigurationManager:
    """Enhanced configuration manager with per-database SSH and Oracle settings"""
    
    def __init__(self, settings: Optional[DatabaseTDESettings] = None):
        self.settings = settings or DatabaseTDESettings()
        self.connections: Dict[str, DatabaseConnection] = {}
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, self.settings.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Load database connections
        self._load_connections()
        
        logger.info(f"Configuration loaded with {len(self.connections)} database connections")
    
    def _load_connections(self):
        """Load database connections from settings with enhanced SSH and Oracle configs"""
        if not self.settings.database_connections:
            logger.warning("No database connections configured")
            return
        
        try:
            connections_data = self.settings.database_connections

            if not isinstance(connections_data, list):
                raise ValueError("Database connections must be a list")
            
            for conn_data in connections_data:
                # Validate required fields
                if "name" not in conn_data:
                    logger.error("Connection missing 'name' field")
                    continue
                
                if "db_type" not in conn_data:
                    logger.error(f"Connection '{conn_data['name']}' missing 'db_type' field")
                    continue
                
                # Convert db_type string to enum
                try:
                    db_type = DatabaseType(conn_data["db_type"])
                except ValueError:
                    logger.error(f"Invalid db_type '{conn_data['db_type']}' for connection '{conn_data['name']}'")
                    continue
                
                # Parse SSH configuration if present
                ssh_config = None
                if "ssh_config" in conn_data and conn_data["ssh_config"]:
                    try:
                        ssh_config = SSHConfig(**conn_data["ssh_config"])
                        logger.info(f"Loaded SSH config for {conn_data['name']}: {ssh_config.host}:{ssh_config.port}")
                    except Exception as e:
                        logger.error(f"Error parsing SSH config for '{conn_data['name']}': {e}")
                
                # Parse Oracle configuration if present
                oracle_config = None
                if "oracle_config" in conn_data and conn_data["oracle_config"]:
                    try:
                        oracle_config_data = conn_data["oracle_config"].copy()
                        
                        # Auto-detect TNS_ADMIN if not specified
                        if "tns_admin" not in oracle_config_data and "oracle_home" in oracle_config_data:
                            oracle_config_data["tns_admin"] = f"{oracle_config_data['oracle_home']}/network/admin"
                            logger.info(f"Auto-detected TNS_ADMIN for {conn_data['name']}: {oracle_config_data['tns_admin']}")
                        
                        oracle_config = OracleConfig(**oracle_config_data)
                        logger.info(f"Loaded Oracle config for {conn_data['name']}: SID={oracle_config.oracle_sid}, HOME={oracle_config.oracle_home}")
                    except Exception as e:
                        logger.error(f"Error parsing Oracle config for '{conn_data['name']}': {e}")
                
                # Create connection object
                try:
                    connection = DatabaseConnection(
                        name=conn_data["name"],
                        db_type=db_type,
                        host=conn_data.get("host"),
                        port=conn_data.get("port"),
                        instance=conn_data.get("instance"),
                        database=conn_data.get("database"),
                        username=conn_data.get("username"),
                        password=conn_data.get("password"),
                        connection_string=conn_data.get("connection_string"),
                        driver=conn_data.get("driver"),
                        ssh_config=ssh_config,
                        oracle_config=oracle_config,
                        additional_params=conn_data.get("additional_params", {})
                    )
                    
                    self.connections[connection.name] = connection
                    logger.info(f"Loaded connection: {connection.name} ({connection.db_type.value})")
                    
                    # Log configuration details
                    if ssh_config:
                        logger.info(f"  SSH: {ssh_config.host}:{ssh_config.port} (user: {ssh_config.username})")
                    if oracle_config:
                        logger.info(f"  Oracle: SID={oracle_config.oracle_sid}, HOME={oracle_config.oracle_home}")
                    
                except Exception as e:
                    logger.error(f"Error creating connection '{conn_data['name']}': {e}")
                    
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse database connections JSON: {e}")
        except Exception as e:
            logger.error(f"Error loading database connections: {e}")
    
    def get_connection(self, name: str) -> Optional[DatabaseConnection]:
        """Get a database connection by name"""
        return self.connections.get(name)
    
    def get_ssh_config(self, connection_name: str) -> Optional[SSHConfig]:
        """Get SSH configuration for a specific database connection"""
        connection = self.get_connection(connection_name)
        return connection.ssh_config if connection else None
    
    def get_oracle_config(self, connection_name: str) -> Optional[OracleConfig]:
        """Get Oracle configuration for a specific database connection"""
        connection = self.get_connection(connection_name)
        return connection.oracle_config if connection else None
    
    def list_connections(self) -> Dict[str, DatabaseConnection]:
        """List all configured connections"""
        return self.connections.copy()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "server": {
                "name": self.settings.server_name,
                "log_level": self.settings.log_level
            },
            "connections": {
                name: json.loads(json.dumps(conn, default=pydantic_encoder))
                for name, conn in self.connections.items()
            }
        }


# Global configuration instance
_config: Optional[ConfigurationManager] = None


def get_config() -> ConfigurationManager:
    """Get or create the global configuration instance"""
    global _config
    if _config is None:
        _config = ConfigurationManager()
    return _config


def reset_config():
    """Reset the global configuration instance (useful for testing)"""
    global _config
    _config = None