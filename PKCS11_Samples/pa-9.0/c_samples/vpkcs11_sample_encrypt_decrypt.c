/**                                                                      **
** Copyright(c) 2012 - 2015                       Confidential Material **
**                                                                      **
** This file is the property of Vormetric Inc.                          **
** The contents are proprietary and confidential.                       **
** Unauthorized use, duplication, or dissemination of this document,    **
** in whole or in part, is forbidden without the express consent of     **
** Vormetric, Inc..                                                     **
**                                                                      **
**************************************************************************/

/*
 ***************************************************************************
 * File: vpkcs11_sample_encrypt_decrypt.c
 ***************************************************************************
 ***************************************************************************
 * This file demonstrates the following
 * 1. Initialization
 * 2. Creating a connection and logging in.
 * 3. Creating a symmetric key on the Data Security Manager
 * 4. Using the symmetric key to encrypt plaintext
 * 5. Using the symmetric key to decrypt ciphertext.
 * 6, Delete key.
 * 7. Clean up.
 */

/* 
   vpkcs11_sample_encrypt_decrypt.c
 */

#include "vpkcs11_sample_helper.h"
#include <stdio.h>
#include <stdlib.h>
#include <wchar.h>


#ifdef __WINDOWS__

typedef int __ssize_t;
typedef __ssize_t ssize_t;

#else
#endif 

#define MAX_RADIX_SIZE 65535
#define READ_BLK_LEN 1024
CK_BYTE	defPlainText[16] = "\xef\xbb\xbf\x53\x65\x63\x74\x69\x6f\x6e\x0d\x0a\x45\x6e\x64\x47"; /* 16 characters */

/* CK_CHAR defPlainText[80] = "Plain text message to be encrypted."; */
unsigned plaintextlen=sizeof(defPlainText);

int     errorCount = 0;
encoding_t 	encodings[5] = {{CS_UTF8, "CS_UTF8"}, {CS_UTF16LE, "CS_UTF16LE"}, {CS_UTF16BE, "CS_UTF16BE"}, {CS_UTF32LE, "CS_UTF32LE"}, {CS_UTF32BE, "CS_UTF32BE"}};
CK_BBOOL blk_mode = CK_FALSE;

static CK_FPE_PARAMETER     fpeparams;
static CK_FPE_PARAMETER_UTF fpeparamsutf;
static CK_FF1_PARAMETER_UTF ff1paramsutf;

static CK_RV createObject (char* keyLabel)
{
    CK_RV rc = CKR_OK;
    CK_UTF8CHAR         app[] = { "VORMETRIC_PKCS11_SAMPLE" };
    CK_UTF8CHAR         keyValue[KEYLEN];
    CK_OBJECT_CLASS     keyClass = CKO_SECRET_KEY;
    CK_KEY_TYPE         keyType = CKK_AES;
    CK_ULONG            keySize = KEYLEN; /* 256 bits */
    CK_BBOOL            bFalse = CK_FALSE;
    CK_BBOOL            bTrue = CK_TRUE;
    CK_OBJECT_HANDLE    hKey = 0x0;

    CK_UTF8CHAR  *label = (CK_UTF8CHAR *) keyLabel;
    CK_ULONG len = (CK_ULONG) strlen(keyLabel);
   
    /* 
	 * AES key template.
     * CKA_LABEL is the name of the key and will be displayed on the DSM
     * CKA_VALUE is the bytes that make up the AES key.
     */

    CK_ATTRIBUTE aesKeyTemplate[19] = {
        {CKA_ID,            label,  len},
        {CKA_LABEL,         label,  len},
        {CKA_APPLICATION,   &app,       sizeof(app)     },
        {CKA_CLASS,         &keyClass,  sizeof(keyClass)},
        {CKA_KEY_TYPE,      &keyType,   sizeof(keyType) },
        {CKA_VALUE,         &keyValue,  sizeof(keyValue)},
        {CKA_VALUE_LEN,     &keySize,   sizeof(keySize) },
        {CKA_TOKEN,         &bTrue,     sizeof(bTrue)   },
        {CKA_ENCRYPT,       &bTrue,     sizeof(bTrue)   },
        {CKA_DECRYPT,       &bTrue,     sizeof(bTrue)   },
        {CKA_SIGN,          &bFalse,    sizeof(bFalse)  },
        {CKA_VERIFY,        &bFalse,    sizeof(bFalse)  },
        {CKA_WRAP,          &bTrue,     sizeof(bTrue)   },
        {CKA_UNWRAP,        &bFalse,    sizeof(bFalse)  },
        {CKA_EXTRACTABLE,       &bFalse,    sizeof(bFalse)  },
        {CKA_ALWAYS_SENSITIVE,  &bFalse,    sizeof(bFalse)  },
        {CKA_NEVER_EXTRACTABLE, &bTrue,     sizeof(bTrue)   },
		{CKA_MODIFIABLE, &bTrue, sizeof(bTrue)},
        {CKA_SENSITIVE,         &bTrue,     sizeof(bTrue)   }
    };
    CK_ULONG    aesKeyTemplateSize = sizeof(aesKeyTemplate)/sizeof(CK_ATTRIBUTE);

    memcpy(keyValue, "\xEF\x43\x59\xD8\xD5\x80\xAA\x4F\x7F\x03\x6D\x6F\x04\xFC\x6A\x94\x2B\x7E\x15\x16\x28\xAE\xD2\xA6\xAB\xF7\x15\x88\x09\xCF\x4F\x3C", KEYLEN);

    rc = FunctionListFuncPtr->C_CreateObject (
                                            hSession,
                                            aesKeyTemplate,
                                            aesKeyTemplateSize,
                                            &hKey
                                             );
    if (rc != CKR_OK || hKey == 0)
    {
        fprintf (stderr, "Error in C_CreateObject(), return value: %d\n", (int)rc);
    }

    return rc;
}

