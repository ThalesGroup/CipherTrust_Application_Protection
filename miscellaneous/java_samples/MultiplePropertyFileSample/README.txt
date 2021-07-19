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

For more information on CADP JCE and samples, refer to the CADP JCE user guide.

Note: 1) Before using this java file ,compile it using javac compiler.
      2) Required CADP JCE jars should be present in the java classpath.


Overview:

File: MultiplePropertyFileSample.java

Usage: java MultiplePropertyFileSample local_config_user local_config_password local_propertyfile_path global_config_user global_config_password keyname

This sample provide overview of multiple properties files support on session level.In this sample there are two different session where one session 
pointing to different properties file and another is using global property file.
Local session is creating a new key and export that key to global session using import/export apis. To validate sharing between Key Managers,
one sample data was encrypted with local session key and decrypted by global session key.

