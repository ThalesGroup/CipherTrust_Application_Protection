# Database TDE MCP Server - Testing Guide

## Starting the Server

```bash
# Start the server for manual testing
uv run python -m database_tde_server

# Test all database connections defined in config
uv run python -m database_tde_server --test-connections
```

## MCP Inspector Testing

```bash
# MCP Inspector UI testing (opens browser)
npx @modelcontextprotocol/inspector uv run python -m database_tde_server

# MCP Inspector CLI (handles protocol flow automatically)
npx @modelcontextprotocol/inspector --cli \
  uv run python -m database_tde_server \
  --method tools/list
```

## MCP Protocol Flow

When testing with raw JSON-RPC, you must follow this exact sequence:

```json
// Step 1: Initialize the server with protocol information
{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "clientInfo": {"name": "test-client", "version": "1.0.0"}, "capabilities": {"tools": {}}}}

// Step 2: Send initialized notification (Server does not respond)
{"jsonrpc": "2.0", "method": "notifications/initialized"}

// Step 3: Now you can list available tools
{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}

// Step 4: Call a specific tool
{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "list_database_connections", "arguments": {}}}
```

## Testing SQL Server Features

### SQL Server Key Management

```bash
# List all SQL Server cryptographic keys
npx @modelcontextprotocol/inspector --cli \
  uv run python -m database_tde_server \
  --method tools/call \
  --tool-name manage_sql_keys \
  --tool-args '{"operation": "list", "sql_connection": "prod_sql"}'

# Create a new SQL Server asymmetric key
npx @modelcontextprotocol/inspector --cli \
  uv run python -m database_tde_server \
  --method tools/call \
  --tool-name manage_sql_keys \
  --tool-args '{"operation": "create", "sql_connection": "prod_sql", "key_name": "TDE_Test_Key", "provider_name": "CipherTrustEKM", "key_type": "RSA", "key_size": "2048"}'

# Rotate the master key for a database
npx @modelcontextprotocol/inspector --cli \
  uv run python -m database_tde_server \
  --method tools/call \
  --tool-name manage_sql_keys \
  --tool-args '{"operation": "rotate_master", "sql_connection": "prod_sql", "database_name": "TestDB", "new_key_name": "TDE_New_Key", "provider_name": "CipherTrustEKM", "key_type": "RSA", "key_size": "2048", "ciphertrust_username": "admin", "ciphertrust_password": "password", "ciphertrust_domain": "root"}'

# Rotate the database encryption key
npx @modelcontextprotocol/inspector --cli \
  uv run python -m database_tde_server \
  --method tools/call \
  --tool-name manage_sql_keys \
  --tool-args '{"operation": "rotate_dek", "sql_connection": "prod_sql", "database_name": "TestDB"}'

# Drop an unused key
npx @modelcontextprotocol/inspector --cli \
  uv run python -m database_tde_server \
  --method tools/call \
  --tool-name manage_sql_keys \
  --tool-args '{"operation": "drop", "sql_connection": "prod_sql", "key_name": "Old_Key", "key_type": "RSA", "remove_from_provider": false}'

# Drop all unused keys
npx @modelcontextprotocol/inspector --cli \
  uv run python -m database_tde_server \
  --method tools/call \
  --tool-name manage_sql_keys \
  --tool-args '{"operation": "drop_unused", "sql_connection": "prod_sql"}'
```

### SQL Server EKM Management

```bash
# List SQL Server EKM providers
npx @modelcontextprotocol/inspector --cli \
  uv run python -m database_tde_server \
  --method tools/call \
  --tool-name manage_sql_ekm_objects \
  --tool-args '{"operation": "manage_ekm_providers", "sql_connection": "prod_sql"}'

# Manage SQL Server credentials
npx @modelcontextprotocol/inspector --cli \
  uv run python -m database_tde_server \
  --method tools/call \
  --tool-name manage_sql_ekm_objects \
  --tool-args '{"operation": "manage_credentials", "sql_connection": "prod_sql", "credential_name": "TDE_Credential", "show_mappings": true}'

# Manage SQL Server logins
npx @modelcontextprotocol/inspector --cli \
  uv run python -m database_tde_server \
  --method tools/call \
  --tool-name manage_sql_ekm_objects \
  --tool-args '{"operation": "manage_logins", "sql_connection": "prod_sql", "tde_only": true}'
```

