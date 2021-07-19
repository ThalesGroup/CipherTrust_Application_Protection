/*************************************************************************
**                                                                      **
** Copyright(c) 2012 - 2014                       Confidential Material **
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
 * File: vpkcs11_sample_helper.c
 ***************************************************************************

 ***************************************************************************
 * This file demonstrates the following
 * 1. Initialization
 * 2. Creating a connection and logging in.
 * 2. Close a connection and logging off.
 * 4. Clean up.
 ***************************************************************************
 */

#include "vpkcs11_sample_helper.h"
#include <stdarg.h>

/*
 **************************************************************************
 *   * Globals 
 **************************************************************************
 */


#define MAX_FIND_RETURN 1


#ifdef _WIN32 
static HINSTANCE dllHandle = NULL;
#else
static void * dllPtr = NULL;
#endif

CK_FUNCTION_LIST_PTR FunctionListFuncPtr = NULL;
static CK_ULONG SlotCount = 0;
static CK_SLOT_ID_PTR SlotList = NULL;

CK_SESSION_HANDLE    hSession = CK_INVALID_HANDLE;

static CK_UTF8CHAR   app[] = { "VORMETRIC_PKCS11_SAMPLE" };
CK_OBJECT_HANDLE hGenKey = 0x0;

#define FPE_LITTLE_ENDIAN	1
#define FPE_BIG_ENDIAN		2

#ifdef _WIN32 
static char* WinX86InstallPath = "C:\\Program Files (x86)\\Vormetric\\DataSecurityExpert\\Agent\\pkcs11\\bin\\vorpkcs11.dll";
static char* WinX64InstallPath = "C:\\Program Files\\Vormetric\\DataSecurityExpert\\Agent\\pkcs11\\bin\\vorpkcs11.dll";
#else
static char* UnixInstallPath = "/opt/vormetric/DataSecurityExpert/agent/pkcs11/lib/libvorpkcs11.so";
#endif

#define INT_LEN (10)
#define HEX_LEN (8)
#define BIN_LEN (32)
#define OCT_LEN (11)

int     opterr = 1;              /* if error message should be printed */
int     optind = 1;             /* index into parent argv vector */
int     optopt;                  /* character checked for validity */
int     optreset;                /* reset getopt */
char   *optarg;                /* argument associated with option */

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
void dumpHexArray( CK_BYTE* array, int length )
{
  int idx = 0;
  for ( idx = 0; idx < length; idx++)
  {
    printf ( "0x%02X|", *(array+idx));
  }
  printf ( "\n");

}

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
CK_OBJECT_HANDLE findKeyByName(char* keyLabel)
{
    CK_OBJECT_HANDLE	hKey = 0x0;
    hKey = findKey(keyLabel, CKO_SECRET_KEY);
    if (CK_INVALID_HANDLE == hKey)
    {
        hKey = findKey(keyLabel, CKO_PUBLIC_KEY);
    }
    return hKey; 
}

CK_OBJECT_HANDLE findKeyByLabel(char* keyLabel) 
{
    CK_OBJECT_HANDLE hKey = CK_INVALID_HANDLE;

    CK_RV rc = CKR_OK;

    CK_UTF8CHAR  *label = (CK_UTF8CHAR *) keyLabel;
    CK_ULONG len = (CK_ULONG) strlen(keyLabel);

    /* find the key by CKA_LABEL. */
    CK_ATTRIBUTE   findKeyTemplate[1] =
    {
		{CKA_LABEL, label, len},
    };

    /* find the key by CKA_ID. */
    CK_ULONG       numOfObjReturned = 0;

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
                                                1
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
                                                    &hKey,
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
    return hKey;
}

