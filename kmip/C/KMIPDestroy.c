/*
 * KMIPDestroy.c	  
 *
 * Sample code is provided for educational purposes
 * No warranty of any kind, either expressed or implied by fact or law
 * Use of this item is not restricted by copyright or license terms
 *
 * Sample code for KMIP Destroy Operation. 
 * 
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "cadp_capi.h"
#include "KMIPMisc.h"

void usage(void)
{
    fprintf(stderr, "usage: KMIPDestroy conf_file UniqueID|all\n");
    exit(1);
}

I_KS_Result Destroy(I_O_Session *handle_p, I_T_CHAR *uniqueID_p)
{
    I_KS_Result result;
    I_KO_AttributeList attrList = NULL;
    unsigned int i;
    I_KS_UniqueIdentifiers *uids_p = NULL;

    do
    {
      

        if (strcmp(uniqueID_p, "all") != 0)
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
            printAttrList(attrList, KMIP_REQUEST);

            result = I_KC_Destroy(*handle_p, attrList);
            if (result.status != I_KT_ResultStatus_Success)
            {
                printf("I_KC_Destroy failed Status:%s Reason:%s\n",
                        I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
                break;
            }
            printAttrList(attrList, KMIP_RESPONSE);
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
        }
        else
        {
            unsigned int destroyed = 0;
            unsigned int failed = 0;
			do{
				// create the attribute list
				result = I_KC_CreateAttributeList(&attrList, NULL);
				if (result.status != I_KT_ResultStatus_Success)
				{
					printf("I_KC_CreateAttributeList failed Status:%s Reason:%s\n",
							I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
					break;
				}
				result = I_KC_Locate(*handle_p, I_KT_StorageStatus_Online, attrList, &uids_p, 0);
				if (result.status != I_KT_ResultStatus_Success)
				{
					printf("I_KC_Locate failed Status:%s Reason:%s\n",
							I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
					break;
				}
		
				for (i = 0; i < uids_p->count; i++)
				{
					I_KC_ClearAttributeList(attrList);
					addUniqueIdentifier(attrList, uids_p->uniqueIdentifiers_pp[i]);

					result = I_KC_Destroy(*handle_p, attrList);
					if (result.status != I_KT_ResultStatus_Success)
						failed++;
					else
						destroyed++;

				}
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
				if(!uids_p->count)break;
				
			}while(result.status == I_KT_ResultStatus_Success);
			printf("Total Objects Found : %d,Destroyed %d objects, Failed to destroy %d objects\n", uids_p->count, destroyed, failed);
        }
    } while (0);

    /* Clean up */
    if (uids_p != NULL)
        I_KC_FreeUniqueIdentifiers(uids_p);
    
    return result;
}

int main(int argc, char **argv)
{

    I_O_Session sess;
    char *path;
    int argp;
    char *uniqueID_p;
    I_T_RETURN rc;
    I_KS_Result result;

    if (argc < 3)
        usage(); // exit

    argp = 1;
    path = argv[argp++];
    uniqueID_p = argv[argp++];

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

    result = Destroy(&sess, uniqueID_p);
    if (result.status != I_KT_ResultStatus_Success)
    {
        printf("Destroy failed Status:%s Reason:%s\n",
                I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
    }
    else
        printf("Destroy Successful\n");

    I_C_CloseSession(sess);
    I_C_Fini();
    return rc;
}

