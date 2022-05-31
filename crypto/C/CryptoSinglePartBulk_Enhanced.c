/*
 * CryptoSinglePartBulk_Enhanced.c  1.0
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

#define KEYVERSION_OVERHEAD 3   /* if using versioned key, encrypted data */
#define UTIL_FREE( x ) { if ( x != NULL ) { free( x ) ; x = NULL ; } }
#define UTIL_DELETE( x ) { if ( x != NULL ) { delete x ; x = NULL ; } }


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
    fprintf(stderr, "usage: CryptoSinglePartBulk_Enhanced conf_file keyname passphrase user passwd\n"
        "\n  conf_file - typically, CADP_CAPI.properties\n"
        "  keyname - key name\n"
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
    unsigned int argp = 0;
    I_O_CipherSpec cipherspec = NULL;
    I_T_BYTE *passphrase = NULL;
    I_T_RETURN rc = I_E_OK;
    I_T_Operation op;
    char **iv1 = NULL;
    char **input = NULL;
    char **output = NULL, **dec_output = NULL;
    I_T_UINT *inlens= NULL, *outlens= NULL,*declens=NULL;

    int i, j=0, repeat=8;                                                        
    I_T_IVType ivflag = I_T_IV_Single;
    I_T_BOOL Error_f = 1;
    int outputsize = 0;
    I_T_UINT cryptoinlen1, cryptoinlen2, cryptooutlen1, cryptooutlen2;


    // Input  data

      char in[8][10]={"1234","5678","abcd","efghzzz","ijkl","mnop","0101","0202"};

     // in   case want to use IV per element
   // char ivarr[8][16]={"1234567812345678","1234567812345678","1234567812345678","1234567812345678","1234567812345678","1234567812345678","1234567812345678","1234567812345678"};
    unsigned int ivlen = 0;


    do
    {

      if (argc < 3)
      usage(); // exit

      argp = 1;
      path  = argv[argp++];
      keyname = argv[argp++];
     algo = "RSA";
     //algo = "AES";
      // optional cache passphrase
      if (argc > 3)
	{
	   if(strncmp(argv[argp],"null",4) != 0)
                passphrase = (I_T_BYTE*)argv[argp];
		argp++;
		if(argc == 5)
		{
			usage();
		    exit(0);
		}
		if(argc > 5 )
		{
			user = argv[argp++];
			pass = argv[argp++];
		}
	}


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

   // allocate memory for inputdata, outputdata, decrypteddata 
    input = (char **) calloc (repeat,sizeof (char *));
    inlens = (I_T_UINT *) calloc (repeat, sizeof (I_T_UINT));
    output = (char **) calloc (repeat, sizeof (char *));
    outlens = (I_T_UINT *) calloc (repeat, sizeof (I_T_UINT));
    dec_output = (char **)calloc(repeat,sizeof(char *));
    declens = (I_T_UINT *) calloc (repeat, sizeof (I_T_UINT));
    //iv1 = (char **) calloc (repeat, sizeof (char *));


    // operation (need to change if using RSA)
  op = I_T_Operation_PublicEncrypt;
  //op = I_T_Operation_Encrypt;
	
	
   if(op == I_T_Operation_PublicEncrypt)
	{
		
	 	cryptoinlen1 = strlen(in[0]);
 		rc = I_C_CalculateOutputSizeForKey(sess,
                cipherspec, op, cryptoinlen1, &cryptooutlen1);

        if(rc != I_E_OK)
        {
            fprintf(stderr, "I_C_CalculateOutputSizeForKey error: %s\n",
            I_C_GetErrorString(rc));
            break;
        }
	 for (i = 0; i < repeat; i++)
  	{
   /* This function will tell us how much memory to allocate for the
 *        * ciphertext.  The length will be set in encdatalen. */

               input[i] = (char *) malloc (strlen(in[i]));
               inlens[i] = strlen(in[i]);
               output[i] = (char *) malloc (cryptooutlen1);
               outlens[i] = cryptooutlen1;
               memcpy(input[i],in[i],cryptoinlen1);

 	 }

       }	
   else
	{
	
   	 	for (i = 0; i < repeat; i++)
    		{
       		cryptoinlen1 = strlen(in[i]);
	
   /* This function will tell us how much memory to allocate for the 
     * ciphertext.  The length will be set in encdatalen. */
      		 rc = I_C_CalculateOutputSizeForKey(sess, cipherspec, op, cryptoinlen1, &cryptooutlen1);

        	if(rc != I_E_OK) 
       		 {
            		fprintf(stderr, "I_C_CalculateOutputSizeForKey error: %s\n",
            		I_C_GetErrorString(rc));
           		 break;
       		 }

        	input[i] = (char *) malloc (cryptoinlen1);
        	inlens[i] = cryptoinlen1;
        	output[i] = (char *) malloc (cryptooutlen1);
        	outlens[i] = cryptooutlen1;
        	memcpy(input[i],in[i],cryptoinlen1);
     
        // ivlen = 16;
        // iv1[i] = (char *) malloc(ivlen);
        // memcpy(iv1[i],ivarr[i],ivlen);

    		}// end of for loop */
	if(rc != I_E_OK)
        break;

	}


        //API call for Encryption
        j++;
        rc = I_C_CryptBulk_Enhanced(sess, cipherspec, op, repeat, ivflag,
                            (const I_T_BYTE **) iv1, ivlen,
                            (const I_T_BYTE **) input, inlens,
                            (I_T_BYTE **) output, outlens,I_T_Uspec_Single,NULL);
        if (rc != I_E_OK)
        {
            I_T_RETURN err;
            I_C_GetLastError (sess, &err);
            fprintf (stderr, "I_C_CryptBulk_Enhanced()#%d returned %d (%s)\n", j,
                         rc, I_C_GetErrorString (err));
            break;
        }
	for(i=0;i<repeat;i++)
	{
           hexprint("Encrypted Text(Hex)", output[i], outlens[i]);
        }	

   /* now decrypt what we encrypted: (need to change for RSA)*/
    switch (op)
    {
        case I_T_Operation_Encrypt:
            op = I_T_Operation_Decrypt;
		break;
	
	case  I_T_Operation_PublicEncrypt:
           	op = I_T_Operation_PrivateDecrypt;
            break;
    }
     

	if(op == I_T_Operation_PrivateDecrypt)
	{
        	cryptoinlen2 = outlens[0];

        /* This function will tell us how much memory to allocate for the
         * ciphertext.  The length will be set in encdatalen.*/
         	rc = I_C_CalculateOutputSizeForKey(sess,
                cipherspec, op, cryptoinlen2, &cryptooutlen2);

         	if(rc != I_E_OK)
           	{
            	fprintf(stderr, "I_C_CalculateOutputSizeForKey error: %s\n",
            	I_C_GetErrorString(rc));
            	break;
           	}

		for (i = 0; i < repeat; i++)
   		 {
        		declens[i] = cryptooutlen2;
           		dec_output[i] = (char*)malloc(cryptooutlen2);
   		 }
	}
	else
	{
		 for (i = 0; i < repeat; i++)
		  {
			 cryptoinlen2 = outlens[i];
			 rc = I_C_CalculateOutputSizeForKey(sess,cipherspec, op, cryptoinlen2, &cryptooutlen2);

                	if(rc != I_E_OK)
               		 {
                		fprintf(stderr, "I_C_CalculateOutputSizeForKey error: %s\n",
                		I_C_GetErrorString(rc));
                		break;
               		 }

                	declens[i] = cryptooutlen2;
                        dec_output[i] = (char*)malloc(cryptooutlen2);
		   }

			 if(rc != I_E_OK)
       			 break;
	   }

        //API call for Decryption
        j++;
        rc = I_C_CryptBulk_Enhanced(
                 sess,
                 cipherspec,
                 op,
                 repeat,
                 ivflag,
                 (const I_T_BYTE **)iv1,
                 ivlen,
                 (const I_T_BYTE **)output,
                 outlens,
                 (I_T_BYTE **)dec_output,
                 declens,
                 I_T_Uspec_Single,NULL);
        if (rc != I_E_OK)
        {
            I_T_RETURN err;
            I_C_GetLastError(sess,&err);
            fprintf(stderr,"I_C_CryptBulk_Enhanced()#%d returned %d (%s)\n",j,
                rc,I_C_GetErrorString(err));
             break;
        }

       for (i = 0; i < repeat; i++)
       {
          if(strncmp(input[i],dec_output[i], inlens[i]))
          {
            fprintf(stderr,"Decrypted text is not matching with original "
                "plain text for bulk operation\n");
            Error_f = 0;
          }
       }
       if(Error_f  == 1)
       {
          fprintf(stderr,("Bulk operation Passed \n"));
       }

	for(i=0;i<repeat;i++)
        {
           hexprint("Decrypted plainText(Hex)",dec_output[i], declens[i]);
                                            
         }
                       
}while(0);

   if(input)
   {
    for (i = 0; i < repeat; i++)
    {
      UTIL_FREE(input[i]);
      UTIL_FREE(dec_output[i]);
      UTIL_FREE(output[i]);
    }
    UTIL_FREE(input);
    UTIL_FREE(output);
    UTIL_FREE(dec_output);
    UTIL_FREE(inlens);
    UTIL_FREE(outlens);
    UTIL_FREE(declens);
   }

    if (cipherspec != NULL)
    I_C_DeleteCipherSpec(cipherspec);
    if (sess != NULL)
    I_C_CloseSession(sess);
    I_C_Fini();
    return rc;

}
