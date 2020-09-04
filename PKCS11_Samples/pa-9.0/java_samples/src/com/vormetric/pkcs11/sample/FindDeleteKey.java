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
 * File: FindDeleteKey.java
 ***************************************************************************
 ***************************************************************************
 * This file is designed to be run after CreateKey and  
 * demonstrates the following:
 * 1. Initialization.
 * 2. Creating a connection and logging in.
 * 3. Querying for a key using the keyname.
 * 4. Deleting the key that was found.
 * 5. Clean up.
 */

import java.io.*;
import java.security.*;
import sun.security.pkcs11.wrapper.*;
import static sun.security.pkcs11.wrapper.PKCS11Constants.*;
import sun.security.pkcs11.Secmod.*;

public class FindDeleteKey {

	//public static final String keyName = "test_pub_key";
    public static final String defKeyName = "vpkcs11_java_test_key";

    public static void usage()
    {
        System.out.println ("usage: java com.vormetric.pkcs11.sample.FindDeleteKey -p pin [-k keyName] [-m module]");
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
	        if(keyName == null)
	            keyName = defKeyName;

            System.out.println ("Start FindDeleteKey ..." );
            Vpkcs11Session session = Helper.startUp(Helper.getPKCS11LibPath(libPath), pin, initArgs);

            long keyID = Helper.findKey(session, keyName) ;

            if (keyID == 0)
            {
                System.out.println ("The key is not found, no deletion." );
            }
            else
            {
                /* If the key is found, delete the key */
                System.out.println ("The key is found: "+keyName + "; Deleting key...");
                session.p11.C_DestroyObject (session.sessionHandle, keyID);
                System.out.println ("Successfully deleted the key from DSM.");
            }

            keyID = Helper.findKey(session, keyName) ;
            if (keyID == 0)
            {
                System.out.println ("The key is not found; delete successful." );
            }
            else
            {
                System.out.println ("The key is found; delete key unsuccessful.");
            }

            Helper.closeDown(session);
            System.out.println ("End FindDeleteKey." );
	    }
		catch (PKCS11Exception e)
	    {
			e.printStackTrace();
	    }
		catch (Exception e)
	    {
			e.printStackTrace();
	    }
    }
}
