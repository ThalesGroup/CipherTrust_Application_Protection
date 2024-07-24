/**
 * Sample code is provided for educational purposes.
 * No warranty of any kind, either expressed or implied by fact or law. 
 * Use of this item is not restricted by copyright or license terms.
 */

import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.security.Security;
import java.util.Arrays;

import javax.crypto.Cipher;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;

import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAEPrivateKey;
import com.ingrian.security.nae.NAEPublicKey;
import com.ingrian.security.nae.NAESecureRandom;
import com.ingrian.security.nae.NAESession;

/**
 * This sample shows how to encrypt/decrypt a file using RSA Algorithm.
 * Use RSA key size greater than 1024 for this sample.
 * To encrypt the file: 
 *
 * 1) Generate a symmetric AES-256 key and IV which will be used to encrypt the input file.
 * 2) Write the AES-256 key and IV, encrypted together with Asymmetric public key to the output file.
 * 3) Write the input file encrypted with AES-256 key and IV to the output file.
 * 
 * To decrypt the file: 
 *
 * 1) Read AES-256 key and IV from the input file and decrypt them using private key.
 * 2) Write the encrypted file decrypted using AES-256 key and IV to the decrypted file.
 * 
 */
public class FileEncryptionDecryptionSampleUsingRSA {
	
	//how many bytes of data to be read from the input stream (can be any size)
	public final static int BUFFERSIZE=512;

	public static void main(String[] args) throws Exception {
		if (args.length != 6) {
			System.err.println(
					"Usage: java FileEncryptionDecryptionSampleUsingRSA userName password asymKeyName fileToEncrypt encryptedFile decryptedFile");
			System.exit(-1);
		}

		String userName = args[0];
		String password = args[1];
		String asymKeyName = args[2];
		String fileToEncrypt = args[3];
		String encryptedFile = args[4];
		String decryptedFile = args[5];
				
		//Add Ingrian provider to the list of JCE providers
		Security.addProvider(new IngrianProvider());
		NAESession session = null;
		try {
			
			//Creates NAE Session and pass in NAE userName and password
			session = NAESession.getSession(userName, password.toCharArray());
			
			//Creates NAEPublicKey object
			NAEPublicKey asymPubKey = NAEKey.getPublicKey(asymKeyName, session);
			//Get NAESecureRandom object
			NAESecureRandom rng = new NAESecureRandom(session);
			performEncryption(fileToEncrypt, encryptedFile, asymPubKey, rng);
			
			//Creates NAEPrivateKey object
			NAEPrivateKey asymPrivKey = NAEKey.getPrivateKey(asymKeyName, session);
			performDecryption(encryptedFile, decryptedFile, asymPrivKey);
			
		} catch (Exception e) {
			System.err.println("The Cause is " + e.getMessage() + ".");
			throw e;
		} finally {
			if (session != null) {
				//Close NAESession
				session.closeSession();
			}
		}
	}
	
	private static void performEncryption(String fileToEncrypt, String encryptedFile, NAEPublicKey asymPubKey, NAESecureRandom rng ) throws Exception {
		
		FileOutputStream fos = null;
		FileInputStream fis = null;
		
		try {
			//use NAESecureRandom object to generate the AES-256 key which is used to encrypt the file
			byte[] aeskey = new byte[32];
			rng.nextBytes(aeskey);

			//generate random IV which is used to encrypt the file
			byte[] iv = new byte[16];
			rng.nextBytes(iv);
			IvParameterSpec ivSpec = new IvParameterSpec(iv);

			//set up the Symmetric key and cipher
			SecretKeySpec symEncryptKey = new SecretKeySpec(aeskey, "AES");
			Cipher symEncryptCipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
			symEncryptCipher.init(Cipher.ENCRYPT_MODE, symEncryptKey, ivSpec);

			//set up the encrypt cipher
			Cipher asymEncryptCipher = Cipher.getInstance("RSA/None/PKCS1OAEPPaddingSHA384", "IngrianProvider");
			//initialize cipher to encrypt
			asymEncryptCipher.init(Cipher.ENCRYPT_MODE, asymPubKey);

			//create a FileOutputStream to write AES key and IV encrypted together with Asymmetric key to file
			fos = new FileOutputStream(encryptedFile);
			byte[] aeskeyIv = Arrays.copyOf(aeskey, 48);
		    System.arraycopy(iv, 0, aeskeyIv, 32, 16);
		    byte[] encAeskeyIvBuf=asymEncryptCipher.doFinal(aeskeyIv);
			fos.write(encAeskeyIvBuf);
			
			//create a FileInputStream to read the input file
			fis = new FileInputStream(fileToEncrypt);

			//read the file as blocks and write encrypted text using symmetric cipher to the FileOutputStream
			byte[] inbuf = new byte[BUFFERSIZE];
			byte[] cipherEncryptText;
			int len = 0;
			while((len = fis.read(inbuf)) != -1) {
				cipherEncryptText = symEncryptCipher.update(inbuf, 0, len);
				if(cipherEncryptText != null)
					fos.write(cipherEncryptText);
			}
			
			cipherEncryptText = symEncryptCipher.doFinal();
			if(cipherEncryptText != null) {
				fos.write(cipherEncryptText);
			}
			System.out.println("Done encrypting the file.");
			
		}catch(Exception e) {
			System.err.println("The Cause is " + e.getMessage() + ".");
			throw e;
		}finally {
			if (fis != null) {
				fis.close();
			}
			if (fos != null) {
				fos.close();
			}
		}
	}
	
