package com.vormetric.pkcs11.sample;

import static sun.security.pkcs11.wrapper.PKCS11Constants.CKM_RSA_PKCS;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKM_RSA_PKCS_KEY_PAIR_GEN;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKM_SHA224_HMAC;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKM_SHA256_HMAC;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKM_SHA384_HMAC;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKM_SHA512_HMAC;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKM_SHA_1_HMAC;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKO_PRIVATE_KEY;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKO_PUBLIC_KEY;

/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/

/*
 ***************************************************************************
 * File: SignVerify.java
 ***************************************************************************
 ***************************************************************************
 * This file demonstrates the following
 * 1. Initialization
 * 2. Creating a connection and logging in.
 * 3. Creating a secure hash for a given
 * 4. Using the symmetric key to encrypt plaintext
 * 5. Using the symmetric key to decrypt ciphertext.
 * 6, Delete key.
 * 7. Clean up.
 */
import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStream;

import sun.security.pkcs11.wrapper.CK_MECHANISM;
import sun.security.pkcs11.wrapper.PKCS11Exception;

public class SignVerify {

    public static final CK_MECHANISM hmacSha256Mech  = new CK_MECHANISM (CKM_SHA256_HMAC);
    public static final CK_MECHANISM hmacSha1Mech  = new CK_MECHANISM (CKM_SHA_1_HMAC);
    public static final CK_MECHANISM hmacSha224Mech  = new CK_MECHANISM (CKM_SHA224_HMAC);
    public static final CK_MECHANISM hmacSha384Mech  = new CK_MECHANISM (CKM_SHA384_HMAC);
    public static final CK_MECHANISM hmacSha512Mech  = new CK_MECHANISM (CKM_SHA512_HMAC);
    public static final CK_MECHANISM rsaPkcsMech  = new CK_MECHANISM (CKM_RSA_PKCS);
    
    public static String plainTextInp = "Plain text message to be hashed.";

    public static void usage() {
        System.out.println("usage: java [-cp CLASSPATH] com.vormetric.pkcs11.sample.SignVerify -p pin [-k keyName] [-o operation] [-m module] [-i message] [-g gen_key_action] [-ls lifeSpan]");
        System.out.println("-p: Username:Password of Keymanager");
        System.out.println("-k: Keyname on Keymanager");
        System.out.println("-i: Message in plainText");
        System.out.println("-m: Path of directory where dll is deployed/installed");
	System.out.println("-o: HMAC-SHA256 (default), HMAC-SHA1, HMAC-SHA224, HMAC-SHA384, or HMAC-SHA512, or RSA");
	System.out.println("-g: 0 for versionCreate, 1 for versionRotate, 2 for versionMigrate, 3 for nonVersionCreate");
        System.out.println("-ls: Life Span, Life span of key in days");
        System.exit(1);
    }

    public static String toHex(byte[] bytes) {
		String result = "";
		for (int i = 0; i < bytes.length; i++) {
			result += String.format("%02x", bytes[i]);
		}
		return result;
    }

