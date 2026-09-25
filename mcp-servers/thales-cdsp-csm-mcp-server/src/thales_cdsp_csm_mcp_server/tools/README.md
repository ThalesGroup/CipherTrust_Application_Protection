# Thales CDSP CSM MCP Server Tools

This directory contains all the tools for the Thales CDSP CSM MCP Server, providing comprehensive secrets management, authentication, and security capabilities.

## Available Tools

### 🔐 [Secrets Management](./secrets/)
- **Tool**: `manage_secrets`
- **Actions**: create, get, update, delete, list
- **Features**: Smart deletion, bulk operations, DFC key handling

### 🔑 [DFC Keys Management](./dfc_keys/)
- **Tool**: `manage_dfc_keys`
- **Actions**: create, update, delete, list, set_state
- **Features**: Create DFC keys, auto-rotation, certificate generation, customer fragments integration

### 🔐 [Authentication Methods](./auth_methods/)
- **Tool**: `manage_auth_methods`
- **Actions**: create_api_key, create_email, update, delete, delete_auth_methods, list, get
- **Features**: Multiple auth types supported, bulk operations

### 📄 [Customer Fragments](./customer_fragments/)
- **Tool**: `manage_customer_fragments`
- **Actions**: list, export, download
- **Features**: Export functionality, JSON support

### 🛡️ [Security Guidelines](./guidelines/)
- **Tool**: `security_guidelines`
- **Actions**: get_guidelines, validate, audit, compliance_check
- **Features**: Enterprise security guidance, compliance validation

### 🔄 [Rotation Management](./rotation/)
- **Tool**: `manage_rotation`
- **Actions**: set_rotation, update_settings, list_rotation, get_rotation_status
- **Features**: Automated rotation, scheduling, status monitoring

## Architecture

All tools inherit from `BaseThalesCDSPCSMTool` and provide:
- Hybrid logging (MCP client + file logging)
- Comprehensive error handling
- Audit trail capabilities
- Integration with Akeyless Vault API

## Usage

Each tool directory contains detailed documentation about its specific capabilities and actions. 