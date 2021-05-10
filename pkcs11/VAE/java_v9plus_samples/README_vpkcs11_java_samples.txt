
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

1. All the Java samples are compiled and tested using JDK version 11.0.1 on Linux and Windows.

Overview:
The following samples below provide PKCS#11 Java code to demonstrate the following:
1. Encrypt and decrypt file using an AES256 key.
To use these files, the user must have the Vormetric key agent properly installed and registered with a Data Security Manager. 
Optionally set the environment variable VPKCS11LIBPATH point to the library file. 

e.g. in Linux .bash_profile: 
VPKCS11LIBPATH=/opt/vormetric/DataSecurityExpert/agent/pkcs11/lib/libvorpkcs11.so
export VPKCS11LIBPATH

Details about the command line parameters: 
-p pin       #  the password user selected when registering  the PKCS11 library to the DSM after installation.
-m module    #  the path to the Vormetric PKCS11 library : libvorpkcs11.so.


File: EncryptDecryptMessage.java
usage: java [-cp CLASSPATH] com.vormetric.pkcs11.sample.EncryptDecryptMessage -p pin [-k keyName] [-g genAction ] [-m module] [-o operation] CTR or CBC_PAD (default) or FPE or GCM [-f 'inputtokenfile'] ([-c 'char set']|[-r 'charset file']|[-l 'literal charset file']) [-u utf-mode-name] [-d 'decryptedfile'] [-a 'associated data'] [-t tagSize] 
genAction: 0, versioned_key; 1, rotate versioned key; 2, migrate from non-versioned key to versioned key; 3, non-versioned key.

This file demonstrates the following:
1. Initialization.
2. Creating a connection and logging in.
3. Creating a symmetric key on the Data Security Manager.
4. Using the symmetric key to encrypt the input file name and write the encrypted output into "filename.enc".
5. Using the symmetric key to decrypt the "filename.enc" and write the decrypted output into "filename.dec".
6. Compare the original input file name with "filename.dec", should be the same.
7. Clean up.

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

$>java -cp lib/pkcs11-wrapper-{version}.jar;build/classes  com.vormetric.pkcs11.sample.EncryptDecryptMessage -p yourPIN

$>java -cp lib/pkcs11-wrapper-{version}.jar;build/classes  com.vormetric.pkcs11.sample.EncryptDecryptMessage -p yourPIN -m /opt/vormetric/DataSecurityExpert/agent/pkcs11/lib/libvorpkcs11.so

TIP:

If special characters like exclamation point('!'), dollar sign ('$') or dash
('-) are used inside the PIN, when running the sample on Linux/Unix shell
prompt, Escape character backslash ('\') must be used in front of those characters
to prevent shell from expanding the string after.
e.g. if PIN = '!123Admin', on Linux/Unix shell you should run a sample like the
following:
java -cp  lib/pkcs11-wrapper-{version}.jar;build/classes  com.vormetric.pkcs11.sample.EncryptDecryptMessage  -p \!123Admin 


