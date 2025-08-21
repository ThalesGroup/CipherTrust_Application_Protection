# Thales CipherTrust Data Security Platform CAKM MCP Server
[![Trust Score](https://archestra.ai/mcp-catalog/api/badge/quality/sanyambassi/thales-cdsp-cakm-mcp-server)](https://archestra.ai/mcp-catalog/sanyambassi__thales-cdsp-cakm-mcp-server)

A Model Context Protocol (MCP) server for Database EKM/TDE operations using CipherTrust Application Key Management (CAKM).

## 🔑 Features

- **Resource-Based Management**: Tools are organized by the database objects they manage (e.g., keys, encryption, wallets), not just by actions.
- **Operational Grouping**: Each tool exposes multiple `operations` (e.g., `create`, `list`, `rotate`) for comprehensive lifecycle management.
- **Unified Status & Auditing**: A single tool (`status_tde_ekm`) provides health, compliance, and configuration monitoring across all supported databases.
- **Advanced Oracle TDE Detection**: Intelligent detection of Oracle TDE configurations including:
  - **HSM-only TDE**: Direct HSM wallet usage
  - **HSM with Auto-login**: Forward migrated configurations (HSM primary, auto-login secondary)  
  - **FILE wallet TDE**: Password-based software wallets
  - **FILE with Auto-login**: Standard or reverse migrated configurations
  - **Migration Status Recognition**: Automatically identifies forward/reverse migration states based on wallet order and types
- **Database TDE Operations**: Encrypt, decrypt, and manage TDE on multiple database types.
- **CipherTrust Integration**: Seamless integration with CipherTrust Manager via CAKM EKM.
- **Multi-Database Support**: SQL Server and Oracle Database.
- **Key Rotation**: Automated encryption key rotation with key management on Thales CipherTrust Manager.

> **🎥 [Watch Demo Video](https://www.youtube.com/watch?v=5GezP4_CEyY)** - See the MCP server in action managing database encryption

## 🚀 Quick Start

### Clone the Repository

```bash
# Clone the repository
git clone https://github.com/sanyambassi/thales-cdsp-cakm-mcp-server.git
cd thales-cdsp-cakm-mcp-server
```

### Installation

```bash
# Install dependencies
uv venv && source .venv/bin/activate  # Linux/Mac
# uv venv && .venv\Scripts\activate   # Windows
uv pip install -e .

# Configure (copy the example configuration)
# Note: Create your own .env file with database connection details
# See docs/PREREQUISITES.md for configuration examples

# Test connections
uv run python -m database_tde_server --test-connections
```

### Usage

```bash
# Start the MCP server
uv run python -m database_tde_server
```

## 📦 Installing `uv`

This project uses `uv` to manage dependencies and run scripts. Please install it using one of the methods below.

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Linux, macOS, and other shells:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

For more information, visit the [uv installation guide](https://github.com/astral-sh/uv#installation).


## 🔧 Available Tools

- **Core Tools**
    - `list_database_connections()`: Lists all configured database connections.
- **Unified Status & Auditing**
    - `status_tde_ekm()`: Provides a unified interface to monitor the health, configuration, and compliance of TDE across both SQL Server and Oracle.
- **SQL Server Tools**
    - `manage_sql_ekm_objects()`: Manages EKM providers, credentials, and their associated server logins.
    - `manage_sql_keys()`: Manages the lifecycle of cryptographic keys (Asymmetric Master Keys and DEKs), including creation, listing, dropping, and rotation.
    - `manage_sql_encryption()`: Encrypts or decrypts one or more SQL Server databases.
- **Oracle Tools**
    - `manage_oracle_tde_deployment()`: Handles high-level TDE deployment workflows like initial setup or migration to/from an HSM.
    - `manage_oracle_configuration()`: Manages TDE-related database parameters.
    - `manage_oracle_wallet()`: Performs all wallet-specific actions (open, close, backup, manage auto-login).
    - `manage_oracle_keys()`: Manages the lifecycle of Master Encryption Keys (MEKs), including rotation and listing.
    - `manage_oracle_tablespace_encryption()`: Manages the encryption and decryption of specific tablespaces.

## 🤖 AI Assistant Integration

Add to your AI assistant configuration:

### Claude Desktop
```json
{
  "mcpServers": {
    "database-tde": {
      "command": "uv",
      "args": ["run", "python", "-m", "database_tde_server"],
      "cwd": "/path/to/cakm-mcp-server-sql-oracle",
      "env": {
        "DB_TDE_SERVER_NAME": "database-tde-mcp",
        "DB_TDE_LOG_LEVEL": "INFO",
        "DB_TDE_DATABASE_CONNECTIONS": "[{\"name\":\"prod_sql\",\"db_type\":\"sqlserver\",\"host\":\"sql-prod.company.com\",\"port\":1433,\"username\":\"tde_admin\",\"password\":\"secure_password\"},{\"name\":\"oracle_cdb1\",\"db_type\":\"oracle\",\"host\":\"oracle-prod.company.com\",\"port\":1521,\"username\":\"sys\",\"password\":\"oracle_password\",\"oracle_config\":{\"oracle_home\":\"/u01/app/oracle/product/21.0.0/dbhome_1\",\"oracle_sid\":\"cdb1\",\"service_name\":\"orcl\",\"mode\":\"SYSDBA\",\"wallet_root\":\"/opt/oracle/wallet\"},\"ssh_config\":{\"host\":\"oracle-prod.company.com\",\"username\":\"oracle\",\"private_key_path\":\"/path/to/private-key.pem\",\"port\":22,\"timeout\":30}}]"
      }
    }
  }
}
```

### Cursor AI (mcp.json)
```json
{
  "mcpServers": {
    "database-tde": {
      "command": "uv",
      "args": ["run", "python", "-m", "database_tde_server"],
      "cwd": "/path/to/cakm-mcp-server-sql-oracle",
      "env": {
        "DB_TDE_SERVER_NAME": "database-tde-mcp",
        "DB_TDE_LOG_LEVEL": "INFO",
        "DB_TDE_DATABASE_CONNECTIONS": "[{\"name\":\"prod_sql\",\"db_type\":\"sqlserver\",\"host\":\"sql-prod.company.com\",\"port\":1433,\"username\":\"tde_admin\",\"password\":\"secure_password\"},{\"name\":\"oracle_cdb1\",\"db_type\":\"oracle\",\"host\":\"oracle-prod.company.com\",\"port\":1521,\"username\":\"sys\",\"password\":\"oracle_password\",\"oracle_config\":{\"oracle_home\":\"/u01/app/oracle/product/21.0.0/dbhome_1\",\"oracle_sid\":\"cdb1\",\"service_name\":\"orcl\",\"mode\":\"SYSDBA\",\"wallet_root\":\"/opt/oracle/wallet\"},\"ssh_config\":{\"host\":\"oracle-prod.company.com\",\"username\":\"oracle\",\"private_key_path\":\"/path/to/private-key.pem\",\"port\":22,\"timeout\":30}}]"
      }
    }
  }
}
```

### Gemini CLI (settings.json)
```json
{
  "mcpServers": {
    "database-tde": {
      "command": "uv",
      "args": ["run", "python", "-m", "database_tde_server"],
      "cwd": "/path/to/cakm-mcp-server-sql-oracle",
      "env": {
        "DB_TDE_SERVER_NAME": "database-tde-mcp",
        "DB_TDE_LOG_LEVEL": "INFO",
        "DB_TDE_DATABASE_CONNECTIONS": "[{\"name\":\"prod_sql\",\"db_type\":\"sqlserver\",\"host\":\"sql-prod.company.com\",\"port\":1433,\"username\":\"tde_admin\",\"password\":\"secure_password\"},{\"name\":\"oracle_cdb1\",\"db_type\":\"oracle\",\"host\":\"oracle-prod.company.com\",\"port\":1521,\"username\":\"sys\",\"password\":\"oracle_password\",\"oracle_config\":{\"oracle_home\":\"/u01/app/oracle/product/21.0.0/dbhome_1\",\"oracle_sid\":\"cdb1\",\"service_name\":\"orcl\",\"mode\":\"SYSDBA\",\"wallet_root\":\"/opt/oracle/wallet\"},\"ssh_config\":{\"host\":\"oracle-prod.company.com\",\"username\":\"oracle\",\"private_key_path\":\"/path/to/private-key.pem\",\"port\":22,\"timeout\":30}}]"
      }
    }
  }
}
```

### Architecture Overview
```
MCP Server ↔ Database Server ↔ CAKM Provider/Library ↔ CipherTrust Manager
```

**Note**: This MCP server communicates only with database servers. The CAKM providers installed on database servers handle all communication with CipherTrust Manager.

### Oracle TDE Enablement Logic

The server uses Oracle-documented logic to determine TDE status based on wallet configurations and TDE parameters:

**✅ TDE is ENABLED when:**
- Any wallet shows `OPEN` status AND Master Encryption Keys (MEKs) exist

**📊 Wallet Order Types (from Oracle V$ENCRYPTION_WALLET):**
- **SINGLE**: Only one wallet type configured
- **PRIMARY**: Primary wallet in a dual-wallet configuration  
- **SECONDARY**: Secondary wallet in a dual-wallet configuration

**🔧 TDE Configuration Parameter Values:**
- **FILE**: TDE configured to use FILE wallets only
- **HSM**: TDE configured to use HSM wallets only
- **HSM|FILE**: TDE configured with HSM as primary, FILE as secondary
- **FILE|HSM**: TDE configured with FILE as primary, HSM as secondary

**📊 Supported TDE Scenarios:**
1. **HSM-only TDE**: HSM wallet OPEN (SINGLE), TDE_CONFIGURATION=HSM
2. **HSM with Auto-login (Migrated)**: HSM wallet OPEN (PRIMARY), auto-login wallet OPEN (SECONDARY), TDE_CONFIGURATION=HSM|FILE
3. **HSM with Auto-login (Not Migrated)**: HSM wallet OPEN (PRIMARY), auto-login wallet OPEN_NO_MASTER_KEY (SECONDARY), TDE_CONFIGURATION=HSM|FILE
4. **FILE wallet TDE**: PASSWORD wallet OPEN (SINGLE), TDE_CONFIGURATION=FILE
5. **FILE with Auto-login (Reverse Migrated)**: PASSWORD wallet OPEN (PRIMARY), auto-login wallet OPEN (SECONDARY), TDE_CONFIGURATION=FILE|HSM
6. **FILE with Auto-login**: PASSWORD wallet OPEN (PRIMARY), auto-login wallet OPEN (SECONDARY), TDE_CONFIGURATION=FILE

**🔍 Migration Detection Logic:**
- **Forward Migration**: HSM becomes PRIMARY (HSM|FILE configuration) → Database migrated from FILE to HSM
- **Reverse Migration**: FILE becomes PRIMARY (FILE|HSM configuration) → Database migrated from HSM back to FILE
- **WALLET_ORDER** and **TDE_CONFIGURATION** are correlated to determine the migration state

**📋 Status Information:**
- TDE configuration parameters validate the expected wallet hierarchy
- Wallet order and TDE_CONFIGURATION together determine the deployment scenario

## 🔧 Oracle TDE Operations Guide

The `oracle_tde_deployment` tool provides different operations for various TDE setup scenarios:

### Operation Types & Use Cases

**1. HSM-Only TDE Setup (No Auto-login)**
```json
{
  "oracle_connection": "oracle_cdb2",
  "operation": "setup_hsm_only",
  "ciphertrust_username": "tdeuser",
  "ciphertrust_password": "Thales123!",
  "ciphertrust_domain": "TDE",
  "auto_restart": true
}
```
- **Use when**: "Skip auto-login wallet creation" or "HSM only"
- **Creates**: HSM keystore only
- **Result**: Manual wallet opening required after restarts
- **No software_wallet_password needed**

**2. Complete TDE Setup (HSM + Auto-login)**
```json
{
  "oracle_connection": "oracle_cdb2",
  "operation": "setup_hsm_with_autologin",
  "ciphertrust_username": "tdeuser", 
  "ciphertrust_password": "Thales123!",
  "ciphertrust_domain": "TDE",
  "software_wallet_password": "Thales123!",
  "auto_restart": true
}
```
- **Use when**: "Set up complete TDE with auto-login"
- **Creates**: HSM + software wallet + auto-login keystore
- **Result**: Database starts automatically without manual intervention
- **Requires software_wallet_password**

**3. Add Auto-login to Existing TDE**
```json
{
  "oracle_connection": "oracle_cdb2",
  "operation": "add_autologin",
  "ciphertrust_username": "tdeuser",
  "ciphertrust_password": "Thales123!", 
  "ciphertrust_domain": "TDE",
  "software_wallet_password": "Thales123!",
  "auto_restart": true
}
```
- **Use when**: Database has HSM TDE, want to add auto-login
- **Creates**: Software wallet + auto-login for existing HSM setup
- **Requires software_wallet_password**

**4. Check TDE Status**
```json
{
  "oracle_connection": "oracle_cdb2",
  "operation": "get_tde_status"
}
```
- **Use when**: Want to see current TDE configuration
- **Returns**: Comprehensive wallet and TDE status
- **No credentials needed**

### Quick Reference
- **"Skip auto-login"** → Use `setup_hsm_only`
- **"Complete TDE setup"** → Use `setup_hsm_with_autologin`  
- **"Add auto-login to existing"** → Use `add_autologin`
- **"Check what I have"** → Use `get_tde_status`

**📚 References:**
- [Oracle V$ENCRYPTION_WALLET Documentation](https://docs.oracle.com/en/database/oracle/oracle-database/19/refrn/V-ENCRYPTION_WALLET.html)
- [Oracle TDE_CONFIGURATION Parameter](https://docs.oracle.com/en/database/oracle/oracle-database/19/refrn/TDE_CONFIGURATION.html)

### Example Prompts
```
"Show me the TDE status of all my databases"
"For my 'prod_sql' connection, list all the asymmetric keys using the 'manage_sql_keys' tool"
"Rotate the master key on the 'Db05' database using the 'prod_sql' connection"
"Encrypt the 'SalesDB' database on my 'prod_sql' server"
"What is the wallet status for my 'oracle_cdb2' connection?"
```

### Important Notes
- **Automatic Database Restarts**: When specified in prompts, MCP tools can automatically restart Oracle databases as part of TDE operations
- **SSH Authentication**: Oracle connections support both private key and password authentication
  - Private key: Use `"private_key_path": "/path/to/key.pem"` in ssh_config
  - Password: Use `"password": "your_ssh_password"` in ssh_config (instead of private_key_path)
- **Supported Databases**: Microsoft SQL Server and Oracle Database are supported

## 📚 Documentation

- [Prerequisites](docs/PREREQUISITES.md) - System requirements and setup
- [Testing Guide](docs/TESTING.md) - Comprehensive testing procedures
- [Example Prompts](docs/EXAMPLE_PROMPTS.md) - Ready-to-use testing prompts for SQL Server and Oracle

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
