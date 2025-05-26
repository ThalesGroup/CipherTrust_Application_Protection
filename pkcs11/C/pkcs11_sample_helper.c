/*************************************************************************
**                                                                      **
** Sample code is provided for educational purposes.                    **
** No warranty of any kind, either expressed or implied by fact or law. **
** Use of this item is not restricted by copyright or license terms.    **
**                                                                      **
**************************************************************************/
/*
 ***************************************************************************
 * File: pkcs11_sample_helper.c
 ***************************************************************************

 ***************************************************************************
 * This file demonstrates the following
 * 1. Initialization
 * 2. Creating a connection and logging in.
 * 2. Close a connection and logging off.
 * 4. Clean up.
 ***************************************************************************
 */

#ifdef __linux__
#define _GNU_SOURCE
#endif
#include "pkcs11_sample_helper.h"
#include <stdarg.h>


/*
 **************************************************************************
 *   * Globals
 **************************************************************************
 */


#define MAX_FIND_RETURN 1000


#ifdef _WIN32
static HINSTANCE dllHandle = NULL;
#else
static void *dllPtr = NULL;
#endif


CK_FUNCTION_LIST_PTR    FunctionListFuncPtr = NULL;
static CK_ULONG         SlotCount = 0;
static CK_SLOT_ID_PTR   SlotList = NULL;

CK_SESSION_HANDLE       hSession = CK_INVALID_HANDLE;

static CK_UTF8CHAR      app[] = { "CADP_PKCS11_SAMPLE" };
CK_OBJECT_HANDLE        hGenKey = 0x0;
CK_BYTE		    def_iv[] =	"\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\x0C\x0D\x0E\x0F\x10\x00";
CK_ULONG        iv_length = 16;
CK_BYTE         def_gcm_iv[512] = "\xae\xc6\x12\xbe\x7c\x1d\xdb\x65\x9a\x4b\x31\x5c";
CK_BYTE		    def_aad[512] =	"\x38\x59\xb3\xc9\xd0\xb4\x2d\x45\xc4\x3e\x8e\xbd\x4c\x8c\xbd\xe1\xb6\xeb\x21\x06";
CK_ULONG        tag_bits = 96;
CK_ULONG        aad_length = 20;
CK_ULONG        gcm_iv_length = 12;
static char plainSerial[] = "0123456789-abcdefghijklmnopqrstuvwxyz;:,.ABCDEFGHIJKLMNOPQRSTUVWXYZ";

CK_BBOOL        bAlwaysSensitive = CK_FALSE;
CK_BBOOL        bNeverExtractable = CK_FALSE;

#ifdef _WIN32
static char *WinX64InstallPath = "C:\\Program Files\\CipherTrust\\CADP_for_C\\libcadp_pkcs11.dll";
#else
static char *UnixInstallPath = "/opt/CipherTrust/CADP_for_C/libcadp_pkcs11.so";
#endif

#define FPE_LITTLE_ENDIAN	1
#define FPE_BIG_ENDIAN		2

#define INT_LEN (10)
#define HEX_LEN (8)
#define BIN_LEN (32)
#define OCT_LEN (11)

int     opterr = 1;              /* if error message should be printed */
int     optind = 1;             /* index into parent argv vector */
int     optopt;                  /* character checked for validity */
int     optreset;                /* reset getopt */
char    *optarg;                /* argument associated with option */
unsigned long ulCachedTime = 10080;

#define BADCH   (int)'?'
#define BADARG  (int)':'
#define EMSG    ""

/*
************************************************************************
* Function: dumpHexArray
* Print out Hexical from a byte array
************************************************************************
* Parameters: array - a byte array, length - the length of byte array to dump
* Returns: none
************************************************************************
*/
void dumpHexArray(CK_BYTE* array, int length )
{
    int idx = 0;
    for ( idx = 0; idx < length; idx++)
    {
        printf ( "0x%02X|", *(array+idx));
    }
    printf ( "\n");
}

CK_BYTE_PTR hexStringArray(const char *hexstr, CK_ULONG *outlen)
{
    int i;
    int b;
    CK_BYTE_PTR out = NULL;
    int len = (int) strlen(hexstr);
    *outlen = len >> 1;
    if ((len & 0x00000001) != 0 || *outlen == 0)
    {
        printf("invalid or odd hex string\n");
        *outlen = 0;
        return out;
    }

    out = (CK_BYTE_PTR) calloc(*outlen, sizeof (CK_BYTE));
    for (i = 0; i < len; i += 2)
    {
        if (!isxdigit(hexstr[i]) || !isxdigit(hexstr[i + 1]))
        {
            printf("invalid charater in hex string\n");
            *outlen = 0;
            free(out);
            out = NULL;
            return out;
        }
        if (sscanf(hexstr + i, "%02x", &b) < 0)
        {
            printf("Failed to sscan hexstr\n");
        }
        out[i >> 1] = (char ) b;
    }
    return out;
}

/*
************************************************************************
* Function: findKeyByName
* Finds a key by its CKA_LABEL which corresponds to the name
* of the key displayed on the Key Manager.
* This function calls the findKey(label, type) to do 2 search from Key Manager,
* first search for symmetric key then search for asymmetric key
************************************************************************
* Parameters: keyLabel
* Returns: CK_OBJECT_HANDLE the key handle
************************************************************************
*/
CK_RV findKeyByLabel(char *keyLabel, CK_OBJECT_HANDLE *phKey, CK_OBJECT_CLASS *pObjClass)
{
    CK_RV rv = CKR_OK;
    rv = findKey(keyLabel, keyIdLabel, CKO_SECRET_KEY, phKey);
    if(*phKey != CK_INVALID_HANDLE)
    {
        *pObjClass = CKO_SECRET_KEY;
    }
    else
    {
        rv = findKey(keyLabel, keyIdLabel, CKO_PUBLIC_KEY, phKey);

        if(*phKey != CK_INVALID_HANDLE)
        {
            *pObjClass = CKO_PUBLIC_KEY;
        }
        else
        {
            *pObjClass = 0xffff;
        }
    }
    return rv;
}

/*
************************************************************************
* Function: setKeyStateAttribute
* Sets the key state.
************************************************************************
* Parameters: hKey
*             state
************************************************************************
*/
CK_RV setKeyStateAttribute(CK_OBJECT_HANDLE hKey, KeyState state)
{
    CK_RV        rc = CKR_OK;

    CK_ATTRIBUTE setAttrsTemplate[] =
    {
        {CKA_THALES_KEY_STATE, &state, sizeof(KeyState) }
    };

    CK_ULONG     setAttrsTemplateSize = sizeof(setAttrsTemplate) / sizeof(CK_ATTRIBUTE);

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

CK_RV setKeyAlias(CK_OBJECT_HANDLE hKey, char *alias)
{
    CK_RV        rc = CKR_OK;
    CK_ULONG     aliasLen = alias ? (CK_ULONG)strlen((const char *)alias) : 0;

    CK_ATTRIBUTE setAttrsTemplate[] =
    {
        {CKA_THALES_OBJECT_ALIAS, alias, aliasLen }
    };

    CK_ULONG     setAttrsTemplateSize = sizeof(setAttrsTemplate) / sizeof(CK_ATTRIBUTE);

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
        printf("Successfully %s key alias to: %s for key handle: %d.\n", alias?"set":"delete", alias?alias:"NULL", (int)hKey);
    }
    return rc;
}

CK_RV findKeyByVersion( char* keyLabel, CK_ULONG keyVersion, CK_OBJECT_HANDLE_PTR phKey )
{
    CK_RV rc = CKR_OK;

    CK_UTF8CHAR  *label = (CK_UTF8CHAR *) keyLabel;
    CK_ULONG len = (CK_ULONG) strlen(keyLabel);

    /* find the key by CKA_LABEL. */
    CK_ATTRIBUTE findKeyTemplate[] =
    {
        { CKA_LABEL, label, len },
        { CKA_THALES_KEY_VERSION, &keyVersion, sizeof(keyVersion) }
    };

    /* find the key by CKA_ID. */
    CK_ULONG            numOfObjReturned = 0;

    /* call FindObjectsFinal just in case there's another search ongoing for this session. */
    rc = FunctionListFuncPtr->C_FindObjectsFinal(hSession);
    if (rc != CKR_OK)
    {
        printf ("The first C_FindObjectsFinal  failed \n");
        goto FREE_RESOURCE;
    }

    rc = FunctionListFuncPtr->C_FindObjectsInit(
             hSession,
             (CK_ATTRIBUTE_PTR)&findKeyTemplate,
             2
         );
    if (rc != CKR_OK)
    {
        printf ("C_FindObjectsInit failed \n");
        goto FREE_RESOURCE;
    }

    /* loop thorugh C_FindObjcts until numOfObjReturned is 0 and we break out
     * of the loop. we expect to find only 1 private key that matches
     * the name.
     */

    while (CK_TRUE)
    {
        rc = FunctionListFuncPtr->C_FindObjects( hSession,
                phKey,
				MAX_FIND_RETURN,
                &numOfObjReturned );

        if (rc != CKR_OK )
        {
            printf ("C_FindObjects with unexpected result\n");
            goto FREE_RESOURCE;
        }

        if (numOfObjReturned == 0)
        {
            break;
        }
    }

    rc = FunctionListFuncPtr->C_FindObjectsFinal(hSession);

    if (rc != CKR_OK)
    {
        printf ("Call to C_FindObjectsFinal failed\n");
    }

FREE_RESOURCE:
    return rc;
}

/*
************************************************************************
* Function: findKeyByType
* Finds a key by its CKA_LABEL and CKA_CLASS which corresponds to the name and type
* of the key displayed on the Key Manager.
* The FindKey paradigm allows for only one Find to happen at one time in
* a session, so we have to call C_FindObjectsFinal first in case there is another
* dangling find.
* After that, we call C_FindObjectsInit and C_FindObjects
* C_FindObjects then returns a single key handle that corresponds to the key name.
************************************************************************
* Parameters: keyLabel and keyType
* Returns: CK_OBJECT_HANDLE the key handle
************************************************************************
*/

CK_RV findKeyByType( CK_OBJECT_CLASS keyType, CK_OBJECT_HANDLE phaKey[] )
{
    CK_RV rc = CKR_OK;

    /* find the key by CKA_LABEL. */

    CK_ATTRIBUTE findKeyTemplate[] =
    {
        {CKA_CLASS, &keyType, sizeof(keyType)}
    };

    CK_ULONG  findKeyTemplateSize = sizeof(findKeyTemplate)/sizeof(CK_ATTRIBUTE);

    /* find the key by CKA_ID. */
    CK_ULONG            numOfObjReturned = 0;

    /* call FindObjectsFinal just in case there's another search ongoing for this session. */
    rc = FunctionListFuncPtr->C_FindObjectsFinal(hSession);
    if (rc != CKR_OK)
    {
        fprintf (stderr, "FAIL: call to the first C_FindObjectsFinal() failed: %lu.\n", rc);
        phaKey[0] = CK_INVALID_HANDLE;
        return rc;
    }

    rc = FunctionListFuncPtr->C_FindObjectsInit(hSession,
            (CK_ATTRIBUTE_PTR)&findKeyTemplate,
            findKeyTemplateSize
                                               );
    if (rc != CKR_OK)
    {
        fprintf (stderr, "FAIL: call to C_FindObjectsInit() failed: %lu .\n", rc);
        phaKey[0] = CK_INVALID_HANDLE;
        return rc;
    }

    /* loop thorugh C_FindObjcts until numOfObjReturned is 0 and we break out
     * of the loop. we expect to find only 1  key that matches the name.
     */

    rc = FunctionListFuncPtr->C_FindObjects( hSession,
            phaKey,
            MAX_FIND_RETURN,
            &numOfObjReturned );

    if (rc != CKR_OK )
    {
        fprintf (stderr, "FAIL: call to C_FindObjects() with unexpected result Error: 0x%08x.\n", (unsigned int)rc);
        phaKey[0] = CK_INVALID_HANDLE;
        return rc;
    }

    fprintf (stdout, "SUCCESS: call to C_FindObjects() with %u of objects returned.\n", (unsigned int)numOfObjReturned);

    rc = FunctionListFuncPtr->C_FindObjectsFinal(hSession);

    if (rc != CKR_OK)
    {
        fprintf (stderr, "FAIL: Call to C_FindObjectsFinal failed: %lu.\n", rc);
        phaKey[0] = CK_INVALID_HANDLE;
    }
    return rc;
}

void
parse_ck_date(char *optarg, CK_DATE *pcDate)
{
    char* tok = strtok(optarg, "/-");

    if(tok) memcpy(pcDate->year, tok, 4);

    tok = strtok(NULL, "/-");
    if(tok) memcpy(pcDate->month, tok, 2);

    tok = strtok(NULL, "/-");
    if(tok) memcpy(pcDate->day, tok, 2);
}

