# Thales CSM MCP Server

[![Trust Score](https://archestra.ai/mcp-catalog/api/badge/quality/sanyambassi/thales-cdsp-csm-mcp-server)](https://archestra.ai/mcp-catalog/sanyambassi__thales-cdsp-csm-mcp-server)

Simple MCP server for Thales CipherTrust Secrets Management, powered by Akeyless.

## 🎬 **Demo Videos**

> **📹 Part I: Usage & Functionality** - [Watch on YouTube](https://youtu.be/zgpvsL_GY64)
> 
> *This video demonstrates:*
> - Setting up Cursor AI integration
> - Creating and managing secrets and DFC Keys through AI chat
> - Security compliance workflows
> - Example prompts and functionality

> **📹 Part II: Deployment & Installation** - [Watch on YouTube](https://youtu.be/XLTQ31hGzeU)
> 
> *This video covers:*
> - Step-by-step installation process
> - Configuration and setup
> - Deployment options

## 📋 **Prerequisites**

Before you begin, ensure you have the following installed on your system:

- **Python 3.8+**: Required for running the MCP server
- **uv**: Modern Python package manager (recommended) or pip
- **git**: For cloning the repository
- **dotenv**: Environment variable management
- **fastmcp**: MCP server framework
- **Thales CipherTrust Manager access**
- **Valid Akeyless credentials**

### **Installing Prerequisites**

#### **Python**
```bash
# Check if Python is installed
python --version
# or
python3 --version

# Install Python (Ubuntu/Debian)
sudo apt update && sudo apt install python3 python3-pip

# Install Python (macOS)
brew install python

# Install Python (Windows)
# Download from https://python.org
```

#### **uv (Recommended)**
```bash
# Install uv
pip install uv

# Verify installation
uv --version
```

#### **git**
```bash
# Check if git is installed
git --version

# Install git (Ubuntu/Debian)
sudo apt update && sudo apt install git

# Install git (macOS)
brew install git

# Install git (Windows)
# Download from https://git-scm.com
```

#### **dotenv**
```bash
# Check if python-dotenv is installed
python -c "import dotenv; print('dotenv available')"

# Install python-dotenv
pip install python-dotenv

# Verify installation
python -c "import dotenv; print(f'dotenv version: {dotenv.__version__}')"
```

#### **fastmcp**
```bash
# Check if fastmcp is installed
python -c "import fastmcp; print('fastmcp available')"

# Install fastmcp
pip install fastmcp

# Verify installation
python -c "import fastmcp; print(f'fastmcp version: {fastmcp.__version__}')"
```

## 🚀 **What It Does**

- **Secrets Management**: Create, read, update, delete secrets
- **DFC Key Management**: DFC encryption keys (AES, RSA)
- **Account Management**: Get Akeyless account details
- **Analytics**: Fetch analytics data
- **Authentication Methods**: Manage Authentication Methods
- **Roles**: Manage Roles
- **Targets**: Manage Targets
- **Security**: Guidelines and best practices
- **MCP Protocol**: Model Context Protocol compliance

## ⚡ **Quick Start**

### **1. Install**

#### **Option A: Using pip (Traditional)**
```bash
git clone https://github.com/sanyambassi/thales-cdsp-csm-mcp-server
cd thales-cdsp-csm-mcp-server
pip install -r requirements.txt
```

#### **Option B: Using uv (Recommended)**
```bash
# Install uv if you don't have it
pip install uv

# Clone and setup
git clone https://github.com/sanyambassi/thales-cdsp-csm-mcp-server
cd thales-cdsp-csm-mcp-server

# Install dependencies (creates .venv automatically)
uv sync
```

### **2. Configure**
Create `.env` file:
```env
AKEYLESS_ACCESS_ID=your_access_id
AKEYLESS_ACCESS_KEY=your_access_key
AKEYLESS_API_URL=https://your-ciphertrust-manager/akeyless-api/v2
LOG_LEVEL=INFO
```

### **3. Run**

#### **Using pip (Traditional)**
```bash
# stdio mode
python main.py

# HTTP mode 
python main.py --transport streamable-http --host localhost --port 8000
```

#### **Using uv (Recommended)**
```bash
# stdio mode
uv run python main.py

# HTTP mode 
uv run python main.py --transport streamable-http --host localhost --port 8000
```

## 🛠️ **Available Tools**

| Tool | Description |
|------|-------------|
| `manage_secrets` | Create, read, update, delete secrets |
| `manage_dfc_keys` | Manage encryption keys |
| `manage_auth_methods` | Authentication and access control |
| `manage_rotation` | Secret rotation policies |
| `manage_customer_fragments` | Enhanced security features |
| `security_guidelines` | Security best practices |
| `manage_roles` | List and get role information |
| `manage_targets` | List and get target information |
| `manage_analytics` | Get analytics and monitoring data |
| `manage_account` | Get account settings and licensing |
| `get_api_reference` | Get API reference for native Akeyless integrations (generic workflows + S3 example) |

## 🔍 **Test It**

```bash
# Run tests
python tests/run_tests.py
python.exe tests\test_mcp_protocol.py

# Test health endpoint (HTTP mode)
curl http://localhost:8000/health
```

## 📚 **Documentation**

- **[TRANSPORT_MODES.md](docs/TRANSPORT_MODES.md)** - How to run
- **[TOOLS.md](docs/TOOLS.md)** - What tools do
- **[TESTING.md](docs/TESTING.md)** - Complete testing guide
- **[AI Assistant Configs](config)** - MCP json examples for AI Assistants

## 🎯 **Use Cases**

- **AI Assistants**: Claude Desktop, Cursor AI
- **Web Applications**: REST API integration
- **Automation**: CI/CD, scripts, tools
- **Enterprise**: Secrets management, compliance

## 🤖 **AI Assistant Integration**

### **Claude Desktop**
```json
{
  "mcpServers": {
    "thales-csm": {
      "command": "python",
      "args": ["main.py", "--transport", "stdio"],
      "env": {
        "AKEYLESS_ACCESS_ID": "your_access_id_here",
        "AKEYLESS_ACCESS_KEY": "your_access_key_here",
        "AKEYLESS_API_URL": "https://your-ciphertrust-manager/akeyless-api/v2",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### **Cursor AI**
```json
{
  "mcpServers": {
    "thales-csm": {
      "command": "python",
      "args": ["main.py", "--transport", "stdio"],
      "env": {
        "AKEYLESS_ACCESS_ID": "your_access_id_here",
        "AKEYLESS_ACCESS_KEY": "your_access_key_here",
        "AKEYLESS_API_URL": "https://your-ciphertrust-manager/akeyless-api/v2",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### **Configuration Parameters**
- **`env`**: Environment variables for Akeyless authentication and logging
- **`command`**: Python executable to run the server
- **`args`**: Command line arguments for the server

### **⚠️ Important Notes**
- **Full Path Required**: `args` must include the full absolute path to `main.py`
- **Windows Paths**: Use double backslashes `\\` in Windows paths (e.g., `C:\\thales-cdsp-csm-mcp-server\\main.py`)
- **Unix Paths**: Use forward slashes `/` in Unix/Linux paths (e.g., `/home/user/thales-cdsp-csm-mcp-server/main.py`)

### **Configuration Templates**
- **[config/mcp-config-uv.json](config/mcp-config-uv.json)** - UV package manager setup
- **[config/mcp-config.json](config/mcp-config.json)** - Basic configuration template

## 🤝 **Support**

- **Issues**: [GitHub Issues](https://github.com/sanyambassi/thales-cdsp-csm-mcp-server/issues)
- **Documentation**: Check the docs folder above

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

