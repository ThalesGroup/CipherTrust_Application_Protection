/*************************************************************************
**                                                                                                                             **
** Copyright(c) 2022                                  Confidential Material                                           **
**                                                                                                                             **
** This file is the property of Thales Group.                                                                          **
** The contents are proprietary and confidential.                                                               **
** Unauthorized use, duplication, or dissemination of this document,                                      **
** in whole or in part, is forbidden without the express consent of                                         **
** Thales Group.                                                                                                              **
**                                                                                                                             **
**************************************************************************/
/*
 ***************************************************************************
 * File: pkcs11_sample_helper.h
 ***************************************************************************
 ***************************************************************************
 * pkcs11 sample helper header file
 ***************************************************************************
 */

#ifndef __pkcs11_sample_helper_h__
#define __pkcs11_sample_helper_h__

#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>

#ifdef __WINDOWS__
#define snprintf _snprintf
#endif

#ifdef _WIN32
#define _WINSOCKAPI_ /* do not include winsock.h */
#include "cryptoki.h"
#include <tchar.h>
#include <windows.h>
#include <Accctrl.h>
#include <Aclapi.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/timeb.h>
#else
#include "pkcs11.h"
#include "pkcs11t.h"
#include <stdlib.h>
#include <errno.h>
#include <dlfcn.h>
#include <string.h>
#include <sys/stat.h>
#endif
#include <time.h>
#include "fpe.h"

#define AES_BLOCK_SIZE  16
#define DEFAULT_KEYLEN	32
#define MAX_RADIX_SIZE  65535
#define READ_BLK_LEN    1024
#define MODULUS_BITS    2048

extern CK_ULONG             aad_length;
extern CK_ULONG             iv_length;
extern CK_ULONG             gcm_iv_length;
extern CK_ULONG             tag_bits;
extern CK_BYTE              def_iv[];
extern CK_BYTE              def_gcm_iv[];
extern CK_BYTE              def_aad[];
extern CK_FUNCTION_LIST_PTR FunctionListFuncPtr;
extern CK_OBJECT_HANDLE     hGenKey;
extern CK_SESSION_HANDLE    hSession;
extern CK_BBOOL             bAlwaysSensitive;
extern CK_BBOOL             bNeverExtractable;


#define kp  ((int)'k' << 8 | (int)'p')
#define kt  ((int)'k' << 8 | (int)'t')
#define ks  ((int)'k' << 8 | (int)'s')
#define ka  ((int)'k' << 8 | (int)'a')

#define dc  ((int)'d' << 8 | (int)'c')   /* date object creation */
#define dt  ((int)'d' << 8 | (int)'t')   /* date object destroyed */
#define da  ((int)'d' << 8 | (int)'a')   /* date key activation */
#define dp  ((int)'d' << 8 | (int)'p')   /* date key suspension */
#define dd  ((int)'d' << 8 | (int)'d')   /* date key deactivation */
#define dm  ((int)'d' << 8 | (int)'m')   /* date key compromised */
#define dr  ((int)'d' << 8 | (int)'r')   /* date key compromise occurrence */

#define ls  ((int)'l' << 8 | (int)'s')   /* life span of the key */
#define ps  ((int)'p' << 8 | (int)'s')   /* date process start */
#define pt  ((int)'p' << 8 | (int)'t')   /* date protect stop */

#define op  ((int)'o' << 8 | (int)'p')
#define np  ((int)'n' << 8 | (int)'p')
#define iv  ((int)'i' << 8 | (int)'v')
#define ta  ((int)'t' << 8 | (int)'a')

#define ne  ((int)'n' << 8 | (int)'e')
#define as  ((int)'a' << 8 | (int)'s')

#define ca  ((int)'c' << 8 | (int)'a')
#define ct  ((int)'c' << 8 | (int)'t')
#define c1  ((int)'c' << 8 | (int)'1')
#define c2  ((int)'c' << 8 | (int)'2')
#define c3  ((int)'c' << 8 | (int)'3')
#define c4  ((int)'c' << 8 | (int)'4')
#define c5  ((int)'c' << 8 | (int)'5')

#define na  ((int)'n' << 8 | (int)'a')
#define Sa  ((int)'S' << 8 | (int)'a')

#define CKA_THALES_DEFINED                                     0x40000000
#define CKA_VORM_DEFINED                                       0x70000000
#define CKO_THALES_KEY_PAIR                                    0x40000023

