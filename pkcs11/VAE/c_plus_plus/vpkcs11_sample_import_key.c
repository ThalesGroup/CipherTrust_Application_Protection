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
 * File: vpkcs11_sample_import_key.c
 ***************************************************************************
 ***************************************************************************
 * This file is designed to be run after vpkcs11_sample_find_export_key and
 * demonstrates the following:
 * 1. Initialization
 * 2. Creating a connection and logging in.
 * 3. Querying for a key using the keyname.
 * 4. Import the key which was read from a file, into DSM, using the wrappingKey
 * 5. Check the existence of the imported key
 * 6. Clean up.
 */

#include "vpkcs11_sample_import_key.h"
#include "vpkcs11_sample_helper.h"

static CK_OBJECT_CLASS  objClass = CKO_SECRET_KEY;
static CK_OBJECT_CLASS  unwrappingObjClass = CKO_SECRET_KEY;

/*
********************************************
* Function: unwrapKey
********************************************
* Imports a key into the DataSecurity Manager wrapped with another key with wrapped key value.
*************************************************
* Parameters:
* phKey -- to hold the imported key handle into the new DSM
* hUnwrappingKey -- key handle used to wrap/unwrap the key above.
* 
**********************************************************
*/
static CK_RV unwrapKey (char * keyLabel, CK_OBJECT_HANDLE_PTR phKey, CK_OBJECT_HANDLE hUnwrappingKey, CK_BYTE_PTR pWrappedKey, CK_ULONG ulWrappedKeyLen, int format_type, char *KEYID, char *UUID, char *MUID)
{
	CK_RV rc;
	CK_MECHANISM	mechImportKey = { CKM_AES_CBC_PAD, def_iv, 16 }; 
	CK_UTF8CHAR	app[] = { "VORMETRIC_PKCS11_IMPORT_SAMPLE" };  

	CK_OBJECT_CLASS	keyClass = CKO_SECRET_KEY ;
	CK_KEY_TYPE	keyType = CKK_AES;  /* support importing symmetric key */
	CK_ULONG	keySize = DEFAULT_KEYLEN;   /* 32 bytes  */
	CK_BBOOL	bFalse = CK_FALSE;
	CK_BBOOL	bTrue = CK_TRUE; 

	CK_UTF8CHAR     *label = (CK_UTF8CHAR *) keyLabel;
	CK_ULONG        len = keyLabel ? (CK_ULONG) strlen(keyLabel) : 0;

	CK_ATTRIBUTE symKeyTemplate[20] = {
        /* type,            	pValue, 	ulValueLen     */
		{CKA_ID,				label,		len 			},
		{CKA_LABEL,				label,		len 	    	},
		{CKA_APPLICATION,		&app,		sizeof(app)		},
		{CKA_CLASS,				&keyClass,	sizeof(keyClass)},
		{CKA_KEY_TYPE,			&keyType,	sizeof(keyType)	}, 	
		{CKA_VALUE_LEN,			&keySize,	sizeof(keySize)	},
		{CKA_TOKEN,				&bTrue,		sizeof(bTrue)	},
		
		{CKA_ENCRYPT,			&bTrue,		sizeof(bTrue)	},
		{CKA_DECRYPT,			&bTrue,		sizeof(bTrue)	},
		{CKA_SIGN,				&bFalse,	sizeof(bFalse)	},
		{CKA_VERIFY,			&bFalse,	sizeof(bFalse)	},
		{CKA_WRAP,				&bTrue,		sizeof(bTrue)	},
		{CKA_UNWRAP,			&bFalse,	sizeof(bFalse)	},
		{CKA_EXTRACTABLE,		&bFalse,	sizeof(bFalse)	},
		{CKA_ALWAYS_SENSITIVE,	&bFalse,	sizeof(bFalse)	},
		{CKA_NEVER_EXTRACTABLE,	&bTrue,		sizeof(bTrue)	},
		{CKA_SENSITIVE,			&bTrue,		sizeof(bTrue)	},
	};

	CK_ULONG symKeyTemplateSize = sizeof(symKeyTemplate)/sizeof(CK_ATTRIBUTE)-3;

	CK_ATTRIBUTE	asymmKeyTemplate[10] = {

		{CKA_LABEL, label, len }, /* Keyname */
		{CKA_CLASS, &keyClass, sizeof(keyClass)},
		{CKA_KEY_TYPE,	&keyType,	sizeof(keyType)	}, 
		{CKA_ENCRYPT, &bTrue, sizeof(bTrue)},
		{CKA_VERIFY, &bTrue, sizeof(bTrue)},
		{CKA_WRAP, &bTrue, sizeof(bTrue)},
		{CKA_TOKEN, &bTrue, sizeof(bTrue)}
	};
	CK_ULONG asymmKeyTemplateSize = sizeof(asymmKeyTemplate)/sizeof(CK_ATTRIBUTE)-3;

	CK_ATTRIBUTE_PTR importKeyTemplate;
	CK_ULONG         importKeyTemplateSize;

	if(unwrappingObjClass != CKO_SECRET_KEY && hUnwrappingKey != CK_INVALID_HANDLE)
	{
	  mechImportKey.mechanism = CKA_THALES_DEFINED | CKM_RSA_PKCS;
	}
	
	if(objClass != CKO_SECRET_KEY && format_type != 0) {
		mechImportKey.mechanism |= (CK_MECHANISM_TYPE)(format_type | CKA_THALES_DEFINED);
		keyClass = objClass;
		keyType = CKK_RSA; 
		importKeyTemplate = asymmKeyTemplate;
		importKeyTemplateSize = asymmKeyTemplateSize;
	}
	else {
		importKeyTemplate = symKeyTemplate;
		importKeyTemplateSize = symKeyTemplateSize;
	}

	if (KEYID) {
		importKeyTemplate[importKeyTemplateSize].type = CKA_THALES_OBJECT_IKID;
		importKeyTemplate[importKeyTemplateSize].pValue = KEYID;
		importKeyTemplate[importKeyTemplateSize++].ulValueLen = (CK_ULONG)strlen(KEYID);
    }
	
    if (UUID) {
		importKeyTemplate[importKeyTemplateSize].type = CKA_THALES_OBJECT_UUID;
		importKeyTemplate[importKeyTemplateSize].pValue = UUID;
		importKeyTemplate[importKeyTemplateSize++].ulValueLen = (CK_ULONG)strlen(UUID);
    }
	
    if (MUID) {
		importKeyTemplate[importKeyTemplateSize].type = CKA_THALES_OBJECT_MUID;
		importKeyTemplate[importKeyTemplateSize].pValue = MUID;
		importKeyTemplate[importKeyTemplateSize++].ulValueLen = (CK_ULONG)strlen(MUID);
    }

	
	do
	{
		rc = FunctionListFuncPtr->C_UnwrapKey(hSession,
						      &mechImportKey, 
						      hUnwrappingKey,
						      pWrappedKey,
						      ulWrappedKeyLen,
						      importKeyTemplate,
						      importKeyTemplateSize,										    
						      phKey);
		
		if (rc != CKR_OK)
		{
			fprintf(stderr, "FAIL: call to C_UnwrapKey() failed: %x \n", (unsigned int)rc);
			break;
		}
		else
		{
			printf("C_UnwrapKey succeed, Imported key handle is: %x \n", (unsigned int)*phKey);		
		}

	} while (0);

	return rc;
}

