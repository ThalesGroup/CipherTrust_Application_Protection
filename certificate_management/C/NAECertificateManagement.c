/*
 * NAECertificateManagement.c 
 *
 * Sample code is provided for educational purposes
 * No warranty of any kind, either expressed or implied by fact or law
 * Use of this item is not restricted by copyright or license terms
 *
 * This sample shows how to use different certificate operations:
 * import and export certificate and its private key (if present);
 * export CA certificate and certificate chain. The imported
 * certificates must be in either PKCS#1, PKCS#8, or PKCS#12 format.
 * If encrypted, PKCS#12 certificates must be encrypted with 3DES.
 *
 * Included with this sample code are three sample certificates:
 * cert.pkcs1, cert.pkcs8, and cert.pkcs12. These sample certificates 
 * and CA are present in Certificates directory parallel to sample
 * directory. To use those samples, you must first install the 
 * signing CA (sample_ca) to your Key Manager and then add that CA 
 * to Trusted CA List used by the Key Server. The password for 
 * cert.pkcs12 is asdf1234. 
 * Further instructions can be found in the CADP-CAPI User Guide.
 *       
 * These sample certificates are included as a convenience. You can 
 * also use your own certificates. 
 *
 */


#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "cadp_capi.h"

void usage_csr(void)
{
    fprintf(stderr, "\n  usage: usage: NAECertificateManagement conf_file user passwd OPERATION keyName  commonName  CAName  CertificateUsage CertificateExpiry \n"
            "\n  conf_file - typically, CADP_CAPI.properties\n"
            "  user - NAE user.\n"
            "  passwd - NAE user's password.\n"
	    "  OPERATION - IMPORT To import the Certificate on Key Manager.\n"
            "            - CSR To Create and Sign the Certificate on Key Manager. \n"
            "  keyName - key name for an existing asymmetric key on Key Manager.\n"
	    "  commonName - Contains the common name for the certificate.\n"
	    "  modify the sample that contain the structure for other Certificate parameters.\n"
	    "  CAName - Contains the name of the Certificate Authority (CA) that signs the certificate. This must be an existing Local CA on the Key Manager.\n"
	    "  CertificateUsage - Indicates whether the certificate is used for a Client, the Server, or an Intermediate CA.\n"
	    "                     0 to Client \n"
	    "                     1 to Server \n"
	    "                     2 to Intermediate CA n"
	    "  CertificateExpiry - Contains the certificate expiry time in days.\n"
            "  countryNAME - countryName is mandatory parameter for CSR create Request.Sample internally send the country name.\n"
            );
    exit(1);
}

void usage_import(void)
{
        //fprintf(stderr, "usage: NAECertificateManagement conf_file fileName certName pkcs12Password  user passwd\n"
    fprintf(stderr, "\n  usage: NAECertificateManagement conf_file user passwd OPERATION  fileName certName pkcs12Password  \n"
        "\n  conf_file - typically, CADP_CAPI.properties\n"
        "  user - (optional NAE user) user can be in a root domain or in a specific domain. For domain user, specify domain||username.\n"
	"  passwd - optional (mandatory if user is specified) NAE user's password.\n"
	"  OPERATION - IMPORT To import the Certificate on Key Manager.\n"
        "            - CSR To Create and Sign the Certificate on Key Manager.\n"
        "  fileName - File/Certificate name with absolute path to be imported on Key Manager.\n"
        "  certName - Name of imported certificate created on Key Manager.\n"
        "  pkcs12Password - Password for PKCS#12 format certificate. It can be null if cert data is in PKCS#1 or PKCS#8 format.It is Required for Import Operation.\n"
    );
    exit(1);
}

