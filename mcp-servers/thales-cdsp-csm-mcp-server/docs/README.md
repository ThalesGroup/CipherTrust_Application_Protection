# Documentation Overview

Docs for the Thales CSM MCP Server.

## 📚 **Available Docs**

| Document | Purpose | What You'll Find |
|----------|---------|------------------|
| **[TESTING.md](TESTING.md)** | How to test | Run test script |
| **[TRANSPORT_MODES.md](TRANSPORT_MODES.md)** | How to run | stdio vs HTTP modes |
| **[TOOLS.md](TOOLS.md)** | What tools do | Tool reference, examples |
| **[TESTING.md](TESTING.md)** | How to test | Complete testing guide |

## 🚀 **Quick Start**

1. **Setup**: Install dependencies, configure `.env`
2. **Run**: `python main.py --transport stdio` or `--transport streamable-http`
3. **Test**: Use the testing guides above
4. **Use**: Integrate with MCP clients or HTTP apps

## 🎯 **What This Server Does**

- **Secrets Management**: Create, read, update, delete secrets
- **Key Management**: DFC encryption keys (AES, RSA)
- **Authentication**: Access control and policies
- **Security**: Guidelines and best practices
- **MCP Protocol**: Model Context Protocol compliance

## 🔧 **Need Help?**

- Check the specific doc for your question
- Run tests to verify functionality
- Check server logs for errors
- Ensure credentials are configured
