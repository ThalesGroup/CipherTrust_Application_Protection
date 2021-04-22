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
 * File: vpkcs11_sample_find_delete_key.c
 ***************************************************************************
 * Usage: vorpkcs11_sample_find_delete_key [-k name] <module>
 ***************************************************************************
 * This file is designed to be run after vorpkcs11_create_key_sample and  
 * demonstrates the following:
 * 1. Initialization
 * 2. Creating a connection and logging in.
 * 3. Querying for a key using the keyname.
 * 4. Deleting the key that was found.
 * 4. Clean up.
 */

#include "vpkcs11_sample_helper.h"


void usage()
{
  printf ("Usage: vpkcs11_sample_find_delete_key -p pin -s slotID -k keyName [-m module]\n");
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
	int slotId = 0;

    char *keyLabel = NULL;
    char *pin = NULL;
    char *libPath = NULL;
	char *foundPath = NULL;
	
    int loggedIn = 0;

    CK_OBJECT_HANDLE	hKey = 0x0;
	int c;
	extern char *optarg;
	extern int optind;

	while ((c = getopt(argc, argv, "p:k:m:s:")) != EOF)
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

		case '?':
		default:
			usage();
			break;
	}
    if ((NULL == pin) || (NULL == keyLabel) || (optind < argc))
	{
		usage();
	}
	
    printf("Begin Find and Delete Key sample: ...\n");

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

		hKey = findKeyByName(keyLabel);
		if (CK_INVALID_HANDLE == hKey)
		{
			fprintf(stderr, "FAIL: Unable to find the Key. \n");
			break;
		}
		/* key is found, now delete the key */
		rc = deleteKey(hKey);
		if (rc != CKR_OK)
		{
			fprintf(stderr, "FAIL: deleteKey with unexpected result\n");
		}
		else
		{
			printf("PASS: Successfully found and deleted key. \n");
		}
	} while (0);

    if (loggedIn)
    {
        rc = logout();
        if (rc == CKR_OK)
        {
            printf("Successfully logged out.\n");
        }
    }
 
	cleanup ();
    printf("End Find and Delete Key sample.\n");
    fflush(stdout);
	return 0;
}

