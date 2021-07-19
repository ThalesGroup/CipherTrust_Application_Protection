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

For more information on CADP JCE and samples, refer to the CADP JCE user guide.

Note: 1)Before using these java files ,compile these files using javac compiler.
      2)Required CADP JCE jars should be present in the java classpath.

Overview:

Certificate_Types:

Various type of certificates and CA samples are present in this directory :

1) cert.pkcs1
2) cert.pkcs8
3) cert.pkcs12
4) sample_ca.crt


Samples:

File: CertCreationAndSignSample.java
Usage: java CertCreationAndSignSample username password keyname -cn cnName -country countryName -ca caName -expiry expiryTime
This sample will first create a CSR request on the Key Manager with the existing key pair then use CSR data from the Key Manager 
to get it signed by the CA authority present on the Key Manager itself.

File: CertSample.java
Usage: java CertSample user password fileName certName caName pkcs12Password (pkcs12Password can be null if cert data is in PKCS#1 format)
This sample shows how to use different certificate operations:
 1. Import and export certificate and its private key (if present)
 2. Export CA certificate and certificate chain. 
Note: The imported certificates must be in either PKCS#1, PKCS#8, or PKCS#12 format. 
 
File: CertSigningSample.java
Usage: java CertSigningSample userName password -csr csrFilePath -ca caName -expiry expiryTime
This sample shows how to sign the CSR which may be generated using user's private key pair. In this user has to pass the CSR either the
complete file path or bytes, CA name to sign the CSR and the expire time. Once all the necessary inputs are provided Key Manager will 
sign the request and return signed document.


Utility :

File: SelfSignedCertificateUtility.java 
Usage: java SelfSignedCertificateUtility [-user KeyManagerUserName] [-password KeyManagerPassword] -key rsaOrECCKeyName -file details.properties [-certPass certPassword]

This sample generates the self signed certificate with the specified properties (like KeyUsage, Validity, Algorithm etc.) in the details.properties file.