#define CKA_THALES_KEY_STATE_START_DATE                        0x0010 
#define CKA_THALES_KEY_STATE_STOP_DATE                         0x0020 
#define CKA_THALES_KEY_STATE_OCCURRENCE_DATE                   0x0030 

#define CKA_THALES_KEY_STATE                                   ( CKA_THALES_DEFINED | 0x1000 )
#define CKA_THALES_KEY_STATE_PREACTIVATED                      ( CKA_THALES_DEFINED | 0x1001 )
#define CKA_THALES_KEY_STATE_ACTIVATED                         ( CKA_THALES_DEFINED | 0x1002 )
#define CKA_THALES_KEY_STATE_SUSPENDED                         ( CKA_THALES_DEFINED | 0x1003 )
#define CKA_THALES_KEY_STATE_DEACTIVATED                       ( CKA_THALES_DEFINED | 0x1004 )
#define CKA_THALES_KEY_STATE_EXPIRED                           ( CKA_THALES_DEFINED | 0x1005 )

#define CKA_THALES_KEY_STATE_COMPROMISED                       ( CKA_THALES_DEFINED | 0x1006 )
#define CKA_THALES_KEY_STATE_DESTROYED                         ( CKA_THALES_DEFINED | 0x1007 )

#define CKA_THALES_KEY_STATE_ACTIONS                           ( CKA_THALES_DEFINED | 0x0100 )

#define CKA_THALES_DATE_OBJECT_CREATE	                       ( CKA_THALES_DEFINED | 0x1B )
#define CKA_THALES_DATE_OBJECT_DESTROY	                       ( CKA_THALES_DEFINED | 0x1C )

#define CKA_THALES_DATE_OBJECT_CREATE_EL	                   ( (CKA_THALES_DATE_OBJECT_CREATE & 0x0FFFFFFF) | CKA_VORM_DEFINED ) 
#define CKA_THALES_DATE_OBJECT_DESTROY_EL	                   ( (CKA_THALES_DATE_OBJECT_DESTROY & 0x0FFFFFFF) | CKA_VORM_DEFINED )

#define CKA_THALES_DATE_KEY_ACTIVATION                         ( CKA_THALES_KEY_STATE_ACTIVATED | CKA_THALES_KEY_STATE_START_DATE  )
#define CKA_THALES_DATE_KEY_SUSPENSION                         ( CKA_THALES_KEY_STATE_SUSPENDED | CKA_THALES_KEY_STATE_START_DATE  )
#define CKA_THALES_DATE_KEY_EXPIRATION                         ( CKA_THALES_KEY_STATE_EXPIRED   | CKA_THALES_KEY_STATE_START_DATE  )
#define CKA_THALES_DATE_KEY_DEACTIVATION                       ( CKA_THALES_KEY_STATE_DEACTIVATED | CKA_THALES_KEY_STATE_START_DATE  )
#define CKA_THALES_DATE_KEY_COMPROMISED                        ( CKA_THALES_KEY_STATE_COMPROMISED | CKA_THALES_KEY_STATE_START_DATE  )
#define CKA_THALES_DATE_KEY_COMPROMISE_OCCURRENCE              ( CKA_THALES_KEY_STATE_COMPROMISED | CKA_THALES_KEY_STATE_OCCURRENCE_DATE  )

#define CKA_THALES_DATE_KEY_ACTIVATION_EL                      ( (CKA_THALES_DATE_KEY_ACTIVATION & 0x0FFFFFFF) | CKA_VORM_DEFINED ) 
#define CKA_THALES_DATE_KEY_SUSPENSION_EL                      ( (CKA_THALES_DATE_KEY_SUSPENSION & 0x0FFFFFFF) | CKA_VORM_DEFINED ) 
#define CKA_THALES_DATE_KEY_EXPIRATION_EL                      ( (CKA_THALES_DATE_KEY_EXPIRATION  & 0x0FFFFFFF) | CKA_VORM_DEFINED ) 
#define CKA_THALES_DATE_KEY_DEACTIVATION_EL                    ( (CKA_THALES_DATE_KEY_DEACTIVATION & 0x0FFFFFFF) | CKA_VORM_DEFINED ) 
#define CKA_THALES_DATE_KEY_COMPROMISED_EL                     ( (CKA_THALES_DATE_KEY_COMPROMISED & 0x0FFFFFFF) | CKA_VORM_DEFINED ) 


