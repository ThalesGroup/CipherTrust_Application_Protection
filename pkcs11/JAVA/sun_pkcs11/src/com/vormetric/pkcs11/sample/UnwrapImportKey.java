package com.vormetric.pkcs11.sample;

import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_MODIFIABLE;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_ALWAYS_SENSITIVE;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_CLASS;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_DECRYPT;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_ENCRYPT;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_EXTRACTABLE;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_KEY_TYPE;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_LABEL;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_NEVER_EXTRACTABLE;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_SENSITIVE;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_SIGN;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_TOKEN;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_UNWRAP;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_VALUE_LEN;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_VERIFY;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_WRAP;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKK_AES;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKK_RSA;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKM_AES_CBC_PAD;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKO_PRIVATE_KEY;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKO_PUBLIC_KEY;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKO_SECRET_KEY;
/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/

/*
***************************************************************************
* File: UnwrapImportKey.java
***************************************************************************
***************************************************************************
* This file demonstrates the following:
* 1. Initialization.
* 2. Create a connection and log in.
* 3. Read the wrapped key from the file.
* 4. Unwrap it using wrapping key.
* 5. Clean up.
***************************************************************************
*/
import sun.security.pkcs11.wrapper.CK_ATTRIBUTE;
import sun.security.pkcs11.wrapper.CK_MECHANISM;
import sun.security.pkcs11.wrapper.PKCS11Constants;
import sun.security.pkcs11.wrapper.PKCS11Exception;

public class UnwrapImportKey {

    public static final String defsourceKeyName = "pkcs11_java_test_key_";
    public static final String defWrappingKeyName = "pkcs11_java_test_wrappingKey";

