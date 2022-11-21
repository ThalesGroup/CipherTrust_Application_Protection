/**                                                                      **
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
 * File: pkcs11_sample_sign_verify.c
 ***************************************************************************
 ***************************************************************************
 * This file demonstrates the following
 * 1. Initialization
 * 2. Creating a connection and logging in.
 * 3. Creating a symmetric key on the Key Manager for MAC'ing
 * 4. Sign and verify using HMAC-SHA mechanisms for a given message
 * 5. Clean up.
 */

/*
   pkcs11_sample_sign_verify.c
 */

#include "pkcs11_sample_sign_verify.h"
#include "pkcs11_sample_helper.h"
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

#ifdef __WINDOWS__

typedef int __ssize_t;
typedef __ssize_t ssize_t;

#else
#endif

#define READ_BLK_LEN 1024
CK_BYTE	defPlaintextMsg[80] = "\xef\xbb\xbf\x53\x65\x63\x74\x69\x6f\x6e\x0d\x0a\x45\x6e\x64\x47\x6c\x6f\x62\x61\x6C\x0D\x0A"; /* 23 characters */
unsigned plaintextLen=23;
int     errorCountDigest = 0;

CK_OBJECT_HANDLE     hPubKey = CK_INVALID_HANDLE;
CK_OBJECT_HANDLE     hPrivKey = CK_INVALID_HANDLE;
CK_BBOOL             bAsymKey = CK_FALSE;

#ifdef DIGESTKEY_VERIFY
static CK_RV computeDigest(CK_SESSION_HANDLE hSess, CK_MECHANISM *pMech,
                           CK_BYTE *pBuf, unsigned int len, CK_BYTE **message,
                           unsigned long *messageLen)
{
    /* General */
    CK_RV rc = CKR_OK;

    /* C_DigestInit */
    rc = FunctionListFuncPtr->C_DigestInit(hSess, pMech);
    if (rc != CKR_OK)
    {
        fprintf(stderr, "FAIL: call to C_DigestInit() failed.\n");
        return rc;
    }

    switch (pMech->mechanism)
    {
    case CKM_SHA256_HMAC:
    case CKM_SHA_1_HMAC:
    case CKM_SHA224_HMAC:
    case CKM_SHA384_HMAC:
    case CKM_SHA512_HMAC:

        rc = FunctionListFuncPtr->C_DigestKey(hSess, hGenKey);
        if (rc != CKR_OK)
        {
            fprintf(stderr, "FAIL: call to C_DigestKey() failed.\n");
            return rc;
        }
    default:
        break;
    }

    /* call C_DigestUpdate by pass in NULL to get message buffer size */
    rc = FunctionListFuncPtr->C_DigestUpdate(hSess, pBuf, len);
    if (rc != CKR_OK)
    {
        fprintf (stderr, "FAIL: call to C_DigestUpdate() failed.\n");
        return rc;
    }
    else
    {
        printf ("call to C_DigestUpdate() succeeded\n");
    }

    *messageLen = 0;
    /* first call C_DigestFinal by pass in NULL to get message buffer size */
    rc = FunctionListFuncPtr->C_DigestFinal(hSess, NULL, messageLen);
    if (rc != CKR_OK)
    {
        fprintf (stderr, "FAIL: 1st call to C_DigestFinal() failed.\n");
        return rc;
    }
    else
    {
        printf ("1st call to C_DigestFinal() succeeded: size = %u.\n", (unsigned int) *messageLen);
        *message = (CK_BYTE *)calloc( 1, sizeof(CK_BYTE) * *messageLen );
        if (!*message)
            return CKR_HOST_MEMORY;
    }

    /* then call C_Digest to get actual message */
    rc = FunctionListFuncPtr->C_DigestFinal(hSess, *message, messageLen);
    if (rc != CKR_OK)
    {
        fprintf (stderr, "FAIL: 2nd call to C_DigestFinal() failed\n");
        return rc;
    }
    else
    {
        printf ("2nd call to C_DigestFinal() succeeded. Digested Text:\n");
        dumpHexArray( *message, (int) *messageLen );
    }

    return rc;
}
#endif

