# Sample Code for Java

##Overview:

**File:** *JavaUtilLogger.java*

*JavaUtilLogger* provides custom logging implementation of IngrianLogging using the java logging framework.It provides implementation of the *IngrianLogService* interface.
User can configure the file and console handler's properties in the *log.properties* file. 
It will create a log file in the current working directory.


**File:** *CustomLoggerSample.java*

*`Usage: java CustomLoggerSample user password keyname`*

This sample shows how to create a *Message Authentication Code(MAC)* and how to *verify* it using the **CADP JCE Custom Logging** configurations.

**Note:** *JavaUtilLogger* class provides the custom logging configurations. The *CustomLoggerSample* class will use these custom configurations to log the messages in the log file or on the console.


##Prerequisites: 

All the Java samples are compiled and tested using ***JDK version 1.8.0_111*** .

To use these sample files, user must have

- **CADP JCE** installed and configured.
- A ***javac*** compiler to compile the samples.
- ***CADP JCE Jar*** files in the java classpath.
    

##More Information

For more information on *custom/external logger*, refer to the *CADP JCE User Guide*.

