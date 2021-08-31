# Sample Code for Custom Loggers in Java

## Overview

## Samples

1. Custom Logger

    *JavaUtilLogger* provides custom logging implementation of IngrianLogging using the java logging framework. It provides implementation of the *IngrianLogService* interface.
    User can configure the file and console handler's properties in the *log.properties* file. 
    It will create a log file in the current working directory.

    * File: [*JavaUtilLogger.java*](JavaUtilLogger.java)

1. Using a Custom Logger

    This sample shows how to create a *Message Authentication Code(MAC)* and how to *verify* it using the **CADP JCE Custom Logging** configurations.

    **Note:** *JavaUtilLogger* class provides the custom logging configurations. The *CustomLoggerSample* class will use these custom configurations to log the messages in the log file or on the console.

    * File: [*CustomLoggerSample.java*](CustomLoggerSample.java)
    * Usage: 
    ```shell
    java CustomLoggerSample <username> <password> <keyname>
    ```

## Prerequisites: 

All the Java samples are compiled and tested using ***JDK version 1.8.0_111***.

To use these sample files, user must have

- `CADP JCE` installed and configured.
- A `javac` compiler in path to compile the sample. 
    
## More Information

For more information on custom/external loggers, refer to the `CADP JCE User Guide`.

