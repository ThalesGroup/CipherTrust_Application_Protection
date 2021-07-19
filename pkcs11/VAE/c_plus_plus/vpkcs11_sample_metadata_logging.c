/*************************************************************************
**                                                                      **
** Copyright(c) 2012 - 2017                       Confidential Material **
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
 * File: vpkcs11_sample_metadata_logging.c
 ***************************************************************************
 ***************************************************************************
 * This file demonstrates the following
 * 1. Initialization
 * 2. Creating a connection and logging in.
 * 3. Finding an existing symmetric key; if not found,
 * 4. Creating a symmetric key on the Data Security Manager
 * 5. Using the symmetric key to encrypt plaintext;
 *    passing in metadata from first call
 * 6. Using the symmetric key to decrypt ciphertext.
 *    passing in metadata from first call
 * 7, Delete key.
 * 8. Clean up.
 */

/*
    vpkcs11_sample_metadata_logging.c
 */

#include <stdio.h>

#ifdef _WIN32
#define _WINSOCKAPI_ /* do not include winsock.h */
#include "cryptoki.h"
#include <tchar.h>
#include <windows.h>
#include <Accctrl.h>
#include <Aclapi.h>
#else
#include "pkcs11.h"
#include "pkcs11t.h"
#include <stdlib.h>
#include <errno.h>
#include <dlfcn.h>
#include <time.h>
#include <string.h>
#endif

#include "vpkcs11_sample_helper.h"

static CK_BYTE		plainText[] ="\xef\xbb\xbf\x53\x65\x63\x74\x69\x6f\x6e\x0d\x0a\x45\x6e\x64\x47\x6c\x6f\x62\x61\x6C\x0D\x0A\x11\x12\x13\x14\x15\x16\x17\x18";
static CK_ULONG		plainTextLen = 20;

extern CK_FUNCTION_LIST_PTR FunctionListFuncPtr;

/* ************************************************************************
 * Function: encryptAndDecrypt
 * This function first encrypts a block of data using a symmetric key. Then
 * decrypts the ciphertext with the same key to make sure the plain text and
 * decrypted text matches.
 * There are two calls for each Encrypt or Decrypt; EncryptFinal or DecryptFinal
 * The first call calculates the appropriate size of the buffer needed;
 * and pass in the user provided meta data for logging purpose
 * The caller is responsible for creating a buffer for the output that is
 * of sufficient size.
 ************************************************************************
 * Parameters: none
 * Returns: CK_RV
 ************************************************************************
 */
static CK_RV encryptAndDecrypt ()
{
	/* C_Encrypt */
	CK_MECHANISM	mechEncryptionPad = { CKM_AES_CBC_PAD, def_iv, 16 };
	CK_BYTE*		cipherText = NULL_PTR;
	CK_ULONG		cipherTextLen = 0;
	CK_ULONG        metaDataLen = 256;
	CK_CHAR         metadata[] = "META: This is a test metadata/Encryption: user: tester: hostname" ;
	CK_CHAR         metadata2[] = "META: This is a test metadata/Decryption: user: tester: hostname" ;

	/* For C_Decrypt */
	CK_BYTE*		decryptedText = NULL_PTR;
	CK_ULONG		decryptedTextLen = 0;

	/* General */
	CK_RV rc = CKR_OK;
	int status;

	/* C_EncryptInit */
	rc = FunctionListFuncPtr->C_EncryptInit(
											hSession,
											&mechEncryptionPad,
											hGenKey
											);
	if ( rc != CKR_OK )
		{
			printf ("C_EncryptInit failed\n");
			return rc;
		}

	cipherText = (CK_BYTE *)calloc( 1, sizeof(CK_BYTE) * metaDataLen );
	if(cipherText != NULL)
		{
			sprintf((char*)cipherText, "%s", (char *)metadata);
		}

	printf ("Plain Text length: %d\n", (int)sizeof( plainText));
    /* first call C_Encrypt by pass in metadata and obtain cipherText buffer size upon CKR_OK return */
	rc = FunctionListFuncPtr->C_Encrypt(
										hSession,
										plainText, sizeof(plainText),
										cipherText, &cipherTextLen
										);
	if (rc != CKR_OK)
    {
	   printf ("C_Encrypt failed\n");
	   return rc;
    }
    else
    {
	   printf ("C_Encrypt succeed, cipherTextLen is : %ld \n", (long)cipherTextLen);
	   cipherText = (CK_BYTE *)calloc( 1, sizeof(CK_BYTE) * cipherTextLen );
    }

    /* then call C_Encrypt to get actual cipherText and actual encrypted length */
	rc = FunctionListFuncPtr->C_Encrypt(
										hSession,
										plainText, sizeof(plainText),
										cipherText, &cipherTextLen
										);
	if (rc != CKR_OK)
    {
	   printf ("C_Encrypt failed\n");
	   return rc;
    }
    else
    {
	   printf ("C_Encrypt succeed, cipherTextLen is : %ld \n", (long)cipherTextLen);
       dumpHexArray( cipherText, (int)cipherTextLen );
    }

	/*C_Decrypt*/
	rc = FunctionListFuncPtr->C_DecryptInit(
											hSession,
											&mechEncryptionPad,
											hGenKey
											);
	if (rc != CKR_OK)
	{
		printf ("C_DecryptInit failed\n");
    	return rc;
	}

	decryptedText = (CK_BYTE *)calloc( 1, sizeof(CK_BYTE) * metaDataLen );
	if(decryptedText != NULL)
		{
			sprintf((char*)decryptedText, "%s", (char *) metadata2);
		}
    /* Pass in metadata and obtain the decrypted buffer size upon CKR_OK return */
	rc = FunctionListFuncPtr->C_Decrypt(
						hSession,
						cipherText, cipherTextLen,
						decryptedText, &decryptedTextLen
						);
	if (rc != CKR_OK)
	{
		printf ("C_Decrypt failed\n");
		return rc;
	}
    else
    {
		printf ("C_Decrypt succeed, decryptedTextLen: %ld\n", (long) decryptedTextLen);
		decryptedText = (CK_BYTE *)calloc( 1, sizeof(CK_BYTE) * decryptedTextLen );
        if ( NULL == decryptedText)
            return CKR_HOST_MEMORY;
        dumpHexArray( decryptedText, (int)decryptedTextLen);
    }

    /* now pass in the bufffer, to get the decrypted text and return decrypted size */
	rc = FunctionListFuncPtr->C_Decrypt(
										hSession,
										cipherText, cipherTextLen,
										decryptedText, &decryptedTextLen
										);
	if (rc != CKR_OK)
	{
		printf ("C_Decrypt failed\n");
		return rc;
	}
    else
    {
		printf ("C_Decrypt succeed, decryptedTextLen: %ld\n", (long)decryptedTextLen);
        dumpHexArray( decryptedText, (int)decryptedTextLen );
    }

	/* compare the plaintext and decrypted text */
	status = memcmp( plainText, decryptedText, plainTextLen );
	if (status == 0)
	{
		printf ("Success! Plain Text and Decrypted Text match! \n");
	}
	else
	{
		printf ("Failure!, Plain Text and Decrypted Text do NOT match!! \n");
	}
	/* cleanup and free memory */
	if (cipherText)
		free (cipherText);
	if (decryptedText)
		free (decryptedText);
	return rc;
}