void usage(void)
{
    //fprintf(stderr, "usage: NAECertificateManagement conf_file fileName certName pkcs12Password  user passwd\n"
      fprintf(stderr, "\n  usage: NAECertificateManagement conf_file user passwd OPERATION \n"
        "\n  conf_file - typically, CADP_CAPI.properties\n"
        "  user - (optional NAE user) user can be in a root domain or in a specific domain. For domain user, specify domain||username\n"
	"  passwd - optional (mandatory if user is specified) NAE user's password.\n"
	"  OPERATION - IMPORT fileName certName pkcs12Password\n"
        "            - CSR  keyName  commonName  CAName  CertificateUsage CertificateExpiry \n"
	"  For import provide the below mentioned parameters after operation.\n"
        "  fileName - File/Certificate name with absolute path to be imported on Key Manager\n"
        "  certName - Name of imported certificate created on Key Manager.\n"
        "  pkcs12Password - Password for PKCS#12 format certificate. It can be null if cert data is in PKCS#1 or PKCS#8 format.\n"
        "                   It is Required for Import Operation.\n"
	"  FOR CSR Utility provide the below mentioned parameters after operation parameter.\n"
        "  keyName - key name for an existing asymmetric key on Key Manager. \n"
        "  commonName - Contains the common name for the certificate.\n"
	"  modify the sample that contain the structure for other optional Certificate parameters.\n"
        "  CAName - Contains the name of the Certificate Authority (CA) that signs the certificate.This must be an existing Local CA on the Key Manager.\n"
        "  CertificateUsage - Indicates whether the certificate is used for a Client, the Server, or an Intermediate CA.\n"
	"                     0 to Client.\n"
        "                     1 to Server.\n"
	"                     2 to Intermediate CA.\n"
	"  CertificateExpiry - Contains the certificate expiry time in days\n"
        "  countryNAME - countryName is mandatory parameter for CSR create Request.Sample internally send the country name.\n"
	);
    exit(1);
}

void makeupper(char *p)
{
    for (; *p != '\0'; p++)
        *p = toupper(*p);
}


