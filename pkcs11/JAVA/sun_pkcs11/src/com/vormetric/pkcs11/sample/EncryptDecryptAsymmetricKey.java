package com.vormetric.pkcs11.sample;

import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_CLASS;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_DECRYPT;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_ENCRYPT;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_LABEL;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_MODULUS_BITS;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_PRIVATE;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_PUBLIC_EXPONENT;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_SENSITIVE;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_SIGN;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_TOKEN;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_UNWRAP;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_VERIFY;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_WRAP;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKM_RSA_PKCS;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKM_RSA_PKCS_KEY_PAIR_GEN;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKO_PRIVATE_KEY;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKO_PUBLIC_KEY;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_EXTRACTABLE;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_MODIFIABLE;

/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/

/* IMPORTANT 
 *
 * With Java Version JDK 8u241 and onwards, there are changes done (SunPKCS11 
 * Provider Upgraded with Support for PKCS#11 v2.40 
 * http://bugs.java.com/bugdatabase/view_bug.do?bug_id=JDK-8080462) in the 
 * prototype of C_Encrypt and C_Decrypt API's. The number of parameters in 
 * these API's has been increased to 9 instead of 7 with earlier JDK versions.
 * So if Java Version JDK 8u241 and higher installed on machine, then API's 
 * parameters will be increased to 9 and 0 will be passed. 
 * 
 * For example:
 * C_Encrypt Call with 7 Arguments:
 * session.p11.C_Encrypt(session.sessionHandle, plainBytes, 0, plainBytesLen, outText, 0, 0);
 * C_Encrypt Call with 9 Arguments:
 * session.p11.C_Encrypt(session.sessionHandle, <Newly added argument> 0, plainBytes, 0, plainBytesLen, <Newly added argument> 0, outText, 0, 0);
 *
 * C_Decrypt Call with 7 Arguments:
 * session.p11.C_Decrypt(session.sessionHandle, encryptedBytes, 0, encryptedDataLen, outText, 0, 0);
 * C_Decrypt Call with 9 Arguments:
 * session.p11.C_Decrypt(session.sessionHandle, <Newly added argument> 0, encryptedBytes, 0, encryptedDataLen, <Newly added argument> 0, outText, 0, 0);
 *
 * Note:
 * These newly added 2 arguments will not impact any existing functionality in C_Encrypt and C_Decrypt API's.
 *
 */

/*
 ***************************************************************************
 * File: public class EncryptDecryptAsymmetricKey.java
 ***************************************************************************
 ***************************************************************************
 * This file demonstrates the following
 * 1. Initialization
 * 2. Create a connection and logging in.
 * 3. Create an asymmetric key pair on the KeyManager
 * 4. Encrypt and descrypt a message
 * 5. Clean up.
 */

import sun.security.pkcs11.wrapper.CK_ATTRIBUTE;
import sun.security.pkcs11.wrapper.CK_MECHANISM;
import sun.security.pkcs11.wrapper.PKCS11Exception;

public class EncryptDecryptAsymmetricKey {
    public static final String publicKeyname = "pkcs11_java_test_key";
    public static final String privateKeyname = "java_test_keypair_private";
    public static final String signText = "The message to be signed.";

    public static void usage()
    {
        System.out.println ("usage: java [-cp CLASSPATH] com.vormetric.pkcs11.sample.EncryptDecryptAsymmetricKey -p pin [-m module] [-kp keypair_label]");
        System.out.println("-p: Username:Password of Keymanager");
        System.out.println("-m: Path of directory where dll is deployed/installed");
	System.out.println("-kp: Keyname on Keymanager");
        System.exit (1);
    }

