/*************************************************************************
**                                                                      **
** Sample code is provided for educational purposes.                    **
** No warranty of any kind, either expressed or implied by fact or law. **
** Use of this item is not restricted by copyright or license terms.    **
**                                                                      **
**************************************************************************/
/*
 ***************************************************************************
 * File: pkcs11_sample_create_object.c
 ***************************************************************************
 ***************************************************************************
 * This file demonstrates the following
 * 1. Initialization
 * 2. Creating a connection and logging in.
 * 3. Registering a key or an opaque object on the Key Manager
 * 4. Clean up.
 ***************************************************************************
 */

#include "pkcs11_sample_helper.h"
#include <time.h>

static CK_DATE creationDate = { "", "", "" };

static CK_RV encryptDecryptBuf(CK_SESSION_HANDLE hSess, CK_OBJECT_HANDLE hGenKey, CK_MECHANISM *pMechEnc, CK_MECHANISM *pMechDec)
{
    /* General */
    CK_RV rc        = CKR_OK;
    CK_BYTE		    *cipherText = (CK_BYTE *) "";
    CK_ULONG		cipherTextLen = 0;
    /* For C_Decrypt */
    CK_BYTE         *decryptedText = NULL_PTR;
    CK_ULONG		decryptedTextLen = 0;
    int             status;
    // int taglen = (tag_bits & 0x7) == 0 ? tag_bits >> 3 : (tag_bits >> 3) + 1;
    int taglen = tag_bits >> 3;
    CK_BYTE pBuf[32] =
    {
        't', 'h', 'i', 's', ' ', 'i', 's', ' ',
        'm', 'y', ' ', 's', 'a', 'm', 'p', 'l',
        'e', ' ', 'p', 'l', 'n', ' ', 'd', 'a',
        't', 'a', ' ', '5', '4', '3', '2', '1'
    };
    int len = sizeof(pBuf);

    (void) taglen;

    /* C_EncryptInit */
    rc = FunctionListFuncPtr->C_EncryptInit(hSess,
                                            pMechEnc,
                                            hGenKey
                                           );

    if (rc != CKR_OK)
    {
        fprintf(stderr, "FAIL: call to C_EncryptInit() failed. rv=0x%x\n", (unsigned int)rc);
        goto END;
    }

    /* first call C_Encrypt by pass in NULL to get cipherText buffer size */
    rc = FunctionListFuncPtr->C_Encrypt(
             hSess,
             pBuf, len,
             NULL, &cipherTextLen
         );
    if (rc != CKR_OK)
    {
        fprintf (stderr, "FAIL: 1st call to C_Encrypt() failed. rv=0x%x\n", (unsigned int)rc);
        goto END;
    }
    else
    {
        printf ("1st call to C_Encrypt() succeeded: size = %u.\n", (unsigned int)cipherTextLen);
        cipherText = (CK_BYTE *)calloc( 1, sizeof(CK_BYTE) * cipherTextLen );
        if (!cipherText)
        {
            rc =  CKR_HOST_MEMORY;
            goto END;
        }
    }

    /* then call C_Encrypt to get actual cipherText */
    rc = FunctionListFuncPtr->C_Encrypt(
             hSess,
             pBuf, len,
             cipherText, &cipherTextLen
         );
    if (rc != CKR_OK)
    {
        fprintf (stderr, "FAIL: 2nd call to C_Encrypt() failed. rv=0x%x\n", (unsigned int)rc);
        goto END;
    }

    /* C_DecryptInit */
    printf("About to call C_DecryptInit()\n");

    rc = FunctionListFuncPtr->C_DecryptInit(
             hSess,
             pMechDec,
             hGenKey
         );

    if (rc != CKR_OK)
    {
        fprintf (stderr, "FAIL: Call to C_DecryptInit() failed. rv=0x%x\n", (unsigned int)rc);
        free (cipherText);
        goto END;
    }

    /* pass in NULL, to get the decrypted buffer size  */
    /* usually, use the same size of ciphterText should be fine. */
    printf("About to call C_Decrypt(), output length set to %lu\n", decryptedTextLen);
    rc = FunctionListFuncPtr->C_Decrypt(
             hSess,
             cipherText, cipherTextLen,
             NULL, &decryptedTextLen
         );
    if (rc != CKR_OK)
    {
        fprintf (stderr, "FAIL : 1st call to C_Decrypt() failed. rv=0x%x\n", (unsigned int)rc);
        free (cipherText);
        goto END;
    }
    else
    {
        printf ("1st call to C_Decrypt() succeeded.\n");
        decryptedText = (CK_BYTE *)calloc( 1, sizeof(CK_BYTE) * decryptedTextLen );
        if ( NULL == decryptedText)
        {
            free (cipherText);
            rc =  CKR_HOST_MEMORY;
            goto END;
        }
    }

    /* now pass in the buffer, to get the decrypted text and real decrypted size */
    printf("a.t.c. C_Decrypt(), output length set to %lu\n", decryptedTextLen);
    rc = FunctionListFuncPtr->C_Decrypt(
             hSess,
             cipherText, cipherTextLen,
             decryptedText, &decryptedTextLen
         );

    if (rc != CKR_OK)
    {
        fprintf (stderr, "FAIL: 2nd call to C_Decrypt() failed. rv=0x%x\n", (unsigned int)rc);
        free (cipherText);
        goto END;
    }
    else
    {
        printf ("2nd call to C_Decrypt() succeeded. Decrypted Text:\n");
        dumpHexArray(decryptedText, (int)decryptedTextLen);
    }

    /* cleanup and free memory */
    free (cipherText);

    /* compare the plaintext and decrypted text */
    status = memcmp( pBuf, decryptedText, decryptedTextLen );
    if (status == 0)
    {
        printf ("Success! Plain Text and Decrypted Text match!! \n\n");
        rc =  CKR_OK;
        goto END;
    }
    else
    {
        printf ("Failure!, Plain Text and Decrypted Text do NOT match!! \n");
        rc =  CKR_GENERAL_ERROR;
        goto END;
    }

END:
    if(decryptedText)
        free(decryptedText);

    return rc;
}

