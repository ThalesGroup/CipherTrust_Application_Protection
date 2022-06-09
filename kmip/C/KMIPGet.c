/*
 * KMIPGet.c	
 *
 * Sample code is provided for educational purposes
 * No warranty of any kind, either expressed or implied by fact or law
 * Use of this item is not restricted by copyright or license terms
 *
 * Sample code for KMIP Get Operation. 
 * 
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "cadp_capi.h"
#include "KMIPMisc.h"

void usage(void)
{
    fprintf(stderr, "usage: KMIPGet conf_file uniqueID|-name name\n");
    exit(1);
}

I_KS_Result Get(I_O_Session *handle_p, I_T_CHAR *uniqueID_p, I_T_CHAR *name, int *keyFlag)
{
    I_KS_Result result;
    I_KO_AttributeList attrList = NULL;
    I_KS_Object* object_p = NULL;
    I_KS_GetRequest getRequest;
    I_T_UINT i;
    I_KS_UniqueIdentifiers *uids_p = NULL;

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
                *keyFlag = 1;
                break;
            }
            else
            {
                I_KC_ClearAttributeList(attrList);
                addUniqueIdentifier(attrList, uids_p->uniqueIdentifiers_pp[0]);
            }

        }

        printAttrList(attrList, KMIP_REQUEST);

        getRequest.keyFormat_t = I_KT_KeyFormat_None;

        result = I_KC_Get(*handle_p, attrList, &getRequest, &object_p);
        if (result.status != I_KT_ResultStatus_Success)
        {
            printf("I_KC_GetAttributes failed Status:%s Reason:%s\n",
                    I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
            break;
        }
        else
        {
            printf("----Get Response----\n");
            switch (object_p->objectType_t)
            {
                case I_KT_ObjectType_SymmetricKey:
                    printf("Object Type : SymmetricKey\n");
                    printf("Key Material Length : %d\n", object_p->object_u.symmetricKey_s.keyBlock_s.keyBytes_s.byteStringLen);
                    printf("Key Material : ");
                    for (i = 0; i < object_p->object_u.symmetricKey_s.keyBlock_s.keyBytes_s.byteStringLen; i++)
                    {
                        printf("%2.2X", object_p->object_u.symmetricKey_s.keyBlock_s.keyBytes_s.byteString_p[i]);
                    }
                    printf("\n");
                    printKeyFormat(object_p->object_u.symmetricKey_s.keyBlock_s.keyFormat_t);
                    break;
                case I_KT_ObjectType_SecretData:
                    printf("Object Type : Secret Data\n");
                    switch (object_p->object_u.secretData_s.secretDataType)
                    {
                        case I_KT_SecretData_None:
                            printf("Secret Data Type: I_KT_SecretData_None\n");
                            break;
                        case I_KT_SecretData_Password:
                            printf("Secret Data Type: I_KT_SecretData_Password\n");
                            break;
                        case I_KT_SecretData_Seed:
                            printf("Secret Data Type: I_KT_SecretData_Seed\n");
                            break;
                        default:
                            printf("Secret Data Type: Invalid or unknown Secret Data Type\n");
                    }
                    printf("Key Material Length : %d\n", object_p->object_u.secretData_s.keyBlock_s.keyBytes_s.byteStringLen);
                    printf("Key Material : ");
                    for (i = 0; i < object_p->object_u.secretData_s.keyBlock_s.keyBytes_s.byteStringLen; i++)
                    {
                        printf("%2.2X", object_p->object_u.secretData_s.keyBlock_s.keyBytes_s.byteString_p[i]);
                    }
                    printf("\n");
                    printKeyFormat(object_p->object_u.secretData_s.keyBlock_s.keyFormat_t);
                    break;
                case I_KT_ObjectType_Template:
                {
                    printf("Object Type : Template\n");
                    printAttrList(attrList, KMIP_RESPONSE);
                }
                    break;
                case I_KT_ObjectType_OpaqueObject:
                    printf("Object Type : OpaqueObject\n");
                    break;
                case I_KT_ObjectType_PublicKey:
                    printf("Object Type : PublicKey\n");
			        printf("Key Material Length : %d\n", object_p->object_u.publicKey_s.keyBlock_s.keyBytes_s.byteStringLen);
                    printf("Key Material : ");
                    for (i = 0; i < object_p->object_u.publicKey_s.keyBlock_s.keyBytes_s.byteStringLen; i++)
                    {
                        printf("%2.2X", object_p->object_u.publicKey_s.keyBlock_s.keyBytes_s.byteString_p[i]);
                    }
                    printf("\n");
                    printKeyFormat(object_p->object_u.publicKey_s.keyBlock_s.keyFormat_t);
                    break;
                case I_KT_ObjectType_PrivateKey:
                    printf("Object Type : PrivateKey\n");
					printf("Key Material Length : %d\n", object_p->object_u.privateKey_s.keyBlock_s.keyBytes_s.byteStringLen);
                    printf("Key Material : ");
                    for (i = 0; i < object_p->object_u.privateKey_s.keyBlock_s.keyBytes_s.byteStringLen; i++)
                    {
                        printf("%2.2X", object_p->object_u.privateKey_s.keyBlock_s.keyBytes_s.byteString_p[i]);
                    }
                    printf("\n");
                    printKeyFormat(object_p->object_u.privateKey_s.keyBlock_s.keyFormat_t);
                        
                    break;
                case I_KT_ObjectType_Certificate:
                    printf("Object Type : Certificate\n");
                    break;
                case I_KT_ObjectType_SplitKey:
                    printf("Object Type : SplitKey\n");
                    break;
            }
        }
    } while (0);

    if (uids_p != NULL)
        I_KC_FreeUniqueIdentifiers(uids_p);
    if (object_p != NULL)
        I_KC_FreeManagedObject(object_p);
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
    int argp, keyFlag = 0;
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

    result = Get(&sess, uniqueID_p, name, &keyFlag);
    if (result.status != I_KT_ResultStatus_Success)
    {
        printf("Get failed Status:%s Reason:%s\n",
                I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
    }
    else if(keyFlag == 1)
    {
        printf("Object not found\n");
    }
    else
        printf("Get Operations Successful\n");

        I_C_CloseSession(sess);
    I_C_Fini();
    return rc;
}

