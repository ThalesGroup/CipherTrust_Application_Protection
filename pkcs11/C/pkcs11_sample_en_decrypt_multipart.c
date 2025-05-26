
/*************************************************************************
**                                                                      **
** Sample code is provided for educational purposes.                    **
** No warranty of any kind, either expressed or implied by fact or law. **
** Use of this item is not restricted by copyright or license terms.    **
**                                                                      **
**************************************************************************/

/*
 ***************************************************************************
 * File: pkcs11_sample_en_decrypt_multipart.c
 ***************************************************************************
 ***************************************************************************
 * This file demonstrates the following
 * 1. Initialization
 * 2. Creating a connection and logging in.
 * 3. Find or Create the symmetric key
 * 4. Using the symmetric key to encrypt file content
 * 5. Using the symmetric key to decrypt the encrypted file content.
 * 6. Compare the original and decrypted file content.
 * 7. Clean up.
 */

#include "pkcs11_sample_en_decrypt_multipart.h"
#include "pkcs11_sample_helper.h"

/*
 ***************************************************************************
 * Static Local Variables
 **************************************************************************
 */

#define MAX_SIZE_OF_KEY 128
#define AES_BLOCK_SIZE 16
#define MAX_FIND_RETURN 1


static const char outfilename[] = "encryptedtext.dat";
static const char outfilename2[] = "decryptedtext.dat";
CK_GCM_PARAMS   gcmParams = {def_gcm_iv, 12, 128, def_aad, 16, 96};


/*
 ************************************************************************
 * Function: encryptAndDecryptFile
 * This function first encrypts the source file using a symmetric key by calling mutli-part encryption functions.
 * which is C_EncryptInit(), C_EncryptUpdte() in  a loop, then C_EncryptFinal() for the last part, and
 * same the encrypted file.
 * After that,  calling multipart decryption functions:
 * which is C_DecryptInit(), and C_DecryptUpdate() in a loop, then C_DecryptFinal() for the last part,
 * and save the decrypted file.
 * Last, compare the contect of the original source file and decrypted file to make sure they are
 * identical.
 ************************************************************************
 * Parameters: none
 * Returns: CK_RV
 ************************************************************************
 */
