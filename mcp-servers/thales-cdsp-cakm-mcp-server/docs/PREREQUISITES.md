# Prerequisites

## System Requirements

- **Python**: 3.11 or higher
- **Operating System**: Windows, Linux, or macOS
- **Memory**: Minimum 512MB RAM available
- **Network**: Access to database servers and CipherTrust Manager

## Development & Build Tools

- **uv**: An extremely fast Python package installer and resolver, used to manage dependencies and run scripts for this project.
  - See installation instructions in the main [README.md](../README.md#-installing-uv).

## Database Requirements

### SQL Server
- **Version**: SQL Server 2016 or later
- **Permissions**: 
  - `sysadmin` role or `db_owner` on target databases
- **Features**: TDE must be available (Enterprise/Developer edition)
- **CAKM Provider**: 
  - CAKM provider must be pre-installed on SQL Server
  - EKM Cryptographic provider must be created before MCP server operations
  - CAKM properties file must be configured with CipherTrust Manager details

### Oracle Database
- **Version**: Oracle 12c or later
- **Permissions**:
  - `SYSDBA` privileges for TDE operations
  - `ADMINISTER KEY MANAGEMENT` system privilege
- **Features**: Advanced Security Option (ASO) license required
- **CAKM Library**: 
  - CAKM library must be pre-installed on Oracle Database server
  - CAKM properties file must be configured with CipherTrust Manager details
  - Library must be properly integrated with Oracle Wallet management


## CipherTrust Manager Requirements

- **CipherTrust Manager version v2.11 or higher**
- **Valid CAKM License insalled on CipherTrust manager**

### CAKM (CipherTrust Application Key Management)
- **Version**: CAKM version 8.x
- **License**: CAKM license installed on CipherTrust manager
- **Network**: Network connectivity to CipherTrust Manager from the database server on NAE interface
- **Authentication**: Valid CipherTrust Manager credentials

## Software Dependencies

### Python Packages
All Python dependencies are managed via `pyproject.toml` and will be installed automatically:

- `pyodbc>=5.0.0` - SQL Server connectivity
- `oracledb>=1.0.0` - Oracle Database connectivity  
- `paramiko>=2.7.0` - SSH connectivity for Oracle operations
- `mcp[cli]>=1.0.0` - Model Context Protocol framework
- `pydantic>=2.0.0` - Data validation and settings

### Database Drivers and Client Libraries

#### SQL Server Connection Requirements
- **Driver**: Microsoft ODBC Driver 17 or 18 for SQL Server
- **Python Package**: `pyodbc` (automatically installed with MCP server)
- **Supported Platforms**: Windows, Linux, macOS

**Installation:**

**Windows:**
```bash
# Download and install from Microsoft:
# https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
# ODBC Driver 18 for SQL Server (recommended)
```

**Linux (Ubuntu/Debian):**
```bash
# Install Microsoft ODBC Driver 18
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list | sudo tee /etc/apt/sources.list.d/msprod.list
sudo apt-get update
sudo apt-get install -y msodbcsql18 unixodbc-dev
```

**Linux (RHEL/CentOS):**
```bash
# Install Microsoft ODBC Driver 18
sudo curl -o /etc/yum.repos.d/msprod.repo https://packages.microsoft.com/config/rhel/8/prod.repo
sudo yum remove unixODBC-utf16 unixODBC-utf16-devel
sudo yum install -y msodbcsql18 unixODBC-devel
```

**macOS:**
```bash
# Install via Homebrew
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
brew install msodbcsql18 mssql-tools18
```

**Verify Installation:**
```bash
# Check available ODBC drivers
odbcinst -q -d
# Should show: [ODBC Driver 18 for SQL Server]

# Test Python connectivity
python -c "import pyodbc; print('SQL Server drivers:', [x for x in pyodbc.drivers() if 'SQL Server' in x])"
```

#### Oracle Connection Requirements
- **Client**: Oracle Instant Client 21c or later (optional - see thin mode below)
- **Python Package**: `oracledb>=1.0.0` (automatically installed with MCP server)
- **Supported Platforms**: Windows, Linux, macOS

**Installation:**

**Option 1: Oracle Instant Client (Recommended)**
```bash
# Download from Oracle website:
# https://www.oracle.com/database/technologies/instant-client/downloads.html

# Linux example:
wget https://download.oracle.com/otn_software/linux/instantclient/2110000/instantclient-basic-linux.x64-21.10.0.0.0dbru.zip
unzip instantclient-basic-linux.x64-21.10.0.0.0dbru.zip
sudo mv instantclient_21_10 /opt/oracle/

# Set environment variables
export ORACLE_HOME=/opt/oracle/instantclient_21_10
export LD_LIBRARY_PATH=$ORACLE_HOME:$LD_LIBRARY_PATH
export PATH=$ORACLE_HOME:$PATH
```

**Option 2: python-oracledb Thick Mode (No Oracle Client Required)**
```python
# The MCP server can use oracledb in thin mode (no Oracle client needed)
# Or thick mode (requires Oracle client) for full compatibility
import oracledb
oracledb.init_oracle_client()  # Only if using thick mode
```

**Environment Variables:**
```bash
# Required for Oracle connections
export ORACLE_HOME=/path/to/oracle/client
export TNS_ADMIN=/path/to/tnsnames/directory
export LD_LIBRARY_PATH=$ORACLE_HOME/lib:$LD_LIBRARY_PATH  # Linux
export DYLD_LIBRARY_PATH=$ORACLE_HOME/lib:$DYLD_LIBRARY_PATH  # macOS
```

**Verify Installation:**
```bash
# Test Oracle client
sqlplus -v

# Test Python connectivity
python -c "import oracledb; print('Oracle client available')"

# Test with oracledb thick mode
python -c "import oracledb; oracledb.init_oracle_client(); print('Oracle thick mode available')"
```

#### Connection String Examples

**SQL Server:**
```python
# Example connection strings used by MCP server
"Driver={ODBC Driver 18 for SQL Server};Server=server.company.com;Database=master;UID=username;PWD=password;TrustServerCertificate=yes"
```

**Oracle:**
```python
# Example connection strings used by MCP server
"sys/password@server.company.com:1521/service_name AS SYSDBA"
"sys/password@(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=server.company.com)(PORT=1521))(CONNECT_DATA=(SERVICE_NAME=orcl))) AS SYSDBA"
```

#### SSH Client Requirements (Oracle Only)

- **Purpose**: Required for Oracle database restart operations during TDE setup
- **Python Package**: `paramiko>=2.7.0` (automatically installed with MCP server)
- **Authentication**: SSH key or password authentication

**SSH Key Setup:**
```bash
# Generate SSH key pair (if needed)
ssh-keygen -t rsa -b 4096 -f ~/.ssh/oracle_key

# Copy public key to Oracle server
ssh-copy-id -i ~/.ssh/oracle_key.pub oracle@oracle-server.company.com

# Test SSH connectivity
ssh -i ~/.ssh/oracle_key oracle@oracle-server.company.com "echo 'SSH connection successful'"
```



## Network Configuration

### Firewall Rules
Ensure the following ports are accessible:

- **SQL Server**: 1433 (default)
- **Oracle**: 1521 (default)
- **CipherTrust Manager**: 443 (HTTPS)
- **SSH** (for Oracle connections): 22

### SSL/TLS
- Valid SSL certificates for CipherTrust Manager
- Database SSL connections recommended

## Security Requirements
### Access Control
- Implement least-privilege access principles
- Use service accounts with minimal required permissions
- Regular access reviews and updates

## Installation Verification

After installing prerequisites, verify your setup:

```bash
# Test Python packages (automatically installed with MCP server)
python -c "import pyodbc; print('SQL Server driver available')"
python -c "import oracledb; print('Oracle client available')"
python -c "import paramiko; print('SSH connectivity available')"

# Test MCP server
uv run python -m database_tde_server --test-connections

# Test CipherTrust connectivity
curl -k https://your-ciphertrust-manager:443/api/v1/system/info
```

## CAKM Integration Setup

### SQL Server CAKM Provider Setup
1. **Install CAKM Provider**: Download and install from Thales CipherTrust Manager
   - **Official Documentation**: [Installing CAKM for Microsoft SQL Server EKM Provider](https://thalesdocs.com/ctp/con/cakm/cakm-mssql-ekm/latest/admin/cakm_mssql_ekm-installing_protectapp/index.html)
2. **Configure Properties File**: 
   ```
   # Example CAKM properties file location
   C:\Program Files\CipherTrust\CAKM\cakm_mssql_ekm.properties
   ```
3. **Create EKM Cryptographic Provider**:
   ```sql
   CREATE CRYPTOGRAPHIC PROVIDER CipherTrustEKM
   FROM FILE = 'C:\Program Files\CAKM For SQL EKM\cakm_mssql_ekm.dll'
   ```

### Oracle CAKM Library Setup
1. **Install CAKM Library**: Download and install from Thales CipherTrust Manager
   - **Official Documentation**: [Installing CAKM for Oracle TDE](https://thalesdocs.com/ctp/con/cakm/cakm-oracle-tde/latest/admin/tde-install_cakm_oracle_tde/index.html)
2. **Configure Properties File**:
   ```
   # Example CAKM properties file location
   /opt/CipherTrust/CAKM_for_Oracle_TDE/CADP_PKCS11.properties
   ```
3. **Verify Library Integration**:
   ```bash
   # Check library is properly loaded
   ldd /opt/oracle/extapi/64/hsm/CipherTrust/CAKM_for_Oracle_TDE/libcadp_pkcs11.so
   ```

## Troubleshooting Common Issues

### ODBC Driver Issues
- Ensure proper driver version is installed
- Check driver name in connection strings
- Verify system PATH includes driver location

### Oracle Connection Issues
- Verify ORACLE_HOME and TNS_ADMIN paths
- Check tnsnames.ora file configuration
- Test with sqlplus or similar tools first

### CipherTrust Connectivity
- Verify network connectivity
- Check SSL certificate validity
- Ensure proper authentication credentials

### Permission Issues
- Verify database user permissions
- Check system privileges for TDE operations
- Ensure service account has necessary rights 
