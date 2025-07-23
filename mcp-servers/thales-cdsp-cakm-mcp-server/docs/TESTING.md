# ==============================================================================
# Testing Commands Reference
# ==============================================================================

"""
🧪 TESTING COMMANDS:

# Run comprehensive test suite
# Note: Test scripts may need updating to reflect the new tool structure.
uv run python scripts/test_comprehensive.py

# Run all pytest unit tests
uv run pytest tests/ -v

# Test with coverage
uv run pytest tests/ --cov=database_tde_server --cov-report=html

# ------------------------------------------------------------------------------
# Manual & Inspector Testing
# ------------------------------------------------------------------------------

# Start the server for manual testing
uv run python -m database_tde_server

# List all available tools using raw JSON-RPC
# Then send: {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}

# MCP Inspector UI testing (opens browser)
npx @modelcontextprotocol/inspector uv run python -m database_tde_server

# MCP Inspector CLI: List all tools
npx @modelcontextprotocol/inspector --cli \
  uv run python -m database_tde_server \
  --method tools/list

# MCP Inspector CLI: Test a simple tool
npx @modelcontextprotocol/inspector --cli \
  uv run python -m database_tde_server \
  --method tools/call \
  --tool-name list_database_connections

# ------------------------------------------------------------------------------
# Testing Consolidated Tools (with --tool-args)
# ------------------------------------------------------------------------------

# Test 'manage_sql_keys' to list keys
npx @modelcontextprotocol/inspector --cli \
  uv run python -m database_tde_server \
  --method tools/call \
  --tool-name manage_sql_keys \
  --tool-args '{"operation": "list", "sql_connection": "prod_sql"}'

# Test 'status_tde_ekm' to assess a SQL database
npx @modelcontextprotocol/inspector --cli \
  uv run python -m database_tde_server \
  --method tools/call \
  --tool-name status_tde_ekm \
  --tool-args '{"operation": "assess_sql", "connection_name": "prod_sql", "database_name": "Db01"}'

# ------------------------------------------------------------------------------
# Oracle TDE Scenario Testing
# ------------------------------------------------------------------------------

# Test Oracle TDE comprehensive assessment (shows all scenarios)
npx @modelcontextprotocol/inspector --cli \
  uv run python -m database_tde_server \
  --method tools/call \
  --tool-name status_tde_ekm \
  --tool-args '{"operation": "assess_oracle", "connection_name": "oracle_cdb1"}'

# Test Oracle wallet status (detailed wallet information)
npx @modelcontextprotocol/inspector --cli \
  uv run python -m database_tde_server \
  --method tools/call \
  --tool-name manage_oracle_wallet \
  --tool-args '{"operation": "status", "oracle_connection": "oracle_cdb1", "container": "CDB$ROOT"}'

# Test Oracle container listing (shows all PDBs)
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

# Test Oracle MEK listing
npx @modelcontextprotocol/inspector --cli \
  uv run python -m database_tde_server \
  --method tools/call \
  --tool-name manage_oracle_keys \
  --tool-args '{"operation": "list", "oracle_connection": "oracle_cdb1"}'

# Test Oracle TDE configuration parameters
npx @modelcontextprotocol/inspector --cli \
  uv run python -m database_tde_server \
  --method tools/call \
  --tool-name manage_oracle_configuration \
  --tool-args '{"operation": "get", "oracle_connection": "oracle_cdb1"}'

# ------------------------------------------------------------------------------
# Oracle TDE Migration Testing
# ------------------------------------------------------------------------------

# Test Oracle TDE initial setup (HSM-only)
npx @modelcontextprotocol/inspector --cli \
  uv run python -m database_tde_server \
  --method tools/call \
  --tool-name manage_oracle_tde_deployment \
  --tool-args '{"operation": "initial_setup", "oracle_connection": "oracle_cdb1", "ciphertrust_user": "admin", "ciphertrust_password": "password", "wallet_root_path": "/opt/oracle/wallet"}'

# Test Oracle TDE migration to HSM (from FILE wallet)
npx @modelcontextprotocol/inspector --cli \
  uv run python -m database_tde_server \
  --method tools/call \
  --tool-name manage_oracle_tde_deployment \
  --tool-args '{"operation": "migrate_to_hsm", "oracle_connection": "oracle_cdb1", "ciphertrust_user": "admin", "ciphertrust_password": "password", "software_wallet_password": "wallet_pass"}'

# Test Oracle TDE reverse migration to FILE (from HSM)
npx @modelcontextprotocol/inspector --cli \
  uv run python -m database_tde_server \
  --method tools/call \
  --tool-name manage_oracle_tde_deployment \
  --tool-args '{"operation": "reverse_migrate_from_hsm", "oracle_connection": "oracle_cdb1", "ciphertrust_user": "admin", "ciphertrust_password": "password", "software_wallet_password": "new_wallet_pass"}'

# ------------------------------------------------------------------------------
# Expected Oracle TDE Scenarios in Testing:
# ------------------------------------------------------------------------------

"""
🔍 ORACLE TDE SCENARIOS TO VERIFY (Based on Oracle Documentation):

