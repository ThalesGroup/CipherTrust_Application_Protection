/*
 * CryptoSinglePart_FPE.c  
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

#define FPE_AES_UNICODE_ALG "FPE/AES/UNICODE"
#define FPE_AES_UNICODE_LEN 15
#define FPE_FF3_UNICODE_ALG "FPE/FF3/UNICODE"
#define FPE_FF3_UNICODE_LEN 15
#define FPE_FF1_UNICODE_ALG "FPE/FF1/UNICODE"
#define FPE_FF1_UNICODE_LEN 15
#define FPE_FF1v2_UNICODE_ALG "FPE/FF1v2/UNICODE"
#define FPE_FF1v2_UNICODE_LEN 17

#define UTF8 "UTF8"
#define UTF8_LEN 4
#define UTF_8 "UTF-8"
#define UTF_8_LEN 5
#define UTF16LE "UTF16LE"
#define UTF16LE_LEN 7
#define UTF_16LE "UTF-16LE"
#define UTF_16LE_LEN 8
#define UTF16BE "UTF16BE"
#define UTF16BE_LEN 7
#define UTF_16BE "UTF-16BE"
#define UTF_16BE_LEN 8
#define UTF32LE "UTF32LE"
#define UTF32LE_LEN 7
#define UTF_32LE "UTF-32LE"
#define UTF_32LE_LEN 8
#define UTF32BE "UTF32BE"
#define UTF32BE_LEN 7
#define UTF_32BE "UTF-32BE"
#define UTF_32BE_LEN 8

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

void printtext(const char* label, const I_T_BYTE *in, int len,char *algo)
{
   if(strstr(algo, "UNICODE"))
   {
       char *tmp=calloc(len+1,sizeof(char));
       if (tmp != NULL)
       {
           memcpy(tmp,in,len);
           printf(" %s: %s \n", label,tmp);
           free(tmp);
           tmp=NULL;
       }

   }
   else
   {
       int i;
       fprintf(stdout, "%s:", label);
       for(i = 0; i < len && i < 80; i++) 
       {
           fprintf(stdout,"%c ",(unsigned char)in[i]);
       }
       fprintf(stdout,"\n");
   }
}


void usage(void)
{
    fprintf(stderr, "usage: CryptoSinglePart_FPE conf_file keyname algorithm indata iv passphrase user passwd tweakalgo tweakdata charset radix unicodeType headerMode\n"
        "\n  conf_file - typically, CADP_CAPI.properties\n"
        "  keyname - key name\n"
        "  algorithm - long FPE algorithm name only , for example, 'FPE/AES/CARD10'\n"
        "  indata - sample data to encrypt based on cardinality \n"
	"  iv - initialization vector (cardinality based),len is BLOCKSIZE*2(hex encoded charactes): BLOCKSIZE for CARD10=56 CARD26=40 CARD62=32\n"
        "       IV is required when indata len >BLOCKSIZE ,else IV not required, 'null' for null iv.\n"
        "       IV is not required incase of FPE/FF3/ algorithm.\n"
        "  passphrase - optional cache passphrase, 'null' for null passphrase\n"
	"  user - (optional NAE user) user can be in a root domain or in a specific domain. For domain user, specify domain||username\n"
	"  passwd - optional (mandatory if user is specified) NAE user's password\n"
	"  tweakalgo - optional  Tweak algorithm\n"
	"  tweakdata - optional  Tweak data value:Hex encoded string(16 character) if tweakalgo= NONE, otherwise ASCII\n"
	"  charset - optional  Character set of input data\n"
	"  radix - optional  Radix of input data\n"
	"  unicodeType - Unicode type (UTF-8/UTF-16LE/UTF-16BE/UTF-32LE/UTF-32BE)\n"
        "  headerMode - Version Header Mode (for versionkey mode value should be always 1 or 2)\n"
        "               headerMode = 0 (NONE)\n"
        "               headerMode = 1 (EXTERNAL_HEADER : version key header stored in userSpec.)\n"
        "               headerMode = 2 (INTERNAL_HEADER : version key header adjust in cipher data.)\n"
        "\n Incase of FPE/FF3 & PFE/FF1 CARD10 CARD26 & CARD62, user provided charset and radix will be ignored.\n\n"
	"  card62Ordering - (0 - Legacy or 1 - recommended charset order)to use legacy CARD62 chraset order,\n"
        "                   or to decrypt data those were encrypted in CADP CAPI version < 8.12.2 \n"
    );
    exit(1);
}

int main(int argc, char **argv)
{

    I_O_Session sess = NULL; 
    char *path = NULL, *user = NULL, *pass = NULL , *keyname = NULL, *algo = NULL;
    I_T_BYTE *indata = NULL, *cryptoin1 = NULL, *cryptoin2 = NULL, *cryptoout1 = NULL, *cryptoout2 = NULL;
    char *tweakdata = NULL,*tweakalgo = NULL,*inp_iv= NULL, *header_mode = NULL, *char62_order = NULL;
    char*  iv = NULL, *charset = NULL, *radix = NULL, *charsetType = NULL;
    I_T_BYTE *passphrase = NULL;
    unsigned int argp = 0, ivlen = 0, indatalen = 0,tweakdata_len = 0,tweakalgo_len=0, charset_len = 0, radix_len = 0, charsetType_Len = 0;
    unsigned int header_mode_len = 0, char62_order_len = 0;
    I_T_UINT cryptoinlen1, cryptoinlen2, cryptooutlen1, cryptooutlen2;
    I_O_CipherSpec cipherspec = NULL;
    I_O_UserSpec userspec = NULL;
    I_T_RETURN rc = I_E_OK;
    I_T_Operation operation;
    I_T_BYTE utfmode = 0;
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
                                        charset = argv[argp];
                                    argp++;
                                }
                                if(argc > 12)
                                {
                                    if(strncmp(argv[argp],"null",4) != 0)
                                        radix = argv[argp];
                                    argp++;
                                 }
                                 if(argc > 13)
                                 {
                                    if(strncmp(argv[argp],"null",4) != 0)
                                        charsetType = argv[argp];
                                    argp++;
                                 }
                                 if(argc > 14)
                                 {
                                    if(strncmp(argv[argp],"null",4) != 0)
                                        header_mode = argv[argp];
                                    argp++;
                                 }
                                 if(argc > 15)
                                 {
                                    if(strncmp(argv[argp],"null",4) != 0)
                                        char62_order = argv[argp];
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
         if(ivlen > 1)
         { 
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
          else
          {
             fprintf(stderr, "Error: IV shouldn't be single character.\n"); 
             return -1;
          }
        }
        indatalen = (unsigned int)strlen((char *)indata);
        
        if(tweakdata)
           tweakdata_len = strlen(tweakdata);

        if(tweakalgo)
           tweakalgo_len =  strlen(tweakalgo);
               
        if(charset)
           charset_len = strlen(charset);

        if(radix)
           radix_len = strlen(radix);

        //setutfmode
        if(charsetType)
           charsetType_Len = strlen(charsetType);

        if(header_mode)
           header_mode_len = strlen(header_mode);

        if(char62_order)
           char62_order_len = strlen(char62_order);

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

    if(tweakalgo)
        rc = I_C_SetUserSpec(I_T_USPEC_TWEAKALGO,tweakalgo,tweakalgo_len,&userspec);

    if (rc != I_E_OK)
    {
        fprintf(stderr, "I_C_SetUserSpec error: %s\n",
            I_C_GetErrorString(rc));
            break;
    }

    if(tweakdata)
       rc = I_C_SetUserSpec(I_T_USPEC_TWEAKDATA,tweakdata,tweakdata_len,&userspec);

    if (rc != I_E_OK)
    {
        fprintf(stderr, "I_C_SetUserSpec error: %s\n",
            I_C_GetErrorString(rc));
            break;
    }

    if(radix)
     rc = I_C_SetUserSpec(I_T_USPEC_RADIX, radix, radix_len,&userspec);

    if (rc != I_E_OK)
    {
        fprintf(stderr, "I_C_SetUserSpec error: %s\n",
            I_C_GetErrorString(rc));
            break;
    }
    
    if(charset)
    {
        if(strchr(charset, '-'))
           rc = I_C_SetUserSpec(I_T_USPEC_CHARSET_RANGE, charset, charset_len,&userspec);
        else
           rc = I_C_SetUserSpec(I_T_USPEC_CHARSET, charset, charset_len,&userspec);
    }

    if (rc != I_E_OK)
    {
        fprintf(stderr, "I_C_SetUserSpec error: %s\n",
            I_C_GetErrorString(rc));
            break;
    }

    if(charsetType)
        rc = I_C_SetUserSpec(I_T_USPEC_UTFMODE, charsetType, charsetType_Len,&userspec);

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

   /* Set "0" in userspec, if you want to decrypt existing encrypted data,
    * those were encrypted using CAPI version  < 8.12.2 for CARD62 algo only.
    * Set 0: Legacy charset order, 1: recommended charset order
    */
    if(char62_order)
        rc = I_C_SetUserSpec(I_T_USPEC_CARD62_CHARSET_ORDER, char62_order, char62_order_len,&userspec);

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


    //calculate output byte for FF3 Unicode
    if((strncmp(algo, FPE_FF3_UNICODE_ALG, FPE_FF3_UNICODE_LEN) == 0) ||
       (strncmp(algo, FPE_FF1_UNICODE_ALG, FPE_FF1_UNICODE_LEN) == 0) ||
       (strncmp(algo, FPE_FF1v2_UNICODE_ALG, FPE_FF1v2_UNICODE_LEN) == 0))
    {
        if(charsetType){
            if(!strncmp(charsetType, UTF8, UTF8_LEN) || !strncmp(charsetType, UTF_8, UTF_8_LEN))
                cryptooutlen1 *= 4;
            if(!strncmp(charsetType, UTF16BE, UTF16BE_LEN) || !strncmp(charsetType, UTF16LE, UTF16LE_LEN) ||
               !strncmp(charsetType, UTF_16BE, UTF_16BE_LEN) || !strncmp(charsetType, UTF_16LE, UTF_16LE_LEN))
                cryptooutlen1 *= 2;
        }
        else
        {
            fprintf(stderr, "UTF mode shouldn't be null for this algo.\n");
            break;
        }
    }

    if (strncmp(algo, FPE_AES_UNICODE_ALG, FPE_AES_UNICODE_LEN) == 0)
        cryptoout1 = (I_T_BYTE *) calloc(4*cryptooutlen1,sizeof(I_T_BYTE));
    else
        cryptoout1 = (I_T_BYTE *) calloc(cryptooutlen1,sizeof(I_T_BYTE));

    if (!cryptoout1)
    {
            fprintf(stderr, "Failed to allocate %d bytes.\n", cryptooutlen1);
            break;
    }

    hexprint("Plain Text (Hex)", cryptoin1, cryptoinlen1);

    rc = I_C_Crypt_Enhanced(sess, cipherspec, operation,
                iv, ivlen, cryptoin1, cryptoinlen1, (I_T_BYTE*) cryptoout1, &cryptooutlen1,userspec);
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
                    printtext("Encrypted Text", cryptoout1,cryptooutlen1,algo);
                    hexprint("Encrypted Text (Hex)", cryptoout1, cryptooutlen1);
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
        if (ver_header  != NULL && ver_header_len > 0)
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

        //calculate output byte for FF3 Unicode
        if((strncmp(algo, FPE_FF3_UNICODE_ALG, FPE_FF3_UNICODE_LEN) == 0) ||
           (strncmp(algo, FPE_FF1_UNICODE_ALG, FPE_FF1_UNICODE_LEN) == 0) ||
           (strncmp(algo, FPE_FF1v2_UNICODE_ALG, FPE_FF1v2_UNICODE_LEN) == 0))
        {
            if(!strncmp(charsetType, UTF8, UTF8_LEN) || !strncmp(charsetType, UTF_8, UTF_8_LEN))
                cryptooutlen2 *= 4; 
            if(!strncmp(charsetType, UTF16BE, UTF16BE_LEN) || !strncmp(charsetType, UTF16LE, UTF16LE_LEN) ||
               !strncmp(charsetType, UTF_16BE, UTF_16BE_LEN) || !strncmp(charsetType, UTF_16LE, UTF_16LE_LEN))
                cryptooutlen2 *= 2;
        }
   
        if (strncmp(algo, FPE_AES_UNICODE_ALG, FPE_AES_UNICODE_LEN) == 0)
            cryptoout2 = (I_T_BYTE *) calloc(2*cryptooutlen2,sizeof(I_T_BYTE));
        else
            cryptoout2 = (I_T_BYTE *) calloc(cryptooutlen2,sizeof(I_T_BYTE));

        if (!cryptoout2)
        {
            fprintf(stderr, "Failed to allocate %d bytes.\n", cryptooutlen2);
            break;
        }

        if(ver_header != NULL && ver_header_len > 0)
        {
           rc = I_C_SetUserSpec(I_T_USPEC_VERSION_HEADER,ver_header,ver_header_len,&userspec);
           if (rc != I_E_OK)
           {
              fprintf(stderr, "I_C_SetUserSpec error: %s\n",
              I_C_GetErrorString(rc));
              break;
           }
        }

        rc = I_C_Crypt_Enhanced(sess, cipherspec, operation,
                iv, ivlen, cryptoin2, cryptoinlen2, (I_T_BYTE*) cryptoout2, &cryptooutlen2,userspec);

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
                    printtext("Decrypted PlainText", cryptoout2,cryptooutlen2,algo);
                    hexprint("Decrypted Text (Hex)", cryptoout2, cryptooutlen2);
                    break;
            }
    }

   }while (0);

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
    if (iv != NULL)
       free(iv);
    if (sess != NULL)
       I_C_CloseSession(sess);
    I_C_Fini();
    return rc;

}
