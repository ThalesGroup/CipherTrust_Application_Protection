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
 * File: vpkcs11_sample_create_key.c
 ***************************************************************************
 
 ***************************************************************************
 * This file demonstrates the following
 * 1. Initialization
 * 2. Create a connection and logging in.
 * 3. Create a key on the Data Security Manager
 * 4. Clean up.
 ***************************************************************************
 */

#include "vpkcs11_sample_helper.h" 


void usage()
{
  printf ("Usage: vpkcs11_sample_create_key -p pin -s slotID -k keyName [-m module]\n");
  exit (2);
}

/*
 ************************************************************************
 * Function: main
 ************************************************************************
 */

int main (int argc, char* argv[])
{
	CK_RV  rc; 
	char * keyLabel = NULL;
	char * pin = NULL;
    char * libPath = NULL;
	char * foundPath = NULL;
    int loggedIn = 0;
	int slotId = 0;

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
	if ((NULL == pin) || ( NULL == keyLabel ) || (optind < argc))
	{
		usage();
	}

    printf("Begin Create Key sample: ...\n");

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

		printf("Done initializing slot list. \n Opening session and logging in\n");
		rc = openSessionAndLogin(pin, slotId);
		if (rc != CKR_OK)
		{
			fprintf(stderr, "FAIL: Unable to open session and login.\n");
			break;
		}
		loggedIn = 1;
		printf("Successfully logged in. \n");

		if(keyLabel) {
			if (findKeyByLabel(keyLabel) != CK_INVALID_HANDLE)
			{
				fprintf(stderr, "FAIL: Key with same name already exist. \n");
				break; 
			}	

			printf("Creating key \n");
			rc = createKey(keyLabel);
		
			if (findKeyByLabel(keyLabel) != CK_INVALID_HANDLE)
			{			
				fprintf(stderr, "Key with name: %s created on DSM. \n", keyLabel);
				break;
			}
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
    printf("End Create Key sample.\n");
    fflush(stdout);
	return 0;
}

