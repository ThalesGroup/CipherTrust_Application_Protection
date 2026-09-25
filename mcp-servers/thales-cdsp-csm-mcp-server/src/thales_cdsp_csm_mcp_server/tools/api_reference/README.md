# API Reference Tool

## Overview

The `get_api_reference` tool provides developers with complete API reference information to build applications that directly integrate with Thales CipherTrust/Akeyless APIs. This enables AI assistants to generate native code that can fetch secrets, authenticate, and perform operations without depending on the MCP server.

## Purpose

This tool bridges the gap between MCP tools and native application development by providing:
- **Complete API specifications** for Akeyless endpoints
- **Working code examples** in multiple programming languages
- **Complete workflow implementations** for common use cases
- **Best practices** and security considerations

## Use Cases

### For AI Assistants
When a developer asks an AI assistant to "create an app that connects to a database using secrets from CipherTrust", the assistant can:

1. **Call this tool** to get complete API reference
2. **Generate native code** that directly calls Akeyless APIs
3. **Create a complete application** that fetches credentials at runtime
4. **Build production-ready solutions** that don't depend on MCP servers

### For Developers
- **Learn Akeyless APIs** without reading external documentation
- **Get working code examples** that can be copied directly into applications
- **Understand authentication flows** and security best practices
- **Implement complete workflows** like database connections with secret management

## Available Actions

### `get` - Get API Reference Information

#### Parameters
- **`api_endpoint`** (string): Specific API endpoint or 'workflow' for complete examples
  - `auth` - Authentication endpoint reference
  - `get-secret-value` - Secret retrieval endpoint reference
  - `list-items` - List items endpoint reference
  - `workflow` or `generic_workflow` - Core Akeyless integration patterns
  - `list-roles` - List roles endpoint reference
  - `list-targets` - List targets endpoint reference

- **`language`** (string, default: "python"): Programming language for code examples
- **`include_auth`** (boolean, default: true): Include authentication examples
- **`include_error_handling`** (boolean, default: true): Include error handling examples

#### Examples

**Get Generic Workflow Reference:**
```python
# Get complete generic Akeyless integration workflow
reference = await get_api_reference(
    api_endpoint="workflow",
    language="python",
    include_error_handling=True
)
```

**Get Authentication Reference:**
```python
# Get authentication API reference
auth_ref = await get_api_reference(
    api_endpoint="auth",
    language="python"
)
```

**Get Secret Retrieval Reference:**
```python
# Get secret retrieval API reference
secret_ref = await get_api_reference(
    api_endpoint="get-secret-value",
    language="python"
)
```

## Workflow Examples

### Core Akeyless Integration Workflow

The tool provides a **generic workflow** that demonstrates the three core patterns:

1. **Authenticate with CSM/Akeyless** to retrieve the token
2. **Create secrets on CSM/Akeyless** (when creating new apps or modifying existing apps with hardcoded credentials)
3. **Build/Modify user application** to retrieve secrets from CSM/Akeyless at runtime (retrieve token is still the first step)

#### Generic Implementation Includes:
- `AkeylessClient` class for authentication and secret management
- `ApplicationConfig` class for configuration management
- Database and API configuration examples
- Environment variable configuration
- Comprehensive error handling
- Retry logic with exponential backoff
- Production-ready security practices

#### Use Cases:
- **Database Connections** - Store connection strings securely
- **API Keys** - Manage external service credentials
- **Configuration** - Application settings and parameters
- **SSL Certificates** - Security certificates and keys
- **OAuth Tokens** - Authentication credentials
- **Any Sensitive Data** - Application secrets and configuration

### Generic Application Integration Examples

The tool provides complete workflows that demonstrate:

1. **Authentication** with Akeyless to get access token
2. **Secret Retrieval** using the token to fetch application credentials
3. **Application Integration** using retrieved secrets for database connections, API calls, etc.
4. **Error Handling** with retry logic and proper exception management
5. **Best Practices** for production deployments