static CK_RV encryptAndDecryptFile(char *operation, char *infilename, char *header_version)
{
    CK_BYTE		   *plainTextBuf = NULL_PTR;
    CK_ULONG	    plainTextBufferLen = 1024; /* should be a multiple of 16 for compatibility with ECB and CBC modes */

    /* C_Encrypt */
    CK_MECHANISM    mechEncryptionPad = { CKM_AES_CBC_PAD, def_iv, 16 };
    CK_MECHANISM    mechEncryptionCBC = { CKM_AES_CBC    , def_iv, 16 };
    CK_MECHANISM    mechEncryptionECB = { CKM_AES_ECB    , def_iv, 16 };
    CK_MECHANISM    mechEncryptionCTR = { CKM_AES_CTR    , def_iv, 16 };
    CK_MECHANISM    mechEncryptionGCM = { CKM_AES_GCM, &gcmParams, sizeof (CK_GCM_PARAMS) };
    CK_MECHANISM   *pmechEncryption   = &mechEncryptionPad;
    CK_BYTE		   *cipherText = NULL_PTR;
    CK_ULONG		cipherTextLen = 0;
    CK_ULONG        totalcipherTextLen = 0;

    /* For C_Decrypt */
    CK_BYTE*		decryptedText = NULL_PTR;
    CK_ULONG		decryptedTextLen = 0;

    /* CK_BYTE*		lastPartText = NULL_PTR; */
    CK_BBOOL        bCompareResult = CK_TRUE;
    /* General */
    CK_RV rc = CKR_OK;
    int   status;
    FILE *fpin = NULL;
    FILE *fpout = NULL;
    FILE *fpout2 = NULL;
    CK_ULONG  bytesRead = 0;
    CK_ULONG  bytesResult = 0;
    CK_ULONG  bytesResult2 = 0;
    CK_ULONG  encheader=0; /* no header */
    CK_ULONG  decheader=0; /* no header */
    int is_gcm = 0;
    // int tag_len = ((tag_bits & 0x00000007) != 0) ? (tag_bits >> 3) + 1 : (tag_bits >> 3);
    int tag_len = tag_bits >> 3;
    size_t n = 0;

    if (!operation)                     pmechEncryption = &mechEncryptionPad;
    else if (!strcmp(operation, "CTR")) pmechEncryption = &mechEncryptionCTR;
    else if (!strcmp(operation, "ECB")) pmechEncryption = &mechEncryptionECB;
    else if (!strcmp(operation, "CBC")) pmechEncryption = &mechEncryptionCBC;
    else if (!strcmp(operation, "GCM"))
    {
        pmechEncryption = &mechEncryptionGCM;
        is_gcm = 1;
    }
    else                                pmechEncryption = &mechEncryptionPad;

    if (!header_version || strlen(header_version)!=4 || header_version[0]!='v' || header_version[2]!='.') encheader=decheader=0; /* no header */
    else switch(header_version[3])
        {
        case '5':
            encheader=CKM_THALES_V15HDR|CKM_VENDOR_DEFINED;
            decheader=CKM_THALES_ALLHDR|CKM_VENDOR_DEFINED;
            break;
        case '1':
            encheader=CKM_THALES_V21HDR|CKM_VENDOR_DEFINED;
            decheader=CKM_THALES_ALLHDR|CKM_VENDOR_DEFINED;
            break;
        case '7':
            encheader=CKM_THALES_V27HDR|CKM_VENDOR_DEFINED;
            decheader=CKM_THALES_ALLHDR|CKM_VENDOR_DEFINED;
            break;
        default :
            encheader=0; /* no header */
            decheader=0; /* no header */
            break;
        }

    pmechEncryption->mechanism |= encheader;

    do
    {
        fpin = fopen(infilename, "r");
        fpout = fopen(outfilename, "w+b");

        if (fpin == NULL || fpout == NULL)
        {
            printf("File open error.\n");
            break;
        }
        plainTextBuf = (CK_BYTE *)calloc(1, sizeof(CK_BYTE) * plainTextBufferLen);

        if (plainTextBuf == NULL)
        {
            printf("Memory calloc failed for plainTextBuf\n");
            break;
        }

        memset((void *)plainTextBuf, 0, plainTextBufferLen);

        /* if GCM, save space for the tag */
        if (is_gcm && tag_bits > 0)
        {
            n = fwrite(plainTextBuf, sizeof(CK_BYTE), tag_len, fpout);
            if(n != sizeof(CK_BYTE) * tag_len)
            {
                printf("C_EncryptUpdate fwrite cipherText failed\n");
            }
            else
            {
                printf("fwrite reserve space for tag in cipherText file: %d\n", tag_len);
            }
        }

        /* C_EncryptInit */
        rc = FunctionListFuncPtr->C_EncryptInit(
                 hSession,
                 pmechEncryption,
                 hGenKey
             );
        if (rc != CKR_OK)
        {
            printf("C_EncryptInit failed\n");
            break;
        }

        while (!feof(fpin) && !ferror(fpin))
        {
            n = 0;
            bytesResult = (CK_ULONG)fread(plainTextBuf, 1, plainTextBufferLen, fpin);
            printf("%d bytes read from input file\n", (int) bytesResult);
            if ((int) bytesResult <= 0) break;
            bytesRead += bytesResult;

            if (bytesResult == 0)
                break;

            cipherTextLen = 0; /* this is the preferred method of asking for the estimated buffer length */
            rc = FunctionListFuncPtr->C_EncryptUpdate(
                     hSession,
                     plainTextBuf, bytesResult,
                     NULL, &cipherTextLen
                 );
            if (rc != CKR_OK)
            {
                printf("C_EncryptUpdate failed\n");
                break;
            }
            else printf("test   call to C_EncryptUpdate(): cipherTextLen returned as %lu\n", cipherTextLen);

            cipherText = (CK_BYTE *)calloc(1, sizeof(CK_BYTE) * cipherTextLen);
            memset((void *)cipherText, 0, cipherTextLen);

            rc = FunctionListFuncPtr->C_EncryptUpdate(
                     hSession,
                     plainTextBuf, bytesResult,
                     cipherText, &cipherTextLen
                 );
            if (rc != CKR_OK)
            {
                printf("C_EncryptUpdate failed\n");
                break;
            }
            else printf("actual call to C_EncryptUpdate(): cipherTextLen returned as %lu\n", cipherTextLen);
            totalcipherTextLen += cipherTextLen;
            memset((void *)plainTextBuf, 0, plainTextBufferLen);
            n = fwrite(cipherText, sizeof(CK_BYTE), cipherTextLen, fpout);
            if(n != sizeof(CK_BYTE) * cipherTextLen)
            {
                printf("C_EncryptUpdate fwrite cipherText failed\n");
            }
            free(cipherText);
            cipherText = NULL_PTR;
        }

        if (rc != CKR_OK)
        {
            /* break out of outer while loop */
            break;
        }

        /* pass in NULL pointer to get output buffer size */
        rc = FunctionListFuncPtr->C_EncryptFinal(
                 hSession,
                 NULL, &cipherTextLen
             );
        if (rc != CKR_OK)
        {
            printf("C_EncryptFinal failed\n");
            break;
        }

        cipherText = (CK_BYTE *)calloc(1, sizeof(CK_BYTE) * cipherTextLen);
        if (NULL == cipherText)
        {
            rc = CKR_HOST_MEMORY;
            break;
        }
        memset((void *)cipherText, 0, cipherTextLen);

        rc = FunctionListFuncPtr->C_EncryptFinal(
                 hSession,
                 cipherText, &cipherTextLen
             );
        if (rc != CKR_OK)
        {
            printf("C_EncryptFinal failed\n");
            break;
        }
        else
        {
            printf("C_EncryptFinal Succeed, will write last %ld bytes to the encrypted file.\n", (long)cipherTextLen);
            totalcipherTextLen += cipherTextLen;
            printf("Total cipher text length: %lu bytes - last part length = %lu\n", totalcipherTextLen, cipherTextLen);
        }

        if (is_gcm && cipherTextLen != 0)
        {
            if ((CK_ULONG) tag_len > cipherTextLen)
            {
                printf("C_EncryptFinal failed for GCM: %d > %lu\n", tag_len, cipherTextLen);
                cipherTextLen = 0;
            }
            else
            {
                cipherTextLen -= (CK_ULONG) tag_len;
                totalcipherTextLen -= (CK_ULONG) tag_len;
            }
        }
        if (cipherTextLen != 0)
        {
            n = fwrite(cipherText, sizeof(CK_BYTE), cipherTextLen, fpout);
            if(n != sizeof(CK_BYTE) * cipherTextLen)
            {
                printf("C_EncryptFinal fwrite cipherText failed\n");
            }
        }
        if (is_gcm)
        {
            int i = 0;

            printf("fseek to beginning of file to write tag with length = %d\n", tag_len);

            if (fseek(fpout, 0L, SEEK_SET) != 0)
            {
                printf("fseek failed to write tag (%d)\n", errno);
            }
            n = fwrite(cipherText + cipherTextLen, sizeof(CK_BYTE), tag_len, fpout);
            if(n != sizeof(CK_BYTE) * tag_len)
            {
                printf("fwrite at offset 0: failed to write tag (%d)\n", errno);
            }
            printf("Wrote tag = ");
            for (; i < tag_len; i++)
            {
                printf("%02x", cipherText[cipherTextLen + i]);
            }
            printf("\n");
        }
        free(cipherText);
        cipherText = NULL_PTR;

        fflush(fpout);
        fclose(fpout);
        fclose(fpin);

        fpout = fopen(outfilename, "r+b");
        fpout2 = fopen(outfilename2, "w+");

        if (fpout == NULL || fpout2 == NULL)
        {
            printf("File open error.\n");
            break;
        }
        fseek(fpout, 0, SEEK_SET);

        /*C_Decrypt*/
        pmechEncryption->mechanism |= decheader; /* this sets the ALLHDR bitmask, as required */
        rc = FunctionListFuncPtr->C_DecryptInit(
                 hSession,
                 pmechEncryption,
                 hGenKey
             );
        if (rc != CKR_OK)
        {
            printf("C_DecryptInit failed\n");
            break;
        }

        cipherTextLen = plainTextBufferLen;
        cipherText = (CK_BYTE *)calloc(1, sizeof(CK_BYTE)* cipherTextLen);
        if (NULL == cipherText)
        {
            rc = CKR_HOST_MEMORY;
            break;
        }
        memset((void *)cipherText, 0, cipherTextLen);
        if (!cipherText)
        {
            rc = CKR_HOST_MEMORY;
            break;
        }

        bytesRead = 0;
        while (!feof(fpout) && !ferror(fpout))
        {
            n = 0;
            bytesResult = (CK_ULONG)fread(cipherText, 1, cipherTextLen, fpout);

            if (bytesRead == 0 && is_gcm)
            {
                int i;
                printf("read tag = ");
                for (i = 0; i < tag_len; i++)
                {
                    printf("%02x", cipherText[i]);
                }
                printf("\n");
            }
            bytesRead += bytesResult;

            if (bytesResult == 0)
                break;

            decryptedTextLen = 0; /* this is the preferred method for getting the estimated buffer size */
            rc = FunctionListFuncPtr->C_DecryptUpdate(
                     hSession,
                     cipherText, bytesResult,
                     NULL, &decryptedTextLen
                 );
            if (rc != CKR_OK)
            {
                printf("C_DecryptUpdate failed (1st of 2)\n");
                break;
            }

            /* allocate output buffer for decrypted Text */
            decryptedText = (CK_BYTE *)calloc(1, sizeof(CK_BYTE)* decryptedTextLen);
            memset(decryptedText, 0, decryptedTextLen);
            if (!decryptedText)
            {
                rc = CKR_HOST_MEMORY;
                break;
            }

            rc = FunctionListFuncPtr->C_DecryptUpdate(
                     hSession,
                     cipherText, bytesResult,
                     decryptedText, &decryptedTextLen
                 );
            if (rc != CKR_OK)
            {
                printf("C_DecryptUpdate failed (2nd of 2)\n");
                break;
            }
            else
            {
                printf("read and decrypted %u bytes\n", (unsigned int) decryptedTextLen);
                printf("contents = %c%c%c%c...%c%c%c%c\n", decryptedText[0], decryptedText[1],
                       decryptedText[2], decryptedText[3], decryptedText[decryptedTextLen - 4],
                       decryptedText[decryptedTextLen - 3], decryptedText[decryptedTextLen - 2],
                       decryptedText[decryptedTextLen - 1]);
            }

            n = fwrite(decryptedText, sizeof(CK_BYTE), decryptedTextLen, fpout2);
            if(n != sizeof(CK_BYTE) * decryptedTextLen)
            {
                printf("C_DecryptUpdate fwrite cipherText failed\n");
            }
            free(decryptedText);
            decryptedText = NULL_PTR;

            cipherTextLen = plainTextBufferLen;
            memset((void *)cipherText, 0, cipherTextLen);
        }

        if (rc != CKR_OK)
        {
            break;
        }

        /* pass in NULL pointer to get output buffer size */
        rc = FunctionListFuncPtr->C_DecryptFinal(
                 hSession,
                 NULL, &decryptedTextLen
             );
        if (rc != CKR_OK)
        {
            printf("C_DecryptFinal failed = 0x%08x\n", (unsigned int) rc);
            break;
        }

        /* allocate output buffer for decrypted Text */
        decryptedText = (CK_BYTE *)calloc(1, sizeof(CK_BYTE)* decryptedTextLen);
        if (NULL == decryptedText)
        {
            rc = CKR_HOST_MEMORY;
            break;
        }
        memset(decryptedText, 0, decryptedTextLen);
        if (!decryptedText)
        {
            rc = CKR_HOST_MEMORY;
            break;
        }

        rc = FunctionListFuncPtr->C_DecryptFinal(
                 hSession,
                 decryptedText, &decryptedTextLen
             );
        if (rc != CKR_OK)
        {
            if (rc == CKR_ENCRYPTED_DATA_INVALID && is_gcm)
            {
                printf("C_DecryptFinal TAG check failed!\n");
            }
            else
            {
                printf("C_DecryptFinal failed = 0x%08x\n", (unsigned int) rc);
            }
            break;
        }
        else
        {
            printf("C_DecryptFinal succeed, got decrypted Text Length: %ld . \n", (long)decryptedTextLen);
        }

        if (decryptedTextLen != 0)
        {
            n = fwrite(decryptedText, sizeof(CK_BYTE), decryptedTextLen, fpout2);
            if(n != sizeof(CK_BYTE) * decryptedTextLen)
            {
                printf("C_DecryptFinal fwrite cipherText failed\n");
            }
            fflush(fpout2);
        }

        if(decryptedText)
        {
            free(decryptedText);
            decryptedText = NULL_PTR;
        }

        fclose(fpout2);
        fclose(fpout);

        fpin = fopen(infilename, "r");
        fpout2 = fopen(outfilename2, "r");

        if (fpin == NULL || fpout2 == NULL)
        {
            printf("File open error.\n");
            break;
        }

        fseek(fpout2, 0, SEEK_SET);
        fseek(fpin, 0, SEEK_SET);

        decryptedText = (CK_BYTE *)calloc(1, sizeof(CK_BYTE)* plainTextBufferLen);
        bytesRead = 0;
        while (!feof(fpin) && !ferror(fpin))
        {
            bytesResult = (CK_ULONG)fread(plainTextBuf, 1, plainTextBufferLen, fpin);
            bytesResult2 = (CK_ULONG)fread(decryptedText, 1, bytesResult, fpout2);

            /* compare the plaintext and decrypted text */
            status = memcmp(plainTextBuf, decryptedText, bytesResult);
            bCompareResult &= (status == 0) && (bytesResult == bytesResult2);
        }

        fclose(fpout2);
        fclose(fpin);

        if (bCompareResult == CK_TRUE)
        {
            printf("Success! PlainText and DecryptedText match! \n");
        }
        else
        {
            printf("Plaintext and Decrypted Text do not match \n");
        }
    }
    while (0);

    /* cleanup and free memory */

    if(cipherText)
    {
        free (cipherText);
        cipherText = NULL;
    }
    if(plainTextBuf)
    {
        free (plainTextBuf);
        plainTextBuf = NULL;
    }
    if(decryptedText)
    {
        free (decryptedText);
        decryptedText = NULL;
    }

    return rc;
}

