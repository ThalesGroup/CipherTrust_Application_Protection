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
 * File: pkcs11_sample_create_key.c
 ***************************************************************************

 ***************************************************************************
 * This file demonstrates the following
 * 1. Initialization
 * 2. Create a connection and logging in.
 * 3. Create a key on the Key Manager
 * 4. Clean up.
 ***************************************************************************
 */

#include "pkcs11_sample_create_key.h"
#include "pkcs11_sample_helper.h"

void usageCreateKey()
{
    printf ("Usage: pkcs11_sample_create_key -p pin -s slotID -k keyName [-i {k|m|u}:identifier] [-g gen_key_action] [-a alias] [-m module] [-ls lifespan] [-ct cached_time] [-z key_size]\n");
    printf ("\n -g gen_key_action: 0, 1, 2, or 3.  versionCreate: 0, versionRotate: 1, versionMigrate: 2, nonVersionCreate: 3");
    printf ("\n -ls lifespan: how many days until next version will be automatically rotated(created); template with lifespan will be versioned key automatically.");
    printf ("\n -ct cached_time: cached time in minutes for the key");
    printf ("\n -z key_size key size for symmetric key in bytes.");
    printf ("\n -i identifier: one of 'imported key id' as 'k', MUID as 'm', or UUID as 'u'.\n");
    printf ("Note: The typical use case for the '-i' option is in conjuction with the '-g 1' or '-g 2' options (rotate key or migrate key, respectively)\n");
    exit (2);
}

