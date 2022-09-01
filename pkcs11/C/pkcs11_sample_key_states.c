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
 * 3. Tries to find a symmetric key on the Key Manager
 * 4. If the key didn't exist, create it with key dates attached
 * 5. If the key already existed, modify the key state and/or key dates.
 * 6. Clean up.
 */

#include "pkcs11_sample_helper.h"
/*
 ***************************************************************************
 * local variables
 **************************************************************************
 */
static CK_UTF8CHAR app[] = { "CADP_PKCS11_SAMPLE_KEY_STATE" };



/*
 *  ************************************************************************
 *  Function: createSymKey
 *  Creates and AES 256 key on the Key Manager.
 *  The keyLabel is the name of the key displayed on the Key Manager.
 *  ************************************************************************
 */

CK_RV createSymKeywDates (char* keyLabel, CK_ATTRIBUTE_TYPE attrTypes[], char* pcKeyDates[], CK_ULONG keyDateCount, int gen_action)
{
    CK_RV            rc = CKR_OK;
    CK_MECHANISM     mechGenKey = { CKM_AES_KEY_GEN, NULL_PTR, 0};
    CK_OBJECT_CLASS  keyClass = CKO_SECRET_KEY;
    CK_KEY_TYPE      keyType = CKK_AES;
    CK_ULONG         keySize = 32; /* 256 bits */
    CK_BBOOL         bFalse = CK_FALSE;
    CK_BBOOL         bTrue = CK_TRUE;

    CK_UTF8CHAR      *label = (CK_UTF8CHAR *) keyLabel;
    CK_ULONG         len = (CK_ULONG) strlen(keyLabel);

    CK_LONG          keyVersionAction = gen_action;
    unsigned int     i, keyDateIndex;
    CK_DATE          keyDates[KEY_TRANS_DATES_MAX];
    CK_LONG          lepoch[KEY_TRANS_DATES_MAX] = { 0 };

    CK_ATTRIBUTE_PTR pKeyTemplate = NULL;

    /* AES key template.
     * CKA_LABEL is the name of the key and will be displayed on the Key Manager.
     * CKA_VALUE_LEN is the size of the AES key.
     */

    CK_ATTRIBUTE aesKeyTemplate[] =
    {
        {CKA_ID,            label,     len   },
        {CKA_LABEL,         label,     len   },
        {CKA_APPLICATION,   &app,      sizeof(app)       },
        {CKA_CLASS,         &keyClass,  sizeof(keyClass) },
        {CKA_KEY_TYPE,      &keyType,   sizeof(keyType)  },
        {CKA_VALUE_LEN,     &keySize,   sizeof(keySize)  },
        {CKA_TOKEN,         &bTrue,     sizeof(bTrue)    },
        {CKA_ENCRYPT,       &bTrue,     sizeof(bTrue)    },
        {CKA_DECRYPT,       &bTrue,     sizeof(bTrue)    },
        {CKA_SIGN,          &bFalse,    sizeof(bFalse)   },
        {CKA_VERIFY,        &bFalse,    sizeof(bFalse)   },
        {CKA_WRAP,          &bTrue,     sizeof(bTrue)    },
        {CKA_UNWRAP,        &bFalse,    sizeof(bFalse)   },
        {CKA_EXTRACTABLE,   &bFalse,    sizeof(bFalse)   },
        {CKA_ALWAYS_SENSITIVE,    &bFalse,    sizeof(bFalse)  },
        {CKA_NEVER_EXTRACTABLE,   &bTrue,     sizeof(bTrue)   },
        {CKA_SENSITIVE,           &bTrue,     sizeof(bTrue)   },
        {CKA_THALES_KEY_VERSION_ACTION, &keyVersionAction, sizeof(keyVersionAction) }
    };
    CK_ULONG  aesKeyTemplateSize = sizeof(aesKeyTemplate)/sizeof(CK_ATTRIBUTE);

    if(keyDateCount > 0)
    {
        pKeyTemplate = (CK_ATTRIBUTE_PTR)calloc( (aesKeyTemplateSize + keyDateCount), sizeof(CK_ATTRIBUTE) );
        if(!pKeyTemplate)
        {
            printf ("Error allocating memory for pKeyTemplate!\n");
            return CKR_HOST_MEMORY;
        }

        for(i=0; i<aesKeyTemplateSize; i++)
        {
            pKeyTemplate[i].type = aesKeyTemplate[i].type;
            pKeyTemplate[i].pValue = aesKeyTemplate[i].pValue;
            pKeyTemplate[i].ulValueLen = aesKeyTemplate[i].ulValueLen;
        }

        aesKeyTemplateSize += keyDateCount;

        for(keyDateIndex=0; i<aesKeyTemplateSize; i++, keyDateIndex++)
        {
            pKeyTemplate[i].type = attrTypes[keyDateIndex];

            if( (attrTypes[keyDateIndex] & CKA_THALES_DEFINED) == CKA_THALES_DEFINED )
            {

                parse_ck_date(pcKeyDates[keyDateIndex], &keyDates[keyDateIndex]);

                pKeyTemplate[i].pValue = &keyDates[keyDateIndex];
                pKeyTemplate[i].ulValueLen = sizeof(CK_DATE);
            }
            else if( (attrTypes[keyDateIndex] & CKA_VENDOR_DEFINED) == CKA_VENDOR_DEFINED )
            {
                lepoch[keyDateIndex] = atol(pcKeyDates[keyDateIndex]);
                pKeyTemplate[i].pValue = &lepoch[keyDateIndex];
                pKeyTemplate[i].ulValueLen = sizeof(CK_LONG);
            }
        }
    }

    rc = FunctionListFuncPtr->C_GenerateKey(hSession,
                                            &mechGenKey,
                                            pKeyTemplate != NULL ? pKeyTemplate : aesKeyTemplate,
                                            aesKeyTemplateSize,
                                            &hGenKey
                                           );
    if (rc != CKR_OK || hGenKey == 0)
    {
        printf ("Error generating Key: 0x%8x\n", (unsigned int)rc);
    }
    else
    {
        printf ("Successfully generating Key with name: %s\n", keyLabel);
    }

    if( pKeyTemplate )
    {
        free(pKeyTemplate);
    }
    return rc;
}

