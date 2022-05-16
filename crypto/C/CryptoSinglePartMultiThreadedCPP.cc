/*
 * CryptoSinglePartMultiThreadedCPP.c  
 *
 * Sample code is provided for educational purposes
 * No warranty of any kind, either expressed or implied by fact or law
 * Use of this item is not restricted by copyright or license terms
 *
 *  Crypto C++ Sample using Single Part Data in MultiThreaded mode.
 *
 */

#include "thread.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "cadp_capi.h"


class CryptoParameters
{
public:
    I_O_Session sess;
    I_O_CipherSpec cipherspec;
    I_T_BYTE *indata, *iv, *encdata;
    int ivlen, indatalen;
    I_T_UINT encdatalen;
};

void hexprint (const I_T_BYTE *in, int len)
{
    int i;
    for(i = 0; i < len && i < 80; i++) {
           fprintf(stdout,"%2.2x ",(unsigned char)in[i]);
    }
    fprintf(stdout,"\n");
}


void usage(void)
{
        fprintf(stderr, "usage: CryptoSinglePartMultiThreadedCPP conf_file keyname algorithm indata iv passphrase user passwd\n"
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



void threadMain(void *arg1, void *arg2)
{
    I_T_RETURN rc;
    char *threadid = (char*)arg1;
    CryptoParameters *cp = (CryptoParameters*)arg2;
    printf("Starting thread (%s).\n", threadid);
    rc = I_C_Crypt(cp->sess, cp->cipherspec,I_T_Operation_Encrypt,
            		cp->iv, cp->ivlen, cp->indata, cp->indatalen,
	   		(I_T_BYTE*)cp->encdata,&cp->encdatalen);

    if (rc != I_E_OK) {
        fprintf(stderr, "I_C_Crypt() error: %s\n",
                I_C_GetErrorString(rc));
    }
    else
    {
          printf("Thread (%s) successfully encrypted the data.\n", threadid);
        // print output in hex:
        hexprint(cp->encdata, cp->encdatalen);
    }


}

int main(int argc, char **argv)
{
    const int NumThreads = 100;

    I_T_UINT   passphraseLength = 0;
    BaseThread **threads = 
	new BaseThread*[NumThreads];
    CryptoParameters **cps =  new CryptoParameters*[NumThreads];

	I_O_Session sess; 
	char *path = NULL, *user = NULL, *pass = NULL , *keyname = NULL, *algo = NULL;
    I_T_BYTE *indata = NULL, *iv = NULL, *encdata = NULL;
    unsigned int argp = 0, ivlen = 0, indatalen = 0;
    I_T_UINT encdatalen = 0;
    I_O_CipherSpec cipherspec[NumThreads];
    I_T_BYTE *passphrase = NULL;
    I_T_RETURN rc = I_E_OK;
    
	if (argc < 5)
        usage(); // exit

    argp = 1;
    path  = argv[argp++];
    keyname = argv[argp++];
    algo = argv[argp++];
    indata = (I_T_BYTE*)argv[argp++];
    char **data = new char*[NumThreads];

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
        I_C_Fini();
        return rc;
    }
    int i=0;

    for (i = 0; i < NumThreads; i++)
    {
    rc = I_C_CreateCipherSpec(algo,keyname,&cipherspec[i]);

    if (rc != I_E_OK) {
        fprintf(stderr, "I_C_CreateCipherSpec error: %s\n",
                I_C_GetErrorString(rc));
        I_C_CloseSession(sess);
        I_C_Fini();
        return rc;
    }
    /* This function will tell us how much memory to allocate for the
 *      * ciphertext.  The length will be set in encdatalen. */
    rc = I_C_CalculateEncipheredSizeForKey(sess,
            cipherspec[i],I_T_Operation_Encrypt,indatalen,&encdatalen);

    if(rc != I_E_OK) {
        fprintf(stderr, "I_C_CalculateEncipheredSizeForKey error: %s\n",
                I_C_GetErrorString(rc));
        I_C_DeleteCipherSpec(cipherspec[i]);
        I_C_CloseSession(sess);
        I_C_Fini();
        return rc;
    }

 
        cps[i] = new CryptoParameters;
        cps[i]->sess = sess;
        cps[i]->cipherspec = cipherspec[i];
        cps[i]->indata = indata;
        cps[i]->iv = iv;
        cps[i]->encdata = new I_T_BYTE[encdatalen];

       if (!cps[i]->encdata)
       {
          fprintf(stderr,"Failed to allocate %d bytes.\n", encdatalen);
          I_C_DeleteCipherSpec(cipherspec[i]);
          I_C_CloseSession(sess);
          I_C_Fini();
          exit(1);
       }

        cps[i]->ivlen = ivlen;
        cps[i]->indatalen = indatalen;
        cps[i]->encdatalen = encdatalen;
        cps[i]->cipherspec = cipherspec[i];
    }


    for (i = 0; i < NumThreads; i++)
    {
	    data[i] = (char *)new char[30];
	    sprintf(data[i], "%d", i);
	    threads[i] = new BaseThread((BaseThread::ThreadRoutine)threadMain, 
					(BaseThread::ThreadRoutineParam)data[i],
					(BaseThread::ThreadRoutineParam)cps[i]);
	    threads[i]->init();
    }
    for (i=0; i<NumThreads; i++)
	    threads[i]->run();

    for (i=0; i<NumThreads; i++)
    {	    
        threads[i]->join();
    }

    for (i=0; i<NumThreads; i++)
    {
        delete []data[i];
	delete threads[i];
    } 
    delete [] data;
    delete [] threads;

    for (i=0; i<NumThreads; i++)
    {
        delete [] cps[i]->encdata;
	delete cps[i];
    I_C_DeleteCipherSpec(cipherspec[i]);
    }
    delete [] cps;
    I_C_CloseSession(sess);
    I_C_Fini();

    printf("\nEnding CryptoSinglePartMultiThreadedCPP program with multiple threads\n");
    return 0;
}