static CK_RV migrateNonVersionedKey(CK_OBJECT_HANDLE hKey, int gen_action)
{
    CK_RV		rc = CKR_OK;

    /* CK_DATE     endDate;	 */
    CK_ATTRIBUTE_PTR setAttrsTemplate;
    CK_ULONG	 setAttrsTemplateSize;
    CK_LONG      keyVersionAction = gen_action;

    CK_ATTRIBUTE setAttrsTemplateSymm[] =
    {
        { CKA_THALES_KEY_VERSION_ACTION, &keyVersionAction, sizeof(keyVersionAction) }
    };

    setAttrsTemplate = setAttrsTemplateSymm;
    setAttrsTemplateSize = sizeof(setAttrsTemplateSymm) / sizeof(CK_ATTRIBUTE);

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

/*
 ************************************************************************
 * Function: main
 ************************************************************************
 */
#ifdef THALES_CLI_MODE
int createKeySample (int argc, char* argv[])
#else
int main(int argc, char* argv[])
#endif
{
    extern char *optarg;
    extern int optind;

    CK_RV  rc = CKR_OK;
    char *keyLabel = NULL;
    char *pin = NULL;
    char *libPath = NULL;
    char *foundPath = NULL;
    int loggedIn = 0;
    int slotId = 0;
    int genAction = nonVersionCreate;
    char * keyAlias = NULL;
    char * pKsid = NULL;
    int   ksid_type = keyIdLabel;
    int   key_size = 32;
    int   noDelete=0;
    unsigned long lifespan = 0;
    CK_OBJECT_HANDLE hKey = CK_INVALID_HANDLE;

    int c;
    optind = 1;    /* resets optind to 1 to call getopt() multiple times in sample_cli */

    while ((c = newgetopt(argc, argv, "a:k:p:m:s:g:i:as;ls:ct:z:ne;np;")) != EOF)
    {
        switch (c)
        {
        case 'p':
            pin = optarg;
            break;
        case 'k':
            keyLabel = optarg;
            pKsid = keyLabel;
            ksid_type = keyIdLabel;
            break;
        case 'z':
            key_size = atoi(optarg);
            break;
        case 'm':
            libPath = optarg;
            break;
        case 's':
            slotId = atoi(optarg);
            break;
        case 'g':
            genAction = atoi(optarg);
            break;
        case ct:
            ulCachedTime = (unsigned long)atoi(optarg);
            break;
        case 'a':
            keyAlias = optarg;
            pKsid = keyAlias;
            ksid_type = keyIdAlias;

            break;
        case np:
        case as:
            bAlwaysSensitive = CK_TRUE;
            break;
        case ne:
            bNeverExtractable = CK_TRUE;
            break;
        case 'i':
            ksid_type = parse_ksid_sel(optarg, &pKsid);
            if(ksid_type == keyIdAlias)
                keyAlias = pKsid;
            break;
        case ls:
            lifespan = (unsigned long)atoi(optarg);
            break;
        case 'n':
            noDelete = 1;
            break;
        case '?':
        default:
            usageCreateKey();
            break;
        }
    }

    if ((NULL == pin) || (pKsid == NULL) || (optind < argc))
    {
        usageCreateKey();
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

        if(pKsid)
        {
            rc = findKey(pKsid, ksid_type, CKO_SECRET_KEY, &hKey);

            if (rc != CKR_OK)
            {
                if (genAction == versionRotate || genAction == versionMigrate)
                {
                    fprintf(stderr, "Find Key Error: %lu. \n", rc);
                    break;
                }
            }
            else if (hKey == CK_INVALID_HANDLE)
            {
                if (genAction == versionRotate || genAction == versionMigrate)
                {
                    fprintf(stderr, "Find Key Error: bad handle\n");
                    rc = CKR_KEY_HANDLE_INVALID;
                    break;
                }
                printf("Creating key \n");

                if(genAction == versionCreate)
                    rc = createKey(keyLabel, keyAlias, genAction, lifespan, key_size);
                else
                    rc = createKeyS(keyLabel, key_size);

                if (rc == CKR_OK && hGenKey != CK_INVALID_HANDLE)
                {
                    fprintf(stderr, "Key with name: %s Created on Key Manager. \n", keyLabel);
                    getSymAttributesValue(hGenKey, 0, NULL, NULL);
                }
                else
                {
                    if (rc != CKR_OK)
                    {
                        fprintf(stderr, "Create Key error:%lu \n", rc);
                    }
                    else
                    {
                        fprintf(stderr, "Create Key error: Invalid Key Handle! \n");
                        rc = CKR_KEY_HANDLE_INVALID;
                    }
                    break;
                }
            }
            else
            {
                printf("Found key '%s', type: %d, hKey = %u.\n", pKsid, ksid_type, (unsigned int)hKey);

                if(genAction == versionRotate)
                {
                    char label[512];

                    getSymAttributesValue(hKey, 0, NULL, label);
                    printf("Rotating versioned key '%s'\n", label);
                    if (!keyLabel) keyLabel=label;
                    rc = createKey(keyLabel, keyAlias,  genAction, lifespan, key_size);
                    if (rc == CKR_OK && hGenKey != CK_INVALID_HANDLE)
                    {
                        fprintf(stdout, "Successfully rotated key with the name: '%s' on Key Manager! \n", keyLabel);
                        getSymAttributesValue(hGenKey, 0, NULL, NULL);
                    }
                    else
                    {
                        fprintf(stdout, "key rotation failure, with the name: '%s' error code: %lu  on Key Manager! \n", keyLabel, rc);
                        break;
                    }
                }
                else if(genAction == versionMigrate)
                {
                    fprintf(stdout, "Migration of key is not supported\n");
                    break;
                    printf("Migrating non-versioned key to versioned key \n");
                    rc = migrateNonVersionedKey(hKey, genAction);
                    if(rc == CKR_OK)
                    {
                        fprintf(stdout, "Key with the name: %s: Migrated on Key Manager! \n", keyLabel);

                        rc = findKey(pKsid, ksid_type, CKO_SECRET_KEY, &hKey);

                        if(rc == CKR_OK)
                            printf("Found key '%s', type: %d, hKey = %u.\n", pKsid, ksid_type, (unsigned int)hKey);
                        else
                        {
                            fprintf(stderr, "Error: finding key '%s', type: %d, rc = %u.\n", pKsid, ksid_type, (unsigned int)rc);
                        }
                    }
                    else
                    {
                        fprintf(stderr, "Error: Key with the name: %s: Not migrated: %lu. \n", keyLabel, rc);
                        break;
                    }
                }
                else
                {
                    if(!noDelete)
                    {

                        rc = deleteKey(hKey, CK_TRUE);

                        if(keyLabel)
                        {
                            if(rc == CKR_OK)
                            {
                                fprintf(stdout, "Key with the name: %s: Deleted on Key Manager!! \n", keyLabel);
                            }
                            else
                            {
                                fprintf(stderr, "Error: Key with the name: %s: Not Deleted from Key Manager! rc=%lu. \n", keyLabel, rc);
                                break;
                            }

                            printf("Creating key after existing key deletion:\n");

                            if(genAction == versionCreate)
                                rc = createKey(keyLabel, keyAlias, genAction, lifespan, key_size);
                            else
                                rc = createKeyS(keyLabel, key_size);

                            if (rc == CKR_OK && hGenKey != CK_INVALID_HANDLE)
                            {
                                fprintf(stderr, "Key with name: %s created on Key Manager! key handle: %u, after existing key deletion. \n", keyLabel, (unsigned int)hGenKey);
                                getSymAttributesValue(hGenKey, 0, NULL, NULL);
                            }
                            else
                            {
                                if (rc != CKR_OK)
                                {
                                    fprintf(stderr, "Create Key error:%lu \n", rc);
                                }
                                else
                                {
                                    fprintf(stderr, "Create Key error: Invalid Key Handle! \n");
                                    rc = CKR_KEY_HANDLE_INVALID;
                                }
                                break;
                            }
                        }
                    }
                    else
                    {
                        fprintf(stderr, "Error: Key with the name %s: already exists/no deletion or incorrect key action specified! \n", keyLabel);
                        break;
                    }
                }
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

    cleanup ();
    printf("End Create Key sample.\n");
    fflush(stdout);
    return rc;
}
