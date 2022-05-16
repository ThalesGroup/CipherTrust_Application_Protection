/*
 * KMIPLocate.c	
 *
 * Sample code is provided for educational purposes
 * No warranty of any kind, either expressed or implied by fact or law
 * Use of this item is not restricted by copyright or license terms
 *
 * Sample code for KMIP Locate Operation 
 * 
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "cadp_capi.h"
#include "KMIPMisc.h"

void usage(void)
{
    fprintf(stderr, "usage: KMIPLocate conf_file [name|all|Link]\n");
    exit(1);
}

I_KS_Result Locate(I_O_Session *handle_p, char *name)
{
    I_KO_AttributeList attrList = NULL;
    I_KS_Result result;
    I_T_UINT i = 0;
    I_KS_UniqueIdentifiers *uniqueIdentifiers_p = NULL;

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
		if (strcmp(name, "Link") == 0)
		{
			addLink(attrList);
			printAttrList(attrList, KMIP_REQUEST);
		}

        else if (strcmp(name, "all") != 0)
        {
            addName(attrList, name, NULL);
            printAttrList(attrList, KMIP_REQUEST);
        }
		
        result = I_KC_Locate(*handle_p, I_KT_StorageStatus_Online, attrList, &uniqueIdentifiers_p, 0);
        if (result.status != I_KT_ResultStatus_Success)
        {
            printf("I_KC_Locate failed Status:%s Reason:%s\n",
                    I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
            break;
        }

        printf("----Locate Response----\n");
        printf("Unique IDs Retrieved : %d \n", uniqueIdentifiers_p->count);

        for (i = 0; i < uniqueIdentifiers_p->count; i++)
        {
            printf("%5d.  %s\n", i + 1, uniqueIdentifiers_p->uniqueIdentifiers_pp[i]);
        }
    } while (0);

    if (uniqueIdentifiers_p != NULL)
        I_KC_FreeUniqueIdentifiers(uniqueIdentifiers_p);

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
    char *path, *name = NULL;
    int argp;
    I_T_RETURN rc;
    I_KS_Result result;

    if (argc < 3)
        usage(); // exit

    argp = 1;
    path = argv[argp++];

    name = argv[argp];

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

    result = Locate(&sess, name);
    if (result.status != I_KT_ResultStatus_Success)
    {
        printf("Locate failed Status:%s Reason:%s\n",
                I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
    }
    else
        printf("Locate Successful\n");

    I_C_CloseSession(sess);
    I_C_Fini();
    return rc;

}