void metadataLoggingUsage()
{
	printf ("Usage: vpkcs11_sample_metadata_logging -p pin -s slotID -k keyName [-i {k|m|u}:identifier] [-m module]\n");
	printf ("-i identifier: one of 'imported key id' as 'k', MUID as 'm', or UUID as 'u'.\n");
	exit (2);
}

/*
 ************************************************************************
 * Function: main
 ************************************************************************
 */
#ifdef THALES_CLI_MODE
int metadataLoggingSample (int argc, char* argv[])
#else
int main(int argc, char* argv[])
#endif
{
	CK_RV rc;
	char *keyLabel = NULL;
    char *pin = NULL;
    char *libPath = NULL;
	char *foundPath = NULL;
    int  slotId = 0;
	int  c;
	
	char * pKsid = NULL;
	int ksid_type = keyIdLabel;
	
	extern char *optarg;
	extern int optind;
    int loggedIn = 0;
	int key_size = 32;

	while ((c = newgetopt(argc, argv, "p:k:m:s:i:z:")) != EOF)
		switch (c) {
		case 'p':
			pin = optarg;
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
		case 'z':
			key_size = atoi(optarg);
			break;
		case 'i':
			ksid_type = parse_ksid_sel(optarg, &pKsid);
			break;
		case '?':
		default:
			metadataLoggingUsage();
			break;
	}

	if ((NULL == pin) || (optind < argc))
	{
		metadataLoggingUsage();
	}

	printf("Begin Meta data Logging Message sample.\n");

	do
	{
		/* load PKCS11 library and initalize. */
		printf ("Initializing PKCS11 library \n");
		foundPath = getPKCS11LibPath(libPath);
		if(foundPath == NULL)
		{
			printf("Error getting PKCS11 library path.\n");
			exit(1);
		}

		rc = initPKCS11Library(foundPath);
		if (rc != CKR_OK)
			{
				break;
			}
		printf ("Done initializing PKCS11 library \n Initializing slot list\n");
		rc = initSlotList();
		if (rc != CKR_OK)
			{
				break;
			}

		printf ("Done initializing slot list. \n Opening session and logging in\n");
		rc = openSessionAndLogin (pin, slotId);
		if (rc != CKR_OK)
			{
				break;
			}
		loggedIn = 1;

		if(keyLabel) {
			pKsid = keyLabel;
			ksid_type = keyIdLabel;
		}

		if (pKsid == NULL) {
			fprintf(stderr, "missing key label or ID\n");
			break;
		}
		printf ("Successfully logged in. \n Looking for key = %s\n", pKsid);
		rc = findKey(pKsid, ksid_type, CKO_SECRET_KEY, &hGenKey) ;

		if ( CK_INVALID_HANDLE != hGenKey ) {
			printf ("Successfully found previously created key.\n");
			rc = deleteKey (hGenKey, CK_TRUE);
			if (rc != CKR_OK)
			{
				printf ("Error removing previously created key: %x\n", (unsigned int)hGenKey);
				break;
			}
			else {
				printf ("Successfully removed previously created key.\n");
			}			
		}
				
		if (keyLabel == NULL) {
			// need a key label to create
			fprintf(stderr, "\nmissing key label for creation\n");
			break;
		}
		
		rc = createKeyS (keyLabel, key_size);
		if (rc != CKR_OK)
		{
			fprintf(stderr, "Error = %d creating key %s.\n", (int)rc, keyLabel);
			break;
		}
		printf ("Successfully created key.\n");
			
		rc = encryptAndDecrypt();
		if (rc != CKR_OK)
		{
			break;
		}

		printf ("Successfully encrypted and decrypted\n");
		rc = deleteKey (hGenKey, CK_TRUE);
		if (rc != CKR_OK)
		{
			break;
		}
		printf("Successfully deleted key\n");
	} while (0);

    if (loggedIn)
    {
        if (logout() == CKR_OK)
        {
            printf("Successfully logged out.\n");
        }
    }

    cleanup();
    printf("End Meta data logging Message sample.\n");
    fflush(stdout);
	return rc;
}