int
parse_format_type(char *sel)
{
    int format_type = CKA_RAW_FORMAT;

    if(sel == NULL)
    {
        printf("Invalid format type.");
        return 0;
    }

    if(strncmp(sel, "pem", 3) == 0)
        format_type = CKA_THALES_PEM_FORMAT;
    else if(strncmp(sel, "der", 3) == 0)
        format_type = CKA_THALES_DER_FORMAT;
    else if(strncmp(sel, "p7b", 3) == 0)
        format_type = CKA_THALES_P7B_FORMAT;

    return format_type;
}

int
parse_ksid_sel(char *sel, char **ppKsid)
{
    int sid_type = keyIdLabel;

    if(sel == NULL || strlen(sel) <= 2 || sel[1] != ':' )
    {
        printf("Invalid key identifier input.\n");
        return 0;
    }

    switch (sel[0])
    {
        /* n is keyname */
    case 'n':
        sid_type = keyIdLabel;
        break;
    case 'u':
        sid_type = keyIdUuid;
        break;
    case 'i':
        sid_type = keyIdAttr;
        break;
    case 'm':
        sid_type = keyIdMuid;
        break;
    case 'k':
        sid_type = keyIdImport;
        break;
    case 'a':
        sid_type = keyIdAlias;
        break;

    default:
        sid_type = 0;
        printf("Invalid sid type input.\n");
        break;
    }

    *ppKsid = (sel+2);
    return sid_type;
}

char *
parse_key_class(char *key, CK_OBJECT_CLASS  *pObjCls)
{

    if( key == NULL || strlen(key) <= 2 )
    {
        printf("Invalid key identifier input.\n");
        return 0;
    }

    if(strchr(key, ':') == NULL || key[1] != ':')
    {
        *pObjCls = CKO_SECRET_KEY;
        return key;
    }
    else
    {
        switch(key[0])
        {
        case 's':
            *pObjCls = CKO_SECRET_KEY;
            break;
        case 'c':
            *pObjCls = CKO_PUBLIC_KEY;
            break;
        case 'v':
            *pObjCls = CKO_PRIVATE_KEY;
            break;

        default:
            return NULL;
        }

        return key+2;
    }
}

CK_KEY_TYPE getKeyType(char *keyType)
{
        if (strncmp(keyType, "AES", 3) == 0) return CKK_AES;
        else if (strncmp(keyType, "RSA", 3) == 0) return CKK_RSA;
        else if (strncmp(keyType, "EC", 2) == 0) return CKK_EC;
        else if (strncmp(keyType, "HMAC-SHA1", 9) == 0) return CKK_SHA_1_HMAC;
        else if (strncmp(keyType, "HMAC-SHA256", 11) == 0) return CKK_SHA256_HMAC;
        else if (strncmp(keyType, "HMAC-SHA384", 11) == 0) return CKK_SHA384_HMAC;
        else if (strncmp(keyType, "HMAC-SHA512", 11) == 0) return CKK_SHA512_HMAC;
}

CK_RV findKey( char* keySearchId, int keyidType, CK_OBJECT_CLASS keyType, CK_OBJECT_HANDLE *phKey )
{
    CK_RV rc = CKR_OK;
    CK_UTF8CHAR  *ksid = (CK_UTF8CHAR *) keySearchId;

    CK_ULONG ksid_len = keySearchId ? (CK_ULONG) strlen(keySearchId) : 0;

    /* find the key by CKA_ID. */
    CK_ULONG  numOfObjReturned = 0;
    CK_ATTRIBUTE_PTR findKeyTemplatePtr;
    CK_ULONG  findKeyTemplateSize;

    /* find the key by CKA_LABEL. */
    CK_ATTRIBUTE findKeyTemplatePass[] =
    {
        {CKA_LABEL, ksid, ksid_len},
        {CKA_CLASS, &keyType, sizeof(keyType)}
    };

    switch(keyidType)
    {
    case keyIdLabel:
        findKeyTemplatePass[0].type = CKA_LABEL;
        break;

    case keyIdAttr:
        findKeyTemplatePass[0].type = CKA_ID;
        break;

    case keyIdUuid:
        findKeyTemplatePass[0].type = CKA_THALES_OBJECT_UUID;
        break;

    case keyIdMuid:
        findKeyTemplatePass[0].type = CKA_THALES_OBJECT_MUID;
        break;

    case keyIdImport:
        findKeyTemplatePass[0].type = CKA_THALES_OBJECT_IKID;
        break;

    case keyIdAlias:
        findKeyTemplatePass[0].type = CKA_THALES_OBJECT_ALIAS;
        break;

    default:
        rc = CKR_ARGUMENTS_BAD;
        fprintf (stderr, "FAIL: call to the findKey() failed; rc=0x%8x; KeyId type : %x", (unsigned int)rc, keyidType);
        return rc;
    }

    findKeyTemplatePtr = findKeyTemplatePass;
    findKeyTemplateSize = sizeof(findKeyTemplatePass)/sizeof(CK_ATTRIBUTE);

    /* call FindObjectsFinal just in case there's another search ongoing for this session. */
    rc = FunctionListFuncPtr->C_FindObjectsFinal(hSession);
    if (rc != CKR_OK)
    {
        fprintf (stderr, "FAIL: call to the first C_FindObjectsFinal() failed; rc=0x%08x\n", (unsigned int)rc);
        *phKey = CK_INVALID_HANDLE;
        return rc;
    }

    rc = FunctionListFuncPtr->C_FindObjectsInit(hSession,
            findKeyTemplatePtr,
            findKeyTemplateSize
                                               );
    if (rc != CKR_OK)
    {
        fprintf (stderr, "FAIL: call to C_FindObjectsInit() failed: rc=0x%08x.\n", (unsigned int)rc);
        *phKey = CK_INVALID_HANDLE;
        return rc;
    }

    /* loop thorugh C_FindObjcts until numOfObjReturned is 0 and we break out
     * of the loop. we expect to find only 1  key that matches the name.
     */

    while (CK_TRUE)
    {
        rc = FunctionListFuncPtr->C_FindObjects( hSession,
                phKey,
                MAX_FIND_RETURN,
                &numOfObjReturned );

        if (rc != CKR_OK )
        {
            fprintf (stderr, "Error: call to C_FindObjects() returned %d objects with error; rc=0x%08x.\n", (int)numOfObjReturned, (unsigned int)rc);
        }

        if ((numOfObjReturned == 0) || (numOfObjReturned == 1))
        {
            break;
        }
    }

    rc = FunctionListFuncPtr->C_FindObjectsFinal(hSession);

    if (rc != CKR_OK)
    {
        fprintf (stderr, "FAIL: Call to C_FindObjectsFinal failed; rc=0x%08x.\n", (unsigned int)rc);
    }

    return rc;
}

/*
 ************************************************************************
 * Function: findKeysByCkaType
 * Finds the keys present on the CM by key type.
 ************************************************************************
 * Parameters: keytype, max number of objects, buffer for key handles returned  
 * 
 * Returns: CK_RV
 ************************************************************************
 */

CK_RV findKeysByCkaType(CK_KEY_TYPE keytype, CK_ULONG *numObjects, CK_OBJECT_HANDLE *phKeys)
{
    CK_RV rc = CKR_OK;

    /* find the key by CKA_ID. */
    CK_ULONG  numOfObjReturned = 0;
    CK_ATTRIBUTE_PTR findKeyTemplatePtr;
    CK_ULONG  findKeyTemplateSize;

    /* find the key by CKA_KEY_TYPE. */
    CK_ATTRIBUTE findKeyTemplatePass[] =
    {
        {CKA_KEY_TYPE, &keytype, sizeof(keytype)}
    };
    
	findKeyTemplatePtr = findKeyTemplatePass;
    findKeyTemplateSize = sizeof(findKeyTemplatePass)/sizeof(CK_ATTRIBUTE);

    /* call FindObjectsFinal just in case there's another search ongoing for this session. */
    rc = FunctionListFuncPtr->C_FindObjectsFinal(hSession);
    if (rc != CKR_OK)
    {
        fprintf (stderr, "FAIL: call to the first C_FindObjectsFinal() failed; rc=0x%08x\n", (unsigned int)rc);
        *phKeys = CK_INVALID_HANDLE;
        return rc;
    }

    rc = FunctionListFuncPtr->C_FindObjectsInit(hSession,
            findKeyTemplatePtr,
            findKeyTemplateSize
                                               );
    if (rc != CKR_OK)
    {
        fprintf (stderr, "FAIL: call to C_FindObjectsInit() failed: rc=0x%08x.\n", (unsigned int)rc);
        *phKeys = CK_INVALID_HANDLE;
        return rc;
    }

    /* loop thorugh C_FindObjcts until numOfObjReturned is 0 and we break out
     * of the loop. we expect to find only 1  key that matches the name.
     */

    while (CK_TRUE)
    {
        rc = FunctionListFuncPtr->C_FindObjects( hSession,
                phKeys,
                *numObjects,
                &numOfObjReturned);

        if (rc != CKR_OK )
        {
            fprintf (stderr, "Error: call to C_FindObjects() returned %d objects with error; rc=0x%08x.\n", (int)numOfObjReturned, (unsigned int)rc);
        }

        if ((numOfObjReturned == 0) || (numOfObjReturned <= *numObjects))
        {
			*numObjects = numOfObjReturned;
            break;
        }
    }

    rc = FunctionListFuncPtr->C_FindObjectsFinal(hSession);

    if (rc != CKR_OK)
    {
        fprintf (stderr, "FAIL: Call to C_FindObjectsFinal failed; rc=0x%08x.\n", (unsigned int)rc);
    }

    return rc;
}


CK_RV findKeysByIdAttr(char* keySearchId, CK_ULONG *numObjects, CK_OBJECT_HANDLE *phKeys)
{
    CK_RV rc = CKR_OK;
    CK_UTF8CHAR  *ksid = (CK_UTF8CHAR *) keySearchId;
    CK_ULONG ksid_len = keySearchId ? (CK_ULONG) strlen(keySearchId) : 0;

    /* find the key by CKA_ID. */
    CK_ULONG  numOfObjReturned = 0;
    CK_ATTRIBUTE_PTR findKeyTemplatePtr;
    CK_ULONG  findKeyTemplateSize;

    /* find the key by CKA_LABEL. */
    CK_ATTRIBUTE findKeyTemplatePass[] =
    {
        {CKA_ID, ksid, ksid_len}
    };

	findKeyTemplatePtr = findKeyTemplatePass;
    findKeyTemplateSize = sizeof(findKeyTemplatePass)/sizeof(CK_ATTRIBUTE);

    /* call FindObjectsFinal just in case there's another search ongoing for this session. */
    rc = FunctionListFuncPtr->C_FindObjectsFinal(hSession);
    if (rc != CKR_OK)
    {
        fprintf (stderr, "FAIL: call to the first C_FindObjectsFinal() failed; rc=0x%08x\n", (unsigned int)rc);
        *phKeys = CK_INVALID_HANDLE;
        return rc;
    }

    rc = FunctionListFuncPtr->C_FindObjectsInit(hSession,
            findKeyTemplatePtr,
            findKeyTemplateSize
                                               );
    if (rc != CKR_OK)
    {
        fprintf (stderr, "FAIL: call to C_FindObjectsInit() failed: rc=0x%08x.\n", (unsigned int)rc);
        *phKeys = CK_INVALID_HANDLE;
        return rc;
    }

    /* loop thorugh C_FindObjcts until numOfObjReturned is 0 and we break out
     * of the loop. we expect to find only 1  key that matches the name.
     */

    while (CK_TRUE)
    {
        rc = FunctionListFuncPtr->C_FindObjects( hSession,
                phKeys,
                *numObjects,
                &numOfObjReturned);

        if (rc != CKR_OK )
        {
            fprintf (stderr, "Error: call to C_FindObjects() returned %d objects with error; rc=0x%08x.\n", (int)numOfObjReturned, (unsigned int)rc);
        }

        if ((numOfObjReturned == 0) || (numOfObjReturned <= *numObjects))
        {
			*numObjects = numOfObjReturned;
            break;
        }
    }

    rc = FunctionListFuncPtr->C_FindObjectsFinal(hSession);

    if (rc != CKR_OK)
    {
        fprintf (stderr, "FAIL: Call to C_FindObjectsFinal failed; rc=0x%08x.\n", (unsigned int)rc);
    }

    return rc;
}

/*
 ************************************************************************
 * Function: deleteKey
 * Delete key from the Key Manager by key handle.
 ************************************************************************
 * Parameters: hKey -- the handle of the key on Key Manager to be deleted
 * Returns: CK_RV
 ************************************************************************
 */

