# Sample Code for Key Management Interoperability Protocol (KMIP) in Java

## Overview

## Samples

1. Batch Operations

    This sample demonstrates the *KMIP Batch Session* feature of **CADP JCE** . This sample shows how to *create, manipulate and delete* keys using a KMIP Batch Session.

    * File: [*KMIPBatchSample.java*](KMIPBatchSample.java)
    * Usage: 
    ```shell
    java KMIPBatchSample <clientCertAlias> <keyStorePassword> <keyname>
    ```

    **Note:** *keyName* is the base name for the keys.

1. Register and Export

    This sample shows how to :
    - *register* an **NAECertificate** managed object on the Key Manager over *KMIP*.
    - *export* an **NAECertificate** managed object from the Key Manager over *KMIP*.

    * File: [*KMIPCertificateSample.java*](KMIPCertificateSample.java)
    * Usage: 
    ```shell
    java KMIPCertificateSample <clientCertAlias> <keyStorePassword> <certName> 
    ```

1. Find a Certificate by Name or Attribute

    This sample shows how to:
    - locate certificates matching specified *KMIP* attribute criteria.
    - find the managed object's name and type of object from the server.

    * File: [*KMIPCertLocateSample.java*](KMIPCertLocateSample.java)
    * Usage: 
    ```shell
    java KMIPCertLocateSample <clientCertAlias> <keyStorePassword> <certName> 
    ```

1. Create and use a Symmetric Key with KMIP

    This sample shows how to create a *Symmetric key* using *KMIP* via **CADP JCE** and then use that new key to encrypt data.

    * File: [*KMIPCreateAndEncryptSample.java*](KMIPCreateAndEncryptSample.java)
    * Usage: 
    ```shell
    java KMIPCreateAndEncryptSample <clientCertAlias> <keyStorePassword> <username> <password> <keyname>
    ```

1. Create and use an AES Key with KMIP

    This sample shows how to create a *Symmetric key* using *KMIP*. The key created will be a 256-bit **AES** Symmetric Key with the given name.
    
    * File: [*KMIPCreateSymmetricKeySample.java*](KMIPCreateSymmetricKeySample.java)
    * Usage: 
    ```shell
    java KMIPCreateSymmetricKeySample <clientCertAlias> <keyStorePassword> <keyname>
    ```

1. Manage the Lifecycle of a Key with KMIP

    This sample demonstrates *KMIP managed object lifecycle* using the *KMIP* State attribute and associated date attributes.

    * File: [*KMIPDatesAndStatesSample.java*](KMIPDatesAndStatesSample.java)
    * Usage: 
    ```shell
    java KMIPDatesAndStatesSample <clientCertAlias> <keyStorePassword> <keyname>
    ```

1. Find a Key based on Attributes

    This sample program uses the *KMIP Locate* operation to get a set of *unique identifiers* for server managed keys with attributes matching a specified set of properties.

    * File: [*KMIPDeleteAttributeSample.java*](KMIPDeleteAttributeSample.java)
    * Usage: 
    ```shell
    java KMIPDeleteAttributeSample <clientCertAlias> <keyStorePassword>
    ```


1. Get Supported Version
    
    This sample is used to identify *KMIP Protocol versions* supported on Key Manager.

    * File: [*KMIPDiscoverVersionSample.java*](KMIPDiscoverVersionSample.java)
    * Usage: 
    ```shell
    java KMIPDiscoverVersionSample <clientCertAlias> <keyStorePassword>
    ```

1. Encrypt/Decrypt in Remote mode with KMIP

    This sample demonstrates *KMIP encryption and decryption* in *remote* mode in *KMIP* session. This sample shows *crypto* operation using the **GCM** algorithm. 
    User can also use other algorithms such as *AES with CBC/EBC mode and PKCS5Padding/NoPadding* .

    * File: [*KMIPEncryptAndDecrypt.java*](KMIPEncryptAndDecrypt.java)
    * Usage: 
    ```shell
    java KMIPEncryptAndDecrypt certAlias certPassword <keyname> tagLength iv data
    ```

1. Generate Public/Private key pairs

    This sample shows how to request the Key Manager to generate a *public/private* **RSA** key pair using the *KMIP Create Key Pair* operation.

    * File: [*KMIPGenKeys.java*](KMIPGenKeys.java)
    * Usage: 
    ```shell
    java KMIPGenKeys <clientCertAlias> <keyStorePassword> <keyname> length
    ```

