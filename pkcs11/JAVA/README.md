# PKCS11 Java Wrapper Samples

This readme file contains the following information:

- Overview
- Prerequisites
- CADP for C PKCS11 Library Path (Default Path)
- How to Run the Code Samples
- Viewing Sample Usage Information


## Overview

It is a JAR file that provides PKCS11 JAVA wrapper APIs. Underknith it call CADP for C PKCS11 C APIs.

Note: For details about the CADP for C PKCS11 APIs, refer to the CipherTrust Application Data Protection PKCS11 API Reference Guide. For information about how to install, configure, and upgrade CADP for C, refer to the online CADP for C user documentation at https://thalesdocs.com.

The following samples provide CADP for C PKCS11 code to illustrate the following functionality:

- CreateKey.java : Creates an AES key.
- CreateObject.java : Creates a random or opaque key object.
- DigestMessage.java : Computes a digest or HMAC with a given key.
- EncryptDecryptAsymmetricKey.java : Encrypts and decrypts the content with the asymmetric key. 
- EncryptDecryptFile.java : Encrypts and decrypts the file content.
- EncryptDecryptMessage.java : Encrypts and decrypts the input data from the file with extra options like charset, reserve leftmost character, etc.
- EncryptDecryptMetadata.java : Encrypts and decrypts the content.
- FindDeleteKey.java: Finds and deletes an AES key.
- CreateKeypairSignMessage: Creates a key pair and signs using an RSA key pair.
- FindExportKey: Exports a key from a Key Manager wrapped by a wrapping key.
- SignVerify: Signs and verifies a given message based on a generated symmetric key
- KeyStateTransition.java : Creates a key with given key state transition dates or sets key states or key state transition dates for a given key.
- GenerateRandom.java : Generates a random sequence of bytes.
- UnwrapImportKey.java : Reads the wrapped bytes from a file provided by the user, and then imports the key with unwrapped bytes. 
- TestKeyAttributes.java : Create an asymmetric key pair. Sign a piece of message, Verify the message was signed with the created private key, and delete the key pair.
- Helper.java: Contains global settings, pkcs11 library path, and helper functions shared by other .c files.


## Prerequisites

To run PKCS11 Java Samples :
- The minimum Java version must be 8 (minimum 1.8.0_111).
- CADP for C library must be installed.
- CADP-pkcs11-wrapper-1.0 Jar must be in the classpath.
- Add CADP for C PKCS11 Library Path inside Helper.Java sample.

## CADP for C PKCS11 Library Path (Default Path)

The default path for the CADP for C PKCS11 library in Windows is the following:

    C:\Program Files\CipherTrust\CADP_for_C\libcadp_pkcs11.dll

The default path for the CADP for C PKCS11 library in Linux is the following:

    /opt/CipherTrust/CADP_for_C/libcadp_pkcs11.so


## How to Run the Code Samples

This section provides instructions on how to view the sample usage information and run the PKCS11 Java Samples in Windows and Linux. For Linux, additional information is provided on how to set the path of the CADP_PKCS11.properties file through an environment variable (if required).

### Windows & Linux

#### Running Code Samples
Go to the src directory placed inside custom_wrapper or sun_pkcs11 according to your requirement for samples.

Run the following command to run the CreateKey.java sample from custom_wrapper:

### To Compile – 
java -cp .;cadp-pkcs11-wrapper-1.0.jar com.vormetric.pkcs11.sample.Helper.java  com.vormetric.pkcs11.sample.CreateKey.java

### To Run - 
java -cp .;cadp-pkcs11-wrapper-1.0.jar com.vormetric.pkcs11.sample.Helper com.vormetric.pkcs11.sample.CreateKey

Note: In a similar fashion, you can run other java samples.


#### Viewing Sample Usage Information

Before running the code samples in Windows, learn how to run a sample by viewing its usage information (if you do not already know how to do so). To view usage information about a given sample, enter the name of the executable sample file from the directory in which the executable files are located. For example:

java -cp .;cadp-pkcs11-wrapper-1.0.jar com.vormetric.pkcs11.sample.Helper  com.vormetric.pkcs11.sample.CreateKey usage

The following displays: 

usage: java [-cp CLASSPATH] com.cadp.pkcs11.sample.CreateKey -p pin [-k keyName] [-m module] [-g gen_key_action]

-p: Username: Password of Keymanager
-k: Keyname on Keymanager
-m: Path of directory where library (Dll) is deployed/installed
-g: ...0 for versionCreate, 1 for versionRotate, 2 for versionMigrate, 3 for nonVersionCreate