package com.vormetric.pkcs11.sample;


import sun.security.pkcs11.wrapper.CK_ATTRIBUTE;
/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/

/*
***************************************************************************
* File: CreateKey.java
***************************************************************************
***************************************************************************
* This file demonstrates the following:
* 1. Initialization.
* 2. Create a connection and log in.
* 3. Create a symmetric key on the KeyManager.
* 4. Clean up.
***************************************************************************
*/


public class CreateKey{

    public static void migrateNonVersionedKey(Vpkcs11Session session, long hKey, int gen_action)
	{
		try {
            CK_ATTRIBUTE[] setAttributes = new CK_ATTRIBUTE[] {
            	new CK_ATTRIBUTE (0x40000082L, gen_action) /* CKA_THALES_KEY_VERSION_ACTION */
            };
            session.p11.C_SetAttributeValue(session.sessionHandle, hKey, setAttributes);
		}
        catch (Exception e)
        {
            e.printStackTrace();
        }
	}

    public static void usage()
    {
        System.out.println ("usage: java [-cp CLASSPATH] com.vormetric.pkcs11.sample.CreateKey -p pin [-k keyName] [-m module] [-g gen_key_action] [-as always_sensitive] [-ne never_extractable] [-ls lifeSpan]");
        System.out.println("-p: Username:Password of Keymanager");
        System.out.println("-k: Keyname on Keymanager");
        System.out.println("-m: Path of directory where dll is deployed/installed");
        System.out.println("-g: 0 for versionCreate, 1 for versionRotate, 2 for versionMigrate, 3 for nonVersionCreate");
	System.out.println("-as: Always Sensitive, it allows the source key to be exported only when wrappingKey is provided");
        System.out.println("-ne: Never Extractable, if this flag is set ,key wrapping never succeeds, no matter whether wrapping key exists or not");
        System.out.println("-ls: Life Span, Life span of key in days");
        System.out.println("Note: Always Sensitive and Never Extractable flags both are used to prevent unencrypted keys from being exported from the Key Manager.");
        System.exit (1);
    }

    public static void main ( String[] args)
    {
        String pin = null;
        String libPath = null;
        String keyName = "pkcs11_java_test_key";
        int genAction = 3;
        int lifespan = 0;
        boolean bAlwSens = false;
        boolean bNevExtr = false;
        Vpkcs11Session session = null;

        for (int i=0; i<args.length; i+=2)
        {
            if (args[i].equals("-p")) pin = args[i+1];
            else if (args[i].equals("-m")) libPath = args[i+1];
            else if (args[i].equals("-k")) keyName = args[i+1];
            else if (args[i].equals("-g")) genAction = Integer.parseInt(args[i+1]);
            else if (args[i].equals("-ls")) lifespan = Integer.parseInt(args[i+1]);
            else if (args[i].equals("-as")) bAlwSens = true;
            else if (args[i].equals("-ne")) bNevExtr = true;
            else usage();
        }

		try
	    {
            System.out.println ("Start CreateKey ..." );
            session = Helper.startUp(Helper.getPKCS11LibPath(libPath), pin);

            long keyID = Helper.findKey(session, keyName) ;

            if (genAction == 2 /* migrate */)
            {
                System.out.println("Key: " +keyName + ", ID: " + keyID);

				migrateNonVersionedKey(session, keyID, genAction);
                System.out.println ("Key: " + keyName + " was migrated.");

                keyID = Helper.findKey(session, keyName) ;

                System.out.println("Key: " +keyName + ", ID: " + keyID);
            }
            else if (genAction == 1 /* rotate */)
            {
                keyID = Helper.createKey(session, keyName, genAction, 0, bAlwSens, bNevExtr);
                if(keyID != 0)
                    System.out.println ("Key: " + keyName + " was rotated.");
                else
                    System.out.println ("Key: " + keyName + " was not rotated.");
            }
            else if (keyID == 0)
            {
                System.out.println ("The key not found, creating it..." );
                keyID = Helper.createKey(session, keyName, genAction, lifespan, bAlwSens, bNevExtr);

                if(keyID != 0)
                    System.out.println ("Key successfully Generated. Key Handle: " + keyID);
                else
                    System.out.println ("Key: " + keyName + " was not generated.");
            }
            else
            {
                System.out.println ("There is a key with same name already exists in KeyManager, Please run FindDeleteKey to delete it from KeyManager.");
            }
	    }
		catch (Exception e)
	    {
            e.printStackTrace();
	    }
	    finally {
            Helper.closeDown(session);
            System.out.println ("End CreateKey." );
        }
    }
}
