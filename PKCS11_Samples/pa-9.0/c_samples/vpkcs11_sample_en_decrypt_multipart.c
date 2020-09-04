
/*************************************************************************
**                                                                      **
** Copyright(c) 2012 - 2014                       Confidential Material **
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
 * File: vpkcs11_sample_en_decrypt_multipart.c
 ***************************************************************************
 ***************************************************************************
 * This file demonstrates the following
 * 1. Initialization
 * 2. Creating a connection and logging in.
 * 3. Find or Create the symmetric key
 * 4. Using the symmetric key to encrypt file content
 * 5. Using the symmetric key to decrypt the encrypted file content.
 * 6. Compare the original and decrypted file content.
 * 7. Clean up.
 */

#include "vpkcs11_sample_helper.h"

/*
 ***************************************************************************
 * Static Local Variables
 **************************************************************************
 */

#define MAX_SIZE_OF_KEY 128
#define AES_BLOCK_SIZE 16
#define MAX_FIND_RETURN 1

static CK_BYTE          iv[] =  "\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\x0C\x0D\x0E\x0F\x10\x00";

static const char outfilename[] = "encryptedtext.dat";
static const char outfilename2[] = "decryptedtext.dat";

/* 
 ************************************************************************
 * Function: encryptAndDecryptFile
 * This function first encrypts the source file using a symmetric key by calling mutli-part encryption functions. 
 * which is C_EncryptInit(), C_EncryptUpdte() in  a loop, then C_EncryptFinal() for the last part, and 
 * same the encrypted file. 
 * After that,  calling multipart decryption functions: 
 * which is C_DecryptInit(), and C_DecryptUpdate() in a loop, then C_DecryptFinal() for the last part,
 * and save the decrypted file.
 * Last, compare the contect of the original source file and decrypted file to make sure they are
 * identical.
 ************************************************************************
 * Parameters: none
 * Returns: CK_RV
 ************************************************************************
 */