/*
************************************************************************
* Function: findKeyByType
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

CK_OBJECT_HANDLE findKeyByType( CK_OBJECT_CLASS keyType ) 
{
	
    CK_OBJECT_HANDLE hKey = CK_INVALID_HANDLE;

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
       fprintf (stderr, "FAIL: call to the first C_FindObjectsFinal() failed.\n");
       return hKey;
    }

    rc = FunctionListFuncPtr->C_FindObjectsInit(
                                                hSession,
                                                (CK_ATTRIBUTE_PTR)&findKeyTemplate,
                                                findKeyTemplateSize
                                                );
    if (rc != CKR_OK)
    {
      fprintf (stderr, "FAIL: call to C_FindObjectsInit() failed.\n");
      return hKey;
    }

    /* loop thorugh C_FindObjcts until numOfObjReturned is 0 and we break out 
     * of the loop. we expect to find only 1  key that matches the name. 
     */

    while (CK_TRUE)
    {
       rc = FunctionListFuncPtr->C_FindObjects( hSession,
                                                &hKey,
                                                MAX_FIND_RETURN,
                                                &numOfObjReturned );

       if (rc != CKR_OK )
       {
          fprintf (stderr, "FAIL: call to C_FindObjects() with unexpected result.\n");
          hKey = CK_INVALID_HANDLE;
          break;
       }

       if ((numOfObjReturned == 0) || (numOfObjReturned == 1))
       {
		   break;
       }
    }

    rc = FunctionListFuncPtr->C_FindObjectsFinal(hSession);

    if (rc != CKR_OK)
    {
		fprintf (stderr, "FAIL: Call to C_FindObjectsFinal failed.\n");
		hKey = CK_INVALID_HANDLE;
    }
    return hKey;
}

CK_OBJECT_HANDLE findKey( char* keyLabel, CK_OBJECT_CLASS keyType ) 
{
	
    CK_OBJECT_HANDLE hKey = CK_INVALID_HANDLE;

    CK_RV rc = CKR_OK;
    CK_UTF8CHAR  *label = (CK_UTF8CHAR *) keyLabel;
    CK_ULONG len = (CK_ULONG) strlen(keyLabel);

    /* find the key by CKA_LABEL. */

	CK_ATTRIBUTE findKeyTemplate[] =
		{
			{CKA_LABEL, label, len},
			{CKA_CLASS, &keyType, sizeof(keyType)}
		};	
	
	CK_ULONG  findKeyTemplateSize = sizeof(findKeyTemplate)/sizeof(CK_ATTRIBUTE);
	
    /* find the key by CKA_ID. */
    CK_ULONG            numOfObjReturned = 0;

    /* call FindObjectsFinal just in case there's another search ongoing for this session. */
    rc = FunctionListFuncPtr->C_FindObjectsFinal(hSession);
    if (rc != CKR_OK)
    {
       fprintf (stderr, "FAIL: call to the first C_FindObjectsFinal() failed.\n");
       return hKey;
    }

    rc = FunctionListFuncPtr->C_FindObjectsInit(
                                                hSession,
                                                (CK_ATTRIBUTE_PTR)&findKeyTemplate,
                                                findKeyTemplateSize
                                                );
    if (rc != CKR_OK)
    {
      fprintf (stderr, "FAIL: call to C_FindObjectsInit() failed.\n");
      return hKey;
    }

    /* loop thorugh C_FindObjcts until numOfObjReturned is 0 and we break out 
     * of the loop. we expect to find only 1  key that matches the name. 
     */

    while (CK_TRUE)
    {
       rc = FunctionListFuncPtr->C_FindObjects( hSession,
                                                &hKey,
                                                MAX_FIND_RETURN,
                                                &numOfObjReturned );

       if (rc != CKR_OK )
       {
          fprintf (stderr, "FAIL: call to C_FindObjects() with unexpected result.\n");
          hKey = CK_INVALID_HANDLE;
          break;
       }

       if ((numOfObjReturned == 0) || (numOfObjReturned == 1))
       {
         break;
       }
    }

    rc = FunctionListFuncPtr->C_FindObjectsFinal(hSession);

    if (rc != CKR_OK)
    {
      fprintf (stderr, "FAIL: Call to C_FindObjectsFinal failed.\n");
      hKey = CK_INVALID_HANDLE;
    }
    return hKey;
}

