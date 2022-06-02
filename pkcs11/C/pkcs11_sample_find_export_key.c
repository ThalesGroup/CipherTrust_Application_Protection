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
 * File: pkcs11_sample_find_export_key.c
 ***************************************************************************
 ***************************************************************************
 * This file is designed to be run after pkcs11_sample_create_key and
 * demonstrates the following:
 * 1. Initialization
 * 2. Creating a connection and logging in.
 * 3. Querying for a key using the keyname.
 * 4. Export the key using the wrappingKey that was found.
 * 4. Clean up.
 */

#include "pkcs11_sample_find_export_key.h"
#include "pkcs11_sample_helper.h"

/*
 ***************************************************************************
 * Local Variables
 **************************************************************************
 */

#define AES_BLOCK_SIZE 16
#define MAX_FIND_RETURN 1

static const char outfilename[] = "keytext.dat";

static CK_RV wrapAndExportKey (CK_OBJECT_HANDLE hKey, CK_OBJECT_HANDLE hWrappingKey, CK_OBJECT_CLASS wrappingObjClass, int format_type);

static CK_BBOOL bAsymKeyPair = CK_FALSE;
static CK_OBJECT_CLASS   wrappingObjClass = CKO_SECRET_KEY;

/*
 ************************************************************************
 * Function: findExportKey
 * This function first search for the source key and wrapping key from Key Manager
 ************************************************************************
 * Parameters: none
 * Returns: CK_RV
 ************************************************************************
 */

