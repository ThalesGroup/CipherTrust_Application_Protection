
# PKCS11 Integrations/Sample Code

## Overview
CADP_PKCS11_Samples.exe or CADP_PKCS11_Samples.dll is a command-line interface tool to understand the PKCS11 interface.

## Prerequisites: 
In order to run CADP_PKCS11_Samples :
> - .NET 6.0 or higher must be installed.<br>
> - CADP for C must be installed.


## Compilation:
Refer Pkcs11Interop.dll in your application present at below path (default location), after installing CADP for C.
#### For Windows: 
     C:\Program Files\CipherTrust\CADP_for_C\wrapper\.NETCore
#### For Linux : 
     /opt/CipherTrust/CADP_for_C/wrapper/dotNETCore
You can build the sample either from Visual Studio or dotnet cli through the command `dotnet build -c Release`
 

## Usage: 
### Run sample from executable(only on windows):
CADP_PKCS11_Samples.exe -p pin -t [0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | a | b | c | d] [-k|-kp <keyname>] [-o encryption mode] [-TagLen length of Tag in AES/GCM] [-f input File]
[-c char set]|[-r charset file with range input]|[-l charset file with literal input] [-u utf mode] [-h headermode] [-w tweak] [-W wrappingkeyname] [-n false|true] [-m true|false] [-I Non-unique searchable ID CKA_ID]
[-CurveOid curve Oid, for ECC keys only] [-Aa Asymmetric algorithm name - RSA/EC, useful with '-t a' sample option when -Kp is used)

#### Example
     CADP_PKCS11_Samples.exe -p username:password -k testkey1 -t 1



### Run sample from dotnet cli:
dotnet CADP_PKCS11_Samples.dll -p pin -t [0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | a | b | c | d] [-k|-kp <keyname>] [-o encryption mode] [-TagLen length of Tag in AES/GCM] [-f input File]
[-c char set]|[-r charset file with range input]|[-l charset file with literal input] [-u utf mode] [-h headermode] [-w tweak] [-W wrappingkeyname] [-n false|true] [-m true|false] [-I Non-unique searchable ID CKA_ID]
[-CurveOid curve Oid, for ECC keys only] [-Aa Asymmetric algorithm name - RSA/EC, useful with '-t a' sample option when -Kp is used)

#### Example
     dotnet CADP_PKCS11_Samples.dll -p username:password -k testkey1 -t 1

## Option for various command
### Choices for the -t option:
    0. Run all samples.
    1. Create key sample.                                                               		
    2. Create key object sample.
    3. Find and delete the key sample.
    4. Encrypt and decrypt sample.
    5. Encrypt and decrypt with different mode (FPE) sample.
    6. Create a key pair and sign the message sample.
    7. Find and export a key from key manager sample.
    8. Encrypt and decrypt a file sample.
    9. Encrypt and decrypt a file and log meta data sample.
    a. Test key attributes sample.                            
    b. Compute message digest for the default test string.
    c. Compute message digest for a given input file.
    d. Encrypt and decrypt with GCM mode sample.
    e. Create a ECC key pair and sign the message sample.
### Choices for the -o option:
     ECB ... ECB mode
     CBC ... CBC mode
     GCM ... GCM mode
     CBC_PAD ... CBC_PAD mode
     sha256  ... SHA256 mode
     sha384  ... SHA384 mode
     sha512  ... SHA512 mode
     sha256-HMAC  ... SHA256-HMAC mode
     sha384-HMAC  ... SHA384-HMAC mode
     sha512-HMAC  ... SHA512-HMAC mode
     SHA1-ECDSA   ... SHA1-ECDSA mode
     SHA256-ECDSA  ... SHA256-ECDSA mode
     SHA384-ECDSA  ... SHA384-ECDSA mode
     SHA512-ECDSA  ... SHA512-ECDSA mode
### Choices for the -O option:
    true    ... Opaque object
    false   ... Non Opaque object
### Choices for the -TagLen option:
     4 - 16 ... bytes taglength for GCM
### Choices for the -g option:
     0 ... generate a versioned key
     1 ... rotate a versioned key
     2 ... migrate a non-versioned key to a versioned key (Not Supported)
     3 ... generate a non-versioned key
### Choices for the -m (metadata) option:
     false ... don't add metadata
     true  ... add metadata
### Choices for the -n option:
     false ... no-delete is not active, hence delete the key as usual
     true ... no-delete enabled, thus deletion of the key is blocked.
### Choices for the -H option:
     v1.5 ... use version 1.5 header
     v1.5base64 ... use version 1.5 header, then encode everything in the BASE64 code
     v2.1 ... use version 2.1 header
     v2.7 ... use version 2.7 header
### Choices for the -CurveOid option:
     secp224k1-225-06052b81040020, secp224r1-224-06052b81040021, secp256k1-256-06052b8104000a
     secp384r1-384-06052b81040022, secp521r1-521-06052b81040023, prime256v1-256-06082a8648ce3d030107
     brainpoolP224r1-224-06092b2403030208010105, brainpoolP224t1-224-06092b2403030208010106
     brainpoolP256r1-256-06092b2403030208010107, brainpoolP256t1-256-06092b2403030208010108
     brainpoolP384r1-384-06092b240303020801010b, brainpoolP384t1-384-06092b240303020801010c
     brainpoolP512r1-512-06092b240303020801010d, brainpoolP512t1-512-06092b240303020801010e
### Choices for the -Aa option:");
     RSA ... RSA Keypair
     EC  ... ECC keypair     
     

The program CADP_PKCS11_Samples consists of the main program whose source code can be found in Program.cs and ten other source code files, 
each of which contains a sample class for a particular functionality, e.g. encryption or signing. 
Two other source files, Settings.cs and Sample_Helpers.cs, contain global settings, Native PKCS11 library path and helper functions, respectively.
## Native PKCS11 library path(Default path)
### For Windows:
    C:\Program Files\CipherTrust\CADP_for_C\libcadp_pkcs11.dll
### For Linux:
    /opt/CipherTrust/CADP_for_C/libcadp_pkcs11.so
    
User can modify the native PKCS11 library path according to their platform. 

## How to enable pkcs11 interop level log    
Uncomment the following lines from Settings.cs to generate the PKCS11 interop level log
```
SimplePkcs11InteropLoggerFactory simpleLoggerFactory = new SimplePkcs11InteropLoggerFactory();
simpleLoggerFactory.EnableFileOutput("log.txt");
simpleLoggerFactory.MinLogLevel = Pkcs11InteropLogLevel.Error;
Pkcs11InteropLoggerFactory.SetLoggerFactory(simpleLoggerFactory);
```
 
