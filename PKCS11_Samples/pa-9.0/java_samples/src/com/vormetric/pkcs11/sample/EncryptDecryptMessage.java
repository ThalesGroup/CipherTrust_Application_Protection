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
import java.nio.CharBuffer;
import java.nio.charset.*;
import java.nio.file.*;
import java.security.*;
import java.util.*;

import sun.nio.cs.*;
import sun.security.pkcs11.wrapper.*;
import static sun.security.pkcs11.wrapper.PKCS11Constants.*;
import sun.security.pkcs11.Secmod.*;

public class EncryptDecryptMessage {

	public static final byte[] iv = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x10, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F};
    public static final byte[] UTF8_BOM = { (byte)0xef, (byte)0xbb, (byte)0xbf };

    public static final byte[] UTF16BE_BOM = { (byte)0xfe, (byte)0xff };
    public static final byte[] UTF16LE_BOM = { (byte)0xff, (byte)0xfe };

    public static final byte[] UTF32BE_BOM = { 0x00, 0x00, (byte)0xfe, (byte)0xff };
    public static final byte[] UTF32LE_BOM = { (byte)0xff, (byte)0xfe, 0x00, 0x00 };

	public static final CK_MECHANISM encMechCbcPad = new CK_MECHANISM (CKM_AES_CBC_PAD, iv);
	public static final CK_MECHANISM encMechCtr    = new CK_MECHANISM (CKM_AES_CTR    , iv);
    public static final CK_MECHANISM encMechCbc    = new CK_MECHANISM (CKM_AES_CBC, iv);

    public static final String plainTextInp = "Plain text message to be encrypted.";

    public static void usage()
    {
        System.out.println ("usage: java com.vormetric.pkcs11.sample.EncryptDecryptMessage -p pin [-k keyName] [-m module] [-o operation {CTR | CBC_PAD (default) ");
        System.out.println(" | FPE | FF1 } ] [-f 'inputtokenfile'] ([-c 'char set']|[-r 'charset file']|[-l 'literal charset file']) [-u utf-mode-name] [-d 'decryptedfile']");
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
        if(strMode.equalsIgnoreCase("UTF-8"))
            btmode = 1;
        else if(strMode.equalsIgnoreCase("UTF-16LE"))
            btmode = 2;
        else if(strMode.equalsIgnoreCase("UTF-16"))
            btmode = 3;
        else if(strMode.equalsIgnoreCase("UTF-32LE"))
            btmode = 4;
        else if(strMode.equalsIgnoreCase("UTF-32"))
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
            strMode = "UTF-16";
        else if( bta[0] == UTF32BE_BOM[0] && bta[1] == UTF32BE_BOM[1] &&
                bta[2] == UTF32BE_BOM[2] && bta[3] == UTF32BE_BOM[3] )
            strMode = "UTF-32";
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

    private static byte[] appendUTFBOM(byte[] bta, int btmode)
    {
        byte[] rar = null;
        switch (btmode) {
            case 1:
                rar = new byte[bta.length + 3];
                System.arraycopy(UTF8_BOM, 0, rar, 0, 3);
                System.arraycopy(bta, 0, rar, 3, bta.length);
                break;

            case 2:
                rar = new byte[bta.length + 2];
                System.arraycopy(UTF16LE_BOM, 0, rar, 0, 2);
                System.arraycopy(bta, 0, rar, 2, bta.length);
                break;

            case 3:
                rar = new byte[bta.length + 2];
                System.arraycopy(UTF16BE_BOM, 0, rar, 0, 2);
                System.arraycopy(bta, 0, rar, 2, bta.length);
                break;

            case 4:
                rar = new byte[bta.length + 4];
                System.arraycopy(UTF32LE_BOM, 0, rar, 0, 4);
                System.arraycopy(bta, 0, rar, 4, bta.length);
                break;

            case 5:
                rar = new byte[bta.length + 4];
                System.arraycopy(UTF32BE_BOM, 0, rar, 0, 4);
                System.arraycopy(bta, 0, rar, 4, bta.length);
                break;
        }
        return rar;
    }

    public static void main ( String[] args) {
        String pin = null;
        String libPath = null;
        String initArgs = "";
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
        String keyName = "vpkcs11-java-test-key";
        FileWriter decryptedWriter = null;
        String fileUtfMode = "ASCII";
        String inputUtfMode = null;

        byte[] tweak = {0x07, 0x06, 0x05, 0x04, 0x03, 0x02, 0x01, 0x00};
        CK_MECHANISM encMechFpe = null;
        CK_MECHANISM encMech = null;

        int i;
        for (i = 0; i < args.length; i += 2) {
            if (args[i].equals("-p")) pin = args[i + 1];
            else if (args[i].equals("-m")) libPath = args[i + 1];
            else if (args[i].equals("-o")) operation = args[i + 1];
            else if (args[i].equals("-f")) plainInputFile = args[i + 1];
            else if (args[i].equals("-iu")) inputUtfMode = args[i + 1];
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
            else if (args[i].equals("-d")) decryptedOutFile = args[i + 1];
            else if (args[i].equals("-a")) initArgs = args[i+1];
            else usage();
        }
        if(utfMode == null) utfMode = "ASCII";

        try {
            System.out.println("Start EncryptDecryptMessage ...");
            Vpkcs11Session session = Helper.startUp(Helper.getPKCS11LibPath(libPath), pin, initArgs);

            long keyID = Helper.findKey(session, keyName);

            if (keyID == 0) {
                System.out.println("the key is not found, creating it...");
                keyID = Helper.createKey(session, keyName);
                System.out.println("Key successfully Created. Key Handle: " + keyID);
            } else {
                System.out.println("Key successfully Found. Key Handle: " + keyID);
            }

            File encryptedFile = new File(encryptedOutFile);
            OutputStream encryptedOutFS = new FileOutputStream(encryptedFile);

            if(decryptedOutFile != null)
                decryptedWriter = new FileWriter(decryptedOutFile);

            String plainText, decryptedText;
            byte[] byteContent;
            byte[] plainBytes;
            byte[] decryptedBytes;
            byte[] bta;
            int len, plainBytesLen;
            String strContent;
            int radix = 0;
            ByteBuffer btBuf;
            ByteOrder btOrder = getSelByteOrder(utfMode);
            byte btMode = getUtfMode(utfMode);

            if (operation.equals("CTR")) {
                System.out.println("CTR mode selected");
                encMech = encMechCtr;

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

                        CharBuffer cb;
                        CharsetEncoder encoder = Charset.forName(utfMode).newEncoder();

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

                encMech = encMechFpe;

            } else if (operation.equals("CBC")) {
                System.out.println("CBC mode selected");
                encMech = encMechCbc;
            } else {
                System.out.println("CBC PAD mode selected");
                encMech = encMechCbcPad;
            }

            /* encrypt, decrypt with key */
            if (plainInputFile != null) {
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
                                decryptedBytes = encryptDecryptBuf(session, encMech, keyID, plainBytes, encryptedOutFS, utfMode);
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
                                System.out.println("Fpe mode only supports input length >= 2.");
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

                    plainBytesLen = inputFS.read(plainBytes);
                    plainText = new String(plainBytes);

                    decryptedBytes = encryptDecryptBuf(session, encMech, keyID, plainBytes, encryptedOutFS, utfMode);
                    decryptedText = new String(decryptedBytes);

                    if(decryptedWriter != null) {
                        decryptedWriter.write(decryptedText);
                    }
                }
            } else {
                plainBytes = plainTextInp.getBytes();
                decryptedBytes = encryptDecryptBuf(session, encMech, keyID, plainBytes, encryptedOutFS, utfMode);
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

        public static byte[]  encryptDecryptBuf(Vpkcs11Session session, CK_MECHANISM encMech, long keyID, byte[] plainBytes, OutputStream encryptedOutFS, String utfMode)
        {
            try {
                byte[] encryptedText;
                byte[] decryptedBytes;
                byte[] decryptedData;
                int encryptedDataLen = 0;
                int decryptedDataLen = 0;
                byte[] outText = {};

                int plainBytesLen = plainBytes.length;
                System.out.println("plaintext byte length: " + plainBytesLen);

                session.p11.C_EncryptInit(session.sessionHandle, encMech, keyID);
                System.out.println("C_EncryptInit success.");

                encryptedDataLen = session.p11.C_Encrypt(session.sessionHandle, plainBytes, 0, plainBytesLen, outText, 0, 0);
                System.out.println("C_Encrypt success. Encrypted data len = " + encryptedDataLen);

                encryptedText = new byte[encryptedDataLen];
                encryptedDataLen = session.p11.C_Encrypt(session.sessionHandle, plainBytes, 0, plainBytesLen, encryptedText, 0, encryptedDataLen);
                System.out.println("C_Encrypt 2nd call succeed. Encrypted data len = " + encryptedDataLen);

                System.out.println("Encrypted Text =  " + new String(encryptedText, Charset.forName(utfMode)));
                encryptedOutFS.write(encryptedText, 0, encryptedDataLen);

                session.p11.C_DecryptInit(session.sessionHandle, encMech, keyID);
                System.out.println("C_DecryptInit success.");

                decryptedDataLen = session.p11.C_Decrypt(session.sessionHandle, encryptedText, 0, encryptedDataLen, outText, 0, 0);
                System.out.println("C_Decrypt success. Decrypted data length = " + decryptedDataLen);

                decryptedData = new byte[decryptedDataLen];
                decryptedDataLen = session.p11.C_Decrypt(session.sessionHandle, encryptedText, 0, encryptedDataLen, decryptedData, 0, decryptedDataLen);
                System.out.println("C_Decrypt 2nd call succeed. Decrypted data length = " + decryptedDataLen);

                decryptedBytes = new byte[decryptedDataLen];
                System.arraycopy(decryptedData, 0, decryptedBytes, 0, decryptedDataLen);

                String decryptedTextStr = new String(decryptedBytes, Charset.forName(utfMode));
                String plainTextStr = new String(plainBytes, Charset.forName(utfMode));

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
