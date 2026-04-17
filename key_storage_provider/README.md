# CADP for C Integrations/Sample Code

This readme file contains the following information:

- Overview
- Prerequisites
- How to Compile the Source Code
- How to Run the Code Samples
- KSP Provider Library Path (Default Path)
- Sample Code Descriptions

## Overview

CipherTrust Application Data Protection (CADP) for C enables you to integrate your applications with the cryptographic and key-management capabilities of the CipherTrust Manager using Microsoft's CNG framework.

The CADP for C provider supports the Key Storage Provider (KSP) interface, allowing applications to use CipherTrust Manager for secure key storage and cryptographic operations through standard Windows cryptographic APIs. The provider seamlessly integrates with enterprise applications including SQL Server Management Studio (SSMS) for database administration and Always Encrypted operations.

Key features include:
- **Windows CNG Integration**: Native integration with Microsoft's Cryptography API: Next Generation
- **SQL Server Always Encrypted Support**: Column Master Key (CMK) and Column Encryption Key (CEK) management
- **Multiple Key Types**: Support for AES, RSA, and Elliptic Curve (EC) keys
- **Key Lifecycle Management**: Key creation, rotation, and secure storage
- **Cross-Platform Compatibility**: Works with various Windows applications and databases

The following samples provide CADP for C Integration code to demonstrate key storage operations, database encryption, and seamless integration with enterprise applications like SSMS and ADCS:

### C# Samples:
- **Create_CMK_CEK.cs**: Creates Column Master Keys and Column Encryption Keys for SQL Server Always Encrypted
- **CMK_CEK_Rotation.cs**: Demonstrates key rotation for Always Encrypted scenarios
- **SQLInsert.cs**: Shows how to perform database operations with encrypted columns

### C++ Samples:
- **CreateKey**: Creates cryptographic keys (AES, RSA, EC) using CNG APIs
- **CreateSelfSignedCert**: Generates self-signed certificates
- **SignVerify**: Demonstrates digital signature creation and verification
- **SymmetricKeyEncryption**: Encrypts and decrypts data using symmetric keys

## Prerequisites

Before running the CADP for C Integration code samples, ensure the following:

1. **CADP for C Integration Installation**: Install the CADP for C Integration CADP_Integration_Setup.exe program
2. **Windows Platform**: KSP provider is Windows-specific
3. **Visual Studio**: Required for C++ sample compilation
4. **KSP Provider Registration**: The Thales KSP provider must be registered in Windows
5. **Configuration File**: CADP_Integration.properties file must be properly configured
6. **CipherTrust Manager**: Access to a configured CipherTrust Manager instance

### C# Prerequisites:
- **.NET Framework**: Compatible .NET Framework version
- **SQL Server** (for Always Encrypted samples): SQL Server with Always Encrypted support
- **System.Security.Cryptography**: Access to CNG classes

### C++ Prerequisites:
- **Visual Studio 2022 or later**: For compilation of C++ projects
- **Windows SDK**: For CNG header files and libraries
- **NCrypt Library**: Windows CNG library (ncrypt.lib)

## Downloading CADP for C CNG Source Code Files

Prior to compiling the CADP for C KSP sample source code, ensure you have the following files:

> - Project files (.vcxproj for C++)
> - Source files (.cpp, .cs)
> - Header files (.h)

## How to Compile the Source Code

This section provides instructions on how to compile the source code for CADP for C CNG samples.

### C++ Samples

#### Windows (Visual Studio)

To compile the C++ samples in Windows:

1. Navigate to the 'Sample/C++' directory
2. Open the specific sample directory (CreateKey, CreateSelfSignedCert, SignVerify, or SymmetricKeyEncryption)
3. Using Visual Studio, open the respective .vcxproj file
4. Ensure the Thales KSP provider is properly registered and configured
5. Build the project

**Build Output**: Executable files will be created in the Debug or Release directory based on your build configuration.

## Configuration Note

**Before compiling:** Verify that the Additional Library Directories path in your project settings (Project Properties → Configuration Properties → Linker → General) matches your installed Windows SDK version:

**Current setting:** `C:\Program Files (x86)\Windows Kits\10\Lib\10.0.26100.0\um\x64`

