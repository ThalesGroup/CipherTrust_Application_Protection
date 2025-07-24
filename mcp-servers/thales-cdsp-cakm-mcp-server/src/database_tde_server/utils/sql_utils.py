"""
SQL query building utilities for Database TDE operations
"""

import re
from typing import Dict, Any, List, Optional, Union
from ..models import DatabaseType

def escape_sql_identifier(identifier: str) -> str:
    """
    Escape SQL identifier (database, table, column name) for safe use in queries
    
    Args:
        identifier: SQL identifier to escape
        
    Returns:
        Escaped identifier wrapped in brackets (SQL Server) or quotes (Oracle)
    """
    # Remove any existing brackets and escape internal brackets
    clean_identifier = identifier.strip('[]"')
    escaped_identifier = clean_identifier.replace(']', ']]').replace('"', '""')
    return f'[{escaped_identifier}]'  # SQL Server style

def escape_oracle_identifier(identifier: str) -> str:
    """
    Escape Oracle identifier
    
    Args:
        identifier: Oracle identifier to escape
        
    Returns:
        Escaped identifier wrapped in quotes
    """
    clean_identifier = identifier.strip('"')
    escaped_identifier = clean_identifier.replace('"', '""')
    return f'"{escaped_identifier}"'

def format_algorithm_name(key_type: str, key_size: int) -> str:
    """
    Format algorithm name for SQL Server
    
    Args:
        key_type: Key type (RSA or AES)
        key_size: Key size in bits
        
    Returns:
        Formatted algorithm name (e.g., "RSA_2048", "AES_256")
    """
    return f"{key_type.upper()}_{key_size}"

def build_connection_string(
    db_type: DatabaseType,
    host: str,
    port: int,
    username: str,
    password: str,
    database: Optional[str] = None,
    instance: Optional[str] = None,
    driver: Optional[str] = None,
    **kwargs
) -> str:
    """
    Build database connection string
    
    Args:
        db_type: Database type
        host: Database host
        port: Database port
        username: Username
        password: Password
        database: Optional database name
        instance: Optional instance name (SQL Server) or service name (Oracle)
        driver: Optional driver name
        **kwargs: Additional connection parameters
        
    Returns:
        Connection string
    """
    if db_type == DatabaseType.SQLSERVER:
        driver = driver or "ODBC Driver 17 for SQL Server"
        server = f"{host},{port}"
        if instance:
            server = f"{host}\\{instance},{port}"
        
        conn_str = (f"DRIVER={{{driver}}};"
                   f"SERVER={server};"
                   f"UID={username};"
                   f"PWD={password};"
                   f"TrustServerCertificate=yes;")
        
        if database:
            conn_str += f"DATABASE={database};"
        
        # Add additional parameters
        for key, value in kwargs.items():
            conn_str += f"{key}={value};"
        
        return conn_str
    
    elif db_type == DatabaseType.ORACLE:
        # Oracle connection string formats
        if instance:
            # Use service name or SID
            dsn = f"{host}:{port}/{instance}"
        else:
            dsn = f"{host}:{port}"
        
        # Check for additional Oracle parameters
        service_name = kwargs.get("service_name")
        if service_name:
            dsn = f"{host}:{port}/{service_name}"
        
        # For oracledb library, we return the DSN
        # The actual connection will be made using oracledb.connect(user=, password=, dsn=)
        return dsn
    
    elif db_type == DatabaseType.MYSQL:
        # Future implementation
        conn_str = f"mysql+pymysql://{username}:{password}@{host}:{port}"
        if database:
            conn_str += f"/{database}"
        return conn_str
    
    elif db_type == DatabaseType.POSTGRESQL:
        # Future implementation
        conn_str = f"postgresql://{username}:{password}@{host}:{port}"
        if database:
            conn_str += f"/{database}"
        return conn_str
    
    else:
        raise ValueError(f"Unsupported database type: {db_type}")

class SQLQueryBuilder:
    """Utility class for building SQL queries"""
    
    @staticmethod
    def check_database_encryption(database_name: Optional[str] = None) -> str:
        """Build query to check database encryption status (SQL Server)"""
        base_query = """
        SELECT 
            d.name AS database_name,
            d.database_id,
            d.is_encrypted,
            e.encryption_state,
            CASE e.encryption_state
                WHEN 0 THEN 'No database encryption key present, no encryption'
                WHEN 1 THEN 'Unencrypted'
                WHEN 2 THEN 'Encryption in progress'
                WHEN 3 THEN 'Encrypted'
                WHEN 4 THEN 'Key change in progress'
                WHEN 5 THEN 'Decryption in progress'
            END AS encryption_state_desc,
            e.percent_complete,
            e.key_algorithm,
            e.key_length,
            c.name AS certificate_name,
            ak.name AS asymmetric_key_name
        FROM sys.databases AS d
        LEFT JOIN sys.dm_database_encryption_keys AS e
            ON d.database_id = e.database_id
        LEFT JOIN master.sys.certificates AS c
            ON e.encryptor_thumbprint = c.thumbprint
        LEFT JOIN master.sys.asymmetric_keys AS ak
            ON e.encryptor_thumbprint = ak.thumbprint
        """
        
        if database_name:
            base_query += f" WHERE d.name = {escape_sql_identifier(database_name)}"
        else:
            base_query += " WHERE d.name NOT IN ('master', 'tempdb', 'model', 'msdb')"
        
        base_query += " ORDER BY d.name"
        return base_query
    
    @staticmethod
    def list_cryptographic_providers() -> str:
        """Build query to list cryptographic providers (SQL Server)"""
        return """
        SELECT 
            name, 
            provider_id, 
            guid, 
            friendly_name, 
            authentication_type
        FROM sys.cryptographic_providers
        ORDER BY name
        """
    
    @staticmethod
    def list_asymmetric_keys() -> str:
        """Build query to list asymmetric keys (SQL Server)"""
        return """
        USE master;
        SELECT 
            name,
            algorithm_desc,
            key_length,
            string_sid,
            principal_id,
            thumbprint,
            create_date,
            modify_date
        FROM sys.asymmetric_keys
        ORDER BY name
        """
    
    @staticmethod
    def list_symmetric_keys() -> str:
        """Build query to list symmetric keys (SQL Server)"""
        return """
        USE master;
        SELECT 
            name,
            key_length,
            algorithm_desc,
            key_guid,
            create_date,
            modify_date
        FROM sys.symmetric_keys
        WHERE name != '##MS_ServiceMasterKey##'
        ORDER BY name
        """
    
    # SQL Server specific methods continue...
    # (keeping all existing SQL Server methods)
    
    @staticmethod
    def check_key_exists(key_name: str, is_asymmetric: bool) -> str:
        """Build query to check if key exists (SQL Server)"""
        table = "sys.asymmetric_keys" if is_asymmetric else "sys.symmetric_keys"
        return f"""
        USE master;
        SELECT name FROM {table} 
        WHERE name = {escape_sql_identifier(key_name)}
        """

