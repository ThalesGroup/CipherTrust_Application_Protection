# Sample Code for Miscellaneous Topics in Java

## Overview

## Samples

1. Encrypt/Decrypt with AES-GCM

    This sample provides an overview of *multiple properties files support* on a *session* level. 

    In this sample, there are two different sessions. One session pointing to one properties file and another is using global properties file. *Local session* is creating a new key and *export* that key to *global session* using *import/export* APIs. To validate *sharing* between Key Managers, one sample data will be encrypted with *local session* key and decrypted by the *global session* key.

    * File: [*MultiplePropertyFileSample.java*](MultiplePropertyFileSample.java)
    * Usage: 
    ```shell
    java MultiplePropertyFileSample <local_config_user> <local_config_password> <local_propertyfile_path> <global_config_user> <global_config_password> <keyname>
    ```

## Prerequisites: 

All the Java samples are compiled and tested using ***JDK version 1.8.0_111***.

To use these sample files, user must have

- `CADP for JAVA` installed and configured.
- A `javac` compiler in path to compile the sample. 
    
## More Information

For more information on CADP for JAVA and samples, refer to the `CADP for JAVA User Guide`.