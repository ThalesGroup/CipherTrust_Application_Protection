# Sample Code for Java

##Overview:

**File:**  *ECCKeySample.java*

*`Usage: java ECCKeySample user password keyName groupName`*

This sample shows how to perform the following *key operations* using the **ECC** keys:

1. *Create* an ECC key pair with the group permissions. 
1. *Export* public key data.
1. *Export* private key data.
1. *Delete* the key pair from Key Manager.
1. *Import* the key pair back to Key Manager.
1. *Export* private key data in **PEM-PKCS#8** and **PEM-SEC1** format.

**File:** *HKDFSecretKeySample.java*

*`Usage: java HKDFSecretKeySample user password masterKeyName aesKeyName_1 aesKeyName_2 hmacKeyName_1 hmacKeyName_2`*

This sample shows how to create **AES** and **HmacSHA256 key** using Key Derivation Function (**KDF**) based on a Hash-based Message Authentication Code (**HMAC**) using a Master Key 
present on the Key Manager. It illustrates that two keys created using HKDF have the same key data using *Encryption/Decryption* and *MAC/MACVerfiy* operations.

**File:** *IngrianKeySample.java*

*`Usage: java IngrianKeySample user password keyname group`*

This sample shows how to use additional *key features* defined by **CADP JCE**:

1. *Create* an **AES** key with custom attributes 
1. *Add* and *delete* key's custom attributes
1. *Create* a new version of key on Key Manager
1. *Modify* version of key

**File:** *KeyNameSample.java*

*`Usage: java KeyNameSample -user [userName] -password [password] -attr [attributName] -attrV [attributeValue] -fingerprint [fingerprint] -offset [keyOffset] -max [maxKeys]`*

This sample shows how to fetch *owner keys* and *global keys*.

**File:** *KeyPermissionsSample.java*

*`Usage: java KeyPermissionsSample user password keyname group`*

This sample shows the *group permissions* linked to any key.

**File:** *RSAKeySample.java*

*`Usage: java RSAKeySample user password keyname group`*

This sample shows how to use different *key operations* for *asymmetric keys*:

1. *Create* an **RSA** key pair with the group permissions
1. *Export* public key and private key data
1. *Delete* the key pair from Key Manager
1. *Import* the key pair back to Key Manager

**File:** *SecretKeySample.java*

*`Usage: java SecretKeySample user password keyname group`*

This sample shows how to use different *key operations* for *symmetric keys*:

1. *Create* an ***AES*** key 
2. *Export* the key data from the Key Manager
3. *Clone* the key
4. *Delete* the key from Key Manager
5. *Import* the key back to Key Manager

**File:** *WrapKeySample.java*

*`Usage: java WrapKeySample user password keyToWrapName wrappingKeyName groupName`*

This sample shows how to *wrap* a key for exporting from the Key Manager using the **CADP JCE**.

##Prerequisites: 

All the Java samples are compiled and tested using ***JDK version 1.8.0_111*** .

To use these sample files, user must have

- **CADP JCE** installed and configured.
- A ***javac*** compiler to compile the samples.
- ***CADP JCE Jar*** files in the java classpath.
    

##More Information

For more information on CADP JCE and samples, refer to the *CADP JCE User Guide*.