class OracleQueryBuilder:
    """Utility class for building Oracle-specific queries"""
    
    @staticmethod
    def check_wallet_status() -> str:
        """Build query to check Oracle wallet status"""
        return """
        SELECT 
            CON_ID,
            WRL_TYPE,
            WRL_PARAMETER,
            STATUS,
            WALLET_TYPE,
            WALLET_ORDER,
            FULLY_BACKED_UP
        FROM V$ENCRYPTION_WALLET
        ORDER BY CON_ID
        """
    
    @staticmethod
    def list_encrypted_tablespaces() -> str:
        """Build query to list encrypted tablespaces"""
        return """
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
        WHERE vt.NAME NOT IN ('SYSTEM', 'SYSAUX', 'TEMP', 'UNDOTBS1', 'UNDOTBS2', 'USERS')
        AND vt.NAME NOT LIKE 'SYS%'
        AND vt.NAME NOT LIKE 'AUX%'
        AND vt.NAME NOT LIKE 'TEMP%'
        AND vt.NAME NOT LIKE 'UNDO%'
        AND vt.NAME NOT LIKE 'USERS%'
        AND vt.NAME NOT LIKE 'PDB$SEED%'
        AND c.OPEN_MODE = 'READ WRITE'
        ORDER BY c.NAME, vt.NAME
        """
    
    @staticmethod
    def list_master_encryption_keys() -> str:
        """Build query to list Oracle MEKs"""
        return """
        SELECT 
            TS#,
            MASTERKEYID_BASE64 AS KEY_ID,
            TAG,
            KEYVERSION,
            ACTIVATION_TIME,
            CREATOR,
            CREATOR_PDBNAME,
            ACTIVATING_PDBNAME,
            GLOBALLY_ACTIVATED
        FROM V$ENCRYPTION_KEYS
        ORDER BY ACTIVATION_TIME DESC
        """
    
    @staticmethod
    def list_containers() -> str:
        """Build query to list Oracle containers (PDBs)"""
        return """
        SELECT 
            CON_ID,
            NAME,
            OPEN_MODE,
            RESTRICTED,
            CREATION_TIME,
            TOTAL_SIZE
        FROM V$PDBS
        ORDER BY CON_ID
        """
    
    @staticmethod
    def check_tde_configuration() -> str:
        """Build query to check Oracle TDE configuration"""
        return """
        SELECT 
            NAME,
            VALUE,
            ISDEFAULT,
            ISMODIFIED
        FROM V$PARAMETER
        WHERE NAME IN ('wallet_root', 'encrypt_new_tablespaces', 'compatible')
        ORDER BY NAME
        """
    
    @staticmethod
    def generate_mek(wallet_password: str, backup_tag: str, container: str = "ALL") -> str:
        """Build command to generate Oracle MEK"""
        return f"""
        ADMINISTER KEY MANAGEMENT SET KEY
        IDENTIFIED BY "{wallet_password}"
        WITH BACKUP USING '{backup_tag}'
        CONTAINER = {container}
        """
    
    @staticmethod
    def open_wallet(wallet_password: Optional[str] = None) -> str:
        """Build command to open Oracle wallet"""
        if wallet_password:
            return f'ADMINISTER KEY MANAGEMENT SET KEYSTORE OPEN IDENTIFIED BY "{wallet_password}"'
        else:
            return "ADMINISTER KEY MANAGEMENT SET KEYSTORE OPEN"
    
    @staticmethod
    def close_wallet() -> str:
        """Build command to close Oracle wallet"""
        return "ADMINISTER KEY MANAGEMENT SET KEYSTORE CLOSE"
    
    @staticmethod
    def encrypt_tablespace(tablespace_name: str, online: bool = True) -> str:
        """Build command to encrypt Oracle tablespace"""
        method = "ONLINE" if online else "OFFLINE"
        
        if online:
            return f"""
            ALTER TABLESPACE {escape_oracle_identifier(tablespace_name)} 
            ENCRYPTION ONLINE 
            USING 'AES256' 
            ENCRYPT
            """
        else:
            return f"""
            ALTER TABLESPACE {escape_oracle_identifier(tablespace_name)} 
            ENCRYPTION OFFLINE 
            USING 'AES256' 
            ENCRYPT
            """