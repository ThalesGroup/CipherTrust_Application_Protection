# Targets Management Tools

This module provides tools for managing targets in the Thales CSM Akeyless Vault.

## Available Operations

### List Targets
- **Action**: `list`
- **Description**: List all targets with optional filtering by type
- **Parameters**:
  - `filter`: Filter by target name or part of it
  - `json`: Set output format to JSON (default: false)
  - `pagination_token`: Next page reference for pagination
  - `target_types`: List of target types to filter by
  - `uid_token`: Universal identity token (for universal_identity authentication)

### Get Target
- **Action**: `get`
- **Description**: Get detailed information about a specific target (includes version support)
- **Parameters**:
  - `name`: Target name (required)
  - `json`: Set output format to JSON (default: false)
  - `show_versions`: Include all target versions in reply (default: false)
  - `target_version`: Specific target version to retrieve (0 for latest, optional)
  - `uid_token`: Universal identity token (for universal_identity authentication)

## Supported Target Types

The following target types are supported for filtering:
- **Databases**: `hanadb`, `cassandra`, `mysql`, `mongodb`, `snowflake`, `mssql`, `redshift`, `postgres`, `oracle`
- **Cloud Platforms**: `aws`, `azure`, `gcp`, `gke`, `eks`, `k8s`
- **Services**: `ssh`, `rabbitmq`, `artifactory`, `dockerhub`, `github`, `chef`, `web`, `salesforce`
- **Security**: `venafi`, `ldap`

## Usage Examples

### List all targets
```python
# List all targets
await manage_targets(action="list")

# List targets with filter
await manage_targets(action="list", filter="database")

# List targets by type
await manage_targets(action="list", target_types=["mysql", "postgres"])

# List targets with JSON output
await manage_targets(action="list", json=True)
```

### Get specific target
```python
# Get target details
await manage_targets(action="get", name="mysql-database")

# Get target details with versions
await manage_targets(action="get", name="mysql-database", show_versions=True)

# Get specific target version
await manage_targets(action="get", name="mysql-database", target_version=2)

# Get target details with JSON output
await manage_targets(action="get", name="mysql-database", json=True)
```

## Error Handling

The tool provides comprehensive error handling with:
- Input validation
- API error handling
- User-friendly error messages
- Logging for debugging

## Authentication

Supports both standard token authentication and universal identity authentication through the `uid_token` parameter.

## Target Type Filtering

When using the `target_types` parameter, you can specify one or more target types to filter the results. This is useful for:
- Finding all database targets
- Locating cloud-specific targets
- Identifying security-related targets
- Organizing targets by infrastructure component 