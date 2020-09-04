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
 * File: vpkcs11_sample_keypair_create_sign.c
 ***************************************************************************
 ***************************************************************************
 * This file demonstrates the following
 * 1. Initialization
 * 2. Creating a connection and logging in.
 * 3. Creating a keypair on the Data Security Manager 
 * 4. Signing a piece of data with the created keypair
 * 5. Delete the keypair.
 * 5. Clean up.
 */

#include "vpkcs11_sample_helper.h"
/*
 ***************************************************************************
 * local variables
 **************************************************************************
 */

static CK_OBJECT_HANDLE	hKeyRSAPublic = 0x0;
static CK_OBJECT_HANDLE	hKeyRSAPrivate = 0x0;
/* static CK_BYTE			data[] = { "some data" }; */
static CK_OBJECT_HANDLE	hPublicKey = 0x0;
static CK_OBJECT_HANDLE	hPrivateKey = 0x0;

#define ASYMKEY_BUF_LEN 4096
/* 
 ************************************************************************
 * Function: createKeyPair
 * Creates an RSA keypair on the DSM. 
 * The keyLabel is the name of the key displayed on the DSM.
 * modulusBits is the key strength. In this case, 2048 bits
 ************************************************************************
 * Parameters: none
 * Returns: CK_RV
 ************************************************************************
 */

static CK_RV createKeyPair (char * keyLabel)
{
	/* C_GenerateKeyPair */
	
	CK_MECHANISM		mechanism = { CKM_RSA_PKCS_KEY_PAIR_GEN, NULL_PTR, 0 };
	CK_ULONG			modulusBits = 2048;
	CK_BYTE				publicExponent[4] = { 0x01, 0x00, 0x01, 0x00 }; /* 65537 in bytes */
	CK_BBOOL			bTrue = CK_TRUE;
	CK_OBJECT_CLASS		pubkey_class = CKO_PUBLIC_KEY;
	CK_OBJECT_CLASS		privkey_class = CKO_PRIVATE_KEY;
	CK_ULONG            keyLabel_len = (CK_ULONG)strlen((const char *)keyLabel);

	CK_ATTRIBUTE	publicKeyTemplate[] = {
		{CKA_LABEL, keyLabel, keyLabel_len }, /* Keyname */
		{CKA_CLASS, &pubkey_class, sizeof(pubkey_class)},
		{CKA_ENCRYPT, &bTrue, sizeof(bTrue)},
		{CKA_VERIFY, &bTrue, sizeof(bTrue)},
		{CKA_WRAP, &bTrue, sizeof(bTrue)},
		{CKA_TOKEN, &bTrue, sizeof(bTrue)},
		{CKA_MODIFIABLE, &bTrue, sizeof(bTrue)},
		{CKA_PUBLIC_EXPONENT, publicExponent, sizeof(publicExponent)},
		{CKA_MODULUS_BITS, &modulusBits, sizeof(modulusBits)}
	};

	CK_ATTRIBUTE	privateKeyTemplate[] = {
		{CKA_LABEL, keyLabel, keyLabel_len }, /* Keyname*/
		{CKA_CLASS, &privkey_class, sizeof(privkey_class)},
		{CKA_TOKEN, &bTrue, sizeof(bTrue)},
		{CKA_PRIVATE, &bTrue, sizeof(bTrue)},
		{CKA_SENSITIVE, &bTrue, sizeof(bTrue)},
		{CKA_DECRYPT, &bTrue, sizeof(bTrue)},
		{CKA_SIGN, &bTrue, sizeof(bTrue)},
		{CKA_MODIFIABLE, &bTrue, sizeof(bTrue)},
		{CKA_UNWRAP, &bTrue, sizeof(bTrue)}
	};

	CK_RV		rc = CKR_OK;
	CK_ULONG	publicKeyTemplateSize = sizeof(publicKeyTemplate)/sizeof(CK_ATTRIBUTE);
	CK_ULONG	privateKeyTemplateSize = sizeof(privateKeyTemplate)/sizeof(CK_ATTRIBUTE);
	
	rc = FunctionListFuncPtr->C_GenerateKeyPair(
												hSession,
												&mechanism,
												publicKeyTemplate, publicKeyTemplateSize,
												privateKeyTemplate, privateKeyTemplateSize,
												&hKeyRSAPublic,
												&hKeyRSAPrivate
												);

	if (rc != CKR_OK || hKeyRSAPublic == 0 || hKeyRSAPrivate == 0)
		{
			printf ("Error generating Key Pair\n");
			return rc;
		}
	return rc;
}

