# Sample Code for Java

## Overview:


**File:** *FileUpload.java* 

*`Usage: java FileUpload url=webserviceurl awsKey=accessKey awsSecretKey=secretKey bucket=bucketName region=region user=KeyManagerUserName password=KeyManagerPassword key=keyName fileName=filename filepath=filepath [isClientSide=isClientSide] [transformation=transformation] [alias=certalias] [certPassword=certPassword] [canKeyRotate=canKeyRotate]`*

This sample shows how to *upload* a file to **AWS S3 Server** using *Thales Cloud Web Services*. In this sample, we demonstrate how to use *Http Client*. 
User can also use any other client. However, user must take care of the parameters used in this sample. If any other client is used, then parameters name should be same.

**File:** *FileDownload.java*

*`Usage: java FileDownload url=webserviceurl awsKey=accessKey awsSecretKey=secretKey bucket=bucketName region=region user=KeyManagerUserName password=KeyManagerPassword key=keyName fileName=filename destination=destinationFile [clientSide=isClientSide] [transformation=transformation] [alias=certalias] [certPassword=certPassword] [version=version]`*

This sample shows how to *download* file from **AWS S3 Server** using *Thales Cloud Web Services*. In this sample, we demonstrate how to use *Http Client*. 
User can also use any other client. However, user must take care of the parameters used in this sample. If any other client is used, then parameters name should be same.

## Prerequisites: 

All the Java samples are compiled and tested using ***JDK version 1.8.0_111*** .

To use these sample files,

- User must have  ***CADP JCE CSEG WebService*** (*safenetcloud.war*) installed and configured.
- A ***javac*** compiler to compile the samples.
- *Download and add* the following **Jar** files along with **CADP JCE Jar** files to the java classpath  :
	- **httpclient-4.5.1.jar**
    - **httpcore-4.4.4.jar**
    - **httpmime-4.5.1.jar**
    - **commons-logging-1.1.1.jar**


## More Information
For more information on CSEG WebService, refer to the *CADP JCE CSEG WebService User Guide*.


