/*
 * CryptoSinglePart_FPE_CC_SSN.c  
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


static char asciiToHex[] = {
// 0                    4                    8                    c                 //hi
0xff,0xff,0xff,0xff, 0xff,0xff,0xff,0xff, 0xff,0xff,0xff,0xff ,0xff,0xff,0xff,0xff,// 0
0xff,0xff,0xff,0xff, 0xff,0xff,0xff,0xff, 0xff,0xff,0xff,0xff ,0xff,0xff,0xff,0xff,// 1
0xff,0xff,0xff,0xff, 0xff,0xff,0xff,0xff, 0xff,0xff,0xff,0xff ,0xff,0xff,0xff,0xff,// 2
0x00,0x01,0x02,0x03, 0x04,0x05,0x06,0x07, 0x08,0x09,0xff,0xff ,0xff,0xff,0xff,0xff,// 3
0xff,0x0a,0x0b,0x0c, 0x0d,0x0e,0x0f,0xff, 0xff,0xff,0xff,0xff ,0xff,0xff,0xff,0xff,// 4
0xff,0xff,0xff,0xff, 0xff,0xff,0xff,0xff, 0xff,0xff,0xff,0xff ,0xff,0xff,0xff,0xff,// 5
0xff,0x0a,0x0b,0x0c, 0x0d,0x0e,0x0f,0xff, 0xff,0xff,0xff,0xff ,0xff,0xff,0xff,0xff,// 6
0xff,0xff,0xff,0xff, 0xff,0xff,0xff,0xff, 0xff,0xff,0xff,0xff ,0xff,0xff,0xff,0xff,// 7
0xff,0xff,0xff,0xff, 0xff,0xff,0xff,0xff, 0xff,0xff,0xff,0xff ,0xff,0xff,0xff,0xff,// 8
0xff,0xff,0xff,0xff, 0xff,0xff,0xff,0xff, 0xff,0xff,0xff,0xff ,0xff,0xff,0xff,0xff,// 9
0xff,0xff,0xff,0xff, 0xff,0xff,0xff,0xff, 0xff,0xff,0xff,0xff ,0xff,0xff,0xff,0xff,// a
0xff,0xff,0xff,0xff, 0xff,0xff,0xff,0xff, 0xff,0xff,0xff,0xff ,0xff,0xff,0xff,0xff,// b
0xff,0xff,0xff,0xff, 0xff,0xff,0xff,0xff, 0xff,0xff,0xff,0xff ,0xff,0xff,0xff,0xff,// c
0xff,0xff,0xff,0xff, 0xff,0xff,0xff,0xff, 0xff,0xff,0xff,0xff ,0xff,0xff,0xff,0xff,// d
0xff,0xff,0xff,0xff, 0xff,0xff,0xff,0xff, 0xff,0xff,0xff,0xff ,0xff,0xff,0xff,0xff,// e
0xff,0xff,0xff,0xff, 0xff,0xff,0xff,0xff, 0xff,0xff,0xff,0xff ,0xff,0xff,0xff,0xff,// f
};


int ConvertAsciiToPackedHex(char *asciiDigitArrayPtr, char *packedHexArrayPtr, int numOfDigits)
{
    int digitCount;

    for(digitCount = 0; digitCount < numOfDigits; digitCount++)
    {
      /* check if non-hex digit */
                  if((char)asciiToHex[(int) *asciiDigitArrayPtr] < 0)
      {
                                return 0;
      }

      /* digit count is zero-based, so even counts are same as odd no of digits */
      if ((digitCount % 2) == 0)   /* check if even counts (ie. zero remainder) */
      {
        *packedHexArrayPtr &= 0x0F;                                    /* clear top nibble */
        *packedHexArrayPtr |= asciiToHex[(int) *asciiDigitArrayPtr] << 4;    /* move to top nibble */
      }
      else
      {
        *packedHexArrayPtr &= 0xF0;                                    /* clear bottom nibble */
        *packedHexArrayPtr |= asciiToHex[(int) *asciiDigitArrayPtr];         /* move to bottom nibble */
        packedHexArrayPtr++;                                 /* increment on every second digit */
      }
      asciiDigitArrayPtr++;
                }
    return 1;
}

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

void printtext(const char* label, const I_T_BYTE *in, int len)
{
    int i;
    fprintf(stdout, "%s:", label);
    for(i = 0; i < len && i < 80; i++) 
    {
        fprintf(stdout,"%c ",(unsigned char)in[i]);
    }
    fprintf(stdout,"\n");
}