static CK_RV signBlock(CK_SESSION_HANDLE hSess, CK_MECHANISM *pMech,
                       CK_BYTE *pBuf, unsigned int len, CK_BYTE **signature,
                       CK_ULONG *signatureLen)
{
    /* General */
    CK_RV rc = CKR_OK;

    /* C_SignInit */
    if(bAsymKey == CK_TRUE)
        rc = FunctionListFuncPtr->C_SignInit(hSess, pMech, hPrivKey);
    else
        rc = FunctionListFuncPtr->C_SignInit(hSess, pMech, hGenKey);

    if (rc != CKR_OK)
    {
        fprintf(stderr, "FAIL: call to C_SignInit() failed.\n");
        return rc;
    }

    *signatureLen = 0;
    /* first call C_Sign by pass in NULL to get signature buffer size */
    rc = FunctionListFuncPtr->C_Sign(hSess, pBuf, len, NULL, signatureLen);
    if (rc != CKR_OK)
    {
        fprintf (stderr, "FAIL: 1st call to C_Sign() failed.\n");
        return rc;
    }

    *signature = (CK_BYTE *)calloc( 1, sizeof(CK_BYTE) * *signatureLen );
    if (!*signature)
        return CKR_HOST_MEMORY;

    /* call C_Sign by pass in NULL to get signature buffer size */
    rc = FunctionListFuncPtr->C_Sign(hSess, pBuf, len, *signature, signatureLen);
    if (rc != CKR_OK)
    {
        fprintf (stderr, "FAIL: call to C_Sign() failed.\n");
        return rc;
    }
    else
    {
        printf ("call to C_Sign() succeeded\n");
        dumpHexArray( *signature, (int) *signatureLen );
    }

    return rc;
}


static CK_RV verifyBlock(CK_SESSION_HANDLE hSess, CK_MECHANISM *pMech,
                         CK_BYTE *pBuf, unsigned int len, CK_BYTE *signature,
                         CK_ULONG signatureLen)
{
    /* General */
    CK_RV rc = CKR_OK;

    /* C_VerifyInit */
    if(bAsymKey == CK_TRUE)
        rc = FunctionListFuncPtr->C_VerifyInit(hSess, pMech, hPubKey);
    else
        rc = FunctionListFuncPtr->C_VerifyInit(hSess, pMech, hGenKey);

    if (rc != CKR_OK)
    {
        fprintf(stderr, "FAIL: call to C_VerifyInit() failed.\n");
        return rc;
    }

    /* call C_Verify by pass in NULL to get signature buffer size */
    rc = FunctionListFuncPtr->C_Verify(hSess, pBuf, len, signature, signatureLen);
    if (rc != CKR_OK)
    {
        fprintf (stderr, "FAIL: call to C_Verify() failed = 0x%x\n", (int) rc);
        return rc;
    }
    else
    {
        printf ("call to C_Verify() succeeded\n");
    }

    return rc;
}

/*
 ************************************************************************
 * Function: signVerifyFile
 * This function takes a given message and computes the correponding signature,
 * using a key
 ************************************************************************
 * Parameters: operation ... SHA256-HMAC, SHA224-HMAC, SHA1-HMAC, SHA384-HMAC, SHA512-HMAC, SHA1-RSA, SHA256-RSA, SHA384-RSA, SHA512-RSA
 * Returns: CK_RV
 ************************************************************************
 */
