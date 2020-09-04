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
 * File: vpkcs11_sample_renew_cert.c
 ***************************************************************************
 ***************************************************************************
 * This file call C_Initialize() for certificate renewal. This sample
 * is to be used as a cron job when an application using the pkcs11
 * library does not have persmission to renew the agent certificate
 * before it expires. The steps involved are:
 *
 * 1. Initialization
 * 2. Clean up.
 */

/*
 *  vpkcs11_sample_renew_cert.c
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

int main(int argc, char* argv[])
{
    CK_RV rc;
    char *foundPath = NULL;
    char *libPath = NULL;
    (void) argv;
    (void) argc;

    /* load PKCS11 library and initalize. */
    printf("Initializing PKCS11 library \n");
    foundPath = getPKCS11LibPath(libPath);
    if(foundPath == NULL)
    {
	printf("Error getting PKCS11 library path.\n");
	return 1;
    }

    rc = initPKCS11Library(foundPath);
    if (rc != CKR_OK)
    {
	fprintf(stderr, "FAIL: Unable to initialize PKCS11 library. \n");
	return 2;
    }

    cleanup();
    printf("End Certificate renewal sample.\n");
    fflush(stdout);
    return 0;
}

