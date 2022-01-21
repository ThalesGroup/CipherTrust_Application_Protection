package com.cadp.pkcs11.sample;

/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/

/*
 **************************************************************************
 * File: CreateObject.java
 * This sample performs the following functions
 **************************************************************************
 * Initialize the function.
 * Log into the KeyManager.
 * Create a symmetric  key object on the KeyManager.
 * Log out.
 * Clean up the library.
 *************************************************************************
 */

import java.io.*;
import java.security.*;
import sun.security.pkcs11.wrapper.*;
import static sun.security.pkcs11.wrapper.PKCS11Constants.*;
import sun.security.pkcs11.Secmod.*;

public class CreateObject{
    public static final String defKeyName = "pkcs11_java_test_key";
    public static final String app = "PKCS11_SAMPLE";
    public static final String keyValue = "this is my sample key data 54321";

    public static void usage()
    {
        System.out.println ("usage: java [-cp CLASSPATH] com.cadp.pkcs11.sample.CreateObject -p pin [-m module]");
        System.out.println("-p: Username:Password of Keymanager");
        System.out.println("-m: Path of directory where dll is deployed/installed");
        System.exit (1);
    }

    public static void main ( String[] args)
    {

        String pin = null;
        String libPath = null;
        String keyName = null;
        boolean bAlwSens = false;
        boolean bNevExtr = false;
        Vpkcs11Session session = null;

        for (int i=0; i<args.length; i+=2)
        {
            if (args[i].equals("-p")) pin = args[i+1];
            else if (args[i].equals("-m")) libPath = args[i+1];
            else if (args[i].equals("-k")) keyName = args[i+1];
            else if (args[i].equals("-as")) bAlwSens = true;
            else if (args[i].equals("-ne")) bNevExtr = true;
            else usage();
        }

        try
        {
            if(keyName == null)
                keyName = defKeyName;

            System.out.println ("Start CreateObject ..." );
            session = Helper.startUp(Helper.getPKCS11LibPath(libPath),pin );

            long keyID = Helper.findKey(session, keyName) ;
            long findKeyID;

            if (keyID == 0)
            {
                System.out.println ("the key not found, creating it..." );
                keyID = Helper.createKeyObject(session, keyName, app, keyValue.getBytes(), bAlwSens, bNevExtr);

                if(keyID != 0) {
                    findKeyID = Helper.findKey(session, keyName);
                    System.out.println ("Found key ID: "+findKeyID+" for key name "+keyName);
                }
            }
            else {
                System.out.println("A key with the same name already exists on the KeyManager - please delete the key from the KeyManager first.");
            }
        }
        catch (Exception e)
        {
            e.printStackTrace();
        }
        finally {
            Helper.closeDown(session);
            System.out.println ("End CreateObject." );
        }
    }
}
