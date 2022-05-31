/*
 * KMIPGetAttributeList.c	
 *
 * Sample code is provided for educational purposes
 * No warranty of any kind, either expressed or implied by fact or law
 * Use of this item is not restricted by copyright or license terms
 *
 * Sample code for KMIP GetAttributeList Operation. 
 * 
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "cadp_capi.h"
#include "KMIPMisc.h"

void usage(void)
{
    fprintf(stderr, "usage: KMIPGetAttributeList conf_file uniqueID|-name name\n");
    exit(1);
}

I_KS_Result GetAttributeList(I_O_Session *handle_p, char* uniqueID_p, I_T_CHAR *name)
{
    I_KO_AttributeList attrList = NULL;
    char *name_p = NULL;
	I_T_UINT attributeCount=0;
    I_KS_Result result;
    I_KS_UniqueIdentifiers *uids_p = NULL;
	I_KS_AttributeNameList *attrNameList_p = NULL;
	int iLoop = 0;
	

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

        if (uniqueID_p != NULL)
            addUniqueIdentifier(attrList, uniqueID_p);
        else if (name != NULL)
        {
            //Use Locate to find UniqueID.
            addName(attrList, name, NULL);
            result = I_KC_Locate(*handle_p, I_KT_StorageStatus_Online, attrList, &uids_p, 0);
            if (result.status != I_KT_ResultStatus_Success)
            {
                printf("I_KC_Locate failed Status:%s Reason:%s\n",
                        I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
                break;
            }

            if (uids_p->count == 0)
            {
                printf("No object exist for specified name.\n");
				result.reason = I_KT_ResultReason_ItemNotFound;
				result.status = I_KT_ResultStatus_OperationFailed;
                return result;;
            }
            else
            {
                I_KC_ClearAttributeList(attrList);
                addUniqueIdentifier(attrList, uids_p->uniqueIdentifiers_pp[0]);
            }

        }

        printAttrList(attrList, KMIP_REQUEST);


        result = I_KC_GetAttributesList(*handle_p, attrList,&attrNameList_p);
		if (result.status != I_KT_ResultStatus_Success)
        {
            printf("I_KC_GetAttributeList failed Status:%s Reason:%s\n",
                    I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
            break;
        }
        else
        {
            printAttributeNameList(attrNameList_p);
        }

    } while (0);
	if(attrNameList_p != NULL)
		I_KC_FreeAttributeNameList(attrNameList_p);
	if (uids_p != NULL)
        I_KC_FreeUniqueIdentifiers(uids_p);
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
    char *uniqueID_p = NULL, *name = NULL;
    I_T_RETURN rc;
    I_KS_Result result;

    if (argc < 3)
        usage(); // exit

    argp = 1;
    path = argv[argp++];

    if (argc >= 3)
    {

        if (strcmp(argv[argp], "-name") != 0)
            uniqueID_p = argv[argp];
        else
            name = argv[++argp];
    }

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

    result = GetAttributeList(&sess, uniqueID_p, name);
    if (result.status != I_KT_ResultStatus_Success)
    {
        printf("GetAttributeList failed Status:%s Reason:%s\n",
                I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
    }
    else
        printf("\n GetAttributeList Successful\n");

    I_C_CloseSession(sess);
    I_C_Fini();
    return rc;
}
