/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
import javax.crypto.Cipher;

import com.ingrian.security.nae.GCMParameterSpec;
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.NAECipher;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAESession;

/**
 * This sample shows how to perform crypto-operations(Encrypt and Decrypt)
 * using AES-GCM mode. IV and AAD should be passed in the Hexadecimal in this
 * sample. authTagLength should be between 32 to 128 and must be multiple of 8.
 *   File Name: AESGCMEncryptionDecryptionSample.java
 */
public class AESGCMEncryptionDecryptionSample {

	public static void main(String[] args) throws Exception{

		if (args.length != 7)
	    {
	        System.err.println
		("Usage: java AESGCMEncryptionDecryptionSample user password keyname "
				+ "authTagLength iv aad data");
	        System.exit(-1);
	    } 
	    String username  = args[0];
	    String password  = args[1];
	    String keyName   = args[2];
		int    authTagLength =  Integer.parseInt(args[3]);
		String iv  		 = args[4];
		String aad 		 = args[5];
		String data		 = args[6];
		
		/**
		 * Note: For AES-GCM algorithm, same combination of nonce (IV) and key must not be reused 
		 * during encryption/decryption operations.
		 */
		byte[] ivBytes = IngrianProvider.hex2ByteArray(iv);
		byte[] aadBytes = IngrianProvider.hex2ByteArray(aad);
		byte[] dataBytes = data.getBytes();
		
		System.out.println("iv: " + IngrianProvider.byteArray2Hex(ivBytes));
		System.out.println("AAD: " + IngrianProvider.byteArray2Hex(aadBytes));
		
		NAESession session = null;
	 	try {
	 		session = NAESession.getSession(username, password.toCharArray(), "hello".toCharArray());
	 		NAEKey key = NAEKey.getSecretKey(keyName, session);
	 		GCMParameterSpec spec = new GCMParameterSpec(authTagLength, ivBytes, aadBytes);
	 		Cipher encryptCipher = NAECipher.getNAECipherInstance("AES/GCM/NoPadding", "IngrianProvider");
	 		encryptCipher.init(Cipher.ENCRYPT_MODE, key, spec);
	 	
	 		byte[] encrypt = null;
 			encrypt = encryptCipher.doFinal(dataBytes);
	 		System.out.println("Encrypt: " + IngrianProvider.byteArray2Hex(encrypt));
		
	 		Cipher decryptCipher = NAECipher.getNAECipherInstance("AES/GCM/NoPadding", "IngrianProvider");
	 		decryptCipher.init(Cipher.DECRYPT_MODE, key, spec);
	 		byte[] decrypt = decryptCipher.doFinal(encrypt);
	 		
	 		System.out.println("data: " + new String(decrypt));	 		
		} catch (Exception e) {
			e.printStackTrace();
                       System.out.println("The Cause is " + e.getMessage() + ".");
	               throw e;
		} finally{
			// releasing session
			if(session!=null) {
        session.closeSession();
      }
		}

	 	
	}
}