static CK_RV setKeyDateAttributes(CK_OBJECT_HANDLE hKey, CK_ATTRIBUTE_TYPE attrTypes[], char* pcKeyDates[], CK_ULONG keyDateCount)
{
    CK_RV      rc = CKR_OK;
    CK_ULONG   setAttrsTemplateSize = keyDateCount;
    CK_DATE    keyDates[KEY_TRANS_DATES_MAX];
    unsigned int i;
    CK_LONG    lepoch[KEY_TRANS_DATES_MAX] = { 0 };

    CK_ATTRIBUTE_PTR setAttrsTemplate = (CK_ATTRIBUTE_PTR)calloc( keyDateCount, sizeof(CK_ATTRIBUTE) );
    if(!setAttrsTemplate)
    {
        printf ("Error allocating memory for pKeyTemplate!\n");
        return CKR_HOST_MEMORY;
    }

    for(i=0; i<setAttrsTemplateSize; i++)
    {
        setAttrsTemplate[i].type = attrTypes[i];
        if( (attrTypes[i] & CKA_THALES_DEFINED) == CKA_THALES_DEFINED)
        {
            parse_ck_date(pcKeyDates[i], &keyDates[i]);
            setAttrsTemplate[i].pValue = &keyDates[i];
            setAttrsTemplate[i].ulValueLen = sizeof(CK_DATE);
        }
        else if( (attrTypes[i] & CKA_VENDOR_DEFINED) == CKA_VENDOR_DEFINED )
        {
            lepoch[i] = atol(pcKeyDates[i]);
            setAttrsTemplate[i].pValue = &lepoch[i];
            setAttrsTemplate[i].ulValueLen = sizeof(CK_LONG);
        }
    }

    rc = FunctionListFuncPtr->C_SetAttributeValue(hSession,
            hKey,
            setAttrsTemplate,
            setAttrsTemplateSize);


    free(setAttrsTemplate);

    if (rc != CKR_OK)
    {
        printf ("Error Setting key attributes: %08x.\n", (unsigned int)rc);
        return rc;
    }
    return rc;
}