void usage(void)
{

    fprintf(stderr, "usage: CryptoSinglePart_FPE_CC_SSN conf_file keyname algorithm indata iv passphrase user passwd tweakalgo tweakdata headerMode\n"
        "\n  conf_file - typically, CADP_CAPI.properties\n"
        "  keyname - key name\n"
		"  algorithm - long FPE algorithm name only , current support: 'FPE/AES, FPE/FF1v2 and FPE/FF3-1' with CARD10, CARD26 and CARD62 only\n"
        "  indata - sample data to encrypt based on cardinality \n"
	"  iv - initialization vector,not required, 'null'\n"
        "  passphrase - optional cache passphrase, 'null' for null passphrase\n"
	"  user - (optional NAE user) user can be in a root domain or in a specific domain. For domain user, specify domain||username\n"
	"  passwd - optional (mandatory if user is specified) NAE user's password\n"
	"  tweakalgo - optional  Tweak algorithm\n"
	"  tweakdata - optional  Tweak data value:Hex encoded string(16 character) if tweakalgo= NONE, otherwise ASCII\n"
        "  headerMode - Version Header Mode (for versionkey mode value should be always 1  i.e. EXTERNAL_HEADER)\n"
        "               headerMode = 0 (NONE)\n"
        "               headerMode = 1 (EXTERNAL_HEADER : version key header stored in userSpec.)\n"
        "               headerMode = 2 (INTERNAL_HEADER : version key header adjust in cipher data. But not supported right now.)\n"
    );
    exit(1);
}

