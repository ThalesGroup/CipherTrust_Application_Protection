# DFC Keys Management Tools

This directory contains tools for managing DFC (Data Format Conversion) keys in the Thales CDSP CSM MCP Server.

## Available Tool

### `manage_dfc_keys`
Comprehensive DFC keys management tool with the following actions:

- **`create`** - Create new DFC keys with encryption algorithms
- **`update`** - Update DFC key properties and settings
- **`delete`** - Delete DFC keys (with soft delete support)
- **`list`** - List DFC keys in directories
- **`set_state`** - Enable/disable DFC keys

## Features

- **Encryption Algorithms**: AES128GCM, AES256GCM, RSA2048, and more
- **Auto-rotation**: Configurable rotation intervals (7-365 days)
- **Certificate Generation**: Self-signed certificate creation with X.509 support
- **Customer Fragments**: Integration with customer fragment protection
- **Delete Protection**: Protection from accidental deletion
- **Tagging System**: Flexible tagging for organization
- **Directory-based organization**
- **Filtering capabilities**
- **Comprehensive audit logging**
- **Integration with secrets management tool for protection handling** 