#define CKA_THALES_KEY_ACTION_PROTECT_ONLY                     ( CKA_THALES_DEFINED | 0x0102 )
#define CKA_THALES_KEY_ACTION_PROCESS_ONLY                     ( CKA_THALES_DEFINED | 0x0103 )
#define CKA_THALES_DATE_KEY_PROTECT_STOP                       ( CKA_THALES_KEY_ACTION_PROTECT_ONLY | CKA_THALES_KEY_STATE_STOP_DATE  )
#define CKA_THALES_DATE_KEY_PROCESS_START                      ( CKA_THALES_KEY_ACTION_PROCESS_ONLY | CKA_THALES_KEY_STATE_START_DATE  )

#define ASYMKEY_BUF_LEN               4096
#define SYMKEY_BUF_LEN                128
  
#define CKM_THALES_BASE64             0x08000000 /* this is just a modifier for V15HDR */
#define CKM_THALES_V27HDR             0x04000000
#define CKM_THALES_V21HDR             0x02000000
#define CKM_THALES_V15HDR             0x01000000
#define CKM_THALES_ALLHDR             0x07000000

#define CKA_RAW_FORMAT                0x00000000
#define CKA_THALES_PEM_FORMAT         0x00100000 
#define CKA_THALES_DER_FORMAT         0x00400000 
#define CKA_THALES_P7B_FORMAT         0x00700000 
#define CKA_THALES_CACHE_INVALIDATE   0x000F0000

#define CKA_THALES_CACHED_ON_HOST		 ( CKA_VENDOR_DEFINED | 0x61 )
#define CKA_THALES_UNIQUE_TO_HOST	     ( CKA_VENDOR_DEFINED | 0x62 )
#define CKA_THALES_KEY_CACHED_TIME       ( CKA_VENDOR_DEFINED | 0x63 )

#define CKA_THALES_KEY_VERSION           ( CKA_THALES_DEFINED | 0x81 )
#define CKA_THALES_KEY_VERSION_ACTION    ( CKA_THALES_DEFINED | 0x82 )
#define CKA_THALES_KEY_VERSION_LIFE_SPAN ( CKA_THALES_DEFINED | 0x83 )

#define CKA_THALES_VERSIONED_KEY         ( CKA_THALES_DEFINED | 0x85 )
#define CKA_THALES_OBJECT_ALIAS          ( CKA_THALES_DEFINED | 0x86 )
#define CKA_THALES_OBJECT_UUID           ( CKA_THALES_DEFINED | 0x87 )
#define CKA_THALES_OBJECT_MUID           ( CKA_THALES_DEFINED | 0x88 )
#define CKA_THALES_OBJECT_IKID           ( CKA_THALES_DEFINED | 0x89 )

#define CKA_THALES_BASE_LABEL            ( CKA_THALES_DEFINED | 0x71 )
#define CKA_THALES_BASE_ALIAS            ( CKA_THALES_DEFINED | 0x72 )
#define CKA_THALES_BASE_UUID             ( CKA_THALES_DEFINED | 0x73 )
#define CKA_THALES_BASE_MUID             ( CKA_THALES_DEFINED | 0x74 )
#define CKA_THALES_BASE_IKID             ( CKA_THALES_DEFINED | 0x75 )

#define CKA_THALES_CUSTOM_DEFINED        ( CKA_THALES_DEFINED | 0x8000 )
#define CKA_THALES_CUSTOM_1              ( CKA_THALES_CUSTOM_DEFINED | 0x01 )
#define CKA_THALES_CUSTOM_2              ( CKA_THALES_CUSTOM_DEFINED | 0x02 )
#define CKA_THALES_CUSTOM_3              ( CKA_THALES_CUSTOM_DEFINED | 0x03 )
#define CKA_THALES_CUSTOM_4              ( CKA_THALES_CUSTOM_DEFINED | 0x04 )
#define CKA_THALES_CUSTOM_5              ( CKA_THALES_CUSTOM_DEFINED | 0x05 )

#define CKO_THALES_OPAQUE_OBJECT         ( CKA_THALES_DEFINED | 0x0009 )

#define KEY_TRANS_DATES_MAX              10

#ifndef CKF_DISABLE_FIPS
#define CKF_DISABLE_FIPS        0x40000000
#endif

