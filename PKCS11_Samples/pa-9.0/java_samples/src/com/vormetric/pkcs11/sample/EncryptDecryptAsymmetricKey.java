package com.vormetric.pkcs11.sample;
/*************************************************************************
 **                                                                                                                                           **
 ** Copyright(c) 2014                         Confidential Material     **
 **                                                                                                                                            **
 ** This file is the property of Vormetric Inc.                         **
 ** The contents are proprietary and confidential.                      **
 ** Unauthorized use, duplication, or dissemination of this document,   **
 ** in whole or in part, is forbidden without the express consent of    **
 ** Vormetric, Inc..                                                    **
 **                                                                     **
 **************************************************************************/
/*
 ***************************************************************************
 * File: public class EncryptDecryptAsymmetricKey.java
 ***************************************************************************
 ***************************************************************************
 * This file demonstrates the following
 * 1. Initialization
 * 2. Create a connection and logging in.
 * 3. Create an asymmetric key pair on the Data Security Manager
 * 4. Encrypt and descrypt a message
 * 5. Clean up.
 */

import java.io.*;
import java.security.*;
import sun.security.pkcs11.wrapper.*;
import static sun.security.pkcs11.wrapper.PKCS11Constants.*;
import sun.security.pkcs11.Secmod.*;

public class EncryptDecryptAsymmetricKey {
    public static final String publicKeyname = "vpkcs11_java_test_key";
    public static final String privateKeyname = "java_test_keypair_private";
    public static final String signText = "The message to be signed.";

    public static void usage()
    {
        System.out.println ("usage: java com.vormetric.pkcs11.sample.EncryptDecryptAsymmetricKey -p pin [-m module]");
        System.exit (1);
    }