1. Find a Key based on Standard KMIP Attributes

    This sample shows how to *locate* keys matching a particular criteria and access the values of all *standard (non-custom) KMIP* attributes.

    * File: [*KMIPGetSample.java*](KMIPGetSample.java)
    * Usage: 
    ```shell
    java KMIPGetSample <clientCertAlias> <keyStorePassword>
    ```

1. Find a RSA-2048 Key based on Custom Attributes

    This sample shows how to *locate* keys matching a particular criteria and access the values of the supplied custom *KMIP* attributes.
    It will only work for ***RSA-2048*** keys. In this sample we are fetching only *user's defined custom attribute* of key using *KMIP* session.

    * File: [*KMIPGetCustomAttribute.java*](KMIPGetCustomAttribute.java)
    * Usage: 
    ```shell
    java KMIPGetCustomAttribute <clientCertAlias> <keyStorePassword> <keyname> customAttribute1#customAttribute2#customAttribute3
    ```

1. Find all RSA keys in date range

    This sample shows how to *find all* **RSA** keys with an initial date between a given set of start and end dates.
    This shows how to *locate* keys matching a particular criteria and access the values of all supported *non-custom KMIP* attributes.

    * File: [*KMIPgetDateRangeSample.java*](KMIPgetDateRangeSample.java)
    * Usage: 
    ```shell
    java KMIPgetDateRangeSample <clientCertAlias> <keyStorePassword> startDate endDate
    ``` 

    **Note:** Specify the dates in this format `MM.dd.yyyy`.

1. Generate Public/Private Keys on Client then Register with Key Manager

    This sample shows how to generate *asymmetric public/private* key pairs on the client and then register the keys on the Key Manager via *KMIP*. 
    The keys are generated and registered as **RSA-2048**.

    * File: [*KMIPKeyPairSample.java*](KMIPKeyPairSample.java)
    * Usage: 
    ```shell
    java KMIPKeyPairSample <clientCertAlias> <keyStorePassword> privateKeyName publicKeyName
    ```

1. Find a Key by Attributes

    This sample shows how to *locate* keys matching a specified *KMIP* Attribute criteria,find the managed object's name and type of object and then to *export* the key material associated with the managed object from the server.

    * File: [*KMIPLocateSample.java*](KMIPLocateSample.java)
    * Usage: 
    ```shell
    java KMIPLocateSample <clientCertAlias> <keyStorePassword> [-Name <keyname>]
    ```

1. Modify Standard KMIP Attributes on a Key

    This sample shows how to *locate* a key using *KMIP* and *modify* a standard *KMIP* attribute.

    * File: [*KMIPModifySample.java*](KMIPModifySample.java)
    * Usage: 
    ```shell
    java KMIPModifySample <clientCertAlias> <keyStorePassword>
    ```

1. KMIP Query

    This sample shows how to use *KMIP Query* Operation. Query results are requested by specifying a *List* collection of Query enum values for the query information to be returned from the Key Manager.

    * File: [*KMIPQuerySample.java*](KMIPQuerySample.java)
    * Usage: 
    ```shell
    java KMIPQuerySample <clientCertAlias> <keyStorePassword>
    ```

1. Get Attributes of Secret Data Objects

    This sample shows how to get *Secret data's custom attribute object* from the Key Manager.

    * File: [*KMIPSecretDataGetCustomAttributeSample.java*](KMIPSecretDataGetCustomAttributeSample.java)
    * Usage: 
    ```shell
    java KMIPSecretDataGetCustomAttributeSample <clientCertAlias> ClientcertPassword secretDataName customAttribute
    ```

1. Register and Export KMIP Secret Data Objects

    This sample shows how to *register* and *export* a KMIPSecretData managed object to and from the Key Manager.

    * File: [*KMIPSecretDataSample.java*](KMIPSecretDataSample.java)
    * Usage: 
    ```shell
    java KMIPSecretDataSample <clientCertAlias> <keyStorePassword> [keyName]
    ```

1. Wrap/Unwrap a Key

    This sample shows the *Key Wrap/Unwrap* functionality using *KMIP*.

    * File: [*KMIPWrapUnwrapSample.java*](KMIPWrapUnwrapSample.java)
    * Usage: 
    ```shell
    java KMIPWrapUnwrapSample <clientCertAlias> <keyStorePassword> wrapping_keyname wrapped_keyname
    ```

## Prerequisites: 

All the Java samples are compiled and tested using ***JDK version 1.8.0_111***.

To use these sample files, user must have

- `CADP JCE` installed and configured.
- A `javac` compiler in path to compile the sample. 
    
## More Information

For more information on KMIP samples, refer to the `CADP JCE User Guide`.

