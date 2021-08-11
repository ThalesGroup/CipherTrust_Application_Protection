
# PKCS11 Integrations/Sample Code

## Overview:
VPkcs11_Sample.exe or VPkcs11_Sample.dll is a command-line interface tool to understand the PKCS11 interface.

## Prerequisites: 
In order to run VPkcs11_Sample :
> - .NET Core 3.1 or higher must be installed.<br>
> - CADP.NetCore NuGet package must be installed.
> - Vormetric Key Agent must be install and registered with a Data Security Manager (DSM).

## Note: 
Vormetric Key Agent can be found in CADP .NetCore NuGet installed directory.

## Compilation:
You can build the sample either from Visual Studio or dotnet cli through the command `dotnet build -c Release`
 

## Usage: 
### Run sample from executable(only on windows):
`VPkcs11_Sample.exe -p pin -t [0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | a | b | c] [-k|-kp keyname] [-o encryption mode] [-f input File]
[-c char set]|[-r charset file with range input]|[-l charset file with literal input] [-u utf mode] [-h headermode] [-w tweak] [-W wrappingkeyname] [-n 0|1] [-m true|false])`

#### Example
VPkcs11_Sample.exe -p pin1234# -k testkey1 -t 1



### Run sample from dotnet cli:
`dotnet VPkcs11_Sample.dll -p pin -t [0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | a | b | c] [-k|-kp keyname] [-o encryption mode] [-f input File]
[-c char set]|[-r charset file with range input]|[-l charset file with literal input] [-u utf mode] [-h headermode] [-w tweak] [-W wrappingkeyname] [-n 0|1] [-m true|false])`

#### Example
dotnet VPkcs11_Sample.dll -p pin1234# -k testkey1 -t 1

## Option for various command
### Choices for the -t option:
    0. Run all samples.
    1. Create key sample.                                                               		
    2. Create key object sample.
    3. Find and delete the key sample.
    4. Encrypt and decrypt sample.
    5. Encrypt and decrypt with different mode (FPE) sample.
    6. Create a key pair and sign the message sample.
    7. Find and export a key from DSM sample.
    8. Encrypt and decrypt a file sample.
    9. Encrypt and decrypt a file and log meta data sample.
    a. Test key attributes sample.                            
    b. Compute message digest for the default test string.
    c. Compute message digest for a given input file.
### Choices for the -o option:
     ECB ... ECB mode
     CBC ... CBC mode
     CBC_PAD ... CBC_PAD mode
     sha256  ... SHA256 mode
     sha384  ... SHA384 mode
     sha512  ... SHA512 mode
     sha256-HMAC  ... SHA256-HMAC mode
     sha384-HMAC  ... SHA384-HMAC mode
     sha512-HMAC  ... SHA512-HMAC mode
### Choices for the -g option:
     0 ... generate a versioned key
     1 ... rotate a versioned key
     2 ... migrate a non-versioned key to a versioned key
     3 ... generate a non-versioned key
### Choices for the -m (metadata) option:
     false ... don't add metadata
     true  ... add metadata
### Choices for the -n option:
     0 ... no-delete is not active, hence delete the key as usual
     1 ... no-delete enabled, thus deletion of the key is blocked.
### Choices for the -h option:
     v1.5 ... use version 1.5 header
     v1.5base64 ... use version 1.5 header, then encode everything in the BASE64 code
     v2.1 ... use version 2.1 header
     v2.7 ... use version 2.7 header
     

The program VPkcs11_Sample consists of the main program whose source code can be found in Program.cs and ten other source code files.
each of which contains a sample class for a particular functionality, e.g. encryption or signing. 
Two other source files, Settings.cs and Sample_Helpers.cs, contain global settings and helper functions, respectively.