/*
 ************************************************************************
 * Function: findnImportKey
 * This function first search for the source key and unwrapping key from DSM
 ************************************************************************
 * Parameters: none
 * Returns: CK_RV
 ************************************************************************
 */

static CK_RV findnImportKey (char* keyLabel, char* wrappingKeySearchId, char* key_filename, int format_type, char *KEYID, char *UUID, char *MUID)
{
	CK_RV            rc = CKR_OK;
	/* CK_OBJECT_CLASS		keyClass = CKO_SECRET_KEY; */
	CK_OBJECT_HANDLE hFoundKey = 0x0;
	CK_OBJECT_HANDLE hUnwrappingKey = CK_INVALID_HANDLE;
	/*	CK_OBJECT_CLASS  wrappingObjClass = CKO_SECRET_KEY; */
	
	FILE *           fp = NULL;
	CK_BYTE_PTR	 pBuf;
	int              bf_len;
	int              readlen = 0;
	CK_BYTE          pWrapped[4096];
	CK_ULONG         ulWrappedKeyLen = 0;
	CK_OBJECT_HANDLE hImportKey;
	
	if(wrappingKeySearchId != NULL)
	{
		rc = findKey(wrappingKeySearchId, keyIdLabel, unwrappingObjClass, &hUnwrappingKey);

		if (CK_INVALID_HANDLE == hUnwrappingKey)
		{
	        fprintf (stderr, "FAIL: Cannot find the unwrapping key: %s.\n", wrappingKeySearchId);
		}
		else
		{
			printf ("Found unwrapping key : %s successfully; key handle: 0x%x.\n", wrappingKeySearchId, (unsigned int)hUnwrappingKey);
		}
	}

	if(keyLabel != NULL)
	{
		rc = findKey(keyLabel, keyIdLabel, objClass, &hFoundKey);

		if (CK_INVALID_HANDLE == hFoundKey)
		{
			fprintf (stderr , "The source key: %s doesn't exist in DSM; proceed with unwrapping (importing) to DSM\n", keyLabel);
		}
		else
		{
			printf ("Found source key : %s already exist in the DSM! Exiting...\n", keyLabel);
			return CKR_ARGUMENTS_BAD;
		}
	}

	/* read wrapped key bytes from input file */
	fp = fopen(key_filename, "r+");
		
	if (!fp) {
		fprintf(stderr, "Unable to open input key file: %s", key_filename);
		return CKR_GENERAL_ERROR;
	}
	else {
		memset(pWrapped, 0, sizeof(pWrapped));
		do
		{
			bf_len = READ_BLK_LEN;
			pBuf = NULL;
			readlen = fgetline((char**)&pBuf, &bf_len, fp);

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
			
			if(strstr( (char*)pBuf, "Key Value:" ) != NULL)
			{
				readlen = (int)fread(pWrapped, sizeof(CK_BYTE), sizeof(pWrapped), fp);
								
				if(readlen < 32) {
					fprintf(stderr, "Error reading key bytes, wrapped key bytes length = %d", (int)readlen);
					fclose(fp);	
					return CKR_GENERAL_ERROR;
				}
				
				ulWrappedKeyLen = readlen; /* (readlen/16) * 16; */
				printf("Read wrapped key bytes length = %d\n", (int)ulWrappedKeyLen);
				break;
			}					   			
		} while (readlen >= 0);
		
		if(keyLabel != NULL) {
			rc = unwrapKey(keyLabel, &hImportKey, hUnwrappingKey, pWrapped, ulWrappedKeyLen, format_type, KEYID, UUID, MUID);
			if (rc == CKR_OK)
			{
				printf ("Successfully unwrapped and imported key with handle: 0x%x with unwrapping key %s into DSM.\n", (unsigned int)hImportKey, wrappingKeySearchId != NULL ? wrappingKeySearchId : "no" );
			}
			else {
				printf ("unwrapAndImportKey failed, error code %08x\n", (unsigned) rc);
			}
		}
		fclose(fp);	
	}

	return rc;
}

