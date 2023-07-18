# Integration/Sample Code for C#/.NET Core

## Overview
The following samples shows how to manage keys.

* NaeKeyManagement.cs
  * This sample shows how to *get the attributes of the key*.
* ExportWrappedKey.cs
  * This sample shows how to *export an AES key wrapped using an RSA key*.

## Prerequisites: 
In order to run C# samples, 
1. .NET 6.0 or higher must be installed.
1. CipherTrust.CADP.NETCore NuGet package must be installed.

## Usage: 
1. Create a console application. Let's say `SampleApp`.
1. From the available sample cs files, add anyone to the project.
1. Add the CipherTrust.CADP.NETCore NuGet package to the project and build using command `dotnet build -c Release`. To know more about NuGet package and how to add it, refer to [CipherTrust.CADP.NETCore](https://www.nuget.org/packages/CipherTrust.CADP.NETCore/).
1. Use either of the following commands to execute the project.
    * `dotnet run` command to run the project at a terminal prompt.
    * `dotnet` command to run `SampleApp.dll` at location `\bin\release\net6.0` using terminal. Example: `dotnet SampleApp.dll`
    * [Windows Only] `SampleApp.exe` at location `\bin\release\net6.0` using terminal. Example: `SampleApp.exe`

## More Information
For more information on CADP for .NET Core, refer to the [CADP for .NET Core user guide](https://thalesdocs.com/ctp/con/cadp/cadp-netcore/latest/index.html).