### SQL Server Database Encryption

```bash
# Encrypt a SQL Server database
npx @modelcontextprotocol/inspector --cli \
  uv run python -m database_tde_server \
  --method tools/call \
  --tool-name manage_sql_encryption \
  --tool-args '{"operation": "encrypt", "sql_connection": "prod_sql", "database_names": "TestDB", "provider_name": "CipherTrustEKM", "ciphertrust_username": "admin", "ciphertrust_password": "password", "key_name": "TDE_Key", "ciphertrust_domain": "root"}'

# Encrypt multiple SQL Server databases
npx @modelcontextprotocol/inspector --cli \
  uv run python -m database_tde_server \
  --method tools/call \
  --tool-name manage_sql_encryption \
  --tool-args '{"operation": "encrypt", "sql_connection": "prod_sql", "database_names": "DB1,DB2,DB3", "provider_name": "CipherTrustEKM", "ciphertrust_username": "admin", "ciphertrust_password": "password", "key_name": "TDE_Key", "ciphertrust_domain": "root"}'

# Encrypt all user databases
npx @modelcontextprotocol/inspector --cli \
  uv run python -m database_tde_server \
  --method tools/call \
  --tool-name manage_sql_encryption \
  --tool-args '{"operation": "encrypt", "sql_connection": "prod_sql", "database_names": "all databases", "provider_name": "CipherTrustEKM", "ciphertrust_username": "admin", "ciphertrust_password": "password", "key_name": "TDE_Key", "ciphertrust_domain": "root"}'

# Decrypt a SQL Server database
npx @modelcontextprotocol/inspector --cli \
  uv run python -m database_tde_server \
  --method tools/call \
  --tool-name manage_sql_encryption \
  --tool-args '{"operation": "decrypt", "sql_connection": "prod_sql", "database_names": "TestDB"}'

# Decrypt all encrypted databases
npx @modelcontextprotocol/inspector --cli \
  uv run python -m database_tde_server \
  --method tools/call \
  --tool-name manage_sql_encryption \
  --tool-args '{"operation": "decrypt", "sql_connection": "prod_sql", "database_names": "all encrypted databases"}'
```

### SQL Server Status and Assessment

```bash
# Get comprehensive SQL Server TDE assessment
npx @modelcontextprotocol/inspector --cli \
  uv run python -m database_tde_server \
  --method tools/call \
  --tool-name status_tde_ekm \
  --tool-args '{"operation": "assess_sql", "connection_name": "prod_sql"}'

# Generate SQL Server TDE compliance report
npx @modelcontextprotocol/inspector --cli \
  uv run python -m database_tde_server \
  --method tools/call \
  --tool-name status_tde_ekm \
  --tool-args '{"operation": "compliance_report", "connection_name": "prod_sql"}'

# Export TDE configuration
npx @modelcontextprotocol/inspector --cli \
  uv run python -m database_tde_server \
  --method tools/call \
  --tool-name status_tde_ekm \
  --tool-args '{"operation": "export_config", "connection_name": "prod_sql", "format": "json"}'
```

## Testing Oracle TDE Features

### General Oracle TDE Testing