    public static final String appName = "pkcs11_java_test with real wrappingKey";
    public static final String keyValue = "this is my sample key data 12345";
    public static final byte[] iv = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x10, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F};

    public static final String defKeyFileName = "wrappedKey.dat";
    public static final String keyFileName2 = "decrypted_wrappedKey_find_export.dat";

    public static void usage()
    {
        System.out.println ("usage: java [-cp CLASSPATH] com.vormetric.pkcs11.sample.UnwrapImportKey -p pin [-k sourceKeyName]" +
        " [-u wrappingKeyName] [-f keyformat] [-m module] [-c public-key-name] [-v private-key-name] [-i keyfile]");
        System.out.println("-p: Username:Password of Keymanager");
        System.out.println("-k: Source keyname on Keymanager");
        System.out.println("-u: Wrapping Keyname on Keymanager");
        System.out.println("-c: Public keyname on Keymanager");
        System.out.println("-f: Format of key on Keymanager");
        System.out.println("-m: Path of directory where dll is deployed/installed");
        System.out.println("-i: Input filename");    
        System.out.println("-v: Private keyname");
        System.exit (1);
    }
    public static void main ( String[] args) throws Exception
    {
        String pin = null;
        String libPath = null;
        String keyName = null;
        String inputFileName = null;
        String unwrappingKeyName = null;
        String formatName = null;
        byte[] wrappedKey = null;
        CK_ATTRIBUTE[] attrs = null;
        Vpkcs11Session session = null;
        long unwrappingKey = 0L;
        long objClass = CKO_SECRET_KEY;
        long unwrapObjClass = CKO_SECRET_KEY;

        for (int i=0; i<args.length; i+=2)
        {
            if (args[i].equals("-p")) pin = args[i+1];
            else if (args[i].equals("-m")) libPath = args[i+1];
            else if (args[i].equals("-k")) {
                keyName = args[i+1];
            }
            else if (args[i].equals("-c")) {
                keyName = args[i+1];
                objClass = CKO_PUBLIC_KEY;
            }
            else if (args[i].equals("-v")) {
                keyName = args[i+1];
                objClass = CKO_PRIVATE_KEY;
            }
            else if (args[i].equals("-u")) {
                unwrappingKeyName = args[i+1];
            }
            else if (args[i].equals("-i")) inputFileName = args[i+1];
            else if (args[i].equals("-f")) formatName = args[i+1];
            else usage();
        }

        if (pin == null)
            usage();

        try
        {
            if(keyName == null)
                keyName = defsourceKeyName;

            if(inputFileName == null)
                inputFileName = defKeyFileName;

            System.out.println ("Start UnwrapImportKey ..." );
            session = Helper.startUp(Helper.getPKCS11LibPath(libPath),pin);

            long sourceKey = Helper.findKey(session, keyName) ;

            if(unwrappingKeyName != null) {

                unwrapObjClass = Helper.parseKeyName(unwrappingKeyName);
                if(unwrapObjClass != 0) {
                    unwrappingKeyName = unwrappingKeyName.substring(2);
                    unwrappingKey = Helper.findKey(session, unwrappingKeyName, unwrapObjClass);
                }
                else {
                    unwrapObjClass = CKO_SECRET_KEY;
                    unwrappingKey = Helper.findKey(session, unwrappingKeyName);
                }
            }

    	    CK_MECHANISM mechanism = new CK_MECHANISM (CKM_AES_CBC_PAD, iv);

	        if (unwrappingKey == 0)
            {
                System.out.println ("Unwrapping key not used..." );
            }
            else {
                System.out.println ("Successfully found unwrapping key. Handle: " + unwrappingKey);
            }

		/* If any key are found, they are returned in the keyID array.
			   Check the keyID array length to see if the find is successful */
            if (sourceKey != 0)
            {
                System.out.println ("Found source key. Handle: " + sourceKey + " ; need to use differnt key name for importing");
            }
            else
            {
                System.out.println ("Source Key "+ keyName +" NOT exist on KeyManager. Importing...");
                wrappedKey = Helper.readKey(inputFileName);

                CK_ATTRIBUTE[] symAttrs = new CK_ATTRIBUTE[]
                {
                        new CK_ATTRIBUTE (CKA_LABEL, keyName),
                        new CK_ATTRIBUTE (CKA_CLASS, CKO_SECRET_KEY),
                        new CK_ATTRIBUTE (CKA_KEY_TYPE, CKK_AES),
                        new CK_ATTRIBUTE (CKA_VALUE_LEN, 32),
                        new CK_ATTRIBUTE (CKA_TOKEN, true),
                        new CK_ATTRIBUTE (CKA_ENCRYPT, true),
                        new CK_ATTRIBUTE (CKA_DECRYPT, true),
                        new CK_ATTRIBUTE (CKA_SIGN, false),
                        new CK_ATTRIBUTE (CKA_VERIFY, false),
                        new CK_ATTRIBUTE (CKA_WRAP, true),
                        new CK_ATTRIBUTE (CKA_UNWRAP, true),
                        new CK_ATTRIBUTE (CKA_EXTRACTABLE, false),
                        new CK_ATTRIBUTE (CKA_ALWAYS_SENSITIVE, false),
                        new CK_ATTRIBUTE (CKA_NEVER_EXTRACTABLE, true),
                        new CK_ATTRIBUTE (CKA_SENSITIVE, true),
                        new CK_ATTRIBUTE (Helper.CKA_KEY_CACHE_ON_HOST, true),
                        new CK_ATTRIBUTE (Helper.CKA_KEY_CACHED_TIME, 44640),
                        new CK_ATTRIBUTE (CKA_MODIFIABLE, true)
                };

                CK_ATTRIBUTE[] asymAttrs = new CK_ATTRIBUTE[]
                {
                        new CK_ATTRIBUTE (CKA_LABEL, keyName),
                        new CK_ATTRIBUTE (CKA_CLASS, objClass),
                        new CK_ATTRIBUTE (CKA_KEY_TYPE, CKK_RSA),
                        new CK_ATTRIBUTE (CKA_ENCRYPT, true),
                        new CK_ATTRIBUTE (CKA_DECRYPT, true),
                        new CK_ATTRIBUTE (CKA_SIGN, true),
                        new CK_ATTRIBUTE (CKA_VERIFY, true),
                        new CK_ATTRIBUTE (CKA_WRAP, true),
                        new CK_ATTRIBUTE (CKA_TOKEN, true)
                };

                if( unwrappingKey != 0 && Helper.isKeySymmetric(unwrappingKey) ) {
                    mechanism.mechanism = Helper.CKA_THALES_DEFINED | PKCS11Constants.CKM_RSA_PKCS;
                }

                if( formatName != null && formatName.equals("pem") )
                    mechanism.mechanism |= Helper.CKM_THALES_PEM_FORMAT;

                /* Importing asymmetric key */
                if(objClass != PKCS11Constants.CKO_SECRET_KEY) {

                    mechanism.mechanism |= Helper.CKA_THALES_DEFINED;
                    attrs = asymAttrs;
                }
                else {
                    /* importing symmetric key */
                    attrs = symAttrs;
                }
                
                long importedKey = session.p11.C_UnwrapKey(session.sessionHandle, mechanism, unwrappingKey, wrappedKey, attrs);
                System.out.println ("Successfully unwrapped key. Imported key "+keyName+"; handle: "  + importedKey);
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
            System.out.println ("End UnwrapImportKey." );
        }
    }
}
