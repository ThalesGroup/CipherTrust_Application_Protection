/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
import java.security.Security;

import javax.crypto.Cipher;

import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.NAECipher;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAESEEDCipher;
import com.ingrian.security.nae.NAESession;

/**
 * To perform file encryption operation using SEED in local mode.
 * 
 * File Name: FileEncryptionSampleUsingSEED.java
 */

public class FileEncryptionSampleUsingSEED {
	public static void main(String[] args) {
		if (args.length != 8) {
			System.err
					.println("Usage: java FileEncryptionSampleUsingSEED user password keyname fileToEncrypt "
							+ "encryptedFile decryptedFile iv blockSize");
			System.exit(-1);
		}
		String username = args[0];
		String password = args[1];
		String keyName = args[2];
		String srcName = args[3];
		String dstName = args[4];
		String decrName = args[5];
		String iv = args[6];
		int blockSize = Integer.parseInt(args[7]);

		byte[] ivBytes = iv.getBytes();

		System.out.println("iv: " + IngrianProvider.byteArray2Hex(ivBytes));

		String Algo = "SEED/CBC/PKCS5Padding";

		Security.addProvider(new IngrianProvider());
		NAESession session = null;
		try {
			session = NAESession.getSession(username, password.toCharArray());
			NAEKey key = NAEKey.getSecretKey(keyName, session);

			// IvParameterSpec ivSpec = new
			// IvParameterSpec(IngrianProvider.hex2ByteArray(iv));
			NAECipher cipher = NAECipher.getNAECipherInstance(Algo,
					"IngrianProvider");
			cipher.init(Cipher.ENCRYPT_MODE, key);

			NAESEEDCipher seed = cipher.get_seed();
			seed.update(srcName, dstName, blockSize, cipher);

			cipher.init(Cipher.DECRYPT_MODE, key);
			seed = cipher.get_seed();
			seed.update(dstName, decrName, blockSize, cipher);

		} catch (Exception e) {
			e.printStackTrace();
		} finally {
			if (session != null) {
				session.closeSession();
			}
		}
	}
}
