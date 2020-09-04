package com.vormetric.pkcs11.sample;
/*************************************************************************
 **                                                                      **
 ** Copyright(c) 2013                              Confidential Material **
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
 * File: FindExportKey.java
 ***************************************************************************
 ***************************************************************************
 * This file is designed to be run after CreateKey and
 * demonstrates the following:
 * 1. Initialization
 * 2. Creating a connection and logging in.
 * 3. Querying for a key using the keyname.
 * 4. Export the key that was found.
 * 4. Clean up.
 */

import java.io.*;
import java.security.*;
import sun.security.pkcs11.wrapper.*;
import static sun.security.pkcs11.wrapper.PKCS11Constants.*;
import sun.security.pkcs11.Secmod.*;
import java.util.Arrays;

public class FindExportKey {

    public static final String defsourceKeyName = "vpkcs11_java_test_key";

    public static final String defWrappingKeyName = "vpkcs11_java_test_wrappingKey";
    public static final String appName = "vpkcs11_java_test with real wrappingKey";
    public static final String keyValue = "this is my sample key data 12345";
    public static final byte[] iv = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x10, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F};

    public static final String keyFileName = "wrappedKey_find_export.dat";
    public static final String keyFileName2 = "decrypted_wrappedKey_find_export.dat";

    public static void usage()
    {
        System.out.println ("usage: java com.vormetric.pkcs11.sample.FindExportKey -p pin [-k sourceKeyName] [-m module]");
        System.exit (1);
    }

    public static void main ( String[] args)
    {
        String pin = null;
        String libPath = null;
        String sourceKeyName = null;
        String wrappingKeyName = null;
        String initArgs = "";

        int i;
        for (i=0; i<args.length; i+=2)
        {
            if (args[i].equals("-p")) pin = args[i+1];
            else if (args[i].equals("-m")) libPath = args[i+1];
            else if (args[i].equals("-k")) sourceKeyName = args[i+1];
            else if (args[i].equals("-w")) wrappingKeyName = args[i+1];
            else if (args[i].equals("-a")) initArgs = args[i+1];
            else usage();
        }

        try
        {
            if(sourceKeyName == null)
                sourceKeyName = defsourceKeyName;

            if(wrappingKeyName == null)
                wrappingKeyName = defWrappingKeyName;

            System.out.println ("Start FindExportKey ..." );
            Vpkcs11Session session = Helper.startUp(Helper.getPKCS11LibPath(libPath), pin, initArgs);

            long sourceKey = Helper.findKey(session, sourceKeyName) ;

            if (sourceKey == 0)
            {
                System.out.println ("Source key not found, creating it..." );
                sourceKey = Helper.createKeyObject(session, sourceKeyName, appName, keyValue);
            }

            long wrappingKey = Helper.findKey(session, wrappingKeyName);
            if (wrappingKey == 0)
            {
                System.out.println ("Wrapping key not found, creating it..." );
                wrappingKey = Helper.createKeyObject(session, wrappingKeyName, appName, keyValue);
            }

			/* If any key are found, they are returned in the keyID array.
			   Check the keyID array length to see if the find is successful */
            if (sourceKey != 0)
            {
                System.out.println ("Successfully found source key. Handle = " + sourceKey);
                System.out.println ("Successfully found wrapping key. Handle = " + wrappingKey);
                CK_MECHANISM mechanism = new CK_MECHANISM (CKM_AES_CBC_PAD, iv);
				/* If the key is found, delete the key */
                byte[] wrappedKey = session.p11.C_WrapKey(session.sessionHandle, mechanism, wrappingKey, sourceKey );
                System.out.println ("Successfully wrapped key. wrapped key length: "  + wrappedKey.length);
                Helper.saveKey(wrappedKey, keyFileName);

            }
            else
            {
                // shouldn't happen.
                System.out.println ("Source Key not found. No exporting");
            }

            Helper.closeDown(session);
            System.out.println ("End FindExportKey." );
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
