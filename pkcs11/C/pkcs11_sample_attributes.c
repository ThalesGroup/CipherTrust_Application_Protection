 /*************************************************************************
**                                                                      **
** Copyright(c) 2022                              Confidential Material **
**                                                                      **
** This file is the property of Thales Group.                           **
** The contents are proprietary and confidential.                       **
** Unauthorized use, duplication, or dissemination of this document,    **
** in whole or in part, is forbidden without the express consent of     **
** Thales Group.                                                        **
**                                                                      **
**************************************************************************/
/*
 ***************************************************************************
 * File: pkcs11_sample_attributes.c
 ***************************************************************************
 ***************************************************************************
 * This file demonstrates the following
 * 1. Initialization
 * 2. Creating a connection and logging in.
 * 3. Creating a symmetric key or asymmetric keypair with custom attributes on the Key Manager
 * 4. If Key already exists, setting specific key attributes
 * 5. Retrieving and printing out the key attributes
 * 5. Clean up.
 */

#ifndef __WINDOWS__
#include <unistd.h>
#else
#define getopt newgetopt
#endif

#include "pkcs11_sample_attributes.h"
#include "pkcs11_sample_helper.h"
/*
 ***************************************************************************
 * local variables
 **************************************************************************
 */

static char  DEFAULT_CUSTOM_VALUE[] = { "default custom value" };
static char plainSerial[] = "0123456789-abcdefghijklmnopqrstuvwxyz;:,.ABCDEFGHIJKLMNOPQRSTUVWXYZ";

/* static CK_BYTE			data[] = { "some data" }; */
static CK_OBJECT_HANDLE	hPublicKey = 0x0;
static CK_OBJECT_HANDLE	hPrivateKey = 0x0;

extern unsigned long ulCachedTime;

/*static char def_passwd[] = { "Pas$w0rd#" }; */
/*static char def_passwd2[] = { "Passw0rd!" }; */

/*
 ************************************************************************
 * Function: createKeyPair
 * Creates an RSA/ECC keypair on the Key Manager.
 * The keyLabel is the name of the key displayed on the Key Manager.
 * curveOid for ECC keys only
 ************************************************************************
 * Parameters: none
 * Returns: CK_RV
 ************************************************************************
 */

