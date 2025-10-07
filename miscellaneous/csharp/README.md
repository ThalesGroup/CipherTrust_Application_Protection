# Integration/Sample Code for C#/.NET Core

## Overview
PassPhraseSecureUtility.cs sample shows how to use PassPhraseEncryption method provided in CADP.NetCore.Utility namespace. This utility can be used to obfuscate the login credentials as well as client certificate passphrase.

TestCryptoDataUtility.cs sample shows how to use CryptoDataUtility.dll for user to perform crypto operations without specifying the key name. To accomplish this, the ciphertext, at the time of encryption, is bundled with the same meta data, of the key, which was used for encryption.

AddTransactionIdSample.cs sample shows how to set and unset Transaction ID in the log entries using TransactionID property of LoggerWrapper class.

CryptoHeaderModuleSample.cs sample shows how to use CryptoHeaderModule.dll for user to perform encryption, decryption, HMAC generation, and HMAC verification. Encrypting data comes in two flavors: with headers and without headers.

## Prerequisites: 
In order to run C# samples, 
1. .NET 6.0 or higher must be installed.
1. CipherTrust.CADP.NETCore NuGet package must be installed.

## Usage: 
1. Create a console application. Let's say `SampleApp`.
1. From the available sample cs files, add anyone to the project.
1. Add the CipherTrust.CADP.NETCore NuGet package to the project. To know more about NuGet package and how to add it, refer to [CipherTrust.CADP.NETCore](https://www.nuget.org/packages/CipherTrust.CADP.NETCore/)
1. [**For TestCryptoDataUtility sample only**] Add CryptoDataUtility.dll as reference in project. On installing CADP for .NetCore Nuget package, this dll would be available at "%UserProfile%\\.nuget\packages\ciphertrust.cadp.netcore\\<package-version\>\utility\" folder.
1. [**For CryptoHeaderModule sample only**] Add CryptoHeaderModule.dll as reference in project. On installing CADP for .NetCore Nuget package, this dll would be available at "%UserProfile%\\.nuget\packages\ciphertrust.cadp.netcore\\<package-version\>\utility\" folder.
1. Build using command `dotnet build -c Release`.
1. Use either of the following commands to run-
    * `dotnet run` command to run the project at a terminal prompt.
    * `dotnet` command to run `SampleApp.dll` at location `\bin\release\net6.0` using terminal. Example: `dotnet SampleApp.dll`
    * [**Windows Only**] `SampleApp.exe` at location `\bin\release\net6.0` using terminal. Example: `SampleApp.exe`
    * Provide the command line parameter as required for both the samples.

## More Information
For more information on CADP for .NET Core, refer to the [CADP for .NET Core user guide](https://thalesdocs.com/ctp/con/cadp/cadp-netcore/alpha-8.14.0/index.html).
