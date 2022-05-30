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


/* static CK_BYTE			data[] = { "some data" }; */

extern unsigned long ulCachedTime;

/*static char def_passwd[] = { "Pas$w0rd#" }; */
/*static char def_passwd2[] = { "Passw0rd!" }; */



/* static CK_RV setKeyAliasAttribute(CK_OBJECT_HANDLE hKey, char *newalias)
{
    CK_RV rc = CKR_OK;
	CK_ULONG nalias_len = newalias ? (CK_ULONG)strlen(newalias) : 0;

    CK_ULONG	 setAttrsTemplateSize;
    CK_ATTRIBUTE setAttrsTemplate[] = {
		{CKA_THALES_OBJECT_ALIAS, newalias, nalias_len}
    };

	setAttrsTemplateSize = sizeof(setAttrsTemplate) / sizeof(CK_ATTRIBUTE);

    rc = FunctionListFuncPtr->C_SetAttributeValue(hSession,
                                                  hKey,
                                                  setAttrsTemplate,
                                                  setAttrsTemplateSize);

    if (rc != CKR_OK) {
        printf ("Error Setting key alias: %08x.\n", (unsigned int)rc);
        return rc;
    }
    return rc;
	} */

static CK_RV setKeyState(CK_OBJECT_HANDLE hKey, KeyState  state)
{
    CK_RV       rc = CKR_OK;
    CK_ULONG	setAttrsTemplateSize;

    CK_ATTRIBUTE setAttrsTemplate[] =
    {
        {CKA_THALES_KEY_STATE, &state, sizeof(KeyState) }
    };

    setAttrsTemplateSize = sizeof(setAttrsTemplate) / sizeof(CK_ATTRIBUTE);

    rc = FunctionListFuncPtr->C_SetAttributeValue(hSession,
            hKey,
            setAttrsTemplate,
            setAttrsTemplateSize);

    if (rc != CKR_OK)
    {
        printf ("Error Setting key state: %08x.\n", (unsigned int)rc);
        return rc;
    }
    else
    {
        printf ("Successfully setting key state to %d: for key handle: %u\n", (int)state, (unsigned int)hKey);
    }
    return rc;
}

/*
static CK_RV setKeyLabel(CK_OBJECT_HANDLE hKey, char *newlabel)
{
    CK_RV rc = CKR_OK;
    CK_ULONG nlabel_len = newlabel ? (CK_ULONG)strlen(newlabel) : 0;

    CK_ULONG     setAttrsTemplateSize;
    CK_ATTRIBUTE setAttrsTemplate[] = {
        {CKA_LABEL, newlabel, nlabel_len}
    };

    setAttrsTemplateSize = sizeof(setAttrsTemplate) / sizeof(CK_ATTRIBUTE);

    rc = FunctionListFuncPtr->C_SetAttributeValue(hSession,
                                                  hKey,
                                                  setAttrsTemplate,
                                                  setAttrsTemplateSize);

    if (rc != CKR_OK) {
        printf ("Error setting key label: %08x.\n", (unsigned int)rc);
        return rc;
    }
    return rc;
	} */

