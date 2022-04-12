# Sample code for CADP Vaultless Tokenization

## **Overview**
---
The CADP Vaultless Tokenization is a data tokenization framework written in Java to generate tokens from plaintext without using vault. These samples are used for tokenization/detokenization feature for single, bulk, batch, multithreaded etc.
---
## **Samples**

1. Vaultless tokenization sample in multithreaded mode

	This sample shows how to use CADP Vaultless Tokenization in multithreaded environment using batch.

     * File: [*VaultLessMultiThreadSample.java*](VaultLessMultiThreadSample.java)
    * **Usage**:
    ```shell
    java VaultLessMultiThreadSample naeUser naePswd keyName numberofThreads batchSize
    ```
2. Vaultless tokenization sample for single and batch

    This sample shows how to use CADP Vaultless Tokenization for single and batch mode.

     * File: [*TokenServiceVaultlessSample.java*](TokenServiceVaultlessSample.java)
    * **Usage**:
    ```shell
    java TokenServiceVaultlessSample naeuser naepassword keyname dataToEncrypt
    ```

    > CADP Vaultless Tokenization performs the bulk tokenization/detokenization operations based on the configurations set in the migration.properties and detokenization.properties files located in [*bulkutility*](bulkutility) folder categorized by Input type.

---
## **Prerequisites**:

* Java version should be 7, 8, 10, or 11.
* Download the encryption policy files for unlimited strength ciphers (US_export_policy.jar and
local_policy.jar) and install them in JRE_HOME/lib/security when using Java version 7 or 8.

> For Sun/Oracle or IBM Java, download corresponding version of the Java Cryptography
Extension (JCE) Unlimited Strength Jurisdiction Policy Files.


