
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

Overview:
The following samples provide PKCS#11 C code to illustrate the following:
1. Create an AES256 key.
2. Find and delete an AES256 key.
3. Encrypt and decrypt message using an AES256 key.
4. Create a key pair and sign using an RSA1024 key pair.
5. Export a key from Data Security Manager wrapped by a wrapping key.
6. Encrypt and decrypt file using an AES256 key.
7. Passing user defined meta data for logging purposes while encrypting/decrypting messages using an AES256 key.

To use these files, the user must have the Vormetric key agent properly installed and registered with a Data Security Manager. 
Optionally set the environment variable VPKCS11LIBPATH point to the library
file. 

e.g. in Linux .bash_profile: 
VPKCS11LIBPATH=/opt/vormetric/DataSecurityExpert/agent/pkcs11/lib/libvorpkcs11.so
export VPKCS11LIBPATH

Details about the command line parameters:
-p pin       #  the password user selected when registering  the PKCS11 library to the DSM after installation.
-k keyname   #  the name of the key
-m module    #  the path to the Vormetric PKCS11 library: libvorpkcs11.so
-f file	     #  the filename [relative or absolute] to be processed

example: 
vpkcs11_sample_create_key -p Password -k TestKey -m /opt/vormetric/DataSecurityExpert/agent/pkcs11/lib/libvorpkcs11.so

File: vpkcs11_sample_create_key.c
Usage: vpkcs11_sample_create_key -p pin -k keyName [-m module]
This file demonstrates the following:
1. Initialization.
2. Creating a connection and logging in.
3. Creating a key on the Data Security Manager.
4. Clean up.

File: vpkcs11_sample_create_object.c
Usage: vpkcs11_sample_create_object -p pin -k keyName [-m module]
This file demonstrates the following:
1. Initialization.
2. Creating a connection and logging in.
3. Creating a key object on the Data Security Manager.
4. Clean up.

File: vpkcs11_sample_find_delete_key.c
Usage: vpkcs11_sample_find_delete_key -p pin -k keyName [-m module]
This file is designed to be run after vpkcs11_sample_create_key and  
demonstrates the following:
1. Initialization.
2. Creating a connection and logging in.
3. Querying for a key using the key name.
4. Deleting the key that was found.
5. Clean up.:
 

File: vpkcs11_sample_encrypt_decrypt.c
Usage: vpkcs11_sample_encrypt_decrypt  -p pin -k keyName [-m module] [-o operation] ([-f "inputtokenfile path"] [-c "char set (ascending)"])
This file demonstrates the following:
1. Initialization.
2. Creating a connection and logging in.
3. Creating a symmetric key on the Data Security Manager.
4. Using the symmetric key to encrypt plain text or token (FPE) in different mode.
5. Using the symmetric key to decrypt cipher text or token (FPE) in corresponding mode.
6. Delete key.
7. Clean up.

File: vpkcs11_sample_en_decrypt_multipart.c
Usage: vpkcs11_sample_en_decrypt_multipart -p pin -k keyName -f filename [-m module]
This file demonstrates the following:
1. Initialization.
2. Creating a connection and logging in.
3. Creating a symmetric key on the Data Security Manager.
4. Using the symmetric key to encrypt the content of the file, and save the encrypted content into a file named "encryptedtext.dat".
5. Using the symmetric key to decrypt the content of "encryptedtext.dat" and save the decrypted content into a file name "decryptedtext.dat".
6. Compare the content of original source file with content from "decryptedtext.dat", should be the same.
7. Delete key.
8. Clean up.

File: vpkcs11_sample_keypair_create_sign.c
Usage: vpkcs11_sample_keypair_create_sign -p pin -k keyName[-m module]
This file demonstrates the following:
1. Initialization.
2. Creating a connection and logging in.
3. Creating a key pair on the Data Security Manager. 
4. Signing a piece of data with the created key pair.
5. Delete the key pair.
6. Clean up.

File: vpkcs11_sample_find_export_key.c
Usage: vpkcs11_sample_find_export_key  -p pin -k keyName -w wrappingKeyName [-m module]
This file demonstrates the following:
1. Initialization
2. Creating a connection and logging in.
3. Find a source key on the Data Security Manager.
4. Find a wrapping key on the Data Security Manager.
5. Wrap the source key with the wrapping key by calling C_WrapKey function. 
8. Save the wrapped key value to a binary file.
9. Clean up.

File: vpkcs11_sample_metadata_logging.c
Usage: vpkcs11_sample_metadata_logging -p pin -k keyName [-m module]
This file demonstrates the following:
1. Initialization.
2. Creating a connection and logging in.
3. Finding an existing symmetric key on the Data Security Manager.
4. Creating a symmetric key on the Data Security Manager if one doesn't exist.
5. Passing in user defined metadata while using the key created to encrypt plain text;
   metadata will be logged and uploaded depending on logging level.
6. Passing in user defined metadata while using the key created to decrypt cipher text;
   metadata will be logged and uploaded depending on logging level.
7. Search and Delete key.
8. Clean up.

File: vpkcs11_sample_helper.c
This file has helper functions shared by other .c files

Compilation:
To compile the sample c files on Linux, simply type 'make'
:wq!

TIP: 

If special characters like exclamation point('!'), dollar sign ('$') or dash
('-) are used inside the PIN, when running the sample on Linux/Unix shell
prompt, Escape character backslash ('\') must be used in front of those characters
to prevent shell from expanding the string after. 
e.g. if PIN = '!123Admin', on Linux/Unix shell you should run sample like
following: 
./vpkcs11_sample_create_key -p \!123Admin -k testKeyName


