This readme file contains the following information:

* Overview
* How to Compile Sample Applications
* Sample Applications
* Limitations

## Overview

CADP for C v8.13.0.000 supports Key Management using KMIP protocol for communication with the KMIP server. Currently, only the following managed objects are supported: Symmetric Key, Template, and Secret Data.

For API details, refer to the KMIP Key Management API section in the CADP for C API Guide. To use KMIP with CADP CAPI, you must set the KMIP_Spec_File, KMIP_IP, KMIP_Port, Protocol, and CA_File parameters in the  properties file.

**Important!** Additional parameters can be set for the additional features. To use the KMIP Key Management features, the Protocol parameter should be set to ssl.

For details on KMIP, visit: http://www.oasis-open.org/standards#kmip.

## How to Compile Sample Applications

Included with the CADP for C v8.13.0.000 software are sample C/C++ files, the source code for sample applications that you can use to test your installation.

>*To compile the sample application on **Windows**:*

1. Navigate to `<installation_Directory>` i.e., C:\Program Files\CipherTrust\CADP_for_C\.

2. Copy "C" directory of sample applications (CipherTrust_Application_Protection\kmip\C) to `<installation_Directory>`.

3. Navigate to `<installation_Directory>\C\VC`

4. Open the `sample.sln` file in Visual Studio 2010.

5. Select a sample project and build it.

>*To compile the sample application on **Linux**:*

You can compile this with a C++ or C compiler such as gcc (3.2.x or greater). If you have an older gcc or another C compiler, you may need to obtain libstdc++.so.5 and possibly libgcc_s.so.

1. Navigate to `<installation_Directory>`. For example, consider that `<installation_Directory>` is /opt/CipherTrust/CADP_for_C/.

2. Copy "C" directory of sample applications (CipherTrust_Application_Protection/kmip/C) to the `<installation_Directory>`.

3. Navigate to `<installation_Directory>/C/`.

4. Run make command.
```
   [root@machine C]# make
```
5. Run a sample with valid arguments.
```
   [root@machine C]# ./KMIPCreate -h
```

## Sample Applications

Sample applications to demonstrate the use of KMIP Key Management API.

**KMIP Key Management Sample Applications**

The KMIP Key Management sample applications supplied with CADP for C are:

Application | Description
---|---
KMIPLocate.c | Demonstrates the KMIP Locate operation.
KMIPRegisterSymmetricKey.c | Demonstrates the KMIP Register operation with Symmetric Key.
KMIPRegisterTemplate.c | Demonstrates the KMIP Register operation with Template.
KMIPRegisterSecretData.c | Demonstrates the KMIP Register operation with Secret Data.
KMIPRegisterCustomBigInt.c | Demonstrates the KMIP Register operation with Template and Big Integer Custom Attribute.
KMIPGet.c | Demonstrates the KMIP Get operation.
KMIPGetAttributes.c| Demonstrates the KMIP GetAttributes operation.
KMIPGetAttributeList.c | Demonstrates the KMIP GetAttributeList operation.
KMIPDeleteAttribute.c | Demonstrates the KMIP DeleteAttribute operation.
KMIPRegisterPublicKey.c | Demonstrates the KMIP RegisterPublicKey operation.
KMIPRegisterPrivateKey.c | Demonstrates the KMIP RegisterPrivateKey operation.
KMIPCreate.c | Demonstrates the KMIP Create operation.
KMIPAddAttribute.c | Demonstrates the KMIP AddAttribute operation.
KMIPModifyAttribute.c | Demonstrates the KMIP ModifyAttribute operation.
KMIPQuery.c | Demonstrates the KMIP Query operation.
KMIPDestroy.c | Demonstrates the KMIP Destroy operation.
KMIPGetCustomAttribute.c | Demonstrates the KMIP Get Custom attribute operation by name and index.
KMIPSetDate.c | Demonstrates the KMIP Add and Modify date attributes.
KMIPRevoke.c | Demonstrates the KMIP Revoke operation.
KMIPCreateKeyPair.c | Demonstrates KMIP Create key pair operation.
KMIPGetWrappedKey.c | Demonstrates KMIP Key wrapping/unwrapping.
KMIPDiscoverVersion.c | Demonstrates KMIP Discover Version. 
KMIPReKey.c | Demonstrates KMIP ReKey operation.
KMIPReKeyPair.c | Demonstrates KMIP ReKey Key Pair operation.
KMIPCrypto.c | Demonstrates KMIP cryptographic operations.
KMIPCrypto_AES_GCM.c | Demonstrates KMIP cryptographic operations for algorithm AES/GCM.
KMIPCrypto_RSA.c | Demonstrates KMIP cryptographic operations for algorithm RSA.

## Limitations

* If KMIP is configured (by configuring the KMIP_IP parameter in the properties file), using I_C_OpenSession with the I_T_Auth_Password parameter returns failure.  

    You can use the I_T_AuthNoPassword parameter for no credential support. To use Credential Base object, the I_T_Auth_KMIP parameter is used.

* Register Template operations using an existing template name are not supported.
* Create operation does not support HMAC algorithms and key creation from template.
* ModifyAttribute operation supports limited attributes. Only the String and DateTime attributes are currently supported.
* Locate operation using wild cards and regular expressions is not supported.

---