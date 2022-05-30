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
 * File: pkcs11_sample_digest.c
 ***************************************************************************
 ***************************************************************************
 * This file demonstrates the following
 * 1. Initialization
 * 2. Creating a connection and logging in.
 * 3. Creating a symmetric key on the Key Manager for MAC'ing
 * 4. Compute the digest of HMAC for a given message
 * 5. Clean up.
 */

/*
   pkcs11_sample_digest.c
 */

#include "pkcs11_sample_digest.h"
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
CK_BYTE	defPlainTextDigest[80] = "\xef\xbb\xbf\x53\x65\x63\x74\x69\x6f\x6e\x0d\x0a\x45\x6e\x64\x47\x6c\x6f\x62\x61\x6C\x0D\x0A"; /* 23 characters */
unsigned plaintextdigestlen=23;
int     errorCountDigest = 0;


ssize_t getline_w(char **lineptr, size_t *n, FILE *stream)
{
    char *bufptr = NULL;
    char *p = bufptr;
    size_t size = 0;
    int c;
    long len;

    if (lineptr == NULL)
    {
        return -1;
    }
    if (stream == NULL)
    {
        return -1;
    }
    if (n == NULL)
    {
        return -1;
    }
    bufptr = *lineptr;
    size = *n;

    c = fgetc(stream);
    if (c == EOF)
    {
        return -1;
    }
    if (bufptr == NULL)
    {
        bufptr = (char *)malloc(READ_BLK_LEN);
        if (bufptr == NULL)
        {
            return -1;
        }
        size = READ_BLK_LEN;
    }
    p = bufptr;
    while(c != EOF)
    {
        if ((p - bufptr) > (int)(size - 1))
        {
            len = (long)(p - bufptr);
            size += READ_BLK_LEN;
            bufptr = (char *)realloc(bufptr, size);
            if (bufptr == NULL)
            {
                return -1;
            }
            p = bufptr + len;
        }
        *p++ = (char)c;
        if (c == '\n')
        {
            break;
        }
        c = fgetc(stream);
    }

    *p = '\0';
    *lineptr = bufptr;
    *n = size;

    return (int)(p - bufptr);
}


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
    case CKM_SHA224_HMAC:
    case CKM_SHA384_HMAC:
    case CKM_SHA512_HMAC:
        rc = FunctionListFuncPtr->C_DigestKey(hSess, hGenKey);
        if (rc != CKR_OK)
        {
            fprintf(stderr, "FAIL: call to C_DigestKey() failed.\n");
            return rc;
        }
        else
            fprintf(stderr, "C_DigestKey() successfully digested a key.\n");
        break;
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

/*
 ************************************************************************
 * Function: computeDigest
 * This function takes a given message and computes the correponding digest,
 * and HMAC it using a key if available
 ************************************************************************
 * Parameters: operation ... SHA256, SHA384, SHA512 and SHA256-HMAC
 * Returns: CK_RV
 ************************************************************************
 */
