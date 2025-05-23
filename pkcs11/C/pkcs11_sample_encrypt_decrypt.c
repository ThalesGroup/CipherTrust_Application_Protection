/*************************************************************************
**                                                                      **
** Sample code is provided for educational purposes.                    **
** No warranty of any kind, either expressed or implied by fact or law. **
** Use of this item is not restricted by copyright or license terms.    **
**                                                                      **
**************************************************************************/

/*
 ***************************************************************************
 * File: pkcs11_sample_encrypt_decrypt.c
 ***************************************************************************
 ***************************************************************************
 * This file demonstrates the following
 * 1. Initialization
 * 2. Creating a connection and logging in.
 * 3. Creating a symmetric key on the Key Manager
 * 4. Using the symmetric key to encrypt plaintext
 * 5. Using the symmetric key to decrypt ciphertext.
 * 6, Delete key.
 * 7. Clean up.
 */

/*
   pkcs11_sample_encrypt_decrypt.c
 */

#include "pkcs11_sample_encrypt_decrypt.h"
#include "pkcs11_sample_helper.h"
#include <stdio.h>
#include <stdlib.h>
#include <wchar.h>

#ifdef __WINDOWS__

typedef int __ssize_t;
typedef __ssize_t ssize_t;

#else
#endif

#ifdef THALES_CLI_MODE
extern CK_GCM_PARAMS   gcmParams;
#else
CK_GCM_PARAMS   gcmParams = {def_gcm_iv, 12, 128, def_aad, 16, 96};
#endif

/**
 * default data set for GCM only:
	  [Keylen = 128]
	  [IVlen = 96]
	  [PTlen = 128]
	  [AADlen = 160]
	  [Taglen = 96]

	  Key = 70fb02388301f16c4193b0fc70683f3f
	  IV = aec612be7c1ddb659a4b315c
	  PT = 68e6bc0b08b8adbdc00005ae44723c8e
	  AAD = 3859b3c9d0b42d45c43e8ebd4c8cbde1b6eb2106
	  CT = a7c52a23b09062a1fb77d47ff83a114f
	  Tag = 79f91fa572220432ee3a6495
*/

//CK_GCM_PARAMS   gcmParams = {def_gcm_iv, 12, 128, def_aad, 16, 96};
CK_OBJECT_HANDLE     hPubKey = CK_INVALID_HANDLE;
CK_OBJECT_HANDLE     hPrivKey = CK_INVALID_HANDLE;
CK_BBOOL bAsymKey = CK_FALSE;

CK_BYTE gcmPlainText[] = "\x68\xe6\xbc\x0b\x08\xb8\xad\xbd\xc0\x00\x05\xae\x44\x72\x3c\x8e";
unsigned gcmplaintextlen = 16;
CK_BYTE	defPlainText[80] = "\xef\xbb\xbf\x53\x65\x63\x74\x69\x6f\x6e\x0d\x0a\x45\x6e\x64\x47\x6c\x6f\x62\x61\x6C\x0D\x0A\x42"; /* 24 characters */
unsigned plaintextlen=24;
int     errorCount = 0;
encoding_t 	encodings[5] = {{CS_UTF8, "CS_UTF8"}, {CS_UTF16LE, "CS_UTF16LE"}, {CS_UTF16BE, "CS_UTF16BE"}, {CS_UTF32LE, "CS_UTF32LE"}, {CS_UTF32BE, "CS_UTF32BE"}};
CK_BBOOL blk_mode = CK_FALSE;

int fgetline_w(char **lineptr, int *n, FILE *stream, CK_BYTE enc_mode)
{
    char *bufptr = NULL;
    char *p = bufptr;
    int size = 0;
    wint_t wc;
    long len;
    CK_BYTE CP[4];
    int ret;

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

    wc = fgetwc(stream);

    if (wc == WEOF)
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

    while (wc == '\n' || wc == '\r')
        wc = fgetwc(stream);

    while(wc != WEOF)
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

        if (wc == '\n' || wc == '\r')
        {
            break;
        }

        ret = gen_utf( (unsigned int)wc, enc_mode, CP);

        if (ret != 0)
        {
            memcpy(p, CP, ret);
            p += ret;
        }

        wc = fgetwc(stream);
    }

    *p = '\0';
    *lineptr = bufptr;
    *n = size;

    return (int)(p - bufptr);
}


