package com.vormetric.pkcs11.sample;


import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKA_CLASS;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKA_DECRYPT;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKA_ENCRYPT;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKA_LABEL;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKA_MODULUS_BITS;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKA_PRIVATE;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKA_PUBLIC_EXPONENT;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKA_SENSITIVE;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKA_SIGN;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKA_TOKEN;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKA_UNWRAP;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKA_VERIFY;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKA_WRAP;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKM_RSA_PKCS;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKM_RSA_PKCS_KEY_PAIR_GEN;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKO_PRIVATE_KEY;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKO_PUBLIC_KEY;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKA_MODIFIABLE;

import com.vormetric.pkcs11.wrapper.CK_ATTRIBUTE;
import com.vormetric.pkcs11.wrapper.CK_MECHANISM;
import com.vormetric.pkcs11.wrapper.PKCS11Exception;
/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/

/*
 ***************************************************************************
 * File: CreateKeypairSignMessage.java
 ***************************************************************************
 ***************************************************************************
 * This file demonstrates the following
 * 1. Initialization
 * 2. Create a connection and logging in.
 * 3. Create an asymmetric key pair on the KeyManager
 * 4. Sign a piece of message with the created private key
 * 5. Verify the message was signed with the created private key
 *    by using public key Id and signed signature.
 * 6. Delete the keypair.
 * 7. Clean up.
 */


public class CreateKeypairSignMessage {
	public static final String defPublicKeyname = "java_test_keypair";
	public static final String privateKeyname = "java_test_keypair_private";
    public static final String signText = "The message to be signed.";

    public static void usage()
    {
        System.out.println ("usage: java [-cp CLASSPATH] com.vormetric.pkcs11.sample.CreateKeypairSignMessage -p pin [-m module] [-kp keypair_label]");
        System.out.println("-p: Username:Password of Keymanager");
        System.out.println("-m: Path of directory where dll is deployed/installed");
        System.out.println("-kp: Keyname on Keymanager");
        System.exit (1);
    }

    public static void main ( String[] args)
    {
        String pin = null;
        String libPath = null;
		String publicKeyname = null;
		Vpkcs11Session session = null;

		if (args.length < 2) usage();
		for (int i=0; i<args.length; i+=2)
		{
			if (args[i].equals("-p")) pin = args[i+1];
			else if (args[i].equals("-m")) libPath = args[i+1];
			else if (args[i].equals("-kp")) publicKeyname = args[i+1];
			else usage();
		}

		long publickeyID, privatekeyID;
		long[] keyIDArr;

		try
	    {
	    	if(publicKeyname == null)
				publicKeyname = defPublicKeyname;

            System.out.println ("Start CreateKeypairSignMessage ..." );
            session = Helper.startUp(Helper.getPKCS11LibPath(libPath), pin);

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
					new CK_ATTRIBUTE (CKA_MODULUS_BITS, modulusBits),
					new CK_ATTRIBUTE (CKA_MODIFIABLE, true)
			};

			CK_ATTRIBUTE[] privateKeyAttr = new CK_ATTRIBUTE[]
			{
					new CK_ATTRIBUTE (CKA_CLASS, CKO_PRIVATE_KEY),
					new CK_ATTRIBUTE (CKA_LABEL, privateKeyname),
					new CK_ATTRIBUTE (CKA_TOKEN, true),
					new CK_ATTRIBUTE (CKA_PRIVATE, true),
					new CK_ATTRIBUTE (CKA_SENSITIVE, true),
					new CK_ATTRIBUTE (CKA_DECRYPT, true),
					new CK_ATTRIBUTE (CKA_SIGN, true),
					new CK_ATTRIBUTE (CKA_UNWRAP, true),
					new CK_ATTRIBUTE (CKA_MODIFIABLE, true)
			};

            publickeyID = Helper.findKey(session, publicKeyname, CKO_PUBLIC_KEY);
            if (publickeyID != 0)
            {
                session.p11.C_DestroyObject(session.sessionHandle, publickeyID);
                System.out.println ("Removed existing keypair");
            }

            keyIDArr = session.p11.C_GenerateKeyPair (session.sessionHandle, mechanism, publicKeyAttr, privateKeyAttr);
			System.out.println ("Keypair successfully Generated. Public Key Handle: " + keyIDArr[0] + " Private Key Handle: " + keyIDArr[1]);

			/* The public key handle  is always the first one in the array. Private key the second */
			publickeyID = keyIDArr[0];
			privatekeyID = keyIDArr[1];

			/* Create the sign mechanism and sign with the private key */
			CK_MECHANISM signMech = new CK_MECHANISM (CKM_RSA_PKCS);
			//long sigLen = modulusBits/8;

			session.p11.C_SignInit (session.sessionHandle, signMech, privatekeyID);
			byte[] signature = session.p11.C_Sign (session.sessionHandle, signText.getBytes());
			System.out.println ("Successfully signed. Text to sign = " + signText + " signature = " + signature.toString());

			session.p11.C_VerifyInit (session.sessionHandle, signMech, publickeyID);
			session.p11.C_Verify(session.sessionHandle, signText.getBytes(), signature);
			System.out.println ("Successfully verified.");

			/* delete the keypair */
			session.p11.C_DestroyObject (session.sessionHandle, publickeyID);
			System.out.println ("Successfully deleted keypair.");

            long keyID = Helper.findKey(session, publicKeyname);
            if (keyID == 0)
            {
                System.out.println ("The key : " + publicKeyname + " has been deleted." );
            }
            else
            {
                System.out.println ("The key : " + publicKeyname + " still exists in KeyManager.");
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
			System.out.println ("End CreateKeypairSignMessage." );
		}
    }
}
