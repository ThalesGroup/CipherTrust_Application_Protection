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
 * File: vpkcs11_sample_create_object.c
 ***************************************************************************
 ***************************************************************************
 * This file demonstrates the following
 * 1. Initialization
 * 2. Creating a connection and logging in.
 * 3. Registering a key on the Data Security Manager
 * 4. Clean up.
 ***************************************************************************
 */

#include "vpkcs11_sample_helper.h"

/* 
 ************************************************************************
 * Function: createObject
 * Imports an AES 256 key into the DSM. 
 * The keyLabel is the name of the key displayed on the DSM.
 ************************************************************************
 * Parameters: keyLabel
 * Returns: CK_RV
 ************************************************************************
 */

static CK_RV createObject (char* keyLabel)
{
	CK_RV rc = CKR_OK;
    CK_UTF8CHAR			app[] = { "VORMETRIC_PKCS11_SAMPLE" };
	CK_UTF8CHAR  		keyValue[KEYLEN] = {
        't', 'h', 'i', 's', ' ', 'i', 's', ' ',
        'm', 'y', ' ', 's', 'a', 'm', 'p', 'l',
        'e', ' ', 'k', 'e', 'y', ' ', 'd', 'a',
        't', 'a', ' ', '5', '4', '3', '2', '1' };
	 
    CK_OBJECT_CLASS		keyClass = CKO_SECRET_KEY;
	CK_KEY_TYPE			keyType = CKK_AES; 
	CK_ULONG			keySize = KEYLEN; /* 256 bits */ 
	CK_BBOOL			bFalse = CK_FALSE;
	CK_BBOOL			bTrue = CK_TRUE;
    CK_OBJECT_HANDLE	hKey = 0x0;

	CK_UTF8CHAR  *label = (CK_UTF8CHAR *) keyLabel;
	CK_ULONG len = (CK_ULONG) strlen(keyLabel);

	/* AES key template. 
	 * CKA_LABEL is the name of the key and will be displayed on the DSM
	 * CKA_VALUE is the bytes that make up the AES key. 
	 */

	CK_ATTRIBUTE aesKeyTemplate[19] = {
		{CKA_ID,			label,	len},
		{CKA_LABEL,			label,	len},
		{CKA_APPLICATION,	&app,		sizeof(app)		},
		{CKA_CLASS,			&keyClass,	sizeof(keyClass)},
		{CKA_KEY_TYPE,		&keyType,	sizeof(keyType)	},
		{CKA_VALUE,			&keyValue,	sizeof(keyValue)},
		{CKA_VALUE_LEN,		&keySize,	sizeof(keySize)	},
		{CKA_TOKEN,			&bTrue,		sizeof(bTrue)	},
		{CKA_ENCRYPT,		&bTrue,		sizeof(bTrue)	},
		{CKA_DECRYPT,		&bTrue,		sizeof(bTrue)	},
		{CKA_SIGN,			&bFalse,	sizeof(bFalse)	},
		{CKA_VERIFY,		&bFalse,	sizeof(bFalse)	},
		{CKA_WRAP,			&bTrue,		sizeof(bTrue)	},
		{CKA_UNWRAP,		&bFalse,	sizeof(bFalse)	},
		{CKA_EXTRACTABLE,		&bFalse,	sizeof(bFalse)	},
		{CKA_ALWAYS_SENSITIVE,	&bFalse,	sizeof(bFalse)	},
		{CKA_NEVER_EXTRACTABLE,	&bTrue,		sizeof(bTrue)	},
		{CKA_MODIFIABLE,	&bTrue, sizeof(bTrue)},
		{CKA_SENSITIVE,			&bTrue,		sizeof(bTrue)	}
	};
	CK_ULONG	aesKeyTemplateSize = sizeof(aesKeyTemplate)/sizeof(CK_ATTRIBUTE);
	
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

void usage()
{
  printf ("Usage: vpkcs11_sample_create_object -p pin -s slotID -k keyName [-m module]\n");
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
    char * keyLabel = NULL;
    char * pin = NULL;
    char * libPath = NULL;
	char * foundPath = NULL;
    int slotId = 0;

    int c;
    extern char *optarg;
    extern int optind;
    int loggedIn = 0;

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

    printf("Begin Create Object sample: ...\n");

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

		if (findKeyByName(keyLabel) != CK_INVALID_HANDLE)
		{
			fprintf(stderr, "FAIL: Key with same name already exist. \n");
			break;
		}

		printf("Registering key ...\n");
		rc = createObject(keyLabel);

		if (rc != CKR_OK)
		{
			fprintf(stderr, "FAIL: Key object registration failed.\n");
		}
		else
		{
			printf("Successfully called C_CreateObject key.\n");
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
    printf("End Create Object sample.\n");
    fflush(stdout);
	return 0;
}

