This readme file contains the following information:

 - Overview
 - How to Compile Sample Applications
 - Sample Applications
 - Limitations

================================================================================
                            --- :: OVERVIEW :: ---
================================================================================

CADP for C v8.13.0.000 supports Certificate Management using NAE protocol for 
communication with the Key Manager server.

For API details, refer to the NAE Certificate Management API section in the CADP for C
API Guide. To use NAE with CADP for C, you must set the NAE_IP, NAE_Port,
Protocol, and CA_File parameters in the properties file.

Important! Additional parameters can be set for additional features. To use the 
NAE Certificate Management features, the Protocol parameter should be set to ssl.
For details on NAE parameters, refer to "Configuration" page in the  
CADP for C user guide.

================================================================================
              --- :: HOW TO COMPILE SAMPLE APPLICATIONS :: ---
================================================================================

Included with the CADP for C v8.13.0.000 software are sample C/C++ files, the
source code for sample applications that you can use to test your installation. 
To compile the sample application on Windows:

1. Navigate to <installation_Directory> i.e., C:\Program Files\CipherTrust\CADP_for_C\.

2. Copy C directory of samples which is downloded from github.

3. Navigate to <installation_Directory>\C\VC

4. Open the `sample.sln` file in Visual Studio 2010.

5. Select a sample project and build it.


To compile the sample application on Linux:

1. Navigate to <installation_Directory>. For example, 
   consider that <installation_Directory> is /opt/CipherTrust/CADP_for_C/

2. Copy C directory of samples which is downloded from github.

3. Navigate to <installation_Directory>/C/.

4. Run make command.

5. Run a sample with valid arguments.

================================================================================
                        --- :: SAMPLE APPLICATIONS :: ---
================================================================================

Sample applications to demonstrate the use of NAE Certificate Management.

   NAE Certificate Management Sample Application
   =====================================
   The NAE Certificate Management sample application supplied with CADP for C
   is:

    - NAECertificateManagement.c          :     Performs import certificate operation.
                                                Creates a certificate on Key Manager.

================================================================================
                             --- :: LIMITATIONS :: ---
================================================================================

 - ModifyAttribute operation supports limited attributes. Only the String and 
   DateTime attributes are currently supported.

 - Locate operation using wild cards and regular expressions is not supported.

================================================================================