CK_RV deleteKey (CK_OBJECT_HANDLE hKey, CK_BBOOL bSetKeyState)
{
    CK_RV rc;

    if(bSetKeyState == CK_TRUE)
    {
        rc = setKeyStateAttribute(hKey, (KeyState) 3 /* deactivated */);
        if (rc != 0)
        {
            fprintf (stderr, "FAIL: setKeyStateAttribute failed: %u\n", (unsigned int)hKey);
        }
    }

    rc = FunctionListFuncPtr->C_DestroyObject (hSession, hKey);
    if (rc != 0)
    {
        fprintf (stderr, "FAIL:  C_DestroyObject failed: %u\n", (unsigned int)hKey);
    }
    return rc;
}

/*
**************************************************************************
 * Function: cleanup
 * Cleans up the local memory, and unloads the dll
 *************************************************************************
 * Parameters: none
 * Return: CK_RV rc
 *************************************************************************
 */

void cleanup ()
{
    if (hSession != CK_INVALID_HANDLE)
        FunctionListFuncPtr->C_CloseSession (hSession);
    if (SlotList)
    {
        free (SlotList);
        SlotList = NULL;
    }
    if (FunctionListFuncPtr)
        FunctionListFuncPtr->C_Finalize(NULL);
#ifdef __WINDOWS__
    if (dllHandle)
        FreeLibrary (dllHandle);
#else
    if (dllPtr)
        dlclose (dllPtr);
#endif

}

/*
**************************************************************************
* Function: isFileExist
* Check if the file exist
*************************************************************************
* Parameters: char* path
* Return: 1 : true, 0 : false
*************************************************************************
*/
int isFileExist(char* path )
{
#ifdef _WIN32
    struct _stat buffer;
    return (_stat( path, &buffer) == 0);
#else
    struct stat buffer;
    return (stat( path, &buffer) == 0);
#endif
}

/*
**************************************************************************
* Function: getPKCS11LibPath
* Determine the path of CADP PKCS11 library path base on following priorities:
* 1. From command line input parameter libPath
* 2. From the environment variable $PKCS11LIBPATH
* 3. From default installation location of CADP PKCS11 library
*************************************************************************
* Parameters: char* path
* Return: 1 : true, 0 : false
*************************************************************************
*/
char* getPKCS11LibPath(char* libPath)
{
    static char * path = NULL;
    char *pathFromEnv = NULL;

    if ( path != NULL )
    {
        return path;
    }
    if (( libPath != NULL ) && (strcmp(libPath, "") != 0))
    {
        path = libPath;
    }
    else
    {
        pathFromEnv = getenv("PKCS11LIBPATH");
        if (pathFromEnv != NULL && strnlen(pathFromEnv, 1024) < 1024)
        {
            path = pathFromEnv;
            for (; *pathFromEnv; pathFromEnv++)
            {
                if (!isprint(*pathFromEnv))
                {
                    path = NULL;
                    break;
                }
            }
        }

        if (( path == NULL ) || (strcmp(path, "") == 0))
        {
            /*  try to determine by default installation on windows or Unix */
#ifdef _WIN32
            if ( isFileExist(WinX64InstallPath))
            {
                path = WinX64InstallPath;
            }
            else
            {
                fprintf(stderr, "FAIL: WinX64InstallPath point to a file that does not exist: %s.", WinX64InstallPath);
                exit(2);
            }
#else
            if ( isFileExist(UnixInstallPath))
            {
                path = UnixInstallPath;
            }
            else
            {
                fprintf(stderr, "FAIL: UnixInstallPath point to a file that does not exist: %s.", UnixInstallPath);
                exit(3);
            }
#endif
        }
        else
        {
            if ( isFileExist(path) )
            {
                /* file found , okay to return */
            }
            else
            {
                fprintf(stderr, "FAIL: PKCS11LIBPATH point to a file that does not exist: %s.", path);
                exit(4);
            }
        }
    }
    printf("Using PKCS11 library at path: %s\n" , path);
    return path;
}

/*
************************************************************************
 * Function: initPKCS11Library
 * Loads the dll and gets the function list from the DLL
 ***********************************************************************
 * Parameters: const char* filename -- location of the DLL
 * Returns: CK_RV rc
 ***********************************************************************
 */

CK_RV initPKCS11Library (const char* filename)
{
    CK_RV rc;
    CK_VOID_PTR pInitArgs = NULL_PTR;
    CK_C_INITIALIZE_ARGS initArgs;
    CK_C_GetFunctionList get_function_list;

#ifdef _WIN32
    dllHandle = LoadLibrary (filename);
    if (!dllHandle)
    {
        fprintf(stderr, "FAIL: Cannot Load Library %s.\n", filename);
        return CKR_FUNCTION_FAILED;
    }

    get_function_list = (CK_C_GetFunctionList)
                        GetProcAddress(dllHandle, "C_GetFunctionList");

#else
    dllPtr = dlopen (filename, RTLD_NOW);
    if (!dllPtr)
    {
        fprintf(stderr, " FAIL: call to dlopen() failed because %s.\n", dlerror());
        return CKR_FUNCTION_FAILED;
    }
    get_function_list = (CK_C_GetFunctionList)
                        dlsym( dllPtr, "C_GetFunctionList" );

#endif

    if (!get_function_list)
    {
        fprintf(stderr, "FAIL: Cannot get Function List from library.\n");
        return CKR_FUNCTION_FAILED;
    }

    get_function_list(&FunctionListFuncPtr);
    initArgs.flags = CKF_DISABLE_FIPS;
    initArgs.pReserved = NULL_PTR;
    pInitArgs = (CK_C_INITIALIZE_ARGS_PTR)&initArgs;
    rc = FunctionListFuncPtr->C_Initialize (pInitArgs);

    return rc;
}

/*
 ************************************************************************
 * Function: initSlotList
 * Gets the slot list from the Key Manager. The Key Manager will only have 1 slot.
 ************************************************************************
 * Parameters: none
 * returns: CK_RV
 ************************************************************************
 */

CK_RV  initSlotList (void)
{
    CK_RV rc = CKR_OK;
    CK_ULONG mechCount = 0;
    CK_MECHANISM_TYPE_PTR mechList = NULL;

    /* First get the number of slots by passing in NULL in FALSE and NULL */
    rc = FunctionListFuncPtr->C_GetSlotList (CK_FALSE, NULL_PTR, &SlotCount);
    if (rc != CKR_OK)
    {
        printf ("Error getting number of slots\n");
        return rc;
    }

    /* now that we know the number of slots, allocate space. */
    SlotList = (CK_SLOT_ID_PTR) malloc (SlotCount * sizeof (CK_SLOT_ID));

    /* get the actual slot list */
    rc = FunctionListFuncPtr->C_GetSlotList (TRUE, SlotList, &SlotCount);

    if (rc != CKR_OK)
    {
        printf ("Unable to get Slot List\n");
    }

    /* get the mechanism list, only obtain for slot id 0 */
    rc = FunctionListFuncPtr->C_GetMechanismList (0, NULL, &mechCount);

    if (rc != CKR_OK)
    {
        printf ("Unable to get Mechanism List Count\n");
    }

    if(mechCount <= 0)
    {
        printf ("Mechanism List Count error; mechCount: %d\n", (int)mechCount);
        return rc;
    }

    mechList = (CK_MECHANISM_TYPE_PTR)calloc(mechCount, sizeof(CK_MECHANISM_TYPE));

    rc = FunctionListFuncPtr->C_GetMechanismList (0, mechList, &mechCount);
    if (rc != CKR_OK)
    {
        printf ("Error getting Mechanism List \n");
    }
    else
    {
        /*	if(mechList != NULL)
        {
        	for(i =0; i<mechCount; i++)
        	{
        		printf("Mechanism %d: 0x%x\n", i, (unsigned int)mechList[i]);
        	}
        	} */
    }
    if(mechList)
        free(mechList);
    return rc;
}


/*
 ************************************************************************
 * Function: openSessionAndLogin
 ************************************************************************
 * Opens a session on the Key Manager and logs in as a user.
 * Sets the session handle global to be used for the remainder of this program.
 * The password for user login is the password specified to the Key Manager
 * during agent registration.
 ************************************************************************
 * Parameters: none
 * Returns: CK_RV
 ************************************************************************
 */
CK_RV openSessionAndLogin ( char* pin, int slotId )
{
    CK_RV rc = CKR_OK;
    rc = FunctionListFuncPtr->C_OpenSession ( SlotList[slotId],
            0,
            (void *)"pkcs11_sample_session",
            NULL_PTR,
            &hSession
                                            );
    if (rc != CKR_OK)
    {
        printf ("Unable to OpenSession\n");
        return rc;
    }
    rc = FunctionListFuncPtr->C_Login (
             hSession,
             CKU_USER,
             (CK_UTF8CHAR *)pin,
             (CK_ULONG)strlen(pin)
         );
    if (rc != CKR_OK)
    {
        printf ("Unable to login\n");
    }
    return rc;
}