int main(int argc, char **argv)
{

    I_O_Session sess = NULL; 
    char *path = NULL, *user = NULL, *pass = NULL , *fileName = NULL, *certName = NULL, *pkcs12Password = NULL, *keyName = NULL, *commonName = NULL, *CAName = NULL;
    char *data = NULL, *dataSize =0, *buffer = NULL, *cert = NULL, *certSign = NULL, *operation = NULL;
    unsigned int argp = 0, ivlen = 0, indatalen = 0, certificateUsage = 0,certificateExpiry = 0 ;
    FILE *fp;
    long lSize;
    I_T_RETURN rc = I_E_OK;
    int size = 0, len =0, signlen = 0, i=0;
    I_T_CertificateDetails *certInfo = NULL;
    do
    {
	if (argc < 5)
	usage(); // exit
	argp = 1;
	path  = argv[argp++];
	user = argv[argp++];
	pass = argv[argp++]; 
	operation = argv[argp++];
	makeupper(operation);
        if(strcmp(operation, "IMPORT") == 0)
 	{
            if (argc >= 5)
	    {
	        if (argc < 8)
		    usage_import();
		    fileName = argv[argp++];
		    certName = argv[argp++];
		    if(strncmp(argv[argp],"null",4) != 0)
		        pkcs12Password = (I_T_BYTE*)argv[argp];
            }
            fp = fopen ( fileName, "rb" );
	    if( !fp ) 
	    {
	        fprintf(stderr,"Cert file %s not present \n",fileName);
		 break;
            }
            fseek( fp , 0L , SEEK_END);
	    lSize = ftell( fp );
	    rewind( fp );

	    /* allocate memory for entire content */
	    buffer = calloc( 1, lSize+1 );
	    if( !buffer ) 
	    {
	        fclose(fp),
		fprintf(stderr,"Memory alloc fails\n");
		break;
	    }

	    /* copy the file into the buffer */
	    if( 1!=fread( buffer , lSize, 1 , fp) )
	    {  
	        fclose(fp);
		free(buffer);
                buffer = NULL;
		fprintf(stderr,"Not able to read file %s\n",fileName);
		break;
            }

	    /* do your work here, buffer is a string contains the whole text */
            size = lSize;
            fclose(fp);
            }else if(strcmp(operation, "CSR") == 0){
                if (argc >= 5)
		{
	            if (argc < 10)
			usage_csr();
			keyName = argv[argp++];
			commonName = argv[argp++];
			CAName = argv[argp++];
			certificateUsage = atoi(argv[argp++]);
			certificateExpiry = atoi(argv[argp]);
		 }else{
                         usage();
                 }

	    }else{
		printf("InValid Operation");
                break;
	    }
	    rc = I_C_Initialize(I_T_Init_File,path);

	    if (rc != I_E_OK)
	    {
	        fprintf(stderr, "I_C_Initialize error: %s\n",
		         I_C_GetErrorString(rc));
	        break;	
	    }

	    if(user != NULL)
	        rc = I_C_OpenSession(&sess,I_T_Auth_Password,user,pass);
	    else
		rc = I_C_OpenSession(&sess,I_T_Auth_NoPassword,NULL,NULL);

	    if (rc != I_E_OK)
	    {
	        fprintf(stderr, "I_C_OpenSession error: %s\n",
			  I_C_GetErrorString(rc));
		break;
	    }
	    if(strcmp(operation, "IMPORT") == 0){
                rc = I_C_ImportCertificate( sess,certName,1, 1, NULL ,pkcs12Password, buffer, size );
		if (rc != I_E_OK)
		{
		    fprintf(stderr, "I_C_ImportCertificate error: %s\n",
						I_C_GetErrorString(rc));
		    break;
		}
		else
		{
		     fprintf(stdout,"Certificate Imported Successfuly\n");
		}
        	if(buffer){
            	    free(buffer);    
                    buffer = NULL;
                }
	     }else if(strcmp(operation, "CSR") == 0)
	     {
		certInfo = (I_T_CertificateDetails *) calloc(1,sizeof(I_T_CertificateDetails));
		certInfo->organizationName = "thales";
		certInfo->organizationalUnitName = "noida";
		certInfo->locality = "office";
		certInfo->stateProvinceName = "UP";
		/*CountryName is mandatory parameter for I_C_CreateCertificateRequest API.So always pass the struture to this API */
		certInfo->countryName = "IN"; 
		certInfo->emailAddr = "thales@gmail.com";
		certInfo->ipList = NULL;
		certInfo->dnsList = NULL;
		certInfo->ipList = (char **)calloc(3,sizeof(char *));
		for(i=0;i<3;i++)
		{
		    certInfo->ipList[i]=strdup("__insert_ip_address_here___");
		}
		certInfo->dnsList = (char **)calloc(3,sizeof(char *));
		for(i=0;i<3;i++)
		{
		    certInfo->dnsList[i] = strdup("__insert_fqdn_here___");
		}
	      	certInfo->ipLen = 3;
	     	certInfo->dnsLen = 3;
	 	rc = I_C_CreateCertificateRequest( sess ,keyName,commonName,certInfo, &cert , (I_T_UINT *)&len);
		if (rc != I_E_OK)
		{
		     fprintf(stderr, "I_C_CreateCertificateRequest error: %s\n",
		               I_C_GetErrorString(rc));
                     goto cleanup;
	        }
                else
                {
                     fprintf(stdout,"CSR Creation request executed successfuly on Key Manager\n");
                }
		
		rc = I_C_CreateCertificateSignRequest( sess ,CAName, certificateUsage , certificateExpiry , cert ,len ,&certSign , (I_T_UINT *)&signlen);
		if (rc != I_E_OK)
		{
		     fprintf(stderr, "I_C_CreateCertificateSignRequest error: %s\n",
					I_C_GetErrorString(rc));
                     goto cleanup;
		}
		else
                {
                     fprintf(stdout,"CSR Sign request successfuly executed on Key Manager \n");
                }
		cleanup:
		if(cert){
		    //printf("\n Going to delete Certificate Creation output buffer \n");
		     I_C_Free(cert);
		     cert = NULL;
		}
		if(certSign){
		    //printf("\n Going to delete Certificate Sign output buffer \n");
		      I_C_Free(certSign);
		      certSign = NULL;
		}
		if(certInfo){
		    //printf("Going to delete Certificate Option parameter structure \n");
		    if(certInfo->ipList)
		    {
	                for(i = 0 ; i <3 ; i++)
			{
			     if (certInfo->ipList[i]){
		                 free(certInfo->ipList[i]);
				 certInfo->ipList[i] = NULL;
			     }
			}
			free(certInfo->ipList);
                        certInfo->ipList = NULL;
		    }
                    if(certInfo->dnsList){
		        for(i = 0 ; i <3 ; i++)
			{
			    if (certInfo->dnsList[i]){ 
			        free(certInfo->dnsList[i]);
				certInfo->dnsList[i]= NULL;
			    }
			}
                        free(certInfo->dnsList);
                        certInfo->dnsList = NULL;
                    }
                    free(certInfo);
                    certInfo = NULL;
		  }
         }else{
	     printf("InValid Operation");
             break;
	}
    }
    while (0);
    if (sess != NULL)
    I_C_CloseSession(sess);
    if(buffer)
    free(buffer);
    I_C_Fini();
    return rc;

}
