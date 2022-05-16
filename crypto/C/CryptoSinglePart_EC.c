/*
 * CryptoSinglePart_EC.c
 *
 * Sample code is provided for educational purposes
 * No warranty of any kind, either expressed or implied by fact or law
 * Use of this item is not restricted by copyright or license terms
 *
 *  Crypto Sample using Single Part Data.
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "cadp_capi.h"

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
    fprintf(stderr, "usage: ./CryptoSinglePart_EC conf_file keyname algo indata iv passphrase user passwd  \n"
        "\n  conf_file - typically, CADP_CAPI.properties\n"
        "  keyname - key name\n"
        "  algo - algorithm name\n"
        "  indata - sample data to encrypt\n"
	"  iv - initialization vector\n"
        "  passphrase - optional cache passphrase, 'null' for null passphrase\n"
	"  user - (optional NAE user) user can be in a root domain or in a specific domain. For domain user, specify domain||username\n"
	"  passwd - optional (mandatory if user is specified) NAE user's password\n"
    );
    exit(1);
}

int main(int argc, char **argv)
{

    I_O_Session sess = NULL; 
    char *path = NULL, *user = NULL, *pass = NULL , *keyname = NULL, *algo = NULL;
    I_T_BYTE *indata = NULL, *cryptoin1 = NULL, *cryptoin2 = NULL, *cryptoout1 = NULL, *cryptoout2 = NULL;
    I_T_BYTE *passphrase = NULL;
    char *mac_data_tag = NULL,*ephemeral_key_tag = NULL;
    char*  iv = NULL;
    unsigned int argp = 0, ivlen = 0, indatalen = 0;
    I_T_UINT cryptoinlen1, cryptoinlen2, cryptooutlen1, cryptooutlen2;
    I_O_CipherSpec cipherspec = NULL;
    I_O_UserSpec userspec_enc = NULL, userspec_dec = NULL;
    I_T_RETURN rc = I_E_OK;
    I_T_Operation operation;
    int mac_data_tag_len = 0,ephemeral_key_tag_len = 0;
    do
    {
                if (argc < 5)
        usage(); // exit

    argp = 1;
    path  = argv[argp++];
    keyname = argv[argp++];
    algo = argv[argp++];
    indata = (I_T_BYTE*)argv[argp++];

        if(argc > 5)
        {
            if(strncmp(argv[argp],"null",4) != 0)
                iv = (I_T_BYTE*)argv[argp];
                argp++;
                // optional cache passphrase
        if (argc > 6)
                {
                        if(strncmp(argv[argp],"null",4) != 0)
                passphrase = (I_T_BYTE*)argv[argp];
                        argp++;
                        if(argc == 8)
                        {
                                usage();
                            exit(0);
                        }
                        if(argc > 8 )
                        {
                                user = argv[argp++];
                                pass = argv[argp++];
                        }
                }
        }

        if(iv)
        ivlen = (unsigned int)strlen((char *)iv);
        if(indata != NULL)
        indatalen = (unsigned int)strlen((char *)indata);
    
    rc = I_C_Initialize(I_T_Init_File,path);

    if (rc != I_E_OK)
    {
        fprintf(stderr, "I_C_Initialize error: %s\n",
            I_C_GetErrorString(rc));
        return rc;
    }
    if (passphrase)
    {
                // open session and pass cache passphrase:
                if(user != NULL)
            rc = I_C_OpenSessionPersistentCachePassphrase(
                &sess,I_T_Auth_Password,user,pass,passphrase,
                (unsigned int)strlen((char*)passphrase));
                else
                        rc = I_C_OpenSessionPersistentCachePassphrase(
                &sess,I_T_Auth_NoPassword,NULL,NULL,passphrase,
                (unsigned int)strlen((char*)passphrase));
    }
    else
    {
	if(user != NULL)
           rc = I_C_OpenSession(&sess,I_T_Auth_Password,user,pass);
	else
           rc = I_C_OpenSession(&sess,I_T_Auth_NoPassword,NULL,NULL);
    } 
    if (rc != I_E_OK)
    {
        fprintf(stderr, "I_C_OpenSession error: %s\n",
            I_C_GetErrorString(rc));
            break;
    }

    rc = I_C_CreateCipherSpec(algo,keyname,&cipherspec);

    if (rc != I_E_OK) 
    {
        fprintf(stderr, "I_C_CreateCipherSpec error: %s\n",
            I_C_GetErrorString(rc));
            break;
    }
    if (!strncmp(algo, "SHA", 3))
        operation = I_T_Operation_Sign;
    else
        operation = I_T_Operation_PublicEncrypt;


    /* Below function is call to allocate the memory to UserSpec 
     *  to store the Ephemeral public key and mac data */
    if (operation == I_T_Operation_PublicEncrypt)
    {
        rc = I_C_SetUserSpec(I_T_USPEC_EC_ENCRYPTION,NULL,0,&userspec_enc);
        if (rc != I_E_OK)
        {
            fprintf(stderr, "I_C_SetUserSpec error: %s\n",
            I_C_GetErrorString(rc));
            break;
        }
    }
    cryptoinlen1 = indatalen;
    cryptoin1 = indata;

    /* This function will tell us how much memory to allocate for the 
     * ciphertext.  The length will be set in encdatalen. */
        rc = I_C_CalculateOutputSizeForKey(sess,
                cipherspec, operation, cryptoinlen1, &cryptooutlen1);

    if(rc != I_E_OK) 
    {
            fprintf(stderr, "I_C_CalculateOutputSizeForKey error: %s\n",
            I_C_GetErrorString(rc));
            break;
    }

    if(cryptooutlen1 > 0){
        cryptoout1 = (I_T_BYTE *) malloc(cryptooutlen1);

        if (!cryptoout1)
        {
            fprintf(stderr, "Failed to allocate %d bytes.\n", cryptooutlen1);
            break;
        }
    }
    rc = I_C_Crypt_Enhanced(sess, cipherspec, operation,
                iv,ivlen , cryptoin1, cryptoinlen1, (I_T_BYTE*) cryptoout1, &cryptooutlen1,userspec_enc);
    if (rc != I_E_OK)
    {
        fprintf(stderr, "I_C_Crypt_Enhanced() error: %s\n",
            I_C_GetErrorString(rc));
            break;
    }
    else
    {
        switch (operation) {
            case I_T_Operation_PublicEncrypt:
            case I_T_Operation_Encrypt:
                if ((cryptoout1 != NULL) && cryptooutlen1 != 0)
                    hexprint("Encrypted Text (Hex)", cryptoout1, cryptooutlen1);
                ephemeral_key_tag = calloc(330,sizeof(char));
                rc = I_C_GetUserSpec(I_T_USPEC_EC_EPHEMERAL_KEY,ephemeral_key_tag,&ephemeral_key_tag_len,&userspec_enc);
                if (rc != I_E_OK)
                {
                    fprintf(stderr, "I_C_GetUserSpec error: %s\n",
                    I_C_GetErrorString(rc));
                    break;
                }
                if ((ephemeral_key_tag != NULL) && ephemeral_key_tag_len != 0)
                    hexprint("ephemeral key (Hex) ",ephemeral_key_tag , ephemeral_key_tag_len);
                mac_data_tag = calloc(140,sizeof(char));
                rc = I_C_GetUserSpec(I_T_USPEC_EC_MAC_DATA,mac_data_tag,&mac_data_tag_len,&userspec_enc);
                if (rc != I_E_OK)
                {
                    fprintf(stderr, "I_C_GetUserSpec error: %s\n",
                    I_C_GetErrorString(rc));
                    break;
                }
                if ((mac_data_tag != NULL) && mac_data_tag_len != 0)
                    hexprint("Mac Data (Hex) ",mac_data_tag , mac_data_tag_len);
                break;
            case I_T_Operation_Sign:
                hexprint("Signed Text (Hex)", cryptoout1, cryptooutlen1);
                break;

         }
      }
  
      if (!strncmp(algo, "SHA", 3))
      {
            operation = I_T_Operation_SignV;
            iv = cryptoout1;
            ivlen = cryptooutlen1;
            cryptoin2 = indata;
            cryptoinlen2 = indatalen;
      }
      else
      {
            //printf("phemeral_key_tag_len = %d and mac_data_tag_len = %d \n",ephemeral_key_tag_len,mac_data_tag_len);
        rc = I_C_SetUserSpec(I_T_USPEC_EC_EPHEMERAL_KEY,ephemeral_key_tag,ephemeral_key_tag_len,&userspec_dec);
        if (rc != I_E_OK)
        {
            fprintf(stderr, "I_C_SetUserSpec error: %s\n",
            I_C_GetErrorString(rc));
            break;
        }
        rc = I_C_SetUserSpec(I_T_USPEC_EC_MAC_DATA,mac_data_tag,mac_data_tag_len,&userspec_dec);
        if (rc != I_E_OK)
        {
            fprintf(stderr, "I_C_SetUserSpec error: %s\n",
            I_C_GetErrorString(rc));
            break;
        }
        operation = I_T_Operation_PrivateDecrypt;
        cryptoin2 = cryptoout1;
        cryptoinlen2 = cryptooutlen1;
      }
      if (cryptoin2 != NULL && cryptoinlen2 > 0)
      {
        rc = I_C_CalculateOutputSizeForKey(sess,
                cipherspec, operation, cryptoinlen2, &cryptooutlen2);

        if (rc != I_E_OK)
        {
            fprintf(stderr, "I_C_CalculateOutputSizeForKey error: %s\n",
                    I_C_GetErrorString(rc));
            break;
        }

        cryptoout2 = (I_T_BYTE *) malloc(cryptooutlen2);

        if (!cryptoout2)
        {
            fprintf(stderr, "Failed to allocate %d bytes.\n", cryptooutlen2);
            break;
        }
        rc = I_C_Crypt_Enhanced(sess, cipherspec, operation,
             iv,ivlen, cryptoin2, cryptoinlen2, (I_T_BYTE*) cryptoout2, &cryptooutlen2,userspec_dec);

        if (rc != I_E_OK)
        {
            fprintf(stderr, "I_C_Crypt_Enhanced() error: %s\n",
                    I_C_GetErrorString(rc));
            break;
        }
        else
        {
            switch (operation) {
                case I_T_Operation_PrivateDecrypt:
                case I_T_Operation_Decrypt:
                    hexprint("Decrypted PlainText(Hex)", cryptoout2, cryptooutlen2);
                    break;
                case I_T_Operation_SignV:
                {
                    char *result = cryptoout2;
                    if (*result == 1)
                        fprintf(stdout, "Sign Verfification Passed.\n");
                    else
                        fprintf(stdout, "Sign Verfification Failed.\n");
                }
                break;    
            }
        }
      }

   }while (0);

    if (mac_data_tag != NULL)
        free(mac_data_tag);
    if(ephemeral_key_tag != NULL)
        free(ephemeral_key_tag);
    if (cryptoout1 != NULL)
        free(cryptoout1);
    if (cryptoout2 != NULL)
        free(cryptoout2);
    if (cipherspec != NULL)
        I_C_DeleteCipherSpec(cipherspec);
    if (userspec_enc != NULL)
        I_C_DeleteUserSpec(userspec_enc);
    if (userspec_dec != NULL)
        I_C_DeleteUserSpec(userspec_dec);
    if (sess != NULL)
    I_C_CloseSession(sess);
    I_C_Fini();
    return rc;

}
