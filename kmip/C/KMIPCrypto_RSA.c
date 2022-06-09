/*
 * KMIPCrypto_RSA.c  
 *
 * Sample code is provided for educational purposes
 * No warranty of any kind, either expressed or implied by fact or law
 * Use of this item is not restricted by copyright or license terms
 *
 * Sample code for KMIP Crypt/Decrypt Operation. 
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
    for(i = 0; i < len && i < 80; i++)
    {
        fprintf(stdout,"%2.2x ",(unsigned char)in[i]);
    }
    fprintf(stdout,"\n");
}

void usage(void)
{
    fprintf(stderr, "usage: KMIPCrypto_RSA conf_file public_key private_key indata \n");
    exit(1);
}

I_KS_Result Crypto(I_O_Session *handle_p, I_T_CHAR *public_key, I_T_CHAR *private_key, I_T_BYTE *indata, int *keyFlag)
{
    I_KS_Result result;
    unsigned int i = 0;
    I_T_UINT count = 0;  
    I_KO_AttributeList attrList = NULL;
    I_KO_AttributeList attrList1 = NULL;
    I_KS_Object* object_p = NULL;
    I_KS_GetRequest getRequest;
    I_KS_UniqueIdentifiers *uids_p = NULL;
    I_KS_UniqueIdentifiers *uids_p1 = NULL;
    I_KS_Object managedObject;
    I_KS_Crypto_Response *response_encrypt = NULL;
    I_KS_Crypto_Response *response_decrypt = NULL;
    I_T_BYTE *iv_random = NULL;
    I_T_BYTE *ciphertext = NULL;
    unsigned int cipher_len = 0;
    unsigned int iv_len = 0;
    I_T_Operation operation;
  
    do{

        //create the attribute list
        result = I_KC_CreateAttributeList(&attrList, NULL);
        if (result.status != I_KT_ResultStatus_Success)
        {
            printf("I_KC_CreateAttributeList failed Status:%s Reason:%s\n",
                    I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
            break;
        }

        if (public_key != NULL)
        {
            //Use Locate to find UniqueID.
            addName(attrList, public_key, NULL);
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
               
         addRSACryptographicAlgorithm(attrList); 
         
         result = I_KC_Crypto(*handle_p, attrList, ENCRYPT, indata, &response_encrypt);

         if (result.status != I_KT_ResultStatus_Success)
         {
              printf("I_KC_Crypto failed Status:%s Reason:%s\n",
                      I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
              break;
         }

         if(response_encrypt != NULL)
           {
             hexprint("Encrypted Text (Hex)", response_encrypt->Encrypted_data.byteString_p,response_encrypt->Encrypted_data.byteStringLen);
             cipher_len = response_encrypt->Encrypted_data.byteStringLen;
             iv_len = response_encrypt->IV_data.byteStringLen;

             ciphertext = (I_T_BYTE *)malloc(response_encrypt->Encrypted_data.byteStringLen);
             memset(ciphertext, 0, response_encrypt->Encrypted_data.byteStringLen);
             memcpy(ciphertext,  response_encrypt->Encrypted_data.byteString_p, response_encrypt->Encrypted_data.byteStringLen);
           }

        result = I_KC_CreateAttributeList(&attrList1, NULL);
        if (result.status != I_KT_ResultStatus_Success)
        {
            printf("I_KC_CreateAttributeList failed Status:%s Reason:%s\n",
                    I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
            break;
        }

         if (private_key != NULL)
          {
            //Use Locate to find UniqueID.
            addName(attrList1, private_key, NULL);
            result = I_KC_Locate(*handle_p, I_KT_StorageStatus_Online, attrList1, &uids_p1, 0);
            if (result.status != I_KT_ResultStatus_Success)
            {
                printf("I_KC_Locate failed Status:%s Reason:%s\n",
                        I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
                break;
            }

            if (uids_p1->count == 0)
            {
                printf("No object exist for specified name.\n");
                break;
            }
            else
            {
                I_KC_ClearAttributeList(attrList1);
                addUniqueIdentifier(attrList1, uids_p1->uniqueIdentifiers_pp[0]);
            }
          }

        addRSACryptographicAlgorithm(attrList1); 
        addCipherLen(attrList1, cipher_len);

        result =  I_KC_Crypto(*handle_p, attrList1, DECRYPT,ciphertext, &response_decrypt);       
        if (result.status != I_KT_ResultStatus_Success)
        {
             printf("I_KC_Crypto failed for decryption Status:%s Reason:%s\n",
                     I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
             break;
        }
        if(response_decrypt != NULL)
          hexprint("Decrypted Text (Hex)", response_decrypt->Encrypted_data.byteString_p,response_decrypt->Encrypted_data.byteStringLen);


        }while(0);
    if (uids_p != NULL)
        I_KC_FreeUniqueIdentifiers(uids_p);
    if (uids_p1 != NULL)
        I_KC_FreeUniqueIdentifiers(uids_p1);
    if (response_encrypt != NULL)
        I_KC_FreeCryptoObject(response_encrypt);
    if (response_decrypt != NULL)
        I_KC_FreeCryptoObject(response_decrypt);
    if(ciphertext != NULL)
      free(ciphertext);
    if(iv_random != NULL)
      free(iv_random);
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
    if (attrList1 != NULL)
    {
        I_KS_Result result1;
        result1 = I_KC_DeleteAttributeList(attrList1);
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
    int argp, ivlen, keyFlag = 0;
    I_T_RETURN rc;
    I_KS_Result result;
    I_T_BYTE *indata = NULL, *iv = NULL;
    char *pub_key = NULL, *priv_key = NULL;
    I_T_Operation operation;


    if (argc < 4)
        usage(); // exit

    argp = 1;
    path = argv[argp++];
    pub_key = argv[argp++];
    priv_key = argv[argp++];
    indata = (I_T_BYTE*)argv[argp++];
    
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
    result = Crypto(&sess,pub_key,priv_key,indata,&keyFlag);
    if (result.status != I_KT_ResultStatus_Success)
    {
        printf("KMIPCrypto_RSA failed Status:%s Reason:%s\n",
                I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
    }
    else if(keyFlag == 1)
    {
        printf("Object not found\n");
    }
    else
        printf("KMIPCrypto_RSA Successful\n");
    
    I_C_CloseSession(sess);
    I_C_Fini();
    return rc;

}