int fgetline(char **lineptr, int *n, FILE *stream) {
    char *bufptr = NULL;
    char *p = bufptr;
    int size = 0;
    int c;
	long len;

    if (lineptr == NULL) {
    	return -1;
    }
    if (stream == NULL) {
    	return -1;
    }
    if (n == NULL) {
    	return -1;
    }
    bufptr = *lineptr;
    size = *n;

    c = fgetc(stream);
    if (c == EOF) {
    	return -1;
    }
    if (bufptr == NULL) {
    	bufptr = malloc(READ_BLK_LEN);
    	if (bufptr == NULL) {
    		return -1;
    	}
    	size = READ_BLK_LEN;
    }
    p = bufptr;
    while(c != EOF) {
    	if ((p - bufptr) > (int)(size - 1)) {
			len = (long)(p - bufptr);
    		size += READ_BLK_LEN;
    		bufptr = realloc(bufptr, size);
    		if (bufptr == NULL) {
    			return -1;
    		}
			p = bufptr + len;
    	}
    	*p++ = (char)c;
    	if (c == '\n') {
    		break;
    	}
    	c = fgetc(stream);
    }

    *p = '\0';
    *lineptr = bufptr;
    *n = size;

    return (int)(p - bufptr);
}

int fgetline_w(char **lineptr, int *n, FILE *stream, CK_BYTE enc_mode) {
    char *bufptr = NULL;
    char *p = bufptr;
    int size = 0;
	wint_t wc;
	long len;
	CK_BYTE CP[4];
	int ret;
	
    if (lineptr == NULL) {
    	return -1;
    }
    if (stream == NULL) {
    	return -1;
    }
    if (n == NULL) {
    	return -1;
    }
    bufptr = *lineptr;
    size = *n;

	wc = fgetwc(stream);
	
    if (wc == WEOF) {
    	return -1;
    }
    if (bufptr == NULL) {
    	bufptr = malloc(READ_BLK_LEN);
    	if (bufptr == NULL) {
    		return -1;
    	}
    	size = READ_BLK_LEN;
    }
	
    p = bufptr;

	while (wc == '\n' || wc == '\r') 
		wc = fgetwc(stream);
	
    while(wc != WEOF) {
    	if ((p - bufptr) > (int)(size - 1)) {
			len = (long)(p - bufptr);
    		size += READ_BLK_LEN;
    		bufptr = realloc(bufptr, size);
    		if (bufptr == NULL) {
    			return -1;
    		}
			p = bufptr + len;
    	}

		if (wc == '\n' || wc == '\r') {
    		break;
    	}
	   		
		ret = gen_utf( (unsigned int)wc, enc_mode, CP);

		if (ret != 0) {
			memcpy(p, CP, ret);
			p += ret;							
		}								
    	
    	wc = fgetwc(stream);
    }

    *p = '\0';
    *lineptr = bufptr;
    *n = size;
	
    return (int)(p - bufptr);
}

		
static CK_RV encryptDecryptBuf(CK_SESSION_HANDLE hSess, CK_MECHANISM *pMech, CK_BYTE *pBuf, unsigned int len, CK_BYTE **ppDecryptedBuf, unsigned long *pDecryptedLen)
{
	/* General */
	CK_RV rc = CKR_OK;
	CK_BYTE		    *cipherText = (CK_BYTE *) "";	
	CK_ULONG		cipherTextLen = 0;
	
	/* For C_Decrypt */
	CK_BYTE         *decryptedText = NULL_PTR;
	CK_ULONG		decryptedTextLen = 0;
	int    status;
	
	/* C_EncryptInit */
    printf("About to call C_EncryptInit()\n");
	rc = FunctionListFuncPtr->C_EncryptInit(hSess,
											pMech,
											hGenKey
											);
	if (rc != CKR_OK)
	{
		fprintf(stderr, "FAIL: call to C_EncryptInit() failed.\n");
		return rc;
	}	
	 
	/* first call C_Encrypt by pass in NULL to get cipherText buffer size */
	rc = FunctionListFuncPtr->C_Encrypt(
										hSess,
										pBuf, len,
										NULL, &cipherTextLen
										);
	if (rc != CKR_OK)
		{
			fprintf (stderr, "FAIL: 1st call to C_Encrypt() failed, rc=%d.\n", (int)rc);
			return rc;
		}
	else {
		printf ("1st call to C_Encrypt() succeeded: size = %u.\n", (unsigned int)cipherTextLen);
		cipherText = (CK_BYTE *)calloc( 1, sizeof(CK_BYTE) * cipherTextLen );
		if (!cipherText)
			return CKR_HOST_MEMORY;
	}	

	/* then call C_Encrypt to get actual cipherText */
	rc = FunctionListFuncPtr->C_Encrypt(
										hSess,
										pBuf, len,
										cipherText, &cipherTextLen
									    );
	if (rc != CKR_OK) 
    {
		fprintf (stderr, "FAIL: 2nd call to C_Encrypt() failed\n");
		return rc;
    }
    else
    {
       printf ("2nd call to C_Encrypt() succeeded. Encrypted Text:\n");
       dumpHexArray( cipherText, (int)cipherTextLen );
    }

	/* C_DecryptInit */
    printf("About to call C_DecryptInit()\n");
	rc = FunctionListFuncPtr->C_DecryptInit(
											hSess,
											pMech,
											hGenKey
											);
	if (rc != CKR_OK)
	{
		fprintf (stderr, "FAIL: Call to C_DecryptInit() failed\n");
    	return rc;
	}

    /* pass in NULL, to get the decrypted buffer size  */
    /* usually, use the same size of ciphterText should be fine. */
    printf("About to call C_Decrypt(), output length set to %lu\n", decryptedTextLen); 
	rc = FunctionListFuncPtr->C_Decrypt(
						hSess,
						cipherText, cipherTextLen,
						NULL, &decryptedTextLen
						);
	if (rc != CKR_OK)
	{
		fprintf (stderr, "FAIL : 1st call to C_Decrypt() failed, rc=%d.\n", (int)rc);
		return rc;
	}
    else
    {
		printf ("1st call to C_Decrypt() succeeded.\n");
		decryptedText = (CK_BYTE *)calloc( 1, sizeof(CK_BYTE) * decryptedTextLen );
		if ( NULL == decryptedText) 
			return CKR_HOST_MEMORY;
    }

    /* now pass in the buffer, to get the decrypted text and real decrypted size */
    printf("About to call C_Decrypt(), output length set to %lu\n", decryptedTextLen);
	rc = FunctionListFuncPtr->C_Decrypt(
										hSess,
										cipherText, cipherTextLen,
										decryptedText, &decryptedTextLen
										);

	if (rc != CKR_OK)
	{
		fprintf (stderr, "FAIL: 2nd call to C_Decrypt() failed\n");
		*ppDecryptedBuf = NULL;
		*pDecryptedLen = 0;
		return rc;
	}
    else
    {
		printf ("2nd call to C_Decrypt() succeeded. Decrypted Text:\n");
        dumpHexArray(decryptedText, (int)decryptedTextLen);
		*ppDecryptedBuf = decryptedText;
		*pDecryptedLen = decryptedTextLen;
    }

	/* cleanup and free memory */
	if (cipherText) 
		free (cipherText);
	/* compare the plaintext and decrypted text */
	status = memcmp( pBuf, decryptedText, decryptedTextLen );
	if (status == 0)
	{
		printf ("Success! Plain Text and Decrypted Text match!! \n\n");
		return CKR_OK;
	}
	else
	{
		printf ("Failure!, Plain Text and Decrypted Text do NOT match!! \n");		
		return CKR_GENERAL_ERROR;
	}
}

