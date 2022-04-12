# Sample Code for Bring Your Own Key (BYOK) in Java

## Overview

## Samples

1. Wrap key for use with a Cloud Service Provider (CSP)

    This sample shows how to use the *BYOK* feature with a CSP (AWS|Salesforce|GoogleCloud) with the Key Manager and CADP for JAVA. 

    The sample shows how to wrap the AES Key with the specified public key and a specific algorithm. It will produce a wrapped key that can be used for the encryption/decryption in the cloud.

    * File: [*ByokSample.java*](ByokSample.java)
    * Usage:
    ```shell
    java ByokSample -cloudName <AWS|Salesforce|GoogleCloud> -userName <username> -password <password> -aesKeyName <aes-256KeyName> [-publicKeyPath <publicKeyPath>] -wrappedKeyPath <wrappedKeyPath> [-wrappingKeyName <RSAKeyName>] [-outputFormat <base64>] -wrappingAlgo <SHA1|SHA256|PKCS1.5> [-hash256Path <filePath>]
    ```

    **Note:** The -hash256Path parameter is specific to *Salesforce* only.

## Prerequisites: 

All the Java samples are compiled and tested using ***JDK version 1.8.0_111*** .

To use this sample file, user must have

- `CADP for JAVA` installed and configured.
- A `javac` compiler in path to compile the sample. 

## More Information

For more information on CADP for JAVA and samples, refer to the `CADP for JAVA User Guide`.