	private static void performDecryption(String encryptedFile, String decryptedFile, NAEPrivateKey asymPrivKey) throws Exception {
		
		FileOutputStream fos = null;
		FileInputStream fis = null;
		
		try {
			//set up the decrypt cipher
			Cipher asymDecryptCipher = Cipher.getInstance("RSA/None/PKCS1OAEPPaddingSHA384", "IngrianProvider");
			
			//initialize cipher to decrypt
			asymDecryptCipher.init(Cipher.DECRYPT_MODE, asymPrivKey);

			//get Asymmetric key size and check whether it is versioned
			boolean versioned = asymPrivKey.isVersioned();
			int asymkeySize = asymPrivKey.getKeySize();
			if (asymkeySize != 0)
				asymkeySize = asymkeySize / 8;

			//initialize AES key and IV combined array accordingly when key is versioned
			byte[] encAeskeyIv=null;
			if (versioned) {
				encAeskeyIv = new byte[asymkeySize + 3];
			} else {
				encAeskeyIv = new byte[asymkeySize];
			}
			
			//create a FileInputStream and read encrypted AES key and IV into byte arrays and initialize them
			fis = new FileInputStream(encryptedFile);
			fis.read(encAeskeyIv);
			byte[] aeskeyIv=new byte[48];
			aeskeyIv=asymDecryptCipher.doFinal(encAeskeyIv);
			
			byte[] aeskey = Arrays.copyOfRange(aeskeyIv, 0, 32);
			byte[] iv = Arrays.copyOfRange(aeskeyIv, 32, 48);

			//initialize Symmetric cipher with AES key and IV fetched
			IvParameterSpec ivSpecDec = new IvParameterSpec(iv);
			SecretKeySpec symEncryptKey_Dec = new SecretKeySpec(aeskey, "AES");
			Cipher symDecryptCipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
			symDecryptCipher.init(Cipher.DECRYPT_MODE, symEncryptKey_Dec, ivSpecDec);

			//create a FileOutputStream to write the decrypted file data
			fos = new FileOutputStream(decryptedFile);

			//read the file as blocks of data and write decrypted text using symmetric cipher to the FileOutputStream
			byte[] inbuf = new byte[BUFFERSIZE];
			byte[] cipherDecryptText;
			int len = 0;
			while((len = fis.read(inbuf)) != -1) {
				cipherDecryptText = symDecryptCipher.update(inbuf, 0, len);
				if(cipherDecryptText != null) {
					fos.write(cipherDecryptText);
				}
			}
			cipherDecryptText = symDecryptCipher.doFinal();
			
			if(cipherDecryptText != null) {
				fos.write(cipherDecryptText);
			}
			
			System.out.println("Done decrypting the file.");
			
		}catch(Exception e) {
			System.err.println("The Cause is " + e.getMessage() + ".");
			throw e;
		}finally {
			if (fis != null) {
				fis.close();
			}
			if (fos != null) {
				fos.close();
			}
		}
		
	}
}
