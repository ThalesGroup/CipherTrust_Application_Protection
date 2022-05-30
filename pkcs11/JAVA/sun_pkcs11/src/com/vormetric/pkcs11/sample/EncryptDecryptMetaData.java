package com.vormetric.pkcs11.sample;

import static sun.security.pkcs11.wrapper.PKCS11Constants.CKM_AES_CBC_PAD;
/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
/*
***************************************************************************
* File: EncryptDecryptMetaData.java
***************************************************************************
***************************************************************************
* This file demonstrates the following
* 1. Initialization
* 2. Creating a connection and logging in.
* 3. Creating a symmetric key on the KeyManager.
* 4. Using the symmetric key to encrypt plaintext;
*     passing in meta data during first Encrypt call.
* 5. Using the symmetric key to decrypt ciphertext;
*             passing in meta data during first Decrypt call.
* 6. Delete key.
* 7. Clean up.
*/
import sun.security.pkcs11.wrapper.CK_MECHANISM;
import sun.security.pkcs11.wrapper.PKCS11Exception;

public class EncryptDecryptMetaData {

    public static final String defKeyName = "pkcs11_java_test_key";
    public static final byte[] iv = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x10, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F};
    public static final String plainText = "Plain text message to be encrypted.";


    public static void usage()
    {
        System.out.println("usage: java [-cp CLASSPATH] com.vormetric.pkcs11.sample.EncryptDecryptMetaData -p pin [-k keyName] [-m module] [-g genaction] [-h headermode] [-ls lifeSpan]");
        System.out.println("-p: Username:Password of Keymanager");
        System.out.println("-k: Keyname on Keymanager");
        System.out.println("-m: Path of directory where dll is deployed/installed");
        System.out.println("-g: 0...generate versioned key, 1...rotate versioned key, 2...migrate non-versioned key to versioned key, 3...generate non-versioned key");
        System.out.println("-h: v1.5, v1.5base64, v2.1, or v2.7");
	System.out.println("-ls: Life Span, Life span of key in days");
        System.exit (1);
    }

    public static void main ( String[] args)
    {
        String pin = null;
        String libPath = null;
        String keyName = null;
        String headermode = ""; /* none */
        int genAction = 3; /* generate non-versioned key */
        int lifespan = 0;
        Vpkcs11Session session = null;

        if (args.length < 2) usage();

        for (int i=0; i<args.length; i+=2)
        {
            if (args[i].equals("-p")) pin = args[i+1];
            else if (args[i].equals("-m")) libPath = args[i+1];
            else if (args[i].equals("-k")) keyName = args[i+1];
            else if (args[i].equals("-g")) genAction = Integer.parseInt(args[i + 1]);
            else if (args[i].equals("-ls")) lifespan = Integer.parseInt(args[i+1]);
            else if (args[i].equals("-h")) headermode = args[i+1];
            else usage();
        }
        if (pin==null)     usage();
        if (keyName==null) usage();

        long headerenc = 0;
        long headerdec = 0;

        if (headermode.equals("v1.5")) {
          headerenc = Helper.CKM_THALES_V15HDR | Helper.CKM_VENDOR_DEFINED;
          headerdec = Helper.CKM_THALES_ALLHDR| Helper.CKM_VENDOR_DEFINED;
        } else if (headermode.equals("v1.5base64")) {
          headerenc = Helper.CKM_THALES_V15HDR | Helper.CKM_THALES_BASE64 | Helper.CKM_VENDOR_DEFINED;
          headerdec = Helper.CKM_THALES_ALLHDR | Helper.CKM_THALES_BASE64 | Helper.CKM_VENDOR_DEFINED;
        } else if (headermode.equals("v2.1")) {
          headerenc = Helper.CKM_THALES_V21HDR | Helper.CKM_VENDOR_DEFINED;
          headerdec = Helper.CKM_THALES_ALLHDR | Helper.CKM_VENDOR_DEFINED;
        } else if (headermode.equals("v2.7")) {
          headerenc = Helper.CKM_THALES_V27HDR | Helper.CKM_VENDOR_DEFINED;
          headerdec = Helper.CKM_THALES_ALLHDR| Helper.CKM_VENDOR_DEFINED;
        }

		try
	    {
	        CK_MECHANISM encMech = new CK_MECHANISM (headerenc | CKM_AES_CBC_PAD, iv);
	        CK_MECHANISM decMech = new CK_MECHANISM (headerdec | CKM_AES_CBC_PAD, iv);

			if(keyName == null)
				keyName = defKeyName;

            System.out.println ("Start EncryptDecryptMetaData ..." );
            session = Helper.startUp(Helper.getPKCS11LibPath(libPath), pin);

            long keyID = Helper.findKey(session, keyName) ;

            if (keyID == 0)
            {
                System.out.println ("the key is not found, creating it..." );
                keyID = Helper.createKey(session, keyName, genAction, lifespan);
                System.out.println ("Key successfully Created. Key Handle: " + keyID);
            }

			/* encrypt, decrypt with key */
			byte[] outText = { };
			byte[] decryptedText = { };
			int encryptedDataLen = 0;
			int decryptedDataLen = 0;

			/* This is for user passed in logging data; format can be any string. */
			String metadata = "META: This is test meta data: Encryption: ";

			session.p11.C_EncryptInit (session.sessionHandle, encMech, keyID);
			System.out.println ("C_EncryptInit succeed");

			System.out.println ("plaintext = " + plainText);
			System.out.println ("plaintext length = " + plainText.length() + " plaintext byte length: " + plainText.getBytes().length );

			outText = metadata.getBytes();
			encryptedDataLen = session.p11.C_Encrypt (session.sessionHandle, plainText.getBytes(), 0, plainText.length(), outText, 0, 0);
			System.out.println ("C_Encrypt success. encrypted data len = " + encryptedDataLen);

			outText = new byte[encryptedDataLen];
			encryptedDataLen = session.p11.C_Encrypt (session.sessionHandle, plainText.getBytes(), 0, plainText.length(), outText, 0, outText.length);
			System.out.println ("C_Encrypt 2nd call success. encrypted data len = " + encryptedDataLen);

			session.p11.C_DecryptInit (session.sessionHandle, decMech, keyID);
			System.out.println ("C_DecryptInit success");

			/* This is for user passed in logging data; format can be any string, recommend using JSON */
			metadata = "META: This is test meta data: Decryption: ";
			decryptedText = metadata.getBytes();
			decryptedDataLen = session.p11.C_Decrypt (session.sessionHandle, outText, 0, encryptedDataLen, decryptedText, 0, 0);

			decryptedText = new byte [decryptedDataLen];
			decryptedDataLen = session.p11.C_Decrypt (session.sessionHandle, outText, 0, encryptedDataLen, decryptedText, 0, decryptedText.length);
			System.out.println ("C_Decrypt 2nd call success. Decrypted data length = " + decryptedDataLen);

			String decryptedTextStr = new String (decryptedText, 0, decryptedDataLen);
			System.out.println ("C_Decrypt succeed.");
			System.out.println ("Decrypted Text length = " + decryptedText.length + " decrypted string length = " + decryptedTextStr.length());
			System.out.println ("Plain Text = " + plainText + " Decrypted Text = " + decryptedTextStr);

            if(plainText.equals(decryptedTextStr)) {
                System.out.println("=== plainText and decryptedTextStr are equal ===");
            }
            else
            {
                System.out.println("=== plainText and decryptedTextStr are NOT equal ===");
            }

			/* Delete the key */
            Helper.setKeyState (session, keyID, Helper.KeyState.Deactivated);
			session.p11.C_DestroyObject (session.sessionHandle, keyID);
			System.out.println ("Successfully deleted key");
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
            System.out.println ("End EncryptDecryptMessage." );
        }
    }
}