static CK_RV encryptAndDecryptFile(char * infilename)
{
	CK_BYTE*        plainTextBuf = NULL_PTR;
	CK_ULONG	    plainTextBufferLen = 1024;
	
	/* C_Encrypt */
	CK_MECHANISM	mechEncryptionPad = { CKM_AES_CBC_PAD, iv, 16 };
	CK_BYTE*		cipherText = NULL;
	CK_ULONG		cipherTextLen = 0;

	/* For C_Decrypt */
	CK_BYTE*		decryptedText = NULL_PTR;
	CK_ULONG		decryptedTextLen = 0;
	
	/* CK_BYTE*		lastPartText = NULL_PTR; */
	CK_BBOOL         bCompareResult = CK_TRUE;
	/* General */
	CK_RV rc = CKR_OK;
	int   status ;
	FILE *  fpin = NULL;
	FILE * fpout = NULL;
	FILE * fpout2 = NULL;
	CK_ULONG  bytesRead = 0;
	CK_ULONG  bytesResult = 0;
	CK_ULONG  bytesResult2 = 0;

	do
	{

		fpin = fopen(infilename, "r");
		fpout = fopen(outfilename, "w+");

		if (fpin == NULL || fpout == NULL)
		{
			printf("File open error.\n");
			break;
		}
		plainTextBuf = (CK_BYTE *)calloc(1, sizeof(CK_BYTE)* plainTextBufferLen);

		if (plainTextBuf == NULL)
		{
			printf("Memory calloc failed for plainTextBuf\n");
			break;
		}

		memset((void *)plainTextBuf, 0, plainTextBufferLen);

		/* C_EncryptInit */
		rc = FunctionListFuncPtr->C_EncryptInit(
			hSession,
			&mechEncryptionPad,
			hGenKey
			);
		if (rc != CKR_OK)
		{
			printf("C_EncryptInit failed\n");
			break;
		}

		while (!feof(fpin) && !ferror(fpin))
		{
			bytesResult = (CK_ULONG)fread(plainTextBuf, 1, plainTextBufferLen, fpin);
			bytesRead += bytesResult;

			/* pass in NULL Pointer to get the output buffer size */
			if (bytesResult == 0)
				break;

			rc = FunctionListFuncPtr->C_EncryptUpdate(
				hSession,
				plainTextBuf, bytesResult,
				NULL, &cipherTextLen
				);
			if (rc != CKR_OK)
			{
				printf("C_EncryptUpdate failed\n");
				break;
			}

			cipherText = (CK_BYTE *)malloc(sizeof(CK_BYTE)* cipherTextLen);
			memset((void *)cipherText, 0, cipherTextLen);

			rc = FunctionListFuncPtr->C_EncryptUpdate(
				hSession,
				plainTextBuf, bytesResult,
				cipherText, &cipherTextLen
				);
			if (rc != CKR_OK)
			{
				printf("C_EncryptUpdate failed\n");
				break;
			}

			memset((void *)plainTextBuf, 0, plainTextBufferLen);
			fwrite(cipherText, sizeof(CK_BYTE), cipherTextLen, fpout);
			fflush(fpout);
			free(cipherText);
			cipherText = NULL_PTR;
		}

		if (rc != CKR_OK)
		{
			/* break out of outer while loop */
			break;
		}

		/* pass in NULL pointer to get output buffer size */
		rc = FunctionListFuncPtr->C_EncryptFinal(
			hSession,
			NULL, &cipherTextLen
			);
		if (rc != CKR_OK)
		{
			printf("C_EncryptFinal failed\n");
			break;
		}

		cipherText = (CK_BYTE *)malloc(sizeof(CK_BYTE)* cipherTextLen);
		if (NULL == cipherText)
		{
			rc = CKR_HOST_MEMORY;
			break;
		}
		memset((void *)cipherText, 0, cipherTextLen);

		rc = FunctionListFuncPtr->C_EncryptFinal(
			hSession,
			cipherText, &cipherTextLen
			);
		if (rc != CKR_OK)
		{
			printf("C_EncryptFinal failed\n");
			break;
		}
		else
		{
			printf("C_EncryptFinal Succeed, will write last %ld bytes to the encrypted file.\n", (long)cipherTextLen);
		}

		if (cipherTextLen != 0)
			fwrite(cipherText, sizeof(CK_BYTE), cipherTextLen, fpout);

		free(cipherText);
		cipherText = NULL_PTR;

		fflush(fpout);
		fclose(fpout);
		fclose(fpin);

		fpout = fopen(outfilename, "r+");
		fpout2 = fopen(outfilename2, "w+");

		if (fpout == NULL || fpout2 == NULL)
		{
			printf("File open error.\n");
			break;
		}
		fseek(fpout, 0, SEEK_SET);

		/*C_Decrypt*/
		rc = FunctionListFuncPtr->C_DecryptInit(
			hSession,
			&mechEncryptionPad,
			hGenKey
			);
		if (rc != CKR_OK)
		{
			printf("C_DecryptInit failed\n");
			break;
		}

		cipherTextLen = plainTextBufferLen;
		cipherText = (CK_BYTE *)malloc(sizeof(CK_BYTE)* cipherTextLen);
		if (NULL == cipherText)
		{
			rc = CKR_HOST_MEMORY;
			break;
		}
		memset((void *)cipherText, 0, cipherTextLen);
		if (!cipherText)
		{
			rc = CKR_HOST_MEMORY;
			break;
		}

		decryptedTextLen = plainTextBufferLen + AES_BLOCK_SIZE;

		bytesRead = 0;
		while (!feof(fpout) && !ferror(fpout))
		{
			bytesResult = (CK_ULONG)fread(cipherText, 1, cipherTextLen, fpout);
			bytesRead += bytesResult;

			if (bytesResult == 0)
				break;

			/* pass in NULL pointer to get output buffer size */
			rc = FunctionListFuncPtr->C_DecryptUpdate(
				hSession,
				cipherText, bytesResult,
				NULL, &decryptedTextLen
				);
			if (rc != CKR_OK)
			{
				printf("C_DecryptUpdate failed\n");
				break;
			}

			/* allocate output buffer for decrypted Text */
			decryptedText = (CK_BYTE *)malloc(sizeof(CK_BYTE)* decryptedTextLen);
			memset(decryptedText, 0, decryptedTextLen);
			if (!decryptedText)
			{
				rc = CKR_HOST_MEMORY;
				break;
			}

			rc = FunctionListFuncPtr->C_DecryptUpdate(
				hSession,
				cipherText, bytesResult,
				decryptedText, &decryptedTextLen
				);
			if (rc != CKR_OK)
			{
				printf("C_DecryptUpdate failed\n");
				break;
			}

			fwrite(decryptedText, sizeof(CK_BYTE), decryptedTextLen, fpout2);
			fflush(fpout2);

			if(decryptedText) {
				free(decryptedText);
				decryptedText = NULL_PTR;
			}
			cipherTextLen = plainTextBufferLen;
			memset((void *)cipherText, 0, cipherTextLen);
		}

		if (rc != CKR_OK)
		{
			break;
		}

		/* pass in NULL pointer to get output buffer size */
		rc = FunctionListFuncPtr->C_DecryptFinal(
			hSession,
			NULL, &decryptedTextLen
			);
		if (rc != CKR_OK)
		{
			printf("C_DecryptFinal failed\n");
			break;
		}

		/* allocate output buffer for decrypted Text */
		decryptedText = (CK_BYTE *)calloc(1, sizeof(CK_BYTE)* decryptedTextLen);
		if (NULL == decryptedText)
		{
			rc = CKR_HOST_MEMORY;
			break;
		}
		memset(decryptedText, 0, decryptedTextLen);
		if (!decryptedText)
		{
			rc = CKR_HOST_MEMORY;
			break;
		}

		rc = FunctionListFuncPtr->C_DecryptFinal(
			hSession,
			decryptedText, &decryptedTextLen
			);
		if (rc != CKR_OK)
		{
			printf("C_DecryptFinal failed\n");
			break;
		}
		else
		{
			printf("C_DecryptFinal succeed, got decrypted Text Length: %ld . \n", (long)decryptedTextLen);
		}

		if (decryptedTextLen != 0)
		{
			fwrite(decryptedText, sizeof(CK_BYTE), decryptedTextLen, fpout2);
			fflush(fpout2);
		}

		if(decryptedText) {
			free(decryptedText);
			decryptedText = NULL_PTR;
		}
		
		fclose(fpout2);
		fclose(fpout);

		fpin = fopen(infilename, "r");
		fpout2 = fopen(outfilename2, "r");

		if (fpin == NULL || fpout2 == NULL)
		{
			printf("File open error.\n");
			break;
		}

		fseek(fpout2, 0, SEEK_SET);
		fseek(fpin, 0, SEEK_SET);

		decryptedText = (CK_BYTE *)calloc(1, sizeof(CK_BYTE)* plainTextBufferLen);
		bytesRead = 0;
		while (!feof(fpin) && !ferror(fpin))
		{
			bytesResult = (CK_ULONG)fread(plainTextBuf, 1, plainTextBufferLen, fpin);
			bytesResult2 = (CK_ULONG)fread(decryptedText, 1, bytesResult, fpout2);

			/* compare the plaintext and decrypted text */
			status = memcmp(plainTextBuf, decryptedText, bytesResult);
			bCompareResult &= (status == 0) && (bytesResult == bytesResult2);
		}

		fclose(fpout2);
		fclose(fpin);
		
		if (bCompareResult == CK_TRUE)
		{
			printf("Success! PlainText and DecryptedText match! \n");
		}
		else
		{
			printf("Plaintext and Decrypted Text do not match \n");
		}
	}while (0);

	/* cleanup and free memory */

	if(cipherText)
	{
		free (cipherText);
		cipherText = NULL;
	}	
	if(plainTextBuf)
	{
		free (plainTextBuf);
		plainTextBuf = NULL;
	}	
	if(decryptedText)
	{
		free (decryptedText);
		decryptedText = NULL;
	}

	return rc;
}

