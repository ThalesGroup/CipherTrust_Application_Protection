
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
- vpkcs11_sample_create_key: Create an AES256 key.
- vpkcs11_sample_create_object: Create a random or opaque key object
- vpkcs11_sample_attributes: Creating a symmetric key or asymmetric key pair with custom attributes 
- vpkcs11_sample_digest: Compute a digest or HMAC with a given key
- vpkcs11_sample_encrypt_decrypt: Encrypt and Decrypt a file content 
- vpkcs11_sample_en_decrypt_multipart: Encrypt and Decrypt a file content with metadata logging
- vpkcs11_sample_find_delete_key: Find and delete an AES256 key.
- vpkcs11_sample_keypair_create_sign: Create a key pair and sign using an RSA1024 key pair.
- vpkcs11_sample_find_export_key: Export a key from Data Security Manager wrapped by a wrapping key.
- vpkcs11_sample_sign_verify: Sign and verify a given message based on a generated symmetric key
- vpkcs11_sample_enc_dec_multipart_filemeta:  Passing user defined meta data for logging purposes while encrypting/decrypting messages using an AES256 key.
- vpkcs11_sample_key_states: Create a key with given key state transition dates; sets key states, or key state transition dates for a given key
- vpkcs11_sample_gen_random: Generates a random sequence of bytes
- vpkcs11_sample_renew_cert: Renew the client-side public key certificate if expired

To use these files, the user must have the Vormetric key agent properly installed and registered with a Data Security Manager. 
Optionally set the environment variable VPKCS11LIBPATH point to the library
file. 

e.g. in Linux .bash_profile: 
VPKCS11LIBPATH=/opt/vormetric/DataSecurityExpert/agent/pkcs11/lib/libvorpkcs11.so
export VPKCS11LIBPATH

Details about the command line parameters:
-p pin       #  the password user selected when registering  the PKCS11 library to the DSM after installation.
-k keyname   #  the name of the key
-g gen_key_action # 0, 1, 2, or 3.  versionCreate: 0, versionRotate: 1, versionMigrate: 2, nonVersionCreate: 3
-i key identifier # one of 'imported key id' as 'k', MUID as 'm', or UUID as 'u'.
-ls lifespan #  how many days until next version will be automatically rotated(created), template with lifespan will be versioned key automatically.
-ct cache_time # key cache time in minutes
-z key_size  #  key size in bytes
-a key_alias #  key alias to be used in the template, can be multiple attributes
-m module    #  the path to the Vormetric PKCS11 library: libvorpkcs11.so
-f file	     #  the filename [relative or absolute] to be processed

example: 
vpkcs11_sample_create_key -p Password -k TestKey -m /opt/vormetric/DataSecurityExpert/agent/pkcs11/lib/libvorpkcs11.so

/*****************************************************************************/
File: vpkcs11_sample_attributes.c
Usage: vpkcs11_sample_attributes -p pin -s slotID [-k keyName] [-P keyPairName]
[-i {k|m|u}:identifier] [-a alias] [-g gen_key_action] [-1 customAttribute1] 
[-2 customAttribute2] [-3 customAttribute3] [-4 customAttribute4] 
[-5 customAttribute5] [-c] [-d] [-l lifespan] [-z] [-m module]

This file demonstrates the following:
1. Initialization.
2. Creating a connection and logging in.
3. Creating a symmetric key or asymmetric keypair with custom attributes on the Data Security Manager
4. If Key already exists, setting specific key attributes 
5. Retrieving and printing out the key attributes
6. Clean up.

/*****************************************************************************/
File: vpkcs11_sample_create_key.c
Usage: vpkcs11_sample_create_key -p pin -s slotID -k keyName [-i
{k|m|u}:identifier] [-g gen_key_action] [-m module] [-ls lifespan]
gen_key_action: 0, 1, 2, or 3.  versionCreate: 0, versionRotate: 1,
versionMigrate: 2, nonVersionCreate: 3
lifespan: how many days until next version will be automatically
rotated(created); template with lifespan will be versioned key
automatically.identifier: one of 'imported key id' as 'k', MUID as 'm',
or UUID as 'u'. Note: The typical use case for the '-i' option is in conjuction 
with the '-g 1' or '-g 2' options (rotate key or migrate key, respectively)

This file demonstrates the following:
1. Initialization.
2. Creating a connection and logging in.
3. Creating a key on the Data Security Manager.
4. Clean up.


