/*************************************************************************
**                                                                                                                           
** Copyright(c) 2014                              Confidential Material                                           
**                                                                                                                    
** This file is the property of Vormetric Inc.                                                                      
** The contents are proprietary and confidential.                                                               
** Unauthorized use, duplication, or dissemination of this document,                                      
** in whole or in part, is forbidden without the express consent of                                         
** Vormetric, Inc..                                                                                                       
**                                                                                                                            
**************************************************************************/
/*
 ***************************************************************************
 * File: vpkcs11_sample_helper.h
 ***************************************************************************
 ***************************************************************************
 * vpkcs11 sample helper header file
 ***************************************************************************
 */

#ifndef __vpkcs11_sample_helper_h__
#define __vpkcs11_sample_helper_h__

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

#define AES_BLOCK_SIZE 16
#define KEYLEN			32

extern CK_FUNCTION_LIST_PTR FunctionListFuncPtr;
extern CK_OBJECT_HANDLE     hGenKey;
extern CK_SESSION_HANDLE    hSession;

#define kp  ((int)'k' << 8 | (int)'p')

typedef struct encoding {
	CK_BYTE enc_type;
	char enc_name[12];
} encoding_t;

extern char *optarg;
extern int optreset;
extern int optind;
extern int opterr;

int getopt(int argc, char* const *argv, const char *optstr);
char* getPKCS11LibPath( char* libPath);

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
CK_OBJECT_HANDLE findKeyByName(char* keyLabel);

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
CK_OBJECT_HANDLE findKey ( char* keyLabel, CK_OBJECT_CLASS keyType );

CK_OBJECT_HANDLE findKeyByLabel( char* keyLabel) ;

CK_OBJECT_HANDLE findKeyByType( CK_OBJECT_CLASS keyType ) ;
/*
************************************************************************
* Function: deleteKey
* Delete key from the DSM by key handle.
************************************************************************
* Parameters: hKey -- the handle of the key on DSM to be deleted
* Returns: CK_RV
************************************************************************
*/
CK_RV deleteKey (CK_OBJECT_HANDLE hKey);

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
 * Creates and AES 256 key on the DSM. 
 * The keyLabel is the name of the key displayed on the DSM.
 ************************************************************************
 * Parameters: none
 * Returns: CK_RV
 ************************************************************************
 */

CK_RV createKey (char* keyLabel);

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
void dumpHexArray( CK_BYTE* array, int length );


CK_BYTE get_enc_mode(const char * charset_type);

void trim(char * str);

int gen_utf(unsigned X /* in */, CK_BYTE enc_type /* in */, unsigned char *Z /* out */);

CK_BYTE * get_BOM_mode(CK_BYTE* pBuf, int* pReadlen, CK_BYTE* bom_mode);

void put_BOM_mode(CK_BYTE bom_mode, FILE* stream);
#endif /* __vpkcs11_sample_helper_h__ */
