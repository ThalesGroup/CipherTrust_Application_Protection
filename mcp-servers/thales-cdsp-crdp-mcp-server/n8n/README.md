# n8n Conversational AI for CipherTrust RestFul Data Protection (CRDP)

This repository contains a set of [n8n](https://n8n.io/) workflows that create a conversational AI front-end for a CRDP service. This allows users to perform data protection operations, like encrypting and decrypting data, using natural language.

## Workflows

There are two main workflows that work together:

1.  **`MCP Client`**: This is the user-facing workflow. It provides a chat interface where a user can type requests. An AI Agent, powered by a Large Language Model (e.g., OpenAI), parses these requests, maintains conversational memory, and uses the tools provided by the `MCP Server`.

2.  **`MCP Server`**: This workflow acts as a bridge to the actual CRDP service. It exposes the core CRDP functions (protect, reveal, health checks, etc.) as a set of tools over the Model Context Protocol (MCP). The `MCP Client` calls these tools to perform its actions. The server expectes CRDP Service and Probes URLs from the client in order to forward the request to the correct CRDP port.


## Demo Videos

- **Walkthrough**: [https://youtu.be/ILNyWRYQUpw] - How to use the n8n workflows


## Key Features

*   **Conversational Interface**: Protect and reveal data using natural language.
*   **Support for All Core CRDP Tools**: Includes single and bulk operations for `protect` and `reveal`, plus monitoring tools (`health`, `liveness`, `metrics`).
*   **JWT Authorization**: Secure your data operations by providing an optional JWT Bearer Token in your prompts.
*   **Conversational Memory**: The agent can remember context from previous messages in the same session (e.g., you can set the service URL once).
*   **Intelligent Tool Selection**: The agent is prompted to automatically use `bulk` operations when you provide multiple pieces of data.
*   **Strict & Secure**: The agent is configured to always ask for required security parameters (`username`, `protection_policy_name`) and will not proceed without them.
*   **Integration with AI assistants**: Use the following contents in mcp.json or settings.json for AI assistants like Cursor AI, Google gemini or CLaude desktop.

1. Install supergateway with "npm" 
```bash
npm install supergateway
```

2. Setup the MCP server in your AI assistant:
```json
{
  "mcpServers": {
    "n8n_crdp_mcp_server": {
      "command": "npx",
      "args": [
        "-y",
        "supergateway",
        "--sse",
        "http://localhost:5678/mcp/crdp" 
      ]
    }
    }
}
```

## JWT Authentication

The workflows support JWT bearer token authentication for secure CRDP operations:

### **How to Use JWT**

1. **Include JWT in your prompt**: Simply mention the JWT token in your request
2. **Automatic Header Addition**: The MCP Server automatically adds the `Authorization: Bearer <token>` header
3. **Optional Parameter**: JWT is optional - operations work without it if your CRDP service doesn't require authentication

### **Example with JWT**
```
Protect my email john.doe@company.com using PPol1 policy. 
Service URL: http://crdp.internal:8090
JWT: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### **Security Best Practices**
- Use HTTPS for all communications
- Rotate JWT tokens regularly
- Store JWT tokens securely
- Use short-lived tokens when possible

## Template Files

For easy setup, this repository includes two template files:

*   `crdp_demo_mcp_server.json` - MCP Server workflow with CRDP tools
*   `crdp_demo_mcp_client.json` - MCP Client workflow with conversational AI

## Quick Setup

1.  **Import Workflows**: In your n8n instance, import both `crdp_demo_mcp_server.json` and `crdp_demo_mcp_client.json`.
2.  **Configure Credentials**: In the `MCP Client` workflow, edit the "OpenAI Model" node and connect your own OpenAI (or other LLM) credentials.
3.  **Activate Workflows**: Activate both workflows.
4.  **Start Chatting**: Open the chat interface for the `MCP Client` workflow and start making requests!

## Architecture

```
User Chat → MCP Client → MCP Server → CRDP Service
                ↓              ↓
            OpenAI LLM    HTTP Tools
```

The workflows work together to provide a conversational interface to your CRDP service:

- **MCP Client**: Handles user interactions, maintains conversation memory, and uses AI to parse requests
- **MCP Server**: Exposes CRDP API endpoints as tools that the client can call
- **CRDP Service**: Performs the actual data protection and revelation operations

## Example Prompts

**Simple protect operation:**
```
Protect my email address, test@example.com, using the PPol1 policy. The service URL is http://localhost:8090.
```

**Bulk protect operation:**
```
Protect sensitive data in this prompt:

Hi, my name is John Doe. My e-mail is john.doe@gmail.com and I live in California. My SSN is 123-45-6789 and I can be reached 949 781 8590.

The crdp service URL is http://localhost:8090 and the protection policy to use is PPol1
```

**Reveal operation with JWT Authorization:**
```
Reveal the value of "2irL3k7c8y" with PPol1, username my_authorized_user and the JWT "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." at service URL http://localhost:8090.
```

**Bulk reveal operation:**
```
Reveal BbKZ.xsn@JASZ5.uqG and 2irL3k7c8y for user 'app_super_user' with PPol1. The service URL is http://localhost:8090.
```

## Troubleshooting

### **Common Issues**

1. **"Service URL not found"**
   - Always include the service URL in your first message
   - The agent remembers the URL for the session

2. **"Missing required parameters"**
   - Ensure you provide `protection_policy_name` and `username` (for reveal operations)
   - The agent will ask for missing parameters

3. **"Connection refused"**
   - Verify your CRDP service is running and accessible
   - Check the service URL is correct

4. **"Authentication failed"**
   - Verify your JWT token is valid and not expired
   - Ensure the token has proper permissions

### **Getting Help**

- Check the main project [README.md](../README.md) for general CRDP MCP server information
- Review the [testing documentation](../docs/testing.md) for API testing
- Ensure your n8n instance has the required nodes installed