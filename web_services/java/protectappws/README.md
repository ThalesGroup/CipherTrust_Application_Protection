# Sample Code for Java

##Overview:

### SOAP WebService Samples:

**File:** *CertImportExportSample.java*

*`Usage: java CertImportExportSample user password fileName certName certIsDeletable certIsExportable`*

This sample shows how to perform different *certificate operations*: 

- *import* the certificate
-  *export* the certificate. 

**Note:** Use the sample certificate 
(***cert.pkcs8***) from certificate types samples.

**File:** *KeyImportExportSample.java*

*`Usage: java KeyImportExportSample user password keyname algo keyBytes isDeletable isexportable`*

This samples shows how to *import and export* the key from the Key Manager using *SOAP* web service.

**File:** *Session_EncryptSample.java*

*`Usage: java Session_EncryptSample user password keyname plaintext [transformation] [key_iv]`*

This sample shows how to *encrypt* a data using a *SOAP* stateful web service.

**File:** *Session_FPEEncryptSample.java*

*`Usage: java Session_FPEEncryptSample user password keyname plaintext tweakData [tweakAlgo] [keyIv]`*

**Note:** If optional parameters are used, then *both* must be specified.

This sample shows how to *encrypt* a data using a *FPE SOAP* stateful web service.

**File:** *Session_GetAllUsersInfo.java*

*`Usage: java Session_GetAllUsersInfo user password`*

This sample shows the *information of all users* using a *SOAP* stateful web service.

**File:** *Session_HMACSample.java*

*`Usage: java Session_HMACSample user password keyname messageText`*

This sample shows how to *calculate hmac* of data using a *SOAP* stateful web service.

**File:** *Session_RSASample.java*

*`Usage: java Session_RSASample user password keyname messageText transformation`*

This sample shows how to *sign and verify* data using **RSA**.


###REST WebService Samples:

**File:** *Restful_EncryptSample.java*

*`Usage: java Restful_EncryptSample user password keyname plaintext [transformation] [key_iv]`*

This sample shows how to *encrypt* a data using a *restful* web service.

##Prerequisites: 

All the Java samples are compiled and tested using ***JDK version 1.8.0_111*** .

To use these sample files, user must have

- ***CADP JCE WebService*** (*protectappws.war*) installed and configured. We assume that server is running on localhost on port 8080.
- A ***javac*** compiler to compile the samples.
- ***protectappwsClientStub.jar*** and ***CADP JCE Jar*** files in the java classpath.
    

##More Information

For more information on *WebService*, refer to the *CADP JCE WebService User Guide*.