static CK_RV createKeyPair(char *keyLabel, char *custom1, char *custom2, char *custom3, char *curveOid)
{
    /* C_GenerateKeyPair */
    CK_OBJECT_HANDLE    hKeyPublic, hKeyPrivate;
    CK_MECHANISM    mechanism = { CKM_RSA_PKCS_KEY_PAIR_GEN, NULL_PTR, 0 };
    CK_MECHANISM	ecmechanism = { CKM_ECDSA_KEY_PAIR_GEN, NULL_PTR, 0 };
    CK_ULONG    modulusBits = 2048;
    CK_BYTE     publicExponent[4] = { 0x01, 0x00, 0x01, 0x00 }; /* 65537 in bytes */
    CK_BBOOL    bTrue = CK_TRUE;
    CK_OBJECT_CLASS   pubkey_class = CKO_PUBLIC_KEY;
    CK_OBJECT_CLASS   privkey_class = CKO_PRIVATE_KEY;
    CK_ULONG     keyLabel_len = (CK_ULONG)strlen((const char *)keyLabel);
    CK_KEY_TYPE  keytype = CKK_RSA;

    CK_UTF8CHAR  *ca1 = (CK_UTF8CHAR *)custom1;
    CK_ULONG     caLen1 = custom1 ? (CK_ULONG) strlen(custom1) : 0;
    CK_UTF8CHAR  *ca2 = (CK_UTF8CHAR *)custom2;
    CK_ULONG     caLen2 = custom2 ? (CK_ULONG) strlen(custom2) : 0;
    CK_UTF8CHAR  *ca3 = (CK_UTF8CHAR *)custom3;
    CK_ULONG     caLen3 = custom3 ? (CK_ULONG) strlen(custom3) : 0;

    if (curveOid) {
        mechanism = ecmechanism;
        keytype = CKK_EC;
    }

    CK_ATTRIBUTE publicKeyTemplate[] =
    {
        {CKA_LABEL, keyLabel, keyLabel_len }, /* Keyname */
        {CKA_CLASS, &pubkey_class, sizeof(pubkey_class)},
        {CKA_ENCRYPT, &bTrue, sizeof(bTrue)},
        {CKA_VERIFY, &bTrue, sizeof(bTrue)},
        {CKA_WRAP, &bTrue, sizeof(bTrue)},
        {CKA_TOKEN, &bTrue, sizeof(bTrue)},
        {CKA_PUBLIC_EXPONENT, publicExponent, sizeof(publicExponent)},
        {CKA_MODULUS_BITS, &modulusBits, sizeof(modulusBits)} ,
        {CKA_THALES_CUSTOM_1, ca1, caLen1 },
        {CKA_THALES_CUSTOM_2, ca2, caLen2 },
        {CKA_THALES_CUSTOM_3, ca3, caLen3 }
    };
    // In CipherTrust mode, By default EXTRACTABLE and MODIFIABLE are not set to True
    CK_ATTRIBUTE privateKeyTemplate[] =
    {
        {CKA_LABEL, keyLabel, keyLabel_len }, /* Keyname*/
        {CKA_CLASS, &privkey_class, sizeof(privkey_class)},
        {CKA_TOKEN, &bTrue, sizeof(bTrue)},
        {CKA_PRIVATE, &bTrue, sizeof(bTrue)},
        {CKA_SENSITIVE, &bTrue, sizeof(bTrue)},
        {CKA_DECRYPT, &bTrue, sizeof(bTrue)},
        {CKA_SIGN, &bTrue, sizeof(bTrue)},
        {CKA_UNWRAP, &bTrue, sizeof(bTrue)},
        {CKA_THALES_CUSTOM_1, ca1, caLen1 },
        {CKA_THALES_CUSTOM_2, ca2, caLen2 },
        {CKA_THALES_CUSTOM_3, ca3, caLen3 },
        {CKA_EXTRACTABLE, &bTrue, sizeof(bTrue)},
        {CKA_MODIFIABLE, &bTrue, sizeof(bTrue)},
        {CKA_KEY_TYPE, &keytype, sizeof(keytype)},
        {CKA_MODULUS_BITS, &modulusBits, sizeof(modulusBits)}
    };

    if (curveOid) {
        CK_ATTRIBUTE keytypeAttr = {CKA_KEY_TYPE, &keytype, sizeof(keytype)};
        CK_ATTRIBUTE ecParamAttr = {CKA_EC_PARAMS, curveOid, (CK_ULONG)strlen((const char *)curveOid)};
        publicKeyTemplate[6] = keytypeAttr;
        publicKeyTemplate[7] = ecParamAttr;
        privateKeyTemplate[14] = ecParamAttr;
    }

    CK_RV    rc = CKR_OK;
    CK_ULONG publicKeyTemplateSize = sizeof(publicKeyTemplate)/sizeof(CK_ATTRIBUTE);
    CK_ULONG privateKeyTemplateSize = sizeof(privateKeyTemplate)/sizeof(CK_ATTRIBUTE);

    rc = FunctionListFuncPtr->C_GenerateKeyPair(hSession,
            &mechanism,
            publicKeyTemplate, publicKeyTemplateSize,
            privateKeyTemplate, privateKeyTemplateSize,
            &hKeyPublic,
            &hKeyPrivate
                                               );

    if (rc != CKR_OK || hKeyPublic == 0 || hKeyPrivate == 0)
    {
        printf ("Error generating Key Pair: rc=0x%8x\n", (unsigned int)rc);
        return rc;
    }
    return rc;
}

