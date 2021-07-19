/*************************************************************************
**                                                                      **
** Sample code is provided for educational purposes.                    **
** No warranty of any kind, either expressed or implied by fact or law. **
** Use of this item is not restricted by copyright or license terms.    **
**                                                                      **
**************************************************************************/


Prerequisites: 

All the Java samples are compiled and tested using JDK version 1.8.0_111 .

To use these sample files, the user must have the CADP JCE WebService(protectappws.war) properly installed and configured.
It assumes that server is running on localhost on port 8080. 

For more information on WebService, refer to the CADP JCE WebService User Guide.

Note: 1)Before using these java files ,compile these samples using javac compiler.
      2)CADP JCE jars and protectappwsClientStub.jar must be present in the classpath.


Overview:

SOAP_WebService_Samples:

File: CertImportExportSample.java
Usage: java CertImportExportSample user password fileName certName certIsDeletable certIsExportable
This sample shows how to use different certificate operations: import and export certificate. Use the sample certificate 
(cert.pkcs8) file from cert_samples.

File: KeyImportExportSample.java
Usage: java KeyImportExportSample user password keyname algo keyBytes isDeletable isexportable
This samples shows how to import and export the key to Key Manager through SOAP web service.

File: Session_EncryptSample.java
Usage: java Session_EncryptSample user password keyname plaintext [transformation] [key_iv]
This sample shows how to encrypt a data using a SOAP stateful web service.

File: Session_FPEEncryptSample.java
Usage: java Session_FPEEncryptSample user password keyname plaintext tweakData [tweakAlgo] [keyIv]
Note: If optional attributes are used then both must be specified.
This sample shows how to encrypt a data using a FPE SOAP stateful web service.

File: Session_GetAllUsersInfo.java
Usage: java Session_GetAllUsersInfo user password
This sample shows the information of all users using a SOAP stateful web service.

File: Session_HMACSample.java
Usage: java Session_HMACSample user password keyname messageText
This sample shows how to calculate hmac of data using a SOAP stateful web service.

File: Session_RSASample.java
Usage: java Session_RSASample user password keyname messageText transformation
This sample shows how to sign and verify data using RSA.


REST_WebService_Samples:

File: Restful_EncryptSample.java
Usage: java Restful_EncryptSample user password keyname plaintext [transformation] [key_iv]
This sample shows how to encrypt a data using a restful web service.
