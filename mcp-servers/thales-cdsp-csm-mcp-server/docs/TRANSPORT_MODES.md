# Transport Modes

How to run the Thales CSM MCP Server in different modes.

## 🚀 **Available Modes**

### **stdio (Default)**
**Command**: 
```bash
python main.py
# or
python main.py --transport stdio
```

### **HTTP**
**Command**:
```bash
python main.py --transport streamable-http --host 0.0.0.0 --port 8000
```

## ⚙️ **Options**

| Option | Description | Default |
|--------|-------------|---------|
| `--transport` | `stdio` or `streamable-http` | `stdio` |
| `--host` | Host address | `0.0.0.0` |
| `--port` | Port number | `8000` |

## 📋 **What Each Mode Does**

- **stdio**: Direct communication, no network
- **HTTP**: Network accessible, REST endpoints