static CK_RV computeDigestFile(char *operation, char *filename, char *digest_file /*, char *expected*/)
{
    CK_BYTE         *pBuf = NULL;
    CK_BYTE         *pDigestBuf = NULL;
    FILE            *fp_read = NULL;
    FILE            *fp_write = NULL;
    ssize_t         readlen = 0;
    size_t          bf_len = READ_BLK_LEN;
    CK_ULONG        digestLen;
    CK_RV           rc = CKR_OK;

    /* C_Digest */
    CK_MECHANISM	mechSHA256 = { CKM_SHA256, NULL, 0};
    CK_MECHANISM	mechSHA256hmac = { CKM_SHA256_HMAC, NULL, 0};
    CK_MECHANISM	mechSHA384 = { CKM_SHA384, NULL, 0};
    CK_MECHANISM	mechSHA384hmac = { CKM_SHA384_HMAC, NULL, 0};
    CK_MECHANISM	mechSHA512 = { CKM_SHA512, NULL, 0};
    CK_MECHANISM	mechSHA512hmac = { CKM_SHA512_HMAC, NULL, 0};
    CK_MECHANISM	mechSHA224 = { CKM_SHA224, NULL, 0};
    CK_MECHANISM	mechSHA224hmac = { CKM_SHA224_HMAC, NULL, 0};
    CK_MECHANISM  *pmech = NULL;

    /*(void) expected;*/

    int default_case = 0;
    if (strcmp(operation, "SHA512") == 0)
    {
        pmech = &mechSHA512;
    }
    else if (strcmp(operation, "SHA512-HMAC") == 0)
    {
        pmech = &mechSHA512hmac;
    }
    else if (strcmp(operation, "SHA384") == 0)
    {
        pmech = &mechSHA384;
    }
    else if (strcmp(operation, "SHA384-HMAC") == 0)
    {
        pmech = &mechSHA384hmac;
    }
    else if (strcmp(operation, "SHA224") == 0)
    {
        pmech = &mechSHA224;
    }
    else if (strcmp(operation, "SHA224-HMAC") == 0)
    {
        pmech = &mechSHA224hmac;
    }
    else if (strcmp(operation, "SHA256-HMAC") == 0)
    {
        pmech = &mechSHA256hmac;
    }
    else if (strcmp(operation, "SHA256") == 0)
    {
        pmech = &mechSHA256;
    }
    else
    {
        default_case  = 1;
        pmech = &mechSHA256;
        printf("Operation[%s] doesnt exist, Using default operation SHA256\n", operation);
    }
    if(!default_case)
        printf("operation to be used: %s\n", operation);
    if (filename == NULL)
    {
        printf("Plain Text Default: \n");
        dumpHexArray(defPlainTextDigest, plaintextdigestlen);
        rc = computeDigest(hSession, pmech, (CK_BYTE *)defPlainTextDigest, plaintextdigestlen, &pDigestBuf, &digestLen);
    }
    else
    {
        fp_read = strcmp(filename, "-") == 0 ? stdin : fopen(filename, "r");
        if (!fp_read)
        {
            printf("Fail to open file %s.", filename);
            return CKR_FUNCTION_FAILED;
        }

        if(digest_file != NULL)
        {
            fp_write = fopen(digest_file, "w");

            if(!fp_write)
            {
                printf("Fail to open file %s.", digest_file);
                if(fp_read) 	fclose(fp_read);
                return CKR_FUNCTION_FAILED;
            }
        }
        else
        {
            fp_write = stdout;
        }

        do
        {

            pBuf = (CK_BYTE *)calloc( 1, sizeof(CK_BYTE) * bf_len );
            if(pBuf)
            {
                readlen = (ssize_t)fread(pBuf, sizeof(CK_BYTE), READ_BLK_LEN, fp_read);
            }

            if(readlen > 0 && pBuf)
            {
                pDigestBuf = NULL;
                rc = computeDigest(hSession, pmech, pBuf, (unsigned int)readlen, &pDigestBuf, &digestLen);

                assert(fp_write);
                assert(pDigestBuf);
                assert(digestLen);
                if(rc == CKR_OK && fp_write && pDigestBuf)
                {
                    size_t n = fwrite(pDigestBuf, 1, digestLen, fp_write);
                    if (n != digestLen)
                    {
                        fprintf(stderr, "Digest Error: fwrite pDigestBuf failed.\n");
                    }
                }
                else if(rc != CKR_OK)
                {
                    fprintf(stderr, "Digest Error: rc=%d.\n", (int)rc);
                    fprintf(stderr, "PlainText: %s\n", (char *)pBuf);
                    errorCountDigest++;
                }

                if (pDigestBuf)
                {
                    free (pDigestBuf);
                    pDigestBuf = NULL;
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

    if (pDigestBuf)
    {
        free (pDigestBuf);
        pDigestBuf = NULL;
    }

    if(fp_read && fp_read != stdin)
        fclose(fp_read);

    if(fp_write)
        fclose(fp_write);

    return rc;
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



void digestUsage()
{
    printf("Usage: pkcs11_sample_digest -p pin [-s slotID] [-g gen_key_action] [-K] [-k keyName] [-a alias] [-m module_path] [-o operation] [-f input_file_name] [-d digest_file_name] [-q opaque_object_file] [-Q]\n");
    printf("       operation      ... SHA256 (default) or SHA224 or SHA384 or SHA512 \n");
    printf("                          or SHA224-HMAC or SHA256-HMAC or SHA384-HMAC or SHA512-HMAC\n");
    printf("       -K             ... create a key with well-known key bytes on the Key Manager (HMAC functions only)\n");
    printf("       -Q             ... use an opaque object previously stored on Key Manager without passing a binary file");
    printf("       gen_key_action ... versionCreate: 0, nonVersionCreate: 3. Note that neither key rotation nor migration is supported in this sample program.\n");
    exit(2);
}


/*
 ************************************************************************
 * Function: main
 ************************************************************************
 */
#ifdef THALES_CLI_MODE
int digestSample (int argc, char* argv[])
#else
int main(int argc, char* argv[])
#endif
{
    CK_RV rc;
    char *keyLabel = NULL;
    char *pin = NULL;
    char *libPath = NULL;
    char *foundPath = NULL;
    int slotId = 0;
    char *operation = "SHA256";
    char *filename = NULL;
    char *digest_file = "digest.out";
    char *keyAlias = NULL;
    char *oofile = NULL;
    char oo[8000];
    int oolen = 0;
    int   c;
    extern char *optarg;
    extern int optind;
    int loggedIn = 0;
    int createkey = 0;
    int failed = 0;
    int use_key = 0;
    int use_oo = 0;
    int genAction = 0; /* versionCreate */
    int key_size = 32;
    unsigned long lifespan = 0;

    optind = 1; //resets optind to 1 to call getopt() multiple times in sample_cli

    while ((c = newgetopt(argc, argv, "p:Kk:m:s:z:o:f:d:a:g:q:Q")) != EOF)
        switch (c)
        {
        case 'p':
            pin = optarg;
            break;
        case 'K':
            createkey = 1;
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
        case 'z':
            key_size = atoi(optarg);
            break;
        case 'o':
            operation = optarg;
            break;
        case 'f':
            filename = optarg;
            break;
            /*case 'e':
                expected = optarg;
                break;*/
        case 'd':
            digest_file = optarg;
            break;
        case 'a':
            keyAlias = optarg;
            break;
        case 'g':
            genAction = atoi(optarg);
            if (genAction==0 || genAction==3) ;
            else digestUsage();
            break;
        case 'q':
            oofile = optarg;
            use_oo = 1;
            break;
        case 'Q':
            use_oo = 1;
            break;
        case ls:
            lifespan = (unsigned long)atoi(optarg);
            break;
        case '?':
        default:
            digestUsage();
            break;
        }

    if (pin == NULL)
    {
        digestUsage();
    }

    if (strcmp(operation, "SHA256-HMAC") == 0 || strcmp(operation, "SHA224-HMAC") == 0 || strcmp(operation, "SHA512-HMAC") == 0 || strcmp(operation, "SHA384-HMAC") == 0 )
    {
        if (!use_oo)
            use_key = 1;
    }

    if ((use_key || use_oo) && ((NULL == pin) || (NULL == keyLabel)))
    {
        digestUsage();
    }
    if ((optind < argc))
    {
        digestUsage();
    }

    printf("Begin Digest Message sample.\n");

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

        // Opaque object creation. If file name is specified then read it from file and
        // create on Key Manager.
        // otherwise should be searched and retrieved from Key Manager in the same way as
        // other keys are retrieved
        if (use_oo)
        {
            if (createkey)
            {
                printf("unable to handle conflicting -K and -q options\n");
                break;
            }
            if (oofile)
            {
                printf("Ready to read opaque object from file %s\n", oofile);
                oolen = readOpaqueObject(oofile, oo, sizeof (oo));
                if (oolen <= 0)
                {
                    printf("unable to read opaque object\n");
                    break;
                }
                printf("Looking for opaque object with label %s\n", keyLabel);
                rc = findKey(keyLabel, keyIdLabel, CKO_THALES_OPAQUE_OBJECT, &hGenKey);
                if (rc == CKR_OK && hGenKey != CK_INVALID_HANDLE)
                {
                    fprintf(stderr, "Found: opaque object with same name already exist.\n");
                    rc = deleteKey(hGenKey, CK_FALSE);
                    if (rc != CKR_OK)
                    {
                        fprintf(stderr, "FAIL: deleteKey with unexpected result\n");
                        break;
                    }
                    else
                    {
                        printf("PASS: Successfully found and deleted %s. \n", keyLabel);
                    }
                }
                printf("Opaque object does not exist on Key Manager, creating...\n");
                rc = createOpaque(keyLabel, oo, oolen);
                if (rc != CKR_OK)
                    break;
                printf("Successfully created opaque object. Now re-reading from Key Manager\n");
            }
            printf("Looking for opaque object with label %s\n", keyLabel);
            rc = findKey(keyLabel, keyIdLabel, CKO_THALES_OPAQUE_OBJECT, &hGenKey);
            if (CK_INVALID_HANDLE == hGenKey || rc != CKR_OK)
            {
                printf(" Cannot find opaque object on the Key Manager\n");
                break;
            }
        }
        else if (use_key)
        {
            if (createkey && keyLabel)
            {
                rc = createObject(keyLabel);
                if (!rc) printf("Key creation failed\n");
            }

            printf("Successfully logged in. \n Looking for key \n");
            rc = findKey(keyLabel, keyIdLabel, CKO_SECRET_KEY, &hGenKey);
            if (CK_INVALID_HANDLE == hGenKey)
            {
                printf("Key does not exist, creating key... Creating key \n");
                rc = createKey(keyLabel, keyAlias, genAction, lifespan, key_size);
                if (rc != CKR_OK)
                {
                    break;
                }
                printf("Successfully created key.\n");
            }
            printf("Successfully found key.\n");
        }

        rc = computeDigestFile(operation, filename, digest_file /*, expected*/);
        if (rc != CKR_OK)
        {
            failed++;
            break;
        }
        printf("Successfully computed digest\n");
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
    printf("End Digest Message sample.\n");
    fflush(stdout);
    return failed;
}
