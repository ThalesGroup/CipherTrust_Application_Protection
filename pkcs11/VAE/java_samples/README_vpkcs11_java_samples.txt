
/*************************************************************************
**                                                                      **
** Copyright(c) 2014                              Confidential Material **
**                                                                      **
** This file is the property of Vormetric Inc.                          **
** The contents are proprietary and confidential.                       **
** Unauthorized use, duplication, or dissemination of this document,    **
** in whole or in part, is forbidden without the express consent of     **
** Vormetric, Inc..                                                     **
**                                                                      **
**************************************************************************/

Prerequisites:

1. All the Java samples are compiled and tested using JDK version 1.7.0.45 on Linux and Windows.

Overview:
The following samples below provide PKCS#11 Java code to demonstrate the following:
1. Create an AES256 key.
2. Find and delete an AES256 key.
3. Encrypt and decrypt message using an AES256 key.
4. Encrypt and decrypt file using an AES256 key.
5. Create a key pair and sign using an RSA1024 key pair.
6. Export a key from Data Security Manager wrapped by a wrapping key.
7. Passing user defined meta data for logging purposes while encrypting/decrypting message with an AES256 key.
8. Passing user defined meta data for logging while encrypting/decrypting files using an AES256 key.

To use these files, the user must have the Vormetric key agent properly installed and registered with a Data Security Manager.
Optionally set the environment variable VPKCS11LIBPATH point to the library file.

e.g. in Linux .bash_profile:
VPKCS11LIBPATH=/opt/vormetric/DataSecurityExpert/agent/pkcs11/lib/libvorpkcs11.so
export VPKCS11LIBPATH

Details about the command line parameters:
-p pin       #  the password user selected when registering  the PKCS11 library to the DSM after installation.
-m module    #  the path to the Vormetric PKCS11 library : libvorpkcs11.so.

File: CreateKey.java
usage: java [-cp CLASSPATH] com.vormetric.pkcs11.sample.CreateKey -p pin [-k keyName] [-m module] [-g gen_key_action]
gen_key_action: 0: for versionCreate; 1: for versionRotate; 2: for versionMigrate; 3: for nonVersionCreate.

This file demonstrates the following:
1. Initialization.
2. Creating a connection and logging in.
3. Creating a key on the Data Security Manager.
4. Clean up.

File: CreateObject.java
Usage: java [-cp CLASSPATH] com.vormetric.pkcs11.sample.CreateObject -p pin [-m module]
This file demonstrates the following:
1. Initialization.
2. Creating a connection and logging in.
3. Creating a key object by providing template including key value onto the Data Security Manager.
4. Clean up.

File: CreateKeypairSignMessage.java
Usage: java [-cp CLASSPATH] com.vormetric.pkcs11.sample.CreateKeypairSignMessage -p pin [-m module] [-kp keypair_label]
This file demonstrates the following:
1. Initialization.
2. Creating a connection and logging in.
3. Creating a key pair on the Data Security Manager.
4. Signing a piece of data with the created key pair.
5. Delete the key pair.
6. Clean up.

File: EncryptDecryptMessage.java
usage: java [-cp CLASSPATH] com.vormetric.pkcs11.sample.EncryptDecryptMessage -p pin [-k keyName] [-g genAction ] [-m module] [-o operation] CTR or CBC_PAD (default) or FPE [-f 'inputtokenfile'] ([-c 'char set']|[-r 'charset file']|[-l 'literal charset file']) [-u utf-mode-name] [-d 'decryptedfile']
genAction: 0, versioned_key; 1, rotate versioned key; 2, migrate from non-versioned key to versioned key; 3, non-versioned key.

This file demonstrates the following:
1. Initialization.
2. Creating a connection and logging in.
3. Creating a symmetric key on the Data Security Manager.
4. Using the symmetric key to encrypt plain text.
5. Using the symmetric key to decrypt cipher text.
6. Delete key.
7. Clean up.

File: EncryptDecryptFile.java
usage: java [-cp CLASSPATH] com.vormetric.pkcs11.sample.EncryptDecryptFile -p pin -f inputfile -k keyName [-m module] [-n 0|1]
-n 0|1 ... nodelete flag. 0 is the default value and means 'Delete the key.', whereas 1 means 'Do not delete the key.'

This file demonstrates the following:
1. Initialization.
2. Creating a connection and logging in.
3. Creating a symmetric key on the Data Security Manager.
4. Using the symmetric key to encrypt the input file name and write the encrypted output into "filename.enc".
5. Using the symmetric key to decrypt the "filename.enc" and write the decrypted output into "filename.dec".
6. Compare the original input file name with "filename.dec", should be the same.
7. Clean up.

File: EncryptDecryptAsymmetricKey.java
Usage: java [-cp CLASSPATH] com.vormetric.pkcs11.sample.EncryptDecryptAsymmetricKey -p pin [-m module]
This file demonstrates the following
 * 1. Initialization
 * 2. Create a connection and logging in.
 * 3. Create an asymmetric key pair on the Data Security Manager
 * 4. Encrypt and descrypt a message
 * 5. Clean up.

File: EncryptDecryptMetaData.java
Usage: java [-cp CLASSPATH] com.vormetric.pkcs11.sample.EncryptDecryptMetaData -p pin [-k keyName] [-m module] [-g genaction]
genaction: 0...generate versioned key; 1...rotate versioned key; 2...migrate non-versioned key to versioned key; 3...generate non-versioned key.

This file demonstrates the following:
1. Initialization.
2. Creating a connection and logging in.
3. Finding an existing symmetric key on the Data Security Manager.
4. Creating a symmetric key on the Data Security Manager.
5. Passing user defined metadata while using the symmetric key to encrypt plain text;
   metadata will be logged and uploaded depending on logging level.