static CK_RV setKeyAttributeValue(CK_OBJECT_HANDLE hKey, int symmetric, char *custom4, char *custom5)
{
    CK_RV rc = CKR_OK;
    CK_CHAR     ckaSerialBuf[ASYMKEY_BUF_LEN*2+1];
    CK_BYTE     ckaIdBuf[ASYMKEY_BUF_LEN*2+1];
    CK_ATTRIBUTE_PTR setAttrsTemplate;
    CK_ULONG	 setAttrsTemplateSize;
    unsigned int i;
    CK_UTF8CHAR  *custAttribute4 = (CK_UTF8CHAR *) custom4;
    CK_ULONG     custAttributeLen4 = custom4 ? (CK_ULONG) strlen(custom4) : 0;
    CK_UTF8CHAR  *custAttribute5 = (CK_UTF8CHAR *) custom5;
    CK_ULONG     custAttributeLen5 = custom5 ? (CK_ULONG) strlen(custom5) : 0;

    CK_ATTRIBUTE setAttrsTemplateAsymm[] =
    {
        {CKA_THALES_CUSTOM_4, custAttribute4, custAttributeLen4 },
        {CKA_THALES_CUSTOM_5, custAttribute5, custAttributeLen5 }
    };

    CK_ATTRIBUTE setAttrsTemplateSymm[] =
    {
        {CKA_THALES_CUSTOM_4, custAttribute4, custAttributeLen4 },
        {CKA_THALES_CUSTOM_5, custAttribute5, custAttributeLen5 }
    };

    printf("CKA_THALES_CUSTOM_4 will be set to '%s', CKA_THALES_CUSTOM_5 will be set to '%s' for %s key\n", custom4, custom5, symmetric ? "symmetric" : "asymmetric");

    if (!symmetric)
    {
        setAttrsTemplate = setAttrsTemplateAsymm;
        setAttrsTemplateSize = sizeof(setAttrsTemplateAsymm) / sizeof(CK_ATTRIBUTE);
    }
    else
    {
        for (i = 0; i<ASYMKEY_BUF_LEN*2; i+=2)
        {
            snprintf(((char *)ckaIdBuf)+i, 3, "%02x", 255);
        }
        snprintf(((char *)ckaSerialBuf), sizeof(plainSerial), "%s", plainSerial);

        setAttrsTemplate = setAttrsTemplateSymm;
        setAttrsTemplateSize = sizeof(setAttrsTemplateSymm) / sizeof(CK_ATTRIBUTE);
    }

    rc = FunctionListFuncPtr->C_SetAttributeValue(hSession,
            hKey,
            setAttrsTemplate,
            setAttrsTemplateSize);

    if (rc != CKR_OK)
    {
        printf("Error Setting key attributes: %08x.\n", (unsigned int)rc);
        return rc;
    }
    else
    {
        printf("%d attributes set successfully.\n", (int) setAttrsTemplateSize);
    }
    return rc;
}

static CK_RV setKeyAliasAttribute(CK_OBJECT_HANDLE hKey, char *newalias)
{
    CK_RV rc = CKR_OK;
    CK_ULONG nalias_len = newalias ? (CK_ULONG)strlen(newalias) : 0;

    CK_ULONG	 setAttrsTemplateSize;
    CK_ATTRIBUTE setAttrsTemplate[] =
    {
        {CKA_THALES_OBJECT_ALIAS, newalias, nalias_len}
    };

    setAttrsTemplateSize = sizeof(setAttrsTemplate) / sizeof(CK_ATTRIBUTE);

    rc = FunctionListFuncPtr->C_SetAttributeValue(hSession,
            hKey,
            setAttrsTemplate,
            setAttrsTemplateSize);

    if (rc != CKR_OK)
    {
        printf ("Error Setting key alias: %08x.\n", (unsigned int)rc);
        return rc;
    }
    return rc;
}

