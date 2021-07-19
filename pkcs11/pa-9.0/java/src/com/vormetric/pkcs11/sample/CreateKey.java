package com.vormetric.pkcs11.sample;
/*************************************************************************
**                                                                                                                                           **
** Copyright(c) 2014                                    Confidential Material                                          **
**                                                                                                                                            **
** This file is the property of Vormetric Inc.                                                                            **
** The contents are proprietary and confidential.                                                                   **
** Unauthorized use, duplication, or dissemination of this document,                                    **
** in whole or in part, is forbidden without the express consent of                                        **
** Vormetric, Inc..                                                                                                                    **
**                                                                                                                                             **
**************************************************************************/
/*
 ***************************************************************************
 * File: CreateKey.java
 ***************************************************************************
 ***************************************************************************
 * This file demonstrates the following:
 * 1. Initialization.
 * 2. Create a connection and log in.
 * 3. Create a symmetric key on the Data Security Manager.
 * 4. Clean up.
 ***************************************************************************
 */


import java.io.*;
import java.security.*;
import sun.security.pkcs11.wrapper.*;
import static sun.security.pkcs11.wrapper.PKCS11Constants.*;
import sun.security.pkcs11.Secmod.*;

public class CreateKey{

    public static void usage()
    {
        System.out.println ("usage: java com.vormetric.pkcs11.sample.CreateKey -p pin -k keyName [-m module]");
        System.exit (1);
    }

    public static void main ( String[] args) 
    {
        String pin = null;
        String libPath = null;
        String keyName = "vpkcs11_java_test_key";
        String initArgs = "";

        int i;
        for (i=0; i<args.length; i+=2)
        {
            if (args[i].equals("-p")) pin = args[i+1];
            else if (args[i].equals("-m")) libPath = args[i+1];
            else if (args[i].equals("-k")) keyName = args[i+1];
            else if (args[i].equals("-a")) initArgs = args[i+1];
            else usage();
        }

		try 
	    {
            System.out.println ("Start CreateKey ..." );
            Vpkcs11Session session = Helper.startUp(Helper.getPKCS11LibPath(libPath), pin, initArgs);

            long keyID = Helper.findKey(session, keyName) ;

            if (keyID == 0)
            {
                System.out.println ("The key not found, creating it..." );
                keyID = Helper.createKey(session, keyName);

                if(keyID != 0)
                    System.out.println ("Key successfully Generated. Key Handle: " + keyID);
                else
                    System.out.println ("Key: " + keyName + " was not generated.");
            }
            else
            {
                System.out.println ("There is a key with same name already exists in DSM, Please run FindDeleteKey to delete it from DSM.");
            }

            Helper.closeDown(session);
            System.out.println ("End CreateKey." );
	    }
		catch (Exception e)
	    {
            e.printStackTrace();
	    }
    }
}
