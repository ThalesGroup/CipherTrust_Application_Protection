package com.cadp.pkcs11.sample;

/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/


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

import com.cadp.pkcs11.wrapper.*;

import static java.lang.System.exit;
import static com.cadp.pkcs11.wrapper.PKCS11Constants.*;

public class FindExportKey {

    public static final String defsourceKeyName = "pkcs11_java_test_key";

    public static final String appName = "pkcs11_java_test with real wrappingKey";
    public static final String keyValue = "this is my sample key data 12345";
    public static final byte[] iv = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x10, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F};

    public static String outputFileName = "wrappedKey.dat";

    public static void usage()
    {
        System.out.println ("usage: java [-cp CLASSPATH] com.cadp.pkcs11.sample.FindExportKey -p pin [-k sourceKeyName] [-w wrappingKeyName] [-f keyFilename] [-m module]");
        System.out.println("-p: Username:Password of Keymanager");
        System.out.println("-k: Keyname on Keymanager");
        System.out.println("-w: Wrapping keyname on Keymanager");
        System.out.println("-m: Path of directory where dll is deployed/installed");
        System.out.println("-f: KeyFilename type name i.e pem");
        exit (1);
    }

    public static void main ( String[] args)
    {
        String pin = null;
        String libPath = null;
        String sourceKeyName = null;
        String wrappingKeyName = null;
        String formatName = null;
        CK_MECHANISM mechanism = null;
        long objClass = CKO_SECRET_KEY;
        Vpkcs11Session session = null;
        long wrapObjClass = 0L;
        long wrappingKey = 0L;

        for (int i=0; i<args.length; i+=2)
        {
            if (args[i].equals("-p")) pin = args[i+1];
            else if (args[i].equals("-m")) libPath = args[i+1];
            else if (args[i].equals("-k")) sourceKeyName = args[i+1];
            else if (args[i].equals("-c")) {
                sourceKeyName = args[i+1];
                objClass = CKO_PUBLIC_KEY;
            }
            else if (args[i].equals("-v")) {
                sourceKeyName = args[i+1];
                objClass = CKO_PRIVATE_KEY;
            }
            else if (args[i].equals("-w")) wrappingKeyName = args[i+1];
            else if (args[i].equals("-f")) formatName = args[i+1];
            else if (args[i].equals("-o")) outputFileName = args[i+1];
            else usage();
        }

        try
        {
            if(sourceKeyName == null)
                sourceKeyName = defsourceKeyName;

            System.out.println ("Start FindExportKey ..." );
            session = Helper.startUp(Helper.getPKCS11LibPath(libPath),pin );

            long sourceKey = Helper.findKey(session, sourceKeyName, objClass) ;

            if (sourceKey == 0)
            {
                System.out.println ("Exporting source key not found, exiting..." );
                return;
            }
            else
                System.out.println ("Successfully found source key. Handle = " + sourceKey);

            if(wrappingKeyName != null) {

                wrapObjClass = Helper.parseKeyName(wrappingKeyName);
                if(wrapObjClass != 0) {
                    wrappingKeyName = wrappingKeyName.substring(2);
                    wrappingKey = Helper.findKey(session, wrappingKeyName, wrapObjClass);
                }
                else {
                    wrappingKey = Helper.findKey(session, wrappingKeyName);
                }
            }

	        mechanism = new CK_MECHANISM (CKM_AES_CBC_PAD, iv);

            if (wrappingKey == 0)
            {
                System.out.println ("No wrapping key to be used, ..." );
            }
            else  {
                System.out.println ("Successfully found wrapping key. Handle: " + wrappingKey);
            }

		/* If any key are found, they are returned in the keyID array.
			   Check the keyID array length to see if the find is successful */
            if (sourceKey != 0)
            {
                System.out.println ("Exporting key ... ");
               
                if( formatName != null && formatName.equals("pem") )
                    mechanism.mechanism |= Helper.CKA_THALES_DEFINED | Helper.CKM_THALES_PEM_FORMAT;
                else if( wrappingKey != 0 && !Helper.isKeySymmetric(wrappingKey) ) {
                    mechanism.mechanism = Helper.CKA_THALES_DEFINED | PKCS11Constants.CKM_RSA_PKCS;
                }

                /* If the key is found, delete the key */
                byte[] wrappedKey = session.p11.C_WrapKey(session.sessionHandle, mechanism, wrappingKey, sourceKey );
                Helper.saveKey(wrappedKey, outputFileName);
                System.out.println ("Successfully wrapped key at "+outputFileName+"; wrapped key length: "  + wrappedKey.length);
            }
            else
            {
                // shouldn't happen.
                System.out.println ("Source Key not found. No exporting");
            }
        }

        catch (PKCS11Exception e)
        {
            e.printStackTrace();
        }
        catch (Exception e)
        {
            e.printStackTrace();
        }
        finally {
            Helper.closeDown(session);
            System.out.println ("End FindExportKey." );
        }
    }
}
