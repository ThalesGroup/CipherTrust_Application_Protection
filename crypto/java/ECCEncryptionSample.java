/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/

import java.security.Provider;
import java.security.Security;

import javax.crypto.Cipher;
import javax.crypto.spec.IvParameterSpec;
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAESession;

/**
 * This sample demonstrates how to perform encryption/decryption using the ECC key.
 * Note: The key needs to have the encrypt/decrypt permission.
 * 
 */
public class ECCEncryptionSample {
	public static void main(String[] args) throws Exception {
	
		if (args.length != 3) {
			System.err.println("Usage: java ECCEncryptionSample user password keyname");
			System.exit(-1);
		}
		
		String userName = args[0];
		String password = args[1];
		String keyName =  args[2];
		
		// Add Ingrian provider to the list of JCE providers
		Security.addProvider(new IngrianProvider());

		// Get the list of all registered JCE providers
		Provider[] providers = Security.getProviders();
		for (int i = 0; i < providers.length; i++)
			System.out.println(providers[i].getInfo());
		
		String dataToEncrypt = "qwerty";
		String algo = "ECIESwithSHA256AES/CBC/PKCS5Padding";
		String provider = "IngrianProvider";
		NAEKey pubKey = null;
		System.out.println("DataToEncrypt = " + dataToEncrypt);
		NAESession session = null;
		try {
			//Creates NAESession: pass in NAE user and password
			session = NAESession.getSession(userName, password.toCharArray());
			
			//Creates the IvParameterSpec object
			IvParameterSpec ivSpec = new IvParameterSpec("1234567812345678".getBytes());
			
			//Gets public key to encrypt data (just a key handle , key data does not leave the Key Manager)
			pubKey = NAEKey.getPublicKey(keyName, session);
			
			//Creates a encryption cipher
			Cipher encryptCipher = Cipher.getInstance(algo, provider);
			
			//Initializes the cipher to encrypt the data
			encryptCipher.init(Cipher.ENCRYPT_MODE, pubKey, ivSpec);
			
			//Encrypt data 
			byte[] encryptedText = encryptCipher.doFinal(dataToEncrypt.getBytes());
			
			System.out.println("Encrypted Text: "+IngrianProvider.byteArray2Hex(encryptedText));
			
			//Creates a decryption cipher object
			Cipher decryptCipher = Cipher.getInstance(algo, provider);
			
			//Get private key to decrypt data (just a key handle , key data does not leave the Key Manager)
			NAEKey privKey = NAEKey.getPrivateKey(keyName, session);
			
			//Initializes the cipher to decrypt data
			decryptCipher.init(Cipher.DECRYPT_MODE, privKey, ivSpec);
			
			//Decrypt data 
			byte[] decryptedText = decryptCipher.doFinal(encryptedText);
			
			System.out.println("Decrypted text: "+IngrianProvider.toString(decryptedText));
			
		} catch (Exception e) {
			e.printStackTrace();
			throw e;
		} finally {
			if (session != null)
				//Close NAESession
				session.closeSession();
		}

	}

}
