# Postgress Custom Database Driver using Thales CADP for Java

Integration showing how to use a postgress database driver to automatically encrypt and decrypt sensitive data 

## Integrations
This example incorporates Thales CADP encrypt and decrypt functions so application developers do not have to write code 
to make separate calls to encrypt and decrypt data.  In this example the email and address will be automatically be decrypted when
ResultSet rs = stmt.executeQuery("SELECT email,address ,city FROM plaintext_protected limit 5"); is executed in a java application. <i>Note. Has not been written to work with UI based tools.<i>  <br>
<b>ThalesCustomPostgressDriver.java</b> - is the custom Thales driver that overrides extends org.postgresql.Driver.  The only method that was modified is createStatement() which calls ThalesCustomStatementWrapper.<br> 
<b>ThalesCustomStatementWrapper.java</b> -  overrides executeQuery which calls ThalesDecryptingResultSetWrapper<br>
<b>ThalesDecryptingResultSetWrapper.java</b> - overrides getString and checks to see if the column in the query is one that is encrypted. If so it will call the ThalesEncryptDecryptService.callDecryptApi class<br>
<b>ThalesEncryptDecryptService.java</b> - makes calls to CADP to encrypt and decrypt data<br>
<b>DataLoadCsvToDB.java</b> - will load a table with encrypted email and address.<br> 
<b>The application.properties</b> - contains parameters needed by the application including the columns that need encryption.<br>
<b>TestThalesCustomPostgressDriver.java</b> - sample code to test the driver.
<b>ThalesExampleWithWrapper.java</b> - sample code to test the wrapper. 
<b>Dependency</b> - code based on - https://github.com/pgjdbc/pgjdbc
<b>Table used as an example</b>  - CREATE TABLE plaintext_protected (custid SMALLINT, name VARCHAR(100) , address VARCHAR(100) , city VARCHAR(100) , state VARCHAR(2) , zip VARCHAR(10) , phone VARCHAR(20) , email VARCHAR(100) , dob TIMESTAMP, creditcard BIGINT, creditcardcode SMALLINT, ssn VARCHAR(11) );