/*****************************************************************************/
File: vpkcs11_sample_create_object.c
Usage: vpkcs11_sample_create_object -p pin -s slotID {-k keyName | -o opaqueObjectName} [-v keyVersion] [-m module] [-f binarykeyfile] [-K keyID] [-U UUID] [-M MUID]
If -K, -U, and/or -M are specified along with -k or -o, this simulates a 'key import' scenario where the key must have a specific key ID, UUID, and/or MUID

This file demonstrates the following:
1. Initialization.
2. Creating a connection and logging in.
3. Creating and registering a key object or an opaque object on the Data Security Manager.
4. Clean up.

/*****************************************************************************/
File: vpkcs11_sample_digest.c
Usage: vpkcs11_sample_digest -p pin [-s slotID] [-g gen_key_action]
[-K] [-k keyName] [-a alias] [-m module_path] [-o operation] [-f input_file_name]
[-d digest_file_name] [-q opaque_object_file] operation ...SHA256 (default) or 
	SHA224 or SHA384 or SHA512 or SHA1  or MD5 or MD5-HMAC or SHA1-HMAC or
	SHA224-HMAC or SHA256-HMAC or SHA384-HMAC or SHA512-HMAC 
-K ...create a key with well-known key bytes on the DSM (HMAC functions only)

This file demonstrates the following:
1. Initialization
2. Creating a connection and logging in.
3. Creating a symmetric key on the Data Security Manager for MAC'ing
4. Compute the digest of HMAC for a given message
5. Clean up.

/*****************************************************************************/
File: vpkcs11_sample_find_delete_key.c
Usage: vpkcs11_sample_find_delete_key -p pin -k keyName [-m module]
This file is designed to be run after vpkcs11_sample_create_key and  
demonstrates the following:
1. Initialization.
2. Creating a connection and logging in.
3. Querying for a key using the key name.
4. Deleting the key that was found.
5. Clean up.:

/*****************************************************************************/
File: vpkcs11_sample_encrypt_decrypt.c
Usage: vpkcs11_sample_encrypt_decrypt -p pin [-s slotID] -k keyName 
	[-i {k|m|u}:identifier] [-g gen_key_action] [-a alias] [-m module_path] 
	[-o operation] [-f input_file_name] [-iv iv_in_hex] ([-c charset_for_fpe_mode]
	|[-l literal_charset_filename_for_fpe_mode]|[-r ranged_charset_filename_for_fpe_mode]) 
	[-d decrypted_file_name] [-e encrypted_file_name] [-u charsettype] [-h header_version] [-n]
  identifier: one of 'imported key id' as 'k', MUID as 'm', or UUID as 'u'.
  operation...CBC_PAD (default) or CTR or ECB or FPE or FF1
  charsettype...ASCII or UTF8 or UTF16LE or UTF16BE or UTF32LE or UTF32BE (for FPE or FF1 only)
  header_version...v1.5 or v1.5base64 or v2.1 or v.2.7
  -n...noencryption - decrypt only. Useful for decrypting a file
  -a alias...in case the key doesn't exist yet, an alias can be used for key creation. 
Looking up an existing key by means of an alias is not supported in this sample program.

This file demonstrates the following:
1. Initialization
2. Creating a connection and logging in.
3. Creating a symmetric key on the Data Security Manager
4. Using the symmetric key to encrypt plaintext
5. Using the symmetric key to decrypt ciphertext.
6, Delete key.
7. Clean up.

/*****************************************************************************/
File: vpkcs11_sample_en_decrypt_multipart.c
Usage: vpkcs11_sample_en_decrypt_multipart -p pin -s slotID -k keyName 
[-i {k|m|u}:identifier] -f filename [-g gen_key_action] [-a alias] [-m module]
[-o operation] [-h header_version]
  operation...CBC_PAD (default) or CTR or ECB or CBC
  header_version...v1.5 or v2.1 or v.2.7
  identifier: one of 'imported key id' as 'k', MUID as 'm', or UUID as 'u'.
This file demonstrates the following:
1. Initialization
2. Creating a connection and logging in.
3. Find or Create the symmetric key
4. Using the symmetric key to encrypt file content
5. Using the symmetric key to decrypt the encrypted file content.
6. Compare the original and decrypted file content.
7. Clean up.

/*****************************************************************************/
File: vpkcs11_sample_find_delete_key.c
Usage: vpkcs11_sample_find_delete_key -p pin -s slotID -k keyName 
[-i {k|m|u}:identifier] [-m module]

This file is designed to be run after vorpkcs11_create_key_sample and
demonstrates the following:
1. Initialization
2. Creating a connection and logging in.
3. Querying for a key using the keyname.
4. Deleting the key that was found.
5. Clean up.