static CK_RV getAttributesValue(CK_OBJECT_HANDLE hKey)
{
	CK_RV		rc = CKR_OK;
	CK_BYTE     modulusBuf[ASYMKEY_BUF_LEN];

	CK_ULONG	modulusBits;	
	unsigned int i;
	
	CK_BYTE     publicExpoBuf[ASYMKEY_BUF_LEN];
	CK_BYTE     privateExpoBuf[ASYMKEY_BUF_LEN];

	CK_BYTE     keyIdBuf[256];
	char        keyLabel[256];

	CK_OBJECT_CLASS	keyCls;
	CK_ULONG    attrValueLen;
	
	char *      pAttr = NULL;
	
	CK_ATTRIBUTE getAttrsTemplate[] =
	{
		{CKA_ID, keyIdBuf, sizeof(keyIdBuf) },
		{CKA_LABEL, keyLabel, sizeof(keyLabel) },
		{CKA_CLASS, &keyCls, sizeof(keyCls) },

		{CKA_PRIVATE_EXPONENT, privateExpoBuf, sizeof(privateExpoBuf) },
		{CKA_PUBLIC_EXPONENT, publicExpoBuf, sizeof(publicExpoBuf) },
		{CKA_MODULUS, modulusBuf, sizeof(modulusBuf) },		
		{CKA_MODULUS_BITS, &modulusBits, sizeof(modulusBits)}
	};
	CK_ULONG	getAttrsTemplateSize = sizeof(getAttrsTemplate)/sizeof(CK_ATTRIBUTE);
	
	rc = FunctionListFuncPtr->C_GetAttributeValue(hSession ,
												  hKey,
												  getAttrsTemplate,
												  getAttrsTemplateSize);

	if (rc != CKR_OK)
	{
		printf ("Error getting key attributes: %08x.\n", (unsigned int)rc);
		return rc;
	}
	
	printf("CKA_LABEL: %s.\n", keyLabel);
	printf("CKA_CLASS: %08x.\n", (unsigned int)keyCls);
	
	printf("CKA_MODULUS: ");
	attrValueLen = getAttrsTemplate[5].ulValueLen;
	pAttr = (char *)calloc(sizeof(CK_BYTE), attrValueLen*2+1);
	if(pAttr == NULL)
	{
		printf("Error allocating memory.");
		return CKR_HOST_MEMORY;
	}

	for(i = 0; i<attrValueLen; i++)
	{
		snprintf(pAttr+i*2, 3, "%02x", modulusBuf[i]);	
	}	
	pAttr[i*2] = '\0';
	printf("\t %s.\n", pAttr);

	if(pAttr)
		free(pAttr);
	
	printf("CKA_PUBLIC_EXPONENT: ");
	attrValueLen = getAttrsTemplate[4].ulValueLen;
	pAttr = (char *)calloc(sizeof(CK_BYTE), attrValueLen*2+1);
	if(pAttr == NULL)
	{
		printf("Error allocating memory.");
		return CKR_HOST_MEMORY;
	}
	
	for(i = 0; i<attrValueLen; i++)
	{
		snprintf(pAttr+i*2, 3, "%02x", publicExpoBuf[i]);	
	}
	pAttr[i*2] = '\0';
	printf("\t %s.\n", pAttr);

	if(pAttr)
		free(pAttr);
	
	printf("CKA_PRIVATE_EXPONENT: ");
	attrValueLen = getAttrsTemplate[3].ulValueLen;
	
	pAttr = (char *)calloc(sizeof(CK_BYTE), attrValueLen*2+1);
	if(pAttr == NULL)
	{
		printf("Error allocating memory.");
		return CKR_HOST_MEMORY;
	}
	
	for(i = 0; i<attrValueLen; i++)
	{
		snprintf(pAttr+i*2, 3, "%02x", privateExpoBuf[i]);	
	}
	pAttr[i*2] = '\0';
	printf("\t %s.\n", pAttr);

	if(pAttr)
		free(pAttr);

	printf("CKA_MODULUS_BITS: %u.\n", (unsigned int)modulusBits);
	
	return rc;
}

