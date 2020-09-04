package com.vormetric.pkcs11.sample;

/**
 * Created by ycao on 5/20/16.
 */

import java.io.*;
import java.security.*;
import java.util.Date;

import sun.security.pkcs11.wrapper.*;
import static sun.security.pkcs11.wrapper.PKCS11Constants.*;
import sun.security.pkcs11.Secmod.*;


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
 * File: GetKeyAttributes.java
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

public class TestKeyAttributes {

    public static final String publicKeyname = "java_test_keypair";
    public static final String privateKeyname = "java_test_keypair_private";
    public static final String secretKeyname = "java_test_key_sym";
    public static final String signText = "The message to be signed.";

    public static void usage()
    {
        System.out.println ("usage: java com.vormetric.pkcs11.sample.TestKeyAttributes -p pin [-k|-kp keyname] [-m module] [-b modulusBits]");
        System.exit (1);
    }

    public static void main ( String[] args)
    {
        String pin = null;
        String libPath = null;
        String keyName = null;
        String initArgs = "";

        int modulusBits = 2048;
        boolean symmetric = true;

        int i;

        if(args.length % 2 != 0)
            usage();

        for (i=0; i<args.length; i++)
        {
            if (args[i].equals("-p")) pin = args[++i];
            else if (args[i].equals("-m")) libPath = args[++i];
            else if (args[i].equals("-k")) { keyName = args[++i]; symmetric = true; }
            else if (args[i].equals("-kp")) { keyName = args[++i]; symmetric = false; }
            else if (args[i].equals("-b")) modulusBits = Integer.parseInt(args[++i]);
            else if (args[i].equals("-a")) initArgs = args[i+1];
            else usage();
        }

        long publickeyID, privatekeyID, keyID;
        long[] keyIDArr;

        try
        {
            if(pin == null)
                usage();

            System.out.println ("Start TestKeyAttributes ..." );
            Vpkcs11Session session = Helper.startUp(Helper.getPKCS11LibPath(libPath), pin, initArgs);

            if( keyName == null ) {
                if(symmetric == true)
                    keyName = secretKeyname;
                else
                    keyName = publicKeyname;
            }
			/* Create the keypair */
            CK_MECHANISM mechanism;

            if(symmetric == true)
                mechanism = new CK_MECHANISM(CKM_AES_KEY_GEN);
            else
                mechanism = new CK_MECHANISM (CKM_RSA_PKCS_KEY_PAIR_GEN);

            CK_ATTRIBUTE[] retrAttrs;
            CK_ATTRIBUTE[] setAttrs;

            if(symmetric == false) {
                publickeyID = Helper.findKey(session, keyName, CKO_PUBLIC_KEY);
                if (publickeyID != 0)
                {
                    session.p11.C_DestroyObject (session.sessionHandle, publickeyID);
                    System.out.println ("Removed existing keypair");
                }

                keyIDArr = Helper.createKeyPair(session, keyName, mechanism, modulusBits);
                System.out.println("Keypair successfully Generated. Public Key Handle: " + keyIDArr[0] + " Private Key Handle: " + keyIDArr[1]);
                publickeyID = keyIDArr[0];
                privatekeyID = keyIDArr[1];

                keyID = Helper.findKey(session, keyName, CKO_PUBLIC_KEY);
                System.out.println("Found public key: "+keyID);

                retrAttrs = new CK_ATTRIBUTE[]
                        {
                                new CK_ATTRIBUTE(CKA_LABEL),
                                new CK_ATTRIBUTE(CKA_CLASS),
                                new CK_ATTRIBUTE(CKA_KEY_TYPE),
                                new CK_ATTRIBUTE(CKA_MODULUS_BITS),
                                new CK_ATTRIBUTE(CKA_PUBLIC_EXPONENT),
                                new CK_ATTRIBUTE(CKA_MODULUS),
                                new CK_ATTRIBUTE(CKA_END_DATE)
                        };

                session.p11.C_GetAttributeValue(session.sessionHandle, keyID, retrAttrs);

                printAttributes(retrAttrs);
                keyID = Helper.findKey(session, keyName, CKO_PRIVATE_KEY) ;

                System.out.println("Found private key: "+keyID);

                retrAttrs = new CK_ATTRIBUTE[]
                    {
                        new CK_ATTRIBUTE(CKA_LABEL),
                        new CK_ATTRIBUTE(CKA_CLASS),
                        new CK_ATTRIBUTE(CKA_KEY_TYPE),
                        new CK_ATTRIBUTE(CKA_MODULUS_BITS),
                        new CK_ATTRIBUTE(CKA_PRIVATE_EXPONENT),
                        new CK_ATTRIBUTE(CKA_MODULUS),
                        new CK_ATTRIBUTE(CKA_END_DATE)
                    };

                session.p11.C_GetAttributeValue(session.sessionHandle, keyID, retrAttrs);

                printAttributes(retrAttrs);

                CK_DATE endDate = new CK_DATE("2016".toCharArray(), "10".toCharArray(), "31".toCharArray());

                setAttrs = new CK_ATTRIBUTE[]
                        {
                                new CK_ATTRIBUTE(CKA_END_DATE, endDate)
                        };
                session.p11.C_SetAttributeValue(session.sessionHandle, keyID, setAttrs);

                session.p11.C_GetAttributeValue(session.sessionHandle, keyID, retrAttrs);

                printAttributes(retrAttrs);

			    /* delete the keypair */
                session.p11.C_DestroyObject (session.sessionHandle, publickeyID);
                System.out.println ("Successfully deleted keypair");
            }
            else {
                keyID = Helper.findKey(session, keyName, CKO_SECRET_KEY);
                if (keyID != 0)
                {
                    session.p11.C_DestroyObject (session.sessionHandle, keyID);
                    System.out.println ("Removed existing keypair");
                }

                keyID = Helper.createKey(session, keyName);
                System.out.println ("Key successfully Generated. Key Handle: " + keyID);

                retrAttrs = new CK_ATTRIBUTE[]
                        {
                                new CK_ATTRIBUTE(CKA_LABEL),
                                new CK_ATTRIBUTE(CKA_CLASS),
                                new CK_ATTRIBUTE(CKA_KEY_TYPE),
                                new CK_ATTRIBUTE(CKA_END_DATE)
                        };
                session.p11.C_GetAttributeValue(session.sessionHandle, keyID, retrAttrs);

                printAttributes(retrAttrs);

                CK_DATE endDate = new CK_DATE("2016".toCharArray(), "10".toCharArray(), "30".toCharArray());

                setAttrs = new CK_ATTRIBUTE[]
                        {
                                new CK_ATTRIBUTE(CKA_END_DATE, endDate)
                        };
                session.p11.C_SetAttributeValue(session.sessionHandle, keyID, setAttrs);

                session.p11.C_GetAttributeValue(session.sessionHandle, keyID, retrAttrs);

                printAttributes(retrAttrs);
            }

			/* The public key handle  is always the first one in the array. Private key the second */

            keyID = Helper.findKey(session, keyName) ;
            if (keyID == 0)
            {
                System.out.println ("The key " + keyName + " has been deleted." );
            }
            else
            {
                System.out.println ("The key : " + keyName + " still exists in DSM.");
            }
            Helper.closeDown(session);
            System.out.println ("End TestKeyAttributes." );
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

    static void printAttributes(CK_ATTRIBUTE[] getAttrs)
    {
        int i;
        String typeName;
        CK_ATTRIBUTE attr;
        byte[] valArray;
        long lval;
        StringBuilder buf;

        for(i=0; i<getAttrs.length; i++)
        {
            attr = getAttrs[i];
            typeName = Helper.getConstantName((long)attr.type);
            switch ((int)attr.type) {
                case (int)CKA_CLASS:
                case (int)CKA_KEY_TYPE:
                case (int)CKA_MODULUS_BITS:
                case (int)CKA_ID:
                     System.out.println ("Attr type: "+typeName+" Value: "+(attr.getLong() & 0xFFFFL));
                    break;
                case (int)CKA_LABEL:
                    System.out.println ("Attr type: "+typeName+" Value: "+new String(attr.getCharArray()));
                    break;
                case (int)CKA_START_DATE:
                case (int)CKA_END_DATE:
                    CK_DATE ckd = (CK_DATE)attr.pValue;
                    System.out.println("Attr type: "+typeName+" Value: "+String.valueOf(ckd));
                    break;
                default:
                    valArray = attr.getByteArray();
                    buf = new StringBuilder(valArray.length * 2);
                    for(byte b: valArray)
                    {
                       buf.append(String.format("%02x", b & 0xff));
                    }
                    System.out.println ("Attr type: "+typeName+" Value: "+buf.toString());
                    break;
            }

        }
    }
}