static CK_RV signVerifyBuf(CK_SESSION_HANDLE hSess, CK_OBJECT_HANDLE hGenKey, CK_MECHANISM *pMech)
{
    /* General */
	/* For C_Sign */
    CK_RV rc        = CKR_OK;
    CK_BYTE		    *msgDigest = NULL_PTR;
    CK_ULONG		msgDigestLen = 0;
    int             status;
    CK_BYTE pBuf[32] =
    {
        't', 'h', 'i', 's', ' ', 'i', 's', ' ',
        'm', 'y', ' ', 's', 'a', 'm', 'p', 'l',
        'e', ' ', 'p', 'l', 'n', ' ', 'd', 'a',
        't', 'a', ' ', '5', '4', '3', '2', '1'
    };
    int len = sizeof(pBuf);

    /* C_SignInit */
    rc = FunctionListFuncPtr->C_SignInit(hSess, pMech, hGenKey);

    if (rc != CKR_OK)
    {
        fprintf(stderr, "FAIL: call to C_SignInit() failed. rv=0x%x\n", (unsigned int)rc);
        goto END;
    }

    /* first call C_Sign by pass in NULL to get msgDigest buffer size */
    rc = FunctionListFuncPtr->C_Sign(
             hSess,
             pBuf, len,
             NULL, &msgDigestLen
         );
    if (rc != CKR_OK)
    {
        fprintf (stderr, "FAIL: 1st call to C_Sign() failed. rv=0x%x\n", (unsigned int)rc);
        goto END;
    }
    else
    {
        printf ("1st call to C_Sign() succeeded: size = %u.\n", (unsigned int)msgDigestLen);
        msgDigest = (CK_BYTE *)calloc( 1, sizeof(CK_BYTE) * msgDigestLen );
        if (!msgDigest)
        {
            rc =  CKR_HOST_MEMORY;
            goto END;
        }
    }

    /* then call C_Sign to get actual msgDigest */
    rc = FunctionListFuncPtr->C_Sign(
             hSess,
             pBuf, len,
             msgDigest, &msgDigestLen
         );
    if (rc != CKR_OK)
    {
        fprintf (stderr, "FAIL: 2nd call to C_Sign() failed. rv=0x%x\n", (unsigned int)rc);
        goto END;
    }

    /* C_VerifyInit */
    printf("About to call C_VerifyInit()\n");

    rc = FunctionListFuncPtr->C_VerifyInit(hSess, pMech, hGenKey);

    if (rc != CKR_OK)
    {
        fprintf (stderr, "FAIL: Call to C_VerifyInit() failed. rv=0x%x\n", (unsigned int)rc);
        goto END;
    }


    printf("About to call C_Verify(), output length set to %lu\n", msgDigestLen);
    rc = FunctionListFuncPtr->C_Verify(
             hSess,
             pBuf, len,
             msgDigest, msgDigestLen
         );
	switch (rc) {

	case CKR_SIGNATURE_INVALID:
        printf ("C_Verify() failed.\n");
		break;

	case CKR_OK:
        printf ("C_Verify() succeeded.\n");
		break;
    
	default:
        fprintf (stderr, "FAIL : call to C_Verify() failed. rv=0x%x\n", (unsigned int)rc);
    }

END:
    /* cleanup and free memory */
	if (msgDigest) {
		free (msgDigest);
		msgDigest = NULL;
	}
    return rc;
}
 