static CK_RV setKeyStateAttribute(CK_OBJECT_HANDLE hKey, KeyState state)
{
    CK_RV        rc = CKR_OK;

    CK_ATTRIBUTE setAttrsTemplate[] =
    {
        {CKA_THALES_KEY_STATE, &state, sizeof(KeyState) }
    };

    CK_ULONG	 setAttrsTemplateSize = sizeof(setAttrsTemplate) / sizeof(CK_ATTRIBUTE);

    rc = FunctionListFuncPtr->C_SetAttributeValue(hSession,
            hKey,
            setAttrsTemplate,
            setAttrsTemplateSize);

    if (rc != CKR_OK)
    {
        printf ("Error Setting key state/action: %08x.\n", (unsigned int)rc);
        return rc;
    }
    else
    {
        printf("Successfully set key state to: %d for key handle: %d.\n", (int)state, (int)hKey);
    }
    return rc;
}

void usage()
{
    /*printf ("Usage: pkcs11_sample_key_states -p pin -s slotID -k[p] keyName [-i {k|m|u}:identifier] [-ks key_state] [-m module] [ -d{c|t|a|s|d|p|r} |ps|pt key_transition_date ]\n");*/
    printf ("Usage: pkcs11_sample_key_states -p pin -s slotID -k[p] keyName [-i {k|m|u}:identifier] [-ks key_state] [-m module]\n");

    printf ("identifier: one of 'imported key id' as 'k', MUID as 'm', or UUID as 'u'.\n");
    printf ("key_state: ACTIVATED...1, SUSPENDED...2, DEACTIVATED...3, COMPROMISED...4, DESTROYED...5\n");
    /*printf ("key_transition-date: dc: creation_date; dt: destroy_date; da: activation_date; ds: suspend_date; dd: deactivation_date; dp: compromise_date; dr: compromise_occurrence_date; ps: process_start_date; pt: protect_stop_date .\n");
    printf ("key_transition_date: can be in long format or date format, e.g., 1545134551 or 2017/10/30.\n");*/
    exit (2);
}

/*
 ************************************************************************
 * Function: main
 ************************************************************************
 */