void enDecryptMultipartUsage()
{
    printf("Usage: pkcs11_sample_en_decrypt_multipart -p pin -s slotID -k keyName [-i {k|m|u}:identifier] -f filename [-m module] [-o operation] [-h header_version]\n");
    printf("-o  operation...CBC_PAD (default) or CTR or ECB or CBC or GCM\n");
    printf("-h  header_version...v1.5 or v2.1 or v.2.7\n");
    printf("-i identifier: one of 'imported key id' as 'k', MUID as 'm', or UUID as 'u'.\n");
    exit (2);
}

/*
 ************************************************************************
 * Function: main
 ************************************************************************
 */
#ifdef THALES_CLI_MODE
int encryptDecryptMultipartSample (int argc, char* argv[])
#else
int main(int argc, char* argv[])
#endif
{
    CK_RV rc;
    char *keyLabel = NULL;
    char *infilename = NULL;
    int slotId = 0;

    char *pin = NULL;
    char *libPath = NULL;
    char *foundPath = NULL;

    char *pKsid = NULL;
    char *operation = NULL;
    int   ksid_type = keyIdLabel;

    int    c;
    int    key_size = 32;
    char *pAad = NULL;
    extern char *optarg;
    extern int optind;

    int loggedIn = 0;
    char *header_version = NULL; /* NULL, v1.5, v2.1, v2.7 allowed */

    optind = 1; /* resets optind to 1 to call getopt() multiple times in sample_cli */

    while ((c = newgetopt(argc, argv, "p:k:f:m:s:h:i:o:z:a:t:")) != EOF)
        switch (c)
        {
        case 'p':
            pin = optarg;
            break;
        case 'k':
            keyLabel = optarg;
            break;
        case 'f':
            infilename = optarg;
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
        case 'i':
            ksid_type = parse_ksid_sel(optarg, &pKsid);
            break;
        case 'o':
            operation = optarg;
            break;
        case 't':
            tag_bits = atoi(optarg);
            gcmParams.ulTagBits = tag_bits;
            break;
        case 'a':
            pAad = optarg;
            aad_length = (CK_ULONG) strlen(optarg) >> 1;
            gcmParams.ulAADLen = aad_length;
            break;
        case 'h':
            header_version = optarg;
            break;
        case '?':
        default:
            enDecryptMultipartUsage();
            break;
        }

    if (pAad)
    {
        int k=0;
        printf("Obtaining GCM AAD from the command line\n");
        for (k=0; k< (int)aad_length; k++)
        {
            char x[3];
            unsigned u;
            x[2]=0;
            x[0]=pAad[k+k];
            x[1]=pAad[k+k+1];
            if (sscanf(x, "%X", &u) < 0)
            {
                printf("Failed to sscan pAad\n");
            }
            def_aad[k] = (CK_BYTE) u;
        }
        gcmParams.pAAD = (CK_BYTE_PTR) pAad;
    }

    if(keyLabel)
    {
        pKsid = keyLabel;
        ksid_type = keyIdLabel;
    }

    if ((NULL == pin) || (NULL == pKsid) || ( NULL == infilename) || (optind < argc))
    {
        enDecryptMultipartUsage();
    }

    printf("Begin Encrypt and Decrypt File sample: ...\n");

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


        printf("Successfully logged in. \n Looking for key %s \n", pKsid);
        rc = findKey(pKsid, ksid_type, CKO_SECRET_KEY, &hGenKey);
        if (CK_INVALID_HANDLE == hGenKey)
        {
            if(keyLabel)
            {
                printf("Key does not exist, creating key... Creating key \n");
                rc = createKeyS(keyLabel, key_size);
                if (rc != CKR_OK)
                {
                    fprintf(stderr, "FAIL: Unable to create key.\n");
                    break;
                }
                printf("Successfully created key.\n");
            }
        }
        printf("Successfully found key.\n");

        rc = encryptAndDecryptFile(operation, infilename, header_version);
        if (rc != CKR_OK) break;
        printf("Successfully encrypted and decrypted\n");

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
    printf("End Encrypt and Decrypt File sample.\n");
    fflush(stdout);
    return rc;
}
