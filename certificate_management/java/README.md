# Sample Code for Certificate Management in Java

## Overview:

### Certificate Types:

Following *certificates* and *CA samples* are available in the **Certificate_Types** directory:

1. cert.pkcs1
1. cert.pkcs8
1. cert.pkcs12
1. sample_ca.crt

## Samples

1. Create a Certificate Signing Request (CSR) and Use it for Signing

This sample first creates a CSR request on the Key Manager with the existing key pair and then uses the CSR data from the Key Manager to get the CSR signed by the CA present on the Key Manager.

* File: 
[*CertCreationAndSignSample.java*](CertCreationAndSignSample.java)

* Usage:
```shell
java CertCreationAndSignSample username password keyname -cn cnName -country countryName -ca caName -expiry expiryTime
```

1. How to Import/Export Certificates

This sample shows how to use different certificate operations:
 
- *Import and export* certificate and its private key (if present)
- *Export* CA certificate and certificate chain.
  
    **Note:** The imported certificates must have any of the following format:  `PKCS#1`, `PKCS#8`, or `PKCS#12`. 
    * File: [*CertSample.java*](CertSample.java)
    * Usage: 
    ```shell
    java CertSample user password fileName certName caName pkcs12Password (pkcs12Password can be null if cert data is in PKCS#1 format)`*
    ```

1. Signing a CSR

    This sample shows how to sign the CSR that is generated using the user's private key pair. In this case, the user has to pass the following details:

    * *CSR*, specify either the complete file path or bytes
    * *CA name* to sign the CSR 
    * *Expiry time*

    After the details are provided, the Key Manager will sign the request and return the signed document.

    * File: [CertSigningSample.java*](CertSigningSample.java*)
    * Usage:
    ```shell 
    java CertSigningSample <userName> <password> -csr <csrFilePath> -ca <caName> -expiry <expiryTime>
    ```


1. Create a Self-Signed Certificate

This sample generates a self-signed certificate with the specified properties such as *KeyUsage*, *Validity*, and *Algorithm* etc. in the *details.properties* file.

* File: [*SelfSignedCertificateUtility.java*](SelfSignedCertificateUtility.java)

* Usage: 
```shell
java SelfSignedCertificateUtility [-user KeyManagerUserName] [-password KeyManagerPassword] -key rsaOrECCKeyName -file details.properties [-certPass certPassword]
```

## Prerequisites: 

All the Java samples are compiled and tested using ***JDK version 1.8.0_111*** .

To use these sample files, user must have

- `CADP JCE` installed and configured.
- A `javac` compiler in path to compile the sample. 
    
## More Information

For more information on CADP JCE and samples, refer to the `CADP JCE User Guide`.


