/*
 * KMIPCreate.c	
 *
 * Sample code is provided for educational purposes
 * No warranty of any kind, either expressed or implied by fact or law
 * Use of this item is not restricted by copyright or license terms
 *
 * Sample code for KMIP Create Operation.
 * 
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "cadp_capi.h"
#include "KMIPMisc.h"

void usage(void)
{
    fprintf(stderr, "usage: KMIPCreate conf_file user password [keyname1] [keyname2]\n");
    exit(1);
}

I_KS_Result CreateKey(I_O_Session *handle_p, char *keyname1, char* keyname2)
{
    I_KO_AttributeList attrList = NULL;
    I_KS_Result result;

    do
    {
        // create the attribute list
        result = I_KC_CreateAttributeList(&attrList, NULL);
        if (result.status != I_KT_ResultStatus_Success)
        {
            printf("I_KC_CreateAttributeList failed Status:%s Reason:%s\n",
                    I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
            break;
        }

        addName(attrList, keyname1, keyname2);
        addCryptographicAlgorithm(attrList);
        addCryptographicLength(attrList);
        addObjectGroup(attrList);
        addContactInformation(attrList);
        addCustomAttributes(attrList);
        addCryptographicUsageMask(attrList);

        printAttrList(attrList, KMIP_REQUEST);

        // Create the key
        result = I_KC_Create(*handle_p, attrList, I_KT_ObjectType_SymmetricKey);
        if (result.status != I_KT_ResultStatus_Success)
        {
            printf("I_KC_Create failed Status:%s Reason:%s\n",
                    I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
            break;
        }

        printAttrList(attrList, KMIP_RESPONSE);

    }
    while (0);
    // delete the attribute list
    if (attrList != NULL)
    {
        I_KS_Result result1;
        result1 = I_KC_DeleteAttributeList(attrList);
        if (result1.status != I_KT_ResultStatus_Success)
        {
            printf("I_KC_DeleteAttributeList failed Status:%s Reason:%s\n",
                    I_KC_GetResultStatusString(result1), I_KC_GetResultReasonString(result1));
        }
    }

    return result;
}

int main(int argc, char **argv)
{

    I_O_Session sess;
    char *path, *keyname1 = NULL, *keyname2 = NULL, *user = NULL,*password = NULL;
    int argp;
    I_T_RETURN rc;
    I_KS_Result result;

    if (argc < 4)
        usage(); // exit

    argp = 1;
    path = argv[argp++];

    if(strncmp(argv[argp],"null",4) != 0)
      user = argv[argp];
    argp++;

    if(strncmp(argv[argp],"null",4) != 0)
       password = argv[argp];
    argp++;
    
    if (argc >= 5)
        keyname1 = argv[argp];

    if (argc == 6)
        keyname2 = argv[++argp];

    rc = I_C_Initialize(I_T_Init_File, path);

    if (rc != I_E_OK)
    {
        fprintf(stderr, "I_C_Initialize error: %s\n",
                I_C_GetErrorString(rc));
        return rc;
    }

    rc = I_C_OpenSession(&sess, I_T_Auth_KMIP,user,password);

    if (rc != I_E_OK)
    {
        fprintf(stderr, "I_C_OpenSession error: %s\n",
                I_C_GetErrorString(rc));
        I_C_Fini();
        return rc;
    }

    result = CreateKey(&sess, keyname1, keyname2);
    if (result.status != I_KT_ResultStatus_Success)
    {
        printf("CreateKey failed Status:%s Reason:%s\n",
                I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
    }
    else
        printf("CreateKey Successful\n");

    I_C_CloseSession(sess);
    I_C_Fini();
    return rc;

}