static CK_RV encryptDecryptBuf(CK_SESSION_HANDLE hSess, CK_MECHANISM *pMechEnc, CK_MECHANISM *pMechDec, CK_BYTE *pBuf, unsigned int len, CK_BYTE **ppDecryptedBuf, unsigned long *pDecryptedLen, int bOmitEncryption, char *encrypted_file)
{
    /* General */
    CK_RV rc        = CKR_OK;
    CK_BYTE		    *cipherText = (CK_BYTE *) "";
    CK_ULONG		cipherTextLen = 0;
    FILE            *pF;
    /* For C_Decrypt */
    CK_BYTE         *decryptedText = NULL_PTR;
    CK_ULONG		decryptedTextLen = 0;
    int             status;
    int is_gcm = pMechEnc->mechanism == CKM_AES_GCM;
    // int taglen = (tag_bits & 0x7) == 0 ? tag_bits >> 3 : (tag_bits >> 3) + 1;
    int taglen = tag_bits >> 3;

    (void) taglen;

    if (!bOmitEncryption)
    {
        /* C_EncryptInit */
        if(bAsymKey == CK_FALSE)
        {
            rc = FunctionListFuncPtr->C_EncryptInit(hSess,
                                                    pMechEnc,
                                                    hGenKey
                                                   );
        }
        else
        {
            rc = FunctionListFuncPtr->C_EncryptInit(hSess,
                                                    pMechEnc,
                                                    hPubKey
                                                   );
        }

        if (rc != CKR_OK)
        {
            fprintf(stderr, "FAIL: call to C_EncryptInit() failed. rv=0x%x\n", (unsigned int)rc);
            return rc;
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
            return rc;
        }
        else
        {
            printf ("1st call to C_Encrypt() succeeded: size = %u.\n", (unsigned int)cipherTextLen);
            cipherText = (CK_BYTE *)calloc( 1, sizeof(CK_BYTE) * cipherTextLen );
            if (!cipherText)
                return CKR_HOST_MEMORY;
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
            return rc;
        }
        else
        {
            if (is_gcm)
            {
                /* handle GCM output messages */
                CK_BYTE *tag = cipherText + (unsigned int) (cipherTextLen - taglen);
                CK_BYTE *ptr = (CK_BYTE *)calloc( 1, sizeof(CK_BYTE) * cipherTextLen);
                printf("GCM C_Encrypt() succeeded. Original Encrypted Text:\n");
                dumpHexArray( cipherText, (int)cipherTextLen );
                memcpy(ptr, tag, taglen);
                memcpy(ptr + taglen, cipherText, cipherTextLen - taglen);
                printf("TAG = ");
                dumpHexArray( tag, (int)taglen );

                free(cipherText);
                cipherText = ptr;
            }

            printf("AES 2nd call to C_Encrypt() succeeded. Encrypted Text:\n");
            dumpHexArray( cipherText, (int)cipherTextLen );
            if (encrypted_file)
            {
                pF = fopen(encrypted_file, "w");
                if (pF)
                {
                    size_t n = fwrite(cipherText, 1, (size_t) cipherTextLen, pF);
                    if (n != cipherTextLen)
                    {
                        fprintf (stderr, "FAIL: Call to C_DecryptInit() failed. fwrite failed\n");
                    }
                    fclose(pF);
                }
            }
        }
    }
    else
    {
        printf("Encryption omitted, this is decrypt-only mode\n");
        cipherTextLen = (CK_ULONG) len;
        cipherText = (CK_BYTE *) malloc(sizeof(CK_BYTE) * len );
        if (cipherText)
        {
            memcpy(cipherText, pBuf, len);
        }
        else
        {
            return CKR_HOST_MEMORY;
        }
    }

    /* C_DecryptInit */
    printf("About to call C_DecryptInit()\n");

    if(bAsymKey == CK_FALSE)
    {
        rc = FunctionListFuncPtr->C_DecryptInit(
                 hSess,
                 pMechDec,
                 hGenKey
             );
    }
    else
    {
        rc = FunctionListFuncPtr->C_DecryptInit(
                 hSess,
                 pMechDec,
                 hPrivKey
             );
    }

    if (rc != CKR_OK)
    {
        fprintf (stderr, "FAIL: Call to C_DecryptInit() failed. rv=0x%x\n", (unsigned int)rc);
        free (cipherText);
        return rc;
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
        return rc;
    }
    else
    {
        printf ("1st call to C_Decrypt() succeeded.\n");
        decryptedText = (CK_BYTE *)calloc( 1, sizeof(CK_BYTE) * decryptedTextLen );
        if ( NULL == decryptedText)
        {
            free (cipherText);
            return CKR_HOST_MEMORY;
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
        *ppDecryptedBuf = NULL;
        *pDecryptedLen = 0;
        free (cipherText);
        return rc;
    }
    else
    {
        printf ("2nd call to C_Decrypt() succeeded. Decrypted Text:\n");
        dumpHexArray(decryptedText, (int)decryptedTextLen);
        *ppDecryptedBuf = decryptedText;
        *pDecryptedLen = decryptedTextLen;
    }

    /* cleanup and free memory */
    free (cipherText);

    if (!bOmitEncryption)
    {
        /* compare the plaintext and decrypted text */
        status = memcmp( pBuf, decryptedText, decryptedTextLen );
        if (status == 0)
        {
            printf ("Success! Plain Text and Decrypted Text match!! \n\n");
            return CKR_OK;
        }
        else
        {
            printf ("Failure!, Plain Text and Decrypted Text do NOT match!! \n");
            return CKR_GENERAL_ERROR;
        }
    }
    else return CKR_OK;
}

int setDefaultForFF3_1(CK_FPE_GENERIC_PARAMETER *ff31params, char *tweakfilename, char *tweak_algo){
    int tweak_file_size = 0;
    if(tweak_algo){
        ff31params->tweakAlgolen = strlen(tweak_algo);
        memcpy(ff31params->tweakAlgo, tweak_algo, ff31params->tweakAlgolen);
    }
    switch(ff31params->mode){
        case CS_ASCII:
                strcpy((char *)defPlainText, "0123456789");
                plaintextlen=10;
                ff31params->charsetlen = strlen("0123456789ABCDEabcde");
                memcpy(ff31params->charset, "0123456789ABCDEabcde", ff31params->charsetlen);
                break;
        case CS_CARD10:
                strcpy((char *)defPlainText, "0123456789");
                plaintextlen=10;
                break;
        case CS_CARD26:
                strcpy((char *)defPlainText, "0123456789abcde");
                plaintextlen=15;
                break;
        case CS_CARD62:
                strcpy((char *)defPlainText, "0123456789ABCDEabcde");
                plaintextlen=20;
                break;
        case CS_UTF8:
                ff31params->radix = myhtons(10);
                ff31params->charsetlen = myhtonl(30);
                memcpy(ff31params->charset, "\xE2\x82\x80\xE2\x82\x81\xE2\x82\x82\xE2\x82\x83\xE2\x82\x84\xE2\x82\x85\xE2\x82\x86\xE2\x82\x87\xE2\x82\x88\xE2\x82\x89", 30); /* subscript 0-9 */
                strcpy((char *)defPlainText, "\xE2\x82\x88\xE2\x82\x89\xE2\x82\x80\xE2\x82\x81\xE2\x82\x82\xE2\x82\x81\xE2\x82\x82\xE2\x82\x83\xE2\x82\x84\xE2\x82\x85\xE2\x82\x86\xE2\x82\x87\xE2\x82\x88\xE2\x82\x89\xE2\x82\x80\xE2\x82\x80\xE2\x82\x80\xE2\x82\x80");
                plaintextlen=18*3;
                break;
        case CS_UTF16LE:
                ff31params->radix = myhtons(10);
                ff31params->charsetlen = myhtonl(20);
                memcpy(ff31params->charset, "\x80\x20\x81\x20\x82\x20\x83\x20\x84\x20\x85\x20\x86\x20\x87\x20\x88\x20\x89\x20", 20); /* subscript 0-9 */
                strcpy((char *)defPlainText, "\x88\x20\x89\x20\x80\x20\x81\x20\x82\x20\x81\x20\x82\x20\x83\x20\x84\x20\x85\x20\x86\x20\x87\x20\x88\x20\x89\x20\x80\x20\x80\x20\x80\x20\x80\x20");
                plaintextlen=18*2;
                break;
        case CS_UTF16BE:
                ff31params->radix = myhtons(10);
                ff31params->charsetlen = myhtonl(20);
                memcpy(ff31params->charset, "\x20\x80\x20\x81\x20\x82\x20\x83\x20\x84\x20\x85\x20\x86\x20\x87\x20\x88\x20\x89", 20); /* subscript 0-9 */
                strcpy((char *)defPlainText, "\x20\x88\x20\x89\x20\x80\x20\x81\x20\x82\x20\x81\x20\x82\x20\x83\x20\x84\x20\x85\x20\x86\x20\x87\x20\x88\x20\x89\x20\x80\x20\x80\x20\x80\x20\x80");
                plaintextlen=18*2;
                break;
        case CS_UTF32LE:
                ff31params->radix = myhtons(10);
                ff31params->charsetlen = myhtonl(40);
                memcpy(ff31params->charset, "\x80\x20\0\0\x81\x20\0\0\x82\x20\0\0\x83\x20\0\0\x84\x20\0\0\x85\x20\0\0\x86\x20\0\0\x87\x20\0\0\x88\x20\0\0\x89\x20\0\0", 40); /* subscript 0-9 */
                memcpy(defPlainText, "\x88\x20\0\0\x89\x20\0\0\x80\x20\0\0\x81\x20\0\0\x82\x20\0\0\x81\x20\0\0\x82\x20\0\0\x83\x20\0\0\x84\x20\0\0\x85\x20\0\0\x86\x20\0\0\x87\x20\0\0\x88\x20\0\0\x89\x20\0\0\x80\x20\0\0\x80\x20\0\0\x80\x20\0\0\x80\x20\0\0", 4*18);
                plaintextlen=18*4;
                break;
        case CS_UTF32BE:
                ff31params->radix = myhtons(10);
                ff31params->charsetlen = myhtonl(40);
                memcpy(ff31params->charset, "\0\0\x20\x80\0\0\x20\x81\0\0\x20\x82\0\0\x20\x83\0\0\x20\x84\0\0\x20\x85\0\0\x20\x86\0\0\x20\x87\0\0\x20\x88\0\0\x20\x89", 40); /* subscript 0-9 */
                memcpy(defPlainText, "\0\0\x20\x88\0\0\x20\x89\0\0\x20\x80\0\0\x20\x81\0\0\x20\x82\0\0\x20\x81\0\0\x20\x82\0\0\x20\x83\0\0\x20\x84\0\0\x20\x85\0\0\x20\x86\0\0\x20\x87\0\0\x20\x88\0\0\x20\x89\0\0\x20\x80\0\0\x20\x80\0\0\x20\x80\0\0\x20\x80", 4*18);
                plaintextlen=18*4;
                break;
        default: printf("provided charset type is invalid \n");
    }
    if (tweakfilename)
    {
        FILE* pf;
        if ((pf = fopen(tweakfilename, "r")) != NULL ) {
            tweak_file_size = fread(ff31params->tweak, 1, 256, pf);
        }
        if (pf && tweak_file_size);
        if (pf) fclose(pf);
        ff31params->tweak[tweak_file_size] = '\0';
        ff31params->tweaklen = tweak_file_size;
    }
    else{
        memcpy(ff31params->tweak, "D8E7920AFA33A0", 14);
        ff31params->tweak[14] = '\0';
        ff31params->tweaklen = 14;
    }
}


/*
 ************************************************************************
 * Function: encryptAndDecrypt
 * This function first encrypts a block of data using a symmetric key. Then
 * decrypts the ciphertext with the same key to make sure the plain text and
 * decrypted text matches.
 * The caller is responsible for creating a buffer for the output that is
 * of sufficient size.
 ************************************************************************
 * Parameters: operation ... CBC_PAD or CTR or ECB or FPE or FF1
 * Returns: CK_RV
 ************************************************************************
 */
static CK_RV encryptDecrypt(char *operation, char *in_filename, char *piv, char cset_choc, char *charset, char *decrypted_file, char *encrypted_file, char *charsettype, char *header_version, int bOmitEncryption, char *tweakfilename, char *tweak_algo)
{
    CK_BYTE		  def_iv[] = "\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\x0C\x0D\x0E\x0F";
    CK_BYTE	      *pBuf = NULL;
    char            *pCharset = NULL;
    char            *token = NULL;
    CK_BYTE         *pDecryptBuf = NULL, *pPlainBuf = NULL;
    FILE            *fp_read = NULL;
    FILE            *fp_write = NULL;
    FILE            *fp_charset = NULL;
    int             readlen = 0;
    int             act_rdlen = 0;
    int             bf_len;
    char            fopen_mode[128];
    CK_ULONG        decryptedLen;
    CK_BBOOL        bFpeMode = CK_FALSE;
    CK_RV           rc = CKR_OK;
    wint_t          wc;
    const char	  delims[] = ",";
    unsigned short  rdelims[] = { 0x0d, 0x0a };
    int             line_no;
    int             i, j;
    int             ret;
    CK_ULONG        encheader=0; /* no header */
    CK_ULONG        decheader=0; /* no header */

    if (!charsettype) charsettype = "ASCII";

    if (!header_version || strlen(header_version)<4 || header_version[0]!='v' || header_version[2]!='.')
    {
        encheader=0; /* no header */
        decheader=0; /* no header */
    }
    else switch(header_version[3])
        {
            /* v1.5, v1.5base64, v2.1, v2.7 */
        case '5':
            encheader=CKM_THALES_V15HDR|CKM_VENDOR_DEFINED;
            if (header_version[4]=='b') encheader |= CKM_THALES_BASE64;
            decheader=CKM_THALES_ALLHDR|CKM_VENDOR_DEFINED;
            if (header_version[4]=='b') decheader |= CKM_THALES_BASE64;
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

    {
        /* C_Encrypt */
        CK_FPE_PARAMETER     fpeparams;
        CK_FPE_PARAMETER_UTF fpeparamsutf;
        CK_FF1_PARAMETER_UTF ff1paramsutf;
        CK_FPE_GENERIC_PARAMETER ff31params;
        CK_MECHANISM	mechEncryptionPad =    { encheader|CKM_AES_CBC_PAD,   def_iv, 16 };
        CK_MECHANISM	mechEncryptionCtr =    { encheader|CKM_AES_CTR,       def_iv, 16 };
        CK_MECHANISM    mechEncryptionGCM =    { CKM_AES_GCM, &gcmParams, sizeof (CK_GCM_PARAMS) };
        CK_MECHANISM	mechEncryptionECB =    { encheader|CKM_AES_ECB,       def_iv, 16 };
        CK_MECHANISM    mechEncryptionRSA =    { encheader|CKM_RSA_PKCS, NULL, 0 };
        CK_MECHANISM	mechEncryptionFPE =    { encheader|CKM_THALES_FPE, &fpeparams, sizeof(fpeparams) };
        CK_MECHANISM	mechEncryptionFPEUTF = { encheader|CKM_THALES_FPE, &fpeparamsutf, sizeof(fpeparamsutf) };
        CK_MECHANISM	mechEncryptionFF1UTF = { encheader|CKM_THALES_FF1, &ff1paramsutf, sizeof(ff1paramsutf) };
        CK_MECHANISM	mechEncryptionFF31 =   { encheader|CKM_THALES_FF3_1, &ff31params, sizeof(ff31params) };
        CK_MECHANISM    *pmechEncryption = NULL;
        CK_MECHANISM	mechDecryptionPad =    { decheader|CKM_AES_CBC_PAD,   def_iv, 16 };
        CK_MECHANISM	mechDecryptionCtr =    { decheader|CKM_AES_CTR,       def_iv, 16 };
        CK_MECHANISM    mechDecryptionGCM =    { CKM_AES_GCM, &gcmParams, sizeof (CK_GCM_PARAMS) };
        CK_MECHANISM	mechDecryptionECB =    { decheader|CKM_AES_ECB,       def_iv, 16 };
        CK_MECHANISM    mechDecryptionRSA =    { decheader|CKM_RSA_PKCS, NULL, 0 };
        CK_MECHANISM	mechDecryptionFPE =    { decheader|CKM_THALES_FPE, &fpeparams, sizeof(fpeparams) };
        CK_MECHANISM	mechDecryptionFPEUTF = { decheader|CKM_THALES_FPE, &fpeparamsutf, sizeof(fpeparamsutf) };
        CK_MECHANISM	mechDecryptionFF1UTF = { decheader|CKM_THALES_FF1, &ff1paramsutf, sizeof(ff1paramsutf) };
        CK_MECHANISM	mechDecryptionFF31 = { decheader|CKM_THALES_FF3_1, &ff31params, sizeof(ff31params) };
        CK_MECHANISM    *pmechDecryption = NULL;
        CK_BYTE enc_mode = get_enc_mode(charsettype);

        int is_gcm = (strncmp(operation, "GCM", 4) == 0);

        if(!charset)
        {
            if (!strcmp(operation, "FPE") )
            {
                if (!strncmp(charsettype, "UTF", 3))
                {
                    if (tweakfilename)
                    {
                        FILE *pf=fopen(tweakfilename, "r");
                        if (pf && fread(fpeparamsutf.tweak, 1, 8, pf)==8) ;
                        if (pf) fclose(pf);
                    }
                    else               memcpy(fpeparamsutf.tweak, "\xD8\xE7\x92\x0A\xFA\x33\x0A\x73", 8);
                    fpeparamsutf.mode = 1; /* UTF mode */
                    fpeparamsutf.radix = myhtons(10);
                }

                if (!strcmp(charsettype, "ASCII"))
                {
                    if (tweakfilename)
                    {
                        FILE *pf=fopen(tweakfilename, "r");
                        if (pf && fread(fpeparams.tweak, 1, 8, pf)==8) ;
                        if (pf) fclose(pf);
                    }
                    else               memcpy(fpeparams.tweak, "\xD8\xE7\x92\x0A\xFA\x33\x0A\x73", 8);
                    fpeparams.radix = 10;
                    memcpy(fpeparams.charset, "0123456789", 10);
                    strcpy((char *)defPlainText, "98765432109876543210987");
                    plaintextlen=18;
                }
                else if (!strcmp(charsettype, "UTF16BE"))
                {
                    fpeparamsutf.utfmode = CS_UTF16BE;
                    fpeparamsutf.charsetlen = myhtonl(20);
                    memcpy(fpeparamsutf.charset, "\x20\x80\x20\x81\x20\x82\x20\x83\x20\x84\x20\x85\x20\x86\x20\x87\x20\x88\x20\x89", 20); /* subscript 0-9 */
                    strcpy((char *)defPlainText, "\x20\x88\x20\x89\x20\x80\x20\x81\x20\x82\x20\x81\x20\x82\x20\x83\x20\x84\x20\x85\x20\x86\x20\x87\x20\x88\x20\x89\x20\x80\x20\x80\x20\x80\x20\x80");
                    plaintextlen=18*2;
                }
                else if (!strcmp(charsettype, "UTF16LE"))
                {
                    fpeparamsutf.utfmode = CS_UTF16LE;
                    fpeparamsutf.charsetlen = myhtonl(20);
                    memcpy(fpeparamsutf.charset, "\x80\x20\x81\x20\x82\x20\x83\x20\x84\x20\x85\x20\x86\x20\x87\x20\x88\x20\x89\x20", 20); /* subscript 0-9 */
                    strcpy((char *)defPlainText, "\x88\x20\x89\x20\x80\x20\x81\x20\x82\x20\x81\x20\x82\x20\x83\x20\x84\x20\x85\x20\x86\x20\x87\x20\x88\x20\x89\x20\x80\x20\x80\x20\x80\x20\x80\x20");
                    plaintextlen=18*2;
                }
                else if (!strcmp(charsettype, "UTF32BE"))
                {
                    fpeparamsutf.utfmode = CS_UTF32BE;
                    fpeparamsutf.charsetlen = myhtonl(40);
                    memcpy(fpeparamsutf.charset, "\0\0\x20\x80\0\0\x20\x81\0\0\x20\x82\0\0\x20\x83\0\0\x20\x84\0\0\x20\x85\0\0\x20\x86\0\0\x20\x87\0\0\x20\x88\0\0\x20\x89", 40); /* subscript 0-9 */
                    memcpy(defPlainText, "\0\0\x20\x88\0\0\x20\x89\0\0\x20\x80\0\0\x20\x81\0\0\x20\x82\0\0\x20\x81\0\0\x20\x82\0\0\x20\x83\0\0\x20\x84\0\0\x20\x85\0\0\x20\x86\0\0\x20\x87\0\0\x20\x88\0\0\x20\x89\0\0\x20\x80\0\0\x20\x80\0\0\x20\x80\0\0\x20\x80", 4*18);
                    plaintextlen=18*4;
                }
                else if (!strcmp(charsettype, "UTF32LE"))
                {
                    fpeparamsutf.utfmode = CS_UTF32LE;
                    fpeparamsutf.charsetlen = myhtonl(40);
                    memcpy(fpeparamsutf.charset, "\x80\x20\0\0\x81\x20\0\0\x82\x20\0\0\x83\x20\0\0\x84\x20\0\0\x85\x20\0\0\x86\x20\0\0\x87\x20\0\0\x88\x20\0\0\x89\x20\0\0", 40); /* subscript 0-9 */
                    memcpy(defPlainText, "\x88\x20\0\0\x89\x20\0\0\x80\x20\0\0\x81\x20\0\0\x82\x20\0\0\x81\x20\0\0\x82\x20\0\0\x83\x20\0\0\x84\x20\0\0\x85\x20\0\0\x86\x20\0\0\x87\x20\0\0\x88\x20\0\0\x89\x20\0\0\x80\x20\0\0\x80\x20\0\0\x80\x20\0\0\x80\x20\0\0", 4*18);
                    plaintextlen=18*4;
                }
                else if (!strcmp(charsettype, "UTF8"))
                {
                    fpeparamsutf.utfmode = CS_UTF8;
                    fpeparamsutf.charsetlen = myhtonl(30);
                    memcpy(fpeparamsutf.charset, "\xE2\x82\x80\xE2\x82\x81\xE2\x82\x82\xE2\x82\x83\xE2\x82\x84\xE2\x82\x85\xE2\x82\x86\xE2\x82\x87\xE2\x82\x88\xE2\x82\x89", 30); /* subscript 0-9 */
                    strcpy((char *)defPlainText, "\xE2\x82\x88\xE2\x82\x89\xE2\x82\x80\xE2\x82\x81\xE2\x82\x82\xE2\x82\x81\xE2\x82\x82\xE2\x82\x83\xE2\x82\x84\xE2\x82\x85\xE2\x82\x86\xE2\x82\x87\xE2\x82\x88\xE2\x82\x89\xE2\x82\x80\xE2\x82\x80\xE2\x82\x80\xE2\x82\x80");
                    plaintextlen=18*3;
                }
                else
                {
                    fprintf(stderr, "Illegal character set type specified: Use one of ASCII, UTF16BE, UTF16LE, UTF32BE, UTF32LE, UTF8\n");
                    return CKR_GENERAL_ERROR;
                }
            }
            else if (!strcmp(operation, "FF1") )
            {
                ff1paramsutf.radix = myhtons(10);
                if (!charsettype || !*charsettype || !strcmp(charsettype, "ASCII"))
                {
                    ff1paramsutf.utfmode = CS_ASCII;
                    ff1paramsutf.charsetlen = myhtonl(10);
                    memcpy(ff1paramsutf.charset, "0123456789", 10);
                    strcpy((char *)defPlainText, "98765432109876543210987");
                    plaintextlen=18;
                }
                else if (!strcmp(charsettype, "UTF16BE"))
                {
                    ff1paramsutf.utfmode = CS_UTF16BE;
                    ff1paramsutf.charsetlen = myhtonl(20);
                    memcpy(ff1paramsutf.charset, "\x20\x80\x20\x81\x20\x82\x20\x83\x20\x84\x20\x85\x20\x86\x20\x87\x20\x88\x20\x89", 20); /* subscript 0-9 */
                    strcpy((char *)defPlainText, "\x20\x88\x20\x89\x20\x80\x20\x81\x20\x82\x20\x81\x20\x82\x20\x83\x20\x84\x20\x85\x20\x86\x20\x87\x20\x88\x20\x89\x20\x80\x20\x80\x20\x80\x20\x80");
                    plaintextlen=18*2;
                }
                else if (!strcmp(charsettype, "UTF16LE"))
                {
                    ff1paramsutf.utfmode = CS_UTF16LE;
                    ff1paramsutf.charsetlen = myhtonl(20);
                    memcpy(ff1paramsutf.charset, "\x80\x20\x81\x20\x82\x20\x83\x20\x84\x20\x85\x20\x86\x20\x87\x20\x88\x20\x89\x20", 20); /* subscript 0-9 */
                    strcpy((char *)defPlainText, "\x88\x20\x89\x20\x80\x20\x81\x20\x82\x20\x81\x20\x82\x20\x83\x20\x84\x20\x85\x20\x86\x20\x87\x20\x88\x20\x89\x20\x80\x20\x80\x20\x80\x20\x80\x20");
                    plaintextlen=18*2;
                }
                else if (!strcmp(charsettype, "UTF32BE"))
                {
                    ff1paramsutf.utfmode = CS_UTF32BE;
                    ff1paramsutf.charsetlen = myhtonl(40);
                    memcpy(ff1paramsutf.charset, "\0\0\x20\x80\0\0\x20\x81\0\0\x20\x82\0\0\x20\x83\0\0\x20\x84\0\0\x20\x85\0\0\x20\x86\0\0\x20\x87\0\0\x20\x88\0\0\x20\x89", 40); /* subscript 0-9 */
                    memcpy(defPlainText, "\0\0\x20\x88\0\0\x20\x89\0\0\x20\x80\0\0\x20\x81\0\0\x20\x82\0\0\x20\x81\0\0\x20\x82\0\0\x20\x83\0\0\x20\x84\0\0\x20\x85\0\0\x20\x86\0\0\x20\x87\0\0\x20\x88\0\0\x20\x89\0\0\x20\x80\0\0\x20\x80\0\0\x20\x80\0\0\x20\x80", 4*18);
                    plaintextlen=18*4;
                }
                else if (!strcmp(charsettype, "UTF32LE"))
                {
                    ff1paramsutf.utfmode = CS_UTF32LE;
                    ff1paramsutf.charsetlen = myhtonl(40);
                    memcpy(ff1paramsutf.charset, "\x80\x20\0\0\x81\x20\0\0\x82\x20\0\0\x83\x20\0\0\x84\x20\0\0\x85\x20\0\0\x86\x20\0\0\x87\x20\0\0\x88\x20\0\0\x89\x20\0\0", 40); /* subscript 0-9 */
                    memcpy(defPlainText, "\x88\x20\0\0\x89\x20\0\0\x80\x20\0\0\x81\x20\0\0\x82\x20\0\0\x81\x20\0\0\x82\x20\0\0\x83\x20\0\0\x84\x20\0\0\x85\x20\0\0\x86\x20\0\0\x87\x20\0\0\x88\x20\0\0\x89\x20\0\0\x80\x20\0\0\x80\x20\0\0\x80\x20\0\0\x80\x20\0\0", 4*18);
                    plaintextlen=18*4;
                }
                else if (!strcmp(charsettype, "UTF8"))
                {
                    ff1paramsutf.utfmode = CS_UTF8;
                    ff1paramsutf.charsetlen = myhtonl(30);
                    memcpy(ff1paramsutf.charset, "\xE2\x82\x80\xE2\x82\x81\xE2\x82\x82\xE2\x82\x83\xE2\x82\x84\xE2\x82\x85\xE2\x82\x86\xE2\x82\x87\xE2\x82\x88\xE2\x82\x89", 30); /* subscript 0-9 */
                    strcpy((char *)defPlainText, "\xE2\x82\x88\xE2\x82\x89\xE2\x82\x80\xE2\x82\x81\xE2\x82\x82\xE2\x82\x81\xE2\x82\x82\xE2\x82\x83\xE2\x82\x84\xE2\x82\x85\xE2\x82\x86\xE2\x82\x87\xE2\x82\x88\xE2\x82\x89\xE2\x82\x80\xE2\x82\x80\xE2\x82\x80\xE2\x82\x80");
                    plaintextlen=18*3;
                }
                else
                {
                    fprintf(stderr, "Illegal character set type specified: Use one of ASCII, UTF16BE, UTF16LE, UTF32BE, UTF32LE, UTF8\n");
                    return CKR_GENERAL_ERROR;
                }
                /* optional Tweak is appended after the character set */
                if (tweakfilename)
                {
                    FILE *pf=fopen(tweakfilename, "r");
                    if (pf && fread(ff1paramsutf.charset+myhtonl(ff1paramsutf.charsetlen), 1, 8, pf)==8) ;
                    if (pf) fclose(pf);
                    ff1paramsutf.tweaklen = myhtonl(8);
                }
                else ff1paramsutf.tweaklen = myhtonl(0);
            }
            else if (!strcmp(operation, "FF3-1") ){
                
                ff31params.mode = enc_mode;
                
                setDefaultForFF3_1(&ff31params, tweakfilename, tweak_algo);
            }
            else
            {
                plaintextlen=16;
            }
        }
        else
        {
            char *pch = NULL;
            char *p1, *p2, *prng;
            unsigned int  rstart, rend, rcp;
            CK_BYTE CP[4];
            int act_rdx, charsetlen;
            int c = 0x1;
            int cc2 = 0x1;

            if(enc_mode != CS_ASCII)
            {
                fpeparamsutf.mode = 1;
            }else if (!strcmp(operation, "FF3-1")) {

                ff31params.mode = enc_mode;
            }

            if(cset_choc == 'c')
            {
                if (strcmp(operation, "FF3-1") ){
                    strncpy((char *) fpeparams.charset, charset, sizeof(fpeparams.charset)-1);
                    fpeparams.charset[sizeof(fpeparams.charset)-1] = '\0';
                    fpeparams.radix = (CK_BYTE) strlen(charset);

                    strncpy((char *) ff1paramsutf.charset, charset, sizeof(ff1paramsutf.charset)-1);
                    ff1paramsutf.charset[sizeof(ff1paramsutf.charset)-1] = '\0';
                    ff1paramsutf.charsetlen = (unsigned) myhtonl(strlen(charset));
                    ff1paramsutf.radix = (unsigned short) myhtons(strlen(charset));
                    ff1paramsutf.tweaklen = myhtonl(0);
                    ff1paramsutf.utfmode  = 0; /* ASCII */
                }else{
                    if(ff31params.mode == CS_ASCII){
                        setDefaultForFF3_1(&ff31params, tweakfilename, tweak_algo);
                        ff31params.charsetlen = strlen(charset);
                        memcpy(ff31params.charset, charset, ff31params.charsetlen);
                    }
                }
                /* Adding this if user needs to hit tweakdata scenario */
                if (tweakfilename  && strcmp(operation, "FF3-1"))
                {
                    FILE *pf=fopen(tweakfilename, "r");
                    if (pf && fread(ff1paramsutf.charset+myhtonl(ff1paramsutf.charsetlen), 1, 8, pf)==8) ;
                    if (pf) fclose(pf);
                    ff1paramsutf.tweaklen = myhtonl(8);
                }
                else
                    ff1paramsutf.tweaklen = myhtonl(0);
            }
            else if(cset_choc == 'l')
            {
                FILE *fp_charsetutf = NULL;
                fp_charset = fopen(charset, "r");
                if(!fp_charset)
                {
                    fprintf(stderr, "Unable to open character set file: %s", charset);
                    return CKR_GENERAL_ERROR;
                }

                c = fgetc(fp_charset);

                if(enc_mode == CS_ASCII)
                {

                    pCharset = (char *)calloc(4, MAX_RADIX_SIZE); /* UTF encoded charset can be 65535 * 4 bytes long */
                    if(pCharset == NULL)
                    {
                        fprintf(stderr, "Error allocating pCharset!");
                        fclose(fp_charset);
                        return CKR_HOST_MEMORY;
                    }

                    memset(pCharset, 0, MAX_RADIX_SIZE*4);
                    /* This would remove duplicates naturally, for ASCII only */
                    while( c != EOF )
                    {
                        if(c == '\n' || c == '\r') /* filter out newline character \n\r */
                        {
                            c = fgetc(fp_charset);
                            continue;
                        }
                        if(c == EOF )
                            break;
                        pCharset[c] = (char)c;
                        c = fgetc(fp_charset);
                    }
                    fclose(fp_charset);

                    j = 0; /* ASCII code 0 is NULL, will be overwritten */
                    i = 1;

                    do
                    {
                        while(pCharset[i] == '\0')
                            i++;

                        if(i >= MAX_RADIX_SIZE-1)
                            break;

                        fpeparams.charset[j]    = pCharset[i];
                        ff1paramsutf.charset[j] = pCharset[i];
                        j++;
                        i++;
                    }
                    while(i < MAX_RADIX_SIZE-1);

                    fpeparams.charset[j] = '\0'; /* not needed */
                    fpeparams.radix = (CK_BYTE)j;
                    ff1paramsutf.radix = (unsigned short) myhtons(j);
                    ff1paramsutf.utfmode = enc_mode;
                    ff1paramsutf.charsetlen = (unsigned) myhtonl(j);

                    printf("Charset is: %*s, radix=%d.\n", j, (char *) fpeparams.charset, j);
                    if(pCharset)
                    {
                        free(pCharset);
                        pCharset = NULL;
                    }
                } /* ASCII mode */
                else
                {
                    /* some UTF mode */
                    int cc3 = 0x1;
                    int cc4 = 0x1;
                    fprintf(stderr, "C sample: literal input support UTF mode UTF8, UTF16LE/BE, UTF32LE/BE");
                    if(c != EOF)
                        cc2 = fgetc(fp_charset);

                    if(cc2 != EOF)
                    {
                        cc3 = fgetc(fp_charset);
                        if(cc3 != EOF)
                            cc4 = fgetc(fp_charset);
                    }
                    else
                    {
                        fprintf(stderr, "File size too small: %s", charset);
                        return CKR_GENERAL_ERROR;
                    }

                    if(c == 0xFF && cc2 == 0xFE)
                    {
                        if(cc3 == 0x00 && cc4 == 0x00)
                            fp_charsetutf = fopen(charset, "r,ccs=UTF32LE");
                        else
                            fp_charsetutf = fopen(charset, "r,ccs=UTF16LE");
                    }
                    else if(c == 0xFE && cc2 == 0xFF)
                    {
                        fp_charsetutf = fopen(charset, "r,ccs=UTF16BE");
                    }
                    else
                    {
                        if(c == 0xEF && cc2 == 0xBB && cc3 == 0xBF)
                            fp_charsetutf = fopen(charset, "r,ccs=UTF8");
                        else if(c == 0x00 && cc2 == 0x00 && cc3 == 0xFE && cc4 == 0xFF)
                            fp_charsetutf = fopen(charset, "r,ccs=UTF32BE");
                        else
                            fp_charsetutf = fopen(charset, "r");
                    }

                    if(!fp_charsetutf)
                    {
                        fprintf(stderr, "Unable to open character set file with UTF mode: %s", charset);
                        return CKR_GENERAL_ERROR;
                    }

                    fclose(fp_charset);
                    wc = fgetwc(fp_charsetutf); /* SKIP BOM character */
                    act_rdx = 0;
                    charsetlen = 0;

                    wc = fgetwc(fp_charsetutf);

                    while( wc != WEOF )
                    {
                        if(wc == '\n' || wc == '\r') /* filter out newline character \n\r */
                        {
                            wc = fgetwc(fp_charsetutf);
                            continue;
                        }
                        if(wc == WEOF )
                            break;

                        if(act_rdx >= 65535)
                            break;

                        rcp = (unsigned int)wc;
                        ret = gen_utf(rcp, enc_mode, CP);

                        if (ret != 0)
                        {
                            memcpy(fpeparamsutf.charset + charsetlen, CP, ret);
                            memcpy(ff1paramsutf.charset + charsetlen, CP, ret);
                            charsetlen += ret;
                            act_rdx++;
                        }

                        wc = fgetwc(fp_charsetutf);
                    }
                    fclose(fp_charsetutf);

                    if(enc_mode != CS_ASCII && blk_mode == CK_TRUE)
                    {
                        for(i=0; i<2; i++)
                        {
                            ret = gen_utf((unsigned int)rdelims[i], enc_mode, CP);

                            if (ret != 0)
                            {
                                memcpy(fpeparamsutf.charset + charsetlen, CP, ret);
                                memcpy(ff1paramsutf.charset + charsetlen, CP, ret);
                                charsetlen += ret;
                                act_rdx++;
                            }
                        }
                    }

                    if(act_rdx >= 65535)
                    {
                        printf("The character set is limited to 65535 characters, which was exceeded. Exiting...\n");
                        exit(4);
                    }

                    printf("UTF mode = %d, Character set length = %d, Radix = %d", enc_mode, charsetlen, act_rdx);
                    memcpy(fpeparamsutf.tweak, "\xD8\xE7\x92\x0A\xFA\x33\x0A\x73", 8);
                    fpeparamsutf.utfmode = enc_mode;
                    fpeparamsutf.charsetlen = myhtonl(charsetlen);
                    fpeparamsutf.radix = (unsigned short) myhtons(act_rdx);

                    ff1paramsutf.utfmode = enc_mode;
                    ff1paramsutf.charsetlen = (unsigned) myhtonl(charsetlen);
                    ff1paramsutf.radix = (unsigned short) myhtons(act_rdx);
                    ff1paramsutf.tweaklen = myhtonl(0);
                } /* some UTF mode */
            }	/* cset_choc == 'l' */
            else if(cset_choc == 'r') /* r stands for range */
            {
                fp_charset = fopen(charset, "r+");
                if(!fp_charset)
                {
                    fprintf(stderr, "Unable to open character set file: %s", charset);
                    return CKR_GENERAL_ERROR;
                }

                act_rdx = 0;
                charsetlen = 0;

                pBuf = (CK_BYTE *)calloc(1, sizeof(CK_BYTE) * READ_BLK_LEN * 2);
                if( !pBuf )
                {
                    fprintf(stderr, "Error allocating memory for charset file!");
                    goto FREE_RESOURCES;
                }

                readlen = (int)fread(pBuf, sizeof(CK_BYTE), READ_BLK_LEN * 2, fp_charset);
                printf("Read from charset file: readlen = %d.", readlen);

                token = strtok((char *)pBuf, delims);

                while(token)
                {
                    prng = strdup((char *)token);
                    if(!prng)
                        goto FREE_RESOURCES;
                    pch = strchr(prng, '-');

                    if(pch)
                    {
                        /* xxxx-yyyy */
                        p1 = prng;
                        *pch = '\0';
                        p2 = pch+1;
                        trim(p1);
                        trim(p2);
                        rstart = (unsigned int)strtoul(p1, NULL, 16);
                        rend = (unsigned int)strtoul(p2, NULL, 16);
                        printf("range read from range file: %08X-%08X\n", rstart, rend);

                        for(rcp=rstart; rcp<=rend; rcp++)
                        {
                            if(act_rdx >= 65535)
                            {
                                printf("The character set is limited to 65535 characters, which was exceeded. Aborting...\n");
                                exit(4);
                            }

                            ret = gen_utf(rcp, enc_mode, CP);

                            if (ret != 0)
                            {
                                memcpy(fpeparamsutf.charset + charsetlen, CP, ret);
                                memcpy(ff1paramsutf.charset + charsetlen, CP, ret);
                                charsetlen += ret;
                                act_rdx++;
                            }
                        }
                        printf("after processing this range, charsetlen is %d\n", charsetlen);
                    }
                    else
                    {
                        /* single value */
                        p1 = prng;
                        trim(p1);
                        if(act_rdx >= 65535)
                            break;
                        rcp = (unsigned int)strtoul(p1, NULL, 16);
                        ret = gen_utf(rcp, enc_mode, CP);

                        if (ret != 0)
                        {
                            memcpy(fpeparamsutf.charset + charsetlen, CP, ret);
                            memcpy(ff1paramsutf.charset + charsetlen, CP, ret);
                            charsetlen += ret;
                            act_rdx++;
                        }
                    }
                    token = strtok(NULL, delims);

                    if(prng)
                    {
                        free(prng);
                        prng = NULL;
                    }
                }

                if(enc_mode != CS_ASCII && blk_mode == CK_TRUE)
                {
                    for(i=0; i<2; i++)
                    {
                        ret = gen_utf((unsigned int)rdelims[i], enc_mode, CP);

                        if (ret != 0)
                        {
                            memcpy(fpeparamsutf.charset + charsetlen, CP, ret);
                            memcpy(ff1paramsutf.charset + charsetlen, CP, ret);
                            charsetlen += ret;
                            act_rdx++;
                        }
                    }
                }

                if(act_rdx >= 65535)
                {
                    printf("The character set is limited to 65535 characters, which was exceeded. Aborting...\n");
                    exit(4);
                }

                printf("UTF mode = %d, Character set length = %d, Radix = %d\n", enc_mode, charsetlen, act_rdx);

                if (charsetlen<256) memcpy(fpeparams.charset, fpeparamsutf.charset, charsetlen);
                fpeparams.radix = (CK_BYTE)charsetlen;

                memcpy(fpeparamsutf.tweak, "\xD8\xE7\x92\x0A\xFA\x33\x0A\x73", 8);
                fpeparamsutf.utfmode = enc_mode;
                fpeparamsutf.charsetlen = myhtonl(charsetlen);
                fpeparamsutf.radix = (unsigned short) myhtons(act_rdx);

                ff1paramsutf.utfmode = enc_mode;
                ff1paramsutf.charsetlen = (unsigned) myhtonl(charsetlen);
                ff1paramsutf.radix = (unsigned short) myhtons(act_rdx);
                ff1paramsutf.tweaklen = myhtonl(0);

                if(pBuf)
                {
                    free( pBuf );
                    pBuf = NULL;
                }
            }
        } /* a character set or a character set file was specified on the command line */

        if (piv && is_gcm)
        {
            int k=0;
            gcm_iv_length = (CK_ULONG) strlen(piv) >> 1;
            printf("Obtaining GCM IV from the command line\n");
            for (k=0; k< (int) gcm_iv_length; k++)
            {
                char x[3];
                unsigned u;
                x[2]=0;
                x[0]=piv[k+k];
                x[1]=piv[k+k+1];
                sscanf(x, "%X", &u);
                def_gcm_iv[k] = (CK_BYTE) u;
            }
        }
        else if (piv && strlen(piv)==32)
        {
            int k=0;
            printf("Obtaining IV from the command line\n");
            for (k=0; k<16; k++)
            {
                char x[3];
                unsigned u;
                x[2]=0;
                x[0]=piv[k+k];
                x[1]=piv[k+k+1];
                sscanf(x, "%X", &u);
                def_iv[k] = (CK_BYTE) u;
            }
        }
        else if (!piv)
            printf("Using canned IV (because piv is NULL)\n");
        else
            printf("Using canned IV (because strlen(piv) is %d)\n", (int) strlen(piv) );

        printf("IV:\n");
        if (is_gcm)
        {
            dumpHexArray(def_gcm_iv, gcm_iv_length);
        }
        else
        {
            dumpHexArray(def_iv, 16);
        }

        if (!strcmp(operation, "FPE"))
        {
            if (!strcmp(charsettype, "ASCII"))
            {
                pmechEncryption = &mechEncryptionFPE;
                pmechDecryption = &mechDecryptionFPE;
            }
            else
            {
                pmechEncryption = &mechEncryptionFPEUTF;
                pmechDecryption = &mechDecryptionFPEUTF;
            }
            bFpeMode = CK_TRUE;
        }
        else if (!strcmp(operation, "FF3-1"))
        {
            pmechEncryption = &mechEncryptionFF31;
            pmechDecryption = &mechDecryptionFF31;
            bFpeMode = CK_TRUE;
        }
        else if (!strcmp(operation, "FF1"))
        {
            pmechEncryption = &mechEncryptionFF1UTF;
            pmechDecryption = &mechDecryptionFF1UTF;
            bFpeMode = CK_TRUE;
        }
        else if (!strcmp(operation, "CTR"))
        {
            pmechEncryption = &mechEncryptionCtr;
            pmechDecryption = &mechDecryptionCtr;
        }
        else if (!strcmp(operation, "GCM"))
        {
            pmechEncryption = &mechEncryptionGCM;
            pmechDecryption = &mechDecryptionGCM;
            if (aad_length > 0)
            {
                printf("Additional authentication data:\n");
                dumpHexArray(def_aad, aad_length);
            }
            if (tag_bits > 0)
            {
                printf("tag bits = %d (%d bytes)\n", (int) tag_bits, (int) tag_bits >> 3 );
            }
        }
        else if (!strcmp(operation, "ECB"))
        {
            pmechEncryption = &mechEncryptionECB;
            pmechDecryption = &mechDecryptionECB;
        }
        else if (!strcmp(operation, "RSA"))
        {
            pmechEncryption = &mechEncryptionRSA;
            pmechDecryption = &mechDecryptionRSA;
        }
        else  /* default to CBC_PAD */
        {
            pmechEncryption = &mechEncryptionPad;
            pmechDecryption = &mechDecryptionPad;
        }

        if (is_gcm)
        {
            gcmParams.pIv = def_gcm_iv;
            gcmParams.ulIvLen = gcm_iv_length;
            gcmParams.ulIvBits = gcmParams.ulIvLen << 3;
            memcpy(defPlainText, gcmPlainText, gcmplaintextlen);
            plaintextlen = gcmplaintextlen;
        }

        if (in_filename == NULL)
        {
            printf("Plain Text Default: \n");
            dumpHexArray(defPlainText, plaintextlen);
            rc = encryptDecryptBuf(hSession, pmechEncryption, pmechDecryption, (CK_BYTE *)defPlainText, plaintextlen, &pDecryptBuf, &decryptedLen, bOmitEncryption, encrypted_file);
        }
        else
        {
            if(blk_mode)
                fp_read = fopen(in_filename, "rb+");
            else if(enc_mode == CS_UTF8 || enc_mode == CS_UTF16LE || enc_mode == CS_UTF16BE || enc_mode == CS_UTF32LE || enc_mode == CS_UTF32BE)
            {
                strcpy( fopen_mode, "r,ccs=" );
                strcat( fopen_mode, charsettype );

                fp_read = fopen(in_filename, fopen_mode);
                wc = fgetwc(fp_read); /* read the BOM character, otherwise, first wchar_t read will be WEOF: -1 */
                if(wc != 0xFE)
                {
                    fprintf(stderr, "Read BOM character, Get: %x!! No BOM char/encoding used, read from beginning.\n", wc);
                    fseek(fp_read, 0, SEEK_SET);
                }
            }
            else
            {
                fp_read = fopen(in_filename, "r" /*fopen_mode*/);
            }

            if (!fp_read)
            {
                printf("Fail to open file %s.", in_filename);
                return CKR_FUNCTION_FAILED;
            }

            if(decrypted_file != NULL)
            {
                /*	strcpy( fopen_mode, "w,ccs=" );
                	strcat( fopen_mode, charsettype ); */

                fp_write = fopen(decrypted_file, "w+");

                if(!fp_write)
                {
                    printf("Fail to open file %s in %s mode.", decrypted_file, fopen_mode);
                    if(fp_read)
                        fclose(fp_read);
                    return CKR_FUNCTION_FAILED;
                }
            }

            line_no = 0;
            do
            {
                if(bFpeMode && !blk_mode)
                {
                    bf_len = READ_BLK_LEN;
                    pBuf = NULL;

            	    if(enc_mode == CS_UTF8 || enc_mode == CS_UTF16LE || enc_mode == CS_UTF16BE || enc_mode == CS_UTF32LE || enc_mode == CS_UTF32BE)
                    {
                        readlen = fgetline_w((char**)&pBuf, &bf_len, fp_read, enc_mode);
                    }
		    else
                        readlen = fgetline((char**)&pBuf, &bf_len, fp_read);

                    if(readlen < 0)
                    {
                        if(readlen != -1)
                            fprintf(stderr, "Error reading file, readlen = %d", (int)readlen);
                        break;
                    }

                    if(pBuf == NULL)
                    {
                        fprintf(stderr, "Error getting line from file, pBuf = NULL \n");
                        break;
                    }

                    /* for carriage return from windows */
                    while(pBuf[readlen-1] == '\n' || pBuf[readlen-1] == '\r')
                    {
                        pBuf[readlen--] = '\0';
                    }

                    act_rdlen = readlen;
                    if(line_no == 0)
                    {
                        pPlainBuf = get_BOM_mode(pBuf, &act_rdlen, &enc_mode);
                    }
                    else
                        pPlainBuf = pBuf;

                    fprintf(stdout, "PlainText:%s\n", (char *)pPlainBuf);
                }
                else
                {
                    bf_len = READ_BLK_LEN;
                    pBuf = (CK_BYTE *)calloc( bf_len, sizeof(CK_BYTE) );
                    if(pBuf)
                    {
                        readlen = (int)fread(pBuf, sizeof(CK_BYTE), bf_len, fp_read);
                        if (readlen<=0)
                        {
                            fprintf(stderr, "Error reading file, readlen = %d\n", (int)readlen);
                            exit(1);
                        }
                        act_rdlen = readlen;
                        pPlainBuf = get_BOM_mode(pBuf, &act_rdlen, &enc_mode);
                    }
                    else
                    {
                        goto FREE_RESOURCES;
                    }
                }

                if(readlen == 1 && bFpeMode)
                {
                    fprintf(stderr, "FPE mode only supports input length >= 2.\n");
                    if(pBuf)
                    {
                        free (pBuf);
                        pBuf = NULL;
                    }
                    continue;
                }

                if(readlen > 0 && pPlainBuf)
                {
                    pDecryptBuf = NULL;
                    rc = encryptDecryptBuf(hSession, pmechEncryption, pmechDecryption, pPlainBuf, (unsigned int)act_rdlen, &pDecryptBuf, &decryptedLen, bOmitEncryption, encrypted_file);

                    if(rc == CKR_OK && fp_write && pDecryptBuf)
                    {
                        if(bFpeMode)
                        {
                            if(line_no == 0)
                            {
                                put_BOM_mode(enc_mode, fp_write);
                            }
                            ret = (int)fwrite(pDecryptBuf, 1, decryptedLen, fp_write);

                            if(!blk_mode)   /* put line seperator back in */
                            {
                                /* fwrite("\x0d\x0a", 1, 2, fp_write); */
                                size_t n1 = fwrite(rdelims, sizeof(unsigned short), 2, fp_write);
                                if (n1 != 2*sizeof(unsigned short))
                                {
                                    fprintf(stderr, "Encrypt/Decrypt Error: write rdelims failed\n");
                                }
                            }
                        }
                        else
                        {
                            size_t n2 = fwrite(pDecryptBuf, 1, decryptedLen, fp_write);
                            if (n2 != decryptedLen)
                            {
                                fprintf(stderr, "Encrypt/Decrypt Error: write pDecryptBuf failed\n");
                            }
                        }
                    }
                    else if(rc != CKR_OK)
                    {
                        fprintf(stderr, "Encrypt/Decrypt Error: rc=%d.\n", (int)rc);
                        fprintf(stderr, "PlainText: %s\n", (char *)pBuf);
                        errorCount++;
                    }

                    if (pDecryptBuf)
                    {
                        free (pDecryptBuf);
                        pDecryptBuf = NULL;
                    }
                    memset(pBuf, 0, readlen);
                }

                if(pBuf)
                {
                    free (pBuf);
                    pBuf = NULL;
                }
                line_no++;
            }
            while ( bFpeMode && (!blk_mode || readlen == bf_len) );
        }

FREE_RESOURCES:
        if (pDecryptBuf)
        {
            free (pDecryptBuf);
            pDecryptBuf = NULL;
        }

        if(pBuf)
        {
            free (pBuf);
            pBuf = NULL;
        }

        if(fp_read)
            fclose(fp_read);

        if(fp_write)
            fclose(fp_write);

        if(bFpeMode && strcmp(operation, "FF3-1"))
            fprintf(stdout, "FPE/FF1 Tokenization: Encrypt/Decrypt matched error count = %d.\n", errorCount);

        return rc;
    }
}

void usageEncryptDecrypt()
{
    printf ("Usage: pkcs11_sample_encrypt_decrypt -p pin [-s slotID] -k keyName [-i {k|m|u}:identifier] [-m module_path] [-o operation] [-f input_file_name] [-iv iv_in_hex] [-a AAD_in_hex] [-t tag_bits] ([-c charset_for_fpe_mode]|[-l literal_charset_filename_for_fpe_mode]|[-r ranged_charset_filename_for_fpe_mode]) [-d decrypted_file_name] [-e encrypted_file_name] [-u charsettype] [-h header_version] [-n] [-T tweakfile]\n");
    printf ("-i identifier: one of 'imported key id' as 'k', MUID as 'm', or UUID as 'u'.\n");
    printf ("-z key_size key size for symmetric key in bytes.\n");
    printf ("-o operation...CBC_PAD (default) or CTR or ECB or GCM or FPE or FF1 or FF3-1\n");
    printf ("-c charset character set commandline typed input\n");
    printf ("-d optionally included decrypted file name.\n");
    printf ("-e optionally included encrypted file name.\n");
    printf ("-u charsettype...ASCII or UTF8 or UTF16LE or UTF16BE or UTF32LE or UTF32BE (for FPE or FF1 or FF3-1 only)\n");
    printf ("Note* CARD10, CARD26 and CARD62 is only supported for FF3-1\n");
    printf ("-l literal charset file name for the FPE, or FF1 mode.\n");
    printf ("-r range charset file name for the FPE, or FF1 mode.\n");
    printf ("-h header_version...v1.5 or v1.5base64 or v2.1 or v.2.7\n");
    printf ("-n... noencryption - decrypt only. Useful for decrypting a file\n");
    printf ("-T tweakfile ... read an 8-byte FPE/FF1 Tweak from a file\n");
    printf ("-ta tweak algo ... NONE, SHA1, SHA256\n");
    exit(2);
}

/*
 ************************************************************************
 * Function: main
 ************************************************************************
 */
#ifdef THALES_CLI_MODE
int encryptDecryptSample(int argc, char *argv[])
#else
int main(int argc, char *argv[])
#endif
{
    CK_RV rc;
    char *keyLabel = NULL;
    char *pin = NULL;
    char *libPath = NULL;

    char *foundPath = NULL;
    int  slotId = 0;
    char *operation = "CBC_PAD";
    char *filename = NULL;
    char *tweakfilename = NULL;
    char cset_choc = '\0';
    char *decrypted_file = NULL;
    char *encrypted_file = NULL;
    char *ivt = NULL;
    int   c;

    extern char *optarg;
    extern int optind;

    char *pKsid = NULL;
    int ksid_type = keyIdLabel;
    int key_size = 32;

    int loggedIn = 0;
    char *charset = NULL;
    char *pAad = NULL;

    char *tweak_algo = NULL;
    char *charsettype = "ASCII";
    char *header_version = NULL; /* NULL, v1.5, v1.5base64, v2.1, v2.7 allowed */
    int noencryption = 0; /* 0...encrypt&decrypt, 1...decrypt only */
    /*  */

    optind = 1;

    while ((c = newgetopt(argc, argv, "p:k:m:o:f:l:iv:s:c:u:r:d:e:h:b:ta:z:a:t:T:n;")) != EOF)
        switch (c)
        {
        case 'u':
            charsettype = optarg;
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

        case 'o':
            operation = optarg;
            if(!strcmp(operation, "RSA"))
            {
                bAsymKey = CK_TRUE;
            }
            break;
        case 'f':
            filename = optarg;
            break;
        case ta:
            tweak_algo = optarg;
            break;
        case 'T':
            tweakfilename = optarg;
            break;
        case iv:
            ivt = optarg;
            break;
        case 'a':
            pAad = optarg;
            aad_length = (CK_ULONG) strlen(optarg) >> 1;
            gcmParams.ulAADLen = aad_length;
            break;
        case 't':
            tag_bits = atoi(optarg);
            gcmParams.ulTagBits = tag_bits;
            break;
        case 'h':
            header_version = optarg;
            break;
        case 'i':
            ksid_type = parse_ksid_sel(optarg, &pKsid);
            break;
        case 'b':
            blk_mode = CK_TRUE;
            break;
        case 'c':
        case 'r':
        case 'l':
            cset_choc = (char)c;
            charset = optarg;
            break;

        case 'd':
            decrypted_file = optarg;
            break;
        case 'e':
            encrypted_file = optarg;
            break;
        case 'n':
            noencryption = 1; /* 0...encrypt&decrypt, 1...decrypt only */
            break;
        case 'z':
            key_size = atoi(optarg);
            break;
        case '?':
        default:
            usageEncryptDecrypt();
            break;
        }
    if ((NULL == pin) || (optind < argc))
    {
        usageEncryptDecrypt();
    }

    printf("Begin Encrypt and Decrypt Message sample.\n");

    if (pAad)
    {
        int k=0;
        printf("Obtaining GCM AAD from the command line\n");
        for (k=0; k< (int) aad_length; k++)
        {
            char x[3];
            unsigned u;
            x[2]=0;
            x[0]=pAad[k+k];
            x[1]=pAad[k+k+1];
            sscanf(x, "%X", &u);
            def_aad[k] = (CK_BYTE) u;
        }
        // gcmParams.pAAD = (CK_BYTE_PTR) pAad;
    }

    do
    {
        /* load PKCS11 library and initalize. */
        printf("Initializing PKCS11 library \n");
        foundPath = getPKCS11LibPath(libPath);
        if(foundPath == NULL)
        {
            printf("Error getting PKCS11 library path.\n");
            rc = CKR_GENERAL_ERROR;
            break;
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

        printf("Successfully logged in. \n Looking for key %s\n", pKsid);

        if(bAsymKey == CK_FALSE)
        {
            rc = findKey(pKsid, ksid_type, CKO_SECRET_KEY, &hGenKey);

            if (CK_INVALID_HANDLE == hGenKey)
            {
                printf("Key does not exist, creating key... Creating key \n");

                if(keyLabel)
                {
                    rc = createKeyS(keyLabel, key_size);
                    if (rc != CKR_OK)
                    {
                        break;
                    }
                    printf("Successfully created key %s.\n", keyLabel);
                }
            }
            else
            {
                printf("Successfully found key.\n");
            }
        }
        else
        {
            rc = findKey(pKsid, ksid_type, CKO_PUBLIC_KEY, &hPubKey);
            if (rc != CKR_OK)
            {
                fprintf(stderr, "FAIL: Unable to find public key: %s\n", pKsid);
                break;
            }

            rc = findKey(pKsid, ksid_type, CKO_PRIVATE_KEY, &hPrivKey);
            if (rc != CKR_OK)
            {
                fprintf(stderr, "FAIL: Unable to find private key: %s\n", pKsid);
                break;
            }

            if (CK_INVALID_HANDLE == hPubKey || CK_INVALID_HANDLE == hPrivKey)
            {
                fprintf(stderr, "FAIL: Unable to find public or private key: %s\n", pKsid);
                break;
            }
            else
            {
                printf("Successfully found public/private key %s.\n", pKsid);
            }
        }

        rc = encryptDecrypt(operation, filename, ivt, cset_choc, charset, decrypted_file, encrypted_file, charsettype, header_version, noencryption, tweakfilename, tweak_algo);
        if (rc != CKR_OK)
        {
            break;
        }
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
    printf("End Encrypt and Decrypt Message sample.\n");
    fflush(stdout);
    return rc;
}