static CK_RV makeCharset(char cset_choc, char* charset, CK_BYTE enc_mode, CK_MECHANISM_TYPE mechType)
{
	FILE     *fp_charsetutf = NULL;
	FILE     *fp_charset = NULL;
	char     *pCharset = NULL;
	CK_BYTE	 *pBuf = NULL;

	char     *pch = NULL;
	char     *p1, *p2, *prng;
	unsigned int  rstart, rend, rcp;		
	CK_BYTE  CP[4];	
	int      act_rdx, charsetlen;
	int      c = 0x1;
	int      c2 = 0x1;
	int      i, j, ret;	
 
	wint_t          wc;
	const char	    delims[] = ",";
	unsigned short  rdelims[] = { 0x0d, 0x0a };
	
	if(cset_choc == 'c') {
		switch(mechType) {
		case CKM_VORMETRIC_FPE:
			/* cset_choc == 'c' is ASCII by default */
			strncpy((char *) fpeparams.charset, charset, sizeof(fpeparams.charset)-1);
			fpeparams.charset[sizeof(fpeparams.charset)-1] = '\0';
			fpeparams.radix = (CK_BYTE) strlen(charset);						
			break;

		case CKM_THALES_FF1:
			strncpy((char *) ff1paramsutf.charset, charset, sizeof(ff1paramsutf.charset)-1);
			ff1paramsutf.charset[sizeof(ff1paramsutf.charset)-1] = '\0';
			ff1paramsutf.charsetlen = (unsigned) myhtonl(strlen(charset));
			ff1paramsutf.radix      = (unsigned short) myhtons(strlen(charset));            
			ff1paramsutf.utfmode  = 0;  /* ASCII */
			break;
		}
	}
	else if(cset_choc == 'l') {

		fp_charset = fopen(charset, "r");
		if(!fp_charset)
		{
			fprintf(stderr, "Unable to open character set file: %s", charset);
			return CKR_GENERAL_ERROR;
		}
			
		if(enc_mode == CS_ASCII) {
					
			c = fgetc(fp_charset);				
									
			pCharset = (char *)calloc(4, MAX_RADIX_SIZE); /* UTF encoded charset can be 65535 * 4 bytes long */
			if(pCharset == NULL)
			{
				fprintf(stderr, "Error allocating pCharset!");
				fclose(fp_charset);
				return CKR_HOST_MEMORY;
			}
				
			memset(pCharset, 0, MAX_RADIX_SIZE*4);			
			/* This would remove duplicates naturally, for ASCII only */
			while( c != EOF ) {
				if(c == '\n' || c == '\r') /* filter out newline character \n\r */
				{
					c = fgetc(fp_charset);
					continue;
				}
				if(c == EOF )
					break;
				pCharset[c] = (char)c;			
				c = fgetc(fp_charset);
			}			
			fclose(fp_charset);			
				
			j = 0; /* ASCII code 0 is NULL, will be overwritten */
			i = 1;
								
			do {
				while(pCharset[i] == '\0')
					i++;
					
				if(i >= MAX_RADIX_SIZE-1)
					break;
					
				fpeparams.charset[j]    = pCharset[i];
				ff1paramsutf.charset[j] = pCharset[i];
				j++; 
				i++;
			} while(i < MAX_RADIX_SIZE-1);		
				
			fpeparams.charset[j] = '\0'; /* not needed */
			printf("Charset is: %*s, radix=%d.\n", j, (char *) fpeparams.charset, j);
			
			switch(mechType) {
			case CKM_VORMETRIC_FPE:
				fpeparams.radix = (CK_BYTE)j;				
				break;

			case CKM_THALES_FF1:
				ff1paramsutf.radix   = (unsigned short) myhtons(j);
				ff1paramsutf.utfmode = enc_mode;
				ff1paramsutf.charsetlen = (unsigned) myhtonl(j);		
				break;
			}
			
			if(pCharset) {
				free(pCharset);
				pCharset = NULL;
			}
		} /* ASCII mode */
		else {
			int c3 = 0x1;
			int c4 = 0x1;
			fprintf(stderr, "C sample: literal input support UTF mode UTF-8, UTF-16/LE, UTF-32/LE");
			if(c != EOF)
				c2 = fgetc(fp_charset);

			if(c2 != EOF) {
				c3 = fgetc(fp_charset);
				if(c3 != EOF)
					c4 = fgetc(fp_charset);
			}
			else {
				fprintf(stderr, "File size too small: %s", charset);
				return CKR_GENERAL_ERROR;
			}
				
			if(c == 0xFF && c2 == 0xFE) {
				if(c3 == 0x00 && c4 == 0x00)
					fp_charsetutf = fopen(charset, "r,ccs=UTF32LE");
				else 
					fp_charsetutf = fopen(charset, "r,ccs=UTF16LE");					
			}
			else if(c == 0xFE && c2 == 0xFF) {
				fp_charsetutf = fopen(charset, "r,ccs=UTF16BE");					
			}
			else {									
				if(c == 0xEF && c2 == 0xBB && c3 == 0xBF)
					fp_charsetutf = fopen(charset, "r,ccs=UTF8");
				else if(c == 0x00 && c2 == 0x00 && c3 == 0xFE && c4 == 0xFF)
					fp_charsetutf = fopen(charset, "r,ccs=UTF32BE");
				else
					fp_charsetutf = fopen(charset, "r");
			}
				
			if(!fp_charsetutf)
			{
				fprintf(stderr, "Unable to open character set file with UTF mode: %s", charset);
				return CKR_GENERAL_ERROR;
			}
 
			fclose(fp_charset);				
			wc = fgetwc(fp_charsetutf); /* SKIP BOM character */
			act_rdx = 0;
			charsetlen = 0;

			wc = fgetwc(fp_charsetutf);
				
			while( wc != WEOF ) {
				if(wc == '\n' || wc == '\r') /* filter out newline character \n\r */
				{
					wc = fgetwc(fp_charsetutf);
					continue;
				}
				if(wc == WEOF )
					break;

				if(act_rdx >= 65535) 
					break;
					
				rcp = (unsigned int)wc;
				ret = gen_utf(rcp, enc_mode, CP);

				if (ret != 0) {
					memcpy(fpeparamsutf.charset + charsetlen, CP, ret);
					memcpy(ff1paramsutf.charset + charsetlen, CP, ret);
					charsetlen += ret;
					act_rdx++;  						
				}
																		
				wc = fgetwc(fp_charsetutf);
			}			
			fclose(fp_charsetutf);

			if(enc_mode != CS_ASCII && blk_mode == CK_TRUE)
			{								
				for(i=0; i<2; i++)
				{
					ret = gen_utf((unsigned int)rdelims[i], enc_mode, CP);
						
					if (ret != 0) {
						memcpy(fpeparamsutf.charset + charsetlen, CP, ret);
						memcpy(ff1paramsutf.charset + charsetlen, CP, ret);
						charsetlen += ret;
						act_rdx++;										
					}
				}
			}

			if(act_rdx >= 65535) {
				printf("The character set is limited to 65535 characters, which was exceeded. Exiting...\n");
				exit(4);
			}
				
			printf("UTF mode = %d, Character set length = %d, Radix = %d", enc_mode, charsetlen, act_rdx);

			switch(mechType) {
			case CKM_VORMETRIC_FPE:
				memcpy(fpeparamsutf.tweak, "\xD8\xE7\x92\x0A\xFA\x33\x0A\x73", 8);
				fpeparamsutf.utfmode = enc_mode;
				fpeparamsutf.charsetlen = myhtonl(charsetlen);
				fpeparamsutf.radix = (unsigned short) myhtons(act_rdx);
				break;
				
			case CKM_THALES_FF1:
				ff1paramsutf.utfmode = enc_mode;
				ff1paramsutf.charsetlen = myhtonl(charsetlen);
				ff1paramsutf.radix = (unsigned short) myhtons(act_rdx);
				break;
			}
		}			
	}
	else if(cset_choc == 'r') { /* r stands for range */
		char      *token = NULL;
		int       readlen;
		
		fp_charset = fopen(charset, "r+");
		if(!fp_charset)
		{
			fprintf(stderr, "Unable to open character set file: %s", charset);
			return CKR_GENERAL_ERROR;
		}

		act_rdx = 0;
		charsetlen = 0;
			
		pBuf = (CK_BYTE *)calloc(1, sizeof(CK_BYTE) * READ_BLK_LEN * 2);
		if( !pBuf ) {
			fprintf(stderr, "Error allocating memory for charset file!");
			goto FREE_RESOURCES;
		}
			
		readlen = (int)fread(pBuf, sizeof(CK_BYTE), READ_BLK_LEN * 2, fp_charset);			
		if(readlen < 0)
		{
			if(readlen != -1)
				fprintf(stderr, "Error reading file, readlen = %d", (int)readlen);
			return CKR_GENERAL_ERROR;
		}
		
		token = strtok((char *)pBuf, delims);

		while(token) {
			prng = strdup((char *)token);
			if(!prng) {
				printf("Error duplicating token. Aborting...\n");
				return CKR_HOST_MEMORY;
			}
				
			pch = strchr(prng, '-');				
				
			if(pch) {
				p1 = prng;
				*pch = '\0';
				p2 = pch+1;
				trim(p1); trim(p2);
				rstart = (unsigned int)strtoul(p1, NULL, 16);
				rend = (unsigned int)strtoul(p2, NULL, 16);

				for(rcp=rstart; rcp<=rend; rcp++)
				{
					if(act_rdx >= 65535) {
						printf("The character set is limited to 65535 characters, which was exceeded. Aborting...\n");
						exit(4);
					}
										
					ret = gen_utf(rcp, enc_mode, CP);

					if (ret != 0) {
						memcpy(fpeparamsutf.charset + charsetlen, CP, ret);
						memcpy(ff1paramsutf.charset + charsetlen, CP, ret);
						charsetlen += ret;
						act_rdx++;  						
					}
				}					
			}
			else {
				p1 = prng;
				trim(p1);
				if(act_rdx >= 65535) 
					break;
				rcp = (unsigned int)strtoul(p1, NULL, 16);
				ret = gen_utf(rcp, enc_mode, CP);

				if (ret != 0) {
					memcpy(fpeparamsutf.charset + charsetlen, CP, ret);
					memcpy(ff1paramsutf.charset + charsetlen, CP, ret);
					charsetlen += ret;
					act_rdx++;						
				}
			}
			token = strtok(NULL, delims);

			if(prng) {
				free(prng); prng = NULL;
			}
		}
									
		if(enc_mode != CS_ASCII && blk_mode == CK_TRUE)
		{								
			for(i=0; i<2; i++)
			{
				ret = gen_utf((unsigned int)rdelims[i], enc_mode, CP);
					
				if (ret != 0) {
					memcpy(fpeparamsutf.charset + charsetlen, CP, ret);
					memcpy(ff1paramsutf.charset + charsetlen, CP, ret);
					charsetlen += ret;
					act_rdx++;										
				}
			}
		}

		if(act_rdx >= 65535) {
			printf("The character set is limited to 65535 characters, which was exceeded. Aborting...\n");
			exit(4);
		}
			
		printf("UTF mode = %d, Character set length = %d, Radix = %d", enc_mode, charsetlen, act_rdx);

		switch(mechType) {
		case CKM_VORMETRIC_FPE:
			memcpy(fpeparamsutf.tweak, "\xD8\xE7\x92\x0A\xFA\x33\x0A\x73", 8);
			fpeparamsutf.utfmode = enc_mode;
			fpeparamsutf.charsetlen = myhtonl(charsetlen);
			fpeparamsutf.radix = (unsigned short) myhtons(act_rdx);
			break;

		case CKM_THALES_FF1:
			ff1paramsutf.utfmode = enc_mode;
			ff1paramsutf.charsetlen = myhtonl(charsetlen);
			ff1paramsutf.radix = (unsigned short) myhtons(act_rdx);	
			break;
		}
		
		if(pBuf) {
			free( pBuf );
			pBuf = NULL;
		}
	}

 FREE_RESOURCES:
	if(pBuf) {
		free (pBuf);
		pBuf = NULL;
	}
 
	return CKR_OK;
}