1. HSM-only TDE:
   - V$ENCRYPTION_WALLET: HSM wallet OPEN (WALLET_ORDER='SINGLE')
   - TDE_CONFIGURATION: 'KEYSTORE_CONFIGURATION=HSM' 
   - Assessment: "HSM-only TDE (SINGLE wallet)", migration_status: "hsm_only"

2. HSM with Auto-login (Forward Migrated):
   - V$ENCRYPTION_WALLET: HSM wallet OPEN (WALLET_ORDER='PRIMARY'), AUTOLOGIN wallet OPEN (WALLET_ORDER='SECONDARY')
   - TDE_CONFIGURATION: 'KEYSTORE_CONFIGURATION=HSM|FILE'
   - Assessment: "HSM TDE with auto-login (forward migrated)", migration_status: "forward_migrated"

3. HSM with Auto-login (Not Migrated):
   - V$ENCRYPTION_WALLET: HSM wallet OPEN (WALLET_ORDER='PRIMARY'), AUTOLOGIN wallet OPEN_NO_MASTER_KEY (WALLET_ORDER='SECONDARY')
   - TDE_CONFIGURATION: 'KEYSTORE_CONFIGURATION=HSM|FILE'
   - Assessment: "HSM TDE with auto-login (not migrated)", migration_status: "hsm_with_autologin"

4. FILE wallet TDE:
   - V$ENCRYPTION_WALLET: PASSWORD wallet OPEN (WALLET_ORDER='SINGLE')
   - TDE_CONFIGURATION: 'KEYSTORE_CONFIGURATION=FILE'
   - Assessment: "FILE wallet TDE (password-based)", migration_status: "file_only"

5. FILE with Auto-login (Reverse Migrated):
   - V$ENCRYPTION_WALLET: PASSWORD wallet OPEN (WALLET_ORDER='PRIMARY'), AUTOLOGIN wallet OPEN (WALLET_ORDER='SECONDARY')
   - TDE_CONFIGURATION: 'KEYSTORE_CONFIGURATION=FILE|HSM'
   - Assessment: "FILE wallet TDE with auto-login (reverse migrated)", migration_status: "reverse_migrated"

6. FILE with Auto-login (Standard):
   - V$ENCRYPTION_WALLET: PASSWORD wallet OPEN (WALLET_ORDER='PRIMARY'), AUTOLOGIN wallet OPEN (WALLET_ORDER='SECONDARY')
   - TDE_CONFIGURATION: 'KEYSTORE_CONFIGURATION=FILE'
   - Assessment: "FILE wallet TDE (PRIMARY/SECONDARY config)", migration_status: "file_primary_secondary"

7. Misconfiguration Detection:
   - V$ENCRYPTION_WALLET: FILE wallet PRIMARY but TDE_CONFIGURATION='HSM|FILE'
   - Assessment: "Misconfigured: HSM|FILE config but non-HSM primary", migration_status: "misconfigured"

Key Oracle Documentation References:
- WALLET_ORDER values: 'SINGLE', 'PRIMARY', 'SECONDARY'
- TDE_CONFIGURATION formats: 'HSM', 'FILE', 'HSM|FILE', 'FILE|HSM'
- Correlation between WALLET_ORDER and TDE_CONFIGURATION determines scenario

Verification Points:
- TDE enabled = Any wallet OPEN + MEKs exist (V$ENCRYPTION_KEYS count > 0)  
- Migration status determined by WALLET_ORDER + TDE_CONFIGURATION correlation
- Misconfiguration detected when WALLET_ORDER contradicts TDE_CONFIGURATION
- Status description includes TDE_CONFIGURATION value for verification
"""

# Test all database connections defined in config
uv run python -m database_tde_server --test-connections
"""