CK_RV getAsymAttributesValue(CK_OBJECT_HANDLE hKey, CK_OBJECT_CLASS	 objClass, CK_BYTE modulusBuf[], CK_ULONG * pModulusBufSize,
                             CK_BYTE pubExponentBuf[], CK_ULONG *ppubExponentBufSize, CK_BYTE privExponentBuf[], CK_ULONG *pprivExponentBufSize)
{
    CK_RV		rc = CKR_OK;
    CK_ULONG	modulusBits = MODULUS_BITS;

    char        keyUuid[128];
    char        keyMuid[128];
    char        keyImportedId[128];
    char        keyAlias[256];
    CK_BYTE     keyIdBuf[256];

    char        keyLabel[256]= {0};
    char        custom1[1024]= {0};
    char        custom2[1024]= {0};
    char        custom3[1024]= {0};
    char        custom4[1024]= {0};
    char        custom5[1024]= {0};
    unsigned int i, pubExponentIdx, privExponentIdx;

    CK_BBOOL    bEncrypt,bUnwrap,bToken,bWrap,bVerify;
    CK_BBOOL    bCacheOnHost;

    CK_ULONG    attrValueLen;
    CK_ULONG    ulCachedTime = 0;

    char       *pAttr = NULL;
    CK_BYTE    curveId[64] = {0};
    CK_KEY_TYPE keytype = CKK_RSA;

    CK_ATTRIBUTE getAttrsTemplate[] =
    {
        {CKA_ID, keyIdBuf, sizeof(keyIdBuf) },                              /*  0 */
        {CKA_LABEL, (CK_UTF8CHAR *)keyLabel, sizeof(keyLabel) },
        {CKA_CLASS, &objClass, sizeof(objClass) },
        {CKA_KEY_TYPE, &keytype, sizeof(keytype) },

        {CKA_THALES_OBJECT_UUID, keyUuid, sizeof(keyUuid)},                       /*  4 */
        {CKA_THALES_OBJECT_MUID, keyMuid, sizeof(keyMuid)},                       /*  5 */
        {CKA_THALES_OBJECT_ALIAS, keyAlias, sizeof(keyAlias)},                    /*  6 */
        {CKA_THALES_OBJECT_IKID, keyImportedId, sizeof(keyImportedId)},           /*  7 */

        {CKA_THALES_CUSTOM_1, custom1, sizeof(custom1)},
        {CKA_THALES_CUSTOM_2, custom2, sizeof(custom2)},
        {CKA_THALES_CUSTOM_3, custom3, sizeof(custom3)},                    /*  */
        {CKA_THALES_CUSTOM_4, custom4, sizeof(custom4)},
        {CKA_THALES_CUSTOM_5, custom5, sizeof(custom5)},
        {CKA_ENCRYPT, &bEncrypt,sizeof(bEncrypt)},
        {CKA_UNWRAP,  &bUnwrap, sizeof(bUnwrap)},
        {CKA_TOKEN,   &bToken,  sizeof(bToken)},
        {CKA_WRAP,    &bWrap,   sizeof(bWrap)},
        {CKA_VERIFY,  &bVerify, sizeof(bVerify)},

        {CKA_THALES_CACHED_ON_HOST, &bCacheOnHost,   sizeof(bCacheOnHost)},       /*   */
        {CKA_THALES_KEY_CACHED_TIME, &ulCachedTime,  sizeof(ulCachedTime)},

        {CKA_MODULUS_BITS, &modulusBits, sizeof(modulusBits)},
        {CKA_MODULUS, modulusBuf, *pModulusBufSize },
        {CKA_EC_PARAMS, curveId, 64 },
        {CKA_PUBLIC_EXPONENT, pubExponentBuf, *ppubExponentBufSize },
        {CKA_PRIVATE_EXPONENT, privExponentBuf, *pprivExponentBufSize }
    };

    CK_ULONG getAttrsTemplateSize = sizeof(getAttrsTemplate)/sizeof(CK_ATTRIBUTE);

    pubExponentIdx = getAttrsTemplateSize-2;
    privExponentIdx = getAttrsTemplateSize-1;

    if(objClass == CKO_SECRET_KEY)
    {
        getAttrsTemplateSize -= 4;
    }
 
    rc = FunctionListFuncPtr->C_GetAttributeValue(hSession,
            hKey,
            getAttrsTemplate,
            getAttrsTemplateSize);

    if (rc != CKR_OK)
    {
        printf ("Error getting key attributes: %08x.\n", (unsigned int)rc);
        return rc;
    }

    printf("Key Handle: %08x,\n", (unsigned int)hKey);
    printf("CKA_LABEL: '%.*s'\n", (int) getAttrsTemplate[1].ulValueLen, keyLabel);
    printf("CKA_CLASS: %08x.\n", (unsigned int)objClass);
  
    printf("CKA_THALES_OBJECT_UUID:  '%.*s'\n", (int)getAttrsTemplate[4].ulValueLen, keyUuid);
    printf("CKA_THALES_OBJECT_MUID:  '%.*s'\n", (int)getAttrsTemplate[5].ulValueLen, keyMuid);
    printf("CKA_THALES_OBJECT_ALIAS: '%.*s'\n", (int)getAttrsTemplate[6].ulValueLen, keyAlias);
    printf("CKA_THALES_OBJECT_IKID:  '%.*s'\n", (int)getAttrsTemplate[7].ulValueLen, keyImportedId);

    printf("CKA_THALES_CACHE_ON_HOST:  %s\n", bCacheOnHost==CK_TRUE ? "Yes" : "No" );
    printf("CKA_THALES_CACHED_TIME:  %u.\n", (unsigned int)ulCachedTime);

    if(objClass != CKO_SECRET_KEY)
    {
        if (keytype == CKK_EC) {
            printf("CKA_EC_PARAMS: '%.*s'\n", (int) getAttrsTemplate[getAttrsTemplateSize-3].ulValueLen, curveId);
        } else {
            printf("CKA_MODULUS: ");
            attrValueLen = getAttrsTemplate[getAttrsTemplateSize-4].ulValueLen;
            printf( " %u, ", (unsigned int)attrValueLen );
            *pModulusBufSize = attrValueLen;

            pAttr = (char *)calloc(sizeof(CK_BYTE), attrValueLen*2+1);
            if(pAttr == NULL)
            {
                printf("Error allocating memory.");
                return CKR_HOST_MEMORY;
            }

            for(i = 0; i<attrValueLen; i++)
            {
                snprintf(pAttr+i*2, 3, "%02x", modulusBuf[i]);
            }
            pAttr[i*2] = '\0';
            printf("\t %s.\n", pAttr);
            if(pAttr)
            {
                free(pAttr);
                pAttr = NULL;
            }

            if( objClass == CKO_PUBLIC_KEY ){
                printf("CKA_PUBLIC_EXPONENT: ");
                attrValueLen = getAttrsTemplate[pubExponentIdx].ulValueLen;
                printf( " %u, ", (unsigned int)attrValueLen );
                *ppubExponentBufSize = attrValueLen;
           
                pAttr = (char *)calloc(sizeof(CK_BYTE), attrValueLen*2+1);
                if(pAttr == NULL)
                {
                    printf("Error allocating memory.");
                    return CKR_HOST_MEMORY;
                }
           
                for(i = 0; i<attrValueLen; i++)
                {
                    snprintf(pAttr+i*2, 3, "%02x", pubExponentBuf[i]);
                }
                pAttr[i*2] = '\0';
                printf("\t %s.\n", pAttr);
           
                if(pAttr)
                {
                    free(pAttr);
                    pAttr = NULL;
                }
            }
            else if( objClass == CKO_PRIVATE_KEY ){
                printf("CKA_PUBLIC_EXPONENT: ");
                attrValueLen = getAttrsTemplate[pubExponentIdx].ulValueLen;
                printf( " %u, ", (unsigned int)attrValueLen );
                *ppubExponentBufSize = attrValueLen;
           
                pAttr = (char *)calloc(sizeof(CK_BYTE), attrValueLen*2+1);
                if(pAttr == NULL)
                {
                    printf("Error allocating memory.");
                    return CKR_HOST_MEMORY;
                }
           
                for(i = 0; i<attrValueLen; i++)
                {
                    snprintf(pAttr+i*2, 3, "%02x", pubExponentBuf[i]);
                }
                pAttr[i*2] = '\0';
                printf("\t %s.\n", pAttr);
           
                if(pAttr)
                {
                    free(pAttr);
                    pAttr = NULL;
                }
                printf("CKA_PRIVATE_EXPONENT: ");
                attrValueLen = getAttrsTemplate[privExponentIdx].ulValueLen;
                printf( " %u, ", (unsigned int)attrValueLen );
                *pprivExponentBufSize = attrValueLen;
           
                pAttr = (char *)calloc(sizeof(CK_BYTE), attrValueLen*2+1);
                if(pAttr == NULL)
                {
                    printf("Error allocating memory.");
                    return CKR_HOST_MEMORY;
                }
           
                for(i = 0; i<attrValueLen; i++)
                {
                    snprintf(pAttr+i*2, 3, "%02x", privExponentBuf[i]);
                }
                pAttr[i*2] = '\0';
                printf("\t %s.\n", pAttr);
           
                if(pAttr)
                {
                    free(pAttr);
                    pAttr = NULL;
                }
            }
            printf("CKA_MODULUS_BITS: %u.\n", (unsigned int)modulusBits);
        }
    }
    printf("CKA_THALES_CUSTOM_1: %.*s\n", (int)getAttrsTemplate[7].ulValueLen, custom1);
    printf("CKA_THALES_CUSTOM_2: %.*s\n", (int)getAttrsTemplate[8].ulValueLen, custom2);
    printf("CKA_THALES_CUSTOM_3: %.*s\n", (int)getAttrsTemplate[9].ulValueLen, custom3);
    printf("CKA_THALES_CUSTOM_4: %.*s\n", (int)getAttrsTemplate[10].ulValueLen, custom4);
    printf("CKA_THALES_CUSTOM_5: %.*s\n", (int)getAttrsTemplate[11].ulValueLen, custom5);

    printf("CKA_ENCRYPT: %s\n", bEncrypt ? "true" : "false");
    printf("CKA_UNWRAP:  %s\n", bUnwrap  ? "true" : "false");
    printf("CKA_TOKEN:   %s\n", bToken   ? "true" : "false");
    printf("CKA_WRAP:    %s\n", bWrap    ? "true" : "false");
    printf("CKA_VERIFY:  %s\n", bVerify  ? "true" : "false");

    return rc;
}

CK_RV getSymAttributesValue(CK_OBJECT_HANDLE hKey, CK_ULONG keyDateCount, CK_ATTRIBUTE_TYPE attrTypes[], char *pKeyLabelOut)
{
    CK_RV		rc = CKR_OK;
    CK_DATE     createDate = {0}, endDate = {0};
    CK_BYTE     keyIdBuf[256];
    char        keyLabel[256];
    char        keyUuid[128];
    char        keyMuid[128];
    char        keyImportedId[128];
    char        keyAlias[256];
    CK_ULONG    ulCachedTime, i;
    CK_ULONG    ulLifeSpan=0;
    CK_OBJECT_CLASS	keyCls;
    CK_LONG     lKeyVersion;
    char        ch_year[5];
    char        ch_mon[3];
    char        ch_mday[3];

    char        serialno[256]= {0};
    char        custom[5][1024] = { 0 };

    CK_BBOOL    bCacheOnHost, bVersioned, blaSensitive, blnExtractable;
    int         custom1Index = 19;

    CK_ULONG    ulCreationTime, ulDeactivateTime = 0;
    CK_ATTRIBUTE_PTR pKeyTemplate = NULL;
    CK_DATE     keyTransDates[KEY_TRANS_DATES_MAX];
    char        *pKeyDateDesc = NULL;

    CK_ATTRIBUTE getAttrsTemplate[] =
    {
        {CKA_ID, keyIdBuf, sizeof(keyIdBuf) },                                    /*  0 */
        {CKA_LABEL, keyLabel, sizeof(keyLabel) },                                 /*  1 */
        {CKA_SERIAL_NUMBER, serialno, sizeof(serialno)},
        {CKA_CLASS, &keyCls, sizeof(keyCls) },                                    /*  3 */

        {CKA_THALES_DATE_OBJECT_CREATE, &createDate, sizeof(createDate)},
        {CKA_THALES_DATE_KEY_DEACTIVATION, &endDate, sizeof(endDate)},
        {CKA_THALES_CACHED_ON_HOST, &bCacheOnHost,   sizeof(bCacheOnHost)},       /*  6 */
        {CKA_THALES_KEY_CACHED_TIME, &ulCachedTime,  sizeof(ulCachedTime)},
        {CKA_THALES_OBJECT_UUID, keyUuid, sizeof(keyUuid)},                       /*  8 */
        {CKA_THALES_OBJECT_MUID, keyMuid, sizeof(keyMuid)},
        {CKA_THALES_OBJECT_ALIAS, keyAlias, sizeof(keyAlias)},                    /*  10 */
        {CKA_THALES_OBJECT_IKID, keyImportedId, sizeof(keyImportedId)},           /* 11 */
        {CKA_THALES_KEY_VERSION, &lKeyVersion, sizeof(lKeyVersion)},		      /* 12 */
        {CKA_THALES_KEY_VERSION_LIFE_SPAN, &ulLifeSpan, sizeof ulLifeSpan},       /* 13 */
        {CKA_THALES_VERSIONED_KEY, &bVersioned, sizeof(bVersioned) },             /* 14 */
        {CKA_THALES_DATE_OBJECT_CREATE_EL, &ulCreationTime,  sizeof(ulCreationTime)},
        {CKA_THALES_DATE_KEY_DEACTIVATION_EL, &ulDeactivateTime,  sizeof(ulDeactivateTime)},

        {CKA_ALWAYS_SENSITIVE,	&blaSensitive,	sizeof(CK_BBOOL)	},
        {CKA_NEVER_EXTRACTABLE,	&blnExtractable,	sizeof(CK_BBOOL)	},

        {CKA_THALES_CUSTOM_1, custom[0], sizeof(custom[0])},                          /* 17 */
        {CKA_THALES_CUSTOM_2, custom[1], sizeof(custom[1])},
        {CKA_THALES_CUSTOM_3, custom[2], sizeof(custom[2])},
        {CKA_THALES_CUSTOM_4, custom[3], sizeof(custom[3])},                          /* 20 */
        {CKA_THALES_CUSTOM_5, custom[4], sizeof(custom[4])}		                      /* 21 */
    };
    CK_ULONG getAttrsTemplateSize = sizeof(getAttrsTemplate)/sizeof(CK_ATTRIBUTE);

    pKeyTemplate = (CK_ATTRIBUTE_PTR)calloc( (getAttrsTemplateSize + keyDateCount), sizeof(CK_ATTRIBUTE) );
    if(!pKeyTemplate)
    {
        printf ("Error allocating memory for pKeyTemplate!\n");
        return CKR_HOST_MEMORY;
    }

    for(i=0; i<getAttrsTemplateSize; i++)
    {
        pKeyTemplate[i].type = getAttrsTemplate[i].type;
        pKeyTemplate[i].pValue = getAttrsTemplate[i].pValue;
        pKeyTemplate[i].ulValueLen = getAttrsTemplate[i].ulValueLen;
    }

    for(i=0; i<keyDateCount; i++ )
    {
        pKeyTemplate[getAttrsTemplateSize+i].type = attrTypes[i];
        pKeyTemplate[getAttrsTemplateSize+i].pValue = &keyTransDates[i];
        pKeyTemplate[getAttrsTemplateSize+i].ulValueLen = sizeof(CK_DATE);
    }

    getAttrsTemplateSize += keyDateCount;

    rc = FunctionListFuncPtr->C_GetAttributeValue(hSession,
            hKey,
            pKeyTemplate,
            getAttrsTemplateSize);

    if (rc != CKR_OK)
    {
        printf ("Error getting key attributes: %08x.\n", (unsigned int)rc);
        return rc;
    }

    printf("CKA_ID: '%.*s'\n", (int)pKeyTemplate[0].ulValueLen, keyIdBuf);
    printf("CKA_LABEL: '%.*s'\n", (int)pKeyTemplate[1].ulValueLen, keyLabel);
    printf("CKA_SERIAL_NUMBER: '%.*s'\n", (int)pKeyTemplate[2].ulValueLen, serialno);

    if (pKeyLabelOut)
    {
        strncpy(pKeyLabelOut, keyLabel, (size_t) pKeyTemplate[1].ulValueLen);
        pKeyLabelOut[pKeyTemplate[1].ulValueLen] = '\0';
    }
    printf("CKA_CLASS: %08x\n", (unsigned int)keyCls);

    memcpy(ch_year, createDate.year, sizeof(createDate.year));
    ch_year[4] = '\0';
    memcpy(ch_mon, createDate.month, sizeof(createDate.month));
    ch_mon[2] = '\0';
    memcpy(ch_mday, createDate.day, sizeof(createDate.day));
    ch_mday[2] = '\0';
    printf("CKA_THALES_DATE_OBJECT_CREATE: year: %s, month: %s, day: %s\n", ch_year, ch_mon, ch_mday);
    printf("CKA_THALES_DATE_OBJECT_CREATE_EL, Creation Time: %u.\n", (unsigned int)ulCreationTime);

    memcpy(ch_year, endDate.year, sizeof(endDate.year));
    ch_year[4] = '\0';
    memcpy(ch_mon, endDate.month, sizeof(endDate.month));
    ch_mon[2] = '\0';
    memcpy(ch_mday, endDate.day, sizeof(endDate.day));
    ch_mday[2] = '\0';
    printf("CKA_THALES_DATE_KEY_DEACTIVATION: year: %s, month: %s, day: %s\n", ch_year, ch_mon, ch_mday);
    printf("CKA_THALES_DATE_KEY_DEACTIVATION_EL, Deactivation Time: %u.\n", (unsigned int)ulDeactivateTime);

    printf("CKA_THALES_CACHE_ON_HOST:  %s\n", bCacheOnHost==CK_TRUE ? "Yes" : "No" );
    printf("CKA_THALES_VERSIONED_KEY:  %s\n", bVersioned  ? "true" : "false");
    printf("CKA_THALES_CACHED_TIME:  %u\n", (unsigned int)ulCachedTime);

    printf("CKA_NEVER_EXTRACTABLE: \t%s\n", blnExtractable  ? "true" : "false");
    printf("CKA_ALWAYS_SENSITIVE:  \t%s\n", blaSensitive  ? "true" : "false");

    printf("CKA_THALES_OBJECT_UUID:  '%.*s'\n", (int)pKeyTemplate[ 8].ulValueLen, keyUuid);
    printf("CKA_THALES_OBJECT_MUID:  '%.*s'\n", (int)pKeyTemplate[ 9].ulValueLen, keyMuid);
    printf("CKA_THALES_OBJECT_ALIAS: '%.*s'\n", (int)pKeyTemplate[10].ulValueLen, keyAlias);
    printf("CKA_THALES_OBJECT_IKID:  '%.*s'\n", (int)pKeyTemplate[11].ulValueLen, keyImportedId);

    printf("CKA_THALES_KEY_VERSION: %d\n", (int)lKeyVersion);

    if ((int)pKeyTemplate[13].ulValueLen > -1)
        printf("CKA_THALES_KEY_VERSION_LIFE_SPAN: %lu\n", ulLifeSpan);

    for(i=0; i<5; i++)
    {
        custom[i][(int)pKeyTemplate[custom1Index+i].ulValueLen] = 0;
        printf("CKA_THALES_CUSTOM_%d: '%s' (length %d)\n", (int)i+1, custom[i], (int)pKeyTemplate[custom1Index+i].ulValueLen);
    }

    for(i=0; i<keyDateCount; i++ )
    {

        memcpy(ch_year, keyTransDates[i].year, sizeof(endDate.year));
        ch_year[4] = '\0';
        memcpy(ch_mon, keyTransDates[i].month, sizeof(endDate.month));
        ch_mon[2] = '\0';
        memcpy(ch_mday, keyTransDates[i].day, sizeof(endDate.day));
        ch_mday[2] = '\0';

        if(attrTypes[i] == 0) continue;

        switch(attrTypes[i])
        {
        case CKA_THALES_DATE_OBJECT_CREATE:
            pKeyDateDesc = "CKA_THALES_DATE_OBJECT_CREATE";
            break;
        case CKA_THALES_DATE_OBJECT_DESTROY:
            pKeyDateDesc = "CKA_THALES_DATE_OBJECT_DESTROY";
            break;
        case CKA_THALES_DATE_KEY_ACTIVATION:
            pKeyDateDesc = "CKA_THALES_DATE_KEY_ACTIVATION";
            break;

        case CKA_THALES_DATE_KEY_SUSPENSION:
            pKeyDateDesc = "CKA_THALES_DATE_KEY_SUSPENSION";
            break;
        case CKA_THALES_DATE_KEY_DEACTIVATION:
            pKeyDateDesc = "CKA_THALES_DATE_KEY_DEACTIVATION";
            break;
        case CKA_THALES_DATE_KEY_COMPROMISED:
            pKeyDateDesc = "CKA_THALES_DATE_KEY_COMPROMISED";
            break;

        case CKA_THALES_DATE_KEY_COMPROMISE_OCCURRENCE:
            pKeyDateDesc = "CKA_THALES_DATE_KEY_COMPROMISE_OCCURRENCE";
            break;
        case CKA_THALES_DATE_KEY_PROCESS_START:
            pKeyDateDesc = "CKA_THALES_DATE_KEY_PROCESS_START";
            break;
        case CKA_THALES_DATE_KEY_PROTECT_STOP:
            pKeyDateDesc = "CKA_THALES_DATE_KEY_PROTECT_STOP";
            break;
        }

        if(pKeyDateDesc)
            printf("%s: year: %s, month: %s, day: %s.\n", pKeyDateDesc, ch_year, ch_mon, ch_mday);
    }

    if( pKeyTemplate )
    {
        free ( pKeyTemplate );
    }
    return rc;
}


