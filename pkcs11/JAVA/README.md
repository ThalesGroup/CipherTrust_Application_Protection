# PKCS11 Java Wrapper Samples

This readme file contains the following information:

- Overview
- Prerequisites
- CADP for C PKCS11 Library Path (Default Path)
- How to Run the Code Samples
- Viewing Sample Usage Information
- Ant build


## Overview

The following samples below provide PKCS#11 Java code to demonstrate the following:

- CreateKey.java 
    This file demonstrates the following:
    1. Initialization.
    2. Creating a connection and logging in.
    3. Creating a key on the CipherTrust Manager.
    4. Clean up.

- CreateObject.java
    This file demonstrates the following:
    1. Initialization.
    2. Creating a connection and logging in.
    3. Creating a key object by providing template including key value onto the CipherTrust Manager.
    4. Clean up.

- CreateKeypairSignMessage.java
    This file demonstrates the following:
    1. Initialization.
    2. Creating a connection and logging in.
    3. Creating a key pair on the CipherTrust Manager.
    4. Signing a piece of data with the created key pair.
    5. Delete the key pair.
    6. Clean up.

- DigestMessage.java
    This file demonstrates the following:
    1. Initialization.
    2. Creating a connection and logging in.
    3. Creating a secure hash for a given hash mechanism, or
    4. Creating a secure hash for a given file input stream
    5. Clean up.

- EncryptDecryptAsymmetricKey.java
    This file demonstrates the following
    1. Initialization
    2. Create a connection and logging in.
    3. Create an asymmetric key pair on the CipherTrust Manager
    4. Encrypt and descrypt a message
    5. Clean up.
 
- EncryptDecryptFile.java
    This file demonstrates the following:
    1. Initialization.
    2. Creating a connection and logging in.
    3. Creating a symmetric key on the CipherTrust Manager.
    4. Using the symmetric key to encrypt the input file name and write the encrypted output into "filename.enc".
    5. Using the symmetric key to decrypt the "filename.enc" and write the decrypted output into "filename.dec".
    6. Compare the original input file name with "filename.dec", should be the same.
    7. Clean up.

- EncryptDecryptMessage.java
    This file demonstrates the following:
    1. Initialization.
    2. Creating a connection and logging in.
    3. Creating a symmetric key on the CipherTrust Manager.
    4. Using the symmetric key to encrypt plain text.
    5. Using the symmetric key to decrypt cipher text.
    6. Delete key.
    7. Clean up.

- EncryptDecryptMetadata.java
    This file demonstrates the following:
    1. Initialization.
    2. Creating a connection and logging in.
    3. Finding an existing symmetric key on the CipherTrust Manager.
    4. Creating a symmetric key on the CipherTrust Manager.
    5. Passing user defined metadata while using the symmetric key to encrypt plain text;
    metadata will be logged and uploaded depending on logging level.
    6. Passing in user defined metadata while using the symmetric key to decrypt cipher text;
    metadata will be logged and uploaded depending on logging level.
    7. Search and Delete key.
    8. Clean up.

- FindDeleteKey.java
    This file demonstrates the following:
    1. Initialization.
    2. Creating a connection and logging in.
    3. Querying for a key using the keyname.
    4. Deleting the key that was found.
    5. Clean up.

- FindExportKey
    This file demonstrates the following:
    1. Initialization.
    2. Creating a connection and logging in.
    3. Find a source key on the CipherTrust Manager.
    3. Find a wrapping key on the CipherTrust Manager.
    4. Wrap the source key with the wrapping key.
    7. Save the wrapped key value to a binary file.
    8. Clean up.

- SignVerify
    This file demonstrates the following:
    1. Initialization
    2. Creating a connection and logging in.
    3. Create or find an existing symmetric key, used for HMAC mechanism
    4. Using the symmetric key to sign plaintext using the mechanism to generate the hash
    5. Using the symmetric key to verify ciphertext against the existing hash bytes.
    6. Delete key.
    7. Clean up.

- KeyStateTransition.java
    This file demonstrates the following:
    1. Initialization
    2. Creating a connection and logging in.
    3. Creating a symmetric key with key transition dates specified, or
    4. Setting the key transition dates of an existing symmetric key, or
    5. Setting the key state of an existing symmetric key, and
    6. Getting the key attributes of the created or existing key
    7. Clean up.

- GenerateRandom.java
    This file demonstrates the following:
    1. Initialization.
    2. Create a connection and log in.
    3. Seed the Random Generator and generate the random bytes.
    4. Clean up.

