# AI Assistant Integration Guide

This guide shows how to integrate the CRDP MCP Server with AI assistants.

## Prerequisites

- CRDP MCP Server built (`npm install && npm run build`)
- CRDP service running and accessible
- AI assistant installed and configured

## Configuration

All supported AI assistants (Cursor AI, Google Gemini, Claude Desktop) use the same `mcp.json` configuration:

```json
{
  "mcpServers": {
    "crdp": {
      "command": "node",
      "args": ["/path/to/crdp-mcp-server/dist/crdp-mcp-server.js"],
      "env": {
        "CRDP_SERVICE_URL": "http://your-crdp-server:8090",
        "CRDP_PROBES_URL": "http://your-crdp-server:8080",
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

### Path Examples

**Windows:**
```
"args": ["C:\\thales-cdsp-crdp-mcp-server\\dist\\crdp-mcp-server.js"]
```

**macOS/Linux:**
```
"args": ["/home/username/thales-cdsp-crdp-mcp-server/dist/crdp-mcp-server.js"]
```

### Complete Windows Example

```json
{
  "mcpServers": {
    "crdp": {
      "command": "node",
      "args": ["C:\\thales-cdsp-crdp-mcp-server\\dist\\crdp-mcp-server.js"],
      "env": {
        "CRDP_SERVICE_URL": "http://your-crdp-server:8090",
        "CRDP_PROBES_URL": "http://your-crdp-server:8080",
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

## Usage Examples

### Data Protection
```
Protect my email address john.doe@example.com using the email_policy
```

### Data Revelation
```
Reveal the protected data abc123def456 for user admin
```

### With JWT Authentication
```
Protect my SSN 123-45-6789 using ssn_policy. 
JWT: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Health Check
```
Check the health of my CRDP service
```

## Troubleshooting

- **Command not found**: Ensure Node.js is installed and in PATH
- **Connection refused**: Verify CRDP service is online
- **Tools not showing**: Restart assistant after configuration
- **Test directly**: `node dist/crdp-mcp-server.js`