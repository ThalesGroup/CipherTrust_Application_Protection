# Sample Code for Java


## Overview:

**File :** *ByokSample.java*

*`Usage:
java ByokSample -cloudName [AWS|Salesforce|GoogleCloud] -userName <userName> -password <password> -aesKeyName <aes-256 Key Name> [-publicKeyPath <public key path>] -wrappedKeyPath <wrapped key path> [-wrappingKeyName RSA KeyName] [-outputFormat base64] -wrappingAlgo [SHA1|SHA256|PKCS1.5] [-hash256Path filePath]`*

**Note :** The -hash256Path parameter is specific to `Salesforce` only.

This sample shows how to use the *BYOK* feature of clouds 
(`AWS|Salesforce|GoogleCloud`) with Key Manager and CADP JCE . 
It wraps the AES Key with the specified public key and algorithm and produces a wrapped key that is used for the encryption/decryption on the cloud.

## Prerequisites: 

All the Java samples are compiled and tested using ***JDK version 1.8.0_111*** .

To use this sample file, user must have

- **CADP JCE** installed and configured.

- A ***javac*** compiler to compile the sample. 

- ***CADP JCE Jar*** files in the java classpath.


## More Information

- For more information on CADP JCE, refer to the *CADP JCE User Guide* .
- For detailed information on byok samples and parameters, refer to *CADP JCE BYOK Integration Guide*.