/*****************************************************************************/
File: vpkcs11_sample_keypair_create_sign.c
Usage: vpkcs11_sample_keypair_create_sign -p pin -k keyName[-m module]
This file demonstrates the following:
1. Initialization.
2. Creating a connection and logging in.
3. Creating a key pair on the Data Security Manager. 
4. Signing a piece of data with the created key pair.
5. Delete the key pair.
6. Clean up.

/*****************************************************************************/
File: vpkcs11_sample_find_export_key.c
Usage: vpkcs11_sample_find_export_key -p pin -s slotID -k keyName 
[-i {k|m|u}:identifier] -w wrappingKeyName [-m module]

This file demonstrates the following:
1. Initialization
2. Creating a connection and logging in.
3. Find a source key on the Data Security Manager.
4. Find a wrapping key on the Data Security Manager.
5. Wrap the source key with the wrapping key by calling C_WrapKey function. 
8. Save the wrapped key value to a binary file.
9. Clean up.

/*****************************************************************************/
File: vpkcs11_sample_gen_random.c
Usage: vpkcs11_sample_create_object -p pin -s slotID -d seed_material -z random_data_size [-m module]
This file demonstrates the following
1. Initialization
2. Creating a connection and logging in.
3. Seeding and Generating a random sequence of bytes.
4. Clean up.

/*****************************************************************************/
File: vpkcs11_sample_key_states.c

Usage: vpkcs11_sample_key_states -p pin -s slotID -k[p] keyName 
	[-i {k|m|u}:identifier] [-ks key_state] [-m module] [ -d{c|t|a|s|d|p|r} |ps|pt 
key_transition_date ] identifier: one of 'imported key id' as 'k', MUID as 'm', or UUID as 'u'.
key_state: PREACTIVATED...0, ACTIVATED...1, SUSPENDED...2, DEACTIVATED...3, COMPROMISED...4, DESTROYED...5
key_transition-date: dc: creation_date; dt: destroy_date; da: activation_date; 
ds: suspend_date; dd: deactivation_date; dp: compromise_date; i
dr: compromise_occurrence_date; ps: process_start_date; pt: protect_stop_date .
key_transition_date: can be in long format or date format, e.g., 1545134551 or 2017/10/30.
  

This file demonstrates the following
1. Initialization
2. Creating a connection and logging in.
3. Tries to find a symmetric key on the DSM
4. If the key didn't exist, create it with key dates attached
5. If the key already existed, modify the key state and/or key dates.
6. Clean up.

/*****************************************************************************/
File: vpkcs11_sample_metadata_logging.c
Usage: vpkcs11_sample_metadata_logging -p pin -s slotID -k keyName 
[-i {k|m|u}:identifier] [-g gen_key_action] [-a alias] [-m module]
identifier: one of 'imported key id' as 'k', MUID as 'm', or UUID as 'u'.
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

/*****************************************************************************/
File: vpkcs11_sample_renew_cert.c
This file call C_Initialize() for certificate renewal. This sample
is to be used as a cron job when an application using the pkcs11
library does not have persmission to renew the agent certificate
before it expires. The steps involved are:

1. Initialization
2. Clean up.

/*****************************************************************************/
File: vpkcs11_sample_sign_verify.c
usage: vpkcs11_sample_sign_verify -p pin [-s slotID] [-g gen_key_action] 
[-K] [-k keyName] [-op opaqueobjectname] [-q opaquefilename] [-a alias]
[-m module_path] [-o operation] [-f input_file_name] [-d signature_file_name]
[-h header_version]
operation     ...SHA256 (default) or SHA384 or SHA384-HMAC or SHA512 or 
	SHA512-HMAC or SHA1 or SHA1-HMAC or SHA224 or SHA224-HMAC or SHA256-HMAC
 -K     ...create a key with well-known key bytes on the DSM (HMAC_SHA256 only)
header_version...v2.1 or v.2.7

This file demonstrates the following
1. Initialization
2. Creating a connection and logging in.
3. Creating a symmetric key on the Data Security Manager for MAC'ing
4. Sign and verify using HMAC-SHA mechanisms for a given message
5. Clean up.

/*****************************************************************************/
File: vpkcs11_sample_helper.c
This file has helper functions shared by other .c files

Compilation:
To compile the sample c files on Linux, simply type 'make'

TIP: 

If special characters like exclamation point('!'), dollar sign ('$') or dash
('-) are used inside the PIN, when running the sample on Linux/Unix shell
prompt, Escape character backslash ('\') must be used in front of those characters
to prevent shell from expanding the string after. 
e.g. if PIN = '!123Admin', on Linux/Unix shell you should run sample like
following: 
./vpkcs11_sample_create_key -p \!123Admin -k testKeyName


