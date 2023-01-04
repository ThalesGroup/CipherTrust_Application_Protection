/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
import java.security.Security;

import javax.crypto.Cipher;

import com.ingrian.security.nae.GCMParameterSpec;
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.NAEAESGCMCipher;
import com.ingrian.security.nae.NAECipher;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAESession;

/**
 * This samples shows how to perform crypto operation on the file. It will
 * store the encrypted data into the file in hexadecimal format. While 
 * performing decrypt operation the input file should also be in hexadecimal
 * format.
 *
 * It is recommended to use single cipher instance for both encrypt and
 * and decrypt operation only in this specific case. i.e. To perform file
 * encryption operation using gcm in both local and remote  mode.
 * 
 *   File Name: FileEncryptionSampleUsingGCM.java
 */
public class FileEncryptionSampleUsingGCM {

	public static void main(String[] args)  {
		if (args.length != 10)
        {
            System.err.println
		("Usage: java FileEncryptionSampleUsingGCM user password keyname fileToEncrypt "
				+ "encryptedFile decryptedFile authTagLength iv aad blockSize");
            System.exit(-1);
        } 
        String username  = args[0];
        String password  = args[1];
        String keyName   = args[2];
		String srcName   = args[3];
		String dstName   = args[4];
		String decrName  = args[5];
		int    authTagLength =  Integer.parseInt(args[6]);
		String iv  		 = args[7];
		String aad 		 = args[8];
		int    blockSize   = Integer.parseInt(args[9]);
		
		/**
		 * Note: For AES-GCM algorithm, same combination of nonce (IV) and key must not be reused 
		 * during encryption/decryption operations.
		 */
		byte[] ivBytes = iv.getBytes();
		byte[] aadBytes = aad.getBytes();
		
		System.out.println("iv: " + IngrianProvider.byteArray2Hex(ivBytes));
		System.out.println("AAD: " + IngrianProvider.byteArray2Hex(aadBytes));
		
		Security.addProvider(new IngrianProvider());
		NAESession session = null;
 		try {
 			session = NAESession.getSession(username, password.toCharArray());
 			NAEKey key = NAEKey.getSecretKey(keyName, session);

 	 		GCMParameterSpec spec = new GCMParameterSpec(authTagLength, ivBytes, aadBytes);
	 		NAECipher cipher = NAECipher.getNAECipherInstance("AES/GCM/NoPadding", "IngrianProvider");
	 		cipher.init(Cipher.ENCRYPT_MODE, key, spec);
				 		
	 		NAEAESGCMCipher gcm = cipher.get_spi();
	 		gcm.update(srcName, dstName, blockSize, cipher);
		 	
	 		cipher.init(Cipher.DECRYPT_MODE, key, spec);
	 		gcm = cipher.get_spi();
		 	gcm.update(dstName, decrName, blockSize, cipher);
 		} catch (Exception e) {
 			e.printStackTrace();
                       System.out.println("The Cause is " + e.getMessage() + ".");
	               throw e;
 		} finally{
 			if(session!=null) {
				session.closeSession();
			}
 		}
	}

}
