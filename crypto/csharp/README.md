# Integration/Sample Code for C#/.NET Core

## Overview
The following samples show how to perform crypto operations with various ciphers, sign and verify data and much more.

* CryptoOpRijndael.cs
  * This sample shows how to perform *crypto operations* (Encrypt and Decrypt) using **AES** mode. 
* CryptoOpAesGcm.cs
  * This sample shows how to perform *crypto operations* (Encrypt and Decrypt) using **AES-GCM** mode.
* CryptoOpMacVerify.cs
  * This sample shows how to *generate and verify* a **MAC** .
* CryptoOpRSAEncDec.cs
  * This sample shows how to perform *crypto operations* (Encrypt and Decrypt) using a **RSA** key.
* CryptoOpRsaSignVerify.cs
  * This sample shows how to CMS *sign data and verify signed data* using **RSA** key.
* CryptoMultiThreadedHmac.cs
  * This sample shows how to use multiple threads that share the same session and perform mac operations.*
* CryptoOpFpe.cs
  * This sample shows how to perform *crypto operations* (Encrypt and Decrypt) using **FPE**.

## Prerequisites: 
In order to run C# samples, 
1. .NET Core 3.1 or higher must be installed.
1. CipherTrust.CADP.NETCore NuGet package must be installed.

## Usage: 
1. Before using these cs files, create the console application. Let's say `SampleApp`
1. Add the required cs files to the project.
1. Add the CipherTrust.CADP.NETCore NuGet package to the project and build. using command `dotnet build -c Release`
1. Use either of the following commands to execute the project.
    * `dotnet run` command to run the project at a terminal prompt.
    * `dotnet` command to run `SampleApp.dll` at location `\bin\Release\netcoreapp3.1` using terminal. Example: `dotnet SampleApp.dll`
    * [Windows Only] `SampleApp.exe` to run the code at a terminal prompt. Example: `SampleApp.exe`  

## More Information
For more information on CADP for .NET Core, refer to the CADP for .NET Core user guide at [ThalesDocs.com](www.thalesdocs.com/ctp/con/cadp/dotnetcore/index.html).
