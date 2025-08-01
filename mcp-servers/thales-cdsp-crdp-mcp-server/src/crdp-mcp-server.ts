#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ErrorCode,
  ListPromptsRequestSchema,
  ListToolsRequestSchema,
  McpError,
  GetPromptRequestSchema,
  InitializedNotificationSchema,
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
  ListResourceTemplatesRequestSchema,
  Tool,
  Prompt
} from "@modelcontextprotocol/sdk/types.js";
import express from "express";
import axios, { AxiosInstance } from "axios";
import { z } from "zod";

// CRDP client configuration
const CRDP_SERVICE_URL = process.env.CRDP_SERVICE_URL || process.env.CRDP_BASE_URL || "http://localhost:8090";
const CRDP_PROBES_URL = process.env.CRDP_PROBES_URL || process.env.CRDP_BASE_URL || "http://localhost:8090";

console.error(`CRDP Service URL: ${CRDP_SERVICE_URL}`);
console.error(`CRDP Probes URL: ${CRDP_PROBES_URL}`);

// MCP Protocol state management
class MCPServerState {
  private initialized = false;
  
  setInitialized(value: boolean) {
    this.initialized = value;
  }
  
  isInitialized(): boolean {
    return this.initialized;
  }
}

const serverState = new MCPServerState();

// Zod schemas for validation
const ProtectDataSchema = z.object({
  data: z.string().describe("The data to protect"),
  protection_policy_name: z.string().describe("Protection policy name to use"),
  jwt: z.string().optional().describe("JWT token for authorization")
});

const RevealDataSchema = z.object({
  protected_data: z.string().describe("The protected data to reveal"),
  protection_policy_name: z.string().describe("Policy name used for protection"),
  external_version: z.string().optional().describe("Version header information."),
  username: z.string().optional().describe("User identity for authorization (optional, required if JWT is not provided)"),
  jwt: z.string().optional().describe("JWT token for authorization (optional, required if username is not provided)")
}).refine(
  (data) => !!data.username || !!data.jwt,
  { message: "At least one of 'username' or 'jwt' must be provided for reveal operations." }
);

const BulkProtectSchema = z.object({
  request_data: z.array(
    z.object({
      protection_policy_name: z.string(),
      data: z.string()
    })
  ).describe("Array of protection request objects"),
  jwt: z.string().optional().describe("JWT token for authorization")
});

const BulkRevealSchema = z.object({
  protected_data_array: z.array(
    z.object({
      protection_policy_name: z.string(),
      protected_data: z.string(),
      external_version: z.string().optional(),
      nonce: z.string().optional()
    })
  ).describe("Array of reveal request objects"),
  username: z.string().optional().describe("User identity for authorization (optional, required if JWT is not provided)"),
  jwt: z.string().optional().describe("JWT token for authorization (optional, required if username is not provided)")
}).refine(
  (data) => !!data.username || !!data.jwt,
  { message: "At least one of 'username' or 'jwt' must be provided for reveal operations." }
);

// CRDP Client with separate service and probes URLs
class CRDPClient {
  private serviceInstance: AxiosInstance;
  private probesInstance: AxiosInstance;

