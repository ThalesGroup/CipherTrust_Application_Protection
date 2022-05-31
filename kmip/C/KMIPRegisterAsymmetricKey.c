/*
 * KMIPRegisterAsymmetricKey.c	
 *
 * Sample code is provided for educational purposes
 * No warranty of any kind, either expressed or implied by fact or law
 * Use of this item is not restricted by copyright or license terms
 *
 * Sample code for KMIP Register Operation with Asymmetric Key 
 * 
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "cadp_capi.h"
#include "KMIPMisc.h"
#include <openssl/rand.h>

#include <openssl/bn.h>
#include <openssl/rsa.h>
#include <openssl/pem.h>

char pubkey2048 [] =  "-----BEGIN RSA PUBLIC KEY-----\nMIIBCgKCAQEAuzt3MpyV4KA8RbttAZGxVG3zFb7lcYrKmkmgyEsR2xnt152Svgwk\nO1FeQoTcTTql9V1DVbXupr1aQ+z2t4xf6/aCysFv5lpYmepnnbHfOigAYzyWSv64\n1q2VNU5r92z6i6u0A5Ba9Q5SbNtgIzCPoW+sRixVx2yCt+hiVH0mKyrlMNQHyjdc\nbZizohW8hoHF47U9lmHITkmAXqxMBAeVxjDoqxBuVBu1SHqUB8tWvgS73zpQWfnU\nmbz3SWm0a15JOqfghj7ozbEynLk0T3kqRb+B89BwOuhx/xj+4dAQUiHOW3+DY6fN\nKa1JWA+cHc2QdWHcoZo88F4AKU9jK1TmDwIDAQAB\n-----END RSA PUBLIC KEY-----";

char privkey2048 [] = "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEAuzt3MpyV4KA8RbttAZGxVG3zFb7lcYrKmkmgyEsR2xnt152S\nvgwkO1FeQoTcTTql9V1DVbXupr1aQ+z2t4xf6/aCysFv5lpYmepnnbHfOigAYzyW\nSv641q2VNU5r92z6i6u0A5Ba9Q5SbNtgIzCPoW+sRixVx2yCt+hiVH0mKyrlMNQH\nyjdcbZizohW8hoHF47U9lmHITkmAXqxMBAeVxjDoqxBuVBu1SHqUB8tWvgS73zpQ\nWfnUmbz3SWm0a15JOqfghj7ozbEynLk0T3kqRb+B89BwOuhx/xj+4dAQUiHOW3+D\nY6fNKa1JWA+cHc2QdWHcoZo88F4AKU9jK1TmDwIDAQABAoIBAHji+iEZbMOtcXzs\neIMM2FvU6aBesrHOlOVtKHxpy8uVQDV4rag7GqGZ9awpMDxE46Y6YyFR6BaMJ123\n/8uevMgTT3stzdwC9TXbXK86ixB3h1iLY9ZkBF/Hj5DtY1RLbrEDWaT7bV7PsnRK\naBYQYowvGCHuuiuaagPn7KT0cNJpMkftOo9PHm7t2+6v5DxColMz5asI43CwnewG\n/CYMO/6ycG04tSAmLeMO9NHgir/ynlD8SnUCTeyF911Rg5GJpgvqsOSxt9tLfGUz\npMCb5Aql239jpqBk2Da2xIddYTDKJBzJxAT67+jo9/1bU4HuEFq41jLlBOS0GFMi\nlNkXWPECgYEA6xPtgh27iClFpCP4MIWADKvvMl7dQcHr41E5eBAyD8CpPhKHv7pP\nWxOsEf5NBpO635hjk4XW2ZRA8ZgVpJ8lyLNDXJ+8XqGwmU5RdtOYQSA+XiD92Gef\nvjH7C/i0LLhq\nOhMYU7GOK89oT/6KuC3CAUOCeVCkbg7oxBdDmu5TEX0CgYEAy+Vp\nq9iXF5EfGQxgWHHh688bbagtc3UADW7+TcHPb9xgC00bj9+n5RIWLVT6JyrZVCdp\nUg/3c38Kt+fxSK+GMuK+R8RfQLThtZqilTOQoqLvDjrEU7nmv8I7ruVGFy6KCppu\nB7BEaRm/MNm5D3dHCpLrbAF0qnxLvMuLvWxBq3sCgYEAsO0dq/mOxEsz0/cSfApu\nNptM+x807aHzVPI0C648z2hUuJgfvWiPA2BJ+HzqIhIb6t95ynVIIBgZzPuHBpCV\nUnnBMDw0/RA6pxev7nwQsqt+5T91bmOHchGR/g+gI6xknvLyM0OGWmjO/K36X+Zo\nhqT11TKhnwfvnm5X/opy0M0CgYBmz7km88HMGlsJ8Fmsf1Ah7X6xHno8m6R5IZyN\nbMrCZubvC+R3+ZjZQvN3zD+O/GY1ruHGhVKLJGYtMYFS217ZzceQvI4jPJILVnvg\nq+2kdHACRtO0PCsESlZ57BYZnlfw3MnaiqEUNe1YHpDYIZbq2AZpoZpIVQCDpEdE\nLpA2fQKBgQCgdIFvpr/iKZw+ptN/zE91jjLv9dNJ7IPEm5T4XTcGk3p8oOMWBAvV\nA60SjWUZVC9Jm6PfIPd4us65zmCTKvpUgjWWYGZg1VmdRgsl4UNNebUiw6wkVKVI\n7HJpt1o1F8iFDY08Y7LlGhKxpIZcFdRHZw5c9YikSQ7dDGTn5dfl2g==\n-----END RSA PRIVATE KEY-----";

void usage(void)
{
    fprintf(stderr, "usage: KMIPRegisterAsymmetricKey conf_file [keyname1] [keyname2]\n");
    exit(1);
}

int
PEM2DER ( int otype,
          char *pem_str, int len, unsigned char *der_buf, int *der_len )
{
    int rc = -1;

    RSA *rsa = NULL;
    BIO *bio_mem = NULL;
    unsigned char * tmp_buf = NULL;

    bio_mem = BIO_new_mem_buf ( pem_str, len );
    if ( bio_mem == NULL )
        goto end;

    if ( otype == 0 )
        rsa = (RSA *)PEM_read_bio_RSAPrivateKey( bio_mem, NULL, NULL, NULL );
    else if ( otype == 1 )
        rsa = (RSA *)PEM_read_bio_RSAPublicKey( bio_mem, NULL, NULL, NULL );

    if ( rsa == NULL )
    {
        (void) BIO_reset ( bio_mem );
        rsa = (RSA *)PEM_read_bio_RSA_PUBKEY ( bio_mem, NULL, NULL, NULL );

        if ( rsa == NULL )
           goto end;
    }

    if ( otype == 0)
        *der_len = i2d_RSAPrivateKey ( rsa, &tmp_buf );
    else if ( otype == 1 )
        *der_len = i2d_RSAPublicKey ( rsa, &tmp_buf );
    if ( *der_len > 0 )
    {
        memcpy ( der_buf, tmp_buf, *der_len );
        rc = 0;
    }

end:
    if ( bio_mem )
        BIO_free ( bio_mem );
    if ( tmp_buf )
        free ( tmp_buf );
    if ( rsa )
        RSA_free ( rsa );

   return rc;
}


I_KS_Result PrepareKey(I_O_Session *handle_p, char *name, int bPublic, I_KS_Object* pManagedObject,  I_KO_AttributeList* pAttrList)
{
    I_KS_Object managedObject = *pManagedObject;
    char *uniqueID_p = NULL;
    I_KS_Result result;
    int len = 0;
    I_T_BYTE *byteBlock_p = NULL;
    int num = 2048;
    const EVP_CIPHER *enc=NULL;

   
    byteBlock_p = calloc(num,sizeof(I_T_BYTE));
    if ( bPublic == 1 )
    {
         PEM2DER ( bPublic,
                   pubkey2048, sizeof(pubkey2048),
                   (unsigned char*) byteBlock_p, &len );
    }else
    {
         PEM2DER ( bPublic,
                   privkey2048, sizeof( privkey2048),
                   (unsigned char*) byteBlock_p, &len );
    }

   result = I_KC_CreateAttributeList(pAttrList, NULL);
   if (result.status == I_KT_ResultStatus_Success)
  {
       	addName(*pAttrList, name, NULL);
        addObjectGroup(*pAttrList);
       	addContactInformation(*pAttrList);
        addCustomAttributes(*pAttrList);
        addCryptographicUsageMask(*pAttrList);      

       	printAttrList(*pAttrList, KMIP_REQUEST);

        if(1 == bPublic)
	{
		pManagedObject->objectType_t = I_KT_ObjectType_PublicKey;
		
		// fill the key Block
		pManagedObject->object_u.publicKey_s.keyBlock_s.keyAlgo_t = I_KT_CryptographicAlgorithm_RSA;
		pManagedObject->object_u.publicKey_s.keyBlock_s.keyCompress_t = I_KT_KeyCompressionType_None;
		pManagedObject->object_u.publicKey_s.keyBlock_s.keyFormat_t = I_KT_KeyFormat_PKCS1;
		pManagedObject->object_u.publicKey_s.keyBlock_s.keyLength = 2048; // this should be in bits
		pManagedObject->object_u.publicKey_s.keyBlock_s.keyBytes_s.byteString_p = byteBlock_p;
		pManagedObject->object_u.publicKey_s.keyBlock_s.keyBytes_s.byteStringLen = len;
       }
	else
       {
		pManagedObject->objectType_t = I_KT_ObjectType_PrivateKey;
		
		// fill the key Block
		pManagedObject->object_u.privateKey_s.keyBlock_s.keyAlgo_t = I_KT_CryptographicAlgorithm_RSA;
		pManagedObject->object_u.privateKey_s.keyBlock_s.keyCompress_t = I_KT_KeyCompressionType_None;
		pManagedObject->object_u.privateKey_s.keyBlock_s.keyFormat_t = I_KT_KeyFormat_PKCS1;
		pManagedObject->object_u.privateKey_s.keyBlock_s.keyLength = 2048; // this should be in bits
		pManagedObject->object_u.privateKey_s.keyBlock_s.keyBytes_s.byteString_p = byteBlock_p;
		pManagedObject->object_u.privateKey_s.keyBlock_s.keyBytes_s.byteStringLen = len;
	}
   }
   return result;
}

I_KS_Result RegisterAsymmetricKey(I_O_Session *handle_p, char *keyNamePub, char* keyNamePriv)
{
    I_KO_AttributeList attrListPriv = NULL;
    I_KO_AttributeList attrListPub = NULL;
	I_KS_Object privateKeyobj, publicKeyobj;
    I_KS_Object *privateKey = &privateKeyobj;
	I_KS_Object *publicKey = &publicKeyobj;
    I_KS_Result result, result2;
    do
    {

	result = PrepareKey(handle_p, keyNamePriv, 0, privateKey,  &attrListPriv);
        if (result.status != I_KT_ResultStatus_Success)
        {
		printf("I_KC_Register failed for private key. Status:%s Reason:%s\n",
                I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
		break;
        }

	result = PrepareKey(handle_p, keyNamePub, 1, publicKey,  &attrListPub);
        if (result.status != I_KT_ResultStatus_Success)
        {
		printf("I_KC_Register failed for public key. Status:%s Reason:%s\n",
                I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
		break;
        }

        // register the key
        result = I_KC_RegisterAsymmetricKey(*handle_p, attrListPub, publicKey, attrListPriv, privateKey);
        if (result.status != I_KT_ResultStatus_Success)
        {
            printf("I_KC_Register failed Status:%s Reason:%s\n",
                    I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
            break;
        }

        printAttrList(attrListPriv, KMIP_REQUEST);
        printAttrList(attrListPub, KMIP_RESPONSE);

	result = I_KC_Destroy(*handle_p, attrListPub);
	if (result.status != I_KT_ResultStatus_Success) printf("I_KC_Destroy failed Status:%s Reason:%s\n",  I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));

	result = I_KC_Destroy(*handle_p, attrListPriv);
	if (result.status != I_KT_ResultStatus_Success) printf("I_KC_Destroy failed Status:%s Reason:%s\n",  I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));

    }    while (0);

    if (attrListPriv != NULL)
    {
        result2 = I_KC_DeleteAttributeList(attrListPriv);
        if (result2.status != I_KT_ResultStatus_Success)
        {	
            printf("I_KC_DeleteAttributeList failed Status:%s Reason:%s\n",
                    I_KC_GetResultStatusString(result2), I_KC_GetResultReasonString(result2));
        }
    }

    if (attrListPub != NULL)
    {
        I_KS_Result result1;
        result1 = I_KC_DeleteAttributeList(attrListPub);
        if (result2.status != I_KT_ResultStatus_Success)
        {	
            printf("I_KC_DeleteAttributeList failed Status:%s Reason:%s\n",
                    I_KC_GetResultStatusString(result2), I_KC_GetResultReasonString(result2));
        }
    }
	if(privateKeyobj.object_u.privateKey_s.keyBlock_s.keyBytes_s.byteString_p !=NULL)
	{
       free(privateKeyobj.object_u.privateKey_s.keyBlock_s.keyBytes_s.byteString_p);
	   privateKeyobj.object_u.privateKey_s.keyBlock_s.keyBytes_s.byteString_p = NULL;
	   privateKeyobj.object_u.privateKey_s.keyBlock_s.keyBytes_s.byteStringLen = 0;
	}

	if(publicKeyobj.object_u.publicKey_s.keyBlock_s.keyBytes_s.byteString_p !=NULL)
	{
	   free(publicKeyobj.object_u.publicKey_s.keyBlock_s.keyBytes_s.byteString_p);
	   publicKeyobj.object_u.publicKey_s.keyBlock_s.keyBytes_s.byteString_p = NULL;
	   publicKeyobj.object_u.publicKey_s.keyBlock_s.keyBytes_s.byteStringLen = 0;
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

    result = RegisterAsymmetricKey(&sess, keyname1, keyname2);
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