/* 
 ************************************************************************
 * Function: encryptAndDecrypt
 * This function first encrypts a block of data using a symmetric key. Then
 * decrypts the ciphertext with the same key to make sure the plain text and
 * decrypted text matches.
 * The caller is responsible for creating a buffer for the output that is 
 * of sufficient size.
 ************************************************************************
 * Parameters: operation ... CBC_PAD or CTR or ECB or FPE
 * Returns: CK_RV
 ************************************************************************
 */
static CK_RV encryptDecrypt(char *operation, char *in_filename, char *piv, char cset_choc, char *charset, char *decrypted_file, char *charsettype, char* tweak)
{
    CK_BYTE			iv[] = "\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\x0C\x0D\x0E\x0F\x10\x00";    
    CK_BYTE	      	*pBuf = NULL;
		
	CK_BYTE         *pDecryptBuf, *pPlainBuf;
    FILE            *fp_read = NULL;
	FILE            *fp_write = NULL;	
	int             readlen = 0;
	int             act_rdlen = 0;
	int             bf_len;
	char            fopen_mode[128];
	CK_ULONG        decryptedLen;
	CK_BBOOL        bFpeMode = CK_FALSE;
	CK_RV           rc = CKR_OK;
	unsigned short  rdelims[] = { 0x0d, 0x0a };
	CK_MECHANISM_TYPE    selMechanism;

	wint_t          wc;
	int             line_no;
		
	/* C_Encrypt */
	CK_MECHANISM	mechEncryptionPad = { CKM_AES_CBC_PAD,   iv, 16 };
	CK_MECHANISM	mechEncryptionCtr = { CKM_AES_CTR,       iv, 16 };
	CK_MECHANISM	mechEncryptionECB = { CKM_AES_ECB,       iv, 16 };
	CK_MECHANISM	mechEncryptionCBC = { CKM_AES_CBC,       iv, 16 };
	CK_MECHANISM	mechEncryptionFPE = { CKM_VORMETRIC_FPE, &fpeparams, sizeof(fpeparams) };
	CK_MECHANISM	mechEncryptionFPEUTF = { CKM_VORMETRIC_FPE, &fpeparamsutf, sizeof(fpeparamsutf) };
    CK_MECHANISM    mechEncryptionFF1UTF = { CKM_THALES_FF1,    &ff1paramsutf, sizeof(ff1paramsutf) };
    CK_MECHANISM    *pmechEncryption = NULL;

	CK_BYTE         enc_mode = get_enc_mode(charsettype);
	unsigned        tweak_len = tweak ? (unsigned)strlen(tweak) : 0;
			
	/* a character set or a character set file was specified on the command line */
		
	if(enc_mode != CS_ASCII)
	{
		fpeparamsutf.mode = 1; /* UTF mode */

		if (!strncmp(charsettype, "UTF", 3)) {		
			memcpy(fpeparamsutf.tweak, "\xD8\xE7\x92\x0A\xFA\x33\x0A\x73", 8);
		
			/*fpeparamsutf.utfmode = CS_UTF8; 
			  fpeparamsutf.radix = myhtons(10); */
		}
	}

	 if (!strcmp(operation, "FPE")) {
		 selMechanism = CKM_VORMETRIC_FPE;
		 makeCharset(cset_choc, charset, enc_mode, selMechanism);
		 if (!strcmp(charsettype, "ASCII")) {			
			 pmechEncryption = &mechEncryptionFPE;
			 printf("Using FPE in ASCII mode.\n");
		 }
		 else {
			 pmechEncryption = &mechEncryptionFPEUTF;
			 printf("Using FPE in UTF mode.\n");
		 }
		 bFpeMode = CK_TRUE;
	} else if (!strcmp(operation, "FF1")) {
		 selMechanism = CKM_THALES_FF1;
		 makeCharset(cset_choc, charset, enc_mode, selMechanism);
		 ff1paramsutf.tweaklen = myhtonl(tweak_len);
		 pmechEncryption = &mechEncryptionFF1UTF;
		 bFpeMode = CK_TRUE;
		 printf("Using FF1 mode.\n");
    }
	else if (!strcmp(operation, "CTR")) {
		selMechanism = CKM_AES_CTR;
		printf("Using AES/CTR mode.\n");
		pmechEncryption = &mechEncryptionCtr;
	}
    else if (!strcmp(operation, "ECB")) {
		selMechanism = CKM_AES_ECB;
		pmechEncryption = &mechEncryptionECB;
		printf("Using AES/ECB mode.\n");
	}
	else if (!strcmp(operation, "CBC")) {
		selMechanism = CKM_AES_CBC;
		pmechEncryption = &mechEncryptionCBC;
		printf("Using AES/CBC mode.\n");
	}
    else if (!strncmp(operation, "CBC", 3) ) {
		selMechanism = CKM_AES_CBC_PAD;
		pmechEncryption = &mechEncryptionPad;
		printf("Using AES/CBC_PAD (default) mode.\n");
	}
	else {
		printf("Error: %s: Invalid operation.\n", operation);
		return CKR_GENERAL_ERROR;
	}

    if (piv && strlen(piv)==32)
    {
        int k=0;
        printf("Obtaining IV from the command line\n");
        for (k=0; k<16; k++) 
        {
			char x[3];
            unsigned u;
            x[2]=0;
            x[0]=piv[k+k];
            x[1]=piv[k+k+1];
            sscanf(x, "%X", &u);
            iv[k] = (CK_BYTE) u;
        }
    }
	else if (!piv)
        printf("Using canned IV (because piv is NULL)\n");
    else 
        printf("Using canned IV (because strlen(piv) is %d)\n", (int) strlen(piv) );

	
	printf("IV:\n");
    dumpHexArray(iv, 16);   
	
	if (in_filename == NULL) {
		printf("Plain Text Default: \n");
		dumpHexArray((CK_BYTE *)defPlainText, plaintextlen);
		rc = encryptDecryptBuf(hSession, pmechEncryption, (CK_BYTE *)defPlainText, plaintextlen, &pDecryptBuf, &decryptedLen);
	}
	else 
    {		
		if(blk_mode)
			fp_read = fopen(in_filename, "rb+");
		else if(enc_mode != CS_ASCII) {
			strcpy( fopen_mode, "r,ccs=" );
			strcat( fopen_mode, charsettype );
			
			fp_read = fopen(in_filename, fopen_mode);
			wc = fgetwc(fp_read); /* read the BOM character, otherwise, first wchar_t read will be WEOF: -1 */
			if(wc != 0xFE) {
				printf("Read BOM character, Get: %x.", wc);
			}
		}
		else {
			fp_read = fopen(in_filename, "r" /*fopen_mode*/);			
		}
		
        if (!fp_read) {
			printf("Fail to open file %s.", in_filename);
			return CKR_FUNCTION_FAILED;
		}
		
		if(decrypted_file != NULL)
		{
			/*	strcpy( fopen_mode, "w,ccs=" );
				strcat( fopen_mode, charsettype ); */
			
			fp_write = fopen(decrypted_file, "w+");

			if(!fp_write) {
				printf("Fail to open file %s in %s mode.", decrypted_file, fopen_mode);
				if(fp_read)
					fclose(fp_read);
				return CKR_FUNCTION_FAILED;
			}				
		}

		line_no = 0;
		do {
			if(bFpeMode && !blk_mode) {
				bf_len = READ_BLK_LEN;
				pBuf = NULL;
				
				if(enc_mode == CS_ASCII)
					readlen = fgetline((char**)&pBuf, &bf_len, fp_read);				
				else {
					readlen = fgetline_w((char**)&pBuf, &bf_len, fp_read, enc_mode); 					
				}
				
				if(readlen < 0)
				{
					if(readlen != -1)
						fprintf(stderr, "Error reading file, readlen = %d", (int)readlen);
					break;
				}

				if(pBuf == NULL)
				{
					fprintf(stderr, "Error getting line from file, pBuf = NULL \n");
					break;
				}				
			
				/* for carriage return from windows */
				while(pBuf[readlen-1] == '\n' || pBuf[readlen-1] == '\r') 
				{
					pBuf[readlen--] = '\0';			
				}

				act_rdlen = readlen;
				if(line_no == 0)				
			    {
					pPlainBuf = get_BOM_mode(pBuf, &act_rdlen, &enc_mode);
				}
				else
					pPlainBuf = pBuf;

				fprintf(stdout, "PlainText:%s\n", (char *)pPlainBuf);				
			}
			else {
				bf_len = READ_BLK_LEN;
				pBuf = (CK_BYTE *)calloc( bf_len, sizeof(CK_BYTE) );
				if(pBuf) {
					readlen = (int)fread(pBuf, sizeof(CK_BYTE), bf_len, fp_read);
					act_rdlen = readlen;
					pPlainBuf = get_BOM_mode(pBuf, &act_rdlen, &enc_mode);
				}
				else {
					goto FREE_RESOURCES;
				}
			}

			if(readlen == 1 && bFpeMode)
			{
				fprintf(stderr, "Fpe mode only supports input length >= 2.\n");
				if(pBuf) {
					free (pBuf);
					pBuf = NULL;
				}
				continue;
			}
			
			if(readlen > 0 && pPlainBuf)
			{			
				pDecryptBuf = NULL;
				rc = encryptDecryptBuf(hSession, pmechEncryption, pPlainBuf, (unsigned int)act_rdlen, &pDecryptBuf, &decryptedLen);
			
				if(rc == CKR_OK && fp_write && pDecryptBuf)
				{
					if(bFpeMode) {
						if(line_no == 0) {
							put_BOM_mode(enc_mode, fp_write);
						}

						fwrite(pDecryptBuf, 1, decryptedLen, fp_write);						

						if(!blk_mode) { /* put line seperator back in */							
							/* fwrite("\x0d\x0a", 1, 2, fp_write); */
							fwrite(rdelims, sizeof(unsigned short), 2, fp_write);
						}
					}
					else
						fwrite(pDecryptBuf, 1, decryptedLen, fp_write);
				}
				else if(rc != CKR_OK) {					
					fprintf(stderr, "Encrypt/Decrypt Error: rc=%d.\n", (int)rc);
					fprintf(stderr, "PlainText: %s\n", (char *)pBuf);
					errorCount++;
				}
				
				if (pDecryptBuf) {
					free (pDecryptBuf);
					pDecryptBuf = NULL;
				}
				memset(pBuf, 0, bf_len);					
			}
			
			if(pBuf) {
				free (pBuf);
				pBuf = NULL;
			}
			line_no++;
		} while ( bFpeMode && (!blk_mode || readlen == bf_len) );		
	}

 FREE_RESOURCES:

	if(pBuf) {
		free (pBuf);
		pBuf = NULL;
	}
	
	if(fp_read)
		fclose(fp_read);

	if(fp_write)
		fclose(fp_write);

	if(bFpeMode)
		fprintf(stdout, "%s : Encryption/Decryption matched error count = %d.\n", operation, errorCount);
			
	return rc;
}

