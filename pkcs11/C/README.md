# CADP_for_C PKCS11 Samples

This readme file contains the following information:

- Overview
- Prerequisites
- How to Compile the Source Code
- How to Run the Code Samples
- CADP for C PKCS11 Library Path (Default Path)
- About pkcs11_sample_helper File

## Overview

CipherTrust Application Data Protection (CADP) for C enables you to integrate your applications with the cryptographic and key-management capabilities of the CipherTrust Manager.

CADP for C PKCS11 enables data encryption at the application level. Applications can use CADP for C PKCS11 to encrypt a column in a database or a field, such as credit card numbers or Social Security numbers. CADP for C PKCS11 can
also be used to encrypt an entire data file or directory. CADP for C PKCS11 APIs support real-time I/O encryption and decryption of “at rest” data and log files. Data is encrypted by adding CADP for C PKCS11 API calls to existing applications.

The APIs in the CADP for C PKCS11 library are a subset of the PKCS #11 specification version 2.40 with a focus on session management, key management, and cryptographic functions. The CADP for C PKCS11 library acts as a bridge between an application written in the PKCS#11 protocol and the CipherTrust Manager. Your application makes calls with the industry standard PKCS11 APIs and the calls are translated to NAE-XML to communicate with the CipherTrust Manager. In addition, the CADP for C PKCS11 library also offers an in-memory key cache for enhanced cryptographic performance.

Note: For details about the CADP for C PKCS11 APIs, refer to the CipherTrust Application Data Protection PKCS11 API Reference Guide. For information about how to install, configure, and upgrade CADP for C, refer to the online CADP for C user documentation at https://thalesdocs.com.

The following samples provide CADP for C PKCS11 code to illustrate the following functionality:

- pkcs11_sample_cli: Provides an interactive way for the user to use the samples through the CLI.
- pkcs11_sample_create_key: Creates an AES key.
- pkcs11_sample_create_object: Creates a random or opaque key object.
- pkcs11_sample_attributes: Creates a symmetric key or asymmetric key pair with custom attributes.
- pkcs11_sample_digest: Computes a digest or HMAC with a given key.
- pkcs11_sample_encrypt_decrypt: Encrypts and decrypts the content. 
- pkcs11_sample_en_decrypt_multipart: Encrypts and decrypts the file content.
- pkcs11_sample_find_delete_key: Finds and deletes an AES key.
- pkcs11_sample_keypair_create_sign: Creates a key pair and signs using an RSA key pair.
- pkcs11_sample_find_export_key: Exports a key from a Key Manager wrapped by a wrapping key.
- pkcs11_sample_sign_verify: Signs and verifies a given message based on a generated symmetric key
- pkcs11_sample_key_states: Creates a key with given key state transition dates or sets key states or key state transition dates for a given key.
- pkcs11_sample_gen_random: Generates a random sequence of bytes.
- pkcs11_sample_getinfo: Provides information regarding PKCS11 library (Cryptoki version, library version).
- pkcs11_sample_import_key: Reads the wrapped bytes from a file provided by the user, and then imports the key with unwrapped bytes. 
- pkcs11_sample_version_find: Creates the version key (if it does not exist) or rotates the key 51 times (if the version key does exist) and then sets all the states as restricted except for the last one. 

## Prerequisites

Before running the CADP for C PKCS11 code samples, install the CADP for C program.

## Downloading CADP for C PKCS11 Source Code Files

Prior to compiling the CADP for C PKCS11 source code, download the C directory from GitHub, which contains the following files:

> - Solution file
> - Project files
> - Source files
> - Header files
> - Makefile

## How to Compile the Source Code

This section provides instructions on how to compile the source code for CADP for C PKCS11 in Windows and in Linux.


### Windows

After compiling the source code for CADP for C PKCS11 in Windows, the following new directories will be created within the VC directory: 
#
    x64\Debug 

The executable files will be added to the Debug directory after the compilation is successfully completed.

To compile the source code in Windows, do the following:

1. Navigate to the 'VC' directory, which is within the C directory.
2. Using Visual Studio, open the PKCS11.sln file.
3. Within the Solution Explorer of Visual Studio, right click on Solution 'PKCS11' and then select Build Solution.  

### Linux

If you have an older gcc or another C compiler, you may need to obtain 
libstdc++.so and possibly libgcc_s.so.

After successfully compiling the source code for CADP for C PKCS11 in Linux, the executables files will be added to the C directory.

To compile the source code in Linux, do the following:

1. Navigate to the 'C' Directory.
2. Run the following command to "clean" the C directory: 
#
    make clean