/*
 ************************************************************************
 * Function: createObject
 * Imports an AES 256 key into the Key Manager.
 * The keyLabel is the name of the key displayed on the Key Manager.
 ************************************************************************
 * Parameters: keyLabel
 * Returns: CK_RV
 ************************************************************************
 */

static CK_RV createObjectBVersion(char *keyLabel, CK_BBOOL bVersionedKey, int version,
                                  char *pBaseKsid, int bksidType, CK_BBOOL bCreationDate,
                                  CK_BBOOL bOpaque, CK_ULONG opaqueSize, FILE *pf, char *KEYID, char *UUID, char *MUID, char *ALIAS, char *idattr)
{
    CK_RV       rc = CKR_OK;
    CK_UTF8CHAR	app[] = { "CADP_PKCS11_SAMPLE" };
    CK_UTF8CHAR defKeyValue[DEFAULT_KEYLEN] =
    {
        't', 'h', 'i', 's', ' ', 'i', 's', ' ',
        'm', 'y', ' ', 's', 'a', 'm', 'p', 'l',
        'e', ' ', 'k', 'e', 'y', ' ', 'd', 'a',
        't', 'a', ' ', '5', '4', '3', '2', '1'
    };

    CK_OBJECT_CLASS		keyClass = bOpaque == CK_TRUE ? CKO_THALES_OPAQUE_OBJECT : CKO_SECRET_KEY ;
    CK_KEY_TYPE			keyType = CKK_AES;
    CK_ULONG			keySize ;  /* 256 bits  */
    CK_BBOOL			bFalse = CK_FALSE;
    CK_BBOOL			bTrue = CK_TRUE;
    CK_OBJECT_HANDLE	hObject = 0x0;

    CK_UTF8CHAR         *id_label = (CK_UTF8CHAR *) idattr ? idattr : keyLabel;
    CK_UTF8CHAR         *label = (CK_UTF8CHAR *) keyLabel;
    CK_ULONG            len = (CK_ULONG) strlen(keyLabel);
    CK_ULONG            id_len = (CK_ULONG) strlen(id_label);

    CK_LONG             lVersion = (CK_LONG)version;
    CK_UTF8CHAR         *baseKsid = (CK_UTF8CHAR *) pBaseKsid;
    CK_ULONG            aesKeyTemplateBase;
    CK_ULONG            id;
    CK_ULONG            baseKsidLen = pBaseKsid ? (CK_ULONG) strlen(pBaseKsid) : 0;

    CK_BYTE_PTR         keyValue =  bOpaque ? malloc( opaqueSize ) : pf ? malloc(SYMKEY_BUF_LEN) :  &defKeyValue;
    CK_MECHANISM mech = { CKM_AES_CBC_PAD,   def_iv, 16 };
    CK_MECHANISM mechsv = { CKM_SHA256_HMAC, NULL, 0 };
    if(!keyValue)
        return CKR_HOST_MEMORY;

    CK_ULONG            keyvaluelen = bOpaque ? opaqueSize : (CK_ULONG)sizeof(defKeyValue);

    if(pf)
    {
        rc  = readObjectBytes( pf, keyValue, &keyvaluelen, CKA_RAW_FORMAT );
    }

    if(rc == CKR_OK)
        keySize = keyvaluelen;
    else
        goto FREE_RESOURCES;

    /* AES key template.
     * CKA_LABEL is the name of the key and will be displayed on the Key Manager
     * CKA_VALUE is the bytes that make up the AES key.
     */

    CK_ATTRIBUTE aesKeyTemplate[26] =
    {
        /* type,            	pValue, 	ulValueLen     */
        {CKA_ID,				id_label,	id_len 			},
        {CKA_LABEL,				label,		len 			},
        {CKA_APPLICATION,		&app,		sizeof(app)		},
        {CKA_CLASS,				&keyClass,	sizeof(keyClass)},
        {CKA_KEY_TYPE,			&keyType,	sizeof(keyType)	},
        {CKA_VALUE,				keyValue,	keyvaluelen		},
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

        {CKA_THALES_VERSIONED_KEY, &bVersionedKey, sizeof(CK_BBOOL) },
        {CKA_THALES_BASE_LABEL, baseKsid, baseKsidLen               },
        {CKA_THALES_DATE_OBJECT_CREATE, &creationDate, sizeof(CK_DATE) },
        {CKA_THALES_KEY_VERSION, &lVersion, sizeof(lVersion) }
    };
    CK_ULONG	aesKeyTemplateSize =  sizeof(aesKeyTemplate)/sizeof(CK_ATTRIBUTE)-4;


    if( bOpaque && keyValue )
    {
        size_t i;
        // if we have a valid filepointer means we read object from file...
        if(!pf)
            for (i=0; i <opaqueSize; i++)
                keyValue[i] = defKeyValue[ i % sizeof(defKeyValue) ];
    }

    printf("Key label: %s\n", keyLabel);

    if(version < 0)   /* this code assumes that KEY_VERSION is last in the array */
    {
        aesKeyTemplateSize--;

        if(bCreationDate == CK_FALSE)
        {
            aesKeyTemplateSize--;
            aesKeyTemplateBase = aesKeyTemplateSize - 1;
        }
        else
        {
            aesKeyTemplateBase = aesKeyTemplateSize - 2;
        }
    }
    else
    {
        if(bCreationDate == CK_FALSE)
        {
            aesKeyTemplateSize--;
            aesKeyTemplate[aesKeyTemplateSize-1].type = aesKeyTemplate[aesKeyTemplateSize].type;
            aesKeyTemplate[aesKeyTemplateSize-1].pValue = aesKeyTemplate[aesKeyTemplateSize].pValue;
            aesKeyTemplate[aesKeyTemplateSize-1].ulValueLen = aesKeyTemplate[aesKeyTemplateSize].ulValueLen;

            aesKeyTemplateBase = aesKeyTemplateSize - 2;
        }
        else
        {
            aesKeyTemplateBase = aesKeyTemplateSize - 3;
        }
    }

    if (KEYID)
    {
        aesKeyTemplate[aesKeyTemplateSize].type = CKA_THALES_OBJECT_IKID;
        aesKeyTemplate[aesKeyTemplateSize].pValue = KEYID;
        aesKeyTemplate[aesKeyTemplateSize++].ulValueLen = (CK_ULONG)strlen(KEYID);
    }

    if (UUID)
    {
        aesKeyTemplate[aesKeyTemplateSize].type = CKA_THALES_OBJECT_UUID;
        aesKeyTemplate[aesKeyTemplateSize].pValue = UUID;
        aesKeyTemplate[aesKeyTemplateSize++].ulValueLen = (CK_ULONG)strlen(UUID);
    }

    if (MUID)
    {
        aesKeyTemplate[aesKeyTemplateSize].type = CKA_THALES_OBJECT_MUID;
        aesKeyTemplate[aesKeyTemplateSize].pValue = MUID;
        aesKeyTemplate[aesKeyTemplateSize++].ulValueLen = (CK_ULONG)strlen(MUID);
    }

    if (ALIAS)
    {
        aesKeyTemplate[aesKeyTemplateSize].type = CKA_THALES_OBJECT_ALIAS;
        aesKeyTemplate[aesKeyTemplateSize].pValue = ALIAS;
        aesKeyTemplate[aesKeyTemplateSize++].ulValueLen = (CK_ULONG)strlen(ALIAS);
    }

    if( pBaseKsid )
    {
        switch(bksidType)
        {
        case keyIdLabel:
            aesKeyTemplate[aesKeyTemplateBase].type = CKA_THALES_BASE_LABEL;
            break;

        case keyIdUuid:
            aesKeyTemplate[aesKeyTemplateBase].type = CKA_THALES_BASE_UUID;
            break;

        case keyIdMuid:
            aesKeyTemplate[aesKeyTemplateBase].type = CKA_THALES_BASE_MUID;
            break;

        case keyIdImport:
            aesKeyTemplate[aesKeyTemplateBase].type = CKA_THALES_BASE_IKID;
            break;

        case keyIdAlias:
            aesKeyTemplate[aesKeyTemplateBase].type = CKA_THALES_BASE_ALIAS;
            break;

        default:
            rc = CKR_ARGUMENTS_BAD;
            fprintf (stderr, "FAIL: call to the CreateObjectBVersion() failed; rc=0x%8x; BaseKeyId type : %x", (unsigned int)rc, bksidType);
            return rc;
        }
    }
    else
    {
        if(version > 0 || bCreationDate == CK_TRUE)
        {
            rc = CKR_ARGUMENTS_BAD;
            fprintf (stderr, "FAIL: call to the CreateObjectBVersion() failed; rc=0x%8x; No BaseKeyId.", (unsigned int)rc);
            return rc;
        }
        else
        {
            aesKeyTemplateSize --;

            for(id=aesKeyTemplateBase; id<aesKeyTemplateSize; id++)
            {
                aesKeyTemplate[id].type = aesKeyTemplate[id+1].type;
                aesKeyTemplate[id].pValue = aesKeyTemplate[id+1].pValue;
                aesKeyTemplate[id].ulValueLen = aesKeyTemplate[id+1].ulValueLen;
            }
        }
    }

    rc = FunctionListFuncPtr->C_CreateObject (hSession,
            aesKeyTemplate,
            aesKeyTemplateSize,
            &hObject
                                             );
    if (rc != CKR_OK || hObject == 0)
    {
        fprintf (stderr, "Error in C_CreateObject(), return value: %d\n", (int)rc);
    }

	if (!bOpaque) {
		/* encrypt/decrypt using the freshly minted key */
		rc = encryptDecryptBuf(hSession, hObject, &mech, &mech);
		if (rc != CKR_OK)
		{
			fprintf (stderr, "Error in Encrypt/Decrypt: return value: %d\n", (int)rc);
		}
	} else {
		/* sign/verify using the freshly minted key */
		rc = signVerifyBuf(hSession, hObject, &mechsv);
		if (rc != CKR_OK)
		{
			fprintf (stderr, "Error in Sign/Verify: return value: %d\n", (int)rc);
		}
	}

FREE_RESOURCES:
    if((bOpaque || pf) && keyValue)
        free(keyValue);

    // Close file after generating the keyValue so we can use to spot we read a file
    if( pf )
    {
        fclose(pf);
    }
    return rc;
}