/* 
 ************************************************************************
 * Function: deleteKey
 * Delete key from the DSM by key handle. 
 ************************************************************************
 * Parameters: hKey -- the handle of the key on DSM to be deleted
 * Returns: CK_RV
 ************************************************************************
 */

CK_RV deleteKey (CK_OBJECT_HANDLE hKey)
{
    CK_RV rc;
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
	if (SlotList) {
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
* Determine the path of Vormetric PKCS11 library path base on following priorities: 
* 1. From command line input parameter libPath
* 2. From the environment variable $VPKCS11LIBPATH
* 3. From default installation location of Vormetric PKCS11 library
*************************************************************************
* Parameters: char* path
* Return: 1 : true, 0 : false
*************************************************************************
*/
char* getPKCS11LibPath(char* libPath) 
{
  char * path = NULL;
  if (( libPath != NULL ) && (strcmp(libPath, "") != 0))
  {
    path = libPath;
  }
  else
  {
    path = getenv("VPKCS11LIBPATH");
    if (( path == NULL ) || (strcmp(path, "") == 0))
    {
       /*  try to determine by default installation on windows or Unix */
#ifdef _WIN32 
       if ( isFileExist(WinX86InstallPath))
       {
		   path = WinX86InstallPath;  
       }
       else if ( isFileExist(WinX64InstallPath))
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
        fprintf(stderr, "FAIL: VPKCS11LIBPATH point to a file that does not exist: %s.", path);
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
    initArgs.flags = 0;
    initArgs.pReserved = NULL_PTR;
    pInitArgs = (CK_C_INITIALIZE_ARGS_PTR)&initArgs;
	rc = FunctionListFuncPtr->C_Initialize (pInitArgs);

	return rc;
}

/*
 ************************************************************************
 * Function: initSlotList
 * Gets the slot list from the DSM. The DSM will only have 1 slot.
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
	return rc;
}


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
CK_RV openSessionAndLogin ( char* pin, int slotId)
{
	CK_RV rc = CKR_OK;
	rc = FunctionListFuncPtr->C_OpenSession ( 
											 SlotList[slotId], 
											 0, 
											 "vpkcs11_sample_session", 
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

CK_RV createKey (char* keyLabel)
{
    CK_RV rc = CKR_OK;
    CK_MECHANISM        mechGenKey = { CKM_AES_KEY_GEN, NULL_PTR, 0};
    CK_OBJECT_CLASS     keyClass = CKO_SECRET_KEY;
    CK_KEY_TYPE         keyType = CKK_AES;
    CK_ULONG            keySize = 32; /* 256 bits */
    CK_BBOOL            bFalse = CK_FALSE;
    CK_BBOOL            bTrue = CK_TRUE;
	
    CK_UTF8CHAR  *label = (CK_UTF8CHAR *) keyLabel;
    CK_ULONG len = (CK_ULONG) strlen(keyLabel);
	/* char ch_year[5], ch_month[3], ch_day[3]; */

	char * pcEndDate = (char *)malloc(sizeof(CK_DATE)+1);	
	CK_DATE *pEndDate = (CK_DATE *)pcEndDate;
	
	time_t epoch_t;
	struct tm *ptm;
	struct tm end_tm;
	
    /* AES key template. 
     * CKA_LABEL is the name of the key and will be displayed on the Data Security Manager.
     * CKA_VALUE_LEN is the size of the AES key. 
     */

    CK_ATTRIBUTE aesKeyTemplate[] = {
      {CKA_ID,         label,    len   },
      {CKA_LABEL,         label,    len   },
      {CKA_APPLICATION, &app,       sizeof(app)     },
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
      {CKA_EXTRACTABLE,     &bFalse,    sizeof(bFalse)  },
      {CKA_ALWAYS_SENSITIVE,    &bFalse,    sizeof(bFalse)  },
      {CKA_NEVER_EXTRACTABLE,   &bTrue,     sizeof(bTrue)   },
      {CKA_SENSITIVE,           &bTrue,     sizeof(bTrue)   },
      {CKA_MODIFIABLE,           &bTrue,     sizeof(bTrue)   },
	  {CKA_END_DATE, pEndDate, sizeof(CK_DATE)   }
    };
    CK_ULONG  aesKeyTemplateSize = sizeof(aesKeyTemplate)/sizeof(CK_ATTRIBUTE);

	if(!pcEndDate) {
		printf ("Error allocating memory for end date!\n");
		return CKR_HOST_MEMORY;
	}
		
    time(&epoch_t);
	ptm = localtime( &epoch_t );
	end_tm = *ptm;
	end_tm.tm_sec += 31 * 24 * 60 * 60;
		
    mktime( &end_tm );
		   
	snprintf(pcEndDate, sizeof(CK_DATE)+1, "%04d%02d%02d",
			 end_tm.tm_year + 1900, end_tm.tm_mon + 1, end_tm.tm_mday);
	
    rc = FunctionListFuncPtr->C_GenerateKey(
                                          hSession,
                                          &mechGenKey,
                                          aesKeyTemplate, aesKeyTemplateSize,
                                          &hGenKey
                                           );
  if (rc != CKR_OK || hGenKey == 0)
  {
    printf ("Error generating Key\n");
  }
  else
  {
	printf("Successfully generating Key with name: %s\n", keyLabel);
  }

  if(pcEndDate) {
	  free(pcEndDate);
  }
  return rc;
}

/* 
 ************************************************************************
 * Function: getKeyAttributes
 * Demos how to get key attributes from DSM
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
 * Logs out of the DSM and closes the session
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
* getopt -- Parse argc/argv argument vector.
*/
int getopt(int nargc, char * const nargv[], const char *ostr)
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
		if(nc == ';') {			
			optarg = NULL;
			if (!*place)
				++optind;
		}
		else {
			if(*place) {
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

/* 
 * Trim a string on both ends
 */
void trim(char * str)
{
    int dest;
    int mark = 0;
	int src = 0;
    int len = (int)strlen(str);

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

int gen_utf32(unsigned X, int endianness, unsigned char *Z)
{
	if (X <= 0x10FFFF) {
		if (endianness == FPE_BIG_ENDIAN) {
			Z[3] = X & 0xFF;
			Z[2] = (X >> 8) & 0xFF;
			Z[1] = (X >> 16) & 0xFF;
			Z[0] = (X >> 24) & 0xFF;
		} else {
			Z[0] = X & 0xFF;
			Z[1] = (X >> 8) & 0xFF;
			Z[2] = (X >> 16) & 0xFF;
			Z[3] = (X >> 24) & 0xFF;
		}
		/* printf("UTF32: %02X %02X %02X %02X \n", Z[0], Z[1], Z[2], Z[3]); */
		return 4;
    } else {
		return 0;
	}
}

int gen_utf16(unsigned X, int endianness, unsigned char *Z)
{
	unsigned Y;

	if ((X > 0 && X <= 0xD7FF) || (X >= 0xE000 && X <= 0xFFFF)) {
		if (endianness == FPE_BIG_ENDIAN) {
			Z[1] = X & 0xFF;
			Z[0] = (X >> 8) & 0xFF;
		} else {
			Z[0] = X & 0xFF;
			Z[1] = (X >> 8) & 0xFF;
		}
		/* printf("%02X %02X \n", Z[0], Z[1]); */
		return 2;
	} else if (X >= 0x10000 && X <= 0x10FFFF) {
		X = X - 0x10000;

		if (endianness == FPE_BIG_ENDIAN) {
			Y = (X & 0x3FF) + 0xDC00;
			Z[3] = Y & 0xFF;
			Z[2] = (Y >> 8) & 0xFF;

			Y = ((X >> 10) & 0x3FF) + 0xD800;
			Z[1] = Y & 0xFF;
			Z[0] = (Y >> 8) & 0xFF;
		} else {
			Y = (X & 0x3FF) + 0xDC00;
			Z[2] = Y & 0xFF;
			Z[3] = (Y >> 8) & 0xFF;

			Y = ((X >> 10) & 0x3FF) + 0xD800;
			Z[0] = Y & 0xFF;
			Z[1] = (Y >> 8) & 0xFF;
		}
		/* printf("UTF16: %02X %02X %02X %02X \n", Z[0], Z[1], Z[2], Z[3]); */
		return 4;
	} else {
		return 0;
	}
}

int gen_utf8(unsigned X, unsigned char *Z)
{
    if (X <= 0x7F) {
		Z[0] = X & 0x7F;

		/* printf("%02X \n", Z[0]); */
		return 1;
    } else if (X >= 0x80 && X <= 0x7FF) {
		Z[1] = (X & 0x3F) | 0x80;
		Z[0] = ((X>>6) & 0x1F) | 0xC0; 

		/* printf("%02X %02X \n", Z[0], Z[1]); */
		return 2;
    } else if (X >= 0x800 && X <= 0xFFFF) {
		Z[2] = (X & 0x3F) | 0x80;
		Z[1] = ((X>>6) & 0x3F) | 0x80; 
		Z[0] = ((X>>12) & 0x0F) | 0xE0; 

		/* printf("%02X %02X %02X \n", Z[0], Z[1], Z[2]); */
		return 3;
    } else if (X >= 0x10000 && X <= 0x10FFFF) {
		Z[3] = (X & 0x3F) | 0x80;
		Z[2] = ((X>>6) & 0x3F) | 0x80; 
		Z[1] = ((X>>12) & 0x3F) | 0x80; 
		Z[0] = ((X>>18) & 0x7) | 0xF0; 
		
		/* printf("%02X %02X %02X %02X \n", Z[0], Z[1], Z[2], Z[3]); */
		return 4;
    } else {
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

	if ( !charset_type ) {
		enc_mode = CS_ASCII;
	}
	else if (!strcmp(charset_type, "ASCII")) {
		enc_mode = CS_ASCII;
	}
	else if (!strcmp(charset_type, "UTF-16")) {
		enc_mode = CS_UTF16BE;
	}
	else if (!strcmp(charset_type, "UTF-16LE")) {
		enc_mode = CS_UTF16LE;
	}
	else if (!strcmp(charset_type, "UTF-32")) {
		enc_mode = CS_UTF32BE;
	}
	else if (!strcmp(charset_type, "UTF-32LE")) {
		enc_mode = CS_UTF32LE;
	}
	else if (!strcmp(charset_type, "UTF-8")) {
		enc_mode = CS_UTF8;
	}
	else if (!strncmp(charset_type, "UTF", 3)) {
		enc_mode = CS_UTF8;
	}
	else {
		fprintf(stderr, "Illegal character set type specified: Use one of ASCII, UTF-16, UTF-16LE, UTF-32, UTF-32LE, UTF-8\n");
		return CKR_GENERAL_ERROR;
    }
	return enc_mode;
}

CK_BYTE * get_BOM_mode(CK_BYTE* pBuf, int* pReadlen, CK_BYTE* bom_mode)
{
	CK_BYTE* pPlainBuf;
	/* check for BOM character */
	if(!memcmp(pBuf, "\xFF\xFE\x00\x00", 4)) {
		pPlainBuf = pBuf + 4;
		*pReadlen -= 4;
		*bom_mode = CS_UTF32LE;
	}
	else if (!memcmp(pBuf, "\x00\x00\xFE\xFF", 4)) {
		pPlainBuf = pBuf + 4;
		*pReadlen -= 4;
		*bom_mode = CS_UTF32BE;
	}
	else if (!memcmp(pBuf, "\xFE\xFF", 2)) {
		pPlainBuf = pBuf + 2;
		*pReadlen -= 2;
		*bom_mode = CS_UTF16BE;
	}
	else if (!memcmp(pBuf, "\xFF\xFE", 2)) {
		pPlainBuf = pBuf + 2;
		*pReadlen -= 2;
		*bom_mode = CS_UTF16LE;
	}
	else if (!memcmp(pBuf, "\xEF\xBB\xBF", 3)) {
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