static CK_RV setKeyDeactivateDate(CK_OBJECT_HANDLE hKey, int days)
{
    CK_RV        rc = CKR_OK;

    time_t       epoch_t;
    CK_ULONG     dl_time;

    CK_ULONG	 setAttrsTemplateSize;
    CK_ATTRIBUTE setAttrsTemplate[] =
    {
        { CKA_THALES_DATE_KEY_DEACTIVATION_EL, &dl_time, sizeof(CK_ULONG) }
    };

    time(&epoch_t);
    epoch_t += days * 24 * 60 * 60;
    dl_time = (CK_ULONG)epoch_t;

    setAttrsTemplateSize = sizeof(setAttrsTemplate) / sizeof(CK_ATTRIBUTE);

    rc = FunctionListFuncPtr->C_SetAttributeValue(hSession,
            hKey,
            setAttrsTemplate,
            setAttrsTemplateSize);

    if (rc != CKR_OK)
    {
        printf ("Error Setting key deactivation dates %u: %08x.\n", (unsigned int)epoch_t, (unsigned int)rc);
        return rc;
    }
    return rc;
}

static CK_RV setKeyLabel(CK_OBJECT_HANDLE hKey, char *newlabel)
{
    CK_RV rc = CKR_OK;
    CK_ULONG nlabel_len = newlabel ? (CK_ULONG)strlen(newlabel) : 0;

    CK_ULONG     setAttrsTemplateSize;
    CK_ATTRIBUTE setAttrsTemplate[] =
    {
        {CKA_LABEL, newlabel, nlabel_len}
    };

    setAttrsTemplateSize = sizeof(setAttrsTemplate) / sizeof(CK_ATTRIBUTE);

    rc = FunctionListFuncPtr->C_SetAttributeValue(hSession,
            hKey,
            setAttrsTemplate,
            setAttrsTemplateSize);

    if (rc != CKR_OK)
    {
        printf ("Error setting key label: %08x.\n", (unsigned int)rc);
        return rc;
    }
    return rc;
}

void usage()
{
    printf ("Usage: pkcs11_sample_attributes -p pin -s slotID [-k keyName] [-kp keyPairName] [-i {k|m|u}:identifier] [-g gen_key_action] [-a alias] [-c curve_oid] [-z key_size] [-ct cached_time] [-ls lifespan] [-1 customAttribute1] [-2 customAttribute2] [-3 customAttribute3] [-4 customAttribute4] [-5 customAttribute5] [-C] [-D] [-Z] [-m module]\n");
    printf ("-g gen_key_action: 0, 1, 2, or 3.  versionCreate: 0, versionRotate: 1, versionMigrate: 2, nonVersionCreate: 3\n");
    printf ("-i identifier: one of 'imported key id' as 'k', MUID as 'm', or UUID as 'u'.\n");
    printf ("-a alias: key alias, an alias can be used as part of template during key creation. Looking up an existing key by means of an alias is not supported in this sample program.\n");
    printf ("-ct cached_time cached time for key in minutes\n");
    printf ("-ls lifespan: how many days until next version will be automatically rotated(created); template with lifespan will be versioned key automatically.\n");
    printf ("-I Non-unique searchable ID (CKA_ID).");
    printf ("-z key_size key size for symmetric key in bytes.\n");
    printf ("-c curve oid: for ECC keys only.\n");
    printf ("-C ... clear alias\n");
    printf ("-D ... delete custom attributes (see below)\n");
    printf ("-Z ... zap label\n");
    printf ("To set two custom attributes (4 and 5), use -4 and -5\n");
    printf ("To create a new key along with three custom attributes, use -1, -2, and -3\n");
    printf ("To delete custom attributes 4 and 5, use -d\n");
    exit (2);
}

/*
 ************************************************************************
 * Function: main
 ************************************************************************
 */
