/**                                                                      **
** Copyright(c) 2012 - 2017                       Confidential Material **
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
 * File: vpkcs11_sample_getinfo.c
 ***************************************************************************
 ***************************************************************************
 * This file demonstrates the following
 * 1. Initialization
 * 2. Call C_GetInfo.
 */

/* 
   vpkcs11_sample_getinfo.c
 */

#include "vpkcs11_sample_helper.h"
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

/*
 ************************************************************************
 * Function: main
 ************************************************************************
 */
int main (int argc, char* argv[])
{
    CK_RV rc; 
    char *libPath = NULL;
    char *foundPath = NULL;
    CK_INFO info;

    (void) argc;
    (void) argv;

    printf("Begin GetInfo Message sample.\n");

    /* load PKCS11 library and initalize. */
    printf("Initializing PKCS11 library \n");
    foundPath = getPKCS11LibPath(libPath);
    if(foundPath == NULL)
    {
	printf("Error getting PKCS11 library path.\n");
	return 16;
    }
		
    rc = initPKCS11Library(foundPath);		
    if (rc != CKR_OK)
    {
	fprintf(stderr, "FAIL: Unable to initialize PKCS11 library. \n");
	return 17;
    }

    memset(&info, 0, sizeof (CK_INFO));
    rc = FunctionListFuncPtr->C_GetInfo(&info);
    if (rc != CKR_OK)
    {
	fprintf(stderr, "FAIL: Unable to get PKCS11 library Info. \n");
	return 18;
    }

    info.manufacturerID[31] = 0;
    info.libraryDescription[31] = 0;
    printf("\nVAE Library C_GetInfo results\n\n");
    printf("\tCryptoki Version: %d.%d\n", info.cryptokiVersion.major,
	   info.cryptokiVersion.minor);
    printf("\tManufacturer ID: %s\n", &info.manufacturerID[0]);
    printf("\tFlags: %lu\n", info.flags);
    printf("\tLibrary Description: %s\n", &info.libraryDescription[0]);
    printf("\tLibrary Version: %d.%d\n\n", info.libraryVersion.major, info.libraryVersion.minor);
    return 0;
}
