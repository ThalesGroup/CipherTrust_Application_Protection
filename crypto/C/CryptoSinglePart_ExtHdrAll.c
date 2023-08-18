/*
 * CryptoSinglePart_ExtHdrAll.c  
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

#define VERSION_HEADER_SIZE 3

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
    fprintf(stderr, "usage: CryptoSinglePart_ExtHdrAll conf_file keyname algorithm indata iv passphrase user passwd headerMode taglen aaddata\n"
        "  conf_file - typically, CADP_CAPI.properties\n"
        "  keyname - key name\n"
        "  algorithm - long FPE algorithm name only , for example, 'FPE/AES/CARD10'\n"
        "  indata - sample data to encrypt based on cardinality \n"
        "  iv - initialization vector (cardinality based),len is BLOCKSIZE*2(hex encoded charactes): BLOCKSIZE for CARD10=56 CARD26=40 CARD62=32\n"
            "       IV is required when indata len >BLOCKSIZE ,else IV not required, 'null' for null iv.\n"
            "       IV is not required incase of FPE/FF3/ algorithm.\n"
            "  passphrase - optional cache passphrase, 'null' for null passphrase\n"
        "  user - (optional NAE user) user can be in a root domain or in a specific domain. For domain user, specify domain||username\n"
        "  passwd - optional (mandatory if user is specified) NAE user's password\n"
        "  headerMode - Version Header Mode (for versionkey mode value should be always 1 or 2)\n"
        "               headerMode = 0 (Default - INTERNAL_HEADER) \n"
        "               headerMode = 1 (EXTERNAL_HEADER : version key header stored in userSpec.)\n"
        "               headerMode = 2 (INTERNAL_HEADER : version key header adjust in cipher data.)\n"
        "  tagLen – Length of authentication tag, should be between 4 - 16 bytes ... in case of GCM\n"  
        "  aad_data - Additional authenticated data. (Optional) ... for GCM\n" 
    );
    exit(1);
}

int main(int argc, char **argv)
{

    I_O_Session sess = NULL; 
    char *path = NULL, *user = NULL, *pass = NULL , *keyname = NULL, *algo = NULL;
    I_T_BYTE *indata = NULL, *cryptoin1 = NULL, *cryptoin2 = NULL, *cryptoout1 = NULL, *cryptoout2 = NULL;
    char *header_mode = NULL, *iv = NULL, *aad_data = NULL, *authtag_len = NULL, *tag_temp = NULL, *tag_verify = NULL;
    I_T_BYTE *passphrase = NULL;
    unsigned int argp = 0, ivlen = 0, indatalen = 0, header_mode_len = 0;
    I_T_UINT cryptoinlen1, cryptoinlen2, cryptooutlen1, cryptooutlen2;
    I_O_CipherSpec cipherspec = NULL;
    I_O_UserSpec userspec = NULL;
    I_T_RETURN rc = I_E_OK;
    I_T_Operation operation;
    unsigned char *ver_header = NULL;
    int ver_header_len = 0, taglen = 0, len = 0;

    do
    {

       if (argc < 5)
       usage(); // exit

        argp = 1;
        path  = argv[argp++];
        keyname = argv[argp++];
        algo   =  argv[argp++];

        indata = (I_T_BYTE*)argv[argp++];

        if(argc > 5) {
            if(strncmp(argv[argp],"null",4) != 0)
                iv = (I_T_BYTE*)argv[argp];
            argp++;
            if (argc > 6) {
                if (argc <= 8) {
                    usage();
                    exit(0);
                }
                if (argc > 8) {
                    if(strncmp(argv[argp],"null",4) != 0)
                        passphrase = (I_T_BYTE*)argv[argp];
                    argp++;
                    user = argv[argp++];
                    pass = argv[argp++];
                                     
                    if (argc > 9) {
                        if(strncmp(argv[argp],"null",4) != 0)
                            header_mode = argv[argp];
                        argp++;
                    }
                    if (strstr(algo,"AES/GCM") != NULL) {
                        if(argc > 10 ) {
                            if(strncmp(argv[argp],"null",4) != 0)
                                authtag_len = argv[argp];
                            argp++;
                        }
                        if(argc > 11 ) {
                            if(strncmp(argv[argp],"null",4) != 0)
                                aad_data = argv[argp];
                            argp++;
                        }
                    }
                }
            }
        }

        if (iv)
            ivlen = (unsigned int)strlen((char *)iv);

        indatalen = (unsigned int)strlen((char *)indata);

        if(header_mode)
           header_mode_len = strlen(header_mode);

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

        if (authtag_len) {
            rc = I_C_SetUserSpec(I_T_USPEC_AUTHTAGLEN, authtag_len, sizeof(authtag_len), &userspec);
            if (rc != I_E_OK) {
                fprintf(stderr, "I_C_SetUserSpec error: %s\n",
                    I_C_GetErrorString(rc));
                    break;
            }
        }

        if (aad_data != NULL) {
            rc = I_C_SetUserSpec(I_T_USPEC_AADDATA, aad_data, strlen(aad_data), &userspec);
            if (rc != I_E_OK) {
                fprintf(stderr, "I_C_SetUserSpec error: %s\n",
                    I_C_GetErrorString(rc));
                    break;
            }
        }

        if(header_mode) {
            rc = I_C_SetUserSpec(I_T_USPEC_VERSION_HEADER_MODE, header_mode, header_mode_len,&userspec);

        if (rc != I_E_OK) {
            fprintf(stderr, "I_C_SetUserSpec error: %s\n",
                I_C_GetErrorString(rc));
                break;
        }
	}

        operation = I_T_Operation_Encrypt;
        cryptoinlen1 = indatalen;
        cryptoin1 = indata;

        rc = I_C_CalculateOutputSizeForKey(sess, cipherspec, operation, cryptoinlen1, &cryptooutlen1);
        if(rc != I_E_OK) {
                fprintf(stderr, "I_C_CalculateOutputSizeForKey error: %s\n",
                I_C_GetErrorString(rc));
                break;
        }

        cryptoout1 = (I_T_BYTE *) calloc(cryptooutlen1,sizeof(I_T_BYTE));
        if (!cryptoout1) {
            fprintf(stderr, "Failed to allocate %d bytes.\n", cryptooutlen1);
            break;
        }

        hexprint("Plain Text (Hex)          ", cryptoin1, cryptoinlen1);

        rc = I_C_Crypt_Enhanced(sess, cipherspec, operation,
                    iv, ivlen, cryptoin1, cryptoinlen1, (I_T_BYTE*) cryptoout1, &cryptooutlen1,userspec);
        if (rc != I_E_OK) {
            fprintf(stderr, "I_C_Crypt_Enhanced() error: %s\n",
                I_C_GetErrorString(rc));
                break;
        }
        else
        {
            switch (operation) {
                case I_T_Operation_PublicEncrypt:
                case I_T_Operation_Encrypt:
                    hexprint("Encrypted Text (Hex)      ", cryptoout1, cryptooutlen1);
                    break;
             }

            if (authtag_len && atoi(authtag_len)  > 0)
            {
               tag_temp = (char *)malloc(atoi(authtag_len) );
               taglen = 0;

                rc = I_C_GetUserSpec(I_T_USPEC_AUTHTAG ,tag_temp, &taglen, &userspec);
                if (rc != I_E_OK) {
                    fprintf(stderr, "I_C_GetUserSpec error: %s\n",
                    I_C_GetErrorString(rc));
                    break;
                }
            }
        }

        if(header_mode)
        {
            ver_header = calloc(VERSION_HEADER_SIZE +1,sizeof(char));
            rc = I_C_GetUserSpec(I_T_USPEC_VERSION_HEADER,ver_header,&ver_header_len,&userspec);
            if (rc != I_E_OK)
            {
               fprintf(stderr, "I_C_GetUserSpec error: %s\n",
               I_C_GetErrorString(rc));
               break;
            }
            if (ver_header  != NULL && ver_header_len > 0)
            {
               hexprint("Version Header (Hex)      ", ver_header, ver_header_len);
            }
        }
         //DECRYPT operation 

        if (tag_temp != NULL) {
            rc = I_C_SetUserSpec(I_T_USPEC_AUTHTAG, tag_temp, taglen, &userspec);
            if (rc != I_E_OK) {
                fprintf(stderr, "I_C_SetUserSpec error: %s\n",
                I_C_GetErrorString(rc));
                break;
            }
        }
        operation = I_T_Operation_Decrypt;
        cryptoin2 = cryptoout1;
        cryptoinlen2 = cryptooutlen1;

        rc = I_C_CalculateOutputSizeForKey(sess, cipherspec, operation, cryptoinlen2, &cryptooutlen2);
        if (rc != I_E_OK) {
            fprintf(stderr, "I_C_CalculateOutputSizeForKey error: %s\n",
                    I_C_GetErrorString(rc));
            break;
        }

        cryptoout2 = (I_T_BYTE *) calloc(cryptooutlen2,sizeof(I_T_BYTE));
        if (!cryptoout2) {
            fprintf(stderr, "Failed to allocate %d bytes.\n", cryptooutlen2);
            break;
        }

        if(ver_header != NULL && ver_header_len > 0) {
           rc = I_C_SetUserSpec(I_T_USPEC_VERSION_HEADER, ver_header,ver_header_len, &userspec);
           if (rc != I_E_OK) {
              fprintf(stderr, "I_C_SetUserSpec error: %s\n",
              I_C_GetErrorString(rc));
              break;
           }
        }

        rc = I_C_Crypt_Enhanced(sess, cipherspec, operation,
                    iv, ivlen, cryptoin2, cryptoinlen2, (I_T_BYTE*) cryptoout2, &cryptooutlen2,userspec);

        if (rc != I_E_OK) {
            fprintf(stderr, "I_C_Crypt_Enhanced() error: %s\n",
                    I_C_GetErrorString(rc));
            break;
        }
        else
        {
            switch (operation) {
                case I_T_Operation_PrivateDecrypt:
                case I_T_Operation_Decrypt:
                    hexprint("Decrypted Text (Hex)      ", cryptoout2, cryptooutlen2);
                    break;
            }

            if (authtag_len) {
                tag_verify = calloc(2, sizeof(char));
                rc = I_C_GetUserSpec(I_T_USPEC_AUTHTAG_VERIFY, tag_verify, &len, &userspec);
                if (rc != I_E_OK) {
                   fprintf(stderr, "I_C_GetUserSpec error: %s\n",
                   I_C_GetErrorString(rc));
                   break;
                }
                if (tag_verify  != NULL) {
                   int verify = atoi(tag_verify);
                   printf("Tag verify %s\n",verify>0?"Successful":"Failed");
                   free(tag_verify);
                }
            }
        }

   } while (0);

    if(ver_header)
       free(ver_header);
    ver_header = NULL;

    if (cryptoout1 != NULL)
        free(cryptoout1);
    if (cryptoout2 != NULL)
        free(cryptoout2);
    if (cipherspec != NULL)
        I_C_DeleteCipherSpec(cipherspec);
    if(userspec)
       I_C_DeleteUserSpec(userspec);
    if (sess != NULL)
       I_C_CloseSession(sess);
    I_C_Fini();
    return rc;

}