```bash
# Test Oracle TDE comprehensive assessment
npx @modelcontextprotocol/inspector --cli \
  uv run python -m database_tde_server \
  --method tools/call \
  --tool-name status_tde_ekm \
  --tool-args '{"operation": "assess_oracle", "connection_name": "oracle_cdb1"}'

# Test Oracle wallet status
npx @modelcontextprotocol/inspector --cli \
  uv run python -m database_tde_server \
  --method tools/call \
  --tool-name manage_oracle_wallet \
  --tool-args '{"operation": "status", "oracle_connection": "oracle_cdb1", "container": "CDB$ROOT"}'

# Test Oracle container listing
npx @modelcontextprotocol/inspector --cli \
  uv run python -m database_tde_server \
  --method tools/call \
  --tool-name status_tde_ekm \
  --tool-args '{"operation": "list_containers", "connection_name": "oracle_cdb1"}'

# Test Oracle encryption status per container
npx @modelcontextprotocol/inspector --cli \
  uv run python -m database_tde_server \
  --method tools/call \
  --tool-name status_tde_ekm \
  --tool-args '{"operation": "list_tablespaces", "connection_name": "oracle_cdb1", "database_name": "CDB$ROOT", "encrypted_only": true}'

# Test Oracle MEK listing (filtered by database)
npx @modelcontextprotocol/inspector --cli \
  uv run python -m database_tde_server \
  --method tools/call \
  --tool-name manage_oracle_keys \
  --tool-args '{"operation": "list", "oracle_connection": "oracle_cdb1", "container": "CDB$ROOT"}'

# Test Oracle TDE configuration parameters
npx @modelcontextprotocol/inspector --cli \
  uv run python -m database_tde_server \
  --method tools/call \
  --tool-name manage_oracle_configuration \
  --tool-args '{"operation": "get", "oracle_connection": "oracle_cdb1"}'
```

### Test Oracle Tablespace Encryption

```bash
# Test Oracle tablespace encryption status
npx @modelcontextprotocol/inspector --cli \
  uv run python -m database_tde_server \
  --method tools/call \
  --tool-name manage_oracle_tablespace_encryption \
  --tool-args '{"operation": "status", "oracle_connection": "oracle_cdb1", "tablespace_name": "PLAINTEXT_TS", "container": "PDB1"}'

# Test Oracle tablespace encryption
npx @modelcontextprotocol/inspector --cli \
  uv run python -m database_tde_server \
  --method tools/call \
  --tool-name manage_oracle_tablespace_encryption \
  --tool-args '{"operation": "encrypt", "oracle_connection": "oracle_cdb1", "tablespaces": "PLAINTEXT_TS", "container": "PDB1"}'
```

### Test Oracle Key Management

```bash
# Test Oracle MEK rotation with auto-login/HSM wallet (no password required)
npx @modelcontextprotocol/inspector --cli \
  uv run python -m database_tde_server \
  --method tools/call \
  --tool-name manage_oracle_keys \
  --tool-args '{"operation": "rotate", "oracle_connection": "oracle_cdb1", "container": "CDB$ROOT", "backup_tag": "auto_login_rotation_test"}'

# Test Oracle MEK rotation with password-protected wallet
npx @modelcontextprotocol/inspector --cli \
  uv run python -m database_tde_server \
  --method tools/call \
  --tool-name manage_oracle_keys \
  --tool-args '{"operation": "rotate", "oracle_connection": "oracle_cdb1", "container": "CDB$ROOT", "wallet_password": "your_wallet_password", "backup_tag": "password_protected_rotation_test"}'
```

## Testing with Raw JSON-RPC

To manually test features with raw JSON-RPC, follow this sequence:

```json
// Step 1: Initialize the server
{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "clientInfo": {"name": "test-client", "version": "1.0.0"}, "capabilities": {"tools": {}}}}

// Step 2: Send initialized notification
{"jsonrpc": "2.0", "method": "notifications/initialized"}

// Step 3: List available tools
{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}

// Step 4: Test SQL Server key listing
{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "manage_sql_keys", "arguments": {"operation": "list", "sql_connection": "prod_sql"}}}

// Step 5: Test Oracle key listing
{"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "manage_oracle_keys", "arguments": {"operation": "list", "oracle_connection": "oracle_cdb1", "container": "CDB$ROOT"}}}
```