3. Run the following command to compile the source files: 
#  
    make

## How to Run the Code Samples

This section provides instructions on how to view the sample usage information and run the CADP for C PKCS11 samples in Windows and in Linux. For Linux, additional information is provided on how to set the path of the CADP_PKCS11.properties file through an environment variable (if required).

### Windows

#### Viewing Sample Usage Information

Before running the code samples in Windows, learn how to run a sample by viewing its usage information (if you do not already know how to do so). To view usage information about a given sample, enter the name of the executable sample file from the directory in which the executable files are located. For example:

#
    pkcs11_sample_create_key

The following displays: 

Usage: pkcs11_sample_create_key -p pin -s slotID -k keyName [-i {k|m|u}:identifier] [-g gen_key_action] [-a alias] [-m module] [-ls lifespan] [-ct cached_time] [-z key_size]

where:

- -g : gen_key_action: 0, 1, 2, or 3.  versionCreate: 0, versionRotate: 1, versionMigrate: 2, nonVersionCreate: 3
- -ls : lifespan: how many days until next version will be automatically rotated(created); template with lifespan will be versioned key automatically.
- -ct : cached_time: cached time in minutes for the key
- -z : key size for symmetric key in bytes.
- -i : identifier: one of 'imported key id' as 'k', MUID as 'm', or UUID as 'u'.
>> Note : The typical use case for the '-i' option is in conjunction with the '-g 1' or '-g 2' options (rotate key or migrate key, respectively).
>> Note: Version migrate key i.e '-g 2' option is not supported.

#### Running Code Samples

To run a code sample:

1. Go to the directory in which the executable files are located.
2. Enter the name of the executable sample file including the required arguments and then press Enter. For example:

#
      pkcs11_sample_create_key -p username:password -k testkey1 

### Linux:

#### Providing Path through an Environment Variable

If the CADP for C PKCS11 properties file (CADP_PKCS11.properties) is not within the following default directory:

#
    /opt/CipherTrust/CADP_for_C/

or this file is not placed in the same directory where the CADP for C PKCS11 library is located, then you are required to set the path of this file through the environment variable (NAE_Properties_Conf_Filename) using the export command. You must take this step before running the code samples. 

To set the path through the Environment variable (NAE_Properties_Conf_Filename) using the export command: 

#
    export NAE_Properties_Conf_Filename=/sampledir/CipherTrust/CADP_for_C/CADP_PKCS11.properties
   
where sampledir is the directory in which this properties file resides.

#### Viewing Sample Usage Information

Before running the code samples in Linux, learn how to run a sample by viewing its usage information (if you do not already know how to do so). To view usage information about a given sample, enter the name of the executable sample file from the directory in which the executable files are located. For example:

#
    ./pkcs11_sample_create_key 

The following displays: 

Usage: pkcs11_sample_create_key -p pin -s slotID -k keyName [-i {k|m|u}:identifier] [-g gen_key_action] [-a alias] [-m module] [-ls lifespan] [-ct cached_time] [-z key_size]

where:

- -g : gen_key_action: 0, 1, 2, or 3.  versionCreate: 0, versionRotate: 1, versionMigrate: 2, nonVersionCreate: 3
- -ls : lifespan: how many days until next version will be automatically rotated(created); template with lifespan will be versioned key automatically.
- -ct : cached_time: cached time in minutes for the key
- -z : key size for symmetric key in bytes.
- -i :  identifier: one of 'imported key id' as 'k', MUID as 'm', or UUID as 'u'.
>> Note: The typical use case for the '-i' option is in conjunction with the '-g 1' or '-g 2' options (rotate key or migrate key, respectively).
>> Note: Version migrate key i.e '-g 2' option is not supported.

#### Running Code Samples

To run a code sample:

1. Go to the directory in which the executable files are placed.
2. Enter the name of the executable sample file including the required arguments and then press Enter. For example: 

#
    ./pkcs11_sample_create_key -p username:password -k testkey1

## CADP for C PKCS11 Library Path (Default Path)

The default path for the CADP for C PKCS11 library in Windows is the following:

    C:\Program Files\CipherTrust\CADP_for_C\libcadp_pkcs11.dll

The default path for the CADP for C PKCS11 library in Linux is the following:

    /opt/CipherTrust/CADP_for_C/libcadp_pkcs11.so

## About pkcs11_sample_helper File

The pkcs11_sample_helper.c file contains the following:

- global settings
- pkcs11 library path
- helper functions shared by other .c files

You can modify the PKCS11 library path in pkcs11_sample_helper.c file based on your platform.