void usage()
{
    printf("Usage: vpkcs11_sample_encrypt_decrypt -p pin [-s slotID] [-K] -k keyName [-m module_path] [-o operation] [-f input_file_name] [-i iv_in_hex] ([-c charset_for_fpe_mode]|[-r range_charset_filename]|[-l literal_charset_filename]) [-t tweak] [-d decrypted_file_name] [-u charsettype]\n");
    printf("       operation...CBC_PAD (default) or CTR or ECB or FPE\n");
    printf("       -K       ...create a key with known key bytes on the DSM\n");
    printf("       -u       ...charsettype: ASCII (default), UTF-8, UTF-16LE, UTF-16, UTF-32LE, UTF-32\n");
    exit(2);
}

/*
 ************************************************************************
 * Function: main
 ************************************************************************
 */
int main (int argc, char* argv[])
{
	CK_RV rc; 
	char *keyLabel = NULL;
    char *pin = NULL;
    char *libPath = NULL;
	char *foundPath = NULL;
	int  slotId = 0;
    char *operation = "CBC_PAD";
    char *filename = NULL;
	char cset_choc = '\0';
	char *decrypted_file = NULL;
    char *iv = NULL;
	int   c;
	extern char *optarg;
	extern int optind;
    int loggedIn = 0;
    char *charset = NULL;
	char *tweak = NULL;
    int createkey=0;
    char *charsettype = "ASCII";

	while ((c = getopt(argc, argv, "u:p:k:m:o:f:l:i:s:c:r:d:t:bK")) != EOF)
		switch (c) {
        case 'u':
            charsettype = optarg;
            break;
		case 'p':
			pin = optarg;
			break;
        case 'K':
            createkey = 1;
            break;
		case 'k':
			keyLabel = optarg;
			break;
		case 'm':
			libPath = optarg;
			break;
        case 's':
            slotId = atoi(optarg);
            break;
		case 't':
			tweak = optarg;
			break;
        case 'o':
			operation = optarg;
            break;
        case 'f':
            filename = optarg;
            break;
        case 'i':
            iv = optarg;
            break;
		case 'b':
			blk_mode = CK_TRUE;
			break;
		case 'c':
		case 'r':
		case 'l':
			cset_choc = (char)c;
			charset = optarg;
			break;
		case 'd':
			decrypted_file = optarg;
			break;
		case '?':
		default:
			usage();
			break;
	}
	
    if ((NULL == pin) || (NULL == keyLabel) || (optind < argc))
	{
		usage();
	}

    printf("Begin Encrypt and Decrypt Message sample.\n");

	do
	{
		/* load PKCS11 library and initalize. */
		printf("Initializing PKCS11 library \n");
		foundPath = getPKCS11LibPath(libPath);
		if(foundPath == NULL)
		{
			printf("Error getting PKCS11 library path.\n");
			exit(1);
		}
		
		rc = initPKCS11Library(foundPath);		
		if (rc != CKR_OK)
		{
			fprintf(stderr, "FAIL: Unable to initialize PKCS11 library. \n");
			break;
		}

		printf("Done initializing PKCS11 library \n Initializing slot list\n");
		rc = initSlotList();
		if (rc != CKR_OK)
		{
			fprintf(stderr, "FAIL: Unable to initialize Slot List. \n");
			break;
		}

		printf("Done initializing Slot List. \n Opening session and logging in ...\n");
		rc = openSessionAndLogin(pin, slotId);
		if (rc != CKR_OK)
		{
			fprintf(stderr, "FAIL: Unable to open session and login.\n");
			break;
		}
		loggedIn = 1;
		printf("Successfully logged in. \n");

        if (createkey && keyLabel) {
            rc = createObject(keyLabel);
            if (!rc) printf("Key creation failed\n");
        }

		printf("Successfully logged in. \n Looking for key \n");
		hGenKey = findKey(keyLabel, CKO_SECRET_KEY);
		if (CK_INVALID_HANDLE == hGenKey)
		{
			printf("Key does not exist, creating key... Creating key \n");
			rc = createKey(keyLabel);
			if (rc != CKR_OK)
			{
				break;
			}
			printf("Successfully created key.\n");
		}
		printf("Successfully found key.\n");
		
		rc = encryptDecrypt(operation, filename, iv, cset_choc, charset, decrypted_file, charsettype, tweak);
		if (rc != CKR_OK)
		{
			break;
		}
		printf("Successfully encrypted and decrypted\n");	
	} while (0);

    if (loggedIn)
    {
        rc = logout();
        if (rc == CKR_OK)
        {
            printf("Successfully logged out.\n");
        }
    }

    cleanup();
    printf("End Encrypt and Decrypt Message sample.\n");
    fflush(stdout);
	return 0;
}
