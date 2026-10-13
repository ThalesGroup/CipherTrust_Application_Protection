# Authentication Methods Management Tools

This directory contains tools for managing authentication methods in the Thales CDSP CSM MCP Server.

## Available Tool

### `manage_auth_methods`
Comprehensive authentication methods management tool with the following actions:

- **`create_api_key`** - Create API key authentication methods
- **`create_email`** - Create email authentication methods
- **`update`** - Update existing authentication methods
- **`delete`** - Delete specific authentication methods
- **`delete_auth_methods`** - Bulk delete authentication methods in a path
- **`list`** - List authentication methods
- **`get`** - Get specific authentication method details

## Supported Auth Method Types

- **API Key** - Token-based authentication
- **Email** - Email-based authentication with MFA support

## Features

- Modular architecture for different auth method types
- Smart deletion with path-based operations
- Bulk operations support
- Comprehensive audit logging 