#### Complete Implementation Includes:
- `AkeylessClient` class for authentication and secret management
- `ApplicationConfig` class for configuration management
- Environment variable configuration
- Comprehensive error handling
- Retry logic with exponential backoff
- Production-ready security practices

## Supported Languages

Currently supports:
- **Python** - Complete implementations with requests library

Future support planned for:
- JavaScript/Node.js
- Go
- Java
- C#

## API Endpoints Covered

### Authentication
- **POST /auth** - Get access token using access-id and access-key

### Secrets Management
- **POST /get-secret-value** - Retrieve secret values using authentication token
- **POST /list-items** - List available items and secrets

### Access Control
- **POST /list-roles** - List available roles
- **POST /target-list** - List available targets

## Best Practices

The tool provides guidance on:
- **Security**: Store credentials in environment variables
- **Reliability**: Implement retry logic and error handling
- **Performance**: Cache tokens when possible
- **Production**: Use HTTPS and proper logging
- **Cloud Integration**: Prefer managed identities and IAM roles over access keys when possible

## Integration Patterns

### Environment Variables
```bash
export AKEYLESS_ACCESS_ID="your-access-id"
export AKEYLESS_ACCESS_KEY="your-access-key"
export AKEYLESS_URL="https://your-akeyless-endpoint"
export SECRET_NAME="database-credentials"
export APP_CONFIG_SECRET="app-config"
```

### Code Structure
```python
# 1. Initialize Akeyless client
akeyless_client = AkeylessClient(access_id, access_key, base_url)

# 2. Authenticate to get token
akeyless_client.authenticate()

# 3. Retrieve secrets
db_creds = akeyless_client.get_secret("database-credentials")

# 4. Use secrets in your application
# Example: Database connection, API calls, etc.
```

## Benefits

### For Development Teams
- **Faster Development** - Get working code examples immediately
- **Reduced Errors** - Pre-tested implementations with proper error handling
- **Security Best Practices** - Built-in guidance for secure implementations
- **Consistency** - Standardized patterns across applications

### For AI Assistants
- **Complete Context** - Full understanding of Akeyless APIs
- **Code Generation** - Ability to create production-ready applications
- **Workflow Understanding** - Knowledge of complete integration patterns
- **Best Practices** - Guidance for secure and reliable implementations

## Future Enhancements

- **Additional Languages** - Support for more programming languages
- **Framework Templates** - Flask, FastAPI, Express.js, etc.
- **Cloud Provider Integration** - Azure, GCP, AWS specific patterns
- **Advanced Workflows** - Database connections, API integrations, etc.
- **Security Scanning** - Code analysis for security best practices

## Example Output

When requesting a workflow, the tool returns:

```json
{
  "workflow": "Generic Akeyless Integration Workflow",
  "description": "Complete workflow to authenticate with Akeyless, retrieve secrets, and integrate with applications",
  "prerequisites": [
    "Akeyless access ID and access key",
    "Secret stored in Akeyless with application credentials",
    "Python 3.7+ with requests library"
  ],
  "complete_implementation": {
    "basic": "# Complete Python implementation...",
    "with_error_handling": "# Enhanced implementation with retry logic...",
    "environment_variables": {
      "AKEYLESS_ACCESS_ID": "Your Akeyless access ID",
      "AKEYLESS_ACCESS_KEY": "Your Akeyless access key"
    }
  },
  "step_by_step": [
    "1. Authenticate with Akeyless to get token",
    "2. Use token to retrieve application secrets",
    "3. Parse credentials from secrets",
    "4. Use secrets in your application (database, API, etc.)"
  ],
  "best_practices": [
    "Store Akeyless credentials in environment variables",
    "Implement token caching to avoid repeated authentication",
    "Use managed identities and IAM roles when possible"
  ]
}
```

This comprehensive reference enables developers and AI assistants to build native Akeyless integrations for any application type quickly and securely. 