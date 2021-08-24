# Tomcat Servlet Sample Code for Java

##Contents

- Overview
- System Requirements
- Prerequisites
- Configuring the Servlet 
- Running the Servlet
- Running the Servlet with Java Security Manager
- Stopping the Servlet


##Overview

This servlet allows you to *encrypt* and *decrypt* a "**Hello servlet**" string.
It prompts the user to enter *NAE username, password, and key name* and verifies that these values exist on Key Manager. 
It *encrypts* and *decrypts* the string, and then *displays* the registered JCE providers.


##System Requirements

- [Apache Ant](http://ant.apache.org)
- [Apache Tomcat](http://tomcat.apache.org) 
- CADP JCE
- JDK 1.8 or higher


##Prerequisites

To use this sample, ensure that the following conditions are met:

1. **CADP JCE** must be installed. You can use the *CryptoTool* utility to verify the installation.
   
2. NAE User and Key must be created on Key Manager. 



##Configuring the Servlet

To configure servlet:

1. Modify the following parameters in *build.xml* file:

 	**catalina.home** - specify the location of Apache Tomcat home directory.

	**ingrian.home**-  specify the location of **CADP JCE** related jar files and IngrianNAE.properties file.

 	**java.location** - specify the location of the Java.

	**java.compiler**- specify the Java compiler version.

2. Add the following lines to the tomcat *conf/tomcat-users.xml* file:

	    <role rolename="manager-script"/>
    	<user username="tomcat" password="tomcat" roles="manager-script"/>
	
3. Run the "**ant dist**" command to build the war file. This creates a dist directory in parallel to the src directory
   and place the sample.war file in it. By default, **CADP JCE** related jar files and IngrianNAE.properties file are copied to the WEB-INF/lib folder. 
   
    **Note:** If you don’t want these jars to be included in the WEB-INF/lib folder of sample.war file, please do the following 
   and run "**ant dist**" command again to build the war file:

	a) Comment out the following lines in *build.xml* and place these jars in the Java classpath of Tomcat server (set *CLASSPATH*=<%path%> in setenv.bat file of the tomcat bin folder).
	
	     <copy todir="${build.home}/WEB-INF/lib" file="${log4j.jar}"/>
  	     <copy todir="${build.home}/WEB-INF/lib" file="${log4japi.jar}"/>
  	     <copy todir="${build.home}/WEB-INF/lib" file="${commonscollections.jar}"/>
  	     <copy todir="${build.home}/WEB-INF/lib" file="${commonslang.jar}"/>
  	     <copy todir="${build.home}/WEB-INF/lib" file="${guava.jar}"/>
	     <copy todir="${build.home}/WEB-INF/lib" file="${gson.jar}"/>
         <copy todir="${build.home}/WEB-INF/lib" file="${IngrianNAE.jar}"/>
         <copy todir="${build.home}/WEB-INF/lib" file="${IngrianNAE.properties}"/>
	
	 b) Comment out the following listener from the web/WEB-INF/web.xml file.
	 
         <listener>  
    	 <listener-class>
           mypackage.listener.HelloListener
    	 </listener-class>
    	 </listener> 



##Running the Servlet


To run the servlet:

1. Start the Tomcat server.

      On Windows machines, run:
   *$CATALINA_HOME\bin\startup.bat*         

      On Unix machines, run:
   *$CATALINA_HOME/bin/startup.sh*          

2. Use a browser to verify if Tomcat is running on URL http://localhost:8080   

3. Run the "**ant install**" command to deploy the sample. The sample servlet will be
   available at:  *http://localhost:8080/sample/Hello*



##Running the Servlet with Java Security Manager

 


To run the Tomcat servlet using Java security manager:

1. Update the *catalina.policy* file with the following lines. This includes required permissions to run the "sample" servlet application.

        grant codeBase "file:${catalina.home}/webapps/sample/-" {

        // Socket Permission to connect. Like for Key Manager, Syslog etc. Specify your IP and Port.
        permission java.net.SocketPermission "<IP:Port>", "connect";

	    // Runtime Permission
	    permission java.lang.RuntimePermission "getenv.*";
	    permission java.lang.RuntimePermission "getClassLoader";
	    permission java.lang.RuntimePermission "accessClassInPackage.org.apache.*";
	    permission java.lang.RuntimePermission "accessClassInPackage.sun.reflect";
	    permission java.lang.RuntimePermission "accessDeclaredMembers";
	    permission java.lang.RuntimePermission "modifyThread";

	    // Property Permission
	    permission java.util.PropertyPermission "*", "read,write";

	    // File Permission. Like for log file, persistent cache, Keystore etc.
        permission java.io.FilePermission "C:${file.separator}Users${file.separator}JCESampleUser${file.separator}Logs${file.separator}*", "read,write";
	    permission java.io.FilePermission "C:${file.separator}Users${file.separator}JCESampleUser${file.separator}Logs", "read,write";

	    //Security Permission for Ingrian Provider
	    permission java.security.SecurityPermission "putProviderProperty.IngrianProvider";
	    permission java.security.SecurityPermission "insertProvider.IngrianProvider";
	    permission java.security.SecurityPermission "removeProvider.IngrianProvider";

	    //Reflect Permission
	    permission java.lang.reflect.ReflectPermission "suppressAccessChecks";	
	     };
	
     **NOTE:** Given permissions in this sample are for reference only. You can configure permissions as per your application's setup. 

2. Grant below permission under default permissions given for all applications:

	    permission java.security.SecurityPermission "removeProvider.IngrianProvider";
    
3. Start Tomcat, with the **-security** option:

     On Windows machines, run:
   *$CATALINA_HOME\bin\startup.bat -security*

     On Unix machines, run:
   *$CATALINA_HOME/bin/startup.sh -security*	 

4. Use a browser to verify if Tomcat is running on URL*http://localhost:8080*
      
5. Run the "**ant install**" command to deploy the sample. The sample servlet will be
   available at: *http://localhost:8080/sample/Hello*


##Stopping the Servlet


To undeploy the sample, run "**ant remove**" command.

To shut down Tomcat:

   On Windows machines, run: 
  *$CATALINA_HOME\bin\shutdown.bat* 
     
   On Unix machines, run 
  *$CATALINA_HOME/bin/shutdown.sh*        

##More Information

For more information on *CADP JCE* and *CryptoTool*, refer to the *CADP JCE User Guide*.

For more information on Security Manager, click on the link: [Security Manager](https://tomcat.apache.org/tomcat-7.0-doc/security-manager-howto.html)