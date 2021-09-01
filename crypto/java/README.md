# Sample Code for Cryptographic Operations in Java

## Overview

## Samples

1. Encrypt/Decrypt with AES-GCM

    This sample shows how to perform *crypto-operations (Encrypt and Decrypt)* in the  **AES-GCM** mode. 

    **Note:** For this sample, IV and AAD should be passed in the *hexadecimal* format.

    * File: [*AESGCMEncryptionDecryptionSample.java*](AESGCMEncryptionDecryptionSample.java)
    * Usage: 
	```shell
	java AESGCMEncryptionDecryptionSample <username> <password> <keyname> <authTagLength> <iv> <aad> <data>
    ```

1. Using Update method with AES-GCM

    This sample shows how to perform *crypto operations* using update method in the `AES-GCM` mode.

    **Note:** For this sample, IV and AAD should be passed in the *hexadecimal* format.

    * File: [*AESGCMUpdateSample.java*](AESGCMUpdateSample.java)
    * Usage: 
	```shell
	java AESGCMUpdateSample <username> <password> <keyname> <authTagLength> <iv> <aad> <data>
	```

1. Bulk Operations

    This samples show how to perform *bulk operations* using *different algorithms* on different types of data and algorithm data.

    * File: [*BulkOperationSample.java*](BulkOperationSample.java)
    * Usage: 
	```shell
	java BulkOperationSample <username> <password> <keyname> <datafile>
	```

1. Encrypt/Decrypt with AES-GCM in Local mode

    This sample shows how to *encrypt and decrypt* data using `CADP JCE` in the *local mode*.

    * File: [*CachingSample.java*](CachingSample.java)
    * Usage: 
	```shell
	java CachingSample <username> <password> <keyname>
	```

1. CMS Sign Data and Verify

    This sample shows how to perform *CMS sign data and verify signature* using `CADP JCE`.

    * File: [*CMSSignSample.java*](CMSSignSample.java)
    * Usage: 
	```shell
	java CMSSignSample <username> <password> <keyname> <caName>
	```

1. Encryption Utility

    This sample tests the *encryption utility*.

    * File: [*CryptoDataUtilitySample.java*](CryptoDataUtilitySample.java)
    * Usage: 
	```shell
	java CryptoDataUtilitySample <username> <password> <keyname> <textToTransform>
	```


1. Encrypt/Decrypt with ECC

    This sample demonstrates how to perform *encryption/decryption* using the **ECC** key.

    * File: [*ECCEncryptionSample.java*](ECCEncryptionSample.java)
    * Usage: 
	```shell
	java ECCEncryptionSample <username> <password> <keyname>
	```

1. Sign/Verify with ECC

    This sample demonstrates how to perform *Sign and SignVerify* operations using the **ECC** key.

    * File: [*ECCSignSample.java*](ECCSignSample.java)
    * Usage: 
	```shell
	java ECCSignSample <username> <password> <keyname>
	```

1. Encrypt/Decrypt with RSA

    This sample shows how to *encrypt/decrypt* a file using the **RSA** algorithm.

    * File: [*FileEncryptionDecryptionSampleUsingRSA.java*](FileEncryptionDecryptionSampleUsingRSA.java)
    * Usage: 
	```shell
	java FileEncryptionDecryptionSampleUsingRSA <username> <password> <asymKeyName> <fileToEncrypt> <encryptedFile> <decryptedFile>
	```

1. Encrypt/Decrypt a File

    This sample shows how to *encrypt and decrypt* a file using **CADP JCE**.

    * File: [*FileEncryptionSample.java*](FileEncryptionSample.java)
    * Usage: 
	```shell
	java FileEncryptionSample user <password> <keyname> fileToEncrypt encryptedFile decryptedFile
	```

1. File Encryption using ARIA in Local mode

    This sample shows how to perform *file encryption* operation using **ARIA** in the *local mode*.

    * File: [*FileEncryptionSampleUsingARIA.java*](FileEncryptionSampleUsingARIA.java)
    * Usage:
	```shell
	java FileEncryptionSampleUsingARIA <username> <password> <keyname> <fileToEncrypt> <encryptedFile> <decryptedFile> <iv> <blockSize>
	```

1. File Encryption using AES-GCM in Local and Remote mode

    This sample shows how to perform *file encryption* operation using **AES-GCM** in the *Local* and *Remote* mode.

    * File: [*FileEncryptionSampleUsingGCM.java*](FileEncryptionSampleUsingGCM.java)
    * Usage: 
	```shell
	java FileEncryptionSampleUsingGCM <username> <password> <keyname> <fileToEncrypt> <encryptedFile> <decryptedFile> <authTagLength> <iv> <aad> <blockSize>
	```

1. File Encryption using SEED in Local mode

    This sample shows how to perform *file encryption* operation using **SEED** in the *Local* mode.

    * File: [*FileEncryptionSampleUsingSEED.java*](FileEncryptionSampleUsingSEED.java)
    * Usage: 
	```shell
	java FileEncryptionSampleUsingSEED <username> <password> <keyname> fileToEncrypt encryptedFile decryptedFile iv blockSize
	```

1. HMAC/Verify

    This sample shows how to create a *Message Authentication Code (MAC)* and how to *verify* it using **CADP JCE**.

    * File: [*HMACSample.java*](HMACSample.java)
    * Usage: 
	```shell
	java HMACSample <username> <password> <keyname>
	```