typedef struct encoding {
	CK_BYTE enc_type;
	char enc_name[12];
} encoding_t;


typedef enum  {	
	KeyStatePreActive = 0,
	KeyStateActive = 1,
	KeyStateSuspended = 2,
	KeyStateDeactivated = 3,	
	KeyStateCompromised = 4,
	KeyStateDestroyed = 5	
} KeyState;

typedef enum {
	KeyActionProtectnProcess = 0,
	KeyActionProtectOnly = 1,
	KeyActionProcessOnly = 2
} KeyAction;

extern char *optarg;
extern int optreset;
extern int optind;
extern int opterr;
extern unsigned long ulCachedTime;

#define     versionCreate    0
#define     versionRotate    1
#define     versionMigrate   2
#define     nonVersionCreate 3

#define	    keyIdLabel  0x0001
#define 	keyIdUuid   0x0010
#define 	keyIdMuid   0x0011
#define 	keyIdImport 0x0100
#define     keyIdAlias  0x0101
#define	    keyIdAttr   0x0111


int newgetopt(int argc, char* const *argv, const char *optstr);
char *getPKCS11LibPath( char* libPath);

/*
************************************************************************
* Function: findKeyByName
* Finds a key by its CKA_LABEL which corresponds to the name
* of the key displayed on the DSM.
* This function calls the findKey(label, type) to do 2 search from DSM,
* first search for symmetric key then search for asymmetric key
************************************************************************
* Parameters: keyLabel
* Returns: CK_OBJECT_HANDLE the key handle
************************************************************************
*/
CK_RV findKeyByLabel(char* keyLabel, CK_OBJECT_HANDLE * phKey, CK_OBJECT_CLASS *pObjClass);

/*
************************************************************************
* Function: findKey
* Finds a key by its CKA_LABEL and CKA_CLASS which corresponds to the name and type
* of the key displayed on the DSM.
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
CK_RV findKey( char* keySearchId, int keyidType,  CK_OBJECT_CLASS keyType, CK_OBJECT_HANDLE * phKey );


CK_RV findKeyByVersion( char* keyLabel, CK_ULONG keyVersion, CK_OBJECT_HANDLE_PTR phKey );

/*
 * findKeyByType retrieve all the keys that are specific type
 */
CK_RV findKeyByType( CK_OBJECT_CLASS keyType, CK_OBJECT_HANDLE phaKey[] ) ;
/*
************************************************************************
* Function: deleteKey
* Delete key from the DSM by key handle.
************************************************************************
* Parameters: hKey -- the handle of the key on DSM to be deleted
* Returns: CK_RV
************************************************************************
*/
CK_RV deleteKey (CK_OBJECT_HANDLE hKey, CK_BBOOL bSetKeyState);

/*
**************************************************************************
 * Function: cleanup
 * Cleans up the local memory, and unloads the dll
 *************************************************************************
 * Parameters: CK_RV rc
 * Return: CK_RV rc
 *************************************************************************
 */

void cleanup (void);

/*
************************************************************************
 * Function: initPKCS11Library
 * Loads the dll and gets the function list from the DLL
 ***********************************************************************
 * Parameters: const char* filename -- location of the DLL
 * Returns: CK_RV rc
 ***********************************************************************
 */

CK_RV initPKCS11Library (const char* filename);

/*
 ************************************************************************
 * Function: initSlotList
 * Gets the slot list from the DSM. The DSM will only have 1 slot.
 ************************************************************************
 * Parameters: none
 * returns: CK_RV
 ************************************************************************
 */

CK_RV  initSlotList (void);

/*
 ************************************************************************
 * Function: openSessionAndLogin
 ************************************************************************
 * Opens a session on the DSM and logs in as a user.
 * Sets the session handle global to be used for the remainder of this program.
 * The password for user login is the password specified to the DSM
 * during agent registration.
 ************************************************************************
 * Parameters: none
 * Returns: CK_RV
 ************************************************************************
 */
CK_RV openSessionAndLogin ( char* userPin, int slotId );


/* 
 ************************************************************************
 * Function: createKey
 * Creates and AES key on the DSM. 
 * The keyLabel is the name of the key displayed on the DSM.
 * key_size, the key size for symmetric key in bytes
 ************************************************************************
 * Returns: CK_RV
 ************************************************************************
 */
