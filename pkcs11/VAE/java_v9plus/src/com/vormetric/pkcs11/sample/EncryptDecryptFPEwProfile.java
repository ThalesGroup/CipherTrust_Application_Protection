package com.vormetric.pkcs11.sample;

import java.io.*;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Paths;
import com.vormetric.pkcs11.util.VaeProfile;

public class EncryptDecryptFPEwProfile {

    static String defaultProfileName = "default";

    static void usage()
    {
        System.out.println("usage: java com.vormetric.pkcs11.sample.EncryptDecryptFPEwProfile -p pin [-m module] [-f profileFilePath]");
        System.out.println("       [-i 'inputFilePath'] [-d 'decryptedFile'] [-pn profileName]");
        System.exit (1);
    }

    public static void main ( String[] args) {
        String pin = null;
        String libPath = null;

        String encryptedOutFile = "encryptedOut.txt";
        String propertiesInputFile = null;
        String decryptedOutFile = null;
        String plainInputFile = null;

        String plainText = "This is plain text!";
        String cipherText = null;
        String decryptedText = null;

        FileWriter decryptedWriter = null;
        FileWriter encryptedWriter = null;
        String fileUtfMode = "ASCII";
        String inputUtfMode = null;
        String profileName = null;

        byte[] tweak = {0x07, 0x06, 0x05, 0x04, 0x03, 0x02, 0x01, 0x00};

        Vpkcs11Session session = null;

        if (args.length == 0) {
            usage();
            System.exit(0);
        }

        for (int i = 0; i < args.length; i += 2) {
            if      (args[i].equals("-p")) pin = args[i + 1];
            else if (args[i].equals("-m")) libPath = args[i + 1];
            else if (args[i].equals("-pn")) profileName = args[i + 1];
            else if (args[i].equals("-i")) plainInputFile = args[i + 1];
            else if (args[i].equals("-f")) propertiesInputFile = args[i + 1];
            else if (args[i].equals("-iu")) inputUtfMode = args[i + 1];
            else if (args[i].equals("-d")) decryptedOutFile = args[i + 1];

            else usage();
        }

        try {
            System.out.println("Start EncryptDecryptFPEwProfile ...");
            session = Helper.startUp(Helper.getPKCS11LibPath(libPath), pin);

            if (profileName == null) profileName = defaultProfileName;
            VaeProfile vaeprof = new VaeProfile(session.p11, session.sessionHandle, propertiesInputFile);

            vaeprof.initProperties();
            vaeprof.loadProfile(profileName);

            if (plainInputFile == null) {

                cipherText = vaeprof.encryptFpe(plainText);
                decryptedText = vaeprof.decryptFpe(cipherText);

                if (plainText.equals(decryptedText))
                    System.out.println("=== plainText and decryptedText are equal !===");
                else
                    System.out.println("=== plainText and decryptedText are NOT equal !!!===");
            } else {
                File encryptedFile = new File(encryptedOutFile);
                OutputStream encryptedOutFS = new FileOutputStream(encryptedFile);
                encryptedWriter = new FileWriter(encryptedFile);

                if (decryptedOutFile != null)
                    decryptedWriter = new FileWriter(decryptedOutFile);

                File inputFile = new File(plainInputFile);

                int skippedLine = 0;
                int unmatchedLine = 0;

                byte[] byteContent = Files.readAllBytes(Paths.get(plainInputFile));
                fileUtfMode = vaeprof.checkEncodingBOM(byteContent);
                String selUtfMode = inputUtfMode != null ? inputUtfMode : fileUtfMode;

                FileInputStream fis = new FileInputStream(plainInputFile);
                InputStreamReader isr = new InputStreamReader(fis, Charset.forName(selUtfMode));
                BufferedReader br = new BufferedReader(isr);

                String line;
                while ((line = br.readLine()) != null) {
                    plainText = line.replaceAll("[\n\r]", "");
                    decryptedText = null;

                    if(plainText!=null)
                        cipherText = vaeprof.encryptFpe(plainText);

                    if (encryptedWriter != null && cipherText!=null) {
                        encryptedWriter.write(cipherText);
                        encryptedWriter.append(System.lineSeparator());

                        decryptedText = vaeprof.decryptFpe(cipherText);
                    }

                    if(decryptedText != null) {
                        if (decryptedText.equals(plainText))
                            System.out.println("=== plainText and decryptedText are equal !!===");
                        else {
                            unmatchedLine++;
                            System.out.println("=== plainText and decryptedText are NOT equal !!===");
                        }

                        if (decryptedWriter != null) {
                            decryptedWriter.write(decryptedText);
                            decryptedWriter.append(System.lineSeparator());
                        }
                    }
                }

                if (decryptedWriter != null) {
                    decryptedWriter.flush();
                    decryptedWriter.close();
                }

                if (encryptedWriter != null) {
                    encryptedWriter.flush();
                    encryptedWriter.close();
                }
            }
        }
        catch (java.io.FileNotFoundException e) {
            e.printStackTrace();
        }
        catch (java.lang.Exception je) {
            je.printStackTrace();
        }
        finally {
            Helper.closeDown(session);
            System.out.println("End EncryptDecryptFPEwProfile.");
        }
    }
}
