/*
 * KMIPAddAttribute.c	
 *
 * Sample code is provided for educational purposes
 * No warranty of any kind, either expressed or implied by fact or law
 * Use of this item is not restricted by copyright or license terms
 *
 * Sample code for KMIP Add Attribute Operation.
 * 
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "cadp_capi.h"
#include "KMIPMisc.h"

void usage(void)
{
    fprintf(stderr, "usage: KMIPAddAttribute conf_file uniqueID\n");
    exit(1);
}


I_KS_Result AddAttribute(I_O_Session *handle_p, I_T_CHAR *uniqueID_p)
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

        addUniqueIdentifier(attrList, uniqueID_p);
        addAttributeObjectGroup(attrList);

        printAttrList(attrList, KMIP_REQUEST);

        // Add Attribute.
        result = I_KC_AddAttribute(*handle_p, attrList);
        if (result.status != I_KT_ResultStatus_Success)
        {
            printf("I_KC_AddAttribute failed Status:%s Reason:%s\n",
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
    char *path;
    int argp;
    I_T_RETURN rc;
    I_KS_Result result;
    char *uniqueID_p = NULL;

    if (argc < 3)
        usage(); // exit

    argp = 1;
    path = argv[argp++];

	uniqueID_p = argv[argp];

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

    result = AddAttribute(&sess, uniqueID_p);
    if (result.status != I_KT_ResultStatus_Success)
    {
        printf("AddAttribute failed Status:%s Reason:%s\n",
                I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
    }
    else
        printf("AddAttribute Successful\n");

    I_C_CloseSession(sess);
    I_C_Fini();
    return rc;

}

