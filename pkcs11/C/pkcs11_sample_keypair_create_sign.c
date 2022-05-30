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
 * File: pkcs11_sample_keypair_create_sign.c
 ***************************************************************************
 ***************************************************************************
 * This file demonstrates the following
 * 1. Initialization
 * 2. Creating a connection and logging in.
 * 3. Creating a keypair on the Key Manager
 * 4. Signing a piece of data with the created keypair
 * 5. Delete the keypair.
 * 5. Clean up.
 */

#include "pkcs11_sample_keypair_create_sign.h"
#include "pkcs11_sample_helper.h"
/*
 ***************************************************************************
 * local variables
 **************************************************************************
 */

static CK_OBJECT_HANDLE	hKeyRSAPublic = 0x0;
static CK_OBJECT_HANDLE	hKeyRSAPrivate = 0x0;
static CK_BYTE			data[] = { "some data" };
static CK_OBJECT_HANDLE	hPublicKey = 0x0;
static CK_OBJECT_HANDLE	hPrivateKey = 0x0;

/*
 ************************************************************************
 * Function: createKeyPair
 * Creates an RSA keypair on the Key Manager.
 * The keyLabel is the name of the key displayed on the Key Manager.
 * modulusBits is the key strength.
 ************************************************************************
 * Parameters: none
 * Returns: CK_RV
 ************************************************************************
 */

