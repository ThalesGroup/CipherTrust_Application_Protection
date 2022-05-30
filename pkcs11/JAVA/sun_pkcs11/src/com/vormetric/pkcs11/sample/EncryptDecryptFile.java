package com.vormetric.pkcs11.sample;

import static sun.security.pkcs11.wrapper.PKCS11Constants.CKM_AES_CBC_PAD;

/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/

/*
 ***************************************************************************
 * File: EncryptDecryptFile.java
 ***************************************************************************
 ***************************************************************************
 * This sample demonstrates the following
 * 1. Initialization
 * 2. Create a connection and logging in.
 * 3. Create a symmetric key on the KeyManager
 * 4. Using the symmetric key to encrypt a file
 * 5. Using the symmetric key to decrypt encrypted file
 * 6. Compare the source file and decrypted file
 * 7, Delete key.
 * 8. Clean up.
 */
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;

import sun.security.pkcs11.wrapper.CK_MECHANISM;
import sun.security.pkcs11.wrapper.PKCS11Exception;


public class EncryptDecryptFile {

	public static final byte[] iv = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x10, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F};
	public static final CK_MECHANISM encMech = new CK_MECHANISM (CKM_AES_CBC_PAD, iv);
    public static final String plainText = "Plain text message to be encrypted.";


    public static void usage()
    {
        System.out.println("usage: java [-cp CLASSPATH] com.vormetric.pkcs11.sample.EncryptDecryptFile -p pin -f inputfile -k keyName [-m module] [-n 0|1] [-g gen_key_action]");
        System.out.println("-p: Username:Password of Keymanager");
        System.out.println("-m: Path of directory where dll is deployed/installed");
        System.out.println("-k: Keyname on Keymanager");
        System.out.println("-f: Input file path for plainText");
        System.out.println("-n 0|1 ... nodelete flag. 0 is the default value and means 'Delete the key.', whereas 1 means 'Do not delete the key.'");
	System.out.println("-g: 0 for versionCreate, 1 for versionRotate, 2 for versionMigrate, 3 for nonVersionCreate");
        System.exit (1);
    }

    public static void main ( String[] args)
    {
        String pin = null;
        String libPath = null;
        String filePath = null;
        String keyName = "pkcs11_java_test_key";
        int nodelete = 0;
		int genAction = 3;
        Vpkcs11Session session = null;
        int needtocreatekey = 0;
  
        if (args.length <= 2) usage();

        for (int i=0; i<args.length; i+=2)
        {
            if (args[i].equals("-p")) pin = args[i+1];
            else if (args[i].equals("-m")) libPath = args[i+1];
            else if (args[i].equals("-k")) keyName = args[i+1];
            else if (args[i].equals("-f")) filePath = args[i+1];
            else if (args[i].equals("-g")) genAction = Integer.parseInt(args[i + 1]);
            else if (args[i].equals("-n")) nodelete  = Integer.parseInt(args[i + 1]);
            else usage();
        }

        // if file does not exist, exit
        if ( !Helper.isFileExist(filePath))
        {
            System.out.println("The input file: " + filePath + " does NOT exist!");
            usage();
        }

        String cipherFile = filePath + ".enc";
        String decryptedFile = filePath + ".dec";

		try
	    {
            System.out.println ("Start EncryptDecryptFile ..." );
            session = Helper.startUp(Helper.getPKCS11LibPath(libPath), pin);

            long keyID = Helper.findKey(session, keyName) ;

            if (keyID == 0)
            {
                System.out.println ("the key is not found, creating it..." );
                needtocreatekey = 1;
            }
            else
            {
              if (nodelete == 0) {
                // clean up existing key
                Helper.setKeyState (session, keyID, Helper.KeyState.Deactivated);
			    session.p11.C_DestroyObject (session.sessionHandle, keyID);
                needtocreatekey = 1;
              }
            }

            if (needtocreatekey == 1) {
              // create a new test key to make sure cached on host attribute is set to ON.
              keyID = Helper.createKey(session, keyName, genAction, 0);
            }

			/* encrypt, decrypt with key */
            int bufferSize = 1008;
            // make sure the output buffer is bigger than the input buffer, with an extra AES_BLOCK_SIZE space
            int outBufferSize = bufferSize +16 ; // AES_BLOCK_SIZE = 16

			byte[] inBuf = new byte[bufferSize];
			byte[] outBuf = new byte [outBufferSize];
			int encryptedDataLen = 0;
            int decryptedDataLen = 0;

			session.p11.C_EncryptInit (session.sessionHandle, encMech, keyID);
			System.out.println ("C_EncryptInit success.");
			File sourceFile = new File(filePath);
            File destFile = new File(cipherFile);

            InputStream in = new FileInputStream(sourceFile);
            OutputStream out = new FileOutputStream(destFile);

            int len = 0;

            while ((len = in.read(inBuf)) > 0)
            {
                encryptedDataLen = session.p11.C_EncryptUpdate(session.sessionHandle, 0, inBuf, 0, len,  0,  outBuf, 0, 0);
                // System.out.println ("C_EncryptUpdate success. encrypted data len = " + encryptedDataLen);
                outBuf = new byte[encryptedDataLen];
                encryptedDataLen = session.p11.C_EncryptUpdate(session.sessionHandle, 0, inBuf, 0, len,  0,  outBuf, 0, outBuf.length);

                System.out.println ("C_EncryptUpdate 2nd call succeed. Encrypted data len = " + encryptedDataLen);
                // write the encrypted data into the cipher file
                out.write(outBuf, 0, encryptedDataLen);
            }

            // call C_EncryptFinal to get the last block
            encryptedDataLen = session.p11.C_EncryptFinal(session.sessionHandle, 0, outBuf, 0, 0);
            outBuf = new byte[encryptedDataLen];

            encryptedDataLen = session.p11.C_EncryptFinal(session.sessionHandle, 0, outBuf, 0, outBuf.length);
            System.out.println ("C_EncryptFinal success. encrypted data len = " + encryptedDataLen);

            // write the encrypted data into the cipher file
            out.write(outBuf, 0, encryptedDataLen);

            // close two files
            in.close();
            out.close();

            // open another two file to decrypt multi-part
            in = new FileInputStream(destFile);
            out = new FileOutputStream(decryptedFile);

			// now it's time to decrypt the file
			session.p11.C_DecryptInit (session.sessionHandle, encMech, keyID);
			System.out.println ("C_DecryptInit success.");

            while ( (len = in.read(inBuf))> 0)
            {
			    decryptedDataLen = session.p11.C_DecryptUpdate(session.sessionHandle, 0, inBuf, 0, len, 0, outBuf, 0, 0);
                // System.out.println ("C_DecryptUpdate success. decrypted data len = " + decryptedDataLen);

                outBuf = new byte[decryptedDataLen];
                decryptedDataLen = session.p11.C_DecryptUpdate(session.sessionHandle, 0, inBuf, 0, len, 0, outBuf, 0, outBuf.length);

                System.out.println ("C_DecryptUpdate 2nd call succeed. Decrypted data length = " + decryptedDataLen);
                // write the encrypted data into the cipher file
                out.write(outBuf, 0, decryptedDataLen);
            }

            decryptedDataLen = session.p11.C_DecryptFinal(session.sessionHandle, 0, outBuf, 0, 0);

            outBuf = new byte[decryptedDataLen];
            // call decryptFinal to get the last block
            decryptedDataLen = session.p11.C_DecryptFinal(session.sessionHandle, 0, outBuf, 0, outBuf.length);
            System.out.println ("C_DecryptFinal success. decrypted data len = " + decryptedDataLen);

            // write the encrypted data into the cipher file
            out.write(outBuf, 0, decryptedDataLen);

            // close two files
            in.close();
            out.close();

            // need to compare two files are identical
            if (Helper.CompareTwoFiles(filePath, decryptedFile))
            {
                System.out.println ("File comparison succeed. Decrypted file is identical to the original source file");
            }
            else
            {
                System.out.println ("File comparison failed. Decrypted file is NOT identical to the original source file!");
            }

			/* Delete the key */
            Helper.setKeyState (session, keyID, Helper.KeyState.Deactivated);
			session.p11.C_DestroyObject (session.sessionHandle, keyID);
			System.out.println ("Successfully deleted key");
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
            System.out.println ("End EncryptDecryptFile." );
        }
    }
}