static CK_RV getSymAttributesValue(CK_OBJECT_HANDLE hKey)
{
	CK_RV		rc = CKR_OK;
	CK_DATE     endDate;
	CK_BYTE     keyIdBuf[256]; 
	char        keyLabel[256];
	CK_OBJECT_CLASS	keyCls;
	char ch_year[5];
	char ch_mon[3];
	char ch_mday[3];
	
	CK_ATTRIBUTE getAttrsTemplate[] =
	{
		{CKA_ID, keyIdBuf, sizeof(keyIdBuf) }, 
		{CKA_LABEL, keyLabel, sizeof(keyLabel) },
		{CKA_CLASS, &keyCls, sizeof(keyCls) },		
		{CKA_END_DATE, &endDate, sizeof(endDate)}
	};

	CK_ULONG	getAttrsTemplateSize = sizeof(getAttrsTemplate)/sizeof(CK_ATTRIBUTE);
	
	rc = FunctionListFuncPtr->C_GetAttributeValue(hSession ,
												  hKey,
												  getAttrsTemplate,
												  getAttrsTemplateSize);

	if (rc != CKR_OK)
	{
		printf ("Error getting key attributes: %08x.\n", (unsigned int)rc);
		return rc;
	}

	printf("CKA_LABEL: %s.\n", keyLabel);
	printf("CKA_CLASS: %08x.\n", (unsigned int)keyCls);

	memcpy(ch_year, endDate.year, sizeof(endDate.year));
	ch_year[4] = '\0';
	memcpy(ch_mon, endDate.month, sizeof(endDate.month));
	ch_mon[2] = '\0';
	memcpy(ch_mday, endDate.day, sizeof(endDate.day));
	ch_mday[2] = '\0';
	
	printf("CKA_END_DATE: year: %s, month: %s, day: %s.\n", ch_year, ch_mon, ch_mday);
	return rc;
}

static CK_RV setAttributeValue(CK_OBJECT_HANDLE hKey, int symmetric)
{
	CK_RV		rc = CKR_OK;
	CK_CHAR     modulusBuf[ASYMKEY_BUF_LEN*2+1];
	CK_DATE     endDate;	
	CK_ATTRIBUTE_PTR setAttrsTemplate;
	CK_ULONG	setAttrsTemplateSize;
	unsigned int i;
	
	CK_ATTRIBUTE setAttrsTemplateAsymm[] = 
		{			
			{CKA_MODULUS, modulusBuf, sizeof(modulusBuf) }
		};

	CK_ATTRIBUTE setAttrsTemplateSymm[] = 
		{			
			{CKA_END_DATE, &endDate, sizeof(endDate) }
		};	
 
	if(!symmetric) {
				
		for(i = 0; i<ASYMKEY_BUF_LEN*2; i+=2)
		{
			snprintf(((char *)modulusBuf)+i, 2, "%02x", 255);	
		}
		setAttrsTemplate = setAttrsTemplateAsymm;
		setAttrsTemplateSize = 1;
	}
	else {
		memcpy(endDate.year, "2020", sizeof(endDate.year));
		memcpy(endDate.month, "08", sizeof(endDate.month));
		memcpy(endDate.day, "30", sizeof(endDate.day));
		setAttrsTemplate = setAttrsTemplateSymm;
		setAttrsTemplateSize = 1;
	}
		
	rc = FunctionListFuncPtr->C_SetAttributeValue(hSession ,
												  hKey,
												  setAttrsTemplate,
												  setAttrsTemplateSize);

	if (rc != CKR_OK)
	{
		printf ("Error Setting key attributes: %08x.\n", (unsigned int)rc);
		return rc;
	}
	return rc;
}

