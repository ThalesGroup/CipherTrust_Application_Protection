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
 * File: vpkcs11_sample_gen_random.c
 ***************************************************************************
 ***************************************************************************
 * This file demonstrates the following
 * 1. Initialization
 * 2. Creating a connection and logging in.
 * 3. Seeding and Generating a random sequence of bytes.
 * 4. Clean up.
 ***************************************************************************
 */

#include "vpkcs11_sample_helper.h"

/*
 ************************************************************************
 * Function: genRandom
 * Generate a random sequence of bytes of length randomLen
 *
 ************************************************************************
 * Parameters: seedMaterial, randomLen
 * Returns: CK_RV
 ************************************************************************
 */

static CK_RV genRandom (char* seedMaterial, CK_ULONG randomLen)
{
	CK_RV rc = CKR_OK;

	CK_BYTE  *pSeed = (CK_BYTE *) seedMaterial;
	CK_ULONG seedLen = seedMaterial != NULL ? (CK_ULONG) strlen(seedMaterial) : 0;
	CK_BYTE_PTR pRandom = (CK_BYTE_PTR)calloc(1, randomLen * sizeof(CK_BYTE));

	if(!pRandom) {
		fprintf (stderr, "Error allocating memory!");
		exit (4);
	}

	/* AES key template.
	 * CKA_LABEL is the name of the key and will be displayed on the DSM
	 * CKA_VALUE is the bytes that make up the AES key.
	 */
        if (0 < seedLen) {
	    rc = FunctionListFuncPtr->C_SeedRandom (hSession,
	   					    pSeed,
						    seedLen);
        }
	if (rc != CKR_OK)
	{
		fprintf (stderr, "Error in C_SeedRandom(), return value: %d\n", (int)rc);
		goto FREE_RESOURCES;
	}

	rc = FunctionListFuncPtr->C_GenerateRandom (hSession,
						pRandom,
						randomLen);

	if (rc != CKR_OK)
	{
		fprintf (stderr, "Error in C_GenerateRandom(), return value: %d\n", (int)rc);
		goto FREE_RESOURCES;
	}
	else {
        printf("Seed\t\t: %s\nOutput Length\t: %lu\nOutput\t\t: ", seedMaterial, randomLen);
		dumpHexArray(pRandom, (int)randomLen);
	}

 FREE_RESOURCES:
	if(pRandom) {
		free(pRandom);
		pRandom = NULL;
	}
	return rc;
}

/* Function to swap values at two pointers */
void swap(CK_BYTE *x, CK_BYTE *y)
{
    CK_BYTE temp;
    temp = *x;
    *x = *y;
    *y = temp;
}



void usage()
{
  printf ("Usage: vpkcs11_sample_create_object -p pin -s slotID -d seed_material -z random_data_size [-m module]\n");
  exit (2);
}


/*
 ************************************************************************
 * Function: main
 ************************************************************************
 */
int main(int argc, char* argv[])
{
    CK_RV  rc;
    char * pin = NULL;
    char * libPath = NULL;
	char * foundPath = NULL;
	char * seedMat = NULL;
    int slotId = 0;
	int random_sz = 0;

    int c;
    extern char *optarg;
    extern int optind;
    int loggedIn = 0;

    while ((c = newgetopt(argc, argv, "p:d:m:s:z:")) != EOF)
        switch (c) {
        case 'p':
            pin = optarg;
            break;
		case 'd':
			seedMat = optarg;
			break;
        case 'm':
            libPath = optarg;
            break;
		case 'z':
			random_sz = atoi(optarg);
			break;
		case 's':
			slotId = atoi(optarg);
			break;

        case '?':
        default:
            usage();
            break;
    }
    if ((NULL == pin) || (optind < argc))
    {
        usage();
    }

    printf("Begin Generate Random sample: ...\n");

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

		printf("Generate Random Data ...\n");
		rc = genRandom(seedMat, random_sz);

		if (rc != CKR_OK)
		{
			fprintf(stderr, "FAIL: C_GenerateRandom Error: %d.\n", (int)rc);
		}
		else
		{
			printf("Successfully called C_GenerateRandom for generating random byte sequence.\n");
		}
	} while (0);

    if (loggedIn)
    {
        if (logout() == CKR_OK)
        {
            printf("Successfully logged out.\n");
        }
    }

	cleanup ();
    printf("End Generate Random sample.\n");
    fflush(stdout);
	return rc;
}
