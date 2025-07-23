import paramiko
import logging
import time
from typing import Dict, List, Optional, Tuple
import os
from contextlib import contextmanager

from ..config import get_config
from ..models import SSHConfig, OracleConfig

logger = logging.getLogger(__name__)

class OracleSSHManager:
    """SSH manager for Oracle server operations with enhanced key handling and multi-container support"""
    
    def __init__(self, host: str, username: str, password: str, port: int = 22, 
                 timeout: int = 30, key_filename: str = None, allow_agent: bool = True):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.timeout = timeout
        self.key_filename = key_filename
        self.allow_agent = allow_agent
        self.ssh_client = None
        
        # Configure paramiko logging
        paramiko_logger = logging.getLogger("paramiko")
        paramiko_logger.setLevel(logging.WARNING)
    
    @classmethod
    def from_database_config(cls, connection_name: str) -> Optional['OracleSSHManager']:
        """Create SSH manager from database configuration"""
        try:
            config = get_config()
            ssh_config = config.get_ssh_config(connection_name)
            
            if not ssh_config:
                logger.error(f"No SSH configuration found for connection: {connection_name}")
                return None
            
            logger.info(f"Creating SSH manager for {connection_name} from config: {ssh_config.host}:{ssh_config.port}")
            
            # Determine authentication method
            use_key_auth = hasattr(ssh_config, 'private_key_path') and ssh_config.private_key_path
            use_password_auth = hasattr(ssh_config, 'password') and ssh_config.password
            
            if use_key_auth:
                logger.info(f"Using SSH key authentication with key: {ssh_config.private_key_path}")
                return cls(
                    host=ssh_config.host,
                    username=ssh_config.username,
                    password=None,  # Don't pass password when using key
                    port=ssh_config.port,
                    timeout=ssh_config.timeout,
                    key_filename=ssh_config.private_key_path,
                    allow_agent=True
                )
            elif use_password_auth:
                logger.info(f"Using SSH password authentication")
                return cls(
                    host=ssh_config.host,
                    username=ssh_config.username,
                    password=ssh_config.password,
                    port=ssh_config.port,
                    timeout=ssh_config.timeout,
                    key_filename=None,
                    allow_agent=True
                )
            else:
                logger.error(f"No authentication method specified for {connection_name}")
                return None
            
        except Exception as e:
            logger.error(f"Error creating SSH manager from config for {connection_name}: {e}")
            return None
    
    def get_oracle_environment(self, connection_name: str) -> Dict[str, str]:
        """Get Oracle environment variables from database configuration"""
        try:
            config = get_config()
            oracle_config = config.get_oracle_config(connection_name)
            
            if not oracle_config:
                logger.warning(f"No Oracle configuration found for connection: {connection_name}")
                return {}
            
            env_vars = {
                'ORACLE_HOME': oracle_config.oracle_home,
                'ORACLE_SID': oracle_config.oracle_sid,
                'TNS_ADMIN': oracle_config.tns_admin or f"{oracle_config.oracle_home}/network/admin"
            }
            
            logger.info(f"Oracle environment for {connection_name}: SID={oracle_config.oracle_sid}, HOME={oracle_config.oracle_home}")
            return env_vars
            
        except Exception as e:
            logger.error(f"Error getting Oracle environment for {connection_name}: {e}")
            return {}
    
    def connect(self) -> bool:
        """Establish SSH connection with enhanced key handling"""
        try:
            logger.info(f"Attempting SSH connection to {self.host}:{self.port} as {self.username}")
            
            self.ssh_client = paramiko.SSHClient()
            
            # Auto-add policy for unknown hosts (avoids host key verification issues)
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Configure connection parameters
            connect_kwargs = {
                'hostname': self.host,
                'port': self.port,
                'username': self.username,
                'timeout': self.timeout,
                'allow_agent': self.allow_agent,
                'look_for_keys': True,  # Look for SSH keys in default locations
                'banner_timeout': 60,
                'auth_timeout': 60
            }
            
            # Determine authentication method priority
            if self.key_filename and os.path.exists(self.key_filename):
                # Use key authentication (preferred)
                connect_kwargs['key_filename'] = self.key_filename
                logger.info(f"Using SSH key authentication with key: {self.key_filename}")
                
                # Only add password if explicitly provided (for key passphrase)
                if self.password:
                    connect_kwargs['password'] = self.password
                    logger.info("Password provided (may be used for key passphrase)")
            elif self.password:
                # Use password authentication
                connect_kwargs['password'] = self.password
                logger.info("Using SSH password authentication")
            else:
                logger.warning("No authentication method provided - will try SSH agent")
            
            # Attempt connection with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    logger.info(f"SSH connection attempt {attempt + 1}/{max_retries}")
                    self.ssh_client.connect(**connect_kwargs)
                    logger.info(f"SSH connection established to {self.host}")
                    return True
                    
                except paramiko.AuthenticationException as e:
                    logger.error(f"SSH authentication failed: {e}")
                    return False
                    
                except paramiko.SSHException as e:
                    logger.warning(f"SSH connection attempt {attempt + 1} failed: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(2)  # Wait before retry
                    else:
                        logger.error(f"SSH connection failed after {max_retries} attempts")
                        return False
                        
                except Exception as e:
                    logger.error(f"SSH connection error: {e}")
                    return False
                    
        except Exception as e:
            logger.error(f"SSH connection setup failed: {e}")
            return False
    
    def disconnect(self):
        """Close SSH connection safely"""
        try:
            if self.ssh_client:
                self.ssh_client.close()
                logger.info("SSH connection closed")
        except Exception as e:
            logger.warning(f"Error closing SSH connection: {e}")
        finally:
            self.ssh_client = None
    
    def is_connected(self) -> bool:
        """Check if SSH connection is active"""
        try:
            if not self.ssh_client:
                return False
            transport = self.ssh_client.get_transport()
            if not transport or not transport.is_active():
                return False
            # Send a test command to verify connection is truly active
            stdin, stdout, stderr = self.ssh_client.exec_command("echo test", timeout=5)
            stdout.read()
            return True
        except Exception as e:
            logger.debug(f"Connection check failed: {e}")
            return False
    
    def ensure_connected(self) -> bool:
        """Ensure SSH connection is active, reconnect if needed"""
        if self.is_connected():
            return True
        
        logger.info("SSH connection not active, attempting to reconnect...")
        self.disconnect()  # Clean up any stale connection
        return self.connect()
    
    def execute_command(self, command: str, timeout: int = 60, use_bash: bool = True) -> Tuple[bool, str, str]:
        """Execute a command via SSH with enhanced timeout handling"""
        try:
            if not self.ssh_client:
                return False, "", "SSH connection not established"
            
            logger.info(f"Executing SSH command: {command[:100]}...")  # Log first 100 chars
            
            # Wrap command in bash -c to ensure proper execution without sourcing profiles
            if use_bash:
                # Use bash without loading profiles to avoid environment conflicts
                command = f"bash --noprofile --norc -c '{command}'"
            
            # Execute command with timeout
            stdin, stdout, stderr = self.ssh_client.exec_command(
                command, 
                timeout=timeout,
                get_pty=False  # Disable pseudo-terminal to avoid hanging
            )
            
            # Read output with timeout protection
            stdout_str = ""
            stderr_str = ""
            
            # Read stdout with timeout
            try:
                stdout_str = stdout.read().decode('utf-8', errors='ignore').strip()
            except Exception as e:
                logger.warning(f"Error reading stdout: {e}")
            
            # Read stderr with timeout
            try:
                stderr_str = stderr.read().decode('utf-8', errors='ignore').strip()
            except Exception as e:
                logger.warning(f"Error reading stderr: {e}")
            
            # Get exit code with timeout protection
            exit_code = 0
            try:
                exit_code = stdout.channel.recv_exit_status()
            except Exception as e:
                logger.warning(f"Error getting exit code: {e}")
                # If we can't get exit code, assume success if no stderr
                exit_code = 0 if not stderr_str else 1
            
            success = exit_code == 0
            logger.info(f"SSH command completed with exit code: {exit_code}")
            
            return success, stdout_str, stderr_str
            
        except Exception as e:
            logger.error(f"SSH command execution failed: {e}")
            return False, "", str(e)
    
    def test_connection(self) -> Dict[str, any]:
        """Test SSH connection with basic command"""
        try:
            if not self.connect():
                return {"success": False, "error": "SSH connection failed"}
            
            # Test with a simple command
            success, stdout, stderr = self.execute_command("echo 'SSH connection test successful'", timeout=10)
            
            self.disconnect()
            
            return {
                "success": success,
                "stdout": stdout,
                "stderr": stderr,
                "error": stderr if not success else None
            }
            
        except Exception as e:
            self.disconnect()
            return {"success": False, "error": str(e)}
    
    def list_oracle_databases(self, reuse_connection: bool = False) -> Dict[str, any]:
        """List all Oracle container databases on the server"""
        try:
            # Handle connection reuse
            connection_created = False
            if not reuse_connection or not self.is_connected():
                if not self.ensure_connected():
                    return {"success": False, "error": "SSH connection failed"}
                connection_created = True
            
            # Find all running Oracle instances
            cmd = "ps -ef | grep pmon | grep -v grep | awk '{print $8}' | sed 's/ora_pmon_//'"
            success, stdout, stderr = self.execute_command(cmd, timeout=30)
            
            databases = []
            if success and stdout:
                databases = [db.strip() for db in stdout.split('\n') if db.strip()]
            
            # Only disconnect if we created the connection
            if connection_created:
                self.disconnect()
            
            return {
                "success": success,
                "databases": databases,
                "error": stderr if not success else None
            }
            
        except Exception as e:
            self.disconnect()
            return {"success": False, "error": str(e)}
    
    def restart_oracle_database(self, oracle_sid: str, oracle_home: str = None, reuse_connection: bool = False) -> Dict[str, any]:
        """Restart Oracle database with proper environment isolation for multi-container support"""
        try:
            # Handle connection reuse or create new
            connection_created = False
            if not reuse_connection or not self.is_connected():
                if not self.ensure_connected():
                    return {"success": False, "error": "SSH connection failed"}
                connection_created = True
            
            oracle_home = oracle_home or "/opt/oracle/product/21c/dbhome_1"
            
            # First, verify the database exists
            list_result = self.list_oracle_databases(reuse_connection=True)
            if list_result["success"] and oracle_sid not in list_result.get("databases", []):
                logger.warning(f"Database {oracle_sid} not found in running instances. Proceeding anyway...")
            
            results = []
            
            # Create a script that will be executed to ensure proper environment
            restart_script = fr"""#!/bin/bash
# Unset any existing Oracle environment to avoid conflicts
unset ORACLE_SID
unset ORACLE_HOME
unset PATH

# Discover the correct Oracle home for this SID
echo "Discovering Oracle home for SID: {oracle_sid}"

# Method 1: Try to find Oracle home from running processes
ORACLE_HOME_FROM_PROCESS=$(ps -ef | grep pmon | grep {oracle_sid} | grep -v grep | head -1 | awk '{{print $2}}' | xargs -I {{}} sh -c 'ls -la /proc/{{}}/exe 2>/dev/null | sed "s/.*-> //" | sed "s/bin/oracle.*//" | head -1')

# Method 2: Try common Oracle home locations
if [ -z "$ORACLE_HOME_FROM_PROCESS" ]; then
    for home in "/u01/app/oracle/product/21.0.0/dbhome_1" "/opt/oracle/product/21c/dbhome_1" "/u01/app/oracle/product/19.0.0/dbhome_1"; do
        if [ -d "$home" ] && [ -f "$home/bin/sqlplus" ]; then
            ORACLE_HOME_FROM_PROCESS="$home"
            break
        fi
    done
fi

# Method 3: Use the provided oracle_home as fallback
if [ -z "$ORACLE_HOME_FROM_PROCESS" ]; then
    ORACLE_HOME_FROM_PROCESS="{oracle_home}"
fi

# Set the environment with proper PATH including common Unix utilities
export ORACLE_SID={oracle_sid}
export ORACLE_HOME="$ORACLE_HOME_FROM_PROCESS"
export PATH=$ORACLE_HOME/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin:$PATH

echo "Restarting Oracle Database: $ORACLE_SID"
echo "Oracle Home: $ORACLE_HOME"
echo "SQL*Plus location: $(which sqlplus 2>/dev/null || echo 'sqlplus not found')"

# Verify sqlplus is available
if ! command -v sqlplus >/dev/null 2>&1; then
    echo "ERROR: sqlplus not found in PATH: $PATH"
    exit 1
fi

# Step 1: Shutdown
echo "Step 1: Shutting down database..."
sqlplus -S / as sysdba <<EOF
WHENEVER SQLERROR EXIT SQL.SQLCODE
SHUTDOWN IMMEDIATE;
EXIT;
EOF

if [ $? -eq 0 ]; then
    echo "Database shutdown successful"
    sleep 10
    
    # Step 2: Startup
    echo "Step 2: Starting up database..."
    sqlplus -S / as sysdba <<EOF
WHENEVER SQLERROR EXIT SQL.SQLCODE
STARTUP;
EXIT;
EOF
    
    if [ $? -eq 0 ]; then
        echo "Database startup successful"
        sleep 10
        
        # Step 3: Open PDBs
        echo "Step 3: Opening all pluggable databases..."
        sqlplus -S / as sysdba <<EOF
WHENEVER SQLERROR EXIT SQL.SQLCODE
ALTER PLUGGABLE DATABASE ALL OPEN READ WRITE;
EXIT;
EOF
        
        if [ $? -eq 0 ]; then
            echo "PDBs opened successfully"
            
            # Step 4: Verify status
            echo "Step 4: Verifying database status..."
            sqlplus -S / as sysdba <<EOF
SET LINESIZE 200
SET PAGESIZE 50
COLUMN INSTANCE_NAME FORMAT A20
COLUMN STATUS FORMAT A15
SELECT INSTANCE_NAME, INSTANCE_NUMBER, STATUS FROM V\$INSTANCE;
SHOW PARAMETER db_name;
SHOW PARAMETER wallet_root;
SELECT NAME, OPEN_MODE FROM V\$PDBS;
EXIT;
EOF
        fi
    fi
fi
"""
            
            # Execute the restart script
            # Create temporary script file
            script_name = f"/tmp/restart_oracle_{oracle_sid}_{int(time.time())}.sh"
            create_script_cmd = f"cat > {script_name} << 'EOSCRIPT'\n{restart_script}\nEOSCRIPT"
            success, stdout, stderr = self.execute_command(create_script_cmd, timeout=30, use_bash=False)
            
            if success:
                # Make script executable
                chmod_cmd = f"chmod +x {script_name}"
                self.execute_command(chmod_cmd, timeout=10)
                
                # Execute the script
                exec_cmd = f"{script_name}"
                success, stdout, stderr = self.execute_command(exec_cmd, timeout=300, use_bash=False)
                
                # Clean up the script
                cleanup_cmd = f"rm -f {script_name}"
                self.execute_command(cleanup_cmd, timeout=10)
                
                results.append({
                    "step": "complete_restart",
                    "success": success,
                    "output": stdout,
                    "error": stderr
                })
            else:
                results.append({
                    "step": "script_creation",
                    "success": False,
                    "output": stdout,
                    "error": stderr
                })
            
            # Only disconnect if we created the connection
            if connection_created:
                self.disconnect()
            
            overall_success = all(r["success"] for r in results)
            
            return {
                "success": overall_success,
                "stdout": "\n".join([r.get("output", "") for r in results]),
                "stderr": "\n".join([r.get("error", "") for r in results if r.get("error")]),
                "target_database": oracle_sid,
                "oracle_home": oracle_home,
                "steps": results,
                "error": "See individual step results" if not overall_success else None
            }
            
        except Exception as e:
            self.disconnect()
            return {"success": False, "error": str(e)}
    
    def execute_oracle_command(self, oracle_sid: str, sql_command: str, oracle_home: str = None, reuse_connection: bool = False) -> Dict[str, any]:
        """Execute a SQL command on a specific Oracle database"""
        try:
            # Handle connection reuse
            connection_created = False
            if not reuse_connection or not self.is_connected():
                if not self.ensure_connected():
                    return {"success": False, "error": "SSH connection failed"}
                connection_created = True
            
            oracle_home = oracle_home or "/opt/oracle/product/21c/dbhome_1"
            
            # Create a script to execute the SQL command with proper environment
            sql_script = f"""#!/bin/bash
# Clear any existing Oracle environment
unset ORACLE_SID
unset ORACLE_HOME
unset PATH

# Set the specific environment for this database
export ORACLE_SID={oracle_sid}
export ORACLE_HOME={oracle_home}
export PATH=$ORACLE_HOME/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin:$PATH

echo "Executing SQL on database: $ORACLE_SID"

sqlplus -S / as sysdba <<EOF
SET LINESIZE 200
SET PAGESIZE 50
{sql_command}
EXIT;
EOF
"""
            
            # Create and execute the script
            script_name = f"/tmp/oracle_sql_{oracle_sid}_{int(time.time())}.sh"
            create_cmd = f"cat > {script_name} << 'EOSCRIPT'\n{sql_script}\nEOSCRIPT"
            success, stdout, stderr = self.execute_command(create_cmd, timeout=30, use_bash=False)
            
            if success:
                # Make executable and run
                self.execute_command(f"chmod +x {script_name}", timeout=10)
                success, stdout, stderr = self.execute_command(script_name, timeout=60, use_bash=False)
                
                # Clean up
                self.execute_command(f"rm -f {script_name}", timeout=10)
            
            # Only disconnect if we created the connection
            if connection_created:
                self.disconnect()
            
            return {
                "success": success,
                "stdout": stdout,
                "stderr": stderr,
                "error": stderr if not success else None
            }
            
        except Exception as e:
            self.disconnect()
            return {"success": False, "error": str(e)}
    
    def rename_cwallet_file(self, wallet_path: str, reuse_connection: bool = False) -> Dict[str, any]:
        """Rename cwallet.sso file to disable auto-login"""
        try:
            # Handle connection reuse
            connection_created = False
            if not reuse_connection or not self.is_connected():
                if not self.ensure_connected():
                    return {"success": False, "error": "SSH connection failed"}
                connection_created = True
            
            # Check if file exists
            check_cmd = f"ls -la {wallet_path}/cwallet.sso 2>&1"
            success, stdout, stderr = self.execute_command(check_cmd, timeout=30)
            
            if not success or "No such file" in stdout or "No such file" in stderr:
                return {"success": False, "error": f"cwallet.sso not found at {wallet_path}"}
            
            # Create timestamped backup
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_cmd = f"cp {wallet_path}/cwallet.sso {wallet_path}/cwallet.sso.backup.{timestamp}"
            success, stdout, stderr = self.execute_command(backup_cmd, timeout=30)
            if not success:
                logger.warning(f"Backup creation failed: {stderr}")
            
            # Rename the file
            rename_cmd = f"mv {wallet_path}/cwallet.sso {wallet_path}/cwallet.sso.bak"
            success, stdout, stderr = self.execute_command(rename_cmd, timeout=30)
            
            # Verify rename
            verify_cmd = f"ls -la {wallet_path}/cwallet.sso* 2>&1"
            verify_success, verify_stdout, verify_stderr = self.execute_command(verify_cmd, timeout=30)
            
            # Only disconnect if we created the connection
            if connection_created:
                self.disconnect()
            
            return {
                "success": success,
                "stdout": stdout,
                "stderr": stderr,
                "verification": verify_stdout,
                "error": stderr if not success else None
            }
            
        except Exception as e:
            self.disconnect()
            return {"success": False, "error": str(e)}
    
    def restore_cwallet_file(self, wallet_path: str, reuse_connection: bool = False) -> Dict[str, any]:
        """Restore cwallet.sso file to re-enable auto-login"""
        try:
            # Handle connection reuse
            connection_created = False
            if not reuse_connection or not self.is_connected():
                if not self.ensure_connected():
                    return {"success": False, "error": "SSH connection failed"}
                connection_created = True
            
            # Check if backup exists
            check_cmd = f"ls -la {wallet_path}/cwallet.sso.bak 2>&1"
            success, stdout, stderr = self.execute_command(check_cmd, timeout=30)
            
            if not success or "No such file" in stdout or "No such file" in stderr:
                return {"success": False, "error": f"cwallet.sso.bak not found at {wallet_path}"}
            
            # Check if cwallet.sso already exists
            check_existing = f"ls -la {wallet_path}/cwallet.sso 2>&1"
            exists_success, exists_stdout, exists_stderr = self.execute_command(check_existing, timeout=30)
            
            if exists_success and "No such file" not in exists_stdout:
                # File already exists, create backup before overwriting
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                backup_cmd = f"mv {wallet_path}/cwallet.sso {wallet_path}/cwallet.sso.old.{timestamp}"
                self.execute_command(backup_cmd, timeout=30)
            
            # Restore the file
            restore_cmd = f"mv {wallet_path}/cwallet.sso.bak {wallet_path}/cwallet.sso"
            success, stdout, stderr = self.execute_command(restore_cmd, timeout=30)
            
            # Verify restore
            verify_cmd = f"ls -la {wallet_path}/cwallet.sso* 2>&1"
            verify_success, verify_stdout, verify_stderr = self.execute_command(verify_cmd, timeout=30)
            
            # Only disconnect if we created the connection
            if connection_created:
                self.disconnect()
            
            return {
                "success": success,
                "stdout": stdout,
                "stderr": stderr,
                "verification": verify_stdout,
                "error": stderr if not success else None
            }
            
        except Exception as e:
            self.disconnect()
            return {"success": False, "error": str(e)}
    
    def check_oracle_status(self, oracle_sid: str, oracle_home: str = None, reuse_connection: bool = False) -> Dict[str, any]:
        """Check Oracle database status for a specific SID"""
        try:
            # Handle connection reuse
            connection_created = False
            if not reuse_connection or not self.is_connected():
                if not self.ensure_connected():
                    return {"success": False, "error": "SSH connection failed"}
                connection_created = True
            
            oracle_home = oracle_home or "/opt/oracle/product/21c/dbhome_1"
            
            # Create status check script
            status_script = fr"""#!/bin/bash
# Clear environment
unset ORACLE_SID
unset ORACLE_HOME

# Set specific environment
export ORACLE_SID={oracle_sid}
export ORACLE_HOME={oracle_home}
export PATH=$ORACLE_HOME/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin:$PATH

echo "Checking status for database: $ORACLE_SID"

# Check if instance is running
ps -ef | grep pmon | grep {oracle_sid} | grep -v grep
if [ $? -eq 0 ]; then
    echo "Database process is running"
    
    # Get detailed status from SQL*Plus
    sqlplus -S / as sysdba <<EOF
SET LINESIZE 200
COLUMN INSTANCE_NAME FORMAT A20
COLUMN STATUS FORMAT A15
COLUMN DATABASE_STATUS FORMAT A15
SELECT INSTANCE_NAME, STATUS, DATABASE_STATUS FROM V\$INSTANCE;
SELECT NAME, OPEN_MODE FROM V\$DATABASE;
SELECT NAME, OPEN_MODE FROM V\$PDBS;
EXIT;
EOF
else
    echo "Database process is not running"
fi
"""
            
            # Execute status check
            script_name = f"/tmp/check_oracle_{oracle_sid}_{int(time.time())}.sh"
            create_cmd = f"cat > {script_name} << 'EOSCRIPT'\n{status_script}\nEOSCRIPT"
            success, stdout, stderr = self.execute_command(create_cmd, timeout=30, use_bash=False)
            
            if success:
                self.execute_command(f"chmod +x {script_name}", timeout=10)
                success, stdout, stderr = self.execute_command(script_name, timeout=60, use_bash=False)
                self.execute_command(f"rm -f {script_name}", timeout=10)
            
            # Only disconnect if we created the connection
            if connection_created:
                self.disconnect()
            
            return {
                "success": success,
                "status": stdout if success else None,
                "error": stderr if not success else None
            }
            
        except Exception as e:
            self.disconnect()
            return {"success": False, "error": str(e)}
    
    def __enter__(self):
        """Context manager entry - establish connection"""
        if not self.ensure_connected():
            raise RuntimeError("Failed to establish SSH connection")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close connection"""
        self.disconnect()
        return False
    
    @contextmanager
    def persistent_connection(self):
        """Context manager for maintaining a persistent connection across multiple operations"""
        try:
            if not self.ensure_connected():
                raise RuntimeError("Failed to establish SSH connection")
            yield self
        finally:
            self.disconnect()