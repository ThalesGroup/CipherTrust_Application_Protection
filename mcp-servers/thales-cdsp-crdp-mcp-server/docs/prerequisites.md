# Prerequisites

This document outlines the requirements for installing and running the CRDP MCP Server.

## System Requirements

- **Operating System**: Windows, macOS, or Linux
- **Memory**: 2GB RAM minimum
- **Disk Space**: 500MB for installation

## Required Software

### Node.js and npm

**Version**: 18.x or higher

**Installation**:
- **Windows**: Download from [nodejs.org](https://nodejs.org/)
- **macOS**: `brew install node` or download from [nodejs.org](https://nodejs.org/)
- **Linux**: `apt install nodejs npm` or equivalent

**Verification**:
```bash
node --version
npm --version
```

### TypeScript

**Installation**:
```bash
npm install -g typescript
```

**Verification**:
```bash
tsc --version
```

### Git (for cloning the repository)

**Installation**:
- **Windows**: Download from [git-scm.com](https://git-scm.com/)
- **macOS**: `brew install git` or included with Xcode
- **Linux**: `apt install git` or equivalent

## CRDP Service Requirements

The CRDP MCP Server requires access to:

- **CipherTrust RestFul Data Protection (CRDP) Service**
- **CipherTrust Manager** with CRDP application deployed
- **Protection Policies** configured in CRDP

### CRDP Configuration

1. **Verify CRDP service** is running and accessible:
   ```bash
   curl -X GET http://your-crdp-server:8090/healthz
   ```

2. **Configuration Variables**:
   - `CRDP_SERVICE_URL`: URL for data operations (default: `http://localhost:8090`)
   - `CRDP_PROBES_URL`: URL for monitoring (default: `http://localhost:8080`)

### Setting Environment Variables

**Windows PowerShell:**
```powershell
$env:CRDP_SERVICE_URL="http://crdp-server:8090"
```

**Windows CMD:**
```cmd
set CRDP_SERVICE_URL=http://crdp-server:8090
```

**Linux/macOS:**
```bash
export CRDP_SERVICE_URL="http://crdp-server:8090"
```

## Optional Tools

### npx (for running MCP Inspector)

**Installation**: Included with recent npm versions
```bash
npm install -g npx
```

### Verification Checklist

Before proceeding:

- [ ] Node.js v18+ installed
- [ ] npm installed and working
- [ ] TypeScript installed globally
- [ ] CRDP service accessible
- [ ] Protection policies configured in CRDP

## Troubleshooting

- **Node.js not found**: Ensure Node.js is in your PATH
- **TypeScript compilation fails**: Install TypeScript globally
- **Cannot connect to CRDP**: Check service status and firewall settings
- **tsc not found**: Ensure global npm modules are in your PATH 