static CK_OBJECT_HANDLE importAsymKeyPair(char *keyLabel, CK_OBJECT_CLASS keyClass, CK_BYTE modulusBuf[], CK_ULONG modulusBufLen,
        CK_BYTE pubExpoBuf[], CK_ULONG pubExpoBufLen, CK_BYTE privExpoBuf[], CK_ULONG privExpoBufLen,
        CK_BBOOL bCreationDate, unsigned mod_bits)
{
    CK_RV               rc = CKR_OK;
    CK_ULONG			modulusBits = mod_bits;
    /*	CK_BYTE				publicExponent[4] = { 0x01, 0x00, 0x01, 0x00 }; * 65537 in bytes */
    CK_BBOOL			bTrue = CK_TRUE;
    CK_ULONG            keyLabelLen = (CK_ULONG)strlen((const char *)keyLabel);
    CK_OBJECT_HANDLE	hAsymKey;
    CK_KEY_TYPE			keyType = CKK_RSA;

    CK_ATTRIBUTE	asymKeyTemplate[] =
    {
        {CKA_LABEL, keyLabel, keyLabelLen }, /* Keyname */
        {CKA_CLASS, &keyClass, sizeof(keyClass)},
        {CKA_KEY_TYPE,	&keyType,	sizeof(keyType)	},
        {CKA_ENCRYPT, &bTrue, sizeof(bTrue)},
        {CKA_VERIFY, &bTrue, sizeof(bTrue)},
        {CKA_WRAP, &bTrue, sizeof(bTrue)},
        {CKA_TOKEN, &bTrue, sizeof(bTrue)},
        {CKA_MODULUS_BITS, &modulusBits, sizeof(modulusBits)},

        {CKA_MODULUS, modulusBuf, modulusBufLen},
        {CKA_PUBLIC_EXPONENT, pubExpoBuf, pubExpoBufLen},
        {CKA_PRIVATE_EXPONENT, privExpoBuf, privExpoBufLen},
        {CKA_THALES_DATE_OBJECT_CREATE, &creationDate, sizeof(CK_DATE) }
    };
    CK_ULONG asymKeyTemplateSize = sizeof(asymKeyTemplate)/sizeof(CK_ATTRIBUTE);

    if(bCreationDate == CK_FALSE)
    {
        asymKeyTemplateSize--;
    }

    /*	if (keyClass == CKO_PRIVATE_KEY) {

    	asymKeyTemplate[asymKeyTemplateSize-1].type = CKA_PRIVATE_EXPONENT;
    	} */

    rc = FunctionListFuncPtr->C_CreateObject (hSession,
            asymKeyTemplate,
            asymKeyTemplateSize,
            &hAsymKey
                                             );
    if (rc != CKR_OK || hAsymKey == 0)
    {
        fprintf (stderr, "Error in C_CreateObject(), return value: %d\n", (int)rc);
    }

    return hAsymKey;
}