6. Passing in user defined metadata while using the symmetric key to decrypt cipher text;
   metadata will be logged and uploaded depending on logging level.
7. Search and Delete key.
8. Clean up.

File: DigestMessage.java
Usage: java [-cp CLASSPATH] com.vormetric.pkcs11.sample.DigestMessage -p pin [-k keyName] [-f input-file]");
[-o operation] HMAC-SHA256, HMAC-MD5, HMAC-SHA1, HMAC-SHA224, HMAC-SHA384, HMAC-SHA512, MD5, SHA1, SHA224, SHA512, SHA384 or SHA256 (default) [-m module] [-i message]
This file demonstrates the following:
1. Initialization.
2. Creating a connection and logging in.
3. Creating a secure hash for a given hash mechanism, or
4. Creating a secure hash for a given file input stream
5. Clean up.

File: FindDeleteKey.java
Usage: java [-cp CLASSPATH] com.vormetric.pkcs11.sample.FindDeleteKey -p pin [-k keyName] [-m module]

This file demonstrates the following:
1. Initialization.
2. Creating a connection and logging in.
3. Querying for a key using the keyname.
4. Deleting the key that was found.
5. Clean up.

File: FindExportKey.java
Usage: java [-cp CLASSPATH] com.vormetric.pkcs11.sample.FindExportKey -p pin [-k sourceKeyName] [-m module]

This file demonstrates the following:
1. Initialization.
2. Creating a connection and logging in.
3. Find a source key on the Data Security Manager.
3. Find a wrapping key on the Data Security Manager.
4. Wrap the source key with the wrapping key.
7. Save the wrapped key value to a binary file.
8. Clean up.

File: GenerateRandom.java
Usage: java [-cp CLASSPATH] com.vormetric.pkcs11.sample.GenerateRandom -p pin -d seed -z random_output_size [-m module]

This file demonstrates the following:
1. Initialization.
2. Create a connection and log in.
3. Seed the Random Generator and generate the random bytes.
4. Clean up.

File: KeyStateTransition.java
Usage: java [-cp CLASSPATH] com.vormetric.pkcs11.sample.KeyStatesTransition -p pin [-m module]
This file demonstrates the following:
1. Initialization
2. Creating a connection and logging in.
3. Creating a symmetric key with key transition dates specified, or
4. Setting the key transition dates of an existing symmetric key, or
5. Setting the key state of an existing symmetric key, and
6, Getting the key attributes of the created or existing key
7. Clean up.

File: SignVerify.java
Usage: java [-cp CLASSPATH] com.vormetric.pkcs11.sample.SignVerify -p pin [-k keyName] [-o operation] [-m module] [-i message]
'operation' is HMAC-SHA256 (default), HMAC-SHA1, HMAC-SHA224, HMAC-SHA384, or HMAC-SHA512

This file demonstrates the following:
1. Initialization
2. Creating a connection and logging in.
3. Create or find an existing symmetric key, used for HMAC mechanism
4. Using the symmetric key to sign plaintext using the mechanism to generate the hash
5. Using the symmetric key to verify ciphertext against the existing hash bytes.
6, Delete key.
7. Clean up.

File: TestKeyAttributes.java
Usage: java [-cp CLASSPATH] com.vormetric.pkcs11.sample.TestKeyAttributes -p pin [-k keyname] [-m module] [-b modulusBits]

This file demonstrates the following
1. Initialization
2. Create a connection and logging in.
3. Create an asymmetric key pair on the Data Security Manager
4. Getting and printing both public and private key's attributes from custom template
5. Creating a symmetric key on the Data Security Manager
6. Setting and Getting symmetric key's attributes based on custom template, also readonly attributes
7. Clean up.

File: UnwrapImportKey.java
Usage: java [-cp CLASSPATH] com.vormetric.pkcs11.sample.UnwrapImportKey -p pint [-u wrappingkeyName] [-m module] [-v public-key-name] [-c private-key-name] [-f format] [-i keyfile]

This file demostrates the following
1. Initialization
2. Create a connection and loggin in.
3. Using the eventually specified wrappingkey import asymmetric public or private key or import symmetric key read from keyfile.
4. Clean up.


File:Helper.java
This file has helper functions shared by other java files.

Build:
You need ant to build the samples.
To compile the sample files, simply type 'ant compile' in this directory where this
README file resides.

For example:
$>ant compile

Execution:
To run all the sample programs altogether, please first modify the following line in build.xml,
<property name="PIN"  value="YourPIN"/>
replace "YourPIN" into the PIN you used to register the host with DSM, then simply
type 'ant' in this directory where this REAME file resides.

For example:
$>ant

To run the program individually, run the following java command:
$>java <classname> -p yourPIN

For example:

$>java -cp build/classes  com.vormetric.pkcs11.sample.FindExportKey -p yourPIN

$>java -cp build/classes  com.vormetric.pkcs11.sample.FindExportKey -p yourPIN -m /opt/vormetric/DataSecurityExpert/agent/pkcs11/lib/libvorpkcs11.so

TIP:

If special characters like exclamation point('!'), dollar sign ('$') or dash
('-) are used inside the PIN, when running the sample on Linux/Unix shell
prompt, Escape character backslash ('\') must be used in front of those characters
to prevent shell from expanding the string after.
e.g. if PIN = '!123Admin', on Linux/Unix shell you should run a sample like the
following:
java -cp  build/classes  com.vormetric.pkcs11.sample.CreateKey  -p \!123Admin
