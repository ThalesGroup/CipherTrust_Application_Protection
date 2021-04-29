package com.vormetric.pkcs11.sample;
/*************************************************************************
 **                                                                     **
 ** Copyright(c) 2014-2018                        Confidential Material **
 **                                                                     **
 ** This file is the property of Vormetric Inc.                         **
 ** The contents are proprietary and confidential.                      **
 ** Unauthorized use, duplication, or dissemination of this document,   **
 ** in whole or in part, is forbidden without the express consent of    **
 ** Vormetric, Inc..                                                    **
 **                                                                     **
 *************************************************************************/
/*
 ***************************************************************************
 * File: EncryptDecryptMessage.java
 ***************************************************************************
 ***************************************************************************
 * This file demonstrates the following
 * 1. Initialization
 * 2. Creating a connection and logging in.
 * 3. Creating a symmetric key on the Data Security Manager
 * 4. Using the symmetric key to encrypt plaintext
 * 5. Using the symmetric key to decrypt ciphertext.
 * 6, Delete key.
 * 7. Clean up.
 */

import java.io.*;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.charset.*;
import java.nio.file.*;
import java.util.*;



import com.vormetric.pkcs11.wrapper.*;
import com.vormetric.pkcs11.wrapper.params.CK_GCM_PARAMS;

import static com.vormetric.pkcs11.wrapper.PKCS11Constants.*;

public class EncryptDecryptMessage {