void usage()
{
    printf ("Usage: pkcs11_sample_version_find -p pin -s slotID [-k keyName] [-P keyPairName] [-i {k|m|u}:identifier] [-g gen_key_action] [-a alias] [-z key_size] [-c] [-ct cached_time] [-ls lifespan] [-1 customAttribute1] [-2 customAttribute2] [-3 customAttribute3] [-4 customAttribute4] [-5 customAttribute5] [-C] [-D] [-Z] [-m module]\n");
    printf ("-C ... clear alias\n");
    printf ("-g gen_key_action: 0, 1, 2, or 3.  versionCreate: 0, versionRotate: 1, versionMigrate: 2, nonVersionCreate: 3\n");
    printf ("-i identifier: one of 'imported key id' as 'k', MUID as 'm', or UUID as 'u'.\n");
    printf ("-a alias: key alias, an alias can be used as part of template during key creation. Looking up an existing key by means of an alias is not supported in this sample program.\n");
    printf ("-ct cached_time cached time for key in minutes\n");
    printf ("-ls lifespan: how many days until next version will be automatically rotated(created); template with lifespan will be versioned key automatically.\n");
    printf ("-z key_size key size for symmetric key in bytes.\n");
    printf ("-c ... create 50 versions of key\n");
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
    char   *pin = NULL;
    char   *libPath = NULL;
    char   *foundPath = NULL;
    char   *keyLabel = NULL;

    int    slotId = 0;
    int    c;
    CK_OBJECT_HANDLE hKey;
    CK_OBJECT_CLASS  objClass = CKO_SECRET_KEY;

    char   *pKsid = NULL;
    int    ksid_type = keyIdLabel;
    char   *keyAlias = NULL;
    int         clientCompromise = 0;
    extern char *optarg;
    /*extern int  optind;*/
    int         loggedIn = 0;
    int         genAction = 0;
    int         key_size = 32;
    unsigned long lifespan = 0;
    int         versionCnt = 0;

    while ((c = newgetopt(argc, argv, "c;cp:kp:P:m:s:i:a:d:z:g:ls:ct")) != EOF)
    {
        switch (c)
        {

        case 'p':
            pin = optarg;
            break;
        case 'k':
            keyLabel = optarg;
            break;
        case 'c':
            clientCompromise = 1;
            break;
        case kp:
        case 'P': /* key pair */
            keyLabel = optarg;
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
        case 'z':
            key_size = atoi(optarg);
            break;
        case 'a':
            keyAlias = optarg;
            break;
        case ct:
            ulCachedTime = (unsigned long)atoi(optarg);
            break;
        case ls:
            lifespan = (unsigned long)atoi(optarg);
            break;
        case 'i':
            ksid_type = parse_ksid_sel(optarg, &pKsid);
            if(ksid_type == keyIdAlias)
                keyAlias = pKsid;
            break;
        case '?':
        default:
            usage();
            break;
        } /* end switch */
    }

    if (NULL == pin) usage();

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

        if (keyLabel)
        {
            pKsid = keyLabel;
            ksid_type = keyIdLabel;
        }

        if ( pKsid )
        {
            rc = findKey(pKsid, ksid_type, CKO_SECRET_KEY, &hKey);

            if (hKey == CK_INVALID_HANDLE)
            {
                printf("Symmetric key: %s does not exist, creating key...\n", pKsid);


                printf("Symmetric key: %s does not exist, creating key with lifespan %lu...\n", pKsid, lifespan);
                rc = createKey(pKsid, keyAlias, genAction, lifespan, key_size);
                if (rc != CKR_OK)
                {
                    fprintf(stderr, "Failed to create symmetric key (with lifespan) named '%s' on Key Manager. \n", pKsid);
                    break;
                }

                if (keyLabel)
                {
                    rc = findKeyByLabel(keyLabel, &hKey, &objClass);
                    if (rc == CKR_OK && hKey != CK_INVALID_HANDLE)
                    {
                        fprintf(stdout, "Key named '%s' successfully found on Key Manager. \n", keyLabel);
                    }
                    else
                    {
                        fprintf(stderr, "Failed to find key named '%s' on Key Manager. \n", keyLabel);
                        break;
                    }
                }
            }
            else
            {
                printf("Symmetric key with name: %s already exists.\n", pKsid);
                getSymAttributesValue(hKey, 0, NULL, NULL);

                while(versionCnt++ < 50)
                {
                    /*  */

                    if(clientCompromise != 0)
                    {
                        rc = setKeyState( hKey, KeyStateCompromised );

                        if (rc != CKR_OK)
                        {
                            fprintf(stderr, "Failed to set key state to compromised with label '%s' on Key Manager. \n", pKsid);
                            break;
                        }

                        rc = createKey(pKsid, keyAlias, 1 /* rotate */, 0L, key_size);
                        if (rc != CKR_OK)
                        {
                            fprintf(stderr, "Failed to rotate key with label '%s' on Key Manager. \n", pKsid);
                            break;
                        }
                    }

                    if (keyLabel)
                    {
                        rc = findKeyByLabel(keyLabel, &hKey, &objClass);
                        if (rc == CKR_OK && hKey != CK_INVALID_HANDLE)
                        {
                            fprintf(stdout, "Key named '%s' successfully found on Key Manager. Key handle: %u \n", keyLabel, (unsigned int)hKey);

                            getSymAttributesValue(hKey, 0, NULL, NULL);
                        }
                        else
                        {
                            fprintf(stderr, "Failed to find key named '%s' on Key Manager. \n", keyLabel);
                            break;
                        }
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

    cleanup();
    printf("End Get/Set/Delete key attributes sample.\n");
    fflush(stdout);
    return rc;
}
