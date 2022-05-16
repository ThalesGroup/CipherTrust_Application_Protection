/*
 * KMIPQuery.c	
 *
 * Sample code is provided for educational purposes
 * No warranty of any kind, either expressed or implied by fact or law
 * Use of this item is not restricted by copyright or license terms
 *
 * Sample code for KMIP Query Operation. 
 * 
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "cadp_capi.h"
#include "KMIPMisc.h"

void usage(void)
{
    fprintf(stderr, "usage: KMIPQuery conf_file\n");
    exit(1);
}

I_KS_Result Query(I_O_Session *handle_p)
{
    I_KT_QueryFunction queryFunctions[] = {I_KT_QueryFunction_Operations,
        I_KT_QueryFunction_Objects,
        I_KT_QueryFunction_ServerInformation,
        I_KT_QueryFunction_ApplicationNameSpaces,
        I_KT_QueryFunction_ExtensionList,
        I_KT_QueryFunction_ExtensionMap };
    I_T_UINT count = 6;
    I_KS_QueryResponse *queryResponse_p = NULL;
    I_KS_Result result;
    unsigned int i = 0;
	int j=0;

    do
    {
        result = I_KC_Query(*handle_p, queryFunctions, count, &queryResponse_p);
        if (result.status != I_KT_ResultStatus_Success)
        {
            printf("I_KC_Query failed Status:%s Reason:%s\n",
                    I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
            break;
        }

        printf("----Query Response----\n");

        if (queryResponse_p->operationsCount > 0)
            printf("Operations Supported : ");
        for (i = 0; i < queryResponse_p->operationsCount; i++)
        {
            printOperation(queryResponse_p->operation_p[i]);
        }
        printf("\n");

        if (queryResponse_p->objectTypeCount > 0 )
        printf("ObjectType Supported : ");
        for (i = 0; i < queryResponse_p->objectTypeCount; i++)
        {
            printObjectType(queryResponse_p->objectType_p[i]);
        }
        printf("\n");


        if (queryResponse_p->serverInformationElements_p != NULL &&
                queryResponse_p->serverInformationElements_p->value_s.type == I_KT_Struct)
        {
            printf("Server Information (tag:0x%x): \n", queryResponse_p->serverInformationElements_p->tag);
            for (i = 0; i < queryResponse_p->serverInformationElements_p->value_s.value_u.structVal->nFields; i++)
            {
                printElement(queryResponse_p->serverInformationElements_p->value_s.value_u.structVal->fields[i]);
            }
        }

        if (queryResponse_p->vendorIdentification_p != NULL)
        printf("VendorSpecificInformation : %s\n", queryResponse_p->vendorIdentification_p);

		for (i = 0; i < queryResponse_p->applicationNamespaceCount; i++)
        {
            printf("Application NameSpace :  %s\n", queryResponse_p->applicationNamespace_pp[i]);
        }

        for (i = 0; i < queryResponse_p->extensionListCount; i++){
        
            printf("Extension List (tag:0x%x): \n", queryResponse_p->extensionList_p->fields[i]->tag);
            for (j = 0; j< queryResponse_p->extensionList_p->fields[i]->value_s.value_u.structVal->nFields; j++)
            {
                printElement(queryResponse_p->extensionList_p->fields[i]->value_s.value_u.structVal->fields[j]);
            }
        }
        for (i = 0; i < queryResponse_p->extensionMapCount; i++)
        {
            printf("Extension Map :  %s\n", queryResponse_p->extensionMap_pp[i]);
        }


    } 
	while (0);

        if (queryResponse_p != NULL)
            I_KC_FreeQueryResponse(queryResponse_p);

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

    result = Query(&sess);
    if (result.status != I_KT_ResultStatus_Success)
    {
        printf("Query failed Status:%s Reason:%s\n",
                I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
    }
    else
        printf("Query Successful\n");
    
    I_C_CloseSession(sess);
    I_C_Fini();
    return rc;

}

