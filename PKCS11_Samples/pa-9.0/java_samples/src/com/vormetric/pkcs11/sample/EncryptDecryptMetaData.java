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
 * File: EncryptDecryptMetaData.java
 ***************************************************************************
 ***************************************************************************
 * This file demonstrates the following
 * 1. Initialization
 * 2. Creating a connection and logging in.
 * 3. Creating a symmetric key on the Data Security Manager.
 * 4. Using the symmetric key to encrypt plaintext;
 *    	passing in meta data during first Encrypt call.
 * 5. Using the symmetric key to decrypt ciphertext;
 * 		passing in meta data during first Decrypt call.
 * 6, Delete key.
 * 7. Clean up.
 */

import java.io.*;
import java.security.*;
import sun.security.pkcs11.wrapper.*;
import static sun.security.pkcs11.wrapper.PKCS11Constants.*;
import sun.security.pkcs11.Secmod.*;

public class EncryptDecryptMetaData {

	public static final String defKeyName = "vpkcs11_java_test_key";
	public static final byte[] iv = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x10, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F};
	public static final CK_MECHANISM encMech = new CK_MECHANISM (CKM_AES_CBC_PAD, iv);
    public static final String plainText = "Plain text message to be encrypted.";


    public static void usage()
    {
        System.out.println ("usage: java com.vormetric.pkcs11.sample.EncryptDecryptMetaData -p pin [-k keyName] [-m module]");
        System.exit (1);
    }

    public static void main ( String[] args) 
    {
        String pin = null;
        String libPath = null;
		String keyName = null;
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

            System.out.println ("Start EncryptDecryptMetaData ..." );
            Vpkcs11Session session = Helper.startUp(Helper.getPKCS11LibPath(libPath), pin, initArgs);

            long keyID = Helper.findKey(session, keyName) ;

            if (keyID == 0)
            {
                System.out.println ("the key is not found, creating it..." );
                keyID = Helper.createKey(session, keyName);
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

			session.p11.C_DecryptInit (session.sessionHandle, encMech, keyID);
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
			session.p11.C_DestroyObject (session.sessionHandle, keyID);
			System.out.println ("Successfully deleted key");

            Helper.closeDown(session);
            System.out.println ("End EncryptDecryptMessage." );
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
