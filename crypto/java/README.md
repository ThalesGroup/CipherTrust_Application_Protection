# Sample Code for Java

##Overview:


**File:** *AESGCMEncryptionDecryptionSample.java*

*`Usage: java AESGCMEncryptionDecryptionSample user password keyname authTagLength iv aad data`*

This sample shows how to perform *crypto-operations (Encrypt and Decrypt)* in the  **AES-GCM** mode. 

**Note:** For this sample, IV and AAD should be passed in the *hexadecimal* format.

**File:** *AESGCMUpdateSample.java*

*`Usage: java AESGCMUpdateSample user password keyname authTagLength iv aad data`*

This sample shows how to perform *crypto operations* using update method in the **AES-GCM** mode.
 
**Note:** For this sample, IV and AAD should be passed in the *hexadecimal* format.

**File:** *BulkOperationSample.java*

*`Usage: java BulkOperationSample username password keyname datafile`*

This samples show how to perform *bulk operations* using *different algorithms* on different types of data and algorithm data.

**File:** *CachingSample.java*

*`Usage: java CachingSample user password keyname`*

This sample shows how to *encrypt and decrypt* data using **CADP JCE** in the *local mode*.

**File:** *CMSSignSample.java*

*`Usage: java CMSSignSample user password keyname caName`*

This sample shows how to perform *CMS sign data and verify signature* using **CADP JCE**.

**File:** *CryptoDataUtilitySample.java*

*`Usage: java CryptoDataUtilitySample username password keyname transformation text`*

This sample tests the *encryption utility*.

**File:** *ECCEncryptionSample.java*

*`Usage: java ECCEncryptionSample user password keyname`*

This sample demonstrates how to perform *encryption/decryption* using the **ECC** key.

**File:** *ECCSignSample.java*

*`Usage: java ECCSignSample user password keyname`*

This sample demonstrates how to perform *Sign and SignVerify* operations using the **ECC** key.

**File:** *FileEncryptionDecryptionSampleUsingRSA.java*

*`Usage: java FileEncryptionDecryptionSampleUsingRSA userName password asymKeyName fileToEncrypt encryptedFile decryptedFile`*

This sample shows how to *encrypt/decrypt* a file using the **RSA** Algorithm.

**File:** *FileEncryptionSample.java*

*`Usage: java FileEncryptionSample user password keyname fileToEncrypt encryptedFile decryptedFile`*

This sample shows how to *encrypt and decrypt* a file using **CADP JCE**.

**File:** *FileEncryptionSampleUsingARIA.java*

*`Usage: java FileEncryptionSampleUsingARIA user password keyname fileToEncrypt encryptedFile decryptedFile iv blockSize`*

This sample shows how to perform *file encryption* operation using **ARIA** in the *local mode*.

**File:** *FileEncryptionSampleUsingGCM.java*

*`Usage: java FileEncryptionSampleUsingGCM user password keyname fileToEncrypt encryptedFile decryptedFile authTagLength iv aad blockSize`*

This sample shows how to perform *file encryption* operation using **GCM** in the *local and remote* mode.

**File:** *FileEncryptionSampleUsingSEED.java*

*`Usage: java FileEncryptionSampleUsingSEED user password keyname fileToEncrypt encryptedFile decryptedFile iv blockSize`*

This sample shows how to perform *file encryption* operation using **SEED** in the *local* mode.

**File:** *HMACSample.java*

*`Usage: java HMACSample user password keyname`*

This sample shows how to create a *Message Authentication Code(MAC)* and how to *verify* it using **CADP JCE**.

**File:** *MultiThreadMacSample.java*

*`Usage: java MultiThreadMacSample user password mackeyname`*

This sample shows how to use *multiple threads* that share the *same session* and perform *mac operations*.

**File:** *MultiThreadSample.java*

*`Usage: java MultiThreadSample user password keyname`*

This sample shows how to use *multiple threads* that share the *same session* using **CADP JCE**.

**File:** *RSAEncryptionSample.java*

*`Usage: java RSAEncryptionSample user password keyname`*

This sample shows how to *encrypt and decrypt* data using the **RSA** key.

**File:** *SecretKeyEncryptionSample.java*

*`Usage: java SecretKeyEncryptionSample user password keyname`*

This sample shows how to *encrypt and decrypt* data using **CADP JCE**.

**File:** *SignSample.java*

*`Usage: java SignSample user password keyname [saltlength]`*

This sample shows how to perform the *sign data* and *verify signature* operation using **CADP JCE**.


**File:** *CryptoTool.java*

*`Usage: java CryptoTool OPERATION options`*

This sample is used to perform various *crypto* and *key management* operations offered by **CADP JCE**.
 
Supported *Crypto* Operations:

	ENCRYPT, DECRYPT, MAC, MACV, SIGN, SIGNV

Supported *Key Management* Operations:

	GENERATE, DELETE, EXPORT, IMPORT, LIST

Supported Options:

**-auth** *username:passwd* username and password for authentication

**-in** *filename* specify a file instead of stdin

**-out** *filename* specify a file instead of stdout

**-key** *keyname* specify a key name

**-alg** *algoname* specify the name of the algorithm

**-iv** *value*  provide initialization vector when required (must be hex ASCII encoded)

**-sig** *value*  provide signature value as an argument to use for verification (must be hex ASCII encoded)

**-sigfile** *filename*  alternative to **-sig**, provide signature value in a file

**-mac** *value* provide mac value as an argument to use for verification (must be hex ASCII encoded)

**-macfile** *filename*  alternative to **-mac**, provide mac value in a file

**-keysize** *size*  size of key used for key generation

**-exportable** create exportable key

**-deletable** create deletable key

**-ip** *ip* NAE server IP to use  (can be a colon separated list of IP addresses)

**-port** *port* NAE server port to use

**-protocol** *protocol* protocol to use (ssl or tcp)

**-tweakalgo** *TweakAlgo* to specify Tweak Algorithm name for **FPE** encryption

**-tweakdata** *TweakData* to specify Tweak Data for **FPE** encryption

**-aad** *AAD* to specify AAD for *GCM* encryption

**-authtaglength** *authtaglength* to specify authtaglength for **GCM** Encryption
	 



###Samples in FPE directory:

**File:** *FF1EncryptionDecryptionSample.java*

*`Usage: java FF1EncryptionDecryptionSample user password keyname [TweakAlgorithm] [TweakData]`*

**Note:** Specify null for optional parameters if you want to *skip* them.

This sample shows how to *encrypt and decrypt* data using the **FF1** algorithm.

**File:** *FPEEncryptionDecryptionSample.java*

*`Usage: java FPEEncryptionDecryptionSample user password keyname IV [TweakAlgorithm] [TweakData]`*

**Note:** Specify null for optional parameters if you want to *skip* them.

This sample shows how to *encrypt and decrypt* data using **FPE**.

##Prerequisites: 

All the Java samples are compiled and tested using ***JDK version 1.8.0_111*** .

To use these sample files, user must have

- **CADP JCE** installed and configured.
- A ***javac*** compiler to compile the samples.
- ***CADP JCE Jar*** files in the java classpath.
    

##More Information

For more information on CADP JCE and samples, refer to the *CADP JCE User Guide*.