#ifdef THALES_CLI_MODE
int attributesSample (int argc, char *argv[])
#else
int main(int argc, char *argv[])
#endif
{
    CK_RV rc;
    char *pin = NULL;
    char *libPath = NULL;
    char *foundPath = NULL;
    char *keyLabel = NULL;
    char *custom1 = DEFAULT_CUSTOM_VALUE; /* for a newly created key */
    char *custom2 = DEFAULT_CUSTOM_VALUE; /* for a newly created key */
    char *custom3 = DEFAULT_CUSTOM_VALUE; /* for a newly created key */
    char *custom4 = DEFAULT_CUSTOM_VALUE;
    char *custom5 = DEFAULT_CUSTOM_VALUE;
    char *curveOid = NULL;
    int  symmetric = 1;
    int  slotId = 0;
    int  bDeleteTwoAttributes = CK_FALSE;
    int  c;
    CK_OBJECT_HANDLE hKey = CK_INVALID_HANDLE;
    CK_OBJECT_CLASS  objClass = CKO_SECRET_KEY;

    CK_BBOOL    bCustomAttr = CK_FALSE;
    CK_BBOOL    bAliasClear = CK_FALSE;
    CK_BBOOL    bLabelZap   = CK_FALSE;
    char        *pKsid = NULL;
    int         ksid_type = keyIdLabel;
    char        *keyAlias = NULL;
    char        *idattr = NULL;
    CK_ULONG     modulusBufLen = 520;
    CK_ULONG     privExpoBufLen = 512;
    CK_ULONG     pubExpoBufLen = 32;

    extern char *optarg;
    extern int  optind;
    optind = 1; /* resets optind to 1 to call getopt() multiple times in sample_cli */
    int         loggedIn = 0;
    int         genAction = nonVersionCreate;
    int         key_size = 32;
    int         num_days = 0;
    int         versionNo = -1;
    CK_BYTE     pubExponentBuf[32];
    CK_BYTE     privExponentBuf[ASYMKEY_BUF_LEN];
    CK_BYTE     modulusBuf[ASYMKEY_BUF_LEN];
    unsigned long lifespan = 1;

    while ((c = newgetopt(argc, argv, "c:p:kp:m:s:i:a:I:z:d:g:v:1:2:3:4:5:ls:ct:CDZP")) != EOF)
    {
        switch (c)
        {
        case 'c':
            curveOid = optarg;
            break;
        case 'D':
            bDeleteTwoAttributes = CK_TRUE;
            break;
        case 'p':
            pin = optarg;
            break;
        case 'I':
			idattr = optarg;
            break;
        case 'k':
            keyLabel = optarg;
            break;
        case 'P':
            symmetric = 0;
            break;
        case kp:
            keyLabel = optarg;
            symmetric = 0;
            break;
        case 'd':
            num_days = atoi(optarg);
            break;
        case 'g':
            genAction = atoi(optarg);
            break;
        case 'm':
            libPath = optarg;
            break;
        case 's':
            slotId = atoi(optarg);
            break;
        case 'v':
            versionNo = atoi(optarg);
            break;
        case 'z':
            key_size = atoi(optarg);
            break;
        case 'a':
            keyAlias = optarg;
            break;
        case ct:
            ulCachedTime = (unsigned long)atoi(optarg);
            break;
        case 'C':
            keyAlias = NULL;
            bAliasClear = CK_TRUE;
            break;
        case 'Z':
            bLabelZap   = CK_TRUE;
            break;
        case ls:
            lifespan = (unsigned long)atoi(optarg);
            break;
        case 'i':
            ksid_type = parse_ksid_sel(optarg, &pKsid);
            if(ksid_type == keyIdAlias)
                keyAlias = pKsid;
            break;
        case '1':
            custom1 = optarg;
            bCustomAttr = CK_TRUE;
            break;
        case '2':
            custom2 = optarg;
            bCustomAttr = CK_TRUE;
            break;
        case '3':
            custom3 = optarg;
            bCustomAttr = CK_TRUE;
            break;
        case '4':
            custom4 = optarg;
            bCustomAttr = CK_TRUE;
            break;
        case '5':
            custom5 = optarg;
            bCustomAttr = CK_TRUE;
            break;
        case '?':
        default:
            usage();
            break;
        } /* end switch */
    }

    if (keyLabel)
    {
        pKsid = keyLabel;
        ksid_type = keyIdLabel;
    }
	else if (idattr)
	{
        pKsid = idattr;
        ksid_type = keyIdAttr;
	}

    if (NULL == pin || !pKsid) usage();

    printf("Begin Get/Set/Delete Attributes Sample: ...\n");
    do
    {
        /* load PKCS11 library and initalize. */
        printf("Initializing PKCS11 library \n");
        foundPath = getPKCS11LibPath(libPath);
        if (foundPath == NULL)
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

		if (ksid_type == keyIdAttr)
		{
			CK_ULONG numObjects = 1000;
			CK_OBJECT_HANDLE phKeys[1000];
			int i = 0;

			rc = findKeysByIdAttr(pKsid, &numObjects, phKeys);
			if (rc != CKR_OK) {
				break;
			}
			for (i = 0; i < numObjects; i++) {
				printf("\nAttributes for key number %d\n", i + 1);
				getAttributesValue(phKeys[i], 0, NULL, NULL);
			}
		}
		else if (symmetric == 0)
        {
            rc = findKey(pKsid, ksid_type, CKO_PRIVATE_KEY, &hPrivateKey);

            if (CK_INVALID_HANDLE == hPrivateKey)
            {
                printf("Keypair does not exist, Creating key pair...\n");
                rc = createKeyPair(keyLabel, custom1, custom2, custom3, curveOid);
                if (rc != CKR_OK)
                {
                    break;
                }
                printf("Successfully created key pair.\n");
            }
            else if (keyLabel)
            {
                printf("Asymmetric keypair %s already exists.\n", keyLabel);
            }

            rc = findKey(pKsid, ksid_type, CKO_PUBLIC_KEY, &hPublicKey);

            if (CK_INVALID_HANDLE == hPublicKey)
            {
                printf("Finding public key failed.\n");
            }
            else
            {
                printf("Finding public key succeeded, about to retrieve its attributes.\n");
                getAsymAttributesValue(hPublicKey, CKO_PUBLIC_KEY, modulusBuf, &modulusBufLen, pubExponentBuf, &pubExpoBufLen);

                if (bDeleteTwoAttributes) printf("About to delete custom attributes 4 and 5\n");
                else if (bCustomAttr)     printf("About to set custom attributes 4 and 5 to '%s' and '%s', respectively.\n", custom4, custom5);

                if (bDeleteTwoAttributes || bCustomAttr)
                    rc = setKeyAttributeValue(hPublicKey, symmetric, bDeleteTwoAttributes ? NULL : custom4, bDeleteTwoAttributes ? NULL : custom5);
            }

            if(CK_INVALID_HANDLE == hPrivateKey)
            {
                rc = findKey(pKsid, ksid_type, CKO_PRIVATE_KEY, &hPrivateKey);
            }

            if (CK_INVALID_HANDLE == hPrivateKey)
            {
                printf("Finding private key failed.\n");
            }
            else
            {
                printf("Finding private key succeeded, about to retrieve its attributes.\n");
                modulusBufLen = 520;
                getAsymAttributesValue(hPrivateKey, CKO_PRIVATE_KEY, modulusBuf, &modulusBufLen, privExponentBuf, &privExpoBufLen);

                if (bDeleteTwoAttributes) printf("About to delete custom attributes 4 and 5\n");
                else if (bCustomAttr)     printf("About to set custom attributes 4 and 5 to '%s' and '%s', respectively.\n", custom4, custom5);

                if (bDeleteTwoAttributes || bCustomAttr)
                    rc = setKeyAttributeValue(hPrivateKey, symmetric, bDeleteTwoAttributes ? NULL : custom4, bDeleteTwoAttributes ? NULL : custom5);
            }

        }
        else if ( pKsid )
        {
            if(versionNo == -1)
                rc = findKey(pKsid, ksid_type, CKO_SECRET_KEY, &hKey);
            else if(keyLabel)
            {
                printf("Find symmetric key %s by version %d ...\n", pKsid, versionNo);
                rc = findKeyByVersion( keyLabel, versionNo, &hKey );
            }

            if (hKey == CK_INVALID_HANDLE || genAction == versionRotate)
            {

                if (bCustomAttr == CK_TRUE)
                {
                    if (keyLabel)
                    {
                        printf("Symmetric key: %s does not exist, creating key with three custom attributes...\n", pKsid);
                        rc = createSymKeyCustom(keyLabel, keyAlias, genAction, custom1, custom2, custom3);
                        if (rc != CKR_OK)
                        {
                            fprintf(stderr, "Failed to create symmetric key (with custom attributes) named '%s' on Key Manager. \n", keyLabel);
                            break;
                        }
                    }
                }
                else
                {
                    if(genAction == nonVersionCreate)
                    {
                        printf("Symmetric key: %s does not exist, creating key...\n", pKsid);
                        rc = createKeyS(keyLabel, key_size);
                    }
                    else if(genAction == versionRotate)
                    {
                        printf("Symmetric key: %s does not exist, rotating key...\n", pKsid);
                        rc = createKey(pKsid, keyAlias, genAction, lifespan, key_size);
                    }
                    else
                    {
                        printf("Symmetric key: %s does not exist, creating key with lifespan %lu...\n", pKsid, lifespan);
                        rc = createKey(pKsid, keyAlias, genAction, lifespan, key_size);
                    }

                    if (rc != CKR_OK)
                    {
                        fprintf(stderr, "Failed to create symmetric key (with lifespan) named '%s' on Key Manager. \n", pKsid);
                        break;
                    }
                }

                if (keyLabel)
                {
                    rc = findKeyByLabel(keyLabel, &hKey, &objClass);

                    if (rc == CKR_OK && hKey != CK_INVALID_HANDLE)
                    {
                        fprintf(stdout, "Key named '%s' successfully created on Key Manager. \n", keyLabel);

                        rc = setKeyAttributeValue(hKey, symmetric, custom4, custom5);
                        if (rc != CKR_OK)
                        {
                            fprintf(stderr, "Failed to set two custom attributes\n");
                            break;
                        }
                    }
                    else
                    {
                        fprintf(stderr, "Failed to create key named '%s' on Key Manager. \n", keyLabel);
                        break;
                    }
                }
            }
            else
            {
                printf("Symmetric key with name: %s already exists.\n", pKsid);

                if (bLabelZap == CK_TRUE)
                    rc = setKeyLabel(hKey, NULL);
                else if (bAliasClear == CK_FALSE)
                {
                    if(keyAlias == NULL)
                    {
                        if (bDeleteTwoAttributes)
                            printf("About to delete custom attributes 4 and 5\n");
                        else if (bCustomAttr)
                            printf("About to set custom attributes 4 and 5 to '%s' and '%s', respectively.\n", custom4, custom5);

                        if (bDeleteTwoAttributes || bCustomAttr)
                        {
                            rc = setKeyAttributeValue(hKey, symmetric, bDeleteTwoAttributes ? NULL : custom4, bDeleteTwoAttributes ? NULL : custom5);
                        }
                        else if(num_days != 0)
                        {
                            rc = setKeyDeactivateDate( hKey, num_days );
                            if ( rc != CKR_OK)
                            {
                                printf("%s:%d:: Error: rc = %lu\n", __FUNCTION__, __LINE__, rc);
                                break;
                            }
                        }
                    }
                    else
                    {
                        rc = setKeyAliasAttribute(hKey, keyAlias);
                        if ( rc != CKR_OK)
                        {
                            printf("%s:%d:: Error: rc = %lu\n", __FUNCTION__, __LINE__, rc);
                            break;
                        }
                    }
                }
                else
                {
                    rc = setKeyAliasAttribute(hKey, NULL);
                    if ( rc != CKR_OK)
                    {
                        printf("%s:%d:: Error: rc = %lu\n", __FUNCTION__, __LINE__, rc);
                        break;
                    }
                }
            }
            getSymAttributesValue(hKey, 0, NULL, NULL);
        }
    }
    while (0);

    if (loggedIn)
    {
        if (logout() == CKR_OK)
        {
            printf("Successfully logged out.\n");
        }
    }

    cleanup();
    printf("End Get/Set/Delete key attributes sample.\n");
    fflush(stdout);
    return rc;
}