CK_RV getAttributesValue(CK_OBJECT_HANDLE hKey)
{
    CK_RV		rc = CKR_OK;
    CK_DATE     createDate, endDate;
    CK_BYTE     keyIdBuf[256];
    char        keyLabel[256];
    char        keyUuid[128];
    char        keyMuid[128];
    char        keyImportedId[128];
    char        keyAlias[256];
    CK_ULONG    ulCachedTime, i;
    CK_ULONG    ulLifeSpan=0;
    CK_OBJECT_CLASS	keyCls;
    CK_LONG     lKeyVersion;
    char        ch_year[5];
    char        ch_mon[3];
    char        ch_mday[3];

    char        serialno[256]= {0};
    char        custom[5][1024];

    CK_BBOOL    bCacheOnHost, bVersioned, blaSensitive, blnExtractable;
    int         custom1Index = 11;

    CK_ULONG    ulCreationTime, ulDeactivateTime = 0;
    CK_ATTRIBUTE_PTR pKeyTemplate = NULL;
    CK_DATE     keyTransDates[KEY_TRANS_DATES_MAX];
    char        *pKeyDateDesc = NULL;

    CK_ATTRIBUTE getAttrsTemplate[] =
    {
        {CKA_ID, keyIdBuf, sizeof(keyIdBuf) },                                    /*  0 */
        {CKA_LABEL, keyLabel, sizeof(keyLabel) },                                 /*  1 */
        {CKA_SERIAL_NUMBER, serialno, sizeof(serialno)},
        {CKA_CLASS, &keyCls, sizeof(keyCls) },                                    /*  3 */

        {CKA_THALES_OBJECT_UUID, keyUuid, sizeof(keyUuid)},                       /*  4 */
        {CKA_THALES_OBJECT_MUID, keyMuid, sizeof(keyMuid)},
        {CKA_THALES_OBJECT_ALIAS, keyAlias, sizeof(keyAlias)},                    /*  6 */
        {CKA_THALES_OBJECT_IKID, keyImportedId, sizeof(keyImportedId)},           /* 7 */
        {CKA_THALES_VERSIONED_KEY, &bVersioned, sizeof(bVersioned) },             /* 8 */

        {CKA_ALWAYS_SENSITIVE,	&blaSensitive,	sizeof(CK_BBOOL)	},
        {CKA_NEVER_EXTRACTABLE,	&blnExtractable,	sizeof(CK_BBOOL)	},

        {CKA_THALES_CUSTOM_1, custom[0], sizeof(custom[0])},                          /* 11 */
        {CKA_THALES_CUSTOM_2, custom[1], sizeof(custom[1])},
        {CKA_THALES_CUSTOM_3, custom[2], sizeof(custom[2])},
        {CKA_THALES_CUSTOM_4, custom[3], sizeof(custom[3])},                          /* 14 */
        {CKA_THALES_CUSTOM_5, custom[4], sizeof(custom[4])}		                      /* 15 */
    };
    CK_ULONG getAttrsTemplateSize = sizeof(getAttrsTemplate)/sizeof(CK_ATTRIBUTE);

    pKeyTemplate = (CK_ATTRIBUTE_PTR)calloc( (getAttrsTemplateSize), sizeof(CK_ATTRIBUTE) );
    if(!pKeyTemplate)
    {
        printf ("Error allocating memory for pKeyTemplate!\n");
        return CKR_HOST_MEMORY;
    }

    for(i=0; i<getAttrsTemplateSize; i++)
    {
        pKeyTemplate[i].type = getAttrsTemplate[i].type;
        pKeyTemplate[i].pValue = getAttrsTemplate[i].pValue;
        pKeyTemplate[i].ulValueLen = getAttrsTemplate[i].ulValueLen;
    }

    rc = FunctionListFuncPtr->C_GetAttributeValue(hSession,
            hKey,
            pKeyTemplate,
            getAttrsTemplateSize);

    if (rc != CKR_OK)
    {
        printf ("Error getting key attributes: %08x.\n", (unsigned int)rc);
        return rc;
    }

    printf("CKA_ID: '%.*s'\n", (int)pKeyTemplate[0].ulValueLen, keyIdBuf);
    printf("CKA_LABEL: '%.*s'\n", (int)pKeyTemplate[1].ulValueLen, keyLabel);
    printf("CKA_CLASS: %08x\n", (unsigned int)keyCls);

    printf("CKA_THALES_VERSIONED_KEY:  %s\n", bVersioned  ? "true" : "false");

    printf("CKA_NEVER_EXTRACTABLE: \t%s\n", blnExtractable  ? "true" : "false");
    printf("CKA_ALWAYS_SENSITIVE:  \t%s\n", blaSensitive  ? "true" : "false");

    printf("CKA_THALES_OBJECT_UUID:  '%.*s'\n", (int)pKeyTemplate[4].ulValueLen, keyUuid);
    printf("CKA_THALES_OBJECT_MUID:  '%.*s'\n", (int)pKeyTemplate[5].ulValueLen, keyMuid);
    printf("CKA_THALES_OBJECT_ALIAS: '%.*s'\n", (int)pKeyTemplate[6].ulValueLen, keyAlias);
    printf("CKA_THALES_OBJECT_IKID:  '%.*s'\n", (int)pKeyTemplate[7].ulValueLen, keyImportedId);

	for(i=0; i<5; i++)
    {
        custom[i][(int)pKeyTemplate[custom1Index+i].ulValueLen] = 0;
        printf("CKA_THALES_CUSTOM_%d: '%s' (length %d)\n", (int)i+1, custom[i], (int)pKeyTemplate[custom1Index+i].ulValueLen);
    }

    if( pKeyTemplate )
    {
        free ( pKeyTemplate );
    }
    return rc;
}

