This readme file contains the following information:

* Overview
* How to Compile Sample Applications
* Sample Applications
* Limitations

## Overview

CADP for C supports Cryptographic Operations through Cryptographic API using NAE protocol for communication with the Key Manager server.

Cryptographic API can be used to perform local cryptographic operations after fetching keys from Key Manager server.

For API details, refer to the Cryptographic API section in the CADP for C API Guide.

## How to Compile Sample Applications

Included with the CADP for C software are sample C/C++ files, the source code for sample applications that you can use to test your installation.

>*To compile the sample application on **Windows**:*

1. Navigate to `<installation_Directory>` i.e., C:\Program Files\CipherTrust\CADP_for_C\.

2. Copy "C" directory of sample applications (CipherTrust_Application_Protection\crypto\C) to `<installation_Directory>`.

3. Navigate to `<installation_Directory>\C\VC`

4. Open the `sample.sln` file in Visual Studio 2010.

5. Select a sample project and build it.

>*To compile the sample application on **Linux**:*

You can compile this with a C++ or C compiler such as gcc (3.2.x or greater). If you have an older gcc or another C compiler, you may need to obtain libstdc++.so.5 and possibly libgcc_s.so.

1. Navigate to `<installation_Directory>`. For example, consider that `<installation_Directory>` is /opt/CipherTrust/CADP_for_C/.

2. Copy "C" directory of sample applications (CipherTrust_Application_Protection/crypto/C) to the `<installation_Directory>`.

3. Navigate to `<installation_Directory>/C/`.

4. Run make command.
```
   [root@machine C]# make
```
5. Run a sample with valid arguments.
```
   [root@machine C]# ./CryptoSinglePart ../CADP_CAPI.properties aes_key_256 AES abcdef null null username password@1234
```

## Sample Applications

Sample applications to demonstrate the use of Cryptographic operations.

**Crypto Sample Applications**

The Crypto sample applications supplied with CADP for C are:

Application| Description
---|---
CryptoSinglePart.c | Performs cryptographic operations using I_C_Crypt().
CryptoSinglePartMultiThreadedC.c | C sample application to perform cryptographic operations in multithreaded environment using I_C_Crypt().
CryptoSinglePartMultiThreadedCPP.cc | C++ sample application to perform cryptographic operations in multithreaded environment using I_C_Crypt().
CryptoSinglePart_Fast.c | Perform cryptographic operations using I_C_Crypt_Fast(). It works only in local mode, when symmetric cache is on.
CryptoSinglePart_FPE.c | Performs cryptographic operations using I_C_Crypt_Enhanced() for Algo FPE/AES/CARD10 or FPE/AES/CARD62 or FPE/AES/CARD26 or FPE/AES/UNICODE. CARD26, CARD62, and UNICODE works in local mode only.
CryptoSinglePart_AES_GCM.c | Performs cryptographic operations using I_C_Crypt_Enhanced() for Algo AES/GCM.
CryptoSinglePartBulk_Enhanced.c | Performs cryptographic operations using I_C_CryptBulk_Enhanced().
CryptoSinglePart_FPE_CC_SSN.c | Performs FPE cryptographic operations using I_C_Crypt_Enhanced_FpeFormat() for Formats CC/SSN like LAST_FOUR format, these format needs FPE/AES/CARD10 as algo.
CryptoSinglePart_multitenency.c| Uses session level properties file via I_C_OpenSession_filepath() and performs cryptographic operations using I_C_Crypt().
CryptoSinglePart_CMS.c | Performs sign verify operations using I_C_Crypt_Enhanced() in CMS format.
CryptoDataUtility.c | This utility allows the user to decrypt a  string without specifying the keyName. To  accomplish this, the cipher text, at the time of encryption, is bundled with the same meta data, of the key, which was used for encryption.
CryptoSinglePart_EC.c | Performs cryptographic operations using I_C_Crypt_Enhanced() for Algo EC.

## Limitations

* Register Template operations using an existing template name are not supported.
* Create operation does not support HMAC algorithms and key creation from template.
* ModifyAttribute operation supports limited attributes. Only the String and DateTime attributes are currently supported.
* Locate operation using wild cards and regular expressions is not supported.

---