	public static final byte[] iv = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x10, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F};
	public static final byte[] gcm_iv = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C};
    public static final byte[] UTF8_BOM = { (byte)0xef, (byte)0xbb, (byte)0xbf };

    public static final byte[] UTF16BE_BOM = { (byte)0xfe, (byte)0xff };
    public static final byte[] UTF16LE_BOM = { (byte)0xff, (byte)0xfe };

    public static final byte[] UTF32BE_BOM = { 0x00, 0x00, (byte)0xfe, (byte)0xff };
    public static final byte[] UTF32LE_BOM = { (byte)0xff, (byte)0xfe, 0x00, 0x00 };

	public static final CK_MECHANISM encMechCbcPad = new CK_MECHANISM (CKM_AES_CBC_PAD, iv);
	public static final CK_MECHANISM encMechCtr    = new CK_MECHANISM (CKM_AES_CTR    , iv);
    public static final CK_MECHANISM encMechCbc    = new CK_MECHANISM (CKM_AES_CBC    , iv);
    public static final CK_MECHANISM encMechRsa    = new CK_MECHANISM (CKM_RSA_PKCS    , iv);

    public static final String plainTextInp = "Plain text message to be encrypted.";

    public static void usage()
    {
        System.out.println("usage: java com.vormetric.pkcs11.sample.EncryptDecryptMessage -p pin [-k keyName] [-m module] [-o operation {CTR | CBC_PAD (default) | FPE | FF1 | GCM} ]");
        System.out.println("       [-f 'inputtokenfile'] {[-c 'char set']|[-r 'charset file']|[-l 'literal charset file']} [-u utf-mode-name] [-d 'decryptedfile'] [-g genAction] [-a 'associated data'] [-t tagSize]");
        System.out.println("utf-mode-name is one of ASCII, UTF-8, UTF-16LE, UTF-16BE, UTF-32LE, UTF-32BE");
        System.out.println("genAction     is one of 0 (generate versioned key) or 3 (generate non-versioned key)");
        System.exit (1);
    }

    public static ByteOrder getSelByteOrder(String strMode) {
        ByteOrder selByteOrder = null;
        if(strMode.equalsIgnoreCase("UTF-8"))
            selByteOrder = ByteOrder.nativeOrder();
        else if(strMode.equalsIgnoreCase("UTF-16LE"))
            selByteOrder = ByteOrder.LITTLE_ENDIAN;
        else if(strMode.equalsIgnoreCase("UTF-16"))
            selByteOrder = ByteOrder.BIG_ENDIAN;
        else if(strMode.equalsIgnoreCase("UTF-32LE"))
            selByteOrder = ByteOrder.LITTLE_ENDIAN;
        else if(strMode.equalsIgnoreCase("UTF-32"))
            selByteOrder = ByteOrder.BIG_ENDIAN;
        return selByteOrder;
    }

    public static byte getUtfMode(String strMode) {
        byte btmode = -1;
        if     (strMode.equalsIgnoreCase("UTF-8"))
            btmode = 1;
        else if(strMode.equalsIgnoreCase("UTF-16LE"))
            btmode = 2;
        else if(strMode.equalsIgnoreCase("UTF-16BE"))
            btmode = 3;
        else if(strMode.equalsIgnoreCase("UTF-32LE"))
            btmode = 4;
        else if(strMode.equalsIgnoreCase("UTF-32BE"))
            btmode = 5;
        else if(strMode.equalsIgnoreCase("ASCII"))
            btmode = 0;
        return btmode;
    }

    private static String checkEncodingBOM(byte[] bta) {
        String strMode = "ASCII";
        if( bta[0] == UTF8_BOM[0] && bta[1] == UTF8_BOM[1] && bta[2]==UTF8_BOM[2] )
            strMode = "UTF-8";
        else if( bta[0] == UTF32LE_BOM[0] && bta[1] == UTF32LE_BOM[1] &&
                bta[2] == UTF32LE_BOM[2] && bta[3] == UTF32LE_BOM[3] )
            strMode = "UTF-32LE";
        else if(bta[0] == UTF16LE_BOM[0] && bta[1] == UTF16LE_BOM[1])
            strMode = "UTF-16LE";
        else if(bta[0] == UTF16BE_BOM[0] && bta[1] == UTF16BE_BOM[1])
            strMode = "UTF-16BE";
        else if( bta[0] == UTF32BE_BOM[0] && bta[1] == UTF32BE_BOM[1] &&
                bta[2] == UTF32BE_BOM[2] && bta[3] == UTF32BE_BOM[3] )
            strMode = "UTF-32BE";
        return strMode;
    }

    private static byte[] removeUTFBOM(byte[] bta, int btmode)
    {
        switch (btmode)
        {
            case 1:
                if(bta.length > 3)
                {
                    if( bta[0] == UTF8_BOM[0] && bta[1] == UTF8_BOM[1] && bta[2]==UTF8_BOM[2] )
                        bta = Arrays.copyOfRange(bta, 3, bta.length);
                }
                break;
            case 2:
                if(bta.length > 2)
                {
                    if( bta[0] == UTF16LE_BOM[0] && bta[1] == UTF16LE_BOM[1] )
                        bta = Arrays.copyOfRange(bta, 2, bta.length);
                }
                break;
            case 3:
                if(bta.length > 2)
                {
                    if( bta[0] == UTF16BE_BOM[0] && bta[1] == UTF16BE_BOM[1] )
                        bta = Arrays.copyOfRange(bta, 2, bta.length);
                }
                break;
            case 4:
                if(bta.length > 4)
                {
                    if( bta[0] == UTF32LE_BOM[0] && bta[1] == UTF32LE_BOM[1] &&
                        bta[2] == UTF32LE_BOM[2] && bta[3] == UTF32LE_BOM[3] )
                        bta = Arrays.copyOfRange(bta, 4, bta.length);
                }
                break;
            case 5:
                if(bta.length > 4)
                {
                    if( bta[0] == UTF32BE_BOM[0] && bta[1] == UTF32BE_BOM[1] &&
                        bta[2] == UTF32BE_BOM[2] && bta[3] == UTF32BE_BOM[3] )
                        bta = Arrays.copyOfRange(bta, 4, bta.length);
                }
                break;
        }
        return bta;
    }

    public static void main ( String[] args) {
        String pin = null;
        String libPath = null;
        String operation = "CBC_PAD";
        String encryptedOutFile = "encryptedOut.jdt";
        String plainInputFile = null;
        String decryptedOutFile = null;
        String charSetStr = null;
        String tweakStr = null;
        String charSetInputFile = null;
        String utfMode = "ASCII";				
        char charSetChoc = '\0';
        byte[] charSet, tweakSet;
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        String keyName = "vpkcs11_java_test_key";
        FileWriter decryptedWriter = null;
        String fileUtfMode = "ASCII";
        String inputUtfMode = null;
        int genAction = 3;
        String aad = "";
        int tagSize = 96;
        byte[] tweak = {0x07, 0x06, 0x05, 0x04, 0x03, 0x02, 0x01, 0x00};
        CK_MECHANISM encMechFpe = null;
        CK_MECHANISM encMech = null;
        boolean bAsymKey = false;
        int i;
        int lifespan = 0;

        for (i = 0; i < args.length; i += 2) {
            if      (args[i].equals("-p")) pin = args[i + 1];
            else if (args[i].equals("-m")) libPath = args[i + 1];
            else if (args[i].equals("-o")) operation = args[i + 1];
            else if (args[i].equals("-f")) plainInputFile = args[i + 1];
            else if (args[i].equals("-iu")) inputUtfMode = args[i + 1];
            else if (args[i].equals("-ls")) lifespan = Integer.parseInt(args[i+1]);
            else if (args[i].equals("-c")) {
                charSetStr = args[i + 1];
                charSetChoc = 'c';
            }
            else if (args[i].equals("-t")) tweakStr = args[i + 1];
            else if (args[i].equals("-r")) {
                charSetInputFile = args[i + 1];
                charSetChoc = 'r';
            }
            else if (args[i].equals("-l")) {
                charSetInputFile = args[i + 1];
                charSetChoc = 'l';
            }
            else if (args[i].equals("-u")) utfMode = args[i + 1];
            else if (args[i].equals("-k")) keyName = args[i + 1];
            else if (args[i].equals("-g")) genAction = Integer.parseInt(args[i + 1]);
            else if (args[i].equals("-d")) decryptedOutFile = args[i + 1];
            else if (args[i].equals("-a")) aad = args[i + 1];
            else if (args[i].equals("-t")) tagSize = Integer.parseInt(args[i + 1]);
            else usage();
        }
        if(utfMode == null) utfMode = "ASCII";

        try {
            System.out.println("Start EncryptDecryptMessage ...");
            Vpkcs11Session session = Helper.startUp(Helper.getPKCS11LibPath(libPath), pin);

            File encryptedFile = new File(encryptedOutFile);
            OutputStream encryptedOutFS = new FileOutputStream(encryptedFile);

            if(decryptedOutFile != null)
                decryptedWriter = new FileWriter(decryptedOutFile);

            String plainText, decryptedText;
            byte[] byteContent;
            byte[] plainBytes;
            byte[] decryptedBytes;
            byte[] bta;
            long keyID = 0;
            long[] keyIDArr = null;
            int len;
            String strContent;
            int radix = 0;
            ByteBuffer btBuf;
            long publickeyID = 0;
            long privatekeyID = 0;

            ByteOrder btOrder = getSelByteOrder(utfMode);
            byte btMode = getUtfMode(utfMode);

            if (operation.equals("CTR")) {
                System.out.println("CTR mode selected");
                encMech = encMechCtr;
            }
            else if (operation.equals("RSA")){
                System.out.println("RSA mode selected");
                encMech = encMechRsa;
                bAsymKey = true;
            } else if (operation.equals("GCM")) {
            	System.out.println("GCM mode selected");
            	byte[] aadBytes = aad.getBytes();
            	
            	CK_GCM_PARAMS gcmParams = new CK_GCM_PARAMS(gcm_iv, gcm_iv.length, gcm_iv.length<<3, aadBytes,aadBytes.length, tagSize);
            	//System.out.println(gcmParams.toByteArray().length);
            	CK_MECHANISM encMechGcm = new CK_MECHANISM(Helper.CKM_AES_GCM, gcmParams);
            	encMech = encMechGcm; 
            }
            else if (operation.equals("FPE") || operation.equals("FF1")) {
                System.out.println("FPE/FF1 mode selected");

                if(charSetInputFile != null && !charSetInputFile.isEmpty())
                {
                    byteContent = Files.readAllBytes(Paths.get(charSetInputFile));
                    fileUtfMode = checkEncodingBOM(byteContent);

                    if(charSetChoc == 'l' ) {
                        String content;
                        byte[] sortedContent;

                        if(btMode == 0) { /* ASCII */
                            Arrays.sort(byteContent);
                            int cnt_len = byteContent.length;

                            if (cnt_len < 2) {
                                sortedContent = byteContent;
                            } else {
                                int j = 0;
                                i = 1;

                                while (i < cnt_len) {
                                    if (byteContent[i] == byteContent[j]) {
                                        i++;
                                    } else {
                                        byteContent[++j] = byteContent[i];
                                        i++;
                                    }
                                }
                                sortedContent = Arrays.copyOf(byteContent, j + 1);
                            }
                            content = new String(sortedContent, Charset.forName(utfMode));
                            charSetStr = content.replaceAll("[\n\r]", "");
                            radix = charSetStr.length();
                        }
                        else {
                            byteContent = removeUTFBOM(byteContent, getUtfMode(fileUtfMode));
                            strContent = new String(byteContent, Charset.forName(fileUtfMode));

                            baos.reset();
                            for (char c : strContent.toCharArray()) {
                                bta = new String( new char[] {c}).getBytes(utfMode);

                                bta = removeUTFBOM(bta, 3);
                                len = bta.length;
                                btBuf = ByteBuffer.allocate(len);
                                btBuf.order(btOrder);

                                if (btMode == 4 || btMode == 5) {
                                    btBuf.asIntBuffer().put(c);
                                }
                                else if(btMode == 1) {
                                    btBuf = ByteBuffer.wrap(bta).order(btOrder);
                                }
                                else {
                                    btBuf.asCharBuffer().put(c);
                                }
                                radix++;
                                baos.write(btBuf.array());
                            }
                        }
                    }
                    else if(charSetChoc == 'r' ) {
                        strContent = new String(byteContent, Charset.forName("ASCII"));
                        String delims = ",";
                        String[] tokens = strContent.split(delims);
                        int dashid;
                        int rstart, rend, rcp;
                        char[] chars;

                        try {
                            baos.reset();
                            for (String t : tokens) {
                                dashid = t.indexOf('-');
                                if (dashid != -1) {
                                    rstart = Integer.valueOf(t.substring(0, dashid).trim(), 16);
                                    rend = Integer.valueOf(t.substring(dashid + 1).trim(), 16);

                                    for (rcp = rstart; rcp <= rend; rcp++) {
                                        chars = Character.toChars(rcp);
                                        bta = new String(chars).getBytes(utfMode);

                                        bta = removeUTFBOM(bta, 3);
                                        len = bta.length;
                                        btBuf = ByteBuffer.allocate(len);
                                        btBuf.order(btOrder);

                                        if (btMode == 4 || btMode == 5) {
                                            btBuf.asIntBuffer().put(rcp);
                                            radix++;
                                        }
                                        else if(btMode == 1) {
                                            btBuf = ByteBuffer.wrap(bta).order(btOrder);
                                            for (char c : chars)
                                                radix++;
                                        }
                                        else {
                                            for (char c : chars) {
                                                btBuf.asCharBuffer().put(c);
                                                radix++;
                                            }
                                        }
                                        baos.write(btBuf.array());
                                    }
                                } else {

                                    rcp = Integer.valueOf(t.trim(), 16);
                                    chars = Character.toChars(rcp);

                                    bta = new String(chars).getBytes(utfMode);
                                    bta = removeUTFBOM(bta, 3);
                                    len = bta.length;
                                    btBuf = ByteBuffer.allocate(len);
                                    btBuf.order(btOrder);

                                    if (btMode == 4 || btMode == 5) {
                                        btBuf.asIntBuffer().put(rcp);
                                        radix++;
                                    }
                                    else if(btMode == 1) {
                                        btBuf = ByteBuffer.wrap(bta).order(btOrder);
                                        for (char c : chars)
                                            radix++;
                                    }
                                    else {
                                        for (char c : chars) {
                                            btBuf.asCharBuffer().put(c);
                                            radix++;
                                        }
                                    }
                                    baos.write(btBuf.array());
                                }
                            }
                        }
                        catch(java.io.UnsupportedEncodingException iue)
                        {
                            iue.printStackTrace();
                        }
                        catch(java.io.IOException ioe)
                        {}
                    }
                }

                if(utfMode.equals("ASCII")) {
                    charSet = charSetStr != null ? charSetStr.getBytes() : "0123456789".getBytes();
                }
                else {
                    charSet = baos.toByteArray();
                }

                if(charSetChoc == 'c')
                {
                    radix = charSet.length;
                }

                ByteArrayOutputStream fpeIVBytes;
                DataOutputStream dos;

                if(operation.equals("FPE")) {
                    if (utfMode.equals("ASCII")) {
                        fpeIVBytes = new ByteArrayOutputStream(9 + charSet.length);
                        dos = new DataOutputStream(fpeIVBytes);
                        dos.write(tweak, 0, 8);
                        dos.write((charSetStr != null ? charSet.length : 1) & 0xFF);
                    } else {
                        fpeIVBytes = new ByteArrayOutputStream(16 + charSet.length);
                        dos = new DataOutputStream(fpeIVBytes);
                        dos.write(tweak, 0, 8);
                        dos.write(1 & 0xFF);
                        dos.write(btMode & 0xFF);

                        btBuf = ByteBuffer.allocate(2);
                        btBuf.order(ByteOrder.BIG_ENDIAN).putShort((short) (radix & 0xFFFF));
                        dos.write(btBuf.array());
                        btBuf = ByteBuffer.allocate(4);
                        btBuf.order(ByteOrder.BIG_ENDIAN).putInt(charSet.length);
                        dos.write(btBuf.array());
                    }
                    dos.write(charSet, 0, charSet.length);
                    dos.flush();
                    encMechFpe = new CK_MECHANISM(0x80004001L, fpeIVBytes.toByteArray());
                }
                else if(operation.equals("FF1")) {
                    tweakSet = tweakStr != null ? tweakStr.getBytes() : null;
                    fpeIVBytes = new ByteArrayOutputStream(11 + charSet.length + (tweakSet != null ? tweakSet.length : 0));
                    dos = new DataOutputStream(fpeIVBytes);

                    btBuf = ByteBuffer.allocate(4);
                    btBuf.order(ByteOrder.BIG_ENDIAN).putInt(charSet.length);
                    dos.write(btBuf.array());

                    btBuf = ByteBuffer.allocate(4);
                    btBuf.order(ByteOrder.BIG_ENDIAN).putInt(tweakSet != null ? tweakSet.length : 0);
                    dos.write(btBuf.array());

                    btBuf = ByteBuffer.allocate(2);
                    btBuf.order(ByteOrder.BIG_ENDIAN).putShort((short) (radix & 0xFFFF));
                    dos.write(btBuf.array());

                    dos.write(btMode & 0xFF);

                    dos.write(charSet, 0, charSet.length);
                    if(tweakSet != null) {
                        dos.write(tweakSet, 0, tweakSet.length);
                    }

                    dos.flush();
                    encMechFpe = new CK_MECHANISM(0x80004002L, fpeIVBytes.toByteArray());
                }
                encMech = encMechFpe; /* also used for FF1 */
            } else if (operation.equals("CBC")) {
                System.out.println("CBC mode selected");
                encMech = encMechCbc;
            } else {
                System.out.println("CBC PAD mode selected");
                encMech = encMechCbcPad;
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
            /* encrypt, decrypt with key */
            if (plainInputFile != null && bAsymKey == false) {
                File inputFile = new File(plainInputFile);

                if (operation.equals("FPE") || operation.equals("FF1")) {
                    int skippedLine = 0;
                    int unmatchedLine = 0;

                    try {
                        byteContent = Files.readAllBytes(Paths.get(plainInputFile));
                        fileUtfMode = checkEncodingBOM(byteContent);
                        String selUtfMode = inputUtfMode != null ? inputUtfMode : fileUtfMode;

                        FileInputStream fis = new FileInputStream(plainInputFile);
                        InputStreamReader isr = new InputStreamReader(fis, Charset.forName(selUtfMode));
                        BufferedReader br = new BufferedReader(isr);

                        String line;
                        while ((line = br.readLine()) != null) {
                            plainText = line.replaceAll("[\n\r]", "");
                            if(plainText.length() >= 2) {
                                if(utfMode.equals("ASCII")) {
                                    plainBytes = plainText.getBytes();
                                }
                                else {
                                    baos.reset();
                                    plainBytes = plainText.getBytes(Charset.forName(selUtfMode));
                                    plainBytes = removeUTFBOM(plainBytes, getUtfMode(selUtfMode));

                                    plainText = new String(plainBytes, Charset.forName(selUtfMode));

                                    for (char c : plainText.toCharArray()) {
                                        bta = new String( new char[] {c}).getBytes(utfMode);

                                        bta = removeUTFBOM(bta, 3);
                                        len = bta.length;
                                        btBuf = ByteBuffer.allocate(len);
                                        btBuf.order(btOrder);

                                        if (btMode == 4 || btMode == 5) {
                                            btBuf.asIntBuffer().put(c);
                                        }
                                        else if(btMode == 1) {
                                            btBuf = ByteBuffer.wrap(bta).order(btOrder);
                                        }
                                        else {
                                            btBuf.asCharBuffer().put(c);
                                        }
                                        baos.write(btBuf.array());
                                    }

                                    plainBytes = baos.toByteArray();
                                }

                                System.out.println("\nPlainText: " + plainText);
                                decryptedBytes = encryptDecryptBuf(session, encMech, new long[]{keyID}, plainBytes, encryptedOutFS, utfMode);
                                decryptedText = new String(decryptedBytes, Charset.forName(utfMode));

                                if (plainText.equals(decryptedText)) {
                                    System.out.println("=== plainText and decryptedTextStr are equal !!!===");
                                } else {
                                    unmatchedLine++;
                                    System.out.println("=== plainText and decryptedTextStr are NOT equal ===");
                                }

                                if (decryptedWriter != null) {
                                    decryptedWriter.write(decryptedText);
                                    decryptedWriter.append(System.lineSeparator());
                                }
                            }
                            else {
                                System.out.println("FPE and FF1 modes only supports input lengths >= 2.");
                                skippedLine++;
                                if (decryptedWriter != null) {
                                    decryptedWriter.append(System.lineSeparator());
                                }
                                continue;
                            }
                        }
                        System.out.println("Skipped Line Count = "+skippedLine);
                        System.out.println("Unmatched Error Line Count = "+unmatchedLine);

                    } catch (Exception ex) {
                        ex.printStackTrace();
                    }
                }
                else {
                    InputStream inputFS = new FileInputStream(inputFile);
                    int bytesLen = inputFS.available();
                    plainBytes = new byte[bytesLen];

                    inputFS.read(plainBytes);
                    plainText = new String(plainBytes);

                    decryptedBytes = encryptDecryptBuf(session, encMech, new long[]{keyID}, plainBytes, encryptedOutFS, utfMode);
                    decryptedText = new String(decryptedBytes);

                    if(decryptedWriter != null) {
                        decryptedWriter.write(decryptedText);
                    }
                }
            }
            else {
                plainBytes = plainTextInp.getBytes();

                if(bAsymKey == true) {
                    decryptedBytes = encryptDecryptBuf(session, encMech, new long[]{publickeyID, privatekeyID}, plainBytes, encryptedOutFS, utfMode);
                }
                else {
                    decryptedBytes = encryptDecryptBuf(session, encMech, new long[]{keyID}, plainBytes, encryptedOutFS, utfMode);
                }
                decryptedText = new String(decryptedBytes, utfMode);

                if(decryptedWriter != null)
                    decryptedWriter.write(decryptedText);
            }

		    /* Delete the key */
	        /*	session.p11.C_DestroyObject (session.sessionHandle, keyID);
		    System.out.println ("Successfully deleted key"); */

            Helper.closeDown(session);
            System.out.println("End EncryptDecryptMessage.");
            encryptedOutFS.flush();
            encryptedOutFS.close();

            if(decryptedWriter != null) {
                decryptedWriter.flush();
                decryptedWriter.close();
            }

        } catch (Exception e) {
                e.printStackTrace();
        }
    }

        public static byte[]  encryptDecryptBuf(Vpkcs11Session session, CK_MECHANISM encMech, long[] keyIDArr, byte[] plainBytes, OutputStream encryptedOutFS, String utfMode)
        {
            try {
                byte[] encryptedText;
                byte[] decryptedBytes;
                byte[] decryptedData;
                long encryptedDataLen = 0;
                int decryptedDataLen = 0;
                byte[] outText = {};
                long publickeyID = 0;
                long privatekeyID = 0;
                boolean bAsymKey = false;
                int tagLen = 12;

                long keyID = 0;
                if(keyIDArr.length == 1) {
                    keyID = keyIDArr[0];
                }
                else if (keyIDArr.length == 2){
                    publickeyID = keyIDArr[0];
                    privatekeyID = keyIDArr[1];
                    bAsymKey = true;
                }

                int plainBytesLen = plainBytes.length;
                System.out.println("plaintext byte length: " + plainBytesLen);

                if(bAsymKey == true)
                    session.p11.C_EncryptInit(session.sessionHandle, encMech, publickeyID);
                else
                    session.p11.C_EncryptInit(session.sessionHandle, encMech, keyID);
                System.out.println("C_EncryptInit success.");

                encryptedDataLen = session.p11.C_Encrypt(session.sessionHandle, plainBytes, 0, plainBytesLen, outText, 0, 0);
                System.out.println("C_Encrypt success. Encrypted data len = " + encryptedDataLen);

                encryptedText = new byte[Math.toIntExact(encryptedDataLen)];
                encryptedDataLen = session.p11.C_Encrypt(session.sessionHandle, plainBytes, 0, plainBytesLen, encryptedText, 0, encryptedDataLen);
                System.out.println("C_Encrypt 2nd call succeed. Encrypted data len = " + encryptedDataLen);
                if(encMech.mechanism == PKCS11Constants.CKM_AES_GCM) {
                	byte[] temp = new byte[Math.toIntExact(encryptedDataLen)];
                	System.arraycopy(encryptedText, Math.toIntExact(encryptedDataLen)-tagLen , temp, 0, tagLen);
                	System.arraycopy(encryptedText, 0, temp, tagLen, Math.toIntExact(encryptedDataLen)-tagLen);
                	encryptedText =temp;
                	
                }

                System.out.println("Encrypted Text =  " + new String(encryptedText, Charset.forName(utfMode)));
                encryptedOutFS.write(encryptedText, 0, Math.toIntExact(encryptedDataLen));

                if(bAsymKey == true)
                    session.p11.C_DecryptInit(session.sessionHandle, encMech, privatekeyID);
                else
                    session.p11.C_DecryptInit(session.sessionHandle, encMech, keyID);
                System.out.println("C_DecryptInit success.");

                decryptedDataLen = session.p11.C_Decrypt(session.sessionHandle, encryptedText, 0, Math.toIntExact(encryptedDataLen), outText, 0, 0);
                System.out.println("C_Decrypt success. Decrypted data length = " + decryptedDataLen);

                decryptedData = new byte[decryptedDataLen];
                decryptedDataLen = session.p11.C_Decrypt(session.sessionHandle, encryptedText, 0, Math.toIntExact(encryptedDataLen), decryptedData, 0, decryptedDataLen);
                System.out.println("C_Decrypt 2nd call succeed. Decrypted data length = " + decryptedDataLen);

                decryptedBytes = new byte[decryptedDataLen];
                System.arraycopy(decryptedData, 0, decryptedBytes, 0, decryptedDataLen);

                String decryptedTextStr = new String(decryptedBytes, Charset.forName(utfMode));

                System.out.println("Decrypted Text = " + decryptedTextStr);

                return decryptedBytes;

            } catch (PKCS11Exception e) {
                e.printStackTrace();
            } catch (Exception ex) {
                ex.printStackTrace();
            }
            return null;
        }
}
