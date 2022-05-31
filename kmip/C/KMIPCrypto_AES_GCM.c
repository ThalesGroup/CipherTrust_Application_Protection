/*
 * KMIPCrypto_AES_GCM.c  
 *
 * Sample code is provided for educational purposes
 * No warranty of any kind, either expressed or implied by fact or law
 * Use of this item is not restricted by copyright or license terms
 *
 * Sample code for KMIP Crypt Operation. 
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
    fprintf(stderr, "usage: KMIPCrypto_AES_GCM conf_file keyname indata IV IVLen taglen\n"
	"\n conf_file - typically, CADP_CAPI.properties\n"
 	"\n keyname - key name\n"
	"\n indata - sample data to encrypt\n"
	"\n IV - initialization vector\n"
	"\n taglen -  Length of authentication tag, should be between 4 - 16 bytes\n"
	   );
    exit(1);
}

I_KS_Result Crypto(I_O_Session *handle_p, I_T_CHAR *name, I_T_BYTE *indata, I_T_BYTE *iv, unsigned int tag_len, unsigned int iv_len)
{
    I_KS_Result result;
    unsigned int i = 0;
    I_T_UINT count = 0;  
    I_KO_AttributeList attrList = NULL;
    I_KS_Object* object_p = NULL;
    I_KS_GetRequest getRequest;
    I_KS_UniqueIdentifiers *uids_p = NULL;
    I_KS_Object managedObject;
    I_KS_Crypto_Response *response_encrypt = NULL;
    I_KS_Crypto_Response *response_decrypt = NULL;
    I_T_BYTE *iv_random = NULL;
    I_T_BYTE *ciphertext = NULL;
    unsigned int cipher_len = 0;
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

        if (name != NULL)
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
                break;
            }
            else
            {
                I_KC_ClearAttributeList(attrList);
                addUniqueIdentifier(attrList, uids_p->uniqueIdentifiers_pp[0]);
            }
          }
          getRequest.keyFormat_t = I_KT_KeyFormat_None;

          addBlockCipherMode(attrList, I_KT_Mode_GCM);

          addIV(attrList, iv,iv_len);
	  addIVLen(attrList, iv_len);
          addTagLen(attrList,tag_len);
          addpadding(attrList, I_KT_Padding_None);
         
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

             ciphertext = (I_T_BYTE *)malloc(response_encrypt->Encrypted_data.byteStringLen);
             memset(ciphertext, 0, response_encrypt->Encrypted_data.byteStringLen);
             memcpy(ciphertext,  response_encrypt->Encrypted_data.byteString_p, response_encrypt->Encrypted_data.byteStringLen);
           }

         addIV(attrList, iv,iv_len);
        
         addBlockCipherMode(attrList, I_KT_Mode_GCM);

         addpadding(attrList, I_KT_Padding_None);

        addCipherLen(attrList, cipher_len);
        addIVLen(attrList, iv_len);
	addTagLen(attrList,tag_len);
	result =  I_KC_Crypto(*handle_p, attrList, DECRYPT,ciphertext, &response_decrypt);       
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
 
    return result;
}

int main(int argc, char **argv)
{

    I_O_Session sess;
    char *path, *taglen = NULL;
    int argp, ivlen=0;
    I_T_RETURN rc;
    I_KS_Result result;
    I_T_BYTE *indata = NULL, *iv = NULL;
    char *keyname = NULL;
    I_T_Operation operation;


    if (argc < 7)
        usage(); // exit

    argp = 1;
    path = argv[argp++];
    keyname = argv[argp++];
    indata = (I_T_BYTE*)argv[argp++];
    if(argc > 4)
        {
            if(strncmp(argv[argp],"null",4) != 0)
                iv = (I_T_BYTE*)argv[argp];
                argp++;
            ivlen = atoi(argv[argp++]);               
            if(!(ivlen >0 && ivlen <=16))
            {
                rc = I_E_INVALID_IV_SIZE;
                fprintf(stderr, "Invalid IV size %d\n",ivlen);
                exit(0);
            }
        }
    taglen=(argv[argp]);
    if(!(atoi(taglen) >=4 && atoi(taglen) <= 16))
    {
	fprintf(stderr,"Invalid tag len %s\n",taglen);
	exit(0);
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
    result = Crypto(&sess,keyname,indata,iv,atoi(taglen),ivlen);
    if (result.status != I_KT_ResultStatus_Success)
    {
        printf("KMIPCrypto failed Status:%s Reason:%s\n",
                I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
    }
    else
        printf("KMIPCrypto_AES_GCM Successful\n");
    I_C_CloseSession(sess);
    I_C_Fini();
    return rc;

}