void usageCreateObject()
{
    printf("Usage: pkcs11_sample_create_object -p pin -s slotID {-k keyName | -kp keypair_name | -o opaqueObjectName} [-v keyVersion] [-dc creationDate] [-B basekey_identifier] [-m module] [-f binarykeyfile]\n");
    printf("-b opaque object byte size or keypair bits size.\n");
    printf("[-K imported keyID] [-U imported UUID] [-M imported MUID] [-I imported CKA_ID][-A imported alias for key(gloabl unique identifier)]\n");
    printf("-v keyVersion, version of the key being imported, leave empty will use creation date as default for sorting version\n");
    printf("-c creationDate, date of the key being created, used to sort the versions for versioned key, e.g., 2017/10/10 \n");
    printf("Note: If -K, -U, -M, and/or -A are specified along with -k or -o, this simulates a 'key import' scenario where the key must have a specific key ID, UUID, MUID, and/or Alias\n");
    printf("-B base key identifier, can be {n:u:m:k:a} key_identifier");
    printf("-na new alias to be set\n");
    printf("-Da delete existing alias\n");
    printf("Note: keyVersion is a numerical value\n");
    exit(2);
}


/*
 ************************************************************************
 * Function: main
 ************************************************************************
 */

#ifdef THALES_CLI_MODE
int createObjectSample (int argc, char *argv[])
#else
int main(int argc, char *argv[])
#endif
{
    CK_RV        rc;
    char        *objLabel = NULL;
    char        *kpLabel = NULL;
    char        *pin = NULL;
    char        *libPath = NULL;
    char        *foundPath = NULL;
    char        *pKsid = NULL;
    char        *pBaseKsid = NULL;
    int          ksid_type = keyIdLabel;   /* keyIdUuid keyIdMuid keyIdImport */
    int          bk_sid_type = keyIdLabel;
    int          slotId = 0;
    int          key_version = -1;

    CK_OBJECT_CLASS  keyClass = CKO_SECRET_KEY;
    CK_OBJECT_HANDLE hObject = 0;
    CK_OBJECT_HANDLE hPublicKey = 0;
    CK_OBJECT_HANDLE hPrivateKey = 0;
    CK_OBJECT_HANDLE hImportedKey = 0;

    CK_BYTE      pubExpoBuf[ASYMKEY_BUF_LEN];
    CK_BYTE      privExpoBuf[ASYMKEY_BUF_LEN];
    CK_BYTE      modulusBuf[ASYMKEY_BUF_LEN];
    CK_BYTE      modulusBuf2[ASYMKEY_BUF_LEN];
    CK_BBOOL     bVersionedKey = CK_FALSE;
    CK_BBOOL     bCreationDate = CK_FALSE;
    CK_BBOOL     bOpaque = CK_FALSE;
    CK_BBOOL     bAsymKeyPair = CK_FALSE;
    CK_BBOOL     bSetAlias = CK_FALSE;
    CK_ULONG     modulusBufLen = 256;
    CK_ULONG     modulusBufLen2 = 256;
    CK_ULONG     pubExpoBufLen = 256;
    CK_ULONG     privExpoBufLen = 256;

    int c;
    extern char *optarg;
    extern int   optind;
    int          loggedIn = 0;
    FILE        *pf=NULL;
    char        *KEYID=NULL;
    char        *UUID=NULL;
    char        *MUID=NULL;
    char        *ALIAS = NULL;
    char        *idattr = NULL;
    char        *newAlias=NULL;

    unsigned int modBits = MODULUS_BITS;
    unsigned int opaqueSize = 257;

    while ((c = newgetopt(argc, argv, "p:kp:m:s:b:dc:o:f:K:U:I:M:B:A:v:na:Sa")) != EOF)
    {
        switch (c)
        {
        case 'p':
            pin = optarg;
            break;
        case 'k':
            objLabel = parse_key_class(optarg, &keyClass);
            break;
        case kp:
            kpLabel = optarg;
            bAsymKeyPair = CK_TRUE;
            break;
        case 'm':
            libPath = optarg;
            break;
        case 's':
            slotId = atoi(optarg);
            break;
        case 'o':
            bOpaque = CK_TRUE;
            objLabel = optarg;
            break;
        case dc:
            bCreationDate = CK_TRUE;
            parse_ck_date(optarg, &creationDate);
            break;
        case 'v':
            bVersionedKey = CK_TRUE;
            key_version = atoi(optarg);
            break;
        case 'K':
            KEYID= optarg;
            break;
        case 'U':
            UUID = optarg;
            break;
        case 'M':
            MUID = optarg;
            break;
        case 'I':
            idattr = optarg;
            break;
        case 'A':
            ALIAS = optarg;
            break;
        case na:
            bSetAlias = CK_TRUE;
            newAlias = optarg;
            break;
        case Sa:
            bSetAlias = CK_TRUE;
            break;
        case 'b':
            modBits = atoi(optarg);
            opaqueSize = atoi(optarg);
            break;
        case 'f':
            pf = fopen(optarg, "r");
            break;
        case 'B':
            bk_sid_type = parse_ksid_sel(optarg, &pBaseKsid);
            break;
        case '?':
        default:
            usageCreateObject();
            break;
        }
    }

    if ((NULL == pin) || (optind < argc) || (objLabel == NULL))
    {
        usageCreateObject();
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

        if(objLabel)
        {
            pKsid = objLabel;
            ksid_type = keyIdLabel;
        }
        printf("ksid type: %d.\n", ksid_type);

        printf("Creating/Registering key ...\n");

        if( bAsymKeyPair == CK_TRUE )
        {

            if(objLabel != NULL)
            {

                findKey(objLabel, keyIdLabel, CKO_PUBLIC_KEY, &hPublicKey);

                if(hPublicKey != CK_INVALID_HANDLE)
                {

                    getAsymAttributesValue(hPublicKey, CKO_PUBLIC_KEY, modulusBuf, &modulusBufLen, pubExpoBuf, &pubExpoBufLen, privExpoBuf, &privExpoBufLen);
                    printf("CKA_MODULUS (Public Key): size=%u\n", (unsigned int)modulusBufLen);
                    printf("CKA_PUBLIC_EXPONENT: size=%u; \n", (unsigned int)pubExpoBufLen);
                }
                else
                {
                    fprintf(stderr, "Not Found: public key with name %s could not be found. \n", objLabel);
                    break;
                }

                findKey(objLabel, keyIdLabel, CKO_PRIVATE_KEY, &hPrivateKey);

                if(hPrivateKey != CK_INVALID_HANDLE)
                {

                    getAsymAttributesValue(hPrivateKey, CKO_PRIVATE_KEY, modulusBuf2, &modulusBufLen2, pubExpoBuf, &pubExpoBufLen, privExpoBuf, &privExpoBufLen);
                    printf("CKA_MODULUS (Priv Key): size=%u\n", (unsigned int)modulusBufLen2);
                    printf("CKA_PRIVATE_EXPONENT: size=%u; \n", (unsigned int)privExpoBufLen);
                }
                else
                {
                    fprintf(stderr, "Not Found: private key with name %s could not be found. \n", objLabel);
                    break;
                }

                if(kpLabel)
                {
                    hImportedKey = importAsymKeyPair(kpLabel, CKO_PUBLIC_KEY, modulusBuf, modulusBufLen, pubExpoBuf, pubExpoBufLen,
                                                     privExpoBuf, privExpoBufLen, FALSE, modBits);

                    if(hImportedKey != CK_INVALID_HANDLE)
                    {
                        printf("Successfully imported asymmetric key pair '%s'; key handle= 0x%x.\n", kpLabel, (unsigned int)hImportedKey );
                    }
                    else
                    {
                        fprintf(stderr, "Failed to import asym key %s \n", kpLabel);
                        break;
                    }
                }
            }
        }
        else
        {
            if(bOpaque == CK_TRUE)
                rc = findKey(pKsid, ksid_type, CKO_THALES_OPAQUE_OBJECT, &hObject);
            else
                rc = findKey(pKsid, ksid_type, CKO_SECRET_KEY, &hObject);

            if (rc == CKR_OK && hObject != CK_INVALID_HANDLE)
            {
                fprintf(stderr, "Found: %s with same name already exist. \n", bOpaque ? "Opaque Object" : "Key" );
                if(bOpaque == CK_TRUE)
                   goto END; //If object already exists do nothing.
            }

            rc = createObjectBVersion(objLabel, bVersionedKey, key_version, pBaseKsid, bk_sid_type, bCreationDate, bOpaque, opaqueSize, pf, KEYID, UUID, MUID, ALIAS, idattr);

            if (rc != CKR_OK)
            {
                fprintf(stderr, "FAIL: Key object registration failed.\n");
            }
            else
            {
                printf("Successfully created %s: '%s' by C_CreateObject.\n", bOpaque? "opaque object" : "key", objLabel);
            }

            if(bOpaque == CK_TRUE)
                rc = findKey(pKsid, ksid_type, CKO_THALES_OPAQUE_OBJECT, &hObject);
            else
                rc = findKey(pKsid, ksid_type, CKO_SECRET_KEY, &hObject);

            if (rc == CKR_OK && hObject != CK_INVALID_HANDLE)
            {
                printf("%s with name(id) %s found after CreateObject with key handle = %u \n", bOpaque ? "Opaque Object" : "Key", pKsid, (unsigned int)hObject);
            }
            else
            {
                fprintf(stderr, "Fail to find: key with name(id) %s. \n", pKsid);
            }

            if(bSetAlias == CK_TRUE)
            {
                rc = setKeyAlias(hObject, newAlias);
                if (rc == CKR_OK)
                {
                    printf("key alias %s!\n", newAlias? "SET":"DELETED" );
                }
                else
                {
                    fprintf(stderr, "Fail to set key alias; rv = %d\n", (int)rc);
                }
            }
        }

    }
    while (0);

END:
    if (loggedIn)
    {
        if (logout() == CKR_OK)
        {
            printf("Successfully logged out.\n");
        }
    }

    cleanup ();
    printf("End Create Object sample.\n");
    fflush(stdout);
    return rc;
}