void usage()
{
  printf ("Usage: vpkcs11_sample_en_decrypt_multipart -p pin -s slotID -k keyName -f filename [-m module]\n");
  exit (2);
}

/*
 ************************************************************************
 * Function: main
 ************************************************************************
 */
int main (int argc, char* argv[])
{
	CK_RV rc; 
	char * keyLabel = NULL;
	char * infilename = NULL;
	int slotId = 0;

    char * pin = NULL;
    char * libPath = NULL;
	char * foundPath = NULL;
	
	int c;
	extern char *optarg;
	extern int optind;
    int loggedIn = 0;

	while ((c = getopt(argc, argv, "p:k:f:m:s:")) != EOF)
		switch (c) {
		case 'p':
			pin = optarg;
			break;
		case 'k':
			keyLabel = optarg;
			break;
		case 'f':
			infilename = optarg;
			break;
		case 'm':
			libPath = optarg;
			break;
		case 's':
			slotId = atoi(optarg);
			break;

		case '?':
		default:
			usage();
			break;
	}
    if ((NULL == pin) || (NULL == keyLabel) || ( NULL == infilename) || (optind < argc))
	{
		usage();
	}

    printf("Begin Encrypt and Decrypt File sample: ...\n");

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


		printf("Successfully logged in. \n Looking for key \n");
		hGenKey = findKey(keyLabel, CKO_SECRET_KEY);
		if (CK_INVALID_HANDLE == hGenKey)
		{
			printf("Key does not exist, creating key... Creating key \n");
			rc = createKey(keyLabel);
			if (rc != CKR_OK)
			{
				fprintf(stderr, "FAIL: Unable to create key.\n");
				break;
			}
			printf("Successfully created key.\n");
		}
		printf("Successfully found key.\n");

		rc = encryptAndDecryptFile(infilename);
		if (rc != CKR_OK)
		{
			break;
		}
		printf("Successfully encrypted and decrypted\n");

		rc = deleteKey(hGenKey);
		if (rc != CKR_OK)
		{
			break;
		}

		printf("Successfully deleted key\n");
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
    printf("End Encrypt and Decrypt File sample.\n");
    fflush(stdout);
	return 0;
}