CK_RV createObject(char *keyLabel)
{
    CK_RV               rc = CKR_OK;
    CK_UTF8CHAR         app[] = { "CADP_PKCS11_SAMPLE" };
    CK_UTF8CHAR         keyValue[DEFAULT_KEYLEN];
    CK_OBJECT_CLASS     keyClass = CKO_SECRET_KEY;
    CK_KEY_TYPE         keyType = CKK_AES;
    CK_ULONG            keySize = DEFAULT_KEYLEN; /* 256 bits */
    CK_BBOOL            bFalse = CK_FALSE;
    CK_BBOOL            bTrue = CK_TRUE;
    CK_OBJECT_HANDLE    hKey = 0x0;

    CK_UTF8CHAR  *label = (CK_UTF8CHAR *) keyLabel;
    CK_ULONG len = (CK_ULONG) strlen(keyLabel);

    /* AES key template.
     * CKA_LABEL is the name of the key and will be displayed on the Key Manager
     * CKA_VALUE is the bytes that make up the AES key.
     */

    CK_ATTRIBUTE aesKeyTemplate[] =
    {
        {CKA_ID,            label,  len},
        {CKA_LABEL,         label,  len},
        {CKA_APPLICATION,   &app,       sizeof(app)     },
        {CKA_CLASS,         &keyClass,  sizeof(keyClass)},
        {CKA_KEY_TYPE,      &keyType,   sizeof(keyType) },
        {CKA_VALUE,         &keyValue,  sizeof(keyValue)},
        {CKA_VALUE_LEN,     &keySize,   sizeof(keySize) },
        {CKA_TOKEN,         &bTrue,     sizeof(bTrue)   },
        {CKA_ENCRYPT,       &bTrue,     sizeof(bTrue)   },
        {CKA_DECRYPT,       &bTrue,     sizeof(bTrue)   },
        {CKA_SIGN,          &bFalse,    sizeof(bFalse)  },
        {CKA_VERIFY,        &bFalse,    sizeof(bFalse)  },
        {CKA_WRAP,          &bTrue,     sizeof(bTrue)   },
        {CKA_UNWRAP,        &bFalse,    sizeof(bFalse)  },
        {CKA_EXTRACTABLE,       &bFalse,    sizeof(bFalse)  },
        {CKA_ALWAYS_SENSITIVE,  &bAlwaysSensitive,    sizeof(CK_BBOOL)  },
        {CKA_NEVER_EXTRACTABLE, &bNeverExtractable,     sizeof(CK_BBOOL)   },
        {CKA_SENSITIVE,         &bTrue,     sizeof(bTrue)   }
    };
    CK_ULONG    aesKeyTemplateSize = sizeof(aesKeyTemplate)/sizeof(CK_ATTRIBUTE);

    memcpy(keyValue, "\xEF\x43\x59\xD8\xD5\x80\xAA\x4F\x7F\x03\x6D\x6F\x04\xFC\x6A\x94\x2B\x7E\x15\x16\x28\xAE\xD2\xA6\xAB\xF7\x15\x88\x09\xCF\x4F\x3C", DEFAULT_KEYLEN);

    rc = FunctionListFuncPtr->C_CreateObject (hSession,
            aesKeyTemplate,
            aesKeyTemplateSize,
            &hKey
                                             );
    if (rc != CKR_OK || hKey == 0)
    {
        fprintf (stderr, "Error in C_CreateObject(), return value: %d\n", (int)rc);
    }

    return rc;
}

CK_RV createOpaque (char* olabel, char *value, int vlen)
{
    CK_RV               rc = CKR_OK;
    CK_UTF8CHAR         app[] = { "CADP_PKCS11_SAMPLE" };
    CK_UTF8CHAR         keyValue[4096];
    CK_OBJECT_CLASS     keyClass = CKO_THALES_OPAQUE_OBJECT;
    CK_KEY_TYPE         keyType = CKK_AES;
    CK_ULONG            keySize = (CK_ULONG) vlen;
    CK_BBOOL            bFalse = CK_FALSE;
    CK_BBOOL            bTrue = CK_TRUE;
    CK_OBJECT_HANDLE    hKey = 0x0;

    CK_UTF8CHAR  *label = (CK_UTF8CHAR *) olabel;
    CK_ULONG len = (CK_ULONG) strlen(olabel);

    /* AES key template.
     * CKA_LABEL is the name of the key and will be displayed on the Key Manager
     * CKA_VALUE is the bytes that make up the AES key.
     */

    CK_ATTRIBUTE ooTemplate[] =
    {
        {CKA_ID,            label,  len},
        {CKA_LABEL,         label,  len},
        {CKA_APPLICATION,   &app,       sizeof(app)     },
        {CKA_CLASS,         &keyClass,  sizeof(keyClass)},
        {CKA_KEY_TYPE,      &keyType,   sizeof(keyType) },
        {CKA_VALUE,         &keyValue,   (CK_ULONG)vlen  },
        {CKA_VALUE_LEN,     &keySize,   sizeof(keySize) },
        {CKA_TOKEN,         &bTrue,     sizeof(bTrue)   },
        {CKA_ENCRYPT,       &bTrue,     sizeof(bTrue)   },
        {CKA_DECRYPT,       &bTrue,     sizeof(bTrue)   },
        {CKA_SIGN,          &bTrue,    sizeof(bTrue)  },
        {CKA_VERIFY,        &bTrue,    sizeof(bTrue)  },
        {CKA_WRAP,          &bTrue,     sizeof(bTrue)   },
        {CKA_UNWRAP,        &bFalse,    sizeof(bFalse)  },
        {CKA_EXTRACTABLE,       &bFalse,    sizeof(bFalse)  },
        {CKA_ALWAYS_SENSITIVE,	&bAlwaysSensitive,	sizeof(CK_BBOOL)	},
        {CKA_NEVER_EXTRACTABLE,	&bNeverExtractable,	sizeof(CK_BBOOL)	},
        {CKA_SENSITIVE,         &bTrue,     sizeof(bTrue)   }
    };
    CK_ULONG    ooTemplateSize = sizeof(ooTemplate)/sizeof(CK_ATTRIBUTE);

    memcpy(keyValue, value, vlen);
    //memcpy(keyValue, "\xEF\x43\x59\xD8\xD5\x80\xAA\x4F\x7F\x03\x6D\x6F\x04\xFC\x6A\x94\x2B\x7E\x15\x16\x28\xAE\xD2\xA6\xAB\xF7\x15\x88\x09\xCF\x4F\x3C", KEYLEN);

    rc = FunctionListFuncPtr->C_CreateObject (hSession,
            ooTemplate,
            ooTemplateSize,
            &hKey
                                             );
    if (rc != CKR_OK || hKey == 0)
    {
        fprintf (stderr, "Error in C_CreateObject(), return value: %d\n", (int)rc);
    }

    return rc;
}

char **splitKeyAliases(char *keyAlias, unsigned int *pcount)
{
    int index;
    char *pch =keyAlias;
    char **aliases = NULL;
    *pcount = 0;

    if(!keyAlias) return NULL;

    while(*pch)
    {
        if (*pch == ',' || *pch == ';')
            ++(*pcount);
        pch++;
    }
    ++(*pcount);

    aliases = (char **)calloc( *pcount, sizeof(char *) );
    if(!aliases)
    {
        printf ("Error allocating memory for aliases\n");
        return NULL;
    }

    index = 0;
    pch = strtok (keyAlias, ",;");

    while(pch != NULL)
    {

        aliases[index++] = strdup( pch );

        pch = strtok (NULL, ",;");
    }

    return aliases;
}

/*
 ************************************************************************
 * Function: createKey
 * Creates and AES key on the Key Manager.
 * The keyLabel is the name of the key displayed on the Key Manager.
 * key_size, the key size for symmetric key in bytes
 ************************************************************************
 * Returns: CK_RV
 ************************************************************************
 */

CK_RV createKeyS (char* keyLabel, int key_size)
{
    CK_RV rc = CKR_OK;
    CK_MECHANISM		mechGenKey = { CKM_AES_KEY_GEN, NULL_PTR, 0};
    CK_OBJECT_CLASS		keyClass = CKO_SECRET_KEY;
    CK_KEY_TYPE			keyType = CKK_AES;
    CK_ULONG			keySize = key_size; /* 256 bits */
    CK_BBOOL			bFalse = CK_FALSE;
    CK_BBOOL			bTrue = CK_TRUE;

    CK_UTF8CHAR  *label = (CK_UTF8CHAR *) keyLabel;
    CK_ULONG len = (CK_ULONG) strlen(keyLabel);

    /* AES key template.
     * CKA_LABEL is the name of the key and will be displayed on the Key Manager.
     * CKA_VALUE_LEN is the size of the AES key.
     */

    CK_ATTRIBUTE aesKeyTemplate[] =
    {
        {CKA_LABEL,		label,	len },
        {CKA_ID,          label,  len   },
        {CKA_APPLICATION,	&app,		sizeof(app)		},
        {CKA_CLASS,			&keyClass,	sizeof(keyClass)},
        {CKA_KEY_TYPE,		&keyType,	sizeof(keyType)	},
        {CKA_VALUE_LEN,		&keySize,	sizeof(keySize)	},
        {CKA_TOKEN,			&bTrue,		sizeof(bTrue)	},
        {CKA_ENCRYPT,		&bTrue,		sizeof(bTrue)	},
        {CKA_DECRYPT,		&bTrue,		sizeof(bTrue)	},
        {CKA_SIGN,			&bFalse,	sizeof(bFalse)	},
        {CKA_VERIFY,		&bFalse,	sizeof(bFalse)	},
        {CKA_WRAP,			&bTrue,		sizeof(bTrue)	},
        {CKA_UNWRAP,		&bFalse,	sizeof(bFalse)	},
        {CKA_ALWAYS_SENSITIVE,	&bAlwaysSensitive,	sizeof(CK_BBOOL)	},
        {CKA_NEVER_EXTRACTABLE,	&bNeverExtractable,	sizeof(CK_BBOOL)	}
    };
    CK_ULONG	aesKeyTemplateSize = sizeof(aesKeyTemplate)/sizeof(CK_ATTRIBUTE);

    rc = FunctionListFuncPtr->C_GenerateKey(hSession,
                                            &mechGenKey,
                                            aesKeyTemplate, aesKeyTemplateSize,
                                            &hGenKey
                                           );
    if (rc != CKR_OK || hGenKey == 0)
    {
        printf ("Error generating Key\n");
        return rc;
    }

    return rc;
}

/*
 ************************************************************************
 * Function: createKey
 * Creates and AES 256 key on the Key Manager.
 * The keyLabel is the name of the key displayed on the Key Manager.
 ************************************************************************
 * Parameters: none
 * Returns: CK_RV
 ************************************************************************
 */
CK_RV createKey(char *keyLabel, char *keyAlias, int gen_action, CK_ULONG ulifespan, int key_size)
{
    CK_RV               rc = CKR_OK;
    CK_MECHANISM        mechGenKey = { CKM_AES_KEY_GEN, NULL_PTR, 0};
    CK_OBJECT_CLASS     keyClass = CKO_SECRET_KEY;
    CK_KEY_TYPE         keyType = CKK_AES;
    CK_ULONG            keySize = key_size; /* 256 bits */
    CK_BBOOL            bFalse = CK_FALSE;
    CK_BBOOL            bTrue = CK_TRUE;

    CK_BYTE             ckaIdBuf[ASYMKEY_BUF_LEN*2+1];
    CK_BYTE             ckaSerial[256];
    CK_UTF8CHAR         *label = (CK_UTF8CHAR *) keyLabel;
    CK_ULONG            len = keyLabel ? (CK_ULONG) strlen(keyLabel) : 0;
    CK_ULONG            keyVersionAction = gen_action;

    /* char ch_year[5], ch_month[3], ch_day[3]; */
    unsigned int        i;
    unsigned int        aliasCount = 0;
    unsigned int	    aliasCountIdx;
    char                **pKeyAliases = NULL;
    CK_ULONG            templateIndex = 0;
    CK_ULONG            aliasIndex = 0;
    CK_ATTRIBUTE_PTR    pKeyTemplate = NULL;

    /* AES key template.
     * CKA_LABEL is the name of the key and will be displayed on the Key Manager.
     * CKA_VALUE_LEN is the size of the AES key.
     */

    CK_ATTRIBUTE aesKeyTemplate[] =
    {
        {CKA_ID,            label,     len   },
        {CKA_LABEL,         label,     len   },
        {CKA_SERIAL_NUMBER, ckaSerial, sizeof(ckaSerial)},
        {CKA_APPLICATION,    &app,       sizeof(app)     },
        {CKA_CLASS,           &keyClass,  sizeof(keyClass)},
        {CKA_KEY_TYPE,        &keyType,   sizeof(keyType) },
        {CKA_VALUE_LEN,       &keySize,   sizeof(keySize) },
        {CKA_TOKEN,           &bTrue,     sizeof(bTrue)   },
        {CKA_ENCRYPT,     &bTrue,     sizeof(bTrue)   },
        {CKA_DECRYPT,     &bTrue,     sizeof(bTrue)   },
        {CKA_SIGN,            &bFalse,    sizeof(bFalse)  },
        {CKA_VERIFY,      &bFalse,    sizeof(bFalse)  },
        {CKA_WRAP,            &bTrue,     sizeof(bTrue)   },
        {CKA_UNWRAP,      &bFalse,    sizeof(bFalse)  },
        {CKA_ALWAYS_SENSITIVE,	&bAlwaysSensitive,	sizeof(CK_BBOOL)	},
        {CKA_NEVER_EXTRACTABLE,	&bNeverExtractable,	sizeof(CK_BBOOL)	},
        /*  {CKA_THALES_VERSIONED_KEY,   &bTrue,     sizeof(bTrue)   }, */
        {CKA_THALES_KEY_CACHED_TIME,     &ulCachedTime,   sizeof(CK_ULONG)   },

        {CKA_THALES_KEY_VERSION_ACTION, &keyVersionAction, sizeof(keyVersionAction) },
        {CKA_THALES_KEY_VERSION_LIFE_SPAN,  &ulifespan,  sizeof(ulifespan) }
    };
    CK_ULONG  aesKeyTemplateSize = sizeof(aesKeyTemplate)/sizeof(CK_ATTRIBUTE);

    if(ulifespan == 0)
        aesKeyTemplateSize--;

    if(gen_action == nonVersionCreate)
    {
        aesKeyTemplateSize--;

        if(ulifespan != 0)
        {
            aesKeyTemplate[aesKeyTemplateSize-1].type = aesKeyTemplate[aesKeyTemplateSize].type;
            aesKeyTemplate[aesKeyTemplateSize-1].pValue = aesKeyTemplate[aesKeyTemplateSize].pValue;
            aesKeyTemplate[aesKeyTemplateSize-1].ulValueLen = aesKeyTemplate[aesKeyTemplateSize].ulValueLen;
        }
    }

    /*	if(!keyAlias) {

    	for(i=aliasIndex; i<aesKeyTemplateSize-1; i++) {
    		aesKeyTemplate[i].type = aesKeyTemplate[i+1].type;
    		aesKeyTemplate[i].pValue = aesKeyTemplate[i+1].pValue;
    		aesKeyTemplate[i].ulValueLen = aesKeyTemplate[i+1].ulValueLen;
    	}

    	aesKeyTemplateSize--;
    	} */

    pKeyAliases = splitKeyAliases(keyAlias, &aliasCount);

    if(keyAlias && aliasCount > 0)
    {
        pKeyTemplate = (CK_ATTRIBUTE_PTR)calloc( (aesKeyTemplateSize + aliasCount), sizeof(CK_ATTRIBUTE) );
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

        templateIndex = aesKeyTemplateSize;
        aesKeyTemplateSize += aliasCount;
        aliasIndex = 0;

        for(i=templateIndex; i<aesKeyTemplateSize; i++, aliasIndex++)
        {
            pKeyTemplate[i].type = CKA_THALES_OBJECT_ALIAS;
            pKeyTemplate[i].pValue = pKeyAliases[aliasIndex];
            pKeyTemplate[i].ulValueLen = pKeyAliases[aliasIndex] ? (CK_ULONG)strlen(pKeyAliases[aliasIndex]) : 0;
        }
    }
    else
    {
        pKeyTemplate = aesKeyTemplate;
    }

    for(i = 0; i<ASYMKEY_BUF_LEN*2; i+=2)
    {
        snprintf(((char *)ckaIdBuf)+i, 3, "%02x", 255);
    }

    snprintf(((char *)ckaSerial), sizeof(plainSerial), "%s", plainSerial);

    rc = FunctionListFuncPtr->C_GenerateKey(hSession,
                                            &mechGenKey,
                                            pKeyTemplate, aesKeyTemplateSize,
                                            &hGenKey
                                           );
    if (rc != CKR_OK || hGenKey == 0)
    {
        printf ("Error generating Key: 0x%08x\n", (unsigned int)rc);
    }
    else
    {
        printf ("Successfully generated key with name: %s\n", keyLabel);
    }

    if(keyAlias && aliasCount > 0)
    {
        free(pKeyTemplate);
    }

    if(pKeyAliases)
    {
        for(aliasCountIdx = 0; aliasCountIdx  < aliasCount; aliasCountIdx++)
            free(pKeyAliases[aliasCountIdx]);

        free(pKeyAliases);
    }
    return rc;
}

