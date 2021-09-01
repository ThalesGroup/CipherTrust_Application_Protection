# Sample Code for Key Management Operations in Java

## Overview

## Samples

1. Key Operations on an ECC key

    This sample shows how to perform the following *key operations* using the **ECC** keys:

    1. *Create* an ECC key pair with the group permissions. 
    1. *Export* public key data.
    1. *Export* private key data.
    1. *Delete* the key pair from Key Manager.
    1. *Import* the key pair back to Key Manager.
    1. *Export* private key data in **PEM-PKCS#8** and **PEM-SEC1** format.
    
	* File: [*ECCKeySample.java*](ECCKeySample.java)
	* Usage:
	```shell
    java ECCKeySample <username> <password> <keyname> <groupName>
     ```

1. Creating Derived Keys from Master Key

    This sample shows how to create **AES** and **HmacSHA256 key** using Key Derivation Function (**KDF**) based on a Hash-based Message Authentication Code (**HMAC**) using a Master Key present on the Key Manager. It illustrates that two keys created using HKDF have the same key data using *Encryption/Decryption* and *MAC/MACVerfiy* operations.

    * File: [*HKDFSecretKeySample.java*](HKDFSecretKeySample.java)
    * Usage: 
    ```shell
    java HKDFSecretKeySample <username> <password> <masterKeyName> <aesKeyName_1> <aesKeyName_2> <hmacKeyName_1> <hmacKeyName_2>
    ```

1. Additional Key Features/Attributes

    This sample shows how to use additional *key features* defined by **CADP JCE**:
    1. *Create* an **AES** key with custom attributes 
    1. *Add* and *delete* key's custom attributes
    1. *Create* a new version of key on Key Manager
    1. *Modify* version of key

    * File: [*IngrianKeySample.java*](IngrianKeySample.java)
    * Usage: 
    ```shell
    java IngrianKeySample <username> <password> <keyname> <groupName>
    ```

1. Get Keys of an Owner or Global

    This sample shows how to fetch *owner keys* and *global keys*.

    * File: [*KeyNameSample.java*](KeyNameSample.java)
    * Usage: 
    ```shell
    java <keyname>Sample -user <username> -password <password> -attr <attributeName> -attrV <attributeValue> -fingerprint <fingerprint> -offset <keyOffset> -max <maxKeys>
    ```

1. Get Group Permissions of a Key

    This sample shows the *group permissions* linked to any key.

    * File: [*KeyPermissionsSample.java*](KeyPermissionsSample.java)
    * Usage: 
    ```shell
    java KeyPermissionsSample <username> <password> <keyname> <groupname>
    ```

1. Working with Asymmetric Keys

    This sample shows how to use different *key operations* for *asymmetric keys*:

    1. *Create* an **RSA** key pair with the group permissions
    1. *Export* public key and private key data
    1. *Delete* the key pair from Key Manager
    1. *Import* the key pair back to Key Manager

    * File: [*RSAKeySample.java*](RSAKeySample.java)
    * Usage: 
    ```shell
    java RSAKeySample <username> <password> <keyname> <groupname>
    ```

1. Working with Symmetric Keys

    This sample shows how to use different *key operations* for *symmetric keys*:

    1. *Create* an ***AES*** key 
    2. *Export* the key data from the Key Manager
    1. *Clone* the key
    1. *Delete* the key from Key Manager
    1. *Import* the key back to Key Manager

    * File: [*SecretKeySample.java*](SecretKeySample.java)
    * Usage: 
    ```shell
    java SecretKeySample <username> <password> <keyname> <groupname>
    ```

1. Wrapping a key for exporting from Key Manager

    This sample shows how to *wrap* a key for exporting from the Key Manager using the **CADP JCE**.

    * File: [*WrapKeySample.java*](WrapKeySample.java)
    * Usage: 
    ```shell
    java WrapKeySample <username> <password> <keyname> <wrappingKeyName> <groupname>
    ```

## Prerequisites: 

All the Java samples are compiled and tested using ***JDK version 1.8.0_111***.

To use these sample files, user must have

- `CADP JCE` installed and configured.
- A `javac` compiler in path to compile the sample. 
    
## More Information

For more information on CADP JCE and samples, refer to the `CADP JCE User Guide`.
