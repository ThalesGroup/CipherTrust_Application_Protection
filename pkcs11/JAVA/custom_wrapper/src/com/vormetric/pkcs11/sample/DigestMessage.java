package com.vormetric.pkcs11.sample;

import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKM_MD5;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKM_MD5_HMAC;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKM_SHA224;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKM_SHA224_HMAC;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKM_SHA256;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKM_SHA256_HMAC;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKM_SHA384;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKM_SHA384_HMAC;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKM_SHA512;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKM_SHA512_HMAC;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKM_SHA_1;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKM_SHA_1_HMAC;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;

import com.vormetric.pkcs11.wrapper.CK_MECHANISM;
/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
/*
 ***************************************************************************
 * File: EncryptDecryptMessage.java
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

public class DigestMessage {
    public static final CK_MECHANISM sha256Mech      = new CK_MECHANISM (CKM_SHA256);
    public static final CK_MECHANISM sha384Mech      = new CK_MECHANISM (CKM_SHA384);
    public static final CK_MECHANISM sha1Mech        = new CK_MECHANISM (CKM_SHA_1);
    public static final CK_MECHANISM sha224Mech      = new CK_MECHANISM (CKM_SHA224);
    public static final CK_MECHANISM md5Mech         = new CK_MECHANISM (CKM_MD5);
    public static final CK_MECHANISM sha512Mech      = new CK_MECHANISM (CKM_SHA512);
    public static final CK_MECHANISM hmacSha256Mech  = new CK_MECHANISM (CKM_SHA256_HMAC);
    public static final CK_MECHANISM hmacSha1Mech  = new CK_MECHANISM (CKM_SHA_1_HMAC);
    public static final CK_MECHANISM hmacSha224Mech  = new CK_MECHANISM (CKM_SHA224_HMAC);
    public static final CK_MECHANISM hmacSha384Mech  = new CK_MECHANISM (CKM_SHA384_HMAC);
    public static final CK_MECHANISM hmacSha512Mech  = new CK_MECHANISM (CKM_SHA512_HMAC);
    public static final CK_MECHANISM hmacMD5Mech  = new CK_MECHANISM (CKM_MD5_HMAC);

    public static String plainTextInp = "Plain text message to be hashed.";

    public static void usage() {
        System.out.println("usage: java [-cp CLASSPATH] com.vormetric.pkcs11.sample.DigestMessage -p pin [-k keyName] [-f input-file]");
	    System.out.println("[-o operation] [-m module] [-i message] [-g gen_key_action]");
        System.out.println("-p: Username:Password of Keymanager");
        System.out.println("-m: Path of directory where dll is deployed/installed");
        System.out.println("-k: Keyname on Keymanager");
        System.out.println("-f: Input file path for plainText ");  
        System.out.println("-i: Message in plainText");
		System.out.println("-o: HMAC-SHA256, HMAC-MD5, HMAC-SHA1, HMAC-SHA224, HMAC-SHA384, HMAC-SHA512, MD5, SHA1, SHA224, SHA512, SHA384 or SHA256 (default)");
		System.out.println("-g: 0 for versionCreate, 1 for versionRotate, 2 for versionMigrate, 3 for nonVersionCreate");
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
        String operation = "SHA256";
        String hashedOutFile = "hashedOut.jdt";
        String plainInputFile = null;
        String keyName = "pkcs11_java_digest_test_key";
        CK_MECHANISM hashMech = null;
        int digestSize = 32;
        long key = 0;
		int genAction = 3;
        Vpkcs11Session session = null;

        for (int i = 0; i < args.length; i += 2) {
            if (args[i].equals("-p")) pin = args[i + 1];
            else if (args[i].equals("-m")) libPath = args[i + 1];
            else if (args[i].equals("-i")) plainTextInp = args[i + 1];
            else if (args[i].equals("-o")) operation = args[i + 1];
            else if (args[i].equals("-f")) plainInputFile = args[i + 1];
            else if (args[i].equals("-k")) keyName = args[i + 1];
            else if (args[i].equals("-g")) genAction = Integer.parseInt(args[i + 1]);
            else usage();
        }

        try {
            System.out.println("Start DigestMessage ...");
            session = Helper.startUp(Helper.getPKCS11LibPath(libPath), pin);

            long keyID = Helper.findKey(session, keyName);

            if (keyID == 0) {
                System.out.println("the key is not found, creating it...");
                keyID = Helper.createKey(session, keyName, genAction, 0);
                System.out.println("Key successfully Created. Key Handle: " + keyID);
            } else {
                System.out.println("Key successfully Found. Key Handle: " + keyID);
            }

            File hashedFile = new File(hashedOutFile);
            OutputStream hashedOutFS = new FileOutputStream(hashedFile);

            byte[] hashBytes;
            
            if (operation.equals("SHA512")) {
                System.out.println("SHA512 mode selected");
                hashMech = sha512Mech;
                digestSize = 64;
            } else if (operation.equals("SHA384")) {
                System.out.println("SHA384 mode selected");
                hashMech = sha384Mech;
                digestSize = 48;
            } else if (operation.equals("SHA1")) {
                System.out.println("SHA1 mode selected");
                hashMech = sha1Mech;
                digestSize = 20;
            } else if (operation.equals("SHA224")) {
                System.out.println("SHA224 mode selected");
                hashMech = sha224Mech;
                digestSize = 28;
            } else if (operation.equals("MD5")) {
                System.out.println("MD5 mode selected");
                hashMech = md5Mech;
                digestSize = 16;
            } else if (operation.equals("HMAC-SHA256")) {
                System.out.println("HMAC-SHA256 mode selected");
                hashMech = hmacSha256Mech;
                key = keyID;
            } else if (operation.equals("HMAC-SHA1")) {
                System.out.println("HMAC-SHA1 mode selected");
                hashMech = hmacSha1Mech;
                key = keyID;
            } else if (operation.equals("HMAC-SHA224")) {
                System.out.println("HMAC-SHA224 mode selected");
                hashMech = hmacSha224Mech;
                key = keyID;
            } else if (operation.equals("HMAC-SHA384")) {
                System.out.println("HMAC-SHA384 mode selected");
                hashMech = hmacSha384Mech;
		        key = keyID;
                digestSize = 48;
            } else if (operation.equals("HMAC-SHA512")) {
                System.out.println("HMAC-SHA512 mode selected");
                hashMech = hmacSha512Mech;
		        key = keyID;
                digestSize = 64;
            } else if (operation.equals("HMAC-MD5")) {
                System.out.println("HMAC-MD5 mode selected");
                hashMech = hmacMD5Mech;
		        key = keyID;
            } else if (operation.equals("") || operation.equals("SHA256")) {
                System.out.println("SHA256 mode selected");
                hashMech = sha256Mech;
            } else {
                System.out.println("SHA256 mode selected");
                hashMech = sha256Mech;
            }

            if (plainInputFile == null) {
		      hashBytes = digest(session, hashMech, digestSize, plainTextInp.getBytes(), key);
		      System.out.println("digest = " + toHex(hashBytes));
	        } else {
		      FileInputStream is = new FileInputStream(plainInputFile);
		      hashBytes = digestStream(session, hashMech, digestSize, is, key);
		      System.out.println("digest = " + toHex(hashBytes));
		      is.close();
	        }

            hashedOutFS.flush();
            hashedOutFS.close();

        } catch (Exception e) {
	        e.printStackTrace();
        }
        finally {
            Helper.closeDown(session);
            System.out.println("End DigestMessage.");
        }
    }

    public static byte[] digest(Vpkcs11Session session, CK_MECHANISM mech, int digestSize, byte[] input, long key)
	throws Exception {
	  byte[] result = null;

	  session.p11.C_DigestInit(session.sessionHandle, mech);
	  if (key != 0) {
	    session.p11.C_DigestKey(session.sessionHandle, key);
	  }
	  session.p11.C_DigestUpdate(session.sessionHandle, 0, input, 0, input.length);
	  result = new byte[digestSize];
	  int size = session.p11.C_DigestFinal(session.sessionHandle, result, 0, digestSize);
	  return result;
    }

    public static byte[] digestStream(Vpkcs11Session session, CK_MECHANISM mech, int digestSize, InputStream input,long key)
	throws Exception {
	  byte[] result = null;
	  byte[] buffer = new byte[1024];
	  int content = 0;

	  session.p11.C_DigestInit(session.sessionHandle, mech);
	  if (key != 0) {
	    session.p11.C_DigestKey(session.sessionHandle, key);
	  }
	  while ((content = input.read(buffer, 0, buffer.length)) != -1) {
	    session.p11.C_DigestUpdate(session.sessionHandle, 0, buffer, 0, content);
	  }
	  result = new byte[digestSize];
	  int size = session.p11.C_DigestFinal(session.sessionHandle, result, 0, digestSize);
	  return result;
    }
}
