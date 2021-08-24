# Sample Code for Java

## Overview:

**File:** *MultiplePropertyFileSample.java*

*`Usage: java MultiplePropertyFileSample local_config_user local_config_password local_propertyfile_path global_config_user global_config_password keyname`*

This sample provides an overview of *multiple properties files support* on *session* level.In this sample, there are two different sessions. One session 
pointing to one properties file and another is using global properties file.
*Local session* is creating a new key and *export* that key to *global session* using *import/export* APIs. To validate *sharing* between Key Managers,
one sample data will be encrypted with *local session* key and decrypted by the *global session* key.

## Prerequisites: 

All the Java samples are compiled and tested using ***JDK version 1.8.0_111*** .

To use the sample file, user must have

- **CADP JCE** installed and configured.
- A ***javac*** compiler to compile the sample.
- ***CADP JCE Jar*** files in the java classpath.
    

## More Information

For more information on CADP JCE and samples, refer to the *CADP JCE User Guide*.

