# CADP_for_C PKCS11 Samples

## Overview
CADP_for_C PKCS11 samples helps to understand the PKCS11 interface.

## Prerequisites:
In order to run CADP_for_C PKCS11 Samples :
> - CADP for C must be installed.


#### Compilation:
Download C directory from github which contains following :
> - Solution file
> - Project files
> - Source files
> - Header files
> - Makefile

#### For Windows:
     Go to the 'VC' directory, inside C directory where samples are placed
     Open solution in Visual studio
     In Solution Explorer, right click on Solution 'PKCS11' and then click on Build Solution
     New directories(x64\Debug) will created and executables will be created inside this directory
#### For Linux :
    Go to the 'C' Directory where samples are placed and run following make commands for creating executables
    make clean
    make

## Usage:
### For Windows
> - #### Run sample from executable:
pkcs11_sample_create_key -p pin -s slotID -k keyName [-i {k|m|u}:identifier] [-g gen_key_action] [-a alias] [-m module] [-ls lifespan] [-ct cached_time] [-z key_size]
>> - ###### Example
pkcs11_sample_create_key -p username:password -k testkey1

### For Linux
> - #### PKCS11 property file
User can provide CADP_PKCS11.properties path through Environment variable (NAE_Properties_Conf_Filename)
>> - ##### Example
export NAE_Properties_Conf_Filename=/opt/CipherTrust/CADP_for_C/CADP_PKCS11.properties

> - #### Run sample from executable:
pkcs11_sample_create_key -p pin -s slotID -k keyName [-i {k|m|u}:identifier] [-g gen_key_action] [-a alias] [-m module] [-ls lifespan] [-ct cached_time] [-z key_size]

>>> - ##### Example
./pkcs11_sample_create_key -p username:password -k testkey1

Each sample has its own particular functionality, e.g. encryption or signing.
pkcs11_sample_helper.c contains global settings, PKCS11 library path and helper functions, respectively.
## PKCS11 library path(Default path)
### For Windows:
    C:\Program Files\CipherTrust\CADP_for_C\libcadp_pkcs11.dll
### For Linux:
    /opt/CipherTrust/CADP_for_C/libcadp_pkcs11.so

User can modify the PKCS11 library path according to their platform in pkcs11_sample_helper.c file

