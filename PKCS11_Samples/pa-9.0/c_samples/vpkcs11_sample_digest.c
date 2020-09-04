/**                                                                      **
** Copyright(c) 2012 - 2015                       Confidential Material **
**                                                                      **
** This file is the property of Vormetric Inc.                          **
** The contents are proprietary and confidential.                       **
** Unauthorized use, duplication, or dissemination of this document,    **
** in whole or in part, is forbidden without the express consent of     **
** Vormetric, Inc..                                                     **
**                                                                      **
**************************************************************************/

/*
 ***************************************************************************
 * File: vpkcs11_sample_digest.c
 ***************************************************************************
 ***************************************************************************
 * This file demonstrates the following
 * 1. Initialization
 * 2. Creating a connection and logging in.
 * 3. Creating a symmetric key on the Data Security Manager for MAC'ing
 * 4. Compute the digest of HMAC for a given message
 * 5. Clean up.
 */

/* 
   vpkcs11_sample_digest.c
 */

#include "vpkcs11_sample_helper.h"
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

#ifdef __WINDOWS__

typedef int __ssize_t;
typedef __ssize_t ssize_t;

#else
#endif 

#define MAX_RADIX_SIZE 65535
#define READ_BLK_LEN 1024
CK_BYTE	defPlainText[80] = "\xef\xbb\xbf\x53\x65\x63\x74\x69\x6f\x6e\x0d\x0a\x45\x6e\x64\x47\x6c\x6f\x62\x61\x6C\x0D\x0A"; /* 23 characters */
unsigned plaintextlen=23;
int     errorCount = 0;


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

    switch (pMech->mechanism) {
    case CKM_SHA256_HMAC:

	rc = FunctionListFuncPtr->C_DigestKey(hSess, hGenKey);
	if (rc != CKR_OK) {
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
    else {
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
    else {
	printf ("1st call to C_DigestFinal() succeeded: size = %u.\n", (unsigned int) *messageLen);
	*message = (CK_BYTE *)calloc( 1, sizeof(CK_BYTE) * *messageLen );
	if (!*message)
	    return CKR_HOST_MEMORY;
    }	

    /* then call C_Digest to get actual message */
    rc = FunctionListFuncPtr->C_DigestFinal(
	hSess,
	*message, messageLen
	);
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



static CK_RV computeDigestMultiPart(CK_SESSION_HANDLE hSess, CK_MECHANISM *pMech, FILE *in,
				    CK_BYTE **message, unsigned long *messageLen)
{
    /* General */
    CK_RV rc = CKR_OK;
    char buffer[4096];
    size_t bytes_read = 0;

    /* C_DigestInit */
    rc = FunctionListFuncPtr->C_DigestInit(hSess, pMech);
    if (rc != CKR_OK)
    {
	fprintf(stderr, "FAIL: call to C_DigestInit() failed.\n");
	return rc;
    }

    switch (pMech->mechanism) {
    case CKM_SHA256_HMAC:

	rc = FunctionListFuncPtr->C_DigestKey(hSess, hGenKey);
	if (rc != CKR_OK) {
	    fprintf(stderr, "FAIL: call to C_DigestKey() failed.\n");
	    return rc;

	}
    default:
	break;
    }

    while (!feof(in))
    {
	bytes_read = fread(buffer, sizeof(buffer), 1, in);

	/* call C_DigestUpdate by pass in NULL to get message buffer size */
	rc = FunctionListFuncPtr->C_DigestUpdate(hSess, (CK_BYTE *)buffer, (unsigned long) bytes_read);
	if (rc != CKR_OK)
	{
	    fprintf (stderr, "FAIL: call to C_DigestUpdate() failed.\n");
	    return rc;
	}
	else {
	    printf ("call to C_DigestUpdate() succeeded for %d bytes\n", (int) bytes_read);
	}
    }	

    *messageLen = 0;
    /* first call C_DigestFinal by pass in NULL to get message buffer size */
    rc = FunctionListFuncPtr->C_DigestFinal(hSess, NULL, messageLen);
    if (rc != CKR_OK)
    {
	fprintf (stderr, "FAIL: 1st call to C_DigestFinal() failed.\n");
	return rc;
    }
    else {
	printf ("1st call to C_DigestFinal() succeeded: size = %u.\n", (unsigned int) *messageLen);
	*message = (CK_BYTE *)calloc( 1, sizeof(CK_BYTE) * *messageLen );
	if (!*message)
	    return CKR_HOST_MEMORY;
    }	

    /* then call C_Digest to get actual message */
    rc = FunctionListFuncPtr->C_DigestFinal(
	hSess,
	*message, messageLen
	);
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
 * Parameters: operation ... SHA256, SHA384, SHA512 and HMAC-SHA256
 * Returns: CK_RV
 ************************************************************************
 */
static CK_RV computeDigestFile(char *operation, char *filename, char *digest_file, char *expected)
{
    CK_BYTE         *pDigestBuf = NULL;
    FILE            *fp_read = NULL;
    FILE            *fp_write = NULL;
    CK_ULONG        digestLen;
    CK_RV           rc = CKR_OK;

    /* C_Digest */
    CK_MECHANISM	mechSHA256 = { CKM_SHA256, NULL, 0};
    CK_MECHANISM	mechSHA256hmac = { CKM_SHA256_HMAC, NULL, 0};
    CK_MECHANISM	mechSHA384 = { CKM_SHA384, NULL, 0};
    CK_MECHANISM	mechSHA512 = { CKM_SHA512, NULL, 0};
    CK_MECHANISM	*pmech = NULL;

    (void) expected;
	
    if (operation == NULL || *operation == 0
	|| strcmp(operation, "SHA256") == 0 ) {
	pmech = &mechSHA256;
	printf("Operation to be performed: %s\n", operation);
    } else if (strcmp(operation, "SHA512") == 0) {
	pmech = &mechSHA512;
	printf("Operation to be performed: %s\n", operation);
    } else if (strcmp(operation, "SHA384") == 0) {
	pmech = &mechSHA384;
	printf("Operation to be performed: %s\n", operation);
    } else if (strcmp(operation, "HMAC-SHA256") == 0) {
	pmech = &mechSHA256hmac;
	printf("Operation to be performed: %s\n", operation);
    } else {
	printf("Invalid operation: %s\n", operation);
	exit(4);
    }

    if (filename == NULL) {
	printf("Plain Text Default: \n");
	dumpHexArray(defPlainText, plaintextlen);
	rc = computeDigest(hSession, pmech, (CK_BYTE *) defPlainText, plaintextlen, &pDigestBuf, &digestLen);
    }
    else 
    {
	fp_read = strcmp(filename, "-") == 0 ? stdin : fopen(filename, "r");
	if (!fp_read) {
	    printf("Failed to open file %s.", filename);
	    return CKR_FUNCTION_FAILED;
	}
		
	if(digest_file != NULL)
	{
	    fp_write = fopen(digest_file, "w");

	    if(!fp_write) {
		printf("Failed to open file %s.", digest_file);
		if(fp_read) 	fclose(fp_read);
		return CKR_FUNCTION_FAILED;
	    }				
	}
	else
	{
	    fp_write = stdout;
	}
	              
	rc = computeDigestMultiPart(hSession, pmech, fp_read, &pDigestBuf, &digestLen);
	
	if(rc == CKR_OK && fp_write && pDigestBuf)
	{
	    fwrite(pDigestBuf, 1, digestLen, fp_write);
	}
	else if(rc != CKR_OK) {					
	    fprintf(stderr, "Digest Error: rc=%d.\n", (int)rc);
	    errorCount++;
	}
				
	if (pDigestBuf) {
	    free (pDigestBuf);
	    pDigestBuf = NULL;
	}
    }
		
    if(fp_read && fp_read != stdin)
	fclose(fp_read);

    if(fp_write)
	fclose(fp_write);

    return rc;
}


void usage()
{
    printf("Usage: vpkcs11_sample_digest -p pin [-s slotID] [-k keyName] [-m module_path] [-o operation] [-f input_file_name] [-d digest_file_name] [-e expected_digest]\n");
    printf("       operation...SHA256 (default) or SHA384 or SHA512 or HMAC-SHA256\n");
    exit(2);
}


/*
 ************************************************************************
 * Function: main
 ************************************************************************
 */
int main (int argc, char* argv[])
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
    char *expected = NULL;
    int   c;
    extern char *optarg;
    extern int optind;
    int loggedIn = 0;
    int failed = 0;
    int use_key = 0;

    while ((c = getopt(argc, argv, "p:k:m:o:f:i:s:c:r:d:K")) != EOF)
	switch (c) {
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
	    break;
	case 'f':
	    filename = optarg;
	    break;
	case 'e':
	    expected = optarg;
	    break;		
	case 'd':
	    digest_file = optarg;
	    break;
	case '?':
	default:
	    usage();
	    break;
	}

    
    use_key = (strcmp(operation, "HMAC-SHA256") == 0);

    if (NULL == pin || (use_key && NULL == keyLabel)) {
	usage();
    }
    if ((optind < argc))
    {
	usage();
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
	printf("Successfully logged in. use key = %d\n", use_key);

	while (use_key) {

	    printf("Looking for key \n");
	    hGenKey = findKey(keyLabel, CKO_SECRET_KEY);
	    if (CK_INVALID_HANDLE == hGenKey)
	    {
		printf("Key does not exist, creating key... Creating key \n");
		rc = createKey(keyLabel);
		if (rc != CKR_OK)
		{
		    printf("Failed to create key \n");
		    failed++;
		    break;
		}
		printf("Successfully created key.\n");
	    }
	    else {
		printf("Successfully found key.\n");
		break;
	    }
	}	
	rc = computeDigestFile(operation, filename, digest_file, expected);
	if (rc != CKR_OK)
	{
	    failed++;
	    break;
	}
	printf("Successfully computed digest\n");	
    } while (0);

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
