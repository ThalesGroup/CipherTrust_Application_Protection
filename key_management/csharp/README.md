# Integration/Sample Code for C#/.NET Core

## Overview
The following samples shows how to manage keys.

* NaeKeyManagement.cs
  * This sample shows how to *get the attributes of the key*.
* ExportWrappedKey.cs
  * This sample shows how to *export an AES key wrapped using an RSA key*.

## Prerequisites: 
In order to run C# samples, 
1. .NET Core 3.1 or higher must be installed.
1. CADP.NetCore.nupkg must be installed.

## Usage: 
1. Before using these cs files, create the console application. Let's say `SampleApp`
1. Add the required cs files to the project.
1. Add the CADP.NetCore NuGet package to the project and build. using command `dotnet build -c Release`
1. Use either of the following commands to execute the project.
    * `dotnet run` command to run the project at a terminal prompt.
    * `dotnet` command to run `SampleApp.dll` at location `\bin\Release\netcoreapp3.1` using terminal. Example: `dotnet SampleApp.dll`
    * [Windows Only] `SampleApp.exe` to run the code at a terminal prompt. Example: `SampleApp.exe` 

## More Information
For more information on CADP for .NET Core, refer to the CADP for .NET Core user guide at [ThalesDocs.com](www.thalesdocs.com/ctp/con/cadp/dotnetcore/index.html).
