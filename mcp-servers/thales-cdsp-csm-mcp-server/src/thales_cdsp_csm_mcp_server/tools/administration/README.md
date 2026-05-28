# Account Management Tools

This module provides tools for administrative and account management in the Thales CSM Akeyless Vault.

## Available Operations

### Get Account Settings
- **Action**: `get`
- **Description**: Get account settings and licensing information
- **Parameters**:
  - `json`: Set output format to JSON (default: false)
  - `uid_token`: Universal identity token (for universal_identity authentication)

## Account Information Includes

- **Company Details**: Name, address, contact information
- **Licensing**: Tier levels and SLA information
- **Product Settings**: Secrets Management, ADP, SRA configuration
- **Version Control**: Object versioning policies and limits
- **System Access**: JWT TTL settings and authentication configuration
- **Security Policies**: Sharing policies and data protection settings

## Usage Examples

### Get account settings
```python
# Get comprehensive account information
await manage_account(action="get")

# Get account settings with JSON output
await manage_account(action="get", json=True)
```

## Account Data Structure

The tool returns detailed account information including:

### **Company Information**
- Account ID and company name
- Address and contact details
- Phone and email information

### **Licensing & SLA**
- Secrets Management tier and SLA level
- Secure Remote Access configuration
- Product-specific licensing details

### **System Configuration**
- JWT TTL settings (default, minimum, maximum)
- Object versioning policies
- Version limits by item type

### **Security Settings**
- Data protection configuration
- Sharing policy settings
- Item usage event tracking
- Authentication usage monitoring

## Error Handling

The tool provides comprehensive error handling with:
- Input validation
- API error handling
- User-friendly error messages
- Logging for debugging

## Authentication

Supports both standard token authentication and universal identity authentication through the `uid_token` parameter.

## Use Cases

- **License Verification**: Check current tier and SLA levels
- **Capacity Planning**: Review version limits and policies
- **Compliance**: Verify security and sharing policies
- **Administration**: Monitor account configuration and settings 