# Example Prompts for Database TDE MCP Server

This file contains practical example prompts to test the Database TDE MCP Server functionality using AI assistants or MCP clients.

## Prerequisites

- Configure your MCP server with appropriate database connections
- Ensure CAKM providers are installed and configured on database servers
- Replace connection names and credentials with your actual values

## SQL Server Example Prompts

Use the configured MCP server and test the following scenarios:

### 1. Basic Database Operations

**1. List all databases on the prod_sql SQL server.**
```
List all databases on the prod_sql SQL server.
```

**2. List all encrypted databases.**
```
List all encrypted databases.
```

### 2. Database Encryption

**3. Encrypt Db01 with master key MEK01. Use ctm_ekm_provider as the cryptographic provider. Ciphertrust username is admin and password is tdeuser_password**
```
Encrypt Db01 with master key MEK01. Use ctm_ekm_provider as the cryptographic provider. Ciphertrust username is admin and password is tdeuser_password
```

**4. Encrypt Db02 and Db03 with key shared_key. Use the same cryptographic provider and CipherTrust credentials as before.**
```
Encrypt Db02 and Db03 with key shared_key. Use the same cryptographic provider and CipherTrust credentials as before.
```

**5. Encrypt Db05 with key Db05Key.**
```
Encrypt Db05 with key Db05Key.
```

### 3. Key Management and Queries

**6. List the name of the master encryption key for Db05**
```
List the name of the master encryption key for Db05
```

### 4. Key Rotation Operations

**7. Rotate the database encryption key for Db05.**
```
Rotate the database encryption key for Db05.
```

**8. Rotate the master key for Db05 database. Use new_Db05_key as the key name. The new key type is RSA of size 3072.**
```
Rotate the master key for Db05 database. Use new_Db05_key as the key name. The new key type is RSA of size 3072.
```

**9. List the name of the master encryption key for Db05**
```
List the name of the master encryption key for Db05.
```

### 6. Comprehensive Status Reports

**10. List all encrypted databases with the associated master keys.**
```
List all encrypted databases with the associated master keys.
```

## Oracle Example Prompts

Use the configured MCP server and test the following scenarios:

### 1. Connection and TDE Status

**1. List all Oracle database connections.**
```
List all Oracle database connections.
```

**2. Is TDE enabled on any Oracle database from the list?**
```
Is TDE enabled on any Oracle database from the list?
```

### 2. Complete TDE Setup with Auto-login

**3. Enable TDE on oracle_cdb2? Automatically restart the database, if needed. Use the following CipherTrust manager credentials to setup TDE:**
```
Enable TDE on oracle_cdb2. Automatically restart the database, if needed. Use the following CipherTrust manager credentials to setup TDE:
User- tdeuser
Password - tdeuser_password
Domain - TDE

Setup auto-login as well. Use soft_wallet_password as the software wallet password.
```

### 3. TDE Setup without Auto-login

**4. Enable TDE on oracle_cdb3. Automatically restart the database, if needed. Use the following CipherTrust manager credentials to setup TDE:**
```
Enable TDE on oracle_cdb3. Automatically restart the database, if needed. Use the following CipherTrust manager credentials to setup TDE:
User- tdeuser
Password - tdeuser_password
Domain - TDE

Skip auto-login wallet setup/creation.
```

### 4. Configuration Parameter Queries

**5. What's the value of the following system parameters on oracle_cdb2?**
```
What's the value of the following system parameters on oracle_cdb2?
a. tde_configuration
b. wallet_root
c. encrypt_new_tablespaces
```

### 5. Migration Assessment

**6. Migrate TDE for oracle_cd1 database using the following credentials. Specify CipherTrust manager credentials here.**
```
Migrate TDE for oracle_cd1 database using the following credentials. Specify CipherTrust manager credentials here.
```

## Advanced Testing Scenarios

### Compliance and Audit

**Generate TDE compliance report:**
```
Generate a comprehensive TDE compliance report for prod_sql including security recommendations.
```

### Wallet Management

**Oracle wallet operations:**
```
Check the status of Oracle wallet on oracle_cdb1 for all containers.
```

## Tips for Using These Prompts

1. **Replace Placeholders**: Update connection names (`prod_sql`, `oracle_cdb1`, etc.) with your actual connection names
2. **Update Credentials**: Replace usernames/passwords with your actual CipherTrust Manager credentials
3. **Database Names**: Replace database names (`Db01`, `Db02`, etc.) with your actual database names
4. **Sequential Testing**: Run prompts in order for SQL Server scenarios - later prompts depend on earlier ones
5. **Error Handling**: Include intentional error scenarios to test error handling
6. **Documentation**: Document results for audit trails and troubleshooting

## Expected Responses

- **Success**: JSON responses with operation results and status
- **Failures**: Detailed error messages with troubleshooting guidance
- **Status Queries**: Formatted tables or lists showing current state
- **Reports**: Comprehensive reports with recommendations and compliance status

## Troubleshooting Common Issues

1. **Connection Failures**: Verify database server accessibility and credentials
2. **CAKM Provider Missing**: Ensure CAKM providers are installed on database servers
3. **Permission Errors**: Verify database user has required TDE permissions
4. **Wallet Issues**: Check Oracle wallet configuration and paths
5. **SSH Connection Problems**: Verify SSH credentials and connectivity for Oracle operations 