int main(int argc, char **argv)
{

    I_O_Session sess = NULL; 
    char *path = NULL, *user = NULL, *pass = NULL , *keyname = NULL, *algo = NULL;
    I_T_BYTE *indata = NULL, *cryptoin1 = NULL, *cryptoin2 = NULL, *cryptoout1 = NULL, *cryptoout2 = NULL;
    char *tweakdata = NULL,*tweakalgo = NULL,*inp_iv= NULL, *header_mode = NULL;
    char*  iv = NULL;
    I_T_BYTE *passphrase = NULL;
    unsigned int argp = 0, ivlen = 0, indatalen = 0,tweakdata_len = 0,tweakalgo_len=0, header_mode_len = 0;
    I_T_UINT cryptoinlen1, cryptoinlen2, cryptooutlen1, cryptooutlen2;
    I_O_CipherSpec cipherspec = NULL;
    I_O_UserSpec userspec = NULL;
    I_T_RETURN rc = I_E_OK;
    I_T_Operation operation;
    unsigned char *ver_header = NULL;
    int ver_header_len = 0;

    do
    {

       if (argc < 5)
       usage(); // exit

    argp = 1;
    path  = argv[argp++];
    keyname = argv[argp++];
    algo   =  argv[argp++];
    if(strstr(algo,"FPE")==NULL)
     {
        fprintf(stderr, "Invalid algorithm=%s passed for sample \n",algo);
        exit(0);
     }

    indata = (I_T_BYTE*)argv[argp++];

	if(argc > 5)
	{
	    if(strncmp(argv[argp],"null",4) != 0)
	        inp_iv = (I_T_BYTE*)argv[argp];
		argp++;
               if (argc > 6)
		{
			if(argc <= 8)
			{
		            usage();
			    exit(0);
			}
			if(argc > 8 )
			{
                               if(strncmp(argv[argp],"null",4) != 0)
                                   passphrase = (I_T_BYTE*)argv[argp];
                                argp++;
				user = argv[argp++];
				pass = argv[argp++];
                                if(argc == 10)
                                {
                                    usage();
                                    exit(0);
                                }
                                else if(argc > 10 )
                                {
                                    if(strncmp(argv[argp],"null",4) != 0)
                                        tweakalgo = argv[argp];
                                    argp++;
                                    if(strncmp(argv[argp],"null",4) != 0)
                                        tweakdata = argv[argp];
                                    argp++;
                                }
                                if(argc > 11)
                                 {
                                    if(strncmp(argv[argp],"null",4) != 0)
                                        header_mode = argv[argp];
                                    argp++;
                                 }
			}
		}
	}

       // Converting inp_iv which is hex encoded string  to packed hex
	if(inp_iv)
        {
          ivlen = (unsigned int)strlen((char *)inp_iv);
          //hexprint("Inp IV Text (Hex)", inp_iv, ivlen);
          // Converting IV length to even, since hex string is converted to bytes 
          if (ivlen % 2 != 0)
              ivlen = ivlen -1;
         iv = (char *)calloc(ivlen/2,sizeof(char));
         if(ConvertAsciiToPackedHex(inp_iv,iv,ivlen)==0)
         {
            fprintf(stderr, "Invalid IV passed for algorithm=%s  \n",algo);
            exit(0);
         }
          ivlen =  ivlen/2;
          //hexprint("output IV Text (Hex)", iv, ivlen);
        }
        indatalen = (unsigned int)strlen((char *)indata);
    
        if(tweakdata)
           tweakdata_len = strlen(tweakdata);
        if(tweakalgo)
           tweakalgo_len =  strlen(tweakalgo);
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

    //algo = strdup("FPE/AES/CARD10");
    rc = I_C_CreateCipherSpec(algo,keyname,&cipherspec);

    if (rc != I_E_OK) 
    {
        fprintf(stderr, "I_C_CreateCipherSpec error: %s\n",
            I_C_GetErrorString(rc));
            break;
    }

     rc = I_C_SetUserSpec(I_T_USPEC_TWEAKALGO,tweakalgo,tweakalgo_len,&userspec);

    if (rc != I_E_OK)
    {
        fprintf(stderr, "I_C_SetUserSpec error: %s\n",
            I_C_GetErrorString(rc));
            break;
    }

     rc = I_C_SetUserSpec(I_T_USPEC_TWEAKDATA,tweakdata,tweakdata_len,&userspec);

    if (rc != I_E_OK)
    {
        fprintf(stderr, "I_C_SetUserSpec error: %s\n",
            I_C_GetErrorString(rc));
            break;
    }

    if(header_mode)
        rc = I_C_SetUserSpec(I_T_USPEC_VERSION_HEADER_MODE, header_mode, header_mode_len,&userspec);

    if (rc != I_E_OK)
    {
        fprintf(stderr, "I_C_SetUserSpec error: %s\n",
            I_C_GetErrorString(rc));
            break;
    }


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


    rc = I_C_Crypt_Enhanced_FpeFormat(sess, cipherspec, operation,
                iv, ivlen, cryptoin1, cryptoinlen1, (I_T_BYTE*) cryptoout1, &cryptooutlen1,userspec,I_T_LAST_FOUR);
    if (rc != I_E_OK)
    {
        fprintf(stderr, "I_C_Crypt_Enhanced_FpeFormat() error: %s\n",
            I_C_GetErrorString(rc));
            break;
    }
    else
    {
            switch (operation) {
                case I_T_Operation_PublicEncrypt:
                case I_T_Operation_Encrypt:
                    printtext("Encrypted Text", cryptoout1, cryptooutlen1);
                    break;
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
        if (ver_header  != NULL)
        {
           hexprint("Version Header (Hex)", ver_header, ver_header_len);
        }
    }


     //DECRYPT operation 

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

        if(ver_header != NULL)
        {
           rc = I_C_SetUserSpec(I_T_USPEC_VERSION_HEADER,ver_header,ver_header_len,&userspec);
           if (rc != I_E_OK)
           {
              fprintf(stderr, "I_C_SetUserSpec error: %s\n",
              I_C_GetErrorString(rc));
              break;
           }
        }

        rc = I_C_Crypt_Enhanced_FpeFormat(sess, cipherspec, operation,
                iv, ivlen, cryptoin2, cryptoinlen2, (I_T_BYTE*) cryptoout2, &cryptooutlen2,userspec,I_T_LAST_FOUR);

        if (rc != I_E_OK)
        {
            fprintf(stderr, "I_C_Crypt_Enhanced_FpeFormat() error: %s\n",
                    I_C_GetErrorString(rc));
            break;
    }
    else
    {
            switch (operation) {
                case I_T_Operation_PrivateDecrypt:
                case I_T_Operation_Decrypt:
                    printtext("Decrypted PlainText", cryptoout2, cryptooutlen2);
                    break;
            }
    }

   }while (0);

    if (cryptoout1 != NULL)
        free(cryptoout1);
    if (cryptoout2 != NULL)
        free(cryptoout2);
    if(ver_header)
        free(ver_header);
    ver_header = NULL;
    if (cipherspec != NULL)
    I_C_DeleteCipherSpec(cipherspec);
    I_C_DeleteUserSpec(userspec);
    if (iv != NULL)
       free(iv);
    if (sess != NULL)
    I_C_CloseSession(sess);
    I_C_Fini();
    return rc;

}
