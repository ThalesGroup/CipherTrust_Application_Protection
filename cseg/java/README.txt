/*************************************************************************
**                                                                      **
** Sample code is provided for educational purposes.                    **
** No warranty of any kind, either expressed or implied by fact or law. **
** Use of this item is not restricted by copyright or license terms.    **
**                                                                      **
**************************************************************************/


Prerequisites: 

All the Java samples are compiled and tested using JDK version 1.8.0_111 .

To use these sample files, the user must have the CADP JCE CSEG WebService(safenetcloud.war) properly installed and configured.
 
For more information on CSEG WebService, refer to the CADP JCE CSEG WebService User Guide.

Note: 1)Before using these java files ,compile these using javac compiler.
      2)To run the samples, download and add the following jars as well as CADP JCE jars into the java classpath  :
	a) httpclient-4.5.1.jar
	b) httpcore-4.4.4.jar
	c) httpmime-4.5.1.jar
	d) commons-logging-1.1.1.jar
	  
Overview:

File: FileUpload.java (Source code file for FileUpload)

Usage: java FileUpload url=webserviceurl awsKey=accessKey awsSecretKey=secretKey bucket=bucketName region=region user=KeyManagerUserName password=KeyManagerPassword key=keyName fileName=filename filepath=filepath [isClientSide=isClientSide] [transformation=transformation] [alias=certalias] [certPassword=certPassword] [canKeyRotate=canKeyRotate]

This sample shows how to upload file to AWS S3 server using Thales cloud web services. In this sample we show how to use using Http Client. 
User can use any other client it wants to. User should take care of the parameters used in this sample. If any other client is used then parameters name should be same.


File: FileDownload.java (Source code file for FileDownload)

Usage: java FileDownload url=webserviceurl awsKey=accessKey awsSecretKey=secretKey bucket=bucketName region=region user=KeyManagerUserName password=KeyManagerPassword key=keyName fileName=filename destination=destinationFile [clientSide=isClientSide] [transformation=transformation] [alias=certalias] [certPassword=certPassword] [version=version]

This sample shows how to download file from AWS S3 server using Thales cloud web services. In this sample we show how to use using Http Client. 
User can use any other client it wants to. User should take care of the parameters used in this sample. If any other client is used then parameters name should be same.


