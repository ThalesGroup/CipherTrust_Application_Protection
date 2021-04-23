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
 * File: vpkcs11_sample_find_export_key.c
 ***************************************************************************
 ***************************************************************************
 * This file is designed to be run after vpkcs11_sample_create_key and  
 * demonstrates the following:
 * 1. Initialization
 * 2. Creating a connection and logging in.
 * 3. Querying for a key using the keyname.
 * 4. Export the key using the wrappingKey that was found.
 * 4. Clean up.
 */



#include "vpkcs11_sample_helper.h"

/*
 ***************************************************************************
 * Local Variables
 **************************************************************************
 */

#define AES_BLOCK_SIZE 16
#define MAX_FIND_RETURN 1


static CK_BYTE			iv[] =	"\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\x0C\x0D\x0E\x0F\x10\x00"; 
static const char outfilename[] = "keytext.dat";

static CK_RV wrapAndExportKey (CK_OBJECT_HANDLE hKey, CK_OBJECT_HANDLE hWrappingKey);


/*
 ************************************************************************
 * Function: findExportKey
 * This function first search for the source key and wrapping key from DSM
 ************************************************************************
 * Parameters: none
 * Returns: CK_RV
 ************************************************************************
 */

static CK_RV findExportKeys (char* keyLabel, char* wrappingKeyLabel)
{
	CK_RV rc = CKR_OK;
	/* CK_OBJECT_CLASS		keyClass = CKO_SECRET_KEY; */
	CK_OBJECT_HANDLE	hFoundKey = 0x0;
	CK_OBJECT_HANDLE    hWrappingKey = CK_INVALID_HANDLE;

	if(wrappingKeyLabel != NULL)
	{
		hWrappingKey = findKey(wrappingKeyLabel, CKO_SECRET_KEY);

		if (CK_INVALID_HANDLE == hWrappingKey)
		{
	        fprintf (stderr, "FAIL: Cannot find the wrapping key: %s.\n", wrappingKeyLabel);
		} 
		else
		{
			printf ("Found wrapping key : %s successfully.\n", wrappingKeyLabel);
		}
	}

	if(keyLabel != NULL)
	{
		hFoundKey = findKey(keyLabel, CKO_SECRET_KEY);

		if (CK_INVALID_HANDLE == hFoundKey)
		{
			fprintf (stderr , "FAIL : Cannot find the source key: %s. \n", keyLabel);
		} 
		else
		{
			printf ("Found source key : %s successfully.\n", keyLabel);
            rc = wrapAndExportKey(hFoundKey, hWrappingKey);
            if (rc == CKR_OK)
            {
				printf ("Successfully found and exported key.\n");
            } else {
				printf ("wrapAndExportKey failed, error code %08X\n", (unsigned) rc);
            }
		}
	}
	return rc;
}

/*
********************************************
* Function: wrapAndExportKey
********************************************
* Exports a key from the DataSecurity Manager wrapped with another key. 
*************************************************
* Parameters:
* hKey -- wrapped key to be exported
* hWrappingKey -- key used to wrap the key above.
**********************************************************
*/ 
static CK_RV wrapAndExportKey (CK_OBJECT_HANDLE hKey, 	CK_OBJECT_HANDLE hWrappingKey)
{
	CK_RV rc;
    /* C_WrapKey not longer support CKM_AES_ECB any more, */
	CK_MECHANISM	  mechExportKey = { CKM_AES_CBC_PAD, iv, 16 };
	CK_BYTE_PTR       pWrappedKey = NULL;
	CK_ULONG          ulWrappedKeyLen = 0;
	FILE *            fp = NULL;

	do
	{
		rc = FunctionListFuncPtr->C_WrapKey(hSession,
			&mechExportKey,
			hWrappingKey,
			hKey,
			NULL,
			&ulWrappedKeyLen);
		if (rc != CKR_OK)
		{
			fprintf(stderr, "FAIL: call to C_WrapKey() failed\n");
			break;
		}
		else
		{
			printf("C_WrapKey succeed, ulWrappedKeyLen is : %ld \n", (long)ulWrappedKeyLen);

			/* allocate memory for output buffer */
			pWrappedKey = (CK_BYTE_PTR)calloc(1, sizeof(CK_BYTE)* ulWrappedKeyLen);
			if (!pWrappedKey)
			{
				rc = CKR_HOST_MEMORY;
				break;
			}
		}

		rc = FunctionListFuncPtr->C_WrapKey(hSession,
			&mechExportKey,
			hWrappingKey,
			hKey,
			pWrappedKey,
			&ulWrappedKeyLen);
		if (rc != CKR_OK)
		{
			fprintf(stderr, "FAIL: call to C_WrapKey() failed. \n");
			break;
		}

		/* export wrapped key by saving it to a file */
		fp = fopen(outfilename, "a+");

		if (fp)
		{
			fprintf(fp, "Key ID: %lu\n", hKey);
			fprintf(fp, "Key Value: ");

			fwrite(pWrappedKey, sizeof(CK_BYTE), ulWrappedKeyLen, fp);

			fflush(fp);
			fclose(fp);

			printf("Found and Export keys successfully for key: %lu.\n", hKey);
		}

	} while (0);

	if(pWrappedKey)
		free(pWrappedKey);

	return rc;
}


void usage()
{
  printf ("Usage: vpkcs11_sample_find_export_key -p pin -s slotID -k keyName -w wrappingKeyName [-m module]\n");
  exit (2);
}


/*
 ************************************************************************
 * Function: main
 ************************************************************************
 */

int main (int argc, char* argv[])
{
	FILE* 	fp;
	CK_RV rc; 
    char *keyLabel = NULL;
    char *pin = NULL;
    char *libPath = NULL;
	char *foundPath = NULL;
    char *wrappingKeyLabel = NULL;

	int slotId = 0;
    int c;
	extern char *optarg;
	extern int optind;
   	int loggedIn = 0;

	while ((c = getopt(argc, argv, "p:k:w:m:s:")) != EOF)
		switch (c) {
		case 'p':
			pin = optarg;
			break;
		case 'k':
			keyLabel = optarg;
			break;
		case 'w':
			wrappingKeyLabel = optarg;
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
	if ((NULL == pin) || (NULL == keyLabel) || ( NULL == wrappingKeyLabel )  || (optind < argc))
	{
		usage();
	}

    printf("Begin Find and Export Key sample.\n");

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
		printf("Successfully logged in. \n Exporting key \n");

		fp = fopen(outfilename, "w+");

		if (fp)
		{
			fprintf(fp, "Exported keys:\n");
			fclose(fp);
		}

		rc = findExportKeys(keyLabel, wrappingKeyLabel);
	}while (0);

    if (loggedIn)
    {
        rc = logout();
        if (rc == CKR_OK)
        {
            printf("Successfully logged out.\n");
        }
    }

    cleanup();
    printf("End Find and Export Key sample.\n");
    fflush(stdout);;
	return 0;
}

