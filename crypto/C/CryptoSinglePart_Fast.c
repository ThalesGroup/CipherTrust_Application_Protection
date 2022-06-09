/*
 * CryptoSinglePart_Fast.c  
 *
 * Sample code is provided for educational purposes
 * No warranty of any kind, either expressed or implied by fact or law
 * Use of this item is not restricted by copyright or license terms
 *
 *  Crypto Sample using Single Part Data.
 *
 */
#include "thread_c.h"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

#include "cadp_capi.h"

int threadExit = 0;
void hexprint(const char* label, const I_T_BYTE *in, int len)
{
    int i;
    fprintf(stdout, "%s:", label);
    for(i = 0; i < len; i++) 
    {
        fprintf(stdout,"%2.2x ",(unsigned char)in[i]);
    }
    fprintf(stdout,"\n");
}


void usage(void)
{
    fprintf(stderr, "usage: CryptoSinglePart_Fast conf_file keyname algorithm indata iv passphrase user passwd\n"
        "\n  conf_file - typically, CADP_CAPI.properties\n"
        "  keyname - key name\n"
        "  algorithm - long algorithm name, for example, 'AES/CBC/PKCS5Padding'\n"
        "  indata - sample data to encrypt\n"
		"  iv - initialization vector when using CBC mode, not required for ECB, 'null' for null iv\n"
		"  passphrase - optional cache passphrase, 'null' for null passphrase\n"
		"  user - (optional NAE user) user can be in a root domain or in a specific domain. For domain user, specify domain||username\n"
		"  passwd - optional (mandatory if user is specified) NAE user's password\n"
    );
    exit(1);
}

#ifdef WIN32
unsigned __stdcall deleteEVP(void * state)
#else
void *deleteEVP(void * state)
#endif
{
  while(1)
  {
    I_C_DeleteEVP((I_O_CipherState *)state);
    if (threadExit == 1)
        break;
    #ifdef WIN32
        Sleep(3500);
    #else
        sleep(3500);
    #endif
  }
}

int main(int argc, char **argv)
{

    I_O_Session sess = NULL; 
	char *path = NULL, *user = NULL, *pass = NULL , *keyname = NULL, *algo = NULL;
    I_T_BYTE *indata = NULL, *iv = NULL, *cryptoin1 = NULL, *cryptoin2 = NULL, *cryptoout1 = NULL, *cryptoout2 = NULL;
    unsigned int argp = 0, ivlen = 0, indatalen = 0;
    I_T_UINT cryptoinlen1, cryptoinlen2, cryptooutlen1, cryptooutlen2;
    I_O_CipherSpec cipherspec = NULL;
    I_T_BYTE *passphrase = NULL;
    I_T_RETURN rc = I_E_OK;
    I_T_Operation operation;
    int cnt;
    I_O_CipherState st = NULL;
    ThreadHandle tid = 0; 

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

        if (!strncmp(algo, "RSA", 3))
            operation = I_T_Operation_PublicEncrypt;
        else if (!strncmp(algo, "Hmac", 3))
            operation = I_T_Operation_MAC;
        else if (!strncmp(algo, "SHA", 3))
            operation = I_T_Operation_Sign;
        else
            operation = I_T_Operation_Encrypt;


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

        cryptoout1 = (I_T_BYTE *) malloc(cryptooutlen1);

        if (!cryptoout1)
    {
            fprintf(stderr, "Failed to allocate %d bytes.\n", cryptooutlen1);
            break;
    }

    I_C_StateInit(&st);
    Thread_CreateThread(&tid, &deleteEVP, (void *)&st);

    Thread_Run(tid);

     rc = I_C_Crypt_Fast(sess, cipherspec, &st, operation,
                iv, ivlen, cryptoin1, cryptoinlen1, (I_T_BYTE*) cryptoout1, &cryptooutlen1);
     if (rc != I_E_OK)
     {
        fprintf(stderr, "I_C_CryptFast() error: %s\n",
        I_C_GetErrorString(rc));
        break;
     }
     else
     {
        hexprint("Encrypted Text (Hex)", cryptoout1, cryptooutlen1);
     }
            
     operation = I_T_Operation_Decrypt;
            cryptoin2 = cryptoout1;
            cryptoinlen2 = cryptooutlen1;

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

        rc = I_C_Crypt_Fast(sess, cipherspec, &st, operation,
                iv, ivlen, cryptoin2, cryptoinlen2, (I_T_BYTE*) cryptoout2, &cryptooutlen2);
        if (rc != I_E_OK)
        {
            fprintf(stderr, "I_C_Crypt_Fast() error: %s\n",
                    I_C_GetErrorString(rc));
            break;
        }
        else
        {
            hexprint("Decrypted Text (Hex)", cryptoout2, cryptooutlen2);
        }
    
    } while (0);

    if(tid != 0)
    {
        threadExit =1;
        if (threadExit == 1)
            Thread_Join(tid);
    }

    I_C_StateClear(&st);

    if(tid != 0)
    Thread_CloseHandles(tid);

    if (cryptoout1 != NULL)
        free(cryptoout1);
    if (cryptoout2 != NULL)
        free(cryptoout2);
    if (cipherspec != NULL)
    I_C_DeleteCipherSpec(cipherspec);
    if (sess != NULL)
    I_C_CloseSession(sess);
    I_C_Fini();
    return rc;

}
