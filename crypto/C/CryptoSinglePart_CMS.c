/*
 * CryptoSinglePart_CMS.c
 *
 * Sample code is provided for educational purposes
 * No warranty of any kind, either expressed or implied by fact or law
 * Use of this item is not restricted by copyright or license terms
 *
 *  Crypto Sample for CMS format sign verify using Single Part Data.
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
    //for(i = 0; i < len && i < 80; i++) 
    for(i = 0; i < len; i++) 
    {
        fprintf(stdout,"%2.2x ",(unsigned char)in[i]);
    }
    fprintf(stdout,"\n");
}


void usage(void)
{
    fprintf(stderr, "usage: ./CryptoSinglePart_CMS conf_file keyname algorithm indata passphrase user passwd certlist \n"
        "\n  conf_file - typically, CADP_CAPI.properties\n"
        "  keyname - key name\n"
        "  algorithm - long algorithm name, for example, 'SHA1withRSA'\n"
        "  indata - sample data to encrypt\n"
        "  passphrase - optional cache passphrase, 'null' for null passphrase\n"
	"  user - (optional NAE user) user can be in a root domain or in a specific domain. For domain user, specify domain||username\n"
	"  passwd - optional (mandatory if user is specified) NAE user's password\n"
        "  format - CMS format to be used. For example: 'cms/detached/der/enveloped', 'cms/detached/der', 'cms/detached/smime/enveloped', 'cms/detached/smime'. Only these formats are supported \n"
        "  certlist – List of CA from which certificate used for sign verify is signed. List should be , separated \n"  
    );
    exit(1);
}

int main(int argc, char **argv)
{

    I_O_Session sess = NULL; 
    char *path = NULL, *user = NULL, *pass = NULL , *keyname = NULL, *algo = NULL;
    I_T_BYTE *indata = NULL, *cryptoin1 = NULL, *cryptoin2 = NULL, *cryptoout1 = NULL, *cryptoout2 = NULL;
    I_T_BYTE *passphrase = NULL;
    char *certlist = NULL, *format = NULL;
    char*  iv = NULL;
    unsigned int argp = 0, ivlen = 0, indatalen = 0;
    I_T_UINT cryptoinlen1, cryptoinlen2, cryptooutlen1, cryptooutlen2;
    I_O_CipherSpec cipherspec = NULL;
    I_O_UserSpec userspec = NULL;
    I_T_RETURN rc = I_E_OK;
    I_T_Operation operation;
    int *len = NULL;

    do
    {

        if (argc <= 6)
           usage(); // exit

        argp = 1;
        path  = argv[argp++];
        keyname = argv[argp++];
        algo = argv[argp++];
        indata = (I_T_BYTE*)argv[argp++];

	if(strncmp(argv[argp],"null",4) != 0)
            passphrase = (I_T_BYTE*)argv[argp];
	argp++;
	user = argv[argp++];
	pass = argv[argp++];
	       if(argc <= 9)
	       {
		    usage();
		    exit(0);
	       }
               format = argv[argp++]; 
	       certlist = argv[argp];
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

    rc = I_C_SetUserSpec(I_T_USPEC_FORMAT,format,strlen(format),&userspec);
    if (rc != I_E_OK)
    {
        fprintf(stderr, "I_C_SetUserSpec error: %s\n",
            I_C_GetErrorString(rc));
            break;
    }

     operation = I_T_Operation_Sign;;


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
                iv,ivlen , cryptoin1, cryptoinlen1, (I_T_BYTE*) cryptoout1, &cryptooutlen1,userspec);
    if (rc != I_E_OK)
    {
        fprintf(stderr, "I_C_Crypt_Enhanced() error: %s\n",
            I_C_GetErrorString(rc));
            break;
    }
    else
    {
            switch (operation) {
                case I_T_Operation_Sign:
                    hexprint("Signed Text or MAC (Hex)", cryptoout1, cryptooutlen1);
                    break;
            }
    }
     //DECRYPT operation 
      operation = I_T_Operation_SignV;
      iv = cryptoout1;
      ivlen = cryptooutlen1;
      cryptoin2 = indata;
      cryptoinlen2 = indatalen;

      rc = I_C_SetUserSpec(I_T_USPEC_CERTLIST,certlist,strlen(certlist),&userspec);
      if (rc != I_E_OK)
      {
        fprintf(stderr, "I_C_SetUserSpec error: %s\n",
            I_C_GetErrorString(rc));
            break;
      }

      if (cryptoout1 != NULL && cryptooutlen1 > 0)
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
             iv,ivlen, cryptoin2, cryptoinlen2, (I_T_BYTE*) cryptoout2, &cryptooutlen2,userspec);

        if (rc != I_E_OK)
        {
            fprintf(stderr, "I_C_Crypt_Enhanced() error: %s\n",
                    I_C_GetErrorString(rc));
            break;
        }
        else
        {
            switch (operation) {
                case I_T_Operation_SignV:
                {
                    char *result = cryptoout2;
                    if (*result == 1)
                        fprintf(stdout, "Sign or MAC Verfification Passed.\n");
                    else
                        fprintf(stdout, "Sign or MAC Verfification Failed.\n");
                }
                    break;
            }
        }
      }

   }while (0);

    if (cryptoout1 != NULL)
        free(cryptoout1);
    if (cryptoout2 != NULL)
        free(cryptoout2);
    if (cipherspec != NULL)
    I_C_DeleteCipherSpec(cipherspec);
    I_C_DeleteUserSpec(userspec);
    if (sess != NULL)
    I_C_CloseSession(sess);
    I_C_Fini();
    return rc;

}
