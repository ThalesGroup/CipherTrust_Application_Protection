# Integration/Sample Code for C#/.NET Core

## Overview
PassPhraseSecureUtility.cs sample shows how to use PassPhraseEncryption method provided in CADP.NetCore.Utility namespace. This utility can be used to obfuscate the login credentials as well as client certificate passphrase.


## Prerequisites: 
In order to run C# samples, 
1. .NET Core 3.1 or higher must be installed.
1. CipherTrust.CADP.NETCore NuGet package must be installed.

## Usage: 
1. Before using these cs files, create the console application. Let's say `SampleApp`
1. Add the required cs files to the project.
1. Add the CipherTrust.CADP.NETCore NuGet package to the project and build. using command `dotnet build -c Release`. To know more about NuGet package, refer to [CipherTrust.CADP.NETCore](https://www.nuget.org/packages/CipherTrust.CADP.NETCore/).
1. Use either of the following commands to execute the project.
    * `dotnet run` command to run the project at a terminal prompt.
    * `dotnet` command to run `SampleApp.dll` at location `\bin\Release\netcoreapp3.1` using terminal. Example: `dotnet SampleApp.dll`
    * [Windows Only] `SampleApp.exe` to run the code at a terminal prompt. Example: `SampleApp.exe`  

## More Information
For more information on CADP for .NET Core, refer to the [CADP for .NET Core user guide](https://thalesdocs.com/ctp/con/cadp/cadp-netcore/latest/index.html).