void usage()
{
  printf ("Usage: vpkcs11_sample_attributes -p pin -s slotID -k[p] keyName [-m module]\n");
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

    char *pin = NULL;
    char *libPath = NULL;
	char *foundPath = NULL;
	char *keyLabel = NULL;

	int symmetric = 1;
	int slotId = 0;
	int c;
	CK_OBJECT_HANDLE hKey;
	extern char *optarg;
	extern int optind;
    int loggedIn = 0;	
	
	while ((c = getopt(argc, argv, "p:kp:m:s:")) != EOF)
		switch (c) {
		case kp:
			keyLabel = optarg;
			symmetric = 0;
			break;
		case 'p':
			pin = optarg;
			break;
		case 'k':
			keyLabel = optarg;
			symmetric = 1;
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

    printf("Begin Get and Set Attributes Sample: ...\n");
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

		if(symmetric == 0)
		{
			hPrivateKey = findKey(keyLabel, CKO_PRIVATE_KEY);
			if (CK_INVALID_HANDLE == hPrivateKey)
			{
				printf("Keypair does not exist, Creating key pair...\n");
				rc = createKeyPair(keyLabel);
				if (rc != CKR_OK)
				{
					break;
				}
				printf("Successfully created key pair.\n");
			}
			else if(keyLabel)
			{
				printf("Asymmetric keypair %s already exist.\n", keyLabel);
				hKeyRSAPrivate = hPrivateKey;
				hKeyRSAPublic = findKey(keyLabel, CKO_PUBLIC_KEY);
			}
			
			hPublicKey = findKey(keyLabel, CKO_PUBLIC_KEY);
			if (CK_INVALID_HANDLE == hPublicKey)
			{
				printf("Finding public key failed.\n");
			}
			else
			{
				printf("Finding public key succeed.\n");			
				getAttributesValue(hPublicKey);
				/* setAttributeValue(hPublicKey, symmetric); */
			}
			
			hPrivateKey = findKey(keyLabel, CKO_PRIVATE_KEY);
			if (CK_INVALID_HANDLE == hPrivateKey)
			{
				printf("Finding private key failed.\n");
			}
			else
			{
				printf("Finding private key succeed.\n");		
				getAttributesValue(hPrivateKey);
				/* setAttributeValue(hPrivateKey, symmetric); */
			}
		}
		else if( keyLabel ) {
			hKey = findKey(keyLabel, CKO_SECRET_KEY);

			if(hKey == CK_INVALID_HANDLE)
			{
				printf("Symmetric key: %s does not exist, Creating key...\n", keyLabel);
				rc = createKey(keyLabel);
		
				if ((hKey=findKeyByName(keyLabel)) != CK_INVALID_HANDLE)
				{			
					fprintf(stdout, "Key with name: %s created on DSM. \n", keyLabel);
				}
				else {
					fprintf(stderr, "Failed to create key with name: %s on DSM. \n", keyLabel);
					break;
				}				
			}
			else {
				printf("Symmetric key: %s already exist.\n", keyLabel);
			}

			getSymAttributesValue(hKey);
			setAttributeValue(hKey, symmetric);
			getSymAttributesValue(hKey);
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

    cleanup();
    printf("End Get/Set key attributes sample.\n");
    fflush(stdout);
	return 0;
}

