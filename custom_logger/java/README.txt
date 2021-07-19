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
 
For more information on cutom/external logger, refer to the CADP JCE User Guide.

Note: 1) Before using these java files ,compile these samples using javac compiler.
      2) Required CADP JCE jars should be present in the java classpath.

Overview:

File: JavaUtilLogger.java

JavaUtilLogger provides custom logging implementation of IngrianLogging using java logging framework.It provides implementation of IngrianLogService interface.
User can configure the file and console handler's properties in the file, log.properties. 
It will create the log file in the current working directory .


File: CustomLoggerSample.java
Usage: java CustomLoggerSample user password keyname

This sample shows how to create the message authentication code and how to verify it using CADP JCE Custom Logger configuration .
Note: JavaUtilLogger class provides the custom logging and CustomLoggerSample class will use these custom configurations to log the messages in the log file.

