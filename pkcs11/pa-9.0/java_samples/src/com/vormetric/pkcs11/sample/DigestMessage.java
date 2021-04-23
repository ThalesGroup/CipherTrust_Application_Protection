package com.vormetric.pkcs11.sample;
/***************************************************************************
 ** Copyright(c) 2014                           Confidential Material     **
 **                                                                       **
 ** This file is the property of Vormetric Inc.                           **
 ** The contents are proprietary and confidential.                        **
 ** Unauthorized use, duplication, or dissemination of this document,     **
 ** in whole or in part, is forbidden without the express consent of      **
 ** Vormetric, Inc..                                                      **
 **                                                                       **
 **************************************************************************/
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

import java.io.*;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.CharBuffer;
import java.nio.charset.*;
import java.nio.file.*;
import java.security.*;
import java.util.*;

import sun.nio.cs.*;
import sun.security.pkcs11.wrapper.*;
import static sun.security.pkcs11.wrapper.PKCS11Constants.*;

public class DigestMessage {

    public static final CK_MECHANISM sha256Mech      = new CK_MECHANISM (CKM_SHA256);
    public static final CK_MECHANISM sha384Mech      = new CK_MECHANISM (CKM_SHA384);
    public static final CK_MECHANISM sha512Mech      = new CK_MECHANISM (CKM_SHA512);
    public static final CK_MECHANISM hmacSha256Mech  = new CK_MECHANISM (CKM_SHA256_HMAC);

    public static final String plainTextInp = "Plain text message to be hashed.";

    public static void usage() {
        System.out.println("usage: java com.vormetric.pkcs11.sample.DigestMessage -p pin [-k keyName] [-f input-file]");
	System.out.println("       [-o operation] HMAC_SHA256, SHA512, SHA384 or SHA256 (default) [-m module] [-d output-file]");
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
        String decryptedOutFile = null;
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        String keyName = "vpkcs11_java_test_key";
        String initArgs = "";
        FileWriter decryptedWriter = null;
        CK_MECHANISM hashMech = null;
	int digestSize = 32;
	long key = 0;

        int i;
        for (i = 0; i < args.length; i += 2) {
            if (args[i].equals("-p")) pin = args[i + 1];
            else if (args[i].equals("-m")) libPath = args[i + 1];
            else if (args[i].equals("-o")) operation = args[i + 1];
            else if (args[i].equals("-f")) plainInputFile = args[i + 1];
            else if (args[i].equals("-k")) keyName = args[i + 1];
            else if (args[i].equals("-d")) decryptedOutFile = args[i + 1];
            else if (args[i].equals("-a")) initArgs = args[i+1];
            else usage();
        }

        try {
            System.out.println("Start DigestMessage ...");
            Vpkcs11Session session = Helper.startUp(Helper.getPKCS11LibPath(libPath), pin, initArgs);

            long keyID = Helper.findKey(session, keyName);

            if (keyID == 0) {
                System.out.println("the key is not found, creating it...");
                keyID = Helper.createKey(session, keyName);
                System.out.println("Key successfully Created. Key Handle: " + keyID);
            } else {
                System.out.println("Key successfully Found. Key Handle: " + keyID);
            }

            File hashedFile = new File(hashedOutFile);
            OutputStream hashedOutFS = new FileOutputStream(hashedFile);

            if(decryptedOutFile != null) {
                decryptedWriter = new FileWriter(decryptedOutFile);
	    }
            byte[] byteContent;
            byte[] plainBytes;
            byte[] hashBytes;
            byte[] bta;
            int len, plainBytesLen;
            String strContent;

            if (operation.equals("SHA512")) {
                System.out.println("SHA512 mode selected");
                hashMech = sha512Mech;
		digestSize = 64;
            } 
            else if (operation.equals("SHA384")) {
                System.out.println("SHA384 mode selected");
                hashMech = sha384Mech;
		digestSize = 48;
            } 
            else if (operation.equals("HMAC_SHA256")) {
                System.out.println("HMAC_SHA256 mode selected");
                hashMech = hmacSha256Mech;
		key = keyID;
            } 
	    else if (operation.equals("") || operation.equals("SHA256")) {
                System.out.println("SHA256 mode selected");
                hashMech = sha256Mech;
            } else {
                System.out.println("SHA256 mode selected");
                hashMech = sha256Mech;
            }

	    if (plainInputFile == null) {
		hashBytes = digest(session, hashMech, digestSize, plainTextInp.getBytes(), key);
		System.out.println("digest = " + toHex(hashBytes));
	    }
	    else {
		FileInputStream is = new FileInputStream(plainInputFile);
		hashBytes = digestStream(session, hashMech, digestSize, is, key);
		System.out.println("digest = " + toHex(hashBytes));
		is.close();
	    }
            /* encrypt, decrypt with key */
	    /*
            if (plainInputFile != null) {
                File inputFile = new File(plainInputFile);

		{
                    InputStream inputFS = new FileInputStream(inputFile);
                    int bytesLen = inputFS.available();
                    plainBytes = new byte[bytesLen];

                    plainBytesLen = inputFS.read(plainBytes);
                    plainText = new String(plainBytes);

                    decryptedBytes = encryptDecryptBuf(session, hashMech, keyID, plainBytes, hashedOutFS, utfMode);
                    decryptedText = new String(decryptedBytes);

                    if(decryptedWriter != null) {
                        decryptedWriter.write(decryptedText);
                    }
                }
            } else {
                plainBytes = plainTextInp.getBytes();
                decryptedBytes = encryptDecryptBuf(session, hashMech, keyID, plainBytes, hashedOutFS, utfMode);
                decryptedText = new String(decryptedBytes, utfMode);

                if(decryptedWriter != null)
                    decryptedWriter.write(decryptedText);
            }

	    /* Delete the key */
	    /*	session.p11.C_DestroyObject (session.sessionHandle, keyID);
		System.out.println ("Successfully deleted key"); */

            Helper.closeDown(session);
            System.out.println("End DigestMessage.");
            hashedOutFS.flush();
            hashedOutFS.close();

        } catch (Exception e) {
	    e.printStackTrace();
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
