# **Sample code for CADP Vaultless Tokenization**

# **Overview**

The CADP Vaultless Tokenization is a data tokenization application written in Java language to generate tokens of plaintexts without storing it in any vault. These samples are used for tokenization/detokenization feature for single, bulk, batch, multithreaded etc.

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

* CADP for JAVA should be installed and configured.
* JDK(Mininum java 8 is required) must be available in the system to compile and run the samples. 


