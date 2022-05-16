/*
 * KMIPGetAttributes.c	
 *
 * Sample code is provided for educational purposes
 * No warranty of any kind, either expressed or implied by fact or law
 * Use of this item is not restricted by copyright or license terms
 *
 * Sample code for KMIP GetAttributes Operation. 
 * 
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "cadp_capi.h"
#include "KMIPMisc.h"

void usage()
{
   fprintf (stderr, "Usage: KMIPGetCustomAttribute conf_file <keyname> <attr name> <index>\n");
   fprintf (stderr, "Index is optional\n");
   exit(1);
}

I_KS_Result GetAttributes(I_O_Session *handle_p, I_T_CHAR *keyname, char *attrname, int index)
{
    I_KO_AttributeList attrList = NULL;
    char *name_p = NULL;
    I_KS_Result result;
    I_KS_UniqueIdentifiers *uids_p = NULL;
    char *attributes = NULL;
    unsigned int i=0;
    I_KS_Attribute **attr_pp = NULL;
    I_T_UINT count = 0;

    result.status = I_KT_ResultStatus_Success;
    result.reason = I_KT_ResultReason_NoError;

    if((NULL == keyname))
    {
      result.status = I_KT_ResultStatus_OperationFailed;
      return result;
    }
    
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

            //Use Locate to find UniqueID.
            addName(attrList, keyname, NULL);
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
                return result;
            }
            else
            {
                I_KC_ClearAttributeList(attrList);
                addUniqueIdentifier(attrList, uids_p->uniqueIdentifiers_pp[0]);
            }

        printAttrList(attrList, KMIP_REQUEST);

        //I_KS_Attribute attribute;

        attributes = malloc(strlen(attrname)+1);
        strcpy(attributes, attrname);
        result = I_KC_GetAttributes(*handle_p, attrList, (const char**)&attributes, 1);

        if (result.status != I_KT_ResultStatus_Success)
        {
            printf("I_KC_GetAttributes failed Status:%s Reason:%s\n",
                    I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
            break;
        }
        else
        {

            result = I_KC_RetrieveFromAttributeList(attrList, NULL, &attr_pp, &count);
            if(count <= index+1)
            {
               printf("No such index exists \n");
               return result;            
            } 
            if (result.status == I_KT_ResultStatus_Success)
            {
                printf("----Response Attribute List----\n");
                for (i = 0; i < count; i++)
                {
                        if (!strcmp( attr_pp[i]->attributeName,attrname) &&(index == -1)||(i == index+1)) 
                        {
                          printf("Attribute Name : %25s | Index : %3d | Value : ", attr_pp[i]->attributeName, attr_pp[i]->attributeValue.index);
                          printAttributeValue(attr_pp[i]);
                        } 
                }
                I_C_Free(attr_pp);
            }
        }
        free(attributes);
    } while (0);

    if (uids_p != NULL)
        I_KC_FreeUniqueIdentifiers(uids_p);
    if ((attrList != NULL)||(i > count))
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
    char *attrname = NULL; 
    int index = -1;

    if (argc < 4)
        usage(); // exit

    argp = 1;
    path = argv[argp++];
    name = argv[argp++];
    attrname = argv[argp++];  
    if (argc == 5)
    index = atoi(argv[argp]);

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

    result = GetAttributes(&sess,name,attrname,index);
    if (result.status != I_KT_ResultStatus_Success)
    {
        printf("GetAttributes failed Status:%s Reason:%s\n",
                I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
    }
    else
        printf("\nGetAttributes Successful");

    I_C_CloseSession(sess);
    I_C_Fini();
    return rc;
}
