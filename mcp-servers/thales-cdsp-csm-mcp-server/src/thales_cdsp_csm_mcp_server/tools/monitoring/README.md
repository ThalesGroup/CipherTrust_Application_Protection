# Analytics Management Tools

This module provides tools for monitoring and analytics in the Thales CSM Akeyless Vault.

## Available Operations

### Get Analytics
- **Action**: `get`
- **Description**: Get comprehensive analytics data with optional filtering
- **Parameters**:
  - `json`: Set output format to JSON (default: false)
  - `filter_by_type`: Filter analytics by item type (e.g., 'Targets', 'Static Secrets', 'DFC Key')
  - `filter_by_risk`: Filter certificates by risk level ('Expired', 'Healthy')
  - `filter_by_product`: Filter by product ('sm', 'adp', 'sra')
  - `uid_token`: Universal identity token (for universal_identity authentication)

## Analytics Data Includes

- **Item Counts**: By type (Targets, Secrets, Keys, etc.)
- **Geographic Data**: Usage by location
- **Request Metrics**: Volumes and response times
- **Certificate Information**: Expiry data and risk levels
- **Client Usage**: Authentication methods and access patterns
- **Product Statistics**: Secrets Management, ADP, SRA usage

## Usage Examples

### Get all analytics data
```python
# Get comprehensive analytics
await manage_analytics(action="get")

# Get analytics with JSON output
await manage_analytics(action="get", json=True)
```

### Filter by item type
```python
# Get only target-related analytics
await manage_analytics(action="get", filter_by_type="Targets")

# Get only secret-related analytics
await manage_analytics(action="get", filter_by_type="Static Secrets")
```

### Filter by certificate risk
```python
# Get only expired certificates
await manage_analytics(action="get", filter_by_risk="Expired")

# Get only healthy certificates
await manage_analytics(action="get", filter_by_risk="Healthy")
```

### Filter by product
```python
# Get only Secrets Management analytics
await manage_analytics(action="get", filter_by_product="sm")

# Get only ADP analytics
await manage_analytics(action="get", filter_by_product="adp")
```

### Combine filters
```python
# Get target analytics with JSON output
await manage_analytics(
    action="get", 
    filter_by_type="Targets", 
    json=True
)
```

## Filtering Capabilities

The tool provides client-side filtering for:
- **Item Types**: Filter by specific resource types
- **Risk Levels**: Focus on certificate health status
- **Products**: Analyze specific product usage
- **Combined Filters**: Use multiple filters simultaneously

## Error Handling

The tool provides comprehensive error handling with:
- Input validation
- API error handling
- User-friendly error messages
- Logging for debugging

## Authentication

Supports both standard token authentication and universal identity authentication through the `uid_token` parameter. 