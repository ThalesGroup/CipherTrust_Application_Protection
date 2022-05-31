/* KMIPCryptoSinglePart.c  
 *
 * Sample code is provided for educational purposes
 * No warranty of any kind, either expressed or implied by fact or law
 * Use of this item is not restricted by copyright or license terms
 *
 *  KMIP Crypto Sample using Single Part Data.
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "cadp_capi.h"
#include "KMIPMisc.h"

void hexprint(const char* label, const I_T_BYTE *in, int len)
{
    int i;
    fprintf(stdout, "%s:", label);
    for (i = 0; i < len && i < 80; i++)
    {
        fprintf(stdout, "%2.2x ", (unsigned char) in[i]);
    }
    fprintf(stdout, "\n");
}

void usage(void)
{
    fprintf(stderr, "usage: KMIPCryptoSinglePart conf_file keyname indata\n"
            "  conf_file - typically, CADP_CAPI.properties\n"
            "  keyname - name of the key to be created using KMIP Register Operation.\n"
            "  indata - sample data to be encrypted.\n"
            );
    exit(1);
}

I_KS_Result RegisterKey(I_O_Session *handle_p, char *keyname)
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

        memset(byteBlock_p, 0x01, 16);

        // create the attribute list
        result = I_KC_CreateAttributeList(&attrList, NULL);
        if (result.status != I_KT_ResultStatus_Success)
        {
            printf("I_KC_CreateAttributeList failed Status:%s Reason:%s\n",
                    I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
            break;
        }

        addName(attrList, keyname, NULL);
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

    } while (0);
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

    I_O_Session sess = NULL;
    char *path, *keyname;
    I_T_BYTE *indata = NULL, *out = NULL;
    int argp, indatalen;
    I_T_UINT outlen;
    I_O_CipherSpec cipherspec = NULL;
    I_T_RETURN rc;
    I_T_Operation operation;
    I_KS_Result result;


    do
    {
        if (argc < 4)
            usage(); // exit

        argp = 1;
        path = argv[argp++];
        keyname = argv[argp++];
        indata = (I_T_BYTE*) argv[argp++];
        indatalen = strlen((char *) indata);

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
            break;
        }

        result = RegisterKey(&sess, keyname);
        if (result.status != I_KT_ResultStatus_Success)
        {
            printf("RegisterKey failed Status:%s Reason:%s\n",
                    I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
            break;
        } 
        else
            printf("RegisterKey Successful\n");


        rc = I_C_CreateCipherSpec("AES/ECB/PKCS5Padding", keyname, &cipherspec);

        if (rc != I_E_OK)
        {
            fprintf(stderr, "I_C_CreateCipherSpec error: %s\n",
                    I_C_GetErrorString(rc));
            break;
        }


        operation = I_T_Operation_Encrypt;

        /* This function will tell us how much memory to allocate for the 
         * ciphertext.  The length will be set in encdatalen. */
        rc = I_C_CalculateOutputSizeForKey(sess,
                cipherspec, operation, indatalen, &outlen);

        if (rc != I_E_OK)
        {
            fprintf(stderr, "I_C_CalculateOutputSizeForKey error: %s\n",
                    I_C_GetErrorString(rc));
            break;
        }

        out = (I_T_BYTE *) malloc(outlen);

        if (!out)
        {
            fprintf(stderr, "Failed to allocate %d bytes.\n", outlen);
            break;
        }

        rc = I_C_Crypt(sess, cipherspec, operation,
                NULL, 0, indata, indatalen, (I_T_BYTE*) out, &outlen);

        if (rc != I_E_OK)
        {
            fprintf(stderr, "I_C_Crypt() error: %s\n",
                    I_C_GetErrorString(rc));
            break;
        } 
        else
        {
            hexprint("Encrypted Text (Hex)", out, outlen);
        }
    } while (0);

    if (out != NULL)
        free(out);
    if (cipherspec != NULL)
        I_C_DeleteCipherSpec(cipherspec);
    if (sess != NULL)
        I_C_CloseSession(sess);
    I_C_Fini();
    return rc;

}