static CK_RV findExportKeys (char* keySearchId, int keyidType, CK_OBJECT_CLASS wrappedObjClass, int format_type,
                             char* wrappingKeySid, int wrappingKsidType, int versionNo )
{
    CK_RV rc = CKR_OK;
    /* CK_OBJECT_CLASS		keyClass = CKO_SECRET_KEY; */
    CK_OBJECT_HANDLE	hFoundKey = 0x0;
    CK_OBJECT_HANDLE    hWrappingKey = CK_INVALID_HANDLE;


    if(wrappingKeySid != NULL)
    {
        rc = findKey(wrappingKeySid, wrappingKsidType, wrappingObjClass, &hWrappingKey);

        if (CK_INVALID_HANDLE == hWrappingKey)
        {
            fprintf (stderr, "Cannot find the wrapping key: %s;\nSkipping using wrapping key...\n", wrappingKeySid);
        }
        else
        {
            printf ("Found wrapping key with id: %s successfully.\n", wrappingKeySid);
        }
    }

    if(keySearchId != NULL)
    {
        if(versionNo == -1)
            rc = findKey(keySearchId, keyidType, wrappedObjClass, &hFoundKey);
        else if(keyidType == keyIdLabel)
        {
            rc = findKeyByVersion(keySearchId, versionNo, &hFoundKey);
        }

        if (CK_INVALID_HANDLE == hFoundKey)
        {
            fprintf (stderr , "FAIL : Cannot find the source key: %s. \n", keySearchId);
        }
        else
        {
            printf ("Found source key : %s successfully.\n", keySearchId);

            rc = wrapAndExportKey(hFoundKey, hWrappingKey, wrappingObjClass, format_type);
            if (rc == CKR_OK)
            {
                printf ("Successfully found and exported key.\n");
            }
            else
            {
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
static CK_RV wrapAndExportKey (CK_OBJECT_HANDLE hKey, CK_OBJECT_HANDLE hWrappingKey, CK_OBJECT_CLASS wrappingObjClass, int format_type)
{
    CK_RV rc;
    /* C_WrapKey not longer support CKM_AES_ECB any more, */
    CK_MECHANISM	  mechExportKey = { CKM_AES_CBC_PAD, def_iv, 16 };
    CK_BYTE_PTR       pWrappedKey = NULL;
    CK_ULONG          ulWrappedKeyLen = 0;
    FILE *            fp = NULL;

    do
    {
        if(wrappingObjClass != CKO_SECRET_KEY && hWrappingKey != CK_INVALID_HANDLE)
        {
            mechExportKey.mechanism = (CK_MECHANISM_TYPE)(CKA_THALES_DEFINED | CKM_RSA_PKCS);
        }
        else if(format_type != 0)
        {
            mechExportKey.mechanism |= (CK_MECHANISM_TYPE)( format_type );
        }

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
            printf("C_WrapKey call succeed, ulWrappedKeyLen is : %ld \n", (long)ulWrappedKeyLen);

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
            fprintf(stderr, "FAIL: 2nd call to C_WrapKey() failed. error = %x.\n", (unsigned int)rc);
            break;
        }

        /* export wrapped key by saving it to a file */
        fp = fopen(outfilename, "a+");

        if (fp)
        {
            size_t n;
            fprintf(fp, "Key ID: %lu\n", hKey);
            fprintf(fp, "Key Value:\n");

            n = fwrite(pWrappedKey, sizeof(CK_BYTE), ulWrappedKeyLen, fp);
            {
                if (n != sizeof(CK_BYTE) * ulWrappedKeyLen)
                {
                    fprintf(stderr, "FAIL: fwrite pWrappedKey failed. \n");
                }
            }

            fflush(fp);
            fclose(fp);

            printf("Found and Export keys successfully for key: %lu.\n", hKey);
        }

    }
    while (0);

    if(pWrappedKey)
        free(pWrappedKey);

    return rc;
}


void exportKeyUsage()
{
    printf ("Usage: pkcs11_sample_find_export_key -p pin -s slotID -[k|v|c|o] keyName/opaqueObjectName [-i {k|m|u}:identifier] -w wrappingKeyName [-f format] [-e] [-m module]\n");
    printf ("\n -i identifier: one of 'imported key id' as 'k', MUID as 'm', or UUID as 'u'.");
    printf ("\n -k|v|c keyname to be wrapped/exported from the Key Manager; 'k': symmetric key name, 'v': private key, 'c': public key.");
    printf ("\n -o opaque object name to be wrapped/exported from the Key Manager");
    printf ("\n -w wrapping key label to be searched on the Key Manager.");
    printf ("\n -f format type: one of 'pem' or 'der' for asymmetric key output type, omit for symmetric keys.");
    printf ("\n -e invalidate cache and use Key Manager for every export request");
    exit (2);
}

/*
 ************************************************************************
 * Function: main
 ************************************************************************
 */

#ifdef THALES_CLI_MODE
int findExportKeySample (int argc, char* argv[])
#else
int main(int argc, char* argv[])
#endif
{
    FILE*    fp;
    CK_RV    rc;

    char *keyLabel = NULL;
    char *pin = NULL;
    char *libPath = NULL;
    char *foundPath = NULL;
    char *wrappingKeySid = NULL;
    char *pKsid = NULL;

    int   ksid_type = keyIdLabel;
    int   wrapping_ksid_type = keyIdLabel;
    int   format_type = CKA_RAW_FORMAT;

    int versionNo = -1;
    int slotId = 0;
    int c;
    extern char *optarg;
    extern int   optind;
    CK_OBJECT_CLASS objClass = CKO_SECRET_KEY;
    int loggedIn = 0;

    optind = 1; /* resets optind to 1 to call getopt() multiple times in sample_cli */

    while ((c = newgetopt(argc, argv, "p:kp:c:v:w:m:s:i:f:n:o:e")) != EOF)
        switch (c)
        {
        case 'p':
            pin = optarg;
            break;
        case 'k':
            keyLabel = optarg;
            break;
        case kp:
            keyLabel = optarg;
            bAsymKeyPair = CK_TRUE;
            break;
        case 'c':
            keyLabel = optarg;
            bAsymKeyPair = CK_TRUE;
            format_type = CKA_THALES_PEM_FORMAT;
            objClass = CKO_PUBLIC_KEY;
            break;
        case 'v':
            keyLabel = optarg;
            bAsymKeyPair = CK_TRUE;
            format_type = CKA_THALES_PEM_FORMAT;
            objClass = CKO_PRIVATE_KEY;
            break;
        case 'w':
            wrappingKeySid = parse_key_class(optarg, &wrappingObjClass);
            break;
        case 'o':
            objClass = CKO_THALES_OPAQUE_OBJECT;
            ksid_type = parse_ksid_sel(optarg, &pKsid);
            break;
        case 'e':
            format_type |= CKA_THALES_CACHE_INVALIDATE;
            break;
        case 'm':
            libPath = optarg;
            break;
        case 's':
            slotId = atoi(optarg);
            break;
        case 'n':
            versionNo = atoi(optarg);
            break;
        case 'f':
            format_type = parse_format_type(optarg);
            break;
        case 'i':
            ksid_type = parse_ksid_sel(optarg, &pKsid);
            break;

        case '?':
        default:
            exportKeyUsage();
            break;
        }

    if ((NULL == pin) || (optind < argc))
    {
        exportKeyUsage();
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

        if(keyLabel)
        {
            pKsid = keyLabel;
            ksid_type = keyIdLabel;
        }

        fp = fopen(outfilename, "w+");

        if (fp)
        {
            fprintf(fp, "Exported keys:\n");
            fclose(fp);
        }

        rc = findExportKeys(pKsid, ksid_type, objClass, format_type, wrappingKeySid, wrapping_ksid_type, versionNo);
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
    printf("End Find and Export Key sample.\n");
    fflush(stdout);;
    return rc;
}
