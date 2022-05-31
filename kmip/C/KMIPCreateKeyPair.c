/*
 * KMIPCreateKeyPair.c	  
 *
 * Sample code is provided for educational purposes
 * No warranty of any kind, either expressed or implied by fact or law
 * Use of this item is not restricted by copyright or license terms
 *
 * Sample code for KMIP Create key pair Operation.
 * 
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "cadp_capi.h"
#include "KMIPMisc.h"

void usage(void)
{
    fprintf(stderr, "usage: KMIPCreateKeyPair conf_file [Public key] [Private Key]\n");
    exit(1);
}


/*I_KS_Result PrepareKeyAttributes(I_O_Session *handle_p, char *name,  I_KO_AttributeList* pAttrList)
{
    I_KS_Result result;

    result = I_KC_CreateAttributeList(pAttrList, NULL);
    if (result.status == I_KT_ResultStatus_Success)
    {

        addRSACryptographicLength(*pAttrList);
        addObjectGroup(*pAttrList);
        addContactInformation(*pAttrList);
        addCustomAttributes(*pAttrList);
        addCryptographicUsageMask(*pAttrList);
        printAttrList(*pAttrList, KMIP_REQUEST);
   }
   return result;
}*/

I_KS_Result PreparePrivateKeyAttributes(I_O_Session *handle_p, char *name,  I_KO_AttributeList* pAttrList)
{
    I_KS_Result result;

    result = I_KC_CreateAttributeList(pAttrList, NULL);
    if (result.status == I_KT_ResultStatus_Success)
    {

        addRSACryptographicLength(*pAttrList);
 	 addObjectGroup(*pAttrList);
   	     addContactInformation(*pAttrList);
     	  addCustomAttributes(*pAttrList);
        addCryptographicUsageMask_private(*pAttrList);
        printAttrList(*pAttrList, KMIP_REQUEST);
   }
   return result;
}


I_KS_Result PreparePublicKeyAttributes(I_O_Session *handle_p, char *name,  I_KO_AttributeList* pAttrList)
{
    I_KS_Result result;

    result = I_KC_CreateAttributeList(pAttrList, NULL);
    if (result.status == I_KT_ResultStatus_Success)
    {

        addRSACryptographicLength(*pAttrList);
        addObjectGroup(*pAttrList);
        addContactInformation(*pAttrList);
        addCustomAttributes(*pAttrList);
        addCryptographicUsageMask_public(*pAttrList);
        printAttrList(*pAttrList, KMIP_REQUEST);
   }
   return result;
}




I_KS_Result CreateKeyPair(I_O_Session *handle_p, char *keyname_pub, char* keyname_priv)
{
    I_KO_AttributeList attrListPriv = NULL;
    I_KO_AttributeList attrListPub = NULL;
    I_KS_Result result;

    do
    {
        result = PreparePrivateKeyAttributes(handle_p, keyname_priv,  &attrListPriv);
        if (result.status != I_KT_ResultStatus_Success)
        {
                printf("I_KC_CreateKeyPair failed for private key. Status:%s Reason:%s\n",
                I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
                break;
        }

        result = PreparePublicKeyAttributes(handle_p, keyname_pub,  &attrListPub);
        if (result.status != I_KT_ResultStatus_Success)
        {
                printf("I_KC_CreateKeyPair failed for public key. Status:%s Reason:%s\n",
                I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
                break;
        }
   
        // Create the key
        result = I_KC_CreateKeyPair(*handle_p, attrListPriv, keyname_priv,attrListPub, keyname_pub);
        if (result.status != I_KT_ResultStatus_Success)
        {
            printf("I_KC_CreateKeyPair failed Status:%s Reason:%s\n",
                    I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
            break;
        }
    }
    while (0);

    printAttrList(attrListPub, KMIP_RESPONSE);
    // delete the attribute list
    if (attrListPriv != NULL)
    {
        I_KS_Result result1;
        result1 = I_KC_DeleteAttributeList(attrListPriv);
        if (result1.status != I_KT_ResultStatus_Success)
        {
            printf("I_KC_DeleteAttributeList failed Status:%s Reason:%s\n",
                    I_KC_GetResultStatusString(result1), I_KC_GetResultReasonString(result1));
        }
    }

    if (attrListPub != NULL)
    {
        I_KS_Result result1;
        result1 = I_KC_DeleteAttributeList(attrListPub);
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
    char *path, *keyname_pub = NULL, *keyname_priv = NULL;
    int argp;
    I_T_RETURN rc;
    I_KS_Result result;

    if (argc < 2)
        usage(); // exit

    argp = 1;
    path = argv[argp++];

    if (argc >= 3)
        keyname_pub = argv[argp];

    if (argc == 4)
        keyname_priv = argv[++argp];

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

    result = CreateKeyPair(&sess, keyname_pub, keyname_priv);
    if (result.status != I_KT_ResultStatus_Success)
    {
        printf("CreateKeyPair failed Status:%s Reason:%s\n",
                I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
    }
    else
        printf("CreateKeyPair Successful\n");

    I_C_CloseSession(sess);
    I_C_Fini();
    return rc;

}

