/*
 * KMIPDiscoverVersion.c  
 *
 * Sample code is provided for educational purposes
 * No warranty of any kind, either expressed or implied by fact or law
 * Use of this item is not restricted by copyright or license terms
 *
 * Sample code for KMIP Discover Version Operation. 
 * 
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "cadp_capi.h"
#include "KMIPMisc.h"

void usage(void)
{
    fprintf(stderr, "usage: KMIPDiscoverVersion conf_file\n");
    exit(1);
}

I_KS_Result DiscoverVersion(I_O_Session *handle_p)
{
    I_KS_SupportedKMIPVersions *supportedKmipVers_p = NULL;
    I_KS_Result result;
    unsigned int i = 0;
    I_T_UINT count = 0;  
    
    //Either Send empty string array to fetches all supported KMIP protocol version
    //supportedClientVers contains the list of KMIP protocols supported by client,
    //it wants to check if the server as well supports
    char **supportedClientVers=NULL;
    //To check if specific versions are supported
    //pass protocol versions ranked in order of preference (highest preference first)also change count variable
    // char *supportedClientVers[]={ "1.1", "1.0"};
    do
    {
        result = I_KC_DiscoverVersion(*handle_p, supportedClientVers, count, &supportedKmipVers_p);
        if (result.status != I_KT_ResultStatus_Success)
        {
            printf("I_KC_DiscoverVersion failed Status:%s Reason:%s\n",
                    I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
            break;
        }

        printf("---- Discover Version Response----\n");
        if (supportedKmipVers_p->count <= 0)
            printf("No client Version Supported ");
        else {
            printf("Supported Versions : \n");
            for (i = 0; i <supportedKmipVers_p->count; i++)
            {
                printf("%s \n",(supportedKmipVers_p->supportedKmipVers_pp)[i]);
            }
        }
        printf("\n");
    } 
    while (0);

  if (supportedKmipVers_p != NULL)
          I_KC_FreeDiscoverVersionResponse(supportedKmipVers_p);

    return result;
}

int main(int argc, char **argv)
{

    I_O_Session sess;
    char *path;
    int argp;
    I_T_RETURN rc;
    I_KS_Result result;

    if (argc < 2)
        usage(); // exit

    argp = 1;
    path = argv[argp++];

    rc = I_C_Initialize(I_T_Init_File, path);

    if (rc != I_E_OK)
    {
        fprintf(stderr, "I_C_Initialize error: %s\n",
                I_C_GetErrorString(rc));
        return rc;
    }

    rc = I_C_OpenSession(&sess, I_T_Auth_NoPassword, NULL, NULL);

    if (rc != I_E_OK)
    {
        fprintf(stderr, "I_C_OpenSession error: %s\n",
                I_C_GetErrorString(rc));
        I_C_Fini();
        return rc;
    }

    result = DiscoverVersion(&sess);
    if (result.status != I_KT_ResultStatus_Success)
    {
        printf("DiscoverVersion failed Status:%s Reason:%s\n",
                I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
    }
    else
        printf("DiscoverVersion Successful\n");
    
    I_C_CloseSession(sess);
    I_C_Fini();
    return rc;

}

