# Example Prompts for CipherTrust Manager MCP Server

This document contains example prompts that you can use to test the CipherTrust Manager MCP Server with AI assistants like Claude Desktop or Cursor. These prompts demonstrate various CipherTrust Manager operations and can serve as both testing scenarios and usage examples.

## Prerequisites

- CipherTrust Manager MCP Server configured and running
- Valid CipherTrust Manager environment with appropriate permissions
- AI assistant (Claude Desktop/Cursor) configured with the MCP server

## How to Use These Prompts

1. Copy and paste any prompt into your AI assistant chat
2. The AI assistant will use the CipherTrust Manager MCP Server to execute the operations
3. Modify the prompts as needed for your specific environment (IP addresses, domain names, etc.)

---

## Key Management

Use the configured MCP server and perform the following actions:

1. Create an AES 256 bit key called `key1` in the root domain.
2. Create an AES 256 bit key called `key2`. This key must be unexportable.
3. Create an AES 256 bit key called `key3`. This key must be undeleteable.
4. Create an AES 256 bit key called `key4`. This key must be undeleteable and unexportable.
5. Create a key called `LDTKey` to be used with a CTE LDT policy.
6. Export keys `key1` and `LDTKey` and only show me the material of the keys.

Now, create a new domain called `domain1` with admin user as the admin and the default CA as the parent CA. Once done, create the same keys as above in this domain!

Keep your responses short/brief.

---

## User and Group Management

Use the configured MCP server and perform the following actions:

1. Create a new user in the root domain with username `user1` and password `Thales123!`.
2. Create a new user in the root domain with username `user2` and password `Thales123!`. His email is `user2@thales.com`.
3. Create a new group in the root domain with name `thales`. Add users `user1` and `user2` to this group.

---

## System Management and Service Management

Use the configured MCP server and perform the following actions:

1. Tell me the version of the configured CipherTrust Manager.
2. What is the status of the nae and web services on the CipherTrust manager?
3. Forcefully restart the nae service.
4. Set the name of this CipherTrust manager to "demo-instance".
5. List the names and values of all the system properties.
6. Set the value of `MAXIMUM_REFRESH_TOKEN_LIFETIME` property to `24h` and list all properties again.

---

## Cluster Management

Use the configured MCP server and perform the following actions:

1. Is the CipherTrust manager clustered?
2. Create a cluster on this CipherTrust manager. The public address is same as the local host IP which is `10.160.0.100`.
3. After creating the new cluster, add a new node, using fulljoin, to the cluster. Here are the details:

   - **Member node** (existing cluster node): `10.160.0.100`
   - **New node host**: `10.160.0.101`
   - **New node public address**: `10.160.0.101`
   - **New node credentials**:
     - Username: `admin`
     - Password: `Thales123!`
     - URL: `https://10.160.0.101:443`

   Automatically confirm all prompts.

---

## License Management

Use the configured MCP server and perform the following actions:

1. Tell me which licenses are currently active on the CipherTrust manager.
2. Are there any expired licenses or about to expire licenses? When will these licenses expire/deactivate?
3. Do I have the CTE or RWP licenses installed/active?
4. What are the lock codes of the CipherTrust manager?

---

## CTE Operations

Use the configured MCP server and perform the following actions:

1. Create a CTE userset called `US01`. Add the user `Administrator` (uname) and `thales.com` (os_domain) to this user set.
2. Create a new key called `cte_key` to be used with a CTE LDT policy.
3. Create a new LDT policy called `ldtpolicy01`. In the policy, `US01` userset should have permit and apply_key permissions along with all_ops action. Everybody else should be denied by default. For key rules/transformation rules, use `clear_key` as the current key and `cte_key` as the transformation key.
4. Set a guardpoint on `C:\Data` on win-cte-client CTE client on the CipherTrust manager using the LDT policy created above.
```
These actions can also be performed inside a domain.
```
---

## Crypto Operations

Use the configured MCP server and perform the following actions:

### Format Preserving Encryption (FPE)
1. Hide text "I am a Sales Engineer at Thales" using key `key1` (Create if it does not exist)... Use "alphanumeric" as the hint.
2. Then unhide the output from above...

### Encrypt/Decrypt
1. Encrypt text "Hey there!" using an AES Key `key1`. Use any AES Cipher.
2. Decrypt the ciphertext generated above using the output ciphertext blob generated above including the id.

---

## Akeyless Operations

Use the configured MCP server and perform the following actions:

1. Show me the current akeyless configuration.
2. List all akeyless customer fragments.
3. Generate a new customer fragment with a random name.
4. Generate an akeyless token.

---

## Quorum Management

Use the configured MCP server and perform the following actions:

1. Show me a list of all quorum policies.
2. Are any quorum policies active/enabled?
3. Activate/Enable the delete key quorum policy with the default settings.
4. Are there any quorum profiles?

---

## Custom Testing Scenarios

You can create your own testing scenarios by combining different operations. Here are some ideas:

### Scenario 1: Complete Key Lifecycle
```
Use the MCP server to:
1. Create a new domain called "test-domain"
2. Create an AES-256 key in that domain
3. Export the key material
4. Use the key for encryption operations
5. Delete the key
6. Clean up the domain
```

### Scenario 2: User Access Management
```
Use the MCP server to:
1. Create a new user with specific permissions
2. Create a group and add the user to it
3. Test the user's access to different operations
4. Modify the user's permissions
5. Remove the user from the group
```

### Scenario 3: Security Policy Testing
```
Use the MCP server to:
1. Create a CTE policy with specific access rules
2. Test the policy with different user sets
3. Modify the policy rules
4. Apply the policy to a guardpoint
5. Verify the policy is working correctly
```

## Tips for Using These Prompts

1. **Environment Specific**: Modify IP addresses, domain names, and credentials to match your environment
2. **Prerequisites**: Ensure you have the necessary permissions in CipherTrust Manager
3. **Error Handling**: If operations fail, ask the AI assistant to check error messages and retry with corrections
4. **Incremental Testing**: Start with simple operations before moving to complex scenarios
5. **Documentation**: Use these prompts to understand the capabilities of your MCP server

## Troubleshooting Prompts

If you encounter issues, try these diagnostic prompts:

```
Use the MCP server to show me:
1. The current connection status to CipherTrust Manager
2. Available tools and their descriptions
3. The current user's permissions
4. System status and any error messages
```

```
Use the MCP server to test:
1. Basic connectivity with a simple system information request
2. Authentication by listing available domains
3. Key management permissions by listing existing keys
```

## Contributing Additional Prompts

When adding new example prompts:

1. Follow the existing format and structure
2. Include clear, step-by-step instructions
3. Specify any prerequisites or requirements
4. Test the prompts in your environment
5. Document expected outcomes where helpful

---

**Note**: These prompts are designed to work with the CipherTrust Manager MCP Server. Ensure your server is properly configured and you have appropriate permissions before executing these prompts.