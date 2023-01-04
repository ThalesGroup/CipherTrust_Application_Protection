package com.vormetric.pkcs11.sample;

/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/


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


import com.vormetric.pkcs11.wrapper.PKCS11Exception;

public class FindDeleteKey {

	public static final String defKeyName = "pkcs11_java_test_key";

    public static void usage()
    {
        System.out.println ("usage: java [-cp CLASSPATH] com.vormetric.pkcs11.sample.FindDeleteKey -p pin [-k keyName] [-m module]");
        System.out.println("-p: Username:Password of Keymanager");
        System.out.println("-k: Keyname on Keymanager");
        System.out.println("-m: Path of directory where dll is deployed/installed");        
        System.exit (1);
    }

    public static void main ( String[] args)
	{
        String pin = null;
        String libPath = null;
        String keyName = "pkcs11_java_test_key";
        Vpkcs11Session session = null;

        for (int i=0; i<args.length; i+=2)
        {
            if (args[i].equals("-p")) pin = args[i+1];
            else if (args[i].equals("-m")) libPath = args[i+1];
            else if (args[i].equals("-k")) keyName = args[i+1];
            else usage();
        }

		try
	    {
	        if(keyName == null)
	            keyName = defKeyName;

            System.out.println ("Start FindDeleteKey ..." );
            session = Helper.startUp(Helper.getPKCS11LibPath(libPath), pin);

            long keyID = Helper.findKey(session, keyName) ;

            if (keyID == 0)
            {
                System.out.println ("The key is not found, no deletion." );
            }
            else
            {
                System.out.println ("The key is found: "+keyName + "; Setting key state to be deactivated...");
                Helper.setKeyState (session, keyID, Helper.KeyState.Deactivated);
                System.out.println ("Successfully set the key state: "+ Helper.KeyState.Deactivated);

                /* If the key is found, delete the key */
                System.out.println ("The key is found: "+keyName + "; Deleting key...");
                session.p11.C_DestroyObject (session.sessionHandle, keyID);
                System.out.println ("Successfully deleted the key from KeyManager.");
            }

            keyID = Helper.findKey(session, keyName);

            if (keyID == 0)
            {
                System.out.println ("The key is not found; delete successful." );
            }
            else
            {
                System.out.println ("The key is found; delete key unsuccessful.");
            }
	    }
		catch (PKCS11Exception e)
	    {
			e.printStackTrace();
                       System.out.println("The Cause is " + e.getMessage() + ".");
	               throw e;
	    }
		catch (Exception e)
	    {
			e.printStackTrace();
                       System.out.println("The Cause is " + e.getMessage() + ".");
	               throw e;
	    }
	    finally {
            Helper.closeDown(session);
            System.out.println ("End FindDeleteKey." );
        }
    }
}