If compilation fails with library errors, update this path to match your actual Windows SDK installation in `C:\Program Files (x86)\Windows Kits\10\Lib\`.

**Common alternative paths (depending on your Windows SDK version):**
- `C:\Program Files (x86)\Windows Kits\10\Lib\10.0.22621.0\um\x64` (Windows 11 SDK)
- `C:\Program Files (x86)\Windows Kits\10\Lib\10.0.19041.0\um\x64` (Windows 10 SDK v2004)
- `C:\Program Files (x86)\Windows Kits\10\Lib\10.0.18362.0\um\x64` (Windows 10 SDK v1903)

### C# Samples

#### Compilation

To compile the C# samples:

1. Open the C# source files in Visual Studio or your preferred C# IDE
2. Ensure references to System.Security.Cryptography are included
3. Build the project using the IDE or command line:

```
csc Create_CMK_CEK.cs
csc CMK_CEK_Rotation.cs
csc SQLInsert.cs
```

## How to Run the Code Samples

### C++ Samples

#### Viewing Sample Usage Information

Before running the C++ samples, you can execute them without parameters to see usage information:

```
CreateKey.exe
SymmetricKeyEncryption.exe
```

#### Running C++ Code Samples

1. **CreateKey Sample**:
   ```
   CreateKey.exe
   ```
   - Follow the interactive prompts to select key type (AES/RSA/EC)
   - Enter key name and size when prompted
   - Key will be created on the CipherTrust Manager

2. **SymmetricKeyEncryption Sample**:
   ```
   SymmetricKeyEncryption.exe
   ```
   - Enter the key name when prompted
   - Sample will create key if it doesn't exist
   - Demonstrates encryption/decryption with fixed test data

3. **SignVerify Sample**:
   ```
   SignVerify.exe
   ```
   - Creates asymmetric key pair for signing operations
   - Demonstrates digital signature creation and verification

4. **CreateSelfSignedCert Sample**:
   ```
   CreateSelfSignedCert.exe
   ```
   - Generates a self-signed certificate using the CNG provider


### C# Samples

#### Running C# Code Samples

1. **Create_CMK_CEK Sample**:
   ```
   Create_CMK_CEK.exe
   ```
   - Enter CMK (Column Master Key) name when prompted
   - Choose option for CEK creation (manual bytes or managed key)
   - Creates keys suitable for SQL Server Always Encrypted

2. **CMK_CEK_Rotation Sample**:
   ```
   CMK_CEK_Rotation.exe
   ```
   - Demonstrates key rotation for Always Encrypted scenarios
   - Requires existing CMK and CEK setup
   - Updates SQL Server metadata for new key associations

3. **SQLInsert Sample**:
   ```
   SQLInsert.exe
   ```
   - Demonstrates database operations with encrypted columns
   - Requires properly configured Always Encrypted environment

## KSP Provider Library Path (Default Path)

The CADP for C KSP provider libraries are located at:

**Key Storage Provider (KSP)**:
- `C:\Windows\System32\libcadp_ksp.dll`
- `C:\Windows\System32\libcadp_capi.dll`


## Configuration

### Provider Registration

Ensure the KSP provider is registered in Windows registry. The provider name used in samples:
```
"CADP Key Storage Provider"

```

### Configuration File

Configure the CADP_Integration.properties file with your CipherTrust Manager connection details:
```
NAE_IP=<CipherTrust_Manager_IP>
NAE_Port=9000

```

## Supported Key Types and Sizes

### AES Keys
- 128-bit, 192-bit, 256-bit

### RSA Keys  
- 2048-bit, 3072-bit, 4096-bit

### Elliptic Curve Keys
- P-256 (secp256r1)
- P-384 (secp384r1)  
- P-521 (secp521r1)

## Troubleshooting

### Common Issues

1. **Provider not found**: Ensure KSP provider is properly registered
2. **Connection errors**: Verify CADP_Integration.properties configuration
3. **Key creation failures**: Check CipherTrust Manager permissions
4. **Certificate errors**: Ensure proper SSL/TLS configuration

### Error Messages

- **NCryptOpenStorageProvider fail**: Check provider registration and configuration file
- **NCryptCreatePersistedKey failure**: Verify key name uniqueness and permissions
- **SQL Connection errors**: Check connection string and Always Encrypted settings

## Notes

- The KSP provider supports both synchronous and asynchronous operations
- Always Encrypted samples require proper SQL Server setup and configuration

For detailed information about CNG APIs and Always Encrypted, refer to Microsoft documentation and the CipherTrust Manager user guides.