/*
 *  ************************************************************************
 *  Function: createSymKeyCustom
 *  Creates and AES 256 key on the Key Manager.
 *  The keyLabel is the name of the key displayed on the Key Manager.
 *  ************************************************************************
 */
CK_RV createSymKeyCustom(char *keyLabel, char *keyAlias, int gen_action, char *custom1, char *custom2, char *custom3)
{
    CK_RV               rc = CKR_OK;
    CK_MECHANISM        mechGenKey = { CKM_AES_KEY_GEN, NULL_PTR, 0};
    CK_OBJECT_CLASS     keyClass = CKO_SECRET_KEY;
    CK_KEY_TYPE         keyType = CKK_AES;
    CK_ULONG            keySize = 32; /* 256 bits */
    CK_BBOOL            bFalse = CK_FALSE;
    CK_BBOOL            bTrue = CK_TRUE;

    CK_BYTE      ckaIdBuf[ASYMKEY_BUF_LEN*2+1];
    CK_UTF8CHAR  *label = (CK_UTF8CHAR *) keyLabel;
    CK_UTF8CHAR  *alias = (CK_UTF8CHAR *) keyAlias;
    char         serialno[256];

    CK_ULONG     len = (CK_ULONG) strlen(keyLabel);
    CK_ULONG     alen = keyAlias ? (CK_ULONG) strlen(keyAlias)+1 : 1;

    CK_LONG      keyVersionAction = gen_action;

    unsigned int i;

    char    *pcEndDate = (char *)malloc(sizeof(CK_DATE)+1);
    CK_DATE *pEndDate = (CK_DATE *)pcEndDate;

    CK_UTF8CHAR  *ca1 = (CK_UTF8CHAR *)custom1;
    CK_ULONG     caLen1 = custom1 ? (CK_ULONG) strlen(custom1) : 0;
    CK_UTF8CHAR  *ca2 = (CK_UTF8CHAR *)custom2;
    CK_ULONG     caLen2 = custom2 ? (CK_ULONG) strlen(custom2) : 0;
    CK_UTF8CHAR  *ca3 = (CK_UTF8CHAR *)custom3;
    CK_ULONG     caLen3 = custom3 ? (CK_ULONG) strlen(custom3) : 0;

    time_t epoch_t;
    struct tm *ptm;
    struct tm end_tm;

    /* AES key template.
     * CKA_LABEL is the name of the key and will be displayed on the Key Manager.
     * CKA_VALUE_LEN is the size of the AES key.
     */

    CK_ATTRIBUTE aesKeyTemplate[] =
    {
        {CKA_ID,            label,     len   },                                       /*  0 */
        {CKA_LABEL,         label,     len   },
        {CKA_SERIAL_NUMBER, serialno, sizeof(serialno) },
        {CKA_APPLICATION, &app,       sizeof(app)     },
        {CKA_CLASS,           &keyClass,  sizeof(keyClass)},
        {CKA_KEY_TYPE,        &keyType,   sizeof(keyType) },
        {CKA_VALUE_LEN,       &keySize,   sizeof(keySize) },                          /*  6 */
        {CKA_TOKEN,           &bTrue,     sizeof(bTrue)   },
        {CKA_ENCRYPT,     &bTrue,     sizeof(bTrue)   },
        {CKA_DECRYPT,     &bTrue,     sizeof(bTrue)   },
        {CKA_SIGN,            &bFalse,    sizeof(bFalse)  },
        {CKA_VERIFY,      &bFalse,    sizeof(bFalse)  },                              /* 11 */
        {CKA_WRAP,            &bTrue,     sizeof(bTrue)   },
        {CKA_UNWRAP,      &bFalse,    sizeof(bFalse)  },
        {CKA_ALWAYS_SENSITIVE,	&bAlwaysSensitive,	sizeof(CK_BBOOL)	},
        {CKA_NEVER_EXTRACTABLE,	&bNeverExtractable,	sizeof(CK_BBOOL)	},                   /* 15 */
        {CKA_END_DATE,            pEndDate,   sizeof(CK_DATE)   },
        {CKA_THALES_CUSTOM_1, ca1, caLen1 },
        {CKA_THALES_CUSTOM_2, ca2, caLen2 },
        {CKA_THALES_CUSTOM_3, ca3, caLen3 },
        {CKA_THALES_OBJECT_ALIAS,    alias,     alen    },                            /* 20 */
        {CKA_THALES_KEY_VERSION_ACTION, &keyVersionAction, sizeof(keyVersionAction) }
    };
    CK_ULONG  aesKeyTemplateSize = sizeof(aesKeyTemplate)/sizeof(CK_ATTRIBUTE);

    if(!keyAlias)
    {
        /* copy the VERSION_ACTION slot over the ALIAS slot */
        aesKeyTemplate[aesKeyTemplateSize-2] = aesKeyTemplate[aesKeyTemplateSize-1];
        aesKeyTemplateSize--;
    }

    if(gen_action == 3)
        aesKeyTemplateSize--;

    for(i = 0; i<ASYMKEY_BUF_LEN*2; i+=2)
    {
        snprintf(((char *)ckaIdBuf)+i, 3, "%02x", 255);
    }
    snprintf(((char *)serialno), sizeof(plainSerial), "%s", plainSerial);

    if(!pcEndDate)
    {
        printf ("Error allocating memory for end date!\n");
        return CKR_HOST_MEMORY;
    }

    time(&epoch_t);
    ptm = localtime( &epoch_t );
    end_tm = *ptm;
    end_tm.tm_sec += 31 * 24 * 60 * 60;

    mktime( &end_tm );

    if (snprintf(pcEndDate, sizeof(CK_DATE)+1, "%04d%02d%02d",
                 end_tm.tm_year + 1900, end_tm.tm_mon + 1, end_tm.tm_mday) < 0)
    {
        *pcEndDate = '\0';
        return CKR_HOST_MEMORY;
    }

    rc = FunctionListFuncPtr->C_GenerateKey(hSession,
                                            &mechGenKey,
                                            aesKeyTemplate, aesKeyTemplateSize,
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

    if(pcEndDate)
    {
        free(pcEndDate);
    }
    return rc;
}

/*
 ************************************************************************
 * Function: getKeyAttributes
 * Demos how to get key attributes from Key Manager
 ************************************************************************
 * Parameters: hKey - the key handle
 * Returns: CK_RV
 ************************************************************************
 */
CK_RV getKeyAttributes(CK_OBJECT_HANDLE hKey)
{
    CK_RV rc = CKR_OK;
    CK_ATTRIBUTE        attribute;
    CK_BBOOL            bAttrVal;
    CK_BYTE             ckBuffer[100];

    attribute.type = CKA_ID;
    attribute.ulValueLen = sizeof(ckBuffer);
    attribute.pValue = ckBuffer;
    rc = FunctionListFuncPtr->C_GetAttributeValue(hSession ,
            hKey,
            &attribute,
            1);
    if ((rc != CKR_OK) || (attribute.ulValueLen == 0))
    {
        printf ("Error getting attribute value CKA_ID\n");
    }
    else
    {
        printf ("Successfully getting attribute value CKA_ID: %s, length: %ld \n.", (char *)attribute.pValue, (long)attribute.ulValueLen);
    }

    attribute.type = CKA_WRAP;
    attribute.ulValueLen = sizeof(CK_BBOOL);
    attribute.pValue = &bAttrVal;
    rc = FunctionListFuncPtr->C_GetAttributeValue(hSession,
            hKey,
            &attribute,
            1);
    if ((rc != CKR_OK) || (attribute.ulValueLen == 0))
    {
        printf ("Error getting attribute value CKA_WRAP\n");
    }
    else
    {
        printf ("Successfully getting attribute value CKA_WRAP: %d, length: %ld\n.", *(unsigned char*)attribute.pValue, (long)attribute.ulValueLen);
    }

    attribute.type = CKA_LABEL;
    attribute.ulValueLen = sizeof(ckBuffer);
    memset(ckBuffer, 0x0, sizeof(ckBuffer));
    attribute.pValue = ckBuffer;
    rc = FunctionListFuncPtr->C_GetAttributeValue(hSession,
            hKey,
            &attribute,
            1);

    if ((rc != CKR_OK) || (attribute.ulValueLen == 0))
    {
        fprintf (stderr, "Error getting attribute value CKA_LABEL\n");
    }
    else
    {
        printf ("Successfully getting attribute value CKA_LABEL: %s, length : %ld \n.", (char *)attribute.pValue, (long) attribute.ulValueLen);
    }

    return rc;
}

/*
 ************************************************************************
 * Function: logoutAndCloseSession
 * Logs out of the Key Manager and closes the session
 ************************************************************************
 * Parameters: none
 * Returns: CK_RV
 ************************************************************************
 */

CK_RV logout()
{
    CK_RV rc = CKR_OK;
    if (hSession != CK_INVALID_HANDLE)
    {
        rc = FunctionListFuncPtr->C_Logout (hSession);
        if (rc != CKR_OK)
        {
            fprintf (stderr, "FAIL: Unable to Logout\n");
            return rc;
        }
    }
    else
    {
        fprintf (stderr, "FAIL: Cannot perform logout. Invalid session handle. \n");
        return CKR_FUNCTION_FAILED;
    }
    return rc;
}

/*
* newgetopt -- Parse argc/argv argument vector.
*/
int newgetopt(int nargc, char * const nargv[], const char *ostr)
{
    static char *place = EMSG;              /* option letter processing */
    const char *oli;                        /* option letter list index */
    char  nc;

    if (optreset || !*place)
    {
        /* update scanning pointer */
        optreset = 0;
        if (optind >= nargc || *(place = nargv[optind]) != '-')
        {
            place = EMSG;
            return (-1);
        }

        if (place[1] && *++place == '-')
        {
            /* found "--" */
            ++optind;
            place = EMSG;
            return (-1);
        }
    }
    /* option letter okay? */
    optopt = (int)*place++;
    oli = strchr(ostr, optopt);
    if (optopt == (int)':' || !oli)
    {
        /*  if the user didn't specify '-' as an option, assume it means -1.*/
        if (optopt == (int)'-')
            return (-1);
        if (!*place)
            ++optind;
        if (opterr && *ostr != ':')
            (void)printf("illegal option -- %c\n", optopt);
        return (BADCH);
    }

    if ((nc=*(oli+1)) != ':')
    {
        /* don't need argument */
        if(nc == ';')
        {
            optarg = NULL;
            if (!*place)
                ++optind;
        }
        else
        {
            if(*place)
            {
                optopt <<= 8;
                optopt |= (int)*place++;
            }
        }
        oli++;
    }

    if( *++oli != ':' )
    {
        /* don't need argument */
        optarg = NULL;
        if (!*place)
            ++optind;
    }
    else
    {
        /* need an argument */
        if (*place)                     /* no white space */
            optarg = place;
        else if (nargc <= ++optind)
        {
            /* no arg */
            place = EMSG;
            if (*ostr == ':')
                return (BADARG);
            if (opterr)
                (void)printf("option requires an argument -- %c\n", optopt);
            return (BADCH);
        }
        else                            /* white space */
            optarg = nargv[optind];
        place = EMSG;
        ++optind;
    }

    return (optopt);                        /* dump back option letter */
}

int fgetline(char **lineptr, int *n, FILE *stream)
{
    char *bufptr = NULL;
    char *p = bufptr;
    int size = 0;
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

/*
 * Trim a string on both ends
 */
void trim(char * str)
{
    int dest;
    int mark = 0;
    int src = 0;
    int len = str ? (int)strlen(str) : 0;

    if (len == 0)
    {
        return;
    }

    /* Advance src to the first non-whitespace character. */
    while(isspace(str[src]))
        src++;
    mark = src;

    /* Copy the string to the "front" of the buffer */
    for(dest=0; src<len; dest++, src++)
    {
        str[dest] = str[src];
    }

    /* Don't miss reset end NULL '\0' */
    len -= mark;
    str[len] = '\0';

    /* Working backwards, set all trailing spaces to NULL. */
    for(dest=len-1; isspace(str[dest]); --dest)
    {
        str[dest] = '\0';
    }
}

CK_RV readObjectBytes( FILE * fp, CK_BYTE_PTR pObjBuf, CK_ULONG * pulObjLen, int format_type )
{
    int          bf_len;
    int          readlen = 0;
    CK_BYTE_PTR	 pBuf;
    CK_RV        rv = CKR_OK;
    size_t       keyBlkSize = 256;

    if(!fp) return CKR_GENERAL_ERROR;

    switch(format_type)
    {
    case CKA_THALES_PEM_FORMAT:
        keyBlkSize = 4096;
        break;

    case CKA_RAW_FORMAT:
        keyBlkSize = 256;
        break;

    default:
        keyBlkSize = 128;
    }

    do
    {
        bf_len = READ_BLK_LEN;
        pBuf = NULL;
        readlen = fgetline((char**)&pBuf, &bf_len, fp);

        if(readlen < 0)
        {
            if(readlen != -1)
            {
                fprintf(stderr, "Error reading file, readlen = %d", (int)readlen);
                rv = CKR_GENERAL_ERROR;
            }
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

        if(strstr( (char*)pBuf, "Key Value:" ) != NULL)
        {
            readlen = (int)fread(pObjBuf, sizeof(CK_BYTE), keyBlkSize, fp);

            if(format_type == CKA_RAW_FORMAT && readlen % 16 != 0)
            {
                fprintf(stderr, "Error reading key bytes, wrapped key bytes length = %d", (int)readlen);
                return CKR_GENERAL_ERROR;
            }

            *pulObjLen = readlen; /* (readlen/16) * 16; */
            printf("Read object/wrapped bytes length = %d\n", (int)readlen);
            break;
        }
    }
    while (readlen >= 0);

    return rv;
}

int gen_utf32(unsigned X, int endianness, unsigned char *Z)
{
    if (X <= 0x10FFFF)
    {
        if (endianness == FPE_BIG_ENDIAN)
        {
            Z[3] = X & 0xFF;
            Z[2] = (X >> 8) & 0xFF;
            Z[1] = (X >> 16) & 0xFF;
            Z[0] = (X >> 24) & 0xFF;
        }
        else
        {
            Z[0] = X & 0xFF;
            Z[1] = (X >> 8) & 0xFF;
            Z[2] = (X >> 16) & 0xFF;
            Z[3] = (X >> 24) & 0xFF;
        }
        /* printf("UTF32: %02X %02X %02X %02X \n", Z[0], Z[1], Z[2], Z[3]); */
        return 4;
    }
    else
    {
        return 0;
    }
}

int gen_utf16(unsigned X, int endianness, unsigned char *Z)
{
    unsigned Y;

    if ((X > 0 && X <= 0xD7FF) || (X >= 0xE000 && X <= 0xFFFF))
    {
        if (endianness == FPE_BIG_ENDIAN)
        {
            Z[1] = X & 0xFF;
            Z[0] = (X >> 8) & 0xFF;
        }
        else
        {
            Z[0] = X & 0xFF;
            Z[1] = (X >> 8) & 0xFF;
        }
        /* printf("%02X %02X \n", Z[0], Z[1]); */
        return 2;
    }
    else if (X >= 0x10000 && X <= 0x10FFFF)
    {
        X = X - 0x10000;

        if (endianness == FPE_BIG_ENDIAN)
        {
            Y = (X & 0x3FF) + 0xDC00;
            Z[3] = Y & 0xFF;
            Z[2] = (Y >> 8) & 0xFF;

            Y = ((X >> 10) & 0x3FF) + 0xD800;
            Z[1] = Y & 0xFF;
            Z[0] = (Y >> 8) & 0xFF;
        }
        else
        {
            Y = (X & 0x3FF) + 0xDC00;
            Z[2] = Y & 0xFF;
            Z[3] = (Y >> 8) & 0xFF;

            Y = ((X >> 10) & 0x3FF) + 0xD800;
            Z[0] = Y & 0xFF;
            Z[1] = (Y >> 8) & 0xFF;
        }
        /* printf("UTF16: %02X %02X %02X %02X \n", Z[0], Z[1], Z[2], Z[3]); */
        return 4;
    }
    else
    {
        return 0;
    }
}

int gen_utf8(unsigned X, unsigned char *Z)
{
    if (X <= 0x7F)
    {
        Z[0] = X & 0x7F;

        /* printf("%02X \n", Z[0]); */
        return 1;
    }
    else if (X >= 0x80 && X <= 0x7FF)
    {
        Z[1] = (X & 0x3F) | 0x80;
        Z[0] = ((X>>6) & 0x1F) | 0xC0;

        /* printf("%02X %02X \n", Z[0], Z[1]); */
        return 2;
    }
    else if (X >= 0x800 && X <= 0xFFFF)
    {
        Z[2] = (X & 0x3F) | 0x80;
        Z[1] = ((X>>6) & 0x3F) | 0x80;
        Z[0] = ((X>>12) & 0x0F) | 0xE0;

        /* printf("%02X %02X %02X \n", Z[0], Z[1], Z[2]); */
        return 3;
    }
    else if (X >= 0x10000 && X <= 0x10FFFF)
    {
        Z[3] = (X & 0x3F) | 0x80;
        Z[2] = ((X>>6) & 0x3F) | 0x80;
        Z[1] = ((X>>12) & 0x3F) | 0x80;
        Z[0] = ((X>>18) & 0x7) | 0xF0;

        /* printf("%02X %02X %02X %02X \n", Z[0], Z[1], Z[2], Z[3]); */
        return 4;
    }
    else
    {
        return 0;
    }
}

/*
 ************************************************************************
 * Function: gen_utf
 * This function is a wrapper around functions generating utf-8, utf-16,
 * utf-32 encodings.
 * The caller needs to allocate 4 bytes to store the output of the specified
 * encoding.
 ************************************************************************
 * Returns: Number of bytes in the output of specified encoding
 ************************************************************************
 */
int gen_utf(unsigned X /* in */, CK_BYTE enc_type /* in */, unsigned char *Z /* out */)
{
    switch (enc_type)
    {
    case CS_ASCII:
        *Z = (unsigned char) X;
        return 1;
    case CS_UTF8:
        return gen_utf8(X, Z);
    case CS_UTF16LE:
        return gen_utf16(X, FPE_LITTLE_ENDIAN, Z);
    case CS_UTF16BE:
        return gen_utf16(X, FPE_BIG_ENDIAN, Z);
    case CS_UTF32LE:
        return gen_utf32(X, FPE_LITTLE_ENDIAN, Z);
    case CS_UTF32BE:
        return gen_utf32(X, FPE_BIG_ENDIAN, Z);
    }
    return 0;
}

CK_BYTE get_enc_mode(const char * charset_type)
{
    CK_BYTE enc_mode = 0;

    if (!strcmp(charset_type, "ASCII"))
    {
        enc_mode = CS_ASCII;
    }
    else if (!strcmp(charset_type, "UTF16BE"))
    {
        enc_mode = CS_UTF16BE;
    }
    else if (!strcmp(charset_type, "UTF16LE"))
    {
        enc_mode = CS_UTF16LE;
    }
    else if (!strcmp(charset_type, "UTF32BE"))
    {
        enc_mode = CS_UTF32BE;
    }
    else if (!strcmp(charset_type, "UTF32LE"))
    {
        enc_mode = CS_UTF32LE;
    }
    else if (!strcmp(charset_type, "UTF8"))
    {
        enc_mode = CS_UTF8;
    }
    else if (!strncmp(charset_type, "UTF", 3))
    {
        enc_mode = CS_UTF8;
    }
    else if (!strncmp(charset_type, "CARD10", 6))
    {
        enc_mode = CS_CARD10;
    }
    else if (!strncmp(charset_type, "CARD26", 6))
    {
        enc_mode = CS_CARD26;
    }
    else if (!strncmp(charset_type, "CARD62", 6))
    {
        enc_mode = CS_CARD62;
    }
    else
    {
        fprintf(stderr, "Illegal character set type specified: Use one of ASCII, UTF16BE, UTF16LE, UTF32BE, UTF32LE, UTF8\n");
        return CKR_GENERAL_ERROR;
    }
    return enc_mode;
}

CK_BYTE *get_BOM_mode(CK_BYTE* pBuf, int* pReadlen, CK_BYTE* bom_mode)
{
    CK_BYTE* pPlainBuf;
    /* check for BOM character */
    if(!memcmp(pBuf, "\xFF\xFE\x00\x00", 4))
    {
        pPlainBuf = pBuf + 4;
        *pReadlen -= 4;
        *bom_mode = CS_UTF32LE;
    }
    else if (!memcmp(pBuf, "\x00\x00\xFE\xFF", 4))
    {
        pPlainBuf = pBuf + 4;
        *pReadlen -= 4;
        *bom_mode = CS_UTF32BE;
    }
    else if (!memcmp(pBuf, "\xFE\xFF", 2))
    {
        pPlainBuf = pBuf + 2;
        *pReadlen -= 2;
        *bom_mode = CS_UTF16BE;
    }
    else if (!memcmp(pBuf, "\xFF\xFE", 2))
    {
        pPlainBuf = pBuf + 2;
        *pReadlen -= 2;
        *bom_mode = CS_UTF16LE;
    }
    else if (!memcmp(pBuf, "\xEF\xBB\xBF", 3))
    {
        pPlainBuf = pBuf + 3;
        *pReadlen -= 3;
        *bom_mode = CS_UTF8;
    }
    else
        pPlainBuf = pBuf;

    return pPlainBuf;
}

void put_BOM_mode(CK_BYTE bom_mode, FILE* fp_write)
{
    switch(bom_mode)
    {
    case CS_ASCII:
        break;
    case CS_UTF16LE:
        fputs("\xFF\xFE", fp_write);
        break;
    case CS_UTF16BE:
        fputs("\xFE\xFF", fp_write);
        break;
    case CS_UTF32BE:
        fputs("\x00\x00\xFE\xFF", fp_write);
        break;
    case CS_UTF32LE:
        fputs("\xFF\xFE\x00\x00", fp_write);
        break;
    case CS_UTF8:
        fputs("\xEF\xBB\xBF", fp_write);
        break;
    }
}
