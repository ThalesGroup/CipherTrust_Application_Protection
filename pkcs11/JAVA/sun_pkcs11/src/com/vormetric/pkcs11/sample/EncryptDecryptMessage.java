package com.vormetric.pkcs11.sample;

import static sun.security.pkcs11.wrapper.PKCS11Constants.CKM_AES_CBC;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKM_AES_CBC_PAD;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKM_AES_CTR;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKM_RSA_PKCS;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKM_RSA_PKCS_KEY_PAIR_GEN;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKO_PRIVATE_KEY;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKO_PUBLIC_KEY;

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
 * 3. Creating a symmetric key on the Data Security Manager
 * 4. Using the symmetric key to encrypt plaintext
 * 5. Using the symmetric key to decrypt ciphertext.
 * 6, Delete key.
 * 7. Clean up.
 */
import java.io.BufferedReader;
import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import javax.xml.bind.DatatypeConverter;

import sun.security.pkcs11.wrapper.CK_MECHANISM;
import sun.security.pkcs11.wrapper.PKCS11Exception;



public class EncryptDecryptMessage {

    public static final byte[] iv = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x10, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F};
    public static final byte[] UTF8_BOM = { (byte)0xef, (byte)0xbb, (byte)0xbf };

    public static final byte[] UTF16BE_BOM = { (byte)0xfe, (byte)0xff };
    public static final byte[] UTF16LE_BOM = { (byte)0xff, (byte)0xfe };

    public static final byte[] UTF32BE_BOM = { 0x00, 0x00, (byte)0xfe, (byte)0xff };
    public static final byte[] UTF32LE_BOM = { (byte)0xff, (byte)0xfe, 0x00, 0x00 };

    public static final String plainTextInp = "Plain text message to be encrypted. Must be multiple of 16 bytes in order to support all ciphers";

    static void usage()
    {
        System.out.println("usage: java com.vormetric.pkcs11.sample.EncryptDecryptMessage -p pin [-k keyName] [-m module] [-o operation] [-L leftMost] [-R rightMost]");
        System.out.println("       [-f 'inputtokenfile'] {[-c 'char set']|[-r 'charset file']|[-l 'literal charset file']} [-u utf-mode-name] [-d 'decryptedfile'] [-g genAction] [-ls lifespan] [-h headermode] [-t tweakStr] [-iu input utf-mode-name]");
        System.out.println("-p: Username:Password of Keymanager");
        System.out.println("-m: Path of directory where dll is deployed/installed");
        System.out.println("-k: Keyname on Keymanager");
        System.out.println("-f: Input file path for plainText ");
        System.out.println("-L: Number of characters from left "); 
        System.out.println("-R: Number of characters from right"); 
        System.out.println("-c: Charset "); 
        System.out.println("-r: File path of charset"); 
        System.out.println("-l: Literal charset file"); 
        System.out.println("-d: Decrypted file path");
        System.out.println("-ls: Lifespan");
        System.out.println("-o: Operation {CTR | CBC_PAD (default) | CBC | FPE | FF1} "); 
        System.out.println("-u: Utf-mode-name is one of ASCII, UTF-8, UTF-16LE, UTF-16BE, UTF-32LE, UTF-32BE");
        System.out.println("-g: GenAction is one of 0 (generate versioned key) or 3 (generate non-versioned key)");
        System.out.println("-h: v1.5, v1.5base64, v2.1, or v2.7");
	System.out.println("-t: tweak string");
	System.out.println("-iu: input utf-mode-name");
		
        System.exit (1);
    }
    public static ByteOrder getSelByteOrder(String strMode) {
        ByteOrder selByteOrder = ByteOrder.nativeOrder();
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
        if  (strMode.equalsIgnoreCase("UTF-8"))
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
        else if(bta[0] == UTF16LE_BOM[0] && bta[1] == UTF16LE_BOM[1])
            strMode = "UTF-16LE";
        else if(bta[0] == UTF16BE_BOM[0] && bta[1] == UTF16BE_BOM[1])
            strMode = "UTF-16";
        else if( bta[0] == UTF32LE_BOM[0] && bta[1] == UTF32LE_BOM[1] &&
                bta[2] == UTF32LE_BOM[2] && bta[3] == UTF32LE_BOM[3] )
            strMode = "UTF-32LE";
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

    public static void main ( String[] args) throws Exception {
        String pin = null;
        String libPath = null;
        String operation = "CBC_PAD";
        String encryptedOutFile = "encryptedOut.txt";
        String plainInputFile = null;
        String decryptedOutFile = null;
        String charSetStr = null;
        String tweakStr = null;
        String charSetInputFile = null;
        String utfMode = "ASCII";
        String headerMode = "";
        String maskStr = "";
        long headerEnc = 0;
        long headerDec = 0;
        char charSetChoc = '\0';
        byte[] charSet;
        byte[] tweakSet = {0x07, 0x06, 0x05, 0x04, 0x03, 0x02, 0x01, 0x00};
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        String keyName = "pkcs11_java_test_key";
        FileWriter decryptedWriter = null;
        FileWriter encryptedWriter = null;
        String fileUtfMode = "ASCII";
        String inputUtfMode = null;
        int genAction = 3;
        int leftMost = 0;  // reserve leftmost characters not encrypted (excluding filtered char)
        int rightMost = 0; // reserve righttmost characters not encrypted (excluding filtered char)
        int left = 0;  // reserve leftmost characters not encrypted (including filtered char)
        int right = 0; // reserve righttmost characters not encrypted (including filtered char)
        
        CK_MECHANISM encMechFpe = null;
        CK_MECHANISM decMechFpe = null;
        CK_MECHANISM encMech = null;
        CK_MECHANISM decMech = null;
        Vpkcs11Session session = null;
        boolean bAsymKey = false;
        int lifespan = 0;
        
        if (args.length == 0) {
            usage();
            System.exit(0);
        }

        for (int i = 0; i < args.length; i += 2) {
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
            else if (args[i].equals("-h")) headerMode = args[i + 1];
            else if (args[i].equals("-L")) leftMost = Integer.parseInt(args[i + 1]);
            else if (args[i].equals("-R")) rightMost = Integer.parseInt(args[i + 1]);
            else usage();
        }
        if(utfMode == null) utfMode = "ASCII";

        if(headerMode.equals("v1.5")) {
          headerEnc = Helper.CKM_THALES_V15HDR | Helper.CKM_VENDOR_DEFINED;
          headerDec = Helper.CKM_THALES_ALLHDR | Helper.CKM_VENDOR_DEFINED;
        } else if (headerMode.equals("v1.5base64")) {
          headerEnc = Helper.CKM_THALES_V15HDR | Helper.CKM_THALES_BASE64 | Helper.CKM_VENDOR_DEFINED;
          headerDec = Helper.CKM_THALES_ALLHDR | Helper.CKM_THALES_BASE64 | Helper.CKM_VENDOR_DEFINED;
        } else if (headerMode.equals("v2.1")) {
          headerEnc = Helper.CKM_THALES_V21HDR | Helper.CKM_VENDOR_DEFINED;
          headerDec = Helper.CKM_THALES_ALLHDR | Helper.CKM_VENDOR_DEFINED;
        } else if (headerMode.equals("v2.7")) {
          headerEnc = Helper.CKM_THALES_V27HDR | Helper.CKM_VENDOR_DEFINED;
          headerDec = Helper.CKM_THALES_ALLHDR | Helper.CKM_VENDOR_DEFINED;
        }

        try {
            System.out.println("Start EncryptDecryptMessage ...");
            session = Helper.startUp(Helper.getPKCS11LibPath(libPath), pin);

            File encryptedFile = new File(encryptedOutFile);
            encryptedWriter = new FileWriter(encryptedFile);

            if(decryptedOutFile != null)
                decryptedWriter = new FileWriter(decryptedOutFile);

            String plainText, decryptedText;
            byte[] byteContent;
            byte[] plainBytes;
            byte[] decryptedBytes;
            byte[] bta;
            long keyID = 0;
            long[] keyIDArr = null;
            char[] chars;
            int i, len, plainBytesLen;
            String strContent;
            int radix = 0;
            ByteBuffer btBuf;
            long publickeyID = 0;
            long privatekeyID = 0;

            ByteOrder btOrder = getSelByteOrder(utfMode);
            byte btMode = getUtfMode(utfMode);

            if (operation.equals("CTR")) {
                System.out.println("CTR mode selected");
                encMech = new CK_MECHANISM(headerEnc | CKM_AES_CTR, iv);
                decMech = new CK_MECHANISM(headerDec | CKM_AES_CTR, iv);
            }
            else if (operation.equals("RSA")){
                System.out.println("RSA mode selected");
                encMech = new CK_MECHANISM(CKM_RSA_PKCS);
                decMech = new CK_MECHANISM(CKM_RSA_PKCS);
                bAsymKey = true;
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
                            strContent = strContent.replaceAll("[\n\r]", "");

                            baos.reset();
                            List cpLists = new ArrayList();
                            chars = strContent.toCharArray();
                            Arrays.sort(chars);

                            for (char c : chars) {
                                if(!cpLists.contains(c))
                                    cpLists.add(c);
                                else
                                    continue;

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

                        List cpLists = new ArrayList();

                        try {
                            baos.reset();
                            for (String t : tokens) {
                                dashid = t.indexOf('-');
                                if (dashid != -1) {
                                    rstart = Integer.valueOf(t.substring(0, dashid).trim(), 16);
                                    rend = Integer.valueOf(t.substring(dashid + 1).trim(), 16);

                                    for (rcp = rstart; rcp <= rend; rcp++) {
                                        if(!cpLists.contains(rcp))
                                            cpLists.add(rcp);
                                    }
                                } else {
                                    rcp = Integer.valueOf(t.trim(), 16);

                                    if(!cpLists.contains(rcp))
                                        cpLists.add(rcp);
                                }
                            }

                            Collections.sort(cpLists);

                            for (Object icode : cpLists) {
                                rcp = ((Integer)icode).intValue();
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
                                else {
                                    btBuf = ByteBuffer.wrap(bta).order(btOrder);
                                    for (char c : chars)
                                        radix++;
                                }
                                baos.write(btBuf.array());
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
                    // charset str read from stdin must be sorted!
                    charSet = charSetStr != null ? charSetStr.getBytes() : baos.toByteArray();
                    // Need to evaluate charset lenght otherwise there are cases where it will be 0
                    // ie using default charset "0123456789"
                    radix = charSet.length;
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
                        // tweak + radix + charset len need to fit fpeIVBytes
                        if (tweakStr != null){ 
                            tweakSet = DatatypeConverter.parseHexBinary(tweakStr);
                        }
                        fpeIVBytes = new ByteArrayOutputStream(tweakSet.length + 1 + charSet.length);
                        dos = new DataOutputStream(fpeIVBytes);
                        dos.write(tweakSet, 0, tweakSet.length);
                        dos.write((charSet != null ? charSet.length : 1) & 0xFF);
                      }
                      else {
                        fpeIVBytes = new ByteArrayOutputStream(16 + charSet.length);
                        dos = new DataOutputStream(fpeIVBytes);
                        dos.write(tweakSet, 0, 8);
                        // This byte must set to 1
                        dos.write(1 & 0xFF);
                        // 1...UTF8, 2...UTF16LE, 3...UTF16BE, 4...UTF32LE, 5...UTF32BE */
                        dos.write(btMode & 0xFF);

                        btBuf = ByteBuffer.allocate(2);
                        btBuf.order(ByteOrder.BIG_ENDIAN).putShort((short) (radix & 0xFFFF));
                        dos.write(btBuf.array());
                        btBuf = ByteBuffer.allocate(4);
                        btBuf.order(ByteOrder.BIG_ENDIAN).putInt(charSet.length);
                        dos.write(btBuf.array());
                    }
                    System.out.printf( "tweakSet :0x%s\n", DatatypeConverter.printHexBinary( tweakSet ));
                    dos.write(charSet, 0, charSet.length);
                    dos.flush();
                    encMechFpe = new CK_MECHANISM(Helper.CKM_THALES_FPE, fpeIVBytes.toByteArray());
                    decMechFpe = encMechFpe;
                }
                else if(operation.equals("FF1")) {
                    if (tweakStr != null){ 
                        tweakSet = DatatypeConverter.parseHexBinary(tweakStr);
                    }
                    System.out.printf( "tweakSet :0x%s\n", DatatypeConverter.printHexBinary( tweakSet ));
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

                    encMechFpe = new CK_MECHANISM(Helper.CKM_THALES_FF1, fpeIVBytes.toByteArray());
                    decMechFpe = encMechFpe;
                }
                encMech = encMechFpe; /* also used for FF1 */
                decMech = decMechFpe;
            } else if (operation.equals("CBC")) {
                System.out.println("CBC mode selected");
                encMech = new CK_MECHANISM (headerEnc | CKM_AES_CBC, iv);
                decMech = new CK_MECHANISM (headerDec | CKM_AES_CBC, iv);
            } else {
                System.out.println("CBC PAD mode selected");
                encMech = new CK_MECHANISM(headerEnc | CKM_AES_CBC_PAD, iv);
                decMech = new CK_MECHANISM(headerDec | CKM_AES_CBC_PAD, iv);
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
                    
                    BufferedReader br = null;
                    try {
                        byteContent = Files.readAllBytes(Paths.get(plainInputFile));
                        fileUtfMode = checkEncodingBOM(byteContent);
                        String selUtfMode = inputUtfMode != null ? inputUtfMode : fileUtfMode;

                        FileInputStream fis = new FileInputStream(plainInputFile);
                        InputStreamReader isr = new InputStreamReader(fis, Charset.forName(selUtfMode));
                        br = new BufferedReader(isr);

                        String line;
                        while ((line = br.readLine()) != null) {
                            plainText = line.replaceAll("[\n\r]", "");
                            if(plainText.length() >= 2) {
                                
                                System.out.println("\nPlainText: " + plainText);
                                System.out.println("charSetStr: " + charSetStr);
                                System.out.println("leftMost: " + leftMost);
                                System.out.println("rightMost: " + rightMost +"\n");

                                maskStr = new String(plainText);

                                int cnt = 0;
                                while (cnt < leftMost && left < maskStr.length()) {
                                    char c = maskStr.charAt(left);
                                    if (charSetStr.indexOf(c) >= 0) {
                                        cnt++;
                                    }
                                    left++;
                                }
                                
                                cnt = 0;
                                while (cnt < rightMost && right < maskStr.length()) {
                                    char c = maskStr.charAt(maskStr.length()-right-1);
                                    if (charSetStr.indexOf(c) >= 0) {
                                        cnt++;
                                    }
                                    right++;
                                }
                                
                                // filter out char not in charSetStr.
                                StringBuilder newPlainText = new StringBuilder();
                                if (leftMost < 0 || rightMost < 0 
                                                 || leftMost > plainText.length() 
                                                 || rightMost > plainText.length() 
                                                 || left+right > plainText.length()){
                                    System.out.println("Error: Invalid leftMost or rightMost.\n");
                                    System.exit(1);
                                }

                                if(charSetStr!=null) {
                                    for (int k = left; k < plainText.length() - right; k++) {
                                        char c = plainText.charAt(k);
                                        if (charSetStr.indexOf(c) >= 0) {
                                            newPlainText.append(c);
                                        }
                                    }
                                    plainText = newPlainText.toString();
                                }

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

                                decryptedBytes = encryptDecryptBuf(session, encMech, decMech, new long[]{keyID}, 
                                                                   plainBytes, encryptedWriter, utfMode,
                                                                   left, right, maskStr, charSetStr);
                                decryptedText = new String(decryptedBytes, Charset.forName(utfMode));
                                
                                // reconstruct decrypted message to compare with original message (maskStr)
                                if (maskStr.length() > decryptedText.length()) {
                                    StringBuilder newDecryptedText = new StringBuilder();
                                    int m = 0;
                                    int d = 0;
                                    while (m < maskStr.length()){
                                        char c = maskStr.charAt(m);
                                        if (m >= left && m < maskStr.length()-right 
                                                      && charSetStr.indexOf(c) >= 0 
                                                      && d < decryptedText.length()) {
                                            newDecryptedText.append(decryptedText.charAt(d));
                                            d++;
                                        } else {
                                            newDecryptedText.append(c);
                                        }
                                        m++;
                                    } 
                                    decryptedText = newDecryptedText.toString();
                                    System.out.println("Reconstructed Decrypted Text = " + decryptedText);
                                }
                                
                                if (maskStr.equals(decryptedText)) {
                                    System.out.println("=== plainText and decryptedTextStr are equal !!!===");
                                } else {
                                    unmatchedLine++;
                                    System.out.println("=== plainText and decryptedTextStr are NOT equal ===");
                                }

                                if(encryptedWriter != null)
                                    encryptedWriter.append(System.lineSeparator());

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
                                if(encryptedWriter != null)
                                    encryptedWriter.append(System.lineSeparator());
                                continue;
                            }
                        }
                        System.out.println("Skipped Line Count = "+skippedLine);
                        System.out.println("Unmatched Error Line Count = "+unmatchedLine);

                    } catch (Exception ex) {
                        ex.printStackTrace();
                    } finally {
                    	try {
                        	if(br!=null) br.close();
                        	}
                    	catch(IOException e) {}
                    }
                }
                else {
                    InputStream inputFS = new FileInputStream(inputFile);
                    int bytesLen = inputFS.available();
                    plainBytes = new byte[bytesLen];

                    plainBytesLen = inputFS.read(plainBytes);
                    plainText = new String(plainBytes);

                    decryptedBytes = encryptDecryptBuf(session, encMech, decMech, new long[]{keyID}, 
                                                       plainBytes, encryptedWriter, utfMode,
                                                       left, right, maskStr, charSetStr);
                    decryptedText = new String(decryptedBytes);

                    if(encryptedWriter != null)
                        encryptedWriter.append(System.lineSeparator());
                    if(decryptedWriter != null) {
                        decryptedWriter.write(decryptedText);
                    }
                    try{
                      	if(inputFS!=null) inputFS.close();
                    }
                    catch(IOException e) {}
                }
            }
            else {
                plainBytes = plainTextInp.getBytes();

                if(bAsymKey == true) {
                    decryptedBytes = encryptDecryptBuf(session, encMech, decMech, new long[]{publickeyID, privatekeyID}, 
                                                       plainBytes, encryptedWriter, utfMode, left, right, maskStr, charSetStr);
                }
                else {
                    decryptedBytes = encryptDecryptBuf(session, encMech, decMech, new long[]{keyID}, 
                                                       plainBytes, encryptedWriter, utfMode,
                                                       left, right, maskStr, charSetStr);
                }
                decryptedText = new String(decryptedBytes, utfMode);

                if (plainTextInp.equals(decryptedText)) {
                    System.out.println("=== plainText and decryptedTextStr are equal !!!===");
                } else {
                    System.out.println("=== plainText and decryptedTextStr are NOT equal !! ===");
                }

                if(decryptedWriter != null)
                    decryptedWriter.write(decryptedText);
            }

            if(decryptedWriter != null) {
                decryptedWriter.flush();
                decryptedWriter.close();
            }

            encryptedWriter.flush();
            encryptedWriter.close();

            /* Delete the key */
	        /*	session.p11.C_DestroyObject (session.sessionHandle, keyID);
		    System.out.println ("Successfully deleted key"); */

        } catch (Exception e) {
                e.printStackTrace();
                System.out.println("The Cause is " + e.getMessage() + ".");
                throw e;
        }
        finally {
            Helper.closeDown(session);
            System.out.println("End EncryptDecryptMessage.");
        }
    }

        public static byte[]  encryptDecryptBuf(Vpkcs11Session session, 
                                                CK_MECHANISM encMech, 
                                                CK_MECHANISM decMech, 
                                                long[] keyIDArr, 
                                                byte[] plainBytes, 
                                                FileWriter encryptedWriter,
                                                String utfMode,
                                                int left,
                                                int right,
                                                String maskStr,
                                                String charSetStr)
        {
            try {
                byte[] encryptedText;
                byte[] encryptedBytes;
                byte[] decryptedBytes;
                byte[] decryptedData;
                int encryptedDataLen = 0;
                int decryptedDataLen = 0;
                byte[] outText = {};
                long publickeyID = 0;
                long privatekeyID = 0;
                boolean bAsymKey = false;

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
                System.out.println("PlainText to be encrypted: "+new String(plainBytes));
                System.out.println("Plaintext byte length: " + plainBytesLen);

                if(bAsymKey == true)
                    session.p11.C_EncryptInit(session.sessionHandle, encMech, publickeyID);
                else
                    session.p11.C_EncryptInit(session.sessionHandle, encMech, keyID);

                System.out.println("C_EncryptInit success.");

                encryptedDataLen = session.p11.C_Encrypt(session.sessionHandle, plainBytes, 0, plainBytesLen, outText, 0, 0);
                System.out.println("C_Encrypt success. Encrypted data len = " + encryptedDataLen);

                encryptedText = new byte[encryptedDataLen];
                encryptedDataLen = session.p11.C_Encrypt(session.sessionHandle, plainBytes, 0, plainBytesLen, encryptedText, 0, encryptedDataLen);
                System.out.println("C_Encrypt 2nd call succeed. Encrypted data len = " + encryptedDataLen);

                encryptedBytes = new byte[encryptedDataLen];
                System.arraycopy(encryptedText, 0, encryptedBytes, 0, encryptedDataLen);
                String encryptedTextStr = new String(encryptedBytes, Charset.forName(utfMode));
                
                // keep cipher string same format as plaintext
                if (maskStr.length() > encryptedTextStr.length()) {
                    StringBuilder newEncryptedTextStr = new StringBuilder();
                    int m = 0;
                    int d = 0;
                    while (m < maskStr.length()){
                        char c = maskStr.charAt(m);
                        if (m >= left && m < maskStr.length()-right
                                          && charSetStr.indexOf(c) >= 0 
                                          && d < encryptedTextStr.length()) {
                            newEncryptedTextStr.append(encryptedTextStr.charAt(d));
                            d++;
                        } else {
                            newEncryptedTextStr.append(c);
                        }
                        m++;
                    } 
                    encryptedTextStr = newEncryptedTextStr.toString();
                }
                
                System.out.println("Encrypted Text =  " + encryptedTextStr);
                encryptedWriter.write(encryptedTextStr);

                if(bAsymKey == true)
                    session.p11.C_DecryptInit(session.sessionHandle, decMech, privatekeyID);
                else
                    session.p11.C_DecryptInit(session.sessionHandle, decMech, keyID);
                System.out.println("C_DecryptInit success.");

                decryptedDataLen = session.p11.C_Decrypt(session.sessionHandle, encryptedBytes, 0, encryptedDataLen, outText, 0, 0);
                System.out.println("C_Decrypt success. Decrypted data length = " + decryptedDataLen);

                decryptedData = new byte[decryptedDataLen];
                decryptedDataLen = session.p11.C_Decrypt(session.sessionHandle, encryptedBytes, 0, encryptedDataLen, decryptedData, 0, decryptedDataLen);
                System.out.println("C_Decrypt 2nd call succeed. Decrypted data length = " + decryptedDataLen);

                decryptedBytes = new byte[decryptedDataLen];
                System.arraycopy(decryptedData, 0, decryptedBytes, 0, decryptedDataLen);

                String decryptedTextStr = new String(decryptedBytes, Charset.forName(utfMode));
                String plainTextStr = new String(plainBytes, Charset.forName(utfMode));

                System.out.println("Decrypted Text = " + decryptedTextStr);

                return decryptedBytes;

            } catch (PKCS11Exception e) {
                e.printStackTrace();
                System.out.println("The Cause is " + e.getMessage() + ".");
                throw e;
            } catch (Exception ex) {
                ex.printStackTrace();
                System.out.println("The Cause is " + ex.getMessage() + ".");
                throw ex;
            }
            return null;
        }
}