CK_RV createKeyS (char* keyLabel, int key_size);
/*
 ************************************************************************
 * Function: createKey
 * Creates and AES key on the DSM.
 * The keyLabel is the name of the key displayed on the DSM.
 * key_size, the key size for symmetric key in bytes
 * keyAlias, the aliases for the symmetric key on the DSM.
 * lifespan, the lifespan for the symmetric key, key with lifespan will be versioned key
 * gen_action, key version action, can be 0, 1, 2, 3
 ************************************************************************
 * Parameters: keyLabel, keyAlias, gen_action, ulifespan, key_size
 * Returns: CK_RV
 ************************************************************************
 */

CK_RV createKey (char* keyLabel, char * keyAlias, int gen_action, CK_ULONG ulifespan, int key_size); 


/*
 *  ************************************************************************
 *  Function: createSymKeyCustom
 *  Creates and AES 256 key on the DSM.
 *  The keyLabel is the name of the key displayed on the DSM.
 *  ************************************************************************
 */

CK_RV createSymKeyCustom(char *keyLabel, char *keyAlias, int gen_action, char *custom1, char *custom2, char *custom3);
	
/*
 ************************************************************************
 * Function: createOpaque
 * Creates an opaque object on the DSM.
 * The keyLabel is the name of the opaque object displayed on the DSM.
 ************************************************************************
 * Parameters: label, value length 
 * Returns: CK_RV
 ************************************************************************
 */

CK_RV createOpaque (char* label, char * value, int length); 

/*
 ************************************************************************
 * Function: createObject
 * Creates and AES key on the DSM, specify the value of the key
 * The keyLabel is the name of the key displayed on the DSM.
 ************************************************************************
 * Parameters: keyLabel
 * Returns: CK_RV
 ************************************************************************
 */
CK_RV createObject (char* keyLabel);


/*
 ************************************************************************
 * Function: setKeyAlias
 * 
 ************************************************************************
 * Parameters: hKey, alias
 * Returns: CK_RV
 ************************************************************************
 */
CK_RV setKeyAlias(CK_OBJECT_HANDLE hKey, char *alias);
	
/*
************************************************************************
* Function: getKeyAttributes
* Demos how to get key attributes from DSM
************************************************************************
* Parameters: hKey - the key handle
* Returns: CK_RV
************************************************************************
*/

CK_RV getKeyAttributes(CK_OBJECT_HANDLE hKey);
/*
 ************************************************************************
 * Function: logout
 * Logs out of the DSM and closes the session
 ************************************************************************
 * Parameters: none
 * Returns: CK_RV
 ************************************************************************
 */
CK_RV logout(void);

/*
************************************************************************
* Function: dumpHexArray
* Print out Hexical from a byte array
************************************************************************
* Parameters: array - a byte array, length - the length of byte array to dump
* Returns: none
************************************************************************
*/

CK_RV getAsymAttributesValue(CK_OBJECT_HANDLE hKey, CK_OBJECT_CLASS	 objClass, CK_BYTE modulusBuf[], CK_ULONG *pModulusBufSize,
						 CK_BYTE exponentBuf[], CK_ULONG *pExponentBufSize);

CK_RV getSymAttributesValue(CK_OBJECT_HANDLE hKey, CK_ULONG keyDateCount, CK_ATTRIBUTE_TYPE attrTypes[], char *pLabel);

void dumpHexArray( CK_BYTE* array, int length );

CK_BYTE_PTR hexStringArray(const char *hexstr, CK_ULONG *outlen);

int parse_format_type(char *sel); 

int parse_ksid_sel(char* sel, char** ppKsid);

void parse_ck_date(char* optarg, CK_DATE *pcDate);

char * parse_key_class(char * key, CK_OBJECT_CLASS  *pObjCls);

CK_BYTE get_enc_mode(const char * charset_type);

int fgetline(char **lineptr, int *n, FILE *stream);

void trim(char * str);

int gen_utf(unsigned X /* in */, CK_BYTE enc_type /* in */, unsigned char *Z /* out */);

CK_BYTE * get_BOM_mode(CK_BYTE* pBuf, int* pReadlen, CK_BYTE* bom_mode);

void put_BOM_mode(CK_BYTE bom_mode, FILE* stream);


CK_RV readObjectBytes( FILE * fp, CK_BYTE_PTR pObjBuf, CK_ULONG * pulObjLen, int format_type );
#endif /* __pkcs11_sample_helper_h__ */