    public static void main ( String[] args)
    {
        String pin = null;
        String libPath = null;
        String initArgs = "";

        int i;
        for (i=0; i<args.length; i+=2)
        {
            if (args[i].equals("-p")) pin = args[i+1];
            else if (args[i].equals("-m")) libPath = args[i+1];
            else if (args[i].equals("-a")) initArgs = args[i+1];
            else usage();
        }

        long publicKeyID, privateKeyID;
        long[] keyIDArr;

        try
        {
            System.out.println ("Start EncryptDecryptAsymmetricKey ..." );
            Vpkcs11Session session = Helper.startUp(Helper.getPKCS11LibPath(libPath), pin, initArgs);

            publicKeyID = Helper.findKey(session, publicKeyname, CKO_PUBLIC_KEY);
            if (publicKeyID != 0)
            {
			    session.p11.C_DestroyObject (session.sessionHandle, publicKeyID);
			    System.out.println ("Removed existing keypair");
            }

			/* Create the keypair */
            CK_MECHANISM mechanism = new CK_MECHANISM (CKM_RSA_PKCS_KEY_PAIR_GEN);
            byte[] publicExponent = { 0x01, 0x00, 0x01, 0x00 };
            int modulusBits = 2048;

            CK_ATTRIBUTE[] publicKeyAttr = new CK_ATTRIBUTE[]
                {
                    new CK_ATTRIBUTE (CKA_LABEL, publicKeyname),
                    new CK_ATTRIBUTE (CKA_CLASS, CKO_PUBLIC_KEY),
                    new CK_ATTRIBUTE (CKA_ENCRYPT, true),
                    new CK_ATTRIBUTE (CKA_SIGN, true),
                    new CK_ATTRIBUTE (CKA_VERIFY, true),
                    new CK_ATTRIBUTE (CKA_WRAP, true),
                    new CK_ATTRIBUTE (CKA_TOKEN, true),
                    new CK_ATTRIBUTE (CKA_PUBLIC_EXPONENT, publicExponent),
					new CK_ATTRIBUTE (CKA_MODIFIABLE, true),
                    new CK_ATTRIBUTE (CKA_MODULUS_BITS, modulusBits)
                };

            CK_ATTRIBUTE[] privateKeyAttr = new CK_ATTRIBUTE[]
                {
                    new CK_ATTRIBUTE (CKA_LABEL, privateKeyname),
                    new CK_ATTRIBUTE (CKA_CLASS, CKO_PRIVATE_KEY),
                    new CK_ATTRIBUTE (CKA_TOKEN, true),
                    new CK_ATTRIBUTE (CKA_PRIVATE, true),
                    new CK_ATTRIBUTE (CKA_SENSITIVE, true),
                    new CK_ATTRIBUTE (CKA_DECRYPT, true),
                    new CK_ATTRIBUTE (CKA_SIGN, true),
					new CK_ATTRIBUTE (CKA_MODIFIABLE, true),
                    new CK_ATTRIBUTE (CKA_UNWRAP, true)
                };

            keyIDArr = session.p11.C_GenerateKeyPair (session.sessionHandle, mechanism, publicKeyAttr, privateKeyAttr);
            System.out.println ("Keypair successfully Generated. Public Key Handle: " + keyIDArr[0] + " Private Key Handle: " + keyIDArr[1]);
		
			/* The public key handle  is always the first one in the array. Private key the second */
            publicKeyID = keyIDArr[0];
            privateKeyID = keyIDArr[1];

			/* Create the sign mechanism and sign with the private key */
            CK_MECHANISM  encryptMechanism = new CK_MECHANISM (CKM_RSA_PKCS);
            long sigLen = modulusBits/8;

            session.p11.C_EncryptInit(session.sessionHandle, encryptMechanism, publicKeyID);

            String plainText = "Text to be encrypted";
            //	String plainText = "Text to be encrypted1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+-=[]{}|;:<>?,./charunamineni123456-Text to be encrypted1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+-=[]{}|;:<>?,./charunam--Text to be encrypted1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+-=[]{}|;:<>?,./charunamineni123456-Text to be encrypted1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+-=[]{}|;:<>?,./charunamatinamin";
            //	String plainText = "Text to be encrypted1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+-=[]{}|;:<>?,./charunamineni123456";
            System.out.println("=== plainText len = " + plainText.length());
            System.out.println("=== plainText bytes length = " +  plainText.getBytes().length);
            byte[] outText = new byte[120];
            byte[] decryptedText = new byte[plainText.length() + 16];
            int encryptedDataLen = session.p11.C_Encrypt (session.sessionHandle, plainText.getBytes(), 0, plainText.length(), outText, 0, 0);
            System.out.println("=== encrypted Data len first attempt = " + encryptedDataLen);
            outText = new byte[encryptedDataLen];

            encryptedDataLen = session.p11.C_Encrypt (session.sessionHandle, plainText.getBytes(), 0, plainText.length(), outText, 0, outText.length);
            System.out.println("=== encrypted Data len second attempt = " + encryptedDataLen);
            System.out.println("=== encrypted text = " + new String(outText, 0, encryptedDataLen));
           
            session.p11.C_DecryptInit(session.sessionHandle, encryptMechanism, privateKeyID);

            int	 decryptedDataLen = session.p11.C_Decrypt (session.sessionHandle, outText, 0, encryptedDataLen, decryptedText, 0, 0);
            System.out.println ("Decrypted data length first attempt = " + decryptedDataLen);
            decryptedText = new byte [decryptedDataLen];
            decryptedDataLen = session.p11.C_Decrypt (session.sessionHandle, outText, 0, encryptedDataLen, decryptedText, 0, decryptedText.length);
            System.out.println ("Decrypted data length second attempt = " + decryptedDataLen);

            String decryptedTextStr = new String (decryptedText, 0, decryptedDataLen);
            System.out.println("=== decrypted text = " + decryptedTextStr);

             /* delete the keypair */
            session.p11.C_DestroyObject (session.sessionHandle, publicKeyID);
            System.out.println ("Removed asymmetric key");
            Helper.closeDown(session);
            System.out.println ("End EncryptDecryptAsymmetricKey." );
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
