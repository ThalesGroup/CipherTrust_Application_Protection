/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms..............
*/
import javax.crypto.Cipher;
import org.apache.commons.lang3.ArrayUtils;
import com.ingrian.security.nae.GCMParameterSpec;
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.NAECipher;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAESession;

/**
 * This sample shows how to perform crypto-operations(Encrypt and Decrypt) using
 * AES-GCM mode and update method. IV and AAD should be passed in the Hexadecimal in this sample.
 * File Name: AESGCMUpdateSample.java
 */
public class AESGCMUpdateSample {

	public static void main(String[] args) {
		if (args.length != 7) {
			System.err
					.println("Usage: java AESGCMUpdateSample user password keyname "
							+ "authTagLength iv aad data");
			System.exit(-1);
		}
		String username = args[0];
		String password = args[1];
		String keyName = args[2];
		int authTagLength = Integer.parseInt(args[3]);
		String iv = args[4];
		String aad = args[5];
		String data = args[6];
		
		/**
		 * Note: For AES-GCM algorithm, same combination of nonce (IV) and key must not be reused 
		 * during encryption/decryption operations.
		 */
		byte[] ivBytes = iv.getBytes();
		byte[] aadBytes = aad.getBytes();
		byte[] dataBytes = data.getBytes();
		NAESession session = null;
		try {
			session = NAESession.getSession(username, password.toCharArray(),"hello".toCharArray());
			NAEKey key = NAEKey.getSecretKey(keyName, session);
			GCMParameterSpec encSpec = new GCMParameterSpec(authTagLength,ivBytes, aadBytes);
			Cipher encryptCipher = NAECipher.getNAECipherInstance("AES/GCM/NoPadding", "IngrianProvider");
			encryptCipher.init(Cipher.ENCRYPT_MODE, key, encSpec);
			byte[] encryptdoFinal = null, encryptUpdate = null, encryptedText;
			encryptUpdate = encryptCipher.update(dataBytes);
			encryptdoFinal = encryptCipher.doFinal();
			if (encryptUpdate == null)
				encryptedText = encryptdoFinal;
			else
				encryptedText = ArrayUtils.addAll(encryptUpdate, encryptdoFinal);
			System.out.println("Encrypt: "+ IngrianProvider.byteArray2Hex(encryptedText));
			GCMParameterSpec decSpec = new GCMParameterSpec(authTagLength,ivBytes, aadBytes);
			decSpec.setAuthTag(encSpec.getAuthTag());
			byte[] decryptdoFinal = null, decryptUpdate = null, decryptedText;
			Cipher decryptCipher = NAECipher.getNAECipherInstance("AES/GCM/NoPadding", "IngrianProvider");
			decryptCipher.init(Cipher.DECRYPT_MODE, key, decSpec);
			decryptUpdate = decryptCipher.update(encryptedText);
			decryptdoFinal = decryptCipher.doFinal();
			if (decryptUpdate == null)
				decryptedText = decryptdoFinal;
			else
				decryptedText = ArrayUtils.addAll(decryptUpdate, decryptdoFinal);
			System.out.println("data: " + new String(decryptedText));
		} catch (Exception e) {
			e.printStackTrace();
		} finally {
			// releasing session
			if (session != null) {
				session.closeSession();
			}
		}
	}
}
