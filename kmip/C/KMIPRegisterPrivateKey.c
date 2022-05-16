/*
 * KMIPRegisterPrivateKey.c	
 *
 * Sample code is provided for educational purposes
 * No warranty of any kind, either expressed or implied by fact or law
 * Use of this item is not restricted by copyright or license terms
 *
 * Sample code for KMIP Register Operation for Private Key.
 * 
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "cadp_capi.h"
#include "KMIPMisc.h"
#include <openssl/bn.h>
#include <openssl/rsa.h>
#include <openssl/x509.h>

void usage(void)
{
    fprintf(stderr, "usage: KMIPRegisterPrivateKey conf_file [name1] [name2]\n");
    exit(1);
}

I_KS_Result RegisterPrivateKey(I_O_Session *handle_p, char *name1, char* name2)
{
    I_KO_AttributeList attrList = NULL;
    I_KS_Object managedObject;
    char *uniqueID_p = NULL;
    I_KS_Result result;
    int len = 0;
	I_T_BYTE *byteBlock_p = NULL;
	BIO *out=NULL;
	unsigned long f4=RSA_F4;
	RSA *rsa = RSA_new();
	BIGNUM *bn = BN_new();
	int num = 1024;
	const EVP_CIPHER *enc=NULL;


	if(!BN_set_word(bn, f4) || !RSA_generate_key_ex(rsa, num, bn, NULL))
	{
		printf("RSA Key Generation failed\n");
        exit(EXIT_FAILURE);
    }

	out = BIO_new(BIO_s_mem());

    if (!i2d_RSAPrivateKey_bio(out,rsa))
    {
    	printf("RSA Key Conversion failed\n");
		BIO_free_all(out);
        exit(EXIT_FAILURE);
	}

    len = BIO_get_mem_data(out,&byteBlock_p);
		

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
        addName(attrList, name1, name2);
        addObjectGroup(attrList);
        addContactInformation(attrList);
        addCustomAttributes(attrList);
        addCryptographicUsageMask(attrList);
              
        printAttrList(attrList, KMIP_REQUEST);

        managedObject.objectType_t = I_KT_ObjectType_PrivateKey;
		
        // fill the key Block
        managedObject.object_u.privateKey_s.keyBlock_s.keyAlgo_t = I_KT_CryptographicAlgorithm_RSA;
        managedObject.object_u.privateKey_s.keyBlock_s.keyCompress_t = I_KT_KeyCompressionType_None;
        managedObject.object_u.privateKey_s.keyBlock_s.keyFormat_t = I_KT_KeyFormat_PKCS1;
        managedObject.object_u.privateKey_s.keyBlock_s.keyLength = 1024; // this should be in bits
        managedObject.object_u.privateKey_s.keyBlock_s.keyBytes_s.byteString_p = byteBlock_p;
        managedObject.object_u.privateKey_s.keyBlock_s.keyBytes_s.byteStringLen = len;


        // register the key
        result = I_KC_Register(*handle_p, attrList, &managedObject);
        if (result.status != I_KT_ResultStatus_Success)
        {
            printf("I_KC_Register failed Status:%s Reason:%s\n",
                    I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
            break;
        }

        printAttrList(attrList, KMIP_RESPONSE);

    }    
	while (0);

	BIO_free_all(out);
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
    if(rsa) RSA_free(rsa);
    if(bn) BN_free(bn);
    return result;
}

int main(int argc, char **argv)
{

    I_O_Session sess;
    I_T_RETURN rc;
    char *path, *name1 = NULL, *name2 = NULL;
    int argp;
    I_KS_Result result;

    if (argc < 2)
        usage(); // exit

    argp = 1;
    path = argv[argp++];

    if (argc >= 3)
        name1 = argv[argp];
    if (argc == 4)
        name2 = argv[++argp];

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

    result = RegisterPrivateKey(&sess, name1, name2);
    if (result.status != I_KT_ResultStatus_Success)
    {
        printf("RegisterPrivateKey failed Status:%s Reason:%s\n",
                I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
    }
    else
        printf("RegisterPrivateKey Successful");

    I_C_CloseSession(sess);
    I_C_Fini();
    return rc;

}