static CK_RV createKeyPair (char * keyLabel, unsigned mod_bits)
{
    /* C_GenerateKeyPair */
    CK_MECHANISM		mechanism = { CKM_RSA_PKCS_KEY_PAIR_GEN, NULL_PTR, 0 };
    CK_ULONG			modulusBits = mod_bits;
    CK_BYTE				publicExponent[4] = { 0x01, 0x00, 0x01, 0x00 }; /* 65537 in bytes */
    CK_BBOOL			bTrue = CK_TRUE;
    CK_OBJECT_CLASS		pubkey_class = CKO_PUBLIC_KEY;
    CK_ULONG            keyLabel_len = (CK_ULONG)strlen((const char *)keyLabel);

    CK_ATTRIBUTE	publicKeyTemplate[] =
    {
        {CKA_LABEL, keyLabel, keyLabel_len }, /* Keyname */
        {CKA_CLASS, &pubkey_class, sizeof(pubkey_class)},
        {CKA_ENCRYPT, &bTrue, sizeof(bTrue)},
        {CKA_VERIFY, &bTrue, sizeof(bTrue)},
        {CKA_WRAP, &bTrue, sizeof(bTrue)},
        {CKA_TOKEN, &bTrue, sizeof(bTrue)},
        {CKA_PUBLIC_EXPONENT, publicExponent, sizeof(publicExponent)},
        {CKA_MODULUS_BITS, &modulusBits, sizeof(modulusBits)},
        {CKA_ALWAYS_SENSITIVE,	&bAlwaysSensitive,	sizeof(CK_BBOOL)	},
        {CKA_NEVER_EXTRACTABLE,	&bNeverExtractable,	sizeof(CK_BBOOL)	},
    };

    CK_ATTRIBUTE	privateKeyTemplate[] =
    {
        {CKA_LABEL, keyLabel, keyLabel_len }, /* Keyname*/
        {CKA_TOKEN, &bTrue, sizeof(bTrue)},
        {CKA_PRIVATE, &bTrue, sizeof(bTrue)},
        {CKA_SENSITIVE, &bTrue, sizeof(bTrue)},
        {CKA_DECRYPT, &bTrue, sizeof(bTrue)},
        {CKA_SIGN, &bTrue, sizeof(bTrue)},
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

/*
 ************************************************************************
 * Function: signData
 * Signs a piece of data with the RSA private key.
 * modulusBits is the key strength. In this case 2048 bits.
 * The caller is responsible for allocating a buffer of sufficient size
 * to hold the signed data.
 ************************************************************************
 * Parameters: none
 * Returns: CK_RV
 ************************************************************************
 */

static CK_RV signAndVerifyData (unsigned mod_bits)
{
    CK_RV rc = CKR_OK;

    CK_MECHANISM		signMech = { CKM_RSA_PKCS, NULL_PTR, 0 };
    CK_ULONG			dataLen = (CK_ULONG)strlen((const char *)data);
    CK_BYTE*			pSig = NULL_PTR;
//	CK_ULONG			modulusBits = mod_bits;
//	CK_ULONG			sigLen = modulusBits/8;
    CK_ULONG			sigLen = 0;

    do
    {
        rc = FunctionListFuncPtr->C_SignInit( hSession,
                                              &signMech,
                                              hKeyRSAPrivate
                                            );
        if (rc != CKR_OK)
        {
            fprintf(stderr, "FAIL: C_SignInit failed rc\n");
            return rc;
        }

        rc = FunctionListFuncPtr->C_Sign(hSession,
                                         (CK_BYTE *)&data, dataLen,
                                         pSig, &sigLen
                                        );
        if (rc != CKR_OK)
        {
            fprintf (stderr, "FAIL: 1st call to C_Sign() failed.\n");
            return rc;
        }

        pSig = (CK_BYTE *)calloc(1, sizeof(CK_BYTE)* (sigLen + 1));
        if (!pSig)
        {
            fprintf(stderr, "FAIL: calloc() failed \n");
            return rc;
        }

        rc = FunctionListFuncPtr->C_Sign(hSession,
                                         (CK_BYTE *)&data, dataLen,
                                         pSig, &sigLen
                                        );
        if (rc != CKR_OK)
        {
            fprintf(stderr, "FAIL: C_Sign failed.\n");
            return rc;
        }

        rc = FunctionListFuncPtr->C_VerifyInit(
                 hSession,
                 &signMech,
                 hKeyRSAPublic
             );
        if (rc != CKR_OK)
        {
            fprintf(stderr, "FAIL: C_VerifyInit failed.\n");
            return rc;
        }

        rc = FunctionListFuncPtr->C_Verify(
                 hSession,
                 (CK_BYTE *)&data, dataLen,
                 pSig, sigLen
             );
        if (rc != CKR_OK)
        {
            fprintf(stderr, "FAIL: C_Verify failed.\n");
            return rc;
        }
    }
    while (0);

    if (pSig)
    {
        free(pSig);
    }

    return rc;
}

void keypairSignUsage()
{
    printf ("Usage: pkcs11_keypair_create_sign -p pin -s slotID -kp keyName [-b modulus_bit_size] [-m module]\n");
    printf ("\n -kp to be created keypair name");
    printf ("\n -b modulus bits size in bits");
    exit (2);
}

/*
 ************************************************************************
 * Function: main
 ************************************************************************
 */

#ifdef THALES_CLI_MODE
int keypairCreateSignSample (int argc, char* argv[])
#else
int main(int argc, char* argv[])
#endif
{
    CK_RV rc;
    char *pin = NULL;
    char *libPath = NULL;
    char *foundPath = NULL;
    char *keyLabel = NULL;
    int  slotId = 0;
    int  c;
    int  noDelete=0;
    extern char *optarg;
    extern int optind;
    int loggedIn = 0;
    unsigned int modBits = MODULUS_BITS;

    optind = 1; /* resets optind to 1 to call getopt() multiple times in sample_cli */

    while ((c = newgetopt(argc, argv, "p:kp:m:s:b:np;ne;as;n")) != EOF)
        switch (c)
        {
        case 'p':
            pin = optarg;
            break;
        case kp:
            keyLabel = optarg;
            break;
        case 'm':
            libPath = optarg;
            break;
        case 's':
            slotId = atoi(optarg);
            break;
        case 'b':
            modBits = atoi(optarg);
            break;
        case np:
        case as:
            bAlwaysSensitive = CK_TRUE;
            break;
        case ne:
            bNeverExtractable = CK_TRUE;
            break;
        case 'n':
            noDelete = 1;
            break;
        case '?':
        default:
            keypairSignUsage();
            break;
        }
    if ((NULL == pin) || (NULL == keyLabel) || (optind < argc))
    {
        keypairSignUsage();
    }

    printf("Begin Create Keypair and Sign Message sample: ...\n");
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

        rc = findKey(keyLabel, keyIdLabel, CKO_PRIVATE_KEY, &hPrivateKey);
        if (CK_INVALID_HANDLE == hPrivateKey)
        {
            printf("Key does not exist, Creating key pair...\n");
            rc = createKeyPair(keyLabel, modBits);
            if (rc != CKR_OK)
            {
                break;
            }
            printf("Successfully created key pair.\n");
        }
        else
        {
            printf("Asymmetric key pair already exists.\n");
            hKeyRSAPrivate = hPrivateKey;
            rc = findKey(keyLabel, keyIdLabel, CKO_PUBLIC_KEY, &hKeyRSAPublic);
            if (rc != CKR_OK)
            {
                fprintf(stderr, "Error finding public key %s : %lu", keyLabel, rc);
                break;
            }
        }

        rc = signAndVerifyData(modBits);
        if (rc != CKR_OK)
        {
            rc = deleteKey(hPublicKey ? hPublicKey : hKeyRSAPublic, CK_TRUE);
            if (rc == CKR_OK)
                printf("Successfully deleted public/private key pair!\n");
            else
                printf("Deleting public/private key pair failed: %lu.\n", rc);

            break;
        }
        printf("PASS: C_Sign and C_Verify, Successfully signed data and verify the signature.\n");

        rc = findKey(keyLabel, keyIdLabel, CKO_PRIVATE_KEY, &hPrivateKey);
        if (CK_INVALID_HANDLE == hPrivateKey)
        {
            printf("Finding private key failed.\n");
        }
        else
        {
            printf("Successfully found private key; handle: %u.\n", (unsigned int)hPrivateKey );
        }

        rc = findKey(keyLabel, keyIdLabel, CKO_PUBLIC_KEY, &hPublicKey);
        if (CK_INVALID_HANDLE == hPublicKey)
        {
            printf("Finding public key failed.\n");
        }
        else
        {
            printf("Successfully found public key; handle: %u.\n", (unsigned int)hPublicKey);
        }

        if (!noDelete)
        {
            rc = deleteKey(hPublicKey, CK_FALSE);
            if (rc == CKR_OK)
                printf("Successfully deleted public/private key pair!\n");
            else
                printf("Deleting public/private key pair failed: %lu.\n", rc);

            rc = findKey(keyLabel, keyIdLabel, CKO_PUBLIC_KEY, &hPublicKey);
            if (CK_INVALID_HANDLE == hPublicKey)
            {
                printf("Finding public key non-existent! \n");
            }
            else
            {
                printf("Finding public key again; delete unsuccessful! \n");
            }

            rc = findKey(keyLabel, keyIdLabel, CKO_PRIVATE_KEY, &hPrivateKey);
            if (CK_INVALID_HANDLE == hPrivateKey)
            {
                printf("Finding private key non-existent! \n");
            }
            else
            {
                printf("Finding private key again; delete unsuccessful! \n");
            }
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
    printf("End Create Keypair and Sign Message sample.\n");
    fflush(stdout);
    return rc;
}