#ifdef THALES_CLI_MODE
int attributesSample (int argc, char* argv[])
#else
int main (int argc, char* argv[])
#endif
{
    CK_RV rc;

    char *pin = NULL;
    char *libPath = NULL;
    char *foundPath = NULL;
    char *keyLabel = NULL;

    char *pcKeyDates[KEY_TRANS_DATES_MAX];
    long val;
    char *next = NULL;
    int  slotId = 0;
    int  c;

    CK_OBJECT_HANDLE hKey;

    CK_BBOOL  bKeyState = CK_FALSE;
    CK_BBOOL  bKeyDate = CK_FALSE;

    KeyState  key_state = KeyStatePreActive;

    char      *pKsid = NULL;
    int       ksid_type = keyIdLabel;

    CK_ATTRIBUTE_TYPE attrTypes[KEY_TRANS_DATES_MAX] = { 0 };
    CK_ULONG   keyDateCount = 0;

    extern char *optarg;
    extern int optind;
    int loggedIn = 0;
    int genAction = 0;

    while ((c = newgetopt(argc, argv, "ps:kp:ks:m:s:i:dc:dt:da:dp:dd:dm:dr:pt:g:")) != EOF)
    {
        switch (c)
        {
        case kp:
            keyLabel = optarg;
            break;
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
        case 'g':
            genAction = atoi(optarg);
            break;
        case 'i':
            ksid_type = parse_ksid_sel(optarg, &pKsid);
            break;

        case ks:
            key_state = (KeyState)atoi(optarg);
            bKeyState = CK_TRUE;
            break;

        case dc:
        case dt:
        case da:
        case dp:
        case dd:
        case dm:
        case dr:
        case ps:
        case pt:
            bKeyDate = CK_TRUE;
            pcKeyDates[keyDateCount] = strdup(optarg);

            switch(c)
            {
            case dc:
                attrTypes[keyDateCount] = CKA_THALES_DATE_OBJECT_CREATE;
                break;
            case dt:
                attrTypes[keyDateCount] = CKA_THALES_DATE_OBJECT_DESTROY;
                break;
            case da:
                attrTypes[keyDateCount] = CKA_THALES_DATE_KEY_ACTIVATION;
                break;
            case dp:
                attrTypes[keyDateCount] = CKA_THALES_DATE_KEY_SUSPENSION;
                break;
            case dd:
                attrTypes[keyDateCount] = CKA_THALES_DATE_KEY_DEACTIVATION;
                break;
            case dm:
                attrTypes[keyDateCount] = CKA_THALES_DATE_KEY_COMPROMISED;
                break;
            case dr:
                attrTypes[keyDateCount] = CKA_THALES_DATE_KEY_COMPROMISE_OCCURRENCE;
                break;
            case ps:
                attrTypes[keyDateCount] = CKA_THALES_DATE_KEY_PROCESS_START;
                break;
            case pt:
                attrTypes[keyDateCount] = CKA_THALES_DATE_KEY_PROTECT_STOP;
                break;
            }

            val = strtol(pcKeyDates[keyDateCount], &next, 10);

            if(next && *next == '\0' && val != 0)
            {
                attrTypes[keyDateCount] = (attrTypes[keyDateCount] & 0x0FFFFFFF) | 0x80000000;
            }

            keyDateCount++;
            break;
        case '?':
        default:
            usage();
            break;
        } /* end switch */
    }
    if ((NULL == pin) || (optind < argc))
    {
        usage();
    }

    printf("Begin Key States Sample: ...\n");
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
                printf("Symmetric key: %s does not exist, Creating key...\n", pKsid);

                if (keyLabel)
                {
                    rc = createSymKeywDates(keyLabel, attrTypes, pcKeyDates, keyDateCount, genAction);
                    if (rc != CKR_OK)
                    {
                        fprintf(stderr, "Failed to create sym key with custom key state transition date(s) by name: %s on Key Manager. \n", keyLabel);
                        break;
                    }
                    else
                    {
                        hKey = hGenKey;
                    }
                }
#if 0
                /* if (keyLabel) {
                    rc = findKeyByName(keyLabel, &hKey);
                    if (rc == CKR_OK && hKey != CK_INVALID_HANDLE) {
                	fprintf(stdout, "Key with name: %s created on Key Manager. \n", keyLabel); *

                rc = setKeyAttributeValue(hKey, symmetric, custom4, custom5);
                    }
                	else {
                        fprintf(stderr, "Failed to create key with name: %s on Key Manager. \n", keyLabel);
                        break;
                    }
                	} */
#endif
            }
            else
            {
                printf("Symmetric key with name: %s already exists.\n", pKsid);

                if(genAction != 0)
                {
                    rc = createSymKeywDates(keyLabel, attrTypes, pcKeyDates, keyDateCount, genAction);
                    if (rc != CKR_OK)
                    {
                        fprintf(stderr, "Failed to create sym key with custom key state transition date(s) by name: %s on Key Manager. \n", keyLabel);
                        break;
                    }
                }

                if(bKeyDate == CK_TRUE)
                {
                    rc = setKeyDateAttributes(hKey, attrTypes, pcKeyDates, keyDateCount);
                }
                else if(bKeyState == CK_TRUE)
                {
                    rc = setKeyStateAttribute(hKey, key_state);
                }
            }

            getSymAttributesValue(hKey, keyDateCount, attrTypes, NULL);
        }

    }
    while (0);

    if (loggedIn)
    {
        rc = logout();
        if (rc == CKR_OK)
        {
            printf("Successfully logged out.\n");
        }
    }

    cleanup();
    printf("End Get/Set Key States sample.\n");
    fflush(stdout);
    return 0;
}
