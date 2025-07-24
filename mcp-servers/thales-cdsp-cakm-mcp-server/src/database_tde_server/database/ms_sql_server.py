"""
SQL Server implementation for TDE operations
"""

import pyodbc
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from .base import DatabaseInterface
from ..models import DatabaseConnection, EncryptionStatusInfo
from ..utils.exceptions import DatabaseConnectionError, TDEOperationError

logger = logging.getLogger(__name__)

class MSSQLServerDatabase(DatabaseInterface):
    """SQL Server implementation of TDE operations"""
    db_type = "sqlserver"

    def __init__(self, connection: DatabaseConnection, connection_timeout: int = 30):
        super().__init__(connection)
        self.connection_timeout = connection_timeout

    def _get_connection_string(self, database: Optional[str] = None) -> str:
        """Generate SQL Server connection string"""
        if self.connection.connection_string:
            conn_str = self.connection.connection_string
            if database:
                # Add or replace database in connection string
                if "DATABASE=" in conn_str:
                    # Replace existing database
                    import re
                    conn_str = re.sub(r'DATABASE=[^;]*;?', f'DATABASE={database};', conn_str)
                else:
                    # Add database
                    conn_str += f"DATABASE={database};"
            return conn_str

        driver = self.connection.driver or "ODBC Driver 17 for SQL Server"
        server = f"{self.connection.host},{self.connection.port}"
        if self.connection.instance:
            server = f"{self.connection.host}\\{self.connection.instance},{self.connection.port}"

        conn_str = (f"DRIVER={{{driver}}};"
                   f"SERVER={server};"
                   f"UID={self.connection.username};"
                   f"PWD={self.connection.password};"
                   f"TrustServerCertificate=yes;")

        if database:
            conn_str += f"DATABASE={database};"

        return conn_str

    async def connect(self) -> bool:
        """Test database connectivity"""
        try:
            conn_string = self._get_connection_string()
            with pyodbc.connect(conn_string, timeout=self.connection_timeout):
                return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    async def execute_sql(self, sql: str, database: Optional[str] = None) -> Dict[str, Any]:
        """Execute SQL command on SQL Server"""
        try:
            conn_string = self._get_connection_string(database)
        
            # Normalize SQL for checking
            sql_stripped = sql.strip()
            sql_upper = sql_stripped.upper()
        
            # Commands that need autocommit anywhere in the batch
            autocommit_commands = [
                'ALTER DATABASE',
                'CREATE ASYMMETRIC KEY',
                'CREATE SYMMETRIC KEY',
                'CREATE CREDENTIAL',
                'CREATE LOGIN',
                'ALTER LOGIN',
                'ALTER CREDENTIAL',
                'DROP CREDENTIAL',
                'CREATE DATABASE ENCRYPTION KEY',
                'ALTER DATABASE ENCRYPTION KEY'
            ]
        
            # Turn on autocommit if any of those commands appear
            needs_autocommit = any(cmd in sql_upper for cmd in autocommit_commands)
        
            if needs_autocommit:
                # Run entire batch in autocommit mode
                with pyodbc.connect(conn_string, timeout=self.connection_timeout, autocommit=True) as conn:
                    cursor = conn.cursor()
                    # Split into batches on GO
                    batches = [batch.strip() for batch in sql_stripped.split('\nGO\n') if batch.strip()]
                    for batch in batches:
                        cursor.execute(batch)
                    return {"success": True, "results": [{"rows_affected": cursor.rowcount}]}
        
            # Regular (transactional) execution
            with pyodbc.connect(conn_string, timeout=self.connection_timeout) as conn:
                cursor = conn.cursor()
            
                # Split into batches on GO
                statements = [stmt.strip() for stmt in sql_stripped.split('\nGO\n') if stmt.strip()]
                results = []
            
                for statement in statements:
                    cursor.execute(statement)
                
                    # If it's a SELECT-like statement, fetch rows
                    stmt_upper = statement.upper()
                    if stmt_upper.startswith(('SELECT', 'SHOW', 'DESCRIBE')):
                        if cursor.description:
                            columns = [col[0] for col in cursor.description]
                            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
                            results.append({"data": rows, "row_count": len(rows)})
                        else:
                            results.append({"data": [], "row_count": 0})
                    else:
                        conn.commit()
                        results.append({"rows_affected": cursor.rowcount})
            
                return {"success": True, "results": results}
    
        except Exception as e:
            logger.error(f"SQL execution error: {e}")
            logger.error(f"Failed SQL: {sql}")
            return {"success": False, "error": str(e)}

    async def check_encryption_status(self, database_name: Optional[str] = None) -> List[EncryptionStatusInfo]:
        """Check encryption status of SQL Server databases"""
        sql_query = """
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
            COALESCE(ak.name, cert.name) AS encryptor_name,
            CASE
                WHEN ak.name IS NOT NULL THEN 'ASYMMETRIC KEY'
                WHEN cert.name IS NOT NULL THEN 'CERTIFICATE'
                ELSE NULL
            END AS encryptor_type
        FROM sys.databases AS d
        LEFT JOIN sys.dm_database_encryption_keys AS e
            ON d.database_id = e.database_id
        LEFT JOIN master.sys.asymmetric_keys AS ak
            ON e.encryptor_thumbprint = ak.thumbprint
        LEFT JOIN master.sys.certificates AS cert
            ON e.encryptor_thumbprint = cert.thumbprint
        """

        if database_name:
            sql_query += f" WHERE d.name = '{database_name}'"
        else:
            sql_query += " WHERE d.name NOT IN ('master', 'tempdb', 'model', 'msdb')"

        sql_query += " ORDER BY d.name"

        result = await self.execute_sql(sql_query)

        if result["success"]:
            encryption_status = []
            for row in result["results"][0]["data"]:
                status = EncryptionStatusInfo(
                    database_name=row["database_name"],
                    database_id=row["database_id"],
                    is_encrypted=bool(row["is_encrypted"]),
                    encryption_state=row["encryption_state"],
                    encryption_state_desc=row["encryption_state_desc"],
                    percent_complete=row["percent_complete"],
                    key_algorithm=row["key_algorithm"],
                    key_length=row["key_length"],
                    encryptor_name=row["encryptor_name"],
                    encryptor_type=row["encryptor_type"]
                )
                encryption_status.append(status)
            return encryption_status
        else:
            raise TDEOperationError(f"Failed to check encryption status: {result['error']}")

    async def list_cryptographic_providers(self) -> List[Dict[str, Any]]:
        """List cryptographic providers on SQL Server"""
        provider_sql = """
        SELECT name, provider_id, guid, version, dll_path, is_enabled
        FROM sys.cryptographic_providers
        ORDER BY name
        """

        result = await self.execute_sql(provider_sql)

        if result["success"]:
            return result["results"][0]["data"]
        else:
            raise TDEOperationError(f"Failed to list providers: {result['error']}")

    async def list_master_keys(self, key_type: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """List master keys on SQL Server"""
        results = {"asymmetric_keys": [], "symmetric_keys": []}

        # Get asymmetric keys
        if not key_type or key_type.upper() == "RSA":
            asymmetric_sql = """
            SELECT
                name,
                algorithm_desc,
                key_length
            FROM master.sys.asymmetric_keys
            ORDER BY name
            """

            try:
                asym_result = await self.execute_sql(asymmetric_sql)
                if asym_result.get("success") and asym_result.get("results") and len(asym_result["results"]) > 0:
                    results["asymmetric_keys"] = asym_result["results"][0].get("data", [])
            except Exception as e:
                logger.warning(f"Failed to list asymmetric keys: {e}")

        # Get symmetric keys  
        if not key_type or key_type.upper() == "AES":
            symmetric_sql = """
            SELECT
                name,
                key_length,
                algorithm_desc
            FROM master.sys.symmetric_keys
            WHERE name != '##MS_ServiceMasterKey##'
            AND name != '##MS_DatabaseMasterKey##'
            ORDER BY name
            """

            try:
                sym_result = await self.execute_sql(symmetric_sql)
                if sym_result.get("success") and sym_result.get("results") and len(sym_result["results"]) > 0:
                    results["symmetric_keys"] = sym_result["results"][0].get("data", [])
            except Exception as e:
                logger.warning(f"Failed to list symmetric keys: {e}")

        return results

    async def list_databases(self) -> List[Dict[str, Any]]:
        """List all databases on SQL Server"""
        databases_sql = """
        SELECT 
            name AS database_name,
            database_id,
            CONVERT(VARCHAR, create_date, 120) AS create_date,
            collation_name,
            state_desc,
            recovery_model_desc,
            compatibility_level,
            is_read_only,
            is_auto_close_on,
            is_auto_shrink_on,
            page_verify_option_desc
        FROM sys.databases
        ORDER BY name
        """
        
        result = await self.execute_sql(databases_sql)
        
        if result["success"]:
            return result["results"][0]["data"]
        else:
            raise TDEOperationError(f"Failed to list databases: {result['error']}")

    async def create_master_key_only(
        self,
        key_name: str,
        provider_name: str,
        key_size: int,
        key_type: str
    ) -> Dict[str, Any]:
        """Create only the master key without credentials or logins"""
        
        results = []
        algorithm, is_asymmetric = self.parse_key_algorithm(key_type, key_size)
        
        # Check if key already exists
        key_table = "master.sys.asymmetric_keys" if is_asymmetric else "master.sys.symmetric_keys"
        key_check_sql = f"""
        SELECT name FROM {key_table} WHERE name = '{key_name}'
        """
        
        key_exists_result = await self.execute_sql(key_check_sql)
        key_exists = False
        if key_exists_result.get("success") and key_exists_result.get("results"):
            if len(key_exists_result["results"]) > 0 and key_exists_result["results"][0].get("data"):
                key_exists = len(key_exists_result["results"][0]["data"]) > 0
        
        if key_exists:
            return {
                "success": False,
                "error": f"{key_type} key '{key_name}' already exists",
                "key_existed": True
            }
        
        # Check if provider exists
        provider_check_sql = f"""
        SELECT name FROM sys.cryptographic_providers WHERE name = '{provider_name}'
        """
        provider_result = await self.execute_sql(provider_check_sql)
        provider_exists = False
        if provider_result.get("success") and provider_result.get("results"):
            if len(provider_result["results"]) > 0 and provider_result["results"][0].get("data"):
                provider_exists = len(provider_result["results"][0]["data"]) > 0
        
        if not provider_exists:
            return {
                "success": False,
                "error": f"Cryptographic provider '{provider_name}' not found"
            }
        
        # Create the key
        key_creation_type = "ASYMMETRIC" if is_asymmetric else "SYMMETRIC"
        create_key_sql = f"""
        USE master;
        CREATE {key_creation_type} KEY [{key_name}]
        FROM PROVIDER [{provider_name}]
        WITH ALGORITHM = {algorithm},
        PROVIDER_KEY_NAME = '{key_name}',
        CREATION_DISPOSITION = CREATE_NEW;
        """
        
        key_creation_result = await self.execute_sql(create_key_sql)
        results.append({"step": f"create_{key_creation_type.lower()}_key", "result": key_creation_result})
        
        # Add a small delay to ensure key is committed
        await asyncio.sleep(0.1)
        
        return {
            "success": key_creation_result.get("success", False),
            "key_name": key_name,
            "algorithm": algorithm,
            "is_asymmetric": is_asymmetric,
            "provider": provider_name,
            "steps": results
        }

    async def create_tde_infrastructure(
        self,
        key_name: str,
        provider_name: str,
        ciphertrust_username: str,
        ciphertrust_password: str,
        ciphertrust_domain: str,
        key_size: int,
        key_type: str
    ) -> Dict[str, Any]:
        """Create TDE infrastructure for SQL Server"""

        results = []
        algorithm, is_asymmetric = self.parse_key_algorithm(key_type, key_size)

        # Check if key already exists
        key_table = "master.sys.asymmetric_keys" if is_asymmetric else "master.sys.symmetric_keys"
        key_check_sql = f"""
        SELECT name FROM {key_table} WHERE name = '{key_name}'
        """

        key_exists_result = await self.execute_sql(key_check_sql)
        key_exists = False
        if key_exists_result.get("success") and key_exists_result.get("results"):
            if len(key_exists_result["results"]) > 0 and key_exists_result["results"][0].get("data"):
                key_exists = len(key_exists_result["results"][0]["data"]) > 0

        # Always need to ensure credentials exist, even if key exists
        identity = f"{ciphertrust_domain}||{ciphertrust_username}" if ciphertrust_domain != "root" else ciphertrust_username
        
        # Step 1: Handle master credential (per provider + user)
        master_credential_name = f"{provider_name}_{ciphertrust_username}_master_cred"
        
        # Check if master credential exists
        check_master_cred_sql = f"""
        SELECT name FROM master.sys.credentials WHERE name = '{master_credential_name}'
        """
        master_cred_result = await self.execute_sql(check_master_cred_sql)
        master_cred_exists = False
        if master_cred_result.get("success") and master_cred_result.get("results"):
            if len(master_cred_result["results"]) > 0 and master_cred_result["results"][0].get("data"):
                master_cred_exists = len(master_cred_result["results"][0]["data"]) > 0
        
        if not master_cred_exists:
            # Create master credential
            create_credential_sql = f"""
            CREATE CREDENTIAL [{master_credential_name}]
            WITH IDENTITY = '{identity}',
            SECRET = '{ciphertrust_password}'
            FOR CRYPTOGRAPHIC PROVIDER [{provider_name}];
            """
            credential_result = await self.execute_sql(create_credential_sql)
            results.append({"step": "create_master_credential", "credential_name": master_credential_name, "result": credential_result})
        else:
            results.append({"step": "master_credential_exists", "credential_name": master_credential_name, "message": "Using existing master credential"})

        # Step 2: Map master credential to current login (check if already mapped)
        check_mapping_sql = f"""
        SELECT 
            c.name as credential_name,
            c.credential_identity,
            cp.name as provider_name
        FROM sys.server_principal_credentials pc
        JOIN sys.server_principals p ON pc.principal_id = p.principal_id
        JOIN sys.credentials c ON pc.credential_id = c.credential_id
        LEFT JOIN sys.cryptographic_providers cp ON c.target_id = cp.provider_id
        WHERE p.name = '{self.connection.username}' 
        AND c.name LIKE '{provider_name}%_master_cred'
        """
        mapping_result = await self.execute_sql(check_mapping_sql)
        existing_master_cred = None
        if mapping_result.get("success") and mapping_result.get("results"):
            if len(mapping_result["results"]) > 0 and mapping_result["results"][0].get("data"):
                if len(mapping_result["results"][0]["data"]) > 0:
                    existing_master_cred = mapping_result["results"][0]["data"][0]["credential_name"]

        if existing_master_cred and existing_master_cred != master_credential_name:
            # Login already has a different master credential for this provider
            error_msg = (f"SQL login '{self.connection.username}' already has master credential "
                        f"'{existing_master_cred}' mapped for provider '{provider_name}'. "
                        f"Cannot map new credential '{master_credential_name}'. "
                        f"To use different CipherTrust users, update the SQL login in your .env file "
                        f"or use the 'update_credential' tool to update the existing credential's password.")
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "existing_credential": existing_master_cred,
                "attempted_credential": master_credential_name
            }

        if not existing_master_cred:
            # No master credential mapped yet, so map it
            map_credential_sql = f"""
            ALTER LOGIN [{self.connection.username}] ADD CREDENTIAL [{master_credential_name}];
            """
            map_result = await self.execute_sql(map_credential_sql)
            results.append({"step": "map_credential_to_login", "result": map_result})
        else:
            results.append({"step": "credential_mapping_exists", "message": f"Credential already mapped to login {self.connection.username}"})

        # Step 3: Create key if it doesn't exist
        if not key_exists:
            # Create asymmetric/symmetric key
            key_creation_type = "ASYMMETRIC" if is_asymmetric else "SYMMETRIC"
            create_key_sql = f"""
            USE master;
            CREATE {key_creation_type} KEY [{key_name}]
            FROM PROVIDER [{provider_name}]
            WITH ALGORITHM = {algorithm},
            PROVIDER_KEY_NAME = '{key_name}',
            CREATION_DISPOSITION = CREATE_NEW;
            """

            key_creation_result = await self.execute_sql(create_key_sql)
            results.append({"step": f"create_{key_creation_type.lower()}_key", "result": key_creation_result})

            # Step 4: Create TDE login from asymmetric key (only for asymmetric keys)
            if is_asymmetric:
                tde_login_name = f"TDE_Login_{key_name}"
                
                # Check if login already exists
                check_login_sql = f"SELECT name FROM sys.server_principals WHERE name = '{tde_login_name}'"
                login_exists = await self.execute_sql(check_login_sql)
                
                if not (login_exists["success"] and login_exists["results"][0]["data"]):
                    create_tde_login_sql = f"""
                    CREATE LOGIN [{tde_login_name}] FROM ASYMMETRIC KEY [{key_name}];
                    """
                    
                    tde_login_result = await self.execute_sql(create_tde_login_sql)
                    results.append({"step": "create_tde_login", "login_name": tde_login_name, "result": tde_login_result})
                else:
                    results.append({"step": "tde_login_exists", "message": f"TDE login '{tde_login_name}' already exists"})
        else:
            results.append({"step": "key_exists", "message": f"Key '{key_name}' already exists"})

        # Step 5: Handle TDE credential for asymmetric keys (even if key existed)
        if is_asymmetric:
            tde_login_name = f"TDE_Login_{key_name}"
            tde_credential_name = f"{provider_name}_{ciphertrust_username}_{tde_login_name}_cred"
            
            # Check if TDE credential exists
            check_tde_cred_sql = f"""
            SELECT name FROM master.sys.credentials WHERE name = '{tde_credential_name}'
            """
            tde_cred_result = await self.execute_sql(check_tde_cred_sql)
            tde_cred_exists = False
            if tde_cred_result.get("success") and tde_cred_result.get("results"):
                if len(tde_cred_result["results"]) > 0 and tde_cred_result["results"][0].get("data"):
                    tde_cred_exists = len(tde_cred_result["results"][0]["data"]) > 0
            
            if not tde_cred_exists:
                create_tde_credential_sql = f"""
                CREATE CREDENTIAL [{tde_credential_name}]
                WITH IDENTITY = '{identity}',
                SECRET = '{ciphertrust_password}'
                FOR CRYPTOGRAPHIC PROVIDER [{provider_name}];
                """
                
                tde_credential_result = await self.execute_sql(create_tde_credential_sql)
                results.append({"step": "create_tde_credential", "credential_name": tde_credential_name, "result": tde_credential_result})
            else:
                results.append({"step": "tde_credential_exists", "credential_name": tde_credential_name, "message": "Using existing TDE credential"})
            
            # Step 6: Map TDE credential to TDE login (check if already mapped)
            check_tde_mapping_sql = f"""
            SELECT 1 
            FROM sys.server_principal_credentials pc
            JOIN sys.server_principals p ON pc.principal_id = p.principal_id
            JOIN sys.credentials c ON pc.credential_id = c.credential_id
            WHERE p.name = '{tde_login_name}' AND c.name = '{tde_credential_name}'
            """
            tde_mapping_result = await self.execute_sql(check_tde_mapping_sql)
            tde_mapping_exists = False
            if tde_mapping_result.get("success") and tde_mapping_result.get("results"):
                if len(tde_mapping_result["results"]) > 0 and tde_mapping_result["results"][0].get("data"):
                    tde_mapping_exists = len(tde_mapping_result["results"][0]["data"]) > 0
            
            if not tde_mapping_exists:
                map_tde_credential_sql = f"""
                ALTER LOGIN [{tde_login_name}] ADD CREDENTIAL [{tde_credential_name}];
                """
                
                map_tde_result = await self.execute_sql(map_tde_credential_sql)
                results.append({"step": "map_tde_credential_to_tde_login", "result": map_tde_result})
            else:
                results.append({"step": "tde_credential_mapping_exists", "message": f"TDE credential already mapped to {tde_login_name}"})

        return {
            "success": True,
            "key_existed": key_exists,
            "algorithm": algorithm,
            "is_asymmetric": is_asymmetric,
            "master_credential": master_credential_name,
            "tde_credential": f"{provider_name}_{ciphertrust_username}_TDE_Login_{key_name}_cred" if is_asymmetric else None,
            "steps": results
        }

    async def encrypt_database(
        self,
        database_name: str,
        key_name: str,
        is_asymmetric: bool
    ) -> Dict[str, Any]:
        """Encrypt a database with TDE"""

        results = []

        # Create Database Encryption Key
        key_reference = "ASYMMETRIC" if is_asymmetric else "SYMMETRIC"
        create_dek_sql = f"""
        USE [{database_name}];
        CREATE DATABASE ENCRYPTION KEY
        WITH ALGORITHM = AES_256
        ENCRYPTION BY SERVER {key_reference} KEY [{key_name}];
        """

        dek_result = await self.execute_sql(create_dek_sql)
        results.append({"step": "create_database_encryption_key", "result": dek_result})
        
        if not dek_result.get("success", False):
            return {
                "success": False,
                "error": f"Failed to create Database Encryption Key for '{database_name}': {dek_result.get('error')}",
                "steps": results
            }

        # Enable TDE (must be run separately due to transaction restrictions)
        enable_tde_sql = f"ALTER DATABASE [{database_name}] SET ENCRYPTION ON"

        tde_result = await self.execute_sql(enable_tde_sql)
        results.append({"step": "enable_tde", "result": tde_result})

        if not tde_result.get("success", False):
            return {
                "success": False,
                "error": f"Failed to enable TDE for '{database_name}': {tde_result.get('error')}",
                "steps": results
            }

        return {
            "success": True,
            "steps": results
        }

    async def rotate_database_encryption_key(
        self,
        database_name: str,
        algorithm: Optional[str] = None
    ) -> Dict[str, Any]:
        """Rotate database encryption key for SQL Server"""

        # Get current DEK algorithm if not specified
        if not algorithm:
            current_dek_sql = f"""
            SELECT key_algorithm, key_length
            FROM sys.dm_database_encryption_keys
            WHERE database_id = DB_ID('{database_name}')
            """

            current_result = await self.execute_sql(current_dek_sql)

            if not current_result["success"] or not current_result["results"][0]["data"]:
                raise TDEOperationError(f"No encryption key found for database '{database_name}'")

            current_dek = current_result["results"][0]["data"][0]
            algorithm = f"{current_dek['key_algorithm']}_{current_dek['key_length']}"

        # Rotate the DEK
        rotate_dek_sql = f"""
        USE [{database_name}];
        ALTER DATABASE ENCRYPTION KEY
        REGENERATE WITH ALGORITHM = {algorithm};
        """

        rotation_result = await self.execute_sql(rotate_dek_sql)

        return {
            "success": True,
            "algorithm_used": algorithm,
            "rotation_result": rotation_result
        }

    async def rotate_master_key(
        self,
        database_name: str,
        new_key_name: str,
        provider_name: str,
        ciphertrust_username: str,
        ciphertrust_password: str,
        ciphertrust_domain: str,
        key_size: int,
        key_type: str
    ) -> Dict[str, Any]:
        """Rotate master key for SQL Server"""

        results = []

        # Create new master key infrastructure
        infrastructure_result = await self.create_tde_infrastructure(
            new_key_name, provider_name, ciphertrust_username,
            ciphertrust_password, ciphertrust_domain, key_size, key_type
        )
        results.append({"step": "create_new_infrastructure", "result": infrastructure_result})

        # Rotate to new master key
        key_reference = "ASYMMETRIC" if infrastructure_result["is_asymmetric"] else "SYMMETRIC"
        rotate_master_sql = f"""
        USE [{database_name}];
        ALTER DATABASE ENCRYPTION KEY
        ENCRYPTION BY SERVER {key_reference} KEY [{new_key_name}];
        """

        rotation_result = await self.execute_sql(rotate_master_sql)
        results.append({"step": "rotate_to_new_master_key", "result": rotation_result})

        return {
            "success": True,
            "new_key_name": new_key_name,
            "algorithm": infrastructure_result["algorithm"],
            "steps": results
        }
    
    async def drop_master_key(
        self,
        key_name: str,
        key_type: str,
        force: bool = False,
        remove_from_provider: bool = False
    ) -> Dict[str, Any]:
        """Drop a master key from SQL Server"""
        
        results = []
        algorithm, is_asymmetric = self.parse_key_algorithm(key_type, 2048)  # Size doesn't matter for drop
        
        # Check if key exists
        key_table = "master.sys.asymmetric_keys" if is_asymmetric else "master.sys.symmetric_keys"
        key_check_sql = f"""
        SELECT name FROM {key_table} WHERE name = '{key_name}'
        """
        
        key_exists_result = await self.execute_sql(key_check_sql)
        if not (key_exists_result.get("success") and key_exists_result.get("results") 
                and key_exists_result["results"][0].get("data")):
            return {
                "success": False,
                "error": f"{key_type} key '{key_name}' not found"
            }
        
        # Check if key is being used by any databases
        usage_check_sql = f"""
        SELECT 
            db.name as database_name,
            dek.encryption_state,
            CASE 
                WHEN ak.name IS NOT NULL THEN 'ASYMMETRIC'
                WHEN sk.name IS NOT NULL THEN 'SYMMETRIC'
            END as key_type
        FROM sys.dm_database_encryption_keys dek
        INNER JOIN sys.databases db ON dek.database_id = db.database_id
        LEFT JOIN master.sys.asymmetric_keys ak ON dek.encryptor_thumbprint = ak.thumbprint
        LEFT JOIN master.sys.symmetric_keys sk ON dek.encryptor_thumbprint = sk.key_guid
        WHERE ak.name = '{key_name}' OR sk.name = '{key_name}'
        """
        
        usage_result = await self.execute_sql(usage_check_sql)
        databases_using_key = []
        
        if usage_result["success"] and usage_result["results"][0]["data"]:
            databases_using_key = [row["database_name"] for row in usage_result["results"][0]["data"]]
        
        if databases_using_key and not force:
            return {
                "success": False,
                "error": f"Key '{key_name}' is being used by databases: {', '.join(databases_using_key)}. Use force=true to drop anyway.",
                "databases_using_key": databases_using_key
            }
        
        # If asymmetric key, check for associated TDE login
        tde_login_dropped = False
        if is_asymmetric:
            tde_login_name = f"TDE_Login_{key_name}"
            
            # Check if TDE login exists
            login_check_sql = f"""
            SELECT name FROM sys.server_principals WHERE name = '{tde_login_name}'
            """
            login_result = await self.execute_sql(login_check_sql)
            
            if login_result["success"] and login_result["results"][0]["data"]:
                # Check for credential mappings
                cred_check_sql = f"""
                SELECT c.name as credential_name
                FROM sys.server_principal_credentials pc
                JOIN sys.server_principals p ON pc.principal_id = p.principal_id
                JOIN sys.credentials c ON pc.credential_id = c.credential_id
                WHERE p.name = '{tde_login_name}'
                """
                
                cred_result = await self.execute_sql(cred_check_sql)
                
                if cred_result["success"] and cred_result["results"][0]["data"]:
                    # Remove credential mappings
                    for row in cred_result["results"][0]["data"]:
                        cred_name = row["credential_name"]
                        unmap_sql = f"ALTER LOGIN [{tde_login_name}] DROP CREDENTIAL [{cred_name}]"
                        unmap_result = await self.execute_sql(unmap_sql)
                        results.append({
                            "step": "remove_credential_mapping",
                            "login": tde_login_name,
                            "credential": cred_name,
                            "result": unmap_result
                        })
                
                # Drop the TDE login
                drop_login_sql = f"DROP LOGIN [{tde_login_name}]"
                drop_login_result = await self.execute_sql(drop_login_sql)
                results.append({
                    "step": "drop_tde_login",
                    "login": tde_login_name,
                    "result": drop_login_result
                })
                tde_login_dropped = True
        
        # Drop the key
        key_type_sql = "ASYMMETRIC" if is_asymmetric else "SYMMETRIC"
        
        if remove_from_provider:
            # Drop with removal from provider
            drop_key_sql = f"""
            DROP {key_type_sql} KEY [{key_name}] REMOVE PROVIDER KEY
            """
        else:
            # Normal drop (key remains in provider)
            drop_key_sql = f"""
            DROP {key_type_sql} KEY [{key_name}]
            """
        
        drop_result = await self.execute_sql(drop_key_sql)
        results.append({
            "step": f"drop_{key_type_sql.lower()}_key",
            "key_name": key_name,
            "removed_from_provider": remove_from_provider,
            "result": drop_result
        })
        
        return {
            "success": drop_result.get("success", False),
            "key_name": key_name,
            "key_type": key_type,
            "is_asymmetric": is_asymmetric,
            "databases_affected": databases_using_key,
            "tde_login_dropped": tde_login_dropped,
            "removed_from_provider": remove_from_provider,
            "steps": results
        }
    
    async def drop_login(
        self,
        login_name: str,
        force: bool = False
    ) -> Dict[str, Any]:
        """Drop a SQL Server login"""
        
        results = []
        
        # Check if login exists
        login_check_sql = f"""
        SELECT 
            name,
            type_desc,
            is_disabled
        FROM sys.server_principals 
        WHERE name = '{login_name}'
        AND type IN ('S', 'U', 'C')  -- SQL login, Windows login, Certificate-based login
        """
        
        login_result = await self.execute_sql(login_check_sql)
        
        if not (login_result.get("success") and login_result.get("results") 
                and login_result["results"][0].get("data")):
            return {
                "success": False,
                "error": f"Login '{login_name}' not found"
            }
        
        login_info = login_result["results"][0]["data"][0]
        
        # Check for credential mappings
        cred_check_sql = f"""
        SELECT 
            c.name as credential_name,
            c.credential_identity
        FROM sys.server_principal_credentials pc
        JOIN sys.server_principals p ON pc.principal_id = p.principal_id
        JOIN sys.credentials c ON pc.credential_id = c.credential_id
        WHERE p.name = '{login_name}'
        """
        
        cred_result = await self.execute_sql(cred_check_sql)
        mapped_credentials = []
        
        if cred_result["success"] and cred_result["results"][0]["data"]:
            mapped_credentials = [row["credential_name"] for row in cred_result["results"][0]["data"]]
        
        if mapped_credentials and not force:
            return {
                "success": False,
                "error": f"Login '{login_name}' has mapped credentials: {', '.join(mapped_credentials)}. Use force=true to remove mappings and drop.",
                "mapped_credentials": mapped_credentials
            }
        
        # Check for database users owned by this login
        db_user_check_sql = f"""
        SELECT 
            DB_NAME(database_id) as database_name,
            COUNT(*) as user_count
        FROM sys.database_principals dp
        JOIN sys.server_principals sp ON dp.sid = sp.sid
        WHERE sp.name = '{login_name}'
        GROUP BY database_id
        """
        
        db_user_result = await self.execute_sql(db_user_check_sql)
        database_users = []
        
        if db_user_result["success"] and db_user_result["results"][0]["data"]:
            database_users = [row["database_name"] for row in db_user_result["results"][0]["data"]]
        
        # Remove credential mappings if force=True
        if mapped_credentials and force:
            for cred_name in mapped_credentials:
                unmap_sql = f"ALTER LOGIN [{login_name}] DROP CREDENTIAL [{cred_name}]"
                unmap_result = await self.execute_sql(unmap_sql)
                results.append({
                    "step": "remove_credential_mapping",
                    "credential": cred_name,
                    "result": unmap_result
                })
        
        # Drop the login
        drop_login_sql = f"DROP LOGIN [{login_name}]"
        drop_result = await self.execute_sql(drop_login_sql)
        results.append({
            "step": "drop_login",
            "login_name": login_name,
            "result": drop_result
        })
        
        return {
            "success": drop_result.get("success", False),
            "login_name": login_name,
            "login_type": login_info["type_desc"],
            "was_disabled": bool(login_info["is_disabled"]),
            "credentials_unmapped": mapped_credentials if force else [],
            "database_users_orphaned": database_users,
            "steps": results
        }
    
    async def list_logins(self) -> List[Dict[str, Any]]:
        """List all SQL Server logins with their properties"""
        logins_sql = """
        SELECT 
            p.name,
            p.principal_id,
            p.type_desc,
            p.is_disabled,
            p.create_date,
            p.modify_date,
            p.default_database_name,
            -- Count credentials
            (SELECT COUNT(*) 
             FROM sys.server_principal_credentials pc 
             WHERE pc.principal_id = p.principal_id) as credential_count,
            -- Check if it's a TDE login
            CASE 
                WHEN p.name LIKE 'TDE_Login_%' THEN 1
                ELSE 0
            END as is_tde_login,
            -- Get associated asymmetric key name if applicable
            ak.name as asymmetric_key_name
        FROM sys.server_principals p
        LEFT JOIN sys.asymmetric_keys ak ON p.sid = ak.sid
        WHERE p.type IN ('S', 'U', 'C')  -- SQL login, Windows login, Certificate-based login
        ORDER BY p.name
        """
        
        result = await self.execute_sql(logins_sql)
        
        if result["success"]:
            logins = result["results"][0]["data"]
            # Convert datetime objects to strings
            for login in logins:
                if login.get("create_date") and hasattr(login["create_date"], "isoformat"):
                    login["create_date"] = login["create_date"].isoformat()
                if login.get("modify_date") and hasattr(login["modify_date"], "isoformat"):
                    login["modify_date"] = login["modify_date"].isoformat()
            return logins
        else:
            raise TDEOperationError(f"Failed to list logins: {result['error']}")
    
    async def decrypt_database(
        self,
        database_name: str
    ) -> Dict[str, Any]:
        """Decrypt a database (remove TDE)"""
        
        results = []
        
        # Check if database is encrypted
        encryption_status = await self.check_encryption_status(database_name)
        
        if not encryption_status or not encryption_status[0].is_encrypted:
            return {
                "success": False,
                "error": f"Database '{database_name}' is not encrypted"
            }
        
        current_state = encryption_status[0].encryption_state
        if current_state == 5:  # Already decrypting
            return {
                "success": False,
                "error": f"Database '{database_name}' is already being decrypted"
            }
        
        # Step 1: Disable TDE
        disable_tde_sql = f"ALTER DATABASE [{database_name}] SET ENCRYPTION OFF"
        
        disable_result = await self.execute_sql(disable_tde_sql)
        results.append({"step": "disable_tde", "result": disable_result})
        
        if not disable_result.get("success", False):
            return {
                "success": False,
                "error": f"Failed to disable TDE: {disable_result.get('error')}",
                "steps": results
            }
        
        # Step 2: Wait for decryption to complete (optional - just check status)
        status_check_sql = f"""
        SELECT 
            encryption_state,
            percent_complete
        FROM sys.dm_database_encryption_keys
        WHERE database_id = DB_ID('{database_name}')
        """
        
        status_result = await self.execute_sql(status_check_sql)
        decryption_status = None
        
        if status_result["success"] and status_result["results"][0]["data"]:
            status_data = status_result["results"][0]["data"][0]
            decryption_status = {
                "encryption_state": status_data["encryption_state"],
                "percent_complete": status_data["percent_complete"]
            }
        
        # Step 3: Drop the Database Encryption Key (DEK) - only after decryption completes
        # Note: In practice, you may need to wait for decryption to complete (state = 1)
        # before dropping the DEK. For now, we'll attempt it.
        if decryption_status and decryption_status["encryption_state"] in [1, 5]:
            # State 1 = Unencrypted, State 5 = Decryption in progress
            # We can only drop DEK when state is 1
            if decryption_status["encryption_state"] == 1:
                drop_dek_sql = f"""
                USE [{database_name}];
                DROP DATABASE ENCRYPTION KEY;
                """
                
                drop_dek_result = await self.execute_sql(drop_dek_sql)
                results.append({"step": "drop_database_encryption_key", "result": drop_dek_result})
            else:
                results.append({
                    "step": "drop_database_encryption_key", 
                    "result": {
                        "success": False, 
                        "message": "Decryption in progress. DEK will need to be dropped after decryption completes."
                    }
                })
        
        # Get final status
        final_status = await self.check_encryption_status(database_name)
        
        return {
            "success": disable_result.get("success", False),
            "database_name": database_name,
            "initial_state": current_state,
            "decryption_status": decryption_status,
            "final_status": {
                "is_encrypted": final_status[0].is_encrypted if final_status else None,
                "encryption_state": final_status[0].encryption_state if final_status else None,
                "encryption_state_desc": final_status[0].encryption_state_desc if final_status else None
            },
            "steps": results,
            "note": "Decryption may take time for large databases. Monitor progress with get_encryption_status."
        }
    
    async def get_tde_certificate_info(self) -> List[Dict[str, Any]]:
        """Get information about TDE certificates"""
        cert_sql = """
        SELECT 
            c.name,
            c.certificate_id,
            c.principal_id,
            c.start_date,
            c.expiry_date,
            c.subject,
            c.issuer_name,
            c.thumbprint,
            p.name as owner_name,
            CASE 
                WHEN c.pvt_key_encryption_type = 'MK' THEN 'ENCRYPTED BY MASTER KEY'
                WHEN c.pvt_key_encryption_type = 'PW' THEN 'ENCRYPTED BY PASSWORD'
                WHEN c.pvt_key_encryption_type = 'SK' THEN 'ENCRYPTED BY SERVICE MASTER KEY'
                ELSE c.pvt_key_encryption_type
            END as key_encryption_type
        FROM master.sys.certificates c
        LEFT JOIN sys.server_principals p ON c.principal_id = p.principal_id
        WHERE c.name NOT LIKE '##%'  -- Exclude system certificates
        ORDER BY c.name
        """
        
        result = await self.execute_sql(cert_sql)
        
        if result["success"]:
            certs = result["results"][0]["data"]
            # Convert datetime objects to strings
            for cert in certs:
                if cert.get("start_date") and hasattr(cert["start_date"], "isoformat"):
                    cert["start_date"] = cert["start_date"].isoformat()
                if cert.get("expiry_date") and hasattr(cert["expiry_date"], "isoformat"):
                    cert["expiry_date"] = cert["expiry_date"].isoformat()
            return certs
        else:
            raise TDEOperationError(f"Failed to get certificate info: {result['error']}")
    
    async def get_tde_compliance_data(self) -> Dict[str, Any]:
        """Get comprehensive TDE compliance data"""
        compliance_data = {
            "encryption_overview": {},
            "key_details": {},
            "certificate_info": [],
            "provider_info": [],
            "credential_info": {},
            "security_warnings": []
        }
        
        # 1. Encryption Overview
        overview_sql = """
        SELECT 
            COUNT(*) as total_databases,
            SUM(CASE WHEN is_encrypted = 1 THEN 1 ELSE 0 END) as encrypted_databases,
            SUM(CASE WHEN name IN ('master', 'tempdb', 'model', 'msdb') THEN 1 ELSE 0 END) as system_databases,
            SUM(CASE WHEN is_encrypted = 0 AND name NOT IN ('master', 'tempdb', 'model', 'msdb') THEN 1 ELSE 0 END) as unencrypted_user_databases
        FROM sys.databases
        """
        
        overview_result = await self.execute_sql(overview_sql)
        if overview_result["success"] and overview_result["results"][0]["data"]:
            compliance_data["encryption_overview"] = overview_result["results"][0]["data"][0]
        
        # 2. Key Algorithm Distribution
        key_algo_sql = """
        SELECT 
            dek.key_algorithm,
            dek.key_length,
            COUNT(*) as database_count,
            STRING_AGG(db.name, ', ') as databases
        FROM sys.dm_database_encryption_keys dek
        INNER JOIN sys.databases db ON dek.database_id = db.database_id
        GROUP BY dek.key_algorithm, dek.key_length
        ORDER BY database_count DESC
        """
        
        algo_result = await self.execute_sql(key_algo_sql)
        if algo_result["success"]:
            compliance_data["key_details"]["algorithm_distribution"] = algo_result["results"][0]["data"]
        
        # 3. Master Key Usage
        master_keys = await self.list_master_keys()
        compliance_data["key_details"]["master_keys"] = master_keys
        
        # 4. Certificate Information
        try:
            compliance_data["certificate_info"] = await self.get_tde_certificate_info()
        except:
            pass
        
        # 5. Provider Information
        compliance_data["provider_info"] = await self.list_cryptographic_providers()
        
        # 6. Credential Summary
        cred_summary_sql = """
        SELECT 
            COUNT(*) as total_credentials,
            SUM(CASE WHEN name LIKE '%_master_cred' THEN 1 ELSE 0 END) as master_credentials,
            SUM(CASE WHEN name LIKE '%_TDE_Login_%_cred' THEN 1 ELSE 0 END) as tde_credentials,
            COUNT(DISTINCT target_id) as unique_providers
        FROM sys.credentials
        WHERE target_type = 'CRYPTOGRAPHIC PROVIDER'
        """
        
        cred_result = await self.execute_sql(cred_summary_sql)
        if cred_result["success"] and cred_result["results"][0]["data"]:
            compliance_data["credential_info"] = cred_result["results"][0]["data"][0]
        
        # 7. Security Warnings
        # Check for weak key sizes
        weak_keys_sql = """
        SELECT 
            name,
            algorithm_desc,
            key_length
        FROM master.sys.asymmetric_keys
        WHERE key_length < 2048
        """
        
        weak_result = await self.execute_sql(weak_keys_sql)
        if weak_result["success"] and weak_result["results"][0]["data"]:
            for key in weak_result["results"][0]["data"]:
                compliance_data["security_warnings"].append({
                    "type": "WEAK_KEY_SIZE",
                    "severity": "HIGH",
                    "message": f"Key '{key['name']}' uses weak key size ({key['key_length']} bits). Recommended: 2048 bits or higher.",
                    "details": key
                })
        
        # Check for databases with old encryption algorithms
        old_algo_sql = """
        SELECT 
            db.name as database_name,
            dek.key_algorithm,
            dek.key_length
        FROM sys.dm_database_encryption_keys dek
        INNER JOIN sys.databases db ON dek.database_id = db.database_id
        WHERE dek.key_algorithm != 'AES' OR dek.key_length < 256
        """
        
        old_algo_result = await self.execute_sql(old_algo_sql)
        if old_algo_result["success"] and old_algo_result["results"][0]["data"]:
            for db in old_algo_result["results"][0]["data"]:
                compliance_data["security_warnings"].append({
                    "type": "WEAK_ENCRYPTION_ALGORITHM",
                    "severity": "MEDIUM",
                    "message": f"Database '{db['database_name']}' uses {db['key_algorithm']}_{db['key_length']}. Recommended: AES_256.",
                    "details": db
                })
        
        return compliance_data
    
    async def get_encryption_history(self) -> List[Dict[str, Any]]:
        """Get encryption state change history from SQL Server logs"""
        # Note: This is a simplified version. In practice, you'd need to parse SQL Server logs
        # or maintain an audit table to track these changes
        history_sql = """
        SELECT 
            'Current State' as event_type,
            db.name as database_name,
            CASE 
                WHEN dek.encryption_state = 3 THEN 'Encrypted'
                WHEN dek.encryption_state = 2 THEN 'Encryption In Progress'
                WHEN dek.encryption_state = 5 THEN 'Decryption In Progress'
                WHEN dek.encryption_state = 1 THEN 'Unencrypted'
                WHEN dek.encryption_state = 4 THEN 'Key Change In Progress'
                ELSE 'Unknown'
            END as state,
            GETDATE() as event_time,
            dek.key_algorithm,
            dek.key_length,
            ak.name as asymmetric_key_name,
            sk.name as symmetric_key_name
        FROM sys.dm_database_encryption_keys dek
        INNER JOIN sys.databases db ON dek.database_id = db.database_id
        LEFT JOIN master.sys.asymmetric_keys ak ON dek.encryptor_thumbprint = ak.thumbprint
        LEFT JOIN master.sys.symmetric_keys sk ON dek.encryptor_thumbprint = sk.key_guid
        ORDER BY db.name
        """
        
        result = await self.execute_sql(history_sql)
        
        if result["success"]:
            history = result["results"][0]["data"]
            # Convert datetime objects to strings
            for event in history:
                if event.get("event_time") and hasattr(event["event_time"], "isoformat"):
                    event["event_time"] = event["event_time"].isoformat()
            return history
        else:
            return []

    async def check_best_practices(self, include_recommendations: bool = True) -> Dict[str, Any]:
        """Check TDE configuration against a set of best practices."""
        logger.info("Checking TDE best practices...")
        results = {"checks": [], "summary": {"pass": 0, "fail": 0, "total": 0}}
        
        # Check 1: All user databases should be encrypted
        all_dbs = await self.check_encryption_status()
        unencrypted_dbs = [db.database_name for db in all_dbs if not db.is_encrypted]
        if not unencrypted_dbs:
            results["checks"].append({"check": "All user databases encrypted", "status": "PASS"})
            results["summary"]["pass"] += 1
        else:
            results["checks"].append({
                "check": "All user databases encrypted", "status": "FAIL",
                "details": f"Unencrypted databases: {', '.join(unencrypted_dbs)}",
                "recommendation": "Encrypt all user databases to protect data at rest." if include_recommendations else None
            })
            results["summary"]["fail"] += 1
        results["summary"]["total"] += 1

        # Check 2: Strong DEK algorithm (AES_256)
        weak_dek_dbs = [db.database_name for db in all_dbs if db.is_encrypted and (db.key_algorithm != 'AES' or db.key_length != 256)]
        if not weak_dek_dbs:
            results["checks"].append({"check": "DEK uses strong encryption (AES_256)", "status": "PASS"})
            results["summary"]["pass"] += 1
        else:
            results["checks"].append({
                "check": "DEK uses strong encryption (AES_256)", "status": "FAIL",
                "details": f"Databases with weak DEK algorithms: {', '.join(weak_dek_dbs)}",
                "recommendation": "Rotate the Database Encryption Key (DEK) for these databases to AES_256." if include_recommendations else None
            })
            results["summary"]["fail"] += 1
        results["summary"]["total"] += 1

        # Check 3: Strong Master Key algorithm (RSA >= 2048)
        master_keys = await self.list_master_keys()
        weak_master_keys = [k['name'] for k in master_keys.get('asymmetric_keys', []) if k['key_length'] < 2048]
        if not weak_master_keys:
            results["checks"].append({"check": "Master Keys use strong encryption (RSA >= 2048)", "status": "PASS"})
            results["summary"]["pass"] += 1
        else:
            results["checks"].append({
                "check": "Master Keys use strong encryption (RSA >= 2048)", "status": "FAIL",
                "details": f"Master keys with weak encryption: {', '.join(weak_master_keys)}",
                "recommendation": "Rotate databases using these keys to a new Master Key with RSA 2048-bit or higher encryption." if include_recommendations else None
            })
            results["summary"]["fail"] += 1
        results["summary"]["total"] += 1
        
        return results

    async def validate_tde_setup(self, database_name: str) -> Dict[str, Any]:
        """Validate the full TDE chain for a specific database."""
        logger.info(f"Validating TDE setup for database '{database_name}'...")
        validation_steps = []
        
        # Step 1: Check Database Encryption Status
        db_status_list = await self.check_encryption_status(database_name)
        if not db_status_list:
            return {"success": False, "error": f"Database '{database_name}' not found or is a system database."}
        db_status = db_status_list[0]
        if not db_status.is_encrypted:
            return {"success": False, "error": f"Database '{database_name}' is not encrypted."}
        validation_steps.append({"step": "Database Encryption", "status": "PASS", "details": f"Database is encrypted with {db_status.key_algorithm}_{db_status.key_length}."})

        # Step 2: Find the Encryptor (Asymmetric Key or Certificate)
        encryptor_sql = f"""
        SELECT
            COALESCE(ak.name, cert.name) as encryptor_name,
            CASE
                WHEN ak.name IS NOT NULL THEN 'ASYMMETRIC KEY'
                WHEN cert.name IS NOT NULL THEN 'CERTIFICATE'
                ELSE 'UNKNOWN'
            END as encryptor_type,
            p.name as provider_name
        FROM sys.dm_database_encryption_keys dek
        LEFT JOIN master.sys.asymmetric_keys ak ON dek.encryptor_thumbprint = ak.thumbprint
        LEFT JOIN master.sys.certificates cert ON dek.encryptor_thumbprint = cert.thumbprint
        LEFT JOIN master.sys.cryptographic_providers p ON ak.cryptographic_provider_guid = p.guid
        WHERE dek.database_id = DB_ID('{database_name}')
        """
        encryptor_result = await self.execute_sql(encryptor_sql)
        if not (encryptor_result["success"] and encryptor_result["results"][0]["data"]):
            validation_steps.append({"step": "Find Encryptor", "status": "FAIL", "details": "Could not find the Asymmetric Key or Certificate used to encrypt the DEK."})
            return {"success": False, "validation_steps": validation_steps}
        
        encryptor_info = encryptor_result["results"][0]["data"][0]
        encryptor_name = encryptor_info['encryptor_name']
        encryptor_type = encryptor_info['encryptor_type']
        
        if encryptor_type == 'UNKNOWN':
            validation_steps.append({"step": "Find Encryptor", "status": "FAIL", "details": "Found an encryptor but could not determine its type (Key or Certificate)." })
            return {"success": False, "validation_steps": validation_steps}

        validation_steps.append({"step": "Find Encryptor", "status": "PASS", "details": f"DEK is encrypted by {encryptor_type} '{encryptor_name}'."})

        # If the encryptor is not an asymmetric key, the TDE chain validation stops here as logins/credentials do not apply.
        if encryptor_type != 'ASYMMETRIC KEY':
            return {"success": True, "validation_summary": "TDE is enabled using a server certificate. No EKM provider is involved.", "validation_steps": validation_steps}

        # Step 3: Find the TDE Login associated with the key
        login_name = f"TDE_Login_{encryptor_name}"
        login_sql = f"SELECT name FROM sys.server_principals WHERE name = '{login_name}' AND type = 'K'"
        login_result = await self.execute_sql(login_sql)
        if not (login_result["success"] and login_result["results"][0]["data"]):
            validation_steps.append({"step": "Find TDE Login", "status": "FAIL", "details": f"Could not find the TDE login '{login_name}' associated with the key."})
            return {"success": False, "validation_steps": validation_steps}
        validation_steps.append({"step": "Find TDE Login", "status": "PASS", "details": f"Found TDE login '{login_name}'."})
        
        # Step 4: Find the Credential mapped to the TDE Login
        cred_sql = f"""
        SELECT c.name as credential_name, c.credential_identity
        FROM sys.server_principal_credentials spc
        JOIN sys.credentials c ON spc.credential_id = c.credential_id
        WHERE spc.principal_id = SUSER_ID('{login_name}')
        """
        cred_result = await self.execute_sql(cred_sql)
        if not (cred_result["success"] and cred_result["results"][0]["data"]):
            validation_steps.append({"step": "Find TDE Credential", "status": "FAIL", "details": f"Could not find any credentials mapped to login '{login_name}'."})
            return {"success": False, "validation_steps": validation_steps}

        cred_info = cred_result["results"][0]["data"][0]
        validation_steps.append({"step": "Find TDE Credential", "status": "PASS", "details": f"Found credential '{cred_info['credential_name']}' mapped to the TDE login."})
        
        return {"success": True, "validation_summary": "TDE chain appears to be intact.", "validation_steps": validation_steps}