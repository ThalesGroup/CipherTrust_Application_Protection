/*************************************************************************
**                                                                      **
** Sample code is provided for educational purposes.                    **
** No warranty of any kind, either expressed or implied by fact or law. **
** Use of this item is not restricted by copyright or license terms.    **
**                                                                      **
**************************************************************************/

Prerequisites: 

All the Java samples are compiled and tested using JDK version 1.8.0_111 .

To use these sample files, the user must have the CADP JCE properly installed and configured. 

For more information on CADP JCE and samples, refer to the CADP JCE user guide.

Note: 1)Before using these java files ,compile these using javac compiler.
      2)Required CADP JCE jars should be present in the java classpath.


Overview:

File : AESGCMEncryptionDecryptionSample.java
Usage: java AESGCMEncryptionDecryptionSample user password keyname authTagLength iv aad data
This sample shows how to perform crypto-operations(Encrypt and Decrypt) using AES-GCM mode. 
Note: IV and AAD should be passed in the hexadecimal in this sample.

File : AESGCMUpdateSample.java
Usage: java AESGCMUpdateSample user password keyname authTagLength iv aad data
This sample shows how to perform crypto-operations(Encrypt and Decrypt) using AES-GCM mode and update method. 
Note: IV and AAD should be passed in the hexadecimal in this sample.

File: BulkOperationSample.java
Usage: java BulkOperationSample username password keyname datafile
This samples show how to perform bulk operations using different algorithms on different type of data and algorithm data.

File: CachingSample.java
Usage: java CachingSample user password keyname
This sample shows how to encrypt and decrypt data using CADP JCE in local mode.

File: CMSSignSample.java
Usage: java CMSSignSample user password keyname caName
This sample shows how to CMS sign data and verify signature using CADP JCE.

File: CryptoDataUtilitySample.java
Usage: java CryptoDataUtilitySample username password keyname transformation text
This sample will do a test on the encryption utility.

File: ECCEncryptionSample.java
Usage: java ECCEncryptionSample user password keyname
This sample demonstrates how to perform encryption/decryption using the ECC key.

File: ECCSignSample.java
Usage: java ECCSignSample user password keyname
This sample demonstrates how to perform Sign and SignVerify operations using ECC key.

File: FileEncryptionDecryptionSampleUsingRSA.java
Usage: java FileEncryptionDecryptionSampleUsingRSA userName password asymKeyName fileToEncrypt encryptedFile decryptedFile
This sample shows how to encrypt/decrypt a file using RSA Algorithm.

File: FileEncryptionSample.java
Usage: java FileEncryptionSample user password keyname fileToEncrypt encryptedFile decryptedFile
This sample shows how to encrypt and decrypt file using CADP JCE.

File: FileEncryptionSampleUsingARIA.java
Usage: java FileEncryptionSampleUsingARIA user password keyname fileToEncrypt encryptedFile decryptedFile iv blockSize
This sample shows how to perform file encryption operation using ARIA in local mode.

File: FileEncryptionSampleUsingGCM.java
Usage: java FileEncryptionSampleUsingGCM user password keyname fileToEncrypt encryptedFile decryptedFile authTagLength iv aad blockSize
This sample shows how to perform file encryption operation using gcm in both local and remote mode.

File: FileEncryptionSampleUsingSEED.java
Usage: java FileEncryptionSampleUsingSEED user password keyname fileToEncrypt encryptedFile decryptedFile iv blockSize
This sample shows how to perform file encryption operation using SEED in local mode.

File: HMACSample.java
Usage: java HMACSample user password keyname
This sample shows how to create the message authentication code and how to verify it using CADP JCE.

File: MultiThreadMacSample.java
Usage: java MultiThreadMacSample user password mackeyname
This sample shows how to use multiple threads that share the same session and perform mac operations.

File: MultiThreadSamplee.java
Usage: java MultiThreadSample user password keyname
This sample shows how to use multiple threads that share the same session using CADP JCE.

File: RSAEncryptionSample.java
Usage: java RSAEncryptionSample user password keyname
This sample shows how to encrypt and decrypt data using RSA key.

File: SecretKeyEncryptionSample.java
Usage: java SecretKeyEncryptionSample user password keyname
This sample shows how to encrypt and decrypt data using CADP JCE.

File: SignSample.java
Usage: java SignSample user password keyname [saltlength]
This sample shows how to sign data and verify signature using CADP JCE.


File: CryptoTool.java 

USAGE:
	java CryptoTool OPERATION options
 
SUPPORTED CRYPTO OPERATIONS:

	ENCRYPT, DECRYPT, MAC, MACV, SIGN, SIGNV

SUPPORTED KEY MANAGEMENT OPERATIONS:

	GENERATE, DELETE, EXPORT, IMPORT, LIST

SUPPORTED OPTIONS:

-auth username:passwd 
	 username and password for authentication
-in filename 
	 specify a file instead of stdin
-out filename 
	 specify a file instead of stdout
-key keyname 
	 key name
-alg algname 
	 algorithm
-iv value 
	 initialization vector when required (must be hex ASCII encoded)
-sig value  
	 provide signature value as an argument to use for verification (must be hex ASCII encoded)
-sigfile filename  
	 alternative to -sig; provide signature value in a file
-mac value 
	 provide mac value as an argument to use for verification (must be hex ASCII encoded)
-macfile filename  
	 alternative to -mac; provide mac value in a file
-keysize size 
	 key size to use for key generation
-exportable 
	 create exportable key
-deletable 
	 create deletable key
-ip ip 
	 NAE server IP to use  (can be a colon separated list of IP addresses)
-port port 
	 NAE server port to use
-protocol prot 
	 protocol to use (ssl or tcp)
-tweakalgo TweakAlgo 
	 to specify Tweak Algorithm name for FPE encryption
-tweakdata TweakData 
	 to specify Tweak Data for FPE encryption
-aad AAD 
	 to specify AAD for GCM encryption
-authtaglength authtaglength 
	 to specify authtaglength for GCM Encryption
	 
This sample is used to perform various crypto and key management operations offered by CADP JCE.


Samples in FPE directory:

File: FF1EncryptionDecryptionSample.java
Usage: java FF1EncryptionDecryptionSample user password keyname [TweakAlgorithm] [TweakData]
Note: Mention null for optional parameters if you don't want to pass it.
This sample shows how to encrypt and decrypt data using FF1 algorithm.

File: FPEEncryptionDecryptionSample.java
Usage: java FPEEncryptionDecryptionSample user password keyname IV [TweakAlgorithm] [TweakData]
Note: Mention null for optional parameters if you don't want to pass it.
This sample shows how to encrypt and decrypt data using FPE.

