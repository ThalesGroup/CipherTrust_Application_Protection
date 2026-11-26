# Roles Management Tools

This module provides tools for managing roles in the Thales CSM Akeyless Vault.

## Available Operations

### List Roles
- **Action**: `list`
- **Description**: List all roles with optional filtering
- **Parameters**:
  - `filter`: Filter by role name or part of it
  - `json`: Set output format to JSON (default: false)
  - `pagination_token`: Next page reference for pagination
  - `uid_token`: Universal identity token (for universal_identity authentication)

### Get Role
- **Action**: `get`
- **Description**: Get details of a specific role
- **Parameters**:
  - `name`: Role name (required)
  - `json`: Set output format to JSON (default: false)
  - `uid_token`: Universal identity token (for universal_identity authentication)

## Usage Examples

### List all roles
```python
# List all roles
await manage_roles(action="list")

# List roles with filter
await manage_roles(action="list", filter="admin")

# List roles with JSON output
await manage_roles(action="list", json=True)
```

### Get specific role
```python
# Get role details
await manage_roles(action="get", name="admin-role")

# Get role details with JSON output
await manage_roles(action="get", name="admin-role", json=True)
```
## Error Handling

The tool provides comprehensive error handling with:
- Input validation
- API error handling
- User-friendly error messages
- Logging for debugging

## Authentication

Supports both standard token authentication and universal identity authentication through the `uid_token` parameter. 