    public static void main ( String[] args) throws Exception
    {
        String pin = null;
        String libPath = null;
        Vpkcs11Session session = null;
        String keyName = null;
        long publicKeyID, privateKeyID;
        long modulusBits = 2048;

        for (int i=0; i<args.length; i+=2)
        {
            if (args[i].equals("-p")) pin = args[i+1];
            else if (args[i].equals("-kp")) {
                keyName = args[i + 1];
            }
            else if (args[i].equals("-m")) libPath = args[i+1];
            else usage();
        }

        try
        {
            System.out.println ("Start EncryptDecryptAsymmetricKey ..." );
            session = Helper.startUp(Helper.getPKCS11LibPath(libPath), pin);

            if(keyName == null)
                keyName = publicKeyname;

            publicKeyID = Helper.findKey(session, keyName, CKO_PUBLIC_KEY);
            if (publicKeyID != 0)
            {
			    /* session.p11.C_DestroyObject (session.sessionHandle, publicKeyID); */
			    System.out.println ("Found existing public key: " + keyName);
                privateKeyID = Helper.findKey(session, keyName, CKO_PRIVATE_KEY);
                if(privateKeyID != 0)
                    System.out.println ("Using existing asymmetric keypair: " + keyName);
            }
            else {
                /* Create the keypair */
                CK_MECHANISM mechanism = new CK_MECHANISM(CKM_RSA_PKCS_KEY_PAIR_GEN);
                byte[] publicExponent = {0x01, 0x00, 0x01, 0x00};
                long[] keyIDArr;

                CK_ATTRIBUTE[] publicKeyAttr = new CK_ATTRIBUTE[]
                        {
                                new CK_ATTRIBUTE(CKA_LABEL, keyName),
                                new CK_ATTRIBUTE(CKA_CLASS, CKO_PUBLIC_KEY),
                                new CK_ATTRIBUTE(CKA_ENCRYPT, true),
                                new CK_ATTRIBUTE(CKA_SIGN, true),
                                new CK_ATTRIBUTE(CKA_VERIFY, true),
                                new CK_ATTRIBUTE(CKA_WRAP, true),
                                new CK_ATTRIBUTE(CKA_TOKEN, true),
                                new CK_ATTRIBUTE(CKA_PUBLIC_EXPONENT, publicExponent),
                                new CK_ATTRIBUTE(CKA_MODULUS_BITS, modulusBits)
                        };

                CK_ATTRIBUTE[] privateKeyAttr = new CK_ATTRIBUTE[]
                        {
                                new CK_ATTRIBUTE(CKA_LABEL, keyName),
                                new CK_ATTRIBUTE(CKA_CLASS, CKO_PRIVATE_KEY),
                                new CK_ATTRIBUTE(CKA_TOKEN, true),
                                new CK_ATTRIBUTE(CKA_PRIVATE, true),
                                new CK_ATTRIBUTE(CKA_SENSITIVE, true),
                                new CK_ATTRIBUTE(CKA_DECRYPT, true),
                                new CK_ATTRIBUTE(CKA_SIGN, true),
                                new CK_ATTRIBUTE(CKA_EXTRACTABLE, true),
                                new CK_ATTRIBUTE(CKA_MODIFIABLE, true),
                                new CK_ATTRIBUTE(CKA_UNWRAP, true)
                        };

                keyIDArr = session.p11.C_GenerateKeyPair(session.sessionHandle, mechanism, publicKeyAttr, privateKeyAttr);
                System.out.println("Keypair successfully Generated. Public Key Handle: " + keyIDArr[0] + " Private Key Handle: " + keyIDArr[1]);

                /* The public key handle  is always the first one in the array. Private key the second */
                publicKeyID = keyIDArr[0];
                privateKeyID = keyIDArr[1];
            }

			/* Create the sign mechanism and sign with the private key */
            CK_MECHANISM  encryptMechanism = new CK_MECHANISM (CKM_RSA_PKCS);
            //long sigLen = modulusBits/8;

            session.p11.C_EncryptInit(session.sessionHandle, encryptMechanism, publicKeyID);

            String plainText = "Text to be encrypted";
            //	String plainText = "Text to be encrypted1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+-=[]{}|;:<>?,./charunamineni123456-Text to be encrypted1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+-=[]{}|;:<>?,./charunam--Text to be encrypted1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+-=[]{}|;:<>?,./charunamineni123456-Text to be encrypted1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+-=[]{}|;:<>?,./charunamatinamin";
            //	String plainText = "Text to be encrypted1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+-=[]{}|;:<>?,./charunamineni123456";
            System.out.println("=== plainText len = " + plainText.length());
            System.out.println("=== plainText bytes length = " +  plainText.getBytes().length);
            byte[] outText = new byte[120];
            byte[] decryptedText = new byte[plainText.length() + 16];
            int encryptedDataLen = session.p11.C_Encrypt (session.sessionHandle, plainText.getBytes(), 0, plainText.length(), outText, 0, 0);
            System.out.println("=== encrypted Data len first call = " + encryptedDataLen);
            outText = new byte[encryptedDataLen];

            encryptedDataLen = session.p11.C_Encrypt (session.sessionHandle, plainText.getBytes(), 0, plainText.length(), outText, 0, outText.length);
            System.out.println("=== encrypted Data len second call = " + encryptedDataLen);
            System.out.println("=== encrypted text = " + new String(outText, 0, encryptedDataLen));

            session.p11.C_DecryptInit(session.sessionHandle, encryptMechanism, privateKeyID);

            int	 decryptedDataLen = session.p11.C_Decrypt (session.sessionHandle, outText, 0, encryptedDataLen, decryptedText, 0, 0);
            System.out.println ("Decrypted data length first call = " + decryptedDataLen);
            decryptedText = new byte [decryptedDataLen];
            decryptedDataLen = session.p11.C_Decrypt (session.sessionHandle, outText, 0, encryptedDataLen, decryptedText, 0, decryptedText.length);
            System.out.println ("Decrypted data length second call = " + decryptedDataLen);

            String decryptedTextStr = new String (decryptedText, 0, decryptedDataLen);
            System.out.println("=== decrypted text = " + decryptedTextStr);

            if(plainText.equals(decryptedTextStr)) {
                System.out.println("Success: Asymmetric key decrypted text matches plain text!!");
            }
            else {
                System.out.println("Error: Asymmetric keypair decryption doesn't match input text!");
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
            System.out.println ("End EncryptDecryptAsymmetricKey." );
        }
    }

}