static CK_RV signVerifyFile(char *operation, char *filename, char *signature_file, char *header_version)
{
    CK_BYTE	        *pBuf = NULL;
    CK_BYTE         *pSignBuf = NULL;
    FILE            *fp_read = NULL;
    FILE            *fp_write = NULL;
    ssize_t         readlen = 0;
    size_t          bf_len = READ_BLK_LEN;

#ifdef DIGESTKEY_VERIFY
    CK_BYTE         *pDigestBuf = NULL;
    CK_ULONG        digestLen;
    CK_RV           rc1 = CKR_OK;
    int             cmp = 0;
#endif
    CK_ULONG        signLen;
    CK_RV           rc = CKR_OK;
    CK_ULONG        headersign=0; /* no header */
    CK_ULONG        headervfy =0; /* no header */

    if (!header_version || strlen(header_version)<4 || header_version[0]!='v' || header_version[2]!='.')
        headersign=headervfy=0; /* no header */
    else switch(header_version[3])
        {
            /* v2.1, v2.7 */
        case '1':
            headersign=CKM_THALES_V21HDR|CKM_VENDOR_DEFINED;
            headervfy =CKM_THALES_ALLHDR|CKM_VENDOR_DEFINED;
            break;
        case '7':
            headersign=CKM_THALES_V27HDR|CKM_VENDOR_DEFINED;
            headervfy =CKM_THALES_ALLHDR|CKM_VENDOR_DEFINED;
            break;
        default :
            headersign=0; /* no header */
            headervfy =0;
            break;
        }

    /* C_Digest */
    CK_MECHANISM	signmechSHA256hmac = { headersign|CKM_SHA256_HMAC, NULL, 0};
    CK_MECHANISM	signmechSHA384hmac = { headersign|CKM_SHA384_HMAC, NULL, 0};
    CK_MECHANISM	signmechSHA512hmac = { headersign|CKM_SHA512_HMAC, NULL, 0};
    CK_MECHANISM	signmechSHA224hmac = { headersign|CKM_SHA224_HMAC, NULL, 0};
    CK_MECHANISM	signmechSHA1hmac   = { headersign|CKM_SHA_1_HMAC,  NULL, 0};
    CK_MECHANISM	vfymechSHA256hmac  = { headervfy |CKM_SHA256_HMAC, NULL, 0};
    CK_MECHANISM	vfymechSHA384hmac  = { headervfy |CKM_SHA384_HMAC, NULL, 0};
    CK_MECHANISM	vfymechSHA512hmac  = { headervfy |CKM_SHA512_HMAC, NULL, 0};
    CK_MECHANISM	vfymechSHA224hmac  = { headervfy |CKM_SHA224_HMAC, NULL, 0};
    CK_MECHANISM	vfymechSHA1hmac    = { headervfy |CKM_SHA_1_HMAC,  NULL, 0};

    CK_MECHANISM	signvfymechSHA1RSAPkcs     = { CKM_SHA1_RSA_PKCS,  NULL, 0};
    CK_MECHANISM	signvfymechSHA256RSAPkcs   = { CKM_SHA256_RSA_PKCS,  NULL, 0};
    CK_MECHANISM	signvfymechSHA384RSAPkcs   = { CKM_SHA384_RSA_PKCS,  NULL, 0};
    CK_MECHANISM	signvfymechSHA512RSAPkcs   = { CKM_SHA512_RSA_PKCS,  NULL, 0};

    CK_MECHANISM   *pmechsign = NULL;
    CK_MECHANISM   *pmechvfy  = NULL;



    if (strcmp(operation, "SHA512-HMAC") == 0)
    {
        pmechsign = &signmechSHA512hmac;
        pmechvfy  = &vfymechSHA512hmac;
    }
    else if (strcmp(operation, "SHA384-HMAC") == 0)
    {
        pmechsign = &signmechSHA384hmac;
        pmechvfy  = &vfymechSHA384hmac;
    }
    else if (strcmp(operation, "SHA224-HMAC") == 0)
    {
        pmechsign = &signmechSHA224hmac;
        pmechvfy  = &vfymechSHA224hmac;
    }
    else if (strcmp(operation, "SHA1-HMAC") == 0)
    {
        pmechsign = &signmechSHA1hmac;
        pmechvfy  = &vfymechSHA1hmac;
    }
    else if (strcmp(operation, "SHA256-HMAC") == 0)
    {
        pmechsign = &signmechSHA256hmac;
        pmechvfy  = &vfymechSHA256hmac;
    }
    else if (strcmp(operation, "SHA1-RSA") == 0)
    {
        pmechsign = &signvfymechSHA1RSAPkcs;
        pmechvfy  = &signvfymechSHA1RSAPkcs;
    }
    else if (strcmp(operation, "SHA256-RSA") == 0)
    {
        pmechsign = &signvfymechSHA256RSAPkcs;
        pmechvfy  = &signvfymechSHA256RSAPkcs;
    }
    else if (strcmp(operation, "SHA384-RSA") == 0)
    {
        pmechsign = &signvfymechSHA384RSAPkcs;
        pmechvfy  = &signvfymechSHA384RSAPkcs;
    }
    else if (strcmp(operation, "SHA512-RSA") == 0)
    {
        pmechsign = &signvfymechSHA512RSAPkcs;
        pmechvfy  = &signvfymechSHA512RSAPkcs;
    }
    else
    {
        pmechsign = &signmechSHA256hmac;
        pmechvfy  = &vfymechSHA256hmac;
    }

    if (filename == NULL)
    {
        printf("Plain Text Default: \n");
        dumpHexArray(defPlaintextMsg, plaintextLen);
        rc = signBlock(hSession, pmechsign, (CK_BYTE *)defPlaintextMsg, plaintextLen, &pSignBuf, &signLen);

        if (rc == CKR_OK)
        {
            printf("Successful signing of plain text message.\n");
            rc = verifyBlock(hSession, pmechvfy, (CK_BYTE *)defPlaintextMsg, plaintextLen, pSignBuf, signLen);
        }

#ifdef DIGESTKEY_VERIFY
        rc1 = computeDigest(hSession, pmech, (CK_BYTE *)defPlaintextMsg, plaintextLen, &pDigestBuf, &digestLen);
        if (rc1 != CKR_OK || rc != CKR_OK || signLen != digestLen)
        {
            printf("signature/digestkey mismatch for file %s.", filename);
            return CKR_FUNCTION_FAILED;
        }
        cmp = !memcmp(pDigestBuf, pSignBuf, signLen);
        printf("signatureLen = digestLen: %d == %d\n", (int) signLen, (int) digestLen);
        printf("signature = digestkey: %d\n", cmp ? 1 : 0);
#endif
        if (pSignBuf)
        {
            free (pSignBuf);
            pSignBuf = NULL;
        }
    }
    else
    {
        fp_read = strcmp(filename, "-") == 0 ? stdin : fopen(filename, "r");
        if (!fp_read)
        {
            printf("Fail to open file %s.", filename);
            return CKR_FUNCTION_FAILED;
        }

        if(signature_file != NULL)
        {
            fp_write = fopen(signature_file, "w");

            if(!fp_write)
            {
                printf("Fail to open file %s.", signature_file);
                if(fp_read)
                    fclose(fp_read);
                return CKR_FUNCTION_FAILED;
            }
        }
        else
        {
            fp_write = stdout;
        }

        do
        {

            pBuf = (CK_BYTE *)calloc( 1, sizeof(CK_BYTE) * bf_len);
            if(pBuf)
            {
                readlen = (ssize_t)fread(pBuf, sizeof(CK_BYTE), READ_BLK_LEN, fp_read);
            }

            if(readlen > 0 && pBuf)
            {
                pSignBuf = NULL;
                rc = signBlock(hSession, pmechsign, (CK_BYTE *)defPlaintextMsg, plaintextLen, &pSignBuf, &signLen);

                if (rc == CKR_OK)
                {
                    rc = verifyBlock(hSession, pmechvfy, (CK_BYTE *)defPlaintextMsg, plaintextLen, pSignBuf, signLen);
                }

#ifdef DIGESTKEY_VERIFY
                pDigestBuf = NULL;
                rc1 = computeDigest(hSession, pmech, (CK_BYTE *)defPlaintextMsg, plaintextLen,
                                    &pDigestBuf, &digestLen);
                if (rc1 != CKR_OK || rc != CKR_OK || signLen != digestLen)
                {
                    printf("signature/digestkey mismatch for file %s.", filename);
                    return CKR_FUNCTION_FAILED;
                }
                cmp = !memcmp(pDigestBuf, pSignBuf, signLen);
                printf("signatureLen = digestLen: %d == %d\n", (int) signLen, (int) digestLen);
                printf("signature = digestkey: %d\n", cmp ? 1 : 0);
                assert(pDigestBuf);
                assert(digestLen);
#endif
#if 0
                rc = computeDigest(hSession, pmech, pBuf, (unsigned int)readlen, &pDigestBuf, &digestLen);
#endif
                assert(pSignBuf);
                assert(signLen);
                assert(fp_write);
                if(rc == CKR_OK && fp_write && pSignBuf)
                {
                    size_t n = fwrite(pSignBuf, 1, signLen, fp_write);
                    if (n != signLen)
                    {
                        fprintf(stderr, "Digest Error: fwrite pSignBuf failed.\n");
                    }
                }
                else if(rc != CKR_OK)
                {
                    fprintf(stderr, "Digest Error: rc=%d.\n", (int)rc);
                    fprintf(stderr, "PlainText: %s\n", (char *)pBuf);
                    errorCountDigest++;
                }

#ifdef DIGESTKEY_VERIFY
                if (pDigestBuf)
                {
                    free (pDigestBuf);
                    pDigestBuf = NULL;
                }
#endif
                if (pSignBuf)
                {
                    free (pSignBuf);
                    pSignBuf = NULL;
                }
                memset(pBuf, 0, readlen);
            }

            if(pBuf)
            {
                free (pBuf);
                pBuf = NULL;
            }
        }
        while (readlen == READ_BLK_LEN);

        if(pBuf)
        {
            free (pBuf);
            pBuf = NULL;
        }
    }

    if(fp_read && fp_read != stdin)
        fclose(fp_read);

    if(fp_write)
        fclose(fp_write);

    return rc;
}