1. HMAC in MultiThreaded environment

    This sample shows how to use *multiple threads* that share the *same session* and perform *MAC operations*.

    * File: [*MultiThreadMacSample.java*](MultiThreadMacSample.java)
    * Usage: 
	```shell
	java MultiThreadMacSample <username> <password> <mackeyname>
	```

1. Multithreading

    This sample shows how to use *multiple threads* that share the *same session* using **CADP JCE**.

    * File: [*MultiThreadSample.java*](MultiThreadSample.java)
    * Usage: 
	```shell
	java MultiThreadSample <username> <password> <keyname>
    ```

1. Encrypt/Decrypt with RSA

    This sample shows how to *encrypt and decrypt* data using the **RSA** key.

    * File: [*RSAEncryptionSample.java*](RSAEncryptionSample.java)
    * Usage: 
	```shell
	java RSAEncryptionSample <username> <password> <keyname>
	```

1. Encrypt/Decrypt a Secret Key

    This sample shows how to *encrypt and decrypt* data using **CADP JCE**.

    * File: [*SecretKeyEncryptionSample.java*](SecretKeyEncryptionSample.java)
    * Usage: 
	```shell
	java SecretKeyEncryptionSample <username> <password> <keyname>
	```

1. Sign/Verify

    This sample shows how to perform the *sign data* and *verify signature* operation using **CADP JCE**.

    * File: [*SignSample.java*](SignSample.java)
    * Usage: 
	```shell
	java SignSample <username> <password> <keyname> [<saltlength>]
	```

1. Utility to do various Cryptographic and Key Operations

    This sample is used to perform various *crypto* and *key management* operations offered by **CADP JCE**.

    * File: [*CryptoTool.java*](CryptoTool.java)
    * Usage: 
	```shell
	java CryptoTool <OPERATION> <options>
	```

	where `OPERATION` is one of the following supported operations:
	* *Crypto*: `ENCRYPT`, `DECRYPT`, `MAC`, `MACV`, `SIGN`, `SIGNV`
    * *Key Management*: `GENERATE`, `DELETE`, `EXPORT`, `IMPORT`, `LIST`

    and `options` is one or many of the following:
	* Authentication: `-auth <username:passwd>`
    * Input File: `-in <filename>`
		* Default is standard input
    * Output File: `-out <filename>`
		* Default is standard output
    * Key: `-key <keyname>`
    * Algorithm: `-alg <algoName>`
    * Initialization Vector (IV): `-iv <value>`
		* Provide initialization vector when required (must be hex ASCII encoded)
    * Signature: `-sig <value>`
		* Provide signature value as an argument to use for verification (must be hex ASCII encoded)
    * Signature File: `-sigfile <filename>`
		* Alternative to `Signature`
    * MAC: `-mac <MACvalue>`
		* Provide MAC value as an argument to use for verification (must be hex ASCII encoded)
    * MAC File: `-macfile <filename>`
	    * Alternative to `MAC`
    * Key Size: `-keysize <sizeInBytes>`
		* Size of key used for key generation
    * Create an Exportable Key: `-exportable`
    * Create a Deletable Key: `-deletable`
    * Key Manager/NAE Server IP Address: `-ip <ip>`
		* <ip> can be a colon separated list of IP addresses
    * Key Manager/NAE Server Port: `-port <port>`
    * SSL Enabled: `-protocol ssl`
    * SSL Disabled: `-protocol tcp`
    * Tweak Algorithm: `-tweakalgo <TweakAlgo> `
		* To specify Tweak Algorithm name for **FPE** encryption
    * Tweak Data: `-tweakdata <TweakData>`
		* To specify Tweak Data for **FPE** encryption
    * AAD for AES-GCM: `-aad <aad>
    * Auth Tag Length for AES-GCM: `-authtaglength <authtaglength>`

## Samples for Format Preserving Encryption (FPE) [in FPE directory](FPE):

1. Tokenization or Encrypt/Decrypt with FF1

    This sample shows how to *encrypt and decrypt* data using the **FF1** algorithm.

    * File: [*FF1EncryptionDecryptionSample.java*](FPE/FF1EncryptionDecryptionSample.java)
    * Usage: 
	```shell
	java FF1EncryptionDecryptionSample <username> <password> <keyname> [<TweakAlgorithm>] [<TweakData>]
	```

    **Note:** Specify null for optional parameters if you want to *skip* them.

1. Tokenization or Encrypt/Decrypt with FPE

    This sample shows how to *encrypt and decrypt* data using **FPE**.

    * File:* [*FPEEncryptionDecryptionSample.java*](FPE/FPEEncryptionDecryptionSample.java)
    * Usage: 
	```shell
	java FPEEncryptionDecryptionSample <username> <password> <keyname> <iv> [<TweakAlgorithm>] [<TweakData>]
	```

    **Note:** Specify null for optional parameters if you want to *skip* them.

## Prerequisites: 

All the Java samples are compiled and tested using ***JDK version 1.8.0_111***.

To use these sample files, user must have

- `CADP JCE` installed and configured.
- A `javac` compiler in path to compile the sample. 
    
## More Information

For more information on CADP JCE and samples, refer to the `CADP JCE User Guide`.