- UnwrapImportKey.java
    This file demostrates the following
    1. Initialization
    2. Create a connection and loggin in.
    3. Using the eventually specified wrappingkey import asymmetric public or private key or import symmetric key read from keyfile.
    4. Clean up.

- TestKeyAttributes.java
    This file demonstrates the following
    1. Initialization
    2. Create a connection and logging in.
    3. Create an asymmetric key pair on the CipherTrust Manager
    4. Getting and printing both public and private key's attributes from custom template
    5. Creating a symmetric key on the CipherTrust Manager
    6. Setting and Getting symmetric key's attributes based on custom template, also readonly attributes
    7. Clean up.

- Helper.java: This file has helper functions shared by other java files.


## Prerequisites

- All the Java samples are compiled and tested using JDK version 1.8.0_111 on Linux and Windows.

To run PKCS11 Java Samples :

- The minimum Java version must be 8 (minimum 1.8.0_111).
- CADP for C library must be installed.
- cadp-pkcs11-wrapper-2.0 Jar must be in the classpath or added in java command using "-cp".
- Add CADP for C PKCS11 Library Path inside Helper.java sample. If Library path is not updated in Helper.java it can be provided as an input for the samples using [-m module] attribute or it will use the default library path.
- In linux properties file needs to be exported using command "export NAE_Properties_Conf_Filename=/*path to property file*/CADP_PKCS11.properties" if CADP for C is not installed on default path. 
- In windows Property file should be placed parallel to the library file.

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

#### To Compile – 
javac -cp .;cadp-pkcs11-wrapper-2.0.jar com\vormetric\pkcs11\sample\Helper.java  com\vormetric\pkcs11\sample\CreateKey.java

#### To Run - 
java -cp .;cadp-pkcs11-wrapper-2.0.jar com.vormetric.pkcs11.sample.CreateKey

    Note: On Linux replace ';' with ':' in -cp attribute and '\' with '/'.
    Note: Replace cadp-pkcs11-wrapper-2.0.jar with the complete path of cadp-pkcs11-wrapper-2.0.jar or place the jar in current directory.


In a similar fashion, you can run other java samples.


## Viewing Sample Usage Information

Before running the code samples in Windows, learn how to run a sample by viewing its usage information (if you do not already know how to do so). To view usage information about a given sample, enter the name of the executable sample file from the directory in which the executable files are located. For example:

java -cp .;cadp-pkcs11-wrapper-2.0.jar com.vormetric.pkcs11.sample.Helper  com.vormetric.pkcs11.sample.CreateKey usage

The following displays: 

usage: java [-cp CLASSPATH] com.cadp.pkcs11.sample.CreateKey -p pin [-k keyName] [-m module] [-g gen_key_action]

-p: Username: Password of CipherTrust Manager
-k: Keyname on CipherTrust Manager
-m: Path of directory where library (Dll) is deployed/installed
-g: ...0 for versionCreate, 1 for versionRotate, 2 for versionMigrate, 3 for nonVersionCreate

## Ant Build

In linux properties file needs to be exported using command "export NAE_Properties_Conf_Filename=/*path to property file*/CADP_PKCS11.properties" if CADP for C is not installed on default path. 

In windows Property file should be placed parallel to the library file.

### Build:

You need ant to build the samples.

Update Library path in Helper.java placed inside custom_wrapper/src/com/vormetric/pkcs11/sample/Helper.java

Move to the directory where build.xml resides. i.e Inside customer_wrapper or sun_pkcs11.

To run all the sample programs altogether, please first modify the following line in build.xml, property name="wrapper.jar" value="cadp-pkcs11-wrapper-2.0.jar", replace cadp-pkcs11-wrapper-2.0.jar with the complete path of cadp-pkcs11-wrapper-2.0.jar or place the jar in current directory.

If you are using Java 11 or newer then modify the following line in build.xml, property name="jaxb.jar" value="jaxb-api-2.3.1.jar", replace jaxb-api-2.3.1.jar with the complete path of jaxb-api-2.3.1.jar or place the jar in current directory.

To compile the sample files, simply type 'ant compile' in the terminal or cmd of directory.

### Execution 
To run all the sample programs altogether, please first modify the following line in build.xml,
property name="PIN" value="username:password"/
replace "username:password" with the credentials you used to register with the CipherTrust Manager, then simply type 'ant' in the terminal or cmd of directory.