void SignVerifyUsage()
{
    printf("Usage: pkcs11_sample_sign_verify -p pin [-s slotID] [-g gen_key_action] [-K] [-k keyName] [-op opaqueobjectname] [-q opaquefilename] [-a alias] [-m module_path] [-o operation] [-f input_file_name] [-d signature_file_name] [-h header_version]\n");
    printf("       operation     ...SHA256-HMAC (default) or SHA384-HMAC or SHA512-HMAC or SHA224-HMAC or\n");
    printf("                        SHA1-RSA or SHA256-RSA or SHA384-RSA or SHA512-RSA\n");
    printf("       -K            ...create a key with well-known key bytes on the Key Manager (only available for SHA256-HMAC)\n");
    printf("       header_version...v2.1 or v2.7\n");
    exit(2);
}

int
readOpaqueObject(const char *filename, char *oo, int len)
{
    int bytes = -1;
    FILE *in = NULL;

    if (oo == NULL || filename == NULL || len < 8000)
    {
        return -1;
    }
    in = fopen(filename, "r");
    if (in)
    {
        bytes = (int)fread(oo, 1, len, in);
        fclose(in);
    }
    return bytes;
}

/*
 ************************************************************************
 * Function: main
 ************************************************************************
 */
#ifdef THALES_CLI_MODE
int signVerifySample (int argc, char* argv[])
#else
int main(int argc, char* argv[])
#endif
{
    CK_RV rc;
    char *objLabel = NULL;
    char *pin = NULL;
    char *libPath = NULL;
    char *foundPath = NULL;
    int slotId = 0;
    char *operation = "SHA256-HMAC";
    char *filename = NULL;
    char *signature_file = "signature.out";
    char *keyAlias = NULL;
    int   c;
    extern char *optarg;
    extern int optind;
    int loggedIn = 0;
    int createkey = 0;
    int failed = 0;
    int key_size = 32;
    char *opqfile = NULL;
    char opqbuf[8*1024];
    int opqlen = 0;

    int       genAction = 3;
    CK_BBOOL  bOpaque = CK_FALSE;
    unsigned long lifespan = 0;

    char *header_version = NULL; /* NULL, v2.1, v2.7 allowed */

    optind = 1; //resets optind to 1 to call getopt() multiple times in sample_cli

    while ((c = newgetopt(argc, argv, "h:p:k:m:op:q:f:i:s:c:r:d:g:a:z:K")) != EOF)
        switch (c)
        {
        case 'p':
            pin = optarg;
            break;
        case 'K':
            createkey = 1;
            break;
        case 'k':
            objLabel = optarg;
            break;
        case 'm':
            libPath = optarg;
            break;
        case 's':
            slotId = atoi(optarg);
            break;
        case 'o':
            operation = optarg;
            if(strstr(operation, "RSA"))
            {
                bAsymKey = CK_TRUE;
            }
            break;
        case op:
            bOpaque = CK_TRUE;
            objLabel = optarg;
            break;
        case 'q':
            opqfile = optarg;
            break;
        case 'f':
            filename = optarg;
            break;
        case 'd':
            signature_file = optarg;
            break;
        case 'a':
            keyAlias = optarg;
            break;
        case 'g':
            genAction = atoi(optarg);
            break;
        case 'z':
            key_size = atoi(optarg);
            break;
        case ls:
            lifespan = (unsigned long)atoi(optarg);
            break;
        case 'h':
            header_version = optarg;
            break;
        case '?':
        default:
            SignVerifyUsage();
            break;
        }

    if ( (NULL == pin) || (NULL == objLabel) || (createkey&&strcmp(operation, "SHA256-HMAC")) )
    {
        /* -K option works only with SHA256-HMAC */
        SignVerifyUsage();
    }

    if ( (strcmp(operation, "SHA512-HMAC")) && (strcmp(operation, "SHA384-HMAC")) && (strcmp(operation, "SHA224-HMAC")) &&
         (strcmp(operation, "SHA256-HMAC")) && (strcmp(operation, "SHA1-RSA")) && (strcmp(operation, "SHA256-RSA")) && (strcmp(operation, "SHA384-RSA")) &&
         (strcmp(operation, "SHA512-RSA")) )
    {
        printf("Error: Invalid operation provided.\n");
        SignVerifyUsage();
    }

    printf("Begin Sign/Verify Message sample.\n");

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
            failed++;
            break;
        }

        printf("Done initializing PKCS11 library \n Initializing slot list\n");
        rc = initSlotList();
        if (rc != CKR_OK)
        {
            fprintf(stderr, "FAIL: Unable to initialize Slot List. \n");
            failed++;
            break;
        }

        printf("Done initializing Slot List. \n Opening session and logging in ...\n");
        rc = openSessionAndLogin(pin, slotId);
        if (rc != CKR_OK)
        {
            fprintf(stderr, "FAIL: Unable to open session and login.\n");
            failed++;
            break;
        }
        loggedIn = 1;
        printf("Successfully logged in. \n");

        if (createkey && objLabel)
        {
            rc = createObject(objLabel);
            if (!rc) printf("Key creation failed\n");
        }

        printf("Successfully logged in. \n Looking for key \n");

        if(bAsymKey == CK_FALSE)
        {
            rc = findKey(objLabel, keyIdLabel, bOpaque==CK_TRUE ? CKO_THALES_OPAQUE_OBJECT : CKO_SECRET_KEY, &hGenKey);

            if (CK_INVALID_HANDLE == hGenKey)
            {
                if (bOpaque)
                {
                    if (opqfile == NULL)
                    {
                        printf("Error: opaque object file must be specified\n");
                        break;
                    }
                    printf("Opaque object does not exist, creating...\n");
                    opqlen = readOpaqueObject(opqfile, opqbuf, sizeof (opqbuf));
                    if (opqlen <= 0)
                    {
                        printf("unable to read obaque object\n");
                        break;
                    }

                    rc = createOpaque(objLabel, opqbuf, opqlen);
                    if (rc != CKR_OK)
                    {
                        printf("create opaque object failure: rc:%lu\n", rc);
                        break;
                    }
                    printf("Successfully created opaque object %s.\n", objLabel);

                    rc = findKey(objLabel, keyIdLabel, CKO_THALES_OPAQUE_OBJECT, &hGenKey);
                    if (rc != CKR_OK)
                    {
                        printf("[%s:%d]:: findkey failure: rc:%lu\n", __FUNCTION__, __LINE__, rc);
                        break;
                    }
                }
                else
                {
                    printf("Key does not exist, creating key... Creating key \n");
                    rc = createKey(objLabel, keyAlias, genAction, lifespan, key_size);
                    if (rc != CKR_OK)
                    {
                        break;
                    }
                    printf("Successfully created key.\n");
                }
            }
            else
            {
                printf("Successfully found key.\n");
            }
        }
        else
        {
            rc = findKey(objLabel, keyIdLabel, CKO_PUBLIC_KEY, &hPubKey);
            if (rc != CKR_OK)
            {
                fprintf(stderr, "FAIL: Unable to find public key: %s\n", objLabel);
                break;
            }

            rc = findKey(objLabel, keyIdLabel, CKO_PRIVATE_KEY, &hPrivKey);
            if (rc != CKR_OK)
            {
                fprintf(stderr, "FAIL: Unable to find private key: %s\n", objLabel);
                break;
            }

            if (CK_INVALID_HANDLE == hPubKey || CK_INVALID_HANDLE == hPrivKey)
            {
                fprintf(stderr, "FAIL: Unable to find public or private key: %s\n", objLabel);
                break;
            }
            else
            {
                printf("Successfully found public/private key %s.\n", objLabel);
            }
        }

        rc = signVerifyFile(operation, filename, signature_file, header_version);
        if (rc != CKR_OK)
        {
            failed++;
            break;
        }
        printf("Successfully verified signature\n");
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
    printf("End sign verify sample.\n");
    fflush(stdout);
    return failed;
}
