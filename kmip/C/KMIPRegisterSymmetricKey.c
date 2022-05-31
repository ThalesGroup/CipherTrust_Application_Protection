/*
 * KMIPRegisterSymmetricKey.c	
 *
 * Sample code is provided for educational purposes
 * No warranty of any kind, either expressed or implied by fact or law
 * Use of this item is not restricted by copyright or license terms
 *
 * Sample code for KMIP Register Operation with Symmetric Key 
 * 
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "cadp_capi.h"
#include "KMIPMisc.h"
#include <openssl/rand.h>

void usage(void)
{
    fprintf(stderr, "usage: KMIPRegisterSymmetricKey conf_file [keyname1] [keyname2]\n");
    exit(1);
}

I_KS_Result RegisterKey(I_O_Session *handle_p, char *keyname1, char* keyname2)
{
    I_KO_AttributeList attrList = NULL;
    I_T_BYTE *byteBlock_p = NULL;
    I_KS_Object managedObject;
    I_KS_Result result;

    do
    {
        byteBlock_p = malloc(16);
		if (byteBlock_p == NULL)
        {
            printf("Memory Allocation failed\n");
            exit(EXIT_FAILURE);
        }
		RAND_bytes(byteBlock_p,16);

        // create the attribute list
        result = I_KC_CreateAttributeList(&attrList, NULL);
        if (result.status != I_KT_ResultStatus_Success)
        {
            printf("I_KC_CreateAttributeList failed Status:%s Reason:%s\n",
                    I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
            break;
        }

        addName(attrList, keyname1, keyname2);
		addApplicationSpecificInfo(attrList);
        addObjectGroup(attrList);
        addContactInformation(attrList);
        addCustomAttributes(attrList);
        addCryptographicUsageMask(attrList);

        printAttrList(attrList, KMIP_REQUEST);

        // fill the key Block
        managedObject.object_u.symmetricKey_s.keyBlock_s.keyAlgo_t = I_KT_CryptographicAlgorithm_AES;
        managedObject.object_u.symmetricKey_s.keyBlock_s.keyCompress_t = -1;
        managedObject.object_u.symmetricKey_s.keyBlock_s.keyFormat_t = I_KT_KeyFormat_Raw;
        managedObject.object_u.symmetricKey_s.keyBlock_s.keyLength = 16 * 8; // this should be in bits
        managedObject.object_u.symmetricKey_s.keyBlock_s.keyBytes_s.byteString_p = byteBlock_p;
        managedObject.object_u.symmetricKey_s.keyBlock_s.keyBytes_s.byteStringLen = 16;
        managedObject.objectType_t = I_KT_ObjectType_SymmetricKey;


        // register the key
        result = I_KC_Register(*handle_p, attrList, &managedObject);
        if (result.status != I_KT_ResultStatus_Success)
        {
            printf("I_KC_Register failed Status:%s Reason:%s\n",
                    I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
            break;
        }

        printAttrList(attrList, KMIP_RESPONSE);

    }    while (0);
    // delete the attribute list
    if (byteBlock_p != NULL)
        free(byteBlock_p);

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
    char *path, *keyname1 = NULL, *keyname2 = NULL;
    int argp;
    I_T_RETURN rc;
    I_KS_Result result;

    if (argc < 2)
        usage(); // exit

    argp = 1;
    path = argv[argp++];

    if (argc >= 3)
        keyname1 = argv[argp];

    if (argc == 4)
        keyname2 = argv[++argp];

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

    result = RegisterKey(&sess, keyname1, keyname2);
    if (result.status != I_KT_ResultStatus_Success)
    {
        printf("RegisterKey failed Status:%s Reason:%s\n",
                I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
    }
    else
        printf("RegisterKey Successful\n");

    I_C_CloseSession(sess);
    I_C_Fini();
    return rc;

}

