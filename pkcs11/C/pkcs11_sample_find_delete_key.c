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
 * File: pkcs11_sample_find_delete_key.c
 ***************************************************************************
 * Usage: pkcs11_sample_find_delete_key [-k name] <module>
 ***************************************************************************
 * This file is designed to be run after pkcs11_create_key_sample and
 * demonstrates the following:
 * 1. Initialization
 * 2. Creating a connection and logging in.
 * 3. Querying for a key using the keyname.
 * 4. Deleting the key that was found.
 * 4. Clean up.
 */

#include "pkcs11_sample_find_delete_key.h"
#include "pkcs11_sample_helper.h"

void usageDeleteKey()
{
    printf ("Usage: pkcs11_sample_find_delete_key -p pin -s slotID {-k keyName| -a alias} [-i {k|m|u}:identifier] [-m module]\n");
    printf ("identifier: one of 'imported key id' as 'k', MUID as 'm', or UUID as 'u'.\n");
    exit (2);
}

/*
 ************************************************************************
 * Function: main
 ************************************************************************
 */

#ifdef THALES_CLI_MODE
int deleteKeySample (int argc, char* argv[])
#else
int main(int argc, char* argv[])
#endif
{
    CK_RV rc;
    int slotId = 0;
    char *keyLabel = NULL;
    char *alias = NULL;
    char *pin = NULL;
    char *libPath = NULL;
    char *foundPath = NULL;
    char * pKsid = NULL;
    int   ksid_type = keyIdLabel;
    int   loggedIn = 0;

    CK_OBJECT_HANDLE	hKey = 0x0;
    CK_OBJECT_CLASS    objClass = CKO_SECRET_KEY;

    int c;
    extern char *optarg;
    extern int optind;
    optind = 1; /* resets optind to 1 to call getopt() multiple times in sample_cli */

    while ((c = newgetopt(argc, argv, "p:k:m:s:i:a:c:v:")) != EOF)
        switch (c)
        {
        case 'p':
            pin = optarg;
            break;
        case 'k':
            keyLabel = optarg;
            break;
        case 'c':
            keyLabel = optarg;
            objClass = CKO_PUBLIC_KEY;
            break;
        case 'v':
            keyLabel = optarg;
            objClass = CKO_PRIVATE_KEY;
            break;
        case 'a':
            alias = optarg;
            break;
        case 'm':
            libPath = optarg;
            break;
        case 's':
            slotId = atoi(optarg);
            break;
        case 'i':
            ksid_type = parse_ksid_sel(optarg, &pKsid);
            break;
        case '?':
        default:
            usageDeleteKey();
            break;
        }

    if ((NULL == pin) || (optind < argc))
    {
        usageDeleteKey();
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

        if(keyLabel)
        {
            pKsid = keyLabel;
            ksid_type = keyIdLabel;
        }
        else if(alias)
        {
            pKsid = alias;
            ksid_type = keyIdAlias;
        }

        if(keyLabel)
            rc = findKeyByLabel(pKsid, &hKey, &objClass);
        else
            rc = findKey(pKsid, ksid_type, CKO_SECRET_KEY, &hKey);

        if (CK_INVALID_HANDLE == hKey)
        {
            fprintf(stderr, "FAIL: Unable to find the Key. \n");
            break;
        }
        /* key is found, now delete the key */
        rc = deleteKey(hKey, CK_TRUE);
        if (rc != CKR_OK)
        {
            fprintf(stderr, "FAIL: deleteKey with unexpected result\n");
        }
        else
        {
            printf("PASS: Successfully found and deleted key. \n");
        }

        if(keyLabel)
            rc = findKeyByLabel(pKsid, &hKey, &objClass);
        else
            rc = findKey(pKsid, ksid_type, CKO_SECRET_KEY, &hKey);
        if (CK_INVALID_HANDLE == hKey)
        {
            fprintf(stderr, "PASS: Unable to find the Key After deletion. \n");
            break;
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
    printf("End Find and Delete Key sample.\n");
    fflush(stdout);
    return rc;
}