  constructor(serviceURL: string, probesURL: string) {
    this.serviceInstance = axios.create({
      baseURL: serviceURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.probesInstance = axios.create({
      baseURL: probesURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  // Service endpoints (protect/reveal) - use CRDP_SERVICE_URL
  async protectData(data: string, protectionPolicyName?: string, jwt?: string): Promise<{protected_data: string, external_version?: string}> {
    const payload: any = { 
      data,
      protection_policy_name: protectionPolicyName
    };
    
    const headers: any = {};
    if (jwt && jwt.trim() !== '') {
      headers['Authorization'] = `Bearer ${jwt}`;
    }
    
    const response = await this.serviceInstance.post('/v1/protect', payload, { headers });
    return {
      protected_data: response.data.protected_data || response.data.data,
      external_version: response.data.external_version
    };
  }

  async revealData(protectedData: string, username?: string, protectionPolicyName?: string, externalVersion?: string, jwt?: string): Promise<string> {
    const payload: any = { 
      protected_data: protectedData,
      protection_policy_name: protectionPolicyName
    };
    if (username) payload.username = username;
    if (externalVersion) payload.external_version = externalVersion;

    const headers: any = {};
    if (jwt && jwt.trim() !== '') {
      headers['Authorization'] = `Bearer ${jwt}`;
    }

    const response = await this.serviceInstance.post('/v1/reveal', payload, { headers });
    return response.data.revealed_data || response.data.data;
  }

  async protectBulk(requestData: any[], jwt?: string): Promise<any> {
    const payload = { request_data: requestData };
    
    const headers: any = {};
    if (jwt && jwt.trim() !== '') {
      headers['Authorization'] = `Bearer ${jwt}`;
    }
    
    const response = await this.serviceInstance.post('/v1/protectbulk', payload, { headers });
    return response.data;
  }

  async revealBulk(protectedDataArray: any[], username?: string, jwt?: string): Promise<any> {
    const payload: any = { protected_data_array: protectedDataArray };
    if (username) payload.username = username;
    
    const headers: any = {};
    if (jwt && jwt.trim() !== '') {
      headers['Authorization'] = `Bearer ${jwt}`;
    }
    
    const response = await this.serviceInstance.post('/v1/revealbulk', payload, { headers });
    return response.data;
  }

  // Monitoring endpoints - use CRDP_PROBES_URL
  async getMetrics(): Promise<any> {
    const response = await this.probesInstance.get('/metrics');
    return response.data;
  }

  async checkHealth(): Promise<any> {
    const response = await this.probesInstance.get('/healthz');
    return response.data;
  }

  async checkLiveness(): Promise<any> {
    const response = await this.probesInstance.get('/liveness');
    return response.data;
  }
}

// Initialize CRDP client and session manager
const crdpClient = new CRDPClient(CRDP_SERVICE_URL, CRDP_PROBES_URL);

// Create server instance
const server = new Server(
  {
    name: "crdp-mcp-server",
    version: "1.0.0",
    protocolVersion: "2025-06-18"
  },
  {
    capabilities: {
      tools: {},
      prompts: {},
      resources: {},
      templates: {}
    },
  }
);

// Add initialization notification handler
server.setNotificationHandler(InitializedNotificationSchema, async () => {
  serverState.setInitialized(true);
  console.error("CRDP MCP Server initialized and ready for normal operations");
  // You can add any post-initialization logic here
});

// Tools handler - Now checks initialization state
server.setRequestHandler(ListToolsRequestSchema, async () => {
  if (!serverState.isInitialized() && process.env.MCP_TRANSPORT !== "streamable-http") {
    throw new McpError(
      ErrorCode.InvalidRequest, 
      "Server not initialized. Send 'notifications/initialized' first."
    );
  }
  
  return {
    tools: [
        {
          name: "protect_data",
          description: "Protect sensitive data using CipherTrust CRDP. If CRDP is running with JWT verification enabled, 'jwt' is required. 'username' is not supported for protect tools.",
          inputSchema: {
            type: "object",
            properties: {
              data: { type: "string", description: "The data to protect" },
              protection_policy_name: { type: "string", description: "Protection policy name" },
              jwt: { type: "string", description: "JWT token for authorization (optional)" }
            },
            required: ["data", "protection_policy_name"]
          }
        },
        {
          name: "reveal_data",
          description: "Reveal protected data using CipherTrust CRDP. At least one of 'username' or 'jwt' must be provided for reveal operations.",
          inputSchema: {
            type: "object",
            properties: {
              protected_data: { type: "string", description: "The protected data to reveal" },
              username: { type: "string", description: "User identity for authorization (required if JWT is not provided)" },
              protection_policy_name: { type: "string", description: "Policy name used for protection" },
              external_version: { type: "string", description: "Version header information." },
              jwt: { type: "string", description: "JWT token for authorization (required if username is not provided)" }
            },
            required: ["protected_data", "protection_policy_name"]
          }
        },
        {
          name: "protect_bulk",
          description: "Protect multiple data items in a single batch operation. Takes an array of data items to protect. If CRDP is running with JWT verification enabled, 'jwt' is required.",
          inputSchema: {
            type: "object",
            properties: {
              request_data: {
                type: "array",
                items: {
                  type: "object",
                  properties: {
                    protection_policy_name: { type: "string", description: "Policy name to apply to this data item" },
                    data: { type: "string", description: "Sensitive data to protect" }
                  },
                  required: ["protection_policy_name", "data"]
                },
                description: "Array of protection request objects, each with data and policy"
              },
              jwt: { type: "string", description: "JWT token for authorization (required if CRDP has JWT verification enabled)" }
            },
            required: ["request_data"]
          }
        },
        {
          name: "reveal_bulk",
          description: "Reveal multiple protected data items in a single batch operation. At least one of 'username' or 'jwt' must be provided for reveal operations.",
          inputSchema: {
            type: "object",
            properties: {
              protected_data_array: {
                type: "array",
                items: {
                  type: "object",
                  properties: {
                    protection_policy_name: { type: "string", description: "Policy name used for protection" },
                    protected_data: { type: "string", description: "Protected data to reveal" },
                    external_version: { type: "string", description: "Version information if using external versioning" },
                    nonce: { type: "string", description: "Optional nonce value if required" }
                  },
                  required: ["protection_policy_name", "protected_data"]
                },
                description: "Array of reveal request objects, each with protected data and policy"
              },
              username: { type: "string", description: "User identity for authorization (required if JWT is not provided)" },
              jwt: { type: "string", description: "JWT token for authorization (required if username is not provided)" }
            },
            required: ["protected_data_array"]
          }
        },
      {
        name: "get_metrics",
        description: "Get CRDP service metrics",
        inputSchema: {
          type: "object",
          properties: {},
          required: []
        }
      },
      {
        name: "check_health",
        description: "Check CRDP service health status",
        inputSchema: {
          type: "object",
          properties: {},
          required: []
        }
      },
      {
        name: "check_liveness",
        description: "Check CRDP service liveness",
        inputSchema: {
          type: "object",
          properties: {},
          required: []
        }
      }
    ] as Tool[]
  };
});

// Prompts handler
server.setRequestHandler(ListPromptsRequestSchema, async (request) => {
  // Check initialization state for stdio transport
  if (!serverState.isInitialized() && process.env.MCP_TRANSPORT !== "streamable-http") {
    throw new McpError(
      ErrorCode.InvalidRequest, 
      "Server not initialized. Send 'notifications/initialized' first."
    );
  }
  
  return {
    prompts: [
      {
        name: "secure_data_processing",
        description: "Guide for secure data processing",
        inputSchema: {
          type: "object",
          properties: {
            data_type: { 
              type: "string", 
              description: "Type of data being processed (e.g., PII, financial, healthcare)" 
            },
            compliance_requirements: { 
              type: "string", 
              description: "Specific compliance requirements (e.g., GDPR, HIPAA, PCI-DSS)" 
            }
          },
          required: []
        }
      },
      {
        name: "compliance_review",
        description: "Review data handling for compliance",
        inputSchema: {
          type: "object",
          properties: {
            regulation: { 
              type: "string", 
              description: "Specific regulation to check compliance against" 
            },
            data_classification: { 
              type: "string", 
              description: "Classification level of the data being reviewed" 
            }
          },
          required: []
        }
      },
      {
        name: "data_protection_advisor",
        description: "Provides advice on data protection strategies using CRDP",
        inputSchema: {
          type: "object",
          properties: {
            data_category: {
              type: "string",
              description: "Category of data requiring protection (e.g., emails, SSNs, credit cards)"
            },
            industry: {
              type: "string",
              description: "Industry context for specific compliance requirements"
            }
          },
          required: ["data_category"]
        }
      }
    ]
  };
});

server.setRequestHandler(GetPromptRequestSchema, async (request) => {
  // Check initialization state for stdio transport
  if (!serverState.isInitialized() && process.env.MCP_TRANSPORT !== "streamable-http") {
    throw new McpError(
      ErrorCode.InvalidRequest, 
      "Server not initialized. Send 'notifications/initialized' first."
    );
  }

  const { name, arguments: args } = request.params;
  
  if (name === "secure_data_processing") {
    const dataType = args?.data_type || "sensitive data";
    const complianceReq = args?.compliance_requirements || "regulatory requirements";
    
    return {
      messages: [
        {
          role: "user",
          content: {
            type: "text",
            text: `You are developing a secure data processing workflow for ${dataType} that must comply with ${complianceReq}.

**CRDP Protection Framework**:

1. **Data Identification**:
   - Identify all ${dataType} elements requiring protection
   - Classify data according to sensitivity levels
   - Map data elements to appropriate protection policies

2. **Protection Implementation**:
   - Use CRDP protect_data tool for individual data elements
   - Use CRDP protect_bulk for multiple data elements
   - Ensure proper policy selection for each data type

3. **Secure Access Control**:
   - Implement proper username-based access control
   - Use reveal_data only when necessary
   - Apply least-privilege principle to all operations

4. **Monitoring and Auditing**:
   - Use check_health to monitor CRDP service status
   - Implement get_metrics for audit trail
   - Document all protection/reveal operations

What specific guidance do you need regarding ${dataType} protection or ${complianceReq} compliance?`
          }
        }
      ]
    };
  }
  
  if (name === "compliance_review") {
    const regulation = args?.regulation || "applicable regulations";
    const classification = args?.data_classification || "classified data";
    
    return {
      messages: [
        {
          role: "user",
          content: {
            type: "text",
            text: `You are reviewing ${classification} for ${regulation} compliance using CRDP protection:

**Compliance Checklist**:
1. **Data Identification**: Catalog all sensitive data elements
2. **Protection Requirements**: Apply CRDP protection based on classification level
3. **Access Controls**: Verify user identity and authorization
4. **Audit Trail**: Ensure all protect/reveal operations are logged
5. **Data Minimization**: Only reveal data when necessary for authorized purposes

**CRDP Compliance Features**:
- Policy-based protection aligned with regulatory requirements
- User-based access controls
- Comprehensive audit logging via metrics
- Secure reveal operations with proper authorization

**Review Process**:
- Check if all sensitive data is properly protected
- Verify access controls are in place
- Ensure audit trails are maintained
- Validate data handling procedures

Use the CRDP tools to demonstrate compliant data handling practices.`
          }
        }
      ]
    };
  }
  
  if (name === "data_protection_advisor") {
    const dataCategory = args?.data_category || "sensitive data";
    const industry = args?.industry || "your industry";
    
    return {
      messages: [
        {
          role: "user",
          content: {
            type: "text",
            text: `I'll help you develop a comprehensive strategy for protecting ${dataCategory} in ${industry} using CRDP.

**Data Protection Strategy for ${dataCategory}**:

1. **Assessment Phase**:
   - Identify all instances of ${dataCategory} in your systems
   - Evaluate current protection measures
   - Determine compliance requirements specific to ${industry}

2. **Implementation Recommendations**:
   - Select appropriate protection policies for ${dataCategory}
   - Configure proper access controls
   - Implement protection using CRDP tools
   - Set up monitoring and auditing

3. **Best Practices for ${industry}**:
   - Industry-specific compliance considerations
   - Data handling procedures
   - Incident response protocols
   - User training requirements

4. **Technical Implementation with CRDP**:
   - Use protect_data or protect_bulk for ${dataCategory}
   - Set up proper reveal authorization controls
   - Implement health and metrics monitoring
   - Ensure proper policy selection

What specific aspects of ${dataCategory} protection in ${industry} would you like me to address?`
          }
        }
      ]
    };
  }
  
  throw new McpError(ErrorCode.InvalidRequest, `Unknown prompt: ${name}`);
});

// Adding resources capabilities (new in protocol version 2025-06-18)
server.setRequestHandler(ListResourcesRequestSchema, async (request) => {
  // Check initialization state for stdio transport
  if (!serverState.isInitialized() && process.env.MCP_TRANSPORT !== "streamable-http") {
    throw new McpError(
      ErrorCode.InvalidRequest, 
      "Server not initialized. Send 'notifications/initialized' first."
    );
  }
  
  return {
    resources: [
      { 
        name: "crdp_protection_policies", 
        description: "Documentation of available CRDP protection policies",
        uri: "crdp:protection-policies"
      },
      { 
        name: "compliance_guidelines", 
        description: "Guidelines for compliance with various regulations",
        uri: "crdp:compliance-guidelines"
      },
      {
        name: "crdp_integration_guide",
        description: "Guide for integrating CRDP with various applications",
        uri: "crdp:integration-guide"
      }
    ]
  };
});

server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  // Check initialization state for stdio transport
  if (!serverState.isInitialized() && process.env.MCP_TRANSPORT !== "streamable-http") {
    throw new McpError(
      ErrorCode.InvalidRequest, 
      "Server not initialized. Send 'notifications/initialized' first."
    );
  }

  // Ensure uri parameter exists
  if (!request.params || !request.params.uri) {
    throw new McpError(
      ErrorCode.InvalidParams,
      "Missing required parameter: uri"
    );
  }

  const { uri } = request.params;
  
  if (uri === "crdp:protection-policies") {
    return {
      contents: [
        {
          type: "text",
          uri: uri,
          text: `# CRDP Protection Policies

## Available Protection Policies

| Policy Name | Description | Use Case | Format Preservation |
|-------------|-------------|----------|---------------------|
| email_policy | Protects email addresses | User accounts, communications | Yes |
| ssn_policy | Protects Social Security Numbers | Identity documents, HR | Yes |
| cc_policy | Protects credit card numbers | Payment processing | Yes |
| phone_policy | Protects phone numbers | Contact information | Yes |
| name_policy | Protects personal names | User profiles | No |
| address_policy | Protects physical addresses | Shipping, billing | No |
| dob_policy | Protects dates of birth | User verification | Yes |

## Policy Usage Guidelines

1. **Selection Criteria**:
   - Choose policies based on data type
   - Consider regulatory requirements
   - Evaluate performance needs

2. **Implementation**:
   - Use the \`protect_data\` tool with the appropriate policy name
   - Example: \`protect_data({data: "john@example.com", protection_policy_name: "email_policy"})\`

3. **Bulk Operations**:
   - Use \`protect_bulk\` for multiple items with same or different policies
   - More efficient than individual calls

4. **Access Control**:
   - All reveal operations require valid username
   - Policy-specific access controls may apply

For detailed policy configuration, consult the CRDP server administrator.`
        }
      ]
    };
  } else if (uri === "crdp:compliance-guidelines") {
    return {
      contents: [
        {
          type: "text",
          uri: uri,
          text: `# Compliance Guidelines for Data Protection

## Regulatory Frameworks

### GDPR (General Data Protection Regulation)
- **Key Requirements**:
  - Protect all personally identifiable information (PII)
  - Ensure data minimization
  - Implement right to be forgotten
  - Maintain data protection records
- **CRDP Implementation**:
  - Use email_policy, name_policy, address_policy
  - Implement username-based access control
  - Enable audit logging through metrics

### HIPAA (Health Insurance Portability and Accountability Act)
- **Key Requirements**:
  - Protect all protected health information (PHI)
  - Implement technical safeguards
  - Maintain access controls
  - Conduct regular security assessments
- **CRDP Implementation**:
  - Use appropriate policies for PHI elements
  - Implement strict username authorization
  - Enable comprehensive audit trails

### PCI DSS (Payment Card Industry Data Security Standard)
- **Key Requirements**:
  - Protect cardholder data
  - Maintain secure networks
  - Implement strong access controls
  - Regularly test security systems
- **CRDP Implementation**:
  - Use cc_policy for all payment information
  - Implement tokenization for processing
  - Enable secure reveal operations

### CCPA/CPRA (California Consumer Privacy Act)
- **Key Requirements**:
  - Honor right to access
  - Enable right to delete
  - Maintain data inventories
  - Provide disclosure of data use
- **CRDP Implementation**:
  - Enable secure data inventory
  - Implement data lifecycle management
  - Support data deletion processes

## Implementation Checklist

1. **Data Inventory**:
   - Identify all data subject to regulations
   - Map to appropriate protection policies

2. **Protection Implementation**:
   - Apply appropriate CRDP policies
   - Configure access controls
   - Enable audit logging

3. **Documentation**:
   - Record all protection measures
   - Document access control policies
   - Maintain processing records

4. **Verification**:
   - Test protection effectiveness
   - Verify access controls
   - Validate audit trails

For regulatory-specific guidance, consult your compliance officer.`
        }
      ]
    };
  } else if (uri === "crdp:integration-guide") {
    return {
      contents: [
        {
          type: "text",
          uri: uri,
          text: `# CRDP Integration Guide

## Integration Methods

### 1. Direct API Integration
- **Implementation**:
  - Connect to CRDP service via HTTP
  - Use JSON-RPC for commands
  - Configure service URLs
- **Best For**:
  - Custom applications
  - High-volume processing
  - Complex workflows

### 2. MCP Protocol Integration
- **Implementation**:
  - Use Model Context Protocol (stdio or HTTP)
  - Follow initialization sequence
  - Utilize tool-based interface
- **Best For**:
  - AI applications
  - LLM integrations
  - Claude Desktop

### 3. SDK Integration
- **Implementation**:
  - Import CRDP client libraries
  - Configure service connections
  - Use native language functions
- **Best For**:
  - Seamless application integration
  - Simplified development
  - Platform-specific deployments

## Architecture Patterns

### Pattern 1: Data at Rest Protection
- Protect data before storage
- Reveal only when needed
- Maintain protection in database

### Pattern 2: Data in Transit Protection
- Protect before transmission
- Transmit protected form
- Reveal only at secure endpoint

### Pattern 3: Tokenization Service
- Replace sensitive data with tokens
- Store mapping in secure service
- Use tokens in application logic

## Implementation Steps

1. **Environment Setup**:
   \`\`\`bash
   # Configure service URLs
   export CRDP_SERVICE_URL="http://crdp-server:8090"
   export CRDP_PROBES_URL="http://crdp-server:8080"
   \`\`\`

2. **Connection Test**:
   \`\`\`bash
   # Test service health
   curl -X GET http://crdp-server:8080/healthz
   \`\`\`

3. **Basic Protection Flow**:
   \`\`\`javascript
   // Protect data
   const protected = await crdpClient.protectData(sensitiveData, "email_policy");
   
   // Store protected data
   
   // Later, reveal when needed
   const revealed = await crdpClient.revealData(protected, "authorized_user", "email_policy");
   \`\`\`

4. **Error Handling**:
   - Implement retry logic
   - Handle service unavailability
   - Validate responses

For detailed integration scenarios, contact CRDP technical support.`
        }
      ]
    };
  } else {
    throw new McpError(ErrorCode.InvalidRequest, `Unknown resource: ${uri}`);
  }
});

// Templates handler
server.setRequestHandler(ListResourceTemplatesRequestSchema, async (request) => {
  // Check initialization state for stdio transport
  if (!serverState.isInitialized() && process.env.MCP_TRANSPORT !== "streamable-http") {
    throw new McpError(
      ErrorCode.InvalidRequest, 
      "Server not initialized. Send 'notifications/initialized' first."
    );
  }
  
  return {
    resourceTemplates: [
      { 
        name: "data_protection_policy", 
        description: "Template for creating a comprehensive data protection policy",
        uriTemplate: "crdp:templates:{name}"
      },
      { 
        name: "incident_response", 
        description: "Template for data breach incident response procedures",
        uriTemplate: "crdp:templates:{name}"
      },
      {
        name: "compliance_audit",
        description: "Template for conducting a data protection compliance audit",
        uriTemplate: "crdp:templates:{name}"
      }
    ]
  };
});

// Note: GetResourceTemplateRequestSchema is not available in the SDK
// We'll support templates/get in the HTTP handler only

async function handleToolCall(name: string, args: any) {
  try {
    switch (name) {
      case "protect_data": {
        const { data, protection_policy_name, jwt } = ProtectDataSchema.parse(args);
        const result = await crdpClient.protectData(data, protection_policy_name, jwt);
        let responseText = `Data protected successfully. Protected data: ${result.protected_data}`;
        if (result.external_version) {
          responseText += `\nExternal version: ${result.external_version}`;
        }
        return { content: [{ type: "text", text: responseText }] };
      }
      case "reveal_data": {
        const { protected_data, username, protection_policy_name, external_version, jwt } = RevealDataSchema.parse(args);
        const revealedData = await crdpClient.revealData(protected_data, username, protection_policy_name, external_version, jwt);
        return { content: [{ type: "text", text: `Data revealed successfully. Revealed data: ${revealedData}` }] };
      }
      case "protect_bulk": {
        const { request_data, jwt } = BulkProtectSchema.parse(args);
        const result = await crdpClient.protectBulk(request_data, jwt);
        return { content: [{ type: "text", text: `Bulk protection completed. Result: ${JSON.stringify(result, null, 2)}` }] };
      }
      case "reveal_bulk": {
        const { protected_data_array, username, jwt } = BulkRevealSchema.parse(args);
        const result = await crdpClient.revealBulk(protected_data_array, username, jwt);
        return { content: [{ type: "text", text: `Bulk reveal completed. Result: ${JSON.stringify(result, null, 2)}` }] };
      }
      case "get_metrics":
        return { content: [{ type: "text", text: JSON.stringify(await crdpClient.getMetrics(), null, 2) }] };
      case "check_health":
        return { content: [{ type: "text", text: JSON.stringify(await crdpClient.checkHealth(), null, 2) }] };
      case "check_liveness":
        return { content: [{ type: "text", text: JSON.stringify(await crdpClient.checkLiveness(), null, 2) }] };
      default:
        throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${name}`);
    }
  } catch (error) {
    if (error instanceof z.ZodError) {
      throw new McpError(ErrorCode.InvalidParams, `Invalid parameters: ${error.errors.map(e => `${e.path.join('.')} - ${e.message}`).join(', ')}`);
    }
    if (axios.isAxiosError(error)) {
      throw new McpError(ErrorCode.InternalError, `CRDP API error: ${error.message}`);
    }
    throw new McpError(ErrorCode.InternalError, `Tool execution failed: ${String(error)}`);
  }
}

// Helper function to check for missing required parameters and provide elicitation
function checkMissingParameters(toolName: string, args: any): string | null {
  const missingParams: string[] = [];
  let elicitationMessage = "";

  switch (toolName) {
    case "protect_data":
      if (!args.data) missingParams.push("data");
      if (!args.protection_policy_name) missingParams.push("protection_policy_name");
      
      if (missingParams.length > 0) {
        elicitationMessage = `Missing required parameters for protect_data: ${missingParams.join(", ")}.\n\n`;
        if (missingParams.includes("data")) {
          elicitationMessage += "• data: The sensitive data you want to protect (e.g., 'john.doe@example.com', '123-45-6789')\n";
        }
        if (missingParams.includes("protection_policy_name")) {
          elicitationMessage += "• protection_policy_name: The CRDP policy to use for protection (e.g., 'email_policy', 'ssn_policy')\n";
        }
        elicitationMessage += "\nPlease provide all required parameters and try again.";
        return elicitationMessage;
      }
      break;

    case "reveal_data":
      if (!args.protected_data) missingParams.push("protected_data");
      if (!args.username && !args.jwt) missingParams.push("username or jwt");
      if (!args.protection_policy_name) missingParams.push("protection_policy_name");
      
      if (missingParams.length > 0) {
        elicitationMessage = `Missing required parameters for reveal_data: ${missingParams.join(", ")}.\n\n`;
        if (missingParams.includes("protected_data")) {
          elicitationMessage += "• protected_data: The encrypted/protected data to reveal (e.g., 'enc_abc123def456')\n";
        }
        if (missingParams.includes("username") && missingParams.includes("jwt")) {
          elicitationMessage += "• username or jwt: The user identity for whom to reveal the data (required for CRDP authorization)\n";
        } else if (missingParams.includes("username")) {
          elicitationMessage += "• username: The user identity for whom to reveal the data (required for CRDP authorization)\n";
        } else if (missingParams.includes("jwt")) {
          elicitationMessage += "• jwt: The JWT token for authorization (required for CRDP authorization)\n";
        }
        if (missingParams.includes("protection_policy_name")) {
          elicitationMessage += "• protection_policy_name: The policy used for protection (e.g., 'email_policy')\n";
        }
        elicitationMessage += "\nOptional parameters:\n";
        elicitationMessage += "• external_version: Version information for the protected data\n";
        elicitationMessage += "\nPlease provide all required parameters and try again.";
        return elicitationMessage;
      }
      break;

    case "protect_bulk":
      if (!args.request_data) {
        elicitationMessage = `Missing required parameter for protect_bulk: request_data.\n\n`;
        elicitationMessage += "• request_data: Array of objects, each containing:\n";
        elicitationMessage += "  - protection_policy_name (string): CRDP policy name\n";
        elicitationMessage += "  - data (string): The data to protect\n\n";
        elicitationMessage += "Example:\n";
        elicitationMessage += `[\n  {"protection_policy_name": "email_policy", "data": "john@example.com"},\n  {"protection_policy_name": "ssn_policy", "data": "123-45-6789"}\n]`;
        elicitationMessage += "\n\nPlease provide the required parameter and try again.";
        return elicitationMessage;
      }
      
      // Check each item in the array
      if (Array.isArray(args.request_data)) {
        const invalidItems: string[] = [];
        args.request_data.forEach((item: any, index: number) => {
          const itemMissing: string[] = [];
          if (!item.protection_policy_name) itemMissing.push("protection_policy_name");
          if (!item.data) itemMissing.push("data");
          if (itemMissing.length > 0) {
            invalidItems.push(`Item ${index + 1}: missing ${itemMissing.join(", ")}`);
          }
        });
        
        if (invalidItems.length > 0) {
          elicitationMessage = `Invalid items in protect_bulk request_data:\n\n`;
          elicitationMessage += invalidItems.join("\n") + "\n\n";
          elicitationMessage += "Each item must contain:\n";
          elicitationMessage += "• protection_policy_name (string): CRDP policy name\n";
          elicitationMessage += "• data (string): The data to protect\n";
          elicitationMessage += "\nPlease fix the invalid items and try again.";
          return elicitationMessage;
        }
      }
      break;

    case "reveal_bulk":
      if (!args.protected_data_array) missingParams.push("protected_data_array");
      if (!args.username && !args.jwt) missingParams.push("username or jwt");
      
      if (missingParams.length > 0) {
        elicitationMessage = `Missing required parameters for reveal_bulk: ${missingParams.join(", ")}.\n\n`;
        if (missingParams.includes("protected_data_array")) {
          elicitationMessage += "• protected_data_array: Array of objects, each containing:\n";
          elicitationMessage += "  - protection_policy_name (string): CRDP policy name\n";
          elicitationMessage += "  - protected_data (string): The protected data to reveal\n";
          elicitationMessage += "  - external_version (string, optional): Version information\n";
          elicitationMessage += "  - nonce (string, optional): Nonce value\n\n";
        }
        if (missingParams.includes("username") && missingParams.includes("jwt")) {
          elicitationMessage += "• username or jwt: The user identity for whom to reveal the data (required for CRDP authorization)\n";
        } else if (missingParams.includes("username")) {
          elicitationMessage += "• username: The user identity for whom to reveal the data (required for CRDP authorization)\n";
        } else if (missingParams.includes("jwt")) {
          elicitationMessage += "• jwt: The JWT token for authorization (required for CRDP authorization)\n";
        }
        elicitationMessage += "\nExample:\n";
        elicitationMessage += `{\n  "username": "john_doe",\n  "protected_data_array": [\n    {"protection_policy_name": "email_policy", "protected_data": "enc_abc123"},\n    {"protection_policy_name": "ssn_policy", "protected_data": "enc_def456"}\n  ]\n}`;
        elicitationMessage += "\n\nPlease provide all required parameters and try again.";
        return elicitationMessage;
      }
      
      // Check each item in the array
      if (Array.isArray(args.protected_data_array)) {
        const invalidItems: string[] = [];
        args.protected_data_array.forEach((item: any, index: number) => {
          const itemMissing: string[] = [];
          if (!item.protection_policy_name) itemMissing.push("protection_policy_name");
          if (!item.protected_data) itemMissing.push("protected_data");
          if (itemMissing.length > 0) {
            invalidItems.push(`Item ${index + 1}: missing ${itemMissing.join(", ")}`);
          }
        });
        
        if (invalidItems.length > 0) {
          elicitationMessage = `Invalid items in reveal_bulk protected_data_array:\n\n`;
          elicitationMessage += invalidItems.join("\n") + "\n\n";
          elicitationMessage += "Each item must contain:\n";
          elicitationMessage += "• protection_policy_name (string): CRDP policy name\n";
          elicitationMessage += "• protected_data (string): The protected data to reveal\n";
          elicitationMessage += "\nOptional for each item:\n";
          elicitationMessage += "• external_version (string): Version information\n";
          elicitationMessage += "• nonce (string): Nonce value\n";
          elicitationMessage += "\nPlease fix the invalid items and try again.";
          return elicitationMessage;
        }
      }
      break;

    // Metrics and health check tools don't require parameters
    case "get_metrics":
    case "check_health":
    case "check_liveness":
      break;

    default:
      elicitationMessage = `Unknown tool: ${toolName}. Available tools: protect_data, reveal_data, protect_bulk, reveal_bulk, get_metrics, check_health, check_liveness`;
      return elicitationMessage;
  }

  return null; // No missing parameters
}

// Call tool request handler
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  // Check initialization state for stdio transport
  if (!serverState.isInitialized() && process.env.MCP_TRANSPORT !== "streamable-http") {
    throw new McpError(
      ErrorCode.InvalidRequest, 
      "Server not initialized. Send 'notifications/initialized' first."
    );
  }

  const { name, arguments: args } = request.params;
  
  const missingParamMessage = checkMissingParameters(name, args);
  if (missingParamMessage) {
    throw new McpError(
      ErrorCode.InvalidParams,
      missingParamMessage
    );
  }

  return await handleToolCall(name, args);
});

// Streamable HTTP handler function
async function runStreamableHttp(port: number = 3000) {
  const app = express();
  app.use(express.json());

  app.post("/mcp", async (req, res) => {
    try {
      const message = req.body;
      let response;

      console.error(`HTTP request: ${JSON.stringify(message)}`);

      if (!message || !message.method) {
        return res.status(400).json({ 
          jsonrpc: "2.0", 
          error: { 
            code: -32600, 
            message: "Invalid Request: Missing method" 
          },
          id: message.id || null
        });
      }
      
      if (message.method === "initialize") {
        response = {
          jsonrpc: "2.0",
          id: message.id,
          result: {
            protocolVersion: "2025-06-18", // Updated to latest protocol version
            capabilities: {
              tools: {},
              prompts: {},
              resources: {}, // Added resources capability
              templates: {} // Added templates capability
            },
            serverInfo: {
              name: "crdp-mcp-server",
              version: "1.0.0"
            }
          }
        };
      } else if (message.method === "tools/list") {
        response = {
          jsonrpc: "2.0",
          id: message.id,
          result: {
            tools: [
              {
                name: "protect_data",
                description: "Protect sensitive data using CipherTrust CRDP. If CRDP is running with JWT verification enabled, 'jwt' is required. 'username' is not supported for protect tools.",
                inputSchema: {
                  type: "object",
                  properties: {
                    data: { type: "string", description: "The data to protect" },
                    protection_policy_name: { type: "string", description: "Protection policy name" },
                    jwt: { type: "string", description: "JWT token for authorization (optional)" }
                  },
                  required: ["data", "protection_policy_name"]
                }
              },
              {
                name: "reveal_data",
                description: "Reveal protected data using CipherTrust CRDP. At least one of 'username' or 'jwt' must be provided for reveal operations.",
                inputSchema: {
                  type: "object",
                  properties: {
                    protected_data: { type: "string", description: "The protected data to reveal" },
                    username: { type: "string", description: "User identity for authorization (required if JWT is not provided)" },
                    protection_policy_name: { type: "string", description: "Policy name used for protection" },
                    external_version: { type: "string", description: "Version header information." },
                    jwt: { type: "string", description: "JWT token for authorization (required if username is not provided)" }
                  },
                  required: ["protected_data", "protection_policy_name"]
                }
              },
              {
                name: "protect_bulk",
                description: "Protect multiple data items in a single batch operation. Takes an array of data items to protect. If CRDP is running with JWT verification enabled, 'jwt' is required.",
                inputSchema: {
                  type: "object",
                  properties: {
                    request_data: {
                      type: "array",
                      items: {
                        type: "object",
                        properties: {
                          protection_policy_name: { type: "string", description: "Policy name to apply to this data item" },
                          data: { type: "string", description: "Sensitive data to protect" }
                        },
                        required: ["protection_policy_name", "data"]
                      },
                      description: "Array of protection request objects, each with data and policy"
                    },
                    jwt: { type: "string", description: "JWT token for authorization (required if CRDP has JWT verification enabled)" }
                  },
                  required: ["request_data"]
                }
              },
              {
                name: "reveal_bulk",
                description: "Reveal multiple protected data items in a single batch operation. At least one of 'username' or 'jwt' must be provided for reveal operations.",
                inputSchema: {
                  type: "object",
                  properties: {
                    protected_data_array: {
                      type: "array",
                      items: {
                        type: "object",
                        properties: {
                          protection_policy_name: { type: "string", description: "Policy name used for protection" },
                          protected_data: { type: "string", description: "Protected data to reveal" },
                          external_version: { type: "string", description: "Version information if using external versioning" },
                          nonce: { type: "string", description: "Optional nonce value if required" }
                        },
                        required: ["protection_policy_name", "protected_data"]
                      },
                      description: "Array of reveal request objects, each with protected data and policy"
                    },
                    username: { type: "string", description: "User identity for authorization (required if JWT is not provided)" },
                    jwt: { type: "string", description: "JWT token for authorization (required if username is not provided)" }
                  },
                  required: ["protected_data_array"]
                }
              },
              {
                name: "get_metrics",
                description: "Get CRDP service metrics",
                inputSchema: { type: "object", properties: {}, required: [] }
              },
              {
                name: "check_health",
                description: "Check CRDP service health status",
                inputSchema: { type: "object", properties: {}, required: [] }
              },
              {
                name: "check_liveness",
                description: "Check CRDP service liveness",
                inputSchema: { type: "object", properties: {}, required: [] }
              }
            ]
          }
        };
      } else if (message.method === "tools/call") {
        // For HTTP transport, we don't enforce initialization (used for direct API testing)
        // But stdio transport requires proper MCP initialization sequence
        const toolResult = await handleToolCall(message.params.name, message.params.arguments);
        response = {
          jsonrpc: "2.0",
          id: message.id,
          result: toolResult
        };
      } else if (message.method === "prompts/list") {
        response = {
          jsonrpc: "2.0",
          id: message.id,
          result: {
            prompts: [
              { 
                name: "secure_data_processing", 
                description: "Guide for secure data processing",
                inputSchema: {
                  type: "object",
                  properties: {
                    data_type: { 
                      type: "string", 
                      description: "Type of data being processed (e.g., PII, financial, healthcare)" 
                    },
                    compliance_requirements: { 
                      type: "string", 
                      description: "Specific compliance requirements (e.g., GDPR, HIPAA, PCI-DSS)" 
                    }
                  },
                  required: []
                }
              },
              { 
                name: "compliance_review", 
                description: "Review data handling for compliance",
                inputSchema: {
                  type: "object",
                  properties: {
                    regulation: { 
                      type: "string", 
                      description: "Specific regulation to check compliance against" 
                    },
                    data_classification: { 
                      type: "string", 
                      description: "Classification level of the data being reviewed" 
                    }
                  },
                  required: []
                }
              },
              {
                name: "data_protection_advisor",
                description: "Provides advice on data protection strategies using CRDP",
                inputSchema: {
                  type: "object",
                  properties: {
                    data_category: {
                      type: "string",
                      description: "Category of data requiring protection (e.g., emails, SSNs, credit cards)"
                    },
                    industry: {
                      type: "string",
                      description: "Industry context for specific compliance requirements"
                    }
                  },
                  required: ["data_category"]
                }
              }
            ]
          }
        };
      } else if (message.method === "prompts/get") {
        const { name, arguments: args } = message.params;
        
        if (name === "secure_data_processing") {
          const dataType = args?.data_type || "sensitive data";
          const complianceReq = args?.compliance_requirements || "regulatory requirements";
          
          response = {
            jsonrpc: "2.0",
            id: message.id,
            result: {
              messages: [
                {
                  role: "user",
                  content: {
                    type: "text",
                    text: `You are developing a secure data processing workflow for ${dataType} that must comply with ${complianceReq}.

**CRDP Protection Framework**:

1. **Data Identification**:
   - Identify all ${dataType} elements requiring protection
   - Classify data according to sensitivity levels
   - Map data elements to appropriate protection policies

2. **Protection Implementation**:
   - Use CRDP protect_data tool for individual data elements
   - Use CRDP protect_bulk for multiple data elements
   - Ensure proper policy selection for each data type

3. **Secure Access Control**:
   - Implement proper username-based access control
   - Use reveal_data only when necessary
   - Apply least-privilege principle to all operations

4. **Monitoring and Auditing**:
   - Use check_health to monitor CRDP service status
   - Implement get_metrics for audit trail
   - Document all protection/reveal operations

What specific guidance do you need regarding ${dataType} protection or ${complianceReq} compliance?`
                  }
                }
              ]
            }
          };
        } else if (name === "compliance_review") {
          const regulation = args?.regulation || "applicable regulations";
          const classification = args?.data_classification || "classified data";
          
          response = {
            jsonrpc: "2.0",
            id: message.id,
            result: {
              messages: [
                {
                  role: "user",
                  content: {
                    type: "text",
                    text: `You are reviewing ${classification} for ${regulation} compliance using CRDP protection:

**Compliance Checklist**:
1. **Data Identification**: Catalog all sensitive data elements
2. **Protection Requirements**: Apply CRDP protection based on classification level
3. **Access Controls**: Verify user identity and authorization
4. **Audit Trail**: Ensure all protect/reveal operations are logged
5. **Data Minimization**: Only reveal data when necessary for authorized purposes

**CRDP Compliance Features**:
- Policy-based protection aligned with regulatory requirements
- User-based access controls
- Comprehensive audit logging via metrics
- Secure reveal operations with proper authorization

**Review Process**:
- Check if all sensitive data is properly protected
- Verify access controls are in place
- Ensure audit trails are maintained
- Validate data handling procedures

Use the CRDP tools to demonstrate compliant data handling practices.`
                  }
                }
              ]
            }
          };
        } else if (name === "data_protection_advisor") {
          const dataCategory = args?.data_category || "sensitive data";
          const industry = args?.industry || "your industry";
          
          response = {
            jsonrpc: "2.0",
            id: message.id,
            result: {
              messages: [
                {
                  role: "user",
                  content: {
                    type: "text",
                    text: `I'll help you develop a comprehensive strategy for protecting ${dataCategory} in ${industry} using CRDP.

**Data Protection Strategy for ${dataCategory}**:

1. **Assessment Phase**:
   - Identify all instances of ${dataCategory} in your systems
   - Evaluate current protection measures
   - Determine compliance requirements specific to ${industry}

2. **Implementation Recommendations**:
   - Select appropriate protection policies for ${dataCategory}
   - Configure proper access controls
   - Implement protection using CRDP tools
   - Set up monitoring and auditing

3. **Best Practices for ${industry}**:
   - Industry-specific compliance considerations
   - Data handling procedures
   - Incident response protocols
   - User training requirements

4. **Technical Implementation with CRDP**:
   - Use protect_data or protect_bulk for ${dataCategory}
   - Set up proper reveal authorization controls
   - Implement health and metrics monitoring
   - Ensure proper policy selection

What specific aspects of ${dataCategory} protection in ${industry} would you like me to address?`
                  }
                }
            ]
          }
        };
      } else {
        response = {
          jsonrpc: "2.0",
          id: message.id,
          error: {
            code: -32601,
              message: `Unknown prompt: ${name}`
            }
          };
        }
      } else if (message.method === "resources/list") {
        response = {
          jsonrpc: "2.0",
          id: message.id,
          result: {
            resources: [
              { name: "crdp_protection_policies", description: "Documentation of available CRDP protection policies", uri: "crdp:protection-policies" },
              { name: "compliance_guidelines", description: "Guidelines for compliance with various regulations", uri: "crdp:compliance-guidelines" },
              { name: "crdp_integration_guide", description: "Guide for integrating CRDP with various applications", uri: "crdp:integration-guide" }
            ]
          }
        };
      } else if (message.method === "templates/list" || message.method === "resources/templates/list") {
        // Handle both correct method name and MCP Inspector's incorrect method name
        response = {
          jsonrpc: "2.0",
          id: message.id,
          result: {
            resourceTemplates: [
              { name: "data_protection_policy", description: "Template for creating a comprehensive data protection policy", uriTemplate: "crdp:templates:{name}" },
              { name: "incident_response", description: "Template for data breach incident response procedures", uriTemplate: "crdp:templates:{name}" },
              { name: "compliance_audit", description: "Template for conducting a data protection compliance audit", uriTemplate: "crdp:templates:{name}" }
            ]
          }
        };
      } else if (message.method === "templates/get" || message.method === "templates/read") {
        // Check for missing name parameter
        if (!message.params || !message.params.name) {
          response = {
            jsonrpc: "2.0",
            id: message.id,
            error: {
              code: -32602,
              message: "Missing required parameter: name"
            }
          };
          res.setHeader("Content-Type", "application/json");
          res.json(response);
          return;
        }

        const { name } = message.params;
        if (name === "data_protection_policy") {
          response = {
            jsonrpc: "2.0",
            id: message.id,
            result: {
              content: [
                {
                  type: "text",
                  text: `# Data Protection Policy Template

## 1. Introduction
[Organization Name] is committed to protecting the confidentiality, integrity, and availability of all data it processes and stores. This policy outlines the procedures and controls implemented to achieve this goal.

## 2. Scope
This policy applies to all [Organization Name] data, systems, activities, and employees.

## 3. Data Classification
All data must be classified according to the following sensitivity levels:
- **Public**: Information that can be freely shared
- **Internal**: Information for use within the organization
- **Confidential**: Sensitive business information
- **Restricted**: Highly sensitive personal or business information

## 4. Protection Requirements by Classification

| Classification | Protection Method | Access Control | Encryption | Retention |
|---------------|-----------------|--------------|-----------|-----------|
| Public | Standard | Public | Optional | As needed |
| Internal | Standard | All employees | In transit | 3 years |
| Confidential | CRDP Policy | Authorized staff | In transit & at rest | 5 years |
| Restricted | CRDP Policy | Named individuals | End-to-end | 7 years |

## 5. CRDP Protection Policies

The following CRDP protection policies must be applied:
- **PII Data**: Use email_policy, name_policy, phone_policy
- **Financial Data**: Use cc_policy, account_policy
- **Health Information**: Use health_policy
- **Access Credentials**: Use credentials_policy

## 6. Responsibilities
- **Data Owners**: Responsible for classification
- **IT Department**: Responsible for implementing controls
- **Employees**: Responsible for following procedures
- **CISO**: Responsible for oversight and compliance

## 7. Procedures
1. All new data must be classified before processing
2. All restricted and confidential data must use CRDP protection
3. Annual review of all data classifications
4. Quarterly audit of protection measures

## 8. Compliance Monitoring
- Regular scanning for unprotected sensitive data
- Access log reviews
- Protection policy reviews
- Employee training and awareness

## 9. Incident Response
In the event of a data protection incident:
1. Immediate containment
2. CISO notification
3. Investigation
4. Remediation
5. Documentation

## 10. Review and Updates
This policy will be reviewed annually and updated as required.

---

**Last Reviewed**: [DATE]  
**Approved By**: [NAME], [POSITION]`
                }
              ]
            }
          };
        } else if (name === "incident_response") {
          // For brevity, we're only including template headers - full content would be included in real implementation
          response = {
            jsonrpc: "2.0",
            id: message.id,
            result: {
              content: [
                {
                  type: "text",
                  text: `# Data Breach Incident Response Procedure

## 1. Purpose
This procedure defines the steps to be taken in the event of a suspected or confirmed data breach.

## 2. Scope
This procedure covers all incidents involving unauthorized access, disclosure, or loss of protected data.

## 3. Incident Response Team
...`
                }
              ]
            }
          };
        } else if (name === "compliance_audit") {
          // For brevity, we're only including template headers - full content would be included in real implementation
          response = {
            jsonrpc: "2.0",
            id: message.id,
            result: {
              content: [
                {
                  type: "text",
                  text: `# Data Protection Compliance Audit Template

## 1. Audit Information
**Audit Date**: [DATE]  
**Auditor**: [NAME], [POSITION]  
**Scope**: [SYSTEMS/DATA IN SCOPE]  
**Regulatory Focus**: [REGULATIONS]

## 2. Executive Summary
...`
                }
              ]
            }
          };
        } else {
          response = {
            jsonrpc: "2.0",
            id: message.id,
            error: {
              code: -32601,
              message: `Unknown template: ${name}`
            }
          };
        }
      } else if (message.method === "resources/read") {
        // Check for missing uri parameter
        if (!message.params || !message.params.uri) {
          response = {
            jsonrpc: "2.0",
            id: message.id,
            error: {
              code: -32602,
              message: "Missing required parameter: uri"
            }
          };
      res.setHeader("Content-Type", "application/json");
      res.json(response);
          return;
        }

        const { uri } = message.params;
        if (uri === "crdp:protection-policies") {
          response = {
            jsonrpc: "2.0",
            id: message.id,
            result: {
              contents: [
                {
                  type: "text",
                  uri: uri,
                  text: `# CRDP Protection Policies

## Available Protection Policies

| Policy Name | Description | Use Case | Format Preservation |
|-------------|-------------|----------|---------------------|
| email_policy | Protects email addresses | User accounts, communications | Yes |
| ssn_policy | Protects Social Security Numbers | Identity documents, HR | Yes |
| cc_policy | Protects credit card numbers | Payment processing | Yes |
| phone_policy | Protects phone numbers | Contact information | Yes |
| name_policy | Protects personal names | User profiles | No |
| address_policy | Protects physical addresses | Shipping, billing | No |
| dob_policy | Protects dates of birth | User verification | Yes |

## Policy Usage Guidelines

1. **Selection Criteria**:
   - Choose policies based on data type
   - Consider regulatory requirements
   - Evaluate performance needs

2. **Implementation**:
   - Use the \`protect_data\` tool with the appropriate policy name
   - Example: \`protect_data({data: "john@example.com", protection_policy_name: "email_policy"})\`

3. **Bulk Operations**:
   - Use \`protect_bulk\` for multiple items with same or different policies
   - More efficient than individual calls

4. **Access Control**:
   - All reveal operations require valid username
   - Policy-specific access controls may apply

For detailed policy configuration, consult the CRDP server administrator.`
                }
              ]
            }
          };
        } else if (uri === "crdp:compliance-guidelines") {
          response = {
            jsonrpc: "2.0",
            id: message.id,
            result: {
              contents: [
                {
                  type: "text",
                  uri: uri,
                  text: `# Compliance Guidelines for Data Protection

## Regulatory Frameworks

### GDPR (General Data Protection Regulation)
- **Key Requirements**:
  - Protect all personally identifiable information (PII)
  - Ensure data minimization
  - Implement right to be forgotten
  - Maintain data protection records
- **CRDP Implementation**:
  - Use email_policy, name_policy, address_policy
  - Implement username-based access control
  - Enable audit logging through metrics

### HIPAA (Health Insurance Portability and Accountability Act)
- **Key Requirements**:
  - Protect all protected health information (PHI)
  - Implement technical safeguards
  - Maintain access controls
  - Conduct regular security assessments
- **CRDP Implementation**:
  - Use appropriate policies for PHI elements
  - Implement strict username authorization
  - Enable comprehensive audit trails

### PCI DSS (Payment Card Industry Data Security Standard)
- **Key Requirements**:
  - Protect cardholder data
  - Maintain secure networks
  - Implement strong access controls
  - Regularly test security systems
- **CRDP Implementation**:
  - Use cc_policy for all payment information
  - Implement tokenization for processing
  - Enable secure reveal operations

### CCPA/CPRA (California Consumer Privacy Act)
- **Key Requirements**:
  - Honor right to access
  - Enable right to delete
  - Maintain data inventories
  - Provide disclosure of data use
- **CRDP Implementation**:
  - Enable secure data inventory
  - Implement data lifecycle management
  - Support data deletion processes

## Implementation Checklist

1. **Data Inventory**:
   - Identify all data subject to regulations
   - Map to appropriate protection policies

2. **Protection Implementation**:
   - Apply appropriate CRDP policies
   - Configure access controls
   - Enable audit logging

3. **Documentation**:
   - Record all protection measures
   - Document access control policies
   - Maintain processing records

4. **Verification**:
   - Test protection effectiveness
   - Verify access controls
   - Validate audit trails

For regulatory-specific guidance, consult your compliance officer.`
                }
              ]
            }
          };
        } else if (uri === "crdp:integration-guide") {
          response = {
            jsonrpc: "2.0",
            id: message.id,
            result: {
              contents: [
                {
                  type: "text",
                  uri: uri,
                  text: `# CRDP Integration Guide

## Integration Methods

### 1. Direct API Integration
- **Implementation**:
  - Connect to CRDP service via HTTP
  - Use JSON-RPC for commands
  - Configure service URLs
- **Best For**:
  - Custom applications
  - High-volume processing
  - Complex workflows

### 2. MCP Protocol Integration
- **Implementation**:
  - Use Model Context Protocol (stdio or HTTP)
  - Follow initialization sequence
  - Utilize tool-based interface
- **Best For**:
  - AI applications
  - LLM integrations
  - Claude Desktop

### 3. SDK Integration
- **Implementation**:
  - Import CRDP client libraries
  - Configure service connections
  - Use native language functions
- **Best For**:
  - Seamless application integration
  - Simplified development
  - Platform-specific deployments

## Architecture Patterns

### Pattern 1: Data at Rest Protection
- Protect data before storage
- Reveal only when needed
- Maintain protection in database

### Pattern 2: Data in Transit Protection
- Protect before transmission
- Transmit protected form
- Reveal only at secure endpoint

### Pattern 3: Tokenization Service
- Replace sensitive data with tokens
- Store mapping in secure service
- Use tokens in application logic

## Implementation Steps

1. **Environment Setup**:
   \`\`\`bash
   # Configure service URLs
   export CRDP_SERVICE_URL="http://crdp-server:8090"
   export CRDP_PROBES_URL="http://crdp-server:8080"
   \`\`\`

2. **Connection Test**:
   \`\`\`bash
   # Test service health
   curl -X GET http://crdp-server:8080/healthz
   \`\`\`

3. **Basic Protection Flow**:
   \`\`\`javascript
   // Protect data
   const protected = await crdpClient.protectData(sensitiveData, "email_policy");
   
   // Store protected data
   
   // Later, reveal when needed
   const revealed = await crdpClient.revealData(protected, "authorized_user", "email_policy");
   \`\`\`

4. **Error Handling**:
   - Implement retry logic
   - Handle service unavailability
   - Validate responses

For detailed integration scenarios, contact CRDP technical support.`
                }
              ]
            }
          };
        } else {
          response = {
            jsonrpc: "2.0",
            id: message.id,
            error: {
              code: -32601,
              message: `Unknown resource: ${uri}`
            }
          };
        }
      }

      res.setHeader("Content-Type", "application/json");
      res.json(response);
  return;

    } catch (error) {
      console.error("Error handling MCP request:", error);
      res.status(500).json({
        jsonrpc: "2.0",
        id: req.body?.id,
        error: {
          code: -32603,
          message: "Internal error",
          data: error instanceof Error ? error.message : String(error)
        }
      });
  return;
    }
  });

  // Health check endpoint
  app.get("/health", (req, res) => {
    res.json({ 
      status: "healthy", 
      timestamp: new Date().toISOString(),
      transport: "streamable-http"
    });
  });

  // Basic info endpoint
  app.get("/", (req, res) => {
    res.json({ 
      name: "crdp-mcp-server", 
      version: "1.0.0",
      status: "running",
      transport: "streamable-http",
      endpoints: {
        mcp: "/mcp",
        health: "/health"
      }
    });
  });

  app.listen(port, () => {
    console.error(`CRDP MCP Server listening on port ${port}`);
    console.error(`MCP endpoint: http://localhost:${port}/mcp`);
    console.error(`CRDP backend: ${CRDP_SERVICE_URL}`);
  });
}

// Main execution
async function main() {
  const transport = process.env.MCP_TRANSPORT || "stdio";
  const port = parseInt(process.env.MCP_PORT || "3000");
  
  if (transport === "streamable-http") {
    await runStreamableHttp(port);
  } else {
    // Default: stdio transport only
    const stdioTransport = new StdioServerTransport();
    await server.connect(stdioTransport);
    console.error("CRDP MCP Server running on stdio");
  }
}

if (require.main === module) {
  main().catch((error) => {
    console.error("Failed to start CRDP MCP Server:", error);
    process.exit(1);
  });
} 