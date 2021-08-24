# Sample Code for Java

## Overview:

**File:** *KMIPBatchSample.java*

*`Usage: java KMIPBatchSample clientCertAlias keyStorePassword keyName`*

**Note:** *keyName* is the base name for the keys.

This sample demonstrates the *KMIP Batch Session* feature of **CADP JCE** . This sample shows how to *create, manipulate and delete*
keys using a KMIP Batch Session.

**File:** *KMIPCertificateSample.java*

*`Usage: java KMIPCertificateSample clientCertAlias keyStorePassword certName`*

This sample shows how to :

- *register* an **NAECertificate** managed object on the Key Manager over *KMIP*.
- *export* an **NAECertificate** managed object from the Key Manager over *KMIP*.

**File:** *KMIPCertLocateSample.java*

*`Usage: java KMIPCertLocateSample clientCertAlias keyStorePassword certName`*

This sample shows how to:

- locate certificates matching specified *KMIP* attribute criteria.
- find the managed object's name and type of object from the server.

**File:** *KMIPCreateAndEncryptSample.java*

*`Usage: java KMIPCreateAndEncryptSample clientCertAlias keyStorePassword NAEUserName NAEpassword keyName`*

This sample shows how to create a *Symmetric key* using *KMIP* via **CADP JCE** and then use that new key to encrypt data.

**File:** *KMIPCreateSymmetricKeySample.java*

*`Usage: java KMIPCreateSymmetricKeySample clientCertAlias keyStorePassword keyName`*

This sample shows how to create a *Symmetric key* using *KMIP*. The key created will be a 256-bit **AES** Symmetric Key with the given name.

**File:** *KMIPDatesAndStatesSample.java*

*`Usage: java KMIPDatesAndStatesSample clientCertAlias keyStorePassword keyName`*

This sample demonstrates *KMIP managed object lifecycle* using the *KMIP* State attribute and associated date attributes.

**File:** *KMIPDeleteAttributeSample.java*

*`Usage: java KMIPDeleteAttributeSample clientCertAlias keyStorePassword`*

This sample program uses the *KMIP Locate* operation to get a set of *unique identifiers* for server managed keys with attribtues matching
a specified set of properties.

**File:** *KMIPDiscoverVersionSample.java*

*`Usage: java KMIPDiscoverVersionSample clientCertAlias keyStorePassword`*

This sample is used to identify *KMIP Protocol versions* supported on Key Manager.

**File:** *KMIPEncryptAndDecrypt.java*

*`Usage: java KMIPEncryptAndDecrypt certAlias certPassword keyName tagLength iv data`*

This sample demonstrates *KMIP encryption and decryption* in *remote* mode in *KMIP* session. This sample shows *crypto* operation using the **GCM** algorithm. 
User can also use other algorithms such as *AES with CBC/EBC mode and PKCS5Padding/NoPadding* .

**File:** *KMIPGenKeys.java*

*`Usage: java KMIPGenKeys clientCertAlias keyStorePassword keyName length`*

This sample shows how to request the Key Manager to generate a *public/private* **RSA** key pair using the *KMIP Create Key Pair* operation.

**File:** *KMIPGetCustomAttribute.java*

*`Usage: java KMIPGetCustomAttribute clientCertAlias keyStorePassword keyname customAttribute1#customAttribute2#customAttribute3`*

This sample shows how to *locate* keys matching a particular criteria and access the values of the supplied custom *KMIP* attributes.
It will only work for ***RSA-2048*** keys. In this sample we are fetching only *user's defined custom attribute* of key using *KMIP* session.

**File:** *KMIPgetDateRangeSample.java*

*`Usage: java KMIPgetDateRangeSample clientCertAlias keyStorePassword startDate endDate`* 

**Note:** Specify the dates in this format ***MM.dd.yyyy***.

This sample shows how to *find all* **RSA** keys with an initial date between a given set of start and end dates.
This shows how to *locate* keys matching a particular criteria and access the values of all supported *non-custom KMIP* attributes.

**File:** *KMIPGetSample.java*

*`Usage: java KMIPGetSample clientCertAlias keyStorePassword`*

This sample shows how to *locate* keys matching a particular criteria and access the values of all *standard (non-custom) KMIP* attributes.

**File:** *KMIPKeyPairSample.java*

*`Usage: java KMIPKeyPairSample clientCertAlias keyStorePassword privateKeyName publicKeyName`*

This sample shows how to generate *asymmetric public/private* key pairs on the client and then register the keys on the Key Manager via *KMIP*. 
The keys are generated and registered as **RSA-2048**.

**File:** *KMIPLocateSample.java*

*`Usage: java KMIPLocateSample clientCertAlias keyStorePassword [-Name KeyName]`*

This sample shows how to *locate* keys matching a specified *KMIP* Attribute criteria,find the managed object's name and 
type of object and then to *export* the key material associated with the managed object from the server.

**File:** *KMIPModifySample.java*

*`Usage: java KMIPModifySample clientCertAlias keyStorePassword`*

This sample shows how to *locate* a key using *KMIP* and *modify* a standard *KMIP* attribute.

**File:** *KMIPQuerySample.java*

*`Usage: java KMIPQuerySample clientCertAlias keyStorePassword`*

This sample shows how to use *KMIP Query* Operation. Query results are requested by specifying a *List* collection of Query enum values for the query
information to be returned from the Key Manager.

**File:** *KMIPSecretDataGetCustomAttributeSample.java*

*`Usage: java KMIPSecretDataGetCustomAttributeSample clientCertAlias ClientcertPassword secretDataName customAttribute`*

This sample shows how to get *Secret data's custom attribute object* from the Key Manager.

**File:** *KMIPSecretDataSample.java*

*`Usage: java KMIPSecretDataSample clientCertAlias keyStorePassword [keyName]`*

This sample shows how to *register* and *export* a KMIPSecretData managed object to and from the Key Manager.

**File:** *KMIPWrapUnwrapSample.java*

*`Usage: java KMIPWrapUnwrapSample clientCertAlias keyStorePassword wrapping_keyname wrapped_keyname`*

This sample is used to test *Key Wrap/Unwrap* functionality using *KMIP*.

## Prerequisites: 

All the Java samples are compiled and tested using ***JDK version 1.8.0_111*** .

To use these sample files, user must have

- **CADP JCE** installed and configured.
- A ***javac*** compiler to compile the samples.
- ***CADP JCE Jar*** files in the java classpath.
    

## More Information

For more information on *KMIP* samples, refer to the *CADP JCE User Guide*.