void importKeyUsage()
{
	printf ("Usage: vpkcs11_sample_import_key -p pin -s slotID -{k|c|v} key_name|asymm_key_name -i key_filename [-u unwrappingKeyName] [-f format] [-m module] [-K imported keyid] [-M imported MUID] [-U imported UUID]\n");
	printf ("-k to be unwrapped/imported key name onto the DSM; take the form of {s|c|v}:key_name. \n");
	printf ("-u unwrapping key label in the DSM.\n");
	printf ("-i key filename that contains the wrapped key bytes.\n");
	printf ("-f format type: one of 'pem' or 'der' for asymmetric key output type, omit for symmetric keys.\n");
	exit (1);
}

/*
 ************************************************************************
 * Function: main
 ************************************************************************
 */

#ifdef THALES_CLI_MODE
int importKeySample (int argc, char* argv[])
#else
int main(int argc, char* argv[])
#endif
{
	CK_RV rc;
    char *keyLabel = NULL;
    char *pin = NULL;
    char *libPath = NULL;
	char *foundPath = NULL;
    char *unwrappingKeyLabel = NULL;

	char        *KEYID=NULL;
	char        *UUID=NULL;
	char        *MUID=NULL;
	char        *input_filename = NULL;
	CK_OBJECT_HANDLE hKey;

	int   format_type = CKA_RAW_FORMAT;
	int   slotId = 0;
    int   c;
	extern char *optarg;
	extern int optind;

   	int loggedIn = 0;
		
	optind = 1; /* resets optind to 1 to call getopt() multiple times in sample_cli */

	while ((c = newgetopt(argc, argv, "p:k:v:c:u:m:s:f:i:K:U:M:")) != EOF)
		switch (c) {
		case 'p':
			pin = optarg;
			break;
		case 'k':
			keyLabel = parse_key_class(optarg, &objClass);			
			break;
		case 'c':
			keyLabel = optarg;
			objClass = CKO_PUBLIC_KEY;	
			break;
		case 'v':
			keyLabel = optarg;
			objClass = CKO_PRIVATE_KEY;	
			break;	
		case 'u':
			unwrappingKeyLabel = parse_key_class(optarg, &unwrappingObjClass);	
			break;
		case 'm':
			libPath = optarg;
			break;
		case 's':
			slotId = atoi(optarg);
			break;
		case 'f':
			format_type = parse_format_type(optarg);
			break;
		case 'i':
			input_filename = optarg;
			break;
		case 'K':
			KEYID=optarg;
			break;
		case 'U':
			UUID =optarg;
			break;
		case 'M':
			MUID =optarg;
			break;
			
		case '?':
		default:
			importKeyUsage();
			break;
	}

	if ((NULL == pin) || (optind < argc) || !input_filename)
	{
		importKeyUsage();
	}

    printf("Begin Import Key sample.\n");

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

		if(!input_filename) {
			fprintf(stderr, "Filename is NULL.");
			break;
		}
		
		printf("Successfully logged in. \n Importing key from %s \n", input_filename);
		
		rc = findnImportKey(keyLabel, unwrappingKeyLabel, input_filename, format_type, KEYID, UUID, MUID);

		if (rc != CKR_OK) {
			fprintf(stderr, "Error: when importing key: %s, rc=%x.\n", keyLabel, (unsigned int)rc);
			break;
		}
		
		rc = findKey(keyLabel, keyIdLabel, objClass, &hKey);

		if (rc != CKR_OK) {
			fprintf(stderr, "Error: when finding imported key: %s, rc=%x.\n", keyLabel, (unsigned int)rc);			
		}

		if(hKey == CK_INVALID_HANDLE)
		{
	        fprintf (stderr, "FAIL: Cannot find the imported key: %s.\n", keyLabel);
		}
		else
		{
			printf ("Success: Found imported key %s, with key handle: %x.\n", keyLabel, (unsigned int)hKey);
		}
		
	} while (0);

    if (loggedIn)
    {
        if (logout() == CKR_OK)
        {
            printf("Successfully logged out.\n");
        }
    }

    cleanup();
    printf("End Find and Export Key sample.\n");
    fflush(stdout);;
	return rc;
}
