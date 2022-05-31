/*
 * KMIPRevoke.c	
 *
 * Sample code is provided for educational purposes
 * No warranty of any kind, either expressed or implied by fact or law
 * Use of this item is not restricted by copyright or license terms
 *
 * Sample code for KMIP revoke operation.
 * 
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "cadp_capi.h"
#include "KMIPMisc.h"

void usage(void)
{
    fprintf(stderr, "usage: KMIPRevoke conf_file uniqueID KeyRevocationCode RevocationMessage \n where : RevocationCode can be \n \
            1 : Unspecified \n \
            2 : KeyCompromise \n \
            3 : CACompromise \n \
            4 : AffiliationChanged \n \
            5 : Superseded \n \
            6 : CessationOperation \n \
            7 : PrivilegeWithdrawn \n ");
    exit(1);
}

int main(int argc, char **argv)
{

    I_O_Session sess;
    I_T_RETURN rc;
    I_KS_Result result;
    int  argp = 0,revocationCode =0;
    char *path = NULL,*uniqueID_p = NULL,*revocationMsg = NULL;
    time_t compromise_Occurence_Date = NULL;

    if (argc < 4)
        usage(); // exit

    argp = 1;
    path = argv[argp++];

    uniqueID_p = argv[argp++];
    revocationCode = atoi(argv[argp++]);  
    if ( revocationCode > 7)
    {
        printf("Invalid revocation code \n");
        return -1; 		
    }    
    if (argc == 5)
        revocationMsg = argv[argp];

    // For compromise revocation code 
    if (revocationCode == I_KT_RevocationReasonCode_KeyCompromise)
        compromise_Occurence_Date = time(NULL)-100;

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

        
     result = I_KC_Revoke(sess,uniqueID_p,revocationCode,revocationMsg,compromise_Occurence_Date);
     if (result.status != I_KT_ResultStatus_Success)
     {
         printf("I_KC_Revoke failed Status:%s Reason:%s\n",
                    I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
         goto error;
     }
     else
         printf("Revoke operation Successful\n");

    error:
    I_C_CloseSession(sess);
    I_C_Fini();
    return rc;

}

