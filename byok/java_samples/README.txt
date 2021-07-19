/*************************************************************************
**                                                                      **
** Sample code is provided for educational purposes.                    **
** No warranty of any kind, either expressed or implied by fact or law. **
** Use of this item is not restricted by copyright or license terms.    **
**                                                                      **
**************************************************************************/


Prerequisites: 

All the Java samples are compiled and tested using JDK version 1.8.0_111 .

To use these sample files, the user must have the CADP JCE properly installed and configured.
 
For more information on CADP JCE, refer to the CADP JCE User Guide .
For detailed information on byok samples and its parameters, refer to CADP JCE BYOK Integration Guide.

Note: 1)Before using this java file ,compile it using javac compiler. 
      2)Required CADP JCE jars should be present in the java classpath.


Overview:

File: ByokSample.java 
Usage: java ByokSample -cloudName [AWS|Salesforce|GoogleCloud] -userName <userName> -password <password> -aesKeyName <aes-256 Key Name> [-publicKeyPath <public key path>] -wrappedKeyPath <wrapped key path> [-wrappingKeyName RSA KeyName] [-outputFormat base64] -wrappingAlgo [SHA1|SHA256|PKCS1.5] [-hash256Path filePath]
Note: The -hash256Path parameter is specific to Salesforce only.

This sample shows how to use the BYOK feature of clouds (AWS|Salesforce|GoogleCloud) with Key Manager and CADP JCE . 
It wraps the AES Key with the specified public key and algorithm and produces the wrapped key which can be used for the encryption/decryption on the cloud.
