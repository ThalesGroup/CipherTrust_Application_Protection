# Integration/Sample Code for C#/.NET Core

## Overview
PassPhraseSecureUtility.cs sample shows how to use PassPhraseEncryption method provided in CADP.NetCore.Utility namespace. This utility can be used to obfuscate the login credentials as well as client certificate passphrase.

TestCryptoDataUtility.cs sample shows how to use CryptoDataUtility.dll for user to decrypt a string without specifying the keyName. To accomplish this, the ciphertext, at the time of encryption, is bundled with the same meta data, of the key, which was used for encryption.


## Prerequisites: 
In order to run C# samples, 
1. .NET 6.0 or higher must be installed.
1. CipherTrust.CADP.NETCore NuGet package must be installed.

## Usage: 
1. Create a console application. Let's say `SampleApp`.
1. From the available sample cs files, add anyone to the project.
1. Add the CipherTrust.CADP.NETCore NuGet package to the project and build using command `dotnet build -c Release`. To know more about NuGet package and how to add it, refer to [CipherTrust.CADP.NETCore](https://www.nuget.org/packages/CipherTrust.CADP.NETCore/).
1. Step only for TestCryptoDataUtility.cs: On installing CADP for .NetCore nuget package, the CryptoDataUtility.dll gets placed in the "C:\Users\%UserName%\.nuget\packages\ciphertrust.cadp.netcore\<latest-version>\utility\" folder. The user must explicitly add reference of CryptoDataUtility.dll to the application. 
1. Use either of the following commands to execute the project-
    * `dotnet run` command to run the project at a terminal prompt.
    * `dotnet` command to run `SampleApp.dll` at location `\bin\release\net6.0` using terminal. Example: `dotnet SampleApp.dll`
    * [Windows Only] `SampleApp.exe` at location `\bin\release\net6.0` using terminal. Example: `SampleApp.exe`
	* Provide the command line parameter as required for both the samples.


## More Information
For more information on CADP for .NET Core, refer to the [CADP for .NET Core user guide](https://thalesdocs.com/ctp/con/cadp/cadp-netcore/latest/index.html).
