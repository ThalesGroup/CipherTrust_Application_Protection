# Gateway Management Tools

This directory contains tools for managing Akeyless gateways in the Thales CDSP CSM MCP Server.

## Available Tool

### `manage_gateways`
Enterprise gateway management tool with the following actions:

- **`list`** - List available Akeyless gateways

## Features

- **Gateway Infrastructure Monitoring** - View all available gateways in your Akeyless environment
- **Accessibility Control** - Filter gateways by accessibility levels
- **JSON Output Support** - Get structured data for automation and integration
- **Enterprise-Grade Security** - Built on Thales CipherTrust Secrets Management (CSM) with Akeyless Secrets Manager
- **Comprehensive Logging** - Full audit trail for all gateway operations

## Use Cases

- **Infrastructure Monitoring** - Monitor gateway health and availability
- **Security Auditing** - Review gateway configurations and access patterns
- **Automation Integration** - Use gateway lists for automated deployment and management
- **Compliance Reporting** - Generate reports on gateway infrastructure

## API Endpoint

The tool uses the Akeyless `/list-gateways` endpoint to retrieve gateway information.

## Authentication

Requires valid Akeyless authentication token (automatically handled by the MCP server).

## Example Usage

```python
# List all gateways
{
    "action": "list",
    "json": false
}

# List gateways with JSON output
{
    "action": "list", 
    "json": true
}
```