    public static void main ( String[] args) {
        String pin = null;
        String libPath = null;
        String operation = "HMAC-SHA256";
        String hashedOutFile = "hashedOut.jdt";
        String keyName = "pkcs11_java_sign_verify_test_key";
        CK_MECHANISM signvfyMech = null;
        int digestSize = 32;

        long keyID = 0;
        long publickeyID = 0;
        long privatekeyID = 0;
        boolean bAsymKey = false;
        long[] keyIDArr;
		int genAction = 3;
		int lifespan = 0;
        Vpkcs11Session session = null;

        for (int i = 0; i < args.length; i += 2) {
            if (args[i].equals("-p")) pin = args[i + 1];
            else if (args[i].equals("-m")) libPath = args[i + 1];
            else if (args[i].equals("-i")) plainTextInp = args[i + 1];
            else if (args[i].equals("-o")) operation = args[i + 1];
            else if (args[i].equals("-k")) keyName = args[i + 1];
            else if (args[i].equals("-g")) genAction = Integer.parseInt(args[i + 1]);
            else if (args[i].equals("-ls")) lifespan = Integer.parseInt(args[i+1]);
            else usage();
        }

        try {
            System.out.println("Start SignVerify ...");
            session = Helper.startUp(Helper.getPKCS11LibPath(libPath), pin);

            File hashedFile = new File(hashedOutFile);
            OutputStream hashedOutFS = new FileOutputStream(hashedFile);

            byte[] hashBytes;
            //String strContent;
			boolean verifyResult = true;

            if (operation.equals("") || operation.equals("HMAC-SHA256")) {
                System.out.println("HMAC-SHA256 mode selected");
                signvfyMech = hmacSha256Mech;
            }
            else if (operation.equals("HMAC-SHA1")) {
                System.out.println("HMAC-SHA1 mode selected");
                signvfyMech = hmacSha1Mech;
            }
            else if (operation.equals("HMAC-SHA224")) {
                System.out.println("HMAC-SHA224 mode selected");
                signvfyMech = hmacSha224Mech;
            }
            else if (operation.equals("HMAC-SHA384")) {
                System.out.println("HMAC-SHA384 mode selected");
                signvfyMech = hmacSha384Mech;
				digestSize = 48;
            }
            else if (operation.equals("HMAC-SHA512")) {
                System.out.println("HMAC-SHA512 mode selected");
                signvfyMech = hmacSha512Mech;
				digestSize = 64;
            }
            else if (operation.equals("RSA")){
                System.out.println("RSA mode selected");
                signvfyMech = rsaPkcsMech;
                bAsymKey = true;
            }
            else {
                System.out.println("Unknown operation: " + operation + ". Defaulting to HMAC-SHA256 mode");
                signvfyMech = hmacSha256Mech;
            }

            if(bAsymKey == false ) {
                keyID = Helper.findKey(session, keyName);

                if (keyID == 0) {
                    System.out.println("the key is not found, creating it...");
                    keyID = Helper.createKey(session, keyName, genAction, lifespan);
                    System.out.println("Key successfully Created. Key Handle: " + keyID);
                } else {
                    System.out.println("Key successfully Found. Key Handle: " + keyID);
                }
            }
            else {
                publickeyID = Helper.findKey(session, keyName, CKO_PUBLIC_KEY);

                privatekeyID = Helper.findKey(session, keyName, CKO_PRIVATE_KEY);

                if(publickeyID == 0 && privatekeyID == 0) {
                    System.out.println("the keypair is not found, creating it...");
                    keyIDArr = Helper.createKeyPair(session, keyName, new CK_MECHANISM (CKM_RSA_PKCS_KEY_PAIR_GEN), 2048);

                    if(keyIDArr != null) {
                        publickeyID = keyIDArr[0];
                        privatekeyID = keyIDArr[1];
                        System.out.println("Asymmetric KeyPair successfully Created: public key handle: " + publickeyID + ", private key handle: "+privatekeyID);
                    }
                }
                else {
                    System.out.println("Asymmetric keypair successfully Found; public key: " + publickeyID + ", private key: "+privatekeyID);
                }
            }

            try {
                hashBytes = sign(session, signvfyMech, plainTextInp.getBytes(), bAsymKey == false ? keyID : privatekeyID);
                System.out.println("Sign successful; signature = " + toHex(hashBytes));

                verify(session, signvfyMech, plainTextInp.getBytes(), bAsymKey == false ? keyID : publickeyID, hashBytes);
            }
            catch(PKCS11Exception pke){
                verifyResult = false;
            }

            hashedOutFS.flush();
            hashedOutFS.close();
            System.out.println("Verify = " + verifyResult);

        } catch (Exception e) {
			e.printStackTrace();
        }
        finally {
            Helper.closeDown(session);
            System.out.println("End SignVerify.");
        }
    }

    public static byte[] sign(Vpkcs11Session session, CK_MECHANISM mech, byte[] input, long key)
		throws Exception {
		session.p11.C_SignInit(session.sessionHandle, mech, key);
		return session.p11.C_Sign(session.sessionHandle, input);
    }

    public static void verify(Vpkcs11Session session, CK_MECHANISM mech, byte[] input, long key, byte[] hash)
		throws Exception {
		session.p11.C_VerifyInit(session.sessionHandle, mech, key);
		session.p11.C_Verify(session.sessionHandle, input, hash);
    }

}
