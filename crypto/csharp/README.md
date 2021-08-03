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
1. CADP.NetCore.nupkg must be installed.

## Usage: 
1. Before using these cs files, create the console application.
1. Add the required cs files to the project.
1. Add the CADP.NetCore.nupkg to the project and build the project.
1. Use either of the following commands to execute the project.
    * Use `dotnet run` command to run the project at a terminal prompt or within IDE.
    * Use `dotnet` command to run using the `fileName.dll` at a terminal prompt. Example: `dotnet CryptoOpRijndael.dll`
    * [Windows Only] Use `fileName.exe` to run the code at a terminal prompt. Example: `CryptoOpRSAEncDec.exe` 

## More Information
For more information on CADP for .NET Core, refer to the CADP for .NET Core user guide at [ThalesDocs.com](www.thalesdocs.com/ctp/con/cadp/dotnetcore/index.html).
