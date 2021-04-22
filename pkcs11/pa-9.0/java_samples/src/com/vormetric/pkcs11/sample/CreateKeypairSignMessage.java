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
 * File: CreateKeypairSignMessage.java
 ***************************************************************************
 ***************************************************************************
 * This file demonstrates the following
 * 1. Initialization
 * 2. Create a connection and logging in.
 * 3. Create an asymmetric key pair on the Data Security Manager
 * 4. Sign a piece of message with the created private key
 * 5. Verify the message was signed with the created private key
 *    by using public key Id and signed signature. 
 * 6. Delete the keypair.
 * 7. Clean up.
 */

import java.io.*;
import java.security.*;
import sun.security.pkcs11.wrapper.*;
import static sun.security.pkcs11.wrapper.PKCS11Constants.*;
import sun.security.pkcs11.Secmod.*;

public class CreateKeypairSignMessage {
	public static final String defPublicKeyname = "java_test_keypair";
	public static final String privateKeyname = "java_test_keypair_private";
    public static final String signText = "The message to be signed.";

    public static void usage()
    {
        System.out.println ("usage: java com.vormetric.pkcs11.sample.CreateKeypairSignMessage -p pin [-m module]");
        System.exit (1);
    }

    public static void main ( String[] args) 
    {
        String pin = null;
        String libPath = null;
        String publicKeyname = null;
		String initArgs = "";

		int i;
		for (i=0; i<args.length; i+=2)
		{
			if (args[i].equals("-p")) pin = args[i+1];
			else if (args[i].equals("-m")) libPath = args[i+1];
			else if (args[i].equals("-a")) initArgs = args[i+1];
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
            Vpkcs11Session session = Helper.startUp(Helper.getPKCS11LibPath(libPath), pin, initArgs);

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
					new CK_ATTRIBUTE(CKA_MODIFIABLE, true),
					new CK_ATTRIBUTE (CKA_MODULUS_BITS, modulusBits)
			};

			CK_ATTRIBUTE[] privateKeyAttr = new CK_ATTRIBUTE[]
			{
					new CK_ATTRIBUTE (CKA_LABEL, publicKeyname),
					new CK_ATTRIBUTE (CKA_CLASS, CKO_PRIVATE_KEY),
					new CK_ATTRIBUTE (CKA_TOKEN, true),
					new CK_ATTRIBUTE (CKA_PRIVATE, true),
					new CK_ATTRIBUTE (CKA_SENSITIVE, true),
					new CK_ATTRIBUTE (CKA_DECRYPT, true),
					new CK_ATTRIBUTE (CKA_SIGN, true),
					new CK_ATTRIBUTE(CKA_MODIFIABLE, true),
					new CK_ATTRIBUTE (CKA_UNWRAP, true)
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
			long sigLen = modulusBits/8;

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
                System.out.println ("The key : " + publicKeyname + " still exists in DSM.");
            }
            Helper.closeDown(session);
            System.out.println ("End CreateKeypairSignMessage." );
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
